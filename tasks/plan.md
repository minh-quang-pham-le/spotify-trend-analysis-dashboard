# Implementation Plan

> Companion to `SPEC.md`. The spec defines **what** and **why**; this plan defines **how** and **in what order**. Companion task list with checkboxes is in [`todo.md`](todo.md).
>
> Status: **Plan draft v1** — awaiting human review before Implement phase begins.

---

## 0. Locked defaults (from SPEC.md §10 open questions)

Defaults assumed in this plan, callable out so you can override before we touch code:

| # | Question | Default for this plan | Override how |
|---|---|---|---|
| 1 | Primary Kaggle dataset | **Asaniczka — *Top Spotify Songs in 73 Countries (Daily)*** | Update `src/config.py:PRIMARY_DATASET_FILENAME` + `data/raw/README.md`; tasks A2/A3 reabsorb the shift. |
| 2 | Country scope | **Per-country exploration** (`Dim_Country` is in scope; one geography page) | Drop task B7 + D6 + `Dim_Country` rows from `data_model.md`. |
| 3 | Genre taxonomy | **Accept dataset labels as-is for v1** | Add task between B5 and B8 to remap genres; no schema change. |
| 4 | Report format | **Markdown** rendered to PDF at submission | Switch to LaTeX/Word in Phase E only. |
| 5 | `uv` vs `pip` | **`pip` canonical** (`requirements.txt`) | Already supported; `pyproject.toml` works with both. |
| 6 | `documents/` provenance | **Team-owned** — justifications use TODOs until the folder is populated | No plan impact; placeholders flagged in Phase E. |

---

## 1. Phase overview

```
A. Data foundation        ─────►  B. Pipeline implementation
                                      │
                                      ▼
                                  C. Power BI vertical slice
                                      │
                                      ▼
                                  D. Dashboard pages (parallel)
                                      │
                                      ▼
                                  E. Report assembly
                                      │
                                      ▼
                                  F. Polish & submit
```

| Phase | Outcome | Sequencing |
|---|---|---|
| A. Data foundation | Raw CSV downloaded; schema profiled and reconciled with `config.py` | Sequential |
| B. Pipeline implementation | `make build` produces validated star-schema CSVs from raw | Mostly sequential; six dim/fact builders are independent once `clean.py` is done |
| C. Power BI vertical slice | `dashboard.pbix` opens, model loads, one trivial chart renders | Sequential after B |
| D. Dashboard pages | All 7 planned pages built; screenshots exported; justifications drafted | Parallelizable after C |
| E. Report assembly | Final report with findings, methodology, full chart justifications | Sequential after D |
| F. Polish & submit | Code review pass, pre-launch checklist, final tag | Sequential after E |

---

## 2. Dependency graph

```
                          A1 Download dataset
                                  │
                                  ▼
                          A2 Profile schema
                                  │
                                  ▼
                          A3 Reconcile config.py
                                  │
                                  ▼
                          B1 Implement ingest.py
                                  │
                                  ▼
                          B2 Implement clean.py
                                  │
        ┌─────────┬───────────────┼───────────────┬─────────┐
        ▼         ▼               ▼               ▼         ▼
   B3 dim_track  B4 dim_artist  B5 dim_album  B6 dim_date  B7 dim_country
        └─────────┴───────────────┼───────────────┴─────────┘
                                  │
                                  ▼
                       B8 build_fact_track_snapshot
                                  │
                                  ▼
                       B9 validate.py (contracts)
                                  │
                                  ▼
                       B10 export.py (write CSVs)
                                  │
                                  ▼
                       B11 pipeline.py orchestrator
                                  │
                                  ▼
                       B12 End-to-end run: `make build` green
                                  │
                                  ▼
                       C1 Create dashboard.pbix
                                  │
                                  ▼
                       C2 Import + relationships
                                  │
                                  ▼
                       C3 Core DAX measures
                                  │
                                  ▼
                       C4 Smoke chart (one KPI row)
                                  │
        ┌──────┬──────┬──────┬────┴────┬──────┬──────┐
        ▼      ▼      ▼      ▼         ▼      ▼      ▼
       D1     D2     D3     D4        D5     D6     D7
     Overview Mood  Temporal Artists  Audio  Geo   Detail
                                                   (radar)
        └──────┴──────┴──────┴────┬────┴──────┴──────┘
                                  ▼
                       E1 Findings
                                  ▼
                       E2 Chart justifications (cited)
                                  ▼
                       E3 Methodology + intro
                                  ▼
                       E4 Final pass
                                  ▼
                       F1 Pre-launch checklist
                                  ▼
                       F2 Code review pass
                                  ▼
                       F3 Tag v1.0 + submit
```

