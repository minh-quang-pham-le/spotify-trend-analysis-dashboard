"""Load the raw Kaggle dataset into a typed pandas DataFrame.

This module is intentionally thin: read CSV, return DataFrame. Cleaning and
typing happens in ``clean.py`` so the boundary stays sharp. Implementation
lands during the Implement phase — see SPEC.md.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_raw(path: Path | None = None) -> pd.DataFrame:
    """Read the raw Kaggle CSV from ``data/raw/`` and return it untouched.

    Args:
        path: Override path to the raw CSV. Defaults to
            ``data/raw/<PRIMARY_DATASET_FILENAME>`` (see ``src.config``).

    Returns:
        Raw DataFrame — no type coercion, no deduplication, no renaming.

    Raises:
        FileNotFoundError: If the CSV is missing. See README §"Get the data".
    """
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")
