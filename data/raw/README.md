# `data/raw/` — Source CSVs

This folder holds the **untouched Kaggle dataset**. Everything here is gitignored (see `.gitignore`); each teammate downloads the data locally.

## Primary dataset (proposed — final pick pending)

**[Top Spotify Songs in 73 Countries (Daily Updated)](https://www.kaggle.com/datasets/asaniczka/top-spotify-songs-in-73-countries-daily-updated)** by *Asaniczka*.

| Field | Value |
|---|---|
| Expected filename | `universal_top_spotify_songs.csv` |
| Approx. size | ~498 MB CSV (~162 MB zip); grows daily |
| Coverage | Daily charts across 73 countries (+ a blank-country "Global" chart) through 2025-06-11 in this snapshot |
| Has audio features? | ✅ Yes (incl. `key`, `mode`, `time_signature`); ❌ no ISRC, no stream counts, no genre |
| License | ODC Attribution License (ODC-By) — attribute Asaniczka / Spotify when redistributing |

## How to download

1. Sign in to [kaggle.com](https://kaggle.com).
2. Open the dataset page and click **Download**.
3. Unzip and place `universal_top_spotify_songs.csv` directly inside this folder.
4. **Do not** commit the file. `.gitignore` already excludes it.
5. Record the SHA-256 of your local copy below so the team can confirm everyone is on the same snapshot.

```bash
# macOS / Linux
shasum -a 256 data/raw/universal_top_spotify_songs.csv

# Windows PowerShell
Get-FileHash data/raw/universal_top_spotify_songs.csv -Algorithm SHA256
```

## Snapshot log

Update this table when you download a new snapshot.

| Download date | Snapshot date (per dataset) | SHA-256 | Notes |
|---|---|---|---|
| 2026-05-31 | 2025-06-11 (max `snapshot_date`) | `DC5B92D1042A3F1AF52E46583F2CAF9C68A9F2D70DA0F9DA3E5B3D17DD302518` | 497,967,212 bytes. Downloaded via `kaggle datasets download -d asaniczka/top-spotify-songs-in-73-countries-daily-updated --unzip`. ODC-By license. |

## Adding a second dataset

Per `SPEC.md §9`, adding another dataset is an **Ask first** action. If approved, list it here with the same metadata block.
