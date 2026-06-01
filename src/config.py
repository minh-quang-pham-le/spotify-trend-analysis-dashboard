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

# Derived analytical table (NOT part of the star schema): the audio-feature
# Pearson correlation matrix in long form, consumed by the Audio Anatomy heatmap
# (task D5). Exported alongside the star CSVs but not FK-validated.
CORR_AUDIO_FEATURES: str = "corr_audio_features.csv"

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
# Country dimension lookup
# ---------------------------------------------------------------------------
# ISO 3166-1 alpha-2 -> (English display name, region). Covers exactly the 72
# country codes present in the profiled snapshot plus the GLOBAL sentinel.
# Regions use the coarse set agreed in data_model.md: Americas / Europe / Asia /
# Africa / Oceania / Global. The dataset grows daily, so build_dim_country
# degrades gracefully for any future code not listed here (see UNKNOWN_REGION).
COUNTRY_LOOKUP: dict[str, tuple[str, str]] = {
    GLOBAL_COUNTRY_KEY: ("Global", "Global"),
    "AE": ("United Arab Emirates", "Asia"),
    "AR": ("Argentina", "Americas"),
    "AT": ("Austria", "Europe"),
    "AU": ("Australia", "Oceania"),
    "BE": ("Belgium", "Europe"),
    "BG": ("Bulgaria", "Europe"),
    "BO": ("Bolivia", "Americas"),
    "BR": ("Brazil", "Americas"),
    "BY": ("Belarus", "Europe"),
    "CA": ("Canada", "Americas"),
    "CH": ("Switzerland", "Europe"),
    "CL": ("Chile", "Americas"),
    "CO": ("Colombia", "Americas"),
    "CR": ("Costa Rica", "Americas"),
    "CZ": ("Czechia", "Europe"),
    "DE": ("Germany", "Europe"),
    "DK": ("Denmark", "Europe"),
    "DO": ("Dominican Republic", "Americas"),
    "EC": ("Ecuador", "Americas"),
    "EE": ("Estonia", "Europe"),
    "EG": ("Egypt", "Africa"),
    "ES": ("Spain", "Europe"),
    "FI": ("Finland", "Europe"),
    "FR": ("France", "Europe"),
    "GB": ("United Kingdom", "Europe"),
    "GR": ("Greece", "Europe"),
    "GT": ("Guatemala", "Americas"),
    "HK": ("Hong Kong", "Asia"),
    "HN": ("Honduras", "Americas"),
    "HU": ("Hungary", "Europe"),
    "ID": ("Indonesia", "Asia"),
    "IE": ("Ireland", "Europe"),
    "IL": ("Israel", "Asia"),
    "IN": ("India", "Asia"),
    "IS": ("Iceland", "Europe"),
    "IT": ("Italy", "Europe"),
    "JP": ("Japan", "Asia"),
    "KR": ("South Korea", "Asia"),
    "KZ": ("Kazakhstan", "Asia"),
    "LT": ("Lithuania", "Europe"),
    "LU": ("Luxembourg", "Europe"),
    "LV": ("Latvia", "Europe"),
    "MA": ("Morocco", "Africa"),
    "MX": ("Mexico", "Americas"),
    "MY": ("Malaysia", "Asia"),
    "NG": ("Nigeria", "Africa"),
    "NI": ("Nicaragua", "Americas"),
    "NL": ("Netherlands", "Europe"),
    "NO": ("Norway", "Europe"),
    "NZ": ("New Zealand", "Oceania"),
    "PA": ("Panama", "Americas"),
    "PE": ("Peru", "Americas"),
    "PH": ("Philippines", "Asia"),
    "PK": ("Pakistan", "Asia"),
    "PL": ("Poland", "Europe"),
    "PT": ("Portugal", "Europe"),
    "PY": ("Paraguay", "Americas"),
    "RO": ("Romania", "Europe"),
    "SA": ("Saudi Arabia", "Asia"),
    "SE": ("Sweden", "Europe"),
    "SG": ("Singapore", "Asia"),
    "SK": ("Slovakia", "Europe"),
    "SV": ("El Salvador", "Americas"),
    "TH": ("Thailand", "Asia"),
    "TR": ("Turkey", "Asia"),
    "TW": ("Taiwan", "Asia"),
    "UA": ("Ukraine", "Europe"),
    "US": ("United States", "Americas"),
    "UY": ("Uruguay", "Americas"),
    "VE": ("Venezuela", "Americas"),
    "VN": ("Vietnam", "Asia"),
    "ZA": ("South Africa", "Africa"),
}

# Fallback region for any country_key not present in COUNTRY_LOOKUP.
UNKNOWN_REGION: str = "Unknown"

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

# ---------------------------------------------------------------------------
# Validation thresholds (used by src/validate.py — no magic numbers in logic)
# ---------------------------------------------------------------------------

# Spotify popularity score bounds (inclusive).
POPULARITY_MIN: int = 0
POPULARITY_MAX: int = 100

# Audio features bounded to [0, 1]. `loudness` (dB) and `tempo` (BPM > 0) are
# NOT ratios and are validated separately.
RATIO_AUDIO_FEATURE_COLS: tuple[str, ...] = (
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "liveness",
    "speechiness",
    "instrumentalness",
)
