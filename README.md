# IED security documentation survey

A runnable, bounded crawler and evidence-review workflow for Dr. Lin's proposed five-manufacturer survey. It reads public vendor documents; it does not discover, contact or test operational IEDs.

## Repository layout

| Path | What it holds |
|---|---|
| `survey.py` | The command. It runs the `iedsurvey` package beside it; `python -m iedsurvey` does the same. |
| `iedsurvey/` | The tool, one module per step: `fetch`, `extract`, `leads`, `crawl`, `runs`, `inventory`, `sampling`, `review`, `devices`, `worksheet`, then `findings`, `tables`, `glance`, `charts` and `report` for the report. `vocabulary` holds the terms every step shares and `cli` the commands. The package docstring lists them in the order the work flows. |
| `tests/` | One file per part of the tool; the fixtures they share are in `support.py`. |
| `configs/vendors.json` | The catalogue rules for the five vendors, and the definitions of the lifecycle states and of "legacy". |
| `configs/pilot.json`, `pilot/` | The five-product pilot as delivered with 1.0.0, unchanged since. |
| `study/` | The study's own files: inventories, crawl configs, reviews and reports. `study/README.md` says what each file is and how it was made. |
| `runs/`, `cache/` | Run directories and fetched bytes. Not in git. The catalogue study keeps its own outside the synced folder. |

## Quick start

Python 3.10+ is required. Commands below assume the extracted project directory.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python survey.py crawl --config configs/pilot.json --out runs/my_pilot --cache cache
```

On Windows PowerShell, create and activate the environment with `py -3.12 -m venv .venv` and `.\.venv\Scripts\Activate.ps1`; the remaining commands are the same. All files are written as UTF-8 with LF line endings on every platform.

The crawler refuses to overwrite an existing run. Each run records its configuration, source outcomes, redirects, request log, response-byte SHA-256 hashes, extraction locations, keyword leads and a review template. PDFs use one-based physical PDF page numbers, not the page number printed on the page. HTML locations are extraction block numbers bound to the source hash and tool version.

Each extracted source also records what the document says about itself and how it was obtained: `title`, PDF `pdf_created`/`pdf_modified`, `pages`, `empty_pages`, `page_errors` and `encrypted`, the `robots_basis` under which it was fetched, and `text_sha256`, a hash of the normalized extracted text. Dynamic HTML pages return different bytes on every request, so the raw-byte hash of such a page cannot be obtained again; the text hash can. Only a short allowlist of response headers is stored. Cookies and policy headers are dropped.

Download failures, robots exclusions, unsupported formats and empty extraction are logged as failures, never as lack of product support. PDF extraction needs selectable text; this version does not OCR scans or execute JavaScript. It does not bypass login, anti-bot challenges or robots restrictions. Robots rules are matched per RFC 9309, including `*` and `$` wildcards, and are resolved once per host and run. By default there are no automatic retries and a robots.txt that redirects is treated as unresolved rather than followed. This can reduce coverage and is recorded as such. Both can be enabled per config, see below. Every request attempt is in `requests.json`, including timeouts and oversized or truncated responses.

## What the survey establishes

For every device the crawler and the review together record the following. Each line names where it is written down and what it takes to write anything other than "unknown" or "not established".

| What | Recorded in | Needs |
|---|---|---|
| Device identity: manufacturer, exact model, hardware revision, firmware | product entry and device notes (`identity_level`); per finding `model_scope`, `hardware_revision`, `firmware` | what the cited document names; otherwise `not established` |
| Lifecycle status: currently supported, discontinued but supported, discontinued with support not stated, end of support, unknown | inventory, config and device notes (`lifecycle_status`, `lifecycle_evidence`) | a dated vendor source; a quote of the vendor's sentence for anything about support |
| Authentication, integrity and encryption, for each protocol and interface | review rows, one per capability and interface | cited source; a checked quote under `--require-evidence` |
| Support conditions: built in, firmware upgrade, optional module, licence, external gateway | `support_basis` and `conditions` on the row | a quote marked `about: conditions` for anything but built in |
| Default configuration: enabled, disabled, undocumented | `default_state` on the row | a quote marked `about: default` for enabled or disabled |
| Activation requirements: configuration, certificates or keys, compatible master, licence key | `activation_needs` and `activation_requirements` on the row | a quote marked `about: activation` |
| Deployment status: enabled or disabled in practice | `deployment_status` on the row, `unknown` by default | `deployment_evidence` from an installation; a vendor document is refused |

The same questions and the same four results apply to every device, whatever its lifecycle: supported, conditional, explicitly unsupported, unknown. "Legacy" is defined in the config a run is crawled with, as the lifecycle states it covers, and nothing is counted by lifecycle group in a run whose config does not define it (see Lifecycle and what "legacy" means).

## Config options

| Key | Default | Meaning |
|---|---|---|
| `sampling` | required | Statement of how the products were chosen. Copied into the manifest and the report. |
| `title` | `IED security documentation survey` | Report heading. |
| `definitions` | none | What each lifecycle state means, what "legacy" means in words (`legacy`) and which states it covers (`legacy_statuses`), the date they were fixed (`defined_at`) and every change since (`revisions`). Written by `sample` from `configs/vendors.json`. Without it the report counts nothing by lifecycle group. |
| `max_depth` | `0` | Link-following depth. Zero fetches the seeds only. |
| `max_pages_per_product` | `3` | Page budget per product. Seeds are always attempted; the budget limits followed links. |
| `follow_pattern` | `manual\|security\|datasheet\|\.pdf` | A link is followed when this matches its URL or its anchor text. |
| `delay_seconds` | `1` | Minimum gap between requests to one host. A longer robots crawl delay wins. |
| `timeout_seconds` | `25` | Per-request timeout. |
| `max_bytes` | `25000000` | Larger responses are failures. Full instruction manuals can exceed this. |
| `retries` | `0` | Extra attempts after a timeout, connection error or HTTP 429/502/503/504. Honours `Retry-After`. Every attempt is logged. |
| `robots_follow_redirects` | `false` | Follow up to five robots.txt redirects, each inside the product allowlist, as RFC 9309 describes. `true` for every host, or a list of domains such as `["rockwellautomation.com"]` to allow it for those hosts only. |

Per product: `id`, `domains` and `seeds` are required; `vendor`, `model` and `category` are needed by the report; `aliases` is an optional list of model strings; `lifecycle` is one of the five lifecycle states and comes with `lifecycle_evidence` (see Lifecycle and what "legacy" means). A product may set its own `max_depth`, `max_pages_per_product` and `follow_pattern`, since vendors lay out their sites differently. Other product keys are kept untouched, so inventory fields such as lifecycle status or catalog source can live in the same file. The config is checked before the first request. Structural errors stop the run; everything else is printed and stored in the manifest as `config_warnings`.

Enabling `robots_follow_redirects` is a methods decision, not a technical one. Example: `literature.rockwellautomation.com/robots.txt` redirects to the vendor's home page, so that host has no robots rules of its own and every Rockwell manual PDF on it is unreachable under the default. With the option on, the document is fetched and its record says `robots_basis: redirected:<final URL>`, so the paper can disclose it. A host that answers its robots.txt request with an error such as 403 stays off limits whatever this option says.

`crawl` takes two further options. `--only <pattern>` limits a run to the products whose `id` and vendor match, and the manifest records it. `--reuse <run>` takes any URL that an earlier run already fetched from the cache instead of requesting it again; the source record then says `reused_from`. A document that arrived in the earlier run and could not be read, such as a scanned PDF, is taken from the cache too and fails the same way; a request that failed is made again. Where several products share an address, each takes its own earlier record, so its bytes and retrieval time stay the ones recorded for it. The option may be given several times.

A document that sits behind a sign-in is not fetched. A link that points at a login address, or a request that is redirected to one, gets a source record with status `login_required`. A vendor page often lists many manuals whose download buttons all lead to the same sign-in address; the record's `link_count` says how many links did. The report counts these links apart from failures: they are documents that exist and were not used.

## Review, then report

Open `runs/my_pilot/candidates.json` and the `*.segments.json` files. Candidates are search leads only: **no regex can establish product capability**. Inspect the complete passage and applicable product/firmware, then edit a copy of `review_template.json`:

```bash
cp runs/my_pilot/review_template.json reviews.json
cp runs/my_pilot/source_notes_template.json source_notes.json
cp runs/my_pilot/device_notes_template.json device_notes.json
# Edit reviews.json: result, interface, model/hardware/firmware scope, support basis and conditions,
#   default state, activation, evidence quotes, reviewer, date, rationale.
# Edit source_notes.json: each document's own number, revision and date.
# Edit device_notes.json: identity level, lifecycle status with dated vendor evidence, release date.
python survey.py report --run runs/my_pilot --reviews reviews.json --out reports/my_pilot \
    --require-evidence --source-notes source_notes.json --device-notes device_notes.json
