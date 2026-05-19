# Power BI Data Model

Binding contract between `data/processed/*.csv` and `dashboard.pbix`. Renaming or restructuring any of these tables/columns without updating both the CSVs and the `.pbix` will silently break the dashboard.

See `SPEC.md §7` for the rationale behind every choice.

## Tables

### Fact_TrackSnapshot (`fact_track_snapshot.csv`)

Grain: one row per `(track, country, snapshot_date)`. If the chosen Kaggle dataset is a static catalog (no time/country dimension), the grain collapses to one row per track and the country/date FKs become optional.

| Column | Type | Nullable | Notes |
|---|---|---|---|
| track_key | string | no | FK → `Dim_Track` |
| artist_key | string | no | FK → `Dim_Artist` (primary artist only — see ASK FIRST below) |
| album_key | string | no | FK → `Dim_Album` |
| date_key | int (YYYYMMDD) | no | FK → `Dim_Date` |
| country_key | string (ISO-2) | yes* | FK → `Dim_Country`. Required if multi-country dataset is used. |
| popularity | int [0, 100] | no | Spotify popularity score |
| rank | int ≥ 1 | yes | Chart position on that day/country (null if dataset has no chart axis) |
| daily_streams | int ≥ 0 | yes | Estimated daily streams (null if absent in source) |

### Dim_Track (`dim_track.csv`)

| Column | Type | Nullable | Notes |
|---|---|---|---|
| track_key | string | no | Primary key — ISRC if present, else `sha1(name + '|' + primary_artist)[:16]` |
| track_name | string | no | Original casing preserved |
| isrc | string | yes | Normalized: uppercase, no whitespace |
| explicit | bool | no | |
| duration_ms | int ≥ 0 | no | |
| danceability | float [0, 1] | yes | |
| energy | float [0, 1] | yes | |
| valence | float [0, 1] | yes | |
| tempo | float > 0 | yes | BPM |
| acousticness | float [0, 1] | yes | |
| liveness | float [0, 1] | yes | |
| speechiness | float [0, 1] | yes | |
| instrumentalness | float [0, 1] | yes | |
| loudness | float (dB) | yes | Typically [−60, 0] |

### Dim_Artist (`dim_artist.csv`)

| Column | Type | Nullable | Notes |
|---|---|---|---|
| artist_key | string | no | Primary key (stable hash of canonicalized name) |
| artist_name | string | no | Display name |
| primary_genre | string | yes | If dataset provides it |

### Dim_Album (`dim_album.csv`)

| Column | Type | Nullable | Notes |
|---|---|---|---|
| album_key | string | no | Primary key |
| album_name | string | no | |
| release_date | date | yes | |
| total_tracks | int ≥ 1 | yes | |

### Dim_Date (`dim_date.csv`)

| Column | Type | Notes |
|---|---|---|
| date_key | int (YYYYMMDD) | Primary key |
| date | date | |
| year | int | |
| quarter | int [1, 4] | |
| month | int [1, 12] | |
| month_name | string | "January", "February", … |
| day | int [1, 31] | |
| day_of_week | int [1, 7] | Monday = 1 |
| day_name | string | |
| week_of_year | int [1, 53] | |
| is_weekend | bool | |

### Dim_Country (`dim_country.csv`) — only if multi-country dataset

| Column | Type | Notes |
|---|---|---|
| country_key | string (ISO-2) | Primary key, uppercase |
| country_name | string | English name |
| region | string | "Americas", "Europe", "Asia", "Africa", "Oceania" |

## Relationships (Power BI Manage Relationships)

```
Fact_TrackSnapshot[track_key]   ──*──→ Dim_Track[track_key]    (cardinality: many-to-one)
Fact_TrackSnapshot[artist_key]  ──*──→ Dim_Artist[artist_key]  (many-to-one)
Fact_TrackSnapshot[album_key]   ──*──→ Dim_Album[album_key]    (many-to-one)
Fact_TrackSnapshot[date_key]    ──*──→ Dim_Date[date_key]      (many-to-one)
Fact_TrackSnapshot[country_key] ──*──→ Dim_Country[country_key] (many-to-one, only if applicable)
```

All relationships are *single direction* (Dim → Fact filter propagation), and *active*.

## Refresh checklist (after every `make build`)

1. Open `dashboard.pbix` in Power BI Desktop.
2. *Home → Refresh*.
3. Check the *Issues* pane: any missing column = the pipeline schema drifted. Reconcile by either fixing the pipeline or by updating Power Query (M) and reopening this doc.
4. Verify *Model view* — all five relationships still exist.
5. Spot-check one chart per page renders without error.

## Open ASK-FIRST decisions

- **Multi-artist tracks**: currently `artist_key` references the primary artist only. Adding a `Bridge_TrackArtist` table to support multi-artist analytics is a star-schema departure — needs team approval.
- **Genre dimension**: if we promote `primary_genre` out of `Dim_Artist` into its own `Dim_Genre`, the FK chain changes. Decide before implementation.
