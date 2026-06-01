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

**Dashboard page:** Temporal Trends · task **D3**
**File reference:** `dashboard.pbix` → page "Temporal Trends" → visual "Feature evolution by release year"

**1. Question answered.**
How has the sonic character of charting music evolved, by track **release year**?

**2. Chart type & encoding.**
- Chart type: **multi-series line chart** (one line per audio feature).
- X axis: release **year** → horizontal **position** (ordered/time).
- Y axis: mean feature value, 0–1 → vertical **position** on a common scale.
- Color: feature name (danceability / energy / valence / acousticness) → categorical hue (≤4 series, colorblind-safe).
- Restrict the axis to **release_year ≥ 2010** (every such year has ≥100 tracks; pre-2010 is too sparse).

**3. Theory citation.**
Position on a common scale (the most accurately decoded channel) carries both the time axis
and the magnitude; a connected line is the canonical idiom for a trend over an ordered domain.
> TODO: cite Cleveland & McGill (1984) — position along a common scale is the most accurate
> graphical-perception task. — *documents/<cleveland-mcgill>.pdf, slide N*
> TODO: cite Bertin / Munzner — line marks over an ordered (time) key encode trend; the
> *connection* invites reading slope/change. — *documents/<bertin-or-munzner>.pdf, slide N*

**4. Alternatives considered and rejected.**
- **Stacked area of the four features** — would imply the features sum to a meaningful whole; they don't (each is an independent 0–1 score), so stacking is semantically false.
- **Grouped bars per year** — 16 years × 4 features = 64 bars; the trend (the question) is far harder to read than four lines.
- **Small multiples (one mini-line per feature)** — viable, and a good fallback if the four lines overlap too much, but it sacrifices direct cross-feature comparison at a given year.

**5. Trade-offs accepted.**
- **Survivorship / recency bias (important).** These are tracks *charting in 2023–2025*, so pre-2023 points are catalogue *survivors* (classics still charting), **not** a representative sample of their era. The chart shows "the sonic profile of today's charting tracks, by release year" — not "how all music changed." 80.9% of tracks are 2023–2025; older years are thin. State this in the report.
- **Line overlap.** danceability/energy/valence/acousticness can cross; mitigate with distinct colors + tooltips, or switch to small multiples if cluttered.
- Only the **[0,1] ratio features** share this axis; `tempo` (BPM) and `loudness` (dB) are excluded (different scales) — they belong on the Audio Anatomy page.

**Evidence & report talking points (per-distinct-track means by release year):**
- **Danceability rose** ~0.60 (2011) → **0.68–0.69** (2023–2025).
- **Valence (positivity) fell** 0.62 (2010) → **~0.51–0.53** (2017–2025), then plateaued — charting music got modestly *less* upbeat over the 2010s.
- **Acousticness is lowest in the newest releases** (0.243 in 2025 vs ~0.27–0.39 earlier) — more produced/electronic.
- **Energy is U-shaped, not a clean trend** — 0.69 (2010) → dip ~0.58 (2020) → 0.67 (2025); rebuts a simple "music is getting calmer" narrative.

### Chart 5 — Explicit-share over time (stacked area)

**Dashboard page:** Temporal Trends · task **D3**
**File reference:** `dashboard.pbix` → page "Temporal Trends" → visual "Explicit share by release year"

**1. Question answered.**
Is explicit content becoming more dominant among charting tracks, by release year?

**2. Chart type & encoding.**
- Chart type: **area chart of `% Explicit`** — the leaner single-series variant (see
  alternatives), which is **what the dashboard implements**. *(SPEC §8 names a 2-class stacked
  area; a single `% Explicit` area shows the same information since non-explicit = 100% − explicit.)*
- X axis: release **year** → position (ordered/time).
- Y axis: `% Explicit` (0–100%) → height of the filled area.

**3. Theory citation.**
Part-to-whole composition over an ordered (time) domain is the canonical use of a stacked area;
the baseline series is read by position, the band thickness by length.
> TODO: cite Few / Munzner — stacked area for part-to-whole evolution over time; caution that
> only the bottom band has a stable baseline. — *documents/<few-or-munzner>.pdf, slide N*

**4. Alternatives considered and rejected.**
- **Pie chart per year** — destroys the trend (the actual question); 16 pies can't be compared.
- **Single line of `% Explicit`** — leaner and arguably clearer (the split is one number); we keep the stacked area per SPEC §8, but a `% Explicit` line is the recommended companion / tooltip.
- **Clustered bars (explicit vs non-explicit count) per year** — emphasises raw counts (dominated by 2024) over the *share* trend we care about.

**5. Trade-offs accepted.**
- **Two-class stacked area is partly redundant** (non-explicit = 100% − explicit); mitigated by also reporting the `% Explicit` value. 
- **Survivorship bias** (same as Chart 4) — pre-2023 explicit shares come from few, survivor tracks.
- **Annual grain hides a sub-year spike** — see talking point below; offer a **year-quarter drill on 2023–2025** to reveal it.