Critical path: **A1 → A2 → A3 → B1 → B2 → B8 → B9 → B10 → B11 → B12 → C1 → C2 → C3 → C4 → D1 → E1 → E4 → F3**.

---

## 3. Vertical slicing strategy

The temptation is to build the pipeline "horizontally" — every dim, then every fact, then every chart. That's slow to feedback. Vertical slicing means: produce **one runnable end-to-end path** as early as possible, then thicken.

**Slice 1 — Minimal end-to-end (Phases B + C up to C4).**
Smallest viable schema: `Fact_TrackSnapshot` referencing only `Dim_Track`. No artist, album, date, or country dimensions yet. Goal: prove the pipeline writes CSVs Power BI can ingest, and one chart renders.

**Slice 2 — Catalog richness (Phases B3–B5 expanded, dashboard page D4).**
Add `Dim_Artist` and `Dim_Album`. First "real" chart: top 20 artists bar.

**Slice 3 — Temporal axis (B6, D3).**
Add `Dim_Date`, time-intel measures, line + stacked-area charts.

**Slice 4 — Geography (B7, D6) — optional per locked default.**
Add `Dim_Country`, filled map.

**Slice 5 — Audio anatomy (D2, D5).**
Mood map (scatter), correlation heatmap, box/violin. No schema change required.

Each slice ends with a working dashboard. If we run out of time at any slice boundary, the project is still shippable.

---

## 4. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Audio features missing on a large fraction of rows | Medium | High | Profile coverage in A2; if < 60%, treat missing as "Unknown" group and call it out in the report rather than hiding it |
| R2 | ISRC missing or malformed | Medium | Medium | Fallback surrogate key `sha1(name + '|' + primary_artist)[:16]` is already in `data_model.md` |
| R3 | Kaggle dataset schema doesn't match `config.py` defaults | High | Low | Task A3 explicitly reconciles before any cleaning logic is written |
| R4 | Dataset is too large for in-memory pandas | Low | Medium | Asaniczka's ~150 MB is fine on 16 GB RAM. If anyone hits OOM, chunk read with `dtype` overrides |
| R5 | Multi-artist tracks under-represented (we use primary artist only) | High | Low | Documented as a known limitation in the report; bridge table is an ASK-FIRST item per `SPEC.md §9` |
| R6 | Power BI is Windows-only; some teammates may lack a Windows machine | Medium | Medium | Pair with a teammate who has Windows; alternatively run a free Windows VM (Multipass / Parallels) |
| R7 | `documents/` folder empty when Phase E starts | High | Medium | Justifications can land with `TODO: cite <theory>` placeholders; replace before final submission |
| R8 | Date column in raw dataset is not parseable as ISO | Medium | Low | `clean.py` tries `pd.to_datetime` with explicit format; rows that fail become `NaT` and feed `Dim_Date` only via valid dates |
| R9 | Power BI relationship inference breaks if column types differ across CSVs | Medium | High | `validate.py` enforces dtypes before export; `data_model.md` has a refresh checklist |
| R10 | Color palette / accessibility (color-blind safe) | Low | Low | Pick a colorblind-safe palette in C2 and document it in `chart_justifications.md` cross-cutting section |

---

## 5. Parallelism map

After B2 (`clean.py`) is merged, multiple teammates can fan out:

| Worker | Tasks |
|---|---|
| **Pipeline-A** | B3 `dim_track`, B8 `fact_track_snapshot` |
| **Pipeline-B** | B4 `dim_artist`, B5 `dim_album` |
| **Pipeline-C** | B6 `dim_date`, B7 `dim_country` |
| **Validator** | B9 `validate.py`, B10 `export.py` (can start with stub data) |

After C3 (DAX measures done), dashboard page work parallelizes:

| Worker | Tasks |
|---|---|
| **Dash-A** | D1 Overview, D5 Audio anatomy |
| **Dash-B** | D2 Mood map, D7 Radar |
| **Dash-C** | D3 Temporal, D4 Artists |
| **Geo** | D6 Geography (optional) |

