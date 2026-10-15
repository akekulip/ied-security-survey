# IED security documentation survey: runs and fetched documents

The `data/` folder of https://github.com/akekulip/ied-security-survey (private): what the study's results in `study/` rest on,
about 1.4 GB.

| Folder | What it holds |
|---|---|
| `cache/` | Every document the crawler fetched, named by its SHA-256. Vendors' public files, kept for verification only; do not redistribute. |
| `runs/` | One folder per crawl: config, manifest, sources with hashes, request log, extracted text per document, leads, review templates. `sample_2026-10-13_v2_0` is the current sample run; `census_2026-10-13` is the census `enrich` reads. Folders ending in `_replay` are offline re-extractions that check a run; the others are earlier runs kept for provenance. |
| `inventory/listing-2026-10-13/` | The vendor catalogue listings as first fetched, for `inventory --from`. |

Check a run against its documents from the top of the repository: `python survey.py verify --run data/runs/sample_2026-10-13_v2_0 --cache data/cache`.
