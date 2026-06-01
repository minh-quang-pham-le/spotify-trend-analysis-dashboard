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

### ⚠ Modeling decision (PENDING — pick one before building)

`release_date` lives on `dim_album`; features/`explicit` live on `dim_track`. With the model's
single-direction Dim→Fact relationships, **you cannot group a `dim_track` measure by a
`dim_album` attribute directly** (the album filter reaches the fact but not `dim_track`). Two
fixes:

**Approach B — denormalize (RECOMMENDED).** Add `release_year` (int) and `release_quarter`
(text, e.g. `2024-Q1`) to **`dim_track`** in the pipeline (`build_dim_track`, from the track's
earliest album `release_date`). Then everything below is a trivial single-table group-by and
**reuses existing measures** (`Avg Danceability/Energy/Valence/Acousticness`, `% Explicit`,
`Tracks`). Cost: re-run `make build` + Refresh (additive columns — does not break D1/D2). Also
unblocks D5's "by release-year bucket". *Requires team OK — schema/`data_model.md` change.*

**Approach A — DAX only (fallback, no pipeline change).** Add a calc column on `dim_album`
(`release_year = YEAR(dim_album[release_date])`, since Auto date/time is off), and author new
measures that hop through the fact:
```DAX
Avg Energy (by release) =
AVERAGEX(SUMMARIZE(Fact_TrackSnapshot, dim_track[track_key], dim_track[energy]), dim_track[energy])
```
(…one per feature, plus an explicit-share variant). More measures, more complex DAX; use only if
a pipeline rebuild is undesirable.

> The steps below assume **Approach B**. For A, swap `dim_track[release_year]` → the
> `dim_album` calc column and the `Avg <feature>` measures → the `(by release)` measures.

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
