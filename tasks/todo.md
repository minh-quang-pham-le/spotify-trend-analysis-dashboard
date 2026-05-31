# Task List

> Companion to [`plan.md`](plan.md). Tick boxes as you finish. Tasks are ordered by dependency. Most tasks fit in one focused session; if one feels much bigger, split it before starting.
>
> Convention: `[ ]` = todo, `[~]` = in progress, `[x]` = done, `[!]` = blocked (note why on the next line).

---

## Phase A — Data foundation

- [x] **A1. Download the primary Kaggle dataset.**
  - Acceptance: `data/raw/universal_top_spotify_songs.csv` exists locally (not committed). `data/raw/README.md` has a row in the snapshot log with download date + SHA-256.
  - Verify: `shasum -a 256 data/raw/universal_top_spotify_songs.csv` (or Windows `Get-FileHash`) matches the recorded value.
  - Files: `data/raw/`, `data/raw/README.md`.
  - Depends on: nothing.

- [x] **A2. Profile the raw dataset.**
  - Acceptance: `notebooks/01_data_profile.ipynb` exists and reports: column list, dtypes, row count, null fraction per column, cardinality of `artist_name` / `album_name` / `country` if present, date-column min/max, fraction of rows with a valid ISRC, fraction with audio features.
  - Verify: notebook runs top-to-bottom without errors against `data/raw/`. Print a one-paragraph summary at the bottom answering: "Does the dataset match our assumptions in `SPEC.md §7`?"
  - Files: `notebooks/01_data_profile.ipynb`.
  - Depends on: A1.

- [x] **A3. Reconcile `src/config.py` with the real schema.**
  - Acceptance: Any constants in `src/config.py` that don't match the actual column names (e.g. `AUDIO_FEATURE_COLS`, `TRACK_METADATA_COLS`) are renamed or remapped. `data_model.md` is updated if column names diverge from the original schema.
  - Verify: `make test` still passes (smoke tests check constants exist and are non-empty, so renames must keep that property).
  - Files: `src/config.py`, possibly `powerbi/data_model.md`.
  - Depends on: A2.

### Gate G1 — Schema reconciled

> Stop and review with the team. Confirm: (a) the dataset is the one we want, (b) any surprises from A2 are acknowledged, (c) `config.py` reflects reality. Only then start Phase B.

---

## Phase B — Pipeline implementation

- [x] **B1. Implement `src/ingest.py`.**
  - Acceptance: `load_raw(path=None)` reads `data/raw/<dataset>.csv`, returns a `pd.DataFrame`, raises a clear `FileNotFoundError` if missing. No type coercion here.
  - Verify: `make test` includes a unit test that loads a tiny synthetic CSV from `tests/fixtures/` and asserts shape + columns.
  - Files: `src/ingest.py`, `tests/test_ingest.py`, `tests/fixtures/mini_raw.csv`.
  - Depends on: G1.

- [x] **B2. Implement `src/clean.py`.**
  - Acceptance: `clean(raw)` returns a cleaned frame with: snake_case column names, parsed dates, normalized ISRC (uppercase, stripped), no fully-duplicated rows, no rows where the essential identifiers (`track_name` AND `primary_artist_name`) are both missing.
  - Verify: `tests/test_clean.py` covers each transformation with synthetic edge cases. Coverage on `src/clean.py` ≥ 80%.
  - Files: `src/clean.py`, `tests/test_clean.py`.
  - Depends on: B1.

- [x] **B3. Implement `transform.build_dim_track`.**
  - Acceptance: One row per `track_key` (ISRC-first, fallback to hash). Carries `track_name`, `isrc`, `explicit`, `duration_ms`, and all audio features in `AUDIO_FEATURE_COLS`. `track_key` is unique and non-null.
  - Verify: unit test on synthetic frame with duplicates and missing ISRCs; assert uniqueness invariant.
  - Files: `src/transform.py`, `tests/test_transform.py`.
  - Depends on: B2.

