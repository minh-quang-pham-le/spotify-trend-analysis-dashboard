# DAX Measure Catalog

The authoritative list of measures in `dashboard.pbix`. Author each inside Power BI
Desktop (Modeling → New measure) and keep its final form here so the catalogue stays
in sync (this file IS the contract — no silent measures or duplicates in the model).

> Table names use the `data_model.md` contract (PascalCase: `Fact_TrackSnapshot`,
> `Dim_Track`, …). If your model still has the CSV-derived lowercase names, rename the
> tables first (see `powerbi/g4_remediation.md`); Power BI updates measure references
> automatically on rename.

## Naming convention

| Pattern | Example | Meaning |
|---|---|---|
| `# X` | `# Tracks` | Count |
| `Avg X` | `Avg Popularity` | Mean of X |
| `% X` | `% Explicit` | Share / ratio |
| `X YoY` | `Avg Popularity YoY` | Year-over-year delta |

## Reconciliation from the first build (Gate G4)

The first `dashboard.pbix` shipped measures under different names plus duplicates/dead
measures. Rename / delete to reach this catalogue:

| In the first model | Action | Canonical name |
|---|---|---|
| `Tracks Count` | rename | `# Tracks` |
| `Artists Count` | rename | `# Distinct Artists` |
| `Albums Count` | rename | `# Albums` |
| `Average Popularity` | rename | `Avg Popularity` |
| `Average Rank` | rename | `Avg Rank` |
| `Explicit %` | rename | `% Explicit` |
| `Avg Danceability/Energy/Valence/Tempo/Acousticness` | keep | (unchanged) |
| `Total Tracks` | **delete** | duplicate of `# Tracks` |
| `Total Artists` | **delete** | duplicate of `# Distinct Artists` (also referenced the broken `artist_key ` column) |
| `Average Daily Streams` | **delete** | `daily_streams` is all-null in this source — measure is always blank |

---

## KPI measures

```DAX
# Tracks =
DISTINCTCOUNT(Fact_TrackSnapshot[track_key])

# Distinct Artists =
DISTINCTCOUNT(Fact_TrackSnapshot[artist_key])

# Albums =
DISTINCTCOUNT(Fact_TrackSnapshot[album_key])

Avg Popularity =
AVERAGE(Fact_TrackSnapshot[popularity])

Avg Rank =
AVERAGE(Fact_TrackSnapshot[rank])

% Explicit =
DIVIDE(
    CALCULATE(COUNTROWS(Dim_Track), Dim_Track[explicit] = TRUE()),
    COUNTROWS(Dim_Track)
)
```

> The four cards required on the **Overview** page (per todo.md C4) are
> `# Tracks`, `# Distinct Artists`, `Avg Popularity`, `% Explicit`.
> The count KPIs use `DISTINCTCOUNT` on the **fact** so they respond to slicers
> (date / country) — `COUNTROWS(Dim_Track)` would ignore fact-side filters.

## Audio-feature aggregates (defined on Dim_Track)

```DAX
Avg Danceability = AVERAGE(Dim_Track[danceability])
Avg Energy       = AVERAGE(Dim_Track[energy])
Avg Valence      = AVERAGE(Dim_Track[valence])
Avg Tempo        = AVERAGE(Dim_Track[tempo])
Avg Acousticness = AVERAGE(Dim_Track[acousticness])
```

> `Avg Tempo` ignores blanks automatically — the one `tempo = 0` row is null in
> `Dim_Track` (see `data_model.md`), so it does not drag the mean toward zero.

## Time-intelligence (require Dim_Date marked as a Date Table — already done)

```DAX
Avg Popularity YoY =
VAR _current = [Avg Popularity]
VAR _prior =
    CALCULATE([Avg Popularity], SAMEPERIODLASTYEAR(Dim_Date[date]))
RETURN
    DIVIDE(_current - _prior, _prior)

Tracks Last 30 Days =
CALCULATE(
    [# Tracks],
    DATESINPERIOD(Dim_Date[date], MAX(Dim_Date[date]), -30, DAY)
)
```

> Depends on `[Avg Popularity]` and `[# Tracks]` existing first.
> `SAMEPERIODLASTYEAR` / `DATESINPERIOD` need `Dim_Date` marked as a Date Table on
> `Dim_Date[date]` — verified present (`DataCategory = "Time"`, `date` IsKey).

## Country comparison (Dim_Country is in scope)

```DAX
Avg Popularity by Country =
AVERAGEX(VALUES(Dim_Country[country_key]), [Avg Popularity])
```

## Authoring rules

- **One measure per row in this file.** No silent duplicates in the model.
- **Format strings** set in Power BI: `% Explicit` / `Avg Popularity YoY` → `0.0%`;
  count measures (`# …`) → `#,0`; `Avg Popularity` → `#,0.0`.
- **Never reference raw column aggregations** in visuals — always go through a named measure.
