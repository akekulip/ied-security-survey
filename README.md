# IED security documentation survey

A runnable, bounded crawler and evidence-review workflow for Dr. Lin's proposed five-manufacturer survey. It reads public vendor documents; it does not discover, contact or test operational IEDs.

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

## Config options

| Key | Default | Meaning |
|---|---|---|
| `sampling` | required | Statement of how the products were chosen. Copied into the manifest and the report. |
| `title` | `IED security documentation survey` | Report heading. |
| `max_depth` | `0` | Link-following depth. Zero fetches the seeds only. |
| `max_pages_per_product` | `3` | Page budget per product. Seeds are always attempted; the budget limits followed links. |
| `follow_pattern` | `manual\|security\|datasheet\|\.pdf` | A link is followed when this matches its URL or its anchor text. |
| `delay_seconds` | `1` | Minimum gap between requests to one host. A longer robots crawl delay wins. |
| `timeout_seconds` | `25` | Per-request timeout. |
| `max_bytes` | `25000000` | Larger responses are failures. Full instruction manuals can exceed this. |
| `retries` | `0` | Extra attempts after a timeout, connection error or HTTP 429/502/503/504. Honours `Retry-After`. Every attempt is logged. |
| `robots_follow_redirects` | `false` | Follow up to five robots.txt redirects, each inside the product allowlist, as RFC 9309 describes. `true` for every host, or a list of domains such as `["rockwellautomation.com"]` to allow it for those hosts only. |

Per product: `id`, `domains` and `seeds` are required; `vendor`, `model` and `category` are needed by the report; `aliases` is an optional list of model strings; `lifecycle` is `active`, `legacy` or `discontinued` (see Legacy devices). A product may set its own `max_depth`, `max_pages_per_product` and `follow_pattern`, since vendors lay out their sites differently. Other product keys are kept untouched, so inventory fields such as lifecycle status or catalog source can live in the same file. The config is checked before the first request. Structural errors stop the run; everything else is printed and stored in the manifest as `config_warnings`.

Enabling `robots_follow_redirects` is a methods decision, not a technical one. Example: `literature.rockwellautomation.com/robots.txt` redirects to the vendor's home page, so that host has no robots rules of its own and every Rockwell manual PDF on it is unreachable under the default. With the option on, the document is fetched and its record says `robots_basis: redirected:<final URL>`, so the paper can disclose it. A host that answers its robots.txt request with an error such as 403 stays off limits whatever this option says.

`crawl` takes two further options. `--only <pattern>` limits a run to the products whose `id` and vendor match, and the manifest records it. `--reuse <run>` takes any URL that an earlier run already fetched from the cache instead of requesting it again; the source record then says `reused_from`.

A document that sits behind a sign-in is not fetched. A link that points at a login address, or a request that is redirected to one, gets a source record with status `login_required`. A vendor page often lists many manuals whose download buttons all lead to the same sign-in address; the record's `link_count` says how many links did. The report counts these links apart from failures: they are documents that exist and were not used.

## Review, then report

Open `runs/my_pilot/candidates.json` and the `*.segments.json` files. Candidates are search leads only: **no regex can establish product capability**. Inspect the complete passage and applicable product/firmware, then edit a copy of `review_template.json`:

```bash
cp runs/my_pilot/review_template.json reviews.json
cp runs/my_pilot/source_notes_template.json source_notes.json
# Edit reviews.json: result, interface, conditions, evidence quotes, reviewer, date, rationale.
# Edit source_notes.json: each document's own number, revision and date.
python survey.py report --run runs/my_pilot --reviews reviews.json --out reports/my_pilot \
    --require-evidence --source-notes source_notes.json
python survey.py verify --run runs/my_pilot --cache cache
python survey.py replay --run runs/my_pilot --cache cache --out runs/my_pilot_replay
```

The review can be done in stages. Rows left exactly as the template wrote them are ignored and shown as not reviewed, so `report` runs at any point and its coverage line shows how far the review has got. A row that is partly filled in is an error that names the cell; it is never dropped silently.

### Leads

Each candidate carries:

- `matched`, the words that matched, and `match_count` for its page or block. `["SFTP"]` is not an SSH statement and `["VPN"]` is not IPsec, and the lead says which it was.
- `context`, widened to whole sentences, and for HTML `context_before` and `context_after`, the two neighbouring blocks on each side. A heading or table label is never shown alone.
- the nearest preceding `heading` (HTML heading or PDF bookmark) and, when the product has `aliases`, whether the model string appears in the same passage.
- `lead_type`: `capability` for the seven review cells, `related` for neighbouring terms, `statement` for explicit denials and plaintext wording, `profile` for items of a DNP3 Device Profile.

