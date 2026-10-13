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
| `robots_follow_redirects` | `false` | Follow up to five robots.txt redirects, each inside the product allowlist, as RFC 9309 describes. |

Per product: `id`, `domains` and `seeds` are required; `vendor`, `model` and `category` are needed by the report; `aliases` is an optional list of model strings; `lifecycle` is `active`, `legacy` or `discontinued` (see Legacy devices). Other product keys are kept untouched, so inventory fields such as lifecycle status or catalog source can live in the same file. The config is checked before the first request. Structural errors stop the run; everything else is printed and stored in the manifest as `config_warnings`.

Enabling `robots_follow_redirects` is a methods decision, not a technical one. Example: `literature.rockwellautomation.com/robots.txt` redirects to the vendor's home page, so that host has no robots rules of its own and every Rockwell manual PDF on it is unreachable under the default. With the option on, the document is fetched and its record says `robots_basis: redirected:<final URL>`, so the paper can disclose it.

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

## Sampling before scaling

The supplied five-product/family inventory is purposive and security-keyword informed. It exercises all five vendors and multiple document types. It includes controllers as well as protection devices and contains no smart-meter sample yet. It cannot estimate vendor-wide or industry-wide percentages.

For the paper, first freeze an inventory from vendor product catalogs using device categories, not security search hits. Record the inventory date, inclusion/exclusion rule, model identifiers, active/discontinued status and firmware scope. Include smart meters and relays explicitly; keep PLCs, RTACs and gateways separate. Then search every included device with the same query templates. Count missing documents and unknown outcomes. Do not discard devices that support security because they weaken a desired argument.

A vendor's own sitemap is a catalog that needs no search engine. The `sitemap` command lists one, filters it and writes a dated, hashed JSON file. It never edits a config; a person decides what enters the inventory.

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

This is version 1.4: serial bounded crawling, HTML/text-PDF extraction, RFC 9309 robots handling, content-addressed source retention, per-interface review validation with checked evidence quotes, and report generation. It has no headless browser, OCR, automatic search-engine integration, production scheduler, automatic model inventory or automatic semantic verdicts. Those are deliberate scope limits for a supporting paper study.

The immediate next work is author verification of the pilot and a category-based inventory. A second reviewer should independently check a sample, resolve disagreements and retain the original judgments. Report counts and denominators only after that protocol is frozen. Keep mechanism engineering as the main project priority.
