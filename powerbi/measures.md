# DAX Measure Catalog

Reusable DAX measures defined on `Fact_TrackSnapshot` unless noted. Author each measure inside Power BI Desktop (Modeling → New measure) and copy the final form here so the catalogue stays in sync.

> Phase: scaffold. Concrete measures land during the Implement phase. The skeletons below show the intent and naming convention; verify the column names against `data_model.md` before pasting into Power BI.

## Naming convention

| Pattern | Example | Meaning |
|---|---|---|
| `# X` | `# Tracks` | Count |
| `Avg X` | `Avg Popularity` | Mean of X |
| `Median X` | `Median Tempo` | Median |
| `% X` | `% Explicit` | Share / ratio |
| `X YoY` | `Avg Popularity YoY` | Year-over-year delta |

## KPI measures

```DAX
# Tracks =
COUNTROWS(Dim_Track)

# Distinct Artists =
DISTINCTCOUNT(Fact_TrackSnapshot[artist_key])

Avg Popularity =
AVERAGE(Fact_TrackSnapshot[popularity])

% Explicit =
DIVIDE(
    CALCULATE(COUNTROWS(Dim_Track), Dim_Track[explicit] = TRUE()),
    COUNTROWS(Dim_Track)
)
```

## Audio-feature aggregates (defined on Dim_Track)

```DAX
Avg Danceability   = AVERAGE(Dim_Track[danceability])
Avg Energy         = AVERAGE(Dim_Track[energy])
Avg Valence        = AVERAGE(Dim_Track[valence])
Avg Tempo          = AVERAGE(Dim_Track[tempo])
Avg Acousticness   = AVERAGE(Dim_Track[acousticness])
```

## Time-intelligence (require Dim_Date marked as a Date Table)

```DAX
Avg Popularity YoY =
VAR _current = [Avg Popularity]
VAR _prior   = CALCULATE([Avg Popularity], SAMEPERIODLASTYEAR(Dim_Date[date]))
RETURN DIVIDE(_current - _prior, _prior)

Tracks Last 30 Days =
CALCULATE(
    [# Tracks],
    DATESINPERIOD(Dim_Date[date], MAX(Dim_Date[date]), -30, DAY)
)
```

## Country comparison (only if Dim_Country is used)

```DAX
Avg Popularity by Country =
AVERAGEX(VALUES(Dim_Country[country_key]), [Avg Popularity])
```

## Authoring rules

- **One measure per row in this file.** No silent duplicates in the model.
- **Format strings** set in Power BI (percent → `0.0%`, integer → `#,0`).
- **Never reference column raw aggregations** in visuals — always go through a named measure. Future you will thank present you.
