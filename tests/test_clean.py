"""Unit tests for ``src.clean`` (Task B2).

Each transformation in ``clean.clean`` gets a focused synthetic case. Most use
the shared ``raw_df`` fixture; edge cases (missing identifiers) build tiny
full-schema frames via ``_raw`` so a single field can be varied in isolation.
"""

from __future__ import annotations

import pandas as pd

from src import clean
from src.config import GLOBAL_COUNTRY_KEY


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


def test_country_code_uppercased(make_raw) -> None:
    out = clean.clean(make_raw([{"country": "us"}, {"country": " gb "}]))
    assert set(out["country_key"]) == {"US", "GB"}


def test_dates_parsed_to_datetime(cleaned_df: pd.DataFrame) -> None:
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["snapshot_date"])
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["release_date"])


def test_exact_duplicate_rows_dropped(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> None:
    # Fixture has 10 raw rows including one exact duplicate -> 9 after clean.
    assert len(raw_df) == 10
    assert len(cleaned_df) == 9
    assert not cleaned_df.duplicated().any()


def test_rows_missing_both_track_name_and_primary_artist_dropped(make_raw) -> None:
    raw = make_raw(
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


def test_nonpositive_tempo_coerced_to_nan(make_cleaned) -> None:
    # Spotify emits tempo=0 when tempo can't be detected; that is not a real BPM,
    # so it becomes NaN (tempo is nullable in data_model.md). Positives survive.
    out = make_cleaned([{"tempo": 0.0}, {"tempo": 120.0}, {"tempo": -5.0}])
    assert out["tempo"].notna().sum() == 1
    assert (out["tempo"].dropna() == 120.0).all()


def test_spotify_track_id_preserved(cleaned_df: pd.DataFrame) -> None:
    # The 22-char id survives unchanged (it is the basis for track_key).
    ids = set(cleaned_df["spotify_track_id"])
    assert "0aBcDeFgHiJkLmNoPqRsT1" in ids
    assert all(len(i) == 22 for i in ids)
