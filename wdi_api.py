"""Pull World Development Indicators via the World Bank Indicators API.

API docs: https://api.worldbank.org/v2/  (no key required)
Endpoint pattern:
    /v2/country/{iso3;iso3;...}/indicator/{code}?format=json&mrv=N

Only the ISO3 countries present in the AgriConnect table are requested, so the
WDI table is scoped to the portfolio rather than the whole world.
"""
from __future__ import annotations
import time
import requests
import pandas as pd

from . import config, db

BASE = "https://api.worldbank.org/v2"


def fetch_indicator(iso3_codes: list[str], code: str, mrv: int = 5,
                    timeout: int = 60, retries: int = 3) -> pd.DataFrame:
    """Fetch the most-recent `mrv` values of one indicator for many countries."""
    countries = ";".join(iso3_codes)
    url = f"{BASE}/country/{countries}/indicator/{code}"
    params = {"format": "json", "per_page": 20000, "mrv": mrv}
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            payload = r.json()
            if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
                return pd.DataFrame(columns=["iso3", "country", "indicator", "year", "value"])
            rows = [
                {
                    "iso3": d["countryiso3code"],
                    "country": d["country"]["value"],
                    "indicator": config.WDI_INDICATORS.get(code, code),
                    "year": int(d["date"]),
                    "value": d["value"],
                }
                for d in payload[1]
            ]
            return pd.DataFrame(rows)
        except (requests.RequestException, ValueError) as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    return pd.DataFrame(columns=["iso3", "country", "indicator", "year", "value"])


def build_wdi_table(mrv: int = 5) -> pd.DataFrame:
    conn = db.connect()
    projects = db.read_projects(conn)
    iso3_codes = sorted(c for c in projects["iso3"].dropna().unique())
    frames = []
    for code in config.WDI_INDICATORS:
        df = fetch_indicator(iso3_codes, code, mrv=mrv)
        print(f"[wdi] {code:<16} rows={len(df)}")
        frames.append(df)
    wdi = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    db.replace_table(conn, wdi, "wdi")
    conn.close()
    return wdi


if __name__ == "__main__":
    wdi = build_wdi_table()
    print(f"[wdi] total rows loaded: {len(wdi)}")
