# `documents/` — Course materials & data-visualization theory

Drop the course slides, lecture notes, and reading PDFs into this folder. Everything here (except this README) is **gitignored** — most course materials are copyrighted and shouldn't be committed to a public repo.

## What belongs here

- Lecture slides (PDF / PPTX)
- Required readings (e.g., Tufte, Cleveland & McGill, Bertin, Few, Munzner — whichever your course assigns)
- Course handouts
- Anything that will be cited in `report/chart_justifications.md`

## Suggested theory anchors to look for in your slides

The chart-justification rubric in `SPEC.md §8` expects each chart to cite at least one principle. Common anchors:

| Anchor | Use it to justify… |
|---|---|
| **Cleveland & McGill** perceptual hierarchy (1984) | Why position-on-common-scale beats length, beats angle, beats color for quantitative comparison |
| **Bertin** visual variables | Which variable (position, size, value, color hue, etc.) you mapped each data attribute to |
| **Tufte** data-ink ratio | Stripping non-data ink, avoiding chartjunk |
| **Mackinlay's APT ranking** | Automatic ranking of encodings for quantitative / ordinal / nominal data |
| **Few** dashboard design | Pre-attentive attributes, signal vs. noise on dashboards |
| **Munzner** nested model / task taxonomy | What task the chart supports (identify, compare, locate, etc.) |
| **Cairo** functional / beautiful / insightful / enlightening | Holistic critique framing |

## File naming suggestion

`L01_introduction.pdf`, `L02_perception.pdf`, `reading_cleveland_mcgill_1984.pdf` — anything that makes citations like *(documents/L02_perception.pdf, slide 14)* easy to write later.
