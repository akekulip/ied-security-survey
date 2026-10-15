# IED security documentation survey

Collects what five IED vendors (SEL, Schneider Electric, Rockwell Automation, GE Vernova, Siemens) publicly document about the security of their relays, controllers/RTUs, PLCs and meters, and turns a reviewed reading of those documents into a report. It reads public web pages and PDFs only. It never contacts a device.

The current study's own files (inventory, sample, review, reports, paper appendix) are described in `study/README.md`.

This repository is private. It holds:

- **Branch `main`:** the tool (`iedsurvey/`, `survey.py`), tests, configs, the study's results (`study/`), and the five-product pilot's runs and fetched documents (`runs/`, `cache/`).
- **Branch `data`:** the catalogue study's run folders, inventory listings and fetched vendor documents, about 1.4 GB, kept apart so that cloning `main` stays small. Fetch it into its own folder outside any synced folder:

  ```bash
  git clone --branch data --single-branch https://github.com/akekulip/ied-security-survey.git ied_survey_data
  ```

  The commands in `study/README.md` call that folder `$DATA`. The fetched documents are vendors' public files, kept here for verification only; do not redistribute them.

## 1. Set up

Python 3.10 or later.

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate         # macOS / Linux
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

All tests should pass. `python survey.py --help` lists the commands, and `python survey.py <command> --help` lists a command's options. `python -m iedsurvey` does the same as `python survey.py`.

## 2. Quick check: the five-product pilot

```bash
python survey.py crawl --config configs/pilot.json --out runs/my_pilot --cache cache
python survey.py worksheet --run runs/my_pilot --out runs/my_pilot_worksheet
python survey.py report --run runs/my_pilot --reviews runs/my_pilot/review_template.json --out runs/my_pilot_report
```

The crawl fetches a few public pages and PDFs from the vendors' sites (seven in the last run). Open `runs/my_pilot_report/REPORT.md`. With the blank review template it shows what was read and no results; results only come from a review (step 4).

## 3. Run the catalogue survey

Keep the cache and runs outside a synced folder such as OneDrive. The cache for the 2026 study is about 1.5 GB. Set two names once per terminal:

```bash
$DATA = "$HOME/ied_survey_data"; $S = "study/my_survey"     # PowerShell
# DATA=~/ied_survey_data; S=study/my_survey                 # bash
```

Then run the steps in order. Each writes files you can read and correct before the next.

```bash
# 1. List every device in the vendors' catalogues and classify it by the rules in configs/vendors.json
python survey.py inventory --vendors configs/vendors.json --out $S/inventory/listing --cache $DATA/cache

# 2. Census: fetch one product page per catalogue device
python survey.py sample --inventory $S/inventory/listing/inventory.json --census --out $S/census.json
python survey.py crawl --config $S/census.json --out $DATA/runs/census --cache $DATA/cache

# 3. Read the product pages back: model names, categories, lifecycle wording
python survey.py enrich --inventory $S/inventory/listing/inventory.json --run $DATA/runs/census --vendors configs/vendors.json --out $S/inventory/pages

# 4. Draw a seeded sample: up to 4 devices per vendor, category and lifecycle state
python survey.py sample --inventory $S/inventory/pages/inventory.json --per-stratum 4 --seed 20261013 --out $S/sample.json

# 5. Crawl the sample, following links to manuals and data sheets; pages the census already fetched are not fetched again
python survey.py crawl --config $S/sample.json --out $DATA/runs/sample --cache $DATA/cache --reuse $DATA/runs/census

# 6. Check the run: stored bytes match their hashes, and extraction gives the same result offline
python survey.py verify --run $DATA/runs/sample --cache $DATA/cache
python survey.py replay --run $DATA/runs/sample --cache $DATA/cache --out $DATA/runs/sample_replay

# 7. Worksheet for the reviewer: per device and capability, where the security wording is
python survey.py worksheet --run $DATA/runs/sample --out $S/worksheet
```

Checks before going on:

- **After step 1:** read `$S/inventory/listing/inventory.csv`. Every catalogue entry is included, excluded with a reason, or unclassified. To change a rule, edit `configs/vendors.json` and re-apply it without asking the vendors again: `inventory ... --from $S/inventory/listing --out <new folder>`.
- **After step 3:** check the `lifecycle_evidence` sentences in `$S/inventory/pages/inventory.csv`.
- **An interrupted crawl:** run the same command again with `--resume` added. It continues without refetching.
- **One vendor only:** add `--only <pattern>` to `crawl`, for example `--only sel_`.

No command overwrites an existing output; give a new `--out` instead. The one exception is `report`, which replaces the report in its output folder.

## 4. Review

Copy the three templates the crawl wrote, then fill in the copies. The worksheet says where to read.

```bash
cp $DATA/runs/sample/review_template.json $S/reviews.json
cp $DATA/runs/sample/source_notes_template.json $S/source_notes.json
cp $DATA/runs/sample/device_notes_template.json $S/device_notes.json
```