**Evidence & report talking points (share of distinct tracks that are explicit, by release year):**
- **Explicit share roughly 7×'d**: ~5–8% (2010–2013) → ~15–23% (2017–2022) → **~37–38% (2023–2025)**.
- **The jump is concentrated at 2022→2023** (21% → 37%) — a step change, not a gradual climb.
- **Quarterly reveals a 2023-Q4 spike**: 2023-Q3 = 28% → **2023-Q4 = 44%** → settles ~37–39%. The annual 2023 figure (37%) averages this away — a genuinely non-obvious finding worth a sentence in the report (and a reason to keep the optional quarterly view).

### Chart 6 — Top 20 artists (horizontal bar)

**Dashboard page:** Artists · task **D4**
**File reference:** `dashboard.pbix` → page "Artists" → visual "Top 20 artists"

**1. Question answered.**
Who dominates the chart-track set — which artists appear on the charts most?

**2. Chart type & encoding.**
- Chart type: **horizontal bar chart**, top 20 artists (Top-N filter).
- Y axis: `artist_name` → categorical rows, **sorted by the measure descending**.
- X axis: **chart appearances** (`Snapshots`) → bar **length** on a common aligned scale.
- Slicer: time period (`dim_date[date]` range or `dim_date[year]`) so "top artists" can be scoped to a window.
- Horizontal (not vertical) so the long artist names are legible without rotation.

**3. Theory citation.**
Ranking by magnitude across many categories is exactly what bar length on a common scale does
best — position/length is the most accurately decoded encoding, and sorting turns the chart into
a rank.
> TODO: cite Cleveland & McGill (1984) / Mackinlay — length on an aligned scale is top of the
> perceptual hierarchy for quantitative comparison. — *documents/<cleveland-mcgill>.pdf, slide N*
> TODO: cite Few — use **horizontal** bars for long category labels and ranked lists.
> — *documents/<few-show-me-the-numbers>.pdf, page N*

**4. Alternatives considered and rejected.**
- **Pie / treemap of artist share** — part-to-whole; terrible for *ranking* 20 items and comparing close magnitudes (area/angle rank low perceptually).
- **Word cloud of artist names** — sizes text by frequency but has no aligned scale; decorative, not measurable.
- **Vertical column chart** — 20 long artist names force rotated/truncated labels; horizontal bars read top-to-bottom like a leaderboard.

**5. Trade-offs accepted.**
- **Metric choice matters — and is the finding.** We rank by **chart appearances** (≈ total
  popularity, which gives the same order), *not* by average popularity (which floats seasonal /
  one-hit artists — Mariah Carey 93, Arctic Monkeys 92 — to the top) nor by raw track count
  (which surfaces prolific-but-niche regional artists — Kelvin Momo 66 tracks but only ~970
  appearances). Dominance must combine breadth × persistence; appearances/total-popularity
  capture that, the others don't.
- **Primary-artist-only.** `artist_key` credits the *primary* artist; featured artists on the
  40.7% multi-artist tracks are undercounted (known model limitation — see `data_model.md`).
- **Top-20 truncation** hides the long tail by design (the question is about dominators); the
  cut is honest because it's a ranked list, not a part-to-whole.

**Evidence & report talking points (per primary artist, full snapshot):**
- **Bad Bunny is the clear #1** — **51,567 chart appearances** (≈1.6× the #2), **50** distinct
  charting tracks, avg popularity 90. Latin/reggaetón is strongly over-represented in the top
  ranks (Bad Bunny, KAROL G, Feid, Blessd).
- Top-5 by appearances: **Bad Bunny, Billie Eilish, KAROL G, Feid, Sabrina Carpenter**.
- **Taylor Swift's catalogue breadth stands out** — **100** distinct charting tracks, ~2× any
  other top artist (deep back-catalogue charting, not just current singles).
- **Methodological talking point:** "biggest artist" is metric-dependent — appearances → Bad
  Bunny; track count → Taylor Swift; average popularity → Billie Eilish / Mariah Carey. Naming
  the metric is part of the answer.

### Chart 7 — Audio-feature correlation matrix (heatmap)

**Dashboard page:** Audio Anatomy · task **D5**
**File reference:** `dashboard.pbix` → page "Audio Anatomy" → visual "Feature correlation heatmap"

**1. Question answered.**
Which audio features co-vary, and are any redundant?

