"""Unit tests for ``src.transform`` builders (Tasks B3-B8).

Each builder is exercised on the shared ``cleaned_df`` fixture (4 tracks, 3
artists, 4 albums, 2 dates, 3 country keys after dedup) plus targeted synthetic
frames via the ``make_cleaned`` factory.
"""

from __future__ import annotations

from src import transform
from src.config import AUDIO_FEATURE_COLS

# ---------------------------------------------------------------------------
# B3 — build_dim_track
# ---------------------------------------------------------------------------


def test_dim_track_one_row_per_track(cleaned_df) -> None:
    dim = transform.build_dim_track(cleaned_df)
    assert len(dim) == 4  # T1..T4 in the fixture
    assert dim["track_key"].is_unique
    assert dim["track_key"].notna().all()


def test_dim_track_has_required_columns(cleaned_df) -> None:
    dim = transform.build_dim_track(cleaned_df)
    required = {
        "track_key",
        "track_name",
        "spotify_track_id",
        "explicit",
        "duration_ms",
        *AUDIO_FEATURE_COLS,
    }
    assert required <= set(dim.columns)


def test_dim_track_key_equals_spotify_id_when_present(cleaned_df) -> None:
    dim = transform.build_dim_track(cleaned_df)
    assert (dim["track_key"] == dim["spotify_track_id"]).all()


def test_dim_track_falls_back_to_hash_when_id_missing(make_cleaned) -> None:
    cleaned = make_cleaned([{"spotify_id": None, "name": "NoId", "artists": "Ghost"}])
    dim = transform.build_dim_track(cleaned)
    key = dim["track_key"].iloc[0]
    assert isinstance(key, str)
    assert len(key) == 16  # sha1(name|artist)[:16]
    assert all(c in "0123456789abcdef" for c in key)


def test_dim_track_preserves_audio_feature_values(cleaned_df) -> None:
    dim = transform.build_dim_track(cleaned_df)
    t1 = dim.loc[dim["track_name"] == "Sunrise"].iloc[0]
    assert t1["danceability"] == 0.80
    assert t1["valence"] == 0.75