**`reviews.json`**: one row per device, capability and interface. The capabilities are `authentication`, `integrity`, `encryption`, `dnp3_secure_authentication`, `tls`, `ipsec`, `cip_security` and `ssh`.

| Field | What to write |
|---|---|
| `status` | `supported`, `conditional`, `explicitly_unsupported` or `unknown` |
| `unknown_reason` | for `unknown` only: `not_enough_evidence`, `complete_document_silent` or `sources_conflict` |
| `source_ids`, `source_hashes` | the source id and its `sha256`, both from the run's `sources.json` |
| `evidence` | `[{"source_id", "location", "quote"}]`: location as `pdf-page:12` or `html-block:42`, and the quote verbatim, at least 20 characters |
| `interface`, `interface_class` | a short label such as `DNP3 server to SCADA master`; the class is `control_protocol`, `management` or `network` |
| `protocol`, `implementation`, `location`, `model_scope`, `hardware_revision`, `firmware` | what the document says; `not established` where it says nothing |
| `support_basis`, `conditions` | for supported or conditional: `built_in`, `firmware_upgrade`, `optional_module`, `licence`, `external_gateway` or `not_stated`. Anything but `built_in` is `conditional`, and `conditions` says what is needed. |
| `default_state` | for supported or conditional: `enabled`, `disabled` or `undocumented` |
| `activation_needs`, `activation_requirements` | for supported or conditional: `configuration`, `certificates_or_keys`, `compatible_master`, `licence_key`, `other` or `none_stated`, and a sentence describing them |
| `deployment_status` | leave `unknown`, unless `deployment_evidence` from an installation is cited |
| `reviewer`, `reviewed_at`, `rationale`, `review_status` | your name, the date, why; `draft` until checked, then `confirmed` |

`not_assessed` means "not looked at yet". A row left exactly as the template wrote it counts as not reviewed, so the review can be done in stages.

**`source_notes.json`**: per document, its `doc_type` (`device_profile`, `conformance_statement`, `security_guide`, `manual`, `datasheet`, `product_page`, `advisory`, `other`) and `coverage` (`complete` or `partial`), plus its own number, revision and date where it gives them. `complete_document_silent` is accepted only for a complete manual, device profile or conformance statement.

**`device_notes.json`**: per device, `identity_level` (`family`, `model`, `catalogue_number`) and, to change a lifecycle status, dated evidence from the vendor. A device counts as a DNP3 device when its own retrieved documents name DNP3. Set `dnp3` to `not_established` when they name it only for other products or software, or to `supported` when the search missed it; either needs a `dnp3_note` saying why.

## 5. Report

```bash
python survey.py report --run $DATA/runs/sample --reviews $S/reviews.json --source-notes $S/source_notes.json --device-notes $S/device_notes.json --require-evidence --out $S/report
```

The report refuses a row that breaks a rule and names the device and capability, for example a quote that is not at the cited location, or a hash that does not match the run. It writes:

- `REPORT.md`, which opens with the DNP3 table: the devices whose documents name DNP3, the strongest DNP3 protection documented for each (TLS, Secure Authentication, a separate device, or none: plaintext), counted for current and legacy devices, and listed with vendor, model, type and a link to the source;
- `findings_table.csv`, one line per device and interface;
- `devices.csv`, with lifecycle evidence;
- `dnp3.csv`, the DNP3 table one line per device;
- `findings.csv`, `evidence_index.json` and `sources.json`.

`--require-evidence` makes a verbatim quote mandatory for every result.

## 6. Other commands

| Command | When |
|---|---|
| `rebuild --run <run> --cache <cache> --out <new run>` | after the extraction rules change: re-extracts a finished run offline |
| `recheck --old <old run or report> --new <new run>` | after crawling again: which documents changed, and where old quotes are now |
| `rebind --reviews <file> --old <old run or report> --run <new run> --out <file>` | carries a review over to a refetch whose extracted text is unchanged |
| `sitemap --host <host> --match <pattern> --out <file>` | lists one vendor's sitemap by hand |

## Settings

- **`configs/vendors.json`** holds, per vendor:
  - where the catalogue is and the rules that classify each entry;
  - its lifecycle wording;
  - its crawl depth, page budget and which links to follow.
  
  Its `definitions` block says what each lifecycle state means and which states count as legacy. Every report prints it.
- **`configs/pilot.json`** is the five-product pilot config.

## What the crawler does and does not do

- **Public documents only.** It never signs in. A document behind a sign-in is counted and not requested.
- **robots.txt is followed for every host,** and a host whose robots.txt cannot be read is not asked. Only the hosts named in `robots_follow_redirects` may have a robots.txt redirect followed.
- **HTTPS only,** to the domains listed for each product, with a delay between requests.
- **Every fetched file is kept by its SHA-256 hash.** The request log, hashes and retrieval times are in the run directory.
- **A keyword match is a place to read, never a finding.** Findings come only from review rows that quote their source.
