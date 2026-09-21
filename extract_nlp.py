"""Extract structured results-framework fields from project-document text.

Two backends:
  * rule-based (default): regex + keyword heuristics, fully offline and
    explainable field-by-field.
  * llm (real): a live Anthropic Claude call via the official `anthropic` SDK
    (`make_anthropic_caller`). It runs when `ANTHROPIC_API_KEY` (or an
    `ant auth login` profile) is available; otherwise the pipeline falls back
    to the rule-based backend, so it never *depends* on a paid API to run.

The point of the module is not perfect extraction but an *evaluated* one: the
`evaluate` function scores extracted indicator values against the official
baseline/progress/achieved figures in the AgriConnect table (ground truth).
"""
from __future__ import annotations
import os
import re
import json
from dataclasses import dataclass, asdict, field
from typing import Callable

# --- thematic keyword lexicons ----------------------------------------------
CLIMATE_TERMS = ["climate", "resilience", "adaptation", "drought", "flood",
                 "climate-smart", "greenhouse", "emission", "mitigation"]
AGRI_TERMS = ["agricultur", "farmer", "crop", "livestock", "irrigation",
              "food security", "value chain", "smallholder", "productivity"]

NUM = r"[-+]?\d[\d,\.]*"


@dataclass
class Extraction:
    development_objective: str | None = None
    beneficiaries: float | None = None
    indicator_name: str | None = None
    baseline: float | None = None
    target: float | None = None
    actual: float | None = None
    climate_theme: bool = False
    agriculture_theme: bool = False
    matched_terms: list[str] = field(default_factory=list)

    def as_dict(self):
        return asdict(self)


def _to_number(s: str | None):
    if s is None:
        return None
    try:
        return float(s.replace(",", ""))
    except (ValueError, AttributeError):
        return None


def _search(pattern: str, text: str, group: int = 1):
    m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return m.group(group).strip() if m else None


def rule_extract(text: str) -> Extraction:
    """Regex/keyword extraction. Explainable and dependency-free."""
    ex = Extraction()

    # Development objective: text after "development objective" up to a period/newline block.
    ex.development_objective = _search(
        r"(?:project|program|pdo)\s+development\s+objective[s]?\s*[:\-]?\s*(.{20,400}?)(?:\.\s|\n\n)",
        text,
    )

    # Beneficiaries: "X beneficiaries" / "reach X farmers"
    ben = _search(rf"({NUM})\s+(?:direct\s+)?(?:project\s+)?beneficiaries", text)
    if ben is None:
        ben = _search(rf"reach(?:ing)?\s+(?:about\s+)?({NUM})\s+(?:farmers|people|smallholders)", text)
    ex.beneficiaries = _to_number(ben)

    # Indicator line with baseline/target/actual, tolerant to ordering.
    ex.indicator_name = _search(r"indicator\s*[:\-]\s*(.{5,120}?)(?:\.\s|\n)", text)
    ex.baseline = _to_number(_search(rf"baseline\s*[:\-=]?\s*({NUM})", text))
    ex.target = _to_number(_search(rf"(?:end\s*)?target\s*[:\-=]?\s*({NUM})", text))
    ex.actual = _to_number(
        _search(rf"(?:actual|achieved|current\s+value)\s*[:\-=]?\s*({NUM})", text))

    low = text.lower()
    ex.matched_terms = sorted({t for t in CLIMATE_TERMS + AGRI_TERMS if t in low})
    ex.climate_theme = any(t in low for t in CLIMATE_TERMS)
    ex.agriculture_theme = any(t in low for t in AGRI_TERMS)
    return ex


# --- LLM backend (real Anthropic Claude call) --------------------------------
SYSTEM_PROMPT = (
    "You are a precise information-extraction engine for World Bank project "
    "documents (PADs, ISRs, ICRs). Extract only what is stated in the text. "
    "Respond with a SINGLE JSON object and nothing else - no prose, no markdown "
    "code fences."
)

EXTRACTION_INSTRUCTION = """Extract these fields as JSON:
- development_objective (string | null): the project/program development objective
- beneficiaries (number | null): total direct beneficiaries / farmers to be reached
- indicator_name (string | null): the primary results indicator
- baseline (number | null): the indicator's baseline value
- target (number | null): the indicator's end target value
- actual (number | null): the latest actual / achieved value
- climate_theme (boolean): true if the text concerns climate/resilience/adaptation
- agriculture_theme (boolean): true if the text concerns agriculture/farmers/food

Use null when a field is not present. Numbers must be plain numbers (no commas or
units). Return ONLY the JSON object.

DOCUMENT:
"""