These help find and scope a passage. They are not verdicts and every candidate stays `unreviewed`. A lead is a place where a term occurs. Several leads in one document are still one document about one product, so lead counts are never device counts.

`statement_leads.json` holds two groups, apart from `candidates.json`:

- `non_support_statement`: a capability named in a sentence that denies it, such as "TLS is not used", "does not support Secure Authentication" or "no support for IPsec". Conditional wording ("if the device does not support …") is skipped. These are searched for as deliberately as claims of support, because an explicit denial is the only route to `explicitly_unsupported`.
- `plaintext_statement`: unencrypted, not encrypted, no encryption, plain or clear text.

A statement about the product itself can support `explicitly_unsupported` after review. A general statement ("information is often transmitted in plain text") supports nothing about a product. It is a literature lead for the paper's motivation, to be cited as what that vendor wrote, and never a measured share of deployments.

### DNP3 Device Profiles

A DNP3 Device Profile is the vendor's own answer sheet for a product's DNP3 implementation. Its section 1.12, Security Parameters, states which Secure Authentication version is supported and whether TLS is used, item by item, including answers such as "Not relevant – TLS is not used". When a source is a device profile, the tool splits that section into its numbered items and writes them to `<source_id>.profile.json`: number, title, page, the item's whole text, and the option lines that appear marked. Each item is also a `profile` lead.

Marks are read by a heuristic (a leading `X` or a checked-box character), because vendors mark options differently and some marks do not survive text extraction. An item with no detected mark still shows its full text. Nothing here is a finding until a review row quotes the item.

### Review rows

A capability is recorded once per interface, because TLS for a web page and TLS for DNP3 are different findings. Every row with a result other than `unknown` states:

- `interface`: a short label, written the same way on every row that belongs to that interface, for example `DNP3 server to SCADA master`. Rows of one product with the same label are consolidated into one line of the findings table.
- `interface_class`: `control_protocol` (DNP3, IEC 61850, CIP and similar traffic), `management` (engineering tools, web, user login, logging, file transfer) or `network` (protection applied below the protocol, such as IPsec or MACsec).
- `protocol`, `firmware`, `implementation`, and `conditions`. `conditions` is required when the result is `conditional`.
- `review_status`: `draft` until a person has checked the row against the source, then `confirmed`. An empty value counts as `draft`.

To say that nothing is established for control traffic while something is established for management, keep an `unknown` row with an empty `interface` next to the management row.

A row may carry `evidence`, a list of `{"source_id", "location", "quote"}` with the exact segment location (`pdf-page:10`, `html-block:42`) and a verbatim quote of at least 20 characters. A location may also be a short run of consecutive segments, `html-block:10-13`. `report` checks that each quote occurs there, ignoring whitespace, typographic differences and hyphens between letters, since a PDF line break hides whether a hyphen belongs to the word. `--require-evidence` makes a quote mandatory for every result other than `unknown`. The check proves the words are in the cited passage. It does not prove they support the claim.

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

`coverage` says whether the source is the whole document (`complete`) or an excerpt such as one chapter or one web page of a manual (`partial`). Only a complete device profile, conformance statement or manual can support `not_documented`.

The order is guidance for weighing evidence, not a score. A manual for the exact firmware can outweigh a device profile for another one. The report shows the type beside every evidence reference, for example `S1 [manual]`, and `[type not confirmed]` until someone has set it.

### The report

`REPORT.md` opens with the findings table, one row per product and interface: manufacturer, model, lifecycle, firmware, protocol/interface, encryption, authentication, conditions, evidence, review status. `findings_table.csv` holds the same rows with every quote and the source URL and hash.

- The encryption and authentication columns show what the `encryption` and `authentication` rows for that interface say. Nothing is inferred from a mechanism: where only a `tls` or `ssh` row exists, the cell points to it and says the property was not assessed.
- Every product has a control-protocol row, even when nothing is established, so that silence about DNP3 is stated as unknown.
- The capability matrix puts a mark in parentheses when a result exists only for a management or network interface.
- "Counts by category" counts products, never leads or table rows, with the number of products as the denominator.

