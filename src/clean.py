"""Clean the raw DataFrame.

Responsibilities (reconciled to the real Asaniczka schema — see
``powerbi/data_model.md`` Gate-G1 note):

    - Rename raw columns to canonical names (``config.RAW_TO_CANONICAL_COLUMNS``).
    - Derive ``primary_artist_name`` from the comma-delimited ``artist_names``.
    - Map ``country`` to ``country_key``: blank/NaN → ``GLOBAL`` sentinel,
      otherwise uppercased ISO-2 code.
    - Parse ``snapshot_date`` and ``release_date`` to datetime.
    - Drop exactly-duplicated rows.
    - Drop rows missing *both* essential identifiers (``track_name`` AND
      ``primary_artist_name``).

There is no ISRC in this dataset, so the "normalize ISRC" step from the original
SPEC is N/A; ``spotify_track_id`` is the stable identifier and is kept as-is
(whitespace-stripped). Cleaning never invents data — missing-but-recoverable
fields stay missing and get flagged in ``validate.py``.
"""

from __future__ import annotations

import pandas as pd

from src import config

# Explicit output column order — set so CSV exports and downstream selects don't
# drift (SPEC §5). Derived columns (primary_artist_name, country_key) sit next to
# their source columns; the extra audio columns (key/mode/time_signature) are
# retained but not modeled in Dim_Track.
CLEANED_COLUMNS: tuple[str, ...] = (
    "spotify_track_id",
    "track_name",
    "artist_names",
    "primary_artist_name",
    "album_name",
    "release_date",
    "snapshot_date",
    "country_key",
    "rank",
    "daily_movement",
    "weekly_movement",
    "popularity",
    "explicit",
    "duration_ms",
    *config.AUDIO_FEATURE_COLS,
    *config.EXTRA_AUDIO_FEATURE_COLS,
)


def _primary_artist(artist_names: object) -> object:
    """First artist in a comma-delimited list, stripped. NA if none."""
    if pd.isna(artist_names):
        return pd.NA
    first = str(artist_names).split(",")[0].strip()
    return first or pd.NA


def _country_key(country: object) -> str:
    """Uppercased ISO-2 code, or the GLOBAL sentinel for the blank worldwide chart."""
    if pd.isna(country) or not str(country).strip():
        return config.GLOBAL_COUNTRY_KEY
    return str(country).strip().upper()


def _is_blank(series: pd.Series) -> pd.Series:
    """True where a value is NaN or whitespace-only."""
    return series.isna() | (series.astype("string").str.strip() == "")


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of ``raw``.

    Pure function: the input frame is never mutated. The output schema
    (``CLEANED_COLUMNS``) is the internal contract consumed by
    ``transform.build_*``.
    """
    df = raw.rename(columns=config.RAW_TO_CANONICAL_COLUMNS).copy()

    df = df.assign(
        spotify_track_id=df["spotify_track_id"].astype("string").str.strip(),
        track_name=df["track_name"].astype("string").str.strip(),
        primary_artist_name=df["artist_names"].map(_primary_artist).astype("string"),
        country_key=df["country"].map(_country_key),
        release_date=pd.to_datetime(df["release_date"], errors="coerce"),
        snapshot_date=pd.to_datetime(df["snapshot_date"], errors="coerce"),
        # tempo=0 is Spotify's "undetectable" sentinel, not a real BPM — treat as
        # missing (tempo is nullable; keeps the SPEC §7 tempo>0 contract honest).
        tempo=df["tempo"].where(df["tempo"] > 0),
    )

    # Drop rows missing BOTH essential identifiers. (track_name alone or
    # primary_artist alone is enough to keep — never dedup on name alone.)
    both_missing = _is_blank(df["track_name"]) & _is_blank(df["primary_artist_name"])
    df = df.loc[~both_missing]

    # Drop exact duplicate rows across the canonical columns.
    df = df.loc[:, list(CLEANED_COLUMNS)].drop_duplicates().reset_index(drop=True)
    return df