- [x] **B4. Implement `transform.build_dim_artist`.**
  - Acceptance: One row per artist (using primary artist only — known limitation per `data_model.md`). `artist_key` = stable hash of canonicalized name.
  - Verify: synthetic test asserts artists with different casing / accents collapse to the same key.
  - Files: `src/transform.py`, `tests/test_transform.py`.
  - Depends on: B2. (Parallel with B3, B5, B6, B7.)

- [x] **B5. Implement `transform.build_dim_album`.**
  - Acceptance: One row per `(canonicalized album_name, release_date)`. Carries `total_tracks` if available.
  - Verify: same-name albums with different release dates are separate rows.
  - Files: `src/transform.py`, `tests/test_transform.py`.
  - Depends on: B2.

- [x] **B6. Implement `transform.build_dim_date`.**
  - Acceptance: One row per calendar date present in the cleaned frame's snapshot dates. Columns per `data_model.md` (year, quarter, month, month_name, day, day_of_week, day_name, week_of_year, is_weekend). Contiguous: no missing days in the [min, max] range.
  - Verify: assert `len(dim) == (max_date - min_date).days + 1`; assert `is_weekend` matches `day_of_week ∈ {6, 7}`.
  - Files: `src/transform.py`, `tests/test_transform.py`.
  - Depends on: B2.