**2. Chart type & encoding.**
- Chart type: **correlation heatmap** (9×9 matrix over the audio features).
- Rows & columns: the 9 features (danceability, energy, valence, tempo, acousticness, liveness, speechiness, instrumentalness, loudness) → categorical position.
- Cell **color**: Pearson *r* on a **diverging** scale (−1 blue ↔ 0 white ↔ +1 red).
- Cell **label**: the numeric *r* (compensates for color's low decoding accuracy).

**3. Theory citation.**
This is a deliberate **trade-off**: color ranks low in the perceptual hierarchy, but for an
all-pairs overview (81 cells) a position/length encoding would explode; the heatmap is the
standard idiom for the "find the strong cells" gestalt task, and numeric labels restore precision.
> TODO: cite Cleveland & McGill — color/saturation are low-accuracy; acceptable here because the
> task is pattern-spotting, not precise readout. — *documents/<cleveland-mcgill>.pdf, slide N*
> TODO: cite Munzner — matrix view as the idiom for dense pairwise relationships.
> — *documents/<munzner>.pdf, slide N*

**4. Alternatives considered and rejected.**
- **Scatterplot matrix (SPLOM)** — shows the raw joint distributions but 9×9 = 36 off-diagonal panels is far too dense for a dashboard tile.
- **Table of correlation numbers** — exact but gives no gestalt; you can't *see* the clusters.
- **Network/force graph of correlations** — pretty but imprecise and hard to read exact pairs.

**5. Trade-offs accepted.**
- **Color imprecision** — mitigated with on-cell numeric labels.
- **Pearson captures only *linear* association** — a strong non-linear relationship would read as weak; note this in the report.
- Computed over **distinct tracks** (`dim_track`), not snapshots, so it describes the catalogue, not chart-weighted exposure.

**Evidence & report talking points (Pearson r, n = 24,976 distinct tracks; matrix verified symmetric, diagonal = 1.0):**
- **energy ↔ loudness = +0.70** — by far the strongest pair; the two are **near-redundant** (louder = more energetic). A dimension-reduction angle for the report: one could drop `loudness` from feature panels with little information loss.
- **energy ↔ acousticness = −0.50** (and acousticness ↔ loudness = −0.33): the clearest semantic axis — *acoustic ↔ produced/loud*.
- **valence ↔ danceability = +0.36, valence ↔ energy = +0.35**: "happier" tracks are modestly more danceable and energetic.
- **Most pairs are weak (|r| < 0.25)** — `tempo`, `speechiness`, `liveness`, `instrumentalness` are largely orthogonal to the rest → the audio-feature space is **genuinely multidimensional** (justifies using several features rather than collapsing to one).

### Chart 8 — Feature distribution by group (box / violin)

**Dashboard page:** Audio Anatomy · task **D5**
**File reference:** `dashboard.pbix` → page "Audio Anatomy" → visual "Feature dispersion by release-year bucket"

**1. Question answered.**
How does the *dispersion* (not just the mean) of a chosen feature change across groups? Groups =
**release-year buckets** (the source has no genre — SPEC §8 substitution).

**2. Chart type & encoding.**
- Chart type: **box plot** (or violin), one box per release-year bucket.
- X axis: release-year bucket (e.g., `≤2019`, `2020–2022`, `2023`, `2024`, `2025`) → categorical position.
- Y axis: **acousticness** (chosen — largest dispersion change across buckets) → position; box = IQR + median, whiskers, outlier dots.

**3. Theory citation.**
> TODO: cite Tukey / Munzner — the box plot is the canonical idiom for comparing a distribution's
> spread and skew across groups. — *documents/<munzner-or-few>.pdf, slide N*

**4. Alternatives considered and rejected.**
- **Bar of group means** — hides dispersion, which *is* the question.
- **Violin plot** — richer (shows multimodality) but heavier; a fallback if the box hides shape.
- **Jittered strip plot** — overplots badly at ~25k tracks.

**5. Trade-offs accepted.**
- **No native box plot** — needs a custom visual (AppSource "Box & Whisker", MAQ) or a Python/R
  visual; that's the only remaining build dependency (the `release_year` bucket is now on
  `dim_track`, so the data side is unblocked).
- **Survivorship bias** — the `≤2019` and `2020-22` buckets are thin survivor tracks, not
  era-representative; state it on the chart.
- **Skew** — a right-skewed feature (e.g. speechiness) squashes the box near 0 with a long
  outlier tail; **acousticness is well-spread, so its box reads cleanly** — part of why it was chosen.

**Chosen feature & evidence (acousticness, by release-year bucket — median / IQR):**
`≤2019` 0.252 / 0.466 · `2020-22` 0.298 / 0.483 · `2023` 0.194 / 0.350 · `2024` 0.184 / 0.343 ·
`2025` 0.166 / 0.321. **Story:** charting music's acousticness has both **fallen** (median
0.25 → 0.17) **and narrowed** (IQR 0.47 → 0.32) — older charting tracks ranged from acoustic
ballads to electronic, while 2024–25 hits cluster tightly at low acousticness (more uniformly
produced / electronic). Coheres with the heatmap's energy↔acousticness = −0.50 and the D3
falling-acousticness line. **Alternative feature — speechiness** tells the *opposite* (widening)
story: IQR 0.03 → 0.13, Q3 quadrupling (0.07 → 0.18) as rap/spoken content entered the charts;
pick it instead if you'd rather show a *spreading* distribution.

### Chart 9 — Geographic map (filled map)

*TODO during Implement phase. Only if multi-country dimension is in scope.*

### Chart 10 — Top-artist sonic signature (small multiples / radar)

*TODO during Implement phase.*

---

## Cross-cutting design choices

Document one-offs here (color palette, font, layout grid, accessibility considerations) with a single theory citation each.
