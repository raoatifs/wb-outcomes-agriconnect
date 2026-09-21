# World Bank Outcomes Analytics Pipeline: Agriculture, Food Security, and Climate Resilience

A small, reproducible data-science pipeline built around the World Bank Group's
**AgriConnect** outcome data. It ingests the official AgriConnect outcome
extract into SQL, enriches it with country context pulled live from the **World
Bank Indicators (WDI) API**, validates it with **pytest**, prototypes an
**NLP/LLM field extractor** for project documents (PAD / ISR / ICR), and
produces **portfolio analytics** figures and an executive one-pager.

Built as a hands-on companion to the WBG **Department for Outcomes** agenda:
moving from *measuring activity* to *managing for impact*, with food security
and climate resilience — the two Scorecard themes closest to my dissertation —
as the analytical focus.

---

## What it demonstrates (mapped to the role)

| Capability | Where in this repo |
|---|---|
| APIs | `src/wdi_api.py` (Indicators API), `src/docs_api.py` (Documents & Reports API) |
| SQL / relational data | `src/db.py` (SQLite schema; `projects` ⋈ `wdi` on ISO3) |
| Reproducible pipeline | `run_pipeline.py`, modular `src/`, deterministic reruns |
| Version control / workflow | Git repo layout, `requirements.txt`, isolated modules |
| Testing / data validation | `tests/` — 19 pytest checks (completeness, uniqueness, codes, types, ranges, unit consistency) |
| NLP / LLM | `src/extract_nlp.py` — rule-based extractor + optional LLM hook + **evaluation against ground truth** |
| Portfolio analytics | `src/analysis.py` — concentration, regional/practice breakdowns |
| Executive communication | `outputs/executive_one_pager.md`, figures, `ARTICLE_agriconnect.md` |
| WBG results frameworks | PAD→ISR→ICR reporting chain handled in ingest; de-duplication methodology explained |

---

## Repository structure

```
wb-outcomes-agriconnect/
├── README.md
├── requirements.txt
├── run_pipeline.py            # orchestrator (offline by default; --wdi / --docs opt-in)
├── methodology_note.md
├── ARTICLE_agriconnect.md     # draft LinkedIn/Substack article
├── data/
│   ├── raw/                   # AgriConnect xlsx + a synthetic doc fixture
│   └── db/                    # SQLite (gitignored)
├── src/
│   ├── config.py             # paths, WDI indicators, name→ISO3 map
│   ├── db.py                 # SQLite schema + load/query
│   ├── ingest_agriconnect.py # xlsx → projects table
│   ├── wdi_api.py            # WDI Indicators API → wdi table
│   ├── docs_api.py           # Documents & Reports API → document metadata/text
│   ├── extract_nlp.py        # PAD/ISR/ICR field extraction + evaluation
│   └── analysis.py           # portfolio analytics → figures + tables
├── tests/                    # pytest data-quality + extraction tests
└── outputs/
    ├── figures/              # fig1_dedup … fig4_practice (.png)
    ├── tables/               # by_region, by_global_practice, top15_countries, top20_projects (.csv)
    ├── results_summary.json
    └── executive_one_pager.md
```

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python run_pipeline.py          # ingest + analysis (offline)
python run_pipeline.py --wdi    # also pull WDI country context (network)
python run_pipeline.py --docs   # also fetch PAD/ISR/ICR metadata (network)

pytest -q                       # 19 data-quality + extraction checks
python -m src.extract_nlp       # NLP extraction demo on the sample document
```

## Headline results (245 projects; see `outputs/results_summary.json`)

- Portfolio reports **58.3M** cumulative beneficiaries but **10.1M** after
  de-duplication — a **−82.6%** correction. Measuring impact ≠ summing outputs.
- **85%** of de-duplicated beneficiaries are in Sub-Saharan Africa;
  **80%** are delivered through the Agriculture (AGR) Global Practice.
- **Top 5 projects = 69%** and **top 20 = 89%** of all beneficiaries: outcomes
  are highly concentrated.
- **94%** of indicator rows have a baseline of zero — a measurement-quality flag.
- A validation test caught **one row reported in "Number (Thousand)"** that
  would distort any naive aggregation.

## Data & attribution

`data/raw/agriconnect_outcome.xlsx` is the World Bank "External Release"
AgriConnect outcome extract. WDI data © World Bank, retrieved via the public
Indicators API. `data/raw/sample_project_doc.txt` is a **synthetic** fixture for
the offline NLP demo, not a real document. Verify the release status of any WB
file before publishing a public repository.
