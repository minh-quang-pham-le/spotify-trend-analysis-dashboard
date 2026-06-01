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