python survey.py verify --run runs/my_pilot --cache cache
python survey.py replay --run runs/my_pilot --cache cache --out runs/my_pilot_replay
```

The review can be done in stages. Rows left exactly as the template wrote them are ignored and shown as not reviewed, so `report` runs at any point and its coverage line shows how far the review has got. A row that is partly filled in is an error that names the cell; it is never dropped silently.

### Leads

Each candidate carries:

- `matched`, the words that matched, and `match_count` for its page or block. `["SFTP"]` is not an SSH statement and `["VPN"]` is not IPsec, and the lead says which it was.
- `context`, widened to whole sentences, and for HTML `context_before` and `context_after`, the two neighbouring blocks on each side. A heading or table label is never shown alone.
- the nearest preceding `heading` (HTML heading or PDF bookmark) and, when the product has `aliases`, whether the model string appears in the same passage.
- `lead_type`: `capability` for the eight review cells, `related` for neighbouring terms, `statement` for the four statement groups below, `profile` for items of a DNP3 Device Profile.

These help find and scope a passage. They are not verdicts and every candidate stays `unreviewed`. A lead is a place where a term occurs. Several leads in one document are still one document about one product, so lead counts are never device counts.

`statement_leads.json` holds four groups, apart from `candidates.json`. The first two say something about a capability being absent:

- `non_support_statement`: a capability named in a sentence that denies it, such as "TLS is not used", "does not support Secure Authentication" or "no support for IPsec". Conditional wording ("if the device does not support …") is skipped. These are searched for as deliberately as claims of support, because an explicit denial is the only route to `explicitly_unsupported`.
- `plaintext_statement`: unencrypted, not encrypted, no encryption, plain or clear text.

A statement about the product itself can support `explicitly_unsupported` after review. A general statement ("information is often transmitted in plain text") supports nothing about a product. It is a literature lead for the paper's motivation, to be cited as what that vendor wrote, and never a measured share of deployments.

The other two point at the wording a reviewer needs for the facts beyond the result:

- `default_statement`: a security term in a sentence with "by default", "default setting", "factory default" or "out of the box". Where to read for `default_state`.
- `requirement_statement`: a security term in a sentence with "requires", "optional", "licence", an ordering option or "firmware version N or later". Where to read for `support_basis`, `conditions` and `activation_needs`.

They are places to read. "TLS is disabled by default" on a page about the web server says nothing about DNP3, and the worksheet lists such a lead only beside the capability its words name.

### DNP3 Device Profiles

A DNP3 Device Profile is the vendor's own answer sheet for a product's DNP3 implementation. Its section 1.12, Security Parameters, states which Secure Authentication version is supported and whether TLS is used, item by item, including answers such as "Not relevant – TLS is not used". When a source is a device profile, the tool splits that section into its numbered items and writes them to `<source_id>.profile.json`: number, title, page, the item's whole text, and the option lines that appear marked. Each item is also a `profile` lead.

Marks are read by a heuristic (a leading `X` or a checked-box character), because vendors mark options differently and some marks do not survive text extraction. An item with no detected mark still shows its full text. Nothing here is a finding until a review row quotes the item.

### Review rows

A capability is recorded once per interface, because TLS for a web page and TLS for DNP3 are different findings. The cells are the three properties asked about for every interface, `authentication`, `integrity` and `encryption`, and the mechanisms that may provide them: `dnp3_secure_authentication`, `tls`, `ipsec`, `cip_security`, `ssh`. Every row with a result other than `unknown` states:

- `interface`: a short label, written the same way on every row that belongs to that interface, for example `DNP3 server to SCADA master`. Rows of one product with the same label are consolidated into one line of the findings table.
- `interface_class`: `control_protocol` (DNP3, IEC 61850, CIP and similar traffic), `management` (engineering tools, web, user login, logging, file transfer) or `network` (protection applied below the protocol, such as IPsec or MACsec).
- `protocol`, `implementation`, and what the finding applies to: `model_scope` (the exact model or order code the document names, or `family`), `hardware_revision` and `firmware`. Write `not established` where the document does not say. A family manual is evidence for the family, not for each model in it.
- `review_status`: `draft` until a person has checked the row against the source, then `confirmed`. An empty value counts as `draft`.

A `supported` or `conditional` row also states how the capability is obtained, how it ships and what switching it on takes:

| Field | Values | Rule |
|---|---|---|
| `support_basis` | list from `built_in`, `firmware_upgrade`, `optional_module`, `licence`, `external_gateway`, `not_stated` | `supported` means `built_in` alone. Anything else is `conditional`, with `conditions` saying what is needed. |
| `default_state` | `enabled`, `disabled`, `undocumented` | `undocumented` means the documents read do not say. It does not mean disabled. |
| `activation_needs` | list from `configuration`, `certificates_or_keys`, `compatible_master`, `licence_key`, `other`, `none_stated` | Any need named here is described in `activation_requirements`. |
| `deployment_status` | `unknown`, `enabled`, `disabled` | See below. |

A reviewer who has not looked yet writes `not_assessed` in these fields, which is different from saying the documents are silent. Rows from a review written before 1.6.0 lack the fields and are read as `not_assessed`. A row cannot be `confirmed` while any of them is `not_assessed`.

A capability that exists only through an external gateway is `conditional` with `support_basis: ["external_gateway"]`. The report counts it in a column of its own and never as a capability of the device.

**Deployment status** is what an operator actually enabled, which no vendor document can show. It stays `unknown` unless the row cites `deployment_evidence`: a list of `{"kind", "reference", "date", "scope"}`, for example a utility's configuration audit of named relays. A source of the run, or its URL, is refused as deployment evidence. The report states for how many findings deployment is unknown; expect that to be all of them.

An `unknown` row may say why in `unknown_reason`: `not_enough_evidence` (the default), `complete_document_silent` or `sources_conflict`. The last two cite their sources and interface like a result does. To say that nothing is established for control traffic while something is established for management, keep a plain `unknown` row with an empty `interface` next to the management row.

A row may carry `evidence`, a list of `{"source_id", "location", "quote"}` with the exact segment location (`pdf-page:10`, `html-block:42`) and a verbatim quote of at least 20 characters. A location may also be a short run of consecutive segments, `html-block:10-13`. `report` checks that each quote occurs there, ignoring whitespace, typographic differences and hyphens between letters, since a PDF line break hides whether a hyphen belongs to the word. An evidence item may say what it is `about`: `capability` (the default), `conditions`, `default` or `activation`. `--require-evidence` makes a capability quote mandatory for every result other than `unknown`, and a quote of its own for a default of enabled or disabled, for a support basis other than built in, and for stated activation needs. The check proves the words are in the cited passage. It does not prove they support the claim.

### Device notes

`device_notes_template.json` has one record per product, filled from the config: manufacturer, model as listed, `lifecycle_status` with the `lifecycle_evidence` the inventory found, and empty `identity_level`, `release_date` and `release_evidence`. A reviewer corrects and completes a copy, and `report --device-notes` merges it.

- `identity_level` is `family`, `model` or `catalogue_number`. Catalogue entries are often families ("MiCOM P14x", "CompactLogix 5380 Controllers"); the survey keeps the catalogue entry as its unit and does not expand families into models.
- `lifecycle_status` other than `unknown` needs at least one evidence item from the vendor: a source of the run (`source_id`, optionally `location` and `quote`) or a `url` on the product's domains, with a date. The date is `stated_date`, the one the vendor's sentence gives, or failing that the retrieval date. `end_of_support` and `discontinued_supported` need the vendor's sentence as a `quote`; where the item cites a location in a source of the run, the quote is checked there.
- `release_date` needs `release_evidence` of the same kind. It is recorded apart and never decides the lifecycle status.

Without `--device-notes` the report uses what the config carries, under the same rules: a lifecycle status without dated vendor evidence is refused, not printed.

### Source notes

`sources.json` links every source to its URL, retrieval time and SHA-256. The document's own number, revision and date are read off the document by a person and entered in a copy of `source_notes_template.json`, keyed by `source_id`. `document_hints` in that template are snippets found near revision and date markers; they are aids, not answers. Leave a field empty when the document does not say. The report then shows "not established".

The notes also carry `doc_type`. The tool fills `doc_type_suggested` from the title, URL and opening text; a person confirms it by setting `doc_type`. The types, roughly from most to least direct about what one product and firmware can do:

| `doc_type` | What it is |
|---|---|
| `device_profile` | DNP3 Device Profile: itemised capabilities and current values for one product |
| `conformance_statement` | Security or protocol conformance statement, PICS or PIXIT |
| `security_guide` | Security or hardening guide, white paper or application technique |
| `manual` | Instruction, operations or communications manual |
| `datasheet` | Data sheet, brochure or flyer |
| `product_page` | Marketing web page |
| `advisory` | Vulnerability advisory: says what was wrong, and only indirectly what exists |
| `other` | Anything else; say what in `note` |

`coverage` says whether the source is the whole document (`complete`) or an excerpt such as one chapter or one web page of a manual (`partial`). Only a complete device profile, conformance statement or manual can support an `unknown` whose reason is `complete_document_silent`.

The order is guidance for weighing evidence, not a score. A manual for the exact firmware can outweigh a device profile for another one. The report shows the type beside every evidence reference, for example `S1 [manual]`, and `[type not confirmed]` until someone has set it.

### The report

`REPORT.md` opens with the definitions the run was crawled under, then:

- **Devices:** manufacturer, model, category, identity level, lifecycle status with its dated vendor evidence, release date. `devices.csv` holds the same for every device, with a `legacy` column: yes, no, or unknown where the lifecycle state is.
- **Summary** by vendor and category, and by lifecycle group where the config defines the groups, with the number of catalogue entries beside the number in the run.
- **Findings by product and interface:** manufacturer, model, lifecycle, what the evidence applies to (model, hardware revision, firmware), protocol/interface, authentication, integrity, encryption, support conditions, default, activation, deployment, evidence, review status. `findings_table.csv` holds the same rows with every quote and the source URL and hash.
- **Counts:** products per capability under each of the four results. Unknown is one result, followed by columns that say why: complete document silent, sources conflict, a result for another interface only, not enough evidence. "Via external gateway only" and "not reviewed" are counted apart.
- **Default configuration, activation and deployment:** per capability, how many supported or conditional findings ship enabled, disabled or undocumented, how many state activation needs, and for how many deployment is unknown.

**The question first.** Once any cell is reviewed, the report opens with what the survey is for: for legacy devices and for every other lifecycle state, what the reviewed documents establish about protecting control traffic. Each device is placed once, under the strongest of:

| Placed under | Meaning |
|---|---|
| Encryption documented | `encryption` is supported or conditional for a control protocol. Only this group need not be plaintext. |
| Authentication or integrity documented, encryption not | For example DNP3 Secure Authentication: messages are authenticated and still readable. |
| A security mechanism is named, what it protects is not stated | A mechanism row is positive and no property row is. |
| Only through an external gateway or encrypting device | The device itself does not provide it. |
| Vendor states it is not protected | An explicit statement of non-support. |
| A complete manual was read and documents none | Unknown with the reason "complete document silent". Not the same as a vendor statement. |
| Documented for management access only | Login, web or engineering-tool protection; says nothing about the control protocol. |
| Not settled by the public documents | Typically only a product page or brochure could be read. Not the same as unprotected. |

One sentence per group gives the counts. Legacy is one group, with every lifecycle state it covers listed under it, and each other state is a group of its own. The chart `answer` draws those groups and the vendors, `answer-mechanisms` shows which mechanism (DNP3 Secure Authentication, TLS, IPsec, CIP Security, SSH) is documented for control traffic in each group, and the section "Control traffic, device by device" lists every reviewed device with whether it is legacy, its lifecycle state, placement, the three properties, the mechanism and the most direct document read. `charts/devices-control-traffic.json` holds the same per device. A lifecycle state that counts as legacy is shown also when it holds no device. The tables further down stay by lifecycle state, so the legacy group can always be taken apart again.

All of this is what documents say a device can do. Whether it is switched on anywhere is deployment, which stays unknown.

**At a glance.** The report also draws what the run holds, as SVG files in `charts/` beside `REPORT.md`:

| Chart | What it shows | What it does not show |
|---|---|---|
| `catalogue-lifecycle`, `catalogue-category` | Every classified catalogue device by vendor, lifecycle state and category: the sampling frame. | Anything about security. |
| `evidence-base` | The most direct kind of document that could be read for each device, by vendor and by lifecycle state. | Whether a capability exists. It shows how much the review can settle. |
| `not-used` | Documents that exist but were not read: behind a sign-in, refused by the host, unreadable, or beyond the page budget. | Devices; it counts links and sources. |
| `mentions`, `mentions-lifecycle` | Devices whose public documents contain at least one lead for each capability. | Findings. A mention may be a denial or concern another interface, and a group with only brochures shows few mentions whatever its devices can do. |
| `results`, one per lifecycle state, and `results-legacy` where legacy covers several states | Reviewed results per capability for control traffic, in the four results, with unknown split by reason and "not reviewed" in grey. | Anything for a cell nobody has reviewed. It is drawn only once a row is reviewed. |

The charts are written by the tool itself, without a plotting library. `charts/data.json` holds the series behind every chart, each chart has a sentence of the same numbers beside it, and the tables further down carry them in full, so no mark has to be taken on trust. Lifecycle views appear only for a run whose config defines the lifecycle states.

Reading the table:

- The authentication, integrity and encryption columns show what the rows for those properties on that interface say. Nothing is inferred from a mechanism: where only a `tls` or `ssh` row exists, the cell points to it and says the property was not assessed.
- Every product has a control-protocol row, even when nothing is established, so that silence about DNP3 is stated as unknown.
- The capability matrix puts a mark in parentheses when a result exists only for a management or network interface.
- Counts are of products, never of leads or table rows, with the number of products as the denominator.

The report also writes `findings.csv`, `findings.json`, `evidence_index.json`, `candidate_counts.json` (leads by type, never device counts) and `sources.json`, the source manifest with the notes merged in. The Markdown further lists each finding with its quotes, the unresolved cells, the items read from any device profile (labelled as not reviewed), the documents examined with their types, and the sources that yielded no text. Validation rejects records without reviewer, date and rationale, unbound hashes, evidence from another product, failed-source support claims, misquoted evidence, results without an interface class, conditional results without conditions, a `supported` result that is not built in, deployment claims without evidence from an installation, lifecycle states without dated vendor evidence, and duplicate rows for one product, capability and interface. Every refusal names the cell. The reviewer must establish semantic correctness; hash and quote checking cannot do that.

The delivered `pilot/` contains the reviewed pilot, request/source manifests, short evidence excerpts and tests log. Review identity is explicitly `Codex AI review; author confirmation pending`. It is a working research artifact, **not a publication-ready population survey**. All outcomes, including the failed Siemens PDF request, are retained. `pilot/REPORT.md` is the entry point.

## Classification rules

Every capability, for every device and interface, has one of four results.

| Status | Required interpretation |
|---|---|
| supported | Explicit documentation for this product/family and stated interface, built into the device. Configuration may still be required; `default_state` and `activation_needs` say so. |
| conditional | Explicit support that depends on a firmware upgrade, an optional module, a licence or an external gateway. State which, and the conditions. |
| explicitly_unsupported | Explicit vendor statement of non-support for the scoped feature. Silence is insufficient. |
| unknown | The examined evidence does not establish support or non-support. |

An unknown records why where the review can say:

| `unknown_reason` | Meaning |
|---|---|
| `not_enough_evidence` | The default. No document, only part of the documentation, or nothing in it that settles the question. |
| `complete_document_silent` | A complete manual, device profile or conformance statement was searched in full and does not mention the feature. The tool checks this. It is a statement about the documentation, not about the device, and it is never counted as unsupported. |
| `sources_conflict` | Applicable sources disagree. Keep both and resolve firmware, date and scope before analysis. |

Reviews written before 1.6.0 used `not_documented` and `conflicting` as results of their own. They are read as `unknown` with the second and third reason.

Always separate:

- DNP3 Secure Authentication from encryption. An authentication result alone does not establish payload confidentiality.
- TLS for engineering/web/management interfaces from TLS for DNP3 or another control protocol.
- Built-in capability from an optional communication module or an external gateway.
- Product family, exact catalog model and firmware version. A family example must not be counted as several confirmed models.
- Capability from configuration, default enablement and real deployment. The survey cannot measure plaintext prevalence.
- Current documentation from historical documents. Keep revision, publication date and retrieval date separately; HTTP Last-Modified is not automatically the document's publication date.

`ipsec`, `tls`, `cip_security`, `dnp3_secure_authentication`, `authentication`, `integrity`, `encryption`, and `ssh` are overlapping search categories, not disjoint counts. In particular, do not add their totals as device counts. Decryption is generally the counterpart of documented encrypted communication; do not infer an independently supported interface from that word alone.

Those eight are the review cells and the only source of denominators. `integrity` leads are integrity wording about messages or data, HMAC, GMAC, CMAC and message authentication codes; a DNP3 "integrity poll", "signal integrity" and digitally signed firmware are not leads, since none of them is the integrity of a protocol. A capability group holds only terms that name that capability. Neighbouring terms have their own lead-only groups that never become cells: `vpn`, `sftp`, `macsec` and `iec_62351`. A recommendation to use a VPN does not establish native IPsec support, and an SFTP mention is not an explicit SSH statement. The four statement groups are a third kind, kept in their own file as described under Leads. Whether MACsec or IEC 62351 should become review cells is a protocol decision to take before the inventory is frozen, because it changes every denominator.

`cip_security` means ODVA CIP Security. NERC CIP is excluded from that group. A bare "secure authentication" counts as a DNP3 Secure Authentication lead only when DNP3, IEEE 1815 or IEC 62351-5 is mentioned on the same PDF page, in the block's heading, or within three HTML blocks.

## Lifecycle and what "legacy" means

It is widely said that legacy devices have no security. The survey does not assume it. It asks the same questions of every device and records the answers in a form a reader can check, and it does not call a device legacy until a stated criterion is met.

**Lifecycle state and legacy are two things.** Every device has one of five lifecycle states, each resting on what the vendor says in a dated source. Legacy is a definition on top of them. The `definitions` block of `configs/vendors.json` says in words what legacy means (`legacy`) and names the states it covers (`legacy_statuses`). Only the three states in which the vendor has withdrawn the product can be named: a device still on sale, or one whose state nobody could establish, is legacy under no definition. A block without `legacy_statuses`, as every config before 2.0 has, means end of support alone.

| State | Meaning | Legacy as delivered |
|---|---|---|
| `currently_supported` | Listed in the vendor's current catalogue on the inventory date without a notice of discontinuation, or stated by the vendor to be on sale and supported. | no |
| `discontinued_supported` | The vendor states that manufacture or sale has ended and that support continues. | yes |
| `discontinued_support_not_stated` | The vendor states that manufacture or sale has ended; no statement about support was found. | yes |
| `end_of_support` | The vendor states that support has ended. | yes |
| `unknown` | None of the above is established. | no |

`sample` copies the block into the crawl config, so it is covered by the config hash in the run's manifest. The report prints it, counts legacy as one group and still counts every state on its own. A run whose config has no definitions is not counted by lifecycle group at all.

**The definition was revised once, and the report says so.** It was first fixed on 2026-10-13 as end of support alone. Public product pages say when manufacture ended and almost never when support ended, so that definition put no device in the legacy group: of the 484 catalogue devices, 309 are currently supported, 168 are discontinued with support not stated, 7 are unknown and none has a public end-of-support statement. After a first, AI-drafted review of the 99 sampled devices had been counted that way, the author widened legacy to every discontinued device. A definition changed after results were seen is not one fixed before any count. The change is therefore recorded in `definitions.revisions` with its date and what had been counted by then, the tool refuses a revision that leaves that out, and the report lists it under the definitions and no longer prints that they were fixed before any result was counted. The sample, the documents and the review rows are the same under both definitions; only the grouping differs.

What does not decide the state: the protocol a device speaks, a security feature it lacks, the age of its manual, and the vendor's own word "legacy" on a web page. That word is kept in `vendor_label`, beside "obsolete", "active mature" and "under last-time buy", and the state stays whatever the vendor's statements about manufacture and support establish. Release dates are recorded separately and never decide the state.

**Every state other than unknown rests on dated vendor evidence**: the catalogue file that listed the product, with its hash and retrieval date, or the vendor's sentence with the page it was read on, the retrieval date and the date the sentence itself gives ("as of April 8, 2011"). A state without it is refused at report time.

**What the legacy group now is.** Under the delivered definition it is 168 of the 484 catalogue devices, every one of them "discontinued, support not stated": the vendor says the device is no longer made or sold, and nothing public says whether it is still supported. A statement about legacy devices from this survey is a statement about discontinued devices, and the paper should use that word at least once. The 7 devices of unknown state are not counted as legacy; they include products a vendor files under a "legacy" heading without a notice that manufacture has ended. A reviewer who finds such a notice, or an end-of-support statement, enters it in the device notes with its quote.

**Silence in a manual.** Where a complete manual does not mention a capability, record `unknown` with `unknown_reason: complete_document_silent` for the capability on that interface, with the firmware scope the manual states. No quote is possible for silence. Instead `report` checks the row mechanically: every cited source must be a complete manual, device profile or conformance statement (`doc_type` and `coverage: complete` in the source notes), and the keyword search must have found no lead for that capability in it. If leads exist, the report refuses the row until they are reviewed. Where the vendor says so in words, for example a device profile marked "TLS is not used", record `explicitly_unsupported` with the quote. The two are counted apart.

What this supports in the paper: "for N of M devices the vendor has discontinued, the complete product manual documents no authentication or encryption for DNP3", next to the same count for currently supported devices. It does not support "these devices cannot be secured", since an external gateway or a later firmware may add protection, and it says nothing about how many such devices are deployed or how they are configured.

## From five products to the vendor catalogues

The pilot's five products were hand-picked with security keywords in mind, one per vendor. That exercises the tool. It cannot say anything about a vendor's range. The wide survey takes its devices from each vendor's own catalogue instead, by device category and not by security search hits, in the steps below. Every step writes files a person can read and correct before the next one runs.

```bash
DATA=~/ied_survey_data     # cache and runs; keep them out of a synced folder such as OneDrive
S=study/catalogue_2026-10-13
python survey.py inventory --vendors configs/vendors.json --out $S/inventory/listing --cache $DATA/cache
python survey.py sample    --inventory $S/inventory/listing/inventory.json --census --out $S/census.json
python survey.py crawl     --config $S/census.json --out $DATA/runs/census --cache $DATA/cache
python survey.py enrich    --inventory $S/inventory/listing/inventory.json --run $DATA/runs/census --vendors configs/vendors.json --out $S/inventory/pages
python survey.py sample    --inventory $S/inventory/pages/inventory.json --per-stratum 4 --seed 20261013 --out $S/sample.json
python survey.py crawl     --config $S/sample.json --out $DATA/runs/sample --cache $DATA/cache --reuse $DATA/runs/census
python survey.py worksheet --run $DATA/runs/sample --out $S/reports/worksheet
```

`study/README.md` lists the files these steps produced for the delivered study, with the run each report was made from.

### 1. Inventory

`configs/vendors.json` says, per vendor, where the catalogue is and how to read it:

| Key | Meaning |
|---|---|
| `sitemaps`, `sitemap_filter` | The vendor's sitemap files. The filter picks which parts of a sitemap index are worth a request. |
| `scope` | Pattern for the sitemap URLs that are product pages of the kinds surveyed. |
| `rules` | Ordered rules giving a category: `protective_relay`, `controller_rtu`, `plc` or `meter`. |
| `exclude` | Ordered rules with a `reason`: accessories, software, test equipment, I/O modules, family index pages. An exclusion beats a category. |
| `definitions` | What each lifecycle state means, what "legacy" means and which states it covers, and every revision. Copied into every config `sample` writes. |
| `lifecycle` | Rules on the listing. `value` is a lifecycle state; `vendor_label` keeps the vendor's own word, for example `legacy` for a GE URL ending in `-legacy`, without letting it decide the state. Without a match the entry is `currently_supported`, with the listing as its dated evidence. |
| `lifecycle_text` | Wording on the product page that establishes a state, for example a notice that manufacture has ended. Applied by `enrich`, which keeps the sentence, the page, the retrieval date and any date the sentence gives. A rule may set `within`, the number of opening characters of the page it reads. |
| `crawl` | `max_depth`, `max_pages_per_product` and `follow_pattern` for that vendor's pages in the sampled crawl. |
| `adapter` | Used where the catalogue is not a sitemap. SEL product pages are empty without JavaScript, so its list is read from the JSON the site's own product selector loads. |

Each rule reads one field, named by `on`: `url`, `slug` (the last path segment) or `text` (the model name and, where the listing has one, the vendor's one-line product type). The first matching rule wins.

`inventory` fetches the listings through the same robots-checked, cached and logged fetcher as a crawl and writes `inventory.json`, `inventory.csv`, `catalogue.json` (the raw listing) and `requests.json`. Every catalogue entry in scope ends up in exactly one state, with the rule that put it there:

- included, with a category and a lifecycle;
- excluded, with the reason;
- unclassified, when no rule matched. These are listed, never dropped. Their product pages are read in the census so that the page's own opening words can classify them.

Read `inventory.csv` before going on. The rules are judgment calls about what counts as a device, and the file is where a reader checks them. After changing a rule, `inventory --from <previous inventory directory>` applies the new rules to the saved listing without asking the vendors again. The inventory keeps the day the catalogues were listed as `listed_at`, and that day, not the day the rules were last applied, is the inventory date a sample states.

### 2. Census, then what the product pages say

`sample --census` writes a crawl config with one product page per catalogue entry and no link-following. `enrich` then reads those pages back into a new inventory directory: the page title becomes the model name, unclassified entries are classified from their page text or stay unclassified, and a `lifecycle_text` match sets the lifecycle with the matched sentence kept as `lifecycle_evidence`. Where a product page cannot be read without JavaScript, the census requests the product's listed public documents in its place.

The wording a vendor uses is only known once its pages have been read, so `lifecycle_text` rules are written at this point. `enrich --vendors` applies the current rules file and stores it, with its hash, in the new inventory; without the option the rules saved in the inventory are used. Check every `lifecycle_evidence` sentence in `inventory.csv` after a change. Two things went wrong on the first pass over real pages and shaped the delivered rules: a family page that says one variant "has been discontinued" is not a discontinued family, which is what `within` is for, and words such as "migrate" appear on current products too.

Lifecycle is what the vendor's catalogue and page say on the inventory date, in the states the `definitions` fix. A device still listed without a notice is `currently_supported` even if the design is twenty years old, and a vendor whose catalogue shows no lifecycle wording at all has every device recorded that way. The rules delivered here found notices of ended manufacture or sale and no statement of ended support on any product page; see Lifecycle and what "legacy" means.

### 3. Sample

`sample --per-stratum N --seed S` draws up to N devices from every stratum of vendor, category and lifecycle state, so that devices in every lifecycle state are asked the same questions. Strata with fewer entries are taken whole. The same inventory and seed give a byte-identical config, each stratum has its own generator so that adding a vendor does not move another vendor's draw, and the config records the definitions, the seed, the inventory's SHA-256 and the `frame`: per stratum, how many entries the catalogue has and how many were selected. The report prints that frame, so every count has its denominator beside it.

This is a sample of catalogue entries. It supports statements such as "of the 4 sampled discontinued GE relays, public documents establish DNP3 Secure Authentication for none". It does not support statements about installed devices, and with a handful of devices per stratum it does not support percentages.

### 4. Sampled crawl and worksheet

The sampled config applies each vendor's `crawl` settings, so documents linked from the product page are followed. Links are tried in order of how directly the document type speaks about one product: DNP3 device profile first, then conformance statements, security guides and manuals, then data sheets and brochures. A communications or protocol manual is tried before other manuals. `--reuse` keeps the census pages from being requested twice.

Each vendor's `crawl` settings were written after looking at what its product pages link to, and they are the place to look when a run fetches the wrong things. Two examples from the first run: a GE product page links to resource lists and only those lists link to files, so GE needs depth 2 and a budget that leaves room for files after the lists; and a pattern as loose as `catalog` also matches a web shop's catalogue tree.

`worksheet` lays the result out for the reviewer: per product its lifecycle evidence and its sources with their suggested types, and per capability where the leads are, with the matched words, or which sources have none, and where default and requirement wording names that capability. It also writes a copy of the review template with those hints in a `_hints` field beside each cell. The worksheet proposes no result. A lead is a place to read, and "no lead" in a product page is not a statement about the device.

### What a wide run can and cannot show

Only public documents are read. Full instruction manuals of several vendors sit behind a sign-in, or on hosts whose robots.txt cannot be read, and those documents are counted and left alone. For many devices the public material is therefore a product page and a brochure, and most of their cells stay `unknown`. The share of devices for which the public documentation settles nothing is itself a result, reported per vendor, category and lifecycle. It must not be read as those devices lacking security, and an unknown may be recorded as "complete document silent" only where a complete manual was read (see Lifecycle and what "legacy" means). Default configuration and activation requirements can only be answered where a manual was readable, and deployment status not at all.

A report on a wide run stays readable before and during the review:

- With more than 25 unreviewed products, the findings table, the capability matrix and the list of unresolved cells show only products that have a review row, and each says how many it left out. The summary by vendor, category and lifecycle and the counts by category cover every product.
- With more than 60 extracted sources, "What was read" counts them by vendor and document type, and "Sources examined" lists only the sources a review row cites. `sources.json` in the report directory lists all of them.
- With more than 40 sources that yielded no text, they are counted by vendor and outcome instead of listed.

### One vendor's sitemap by hand

The `sitemap` command lists a single sitemap, filters it and writes a dated, hashed JSON file. It is the manual counterpart of `inventory` for a vendor that has no entry in `configs/vendors.json` yet.

```bash
python survey.py sitemap --url https://www.gevernova.com/electrification/sitemap.xml \
    --match protection-control-metering --out study/sitemaps/ge_catalog.json
