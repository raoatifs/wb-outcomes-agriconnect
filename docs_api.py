"""Retrieve public project documents (PAD / ISR / ICR) from the World Bank
Documents & Reports (WDS) API.

API: https://search.worldbank.org/api/v3/wds
We query by project id (P-code), which every AgriConnect row carries, and
return document metadata plus the URLs of the machine-readable text/PDF.
"""
from __future__ import annotations
import time
from pathlib import Path
import requests
import pandas as pd

from . import config, db

WDS = "https://search.worldbank.org/api/v3/wds"
DOCS_DIR = config.DATA / "docs"

# Document type labels used by WDS for the results chain of interest.
DOCTYPES = {
    "PAD": "Project Appraisal Document",
    "ISR": "Implementation Status and Results Report",
    "ICR": "Implementation Completion and Results Report",
}


def fetch_doc_metadata(project_id: str, rows: int = 20,
                       timeout: int = 60) -> pd.DataFrame:
    """Return a metadata frame of public documents for one project id."""
    params = {
        "format": "json",
        "qterm": project_id,
        "fl": "docdt,docty,display_title,pdfurl,txturl,projectid,count",
        "rows": rows,
    }
    r = requests.get(WDS, params=params, timeout=timeout)
    r.raise_for_status()
    docs = r.json().get("documents", {})
    records = []
    for key, d in docs.items():
        if key == "facets":
            continue
        records.append({
            "project_id": project_id,
            "doc_date": d.get("docdt"),
            "doc_type": d.get("docty"),
            "title": d.get("display_title"),
            "pdf_url": d.get("pdfurl"),
            "txt_url": d.get("txturl"),
        })
    return pd.DataFrame(records)


def download_text(txt_url: str, dest: Path, timeout: int = 90) -> Path | None:
    """Download the plain-text rendition of a document if available."""
    if not txt_url:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(txt_url, timeout=timeout)
    r.raise_for_status()
    dest.write_text(r.text, encoding="utf-8", errors="ignore")
    return dest


def collect_for_projects(project_ids: list[str], sleep: float = 0.5) -> pd.DataFrame:
    frames = []
    for pid in project_ids:
        try:
            frames.append(fetch_doc_metadata(pid))
        except requests.RequestException as e:
            print(f"[docs] {pid} failed: {e}")
        time.sleep(sleep)
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not out.empty:
        conn = db.connect()
        db.replace_table(conn, out, "documents")
        conn.close()
    return out


if __name__ == "__main__":
    conn = db.connect()
    projects = db.read_projects(conn)
    conn.close()
    # a small agriculture/water sample for the operational-logic case study
    sample = (projects[projects["global_practice"].isin(["AGR", "WAT"])]
              ["project_id"].head(10).tolist())
    meta = collect_for_projects(sample)
    print(f"[docs] retrieved metadata for {meta['project_id'].nunique() if not meta.empty else 0} projects, "
          f"{len(meta)} documents")
