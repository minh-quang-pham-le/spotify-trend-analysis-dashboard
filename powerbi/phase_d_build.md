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
