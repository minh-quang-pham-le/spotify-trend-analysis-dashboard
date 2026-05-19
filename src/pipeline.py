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


def run() -> int:
    """Execute the full pipeline. Returns a process exit code (0 = success)."""
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")
    # Reference outline:
    # raw = ingest.load_raw()
    # cleaned = clean.clean(raw)
    # tables = {
    #     config.DIM_TRACK: transform.build_dim_track(cleaned),
    #     config.DIM_ARTIST: transform.build_dim_artist(cleaned),
    #     config.DIM_ALBUM: transform.build_dim_album(cleaned),
    #     config.DIM_DATE: transform.build_dim_date(cleaned),
    #     config.DIM_COUNTRY: transform.build_dim_country(cleaned),
    #     config.FACT_TRACK_SNAPSHOT: transform.build_fact_track_snapshot(cleaned),
    # }
    # report = validate.validate_star_schema(tables)
    # if not report.passed:
    #     for err in report.errors:
    #         print(f"VALIDATION ERROR: {err}", file=sys.stderr)
    #     return 1
    # export.export_tables(tables)
    # return 0


if __name__ == "__main__":
    sys.exit(run())