The report also writes `findings.csv`, `findings.json`, `evidence_index.json`, `candidate_counts.json` (leads by type, never device counts) and `sources.json`, the source manifest with the notes merged in. The Markdown further lists each finding with its quotes, the unresolved cells, the items read from any device profile (labelled as not reviewed), the documents examined with their types, and the sources that yielded no text. Validation rejects records without reviewer, date and rationale, unbound hashes, evidence from another product, failed-source support claims, misquoted evidence, results without an interface class, conditional results without conditions, and duplicate rows for one product, capability and interface. The reviewer must establish semantic correctness; hash and quote checking cannot do that.

The delivered `pilot/` contains the reviewed pilot, request/source manifests, short evidence excerpts and tests log. Review identity is explicitly `Codex AI review; author confirmation pending`. It is a working research artifact, **not a publication-ready population survey**. All outcomes, including the failed Siemens PDF request, are retained. `pilot/REPORT.md` is the entry point.

## Classification rules

| Status | Required interpretation |
|---|---|
| supported | Explicit documentation for this product/family and stated interface; configuration may still be required. |
| conditional | Explicit support with a material firmware, feature-selection, module or licensing condition. State it. |
| explicitly_unsupported | Explicit vendor statement of non-support for the scoped feature. Silence is insufficient. |
| not_documented | A complete manual, device profile or conformance statement was searched in full and does not mention the feature. A statement about the documentation, not about the device. |
| unknown | Available examined evidence does not establish support or non-support. Also use for unavailable evidence, and whenever only part of the documentation was read. |
| conflicting | Applicable sources disagree; retain both and resolve firmware/date/scope before analysis. |

Always separate:

- DNP3 Secure Authentication from encryption. An authentication result alone does not establish payload confidentiality.
- TLS for engineering/web/management interfaces from TLS for DNP3 or another control protocol.
- Built-in capability from an optional communication module or an external gateway.
- Product family, exact catalog model and firmware version. A family example must not be counted as several confirmed models.
- Capability from configuration, default enablement and real deployment. The survey cannot measure plaintext prevalence.
- Current documentation from historical documents. Keep revision, publication date and retrieval date separately; HTTP Last-Modified is not automatically the document's publication date.

`ipsec`, `tls`, `cip_security`, `dnp3_secure_authentication`, `authentication`, `encryption`, and `ssh` are overlapping search categories, not disjoint counts. In particular, do not add their totals as device counts. Decryption is generally the counterpart of documented encrypted communication; do not infer an independently supported interface from that word alone.

Those seven are the review cells and the only source of denominators. A capability group holds only terms that name that capability. Neighbouring terms have their own lead-only groups that never become cells: `vpn`, `sftp`, `macsec` and `iec_62351`. A recommendation to use a VPN does not establish native IPsec support, and an SFTP mention is not an explicit SSH statement. `non_support_statement` and `plaintext_statement` are a third kind, kept in their own file as described under Leads. Whether MACsec or IEC 62351 should become review cells is a protocol decision to take before the inventory is frozen, because it changes every denominator.

`cip_security` means ODVA CIP Security. NERC CIP is excluded from that group. A bare "secure authentication" counts as a DNP3 Secure Authentication lead only when DNP3, IEEE 1815 or IEC 62351-5 is mentioned on the same PDF page, in the block's heading, or within three HTML blocks.

## Legacy devices

It is widely said that legacy devices have no security. The survey does not assume it; it records it, device by device, in a form a reader can check.

1. Put legacy and discontinued products in the inventory on purpose, and give every product a `lifecycle`: `active`, `legacy` or `discontinued`. Note in the product entry where that status comes from, for example the vendor's legacy-product list. Counts and the matrix are then split by category and lifecycle, so legacy and current devices are never pooled.
2. Seed the product's complete manual, and its DNP3 Device Profile if one exists. A product page or a single chapter cannot carry a finding of absence.
3. In the source notes, set `doc_type` and `coverage: complete` only when the source is the whole document.
4. Where the manual is silent, record `not_documented` for the capability on that interface, with the firmware scope the manual states. No quote is possible for silence. Instead `report` checks the row mechanically: every cited source must be a complete manual, device profile or conformance statement, and the keyword search must have found no lead for that capability in it. If leads exist, the report refuses the row until they are reviewed.
5. Where the vendor says so in words, for example a device profile marked "TLS is not used", record `explicitly_unsupported` with the quote. That is stronger evidence and the two are counted apart.

