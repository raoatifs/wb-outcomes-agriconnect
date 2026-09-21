"""Central configuration: paths, indicator lists, and the name->ISO3 map.

Keeping paths and constants in one module keeps the rest of the pipeline
importable and testable regardless of the working directory.
"""
from __future__ import annotations
from pathlib import Path

# --- Paths -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
DB_PATH = DATA / "db" / "outcomes.sqlite"
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"

AGRICONNECT_XLSX = RAW / "agriconnect_outcome.xlsx"
AGRICONNECT_SHEET = "Project Details"

# --- Official AgriConnect program figures ------------------------------------
# These are the World Bank's published program-level numbers (external to this
# dataset). The dataset's own de-duplicated sum (~10.1M) is a subset/snapshot
# and is reported separately in the analysis. Update these in one place.
AGRICONNECT = {
    "reach_short": "19M",
    "reach_long": "19 million",
    "reach_asof": "June 2026",
    "goal_short": "200M",
    "goal_long": "200 million",
    "goal_year": "2030",
}

# --- WDI indicators pulled for country context -------------------------------
# Chosen to line up with AgriConnect / Water-for-Food + the WBG Scorecard
# themes of food security and climate/agricultural resilience.
WDI_INDICATORS = {
    "SN.ITK.DEFC.ZS": "prevalence_undernourishment_pct",
    "AG.PRD.FOOD.XD": "food_production_index",
    "AG.LND.AGRI.ZS": "agricultural_land_pct",
    "SP.RUR.TOTL.ZS": "rural_population_pct",
    "SI.POV.DDAY": "poverty_headcount_215_pct",
    "NV.AGR.TOTL.ZS": "agriculture_value_added_pct_gdp",
}

# --- Regional aggregates that appear in the "Country" column ------------------
# These are multi-country operations, not sovereign states, so they are
# excluded from the WDI country join and flagged in the data-quality tests.
REGIONAL_AGGREGATES = {
    "Caribbean",
    "Eastern and Southern Africa",
    "Southern Africa",
    "Western and Central Africa",
}

# --- Country name -> ISO3 (alpha-3) ------------------------------------------
# Curated for exactly the names present in this dataset. Regional aggregates
# map to None on purpose.
NAME_TO_ISO3 = {
    "Afghanistan": "AFG", "Albania": "ALB", "Argentina": "ARG",
    "Bangladesh": "BGD", "Barbados": "BRB", "Belize": "BLZ", "Benin": "BEN",
    "Bhutan": "BTN", "Bolivia": "BOL", "Bosnia and Herzegovina": "BIH",
    "Brazil": "BRA", "Burkina Faso": "BFA", "Burundi": "BDI",
    "Cambodia": "KHM", "Cameroon": "CMR", "Central African Republic": "CAF",
    "Chad": "TCD", "China": "CHN", "Colombia": "COL",
    "Congo, Democratic Republic of": "COD", "Congo, Republic of": "COG",
    "Costa Rica": "CRI", "Cote d'Ivoire": "CIV", "Djibouti": "DJI",
    "Dominican Republic": "DOM", "El Salvador": "SLV", "Eswatini": "SWZ",
    "Ethiopia": "ETH", "Gambia, The": "GMB", "Georgia": "GEO", "Ghana": "GHA",
    "Guinea": "GIN", "Haiti": "HTI", "Honduras": "HND", "India": "IND",
    "Indonesia": "IDN", "Iraq": "IRQ", "Jamaica": "JAM", "Jordan": "JOR",
    "Kenya": "KEN", "Kyrgyz Republic": "KGZ",
    "Lao People's Democratic Republic": "LAO", "Lebanon": "LBN",
    "Lesotho": "LSO", "Liberia": "LBR", "Madagascar": "MDG", "Malawi": "MWI",
    "Mali": "MLI", "Mauritania": "MRT", "Mexico": "MEX",
    "Micronesia, Federated States of": "FSM", "Moldova": "MDA",
    "Mongolia": "MNG", "Montenegro": "MNE", "Morocco": "MAR",
    "Mozambique": "MOZ", "Myanmar": "MMR", "Nepal": "NPL", "Nicaragua": "NIC",
    "Niger": "NER", "Nigeria": "NGA", "North Macedonia": "MKD",
    "Pakistan": "PAK", "Panama": "PAN", "Papua New Guinea": "PNG",
    "Paraguay": "PRY", "Peru": "PER", "Philippines": "PHL", "Rwanda": "RWA",
    "Samoa": "WSM", "Senegal": "SEN", "Serbia": "SRB", "Sierra Leone": "SLE",
    "Solomon Islands": "SLB", "Somalia, Federal Republic of": "SOM",
    "South Sudan": "SSD", "Sri Lanka": "LKA", "Sudan": "SDN",
    "Tajikistan": "TJK", "Tanzania": "TZA", "Timor-Leste": "TLS",
    "Togo": "TGO", "Tonga": "TON", "Tunisia": "TUN", "Turkiye": "TUR",
    "Uganda": "UGA", "Ukraine": "UKR", "Uruguay": "URY", "Uzbekistan": "UZB",
    "Yemen, Republic of": "YEM", "Zambia": "ZMB",
    # regional aggregates -> None
    "Caribbean": None, "Eastern and Southern Africa": None,
    "Southern Africa": None, "Western and Central Africa": None,
}


def iso3(name: str):
    """Return ISO3 for a country name, or None for aggregates/unknowns."""
    return NAME_TO_ISO3.get(str(name).strip())
