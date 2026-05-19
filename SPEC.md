# Spec: Spotify Music Trends 2024–2025 Power BI Dashboard

> Status: **Draft v1** — awaiting human review before proceeding to Plan / Tasks / Implementation.
> Owner: 5-member university team, Data Visualization course.
> Last updated: 2026-05-19.

---

## 1. Objective

### What we're building
A **Power BI dashboard** that explores popular-music trends on Spotify with a focus on **2024–2025** (and early 2026 where the source data permits), driven by a **Kaggle-sourced dataset** and a **reproducible Python pipeline** that emits Power BI-friendly star-schema CSVs.

### Why this scope (and why not the Spotify Web API)
The original brief proposed scraping the Spotify Web API via `spotipy`. During spec review we established a blocker:

> On **2024-11-27**, Spotify deprecated `GET /audio-features`, `GET /audio-analysis`, `GET /recommendations`, `GET /browse/featured-playlists`, `GET /browse/categories/{id}/playlists`, and `GET /artists/{id}/related-artists` for any **new** developer application.
> Source: Spotify Developer changelog, 2024-11-27.

Since the dashboard's analytical thesis hinges on **audio features** (danceability, energy, valence, tempo, acousticness, liveness, speechiness), and none of the team has confirmed grandfathered (pre-2024-11-27) app access, the API path is infeasible without abandoning the most academically interesting axis of analysis. **Decision: pivot to a Kaggle dataset that already contains audio features alongside chart/popularity data.**

### Target users
1. **Course instructor & TAs** — evaluating the final report, expect academic rigor and theory-grounded chart choices.
2. **Team members (5)** — collaborating in Power BI Desktop on Windows, possibly across machines.
3. **A reader of the final report** — should be able to reproduce every chart from the CSVs + a documented Power BI model.

### Success criteria (testable)
- [ ] One end-to-end Python pipeline run (`make build`) produces a `data/processed/` directory containing the star-schema CSVs from a fresh clone, with **zero manual steps** other than placing the raw Kaggle file(s) into `data/raw/`.
- [ ] Processed CSVs satisfy the star-schema contract: every foreign-key value in `Fact_TrackSnapshot` resolves to exactly one row in the corresponding dimension table (validated by `pytest`).
- [ ] No row in `Fact_TrackSnapshot` is missing `popularity` or `track_key`.
- [ ] Track-level deduplication uses **ISRC first, fallback to (track_name + primary_artist_name)** — never on track_name alone.
- [ ] The Power BI `.pbix` file imports all CSVs without Power Query errors and renders the dashboard pages.
- [ ] **Every chart** in the final dashboard has a written justification in `report/chart_justifications.md` that cites at least one source in `documents/`.
- [ ] The README enables a teammate to set up the project from scratch in ≤ 15 minutes.

---

## 2. Tech Stack

| Layer | Choice | Version | Why |
|---|---|---|---|
| Data source | **Kaggle CSV** (primary candidate: *Top Spotify Songs in 73 Countries – Daily* by Asaniczka; secondary: *Spotify Tracks Dataset* by maharshipandya) | latest snapshot at download time | Audio features + recent (2024) chart data |
| Pipeline language | **Python** | 3.11+ | Team familiarity, pandas ecosystem |
| Dataframe library | **pandas** | ≥ 2.2 | Standard for this scale (< 1M rows) |
| Validation | **pandera** *or* hand-written assertions in `tests/` | Choose at plan phase | Schema contracts for star schema |
| Testing | **pytest** | ≥ 8.0 | Industry standard |
| Lint/format | **ruff** | latest | One tool replaces flake8 + isort + black |
| Dependency mgmt | **uv** (preferred) or `pip` + `requirements.txt` | latest | uv is fast and reproducible; fall back to pip if any teammate can't install uv |
| Dashboard | **Power BI Desktop** (Windows, free) | 2.140+ (May 2025 build or newer) | Course requirement |
| Docs | Markdown | — | Renderable on GitHub and locally |

**Explicitly excluded:** `spotipy`, the Spotify Web API, SQL Server, Microsoft Fabric, any paid Power BI Service workspace, scheduled refresh.

---

## 3. Commands

All commands run from the repo root.