What this supports in the paper: "for N of M legacy devices, the complete product manual documents no authentication or encryption for DNP3". It does not support "these devices cannot be secured", since an external gateway or a later firmware may add protection, and it says nothing about how many such devices are deployed.

## From five products to the vendor catalogues

The pilot's five products were hand-picked with security keywords in mind, one per vendor. That exercises the tool. It cannot say anything about a vendor's range. The wide survey takes its devices from each vendor's own catalogue instead, by device category and not by security search hits, in the steps below. Every step writes files a person can read and correct before the next one runs.

```bash
DATA=~/ied_survey_data     # cache and runs; keep them out of a synced folder such as OneDrive
python survey.py inventory --vendors configs/vendors.json --out inventory/2026-10-13 --cache $DATA/cache
python survey.py sample    --inventory inventory/2026-10-13/inventory.json --census --out configs/census.json
python survey.py crawl     --config configs/census.json --out $DATA/runs/census --cache $DATA/cache
python survey.py enrich    --inventory inventory/2026-10-13/inventory.json --run $DATA/runs/census --vendors configs/vendors.json --out inventory/2026-10-13-pages
python survey.py sample    --inventory inventory/2026-10-13-pages/inventory.json --per-stratum 4 --seed 20261013 --out configs/sample.json
python survey.py crawl     --config configs/sample.json --out $DATA/runs/sample --cache $DATA/cache --reuse $DATA/runs/census
python survey.py worksheet --run $DATA/runs/sample --out reports/sample_worksheet
```

### 1. Inventory

`configs/vendors.json` says, per vendor, where the catalogue is and how to read it:

| Key | Meaning |
|---|---|
| `sitemaps`, `sitemap_filter` | The vendor's sitemap files. The filter picks which parts of a sitemap index are worth a request. |
| `scope` | Pattern for the sitemap URLs that are product pages of the kinds surveyed. |
| `rules` | Ordered rules giving a category: `protective_relay`, `controller_rtu`, `plc` or `meter`. |
| `exclude` | Ordered rules with a `reason`: accessories, software, test equipment, I/O modules, family index pages. An exclusion beats a category. |
| `lifecycle` | Rules on the listing, for example a GE URL ending in `-legacy`. Without a match the entry is `active`. |
| `lifecycle_text` | Wording on the product page that marks a device as legacy or discontinued. Applied by `enrich`. A rule may set `within`, the number of opening characters of the page it reads. |
| `crawl` | `max_depth`, `max_pages_per_product` and `follow_pattern` for that vendor's pages in the sampled crawl. |
| `adapter` | Used where the catalogue is not a sitemap. SEL product pages are empty without JavaScript, so its list is read from the JSON the site's own product selector loads. |

