# Study files

What the survey has produced, and how each file was made. The tool is in the same private repository, https://github.com/akekulip/ied-security-survey; the catalogue study's report was made with version 2.2.0. Commands below are run from the top of the repository. The catalogue study's runs and fetched documents are in `data/` at the top of the repository.

**Nothing here is a confirmed finding yet.** Every review row was drafted by an AI assistant and says so in its `reviewer` field ("Claude AI draft review; author confirmation pending"). The reports repeat that under "Reviewers on record". A second AI reading has checked the draft against the retained documents. That does not replace the author's confirmation.

Fetched bytes and run directories are kept outside this folder. The five-product study uses `runs/` and `cache/` at the top of the repository. The catalogue study's are in `data/`, written `$DATA` below; its cache is about 1.2 GB.

## Where to look first

| Question | Open |
|---|---|
| What goes in the paper? | `catalogue_2026-10-13/paper_appendix.tex`: the method, the reconciled table, the devices with documented protection, and every passage with its page, retrieval date and SHA-256 |
| Which devices document DNP3 security, of what kind, and which are plaintext, for current and legacy devices? | `catalogue_2026-10-13/reports/sample_ai_draft/REPORT.md`, section "DNP3 security", or `dnp3.csv` beside it |
| Which sampled devices are discontinued, and what do the documents say about their control traffic? | `catalogue_2026-10-13/reports/sample_ai_draft/REPORT.md`, sections "At a glance" and "Control traffic, device by device" |
| How was each claim and outside source checked? | `catalogue_2026-10-13/review/second_pass_2026-10-14.md` |
| Where should a reviewer read for one device and capability? | `catalogue_2026-10-13/reports/worksheet/worksheet.md` |

## catalogue_2026-10-13/

The five vendors' catalogues as listed on 2026-10-13, and a seeded sample of 99 devices drawn from them.

| File | What it is | Made with |
|---|---|---|
| `inventory/listing/` | Every catalogue entry in scope, placed by the rules in `configs/vendors.json`. `catalogue.json` is the raw listing and `requests.json` the log of the requests that fetched it. | `inventory --from $DATA/inventory/listing-2026-10-13` |
| `inventory/pages/` | The same after each product page was read. This is the sampling frame: 484 devices, of which 309 are currently sold, 168 discontinued with support not stated and 7 of unknown state. | `enrich --run $DATA/runs/census_2026-10-13 --vendors configs/vendors.json` |
| `census.json` | Crawl config of the census: one product page per catalogue entry, 485 entries. Run: `$DATA/runs/census_2026-10-13`. It was cut from the first listing inventory, which has since been deleted; the config keeps that inventory's SHA-256. | `sample --census` |
| `sample.json` | Crawl config of the sample: up to 4 devices per vendor, category and lifecycle state, seed 20261013, with the current definitions. Run: `$DATA/runs/sample_2026-10-13_v2_0`. | `sample --per-stratum 4 --seed 20261013` |
| `review/reviews_ai_draft.json` | The AI-drafted review of the 99 devices: 820 rows covering all 792 cells. | drafted from the worksheet and the retained text; every quote checked by `report --require-evidence` |
| `review/source_notes_ai_draft.json` | Document type and coverage for the 16 sources the review takes as complete manuals. | by the same draft |
| `review/device_notes_ai_draft.json` | The run's device notes, with `dnp3: not_established` and a reason for the 7 devices whose documents name DNP3 only for other products or software (three PowerMonitor meters, three GE EPM meters, the Micro830). | by the same draft |
| `review/second_pass_2026-10-14.md` | The second reading of every finding and every security passage of the sample, and the check of the outside sources (NIST SP 800-82r3, CISA 2026, ABB, DNP3 SAv5) with verbatim quotes and pages. | against the retained documents and the originals |
| `paper_appendix.tex` | The appendix for the paper: method, reconciled table, the devices with documented protection, and every passage with its page, retrieval date and SHA-256. Its numbers and quotes were taken from the run, the review and the report on 2026-10-14. If the review changes, they must be brought up to date. | generated once by a script that is not part of the tool |
| `reports/worksheet/` | Leads per device and capability, for the reviewer. | `worksheet` |
| `reports/sample_ai_draft/` | The sample run with the AI-drafted review. | `report --require-evidence` with the three files in `review/` |

