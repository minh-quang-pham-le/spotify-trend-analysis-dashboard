# Phase D — Dashboard Build Runbook

Click-by-click Power BI Desktop steps for the Phase D pages. Each section is a self-contained
visual. DAX for any new measure lives in [`measures.md`](measures.md); the rubric-based
justification for each chart lives in [`report/chart_justifications.md`](../report/chart_justifications.md).

After building each visual: export a screenshot to `report/figures/` and tick the task in
[`../tasks/todo.md`](../tasks/todo.md).

> The `.pbix` is a single binary — only **one person** should edit it at a time (no parallel
> git branches on it). See `tasks/phase_c_summary.md` → Phase D readiness.

---

## D1 — Overview: popularity histogram ✅ DONE (2026-06-01)

**Goal:** a histogram of `popularity` on the existing **Overview** page, beside the 4 KPI cards.
**Acceptance (todo.md D1):** sensible binning; visible alongside the KPI cards; shape matches
the A2/profile distribution.

> **Status: built and verified.** Snapshot-level framing chosen and locked. Screenshot
> `report/figures/d1_overview_popularity_histogram.png` confirms the left-skewed shape (peak
> bin 80–90). Steps below are retained as the build record.

### Framing (locked): snapshot-level

Count **chart snapshots** (fact rows), which keeps the histogram consistent with the
`Avg Popularity` = 75.9 KPI on the same page (same population) and needs no pipeline change.
The alternative track-level framing is at the bottom of this section.

### Step 1 — add the measure

Modeling → New measure (from `measures.md` → *Phase D additions*):

```DAX
Snapshots = COUNTROWS(fact_track_snapshot)
```

Set its format string to `#,0`.

### Step 2 — create the popularity bins

In the **Data** pane, right-click `fact_track_snapshot[popularity]` → **New group**:

| Field | Value |
|---|---|
| Group type | **Bin** |
| Bin type | **Size of bins** |
| Bin size | **10** |

This creates a field `popularity (bins)` with 10 buckets covering 0–100.

### Step 3 — build the visual

1. On the **Overview** page, add a **Clustered column chart** (place it below / right of the KPI cards).
2. **X-axis**: `popularity (bins)`.
3. **Y-axis (Values)**: the **`Snapshots`** measure.
4. X-axis → sort ascending by `popularity (bins)` so bars read 0→100 left to right.

### Step 4 — format (data-ink: keep it clean)

- Title: **"Distribution of track popularity (chart snapshots)"**.
- X-axis title: **"Spotify popularity (binned, width 10)"**; Y-axis title: **"Chart snapshots"**.
- Legend: **off** (single series).
- Gridlines: minimal; data labels off (the shape is the message, not exact counts).
- Bar color: the agreed colorblind-safe single hue (set once in *Cross-cutting design choices*).

### Step 5 — verify against the profiled shape

The bars should reproduce these proportions (computed from the processed fact CSV,
2025-06-11 snapshot; mean 75.9, median 79, left-skewed):

| Bin | Share | | Bin | Share |
|---|---|---|---|---|
| `[0,10)`   | 0.6%  | | `[50,60)` | 10.8% |
| `[10,20)`  | 0.1%  | | `[60,70)` | 16.1% |
| `[20,30)`  | 0.2%  | | `[70,80)` | 18.2% |
| `[30,40)`  | 0.7%  | | `[80,90)` | **29.8%** (peak) |
| `[40,50)`  | 3.5%  | | `[90,100]`| 19.2% |

Pass condition: the tallest bar is `[80,90)`, the distribution is clearly clustered high
(≈67% of snapshots ≥ 70), not flat/uniform.

### Step 6 — capture evidence

Export a screenshot of the Overview page (KPI cards + histogram) to
`report/figures/d1_overview_popularity_histogram.png`.

---

### Alternative framing: track-level (the catalogue view)

If the team prefers "how popular is the typical *distinct track*" (mean ≈ 52.8, median ≈ 55.7,
peak bin 50–60), Power BI's column binning won't do it directly because `popularity` is on the
fact. You need a per-track value on `dim_track` first:

1. **Data → New column** on `dim_track`:
   ```DAX
   Avg Popularity (track) =
   CALCULATE(AVERAGE(fact_track_snapshot[popularity]))
   ```
2. Right-click that new column → **New group** → Bin, size 10 → `Avg Popularity (track) (bins)`.
3. X-axis = the new bins; Y-axis = **`Tracks`** (`DISTINCTCOUNT(track_key)`).