python survey.py sitemap --host selinc.com --match "selinc.com/products/" --out study/sitemaps/sel_catalog.json
```

`--host` reads the sitemap locations from that host's robots.txt. Sitemap index files are followed up to `--max-files`; files left unfetched are listed in the output. `--match` is a regular expression on the full URL. Do not start it with a bare `/`: Git Bash on Windows rewrites such an argument into a file path.

Query templates for manual discovery (search-engine API not included):

```
site:<official-domain> "<model>" manual
site:<official-domain> "<model>" "DNP3" "secure authentication"
site:<official-domain> "<model>" "TLS"
site:<official-domain> "<model>" "IPsec"
site:<official-domain> "<model>" "cybersecurity"
```

Record queries and search dates in a JSON log; put verified official URLs into the config. The crawler can follow bounded links when `max_depth` is raised from zero. Links inside `<nav>` and `<footer>` are ignored, since site-wide navigation says nothing about a product. The remaining links are followed in order of relevance of their URL and anchor text, not page order. Every seed is attempted. A matched link left unvisited because the budget ran out gets a `skipped` record, so coverage can be counted. Identical bytes fetched twice for one product are recorded once and marked `duplicate`. Follow-links inherit the product association as a *search context*, not proof that every linked document applies to that model. Review that association before accepting a claim. Exact domain/subdomain checks apply to every redirect; set narrow allowlists.

## Reproducibility and redistribution

`cache/` stores source bytes by SHA-256. `verify` checks these bytes; `replay` re-extracts them without the network and compares all candidates exactly. Retain the private cache alongside your run if institutional rules allow. Run directories are checkpointed after each source; interruption leaves an incomplete run without a completed manifest. `crawl --resume` with the same config, output directory and cache continues such a run without refetching recorded sources. Recorded failures stay failures; use a new run for a documented retry.

Extraction and lead rules have their own version, recorded in each manifest as `extraction_version`. `replay` refuses a run made under other rules; a release that only changes reviewing or reporting keeps earlier runs replayable. `rebuild` applies the current version to sources that were already fetched:

```bash
python survey.py rebuild --run runs/my_pilot --cache cache --out runs/my_pilot_v1_2
```

It re-derives segments and leads from the retained bytes into a new run directory, without the network. Source hashes and retrieval times are unchanged, so existing reviews stay bound to the same sources, though block numbers in their evidence may need updating. The manifest records what the run was rebuilt from. `pilot/` was produced by 1.0.0, kept as git tag `v1.0.0-pilot`, and `PACKAGE_SHA256.json` describes that delivery.

Vendor manuals, full HTML and extracted full text are **excluded from this distribution**. The pilot contains URLs, hashes, scope, short excerpts and results. Recrawling may obtain a newer document and different hash; do not silently replace a source under an old review. A new source needs a new review. Without the exact retained source bytes, this package reproduces the procedure, not a guarantee of the vendor's historical bytes.

`recheck` shows what changed between an earlier run and a fresh one, including a run whose source bytes were never retained:

```bash
python survey.py crawl --config configs/pilot.json --out runs/pilot_again --cache cache
python survey.py recheck --old pilot --new runs/pilot_again --out runs/pilot_again_recheck.json
```

For each source it reports whether the raw bytes and the extracted text are unchanged and where each excerpt of the old `evidence_index.json` now occurs. An excerpt that is still present is a reason to re-review that cell against the new source, not a substitute for doing so.

One case needs no new review. A dynamic web page returns different bytes on every request, so a refetch of an unchanged page breaks the hash a review row is bound to while its extracted text, and therefore its `text_sha256`, is identical. `rebind` carries a review over in exactly that case and in no other:

```bash
python survey.py rebind --reviews reviews.json --old reports/my_pilot --run runs/pilot_again --out reviews_pilot_again.json
```

`--old` is any directory holding the `sources.json` the review was bound to: the earlier run, or a report made from it. A row is re-bound only where the earlier source has the bound hash and the same extracted-text hash as the new one; the row records both hashes and the basis under `rebound`, and the report says how many rows were carried this way. If the text of any cited source changed, nothing is written and the rows that need a new review are named. The original file is left as it is, and every evidence quote is still checked against the new run when the report is made.

Before depositing data with a paper, review vendor licensing and repository policy. Hashes and short excerpts are provenance, not redistribution permission. The software is small and standalone so it does not change any P4 build, experiment, switch configuration or existing DNP3 repository.

## Limits and next work

This is version 2.0: a package of small modules with a rule-based catalogue inventory, dated lifecycle evidence, definitions of the lifecycle states and of legacy that travel in the config with every revision recorded, seeded stratified sampling, serial bounded crawling, HTML/text-PDF extraction, RFC 9309 robots handling, content-addressed source retention, per-interface review validation with checked evidence quotes for results, conditions, defaults and activation, and report generation with charts of the frame, the documents read and the reviewed results. It has no headless browser, OCR, automatic search-engine integration, production scheduler or automatic semantic verdicts, it reads nothing behind a sign-in, and it has no source of deployment evidence. Those are deliberate scope limits for a supporting paper study.

The immediate next work is author review of the sampled devices, starting from the worksheet, and of the inventory rules in `configs/vendors.json`. A second reviewer should independently check a sample, resolve disagreements and retain the original judgments. Report counts and denominators only after that protocol is frozen. Keep mechanism engineering as the main project priority.
