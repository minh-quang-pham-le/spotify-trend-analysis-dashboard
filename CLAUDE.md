# CLAUDE.md — Project Context for Claude Code

> Read this **first** in any new session. It tells you what this project is, how it's structured, and what conventions to follow. The authoritative requirements live in `SPEC.md`; this file is the operating manual.

---

## What this project is

A university (Data Visualization course) group project, 5 members, building a **Power BI dashboard** that analyses 2024–2025 Spotify music trends. The dashboard is fed by a **Kaggle dataset** (we deliberately pivoted away from the Spotify Web API — see `SPEC.md §1`) which is transformed by a Python pipeline into a star-schema set of CSVs.

The final deliverable has two parts:
1. **`powerbi/dashboard.pbix`** — the dashboard itself.
2. **`report/`** — a written report that scientifically justifies the choice of *every* chart against data-visualization theory from course materials in `documents/`.

## Why the Kaggle pivot

Spotify deprecated `GET /audio-features` and several related endpoints for *new* developer apps on 2024-11-27. Audio features are central to our analytical thesis, so we use a Kaggle dataset that already contains them. **Do not** propose adding the Spotify Web API back unless the team confirms they have a pre-2024-11-27 grandfathered app.

## Source of truth precedence

When two documents disagree, follow this order:
1. **`SPEC.md`** — what we're building and why.
2. **`powerbi/data_model.md`** — the binding contract between pipeline output and the dashboard.
3. **`README.md`** — onboarding only; should not introduce new decisions.
4. **`CLAUDE.md`** (this file) — operating conventions.

If `SPEC.md` is wrong, **update it first**, then change code.

## Project layout (mirrors `SPEC.md §4`)

```
data/raw/         Kaggle dumps — gitignored, never committed
data/interim/     pipeline temp files — gitignored
data/processed/   star-schema CSVs consumed by Power BI
documents/        course slides / dataviz theory — gitignored (copyright)
notebooks/        exploration only — not part of the build
powerbi/          .pbix + data_model.md + measures.md
report/           final report + chart justifications
src/              the pipeline (pure Python, no UI)
tests/            pytest unit + contract tests
```

## Pipeline architecture

One linear pass, no DAG framework:

```
ingest.py  →  clean.py  →  transform.py  →  validate.py  →  export.py
 (load)       (dedup,        (build star      (FK + null     (write CSVs
              types,           schema)         checks)         to processed/)
              ISRC)
```

`src/pipeline.py` orchestrates these five stages. Each stage is a pure function — given the same input it produces the same output, no hidden state.

## Conventions

- **Python style**: see `SPEC.md §5`. `snake_case`, type hints on public functions, `from __future__ import annotations` at top of every module, ruff-formatted, 100-col line limit.
- **Pandas**: chained `.loc[]` / `.assign()`, avoid in-place mutation, set column order explicitly when exporting.
- **Keys**:
  - `track_key` = `isrc` when present, else `sha1(track_name + '|' + primary_artist_name)[:16]`.
  - `artist_key`, `album_key` = stable hashes of canonicalized names.
  - `date_key` = `YYYYMMDD` integer (Power BI convention).
  - `country_key` = ISO 3166-1 alpha-2 (uppercase).
