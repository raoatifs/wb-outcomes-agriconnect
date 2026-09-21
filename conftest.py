"""Shared fixtures: build the cleaned AgriConnect frame once per test session."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import ingest_agriconnect  # noqa: E402


@pytest.fixture(scope="session")
def projects():
    return ingest_agriconnect.clean(ingest_agriconnect.load_raw())
