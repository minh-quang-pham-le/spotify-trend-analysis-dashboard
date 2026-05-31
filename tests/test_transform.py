"""Unit tests for ``src.transform`` builders (Tasks B3-B8).

Each builder is exercised on the shared ``cleaned_df`` fixture (4 tracks, 3
artists, 4 albums, 2 dates, 3 country keys after dedup) plus targeted synthetic
frames via the ``make_cleaned`` factory.
"""

from __future__ import annotations

from src import config, transform
from src.config import AUDIO_FEATURE_COLS, GLOBAL_COUNTRY_KEY

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


# ---------------------------------------------------------------------------
# B4 — build_dim_artist
# ---------------------------------------------------------------------------


def test_dim_artist_one_row_per_artist(cleaned_df) -> None:
    dim = transform.build_dim_artist(cleaned_df)
    # "Aurora Skye" and "aurora skye" collapse -> 3 distinct artists.
    assert len(dim) == 3
    assert dim["artist_key"].is_unique
    assert dim["artist_key"].notna().all()


def test_dim_artist_has_contract_columns(cleaned_df) -> None:
    dim = transform.build_dim_artist(cleaned_df)
    assert list(dim.columns) == ["artist_key", "artist_name", "primary_genre"]
    # Genre is absent in the source (Gate-G1) -> column exists but is all-null.
    assert dim["primary_genre"].isna().all()


def test_dim_artist_collapses_case_and_accents(make_cleaned) -> None:
    cleaned = make_cleaned(
        [
            {"spotify_id": "id1aaaaaaaaaaaaaaaaaa1", "name": "A", "artists": "Beyoncé"},
            {"spotify_id": "id2aaaaaaaaaaaaaaaaaa2", "name": "B", "artists": "BEYONCE"},
        ]
    )
    dim = transform.build_dim_artist(cleaned)
    assert len(dim) == 1  # "Beyoncé" and "BEYONCE" canonicalize to the same key


def test_dim_artist_keeps_first_seen_display_name(cleaned_df) -> None:
    dim = transform.build_dim_artist(cleaned_df)
    names = set(dim["artist_name"])
    assert "Aurora Skye" in names  # first-seen casing preserved
    assert "aurora skye" not in names


# ---------------------------------------------------------------------------
# B5 — build_dim_album
# ---------------------------------------------------------------------------


def test_dim_album_one_row_per_album(cleaned_df) -> None:
    dim = transform.build_dim_album(cleaned_df)
    assert len(dim) == 4  # Dawn, Night, Fiesta, Reverb
    assert dim["album_key"].is_unique
    assert dim["album_key"].notna().all()


def test_dim_album_has_contract_columns(cleaned_df) -> None:
    dim = transform.build_dim_album(cleaned_df)
    assert list(dim.columns) == ["album_key", "album_name", "release_date", "total_tracks"]
    # total_tracks is not provided by the source -> all-null column.
    assert dim["total_tracks"].isna().all()


def test_dim_album_separates_same_name_different_release_date(make_cleaned) -> None:
    cleaned = make_cleaned(
        [
            {
                "spotify_id": "alb1aaaaaaaaaaaaaaaaa1",
                "name": "x",
                "artists": "a",
                "album_name": "Greatest Hits",
                "album_release_date": "2010-01-01",
            },
            {
                "spotify_id": "alb2aaaaaaaaaaaaaaaaa2",
                "name": "y",
                "artists": "b",
                "album_name": "Greatest Hits",
                "album_release_date": "2020-01-01",
            },
        ]
    )
    dim = transform.build_dim_album(cleaned)
    assert len(dim) == 2  # same name, different release dates -> two albums


def test_dim_album_release_date_value(cleaned_df) -> None:
    dim = transform.build_dim_album(cleaned_df)
    dawn = dim.loc[dim["album_name"] == "Dawn", "release_date"].iloc[0]
    assert str(dawn) == "2024-01-15"


# ---------------------------------------------------------------------------
# B6 — build_dim_date
# ---------------------------------------------------------------------------

DIM_DATE_COLUMNS = [
    "date_key",
    "date",
    "year",
    "quarter",
    "month",
    "month_name",
    "day",
    "day_of_week",
    "day_name",
    "week_of_year",
    "is_weekend",
]


def test_dim_date_contract_columns_and_count(cleaned_df) -> None:
    dim = transform.build_dim_date(cleaned_df)
    assert list(dim.columns) == DIM_DATE_COLUMNS
    assert len(dim) == 2  # 2025-06-10 and 2025-06-11
    assert dim["date_key"].is_unique


def test_dim_date_is_contiguous_filling_gaps(make_cleaned) -> None:
    cleaned = make_cleaned(
        [
            {"snapshot_date": "2025-06-10"},
            {"snapshot_date": "2025-06-13"},
        ]
    )
    dim = transform.build_dim_date(cleaned)
    # No missing days inside [min, max]: 10, 11, 12, 13.
    assert len(dim) == 4
    assert list(dim["date_key"]) == [20250610, 20250611, 20250612, 20250613]


def test_dim_date_key_is_yyyymmdd_int(cleaned_df) -> None:
    dim = transform.build_dim_date(cleaned_df)
    assert dim.loc[dim["date_key"] == 20250610].shape[0] == 1
    assert dim["date_key"].dtype.kind == "i"


def test_dim_date_weekend_matches_day_of_week(make_cleaned) -> None:
    # Span a full week so both weekdays and weekend days appear.
    cleaned = make_cleaned([{"snapshot_date": "2025-06-02"}, {"snapshot_date": "2025-06-08"}])
    dim = transform.build_dim_date(cleaned)
    assert dim["day_of_week"].between(1, 7).all()  # Monday = 1
    assert (dim["is_weekend"] == (dim["day_of_week"] >= 6)).all()
    # 2025-06-07 (Sat) and 2025-06-08 (Sun) are the weekend in this span.
    assert dim["is_weekend"].sum() == 2


# ---------------------------------------------------------------------------
# B7 — build_dim_country
# ---------------------------------------------------------------------------


def test_dim_country_one_row_per_country_key(cleaned_df) -> None:
    dim = transform.build_dim_country(cleaned_df)
    assert list(dim.columns) == ["country_key", "country_name", "region"]
    assert set(dim["country_key"]) == {"US", "GB", GLOBAL_COUNTRY_KEY}
    assert dim["country_key"].is_unique


def test_dim_country_region_mapping(cleaned_df) -> None:
    dim = transform.build_dim_country(cleaned_df).set_index("country_key")
    assert dim.loc["US", "region"] == "Americas"
    assert dim.loc["US", "country_name"] == "United States"
    assert dim.loc["GB", "region"] == "Europe"
    assert dim.loc[GLOBAL_COUNTRY_KEY, "region"] == "Global"
    assert dim.loc[GLOBAL_COUNTRY_KEY, "country_name"] == "Global"


def test_dim_country_unknown_code_degrades_gracefully(make_cleaned) -> None:
    cleaned = make_cleaned([{"country": "ZZ"}])  # not a real ISO-2 code
    dim = transform.build_dim_country(cleaned).set_index("country_key")
    assert dim.loc["ZZ", "region"] == config.UNKNOWN_REGION
    assert dim.loc["ZZ", "country_name"] == "ZZ"