```bash
# One-time setup
uv venv && source .venv/bin/activate     # or: python -m venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"               # or: pip install -r requirements.txt

# Place the Kaggle CSV(s) into data/raw/ manually (see README §"Get the data")

# Build the star-schema CSVs from raw input
make build                               # = python -m src.pipeline

# Tests
make test                                # = pytest -q
make test-cov                            # = pytest --cov=src --cov-report=term-missing

# Lint + format
make lint                                # = ruff check src tests
make fmt                                 # = ruff format src tests

# Clean everything generated
make clean                               # removes data/interim, data/processed, __pycache__

# Quick exploratory profiling (optional)
make profile                             # = python -m src.profile  → prints schema + null counts of processed/
```

Windows teammates without `make` can run the equivalent `python -m …` commands directly; the README will list them.

---

## 4. Project Structure

```
spotify-trend-analysis-dashboard/
├── data/
│   ├── raw/               # Original Kaggle CSVs — gitignored, NEVER committed
│   ├── interim/           # Intermediate parquet/csv during pipeline — gitignored
│   └── processed/         # Final star-schema CSVs (committed if ≤ 25 MB total, else LFS)
│       ├── fact_track_snapshot.csv
│       ├── dim_track.csv
│       ├── dim_artist.csv
│       ├── dim_album.csv
│       ├── dim_date.csv
│       └── dim_country.csv  # only if using the 73-countries dataset
├── documents/             # Course slides, dataviz theory PDFs — populated by team
├── notebooks/             # Jupyter notebooks for exploration (committed, but lightweight)
├── powerbi/
│   ├── dashboard.pbix     # Main Power BI file — manually edited
│   ├── data_model.md      # ERD + table relationships, refresh-after-pipeline checklist
│   └── measures.md        # DAX measure catalog (KPIs, time-intel, ratios)
├── src/
│   ├── __init__.py
│   ├── config.py          # Paths, constants, dataset URLs
│   ├── ingest.py          # Load raw Kaggle CSV → typed pandas DataFrame
│   ├── clean.py           # Dedup, null handling, type coercion, ISRC normalization
│   ├── transform.py       # Build fact + dimension tables
│   ├── validate.py        # Star-schema contracts (FK integrity, non-null keys)
│   ├── export.py          # Write CSVs with Power BI-friendly encoding
│   └── pipeline.py        # Orchestrator: ingest → clean → transform → validate → export
├── tests/
│   ├── conftest.py
│   ├── test_clean.py      # Cleaning unit tests
│   ├── test_transform.py  # Star-schema construction tests
│   └── test_contracts.py  # End-to-end output validation
├── report/
│   ├── final_report.md
│   ├── chart_justifications.md   # One section per chart, citing documents/
│   └── figures/                  # Exported chart PNGs for the written report
├── CLAUDE.md              # Project context for Claude Code (architecture, conventions, gotchas)
├── README.md              # Human onboarding (setup → run → contribute)
├── SPEC.md                # This file
├── Makefile
├── pyproject.toml         # Or requirements.txt + setup.cfg as fallback
├── .gitignore
└── .env.example           # Empty placeholder (no secrets needed for Kaggle CSV path)
```

---

## 5. Code Style

A representative snippet (illustrates type hints, docstring conventions, pandas idioms, and our preference for pure functions):

```python
# src/transform.py
from __future__ import annotations

import pandas as pd

from src.config import AUDIO_FEATURE_COLS


def build_dim_track(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Collapse the cleaned per-(track, country, date) frame into one row per track.

    Audio features are static per ISRC, so we aggregate by ISRC and keep the first
    non-null value for each feature. Tracks without an ISRC use a synthetic key
    derived from (track_name, primary_artist_name).
    """
    keep_cols = ["track_key", "track_name", "isrc", "explicit", "duration_ms", *AUDIO_FEATURE_COLS]
    dim = (
        cleaned
        .sort_values("snapshot_date")
        .drop_duplicates(subset="track_key", keep="first")
        .loc[:, keep_cols]
        .reset_index(drop=True)
    )
    assert dim["track_key"].is_unique, "track_key must be unique in dim_track"
    return dim
```

