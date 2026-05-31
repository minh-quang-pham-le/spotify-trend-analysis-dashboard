"""Pytest fixtures and synthetic-data factories.

All fixtures use synthetic data only — tests must work without the raw Kaggle
dataset being present. ``mini_raw.csv`` is a hand-authored 10-row frame with the
real Asaniczka schema (see ``tests/test_ingest.py`` for the column list); the
``make_raw`` / ``make_cleaned`` factories build tiny full-schema frames so a
single field can be varied in isolation.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd
import pytest

from src import clean, ingest

FIXTURE = Path(__file__).parent / "fixtures" / "mini_raw.csv"

# A full-schema raw row with sensible defaults; tests override individual fields.
# Keeping the 25-column contract intact means clean()/transform never KeyError.
RAW_ROW_DEFAULTS: dict[str, object] = {
    "spotify_id": "0aBcDeFgHiJkLmNoPqRsZ9",
    "name": "Default Track",
    "artists": "Default Artist",
    "daily_rank": 1,
    "daily_movement": 0,
    "weekly_movement": 0,
    "country": "US",
    "snapshot_date": "2025-06-11",
    "popularity": 50,
    "is_explicit": False,
    "duration_ms": 200000,
    "album_name": "Default Album",
    "album_release_date": "2024-01-01",
    "danceability": 0.5,
    "energy": 0.5,
    "key": 1,
    "loudness": -5.0,
    "mode": 1,
    "speechiness": 0.05,
    "acousticness": 0.1,
    "instrumentalness": 0.0,
    "liveness": 0.1,
    "valence": 0.5,
    "tempo": 120.0,
    "time_signature": 4,
}


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """The synthetic raw frame, loaded exactly as ``ingest`` would load it."""
    return ingest.load_raw(FIXTURE)


@pytest.fixture
def cleaned_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """The synthetic frame after ``clean.clean`` — the internal pipeline contract
    consumed by the ``transform.build_*`` builders."""
    return clean.clean(raw_df)


@pytest.fixture
def make_raw() -> Callable[[list[dict[str, object]]], pd.DataFrame]:
    """Factory: build a full-schema raw frame from a list of field-override dicts."""

    def _make(rows: list[dict[str, object]]) -> pd.DataFrame:
        return pd.DataFrame([{**RAW_ROW_DEFAULTS, **r} for r in rows])

    return _make


@pytest.fixture
def make_cleaned(
    make_raw: Callable[[list[dict[str, object]]], pd.DataFrame],
) -> Callable[[list[dict[str, object]]], pd.DataFrame]:
    """Factory: build a cleaned frame from a list of field-override dicts."""

    def _make(rows: list[dict[str, object]]) -> pd.DataFrame:
        return clean.clean(make_raw(rows))

    return _make
