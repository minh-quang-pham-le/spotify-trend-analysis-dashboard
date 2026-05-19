# Spotify Music Trends 2024–2025 — Power BI Dashboard

A Data Visualization course project that analyses popular-music trends on Spotify (2024–2025, extending into early 2026 where the source data allows) and presents them in an interactive Power BI dashboard. The pipeline ingests a Kaggle dataset, reshapes it into a star schema, and emits CSVs ready for direct import into Power BI.

The dashboard is paired with a written report that justifies the choice of every chart against established data-visualization theory (see [`report/chart_justifications.md`](report/chart_justifications.md)).

---

## Quick start (15 minutes)

### Prerequisites

| Tool | Required version | macOS install | Windows install |
|---|---|---|---|
| Python | 3.11+ | `brew install python@3.11` | [python.org](https://python.org) installer |
| Power BI Desktop | latest free build | — *(not supported on macOS — Windows VM or a teammate's machine required)* | Microsoft Store |
| `make` | any | preinstalled | install with [Chocolatey](https://chocolatey.org/): `choco install make` *(optional — `python -m …` works without it)* |
| Git | 2.30+ | preinstalled | [git-scm.com](https://git-scm.com) |

### Setup

```bash
# 1. Clone
git clone https://github.com/minh-quang-pham-le/spotify-trend-analysis-dashboard.git
cd spotify-trend-analysis-dashboard

# 2. Create virtualenv + install deps
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Smoke test — should pass on a fresh checkout
make test                              # Windows: python -m pytest -q
```

### Get the data

The raw Kaggle dataset is **not** committed (see `.gitignore`). Each teammate downloads it locally:

1. Sign in to [kaggle.com](https://kaggle.com).
2. Download the primary dataset (TBD — likely [*Top Spotify Songs in 73 Countries (Daily Updated)*](https://www.kaggle.com/datasets/asaniczka/top-spotify-songs-in-73-countries-daily-updated)).
3. Unzip and place the CSV in `data/raw/`. See [`data/raw/README.md`](data/raw/README.md) for the expected filename and SHA-256 checksum.

### Build

```bash
make build                             # Windows: python -m src.pipeline
```

This reads `data/raw/<dataset>.csv`, validates it, builds the star-schema tables, and writes them to `data/processed/`:

```
data/processed/
├── fact_track_snapshot.csv
├── dim_track.csv
├── dim_artist.csv
├── dim_album.csv
├── dim_date.csv
└── dim_country.csv          # only if multi-country data is used
```

### Open the dashboard

1. Open `powerbi/dashboard.pbix` in Power BI Desktop (Windows only).
2. *Home → Refresh* — Power BI re-reads `data/processed/`.
3. If you renamed or moved any CSV, fix the source paths in *Transform Data → Source*.

---

## Project structure

```
.
├── SPEC.md                 # Source of truth: what we're building and why
├── CLAUDE.md               # Operating manual for Claude Code sessions
├── README.md               # You are here
├── Makefile                # build / test / lint shortcuts
├── pyproject.toml          # Package + dev tooling config
├── requirements.txt        # pip-installable dependency list
├── .env.example            # Empty placeholder (no secrets needed)
├── data/
│   ├── raw/                # Kaggle dumps (gitignored)
│   ├── interim/            # Pipeline scratch (gitignored)
│   └── processed/          # Star-schema CSVs — Power BI's input
├── documents/              # Course slides / dataviz theory (gitignored)
├── notebooks/              # Exploratory Jupyter notebooks
├── powerbi/
│   ├── dashboard.pbix      # Main dashboard (binary, manual edits only)
│   ├── data_model.md       # ERD + relationship documentation
│   └── measures.md         # DAX measure catalog
├── report/
│   ├── final_report.md
│   ├── chart_justifications.md
│   └── figures/            # Exported chart PNGs
├── src/
│   ├── config.py           # Paths, constants
│   ├── ingest.py           # Load raw CSV → DataFrame
│   ├── clean.py            # Dedup, types, ISRC normalization
│   ├── transform.py        # Build fact + dimension tables
│   ├── validate.py         # FK / non-null contracts
│   ├── export.py           # Write CSVs (UTF-8 BOM for Power BI)
│   └── pipeline.py         # Orchestrator
└── tests/                  # pytest suite
```

---

## Common commands

| Task | macOS / Linux | Windows fallback |
|---|---|---|
| Build star-schema CSVs | `make build` | `python -m src.pipeline` |
| Run tests | `make test` | `python -m pytest -q` |
| Run tests with coverage | `make test-cov` | `python -m pytest --cov=src --cov-report=term-missing` |
| Lint | `make lint` | `python -m ruff check src tests` |
| Auto-format | `make fmt` | `python -m ruff format src tests` |
| Clean derived files | `make clean` | manually delete `data/interim/`, `data/processed/`, caches |

---

## Contributing (for teammates)

1. **Read `SPEC.md` first.** It defines the scope, schema, and success criteria.
2. **Make a branch** — `git checkout -b your-name/short-description`.
3. **Write tests for any new transform logic** in `tests/`. Use synthetic data only.
4. **Run `make test` and `make lint` before pushing.**
5. **Never** rename columns in `data/processed/*.csv` without updating `powerbi/data_model.md` *and* the `.pbix` — it silently breaks the dashboard.
6. **Never** commit anything in `data/raw/` or `documents/` — both are gitignored for a reason.

For Claude Code users: see `CLAUDE.md` for conventions, boundaries, and the operating manual.

---

## Team & course context

- 5-member group project, Data Visualization course.
- Final deliverable: a `.pbix` dashboard + a written report justifying every chart with theory citations.
- Course materials live in `documents/` (locally, never committed).

---

## License

Code: TBD by the team (suggest MIT for the pipeline).
Data: governed by the original Kaggle dataset's license — see the dataset page.
Course materials in `documents/`: not redistributed; respect the original copyright.