**Conventions**
- `snake_case` for functions, variables, and file names.
- Module-level constants in `UPPER_SNAKE_CASE` (live in `src/config.py`).
- Type hints on every public function signature; `from __future__ import annotations` at the top of every module.
- Docstrings on every public function — one line summary + optional paragraph. Skip on trivial helpers.
- Pandas: prefer chained `.loc[…]` / `.assign(…)` over in-place mutation; column order set explicitly when writing CSVs.
- Assertions document invariants; they are NOT a substitute for validation in `src/validate.py`.
- No inline magic numbers — every threshold lives in `src/config.py` with a name.
- 100-column line limit (ruff default).

---

## 6. Testing Strategy

| Test level | Where | What it covers | Run frequency |
|---|---|---|---|
| **Unit** | `tests/test_clean.py`, `tests/test_transform.py` | Pure functions in `clean.py` and `transform.py` with small synthetic frames | Pre-commit + CI (if added) |
| **Contract / integration** | `tests/test_contracts.py` | End-to-end pipeline on a tiny fixture; validates FK integrity, non-null keys, value ranges, schema dtypes | Pre-commit + before every dashboard refresh |
| **Manual UI** | Power BI Desktop | Visuals load, no Power Query errors, slicers work, no broken relationships | After every successful `make build` |

Coverage target: **≥ 80%** on `src/clean.py`, `src/transform.py`, `src/validate.py`. `src/ingest.py` and `src/export.py` are I/O shells and exempt.

Fixtures live in `tests/conftest.py` and use **synthetic data only** — never real Kaggle rows — so tests work without the raw dataset.

---

## 7. Data Model (Star Schema for Power BI)

```
                    ┌──────────────┐
                    │   Dim_Date   │
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────▼──────────────────┐    ┌──────────────┐
│ Dim_Artist   │◀───┤  Fact_TrackSnapshot     ├───▶│   Dim_Track  │
└──────────────┘    │                          │    └──────────────┘
                    │  - track_key (FK)        │
┌──────────────┐    │  - artist_key (FK)       │    ┌──────────────┐
│ Dim_Album    │◀───┤  - album_key (FK)        ├───▶│ Dim_Country  │
└──────────────┘    │  - date_key (FK)         │    └──────────────┘
                    │  - country_key (FK)      │
                    │  - rank                  │
                    │  - daily_streams         │
                    │  - popularity            │
                    └──────────────────────────┘
```

**Grain of `Fact_TrackSnapshot`:** one row per `(track, country, snapshot_date)`. If the chosen Kaggle dataset is a static catalog snapshot rather than a daily chart, the grain collapses to one row per track, and `Dim_Country` / `Dim_Date` may be dropped.

**Static-vs-changing attributes:**
- **Audio features live in `Dim_Track`** — they're properties of the recording, not measurements that change over time.
- **`popularity`, `rank`, `daily_streams` live in `Fact_TrackSnapshot`** — they change over time.

**Key strategy:**
- `track_key` = `isrc` when present; else `sha1(track_name + '|' + primary_artist_name)[:16]`. Stored as string.
- `artist_key`, `album_key` = stable hashes of canonicalized names (lowercased, accents stripped, whitespace collapsed).
- `date_key` = `YYYYMMDD` integer (Power BI convention).
- `country_key` = ISO 3166-1 alpha-2 (uppercase).

---

## 8. Visualization Strategy & Justification Workflow

Each dashboard chart will be paired with a section in `report/chart_justifications.md` that:
1. States the **question** the chart answers.
2. Names the chart type.
3. Cites at least one principle from `documents/` (e.g., Cleveland & McGill perceptual hierarchy, Tufte's data-ink ratio, Bertin's visual variables, Few's dashboard design, Munzner's task taxonomy).
4. Names **alternatives considered and rejected** with reasons.

**Proposed dashboard pages and charts** (final list to be refined during plan phase; this is the v1 menu):