Report writing (E1, E3) can start in parallel with later D tasks. E2 needs all charts before it can compile justifications.

---

## 6. Checkpoints (gates between phases)

Each gate is a **stop-and-review** before advancing. If the gate fails, revisit the prior tasks.

| Gate | After task | Pass condition |
|---|---|---|
| **G1 Schema reconciled** | A3 | `config.py` constants match real raw-CSV columns; `notebooks/01_data_profile.ipynb` exists with null/cardinality counts; team reviews and acknowledges any structural surprises |
| **G2 Pipeline green** | B12 | `make build` exits 0; `make test` passes (incl. contract tests); `data/processed/` has the expected 5–6 CSVs; manual eyeball of fact + one dim row makes sense |
| **G3 Model loads** | C2 | Power BI imports CSVs without errors; all relationships in `data_model.md` exist and propagate correctly (test by dropping artist on a track count) |
| **G4 First chart works** | C4 | KPI cards render with real numbers; refresh from disk works |
| **G5 Dashboard complete** | D7 (or last D done) | Every planned visual renders; no broken visuals on any page; team walkthrough |
| **G6 Justifications complete** | E2 | Every chart in the dashboard has a justification with at least one `documents/` citation (no remaining TODOs) |
| **G7 Submission-ready** | F2 | Pre-launch checklist green; `make test` and `make lint` pass; PR review approved; tag created |

---

## 7. Definition of Done (project-level)

A copy of `SPEC.md §1` success criteria, repeated so this plan is self-contained:

- [ ] `make build` regenerates `data/processed/` from a fresh clone with zero manual steps beyond placing the raw CSV.
- [ ] Star-schema FK integrity holds (validated by `pytest`).
- [ ] No row in `Fact_TrackSnapshot` is missing `popularity` or `track_key`.
- [ ] Dedup uses `spotify_id` first, fallback to canonicalized `(track_name, artist)`. *(Revised from ISRC-first at Gate G1 — the Asaniczka dataset has no ISRC; see SPEC.md §9 and `powerbi/data_model.md`.)*
- [ ] `dashboard.pbix` imports all CSVs without Power Query errors and renders every dashboard page.
- [ ] Every chart has a justification in `chart_justifications.md` citing at least one `documents/` source.
- [ ] README enables a teammate to set up the project from scratch in ≤ 15 minutes.

---

## 8. Estimated effort (very rough)

Effort is in "focused-session" units (one teammate, ~2 hours). Reality usually doubles. The user said "don't care about time, just do it as good as possible" so this is purely for sequencing intuition.

| Phase | Sessions | Notes |
|---|---|---|
| A | 2 | Heavy on discovery; the dataset always surprises |
| B | 10 | The largest phase. Six builders + cleaning + validation + export |
| C | 3 | Setup + relationships + first measures |
| D | 7–9 | One session per page, plus polish |
| E | 4 | Writing is slower than it looks |
| F | 2 | Code review + checklist + submission |
| **Total** | **~28–32** | Across 5 teammates ≈ 6–7 sessions each |

---

## 9. What this plan **does not** cover

Out-of-scope items already in `SPEC.md §11` are not repeated here. New plan-level exclusions:

- We do **not** plan to build a CI pipeline (running tests on push). It's nice-to-have but doesn't move the dashboard forward.
- We do **not** plan to write a Power BI deployment pipeline. The `.pbix` file is the deliverable.
- We do **not** plan to implement statistical-significance testing for "findings" — descriptive analytics only, per `SPEC.md §11`.

---

## 10. Verification checklist for this plan

Before proceeding to implementation:

- [ ] You've reviewed the **Locked defaults** in §0 and either confirmed or overridden each one.
- [ ] You've reviewed the **Dependency graph** and agree with the critical path.
- [ ] You've reviewed the **Risk register** and either accept the mitigations or want stronger ones for specific risks.
- [ ] You've reviewed the **Parallelism map** for whether it makes sense given your team's setup.
- [ ] You've reviewed the **Gates** — these are the points where the plan pauses for human approval.
- [ ] You've reviewed [`todo.md`](todo.md) and either accept the task ordering or want changes.

Once green, the next command should be `/agent-skills:build` (or equivalent) to start task **A1**.
