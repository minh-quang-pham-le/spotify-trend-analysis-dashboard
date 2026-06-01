"""End-to-end pipeline orchestrator.

Run with ``python -m src.pipeline`` (or ``make build``). Reads the raw Kaggle
CSV from ``data/raw/``, transforms it into the star schema, validates the
result, and writes ``data/processed/*.csv`` for Power BI to consume.

The orchestrator stays small on purpose: each stage owns its own logic, and
the pipeline just wires them together. Implementation lands during the
Implement phase — see SPEC.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

from src import clean, config, export, ingest, transform, validate


def run(raw_path: Path | None = None, output_dir: Path | None = None) -> int:
    """Execute the full pipeline: ingest → clean → transform → validate → export.

    Args:
        raw_path: Override path to the raw CSV (defaults to the configured
            ``data/raw/<dataset>``).
        output_dir: Override destination for the processed CSVs (defaults to
            ``data/processed/``).

    Returns:
        ``0`` on success; ``1`` if validation fails (export is skipped so Power BI
        never receives a half-broken model).
    """
    raw = ingest.load_raw(raw_path)
    print(f"ingest:    {len(raw):,} raw rows")

    cleaned = clean.clean(raw)
    print(f"clean:     {len(cleaned):,} rows after dedup / drop")

    # Key the frame once; every builder reuses these keys (add_keys is idempotent).
    keyed = transform.add_keys(cleaned)
    tables = {
        config.FACT_TRACK_SNAPSHOT: transform.build_fact_track_snapshot(keyed),
        config.DIM_TRACK: transform.build_dim_track(keyed),
        config.DIM_ARTIST: transform.build_dim_artist(keyed),
        config.DIM_ALBUM: transform.build_dim_album(keyed),
        config.DIM_DATE: transform.build_dim_date(keyed),
        config.DIM_COUNTRY: transform.build_dim_country(keyed),
    }
    print(
        "transform: "
        + ", ".join(f"{name.removesuffix('.csv')}={len(df):,}" for name, df in tables.items())
    )

    report = validate.validate_star_schema(tables)
    if not report.passed:
        print(f"validate:  FAILED ({len(report.errors)} error(s))")
        for err in report.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("validate:  passed")

    # Derived analytical table (not part of the star schema, so added after
    # validation): audio-feature correlation matrix for the Audio Anatomy heatmap.
    tables[config.CORR_AUDIO_FEATURES] = transform.build_corr_audio_features(
        tables[config.DIM_TRACK]
    )

    out = Path(output_dir) if output_dir is not None else config.PROCESSED_DIR
    export.export_tables(tables, output_dir=out)
    print(f"export:    wrote {len(tables)} CSVs to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
