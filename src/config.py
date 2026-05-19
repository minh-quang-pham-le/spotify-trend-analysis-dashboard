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
    "isrc",
    "explicit",
    "duration_ms",
)

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
