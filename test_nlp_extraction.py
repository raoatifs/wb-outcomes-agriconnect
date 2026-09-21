"""Tests for the rule-based extractor and the evaluation harness."""
from src.extract_nlp import rule_extract, evaluate

SAMPLE = """
Project Development Objective: to increase agricultural productivity and
climate resilience of smallholder farmers in the project area. The project is
expected to reach 250000 direct beneficiaries.

Results Indicator: Farmers reached with agricultural assets or services.
Baseline: 0
End Target: 250000
Actual: 180000

The operation promotes climate-smart agriculture, irrigation, and drought
adaptation across the value chain.
"""


def test_extracts_numeric_fields():
    ex = rule_extract(SAMPLE)
    assert ex.baseline == 0
    assert ex.target == 250000
    assert ex.actual == 180000
    assert ex.beneficiaries == 250000


def test_detects_themes():
    ex = rule_extract(SAMPLE)
    assert ex.climate_theme is True
    assert ex.agriculture_theme is True
    assert "irrigation" in ex.matched_terms


def test_captures_objective():
    ex = rule_extract(SAMPLE)
    assert ex.development_objective is not None
    assert "productivity" in ex.development_objective.lower()


def test_evaluate_scores_against_truth():
    ex = rule_extract(SAMPLE).as_dict()
    truth = {"baseline": 0, "target": 250000, "actual": 180000,
             "beneficiaries": 250000}
    scored = evaluate(ex, truth)
    assert scored["_accuracy"] == 1.0
    assert scored["_n_scored"] == 4


def test_evaluate_flags_mismatch():
    scored = evaluate({"actual": 999}, {"actual": 180000})
    assert scored["actual"]["match"] is False
