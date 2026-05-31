"""Write the star-schema tables to ``data/processed/*.csv``.

Power BI reads UTF-8-with-BOM most reliably on Windows, hence ``utf-8-sig``.
Column order is set explicitly so dashboard refreshes don't drift.

Implementation lands during the Implement phase — see SPEC.md.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import config


def export_tables(tables: dict[str, pd.DataFrame], output_dir: Path | None = None) -> None:
    """Write each table in ``tables`` to ``<output_dir>/<name>.csv``.

    Uses ``config.CSV_ENCODING`` (UTF-8 BOM, so Power BI on Windows renders
    non-ASCII names) and ``config.CSV_INDEX`` (False). Column order is whatever
    the ``transform.build_*`` builders produced — they set it to match
    ``data_model.md``. The output directory is created if missing.

    Args:
        tables: Mapping of filename (the ``config.FACT_TRACK_SNAPSHOT`` / ``DIM_*``
            constants) → DataFrame.
        output_dir: Destination directory. Defaults to ``config.PROCESSED_DIR``.
    """
    out = Path(output_dir) if output_dir is not None else config.PROCESSED_DIR
    out.mkdir(parents=True, exist_ok=True)
    for filename, frame in tables.items():
        frame.to_csv(out / filename, index=config.CSV_INDEX, encoding=config.CSV_ENCODING)
