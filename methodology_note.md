# Methodology Note

## 1. Data
- **Source:** World Bank AgriConnect outcome extract ("External Release"),
  sheet *Project Details*: 245 project-indicator rows, one row per project,
  carrying the latest available indicator observation.
- **Fields used:** project id (P-code), country, region, Global Practice,
  status, approval/closing dates, ISR/ICR/PAD reporting fiscal year and
  sequence number, indicator name, unit, and three value fields —
  `baseline_value`, `progress_value`, `achieved_results`.
- **Enrichment:** six WDI indicators (undernourishment, food production index,
  agricultural land %, rural population %, poverty headcount, agriculture value
  added % GDP) pulled for the portfolio's ISO3 countries via the WB Indicators
  API (`mrv=5`).

## 2. The three value fields (this is the crux)
Per the workbook's own variable definitions:
- `progress_value` — the most recent **cumulative reported** value from ISR/ICR.
- `achieved_results` — beneficiaries after **within-project de-duplication** and
  **cross-project geospatial de-duplication**, applying a conversion factor.

Because a person served by two overlapping projects (or counted twice within a
project) should be counted once, `achieved_results ≤ progress_value` for rows
counted in absolute people. The analysis therefore uses **`achieved_results`**
as the impact measure and treats `progress_value` as the raw output tally. The
gap between the two is the headline finding.

## 3. Aggregation rules
- Beneficiary totals sum `achieved_results`, which is always in absolute people.
- Country rankings exclude the 17 **regional operations** (e.g., "Western and
  Central Africa") whose "country" is a multi-country aggregate, so single
  countries are not double-counted against them.
- One row is reported in **"Number (Thousand)"** (P163742, Sri Lanka); it is
  flagged by a test and excluded from the absolute-count invariant. Its effect
  on the 58.3M raw tally is negligible (~0.07M) and none on the de-duplicated
  total.

## 4. Data-quality checks (`tests/`)
Completeness (no missing project ids), uniqueness (no duplicate P-codes or
rows), referential validity (every single-country row maps to a valid ISO3;
regional ops map to none), type correctness (value fields numeric), range sanity
(values non-negative; approval years 2000–2030), domain (status ∈ {Active,
Closed}), and **unit consistency** (scaled-unit rows are flagged). 19 checks;
all pass.

## 5. NLP/LLM extraction
`src/extract_nlp.py` extracts development objective, beneficiaries, indicator
name, baseline, target, actual, and climate/agriculture themes from project
document text. Two backends: a dependency-free **rule-based** extractor (regex +
keyword lexicons) and an optional **LLM hook**. Crucially, the `evaluate`
function scores extracted numeric fields against the **official values in the
AgriConnect table as ground truth** and reports per-field match and an accuracy
score — so extraction quality is measured, not asserted. Known failure modes:
scanned/tabular PADs where results frameworks are images; indicators split
across pages; multiple indicators per document.

## 6. PAD → ISR → ICR logic
The results chain is: the **PAD** defines the development objective, indicators,
baselines, and end targets; **ISRs** report progress during implementation
(the `report_sequence_no` orders them); the **ICR** records final achievement.
This extract holds the latest observation per project; reconstructing a full
target-evolution trajectory for a case-study project uses `src/docs_api.py` to
pull the document series.

## 7. Reproducibility
Deterministic reruns (`if_exists="replace"`), pinned dependencies, modular
importable code, and separated network stages so the core analysis runs offline.

## 8. Limitations
One observation per project (no within-project time series in this file);
`achieved_results` depends on WB's conversion/de-duplication factors, which are
not published per row; regional operations lack country granularity; WDI years
differ from project reporting years, so country context is indicative.
