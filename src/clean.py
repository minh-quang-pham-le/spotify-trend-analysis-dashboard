"""Clean the raw DataFrame.

Responsibilities:
    - Standardize column names (snake_case).
    - Coerce types (release_date → datetime, popularity → int, etc.).
    - Normalize ISRC (uppercase, strip whitespace, drop syntactically invalid).
    - Deduplicate at the (track, country, date) grain.
    - Drop rows missing essential keys.

Cleaning never invents data; missing-but-recoverable fields stay missing and
get flagged in ``validate.py``.

Implementation lands during the Implement phase — see SPEC.md.
"""

from __future__ import annotations

import pandas as pd


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of ``raw``.

    The output schema is consumed by ``transform.build_*`` functions; column
    names and types defined here are part of the internal pipeline contract.
    """
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")