Each rule reads one field, named by `on`: `url`, `slug` (the last path segment) or `text` (the model name and, where the listing has one, the vendor's one-line product type). The first matching rule wins.

`inventory` fetches the listings through the same robots-checked, cached and logged fetcher as a crawl and writes `inventory.json`, `inventory.csv`, `catalogue.json` (the raw listing) and `requests.json`. Every catalogue entry in scope ends up in exactly one state, with the rule that put it there:

- included, with a category and a lifecycle;
- excluded, with the reason;
- unclassified, when no rule matched. These are listed, never dropped. Their product pages are read in the census so that the page's own opening words can classify them.

Read `inventory.csv` before going on. The rules are judgment calls about what counts as a device, and the file is where a reader checks them. After changing a rule, `inventory --from <previous inventory directory>` applies the new rules to the saved listing without asking the vendors again.

### 2. Census, then what the product pages say

`sample --census` writes a crawl config with one product page per catalogue entry and no link-following. `enrich` then reads those pages back into a new inventory directory: the page title becomes the model name, unclassified entries are classified from their page text or stay unclassified, and a `lifecycle_text` match sets the lifecycle with the matched sentence kept as `lifecycle_evidence`. Where a product page cannot be read without JavaScript, the census requests the product's listed public documents in its place.

The wording a vendor uses is only known once its pages have been read, so `lifecycle_text` rules are written at this point. `enrich --vendors` applies the current rules file and stores it, with its hash, in the new inventory; without the option the rules saved in the inventory are used. Check every `lifecycle_evidence` sentence in `inventory.csv` after a change. Two things went wrong on the first pass over real pages and shaped the delivered rules: a family page that says one variant "has been discontinued" is not a discontinued family, which is what `within` is for, and words such as "migrate" appear on current products too.

Lifecycle is what the vendor's catalogue and page say on the inventory date. `discontinued` means the page says the product is no longer made or sold. `legacy` means the vendor lists it as legacy, or says only part of the family is withdrawn, without such a notice. A device still listed without either is `active` here even if the design is twenty years old, so "legacy" in this survey means "marked as such by the vendor" and nothing wider. A vendor whose catalogue shows no lifecycle wording at all has every device recorded as `active`.

### 3. Sample

`sample --per-stratum N --seed S` draws up to N devices from every stratum of vendor, category and lifecycle. Strata with fewer entries are taken whole. The same inventory and seed give a byte-identical config, each stratum has its own generator so that adding a vendor does not move another vendor's draw, and the config records the seed, the inventory's SHA-256 and the `frame`: per stratum, how many entries the catalogue has and how many were selected. The report prints that frame, so every count has its denominator beside it.

This is a sample of catalogue entries. It supports statements such as "of the 4 sampled GE legacy relays, public documents establish DNP3 Secure Authentication for none". It does not support statements about installed devices, and with a handful of devices per stratum it does not support percentages.

### 4. Sampled crawl and worksheet

The sampled config applies each vendor's `crawl` settings, so documents linked from the product page are followed. Links are tried in order of how directly the document type speaks about one product: DNP3 device profile first, then conformance statements, security guides and manuals, then data sheets and brochures. A communications or protocol manual is tried before other manuals. `--reuse` keeps the census pages from being requested twice.

Each vendor's `crawl` settings were written after looking at what its product pages link to, and they are the place to look when a run fetches the wrong things. Two examples from the first run: a GE product page links to resource lists and only those lists link to files, so GE needs depth 2 and a budget that leaves room for files after the lists; and a pattern as loose as `catalog` also matches a web shop's catalogue tree.

`worksheet` lays the result out for the reviewer: per product its sources with their suggested types, and per capability where the leads are, with the matched words, or which sources have none. It also writes a copy of the review template with those hints in a `_hints` field beside each cell. The worksheet proposes no result. A lead is a place to read, and "no lead" in a product page is not a statement about the device.

### What a wide run can and cannot show

Only public documents are read. Full instruction manuals of several vendors sit behind a sign-in, or on hosts whose robots.txt cannot be read, and those documents are counted and left alone. For many devices the public material is therefore a product page and a brochure, and most of their cells stay `unknown`. The share of devices for which the public documentation settles nothing is itself a result, reported per vendor, category and lifecycle. It must not be read as those devices lacking security, and `not_documented` still needs a complete manual (see Legacy devices).

A report on a wide run stays readable before and during the review:

- With more than 25 unreviewed products, the findings table, the capability matrix and the list of unresolved cells show only products that have a review row, and each says how many it left out. The summary by vendor, category and lifecycle and the counts by category cover every product.
- With more than 60 extracted sources, "What was read" counts them by vendor and document type, and "Sources examined" lists only the sources a review row cites. `sources.json` in the report directory lists all of them.
- With more than 40 sources that yielded no text, they are counted by vendor and outcome instead of listed.

### One vendor's sitemap by hand

The `sitemap` command lists a single sitemap, filters it and writes a dated, hashed JSON file. It is the manual counterpart of `inventory` for a vendor that has no entry in `configs/vendors.json` yet.

```bash
python survey.py sitemap --url https://www.gevernova.com/electrification/sitemap.xml \
    --match protection-control-metering --out inventory/ge_catalog.json
python survey.py sitemap --host selinc.com --match "selinc.com/products/" --out inventory/sel_catalog.json
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

Before depositing data with a paper, review vendor licensing and repository policy. Hashes and short excerpts are provenance, not redistribution permission. The software is small and standalone so it does not change any P4 build, experiment, switch configuration or existing DNP3 repository.

## Limits and next work

This is version 1.5: a rule-based catalogue inventory, seeded stratified sampling, serial bounded crawling, HTML/text-PDF extraction, RFC 9309 robots handling, content-addressed source retention, per-interface review validation with checked evidence quotes, and report generation. It has no headless browser, OCR, automatic search-engine integration, production scheduler or automatic semantic verdicts, and it reads nothing behind a sign-in. Those are deliberate scope limits for a supporting paper study.

The immediate next work is author review of the sampled devices, starting from the worksheet, and of the inventory rules in `configs/vendors.json`. A second reviewer should independently check a sample, resolve disagreements and retain the original judgments. Report counts and denominators only after that protocol is frozen. Keep mechanism engineering as the main project priority.
