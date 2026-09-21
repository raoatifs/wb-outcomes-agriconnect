"""SQLite layer: schema, load, and query helpers.

A single relational store keeps the AgriConnect outcome table and the WDI
country-context table joinable on ISO3 code, which is the backbone of the
country-level analysis.
"""
from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    project_id            TEXT,
    project_name          TEXT,
    institution           TEXT,
    approval_date         TEXT,
    closing_date          TEXT,
    approval_year         INTEGER,
    region                TEXT,
    country               TEXT,
    iso3                  TEXT,
    is_regional_aggregate INTEGER,
    global_practice       TEXT,
    project_status        TEXT,
    instrument_type       TEXT,
    project_financier     TEXT,
    report_fiscal_year    INTEGER,
    report_approval_date  TEXT,
    report_sequence_no    INTEGER,
    indicator_name        TEXT,
    unit_of_measure       TEXT,
    baseline_value        REAL,
    progress_value        REAL,
    achieved_results      REAL
);

CREATE TABLE IF NOT EXISTS wdi (
    iso3        TEXT,
    country     TEXT,
    indicator   TEXT,
    year        INTEGER,
    value       REAL
);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    db_path = Path(db_path or config.DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def replace_table(conn: sqlite3.Connection, df: pd.DataFrame, table: str) -> int:
    """Overwrite `table` with `df` (idempotent pipeline reruns)."""
    df.to_sql(table, conn, if_exists="replace", index=False)
    conn.commit()
    return len(df)


def read_projects(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM projects", conn)


def read_wdi(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM wdi", conn)
