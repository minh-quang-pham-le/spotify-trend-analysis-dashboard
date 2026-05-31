"""Build the star-schema fact and dimension tables.

Given a cleaned DataFrame (the ``clean.CLEANED_COLUMNS`` contract), ``transform``
emits:

* ``Fact_TrackSnapshot`` — grain: (track, country, snapshot_date).
  Carries measures: popularity, rank (daily_streams is absent in this source).
* ``Dim_Track``    — one row per track. Carries audio features.
* ``Dim_Artist``   — one row per (canonicalized primary) artist.
* ``Dim_Album``    — one row per (canonicalized album name, release_date).
* ``Dim_Date``     — one row per calendar date in the fact's snapshot range.
* ``Dim_Country``  — one row per country key (incl. the GLOBAL sentinel).

Surrogate keys are built once by ``add_keys`` and reused by every builder, so a
foreign key in the fact is guaranteed to match its dimension's primary key. See
``SPEC.md §7`` and ``powerbi/data_model.md`` for the binding schema.
"""

from __future__ import annotations

import hashlib
import unicodedata

import pandas as pd

from src import config

# ---------------------------------------------------------------------------
# Surrogate-key construction (single source of truth for dims + fact)
# ---------------------------------------------------------------------------


def _sha1_16(text: str) -> str:
    """Stable truncated sha1 hex digest (``SURROGATE_KEY_LENGTH`` chars)."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[: config.SURROGATE_KEY_LENGTH]


def _canonicalize(name: object) -> str:
    """Lowercase, strip accents, collapse internal whitespace. NaN → ''."""
    if pd.isna(name):
        return ""
    decomposed = unicodedata.normalize("NFKD", str(name))
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(stripped.lower().split())


def _hash_unique(values: pd.Series) -> pd.Series:
    """Map a string series to truncated-sha1 keys, hashing each unique value once."""
    mapping = {v: _sha1_16(v) for v in values.unique()}
    return values.map(mapping)


def add_keys(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Return ``cleaned`` with track/artist/album/date surrogate keys added.

    Idempotent: if ``track_key`` is already present the frame is returned as-is,
    so the pipeline can key the frame once and hand it to every builder.
    """
    if "track_key" in cleaned.columns:
        return cleaned
    df = cleaned.copy()

    # track_key = spotify_track_id when present, else sha1(track_name|artist)[:16].
    sid = df["spotify_track_id"].astype("string")
    has_id = sid.notna() & (sid.str.strip() != "")
    surrogate = (
        df["track_name"].fillna("").astype(str) + "|" + df["primary_artist_name"].fillna("").astype(str)
    ).map(_sha1_16)
    df["track_key"] = sid.where(has_id, pd.Series(surrogate, index=df.index)).astype("string")

    # artist_key / album_key = sha1 of canonicalized name(s).
    df["artist_key"] = _hash_unique(df["primary_artist_name"].map(_canonicalize))
    release_iso = df["release_date"].dt.strftime("%Y-%m-%d").fillna("")
    df["album_key"] = _hash_unique(df["album_name"].map(_canonicalize) + "|" + release_iso)

    # date_key = YYYYMMDD integer (Power BI convention).
    df["date_key"] = pd.to_numeric(
        df["snapshot_date"].dt.strftime("%Y%m%d"), errors="coerce"
    ).astype("Int64")

    return df


# ---------------------------------------------------------------------------
# Dimension builders
# ---------------------------------------------------------------------------

_DIM_TRACK_COLS = (
    "track_key",
    "track_name",
    "spotify_track_id",
    "explicit",
    "duration_ms",
    *config.AUDIO_FEATURE_COLS,
)


