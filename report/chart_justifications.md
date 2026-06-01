# Chart Justifications

Every chart in the dashboard gets one section here. Each section follows the rubric defined in `SPEC.md §8`:

1. **Question answered** — what user task does this chart support?
2. **Chart type** — what kind of chart, and what visual encoding does it use?
3. **Theory citation** — at least one principle from `documents/` (Cleveland & McGill, Bertin, Tufte, Mackinlay, Few, Munzner, Cairo, etc.) with file + slide/page reference.
4. **Alternatives considered and rejected** — at least two other chart types we evaluated and why each is worse.
5. **Trade-offs accepted** — what does this chart fail at, and how do we mitigate it elsewhere?

---

## Template (copy this for each new chart)

```markdown
### Chart N — [Short title]

**Dashboard page:** [page name]
**File reference:** `dashboard.pbix` → page "[…]" → visual "[…]"

**1. Question answered.**
[One sentence — what does the user learn from this chart?]

**2. Chart type & encoding.**
- Chart type: [scatter / bar / line / etc.]
- X axis: [data attribute → visual variable]
- Y axis: [data attribute → visual variable]
- Color: [data attribute → palette]
- Size: [data attribute → scale]

**3. Theory citation.**
[Principle, attributed source, location in documents/]
> "Quote or paraphrase."
— *documents/[filename].pdf, slide N* (or page N)

**4. Alternatives considered and rejected.**
- **[Alt 1]** — [why it's worse for this task]
- **[Alt 2]** — [why it's worse for this task]

**5. Trade-offs accepted.**
[Honest description of what this chart fails at, and where in the dashboard we cover that gap.]
```

---

## Charts (to be filled in as the dashboard is built)

### Chart 1 — Topline KPI cards

*TODO during Implement phase.*

### Chart 2 — Popularity distribution histogram

**Dashboard page:** Overview (alongside the KPI cards) · task **D1**
**File reference:** `dashboard.pbix` → page "Overview" → visual "Popularity histogram"

**1. Question answered.**
Is Spotify `popularity` uniformly spread, or concentrated/long-tailed across the tracks
that chart? (Answer from the data: **not uniform — strongly left-skewed toward high
values.** See §"Distribution evidence" below.)

**2. Chart type & encoding.**
- Chart type: **histogram** (clustered column chart over a binned quantitative axis).
- X axis: `popularity` bucketed into 10 equal-width bins of 10 (`[0,10) … [90,100]`) → horizontal position (ordered).
- Y axis: count of chart snapshots (`Snapshots` measure) → bar **length** on an aligned scale.
- Color: single colorblind-safe hue (see *Cross-cutting design choices*); no color encoding — one variable only.

**3. Theory citation.**
The histogram is the canonical idiom for the *characterize-distribution* task over a single
quantitative attribute, and its encodings (position on a common scale + aligned length) are
the two most accurately decoded channels in the perceptual hierarchy.
> TODO: cite Munzner, *Visualization Analysis & Design* — "histogram … shows the distribution of a single quantitative attribute" (idiom for the *characterize distribution* task).
> — *documents/<munzner-or-course-slides>.pdf, slide N*
> TODO: cite Cleveland & McGill (1984) perceptual hierarchy — position/length rank above area, angle, and color for quantitative comparison.
> — *documents/<cleveland-mcgill-slides>.pdf, slide N*

**4. Alternatives considered and rejected.**
- **Box plot** — a compact five-number summary, but it *hides shape*: it would show the high median (79) and a long low whisker, yet conceal the heavy spike in the 80–90 bin and the small low-end bump at 0–10. Our question is explicitly about shape, so a box plot answers the wrong task.
- **Density / violin (KDE)** — smooths the counts behind a bandwidth choice and is not a native Power BI visual (needs a custom/Python visual); on an Overview page next to KPI cards, discrete bars are more legible and reproducible.
- **A single "Avg Popularity" card** — already on the page (75.9). It *collapses* the distribution to one number and hides the left skew; the histogram earns its space precisely because the mean conceals the spread (p05=49, p95=96).

**5. Trade-offs accepted.**
- **Unit of analysis.** This histogram counts **chart snapshots** (track × country × day), so it over-weights songs that chart in many countries for many days — the bars describe *chart-appearance frequency*, not the distinct-track catalogue. The distinct-track distribution sits far lower (mean ≈ 52.8, median ≈ 55.7). Mitigation: label the axis/tooltip "chart snapshots", and report the track-level framing in the Findings section (and optionally as a drill-through). *(Decision 2026-06-01: snapshot-level chosen for the Overview, for consistency with the Avg Popularity KPI; the track-level catalogue variant is documented in `powerbi/phase_d_build.md` for a possible separate page.)*
- **Binning** (width 10) hides within-bin structure and within-track variation (median popularity spread per track is 10 points, p90 is 51). Acceptable for an at-a-glance Overview shape; finer dispersion analysis lives on the Audio Anatomy page (Chart 8).