| # | Page | Chart | Question answered |
|---|---|---|---|
| 1 | Overview | KPI cards (track count, distinct artists, avg popularity, % explicit) | Topline scale of dataset |
| 2 | Overview | Histogram of `popularity` | Is popularity uniformly distributed or long-tailed? |
| 3 | Mood map | **Scatter plot** of valence (x) vs. energy (y), color by popularity, size by streams | Where in the energy–valence plane do popular songs cluster? |
| 4 | Temporal trends | **Line chart** of average danceability / energy / acousticness by release year | How has the sonic character of popular music evolved? |
| 5 | Temporal trends | **Stacked area** of explicit vs. non-explicit share by year | Is explicit content becoming more dominant? |
| 6 | Artists | **Horizontal bar** — top 20 artists by aggregate popularity | Who dominates the chart-track set? |
| 7 | Audio anatomy | **Correlation matrix heatmap** of audio features | Which features co-vary? Are any redundant? |
| 8 | Audio anatomy | **Box / violin plot** of selected feature by genre or by release-year bin | How does dispersion of a feature change across groups? |
| 9 | Geography (only if country dimension exists) | **Filled map** of average popularity by country | Where do these tracks resonate most? |
| 10 | Detail | **Small multiples** — radar charts of audio features for top 5 artists | How do top artists differ in sonic signature? |

---

## 9. Boundaries

### Always do
- Run `make test` and `make lint` before every commit.
- Use **ISRC** as the primary track key when available; fall back to canonicalized `(track_name, primary_artist_name)` only when ISRC is missing.
- Write CSVs as **UTF-8 with BOM** (`encoding="utf-8-sig"`) so Power BI on Windows handles non-ASCII artist names correctly.
- Pin the Kaggle dataset version (URL + downloaded date + SHA-256) in `data/raw/README.md`.
- Cite a `documents/` source for every chart justification.
- Treat `data/raw/` as immutable — transformations write to `data/interim/` and `data/processed/`.

### Ask first
- Adding a second Kaggle dataset alongside the primary (changes the join semantics).
- Changing the grain of `Fact_TrackSnapshot` (cascades through the dashboard).
- Renaming any column in `data/processed/*.csv` — breaks Power BI relationships silently.
- Installing new Python dependencies.
- Committing any file in `data/raw/` to git (probably should be gitignored or LFS).

### Never do
- Commit Kaggle API tokens, `.env` files, or any credential.
- Edit `dashboard.pbix` programmatically — it's a binary file and must be modified in Power BI Desktop only.
- Deduplicate tracks by `track_name` alone (same name, different artists is common).
- Fabricate data to fill gaps — document gaps in the report instead.
- Skip a failing test by deleting or marking it `xfail` without team approval.
- Use Spotify Web API audio-features data (excluded by design; see §1).

---

## 10. Open Questions

These remain unresolved and need a decision before or during the Plan phase. None block writing the spec, but each will block some piece of implementation:

1. **Which exact Kaggle dataset is the primary?** Top candidates:
   - Asaniczka, *Top Spotify Songs in 73 Countries (Daily)* — has chart positions + audio features, good for temporal/geographic analysis.
   - maharshipandya, *Spotify Tracks Dataset* — large genre breadth, audio features, but older snapshot (~2022).
   - Suggested combination: **Asaniczka as primary**, maharshipandya as a supplementary genre-context table if needed.
2. **Country scope** — global aggregation only, or per-country exploration? Drives whether `Dim_Country` exists.
3. **Genre taxonomy** — accept the dataset's labels as-is, or remap to a coarser standard (e.g., 8 macro-genres)?
4. **Report format** — Markdown (rendered to PDF), Word, or LaTeX? Affects how figures are embedded.
5. **`uv` vs. `pip`** — does every teammate's machine support `uv`, or do we ship `requirements.txt` as the canonical interface?
6. **Where do the course slides actually come from?** Confirm the team will drop them into `documents/` before we start writing justifications.

---

## 11. Out of Scope (v1)

- Real-time or scheduled refresh.
- Spotify Web API integration (any endpoint).
- User authentication / multi-tenant Power BI workspace.
- Predictive modeling, ML, or anything beyond descriptive analytics.
- Deploying the dashboard to Power BI Service.
- Cross-platform builds (Windows-only for `.pbix`; Python pipeline runs anywhere).

---

## Verification checklist (gate before Plan phase)

- [ ] Human has reviewed §1 (objective, success criteria).
- [ ] Human has confirmed the Kaggle-only pivot is acceptable (vs. attempting Spotify API).
- [ ] Human has resolved or acknowledged each Open Question in §10.
- [ ] Human approves the proposed star schema in §7.
- [ ] Human approves the v1 chart menu in §8.

Once all checks pass: proceed to **Phase 2: Plan**.
