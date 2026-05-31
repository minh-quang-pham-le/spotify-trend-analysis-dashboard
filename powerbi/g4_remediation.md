# Gate G4 Remediation Runbook

Exact Power BI Desktop steps to clear the Gate G4 blockers. Everything that can be
prepared as code lives in [`power_query.md`](power_query.md) (M) and
[`measures.md`](measures.md) (DAX); this runbook is the click-by-click sequence to
apply them, plus the verification gates.

Do these in order — each step assumes the previous one applied cleanly.

---

## Target values (what "correct" looks like)

Computed from the current `data/processed/` CSVs. After the fixes, the model must match:

| Check | Expected |
|---|---|
| `Dim_Country` row count | **73** |
| `Dim_Artist` row count | **7,565** |
| `Dim_Track` row count | 24,976 |
| `Dim_Album` row count | 17,229 |
| `Dim_Date` row count | 603 |
| Overview `# Tracks` | **24,976** |
| Overview `# Distinct Artists` | **7,565** |
| Overview `Avg Popularity` | **75.91** (≈76 with `#,0`) |
| Overview `% Explicit` | **32.9%** |
| `Avg Rank` (reference) | 25.49 |

---

## Step 1 — Portable source + fix the broken queries (C2: F1, F2, F3)

1. **Home → Transform data** (opens Power Query Editor).
2. **Manage Parameters → New** → create `pProcessedFolder` (Text) = absolute path to
   your `data/processed\` (trailing `\`). See `power_query.md` Step 1.
3. For **each** of the six queries: select it → **Advanced Editor** → paste the
   matching M from `power_query.md` → **Done**.
   - This re-promotes headers on `Dim_Country` / `Dim_Artist` (kills the header-as-data
     rows and the `artist_key ` trailing space) and routes every query through the parameter.
4. **Close & Apply**. Wait for the load to finish with no errors.

## Step 2 — Rename tables to the contract (C2: F4)

In **Model view**, double-click each table header and rename:

| From | To |
|---|---|
| `fact_track_snapshot` | `Fact_TrackSnapshot` |
| `dim_track` | `Dim_Track` |
| `dim_artist` | `Dim_Artist` |
| `dim_album` | `Dim_Album` |
| `dim_date` | `Dim_Date` |
| `dim_country` | `Dim_Country` |

Power BI auto-updates relationships and measure references. Confirm the 5
relationships still show in Model view (all Many-to-one, single arrow, solid line).

## Step 3 — Clean up + rename measures (C3: F6, N2, N3)

1. **Delete** these measures (right-click → Delete): `Total Tracks`, `Total Artists`,
   `Average Daily Streams`.
2. **Rename** (right-click → Rename) per the table in `measures.md`:
   `Tracks Count → # Tracks`, `Artists Count → # Distinct Artists`,
   `Albums Count → # Albums`, `Average Popularity → Avg Popularity`,
   `Average Rank → Avg Rank`, `Explicit % → % Explicit`.

## Step 4 — Add the missing measures (C3: F5)

**Modeling → New measure**, paste each from `measures.md`:
`Avg Popularity YoY`, `Tracks Last 30 Days`, `Avg Popularity by Country`.
(Add them *after* Step 3 — they reference `[Avg Popularity]` and `[# Tracks]`.)

Set format strings: `% Explicit` and `Avg Popularity YoY` → `0.0%`; `# …` → `#,0`.

## Step 5 — Disable Auto date/time (N1)

**File → Options and settings → Options → Current File → Data Load** →
uncheck **Auto date/time**. This removes the hidden `LocalDateTable_*` /
`DateTableTemplate_*` and the stray `Dim_Album[release_date]` auto-relationship.
`Dim_Date` is already marked as the Date Table, so nothing is lost.

---

## Step 6 — Replace the `Average Rank` card with `% Explicit` (C4: F7)

1. Go to the **Overview** page.
2. Click the **4th KPI card** (currently showing **Average Rank**).
3. In the **Visualizations** pane → **Fields** well, remove `Avg Rank`
   (click the *X* next to it).
4. From the **Data** pane, drag **`% Explicit`** into the same **Fields** well.
5. With the card selected, set the value format to Percentage / 1 decimal
   (the measure-level `0.0%` from Step 4 handles this).
6. Update the card's title/label to "% Explicit" if a static title is shown.
7. Confirm the row reads, left→right: **# Tracks, # Distinct Artists, Avg Popularity, % Explicit**.

---

## Step 7 — Refresh validation (C4: F8)

1. **Home → Refresh** (full model refresh from disk).
2. Confirm the refresh dialog reports **no errors** and there are **no yellow warning
   triangles** on any visual.
3. Because the source now uses `pProcessedFolder`, confirm it resolved (no
   "file not found"). On a teammate's machine they only change the parameter value.

---

## Step 8 — Verify row counts (73 countries, 7,565 artists) (C2: F1)

**Data view** (left rail, table icon):

1. Select **`Dim_Country`** → the status bar (bottom) shows the row count → must be **73**.
   - Sort the `country_key` column A–Z and confirm there is **no** row literally
     equal to `country_key` (the old header-as-data junk row).
2. Select **`Dim_Artist`** → status bar must show **7,565**.
   - Confirm no row where `artist_key` = `artist_key`.
3. Cross-check the Overview cards against the **Target values** table above:
   `# Tracks` 24,976 · `# Distinct Artists` 7,565 · `Avg Popularity` ≈76 · `% Explicit` 32.9%.

> Quick alternative without scrolling: drop temporary Card visuals with
> `COUNTROWS(Dim_Country)` (→73) and `COUNTROWS(Dim_Artist)` (→7,565), then delete them.

---

## Step 9 — Commit + evidence (C1: F9, C4: F8)

1. Save the `.pbix`. From the repo root: `git add powerbi/dashboard.pbix` and commit.
2. Export an Overview screenshot (showing the 4 correct KPI numbers) into
   `report/figures/` so G4 has rendered-value evidence.
3. Re-run the Gate G4 review.

---

## After this runbook, the G4 failures map to fixed:

| ID | Failure | Fixed by |
|---|---|---|
| F1 | header rows ingested in Dim_Country/Dim_Artist | Step 1 |
| F2 | `artist_key ` trailing-space column / broken `Total Artists` | Step 1 + Step 3 |
| F3 | hard-coded `D:\` paths | Step 1 (parameter) |
| F4 | lowercase table names vs contract | Step 2 |
| F5 | missing YoY / 30-day / by-country measures | Step 4 |
| F6 | measures.md unsynced + divergent names | Step 3 + `measures.md` |
| F7 | Overview shows Average Rank not % Explicit | Step 6 |
| F8 | no refresh proof / no screenshot | Steps 7 & 9 |
| F9 | `.pbix` not committed | Step 9 |
| N1–N3 | auto-date clutter, dead/dup measures | Steps 5 & 3 |
