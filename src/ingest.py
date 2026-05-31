"""Load the raw Kaggle dataset into a typed pandas DataFrame.

This module is intentionally thin: read CSV, return DataFrame. Cleaning and
typing happens in ``clean.py`` so the boundary stays sharp. Implementation
lands during the Implement phase — see SPEC.md.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import config


def load_raw(path: Path | None = None) -> pd.DataFrame:
    """Read the raw Kaggle CSV from ``data/raw/`` and return it untouched.

    Args:
        path: Override path to the raw CSV. Defaults to
            ``data/raw/<PRIMARY_DATASET_FILENAME>`` (see ``src.config``).

    Returns:
        Raw DataFrame — no type coercion, no deduplication, no renaming. Type
        inference is left to pandas; canonicalization happens in ``clean.py``.

    Raises:
        FileNotFoundError: If the CSV is missing, with a message pointing at the
            expected path. See README §"Get the data".
    """
    csv_path = Path(path) if path is not None else config.RAW_DIR / config.PRIMARY_DATASET_FILENAME
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Raw dataset not found at {csv_path}. Download "
            f"{config.PRIMARY_DATASET_FILENAME} into {config.RAW_DIR} "
            f"(see README §'Get the data')."
        )
    # low_memory=False reads the file in one pass so pandas infers a single dtype
    # per column — avoids the DtypeWarning the 2.1M-row real file would otherwise
    # emit. This is consistent inference, not coercion: clean.py owns the types.
    return pd.read_csv(csv_path, low_memory=False)
