# DAX Measure Catalog

The authoritative list of measures in `dashboard.pbix`. Author each inside Power BI
Desktop (Modeling → New measure) and keep its final form here so the catalogue stays
in sync (this file IS the contract — no silent measures or duplicates in the model).

> **Table names match the committed `.pbix`: lowercase, CSV-derived**
> (`fact_track_snapshot`, `dim_track`, `dim_artist`, `dim_album`, `dim_date`,
> `dim_country`). Verified 2026-06-01 by inspecting the file's `DiagramLayout` (all six
> table nodes are lowercase) and `Report/Layout`. An earlier draft of this catalogue used
> PascalCase (`Fact_TrackSnapshot`, …) as an aspirational contract and assumed the Gate-G4
> rename had been applied; it had **not**. Rather than redo the rename in Power BI Desktop,
> the team decided (Gate G4 review) to **accept the file's names as-is and align the docs**.
> The PascalCase rename remains available if ever wanted — see `g4_remediation.md`.

## Verification status

All measures in this catalogue were **verified in Power BI Desktop on 2026-06-01** (Gate G4)
— they exist and evaluate without error. The four Overview KPIs are additionally confirmed
from the committed file's `Report/Layout` (a measure must be bound to a visual to appear
there); the rest are confirmed by the manual Gate-G4 check:

| Measure | Status | Evidence |
|---|---|---|
| `Tracks` | **confirmed** | Overview KPI card 1 (report layer) + Gate-G4 manual check |
| `Distinct Artists` | **confirmed** | Overview KPI card 2 (report layer) + Gate-G4 manual check |
| `Avg Popularity` | **confirmed** | Overview KPI card 3 (report layer) + Gate-G4 manual check |
| `% Explicit` | **confirmed** | Overview KPI card 4 (report layer) + Gate-G4 manual check |
| all measures below | **confirmed** | Gate-G4 manual verification in Power BI Desktop (2026-06-01) |

> The four Overview count/ratio measures live on `fact_track_snapshot`. Note the count
> measures are bare (`Tracks`, `Distinct Artists`) — **not** `#`-prefixed. The DAX below
> reflects that.

## Naming convention

| Pattern | Example | Meaning |
|---|---|---|
| `X` (bare noun) | `Tracks` | Count |
| `Avg X` | `Avg Popularity` | Mean of X |
| `% X` | `% Explicit` | Share / ratio |
| `X YoY` | `Avg Popularity YoY` | Year-over-year delta |

---

## KPI measures

```DAX
Tracks =
DISTINCTCOUNT(fact_track_snapshot[track_key])

Distinct Artists =
DISTINCTCOUNT(fact_track_snapshot[artist_key])

Albums =
DISTINCTCOUNT(fact_track_snapshot[album_key])

Avg Popularity =
AVERAGE(fact_track_snapshot[popularity])

Avg Rank =
AVERAGE(fact_track_snapshot[rank])

% Explicit =
DIVIDE(
    CALCULATE(COUNTROWS(dim_track), dim_track[explicit] = TRUE()),
    COUNTROWS(dim_track)
)
```

> The four cards on the **Overview** page (per todo.md C4) are
> `Tracks`, `Distinct Artists`, `Avg Popularity`, `% Explicit` — all confirmed present.
> The count KPIs use `DISTINCTCOUNT` on the **fact** so they respond to slicers
> (date / country) — `COUNTROWS(dim_track)` would ignore fact-side filters.

## Audio-feature aggregates (defined on dim_track)

```DAX
Avg Danceability = AVERAGE(dim_track[danceability])
Avg Energy       = AVERAGE(dim_track[energy])
Avg Valence      = AVERAGE(dim_track[valence])
Avg Tempo        = AVERAGE(dim_track[tempo])
Avg Acousticness = AVERAGE(dim_track[acousticness])
```

> `Avg Tempo` ignores blanks automatically — the one `tempo = 0` row is null in
> `dim_track` (see `data_model.md`), so it does not drag the mean toward zero.

## Time-intelligence (require dim_date marked as a Date Table)

```DAX
Avg Popularity YoY =
VAR _current = [Avg Popularity]
VAR _prior =
    CALCULATE([Avg Popularity], SAMEPERIODLASTYEAR(dim_date[date]))
RETURN
    DIVIDE(_current - _prior, _prior)

Tracks Last 30 Days =
CALCULATE(
    [Tracks],
    DATESINPERIOD(dim_date[date], MAX(dim_date[date]), -30, DAY)
)
```

> Depends on `[Avg Popularity]` and `[Tracks]` existing first.
> `SAMEPERIODLASTYEAR` / `DATESINPERIOD` need `dim_date` marked as a Date Table on
> `dim_date[date]` — **verified marked** in Power BI Desktop (Gate G4, 2026-06-01).

## Country comparison (dim_country is in scope)

```DAX
Avg Popularity by Country =
AVERAGEX(VALUES(dim_country[country_key]), [Avg Popularity])
```

## Phase D additions (author in Power BI Desktop — NOT yet in the file)

These are needed by Phase D pages and are **not** part of the Gate-G4-verified set above —
author them in Power BI Desktop as each page is built, then move them up once confirmed.

```DAX
Snapshots =
COUNTROWS(fact_track_snapshot)
```

> **D1 (popularity histogram) Y-axis.** Counts fact rows = chart appearances
> (track × country × day) → ~2,110,287 total. Deliberately **distinct from `Tracks`**
> (`DISTINCTCOUNT(track_key)` = 24,976): the histogram bins snapshots, not unique tracks.
> Using `Tracks` on the histogram Y-axis would (mis)count distinct tracks per bin instead.
> Format string `#,0`.

> **D2 (mood map scatter):** no new measure — reuses `Avg Valence`, `Avg Energy`,
> `Avg Popularity`. With one mark per `dim_track[track_key]`, each returns that track's value.

```DAX
Total Popularity =
SUM(fact_track_snapshot[popularity])
```

> **D4 (top-20 artists) — OPTIONAL.** The literal SPEC "aggregate popularity". Ranks artists
> identically to `Snapshots` (popularity is ~uniformly high), so `Snapshots` (already present)
> is the recommended ranking measure; add this only if you want the "aggregate popularity"
> label. Format `#,0`.

## Authoring rules

- **One measure per row in this file.** No silent duplicates in the model.
- **Format strings** set in Power BI: `% Explicit` / `Avg Popularity YoY` → `0.0%`;
  count measures (`Tracks`, `Distinct Artists`, `Albums`) → `#,0`;
  `Avg Popularity` → `#,0.0`.
- **Never reference raw column aggregations** in visuals — always go through a named measure.
