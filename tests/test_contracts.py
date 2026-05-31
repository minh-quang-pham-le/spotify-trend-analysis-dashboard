"""Contract / integration tests for ``src.validate`` (Task B9).

Builds the full star schema from the synthetic ``cleaned_df`` fixture and asserts
``validate_star_schema`` passes on good tables and fails (with a pointed error)
on each kind of contract violation.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src import config, transform, validate


def _tables(cleaned: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        config.FACT_TRACK_SNAPSHOT: transform.build_fact_track_snapshot(cleaned),
        config.DIM_TRACK: transform.build_dim_track(cleaned),
        config.DIM_ARTIST: transform.build_dim_artist(cleaned),
        config.DIM_ALBUM: transform.build_dim_album(cleaned),
        config.DIM_DATE: transform.build_dim_date(cleaned),
        config.DIM_COUNTRY: transform.build_dim_country(cleaned),
    }


@pytest.fixture
def good_tables(cleaned_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return _tables(cleaned_df)


@pytest.mark.contract
def test_valid_tables_pass(good_tables) -> None:
    report = validate.validate_star_schema(good_tables)
    assert report.passed, report.errors
    assert report.errors == ()


@pytest.mark.contract
def test_missing_table_fails(good_tables) -> None:
    t = dict(good_tables)
    del t[config.DIM_ARTIST]
    report = validate.validate_star_schema(t)
    assert not report.passed
    assert any(config.DIM_ARTIST in e for e in report.errors)


@pytest.mark.contract
def test_unresolved_foreign_key_fails(good_tables) -> None:
    t = dict(good_tables)
    fact = t[config.FACT_TRACK_SNAPSHOT].copy()
    fact.loc[fact.index[0], "track_key"] = "NONEXISTENT_KEY"
    t[config.FACT_TRACK_SNAPSHOT] = fact
    report = validate.validate_star_schema(t)
    assert not report.passed
    assert any("track_key" in e for e in report.errors)


@pytest.mark.contract
def test_duplicated_primary_key_fails(good_tables) -> None:
    t = dict(good_tables)
    dim = t[config.DIM_TRACK]
    t[config.DIM_TRACK] = pd.concat([dim, dim.iloc[[0]]], ignore_index=True)
    report = validate.validate_star_schema(t)
    assert not report.passed
    assert any("unique" in e.lower() for e in report.errors)


@pytest.mark.contract
def test_out_of_range_popularity_fails(good_tables) -> None:
    t = dict(good_tables)
    fact = t[config.FACT_TRACK_SNAPSHOT].copy()
    fact.loc[fact.index[0], "popularity"] = 200
    t[config.FACT_TRACK_SNAPSHOT] = fact
    report = validate.validate_star_schema(t)
    assert not report.passed
    assert any("popularity" in e for e in report.errors)


@pytest.mark.contract
def test_null_popularity_fails(good_tables) -> None:
    t = dict(good_tables)
    fact = t[config.FACT_TRACK_SNAPSHOT].copy()
    fact["popularity"] = fact["popularity"].astype("float")
    fact.loc[fact.index[0], "popularity"] = None
    t[config.FACT_TRACK_SNAPSHOT] = fact
    report = validate.validate_star_schema(t)
    assert not report.passed
    assert any("popularity" in e for e in report.errors)


@pytest.mark.contract
def test_audio_feature_out_of_range_fails(good_tables) -> None:
    t = dict(good_tables)
    dim = t[config.DIM_TRACK].copy()
    dim.loc[dim.index[0], "danceability"] = 1.5  # ratio must be in [0, 1]
    t[config.DIM_TRACK] = dim
    report = validate.validate_star_schema(t)
    assert not report.passed
    assert any("danceability" in e for e in report.errors)


@pytest.mark.contract
def test_non_contiguous_dim_date_fails(good_tables) -> None:
    t = dict(good_tables)
    # A 2-row frame spanning 3 days (10th and 12th, missing the 11th) is a gap.
    t[config.DIM_DATE] = pd.DataFrame(
        {
            "date_key": [20250610, 20250612],
            "date": [pd.Timestamp("2025-06-10").date(), pd.Timestamp("2025-06-12").date()],
            "year": [2025, 2025],
            "quarter": [2, 2],
            "month": [6, 6],
            "month_name": ["June", "June"],
            "day": [10, 12],
            "day_of_week": [2, 4],
            "day_name": ["Tuesday", "Thursday"],
            "week_of_year": [24, 24],
            "is_weekend": [False, False],
        }
    )
    report = validate.validate_star_schema(t)
    assert not report.passed
    assert any("contiguous" in e.lower() for e in report.errors)
