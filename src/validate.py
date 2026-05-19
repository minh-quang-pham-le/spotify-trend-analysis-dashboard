"""Schema and integrity contracts for the star-schema output.

Runs after ``transform`` and before ``export``. If any contract fails, the
pipeline aborts — Power BI should never receive a half-broken model.

Contracts checked (each must be true):
    1. Every dimension's primary key is unique and non-null.
    2. Every foreign key in ``Fact_TrackSnapshot`` resolves to exactly one
       dimension row.
    3. ``popularity`` is in [0, 100]; audio feature ratios are in [0, 1];
       ``tempo`` > 0.
    4. ``Dim_Date`` is contiguous (no missing days inside its range).
    5. No row in ``Fact_TrackSnapshot`` is fully duplicated.

Implementation lands during the Implement phase — see SPEC.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class ValidationReport:
    """Result of a pipeline validation pass."""

    passed: bool
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def validate_star_schema(tables: dict[str, pd.DataFrame]) -> ValidationReport:
    """Run every contract listed in the module docstring."""
    raise NotImplementedError("Implementation pending — see SPEC.md Plan/Tasks phase.")
