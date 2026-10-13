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

The crawler refuses to overwrite an existing run. Each run records its configuration, source outcomes, redirects, request log, response-byte SHA-256 hashes, extraction locations, keyword leads and a review template. PDFs use one-based physical PDF page numbers, not the page number printed on the page. HTML locations are extraction block numbers bound to the source hash and tool version.

Download failures, robots exclusions, unsupported formats and empty extraction are logged as failures, never as lack of product support. PDF extraction needs selectable text; this version does not OCR scans or execute JavaScript. It does not bypass login, anti-bot challenges or robots restrictions. There are no automatic retries; use a new run for a documented retry. Robots redirects are deliberately treated as unresolved rather than followed. This can reduce coverage and is recorded as such.

## Review, then report

Open `runs/my_pilot/candidates.json` and the `*.segments.json` files. Candidates are search leads only: **no regex can establish product capability**. Inspect the complete passage and applicable product/firmware, then edit a copy of `review_template.json`:

```bash
cp runs/my_pilot/review_template.json reviews.json
# Edit reviews.json; fill reviewer, date, rationale and supporting source hashes.
python survey.py report --run runs/my_pilot --reviews reviews.json --out reports/my_pilot
python survey.py verify --run runs/my_pilot --cache cache
python survey.py replay --run runs/my_pilot --cache cache --out runs/my_pilot_replay
```

Report produces CSV, JSON and Markdown. Validation rejects unreviewed records, unbound hashes, evidence from another product, failed-source support claims and duplicate product–capability cells. A single cell may describe multiple interface constraints in its rationale; do not silently generalize them. The reviewer must establish semantic correctness; hash checking cannot do that.

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

## Sampling before scaling

The supplied five-product/family inventory is purposive and security-keyword informed. It exercises all five vendors and multiple document types. It includes controllers as well as protection devices and contains no smart-meter sample yet. It cannot estimate vendor-wide or industry-wide percentages.

For the paper, first freeze an inventory from vendor product catalogs using device categories, not security search hits. Record the inventory date, inclusion/exclusion rule, model identifiers, active/discontinued status and firmware scope. Include smart meters and relays explicitly; keep PLCs, RTACs and gateways separate. Then search every included device with the same query templates. Count missing documents and unknown outcomes. Do not discard devices that support security because they weaken a desired argument.

Query templates for manual discovery (search-engine API not included):

```
site:<official-domain> "<model>" manual
site:<official-domain> "<model>" "DNP3" "secure authentication"
site:<official-domain> "<model>" "TLS"
site:<official-domain> "<model>" "IPsec"
site:<official-domain> "<model>" "cybersecurity"
```

Record queries and search dates in a JSON log; put verified official URLs into the config. The crawler can follow bounded links when `max_depth` is raised from zero and `follow_pattern` is supplied. Follow-links inherit the product association as a *search context*, not proof that every linked document applies to that model. Review that association before accepting a claim. Exact domain/subdomain checks apply to every redirect; set narrow allowlists.

## Reproducibility and redistribution

`cache/` stores source bytes by SHA-256. `verify` checks these bytes; `replay` re-extracts them without the network and compares all candidates exactly. Retain the private cache alongside your run if institutional rules allow. Run directories are checkpointed after each source; interruption leaves an incomplete run without a completed manifest. This version does not resume an interrupted run in place; start a fresh bounded run and preserve the incomplete one.

Vendor manuals, full HTML and extracted full text are **excluded from this distribution**. The pilot contains URLs, hashes, scope, short excerpts and results. Recrawling may obtain a newer document and different hash; do not silently replace a source under an old review. A new source needs a new review. Without the exact retained source bytes, this package reproduces the procedure, not a guarantee of the vendor's historical bytes.

Before depositing data with a paper, review vendor licensing and repository policy. Hashes and short excerpts are provenance, not redistribution permission. The software is small and standalone so it does not change any P4 build, experiment, switch configuration or existing DNP3 repository.

## Limits and next work

This is version 1: serial bounded crawling, HTML/text-PDF extraction, conservative robots handling, content-addressed source retention, review validation and report generation. It has no headless browser, OCR, automatic search-engine integration, production scheduler, automatic model inventory or automatic semantic verdicts. Those are deliberate scope limits for a supporting paper study.

The immediate next work is author verification of the pilot and a category-based inventory. A second reviewer should independently check a sample, resolve disagreements and retain the original judgments. Report counts and denominators only after that protocol is frozen. Keep mechanism engineering as the main project priority.
