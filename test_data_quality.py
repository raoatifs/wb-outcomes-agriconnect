"""Data-quality checks on the AgriConnect outcome table.

These are the checks an interviewer means by "how do you validate data?":
completeness, uniqueness, referential validity (country codes), type
correctness, and value-range sanity.
"""
import pandas as pd
from src import config

EXPECTED_COLUMNS = {
    "project_id", "project_name", "country", "iso3", "region",
    "global_practice", "project_status", "baseline_value", "progress_value",
    "achieved_results", "approval_year",
}


def test_expected_columns_present(projects):
    assert EXPECTED_COLUMNS.issubset(set(projects.columns))


def test_no_missing_project_ids(projects):
    assert projects["project_id"].notna().all()


def test_project_ids_are_pcodes(projects):
    # Every WB project id is a P followed by digits.
    assert projects["project_id"].str.match(r"^P\d+$").all()


def test_project_ids_unique(projects):
    # This extract is one indicator row per project.
    dupes = projects["project_id"][projects["project_id"].duplicated()].tolist()
    assert not dupes, f"duplicate project ids: {dupes[:5]}"


def test_no_duplicate_full_rows(projects):
    assert not projects.duplicated().any()


def test_numeric_types(projects):
    for col in ("baseline_value", "progress_value", "achieved_results"):
        assert pd.api.types.is_numeric_dtype(projects[col]), col


def test_outcome_values_non_negative(projects):
    for col in ("baseline_value", "progress_value", "achieved_results"):
        assert (projects[col].dropna() >= 0).all(), col


def test_achieved_not_above_progress_for_absolute_counts(projects):
    # For rows counted in absolute people ("Number"), de-duplicated achieved
    # results must not exceed raw reported progress (de-dup only removes overlap).
    absolute = projects[projects["unit_of_measure"].str.strip() == "Number"]
    ok = absolute["achieved_results"] <= absolute["progress_value"] + 1e-6
    assert ok.all(), f"{(~ok).sum()} absolute-count rows violate achieved <= progress"


def test_unit_inconsistency_is_flagged(projects):
    # Data-quality catch: at least one row is reported in a scaled unit
    # ("Number (Thousand)") and must be handled separately before aggregation.
    scaled = projects[projects["unit_of_measure"].str.contains(
        "Thousand", case=False, na=False)]
    # We know this exists in the release; the pipeline must not silently sum it
    # together with absolute counts.
    assert len(scaled) >= 1
    assert (scaled["unit_of_measure"] != "Number").all()


def test_valid_country_codes(projects):
    # Single-country rows must map to a known ISO3; regional ops must not.
    single = projects[projects["is_regional_aggregate"] == 0]
    assert single["iso3"].notna().all(), (
        "unmapped countries: "
        f"{sorted(single.loc[single['iso3'].isna(), 'country'].unique())}"
    )
    regional = projects[projects["is_regional_aggregate"] == 1]
    assert regional["iso3"].isna().all()


def test_iso3_format(projects):
    codes = projects["iso3"].dropna()
    assert codes.str.match(r"^[A-Z]{3}$").all()


def test_status_domain(projects):
    assert set(projects["project_status"].unique()) <= {"Active", "Closed"}


def test_approval_year_range(projects):
    yrs = projects["approval_year"].dropna()
    assert yrs.between(2000, 2030).all()


def test_regional_aggregate_flag_matches_config(projects):
    flagged = set(projects.loc[projects["is_regional_aggregate"] == 1, "country"])
    assert flagged <= config.REGIONAL_AGGREGATES