def build_dim_track(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Collapse to one row per track. Audio features (static per recording) live here."""
    df = add_keys(cleaned)
    dim = (
        df.sort_values("snapshot_date")
        .drop_duplicates(subset="track_key", keep="first")
        .loc[:, list(_DIM_TRACK_COLS)]
        .reset_index(drop=True)
    )
    assert dim["track_key"].is_unique, "track_key must be unique in Dim_Track"
    return dim


def build_dim_artist(cleaned: pd.DataFrame) -> pd.DataFrame:
    """One row per artist (canonicalized primary-artist name → stable surrogate key).

    Display name is the first-seen casing for each key. ``primary_genre`` is
    absent in the source (Gate-G1) so it is an all-null column.
    """
    df = add_keys(cleaned)
    dim = (
        df.loc[:, ["artist_key", "primary_artist_name"]]
        .drop_duplicates(subset="artist_key", keep="first")
        .rename(columns={"primary_artist_name": "artist_name"})
        .reset_index(drop=True)
    )
    dim["primary_genre"] = pd.NA
    dim = dim.loc[:, ["artist_key", "artist_name", "primary_genre"]]
    assert dim["artist_key"].is_unique, "artist_key must be unique in Dim_Artist"
    return dim


def build_dim_album(cleaned: pd.DataFrame) -> pd.DataFrame:
    """One row per album, keyed on (canonicalized name, release_date).

    Same-name albums with different release dates are distinct rows. ``release_date``
    is stored as a plain date (no time component) for a clean Power BI import.
    ``total_tracks`` is absent in the source -> all-null column.
    """
    df = add_keys(cleaned)
    dim = (
        df.loc[:, ["album_key", "album_name", "release_date"]]
        .drop_duplicates(subset="album_key", keep="first")
        .reset_index(drop=True)
    )
    dim["release_date"] = dim["release_date"].dt.date
    dim["total_tracks"] = pd.NA
    dim = dim.loc[:, ["album_key", "album_name", "release_date", "total_tracks"]]
    assert dim["album_key"].is_unique, "album_key must be unique in Dim_Album"
    return dim


_DIM_DATE_COLS = (
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
)


def build_dim_date(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Contiguous calendar dimension spanning [min, max] of the snapshot dates.

    Every day in the range gets a row (no gaps), so Power BI time-intelligence
    works. ``day_of_week`` is Monday=1..Sunday=7; ``is_weekend`` is Sat/Sun.
    """
    dates = pd.to_datetime(cleaned["snapshot_date"]).dropna()
    if dates.empty:
        return pd.DataFrame(columns=list(_DIM_DATE_COLS))

    full = pd.date_range(dates.min().normalize(), dates.max().normalize(), freq="D")
    dim = pd.DataFrame(
        {
            "date_key": full.strftime("%Y%m%d").astype(int),
            "date": full.date,
            "year": full.year,
            "quarter": full.quarter,
            "month": full.month,
            "month_name": full.month_name(),
            "day": full.day,
            "day_of_week": full.dayofweek + 1,  # Monday = 1
            "day_name": full.day_name(),
            "week_of_year": full.isocalendar().week.astype(int).to_numpy(),
            "is_weekend": full.dayofweek >= 5,  # Sat=5, Sun=6 (0-based)
        }
    )
    return dim.loc[:, list(_DIM_DATE_COLS)].reset_index(drop=True)


def build_dim_country(cleaned: pd.DataFrame) -> pd.DataFrame:
    """One row per country key present (incl. the GLOBAL sentinel).

    Display name and region come from ``config.COUNTRY_LOOKUP``; codes not in the
    table degrade to (code, ``UNKNOWN_REGION``) so a growing dataset never breaks
    the build.
    """
    keys = sorted(cleaned["country_key"].dropna().unique())
    dim = pd.DataFrame(
        [
            {
                "country_key": k,
                "country_name": config.COUNTRY_LOOKUP.get(k, (k, config.UNKNOWN_REGION))[0],
                "region": config.COUNTRY_LOOKUP.get(k, (k, config.UNKNOWN_REGION))[1],
            }
            for k in keys
        ],
        columns=["country_key", "country_name", "region"],
    )
    assert dim["country_key"].is_unique, "country_key must be unique in Dim_Country"
    return dim


_FACT_COLS = (
    "track_key",
    "artist_key",
    "album_key",
    "date_key",
    "country_key",
    "popularity",
    "rank",
    "daily_streams",
)


def build_fact_track_snapshot(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Build the fact table at the (track, country, snapshot_date) grain.

    Foreign keys are the surrogate keys from ``add_keys``, so they resolve into
    the dimensions by construction. ``daily_streams`` is absent in the source
    (Gate-G1) and kept as an all-null column. Any duplicate grain tuple collapses
    to its first occurrence so the grain is exact.
    """
    df = add_keys(cleaned)
    fact = df.loc[
        :,
        ["track_key", "artist_key", "album_key", "date_key", "country_key", "popularity", "rank"],
    ].copy()
    fact["daily_streams"] = pd.NA
    fact = (
        fact.drop_duplicates(subset=["track_key", "country_key", "date_key"], keep="first")
        .loc[:, list(_FACT_COLS)]
        .reset_index(drop=True)
    )
    return fact
