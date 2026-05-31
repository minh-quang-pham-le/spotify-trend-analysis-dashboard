"""Unit tests for ``src.clean`` (Task B2).

Each transformation in ``clean.clean`` gets a focused synthetic case. Most use
the shared ``raw_df`` fixture; edge cases (missing identifiers) build tiny
full-schema frames via ``_raw`` so a single field can be varied in isolation.
"""

from __future__ import annotations

import pandas as pd

from src import clean
from src.config import GLOBAL_COUNTRY_KEY

# A full-schema raw row with sensible defaults; override individual fields per
# test. Keeps the 25-column contract intact so clean() never KeyErrors.
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


def _raw(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame([{**RAW_ROW_DEFAULTS, **r} for r in rows])


def test_columns_renamed_to_canonical(cleaned_df: pd.DataFrame) -> None:
    cols = set(cleaned_df.columns)
    # Canonical names present...
    for canonical in ("track_name", "explicit", "release_date", "rank", "spotify_track_id"):
        assert canonical in cols
    # ...raw names gone.
    for raw in ("name", "is_explicit", "album_release_date", "daily_rank", "spotify_id"):
        assert raw not in cols


def test_primary_artist_extracted_from_comma_list(cleaned_df: pd.DataFrame) -> None:
    # "Beat Crew, Aurora Skye" -> primary artist is "Beat Crew".
    multi = cleaned_df.loc[cleaned_df["track_name"] == "Midnight", "primary_artist_name"]
    assert (multi == "Beat Crew").all()
    # Single-artist track keeps the whole string.
    solo = cleaned_df.loc[cleaned_df["track_name"] == "Sunrise", "primary_artist_name"]
    assert (solo == "Aurora Skye").all()


def test_country_blank_maps_to_global_sentinel(cleaned_df: pd.DataFrame) -> None:
    assert "country" not in cleaned_df.columns
    assert "country_key" in cleaned_df.columns
    # The two blank-country fixture rows become the GLOBAL sentinel.
    assert (cleaned_df["country_key"] == GLOBAL_COUNTRY_KEY).sum() == 2
    # Real country codes are uppercased.
    assert set(cleaned_df["country_key"]) == {"US", "GB", GLOBAL_COUNTRY_KEY}


def test_country_code_uppercased() -> None:
    out = clean.clean(_raw([{"country": "us"}, {"country": " gb "}]))
    assert set(out["country_key"]) == {"US", "GB"}


def test_dates_parsed_to_datetime(cleaned_df: pd.DataFrame) -> None:
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["snapshot_date"])
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["release_date"])


def test_exact_duplicate_rows_dropped(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> None:
    # Fixture has 10 raw rows including one exact duplicate -> 9 after clean.
    assert len(raw_df) == 10
    assert len(cleaned_df) == 9
    assert not cleaned_df.duplicated().any()


def test_rows_missing_both_track_name_and_primary_artist_dropped() -> None:
    raw = _raw(
        [
            {"name": "Keep Me", "artists": "Someone"},  # keep
            {"name": None, "artists": None},  # both missing -> drop
            {"name": "  ", "artists": "  "},  # blank/whitespace -> drop
            {"name": None, "artists": "Solo"},  # has artist -> keep
            {"name": "Title", "artists": None},  # has name -> keep
        ]
    )
    out = clean.clean(raw)
    assert len(out) == 3
    assert set(out["track_name"].fillna("∅")) >= {"Keep Me", "Title"}


def test_types_coerced(cleaned_df: pd.DataFrame) -> None:
    assert pd.api.types.is_integer_dtype(cleaned_df["popularity"])
    assert pd.api.types.is_bool_dtype(cleaned_df["explicit"])
    assert pd.api.types.is_integer_dtype(cleaned_df["rank"])


def test_clean_is_pure_does_not_mutate_input(raw_df: pd.DataFrame) -> None:
    before = raw_df.copy(deep=True)
    clean.clean(raw_df)
    pd.testing.assert_frame_equal(raw_df, before)


def test_spotify_track_id_preserved(cleaned_df: pd.DataFrame) -> None:
    # The 22-char id survives unchanged (it is the basis for track_key).
    ids = set(cleaned_df["spotify_track_id"])
    assert "0aBcDeFgHiJkLmNoPqRsT1" in ids
    assert all(len(i) == 22 for i in ids)
