# Power Query (M) — source queries for `dashboard.pbix`

Copy-paste-ready M for every table in the model. Paste into Power BI Desktop via
**Home → Transform data → (select query) → Advanced Editor**, or recreate the
queries from scratch.

These replace the queries shipped in the first `dashboard.pbix`, which had three
defects found at Gate G4:

1. **`dim_country` / `dim_artist` skipped `Table.PromoteHeaders`** → the CSV header
   row was ingested as data (74 / 7,566 rows instead of 73 / 7,565) and `dim_artist`
   got a key column literally named `"artist_key "` (trailing space).
2. **Hard-coded `D:\…` absolute paths** → refresh broke on any other machine.
3. **`QuoteStyle.None`** → a track/album/artist name containing a comma would be
   split across columns. All queries below use `QuoteStyle.Csv` (honour quoting).

---

## Step 1 — Create the portable path parameter

Hard-coded absolute paths aren't portable, and a `.pbix` can't natively use a
repo-relative path. The standard fix is a single text **parameter** every query
references; each teammate sets it once after cloning.

**Home → Transform data → Manage Parameters → New:**

| Field | Value |
|---|---|
| Name | `pProcessedFolder` |
| Type | `Text` |
| Current Value | the absolute path to `<your-clone>/data/processed/` **including the trailing `\`** — e.g. `D:\Projects\spotify-trend-analysis-dashboard\data\processed\` |

> The value is machine-local and is **not** a model decision — it's the one thing a
> teammate edits after `git clone` + `make build`. Document it in the README setup steps.

---

## Step 2 — Replace each query's M

Each query name becomes the **table name**, so name them in PascalCase to match
`data_model.md` (`Fact_TrackSnapshot`, `Dim_Track`, …). Column names come straight
from the promoted CSV header, so they already match the contract.

### `Dim_Artist`  ← the broken one (fixes header + trailing space)

```m
let
    Source = Csv.Document(
        File.Contents(pProcessedFolder & "dim_artist.csv"),
        [Delimiter = ",", Columns = 3, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {{"artist_key", type text}, {"artist_name", type text}, {"primary_genre", type text}}
    )
in
    Typed
```

### `Dim_Country`  ← the broken one (fixes header)

```m
let
    Source = Csv.Document(
        File.Contents(pProcessedFolder & "dim_country.csv"),
        [Delimiter = ",", Columns = 3, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {{"country_key", type text}, {"country_name", type text}, {"region", type text}}
    )
in
    Typed
```

### `Dim_Track`

```m
let
    Source = Csv.Document(
        File.Contents(pProcessedFolder & "dim_track.csv"),
        [Delimiter = ",", Columns = 14, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"track_key", type text}, {"track_name", type text}, {"spotify_track_id", type text},
            {"explicit", type logical}, {"duration_ms", Int64.Type},
            {"danceability", type number}, {"energy", type number}, {"valence", type number},
            {"tempo", type number}, {"acousticness", type number}, {"liveness", type number},
            {"speechiness", type number}, {"instrumentalness", type number}, {"loudness", type number}
        }
    )
in
    Typed
```

### `Dim_Album`

```m
let
    Source = Csv.Document(
        File.Contents(pProcessedFolder & "dim_album.csv"),
        [Delimiter = ",", Columns = 4, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {{"album_key", type text}, {"album_name", type text},
         {"release_date", type date}, {"total_tracks", Int64.Type}}
    )
in
    Typed
```

### `Dim_Date`

```m
let
    Source = Csv.Document(
        File.Contents(pProcessedFolder & "dim_date.csv"),
        [Delimiter = ",", Columns = 11, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"date_key", Int64.Type}, {"date", type date}, {"year", Int64.Type},
            {"quarter", Int64.Type}, {"month", Int64.Type}, {"month_name", type text},
            {"day", Int64.Type}, {"day_of_week", Int64.Type}, {"day_name", type text},
            {"week_of_year", Int64.Type}, {"is_weekend", type logical}
        }
    )
in
    Typed
```

### `Fact_TrackSnapshot`

```m
let
    Source = Csv.Document(
        File.Contents(pProcessedFolder & "fact_track_snapshot.csv"),
        [Delimiter = ",", Columns = 8, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"track_key", type text}, {"artist_key", type text}, {"album_key", type text},
            {"date_key", Int64.Type}, {"country_key", type text},
            {"popularity", Int64.Type}, {"rank", Int64.Type}, {"daily_streams", Int64.Type}
        }
    )
in
    Typed
```

---

## Notes

- **`Encoding = 65001`** = UTF-8. The pipeline writes `utf-8-sig` (BOM); Power Query
  strips the BOM. If you ever see a stray `` on the first header (`track_key`),
  drop the `Encoding` argument so Power Query auto-detects the BOM.
- **Re-import alternative:** instead of editing each query, you can delete all six
  and use **Get Data → Folder → `pProcessedFolder`**, then *Combine & Transform*.
  Make sure the combine step keeps `Table.PromoteHeaders` and lands the contract
  column names — that is the root fix for the `dim_country` / `dim_artist` bug.
- After editing, **Close & Apply**, then follow `powerbi/g4_remediation.md` for the
  renames, measures, card swap, refresh, and row-count verification.
