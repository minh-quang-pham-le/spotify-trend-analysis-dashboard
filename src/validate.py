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

from src import config

# Dimension table (filename key) -> its primary-key column.
_DIM_PRIMARY_KEYS: dict[str, str] = {
    config.DIM_TRACK: "track_key",
    config.DIM_ARTIST: "artist_key",
    config.DIM_ALBUM: "album_key",
    config.DIM_DATE: "date_key",
    config.DIM_COUNTRY: "country_key",
}

# Fact foreign-key column -> the dimension (filename key) it must resolve into.
_FACT_FOREIGN_KEYS: dict[str, str] = {
    "track_key": config.DIM_TRACK,
    "artist_key": config.DIM_ARTIST,
    "album_key": config.DIM_ALBUM,
    "date_key": config.DIM_DATE,
    "country_key": config.DIM_COUNTRY,
}


@dataclass(frozen=True)
class ValidationReport:
    """Result of a pipeline validation pass."""

    passed: bool
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _check_primary_keys(tables: dict[str, pd.DataFrame], errors: list[str]) -> None:
    for name, pk in _DIM_PRIMARY_KEYS.items():
        dim = tables[name]
        if pk not in dim.columns:
            errors.append(f"{name}: missing primary-key column '{pk}'")
            continue
        if dim[pk].isna().any():
            errors.append(f"{name}: primary key '{pk}' contains nulls")
        if dim[pk].duplicated().any():
            errors.append(f"{name}: primary key '{pk}' is not unique")


def _check_foreign_keys(fact: pd.DataFrame, tables: dict[str, pd.DataFrame], errors: list[str]) -> None:
    for fk, dim_name in _FACT_FOREIGN_KEYS.items():
        if fk not in fact.columns:
            errors.append(f"fact: missing foreign-key column '{fk}'")
            continue
        if fact[fk].isna().any():
            errors.append(f"fact.{fk}: contains null foreign keys")
        pk = _DIM_PRIMARY_KEYS[dim_name]
        valid = set(tables[dim_name][pk].tolist())
        unresolved = sorted({str(v) for v in fact[fk].dropna().tolist()} - {str(v) for v in valid})
        if unresolved:
            sample = ", ".join(unresolved[:3])
            errors.append(
                f"fact.{fk}: {len(unresolved)} value(s) do not resolve to {dim_name} (e.g. {sample})"
            )


def _check_ranges(fact: pd.DataFrame, dim_track: pd.DataFrame, errors: list[str]) -> None:
    if "popularity" in fact.columns:
        if fact["popularity"].isna().any():
            errors.append("fact.popularity: contains nulls (SPEC §1 requires non-null)")
        pop = fact["popularity"].dropna()
        if not pop.between(config.POPULARITY_MIN, config.POPULARITY_MAX).all():
            errors.append(
                f"fact.popularity: values outside [{config.POPULARITY_MIN}, {config.POPULARITY_MAX}]"
            )
    for col in config.RATIO_AUDIO_FEATURE_COLS:
        if col in dim_track.columns:
            vals = dim_track[col].dropna()
            if not vals.between(0.0, 1.0).all():
                errors.append(f"dim_track.{col}: ratio values outside [0, 1]")
    if "tempo" in dim_track.columns:
        tempo = dim_track["tempo"].dropna()
        if not (tempo > 0).all():
            errors.append("dim_track.tempo: values must be > 0")


def _check_dim_date_contiguous(dim_date: pd.DataFrame, errors: list[str]) -> None:
    if "date" not in dim_date.columns or dim_date.empty:
        return
    dates = pd.to_datetime(dim_date["date"])
    span_days = (dates.max() - dates.min()).days + 1
    if span_days != len(dim_date):
        errors.append(
            f"dim_date: not contiguous ({len(dim_date)} rows span {span_days} calendar days)"
        )


def validate_star_schema(tables: dict[str, pd.DataFrame]) -> ValidationReport:
    """Run every contract listed in the module docstring.

    Returns a :class:`ValidationReport`; ``passed`` is False with explicit error
    messages whenever any contract is violated. All contracts are evaluated (the
    report is exhaustive, not fail-fast) so one run surfaces every problem.
    """
    errors: list[str] = []

    # 0. Required tables present (can't check anything else without them).
    required = [config.FACT_TRACK_SNAPSHOT, *_DIM_PRIMARY_KEYS]
    missing = [name for name in required if name not in tables]
    if missing:
        return ValidationReport(passed=False, errors=tuple(f"missing table: {n}" for n in missing))

    fact = tables[config.FACT_TRACK_SNAPSHOT]

    _check_primary_keys(tables, errors)  # contract 1
    _check_foreign_keys(fact, tables, errors)  # contract 2
    _check_ranges(fact, tables[config.DIM_TRACK], errors)  # contract 3
    _check_dim_date_contiguous(tables[config.DIM_DATE], errors)  # contract 4

    # contract 5: no fully-duplicated fact row.
    if fact.duplicated().any():
        errors.append("fact: contains fully-duplicated rows")

    return ValidationReport(passed=not errors, errors=tuple(errors))
