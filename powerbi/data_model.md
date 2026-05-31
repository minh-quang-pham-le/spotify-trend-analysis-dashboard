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
| rank | int ≥ 1 | yes | Chart position (`daily_rank`, 1–50) on that day/country |
| daily_streams | int ≥ 0 | yes | **Absent in the Asaniczka source** — column stays empty / is dropped. See Gate-G1 note. |

### Dim_Track (`dim_track.csv`)

| Column | Type | Nullable | Notes |
|---|---|---|---|
| track_key | string | no | Primary key — `spotify_id` (ISRC absent in source); `sha1(track_name + '|' + primary_artist)[:16]` only if an id is ever missing. **ISRC→spotify_id is a Gate-G1 decision — see below.** |
| track_name | string | no | Original casing preserved |
| spotify_track_id | string | no | Spotify track id (22-char base62). Stable per-recording key; replaces ISRC, which this source lacks. |
| explicit | bool | no | |
| duration_ms | int ≥ 0 | no | |
| danceability | float [0, 1] | yes | |
| energy | float [0, 1] | yes | |
| valence | float [0, 1] | yes | |
| tempo | float > 0 | yes | BPM. Source `tempo=0` (Spotify "undetectable" sentinel) is coerced to null in `clean.py` — 1 row in the 2025-06-11 snapshot. |
| acousticness | float [0, 1] | yes | |
| liveness | float [0, 1] | yes | |
| speechiness | float [0, 1] | yes | |
| instrumentalness | float [0, 1] | yes | |
| loudness | float (dB) | yes | Typically [−60, 0] |

### Dim_Artist (`dim_artist.csv`)

| Column | Type | Nullable | Notes |
|---|---|---|---|
| artist_key | string | no | Primary key (stable hash of canonicalized name) |
| artist_name | string | no | Display name (primary artist; `artists` is a comma-delimited list — 40.7% multi-artist) |
| primary_genre | string | yes | **Absent in the Asaniczka source** — will be empty. See Gate-G1 note. |

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
| country_key | string (ISO-2) | Primary key, uppercase. Blank-country "Global" chart rows map to the sentinel `GLOBAL` (`config.GLOBAL_COUNTRY_KEY`). |
| country_name | string | English name ("Global" for the worldwide chart) |
| region | string | "Americas", "Europe", "Asia", "Africa", "Oceania", or "Global" |

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

## Gate G1 — schema reconciliation (2026-05-31, pending team sign-off)

Profiling the real Asaniczka snapshot (`notebooks/01_data_profile.ipynb`, 2,110,316 rows, 2023-10-18 → 2025-06-11) showed it diverges from the `SPEC.md §7` assumptions this contract was first written against. `src/config.py` now encodes the reconciliation (`RAW_TO_CANONICAL_COLUMNS`, `PRIMARY_TRACK_ID_COLUMN`, `ABSENT_EXPECTED_COLUMNS`, `EXTRA_AUDIO_FEATURE_COLS`, `GLOBAL_COUNTRY_KEY`). The column-name renames are applied above. **Three items below change project boundaries and need team sign-off before Phase B:**

1. **No ISRC → key on `spotify_id`.** `SPEC.md §9` lists "Always use ISRC as the primary track key" — but this dataset has no ISRC column. `spotify_id` is 100% present and 100% a valid 22-char base62 id, so it is the stable primary key; the `sha1(name+artist)` surrogate becomes a never-expected fallback. *Resolving this updates SPEC §1/§7/§9 wording — confirm with the team.*
2. **No `daily_streams`.** Source has `daily_movement` / `weekly_movement` (chart-position deltas) but no stream counts. The Mood Map's *size = streams* encoding (SPEC §8 chart 3) needs a substitute — proposal: drop the optional size channel (color already encodes popularity) or size by `duration_ms`.
3. **No genre.** Dim_Artist `primary_genre` will be empty. The *box plot by genre* (SPEC §8 chart 8) needs a substitute grouping — proposal: bucket by release-year. (SPEC §10 open question #3 is thereby moot for v1.)

Renames already applied (raw → canonical): `name`→`track_name`, `artists`→`artist_names` (→ primary artist in `clean.py`), `is_explicit`→`explicit`, `album_release_date`→`release_date`, `daily_rank`→`rank`, `spotify_id`→`spotify_track_id`. Extra audio columns available but not yet modeled: `key`, `mode`, `time_signature`.

## Open ASK-FIRST decisions

- **Multi-artist tracks**: currently `artist_key` references the primary artist only. Adding a `Bridge_TrackArtist` table to support multi-artist analytics is a star-schema departure — needs team approval.
- **Genre dimension**: if we promote `primary_genre` out of `Dim_Artist` into its own `Dim_Genre`, the FK chain changes. Decide before implementation.
