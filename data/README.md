# IED security documentation survey: runs and fetched documents

The `data/` folder of https://github.com/akekulip/ied-security-survey (a public repository): what the study's results in `study/` rest on,
about 1.4 GB.

| Folder | What it holds |
|---|---|
| `cache/` | Every document the crawler fetched, named by its SHA-256. Vendors' public files, kept for verification only; do not redistribute. |
| `runs/` | One folder per crawl: config, manifest, sources with hashes, request log, extracted text per document, leads, review templates. `sample_targeted_2026-10-15` is the current sample run: the 2026-10-13 sample, re-extracted with rules 1.4.1, plus the documents of the bounded pass of 2026-10-15. `sample_audit_2026-10-15` is the offline rebuild of `sample_2026-10-13_v2_0`, which the review of 2026-10-13/14 was written against. `codefix_replay_0f13499` is the replay of the current run with tool 2.3.1. `census_2026-10-13` is the census `enrich` reads. Folders ending in `_replay` are offline re-extractions that check a run; the others are earlier runs kept for provenance. |
| `inventory/listing-2026-10-13/` | The vendor catalogue listings as first fetched, for `inventory --from`. |

Check a run against its documents from the top of the repository: `python survey.py verify --run data/runs/sample_targeted_2026-10-15 --cache data/cache`.

The documents first fetched by the bounded pass of 2026-10-15 are in `cache/` with the rest (committed on 2026-10-15 at
the author's direction), and their addresses and SHA-256 hashes are in the run's `sources.json`.
