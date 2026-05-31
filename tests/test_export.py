"""Integration tests for ``src.export`` (Task B10).

Writes tables to a tmp dir and reads them back, asserting filenames, column
order, UTF-8-BOM encoding (so Power BI on Windows renders non-ASCII names), no
stray index column, and a non-ASCII value round-trip.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import config, export, transform


def _all_tables(cleaned: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        config.FACT_TRACK_SNAPSHOT: transform.build_fact_track_snapshot(cleaned),
        config.DIM_TRACK: transform.build_dim_track(cleaned),
        config.DIM_ARTIST: transform.build_dim_artist(cleaned),
        config.DIM_ALBUM: transform.build_dim_album(cleaned),
        config.DIM_DATE: transform.build_dim_date(cleaned),
        config.DIM_COUNTRY: transform.build_dim_country(cleaned),
    }


def test_export_writes_all_tables(cleaned_df, tmp_path: Path) -> None:
    tables = _all_tables(cleaned_df)
    export.export_tables(tables, output_dir=tmp_path)
    for name in tables:
        assert (tmp_path / name).is_file()


def test_export_roundtrip_columns_and_unicode(cleaned_df, tmp_path: Path) -> None:
    dim_artist = transform.build_dim_artist(cleaned_df)
    export.export_tables({config.DIM_ARTIST: dim_artist}, output_dir=tmp_path)
    back = pd.read_csv(tmp_path / config.DIM_ARTIST, encoding=config.CSV_ENCODING)
    assert list(back.columns) == list(dim_artist.columns)
    assert "Café Trío" in set(back["artist_name"])  # non-ASCII round-trips


def test_export_uses_utf8_bom(cleaned_df, tmp_path: Path) -> None:
    export.export_tables(
        {config.DIM_ARTIST: transform.build_dim_artist(cleaned_df)}, output_dir=tmp_path
    )
    raw = (tmp_path / config.DIM_ARTIST).read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM


def test_export_writes_no_index_column(cleaned_df, tmp_path: Path) -> None:
    export.export_tables(
        {config.DIM_TRACK: transform.build_dim_track(cleaned_df)}, output_dir=tmp_path
    )
    back = pd.read_csv(tmp_path / config.DIM_TRACK, encoding=config.CSV_ENCODING)
    assert not any(str(c).startswith("Unnamed") for c in back.columns)


def test_export_creates_missing_output_dir(cleaned_df, tmp_path: Path) -> None:
    out = tmp_path / "nested" / "processed"
    export.export_tables(
        {config.DIM_COUNTRY: transform.build_dim_country(cleaned_df)}, output_dir=out
    )
    assert (out / config.DIM_COUNTRY).is_file()
