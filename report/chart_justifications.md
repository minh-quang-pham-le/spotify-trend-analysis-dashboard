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

*TODO during Implement phase.*

### Chart 3 — Energy × Valence mood map (scatter)

*TODO during Implement phase. Anchor: Cleveland & McGill — position on a common scale ranks first for quantitative comparison.*

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
