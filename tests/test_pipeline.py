"""Integration tests for the orchestrator ``src.pipeline.run`` (Task B11)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import config, pipeline, validate

FIXTURE = Path(__file__).parent / "fixtures" / "mini_raw.csv"

EXPECTED_FILES = (
    config.FACT_TRACK_SNAPSHOT,
    config.DIM_TRACK,
    config.DIM_ARTIST,
    config.DIM_ALBUM,
    config.DIM_DATE,
    config.DIM_COUNTRY,
)


def test_run_succeeds_and_writes_all_csvs(tmp_path: Path) -> None:
    code = pipeline.run(raw_path=FIXTURE, output_dir=tmp_path)
    assert code == 0
    for name in EXPECTED_FILES:
        assert (tmp_path / name).is_file()


def test_run_output_row_counts_match_fixture(tmp_path: Path) -> None:
    pipeline.run(raw_path=FIXTURE, output_dir=tmp_path)
    fact = pd.read_csv(tmp_path / config.FACT_TRACK_SNAPSHOT, encoding=config.CSV_ENCODING)
    dim_track = pd.read_csv(tmp_path / config.DIM_TRACK, encoding=config.CSV_ENCODING)
    assert len(fact) == 9  # 9 distinct (track, country, date) tuples
    assert len(dim_track) == 4  # 4 tracks


def test_run_writes_corr_audio_features(tmp_path: Path) -> None:
    pipeline.run(raw_path=FIXTURE, output_dir=tmp_path)
    path = tmp_path / config.CORR_AUDIO_FEATURES
    assert path.is_file()
    corr = pd.read_csv(path, encoding=config.CSV_ENCODING)
    assert list(corr.columns) == ["feature_x", "feature_y", "r"]
    diag = corr.loc[corr["feature_x"] == corr["feature_y"], "r"]
    assert (diag.round(6) == 1.0).all()


def test_run_returns_1_and_skips_export_on_validation_failure(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        validate,
        "validate_star_schema",
        lambda tables: validate.ValidationReport(passed=False, errors=("synthetic failure",)),
    )
    code = pipeline.run(raw_path=FIXTURE, output_dir=tmp_path)
    assert code == 1
    # Aborted before export — no CSVs written.
    assert not any((tmp_path / name).exists() for name in EXPECTED_FILES)


def test_run_prints_stage_status(tmp_path, capsys) -> None:
    pipeline.run(raw_path=FIXTURE, output_dir=tmp_path)
    out = capsys.readouterr().out.lower()
    for stage in ("ingest", "clean", "transform", "validate", "export"):
        assert stage in out
