"""Build the star-schema fact and dimension tables.

Given a cleaned DataFrame, ``transform`` emits:

* ``Fact_TrackSnapshot`` — grain: (track, country, snapshot_date).
  Carries measures: popularity, rank, daily_streams.
* ``Dim_Track``    — one row per track. Carries audio features and ISRC.
* ``Dim_Artist``   — one row per artist.
* ``Dim_Album``    — one row per album.
* ``Dim_Date``     — one row per calendar date present in the fact.
* ``Dim_Country``  — one row per country (only when multi-country data is used).

See ``SPEC.md §7`` for the binding schema and key strategy.

Implementation lands during the Implement phase — see SPEC.md.
"""

from __future__ import annotations

import pandas as pd


def build_dim_track(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Collapse to one row per track. Audio features and ISRC live here."""
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")


def build_dim_artist(cleaned: pd.DataFrame) -> pd.DataFrame:
    """One row per artist (canonicalized name → stable surrogate key)."""
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")


def build_dim_album(cleaned: pd.DataFrame) -> pd.DataFrame:
    """One row per album (canonicalized name x release_date -> key)."""
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")


def build_dim_date(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Calendar dimension covering every date present in the fact table."""
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")


def build_dim_country(cleaned: pd.DataFrame) -> pd.DataFrame:
    """One row per ISO 3166-1 alpha-2 country code."""
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")


def build_fact_track_snapshot(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Build the fact table at the (track, country, date) grain."""
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")
