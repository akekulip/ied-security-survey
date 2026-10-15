# Study files

What the survey has produced, and how each file was made. The tool is in the same repository, https://github.com/akekulip/ied-security-survey (public). The current outputs were made with version 2.3.0. Commands below are run from the top of the repository. The catalogue study's runs and fetched documents are in `data/` at the top of the repository.

**Nothing here is a confirmed finding yet.** Every review row was drafted by an AI assistant and says so in its `reviewer` field. The rows of 2026-10-13/14 say "Claude AI draft review; author confirmation pending". The D400 correction of 2026-10-15 says "Codex AI audit correction; author confirmation pending". The follow-up rows of 2026-10-15 say "Claude AI draft (audit follow-up 2026-10-15); author confirmation pending". The reports repeat that under "Reviewers on record". The publication gate (`--require-confirmed`) refuses to make publication output until a person has confirmed every row.

Fetched bytes and run directories are kept outside this folder. The five-product study uses `runs/` and `cache/` at the top of the repository. The catalogue study's are in `data/`, written `$DATA` below.

## Where to look first

| Question | Open |
|---|---|
| What goes in the paper? | `catalogue_2026-10-13/paper_2026-10-15/`. The folder holds:<br>• `summary.md`<br>• `dnp3_table.csv`<br>• `paper_appendix.tex`<br>• `paragraph.tex`<br>• `paper_manifest.json`<br>All are written by one command (below) and all are marked as an AI draft until the authors confirm the rows. |
| Which DNP3 entries document DNP3 security, of what kind, by lifecycle group, and which remain unresolved and why? | `catalogue_2026-10-13/paper_2026-10-15/summary.md` |
| Every finding, per device and interface, with quotes and hashes | `catalogue_2026-10-13/reports/targeted_draft_2026-10-15/` (`REPORT.md`, `findings_table.csv`, `dnp3_table.csv`) |
| What earlier work supports, and what it does not | `catalogue_2026-10-13/prior_work.md` |
| How the 2026-10-15 audit was applied and checked | `catalogue_2026-10-13/audit_2026-10-15/`. The folder holds:<br>• `commands.json`: every command with its exit code, versions and output hashes;<br>• `approved_urls.json` and `targeted_pass.json`: the bounded pass and its searches;<br>• `targeted_pass_outcomes.json`: what each approved document gave;<br>• `request_check.json`: every request of the pass checked against the approved list. |
| Where should a reviewer read for one device and capability? | `catalogue_2026-10-13/reports/worksheet/worksheet.md` |

## Correction of 2026-10-15

An external audit (`IED_Survey_Tested_Fixes_2026-10-15.zip`, kept untracked at the top of the repository) found a real error. The Multilin D400 brochure we had retained (source `e9650803a7d08f102554`, pdf-page 1) says "Secure tunneling from master station to the D400 via TLS for DNP3/TCP, Modbus/TCP and IEC 104". The draft review of 2026-10-13/14 counted the D400 as having no DNP3 security, because the tool kept the context of only the first keyword match on a page. Two statements are withdrawn:

- that none of the 31 vendor-discontinued sampled devices documents protection of its control traffic;
- that devices whose documents name no DNP3 security use plaintext. Such an entry is unknown: the retrieved documents establish neither lack of support nor plaintext operation.

What was done:

1. **Tool 2.2.1 (the audit's patch).** The tool now:
   - keeps every match context;
   - labels DNP3 results by what the documents establish, with integrity apart from authentication and external encryption only with its protocol scope;
   - checks extracted text against its recorded hash when building a report;
   - can refuse unconfirmed rows (`--require-confirmed`).

   `replay` now also compares the saved segments, location by location, and the recorded text digests.
2. **D400 correction.** The auditor's script wrote `review/reviews_ai_audit_2026-10-15.json` from `review/reviews_ai_draft.json`, whose hash it checks. The original is unchanged.
3. **Full-cache checks.** `sample_2026-10-13_v2_0` was verified byte for byte and rebuilt offline with rules 1.4.1 into `$DATA/runs/sample_audit_2026-10-15`; the rebuild was then replayed. All 308 extracted documents have the same bytes and the same text digest as before. The review was rebound and every quote checked again. All exit codes are in `audit_2026-10-15/commands.json`.
4. **One bounded pass for unresolved entries.**
   - **Scope.** Every DNP3 entry left unresolved, plus the two gaps the audit named.
   - **Searches.** At most two searches on the vendor's own site per entry, and at most two official documents.
   - **Gaps the audit named.**
     - RTAC: SEL white paper 112760 was already held by the pilot.
     - Micro870: manual 2080-UM002 was already held under the Micro830.
   - **Request control.** `crawl --approved-urls` let the run request only the listed addresses: 21 requests, none outside the list (`request_check.json`).
   - **What it found.**
     - The RTAC white paper documents TLS for the DNP3 server.
     - The Micro870 manual says DNP3 Secure Authentication ships disabled and, once enabled, defaults to version 2.
     - The C60 instruction manual (8.5x) states that DNP is not encrypted, while CyberSentry encrypts Modbus.
     - The SIPROTEC 5 Security manual documents TLS for IEC 61850 MMS, off by default, and nothing for DNP3.
   - **What it did not obtain.**
     - Schneider's download links returned a country-selector page instead of the documents.
     - The SICAM T manual answered 404.
     - SEL's instruction manuals are behind a sign-in.

   These entries remain unknown. `targeted_pass.json` lists every entry with its searches, and `targeted_pass_outcomes.json` lists what each approved document gave.
5. **Draft review of 2026-10-15.** `review/reviews_ai_draft_2026-10-15.json` adds draft rows for these documents. Every quote is checked against the retained text.
6. **The paper outputs.** They come from one command, so their counts are always those of the inputs. They are not repeated here.

The lifecycle label of `currently_supported` is now printed "currently listed", which is what it rests on: listed in the vendor catalogue without a notice of discontinuation. The stored states and the definitions are unchanged.

## catalogue_2026-10-13/

The five vendors' catalogues as listed on 2026-10-13, and a seeded sample of 99 catalogue entries drawn from them.

| File | What it is | Made with |
|---|---|---|
| `inventory/listing/` | Every catalogue entry in scope, placed by the rules in `configs/vendors.json`. `catalogue.json` is the raw listing and `requests.json` the log of the requests that fetched it. | `inventory --from $DATA/inventory/listing-2026-10-13` |
| `inventory/pages/` | The same after each product page was read. This is the sampling frame: 484 entries, of which 309 are currently listed, 168 discontinued with support not stated and 7 of unknown state. | `enrich --run $DATA/runs/census_2026-10-13 --vendors configs/vendors.json` |
| `census.json` | Crawl config of the census: one product page per catalogue entry, 485 entries. Run: `$DATA/runs/census_2026-10-13`. It was cut from the first listing inventory, which has since been deleted; the config keeps that inventory's SHA-256. | `sample --census` |
| `sample.json` | Crawl config of the sample: up to 4 entries per vendor, category and lifecycle state, seed 20261013, with the current definitions. Runs: `$DATA/runs/sample_2026-10-13_v2_0` (2026-10-13), `$DATA/runs/sample_targeted_2026-10-15` (current; same config). | `sample --per-stratum 4 --seed 20261013` |
| `review/reviews_ai_draft.json` | The AI-drafted review of 2026-10-13/14: 820 rows covering all 792 cells. Kept unchanged; superseded. | drafted from the worksheet and the retained text |
| `review/reviews_ai_audit_2026-10-15.json` | The same with the auditor's two D400 rows. | `apply_d400_correction.py` from the audit package |
| `review/reviews_audit_rebound_2026-10-15.json`, `review/reviews_targeted_rebound_2026-10-15.json` | The audit review carried over to the rebuilt run, then to the targeted run (no row needed rebinding: same documents, same text). | `rebind` |
| `review/reviews_ai_draft_2026-10-15.json` | **The current review**: the above plus the draft rows of the bounded pass, 821 rows. | drafted on 2026-10-15; every quote checked by `report --require-evidence` |
| `review/source_notes_ai_draft.json` | Document type and coverage for the 16 sources the review takes as complete manuals. | AI draft of 2026-10-13/14 |
| `review/device_notes_ai_draft.json` | The device notes, with `dnp3: not_established` and a reason for the 7 entries whose documents name DNP3 only for other products or software (three PowerMonitor meters, three GE EPM meters, the Micro830). | AI draft of 2026-10-13/14 |
| `review/second_pass_2026-10-14.md` | The second reading of 2026-10-14. Kept as written, with a superseded notice: it missed the D400. | against the retained documents |
| `audit_2026-10-15/` | The audit follow-up's records:<br>• `commands.json`<br>• `approved_urls.json`, `targeted_pass.json` and `targeted_pass_outcomes.json`<br>• `request_check.json`<br>• `recheck_v2_0_vs_rebuilt.json` | the commands named in `commands.json` |
| `reports/audit_draft_2026-10-15/` | The report of the rebuilt run with the D400 correction. | `report --require-evidence` |
| `reports/targeted_draft_2026-10-15/` | **The current report**: the targeted run with the current review. | `report --require-evidence` |
| `paper_2026-10-15/` | **The current paper outputs**, with their receipt. | `paper` |
| `prior_work.md` | Prior work: what each source supports and what it does not, and what was checked on 2026-10-15. | written by hand |
| `paper_appendix.tex`, `reports/sample_ai_draft/` | The appendix and report of 2026-10-14. Kept as made, with a superseded notice: they carry the D400 error and the plaintext wording. | an untracked script (appendix); `report` (report) |
| `reports/worksheet/` | Leads per entry and capability, for the reviewer. | `worksheet` |

### The legacy definition was revised

The first definition, fixed on 2026-10-13, counted a device as legacy only when the vendor states that support has ended. No public page of the five vendors says so for any device, so the group was empty. After the draft review had been counted that way, the author widened legacy to every vendor-discontinued device. The revision is recorded in `configs/vendors.json` under `definitions.revisions`, travels into `sample.json`, and is printed at the top of every report made from that run. "Legacy" in the tables follows that definition: vendor-discontinued, which says nothing about support, firmware updates or security.

## five_products/

The first study: one hand-picked product per vendor, from `configs/pilot.json`.

| File | What it is | Made with |
|---|---|---|
| `reviews.json`, `source_notes.json` | The AI-drafted review of the five products (42 rows) and the notes on its sources, as written against the first fetch. Left exactly as they were. | AI draft, from the leads and the retained text |
| `reports/as_reviewed/` | The report made from them at the time. Its `sources.json` is the record of the fetch the review was bound to. | `report`, on 2026-10-13 |
| `reviews_rebound.json` | The same rows carried over to the later fetch `runs/run1_x1_4`. Two product pages are dynamic and returned different bytes with identical text, so 14 rows were re-bound; each records both hashes. | `rebind --reviews five_products/reviews.json --old five_products/reports/as_reviewed --run runs/run1_x1_4 --out five_products/reviews_rebound.json` |
| `reports/rebound/` | The report from `runs/run1_x1_4` and the re-bound rows. | `report --require-evidence` |

## Making the outputs again

From the top of the repository, with `DATA=data` and `S=study/catalogue_2026-10-13`. Each command writes a new folder; give a new name if it exists.

```bash
# The run of 2026-10-13, checked byte for byte, then re-extracted with the current rules and checked again
python survey.py verify --run $DATA/runs/sample_2026-10-13_v2_0 --cache $DATA/cache
python survey.py rebuild --run $DATA/runs/sample_2026-10-13_v2_0 --cache $DATA/cache --out $DATA/runs/sample_audit_2026-10-15
python survey.py replay --run $DATA/runs/sample_audit_2026-10-15 --cache $DATA/cache --out $DATA/runs/sample_audit_replay_2026-10-15

# The bounded pass: only the approved addresses may be requested
python survey.py crawl --config $S/sample.json --out $DATA/runs/sample_targeted_2026-10-15 --cache $DATA/cache \
    --reuse $DATA/runs/sample_audit_2026-10-15 --reuse runs/run1 --approved-urls $S/audit_2026-10-15/approved_urls.json
python survey.py verify --run $DATA/runs/sample_targeted_2026-10-15 --cache $DATA/cache
python survey.py replay --run $DATA/runs/sample_targeted_2026-10-15 --cache $DATA/cache --out $DATA/runs/sample_targeted_replay_2026-10-15

# The report and the paper outputs from the current review
python survey.py report --run $DATA/runs/sample_targeted_2026-10-15 --reviews $S/review/reviews_ai_draft_2026-10-15.json \
    --source-notes $S/review/source_notes_ai_draft.json --device-notes $S/review/device_notes_ai_draft.json \
    --require-evidence --out $S/reports/targeted_draft_2026-10-15
python survey.py paper --run $DATA/runs/sample_targeted_2026-10-15 --reviews $S/review/reviews_ai_draft_2026-10-15.json \
    --source-notes $S/review/source_notes_ai_draft.json --device-notes $S/review/device_notes_ai_draft.json \
    --out $S/paper_2026-10-15
```

The crawl of the bounded pass needs the documents it first fetched, which are in the local cache but not in the repository (see `data/README.md`). Without them it would request those addresses again.

For publication, review `review/reviews_ai_draft_2026-10-15.json`:

- correct the rows;
- write your name in `reviewer`;
- set `review_status` to `confirmed`;
- fill every field still `not_assessed`.

Then run `paper ... --require-confirmed`, which refuses while any row is a draft. If not every entry can be checked, make a narrower reviewed subset in a review file of its own, and keep the full draft as the exploratory sample.
