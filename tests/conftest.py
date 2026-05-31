"""Pytest fixtures.

All fixtures use synthetic data only — tests must work without the raw Kaggle
dataset being present. ``mini_raw.csv`` is a hand-authored 10-row frame with the
real Asaniczka schema (see ``tests/test_ingest.py`` for the column list).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src import clean, ingest

FIXTURE = Path(__file__).parent / "fixtures" / "mini_raw.csv"


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """The synthetic raw frame, loaded exactly as ``ingest`` would load it."""
    return ingest.load_raw(FIXTURE)


@pytest.fixture
def cleaned_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """The synthetic frame after ``clean.clean`` — the internal pipeline contract
    consumed by the ``transform.build_*`` builders."""
    return clean.clean(raw_df)