- [x] **B7. Implement `transform.build_dim_country`.** *(skip if dataset is global-only — see locked default #2.)*
  - Acceptance: One row per ISO 3166-1 alpha-2 country code present in the data. `region` populated from a small hardcoded lookup table in `src/config.py`.
  - Verify: assert `country_key.is_unique`; spot-check region mapping.
  - Files: `src/transform.py`, `src/config.py` (region table), `tests/test_transform.py`.
  - Depends on: B2.

- [ ] **B8. Implement `transform.build_fact_track_snapshot`.**
  - Acceptance: Grain is `(track, country, snapshot_date)`. Foreign keys resolve. `popularity` non-null; `rank` and `daily_streams` allowed null where source is null.
  - Verify: unit test confirms grain (no FK collisions, no duplicated FK tuple). Asserts every FK value appears in the corresponding dim's PK set.
  - Files: `src/transform.py`, `tests/test_transform.py`.
  - Depends on: B3–B7.

- [ ] **B9. Implement `src/validate.py` contracts.**
  - Acceptance: `validate_star_schema(tables)` checks every contract from `SPEC.md §7` and `validate.py` docstring. Returns a `ValidationReport` with `passed=False` and explicit error messages when contracts fail.
  - Verify: `tests/test_contracts.py` includes one passing case (good synthetic tables) and at least three failing cases (missing FK, duplicated PK, out-of-range popularity).
  - Files: `src/validate.py`, `tests/test_contracts.py`.
  - Depends on: B8.

- [ ] **B10. Implement `src/export.py`.**
  - Acceptance: `export_tables(tables)` writes each DataFrame to `data/processed/<filename>.csv` with `encoding="utf-8-sig"`, `index=False`, explicit column order matching `data_model.md`. Creates `data/processed/` if missing.
  - Verify: integration test writes to a tmp dir; reads back with `pd.read_csv`; asserts column order and value round-trip including a non-ASCII artist name.
  - Files: `src/export.py`, `tests/test_export.py`.
  - Depends on: B9.

- [ ] **B11. Wire `src/pipeline.py`.**
  - Acceptance: `run()` calls ingest → clean → transform (six builders) → validate (abort on failure) → export. Returns exit code 0 on success, 1 on validation failure. Prints a one-line status per stage.
  - Verify: invoke `python -m src.pipeline` against synthetic raw data in tmp; assert `data/processed/` populated.
  - Files: `src/pipeline.py`, `tests/test_pipeline.py`.
  - Depends on: B10.

- [ ] **B12. End-to-end run on real data.**
  - Acceptance: `make build` against the real Kaggle dataset exits 0. `data/processed/` contains all expected CSVs. Manual eyeball: open one CSV, the rows look correct (no garbled text, no NaN where there shouldn't be).
  - Verify: `make build && make test`. Confirm processed CSV row counts are within ±5% of expected based on A2 profiling.
  - Files: none new; this is execution.
  - Depends on: B11.

### Gate G2 — Pipeline green

> Stop and review: `make build` works on a fresh clone (after A1). `make test` is green. CSVs look plausible. Only then start Phase C.

---

## Phase C — Power BI vertical slice

- [ ] **C1. Create `powerbi/dashboard.pbix`.**
  - Acceptance: Empty .pbix file checked into git (Power BI Desktop, blank report).
  - Verify: file opens in Power BI Desktop without errors.
  - Files: `powerbi/dashboard.pbix`.
  - Depends on: G2.

- [ ] **C2. Import CSVs and define relationships.**
  - Acceptance: All processed CSVs imported via *Get Data → Folder* or per-file. All relationships from `data_model.md` exist in *Model view* with correct cardinality and single-direction filter propagation. `Dim_Date` marked as a Date Table.
  - Verify: drop `Dim_Artist[artist_name]` and a measure into a visual; confirm filter context propagates correctly.
  - Files: `powerbi/dashboard.pbix` (binary, manual edits).
  - Depends on: C1.

- [ ] **C3. Define core DAX measures.**
  - Acceptance: All KPI and audio-feature measures from `powerbi/measures.md` exist in the model. Time-intel measures functional (test by inserting a year slicer).
  - Verify: each measure produces a non-error value when dropped into a card.
  - Files: `powerbi/dashboard.pbix`, `powerbi/measures.md` (kept in sync if measures evolve).
  - Depends on: C2.

- [ ] **C4. Build the smoke chart row.**
  - Acceptance: One report page named "Overview" contains a row of KPI cards (`# Tracks`, `# Distinct Artists`, `Avg Popularity`, `% Explicit`). Refresh from disk works without errors.
  - Verify: numbers in the cards match the numbers computed in `notebooks/01_data_profile.ipynb`.
  - Files: `powerbi/dashboard.pbix`.
  - Depends on: C3.

### Gate G4 — First chart works

> Stop and review. KPI numbers match the profile notebook. Refresh round-trip works. Only then split into parallel D-track work.

---

## Phase D — Dashboard pages (parallel after G4)

Each task ends with: (a) chart built, (b) screenshot exported to `report/figures/`, (c) draft justification section in `report/chart_justifications.md` (TODOs for theory citations OK at this point).

- [ ] **D1. Page: Overview — popularity histogram.** *(extends C4's page)*
  - Acceptance: Histogram of `popularity` with sensible binning. Visible alongside the KPI cards.
  - Verify: visual matches the distribution shape from A2 profiling.
  - Depends on: C4.

- [ ] **D2. Page: Mood Map — energy × valence scatter.**
  - Acceptance: Scatter plot. X = valence, Y = energy, color = popularity, optional size = streams. Tooltip shows track name + artist.
  - Verify: data-point count matches `# Tracks` in the model (within reasonable filter context).
  - Depends on: C4.

- [ ] **D3. Page: Temporal Trends — feature evolution + explicit share.**
  - Acceptance: Line chart of avg(danceability/energy/acousticness/valence) by release year. Stacked area of explicit-share by release year (or year-quarter if year resolution is too coarse).
  - Verify: line chart endpoints match the corresponding `Avg X YoY` measure.
  - Depends on: C4.

- [ ] **D4. Page: Artists — top 20 horizontal bar.**
  - Acceptance: Horizontal bar of top 20 artists by aggregate popularity (or by row count if popularity makes less sense). Slicer for time period.
  - Verify: top-1 artist matches the obvious leader from A2 profiling.
  - Depends on: C4.

- [ ] **D5. Page: Audio Anatomy — correlation heatmap + group box plot.**
  - Acceptance: Matrix visual showing pairwise Pearson correlation across audio features (or a Python visual if matrix is too clumsy). Box plot of one chosen feature by genre or year-bucket.
  - Verify: correlation diagonal is 1.0; symmetric.
  - Depends on: C4.

- [ ] **D6. Page: Geography — filled map.** *(skip if `Dim_Country` not in scope.)*
  - Acceptance: Filled map by country, color = `Avg Popularity by Country`. Hover tooltip with country, avg popularity, top artist.
  - Verify: colored countries equal the cardinality of `Dim_Country` ± a handful (some country names may not resolve in Bing's geocoder).
  - Depends on: C4 and B7.

- [ ] **D7. Page: Detail — top-artist radar small multiples.**
  - Acceptance: One radar (or polar) chart per top-5 artist showing the 5–7 audio features. Use a custom visual from AppSource if needed; if none works, fall back to a faceted bar chart.
  - Verify: radar shape differs visibly between any two of the top 5 artists.
  - Depends on: C4.

### Gate G5 — Dashboard complete

> Walk the team through every page. Every visual renders, no broken visuals, slicers work cross-page. Take final screenshots into `report/figures/`. Only then start Phase E.

---

## Phase E — Report assembly

- [ ] **E1. Findings section.**
  - Acceptance: 3–5 insights in `report/final_report.md §5`, each with: claim, evidence (numbers + chart reference), confidence + limitations.
  - Verify: every numeric claim is reproducible from the dashboard (cross-checked once).
  - Depends on: G5.

- [ ] **E2. Chart justifications (theory-cited).**
  - Acceptance: Every dashboard chart has a section in `chart_justifications.md` following the rubric, with at least one citation to a file in `documents/` (with slide / page reference). Two alternatives rejected per chart.
  - Verify: zero `TODO` markers remain.
  - Depends on: G5 + `documents/` populated.

- [ ] **E3. Methodology + introduction.**
  - Acceptance: §1, §2, §3 of `final_report.md` filled in. Pivot rationale (away from Spotify API) explained.
  - Verify: section reads end-to-end without contradiction.
  - Depends on: nothing later than G5 (can start in parallel with E1).

- [ ] **E4. Final report pass.**
  - Acceptance: Whole report reads coherently. Cross-references resolved. References list complete.
  - Verify: peer-read by a teammate not on the writing track.
  - Depends on: E1, E2, E3.

### Gate G6 — Justifications complete

> Confirm every chart has a real theory citation, no placeholders. Only then proceed to F.

---

## Phase F — Polish & submit

- [ ] **F1. Pre-launch checklist.**
  - Acceptance: Apply `agent-skills:shipping-and-launch` — confirm dashboards open from a fresh clone, all CSVs regenerate, README setup works on a teammate's machine, no committed secrets.
  - Verify: peer follows README from scratch and gets a working dashboard in ≤ 15 min.
  - Depends on: G6.

- [ ] **F2. Code-review pass on pipeline.**
  - Acceptance: Apply `agent-skills:code-review-and-quality` on `src/`. Fix any P0/P1 findings.
  - Verify: `make test`, `make lint` green. Reviewer signs off.
  - Depends on: F1.

- [ ] **F3. Tag release + submit.**
  - Acceptance: `git tag -a v1.0 -m "Final submission"`; push tag. Course submission completed per instructor's process.
  - Verify: tag visible on GitHub; submission acknowledgement received.
  - Depends on: F2.

### Gate G7 — Submission-ready

> Final stop. After this, the project is shipped.

---

## How to use this list

- One task in progress at a time per teammate. Update `[ ]` → `[~]` on start.
- Acceptance criteria are the contract — don't mark `[x]` if they don't hold.
- Verification is non-optional. "Looks right" is not verification.
- When you hit a gate, **stop**, post in the team chat, and wait for sign-off before continuing.
- Discoveries that change the plan get reflected here AND in `plan.md` AND (if material) in `SPEC.md`. Don't let the docs drift.
