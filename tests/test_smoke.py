"""Scaffold smoke tests.

Verifies the test harness, package import, and config paths resolve. These
tests intentionally do not exercise pipeline logic — that arrives during the
Implement phase. They exist so a fresh checkout can run ``make test`` and get
a green bar, proving the scaffolding works.
"""

from __future__ import annotations

from src import __version__ as pkg_version
from src.config import (
    AUDIO_FEATURE_COLS,
    CSV_ENCODING,
    DATA_DIR,
    INTERIM_DIR,
    PROCESSED_DIR,
    RAW_DIR,
    ROOT_DIR,
)


def test_package_imports() -> None:
    assert isinstance(pkg_version, str) and pkg_version


def test_root_dir_exists() -> None:
    assert ROOT_DIR.is_dir()


def test_data_paths_resolve() -> None:
    assert DATA_DIR == ROOT_DIR / "data"
    assert RAW_DIR == DATA_DIR / "raw"
    assert INTERIM_DIR == DATA_DIR / "interim"
    assert PROCESSED_DIR == DATA_DIR / "processed"


def test_audio_feature_cols_non_empty() -> None:
    assert len(AUDIO_FEATURE_COLS) >= 7
    for col in ("danceability", "energy", "valence", "tempo"):
        assert col in AUDIO_FEATURE_COLS


def test_csv_encoding_is_utf8_with_bom() -> None:
    assert CSV_ENCODING == "utf-8-sig"
