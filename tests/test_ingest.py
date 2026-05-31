"""Unit tests for ``src.ingest`` (Task B1).

Ingest is a thin read: load the raw CSV, return it untouched. No type coercion,
no dedup, no renaming — those belong to ``clean.py``. Tests use the synthetic
``fixtures/mini_raw.csv`` only, so they run without the gitignored Kaggle file.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src import ingest

FIXTURE = Path(__file__).parent / "fixtures" / "mini_raw.csv"

# The real Asaniczka raw schema (see notebooks/01_data_profile.ipynb).
RAW_COLUMNS = [
    "spotify_id",
    "name",
    "artists",
    "daily_rank",
    "daily_movement",
    "weekly_movement",
    "country",
    "snapshot_date",
    "popularity",
    "is_explicit",
    "duration_ms",
    "album_name",
    "album_release_date",
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature",
]


def test_load_raw_returns_dataframe_with_expected_shape() -> None:
    df = ingest.load_raw(FIXTURE)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (10, 25)
    assert list(df.columns) == RAW_COLUMNS


def test_load_raw_does_not_dedup_or_coerce() -> None:
    # The exact-duplicate row (rows 8 and 9 in the fixture) must survive ingest;
    # deduplication is clean.py's responsibility, not ingest's.
    df = ingest.load_raw(FIXTURE)
    assert len(df) == 10


def test_load_raw_missing_file_raises_clear_filenotfound() -> None:
    missing = Path("definitely-not-a-real-dataset-7f3a.csv")
    with pytest.raises(FileNotFoundError) as exc:
        ingest.load_raw(missing)
    # The message should point the user at the missing path, not be a bare trace.
    assert "definitely-not-a-real-dataset-7f3a.csv" in str(exc.value)