- **CSV encoding**: write with `encoding="utf-8-sig"` so Power BI on Windows reads non-ASCII artist names correctly.
- **Audio features live on `Dim_Track`** (they don't change over time); popularity / rank / streams live on `Fact_TrackSnapshot`.
- **Constants and paths** live in `src/config.py`. No magic numbers in business logic.

## Commands

```bash
make build       # python -m src.pipeline
make test        # pytest -q
make test-cov    # pytest --cov=src --cov-report=term-missing
make lint        # ruff check src tests
make fmt         # ruff format src tests
make clean       # remove data/interim, data/processed, caches
```

Windows users without `make` run the equivalent `python -m …` commands. The README has the full mapping.

## Boundaries (from `SPEC.md §9`, repeated here because you'll forget)

### Always
- Run `make test` and `make lint` before committing.
- Use ISRC as the primary track identifier; fall back only when missing.
- Treat `data/raw/` as immutable.
- Cite a `documents/` source for every chart justification.

### Ask first
- Adding a new Kaggle dataset or new dependency.
- Changing the grain of `Fact_TrackSnapshot`.
- Renaming any column in `data/processed/*.csv` (silently breaks Power BI).
- Committing anything in `data/raw/`.

### Never
- Commit credentials, `.env`, or course-material PDFs (copyright).
- Edit `dashboard.pbix` programmatically — Power BI Desktop only.
- Deduplicate tracks by `track_name` alone.
- Use the Spotify Web API (deprecated for our use case — see §"Why the Kaggle pivot").
- Skip a failing test by deleting it or marking it `xfail` without team approval.

## Working with this project as Claude

- **Read `SPEC.md` early** in every session — it's short and has the success criteria.
- The data files live outside git. If you reference them in code, **don't** read them eagerly; check whether the user has placed `data/raw/<dataset>.csv` first.
- The `.pbix` is binary. If asked to inspect it, say it must be opened in Power BI Desktop.
- The `documents/` folder is the team's responsibility. If empty, write justifications as TODOs that reference *what* the theory anchor should be (e.g. "TODO: cite Cleveland-McGill perceptual hierarchy from documents/<slide-name>.pdf").
- When proposing a new chart, include the chart-justification rubric from `SPEC.md §8` — question answered, chart type, theory citation, alternatives rejected.

## Current status (update this when state changes)

- Phase: **Phase C (Power BI vertical slice) COMPLETE — Gate G4 PASSED (manually verified in Power BI Desktop, 2026-06-01). Ready to start Phase D (dashboard pages).** Phase B (pipeline) is complete and green. The `dashboard.pbix` has an "Overview" page with 4 KPI cards; refresh-from-disk, KPI values, all five relationships, the `dim_date` Date-Table marking, and the full `measures.md` catalogue were all verified by hand. Completion summary: `tasks/phase_c_summary.md`.
- Pipeline: `ingest → clean → transform (6 builders) → validate → export` all implemented (tasks B1–B12, TDD). `make build` exits 0 on the 2025-06-11 snapshot — **2,110,287** fact rows; dims: dim_track=24,976, dim_artist=7,565, dim_album=17,229, dim_date=603 (2023-10-18→2025-06-11, contiguous), dim_country=73. **68 unit/contract tests green**, ruff clean, coverage on clean/transform/validate ≥ 87%.
- Processed CSVs: **gitignored** — the fact CSV is ~162 MB (> SPEC §4's 25 MB threshold). Regenerate with `make build` (team decision at G1).
- Gate-G1 decisions locked in: key on `spotify_id` (no ISRC), `daily_streams` absent (all-null column), genre absent (all-null `primary_genre`). Plus a data-reality fix: `tempo=0` (Spotify "undetectable" sentinel — 1 row) is coerced to null in `clean.py` (`tempo` is nullable; keeps the SPEC §7 `tempo>0` contract honest).
- Primary Kaggle dataset: **confirmed** — *Top Spotify Songs in 73 Countries (Daily)* by Asaniczka, `universal_top_spotify_songs.csv` (snapshot 2025-06-11, SHA-256 in `data/raw/README.md`). Profiled in `notebooks/01_data_profile.ipynb`.
- Power BI file: **created and committed** (`powerbi/dashboard.pbix`, ~10 MB, model embedded). ZIP inspection (2026-06-01) confirms 6 tables — all **lowercase** (`fact_track_snapshot`, `dim_track`, `dim_artist`, `dim_album`, `dim_date`, `dim_country`) — and one "Overview" page with 4 KPI cards (`Tracks`, `Distinct Artists`, `Avg Popularity`, `% Explicit`). The `g4_remediation.md` runbook was only **partially** applied (card swap landed; PascalCase table rename + `#`-prefixed measure names did **not**). Team decision: **accept the file's lowercase/bare names as-is**; `powerbi/measures.md` + `powerbi/data_model.md` were realigned to the file (2026-06-01). The `.pbix` is binary, so model internals can only be checked in Power BI Desktop — this was done on 2026-06-01: the five relationships, the full `measures.md` catalogue, and the `dim_date` Date-Table marking are all verified present and working (Gate G4 passed).
- `documents/` folder: not yet populated by the team.
- Open questions (`SPEC.md §10`): #1 resolved (dataset), #2 resolved-by-default (per-country — `Dim_Country` is built), #3 moot (no genre). #4 report format, #5 uv-vs-pip, #6 documents provenance still open — none block Phase C.
