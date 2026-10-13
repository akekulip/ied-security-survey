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

Per product: `id`, `domains` and `seeds` are required; `vendor`, `model` and `category` are needed by the report; `aliases` is an optional list of model strings. Other product keys are kept untouched, so inventory fields such as lifecycle status or catalog source can live in the same file. The config is checked before the first request. Structural errors stop the run; everything else is printed and stored in the manifest as `config_warnings`.

Enabling `robots_follow_redirects` is a methods decision, not a technical one. Example: `literature.rockwellautomation.com/robots.txt` redirects to the vendor's home page, so that host has no robots rules of its own and every Rockwell manual PDF on it is unreachable under the default. With the option on, the document is fetched and its record says `robots_basis: redirected:<final URL>`, so the paper can disclose it.

## Review, then report

Open `runs/my_pilot/candidates.json` and the `*.segments.json` files. Candidates are search leads only: **no regex can establish product capability**. Inspect the complete passage and applicable product/firmware, then edit a copy of `review_template.json`:

```bash
cp runs/my_pilot/review_template.json reviews.json
# Edit reviews.json; fill reviewer, date, rationale, supporting source hashes and evidence quotes.
python survey.py report --run runs/my_pilot --reviews reviews.json --out reports/my_pilot --require-evidence
python survey.py verify --run runs/my_pilot --cache cache
python survey.py replay --run runs/my_pilot --cache cache --out runs/my_pilot_replay
```

The review can be done in stages. Rows left exactly as the template wrote them are ignored and shown as not reviewed, so `report` runs at any point and its coverage line shows how far the review has got. A row that is partly filled in is an error that names the cell; it is never dropped silently.

Each candidate carries `match_count` for its page or block, the nearest preceding `heading` (HTML heading or PDF bookmark), and, when the product has `aliases`, whether the model string appears in the same passage. These help find and scope a passage. They are not verdicts and every candidate stays `unreviewed`.

A review cell may carry `evidence`, a list of `{"source_id", "location", "quote"}` with the exact segment location (`pdf-page:10`, `html-block:42`) and a verbatim quote of at least 20 characters. `report` checks that each quote occurs in that segment, ignoring whitespace and typographic differences. `--require-evidence` makes a quote mandatory for every result other than `unknown`. The check proves the words are in the cited passage. It does not prove they support the claim.

Report produces CSV, JSON and Markdown, plus `evidence_index.json` and `candidate_counts.json`. The Markdown has a product by capability matrix, each finding with its scope and quoted evidence, counts per product category with the number of products as an explicit denominator, the unresolved cells, the documents examined, and the sources that yielded no text. Validation rejects records without reviewer, date and rationale, unbound hashes, evidence from another product, failed-source support claims, misquoted evidence and duplicate product–capability cells. A single cell may describe multiple interface constraints in its rationale; do not silently generalize them. The reviewer must establish semantic correctness; hash and quote checking cannot do that.

The delivered `pilot/` contains the reviewed pilot, request/source manifests, short evidence excerpts and tests log. Review identity is explicitly `Codex AI review; author confirmation pending`. It is a working research artifact, **not a publication-ready population survey**. All outcomes, including the failed Siemens PDF request, are retained. `pilot/REPORT.md` is the entry point.

## Classification rules

| Status | Required interpretation |
|---|---|
| supported | Explicit documentation for this product/family and stated interface; configuration may still be required. |
| conditional | Explicit support with a material firmware, feature-selection, module or licensing condition. State it. |
| explicitly_unsupported | Explicit vendor statement of non-support for the scoped feature. Silence is insufficient. |
| unknown | Available examined evidence does not establish support or non-support. Also use for unavailable evidence. |
| conflicting | Applicable sources disagree; retain both and resolve firmware/date/scope before analysis. |

Always separate:

- DNP3 Secure Authentication from encryption. An authentication result alone does not establish payload confidentiality.
- TLS for engineering/web/management interfaces from TLS for DNP3 or another control protocol.
- Built-in capability from an optional communication module or an external gateway.
- Product family, exact catalog model and firmware version. A family example must not be counted as several confirmed models.
- Capability from configuration, default enablement and real deployment. The survey cannot measure plaintext prevalence.
- Current documentation from historical documents. Keep revision, publication date and retrieval date separately; HTTP Last-Modified is not automatically the document's publication date.

`ipsec`, `tls`, `cip_security`, `dnp3_secure_authentication`, `authentication`, `encryption`, and `ssh` are overlapping search categories, not disjoint counts. In particular, do not add their totals as device counts. Decryption is generally the counterpart of documented encrypted communication; do not infer an independently supported interface from that word alone.

Those seven are the review cells and the only source of denominators. The keyword search also has lead-only groups that never become cells: `plaintext_statement` (unencrypted, plain or clear text, "not encrypted", "does not support encryption"), `macsec` and `iec_62351`. `plaintext_statement` exists so that explicit statements of non-support are searched for as deliberately as statements of support. Whether MACsec or IEC 62351 should become review cells is a protocol decision to take before the inventory is frozen, because it changes every denominator.

`cip_security` means ODVA CIP Security. NERC CIP is excluded from that group. A bare "secure authentication" counts as a DNP3 Secure Authentication lead only when DNP3, IEEE 1815 or IEC 62351-5 is mentioned on the same PDF page, in the block's heading, or within three HTML blocks.

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

Extraction rules and block numbering belong to a tool version, so `replay` refuses a run made by another version. `pilot/` was produced by 1.0.0, kept as git tag `v1.0.0-pilot`, and `PACKAGE_SHA256.json` describes that delivery.

Vendor manuals, full HTML and extracted full text are **excluded from this distribution**. The pilot contains URLs, hashes, scope, short excerpts and results. Recrawling may obtain a newer document and different hash; do not silently replace a source under an old review. A new source needs a new review. Without the exact retained source bytes, this package reproduces the procedure, not a guarantee of the vendor's historical bytes.

`recheck` shows what changed between an earlier run and a fresh one, including a run whose source bytes were never retained:

```bash
python survey.py crawl --config configs/pilot.json --out runs/pilot_again --cache cache
python survey.py recheck --old pilot --new runs/pilot_again --out runs/pilot_again_recheck.json
```

For each source it reports whether the raw bytes and the extracted text are unchanged and where each excerpt of the old `evidence_index.json` now occurs. An excerpt that is still present is a reason to re-review that cell against the new source, not a substitute for doing so.

Before depositing data with a paper, review vendor licensing and repository policy. Hashes and short excerpts are provenance, not redistribution permission. The software is small and standalone so it does not change any P4 build, experiment, switch configuration or existing DNP3 repository.

## Limits and next work

This is version 1.1: serial bounded crawling, HTML/text-PDF extraction, RFC 9309 robots handling, content-addressed source retention, review validation with checked evidence quotes, and report generation. It has no headless browser, OCR, automatic search-engine integration, production scheduler, automatic model inventory or automatic semantic verdicts. Those are deliberate scope limits for a supporting paper study.

The immediate next work is author verification of the pilot and a category-based inventory. A second reviewer should independently check a sample, resolve disagreements and retain the original judgments. Report counts and denominators only after that protocol is frozen. Keep mechanism engineering as the main project priority.