def _coerce(data: dict) -> Extraction:
    """Map an LLM/JSON dict onto the Extraction dataclass with light coercion."""
    def num(v):
        if v is None or isinstance(v, bool):
            return None
        if isinstance(v, (int, float)):
            return float(v)
        return _to_number(str(v))
    return Extraction(
        development_objective=data.get("development_objective"),
        beneficiaries=num(data.get("beneficiaries")),
        indicator_name=data.get("indicator_name"),
        baseline=num(data.get("baseline")),
        target=num(data.get("target")),
        actual=num(data.get("actual")),
        climate_theme=bool(data.get("climate_theme", False)),
        agriculture_theme=bool(data.get("agriculture_theme", False)),
        matched_terms=list(data.get("matched_terms", []) or []),
    )


def make_anthropic_caller(model: str | None = None,
                          max_tokens: int = 2048) -> Callable[[str], dict]:
    """Return a `call(prompt) -> dict` backed by a real Claude request.

    Model defaults to claude-opus-5 (override with the LLM_MODEL env var, e.g.
    claude-sonnet-5 or claude-haiku-4-5 for cheaper bulk extraction). Credentials
    are resolved by the SDK from ANTHROPIC_API_KEY or an `ant auth login` profile.
    """
    import anthropic  # imported lazily so the repo runs without the SDK
    client = anthropic.Anthropic()
    model = model or os.environ.get("LLM_MODEL", "claude-opus-5")

    def call(prompt: str) -> dict:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            output_config={"effort": "low"},  # extraction is not reasoning-heavy
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text).strip()
        return json.loads(text)

    return call


def llm_extract(text: str, call: Callable[[str], dict]) -> Extraction:
    """LLM backend. `call` takes a prompt and returns a parsed JSON dict.

    Injected rather than imported so the extractor stays testable without a
    network call; `make_anthropic_caller()` supplies the real Claude-backed one.
    """
    data = call(EXTRACTION_INSTRUCTION + text[:8000])
    return _coerce(data)


def extract(text: str, backend: str = "auto") -> Extraction:
    """Dispatch to a backend. 'auto' uses the LLM when credentials exist, else rules."""
    if backend in ("llm", "auto"):
        try:
            return llm_extract(text, make_anthropic_caller())
        except Exception as e:  # missing SDK/key/network -> graceful fallback
            if backend == "llm":
                raise
            print(f"[nlp] LLM backend unavailable ({type(e).__name__}); using rules.")
    return rule_extract(text)


def evaluate(extracted: dict, truth: dict, tol: float = 0.02) -> dict:
    """Score numeric fields against ground truth (relative tolerance `tol`)."""
    result = {}
    for field_name in ("baseline", "target", "actual", "beneficiaries"):
        e, t = extracted.get(field_name), truth.get(field_name)
        if t is None or e is None:
            result[field_name] = {"extracted": e, "truth": t, "match": None}
            continue
        denom = abs(t) if t else 1.0
        result[field_name] = {
            "extracted": e, "truth": t,
            "match": abs(e - t) / denom <= tol,
        }
    scored = [v["match"] for v in result.values() if v["match"] is not None]
    result["_accuracy"] = round(sum(scored) / len(scored), 3) if scored else None
    result["_n_scored"] = len(scored)
    return result


if __name__ == "__main__":
    from . import config
    sample = config.RAW / "sample_project_doc.txt"
    if not sample.exists():
        print(f"[nlp] no sample at {sample}; run docs_api to download real text.")
        raise SystemExit(0)

    text = sample.read_text(encoding="utf-8", errors="ignore")
    # Ground truth for the fixture (mirrors the AgriConnect table's value fields).
    truth = {"baseline": 0, "target": 250000, "actual": 180000,
             "beneficiaries": 250000}

    print("=== rule-based backend ===")
    rule = rule_extract(text)
    for k, v in rule.as_dict().items():
        print(f"   {k}: {v}")
    print("   accuracy vs truth:", evaluate(rule.as_dict(), truth)["_accuracy"])

    have_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    print(f"\n=== LLM backend (Claude) === {'running' if have_key else 'no ANTHROPIC_API_KEY - skipped'}")
    if have_key:
        try:
            llm = llm_extract(text, make_anthropic_caller())
            for k, v in llm.as_dict().items():
                print(f"   {k}: {v}")
            print("   accuracy vs truth:", evaluate(llm.as_dict(), truth)["_accuracy"])
        except Exception as e:
            print(f"   LLM call failed: {type(e).__name__}: {e}")