This answers the catalogue question but is **inconsistent with the Avg Popularity KPI** on the
same page (75.9 vs a ~55 center). **Decision (2026-06-01): snapshot-level chosen for the
Overview**; this track-level variant is retained only as a possible *separate* analysis page
later — not built.

---

## D2 — Mood Map: energy × valence scatter

**Goal:** a scatter of `valence` (X) × `energy` (Y), colored by popularity, **one mark per
track**, on a new **Mood Map** page.
**Acceptance (todo.md D2):** scatter X=valence, Y=energy, color=popularity; tooltip shows
track + artist; point count matches `Tracks` within filter context.

### Measures

**None new required.** Reuse the existing (Gate-G4-verified) measures `Avg Valence`,
`Avg Energy`, `Avg Popularity`. At one-mark-per-track grain each returns that track's own value
(valence/energy are static per track; popularity is the track's mean across its snapshots).

### Step 1 — new page
Add a report page, rename it **"Mood Map"**.

### Step 2 — scatter chart
1. Insert a **Scatter chart**.
2. **Values → Details**: `dim_track[track_key]` — this forces **one mark per distinct track**
   (what makes the point count equal `Tracks`). Use `track_key`, *not* `track_name`, so
   same-named tracks by different artists don't merge.
3. **X axis**: `Avg Valence`.
4. **Y axis**: `Avg Energy`.
5. Leave **Size** empty.

### Step 3 — color by popularity (continuous gradient)
Format → **Markers → Colors → fx** (conditional formatting) → Format style **Gradient**, based
on **`Avg Popularity`**, min→max over 0–100 (light = low, dark = high).
*(Alternative: a discrete popularity band on the Legend — needs a calc column on `dim_track`;
the gradient avoids that and matches SPEC's "color by popularity".)*

### Step 4 — tooltip
Add to the **Tooltips** well: `dim_track[track_name]`, `dim_artist[artist_name]`,
`Avg Popularity`, `Avg Valence`, `Avg Energy`. (Artist resolves through the fact relationship —
each `track_key` maps to one primary `artist_key`.)

### Step 5 — handle 25k points (overplotting)
- **High-density sampling ON** (default for scatter). 24,976 tracks > the ~10k render cap, so
  Power BI plots a representative sample; the shape holds, the underlying count is exact on a
  `Tracks` card.
- Markers → transparency ~30–50% so dense regions read as shade.
- Optional: an **`Avg Popularity` slicer** (or visual-level filter `Avg Popularity ≥ 60`) to
  focus on popular tracks and bring the plotted count under the cap.

### Step 6 — format
- Title: **"Mood map — energy vs. valence (one mark per track)"**.
- X-axis title **"Valence (musical positiveness, 0–1)"**, axis range **0–1**; Y-axis title
  **"Energy (0–1)"**, range **0–1**.
- Optional: constant lines at x = 0.5 and y = 0.5 to read the four mood quadrants
  (calm-positive / happy-energetic / sad-calm / tense-aggressive).
- Colorblind-safe **sequential** gradient (cross-cutting palette — set once).

### Step 7 — verify
- Drop a temporary `Tracks` card on the page → reads **24,976** (unfiltered) = the underlying
  mark population. *(Rendered marks may be sampled to ~10k — expected, not a failure.)*
- Visual sanity: marks fill the plane centered around **valence ≈ 0.53, energy ≈ 0.65**, and
  the color gradient looks **near-uniform across the plane** (popularity is not regional —
  the expected finding, r ≈ 0.08 / 0.05).

### Step 8 — evidence
Export a screenshot to `report/figures/d2_mood_map_scatter.png` (gitignored — local/report use).

---

## D3 — Temporal Trends: feature evolution (line) + explicit share (stacked area)

**Goal:** on a new **Temporal Trends** page — (a) a multi-line chart of mean audio features by
release year, and (b) a 100% stacked area of explicit share by release year.
**Acceptance (todo.md D3):** line of avg(danceability/energy/acousticness/valence) by release
year; stacked area of explicit share by release year (or year-quarter); line endpoints match
the `Avg <feature>` measures.

### Grain decision (from the data) — **release YEAR**, restricted to ≥ 2010

80.9% of tracks released 2023–2025, thin tail to 1900; every year 2010–2025 has ≥100 tracks,
pre-2010 < 100. So **year** is the primary axis (filter `release_year ≥ 2010` → 16 clean
points). **Year-quarter is too sparse for older years** — use it only as an **optional drill on
2023–2025** (10 quarters), where it exposes the 2023-Q4 explicit spike (28%→44%) the annual view
hides.

### ✅ Modeling decision — RESOLVED (2026-06-01): Approach B implemented

> **`release_year` + `release_quarter` are now on `dim_track`** (pipeline regenerated — re-run
> `make build` and **Refresh** in Power BI to pick up the two new columns + `corr_audio_features.csv`).
> The build steps below work as written. The approaches are kept below for the record.

`release_date` lives on `dim_album`; features/`explicit` live on `dim_track`. With the model's
single-direction Dim→Fact relationships, **you cannot group a `dim_track` measure by a
`dim_album` attribute directly** (the album filter reaches the fact but not `dim_track`). Two
fixes:

**Approach B — denormalize (CHOSEN & IMPLEMENTED).** `release_year` (int) and `release_quarter`
(text, e.g. `2024-Q1`) are now built onto **`dim_track`** by `build_dim_track` (from the track's
earliest album `release_date`). Everything below is a trivial single-table group-by and
**reuses existing measures** (`Avg Danceability/Energy/Valence/Acousticness`, `% Explicit`,
`Tracks`). Additive columns — does not break D1/D2/D4. Also unblocks D5's "by release-year bucket". ✅ Done.

**Approach A — DAX only (fallback, no pipeline change).** Add a calc column on `dim_album`
(`release_year = YEAR(dim_album[release_date])`, since Auto date/time is off), and author new
measures that hop through the fact:
```DAX
Avg Energy (by release) =
AVERAGEX(SUMMARIZE(Fact_TrackSnapshot, dim_track[track_key], dim_track[energy]), dim_track[energy])
```
(…one per feature, plus an explicit-share variant). More measures, more complex DAX; use only if
a pipeline rebuild is undesirable.

> The steps below use **Approach B** (now implemented). Approach A is retained only as the
> no-rebuild alternative; you should not need it.

### Measures
**Approach B: none new** — reuse `Avg Danceability`, `Avg Energy`, `Avg Valence`,
`Avg Acousticness`, `% Explicit`, `Tracks`. (Approach A: ~5 new `(by release)` measures.)

### Step 1 — new page
Add a report page, rename it **"Temporal Trends"**.

### Step 2 — feature-evolution line chart (Chart 4)
1. Insert a **Line chart**.
2. **X axis**: `dim_track[release_year]`; add a visual-level filter `release_year ≥ 2010`.
3. **Y axis (Values)**: `Avg Danceability`, `Avg Energy`, `Avg Valence`, `Avg Acousticness`
   (four lines).
4. X axis → type **Categorical** (or Continuous), sorted ascending.
5. Format: Y range 0–1; distinct colorblind-safe colors per line; title
   **"Sonic character of charting tracks, by release year"**; data labels off.

### Step 3 — explicit-share stacked area (Chart 5)
1. Insert a **100% Stacked area chart**.
2. **X axis**: `dim_track[release_year]` (same `≥ 2010` filter).
3. **Legend**: `dim_track[explicit]` (True/False).
4. **Y axis (Values)**: `Tracks` (the 100%-stack normalises it to share).
5. Title **"Explicit share of charting tracks, by release year"**; explicit = accent hue.
6. *(Optional drill)* duplicate this visual, swap the axis to `dim_track[release_quarter]` and
   filter to 2023–2025 to surface the **2023-Q4 spike (≈44%)**.

### Step 4 — verify
Spot-check the latest-year points against these per-track means (release_year):

| release_year | Avg Dance | Avg Energy | Avg Valence | Avg Acoustic | % Explicit |
|---|---|---|---|---|---|
| 2010 | 0.618 | 0.688 | 0.616 | 0.267 | 5.4% |
| 2020 | 0.652 | 0.580 | 0.513 | 0.385 | 18.9% |
| 2023 | 0.691 | 0.652 | 0.533 | 0.269 | 37.3% |
| 2024 | 0.685 | 0.660 | 0.530 | 0.260 | 37.8% |
| 2025 | 0.673 | 0.673 | 0.517 | 0.243 | 38.4% |

Pass: the 2025 endpoints match `Avg Danceability`≈0.673, `Avg Energy`≈0.673, `Avg Valence`≈0.517,
`Avg Acousticness`≈0.243 (filtered to release_year = 2025); explicit area climbs from ~5% (2010)
to ~38% (2024–2025).

### Step 5 — evidence
Export screenshots to `report/figures/d3_feature_evolution_line.png` and
`report/figures/d3_explicit_share_area.png`.

---

## D4 — Artists: top 20 horizontal bar

**Goal:** a horizontal bar of the top 20 artists by chart presence, with a time slicer, on a new
**Artists** page.
**Acceptance (todo.md D4):** top-20 horizontal bar by aggregate popularity (or row count); time
slicer; top-1 matches the profiled leader.

### Metric decision (from the data) — rank by **chart appearances** (`Snapshots`)

Ranking metrics disagree, and the choice *is* the analytical point:
- **Chart appearances (`Snapshots`)** / **total popularity (`SUM`)** → **Bad Bunny #1** — the
  right "dominance" metric (breadth × persistence). The two give the same order.
- **Avg popularity** → floats seasonal/one-hit artists (Mariah Carey 93, Arctic Monkeys 92) — wrong question.
- **Raw track count** → surfaces prolific-but-niche regional artists (Kelvin Momo 66 tracks, ~970 appearances) — wrong question.

Use **`Snapshots`** (concrete: "appearances on a national daily top-50"); offer `Total
Popularity` as the literal SPEC "aggregate popularity" reading (same ranking).

### Measures
**`Snapshots` already exists** (added for D1 — reuse it). *Optional:* add `Total Popularity`
(`measures.md` → Phase D additions) if you want the literal "aggregate popularity" label. **No
schema/pipeline change.**

### Step 1 — new page
Add a report page, rename it **"Artists"**.

### Step 2 — horizontal bar
1. Insert a **Clustered bar chart** (horizontal).
2. **Y axis**: `dim_artist[artist_name]`.
3. **X axis (Values)**: `Snapshots` (or `Total Popularity`).
4. **Filters → `artist_name` (visual-level)**: filter type **Top N**, **Top 20**, **By value =
   `Snapshots`**.
5. Sort the visual by `Snapshots` **descending** (longest bar on top).

### Step 3 — time slicer
Add a **Slicer** → field `dim_date[year]` (or a `dim_date[date]` *Between* slicer). It filters
the fact, so the top-20 recomputes for the chosen window. *(Note: this is the **snapshot/chart**
date — "who charted most in this period" — not release date.)*

### Step 4 — format
- Title **"Top 20 artists by chart appearances"**; X-axis title **"Chart appearances"**.
- Data labels on (the magnitudes matter); single colorblind-safe hue; remove the legend.
- Y-axis: no title; let names fill the rows.

### Step 5 — verify
Top-1 (unfiltered) must be **Bad Bunny**. Expected top-8 by `Snapshots` (full snapshot):

| Artist | Chart appearances | Distinct tracks |
|---|---|---|
| **Bad Bunny** | **51,567** | 50 |
| Billie Eilish | 32,654 | 17 |
| KAROL G | 30,757 | 33 |
| Feid | 29,643 | 42 |
| Sabrina Carpenter | 29,045 | 24 |
| Taylor Swift | 21,640 | 100 |
| The Weeknd | 21,599 | 34 |
| Jimin | 20,391 | 24 |

Pass: Bad Bunny tops the bar at ~51.6k; the bar is sorted strictly descending. (Switching the
measure to `Tracks` should instead put **Taylor Swift** #1 at 100 — a quick way to demo the
metric-choice point.)

### Step 6 — evidence
Export a screenshot to `report/figures/d4_top_artists_bar.png`.

---

## D5 — Audio Anatomy: correlation heatmap + box plot

**Goal:** on a new **Audio Anatomy** page — (a) a 9×9 audio-feature correlation heatmap, and
(b) a box plot of one feature by release-year bucket.
**Acceptance (todo.md D5):** pairwise-Pearson matrix (or Python visual); box plot by group;
verify the diagonal = 1.0 and the matrix is symmetric.

### Part A — Correlation heatmap (Chart 7) — ready to build

**Decision (2026-06-01): Approach 2 (precomputed CSV) chosen & IMPLEMENTED** — the pipeline now
writes `data/processed/corr_audio_features.csv` (81 rows: `feature_x`, `feature_y`, `r`).
Build steps:

1. After `make build` + Refresh, load the new query and confirm the table **`corr_audio_features`**
   is in the model (add it via the `pProcessedFolder` parameter like the other CSVs — see
   `power_query.md`; promote headers; types: `feature_x`/`feature_y` text, `r` decimal).
2. Insert a **Matrix** visual → **Rows** = `feature_x`, **Columns** = `feature_y`,
   **Values** = `r` (set the value aggregation to **Average** — one row per pair, so it's a no-op).
3. **Format → Cell elements → Background color → fx** → gradient on `r`, diverging
   (−1 = blue, 0 = white, +1 = red); optionally show `r` to 2 decimals as the cell text.
4. Title "Audio-feature correlation".

Alternatives (not used):
- **Approach 1 — Python/R visual.** Drop a Python visual, add the 9 `dim_track` feature columns,
  `sns.heatmap(dataset.corr(), annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1)`. Requires
  Python (pandas+seaborn) in Power BI Desktop.
- **Approach 3 — DAX measure matrix (native, clumsy).** Unpivoted feature table on both axes +
  a Pearson-`r` SUMX measure. Fiddly; SPEC allows skipping it.

**Verify (any approach)** against this matrix (Pearson r, n = 24,976; **diagonal = 1.0,
symmetric**):

|              | dance | energy | val | tempo | acoust | live | speech | instr | loud |
|---|---|---|---|---|---|---|---|---|---|
| **dance**    | 1.00 | 0.17 | 0.36 | -0.11 | -0.24 | -0.12 | 0.15 | -0.04 | 0.15 |
| **energy**   | 0.17 | 1.00 | 0.35 | 0.12 | **-0.50** | 0.15 | 0.01 | -0.14 | **0.70** |
| **valence**  | 0.36 | 0.35 | 1.00 | 0.05 | -0.09 | 0.03 | 0.04 | -0.09 | 0.25 |
| **tempo**    | -0.11 | 0.12 | 0.05 | 1.00 | -0.09 | 0.02 | 0.02 | 0.01 | 0.07 |
| **acoust**   | -0.24 | -0.50 | -0.09 | -0.09 | 1.00 | -0.04 | -0.03 | 0.03 | -0.33 |
| **live**     | -0.12 | 0.15 | 0.03 | 0.02 | -0.04 | 1.00 | 0.03 | -0.04 | 0.09 |
| **speech**   | 0.15 | 0.01 | 0.04 | 0.02 | -0.03 | 0.03 | 1.00 | -0.08 | -0.04 |
| **instr**    | -0.04 | -0.14 | -0.09 | 0.01 | 0.03 | -0.04 | -0.08 | 1.00 | -0.35 |
| **loud**     | 0.15 | 0.70 | 0.25 | 0.07 | -0.33 | 0.09 | -0.04 | -0.35 | 1.00 |

Sanity: strongest cell is energy×loudness (+0.70); energy×acousticness (−0.50) is the strongest
negative. Export → `report/figures/d5_correlation_heatmap.png`.

### Part B — Box plot by group (Chart 8) — feature/buckets chosen; needs a box-plot visual

**Feature: `acousticness`** (chosen for the largest, cleanest dispersion change — see below).
**Buckets:** 5, all well-populated (`≤2019`=3,129 · `2020-22`=1,630 · `2023`=4,693 · `2024`=10,867 · `2025`=4,652).

1. ✅ **Release-year bucket** — `dim_track[release_year]` exists. Add this calc column:
   ```DAX
   Release bucket =
   SWITCH(TRUE(),
       ISBLANK(dim_track[release_year]), "Unknown",
       dim_track[release_year] >= 2025, "2025",
       dim_track[release_year] >= 2024, "2024",
       dim_track[release_year] >= 2023, "2023",
       dim_track[release_year] >= 2020, "2020-22",
       "2019 & earlier")
   ```
   Filter out `"Unknown"` (5 tracks). The labels sort chronologically as-is.
2. **Install the box-plot visual.** Visualizations pane → **··· → Get more visuals** → search
   **"Box and Whisker chart"** (MAQ Software) → **Add**.
3. **Field wells — this is where the first attempt went wrong: do NOT put `acousticness` on the
   axis.** A box plot has no "count" axis; if you see `Count of track_key` you built a histogram.
   - **Category** = `Release bucket`  ← the 5 groups along the X axis
   - **Sampling** = `dim_track[track_key]`  ← one observation per track (sets the granularity)
   - **Value** = `acousticness`  (aggregation **Average** / Don't summarize — one value per track)

   The visual then draws **one box per bucket** (median + IQR + whiskers + outliers). Title
   "Acousticness by release-year bucket".

**Verify** (acousticness median / IQR per bucket): `≤2019` 0.252 / 0.466 · `2020-22` 0.298 / 0.483
· `2023` 0.194 / 0.350 · `2024` 0.184 / 0.343 · `2025` 0.166 / 0.321. The boxes should **drop and
shrink** from 2023 on (median ↓, IQR ↓). Survivorship caveat: the two oldest buckets are thin.

*(Alternative feature `speechiness` — opposite story, IQR 0.03→0.13, Q3 0.07→0.18 — if you'd
rather show a widening distribution.)* Export → `report/figures/d5_feature_boxplot.png`.
