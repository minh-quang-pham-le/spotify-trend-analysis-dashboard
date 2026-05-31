"""Contract tests for the schema reconciliation in ``src/config.py`` (Task A3).

These assert that the constants describing the real Asaniczka schema (discovered
in ``notebooks/01_data_profile.ipynb``) are present and internally consistent.
They use **no raw data** — they only inspect ``config`` — so they run on a fresh
clone without the gitignored CSV, per the ``conftest.py`` synthetic-only rule.
"""

from __future__ import annotations

from src import config


def test_rename_map_covers_known_divergences() -> None:
    m = config.RAW_TO_CANONICAL_COLUMNS
    assert m["name"] == "track_name"
    assert m["artists"] == "artist_names"
    assert m["is_explicit"] == "explicit"
    assert m["album_release_date"] == "release_date"
    assert m["daily_rank"] == "rank"
    assert m["spotify_id"] == config.PRIMARY_TRACK_ID_COLUMN


def test_rename_map_is_injective() -> None:
    # No two raw columns may collapse onto the same canonical name.
    values = list(config.RAW_TO_CANONICAL_COLUMNS.values())
    assert len(values) == len(set(values))


def test_rename_map_only_renames_divergent_columns() -> None:
    # Columns whose raw name already equals the canonical name (popularity,
    # duration_ms, audio features, ...) must NOT appear — they pass through.
    for raw, canonical in config.RAW_TO_CANONICAL_COLUMNS.items():
        assert raw != canonical, f"{raw} is a no-op rename; drop it from the map"


def test_primary_track_id_replaces_isrc_in_metadata() -> None:
    # The dataset has no ISRC; spotify_track_id is the stable key on Dim_Track.
    assert config.PRIMARY_TRACK_ID_COLUMN == "spotify_track_id"
    assert config.PRIMARY_TRACK_ID_COLUMN in config.TRACK_METADATA_COLS
    assert "isrc" not in config.TRACK_METADATA_COLS


def test_absent_expected_columns_recorded() -> None:
    assert set(config.ABSENT_EXPECTED_COLUMNS) == {"isrc", "daily_streams", "primary_genre"}


def test_extra_audio_features_disjoint_from_modeled() -> None:
    assert set(config.EXTRA_AUDIO_FEATURE_COLS) == {"key", "mode", "time_signature"}
    assert set(config.EXTRA_AUDIO_FEATURE_COLS).isdisjoint(config.AUDIO_FEATURE_COLS)


def test_global_country_key_defined() -> None:
    assert config.GLOBAL_COUNTRY_KEY == "GLOBAL"
