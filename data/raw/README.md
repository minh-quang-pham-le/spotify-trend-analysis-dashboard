# `data/raw/` — Source CSVs

This folder holds the **untouched Kaggle dataset**. Everything here is gitignored (see `.gitignore`); each teammate downloads the data locally.

## Primary dataset (proposed — final pick pending)

**[Top Spotify Songs in 73 Countries (Daily Updated)](https://www.kaggle.com/datasets/asaniczka/top-spotify-songs-in-73-countries-daily-updated)** by *Asaniczka*.

| Field | Value |
|---|---|
| Expected filename | `universal_top_spotify_songs.csv` |
| Approx. size | ~150 MB (varies per snapshot) |
| Coverage | Daily charts across 73 countries through ~late 2024 / early 2025 |
| Has audio features? | ✅ Yes |
| License | Check the dataset page before redistributing |

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
| _(none yet)_ | | | |

## Adding a second dataset

Per `SPEC.md §9`, adding another dataset is an **Ask first** action. If approved, list it here with the same metadata block.
