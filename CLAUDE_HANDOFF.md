# Continue the IED survey without diverting the mechanism project

The goal is a small reproducible study of **documented security capability** across SEL, Schneider Electric, Rockwell/Allen-Bradley, GE Vernova/Multilin and Siemens. This is supporting paper evidence, not a new main research project.

1. Run the bundled tests, read `pilot/REPORT.md` and inspect `pilot/evidence_index.json`. Check each positive/conditional finding in the cited official source. Do not treat AI review as independent human verification.
2. Agree on a narrow product sampling frame with Philip: start with protective relays and smart meters; separate controller/gateway/PLC strata. Build the inventory from catalogs before security searches. Log exclusions and unknowns.
3. Add official seeds and run the existing crawler; avoid rewriting it or adding browser automation unless a concrete source requires it. Preserve failed fetches, robots decisions, hashes and search queries. Do not scan live devices.
4. Validate firmware, interface and native/module/gateway scope. Never turn HTTPS management, RADIUS login or firmware signing into a claim of encrypted DNP3. Never turn absence of a mention into non-support.
5. Export the reviewed table with explicit denominators and unresolved records. No claims about deployed encryption/plaintext prevalence follow from this study alone. Find separate observational evidence for that part of the introduction.
6. Write a short methods paragraph and appendix description concurrently with the work. Do not claim a completed survey or invent percentages before coverage and review are complete. Retain negative and inconvenient results.

Stop expansion once this bounded supporting question is answered. Do not modify the existing obfuscation mechanism, hardware, source plans or paper files automatically. This package has no production credentials or deployment actions.