**Distribution evidence (from `data/processed/fact_track_snapshot.csv`, 2025-06-11 snapshot):**
snapshot-level mean = 75.9, median = 79, skew = −1.10; bin shares —
`[0,10)` 0.6% · `[10,20)` 0.1% · `[20,30)` 0.2% · `[30,40)` 0.7% · `[40,50)` 3.5% ·
`[50,60)` 10.8% · `[60,70)` 16.1% · `[70,80)` 18.2% · `[80,90)` 29.8% · `[90,100]` 19.2%.
The Power BI histogram should reproduce these proportions (the D1 verification check).

### Chart 3 — Energy × Valence mood map (scatter)

**Dashboard page:** Mood Map · task **D2**
**File reference:** `dashboard.pbix` → page "Mood Map" → visual "Energy × Valence scatter"

**1. Question answered.**
Where in the energy–valence ("mood") plane do tracks sit, and do *popular* tracks occupy a
distinct region? (Answer from the data: **no** — popularity barely correlates with valence
(r = 0.08) or energy (r = 0.05); popular tracks are spread across the plane, only marginally
above the overall mean. See §"Clustering evidence".)

**2. Chart type & encoding.**
- Chart type: **scatter plot**, one mark per distinct track (`dim_track[track_key]` in Details).
- X axis: `Avg Valence` (0–1) → horizontal **position** on a common scale.
- Y axis: `Avg Energy` (0–1) → vertical **position** on a common scale.
- Color: `Avg Popularity` (0–100) → sequential color **gradient** (secondary / overview channel).
- Size: **none** — the source has no stream counts (SPEC §8); a `duration_ms` size channel was
  rejected as a low-value area encoding (see alternatives).
- Tooltip: track name, primary artist, Avg Popularity, Avg Valence, Avg Energy.

**3. Theory citation.**
The question is fundamentally *spatial* ("where in the plane"), so both quantitative variables
map to the **position** channels — the most accurately decoded encoding in the perceptual
hierarchy — while popularity, a secondary overlay, takes color (lower in the hierarchy, but
adequate for the gestalt judgement "are the bright marks clustered?").
> TODO: cite Cleveland & McGill (1984) — position along a common scale is the most accurately
> decoded graphical-perception task; color/saturation rank far lower.
> — *documents/<cleveland-mcgill-slides>.pdf, slide N*
> TODO: cite Bertin — X and Y are the two planar visual variables; using both for the primary
> quantities is the canonical encoding of a 2-D relationship.
> — *documents/<bertin-slides>.pdf, slide N*

**4. Alternatives considered and rejected.**
- **Two separate histograms (valence, energy)** — show each marginal distribution but destroy
  the *joint* structure; you couldn't tell whether high-energy tracks are also high-valence,
  which is the entire point of a mood plane.
- **2-D density heatmap / hexbin** — handles 25k-point overplotting better, but hides
  individual tracks (no tooltip drill-down) and is not a native Power BI visual; we instead
  accept overplotting via marker transparency + high-density sampling.
- **Adding size = `duration_ms`** — area ranks low in the perceptual hierarchy and duration is
  tangential to the mood question; it would add ink without answering it.

**5. Trade-offs accepted.**
- **Overplotting & sampling.** 24,976 tracks exceed Power BI's scatter render cap (~10,000 with
  high-density sampling on), so the visual plots a representative *sample*, not every point. The
  cluster shape is preserved; the exact count comes from a `Tracks` card. Mitigation: marker
  transparency and an optional `Avg Popularity` slicer to focus on the popular subset (which
  also drops the plotted count under the cap).
- **Color is a weak quantitative channel.** Because popularity barely varies across the plane,
  the gradient reads as near-uniform — which is *itself the finding* (popularity is not
  regional). Color earns little here; the honest read is "position shows the mood spread; color
  shows popularity is not explained by mood."

**Clustering evidence (from `dim_track.csv` + per-track mean popularity over the fact):**
all 24,976 tracks have non-null valence & energy. Overall mean valence 0.533, energy 0.654.
By popularity band (mean valence, mean energy) — `<40`: (0.500, 0.637) · `40–60`: (0.540, 0.655)
· `60–75`: (0.547, 0.665) · `75+`: (0.547, 0.656). Correlation of mean popularity with valence
= 0.078, with energy = 0.045. Conclusion: popular tracks are **not** confined to a
high-energy/high-valence corner.

### Chart 4 — Temporal evolution of audio features (line)

*TODO during Implement phase. Anchor: Cleveland & McGill + Bertin — position over time encodes ordered quantitative change.*

### Chart 5 — Explicit-share over time (stacked area)

*TODO during Implement phase.*

### Chart 6 — Top 20 artists (horizontal bar)

*TODO during Implement phase. Anchor: Mackinlay — length on aligned scale ranks high for ordered categorical comparison.*

### Chart 7 — Audio-feature correlation matrix (heatmap)

*TODO during Implement phase. Anchor: trade-off — color is low in Cleveland & McGill but appropriate for a many-pair overview where position would explode.*

### Chart 8 — Feature distribution by group (box / violin)

*TODO during Implement phase.*

### Chart 9 — Geographic map (filled map)

*TODO during Implement phase. Only if multi-country dimension is in scope.*

### Chart 10 — Top-artist sonic signature (small multiples / radar)

*TODO during Implement phase.*

---

## Cross-cutting design choices

Document one-offs here (color palette, font, layout grid, accessibility considerations) with a single theory citation each.
