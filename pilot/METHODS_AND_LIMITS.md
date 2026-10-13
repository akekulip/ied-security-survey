# Pilot methods and limits

Run date: 2026-10-13 UTC. This is a software validation pilot, not a population study.

Five vendor-associated product/family records were chosen through targeted public web searches. Seven official source URLs were attempted using the supplied Python crawler at depth zero, with at most two seed requests per product/family. Request logs also include robots requests and redirects. Five documents were extracted: one text PDF and four HTML pages. One Siemens PDF returned HTTP 404; Rockwell's compatibility PDF was not fetched because its robots URL redirected to a general literature webpage, leaving crawl permission unresolved. Both failures remain in `sources.json`.

The five successful sources cover SEL RTAC, Schneider PowerLogic ADVC, Rockwell ControlLogix 5580, GE Multilin B90 and Siemens SIPROTEC 5. They mix exact model and family scope, and controllers and relays; there is no smart-meter sample. These records must not be treated as an unbiased sample of IED products, equal vendor coverage, or five independently comparable devices.

Automated patterns found passages mentioning security features. Codex inspected the extracted context and produced 35 product–capability review cells: 8 conditional findings and 27 unknowns. Categories overlap and are not device counts. No unsupported finding was inferred from silence. These are AI-reviewed preliminary classifications; Philip or another researcher must verify them before publication. The Rockwell compatibility uncertainty is deliberately unresolved rather than filled using an unrelated firmware statement.

Document identification:

| Source | Identifiable revision/date | Caution |
|---|---|---|
| SEL security white paper | LWP0018-01; date code 20160111 | Historical RTAC guide; not universal current relay support. |
| Schneider ADVC manual section | PKR39809-02; publication date not established from this section | Feature enablement and WSOS configuration required. |
| Rockwell controller online manual | 1756-UM543 URL; current revision/date not established | Explicit product/firmware compatibility still needs its referenced guide. |
| GE B90 product page | No document revision/date established | CyberSentry sections mention firmware; confirm installed options. |
| Siemens advisory | SSA-750499 V1.2; published 2024-07-09; updated 2025-11-11 | Evidence of encrypted management services in affected configurations, not adequate security or encrypted DNP3. |

The final run's manifest pins the crawler script, input config and Python version. The PDF dependency is pinned in `requirements.txt`. Exact fetched source bytes were SHA-256 verified locally, and offline re-extraction produced identical candidates. Those full documents and extracted texts are not redistributed. `evidence_index.json` contains one short excerpt per successful source, bound to URL, location and hash; full support interpretation also requires surrounding context.

Publication claim this tool can support after adequate sampling and review: which security capabilities the examined vendor documentation states for the sampled products and firmware/interfaces. It cannot establish how often these features are enabled in operational power grids, the fraction of deployed plaintext traffic, or installed-base prevalence. Use separate empirical deployment evidence for those claims. Do not suppress positive security-capability findings to strengthen the paper's motivation.

For a full survey, freeze catalog-based inclusion rules and an inventory before querying security terms; include smart meters; record failures and unknowns; independently double-review a sample; then report denominators and limitations. Keep this supporting study bounded so it does not displace mechanism completion.