The sample run took every document from an earlier run of the same 99 devices. It made three requests, all for one Siemens link that redirects to a host whose robots.txt answers 403, so the link was left alone. `verify` and `replay` pass.

### What the documents establish, in one paragraph

Each device is counted once, under the strongest protection of control traffic its retrieved documents establish:

- Encryption: 6 devices. Two of them are entries of one Siemens family that share one catalogue page.
- Authentication without encryption: 2.
- A security mechanism named, what it protects not stated: 1.
- Protection only through a separate device: 2.
- For the other 88, protection of control traffic is unknown:
  - for 12 a complete manual documents none;
  - for 7 only management access is protected;
  - for 69 the documents settle nothing.

All 11 devices with documented protection are currently sold; none of the 31 vendor-discontinued devices is among them. The counts are lower bounds: for example, an SEL application guide that the sample did not retrieve documents DNP3 over TLS for the SEL RTAC. They describe documents about catalogue entries, not installed devices or enabled settings.

**DNP3.** 32 sampled devices name DNP3 in their own documents. Counted by the strongest DNP3 protection documented:

| | Currently sold | Legacy | Lifecycle unknown | Total |
|---|---|---|---|---|
| Encrypted: DNP3 over TLS | 4 | 0 | 0 | 4 |
| Authenticated, not encrypted (Secure Authentication; off by default in the vendor's manual) | 1 | 0 | 0 | 1 |
| Encryption for its SCADA protocols, DNP3 not named | 1 | 0 | 0 | 1 |
| Only through a separate encrypting device | 2 | 0 | 0 | 2 |
| No DNP3 security documented (plaintext) | 16 | 7 | 1 | 24 |
| Devices | 24 | 7 | 1 | 32 |

Plaintext DNP3 is not only a legacy matter: 16 of the 24 current devices document no DNP3 security either. No vendor page states that support or firmware updates ended for any discontinued device; they say only that manufacture or sale ended. The plaintext count is an upper bound, since the SEL RTAC is one device whose DNP3 over TLS is documented in a guide the sample did not retrieve.

### The legacy definition was revised

The first definition, fixed on 2026-10-13, counted a device as legacy only when the vendor states that support has ended. No public page of the five vendors says so for any device, so the group was empty. After the draft review had been counted that way, the author widened legacy to every vendor-discontinued device. The revision is recorded in `configs/vendors.json` under `definitions.revisions`, travels into `sample.json`, and is printed at the top of every report made from that run.

## five_products/

The first study: one hand-picked product per vendor, from `configs/pilot.json`.

| File | What it is | Made with |
|---|---|---|
| `reviews.json`, `source_notes.json` | The AI-drafted review of the five products (42 rows) and the notes on its sources, as written against the first fetch. Left exactly as they were. | AI draft, from the leads and the retained text |
| `reports/as_reviewed/` | The report made from them at the time. Its `sources.json` is the record of the fetch the review was bound to. | `report`, on 2026-10-13 |
| `reviews_rebound.json` | The same rows carried over to the later fetch `runs/run1_x1_4`. Two product pages are dynamic and returned different bytes with identical text, so 14 rows were re-bound; each records both hashes. | `rebind --reviews five_products/reviews.json --old five_products/reports/as_reviewed --run runs/run1_x1_4 --out five_products/reviews_rebound.json` |
| `reports/rebound/` | The report from `runs/run1_x1_4` and the re-bound rows. | `report --require-evidence` |

## Making the reports again

From the top of the repository, with `DATA=data` and `S=study/catalogue_2026-10-13`:

```bash
python survey.py verify --run $DATA/runs/sample_2026-10-13_v2_0 --cache $DATA/cache
python survey.py report --run $DATA/runs/sample_2026-10-13_v2_0 \
    --reviews $S/review/reviews_ai_draft.json --source-notes $S/review/source_notes_ai_draft.json \
    --device-notes $S/review/device_notes_ai_draft.json \
    --require-evidence --out $S/reports/sample_ai_draft_again
```

`report` writes into the folder it is given and replaces a report that is already there, so the command above uses a new folder name.

To take the review further, copy `review/reviews_ai_draft.json`, change rows and the `reviewer` field as you confirm or correct them, and run `report` on the copy. A row marked `review_status: confirmed` must not leave any field "not assessed".
