"""Write the star-schema tables to ``data/processed/*.csv``.

Power BI reads UTF-8-with-BOM most reliably on Windows, hence ``utf-8-sig``.
Column order is set explicitly so dashboard refreshes don't drift.

Implementation lands during the Implement phase — see SPEC.md.
"""

from __future__ import annotations

import pandas as pd


def export_tables(tables: dict[str, pd.DataFrame]) -> None:
    """Write each table in ``tables`` to ``data/processed/<name>.csv``.

    Use ``encoding=src.config.CSV_ENCODING`` (UTF-8 BOM) and
    ``index=src.config.CSV_INDEX`` (False), writing under
    ``src.config.PROCESSED_DIR``. Filenames in ``tables`` must match the
    constants in ``src.config`` (FACT_TRACK_SNAPSHOT, DIM_*).
    """
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")
