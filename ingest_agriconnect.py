"""Ingest the AgriConnect outcome workbook into the `projects` SQL table.

Handles the messy bits once, here: trimmed headers, coerced numerics, parsed
dates, an ISO3 column, and a regional-aggregate flag.
"""
from __future__ import annotations
import pandas as pd

from . import config, db

RENAME = {
    "Project ID": "project_id",
    "Project Name": "project_name",
    "Institution": "institution",
    "Approval Date": "approval_date",
    "Closing Date": "closing_date",
    "Region": "region",
    "Country": "country",
    "Global Practice": "global_practice",
    "Project Status": "project_status",
    "Instrument Type": "instrument_type",
    "Project Financier": "project_financier",
    "ISR/ICR/PAD Reporting Fiscal Year": "report_fiscal_year",
    "ISR/ICR/PAD Approval Date": "report_approval_date",
    "ISR/ICR/PAD Sequence Number": "report_sequence_no",
    "Indicator Name": "indicator_name",
    "Unit of Measure": "unit_of_measure",
    "Baseline Value": "baseline_value",
    "Progress Value": "progress_value",
    "Achieved Results": "achieved_results",
}
NUMERIC = ["baseline_value", "progress_value", "achieved_results",
           "report_fiscal_year", "report_sequence_no"]


def load_raw(path=None) -> pd.DataFrame:
    path = path or config.AGRICONNECT_XLSX
    df = pd.read_excel(path, sheet_name=config.AGRICONNECT_SHEET)
    df.columns = [c.strip() for c in df.columns]
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={k.strip(): v for k, v in RENAME.items()}).copy()
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["approval_year"] = pd.to_datetime(
        df["approval_date"], errors="coerce").dt.year
    for c in ("approval_date", "closing_date", "report_approval_date"):
        df[c] = pd.to_datetime(df[c], errors="coerce").dt.strftime("%Y-%m-%d")
    df["iso3"] = df["country"].map(config.iso3)
    df["is_regional_aggregate"] = df["country"].isin(
        config.REGIONAL_AGGREGATES).astype(int)
    ordered = [
        "project_id", "project_name", "institution", "approval_date",
        "closing_date", "approval_year", "region", "country", "iso3",
        "is_regional_aggregate", "global_practice", "project_status",
        "instrument_type", "project_financier", "report_fiscal_year",
        "report_approval_date", "report_sequence_no", "indicator_name",
        "unit_of_measure", "baseline_value", "progress_value",
        "achieved_results",
    ]
    return df[ordered]


def ingest(path=None) -> int:
    df = clean(load_raw(path))
    conn = db.connect()
    db.init_db(conn)
    n = db.replace_table(conn, df, "projects")
    conn.close()
    return n


if __name__ == "__main__":
    n = ingest()
    print(f"[ingest] loaded {n} project-indicator rows into projects")
