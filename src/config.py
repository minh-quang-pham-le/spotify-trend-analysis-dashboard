"""Paths, constants, and dataset metadata.

Single source of truth for every magic value used by the pipeline. If a
threshold or column name lives here, code can change it once; if it lives
inline in a module, you'll chase grep results forever.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT_DIR: Path = Path(__file__).resolve().parents[1]

DATA_DIR: Path = ROOT_DIR / "data"
RAW_DIR: Path = DATA_DIR / "raw"
INTERIM_DIR: Path = DATA_DIR / "interim"
PROCESSED_DIR: Path = DATA_DIR / "processed"

REPORT_DIR: Path = ROOT_DIR / "report"
FIGURES_DIR: Path = REPORT_DIR / "figures"

POWERBI_DIR: Path = ROOT_DIR / "powerbi"

# ---------------------------------------------------------------------------
# Dataset metadata
# ---------------------------------------------------------------------------

# Primary Kaggle dataset (see SPEC.md §10 — final choice still pending).
# Override at runtime by setting env var SPOTIFY_DATASET_FILENAME or by passing
# an explicit path to src.ingest.load_raw().
PRIMARY_DATASET_FILENAME: str = "universal_top_spotify_songs.csv"

# ---------------------------------------------------------------------------
# Star-schema output filenames
# ---------------------------------------------------------------------------

FACT_TRACK_SNAPSHOT: str = "fact_track_snapshot.csv"
DIM_TRACK: str = "dim_track.csv"
DIM_ARTIST: str = "dim_artist.csv"
DIM_ALBUM: str = "dim_album.csv"
DIM_DATE: str = "dim_date.csv"
DIM_COUNTRY: str = "dim_country.csv"

# ---------------------------------------------------------------------------
# Column groupings
# ---------------------------------------------------------------------------

AUDIO_FEATURE_COLS: tuple[str, ...] = (
    "danceability",
    "energy",
    "valence",
    "tempo",
    "acousticness",
    "liveness",
    "speechiness",
    "instrumentalness",
    "loudness",
)

TRACK_METADATA_COLS: tuple[str, ...] = (
    "track_name",
    # The Asaniczka dataset has no ISRC (see A3 reconciliation below); the
    # Spotify track id is the stable per-recording identifier instead.
    "spotify_track_id",
    "explicit",
    "duration_ms",
)

# ---------------------------------------------------------------------------
# Schema reconciliation — real Asaniczka schema vs. SPEC.md §7 assumptions
# ---------------------------------------------------------------------------
# Discovered in notebooks/01_data_profile.ipynb (Task A3). SPEC §7 assumed
# ISRC-keyed, differently-named columns; the actual dataset diverges. The
# divergences flagged for the Gate-G1 team review are documented in
# powerbi/data_model.md. clean.py applies the rename below; canonical names are
# what the rest of the pipeline and data_model.md consume.

# Raw column -> canonical column. Only genuinely divergent names appear here;
# columns whose raw name already equals the canonical (popularity, duration_ms,
# album_name, snapshot_date, country, and every AUDIO_FEATURE_COL) pass through
# unchanged. `artists` is a comma-delimited list — clean.py derives the
# primary artist from the renamed `artist_names`.
RAW_TO_CANONICAL_COLUMNS: dict[str, str] = {
    "name": "track_name",
    "artists": "artist_names",
    "is_explicit": "explicit",
    "album_release_date": "release_date",
    "daily_rank": "rank",
    "spotify_id": "spotify_track_id",
}

# Canonical name of the stable identifier used as the basis for `track_key`
# (ISRC is absent, so we fall back to this; surrogate hash only if it is ever
# missing — it is 100% present and valid in the profiled snapshot).
PRIMARY_TRACK_ID_COLUMN: str = "spotify_track_id"

# Audio features the dataset carries but data_model.md / SPEC §7 do not model.
# Kept here so a later chart can opt in; not currently exported to Dim_Track.
EXTRA_AUDIO_FEATURE_COLS: tuple[str, ...] = ("key", "mode", "time_signature")

# Canonical fields SPEC §7 assumed would exist but the source does not provide.
ABSENT_EXPECTED_COLUMNS: tuple[str, ...] = ("isrc", "daily_streams", "primary_genre")

# A blank `country` marks Spotify's worldwide "Global" chart, not a nation.
# clean.py maps it to this sentinel so Dim_Country has a stable key for it.
GLOBAL_COUNTRY_KEY: str = "GLOBAL"

# ---------------------------------------------------------------------------
# I/O conventions
# ---------------------------------------------------------------------------

# Power BI on Windows reads UTF-8 BOM most reliably for non-ASCII text.
CSV_ENCODING: str = "utf-8-sig"
CSV_INDEX: bool = False

# ---------------------------------------------------------------------------
# Key strategy
# ---------------------------------------------------------------------------

# Truncate sha1 hashes to this many hex chars when constructing surrogate keys.
SURROGATE_KEY_LENGTH: int = 16
