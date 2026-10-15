> **Superseded on 2026-10-15; kept as generated.** Built with tool version 2.2.0 from `review/reviews_ai_draft.json`. It counts the Multilin D400 as having no DNP3 security, although its brochure documents a TLS tunnel for DNP3/TCP (source `e9650803a7d08f102554`, pdf-page 1: "Secure tunneling from master station to the D400 via TLS for DNP3/TCP, Modbus/TCP and IEC 104"), and it prints "no DNP3 security documented" as "plaintext", which the documents do not establish. The tables in this folder carry the same errors. Current results: `../../paper_2026-10-15/` (see `study/README.md`).

# IED security documentation survey: catalogue inventory

Sampling: Stratified random sample: up to 4 devices per vendor, category and lifecycle stratum, seed 20261013, drawn from 484 classified catalogue entries; strata with fewer entries are taken whole. A sample of catalogue entries, not of installed devices. Inventory of 2026-10-13; categories and lifecycle come from the vendors' own catalogues and pages.

Products/families in seed inventory: 99. Sources attempted: 319; extracted: 308; failed: 3; duplicate of another source: 8; matched links not followed (page budget): 32; documents behind a sign-in, not requested: 102.

This measures documented capabilities, not enabled settings, installed-base coverage or plaintext prevalence. Unknown is not unsupported. Family-level evidence is not proof for every model/firmware. Capability categories overlap, so counts below are review cells and must not be added up as devices.

Reviewers on record: Claude AI draft review; author confirmation pending (820 rows).

Every capability has one of four results: supported, conditional, explicitly unsupported or unknown. An unknown says why where the review recorded it. "Complete document silent" means a complete manual, device profile or conformance statement was searched and does not mention the capability; it is not a vendor statement that the capability is absent.

## Definitions

First fixed on 2026-10-13 and revised since. What follows is the definition in the config this run was crawled with; each revision is listed with what had been counted when it was made.

- Legacy: A device is counted as legacy when the vendor states, in a dated source, that it has been discontinued: manufacture or sale has ended, whether support continues, has ended or is not mentioned. The three lifecycle states that make up the group are also counted one by one, so a device whose support has ended can still be told from one that is only no longer sold. The protocol a device speaks, a security feature it lacks, the age of its manual and the vendor's own use of the word legacy never decide this.
- Counted as legacy: discontinued, still supported; discontinued, support not stated; end of support.
- Currently supported: Listed in the vendor's current catalogue on the inventory date without a notice of discontinuation, or stated by the vendor to be on sale and supported. Not legacy.
- Discontinued, still supported: The vendor states that manufacture or sale has ended and that support continues. Legacy.
- Discontinued, support not stated: The vendor states that manufacture or sale has ended; no statement about support was found. Legacy.
- End of support: The vendor states that support has ended. Legacy.
- Unknown: None of the above is established. This includes products the vendor only labels legacy, products under a last-time-buy notice and families that are partly withdrawn. Not counted as legacy, because nothing dated says the device has been discontinued.
- Release date: Recorded separately when a vendor source states it. It never decides lifecycle status.
- Revised on 2026-10-13: Legacy widened from the end-of-support state alone to every device the vendor has discontinued. What had been counted by then: A first review of the 99 sampled devices, drafted by an AI assistant and not confirmed by the author, had been counted under the earlier definition. It placed no device in the legacy group, because no public vendor page states an end of support, and 31 devices in the group "discontinued, support not stated". The author then decided that discontinued devices count as legacy. The sample, the documents and the review rows are the same before and after; only the grouping changed.

Legacy under this definition: 31 of 99 devices in this run. Lifecycle status rests on dated vendor evidence for 92 devices and is unknown for 7.

## DNP3 security

Devices whose own retrieved documents name DNP3, by the strongest DNP3 protection the review establishes for them. "Plaintext" means that no DNP3 security is documented: DNP3 then travels readable unless something outside the device, such as a VPN or an encrypting radio, protects it. DNP3 Secure Authentication authenticates messages and does not encrypt them. These are documented capabilities of sampled catalogue entries, not the settings of installed devices or shares of real traffic. A device counts as plaintext when the documents retrieved for it name no DNP3 security; a document the crawl did not retrieve may, so the plaintext count is an upper bound and the others are lower bounds.

Left out by the device notes, because DNP3 is named only in documents about other products: EPM 2200 Digital Power Meter, EPM 6010 Building Automation Power Meter, EPM 7100 Power Quality Meter, 1408 PowerMonitor 1000, 1420 PowerMonitor 500, 1426 PowerMonitor 5000, Micro830 Controllers.

| DNP3 security documented | Currently sold | Legacy | Lifecycle unknown | Total |
|---|---|---|---|---|
| Encrypted: DNP3 over TLS or IPsec | 4 of 24 (17%) | 0 of 7 (0%) | 0 of 1 (0%) | 4 of 32 (12%) |
| Authenticated, not encrypted (e.g. DNP3 Secure Authentication) | 1 of 24 (4%) | 0 of 7 (0%) | 0 of 1 (0%) | 1 of 32 (3%) |
| Encryption documented for its control protocols, DNP3 not named | 1 of 24 (4%) | 0 of 7 (0%) | 0 of 1 (0%) | 1 of 32 (3%) |
| Only through a separate encrypting device | 2 of 24 (8%) | 0 of 7 (0%) | 0 of 1 (0%) | 2 of 32 (6%) |
| No DNP3 security documented (plaintext) | 16 of 24 (67%) | 7 of 7 (100%) | 1 of 1 (100%) | 24 of 32 (75%) |
| Devices whose documents name DNP3 | 24 | 7 | 1 | 32 |

| Legacy | Lifecycle | Vendor | Model | Type | DNP3 security | Source |
|---|---|---|---|---|---|---|
| no | currently supported | GE Vernova / Multilin | G500 Advanced Substation Gateway | controller / RTU | Encrypted: DNP3 over TLS or IPsec | [S20 pdf-page:1](https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G500-Advanced-Substation-Gateway-Brochure-EN-35437-Hybrid-202504-R002.pdf) |
| no | currently supported | GE Vernova / Multilin | Multilin G100 Advanced Substation Gateway | controller / RTU | Encrypted: DNP3 over TLS or IPsec | [S14 pdf-page:1](https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G100-Brochure-EN-33196-Hybrid-202504-R002.pdf) |
| no | currently supported | Siemens | SICAM A8000 Series | controller / RTU | Encrypted: DNP3 over TLS or IPsec | [S273 pdf-page:12](https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf) |
| no | currently supported | Siemens | Substation automation unit | controller / RTU | Encrypted: DNP3 over TLS or IPsec | [S277 pdf-page:12](https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf) |
| no | currently supported | Rockwell Automation / Allen-Bradley | Micro870 Controllers | PLC | Authenticated, not encrypted (e.g. DNP3 Secure Authentication) | [S192 html-block:61](https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/micro870-controllers.html) |
| no | currently supported | SEL | SEL-3560 | controller / RTU | Encryption documented for its control protocols, DNP3 not named | [S225 pdf-page:2](https://selinc.com/api/download/124708/) |
| no | currently supported | SEL | SEL-3505/3505-3 | controller / RTU | Only through a separate encrypting device (conditional: Needs separate SEL serial or wireless encrypting devices.) | [S223 pdf-page:6](https://selinc.com/api/download/100620/) |
| no | currently supported | SEL | SEL-735 | meter | Only through a separate encrypting device (conditional: Needs a separate SEL Real-Time Automation Controller as gateway.) | [S230 pdf-page:13](https://selinc.com/api/download/128658/) |
| no | currently supported | GE Vernova / Multilin | Multilin 339 | protective relay | No DNP3 security documented (plaintext) | [S108](https://www.gevernova.com/electrification/automation/protection-control-metering/motor-protection/multilin-339); [S112](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-339-Brochure-EN-12779O-Hybrid-202504-R003.pdf) |
| no | currently supported | GE Vernova / Multilin | Multilin 850: Advanced Feeder Protection & Bay Controller | protective relay | No DNP3 security documented (plaintext) | [S118](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-850-Brochure-PO-32050-Hybrid-202509-R001.pdf); [S119](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-850P-Brochure-EN-12739L-Hybrid-202504-R001.pdf); [S120](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-850-Brochure-GE-32050-Hybrid-202509-R002.pdf) (+1 more) |
| no | currently supported | GE Vernova / Multilin | Multilin C60/C95 | controller / RTU | No DNP3 security documented (plaintext) | [S1](https://www.gevernova.com/electrification/automation/protection-control-metering/controllers/multilin-c60c95); [S5](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-C60-Brochure-EN-12654K-Hybrid-202504-R003.pdf); [S6](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-UR-and-URPlus-Brochure-EN-12657H-Hybrid-202504-R002.pdf) |
| no | currently supported | GE Vernova / Multilin | Multilin D20E | controller / RTU | No DNP3 security documented (plaintext) | [S10](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-D20E-Brochure-EN-32042-Hybrid-202504-R002.pdf) |
| no | currently supported | GE Vernova / Multilin | P64 MiCOM 5th Generation | protective relay | No DNP3 security documented (plaintext) | [S127](https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf); [S128](https://www.gevernova.com/electrification/sites/default/files/2025-09/MiCOM-Agile-P64-Brochure-EN-35502-Hybrid-202504-R002.pdf) |
| no | currently supported | GE Vernova / Multilin | iSTAT M2x2 Communicating Measurement Centre | meter | No DNP3 security documented (plaintext) | [S77](https://www.gevernova.com/electrification/sites/default/files/2025-11/iSTAT-M232-Communicating-Measurement-Centre-Brochure-EN-33180-Hybrid-202505-R002.pdf) |
| no | currently supported | SEL | SEL Real-Time Automation Controller (RTAC) | controller / RTU | No DNP3 security documented (plaintext) | [S227](https://selinc.com/api/download/111397/); [S228](https://selinc.com/api/download/129976/) |
| no | currently supported | SEL | SEL-2431 | controller / RTU | No DNP3 security documented (plaintext) | [S221](https://selinc.com/api/download/2835/); [S222](https://selinc.com/api/download/2910/) |
| no | currently supported | SEL | SEL-2664S | protective relay | No DNP3 security documented (plaintext) | [S231](https://selinc.com/api/download/105257/); [S232](https://selinc.com/api/download/104471/) |
| no | currently supported | SEL | SEL-351A | protective relay | No DNP3 security documented (plaintext) | [S233](https://selinc.com/api/download/5523/); [S234](https://selinc.com/api/download/5532/) |
| no | currently supported | SEL | SEL-387 | protective relay | No DNP3 security documented (plaintext) | [S235](https://selinc.com/api/download/292/); [S236](https://selinc.com/api/download/236/) |
| no | currently supported | SEL | SEL-421 | protective relay | No DNP3 security documented (plaintext) | [S237](https://selinc.com/api/download/99010/); [S238](https://selinc.com/api/download/222/) |
| no | currently supported | Siemens | Bay controller – SIPROTEC 6MD86 | controller / RTU | No DNP3 security documented (plaintext) | [S270](https://assets.new.siemens.com/siemens/assets/api/uuid:163e4814-2ae6-40c0-b198-35ed52e610e1/SIPROTEC-6MD86-Profile.pdf) |
| no | currently supported | Siemens | Digital Transducer - SICAM T | meter | No DNP3 security documented (plaintext) | [S293](https://assets.new.siemens.com/siemens/assets/api/uuid:09a829eb-0676-4680-8f95-1adaba01a911/SICAM-PQ-Catalog.pdf) |
| no | currently supported | Siemens | Overcurrent and feeder protection – SIPROTEC 7SJ85 | protective relay | No DNP3 security documented (plaintext) | [S299](https://assets.new.siemens.com/siemens/assets/api/uuid:279cb01d-fd3b-4df4-8e04-f1fe98b81d6b/SIPROTEC-5-Catalog-EN.pdf) |
| no | currently supported | Siemens | Power quality recorder - SICAM Q200 | meter | No DNP3 security documented (plaintext) | [S286](https://assets.new.siemens.com/siemens/assets/api/uuid:09a829eb-0676-4680-8f95-1adaba01a911/SICAM-PQ-Catalog.pdf); [S287](https://assets.new.siemens.com/siemens/assets/api/uuid:16e30661-1286-49b8-b194-94516bb56fa6/SICAM-Q200-Profile-EN.pdf) |
| yes | discontinued, support not stated | GE Vernova / Multilin | EPM 5300 Power Metering System | meter | No DNP3 security documented (plaintext) | [S80](https://www.gevernova.com/electrification/automation/protection-control-metering/epm-5300-legacy) |
| yes | discontinued, support not stated | GE Vernova / Multilin | EPM 9900 Advanced Power Quality Meter | meter | No DNP3 security documented (plaintext) | [S91](https://www.gevernova.com/electrification/automation/protection-control-metering/epm-9900-advanced-power-quality-meter-legacy); [S92](https://www.gevernova.com/electrification/resources?prod=epm9900&type=3&node_id=4903); [S96](https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf) (+2 more) |
| yes | discontinued, support not stated | GE Vernova / Multilin | Multilin D20MX - Advanced Substation Automation Controller | controller / RTU | No DNP3 security documented (plaintext) | [S24](https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d20mx-substation-controller-legacy); [S29](https://www.gevernova.com/electrification/sites/default/files/2025-12/Multilin-D20-Analog-Input-Module-Brochure-EN-12792-Hybrid-202505-R002.pdf); [S30](https://www.gevernova.com/electrification/sites/default/files/2025-12/Multilin-D20-Combination-Module-Brochure-EN-12802A-Hybrid-202505-R002.pdf) (+2 more) |
| yes | discontinued, support not stated | GE Vernova / Multilin | Multilin D400 Advanced Substation Gateway | controller / RTU | No DNP3 security documented (plaintext) | [S33](https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d400-legacy); [S39](https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-D400-Brochure-EN-12806D-Hybrid-202505-001.pdf) |
| yes | discontinued, support not stated | Rockwell Automation / Allen-Bradley | Bulletin 857 Motor-feeder Protection Relays | protective relay | No DNP3 security documented (plaintext) | [S219](https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf) |
| yes | discontinued, support not stated | Rockwell Automation / Allen-Bradley | Bulletin 865 Motor-feeder Protection Relays | protective relay | No DNP3 security documented (plaintext) | [S214](https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf) |
| yes | discontinued, support not stated | Schneider Electric | PowerLogic ION7550 RTU | controller / RTU | No DNP3 security documented (plaintext) | [S243](https://www.se.com/us/en/product-range/1872-powerlogic-ion7550-rtu/) |
| unknown | unknown | GE Vernova / Multilin | MiCOM Agile P24x - Legacy | protective relay | No DNP3 security documented (plaintext) | [S154](https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf) |

## Devices

Identity level says whether the entry is a product family, one model or one catalogue number. Lifecycle status rests only on what the vendor says in a dated source; the date is the one the vendor states or, failing that, the day the source was retrieved. Release date is recorded apart and decides nothing. Exact model, hardware revision and firmware are stated per finding below, as the cited document names them.

| Manufacturer | Model | Category | Identity level | Lifecycle status | Dated vendor evidence | Release date |
|---|---|---|---|---|---|---|
| GE Vernova / Multilin | Multilin C60/C95 | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | Multilin D20E | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | Multilin G100 Advanced Substation Gateway | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | G500 Advanced Substation Gateway | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | DART-Legacy | controller_rtu | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "DART-Legacy / GE Vernova / Electrification Skip to main content Explore GE Vernova DART-Legacy Distribution Automation Remote Terminal [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/dart-legacy> | not established |
| GE Vernova / Multilin | Multilin D20MX - Advanced Substation Automation Controller | controller_rtu | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "Multilin D20MX - Advanced Substation Automation Controller Skip to main content Explore GE Vernova Multilin D20MX Substation Controller [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d20mx-substation-controller-legacy> | not established |
| GE Vernova / Multilin | Multilin D400 Advanced Substation Gateway | controller_rtu | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "Multilin D400 Advanced Substation Gateway / GE Vernova / Electrification Skip to main content Explore GE Vernova Multilin D400 - Legacy [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d400-legacy> | not established |
| GE Vernova / Multilin | Multilin H500 - Legacy | controller_rtu | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "Multilin H500 - Legacy / GE Vernova / Electrification Skip to main content Explore GE Vernova Multilin H500 - Legacy Substation Hardened [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-h500-legacy> | not established |
| GE Vernova / Multilin | EPM 2200 Digital Power Meter | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | EPM 6010 Building Automation Power Meter | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | iSTAT i400 Standard Transducers | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | iSTAT M2x2 Communicating Measurement Centre | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | EPM 4000 Sub-meter (Discontinued) | meter | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "EPM 4000 Sub-meter (Discontinued) Skip to main content Explore GE Vernova EPM 4000 Sub-meter - Legacy EPM 4000 is an easy to use [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/epm-4000-sub-meter-legacy> | not established |
| GE Vernova / Multilin | EPM 5300 Power Metering System | meter | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "EPM 5300 Power Metering System Skip to main content Explore GE Vernova EPM 5300 - Legacy Power Metering System Contact Us GE Vernova’s [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/epm-5300-legacy> | not established |
| GE Vernova / Multilin | EPM 7100 Power Quality Meter | meter | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "EPM 7100 Power Quality Meter / GE Vernova / Electrification Skip to main content Explore GE Vernova EPM 7100 - Legacy Power Quality Meter [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/epm-7100-legacy> | not established |
| GE Vernova / Multilin | EPM 9900 Advanced Power Quality Meter | meter | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "EPM 9900 Advanced Power Quality Meter Skip to main content Explore GE Vernova EPM 9900 Advanced Power Quality Meter - Legacy Contact Us GE [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/epm-9900-advanced-power-quality-meter-legacy> | not established |
| GE Vernova / Multilin | BiTRONICS 70 Series - Legacy | meter | not established | unknown (vendor label: legacy) | 2026-10-13: catalogue listing matches legacy <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | IFC Time-overcurrent Relay | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | Multilin 339 | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | Multilin 850: Advanced Feeder Protection & Bay Controller | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | P64 MiCOM 5th Generation | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| GE Vernova / Multilin | DFP200 Digital Feeder Relay (Discontinued) | protective_relay | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "DFP200 Digital Feeder Relay (Discontinued) Skip to main content Explore GE Vernova DFP200 Digital Feeder Protection - Legacy Contact Us [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/dfp200-digital-feeder-protection-legacy> | not established |
| GE Vernova / Multilin | DLPD Digital Line Protection System | protective_relay | not established | discontinued, support not stated | 2026-10-13: "DLPD Digital Line Protection System Skip to main content Explore GE Vernova DLPD Digital Line Protection System - Legacy Contact Us [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/dlpd-digital-line-protection-system> | not established |
| GE Vernova / Multilin | KAVS Check Synchronising Relay | protective_relay | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "KAVS Check Synchronising Relay / GE Vernova / Electrification Skip to main content Explore GE Vernova KAVS - legacy Contact Us Check [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/kavs-legacy> | not established |
| GE Vernova / Multilin | Multilin A60 - Legacy | protective_relay | not established | discontinued, support not stated (vendor label: legacy) | 2026-10-13: "Multilin A60 - Legacy / GE Vernova / Electrification Skip to main content Explore GE Vernova Multilin A60 - Legacy Contact Us Manufacturing [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-a60-legacy> | not established |
| GE Vernova / Multilin | MBCI, MCRI, MRTP AND MVTW – Legacy | protective_relay | not established | unknown (vendor label: legacy, under last-time buy) | 2026-10-13: "MBCI, MCRI, MRTP AND MVTW - Legacy / GE Vernova / Electrification Skip to main content Explore GE Vernova MBCI, MCRI, MRTP AND MVTW - [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/mbci-mcri-mrtp-and-mvtw-legacy> | not established |
| GE Vernova / Multilin | MiCOM Agile P24x - Legacy | protective_relay | not established | unknown (vendor label: legacy, under last-time buy) | 2026-10-13: "MiCOM Agile P24x - Legacy / GE Vernova / Electrification Skip to main content Explore GE Vernova MiCOM Agile P24x - Legacy Motor Protection [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/micom-agile-p24x-legacy> | not established |
| GE Vernova / Multilin | MiCOM Agile P541 & P542 Line Differential Protection | protective_relay | not established | unknown (vendor label: legacy, under last-time buy) | 2026-10-13: "MiCOM Agile P541 & P542 Line Differential Protection / GE Vernova / Electrification Skip to main content Explore GE Vernova MiCOM Agile [...]" <https://www.gevernova.com/electrification/automation/protection-control-metering/micom-agile-p541-p542-legacy> | not established |
| GE Vernova / Multilin | TCCV Directional Overcurrent Relay | protective_relay | not established | unknown (vendor label: legacy) | 2026-10-13: catalogue listing matches legacy <https://www.gevernova.com/electrification/sitemap.xml> | not established |
| Rockwell Automation / Allen-Bradley | 1408 PowerMonitor 1000 | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.rockwellautomation.com/en-us/sitemap.content.xml> (+1 more) | not established |
| Rockwell Automation / Allen-Bradley | 1420 PowerMonitor 500 | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.rockwellautomation.com/en-us/sitemap.content.xml> (+1 more) | not established |
| Rockwell Automation / Allen-Bradley | 1426 PowerMonitor 5000 | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.rockwellautomation.com/en-us/sitemap.content.xml> (+1 more) | not established |
| Rockwell Automation / Allen-Bradley | CompactLogix 5380 Controllers | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.rockwellautomation.com/en-us/sitemap.content.xml> (+1 more) | not established |
| Rockwell Automation / Allen-Bradley | ControlLogix 5590 Controllers | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.rockwellautomation.com/en-us/sitemap.content.xml> (+1 more) | not established |
| Rockwell Automation / Allen-Bradley | LogixEdge Controllers | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.rockwellautomation.com/en-us/sitemap.content.xml> (+1 more) | not established |
| Rockwell Automation / Allen-Bradley | Micro870 Controllers | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.rockwellautomation.com/en-us/sitemap.content.xml> (+1 more) | not established |
| Rockwell Automation / Allen-Bradley | CompactLogix 1768 Controllers | plc | not established | discontinued, support not stated | 2026-10-13: "CompactLogix 1768 Controllers / Rockwell Automation / US Loading CompactLogix 1768 Controllers Allen-Bradley Our CompactLogix 1768-L4x and [...]" <https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/compactlogix-1768-controllers.html> | not established |
| Rockwell Automation / Allen-Bradley | Micro830 Controllers | plc | not established | discontinued, support not stated | December 31, 2023: "Micro830 Controllers / Rockwell Automation / US Loading Micro830 Controllers Allen-Bradley Rockwell Automation announces that as of [...]" <https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/micro830-controllers.html> | not established |
| Rockwell Automation / Allen-Bradley | MicroLogix 1100 Controllers | plc | not established | discontinued, support not stated | 2026-10-13: "MicroLogix 1100 Controllers / Rockwell Automation / US Loading MicroLogix 1100 Controllers Allen-Bradley Our Bulletin 1763 MicroLogix 1100 [...]" <https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/micrologix-1100-controllers.html> | not established |
| Rockwell Automation / Allen-Bradley | MicroLogix 1200 Controllers | plc | not established | discontinued, support not stated | 2026-10-13: "MicroLogix 1200 Controllers / Rockwell Automation / US Loading MicroLogix 1200 Controllers Allen-Bradley Our Bulletin 1762 MicroLogix 1200 [...]" <https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/micrologix-1200-controllers.html> | not established |
| Rockwell Automation / Allen-Bradley | CompactLogix 5370 Controllers | plc | not established | unknown (vendor label: partly discontinued) | 2026-10-13: "CompactLogix 5370 Controllers / Rockwell Automation / US Loading CompactLogix 5370 Controllers Allen-Bradley Some CompactLogix 5370 [...]" <https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/compactlogix-5370-controllers.html> | not established |
| Rockwell Automation / Allen-Bradley | SLC 500 Controllers | plc | not established | unknown (vendor label: partly discontinued) | 2026-10-13: "SLC 500 Controllers / Rockwell Automation / US Loading SLC 500 Controllers Allen-Bradley Some SLC 500 Bulletin numbers are discontinued and [...]" <https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/slc-500-controllers.html> | not established |
| Rockwell Automation / Allen-Bradley | Bulletin 865 Motor-feeder Protection Relays | protective_relay | not established | discontinued, support not stated | 2026-10-13: "Bulletin 865 Motor-feeder Protection Relays / Rockwell Automation / US Loading Bulletin 865 Motor-feeder Protection Relays Allen-Bradley [...]" <https://www.rockwellautomation.com/en-us/products/hardware/circuit-and-load-protection/865-differential-protection-relay.html> | not established |
| Rockwell Automation / Allen-Bradley | Bulletin 857 Motor-feeder Protection Relays | protective_relay | not established | discontinued, support not stated | 2026-10-13: "Bulletin 857 Motor-feeder Protection Relays / Rockwell Automation / US Loading Bulletin 857 Motor-feeder Protection Relays Allen-Bradley [...]" <https://www.rockwellautomation.com/en-us/products/hardware/circuit-and-load-protection/857-protection-relay.html> | not established |
| SEL | SEL-2431 | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| SEL | SEL-3505/3505-3 | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| SEL | SEL-3560 | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| SEL | SEL Real-Time Automation Controller (RTAC) | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| SEL | SEL-734/734T | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| SEL | SEL-735 | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| SEL | SEL-2664S | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| SEL | SEL-351A | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| SEL | SEL-387 | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| SEL | SEL-421 | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://selinc.com/api/cms/contenttype/productselector/> | not established |
| Schneider Electric | Easergy MiCOM C434 | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | SAGE Remote Terminal Units | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | SAITEL Remote Terminal Unit & Controller | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | SCADAPack 500E | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | PowerLogic ION7550 RTU | controller_rtu | not established | discontinued, support not stated | 2026-10-13: "[...] lligent, web-enabled device provides a cost-effective, dedicated WAGES solution and helps to improve energy efficiency. Discontinued [...]" <https://www.se.com/us/en/product-range/1872-powerlogic-ion7550-rtu/> | not established |
| Schneider Electric | PowerLogic EM4200 Series Enercept | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | PowerLogic™ PM3000 Power Meters | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | PowerLogic™ PM5000 Power Meters | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | PowerLogic™ PM8000 Power Quality Meters | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | PM800 series | meter | not established | discontinued, support not stated | 2026-10-13: "96x96mm PowerLogic power-monitoring units for HV and LV networks Discontinued Contact sales Support Center Read more Discontinued Contact [...]" <https://www.se.com/us/en/product-range/918-pm800-series/> | not established |
| Schneider Electric | PowerLogic Enercept | meter | not established | discontinued, support not stated | 2026-10-13: "[...] split-core CTs combines highly accurate digital metering and communications electronics inside one of the CT housings. Discontinued [...]" <https://www.se.com/us/en/product-range/1703-powerlogic-enercept/> | not established |
| Schneider Electric | PowerLogic Energy Meters | meter | not established | discontinued, support not stated | 2026-10-13: "[...] ity PowerLogic Energy Meters Complete, stand-alone tenant sub-metering Accurate energy metering and simple installation Discontinued [...]" <https://www.se.com/us/en/product-range/1717-powerlogic-energy-meters/> | not established |
| Schneider Electric | PowerLogic ION6200 series | meter | not established | discontinued, support not stated | 2026-10-13: "Simple to use, easy to wire and mount, the meter features a compact design and modular architecture for scalability. Discontinued Contact [...]" <https://www.se.com/us/en/product-range/1505-powerlogic-ion6200-series/> | not established |
| Schneider Electric | Modicon M171/M172 Logic Controller | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | Modicon M241 Micro PLC | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | Modicon M258 Compact PLC for Machine Automation | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | Modicon MCM | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | Compact PLC | plc | not established | discontinued, support not stated | 2026-10-13: "[...] nal Links View all customer success stories Schneider Electric University Compact PLC Modicon Compact Part of Modicon - Discontinued [...]" <https://www.se.com/us/en/product-range/61593-compact-plc/> | not established |
| Schneider Electric | Modicon LMC058 / LMC078 | plc | not established | discontinued, support not stated | 2026-10-13: "[...] oftware suite, SoMachine, including the same Motion Libraries based on PLCopen, Embedded I/O, and numerous field buses. Discontinued [...]" <https://www.se.com/us/en/product-range/7744-modicon-lmc058-lmc078/> | not established |
| Schneider Electric | Modicon Premium PAC | plc | not established | discontinued, support not stated | 2026-10-13: "[...] AC for Discrete or Process applications and high availability solutions Part of Modicon PLC for manufacturing processes Discontinued [...]" <https://www.se.com/us/en/product-range/537-modicon-premium-pac/> | not established |
| Schneider Electric | Twido - Programmable Controller | plc | not established | discontinued, support not stated (vendor label: obsolete) | December 2016: "[...] Legal Additional Links View all customer success stories Schneider Electric University Twido - Programmable Controller Obsolete [...]" <https://www.se.com/us/en/product-range/533-twido-programmable-controller/> | not established |
| Schneider Electric | MiCOM P59x | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | MiCOM P841 | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | Sepam series 80 | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | Vamp Arc Protection Relay System | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.se.com/us/en/product-range/google-range-sitemap-US-en.xml> | not established |
| Schneider Electric | MiCOM P22x | protective_relay | not established | discontinued, support not stated | 2026-10-13: "[...] er success stories Schneider Electric University MiCOM P22x Motor and Overcurrent Protection Relay Part of PowerLogic - Discontinued [...]" <https://www.se.com/us/en/product-range/60752-micom-p22x/> | not established |
| Schneider Electric | MiCOM P521 | protective_relay | not established | discontinued, support not stated | 2026-10-13: "[...] tomer success stories Schneider Electric University MiCOM P521 Fast Feeder Differential Protection Part of PowerLogic - Discontinued [...]" <https://www.se.com/us/en/product-range/60745-micom-p521/> | not established |
| Schneider Electric | MiCOM P821 | protective_relay | not established | discontinued, support not stated | 2026-10-13: "[...] w all customer success stories Schneider Electric University MiCOM P821 Breaker Failure Protection Part of PowerLogic - Discontinued [...]" <https://www.se.com/us/en/product-range/60739-micom-p821/> | not established |
| Schneider Electric | Sepam series 20 | protective_relay | not established | discontinued, support not stated | 2026-10-13: "[...] rotection functions with ZSI applications for motors and substation feeders and transformers in any distribution system Discontinued [...]" <https://www.se.com/us/en/product-range/933-sepam-series-20/> | not established |
| Siemens | Bay controller – SIPROTEC 6MD86 | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | SICAM A8000 Series | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | Substation automation unit | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | MAB-Multipurpose-Automation-Box | controller_rtu | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | SENTRON measuring devices for energy transparency | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | Power quality recorder - SICAM Q200 | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | SENTRON measuring devices for energy transparency | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | Digital Transducer - SICAM T | meter | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | SIMATIC S7-1200 G2 | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | SIMATIC S7-1500 R/H CPUs - High Availability | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | SIMATIC S7-1500 Software Controller | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | SIMATIC S7-400 | plc | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | Overcurrent and feeder protection – SIPROTEC 7SJ85 | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | Reyrolle 7SR157: Check Synchronising | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | Reyrolle 7SR46: CT-powered overcurrent protection | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |
| Siemens | SIPROTEC 7SY82 | protective_relay | not established | currently supported | 2026-10-13: listed in the vendor catalogue without a notice of discontinuation <https://www.siemens.com/en-us/sitemap-en-us.xml> | not established |

## Summary by vendor, category and lifecycle

Devices, counted once each, by what the review established for a control protocol. "In the catalogue" is the number of classified entries in the vendor catalogue for that stratum, where the config was drawn from an inventory. A stratum with few devices in this run supports no generalisation.

| Vendor | Category | Lifecycle | In the catalogue | In this run | Authentication of a control protocol | Integrity of a control protocol | Encryption of a control protocol |
|---|---|---|---|---|---|---|---|
| GE Vernova / Multilin | controller_rtu | currently supported | 7 | 4 | 3 unknown: other interface only, 1 unknown | 4 unknown | 2 supported, 2 unknown |
| GE Vernova / Multilin | controller_rtu | discontinued, support not stated | 15 | 4 | 2 unknown: other interface only, 2 unknown | 4 unknown | 4 unknown |
| GE Vernova / Multilin | meter | currently supported | 16 | 4 | 1 unknown: complete document silent, 1 unknown: other interface only, 2 unknown | 2 unknown: complete document silent, 2 unknown | 1 unknown: complete document silent, 3 unknown |
| GE Vernova / Multilin | meter | discontinued, support not stated | 23 | 4 | 1 unknown: complete document silent, 3 unknown | 1 unknown: complete document silent, 3 unknown | 1 unknown: complete document silent, 3 unknown |
| GE Vernova / Multilin | meter | unknown | 1 | 1 | 1 unknown | 1 unknown | 1 unknown |
| GE Vernova / Multilin | protective_relay | currently supported | 66 | 4 | 2 unknown: other interface only, 2 unknown | 4 unknown | 1 unknown: other interface only, 3 unknown |
| GE Vernova / Multilin | protective_relay | discontinued, support not stated | 103 | 4 | 4 unknown | 4 unknown | 4 unknown |
| GE Vernova / Multilin | protective_relay | unknown | 4 | 4 | 1 unknown: complete document silent, 3 unknown | 1 unknown: complete document silent, 3 unknown | 1 unknown: complete document silent, 3 unknown |
| Rockwell Automation / Allen-Bradley | meter | currently supported | 3 | 3 | 3 unknown: complete document silent | 3 unknown: complete document silent | 3 unknown: complete document silent |
| Rockwell Automation / Allen-Bradley | plc | currently supported | 14 | 4 | 1 supported, 1 conditional, 2 unknown | 1 conditional, 3 unknown | 1 conditional, 3 unknown |
| Rockwell Automation / Allen-Bradley | plc | discontinued, support not stated | 5 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Rockwell Automation / Allen-Bradley | plc | unknown | 2 | 2 | 1 unknown: complete document silent, 1 unknown | 1 unknown: complete document silent, 1 unknown | 2 unknown: complete document silent |
| Rockwell Automation / Allen-Bradley | protective_relay | discontinued, support not stated | 2 | 2 | 2 unknown: complete document silent | 2 unknown: complete document silent | 2 unknown: complete document silent |
| SEL | controller_rtu | currently supported | 15 | 4 | 3 unknown: other interface only, 1 unknown | 4 unknown | 1 supported, 1 via external gateway only, 2 unknown |
| SEL | meter | currently supported | 2 | 2 | 2 unknown | 2 unknown | 1 via external gateway only, 1 unknown |
| SEL | protective_relay | currently supported | 44 | 4 | 1 supported, 3 unknown | 4 unknown | 4 unknown |
| Schneider Electric | controller_rtu | currently supported | 10 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Schneider Electric | controller_rtu | discontinued, support not stated | 1 | 1 | 1 unknown | 1 unknown | 1 unknown |
| Schneider Electric | meter | currently supported | 12 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Schneider Electric | meter | discontinued, support not stated | 5 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Schneider Electric | plc | currently supported | 13 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Schneider Electric | plc | discontinued, support not stated | 4 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Schneider Electric | protective_relay | currently supported | 27 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Schneider Electric | protective_relay | discontinued, support not stated | 10 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Siemens | controller_rtu | currently supported | 9 | 4 | 1 unknown: other interface only, 3 unknown | 4 unknown | 2 supported, 1 unknown: other interface only, 1 unknown |
| Siemens | meter | currently supported | 9 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Siemens | plc | currently supported | 10 | 4 | 4 unknown | 4 unknown | 4 unknown |
| Siemens | protective_relay | currently supported | 52 | 4 | 1 unknown: other interface only, 3 unknown | 1 unknown: other interface only, 3 unknown | 1 unknown: other interface only, 3 unknown |

## Findings by product and interface

One row per product and interface. Authentication, integrity and encryption are stated for that interface only; a result for a management interface says nothing about control traffic. "Evidence applies to" is the exact model, hardware revision and firmware the cited documents name. Default, activation and deployment are stated for supported and conditional findings. Full quotes are under "Findings and evidence" and in findings_table.csv; source references are resolved under "Sources examined".

| Manufacturer | Model | Lifecycle | Evidence applies to | Protocol / interface | Authentication | Integrity | Encryption | Support conditions | Default | Activation | Deployment | Evidence | Review status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GE Vernova / Multilin | Multilin C60/C95 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin C60/C95 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | User access to the relay (AAA server) (management) | supported: RADIUS | unknown | unknown | not assessed | not assessed | not assessed | unknown | S1 [type not confirmed] html-block:166: "Enables integration with centrally managed authentication and accounting of all user activities" | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin D20E | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin G100 Advanced Substation Gateway | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Master station link (DNP3/TCP, Modbus/TCP, IEC 104) (control protocol) | unknown; see tls (supported) | unknown; see tls (supported) | supported: TLS tunnel for the SCADA protocols | not assessed | not assessed | not assessed | unknown | S14 [type not confirmed] pdf-page:1: "Secure tunneling from master station via TLS for DNP3/TCP, Modbus/TCP and IEC 104" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin G100 Advanced Substation Gateway | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | User access to the gateway (management) | supported: Local accounts, LDAP, TACACS+ | unknown | not reviewed | not assessed | not assessed | not assessed | unknown | S14 [type not confirmed] pdf-page:7: "Local and Remote Authentication modes are supported to ensure that only authenticated and authorized users [...]" | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin G100 Advanced Substation Gateway | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Remote access to substation devices through the gateway (management) | unknown; see ssh (supported) | unknown; see ssh (supported) | not assessed; see ssh (supported) | not assessed | not assessed | not assessed | unknown | S14 [type not confirmed] pdf-page:7: "Remote access can be secured with TLS or SSH." | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | G500 Advanced Substation Gateway | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Master station link (DNP3/TCP, Modbus/TCP, IEC 104) (control protocol) | unknown; see tls (supported) | unknown; see tls (supported) | supported: TLS tunnel for the SCADA protocols | not assessed | not assessed | not assessed | unknown | S20 [type not confirmed] pdf-page:1: "Secure tunneling from master station via TLS for DNP3/TCP, Modbus/TCP and IEC 104" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | G500 Advanced Substation Gateway | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | User access to the gateway (management) | supported: Local accounts, LDAP, TACACS+ | unknown | not reviewed | not assessed | not assessed | not assessed | unknown | S20 [type not confirmed] pdf-page:9: "Local and Remote Authentication modes are supported to ensure that only authenticated and authorized users [...]" | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | G500 Advanced Substation Gateway | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Remote access to substation devices through the gateway (management) | unknown; see ssh (supported) | unknown; see ssh (supported) | not assessed; see ssh (supported) | not assessed | not assessed | not assessed | unknown | S20 [type not confirmed] pdf-page:9: "Remote access can be secured with TLS or SSH." | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | DART-Legacy | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin D20MX - Advanced Substation Automation Controller | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin D20MX - Advanced Substation Automation Controller | discontinued, support not stated | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | User access to the controller (management) | supported: RADIUS, role based access control | unknown | unknown | built in | not assessed | not assessed | unknown | S24 [type not confirmed] html-block:70: "Built-in cyber security features, such as Remote Authentication Dial-In User Service (RADIUS), Role Based [...]" | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin D20MX - Advanced Substation Automation Controller | discontinued, support not stated | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Firmware and configuration file transfer (management) | unknown; see ssh (supported) | unknown; see ssh (supported) | unknown; see ssh (supported) | not assessed | not assessed | not assessed | unknown | S31 [type not confirmed] pdf-page:1: "SSH and SFTP provide secure firmware and configuration file transfer" | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin D400 Advanced Substation Gateway | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin D400 Advanced Substation Gateway | discontinued, support not stated | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Pass-through and terminal server access to substation devices (management) | unknown; see tls (supported), ssh (supported) | unknown; see tls (supported), ssh (supported) | unknown; see tls (supported), ssh (supported) | not assessed | not assessed | not assessed | unknown | S33 [type not confirmed] html-block:17: "Secure pass through / terminal server, with support for SSH and TLS, allowing personnel to access substation [...]" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin D400 Advanced Substation Gateway | discontinued, support not stated | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | User access to the gateway (management) | supported: LDAP, TACACS+, RADIUS or internal database | unknown | unknown | not assessed | not assessed | not assessed | unknown | S33 [type not confirmed] html-block:14: "Advanced security features including centralized user authentication (LDAP & TACACS+), access control, and [...]" | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin H500 - Legacy | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | EPM 2200 Digital Power Meter | currently supported | model as covered by the cited manual, hardware not established, firmware as covered by the EPM 2200 instruction manual | Communication protocols of the device as described in its manual (control protocol) | unknown; see dnp3_secure_authentication (unknown: complete document silent), tls (unknown: complete document silent), ipsec (unknown: complete document silent), cip_security (unknown: complete document silent), ssh (unknown: complete document silent) | unknown: the complete documentation searched does not mention it | unknown; see tls (unknown: complete document silent), ipsec (unknown: complete document silent), cip_security (unknown: complete document silent), ssh (unknown: complete document silent) | none stated | - | - | unknown | S52 [manual] searched in full, 123 PDF pages: no lead for dnp3_secure_authentication; S52 [manual] searched in full, 123 PDF pages: no lead for tls; S52 [manual] searched in full, 123 PDF pages: no lead for ipsec; S52 [manual] searched in full, 123 PDF pages: no lead for cip_security; S52 [manual] searched in full, 123 PDF pages: no lead for ssh; S52 [manual] searched in full, 123 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | EPM 2200 Digital Power Meter | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Ethernet card web configuration page (management) | supported: User name and password | not reviewed | unknown | not assessed | not assessed | not assessed | unknown | S52 [manual] pdf-page:91: "You will see a User Authentication screen." | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | EPM 6010 Building Automation Power Meter | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | iSTAT i400 Standard Transducers | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | iSTAT M2x2 Communicating Measurement Centre | currently supported | model as covered by the cited manual, hardware not established, firmware as covered by the iSTAT M2x2 manual | Communication protocols of the device as described in its manual (control protocol) | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S75 [manual] searched in full, 72 PDF pages: no lead for dnp3_secure_authentication; S75 [manual] searched in full, 72 PDF pages: no lead for tls; S75 [manual] searched in full, 72 PDF pages: no lead for ipsec; S75 [manual] searched in full, 72 PDF pages: no lead for cip_security; S75 [manual] searched in full, 72 PDF pages: no lead for authentication; S75 [manual] searched in full, 72 PDF pages: no lead for encryption; S75 [manual] searched in full, 72 PDF pages: no lead for ssh; S75 [manual] searched in full, 72 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | EPM 4000 Sub-meter (Discontinued) | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | EPM 5300 Power Metering System | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | EPM 7100 Power Quality Meter | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | EPM 9900 Advanced Power Quality Meter | discontinued, support not stated | model as covered by the cited manual, hardware not established, firmware as covered by the EPM 9000 series DNP guide | DNP3 as described in the EPM 9000 series DNP guide (control protocol) | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S96 [manual] searched in full, 272 PDF pages: no lead for dnp3_secure_authentication; S96 [manual] searched in full, 272 PDF pages: no lead for tls; S96 [manual] searched in full, 272 PDF pages: no lead for ipsec; S96 [manual] searched in full, 272 PDF pages: no lead for cip_security; S96 [manual] searched in full, 272 PDF pages: no lead for authentication; S96 [manual] searched in full, 272 PDF pages: no lead for encryption; S96 [manual] searched in full, 272 PDF pages: no lead for ssh; S96 [manual] searched in full, 272 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | BiTRONICS 70 Series - Legacy | unknown | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | IFC Time-overcurrent Relay | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin 339 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin 850: Advanced Feeder Protection & Bay Controller | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin 850: Advanced Feeder Protection & Bay Controller | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | User access to the relay (AAA server) (management) | supported: RADIUS | unknown | unknown | not assessed | not assessed | not assessed | unknown | S113 [type not confirmed] html-block:57: "High-end cyber security such as AAA, Radius, RBAC and Syslog, enabling NERC CIP requirements." | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | P64 MiCOM 5th Generation | currently supported | model as covered by the cited manual, hardware not established, firmware as covered by technical manual P64-TM-EN-1 | Substation and SCADA protocols of the relay as described in its technical manual (control protocol) | unknown; see dnp3_secure_authentication (unknown: complete document silent), tls (unknown: complete document silent), ipsec (unknown: complete document silent), cip_security (unknown: complete document silent) | unknown; see dnp3_secure_authentication (unknown: complete document silent), tls (unknown: complete document silent), ipsec (unknown: complete document silent), cip_security (unknown: complete document silent) | unknown; see tls (unknown: complete document silent), ipsec (unknown: complete document silent), cip_security (unknown: complete document silent) | none stated | - | - | unknown | S127 [manual] searched in full, 672 PDF pages: no lead for dnp3_secure_authentication; S127 [manual] searched in full, 672 PDF pages: no lead for tls; S127 [manual] searched in full, 672 PDF pages: no lead for ipsec; S127 [manual] searched in full, 672 PDF pages: no lead for cip_security | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | P64 MiCOM 5th Generation | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware as covered by technical manual P64-TM-EN-1 | User access to the IED (front panel, S1 Agile, network ports) (management) | supported: Device and RADIUS server authentication | unknown | unknown | not assessed | enabled | not assessed | unknown | S127 [manual] pdf-page:419: "The IED supports Bypass (no authentication), Device authentication and Server authentication." (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | P64 MiCOM 5th Generation | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware as covered by technical manual P64-TM-EN-1 | S1 Agile engineering tool connection (management) | unknown; see ssh (supported) | unknown; see ssh (supported) | supported: Encrypted passwords in messages between S1 Agile and the IED | not assessed | not assessed | not assessed | unknown | S127 [manual] pdf-page:415: "Encryption of passwords - stored within the IED, in network messages between the MiCOM S1 Agile software and [...]" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | DFP200 Digital Feeder Relay (Discontinued) | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | DLPD Digital Line Protection System | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | KAVS Check Synchronising Relay | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | Multilin A60 - Legacy | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | MBCI, MCRI, MRTP AND MVTW – Legacy | unknown | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | MiCOM Agile P24x - Legacy | unknown | model as covered by the cited manual, hardware not established, firmware as covered by technical manual P24x-TM-EN-J82 | Communication protocols of the device as described in its manual (control protocol) | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S154 [manual] searched in full, 556 PDF pages: no lead for dnp3_secure_authentication; S154 [manual] searched in full, 556 PDF pages: no lead for tls; S154 [manual] searched in full, 556 PDF pages: no lead for ipsec; S154 [manual] searched in full, 556 PDF pages: no lead for cip_security; S154 [manual] searched in full, 556 PDF pages: no lead for authentication; S154 [manual] searched in full, 556 PDF pages: no lead for encryption; S154 [manual] searched in full, 556 PDF pages: no lead for ssh; S154 [manual] searched in full, 556 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | MiCOM Agile P541 & P542 Line Differential Protection | unknown | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| GE Vernova / Multilin | TCCV Directional Overcurrent Relay | unknown | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | 1408 PowerMonitor 1000 | currently supported | model as covered by the cited manual, hardware not established, firmware as covered by user manual 1408-UM002 | Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual (control protocol) | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S166 [manual] searched in full, 216 PDF pages: no lead for dnp3_secure_authentication; S166 [manual] searched in full, 216 PDF pages: no lead for ipsec; S166 [manual] searched in full, 216 PDF pages: no lead for cip_security; S166 [manual] searched in full, 216 PDF pages: no lead for authentication; S166 [manual] searched in full, 216 PDF pages: no lead for encryption; S166 [manual] searched in full, 216 PDF pages: no lead for ssh; S166 [manual] searched in full, 216 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | 1408 PowerMonitor 1000 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Web page and FTP access to the unit (management) | not assessed; see tls (supported) | not assessed; see tls (supported) | not assessed; see tls (supported) | not assessed | not assessed | configuration: HTTPS Enable and FTPS Enable settings are set to 1. | unknown | S166 [manual] pdf-page:55: "you must use a browser capable of supporting SSL" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | 1420 PowerMonitor 500 | currently supported | model as covered by the cited manual, hardware not established, firmware as covered by user manual 1420-UM001 | Communication protocols of the device as described in its manual (control protocol) | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S172 [manual] searched in full, 108 PDF pages: no lead for dnp3_secure_authentication; S172 [manual] searched in full, 108 PDF pages: no lead for tls; S172 [manual] searched in full, 108 PDF pages: no lead for ipsec; S172 [manual] searched in full, 108 PDF pages: no lead for cip_security; S172 [manual] searched in full, 108 PDF pages: no lead for authentication; S172 [manual] searched in full, 108 PDF pages: no lead for encryption; S172 [manual] searched in full, 108 PDF pages: no lead for ssh; S172 [manual] searched in full, 108 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | 1426 PowerMonitor 5000 | currently supported | model as covered by the cited manual, hardware not established, firmware as covered by user manual 1426-UM001 | Communication protocols of the device as described in its manual (control protocol) | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S178 [manual] searched in full, 406 PDF pages: no lead for dnp3_secure_authentication; S178 [manual] searched in full, 406 PDF pages: no lead for tls; S178 [manual] searched in full, 406 PDF pages: no lead for ipsec; S178 [manual] searched in full, 406 PDF pages: no lead for cip_security; S178 [manual] searched in full, 406 PDF pages: no lead for authentication; S178 [manual] searched in full, 406 PDF pages: no lead for encryption; S178 [manual] searched in full, 406 PDF pages: no lead for ssh; S178 [manual] searched in full, 406 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | CompactLogix 5380 Controllers | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware 34.011 or later | EtherNet/IP (CIP) communication (control protocol) | conditional: CIP Security on EtherNet/IP | conditional: CIP Security on EtherNet/IP | conditional: CIP Security on EtherNet/IP | firmware upgrade: Controller firmware revision 34.011 or later, Studio 5000 Logix Designer version 34 or later. | not assessed | cip_security: configuration, other: A security policy (zones and conduits) is defined and deployed with FactoryTalk Policy Manager.; authentication: not assessed; encryption: not assessed; integrity: not assessed | unknown | S183 [type not confirmed] pdf-page:28: "controllers also support CIP Security with firmware revision 34.011 or later" (+8 more) | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | ControlLogix 5590 Controllers | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | EtherNet/IP (CIP) communication (control protocol) | unknown; see cip_security (supported) | unknown; see cip_security (supported) | unknown; see cip_security (supported) | built in | not assessed | not assessed | unknown | S189 [type not confirmed] pdf-page:5: "Integrated CIP Security, secure boot and device-level protection" | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | LogixEdge Controllers | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | Micro870 Controllers | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | DNP3 outstation (slave) communication (control protocol) | supported: DNP3 Secure Authentication version 5 | unknown; see dnp3_secure_authentication (supported) | unknown | not assessed | not assessed | not assessed | unknown | S192 [type not confirmed] html-block:61: "Provide enhanced protocol authentication in DNP3 with Secure Authentication version 5 (SAv5)" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | CompactLogix 1768 Controllers | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | Micro830 Controllers | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | MicroLogix 1100 Controllers | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | MicroLogix 1200 Controllers | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | CompactLogix 5370 Controllers | unknown | model as covered by the cited manual, hardware not established, firmware as covered by user manual 1769-UM021 | EtherNet/IP and serial communication as described in the user manual (control protocol) | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S202 [manual] searched in full, 272 PDF pages: no lead for dnp3_secure_authentication; S202 [manual] searched in full, 272 PDF pages: no lead for tls; S202 [manual] searched in full, 272 PDF pages: no lead for ipsec; S202 [manual] searched in full, 272 PDF pages: no lead for cip_security; S202 [manual] searched in full, 272 PDF pages: no lead for authentication; S202 [manual] searched in full, 272 PDF pages: no lead for encryption; S202 [manual] searched in full, 272 PDF pages: no lead for ssh; S202 [manual] searched in full, 272 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | SLC 500 Controllers | unknown | model as covered by the cited manual, hardware not established, firmware as covered by 1747-UM011, 1747-UM009 and 1747-RM001 | DF1, DH-485, DH+ and Ethernet communication as described in the manuals (control protocol) | unknown; see dnp3_secure_authentication (unknown: complete document silent), tls (unknown: complete document silent), ipsec (unknown: complete document silent), cip_security (unknown: complete document silent), ssh (unknown: complete document silent) | unknown; see dnp3_secure_authentication (unknown: complete document silent), tls (unknown: complete document silent), ipsec (unknown: complete document silent), cip_security (unknown: complete document silent), ssh (unknown: complete document silent) | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S207 [manual] searched in full, 296 PDF pages: no lead for dnp3_secure_authentication; S208 [manual] searched in full, 223 PDF pages: no lead for dnp3_secure_authentication; S209 [manual] searched in full, 694 PDF pages: no lead for dnp3_secure_authentication; S207 [manual] searched in full, 296 PDF pages: no lead for tls; S208 [manual] searched in full, 223 PDF pages: no lead for tls; S209 [manual] searched in full, 694 PDF pages: no lead for tls; S207 [manual] searched in full, 296 PDF pages: no lead for ipsec; S208 [manual] searched in full, 223 PDF pages: no lead for ipsec; S209 [manual] searched in full, 694 PDF pages: no lead for ipsec; S207 [manual] searched in full, 296 PDF pages: no lead for cip_security; S208 [manual] searched in full, 223 PDF pages: no lead for cip_security; S209 [manual] searched in full, 694 PDF pages: no lead for cip_security; S207 [manual] searched in full, 296 PDF pages: no lead for encryption; S208 [manual] searched in full, 223 PDF pages: no lead for encryption; S209 [manual] searched in full, 694 PDF pages: no lead for encryption; S207 [manual] searched in full, 296 PDF pages: no lead for ssh; S208 [manual] searched in full, 223 PDF pages: no lead for ssh; S209 [manual] searched in full, 694 PDF pages: no lead for ssh | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | Bulletin 865 Motor-feeder Protection Relays | discontinued, support not stated | model as covered by the cited manual, hardware not established, firmware as covered by user manual 865-UM001 | Communication protocols of the device as described in its manual (control protocol) | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S214 [manual] searched in full, 296 PDF pages: no lead for dnp3_secure_authentication; S214 [manual] searched in full, 296 PDF pages: no lead for tls; S214 [manual] searched in full, 296 PDF pages: no lead for ipsec; S214 [manual] searched in full, 296 PDF pages: no lead for cip_security; S214 [manual] searched in full, 296 PDF pages: no lead for authentication; S214 [manual] searched in full, 296 PDF pages: no lead for encryption; S214 [manual] searched in full, 296 PDF pages: no lead for ssh; S214 [manual] searched in full, 296 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| Rockwell Automation / Allen-Bradley | Bulletin 857 Motor-feeder Protection Relays | discontinued, support not stated | model as covered by the cited manual, hardware not established, firmware as covered by 857-UM001, 857-UM004 and 857-UM005 | IEC 61850, EtherNet/IP and serial protocols as described in the manuals (control protocol) | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | unknown: the complete documentation searched does not mention it | none stated | - | - | unknown | S219 [manual] searched in full, 504 PDF pages: no lead for dnp3_secure_authentication; S216 [manual] searched in full, 104 PDF pages: no lead for dnp3_secure_authentication; S220 [manual] searched in full, 70 PDF pages: no lead for dnp3_secure_authentication; S219 [manual] searched in full, 504 PDF pages: no lead for tls; S216 [manual] searched in full, 104 PDF pages: no lead for tls; S220 [manual] searched in full, 70 PDF pages: no lead for tls; S219 [manual] searched in full, 504 PDF pages: no lead for ipsec; S216 [manual] searched in full, 104 PDF pages: no lead for ipsec; S220 [manual] searched in full, 70 PDF pages: no lead for ipsec; S219 [manual] searched in full, 504 PDF pages: no lead for cip_security; S216 [manual] searched in full, 104 PDF pages: no lead for cip_security; S220 [manual] searched in full, 70 PDF pages: no lead for cip_security; S219 [manual] searched in full, 504 PDF pages: no lead for authentication; S216 [manual] searched in full, 104 PDF pages: no lead for authentication; S220 [manual] searched in full, 70 PDF pages: no lead for authentication; S219 [manual] searched in full, 504 PDF pages: no lead for encryption; S216 [manual] searched in full, 104 PDF pages: no lead for encryption; S220 [manual] searched in full, 70 PDF pages: no lead for encryption; S219 [manual] searched in full, 504 PDF pages: no lead for ssh; S216 [manual] searched in full, 104 PDF pages: no lead for ssh; S220 [manual] searched in full, 70 PDF pages: no lead for ssh; S219 [manual] searched in full, 504 PDF pages: no lead for integrity; S216 [manual] searched in full, 104 PDF pages: no lead for integrity; S220 [manual] searched in full, 70 PDF pages: no lead for integrity | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-2431 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-3505/3505-3 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Remote serial links to field devices (control protocol) | unknown | unknown | conditional: external gateway only: Serial SCADA protocols through separate encrypting devices | external gateway: Needs separate SEL serial or wireless encrypting devices. | not assessed | not assessed | unknown | S223 [type not confirmed] pdf-page:6: "you can protect remote serial communication to recloser controls" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-3505/3505-3 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Encrypted communication listed under security features (interface not specified) (management) | unknown; see tls (supported) | unknown; see tls (supported) | not assessed; see tls (supported) | not assessed | not assessed | not assessed | unknown | S223 [type not confirmed] pdf-page:10: "Encrypted Communication: SSL/TLS, SSH" | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-3505/3505-3 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | User access to the controller (management) | supported: User accounts, LDAP, RADIUS | unknown | not reviewed | not assessed | not assessed | not assessed | unknown | S223 [type not confirmed] pdf-page:4: "LDAP central authentication for user account management" | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-3560 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Ethernet-tunneled serial SCADA protocols (control protocol) | unknown; see tls (supported), ssh (supported) | unknown; see tls (supported), ssh (supported) | supported: SSH or SSL/TLS tunnelling of serial SCADA protocols over Ethernet | not assessed | not assessed | not assessed | unknown | S225 [type not confirmed] pdf-page:2: "Optional encryption for Ethernet-tunneled serial SCADA protocols and engineering access via Secure Shell [...]" (+2 more) | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-3560 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | User access to the controller (management) | supported: User accounts, LDAP | unknown | not reviewed | not assessed | not assessed | not assessed | unknown | S225 [type not confirmed] pdf-page:2: "Centralized authentication through the Lightweight Directory Access Protocol (LDAP)" | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL Real-Time Automation Controller (RTAC) | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL Real-Time Automation Controller (RTAC) | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Web HMI (management) | supported: Authenticated web access | unknown | unknown | not assessed | not assessed | not assessed | unknown | S227 [type not confirmed] pdf-page:6: "The HMI allows authenticated access for multiple users and locations and is viewable from a web browser." | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-734/734T | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-735 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Meter data to SCADA through a separate RTAC (control protocol) | unknown | unknown | conditional: external gateway only: Encrypted communication provided by an RTAC acting as gateway | external gateway: Needs a separate SEL Real-Time Automation Controller as gateway. | not assessed | not assessed | unknown | S230 [type not confirmed] pdf-page:13: "provides secure, encrypted communications and works as a remote intelligence gateway" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-2664S | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-351A | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-387 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| SEL | SEL-421 | currently supported | model SEL-421-4, -5 (data sheet), hardware not established, firmware not established | IEC 61850 MMS server (control protocol) | supported: MMS authentication | unknown | unknown | not assessed | not assessed | configuration: Enabled by a setting in the Configured IED Description (CID) file. | unknown | S237 [type not confirmed] pdf-page:13: "the relay requires authentication from any client requesting to initiate an MMS session" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Easergy MiCOM C434 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | SAGE Remote Terminal Units | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | SAITEL Remote Terminal Unit & Controller | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | SCADAPack 500E | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | PowerLogic ION7550 RTU | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | PowerLogic EM4200 Series Enercept | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | PowerLogic™ PM3000 Power Meters | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | PowerLogic™ PM5000 Power Meters | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | PowerLogic™ PM8000 Power Quality Meters | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | PM800 series | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | PowerLogic Enercept | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | PowerLogic Energy Meters | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | PowerLogic ION6200 series | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Modicon M171/M172 Logic Controller | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Modicon M241 Micro PLC | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Modicon M258 Compact PLC for Machine Automation | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Modicon MCM | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Compact PLC | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Modicon LMC058 / LMC078 | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Modicon Premium PAC | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Twido - Programmable Controller | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | MiCOM P59x | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | MiCOM P841 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Sepam series 80 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Vamp Arc Protection Relay System | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | MiCOM P22x | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | MiCOM P521 | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | MiCOM P821 | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Schneider Electric | Sepam series 20 | discontinued, support not stated | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Bay controller – SIPROTEC 6MD86 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Bay controller – SIPROTEC 6MD86 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | DIGSI engineering tool connection (management) | unknown | unknown | supported: Encrypted communication between DIGSI and the device | not assessed | not assessed | not assessed | unknown | S269 [type not confirmed] pdf-page:6: "Security through encryption - on the entire communication chain between DIGSI and device" | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Bay controller – SIPROTEC 6MD86 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Network access (IEEE 802.1X) (network) | supported: IEEE 802.1X | unknown | unknown | not assessed | not assessed | not assessed | unknown | S268 [type not confirmed] html-block:13: "role-based access control, signed firmware, authenticated network access and secure event logging" | draft (Claude AI draft review; author confirmation pending) |
| Siemens | SICAM A8000 Series | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) (control protocol) | unknown; see tls (supported) | unknown; see tls (supported) | supported: TLS encryption | not assessed | not assessed | not assessed | unknown | S273 [type not confirmed] pdf-page:12: "DNP3i master/slave (Transport Layer Security (TLS))" (+3 more) | draft (Claude AI draft review; author confirmation pending) |
| Siemens | SICAM A8000 Series | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | IP network layer (network) | unknown; see ipsec (supported) | unknown; see ipsec (supported) | not assessed; see ipsec (supported) | not assessed | not assessed | not assessed | unknown | S272 [type not confirmed] html-block:16: "crypto chip and IPSec encryption" | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Substation automation unit | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) (control protocol) | unknown; see tls (supported) | unknown; see tls (supported) | supported: TLS encryption | not assessed | not assessed | not assessed | unknown | S277 [type not confirmed] pdf-page:12: "DNP3i master/slave (Transport Layer Security (TLS))" (+3 more) | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Substation automation unit | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | IP network layer (network) | unknown; see ipsec (supported) | unknown; see ipsec (supported) | not assessed; see ipsec (supported) | not assessed | not assessed | not assessed | unknown | S276 [type not confirmed] html-block:14: "crypto chip and IPSec encryption" | draft (Claude AI draft review; author confirmation pending) |
| Siemens | MAB-Multipurpose-Automation-Box | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | SENTRON measuring devices for energy transparency | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Power quality recorder - SICAM Q200 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | SENTRON measuring devices for energy transparency | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Digital Transducer - SICAM T | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | SIMATIC S7-1200 G2 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | SIMATIC S7-1500 R/H CPUs - High Availability | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | SIMATIC S7-1500 Software Controller | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | SIMATIC S7-400 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Overcurrent and feeder protection – SIPROTEC 7SJ85 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Overcurrent and feeder protection – SIPROTEC 7SJ85 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware not established | DIGSI 5 engineering tool connection (management) | unknown; see tls (supported) | supported: TLS between DIGSI 5 and the device | supported: TLS between DIGSI 5 and the device | not assessed | not assessed | not assessed | unknown | S299 [type not confirmed] pdf-page:8: "TLS-encrypted communication between DIGSI 5 and the SIPROTEC 5 device" (+2 more) | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Overcurrent and feeder protection – SIPROTEC 7SJ85 | currently supported | model as named in the cited document; exact model or order code not established, hardware not established, firmware V8.3 or later | Network access (IEEE 802.1X) (network) | conditional: IEEE 802.1X | unknown | unknown | firmware upgrade: From firmware V8.3. | not assessed | not assessed | unknown | S299 [type not confirmed] pdf-page:22: "IEEE 802.1X based network authentication (from V8.3)" (+1 more) | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Reyrolle 7SR157: Check Synchronising | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | Reyrolle 7SR46: CT-powered overcurrent protection | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |
| Siemens | SIPROTEC 7SY82 | currently supported | not established | No control protocol established from the examined sources | unknown | unknown | unknown | - | - | - | unknown | none | draft (Claude AI draft review; author confirmation pending) |

## Counts by category and lifecycle group

Products, not leads or table rows. Each product is counted once per capability, under its most favourable documented result for a control protocol. Unknown is one result; the four columns after it say why. "Other interface only" means a result exists for a management or network interface but none for a control protocol. A capability reached only through an external gateway is counted apart and is not the device's own. The last column is the denominator. The same results are counted for every lifecycle group.

| Category | Capability | Supported | Conditional | Via external gateway only | Explicitly unsupported | Unknown | of which complete document silent | of which sources conflict | of which other interface only | of which not enough evidence | Not reviewed | Products |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| controller_rtu, currently supported | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 0 | 16 | 0 | 16 |
| controller_rtu, currently supported | tls | 5 | 0 | 0 | 0 | 11 | 0 | 0 | 1 | 10 | 0 | 16 |
| controller_rtu, currently supported | ipsec | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 2 | 14 | 0 | 16 |
| controller_rtu, currently supported | cip_security | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 0 | 16 | 0 | 16 |
| controller_rtu, currently supported | authentication | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 7 | 9 | 0 | 16 |
| controller_rtu, currently supported | encryption | 5 | 0 | 1 | 0 | 10 | 0 | 0 | 1 | 9 | 0 | 16 |
| controller_rtu, currently supported | ssh | 1 | 0 | 0 | 0 | 15 | 0 | 0 | 2 | 13 | 0 | 16 |
| controller_rtu, currently supported | integrity | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 0 | 16 | 0 | 16 |
| controller_rtu, discontinued, support not stated | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 5 | 0 | 5 |
| controller_rtu, discontinued, support not stated | tls | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 1 | 4 | 0 | 5 |
| controller_rtu, discontinued, support not stated | ipsec | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 5 | 0 | 5 |
| controller_rtu, discontinued, support not stated | cip_security | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 5 | 0 | 5 |
| controller_rtu, discontinued, support not stated | authentication | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 2 | 3 | 0 | 5 |
| controller_rtu, discontinued, support not stated | encryption | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 5 | 0 | 5 |
| controller_rtu, discontinued, support not stated | ssh | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 2 | 3 | 0 | 5 |
| controller_rtu, discontinued, support not stated | integrity | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 5 | 0 | 5 |
| meter, currently supported | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 17 | 5 | 0 | 0 | 12 | 0 | 17 |
| meter, currently supported | tls | 0 | 0 | 0 | 0 | 17 | 4 | 0 | 1 | 12 | 0 | 17 |
| meter, currently supported | ipsec | 0 | 0 | 0 | 0 | 17 | 5 | 0 | 0 | 12 | 0 | 17 |
| meter, currently supported | cip_security | 0 | 0 | 0 | 0 | 17 | 5 | 0 | 0 | 12 | 0 | 17 |
| meter, currently supported | authentication | 0 | 0 | 0 | 0 | 17 | 4 | 0 | 1 | 12 | 0 | 17 |
| meter, currently supported | encryption | 0 | 0 | 1 | 0 | 16 | 4 | 0 | 0 | 12 | 0 | 17 |
| meter, currently supported | ssh | 0 | 0 | 0 | 0 | 17 | 5 | 0 | 0 | 12 | 0 | 17 |
| meter, currently supported | integrity | 0 | 0 | 0 | 0 | 17 | 5 | 0 | 0 | 12 | 0 | 17 |
| meter, discontinued, support not stated | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 8 | 1 | 0 | 0 | 7 | 0 | 8 |
| meter, discontinued, support not stated | tls | 0 | 0 | 0 | 0 | 8 | 1 | 0 | 0 | 7 | 0 | 8 |
| meter, discontinued, support not stated | ipsec | 0 | 0 | 0 | 0 | 8 | 1 | 0 | 0 | 7 | 0 | 8 |
| meter, discontinued, support not stated | cip_security | 0 | 0 | 0 | 0 | 8 | 1 | 0 | 0 | 7 | 0 | 8 |
| meter, discontinued, support not stated | authentication | 0 | 0 | 0 | 0 | 8 | 1 | 0 | 0 | 7 | 0 | 8 |
| meter, discontinued, support not stated | encryption | 0 | 0 | 0 | 0 | 8 | 1 | 0 | 0 | 7 | 0 | 8 |
| meter, discontinued, support not stated | ssh | 0 | 0 | 0 | 0 | 8 | 1 | 0 | 0 | 7 | 0 | 8 |
| meter, discontinued, support not stated | integrity | 0 | 0 | 0 | 0 | 8 | 1 | 0 | 0 | 7 | 0 | 8 |
| meter, unknown | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| meter, unknown | tls | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| meter, unknown | ipsec | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| meter, unknown | cip_security | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| meter, unknown | authentication | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| meter, unknown | encryption | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| meter, unknown | ssh | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| meter, unknown | integrity | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| protective_relay, currently supported | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 16 | 1 | 0 | 0 | 15 | 0 | 16 |
| protective_relay, currently supported | tls | 0 | 0 | 0 | 0 | 16 | 1 | 0 | 1 | 14 | 0 | 16 |
| protective_relay, currently supported | ipsec | 0 | 0 | 0 | 0 | 16 | 1 | 0 | 0 | 15 | 0 | 16 |
| protective_relay, currently supported | cip_security | 0 | 0 | 0 | 0 | 16 | 1 | 0 | 0 | 15 | 0 | 16 |
| protective_relay, currently supported | authentication | 1 | 0 | 0 | 0 | 15 | 0 | 0 | 3 | 12 | 0 | 16 |
| protective_relay, currently supported | encryption | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 2 | 14 | 0 | 16 |
| protective_relay, currently supported | ssh | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 1 | 15 | 0 | 16 |
| protective_relay, currently supported | integrity | 0 | 0 | 0 | 0 | 16 | 0 | 0 | 1 | 15 | 0 | 16 |
| protective_relay, discontinued, support not stated | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 10 | 2 | 0 | 0 | 8 | 0 | 10 |
| protective_relay, discontinued, support not stated | tls | 0 | 0 | 0 | 0 | 10 | 2 | 0 | 0 | 8 | 0 | 10 |
| protective_relay, discontinued, support not stated | ipsec | 0 | 0 | 0 | 0 | 10 | 2 | 0 | 0 | 8 | 0 | 10 |
| protective_relay, discontinued, support not stated | cip_security | 0 | 0 | 0 | 0 | 10 | 2 | 0 | 0 | 8 | 0 | 10 |
| protective_relay, discontinued, support not stated | authentication | 0 | 0 | 0 | 0 | 10 | 2 | 0 | 0 | 8 | 0 | 10 |
| protective_relay, discontinued, support not stated | encryption | 0 | 0 | 0 | 0 | 10 | 2 | 0 | 0 | 8 | 0 | 10 |
| protective_relay, discontinued, support not stated | ssh | 0 | 0 | 0 | 0 | 10 | 2 | 0 | 0 | 8 | 0 | 10 |
| protective_relay, discontinued, support not stated | integrity | 0 | 0 | 0 | 0 | 10 | 2 | 0 | 0 | 8 | 0 | 10 |
| protective_relay, unknown | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 3 | 0 | 4 |
| protective_relay, unknown | tls | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 3 | 0 | 4 |
| protective_relay, unknown | ipsec | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 3 | 0 | 4 |
| protective_relay, unknown | cip_security | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 3 | 0 | 4 |
| protective_relay, unknown | authentication | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 3 | 0 | 4 |
| protective_relay, unknown | encryption | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 3 | 0 | 4 |
| protective_relay, unknown | ssh | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 3 | 0 | 4 |
| protective_relay, unknown | integrity | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 3 | 0 | 4 |
| plc, currently supported | dnp3_secure_authentication | 1 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 11 | 0 | 12 |
| plc, currently supported | tls | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 12 | 0 | 12 |
| plc, currently supported | ipsec | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 12 | 0 | 12 |
| plc, currently supported | cip_security | 1 | 1 | 0 | 0 | 10 | 0 | 0 | 0 | 10 | 0 | 12 |
| plc, currently supported | authentication | 1 | 1 | 0 | 0 | 10 | 0 | 0 | 0 | 10 | 0 | 12 |
| plc, currently supported | encryption | 0 | 1 | 0 | 0 | 11 | 0 | 0 | 0 | 11 | 0 | 12 |
| plc, currently supported | ssh | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 12 | 0 | 12 |
| plc, currently supported | integrity | 0 | 1 | 0 | 0 | 11 | 0 | 0 | 0 | 11 | 0 | 12 |
| plc, discontinued, support not stated | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 0 | 8 |
| plc, discontinued, support not stated | tls | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 0 | 8 |
| plc, discontinued, support not stated | ipsec | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 0 | 8 |
| plc, discontinued, support not stated | cip_security | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 0 | 8 |
| plc, discontinued, support not stated | authentication | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 0 | 8 |
| plc, discontinued, support not stated | encryption | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 0 | 8 |
| plc, discontinued, support not stated | ssh | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 0 | 8 |
| plc, discontinued, support not stated | integrity | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 0 | 8 |
| plc, unknown | dnp3_secure_authentication | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 2 |
| plc, unknown | tls | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 2 |
| plc, unknown | ipsec | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 2 |
| plc, unknown | cip_security | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 2 |
| plc, unknown | authentication | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 1 | 0 | 2 |
| plc, unknown | encryption | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 2 |
| plc, unknown | ssh | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 2 |
| plc, unknown | integrity | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 1 | 0 | 2 |

## Capability matrix

S supported, C conditional, G only through an external gateway, X explicitly unsupported, ? unknown (?s a complete document was searched and is silent, ?c sources conflict), - not reviewed. A mark in parentheses is established only for a management or network interface, not for a control protocol.

| Product | Category | dnp3_secure_authentication | tls | ipsec | cip_security | authentication | encryption | ssh | integrity |
|---|---|---|---|---|---|---|---|---|---|
| Multilin C60/C95 | controller_rtu, currently supported | ? | ? | ? | ? | (S) | ? | ? | ? |
| Multilin D20E | controller_rtu, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Multilin G100 Advanced Substation Gateway | controller_rtu, currently supported | ? | S | ? | ? | (S) | S | (S) | ? |
| G500 Advanced Substation Gateway | controller_rtu, currently supported | ? | S | ? | ? | (S) | S | (S) | ? |
| DART-Legacy | controller_rtu, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| Multilin D20MX - Advanced Substation Automation Controller | controller_rtu, discontinued, support not stated | ? | ? | ? | ? | (S) | ? | (S) | ? |
| Multilin D400 Advanced Substation Gateway | controller_rtu, discontinued, support not stated | ? | (S) | ? | ? | (S) | ? | (S) | ? |
| Multilin H500 - Legacy | controller_rtu, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| EPM 2200 Digital Power Meter | meter, currently supported | ?s | ?s | ?s | ?s | (S) | ? | ?s | ?s |
| EPM 6010 Building Automation Power Meter | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| iSTAT i400 Standard Transducers | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| iSTAT M2x2 Communicating Measurement Centre | meter, currently supported | ?s | ?s | ?s | ?s | ?s | ?s | ?s | ?s |
| EPM 4000 Sub-meter (Discontinued) | meter, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| EPM 5300 Power Metering System | meter, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| EPM 7100 Power Quality Meter | meter, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| EPM 9900 Advanced Power Quality Meter | meter, discontinued, support not stated | ?s | ?s | ?s | ?s | ?s | ?s | ?s | ?s |
| BiTRONICS 70 Series - Legacy | meter, unknown | ? | ? | ? | ? | ? | ? | ? | ? |
| IFC Time-overcurrent Relay | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Multilin 339 | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Multilin 850: Advanced Feeder Protection & Bay Controller | protective_relay, currently supported | ? | ? | ? | ? | (S) | ? | ? | ? |
| P64 MiCOM 5th Generation | protective_relay, currently supported | ?s | ?s | ?s | ?s | (S) | (S) | (S) | ? |
| DFP200 Digital Feeder Relay (Discontinued) | protective_relay, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| DLPD Digital Line Protection System | protective_relay, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| KAVS Check Synchronising Relay | protective_relay, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| Multilin A60 - Legacy | protective_relay, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| MBCI, MCRI, MRTP AND MVTW – Legacy | protective_relay, unknown | ? | ? | ? | ? | ? | ? | ? | ? |
| MiCOM Agile P24x - Legacy | protective_relay, unknown | ?s | ?s | ?s | ?s | ?s | ?s | ?s | ?s |
| MiCOM Agile P541 & P542 Line Differential Protection | protective_relay, unknown | ? | ? | ? | ? | ? | ? | ? | ? |
| TCCV Directional Overcurrent Relay | protective_relay, unknown | ? | ? | ? | ? | ? | ? | ? | ? |
| 1408 PowerMonitor 1000 | meter, currently supported | ?s | (S) | ?s | ?s | ?s | ?s | ?s | ?s |
| 1420 PowerMonitor 500 | meter, currently supported | ?s | ?s | ?s | ?s | ?s | ?s | ?s | ?s |
| 1426 PowerMonitor 5000 | meter, currently supported | ?s | ?s | ?s | ?s | ?s | ?s | ?s | ?s |
| CompactLogix 5380 Controllers | plc, currently supported | ? | ? | ? | C | C | C | ? | C |
| ControlLogix 5590 Controllers | plc, currently supported | ? | ? | ? | S | ? | ? | ? | ? |
| LogixEdge Controllers | plc, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Micro870 Controllers | plc, currently supported | S | ? | ? | ? | S | ? | ? | ? |
| CompactLogix 1768 Controllers | plc, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| Micro830 Controllers | plc, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| MicroLogix 1100 Controllers | plc, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| MicroLogix 1200 Controllers | plc, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| CompactLogix 5370 Controllers | plc, unknown | ?s | ?s | ?s | ?s | ?s | ?s | ?s | ?s |
| SLC 500 Controllers | plc, unknown | ?s | ?s | ?s | ?s | ? | ?s | ?s | ? |
| Bulletin 865 Motor-feeder Protection Relays | protective_relay, discontinued, support not stated | ?s | ?s | ?s | ?s | ?s | ?s | ?s | ?s |
| Bulletin 857 Motor-feeder Protection Relays | protective_relay, discontinued, support not stated | ?s | ?s | ?s | ?s | ?s | ?s | ?s | ?s |
| SEL-2431 | controller_rtu, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SEL-3505/3505-3 | controller_rtu, currently supported | ? | (S) | ? | ? | (S) | G | ? | ? |
| SEL-3560 | controller_rtu, currently supported | ? | S | ? | ? | (S) | S | S | ? |
| SEL Real-Time Automation Controller (RTAC) | controller_rtu, currently supported | ? | ? | ? | ? | (S) | ? | ? | ? |
| SEL-734/734T | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SEL-735 | meter, currently supported | ? | ? | ? | ? | ? | G | ? | ? |
| SEL-2664S | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SEL-351A | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SEL-387 | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SEL-421 | protective_relay, currently supported | ? | ? | ? | ? | S | ? | ? | ? |
| Easergy MiCOM C434 | controller_rtu, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SAGE Remote Terminal Units | controller_rtu, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SAITEL Remote Terminal Unit & Controller | controller_rtu, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SCADAPack 500E | controller_rtu, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| PowerLogic ION7550 RTU | controller_rtu, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| PowerLogic EM4200 Series Enercept | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| PowerLogic™ PM3000 Power Meters | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| PowerLogic™ PM5000 Power Meters | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| PowerLogic™ PM8000 Power Quality Meters | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| PM800 series | meter, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| PowerLogic Enercept | meter, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| PowerLogic Energy Meters | meter, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| PowerLogic ION6200 series | meter, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| Modicon M171/M172 Logic Controller | plc, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Modicon M241 Micro PLC | plc, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Modicon M258 Compact PLC for Machine Automation | plc, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Modicon MCM | plc, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Compact PLC | plc, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| Modicon LMC058 / LMC078 | plc, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| Modicon Premium PAC | plc, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| Twido - Programmable Controller | plc, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| MiCOM P59x | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| MiCOM P841 | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Sepam series 80 | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Vamp Arc Protection Relay System | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| MiCOM P22x | protective_relay, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| MiCOM P521 | protective_relay, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| MiCOM P821 | protective_relay, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| Sepam series 20 | protective_relay, discontinued, support not stated | ? | ? | ? | ? | ? | ? | ? | ? |
| Bay controller – SIPROTEC 6MD86 | controller_rtu, currently supported | ? | ? | ? | ? | (S) | (S) | ? | ? |
| SICAM A8000 Series | controller_rtu, currently supported | ? | S | (S) | ? | ? | S | ? | ? |
| Substation automation unit | controller_rtu, currently supported | ? | S | (S) | ? | ? | S | ? | ? |
| MAB-Multipurpose-Automation-Box | controller_rtu, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SENTRON measuring devices for energy transparency | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Power quality recorder - SICAM Q200 | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SENTRON measuring devices for energy transparency | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Digital Transducer - SICAM T | meter, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SIMATIC S7-1200 G2 | plc, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SIMATIC S7-1500 R/H CPUs - High Availability | plc, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SIMATIC S7-1500 Software Controller | plc, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SIMATIC S7-400 | plc, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | protective_relay, currently supported | ? | (S) | ? | ? | (C) | (S) | ? | (S) |
| Reyrolle 7SR157: Check Synchronising | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| Reyrolle 7SR46: CT-powered overcurrent protection | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |
| SIPROTEC 7SY82 | protective_relay, currently supported | ? | ? | ? | ? | ? | ? | ? | ? |

## Default configuration, activation and deployment

Findings with a supported or conditional result, one per capability and interface. "Undocumented" means the documents read do not say whether the capability is on by default; "not assessed" means the reviewer has not looked yet. Neither means disabled.

| Capability | Findings | Default enabled | Default disabled | Default undocumented | Default not assessed | Activation needs stated | Activation: none stated | Activation not assessed |
|---|---|---|---|---|---|---|---|---|
| dnp3_secure_authentication | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| tls | 9 | 0 | 0 | 0 | 9 | 1 | 0 | 8 |
| ipsec | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 2 |
| cip_security | 2 | 0 | 0 | 0 | 2 | 1 | 0 | 1 |
| authentication | 16 | 1 | 0 | 0 | 15 | 1 | 0 | 15 |
| encryption | 11 | 0 | 0 | 0 | 11 | 0 | 0 | 11 |
| ssh | 6 | 0 | 0 | 0 | 6 | 0 | 0 | 6 |
| integrity | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 2 |

Deployment status is unknown for 49 of 49 findings. Vendor documents show what a device can do, not what an operator has enabled, so enabled or disabled in practice is recorded only where evidence from an installation is cited.

## Findings and evidence

Every row that rests on cited sources: each result, and each unknown recorded because a complete document is silent or sources conflict. Quotes are verbatim from the cited location of the retained source.

### Multilin C60/C95: authentication (supported)

- Interface: User access to the relay (AAA server) (management)
- Protocol: RADIUS
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:166
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:166: "Enables integration with centrally managed authentication and accounting of all user activities"
- Source: S1 [type not confirmed] https://www.gevernova.com/electrification/automation/protection-control-metering/controllers/multilin-c60c95
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin G100 Advanced Substation Gateway: tls (supported)

- Interface: Master station link (DNP3/TCP, Modbus/TCP, IEC 104) (control protocol)
- Protocol: DNP3/TCP, Modbus/TCP and IEC 60870-5-104 through a TLS tunnel
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:1
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:1: "Secure tunneling from master station via TLS for DNP3/TCP, Modbus/TCP and IEC 104"
- Source: S14 [type not confirmed] https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G100-Brochure-EN-33196-Hybrid-202504-R002.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin G100 Advanced Substation Gateway: authentication (supported)

- Interface: User access to the gateway (management)
- Protocol: Local accounts, LDAP, TACACS+
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:7
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:7: "Local and Remote Authentication modes are supported to ensure that only authenticated and authorized users gain access the system"
- Source: S14 [type not confirmed] https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G100-Brochure-EN-33196-Hybrid-202504-R002.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin G100 Advanced Substation Gateway: encryption (supported)

- Interface: Master station link (DNP3/TCP, Modbus/TCP, IEC 104) (control protocol)
- Protocol: TLS tunnel for the SCADA protocols
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:1
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:1: "Secure tunneling from master station via TLS for DNP3/TCP, Modbus/TCP and IEC 104"
- Source: S14 [type not confirmed] https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G100-Brochure-EN-33196-Hybrid-202504-R002.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin G100 Advanced Substation Gateway: ssh (supported)

- Interface: Remote access to substation devices through the gateway (management)
- Protocol: SSH or TLS for remote access
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:7
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:7: "Remote access can be secured with TLS or SSH."
- Source: S14 [type not confirmed] https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G100-Brochure-EN-33196-Hybrid-202504-R002.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### G500 Advanced Substation Gateway: tls (supported)

- Interface: Master station link (DNP3/TCP, Modbus/TCP, IEC 104) (control protocol)
- Protocol: DNP3/TCP, Modbus/TCP and IEC 60870-5-104 through a TLS tunnel
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:1
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:1: "Secure tunneling from master station via TLS for DNP3/TCP, Modbus/TCP and IEC 104"
- Source: S20 [type not confirmed] https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G500-Advanced-Substation-Gateway-Brochure-EN-35437-Hybrid-202504-R002.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### G500 Advanced Substation Gateway: authentication (supported)

- Interface: User access to the gateway (management)
- Protocol: Local accounts, LDAP, TACACS+
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:9
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:9: "Local and Remote Authentication modes are supported to ensure that only authenticated and authorized users gain access the system"
- Source: S20 [type not confirmed] https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G500-Advanced-Substation-Gateway-Brochure-EN-35437-Hybrid-202504-R002.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### G500 Advanced Substation Gateway: encryption (supported)

- Interface: Master station link (DNP3/TCP, Modbus/TCP, IEC 104) (control protocol)
- Protocol: TLS tunnel for the SCADA protocols
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:1
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:1: "Secure tunneling from master station via TLS for DNP3/TCP, Modbus/TCP and IEC 104"
- Source: S20 [type not confirmed] https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G500-Advanced-Substation-Gateway-Brochure-EN-35437-Hybrid-202504-R002.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### G500 Advanced Substation Gateway: ssh (supported)

- Interface: Remote access to substation devices through the gateway (management)
- Protocol: SSH or TLS for remote access
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:9
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:9: "Remote access can be secured with TLS or SSH."
- Source: S20 [type not confirmed] https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G500-Advanced-Substation-Gateway-Brochure-EN-35437-Hybrid-202504-R002.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin D20MX - Advanced Substation Automation Controller: authentication (supported)

- Interface: User access to the controller (management)
- Protocol: RADIUS, role based access control
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:70
- Support basis: built in
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:70: "Built-in cyber security features, such as Remote Authentication Dial-In User Service (RADIUS), Role Based Access Control (RBAC), and user activity logging"
- Source: S24 [type not confirmed] https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d20mx-substation-controller-legacy
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin D20MX - Advanced Substation Automation Controller: ssh (supported)

- Interface: Firmware and configuration file transfer (management)
- Protocol: SSH and SFTP file transfer
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:1
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:1: "SSH and SFTP provide secure firmware and configuration file transfer"
- Source: S31 [type not confirmed] https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-D20MX-Brochure-EN-12711G-Hybrid-202504-R001.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin D400 Advanced Substation Gateway: tls (supported)

- Interface: Pass-through and terminal server access to substation devices (management)
- Protocol: SSH or TLS for pass-through access
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:17
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:17: "Secure pass through / terminal server, with support for SSH and TLS, allowing personnel to access substation devices locally or remotely"
- Source: S33 [type not confirmed] https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d400-legacy
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin D400 Advanced Substation Gateway: authentication (supported)

- Interface: User access to the gateway (management)
- Protocol: LDAP, TACACS+, RADIUS or internal database
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:14
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:14: "Advanced security features including centralized user authentication (LDAP & TACACS+), access control, and auditing"
- Source: S33 [type not confirmed] https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d400-legacy
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin D400 Advanced Substation Gateway: ssh (supported)

- Interface: Pass-through and terminal server access to substation devices (management)
- Protocol: SSH or TLS for pass-through access
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:17
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:17: "Secure pass through / terminal server, with support for SSH and TLS, allowing personnel to access substation devices locally or remotely"
- Source: S33 [type not confirmed] https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d400-legacy
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 2200 Digital Power Meter: dnp3_secure_authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 2200 instruction manual
- Searched: S52 [manual] searched in full, 123 PDF pages: no lead for dnp3_secure_authentication
- Source: S52 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm2200-a7-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 2200 Digital Power Meter: tls (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 2200 instruction manual
- Searched: S52 [manual] searched in full, 123 PDF pages: no lead for tls
- Source: S52 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm2200-a7-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 2200 Digital Power Meter: ipsec (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 2200 instruction manual
- Searched: S52 [manual] searched in full, 123 PDF pages: no lead for ipsec
- Source: S52 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm2200-a7-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 2200 Digital Power Meter: cip_security (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 2200 instruction manual
- Searched: S52 [manual] searched in full, 123 PDF pages: no lead for cip_security
- Source: S52 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm2200-a7-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 2200 Digital Power Meter: authentication (supported)

- Interface: Ethernet card web configuration page (management)
- Protocol: User name and password
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:91
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:91: "You will see a User Authentication screen."
- Source: S52 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm2200-a7-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 2200 Digital Power Meter: ssh (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 2200 instruction manual
- Searched: S52 [manual] searched in full, 123 PDF pages: no lead for ssh
- Source: S52 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm2200-a7-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 2200 Digital Power Meter: integrity (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 2200 instruction manual
- Searched: S52 [manual] searched in full, 123 PDF pages: no lead for integrity
- Source: S52 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm2200-a7-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### iSTAT M2x2 Communicating Measurement Centre: dnp3_secure_authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the iSTAT M2x2 manual
- Searched: S75 [manual] searched in full, 72 PDF pages: no lead for dnp3_secure_authentication
- Source: S75 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/M2x2-EN-M-F-new-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### iSTAT M2x2 Communicating Measurement Centre: tls (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the iSTAT M2x2 manual
- Searched: S75 [manual] searched in full, 72 PDF pages: no lead for tls
- Source: S75 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/M2x2-EN-M-F-new-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### iSTAT M2x2 Communicating Measurement Centre: ipsec (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the iSTAT M2x2 manual
- Searched: S75 [manual] searched in full, 72 PDF pages: no lead for ipsec
- Source: S75 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/M2x2-EN-M-F-new-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### iSTAT M2x2 Communicating Measurement Centre: cip_security (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the iSTAT M2x2 manual
- Searched: S75 [manual] searched in full, 72 PDF pages: no lead for cip_security
- Source: S75 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/M2x2-EN-M-F-new-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### iSTAT M2x2 Communicating Measurement Centre: authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the iSTAT M2x2 manual
- Searched: S75 [manual] searched in full, 72 PDF pages: no lead for authentication
- Source: S75 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/M2x2-EN-M-F-new-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### iSTAT M2x2 Communicating Measurement Centre: encryption (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the iSTAT M2x2 manual
- Searched: S75 [manual] searched in full, 72 PDF pages: no lead for encryption
- Source: S75 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/M2x2-EN-M-F-new-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### iSTAT M2x2 Communicating Measurement Centre: ssh (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the iSTAT M2x2 manual
- Searched: S75 [manual] searched in full, 72 PDF pages: no lead for ssh
- Source: S75 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/M2x2-EN-M-F-new-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### iSTAT M2x2 Communicating Measurement Centre: integrity (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the iSTAT M2x2 manual
- Searched: S75 [manual] searched in full, 72 PDF pages: no lead for integrity
- Source: S75 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/M2x2-EN-M-F-new-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 9900 Advanced Power Quality Meter: dnp3_secure_authentication (unknown: complete document silent)

- Interface: DNP3 as described in the EPM 9000 series DNP guide (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 9000 series DNP guide
- Searched: S96 [manual] searched in full, 272 PDF pages: no lead for dnp3_secure_authentication
- Source: S96 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 9900 Advanced Power Quality Meter: tls (unknown: complete document silent)

- Interface: DNP3 as described in the EPM 9000 series DNP guide (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 9000 series DNP guide
- Searched: S96 [manual] searched in full, 272 PDF pages: no lead for tls
- Source: S96 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 9900 Advanced Power Quality Meter: ipsec (unknown: complete document silent)

- Interface: DNP3 as described in the EPM 9000 series DNP guide (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 9000 series DNP guide
- Searched: S96 [manual] searched in full, 272 PDF pages: no lead for ipsec
- Source: S96 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 9900 Advanced Power Quality Meter: cip_security (unknown: complete document silent)

- Interface: DNP3 as described in the EPM 9000 series DNP guide (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 9000 series DNP guide
- Searched: S96 [manual] searched in full, 272 PDF pages: no lead for cip_security
- Source: S96 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 9900 Advanced Power Quality Meter: authentication (unknown: complete document silent)

- Interface: DNP3 as described in the EPM 9000 series DNP guide (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 9000 series DNP guide
- Searched: S96 [manual] searched in full, 272 PDF pages: no lead for authentication
- Source: S96 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 9900 Advanced Power Quality Meter: encryption (unknown: complete document silent)

- Interface: DNP3 as described in the EPM 9000 series DNP guide (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 9000 series DNP guide
- Searched: S96 [manual] searched in full, 272 PDF pages: no lead for encryption
- Source: S96 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 9900 Advanced Power Quality Meter: ssh (unknown: complete document silent)

- Interface: DNP3 as described in the EPM 9000 series DNP guide (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 9000 series DNP guide
- Searched: S96 [manual] searched in full, 272 PDF pages: no lead for ssh
- Source: S96 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### EPM 9900 Advanced Power Quality Meter: integrity (unknown: complete document silent)

- Interface: DNP3 as described in the EPM 9000 series DNP guide (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by the EPM 9000 series DNP guide
- Searched: S96 [manual] searched in full, 272 PDF pages: no lead for integrity
- Source: S96 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Multilin 850: Advanced Feeder Protection & Bay Controller: authentication (supported)

- Interface: User access to the relay (AAA server) (management)
- Protocol: RADIUS
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:57
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:57: "High-end cyber security such as AAA, Radius, RBAC and Syslog, enabling NERC CIP requirements."
- Source: S113 [type not confirmed] https://www.gevernova.com/electrification/automation/protection-control-metering/feeder-protection/multilin-850
- Review status: draft (Claude AI draft review; author confirmation pending)

### P64 MiCOM 5th Generation: dnp3_secure_authentication (unknown: complete document silent)

- Interface: Substation and SCADA protocols of the relay as described in its technical manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P64-TM-EN-1
- Searched: S127 [manual] searched in full, 672 PDF pages: no lead for dnp3_secure_authentication
- Source: S127 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### P64 MiCOM 5th Generation: tls (unknown: complete document silent)

- Interface: Substation and SCADA protocols of the relay as described in its technical manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P64-TM-EN-1
- Searched: S127 [manual] searched in full, 672 PDF pages: no lead for tls
- Source: S127 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### P64 MiCOM 5th Generation: ipsec (unknown: complete document silent)

- Interface: Substation and SCADA protocols of the relay as described in its technical manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P64-TM-EN-1
- Searched: S127 [manual] searched in full, 672 PDF pages: no lead for ipsec
- Source: S127 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### P64 MiCOM 5th Generation: cip_security (unknown: complete document silent)

- Interface: Substation and SCADA protocols of the relay as described in its technical manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P64-TM-EN-1
- Searched: S127 [manual] searched in full, 672 PDF pages: no lead for cip_security
- Source: S127 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### P64 MiCOM 5th Generation: authentication (supported)

- Interface: User access to the IED (front panel, S1 Agile, network ports) (management)
- Protocol: Device and RADIUS server authentication
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: as covered by technical manual P64-TM-EN-1
- Implementation: as described in the cited document
- Location: pdf-page:419
- Support basis: not assessed
- Default configuration: enabled
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:419: "The IED supports Bypass (no authentication), Device authentication and Server authentication."
- Evidence on default, pdf-page:419: "Server + Device (This is the default setting for IEDs with NIC (Ethernet Board) fitted)"
- Source: S127 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### P64 MiCOM 5th Generation: encryption (supported)

- Interface: S1 Agile engineering tool connection (management)
- Protocol: Encrypted passwords in messages between S1 Agile and the IED
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: as covered by technical manual P64-TM-EN-1
- Implementation: as described in the cited document
- Location: pdf-page:415
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:415: "Encryption of passwords - stored within the IED, in network messages between the MiCOM S1 Agile software and the IED"
- Source: S127 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### P64 MiCOM 5th Generation: ssh (supported)

- Interface: S1 Agile engineering tool connection (management)
- Protocol: SSH
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: as covered by technical manual P64-TM-EN-1
- Implementation: as described in the cited document
- Location: pdf-page:433
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:433: "SSH (for S1 Agile) Yes - only one port at a time"
- Source: S127 [manual] https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### MiCOM Agile P24x - Legacy: dnp3_secure_authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P24x-TM-EN-J82
- Searched: S154 [manual] searched in full, 556 PDF pages: no lead for dnp3_secure_authentication
- Source: S154 [manual] https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### MiCOM Agile P24x - Legacy: tls (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P24x-TM-EN-J82
- Searched: S154 [manual] searched in full, 556 PDF pages: no lead for tls
- Source: S154 [manual] https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### MiCOM Agile P24x - Legacy: ipsec (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P24x-TM-EN-J82
- Searched: S154 [manual] searched in full, 556 PDF pages: no lead for ipsec
- Source: S154 [manual] https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### MiCOM Agile P24x - Legacy: cip_security (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P24x-TM-EN-J82
- Searched: S154 [manual] searched in full, 556 PDF pages: no lead for cip_security
- Source: S154 [manual] https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### MiCOM Agile P24x - Legacy: authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P24x-TM-EN-J82
- Searched: S154 [manual] searched in full, 556 PDF pages: no lead for authentication
- Source: S154 [manual] https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### MiCOM Agile P24x - Legacy: encryption (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P24x-TM-EN-J82
- Searched: S154 [manual] searched in full, 556 PDF pages: no lead for encryption
- Source: S154 [manual] https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### MiCOM Agile P24x - Legacy: ssh (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P24x-TM-EN-J82
- Searched: S154 [manual] searched in full, 556 PDF pages: no lead for ssh
- Source: S154 [manual] https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### MiCOM Agile P24x - Legacy: integrity (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by technical manual P24x-TM-EN-J82
- Searched: S154 [manual] searched in full, 556 PDF pages: no lead for integrity
- Source: S154 [manual] https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1408 PowerMonitor 1000: dnp3_secure_authentication (unknown: complete document silent)

- Interface: Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1408-UM002
- Searched: S166 [manual] searched in full, 216 PDF pages: no lead for dnp3_secure_authentication
- Source: S166 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1408-um002_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1408 PowerMonitor 1000: tls (supported)

- Interface: Web page and FTP access to the unit (management)
- Protocol: HTTPS and FTPS, SSL 3.0 (TLS 1.0)
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:55
- Support basis: not assessed
- Default configuration: not assessed
- Activation: configuration: HTTPS Enable and FTPS Enable settings are set to 1.
- Deployment: unknown
- Evidence, pdf-page:55: "you must use a browser capable of supporting SSL"
- Evidence on activation, pdf-page:55: "0 = HTTPS disable. 1 = HTTPS enable."
- Source: S166 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1408-um002_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1408 PowerMonitor 1000: ipsec (unknown: complete document silent)

- Interface: Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1408-UM002
- Searched: S166 [manual] searched in full, 216 PDF pages: no lead for ipsec
- Source: S166 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1408-um002_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1408 PowerMonitor 1000: cip_security (unknown: complete document silent)

- Interface: Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1408-UM002
- Searched: S166 [manual] searched in full, 216 PDF pages: no lead for cip_security
- Source: S166 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1408-um002_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1408 PowerMonitor 1000: authentication (unknown: complete document silent)

- Interface: Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1408-UM002
- Searched: S166 [manual] searched in full, 216 PDF pages: no lead for authentication
- Source: S166 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1408-um002_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1408 PowerMonitor 1000: encryption (unknown: complete document silent)

- Interface: Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1408-UM002
- Searched: S166 [manual] searched in full, 216 PDF pages: no lead for encryption
- Source: S166 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1408-um002_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1408 PowerMonitor 1000: ssh (unknown: complete document silent)

- Interface: Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1408-UM002
- Searched: S166 [manual] searched in full, 216 PDF pages: no lead for ssh
- Source: S166 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1408-um002_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1408 PowerMonitor 1000: integrity (unknown: complete document silent)

- Interface: Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1408-UM002
- Searched: S166 [manual] searched in full, 216 PDF pages: no lead for integrity
- Source: S166 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1408-um002_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1420 PowerMonitor 500: dnp3_secure_authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1420-UM001
- Searched: S172 [manual] searched in full, 108 PDF pages: no lead for dnp3_secure_authentication
- Source: S172 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1420-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1420 PowerMonitor 500: tls (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1420-UM001
- Searched: S172 [manual] searched in full, 108 PDF pages: no lead for tls
- Source: S172 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1420-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1420 PowerMonitor 500: ipsec (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1420-UM001
- Searched: S172 [manual] searched in full, 108 PDF pages: no lead for ipsec
- Source: S172 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1420-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1420 PowerMonitor 500: cip_security (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1420-UM001
- Searched: S172 [manual] searched in full, 108 PDF pages: no lead for cip_security
- Source: S172 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1420-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1420 PowerMonitor 500: authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1420-UM001
- Searched: S172 [manual] searched in full, 108 PDF pages: no lead for authentication
- Source: S172 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1420-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1420 PowerMonitor 500: encryption (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1420-UM001
- Searched: S172 [manual] searched in full, 108 PDF pages: no lead for encryption
- Source: S172 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1420-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1420 PowerMonitor 500: ssh (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1420-UM001
- Searched: S172 [manual] searched in full, 108 PDF pages: no lead for ssh
- Source: S172 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1420-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1420 PowerMonitor 500: integrity (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1420-UM001
- Searched: S172 [manual] searched in full, 108 PDF pages: no lead for integrity
- Source: S172 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1420-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1426 PowerMonitor 5000: dnp3_secure_authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1426-UM001
- Searched: S178 [manual] searched in full, 406 PDF pages: no lead for dnp3_secure_authentication
- Source: S178 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1426-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1426 PowerMonitor 5000: tls (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1426-UM001
- Searched: S178 [manual] searched in full, 406 PDF pages: no lead for tls
- Source: S178 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1426-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1426 PowerMonitor 5000: ipsec (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1426-UM001
- Searched: S178 [manual] searched in full, 406 PDF pages: no lead for ipsec
- Source: S178 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1426-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1426 PowerMonitor 5000: cip_security (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1426-UM001
- Searched: S178 [manual] searched in full, 406 PDF pages: no lead for cip_security
- Source: S178 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1426-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1426 PowerMonitor 5000: authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1426-UM001
- Searched: S178 [manual] searched in full, 406 PDF pages: no lead for authentication
- Source: S178 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1426-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1426 PowerMonitor 5000: encryption (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1426-UM001
- Searched: S178 [manual] searched in full, 406 PDF pages: no lead for encryption
- Source: S178 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1426-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1426 PowerMonitor 5000: ssh (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1426-UM001
- Searched: S178 [manual] searched in full, 406 PDF pages: no lead for ssh
- Source: S178 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1426-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### 1426 PowerMonitor 5000: integrity (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1426-UM001
- Searched: S178 [manual] searched in full, 406 PDF pages: no lead for integrity
- Source: S178 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1426-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5380 Controllers: cip_security (conditional)

- Interface: EtherNet/IP (CIP) communication (control protocol)
- Protocol: CIP Security on EtherNet/IP
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: 34.011 or later
- Implementation: as described in the cited document
- Conditions: Controller firmware revision 34.011 or later, Studio 5000 Logix Designer version 34 or later.
- Location: pdf-page:28
- Support basis: firmware upgrade
- Default configuration: not assessed
- Activation: configuration, other: A security policy (zones and conduits) is defined and deployed with FactoryTalk Policy Manager.
- Deployment: unknown
- Evidence, pdf-page:28: "controllers also support CIP Security with firmware revision 34.011 or later"
- Evidence on conditions, pdf-page:28: "controllers also support CIP Security with firmware revision 34.011 or later"
- Evidence on activation, pdf-page:189: "Use FactoryTalk Policy Manager software to define zones and conduits."
- Source: S183 [type not confirmed] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/5069-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5380 Controllers: authentication (conditional)

- Interface: EtherNet/IP (CIP) communication (control protocol)
- Protocol: CIP Security on EtherNet/IP
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: 34.011 or later
- Implementation: as described in the cited document
- Conditions: Controller firmware revision 34.011 or later, Studio 5000 Logix Designer version 34 or later.
- Location: pdf-page:28
- Support basis: firmware upgrade
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:28: "CIP Security lets CIP-connected devices authenticate each other before transmitting and receiving data."
- Evidence on conditions, pdf-page:28: "controllers also support CIP Security with firmware revision 34.011 or later"
- Source: S183 [type not confirmed] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/5069-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5380 Controllers: encryption (conditional)

- Interface: EtherNet/IP (CIP) communication (control protocol)
- Protocol: CIP Security on EtherNet/IP
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: 34.011 or later
- Implementation: as described in the cited document
- Conditions: Controller firmware revision 34.011 or later, Studio 5000 Logix Designer version 34 or later.
- Location: html-block:43
- Support basis: firmware upgrade
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:43: "through validation of device authentication, data integrity and data confidentiality"
- Evidence on conditions, pdf-page:28: "controllers also support CIP Security with firmware revision 34.011 or later"
- Source: S182 [type not confirmed] https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/compactlogix-5380-controllers.html
- Source: S183 [type not confirmed] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/5069-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5380 Controllers: integrity (conditional)

- Interface: EtherNet/IP (CIP) communication (control protocol)
- Protocol: CIP Security on EtherNet/IP
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: 34.011 or later
- Implementation: as described in the cited document
- Conditions: Controller firmware revision 34.011 or later, Studio 5000 Logix Designer version 34 or later.
- Location: pdf-page:28
- Support basis: firmware upgrade
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:28: "Data Integrity and Authentication"
- Evidence on conditions, pdf-page:28: "controllers also support CIP Security with firmware revision 34.011 or later"
- Source: S183 [type not confirmed] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/5069-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### ControlLogix 5590 Controllers: cip_security (supported)

- Interface: EtherNet/IP (CIP) communication (control protocol)
- Protocol: CIP Security on EtherNet/IP
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:5
- Support basis: built in
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:5: "Integrated CIP Security, secure boot and device-level protection"
- Source: S189 [type not confirmed] https://literature.rockwellautomation.com/idc/groups/literature/documents/pp/1756-pp001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Micro870 Controllers: dnp3_secure_authentication (supported)

- Interface: DNP3 outstation (slave) communication (control protocol)
- Protocol: DNP3 Secure Authentication version 5
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:61
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:61: "Provide enhanced protocol authentication in DNP3 with Secure Authentication version 5 (SAv5)"
- Source: S192 [type not confirmed] https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/micro870-controllers.html
- Review status: draft (Claude AI draft review; author confirmation pending)

### Micro870 Controllers: authentication (supported)

- Interface: DNP3 outstation (slave) communication (control protocol)
- Protocol: DNP3 Secure Authentication version 5
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:61
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:61: "Provide enhanced protocol authentication in DNP3 with Secure Authentication version 5 (SAv5)"
- Source: S192 [type not confirmed] https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/micro870-controllers.html
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5370 Controllers: dnp3_secure_authentication (unknown: complete document silent)

- Interface: EtherNet/IP and serial communication as described in the user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1769-UM021
- Searched: S202 [manual] searched in full, 272 PDF pages: no lead for dnp3_secure_authentication
- Source: S202 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5370 Controllers: tls (unknown: complete document silent)

- Interface: EtherNet/IP and serial communication as described in the user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1769-UM021
- Searched: S202 [manual] searched in full, 272 PDF pages: no lead for tls
- Source: S202 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5370 Controllers: ipsec (unknown: complete document silent)

- Interface: EtherNet/IP and serial communication as described in the user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1769-UM021
- Searched: S202 [manual] searched in full, 272 PDF pages: no lead for ipsec
- Source: S202 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5370 Controllers: cip_security (unknown: complete document silent)

- Interface: EtherNet/IP and serial communication as described in the user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1769-UM021
- Searched: S202 [manual] searched in full, 272 PDF pages: no lead for cip_security
- Source: S202 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5370 Controllers: authentication (unknown: complete document silent)

- Interface: EtherNet/IP and serial communication as described in the user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1769-UM021
- Searched: S202 [manual] searched in full, 272 PDF pages: no lead for authentication
- Source: S202 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5370 Controllers: encryption (unknown: complete document silent)

- Interface: EtherNet/IP and serial communication as described in the user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1769-UM021
- Searched: S202 [manual] searched in full, 272 PDF pages: no lead for encryption
- Source: S202 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5370 Controllers: ssh (unknown: complete document silent)

- Interface: EtherNet/IP and serial communication as described in the user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1769-UM021
- Searched: S202 [manual] searched in full, 272 PDF pages: no lead for ssh
- Source: S202 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### CompactLogix 5370 Controllers: integrity (unknown: complete document silent)

- Interface: EtherNet/IP and serial communication as described in the user manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 1769-UM021
- Searched: S202 [manual] searched in full, 272 PDF pages: no lead for integrity
- Source: S202 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### SLC 500 Controllers: dnp3_secure_authentication (unknown: complete document silent)

- Interface: DF1, DH-485, DH+ and Ethernet communication as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 1747-UM011, 1747-UM009 and 1747-RM001
- Searched: S207 [manual] searched in full, 296 PDF pages: no lead for dnp3_secure_authentication; S208 [manual] searched in full, 223 PDF pages: no lead for dnp3_secure_authentication; S209 [manual] searched in full, 694 PDF pages: no lead for dnp3_secure_authentication
- Source: S207 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um011_-en-p.pdf
- Source: S208 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um009_-en-p.pdf
- Source: S209 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/1747-rm001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### SLC 500 Controllers: tls (unknown: complete document silent)

- Interface: DF1, DH-485, DH+ and Ethernet communication as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 1747-UM011, 1747-UM009 and 1747-RM001
- Searched: S207 [manual] searched in full, 296 PDF pages: no lead for tls; S208 [manual] searched in full, 223 PDF pages: no lead for tls; S209 [manual] searched in full, 694 PDF pages: no lead for tls
- Source: S207 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um011_-en-p.pdf
- Source: S208 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um009_-en-p.pdf
- Source: S209 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/1747-rm001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### SLC 500 Controllers: ipsec (unknown: complete document silent)

- Interface: DF1, DH-485, DH+ and Ethernet communication as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 1747-UM011, 1747-UM009 and 1747-RM001
- Searched: S207 [manual] searched in full, 296 PDF pages: no lead for ipsec; S208 [manual] searched in full, 223 PDF pages: no lead for ipsec; S209 [manual] searched in full, 694 PDF pages: no lead for ipsec
- Source: S207 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um011_-en-p.pdf
- Source: S208 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um009_-en-p.pdf
- Source: S209 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/1747-rm001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### SLC 500 Controllers: cip_security (unknown: complete document silent)

- Interface: DF1, DH-485, DH+ and Ethernet communication as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 1747-UM011, 1747-UM009 and 1747-RM001
- Searched: S207 [manual] searched in full, 296 PDF pages: no lead for cip_security; S208 [manual] searched in full, 223 PDF pages: no lead for cip_security; S209 [manual] searched in full, 694 PDF pages: no lead for cip_security
- Source: S207 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um011_-en-p.pdf
- Source: S208 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um009_-en-p.pdf
- Source: S209 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/1747-rm001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### SLC 500 Controllers: encryption (unknown: complete document silent)

- Interface: DF1, DH-485, DH+ and Ethernet communication as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 1747-UM011, 1747-UM009 and 1747-RM001
- Searched: S207 [manual] searched in full, 296 PDF pages: no lead for encryption; S208 [manual] searched in full, 223 PDF pages: no lead for encryption; S209 [manual] searched in full, 694 PDF pages: no lead for encryption
- Source: S207 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um011_-en-p.pdf
- Source: S208 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um009_-en-p.pdf
- Source: S209 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/1747-rm001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### SLC 500 Controllers: ssh (unknown: complete document silent)

- Interface: DF1, DH-485, DH+ and Ethernet communication as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 1747-UM011, 1747-UM009 and 1747-RM001
- Searched: S207 [manual] searched in full, 296 PDF pages: no lead for ssh; S208 [manual] searched in full, 223 PDF pages: no lead for ssh; S209 [manual] searched in full, 694 PDF pages: no lead for ssh
- Source: S207 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um011_-en-p.pdf
- Source: S208 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um009_-en-p.pdf
- Source: S209 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/1747-rm001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 865 Motor-feeder Protection Relays: dnp3_secure_authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 865-UM001
- Searched: S214 [manual] searched in full, 296 PDF pages: no lead for dnp3_secure_authentication
- Source: S214 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 865 Motor-feeder Protection Relays: tls (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 865-UM001
- Searched: S214 [manual] searched in full, 296 PDF pages: no lead for tls
- Source: S214 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 865 Motor-feeder Protection Relays: ipsec (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 865-UM001
- Searched: S214 [manual] searched in full, 296 PDF pages: no lead for ipsec
- Source: S214 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 865 Motor-feeder Protection Relays: cip_security (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 865-UM001
- Searched: S214 [manual] searched in full, 296 PDF pages: no lead for cip_security
- Source: S214 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 865 Motor-feeder Protection Relays: authentication (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 865-UM001
- Searched: S214 [manual] searched in full, 296 PDF pages: no lead for authentication
- Source: S214 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 865 Motor-feeder Protection Relays: encryption (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 865-UM001
- Searched: S214 [manual] searched in full, 296 PDF pages: no lead for encryption
- Source: S214 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 865 Motor-feeder Protection Relays: ssh (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 865-UM001
- Searched: S214 [manual] searched in full, 296 PDF pages: no lead for ssh
- Source: S214 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 865 Motor-feeder Protection Relays: integrity (unknown: complete document silent)

- Interface: Communication protocols of the device as described in its manual (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by user manual 865-UM001
- Searched: S214 [manual] searched in full, 296 PDF pages: no lead for integrity
- Source: S214 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 857 Motor-feeder Protection Relays: dnp3_secure_authentication (unknown: complete document silent)

- Interface: IEC 61850, EtherNet/IP and serial protocols as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 857-UM001, 857-UM004 and 857-UM005
- Searched: S219 [manual] searched in full, 504 PDF pages: no lead for dnp3_secure_authentication; S216 [manual] searched in full, 104 PDF pages: no lead for dnp3_secure_authentication; S220 [manual] searched in full, 70 PDF pages: no lead for dnp3_secure_authentication
- Source: S219 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf
- Source: S216 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um004_-en-p.pdf
- Source: S220 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um005_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 857 Motor-feeder Protection Relays: tls (unknown: complete document silent)

- Interface: IEC 61850, EtherNet/IP and serial protocols as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 857-UM001, 857-UM004 and 857-UM005
- Searched: S219 [manual] searched in full, 504 PDF pages: no lead for tls; S216 [manual] searched in full, 104 PDF pages: no lead for tls; S220 [manual] searched in full, 70 PDF pages: no lead for tls
- Source: S219 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf
- Source: S216 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um004_-en-p.pdf
- Source: S220 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um005_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 857 Motor-feeder Protection Relays: ipsec (unknown: complete document silent)

- Interface: IEC 61850, EtherNet/IP and serial protocols as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 857-UM001, 857-UM004 and 857-UM005
- Searched: S219 [manual] searched in full, 504 PDF pages: no lead for ipsec; S216 [manual] searched in full, 104 PDF pages: no lead for ipsec; S220 [manual] searched in full, 70 PDF pages: no lead for ipsec
- Source: S219 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf
- Source: S216 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um004_-en-p.pdf
- Source: S220 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um005_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 857 Motor-feeder Protection Relays: cip_security (unknown: complete document silent)

- Interface: IEC 61850, EtherNet/IP and serial protocols as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 857-UM001, 857-UM004 and 857-UM005
- Searched: S219 [manual] searched in full, 504 PDF pages: no lead for cip_security; S216 [manual] searched in full, 104 PDF pages: no lead for cip_security; S220 [manual] searched in full, 70 PDF pages: no lead for cip_security
- Source: S219 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf
- Source: S216 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um004_-en-p.pdf
- Source: S220 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um005_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 857 Motor-feeder Protection Relays: authentication (unknown: complete document silent)

- Interface: IEC 61850, EtherNet/IP and serial protocols as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 857-UM001, 857-UM004 and 857-UM005
- Searched: S219 [manual] searched in full, 504 PDF pages: no lead for authentication; S216 [manual] searched in full, 104 PDF pages: no lead for authentication; S220 [manual] searched in full, 70 PDF pages: no lead for authentication
- Source: S219 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf
- Source: S216 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um004_-en-p.pdf
- Source: S220 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um005_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 857 Motor-feeder Protection Relays: encryption (unknown: complete document silent)

- Interface: IEC 61850, EtherNet/IP and serial protocols as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 857-UM001, 857-UM004 and 857-UM005
- Searched: S219 [manual] searched in full, 504 PDF pages: no lead for encryption; S216 [manual] searched in full, 104 PDF pages: no lead for encryption; S220 [manual] searched in full, 70 PDF pages: no lead for encryption
- Source: S219 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf
- Source: S216 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um004_-en-p.pdf
- Source: S220 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um005_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 857 Motor-feeder Protection Relays: ssh (unknown: complete document silent)

- Interface: IEC 61850, EtherNet/IP and serial protocols as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 857-UM001, 857-UM004 and 857-UM005
- Searched: S219 [manual] searched in full, 504 PDF pages: no lead for ssh; S216 [manual] searched in full, 104 PDF pages: no lead for ssh; S220 [manual] searched in full, 70 PDF pages: no lead for ssh
- Source: S219 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf
- Source: S216 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um004_-en-p.pdf
- Source: S220 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um005_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bulletin 857 Motor-feeder Protection Relays: integrity (unknown: complete document silent)

- Interface: IEC 61850, EtherNet/IP and serial protocols as described in the manuals (control protocol)
- Model scope: as covered by the cited manual
- Hardware revision: not established
- Firmware: as covered by 857-UM001, 857-UM004 and 857-UM005
- Searched: S219 [manual] searched in full, 504 PDF pages: no lead for integrity; S216 [manual] searched in full, 104 PDF pages: no lead for integrity; S220 [manual] searched in full, 70 PDF pages: no lead for integrity
- Source: S219 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf
- Source: S216 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um004_-en-p.pdf
- Source: S220 [manual] https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um005_-en-p.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL-3505/3505-3: tls (supported)

- Interface: Encrypted communication listed under security features (interface not specified) (management)
- Protocol: SSL/TLS, SSH, HTTPS
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:10
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:10: "Encrypted Communication: SSL/TLS, SSH"
- Source: S223 [type not confirmed] https://selinc.com/api/download/100620/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL-3505/3505-3: authentication (supported)

- Interface: User access to the controller (management)
- Protocol: User accounts, LDAP, RADIUS
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:4
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:4: "LDAP central authentication for user account management"
- Source: S223 [type not confirmed] https://selinc.com/api/download/100620/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL-3505/3505-3: encryption (conditional: external gateway only)

- Interface: Remote serial links to field devices (control protocol)
- Protocol: Serial SCADA protocols through separate encrypting devices
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Conditions: Needs separate SEL serial or wireless encrypting devices.
- Location: pdf-page:6
- Support basis: external gateway
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:6: "you can protect remote serial communication to recloser controls"
- Evidence on conditions, pdf-page:6: "By including SEL serial and wireless encrypting devices"
- Source: S223 [type not confirmed] https://selinc.com/api/download/100620/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL-3560: tls (supported)

- Interface: Ethernet-tunneled serial SCADA protocols (control protocol)
- Protocol: SSH or SSL/TLS tunnelling of serial SCADA protocols over Ethernet
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:2
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:2: "Optional encryption for Ethernet-tunneled serial SCADA protocols and engineering access via Secure Shell (SSH) and Secure Sockets Layer (SSL)/Transport Layer Security (TLS) tunneling"
- Source: S225 [type not confirmed] https://selinc.com/api/download/124708/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL-3560: authentication (supported)

- Interface: User access to the controller (management)
- Protocol: User accounts, LDAP
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:2
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:2: "Centralized authentication through the Lightweight Directory Access Protocol (LDAP)"
- Source: S225 [type not confirmed] https://selinc.com/api/download/124708/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL-3560: encryption (supported)

- Interface: Ethernet-tunneled serial SCADA protocols (control protocol)
- Protocol: SSH or SSL/TLS tunnelling of serial SCADA protocols over Ethernet
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:2
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:2: "Optional encryption for Ethernet-tunneled serial SCADA protocols and engineering access via Secure Shell (SSH) and Secure Sockets Layer (SSL)/Transport Layer Security (TLS) tunneling"
- Source: S225 [type not confirmed] https://selinc.com/api/download/124708/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL-3560: ssh (supported)

- Interface: Ethernet-tunneled serial SCADA protocols (control protocol)
- Protocol: SSH or SSL/TLS tunnelling of serial SCADA protocols over Ethernet
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:2
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:2: "Optional encryption for Ethernet-tunneled serial SCADA protocols and engineering access via Secure Shell (SSH) and Secure Sockets Layer (SSL)/Transport Layer Security (TLS) tunneling"
- Source: S225 [type not confirmed] https://selinc.com/api/download/124708/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL Real-Time Automation Controller (RTAC): authentication (supported)

- Interface: Web HMI (management)
- Protocol: Authenticated web access
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:6
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:6: "The HMI allows authenticated access for multiple users and locations and is viewable from a web browser."
- Source: S227 [type not confirmed] https://selinc.com/api/download/111397/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL-735: encryption (conditional: external gateway only)

- Interface: Meter data to SCADA through a separate RTAC (control protocol)
- Protocol: Encrypted communication provided by an RTAC acting as gateway
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Conditions: Needs a separate SEL Real-Time Automation Controller as gateway.
- Location: pdf-page:13
- Support basis: external gateway
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:13: "provides secure, encrypted communications and works as a remote intelligence gateway"
- Evidence on conditions, pdf-page:13: "provides secure, encrypted communications and works as a remote intelligence gateway"
- Source: S230 [type not confirmed] https://selinc.com/api/download/128658/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SEL-421: authentication (supported)

- Interface: IEC 61850 MMS server (control protocol)
- Protocol: MMS authentication
- Model scope: SEL-421-4, -5 (data sheet)
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:13
- Support basis: not assessed
- Default configuration: not assessed
- Activation: configuration: Enabled by a setting in the Configured IED Description (CID) file.
- Deployment: unknown
- Evidence, pdf-page:13: "the relay requires authentication from any client requesting to initiate an MMS session"
- Evidence on activation, pdf-page:13: "When enabled via a setting in the Configured IED Description (CID) file"
- Source: S237 [type not confirmed] https://selinc.com/api/download/99010/
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bay controller – SIPROTEC 6MD86: authentication (supported)

- Interface: Network access (IEEE 802.1X) (network)
- Protocol: IEEE 802.1X
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:13
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:13: "role-based access control, signed firmware, authenticated network access and secure event logging"
- Source: S268 [type not confirmed] https://www.siemens.com/en-us/products/siprotec/6md86/
- Review status: draft (Claude AI draft review; author confirmation pending)

### Bay controller – SIPROTEC 6MD86: encryption (supported)

- Interface: DIGSI engineering tool connection (management)
- Protocol: Encrypted communication between DIGSI and the device
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:6
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:6: "Security through encryption - on the entire communication chain between DIGSI and device"
- Source: S269 [type not confirmed] https://assets.new.siemens.com/siemens/assets/api/uuid:88ed23f5-d148-49a4-b830-6e301094e0ab/emdgb10022004ausbrochuresiprotec5us.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### SICAM A8000 Series: tls (supported)

- Interface: Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) (control protocol)
- Protocol: IEC 60870-5-104, IEC 61850 and DNP3i over TLS
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:12
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:12: "DNP3i master/slave (Transport Layer Security (TLS))"
- Evidence, pdf-page:12: "IEC 60870-5-104 Master/Slave (Transport Layer Security (TLS))"
- Source: S273 [type not confirmed] https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### SICAM A8000 Series: ipsec (supported)

- Interface: IP network layer (network)
- Protocol: IPsec
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:16
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:16: "crypto chip and IPSec encryption"
- Source: S272 [type not confirmed] https://www.siemens.com/en-us/products/sicam/a8000/
- Review status: draft (Claude AI draft review; author confirmation pending)

### SICAM A8000 Series: encryption (supported)

- Interface: Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) (control protocol)
- Protocol: TLS encryption
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:12
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:12: "DNP3i master/slave (Transport Layer Security (TLS))"
- Evidence, pdf-page:25: "Integrated crypto chip - TLS encryption - IPSec encryption"
- Source: S273 [type not confirmed] https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Substation automation unit: tls (supported)

- Interface: Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) (control protocol)
- Protocol: IEC 60870-5-104, IEC 61850 and DNP3i over TLS
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:12
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:12: "DNP3i master/slave (Transport Layer Security (TLS))"
- Evidence, pdf-page:12: "IEC 60870-5-104 Master/Slave (Transport Layer Security (TLS))"
- Source: S277 [type not confirmed] https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Substation automation unit: ipsec (supported)

- Interface: IP network layer (network)
- Protocol: IPsec
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: html-block:14
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, html-block:14: "crypto chip and IPSec encryption"
- Source: S276 [type not confirmed] https://www.siemens.com/en-us/products/sicam/a8000-cp-8050/
- Review status: draft (Claude AI draft review; author confirmation pending)

### Substation automation unit: encryption (supported)

- Interface: Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) (control protocol)
- Protocol: TLS encryption
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:12
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:12: "DNP3i master/slave (Transport Layer Security (TLS))"
- Evidence, pdf-page:25: "Integrated crypto chip - TLS encryption - IPSec encryption"
- Source: S277 [type not confirmed] https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Overcurrent and feeder protection – SIPROTEC 7SJ85: tls (supported)

- Interface: DIGSI 5 engineering tool connection (management)
- Protocol: TLS between DIGSI 5 and the device
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:8
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:8: "TLS-encrypted communication between DIGSI 5 and the SIPROTEC 5 device"
- Source: S299 [type not confirmed] https://assets.new.siemens.com/siemens/assets/api/uuid:279cb01d-fd3b-4df4-8e04-f1fe98b81d6b/SIPROTEC-5-Catalog-EN.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Overcurrent and feeder protection – SIPROTEC 7SJ85: authentication (conditional)

- Interface: Network access (IEEE 802.1X) (network)
- Protocol: IEEE 802.1X
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: V8.3 or later
- Implementation: as described in the cited document
- Conditions: From firmware V8.3.
- Location: pdf-page:22
- Support basis: firmware upgrade
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:22: "IEEE 802.1X based network authentication (from V8.3)"
- Evidence on conditions, pdf-page:22: "IEEE 802.1X based network authentication (from V8.3)"
- Source: S299 [type not confirmed] https://assets.new.siemens.com/siemens/assets/api/uuid:279cb01d-fd3b-4df4-8e04-f1fe98b81d6b/SIPROTEC-5-Catalog-EN.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Overcurrent and feeder protection – SIPROTEC 7SJ85: encryption (supported)

- Interface: DIGSI 5 engineering tool connection (management)
- Protocol: TLS between DIGSI 5 and the device
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:8
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:8: "TLS-encrypted communication between DIGSI 5 and the SIPROTEC 5 device"
- Source: S299 [type not confirmed] https://assets.new.siemens.com/siemens/assets/api/uuid:279cb01d-fd3b-4df4-8e04-f1fe98b81d6b/SIPROTEC-5-Catalog-EN.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

### Overcurrent and feeder protection – SIPROTEC 7SJ85: integrity (supported)

- Interface: DIGSI 5 engineering tool connection (management)
- Protocol: TLS between DIGSI 5 and the device
- Model scope: as named in the cited document; exact model or order code not established
- Hardware revision: not established
- Firmware: not established
- Implementation: as described in the cited document
- Location: pdf-page:364
- Support basis: not assessed
- Default configuration: not assessed
- Activation: not assessed
- Deployment: unknown
- Evidence, pdf-page:364: "the integrity and confidentiality of the transmitted data are ensured"
- Source: S299 [type not confirmed] https://assets.new.siemens.com/siemens/assets/api/uuid:279cb01d-fd3b-4df4-8e04-f1fe98b81d6b/SIPROTEC-5-Catalog-EN.pdf
- Review status: draft (Claude AI draft review; author confirmation pending)

## Reviewed rows

| Product | Capability | Interface | Review result | Scope |
|---|---|---|---|---|
| Multilin C60/C95 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin C60/C95 | tls | - | unknown | No wording on TLS was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin C60/C95 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin C60/C95 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin C60/C95 | authentication | - | unknown | 10 passages mention authentication in the sources read (4 product page, 2 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin C60/C95 | authentication | User access to the relay (AAA server) | supported | User login through an AAA server. Nothing is stated about protocol traffic. Whether this needs the CyberSentry option is not stated on the page. |
| Multilin C60/C95 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin C60/C95 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin C60/C95 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20E | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20E | tls | - | unknown | No wording on TLS was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20E | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20E | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20E | authentication | - | unknown | No wording on authentication was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20E | encryption | - | unknown | No wording on encryption was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20E | ssh | - | unknown | No wording on SSH was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20E | integrity | - | unknown | No wording on integrity was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin G100 Advanced Substation Gateway | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin G100 Advanced Substation Gateway | tls | Master station link (DNP3/TCP, Modbus/TCP, IEC 104) | supported | The brochure lists TLS tunnelling from the master station for the SCADA protocols among the security features. Brochure-level, family-wide statement. |
| Multilin G100 Advanced Substation Gateway | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin G100 Advanced Substation Gateway | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin G100 Advanced Substation Gateway | authentication | - | unknown | 3 passages mention authentication in the sources read (3 product page, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin G100 Advanced Substation Gateway | authentication | User access to the gateway | supported | User login to the gateway. It does not authenticate the SCADA protocol peers. |
| Multilin G100 Advanced Substation Gateway | encryption | Master station link (DNP3/TCP, Modbus/TCP, IEC 104) | supported | TLS tunnelling is named for DNP3/TCP, Modbus/TCP and IEC 104. The property follows from the mechanism the document names for this protocol; cipher suites and defaults are not stated. |
| Multilin G100 Advanced Substation Gateway | ssh | - | unknown | 3 passages mention SSH in the sources read (3 product page, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin G100 Advanced Substation Gateway | ssh | Remote access to substation devices through the gateway | supported | Remote engineering access through the gateway, not the SCADA link. |
| Multilin G100 Advanced Substation Gateway | integrity | - | unknown | No wording on integrity was found in the sources read for this device (3 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| G500 Advanced Substation Gateway | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| G500 Advanced Substation Gateway | tls | Master station link (DNP3/TCP, Modbus/TCP, IEC 104) | supported | The brochure lists TLS tunnelling from the master station for the SCADA protocols among the security features. Brochure-level, family-wide statement. |
| G500 Advanced Substation Gateway | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| G500 Advanced Substation Gateway | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| G500 Advanced Substation Gateway | authentication | - | unknown | 3 passages mention authentication in the sources read (4 product page, 2 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| G500 Advanced Substation Gateway | authentication | User access to the gateway | supported | User login to the gateway. It does not authenticate the SCADA protocol peers. |
| G500 Advanced Substation Gateway | encryption | Master station link (DNP3/TCP, Modbus/TCP, IEC 104) | supported | TLS tunnelling is named for DNP3/TCP, Modbus/TCP and IEC 104. The property follows from the mechanism the document names for this protocol; cipher suites and defaults are not stated. |
| G500 Advanced Substation Gateway | ssh | - | unknown | 7 passages mention SSH in the sources read (4 product page, 2 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| G500 Advanced Substation Gateway | ssh | Remote access to substation devices through the gateway | supported | Remote engineering access through the gateway, not the SCADA link. |
| G500 Advanced Substation Gateway | integrity | - | unknown | No wording on integrity was found in the sources read for this device (4 product page, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DART-Legacy | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DART-Legacy | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DART-Legacy | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DART-Legacy | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DART-Legacy | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DART-Legacy | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DART-Legacy | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DART-Legacy | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20MX - Advanced Substation Automation Controller | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20MX - Advanced Substation Automation Controller | tls | - | unknown | No wording on TLS was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20MX - Advanced Substation Automation Controller | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20MX - Advanced Substation Automation Controller | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20MX - Advanced Substation Automation Controller | authentication | - | unknown | 5 passages mention authentication in the sources read (4 product page, 4 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin D20MX - Advanced Substation Automation Controller | authentication | User access to the controller | supported | User login, stated as built in. Nothing is stated about the SCADA protocols. |
| Multilin D20MX - Advanced Substation Automation Controller | encryption | - | unknown | No wording on encryption was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D20MX - Advanced Substation Automation Controller | ssh | - | unknown | 2 passages mention SSH in the sources read (4 product page, 4 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin D20MX - Advanced Substation Automation Controller | ssh | Firmware and configuration file transfer | supported | File transfer for maintenance, not the control protocol. |
| Multilin D20MX - Advanced Substation Automation Controller | integrity | - | unknown | No wording on integrity was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D400 Advanced Substation Gateway | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (3 product page, 2 document of unconfirmed type, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D400 Advanced Substation Gateway | tls | - | unknown | 6 passages mention TLS in the sources read (3 product page, 2 document of unconfirmed type, 2 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin D400 Advanced Substation Gateway | tls | Pass-through and terminal server access to substation devices | supported | Named for personnel access through the gateway, not for the SCADA protocols to the master station. |
| Multilin D400 Advanced Substation Gateway | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (3 product page, 2 document of unconfirmed type, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D400 Advanced Substation Gateway | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (3 product page, 2 document of unconfirmed type, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin D400 Advanced Substation Gateway | authentication | - | unknown | 10 passages mention authentication in the sources read (3 product page, 2 document of unconfirmed type, 2 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin D400 Advanced Substation Gateway | authentication | User access to the gateway | supported | User login. Nothing is stated about authenticating SCADA protocol traffic. |
| Multilin D400 Advanced Substation Gateway | encryption | - | unknown | No wording on encryption was found in the sources read for this device (3 product page, 2 document of unconfirmed type, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. Second pass (AI, 2026-10-14): the D400 brochure lists a "Simple VPN server" (pdf-page:1) and its connectivity diagram labels a link "Modbus TCP/SSH Over VPN Tunnel" (pdf-page:4). Neither says which traffic the VPN carries or that the SCADA protocols to the master station are encrypted, so the result stays unknown. |
| Multilin D400 Advanced Substation Gateway | ssh | - | unknown | 8 passages mention SSH in the sources read (3 product page, 2 document of unconfirmed type, 2 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin D400 Advanced Substation Gateway | ssh | Pass-through and terminal server access to substation devices | supported | Named for personnel access through the gateway. |
| Multilin D400 Advanced Substation Gateway | integrity | - | unknown | No wording on integrity was found in the sources read for this device (3 product page, 2 document of unconfirmed type, 2 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin H500 - Legacy | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin H500 - Legacy | tls | - | unknown | No wording on TLS was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin H500 - Legacy | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin H500 - Legacy | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin H500 - Legacy | authentication | - | unknown | 2 passages mention authentication in the sources read (3 product page, 1 document of unconfirmed type, 1 datasheet). The passages concern storage encryption of the built-in drive and a central authentication server the computer can host, not a communication interface.; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin H500 - Legacy | encryption | - | unknown | 7 passages mention encryption in the sources read (3 product page, 1 document of unconfirmed type, 1 datasheet). The passages concern storage encryption of the built-in drive and a central authentication server the computer can host, not a communication interface.; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin H500 - Legacy | ssh | - | unknown | No wording on SSH was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin H500 - Legacy | integrity | - | unknown | No wording on integrity was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 2200 Digital Power Meter | dnp3_secure_authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 123 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 2200 Digital Power Meter | tls | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 1 complete manual(s), 123 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 2200 Digital Power Meter | ipsec | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 123 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 2200 Digital Power Meter | cip_security | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 123 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 2200 Digital Power Meter | authentication | - | unknown | 1 passages mention authentication in the sources read (4 product page, 4 manual, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| EPM 2200 Digital Power Meter | authentication | Ethernet card web configuration page | supported | A login screen for the Ethernet card configuration page; the manual gives default credentials. Nothing is stated about the meter protocols. |
| EPM 2200 Digital Power Meter | encryption | - | unknown | 11 passages mention encryption in the sources read (4 product page, 4 manual, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| EPM 2200 Digital Power Meter | ssh | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 1 complete manual(s), 123 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 2200 Digital Power Meter | integrity | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 1 complete manual(s), 123 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 6010 Building Automation Power Meter | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 3 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 6010 Building Automation Power Meter | tls | - | unknown | 1 passages mention TLS in the sources read (4 product page, 3 manual, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| EPM 6010 Building Automation Power Meter | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 3 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 6010 Building Automation Power Meter | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 3 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 6010 Building Automation Power Meter | authentication | - | unknown | No wording on authentication was found in the sources read for this device (4 product page, 3 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 6010 Building Automation Power Meter | encryption | - | unknown | 9 passages mention encryption in the sources read (4 product page, 3 manual, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| EPM 6010 Building Automation Power Meter | ssh | - | unknown | No wording on SSH was found in the sources read for this device (4 product page, 3 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 6010 Building Automation Power Meter | integrity | - | unknown | 1 passages mention integrity in the sources read (4 product page, 3 manual, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| iSTAT i400 Standard Transducers | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| iSTAT i400 Standard Transducers | tls | - | unknown | No wording on TLS was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| iSTAT i400 Standard Transducers | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| iSTAT i400 Standard Transducers | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| iSTAT i400 Standard Transducers | authentication | - | unknown | No wording on authentication was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| iSTAT i400 Standard Transducers | encryption | - | unknown | No wording on encryption was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| iSTAT i400 Standard Transducers | ssh | - | unknown | No wording on SSH was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| iSTAT i400 Standard Transducers | integrity | - | unknown | No wording on integrity was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| iSTAT M2x2 Communicating Measurement Centre | dnp3_secure_authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 72 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| iSTAT M2x2 Communicating Measurement Centre | tls | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 1 complete manual(s), 72 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| iSTAT M2x2 Communicating Measurement Centre | ipsec | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 72 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| iSTAT M2x2 Communicating Measurement Centre | cip_security | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 72 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| iSTAT M2x2 Communicating Measurement Centre | authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on authentication anywhere in 1 complete manual(s), 72 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| iSTAT M2x2 Communicating Measurement Centre | encryption | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 1 complete manual(s), 72 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| iSTAT M2x2 Communicating Measurement Centre | ssh | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 1 complete manual(s), 72 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| iSTAT M2x2 Communicating Measurement Centre | integrity | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 1 complete manual(s), 72 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 4000 Sub-meter (Discontinued) | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 4000 Sub-meter (Discontinued) | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 4000 Sub-meter (Discontinued) | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 4000 Sub-meter (Discontinued) | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 4000 Sub-meter (Discontinued) | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 4000 Sub-meter (Discontinued) | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 4000 Sub-meter (Discontinued) | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 4000 Sub-meter (Discontinued) | integrity | - | unknown | 2 passages mention integrity in the sources read (2 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| EPM 5300 Power Metering System | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (3 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 5300 Power Metering System | tls | - | unknown | No wording on TLS was found in the sources read for this device (3 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 5300 Power Metering System | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (3 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 5300 Power Metering System | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (3 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 5300 Power Metering System | authentication | - | unknown | No wording on authentication was found in the sources read for this device (3 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 5300 Power Metering System | encryption | - | unknown | No wording on encryption was found in the sources read for this device (3 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 5300 Power Metering System | ssh | - | unknown | No wording on SSH was found in the sources read for this device (3 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 5300 Power Metering System | integrity | - | unknown | No wording on integrity was found in the sources read for this device (3 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 7100 Power Quality Meter | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 2 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 7100 Power Quality Meter | tls | - | unknown | 1 passages mention TLS in the sources read (4 product page, 2 manual, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| EPM 7100 Power Quality Meter | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 2 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 7100 Power Quality Meter | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 2 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 7100 Power Quality Meter | authentication | - | unknown | No wording on authentication was found in the sources read for this device (4 product page, 2 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 7100 Power Quality Meter | encryption | - | unknown | 9 passages mention encryption in the sources read (4 product page, 2 manual, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| EPM 7100 Power Quality Meter | ssh | - | unknown | No wording on SSH was found in the sources read for this device (4 product page, 2 manual, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| EPM 7100 Power Quality Meter | integrity | - | unknown | 1 passages mention integrity in the sources read (4 product page, 2 manual, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| EPM 9900 Advanced Power Quality Meter | dnp3_secure_authentication | DNP3 as described in the EPM 9000 series DNP guide | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 9900 Advanced Power Quality Meter | tls | DNP3 as described in the EPM 9000 series DNP guide | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 9900 Advanced Power Quality Meter | ipsec | DNP3 as described in the EPM 9000 series DNP guide | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 9900 Advanced Power Quality Meter | cip_security | DNP3 as described in the EPM 9000 series DNP guide | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 9900 Advanced Power Quality Meter | authentication | DNP3 as described in the EPM 9000 series DNP guide | unknown: complete document silent | The keyword search found no passage on authentication anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 9900 Advanced Power Quality Meter | encryption | DNP3 as described in the EPM 9000 series DNP guide | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 9900 Advanced Power Quality Meter | ssh | DNP3 as described in the EPM 9000 series DNP guide | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| EPM 9900 Advanced Power Quality Meter | integrity | DNP3 as described in the EPM 9000 series DNP guide | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| BiTRONICS 70 Series - Legacy | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| BiTRONICS 70 Series - Legacy | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| BiTRONICS 70 Series - Legacy | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| BiTRONICS 70 Series - Legacy | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| BiTRONICS 70 Series - Legacy | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| BiTRONICS 70 Series - Legacy | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| BiTRONICS 70 Series - Legacy | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| BiTRONICS 70 Series - Legacy | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| IFC Time-overcurrent Relay | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| IFC Time-overcurrent Relay | tls | - | unknown | No wording on TLS was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| IFC Time-overcurrent Relay | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| IFC Time-overcurrent Relay | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| IFC Time-overcurrent Relay | authentication | - | unknown | No wording on authentication was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| IFC Time-overcurrent Relay | encryption | - | unknown | No wording on encryption was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| IFC Time-overcurrent Relay | ssh | - | unknown | No wording on SSH was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| IFC Time-overcurrent Relay | integrity | - | unknown | No wording on integrity was found in the sources read for this device (3 product page, 1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 339 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 339 | tls | - | unknown | No wording on TLS was found in the sources read for this device (4 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 339 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 339 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 339 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (4 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 339 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (4 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 339 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (4 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 339 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (4 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 850: Advanced Feeder Protection & Bay Controller | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 850: Advanced Feeder Protection & Bay Controller | tls | - | unknown | No wording on TLS was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 850: Advanced Feeder Protection & Bay Controller | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 850: Advanced Feeder Protection & Bay Controller | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin 850: Advanced Feeder Protection & Bay Controller | authentication | - | unknown | 9 passages mention authentication in the sources read (4 product page, 4 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin 850: Advanced Feeder Protection & Bay Controller | authentication | User access to the relay (AAA server) | supported | User login through an AAA server. Nothing is stated about protocol traffic. |
| Multilin 850: Advanced Feeder Protection & Bay Controller | encryption | - | unknown | 1 passages mention encryption in the sources read (4 product page, 4 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin 850: Advanced Feeder Protection & Bay Controller | ssh | - | unknown | 2 passages mention SSH in the sources read (4 product page, 4 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Multilin 850: Advanced Feeder Protection & Bay Controller | integrity | - | unknown | No wording on integrity was found in the sources read for this device (4 product page, 4 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| P64 MiCOM 5th Generation | dnp3_secure_authentication | Substation and SCADA protocols of the relay as described in its technical manual | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 672 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| P64 MiCOM 5th Generation | tls | Substation and SCADA protocols of the relay as described in its technical manual | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 1 complete manual(s), 672 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| P64 MiCOM 5th Generation | ipsec | Substation and SCADA protocols of the relay as described in its technical manual | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 672 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| P64 MiCOM 5th Generation | cip_security | Substation and SCADA protocols of the relay as described in its technical manual | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 672 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| P64 MiCOM 5th Generation | authentication | - | unknown | 33 passages mention authentication in the sources read (4 product page, 1 document of unconfirmed type, 1 manual, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| P64 MiCOM 5th Generation | authentication | User access to the IED (front panel, S1 Agile, network ports) | supported | User login. A bypass mode without authentication exists for local interfaces. The default method for IEDs with an Ethernet board is Server + Device. |
| P64 MiCOM 5th Generation | encryption | - | unknown | 4 passages mention encryption in the sources read (4 product page, 1 document of unconfirmed type, 1 manual, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| P64 MiCOM 5th Generation | encryption | S1 Agile engineering tool connection | supported | Encryption is stated for passwords in engineering-tool and RADIUS messages, not for protocol payloads. |
| P64 MiCOM 5th Generation | ssh | - | unknown | 8 passages mention SSH in the sources read (4 product page, 1 document of unconfirmed type, 1 manual, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| P64 MiCOM 5th Generation | ssh | S1 Agile engineering tool connection | supported | SSH is listed as the service for the S1 Agile engineering tool. |
| P64 MiCOM 5th Generation | integrity | - | unknown | 1 passages mention integrity in the sources read (4 product page, 1 document of unconfirmed type, 1 manual, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| DFP200 Digital Feeder Relay (Discontinued) | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DFP200 Digital Feeder Relay (Discontinued) | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DFP200 Digital Feeder Relay (Discontinued) | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DFP200 Digital Feeder Relay (Discontinued) | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DFP200 Digital Feeder Relay (Discontinued) | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DFP200 Digital Feeder Relay (Discontinued) | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DFP200 Digital Feeder Relay (Discontinued) | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DFP200 Digital Feeder Relay (Discontinued) | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DLPD Digital Line Protection System | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DLPD Digital Line Protection System | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DLPD Digital Line Protection System | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DLPD Digital Line Protection System | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DLPD Digital Line Protection System | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DLPD Digital Line Protection System | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DLPD Digital Line Protection System | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| DLPD Digital Line Protection System | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| KAVS Check Synchronising Relay | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (3 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| KAVS Check Synchronising Relay | tls | - | unknown | No wording on TLS was found in the sources read for this device (3 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| KAVS Check Synchronising Relay | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (3 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| KAVS Check Synchronising Relay | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (3 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| KAVS Check Synchronising Relay | authentication | - | unknown | No wording on authentication was found in the sources read for this device (3 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| KAVS Check Synchronising Relay | encryption | - | unknown | No wording on encryption was found in the sources read for this device (3 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| KAVS Check Synchronising Relay | ssh | - | unknown | No wording on SSH was found in the sources read for this device (3 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| KAVS Check Synchronising Relay | integrity | - | unknown | No wording on integrity was found in the sources read for this device (3 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin A60 - Legacy | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin A60 - Legacy | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin A60 - Legacy | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin A60 - Legacy | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin A60 - Legacy | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin A60 - Legacy | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin A60 - Legacy | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Multilin A60 - Legacy | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MBCI, MCRI, MRTP AND MVTW – Legacy | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MBCI, MCRI, MRTP AND MVTW – Legacy | tls | - | unknown | No wording on TLS was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MBCI, MCRI, MRTP AND MVTW – Legacy | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MBCI, MCRI, MRTP AND MVTW – Legacy | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MBCI, MCRI, MRTP AND MVTW – Legacy | authentication | - | unknown | No wording on authentication was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MBCI, MCRI, MRTP AND MVTW – Legacy | encryption | - | unknown | No wording on encryption was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MBCI, MCRI, MRTP AND MVTW – Legacy | ssh | - | unknown | No wording on SSH was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MBCI, MCRI, MRTP AND MVTW – Legacy | integrity | - | unknown | No wording on integrity was found in the sources read for this device (4 product page, 4 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM Agile P24x - Legacy | dnp3_secure_authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 556 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| MiCOM Agile P24x - Legacy | tls | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 1 complete manual(s), 556 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| MiCOM Agile P24x - Legacy | ipsec | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 556 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| MiCOM Agile P24x - Legacy | cip_security | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 556 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| MiCOM Agile P24x - Legacy | authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on authentication anywhere in 1 complete manual(s), 556 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| MiCOM Agile P24x - Legacy | encryption | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 1 complete manual(s), 556 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| MiCOM Agile P24x - Legacy | ssh | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 1 complete manual(s), 556 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| MiCOM Agile P24x - Legacy | integrity | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 1 complete manual(s), 556 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| MiCOM Agile P541 & P542 Line Differential Protection | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (4 product page, 3 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM Agile P541 & P542 Line Differential Protection | tls | - | unknown | No wording on TLS was found in the sources read for this device (4 product page, 3 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM Agile P541 & P542 Line Differential Protection | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (4 product page, 3 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM Agile P541 & P542 Line Differential Protection | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (4 product page, 3 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM Agile P541 & P542 Line Differential Protection | authentication | - | unknown | No wording on authentication was found in the sources read for this device (4 product page, 3 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM Agile P541 & P542 Line Differential Protection | encryption | - | unknown | No wording on encryption was found in the sources read for this device (4 product page, 3 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM Agile P541 & P542 Line Differential Protection | ssh | - | unknown | No wording on SSH was found in the sources read for this device (4 product page, 3 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM Agile P541 & P542 Line Differential Protection | integrity | - | unknown | No wording on integrity was found in the sources read for this device (4 product page, 3 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| TCCV Directional Overcurrent Relay | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| TCCV Directional Overcurrent Relay | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| TCCV Directional Overcurrent Relay | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| TCCV Directional Overcurrent Relay | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| TCCV Directional Overcurrent Relay | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| TCCV Directional Overcurrent Relay | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| TCCV Directional Overcurrent Relay | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| TCCV Directional Overcurrent Relay | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| 1408 PowerMonitor 1000 | dnp3_secure_authentication | Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 216 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1408 PowerMonitor 1000 | tls | - | unknown | 1 passages mention TLS in the sources read (3 document of unconfirmed type, 2 manual, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| 1408 PowerMonitor 1000 | tls | Web page and FTP access to the unit | supported | HTTPS and FTPS can be enabled by a setting for the web page and file access. The protocol version named is old. Not the EtherNet/IP or Modbus data interface. |
| 1408 PowerMonitor 1000 | ipsec | Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 216 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1408 PowerMonitor 1000 | cip_security | Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 216 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1408 PowerMonitor 1000 | authentication | Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual | unknown: complete document silent | The keyword search found no passage on authentication anywhere in 1 complete manual(s), 216 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1408 PowerMonitor 1000 | encryption | Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 1 complete manual(s), 216 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1408 PowerMonitor 1000 | ssh | Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 1 complete manual(s), 216 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1408 PowerMonitor 1000 | integrity | Data communication of the unit (EtherNet/IP, Modbus) as described in its user manual | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 1 complete manual(s), 216 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1420 PowerMonitor 500 | dnp3_secure_authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 108 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1420 PowerMonitor 500 | tls | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 1 complete manual(s), 108 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1420 PowerMonitor 500 | ipsec | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 108 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1420 PowerMonitor 500 | cip_security | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 108 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1420 PowerMonitor 500 | authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on authentication anywhere in 1 complete manual(s), 108 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1420 PowerMonitor 500 | encryption | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 1 complete manual(s), 108 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1420 PowerMonitor 500 | ssh | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 1 complete manual(s), 108 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1420 PowerMonitor 500 | integrity | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 1 complete manual(s), 108 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1426 PowerMonitor 5000 | dnp3_secure_authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 406 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1426 PowerMonitor 5000 | tls | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 1 complete manual(s), 406 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1426 PowerMonitor 5000 | ipsec | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 406 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1426 PowerMonitor 5000 | cip_security | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 406 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1426 PowerMonitor 5000 | authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on authentication anywhere in 1 complete manual(s), 406 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1426 PowerMonitor 5000 | encryption | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 1 complete manual(s), 406 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1426 PowerMonitor 5000 | ssh | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 1 complete manual(s), 406 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| 1426 PowerMonitor 5000 | integrity | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 1 complete manual(s), 406 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| CompactLogix 5380 Controllers | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (5 manual, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 5380 Controllers | tls | - | unknown | 2 passages mention TLS in the sources read (5 manual, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| CompactLogix 5380 Controllers | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (5 manual, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 5380 Controllers | cip_security | EtherNet/IP (CIP) communication | conditional | The user manual states CIP Security support from a firmware revision, and that the policy is defined with FactoryTalk Policy Manager. The manual also says the CIP Security ports are enabled by default, which is about the ports being open and not about a policy being in force. |
| CompactLogix 5380 Controllers | authentication | EtherNet/IP (CIP) communication | conditional | Stated as a property of CIP Security, which the controller supports from a firmware revision. |
| CompactLogix 5380 Controllers | encryption | EtherNet/IP (CIP) communication | conditional | Stated as a property of CIP Security, which the controller supports from a firmware revision. Confidentiality is listed as a property; whether it is applied depends on the security policy that is configured. |
| CompactLogix 5380 Controllers | ssh | - | unknown | No wording on SSH was found in the sources read for this device (5 manual, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 5380 Controllers | integrity | EtherNet/IP (CIP) communication | conditional | Stated as a property of CIP Security, which the controller supports from a firmware revision. |
| ControlLogix 5590 Controllers | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page, 1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| ControlLogix 5590 Controllers | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page, 1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| ControlLogix 5590 Controllers | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page, 1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| ControlLogix 5590 Controllers | cip_security | EtherNet/IP (CIP) communication | supported | The brochure calls CIP Security integrated. Which of authentication, integrity and confidentiality it provides here, and what is on by default, is not stated in the product page or brochure. |
| ControlLogix 5590 Controllers | authentication | - | unknown | 1 passages mention authentication in the sources read (1 product page, 1 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| ControlLogix 5590 Controllers | encryption | - | unknown | 1 passages mention encryption in the sources read (1 product page, 1 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| ControlLogix 5590 Controllers | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page, 1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| ControlLogix 5590 Controllers | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page, 1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| LogixEdge Controllers | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| LogixEdge Controllers | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| LogixEdge Controllers | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| LogixEdge Controllers | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| LogixEdge Controllers | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| LogixEdge Controllers | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| LogixEdge Controllers | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| LogixEdge Controllers | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro870 Controllers | dnp3_secure_authentication | DNP3 outstation (slave) communication | supported | Stated on the product page. The controller manual was not among the sources read for this entry, so the default and the key setup are not assessed here. Second pass (AI, 2026-10-14): the Micro830, Micro850 and Micro870 user manual 2080-UM002S-EN-E, fetched for the Micro830 entry (source 5f6f1b22b4fd07d375a5, sha256 0f6f1715c95afefc...), states in its Micro870 DNP3 chapter (pdf-page:89): "Enable Secure Authentication The valid selections are Enabled (Checked) and Disabled (Unchecked). Default value is Disabled (Unchecked)." A row may cite only sources of its own entry, so default_state stays not assessed here. |
| Micro870 Controllers | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro870 Controllers | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro870 Controllers | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro870 Controllers | authentication | DNP3 outstation (slave) communication | supported | Protocol authentication for DNP3 is stated. DNP3 Secure Authentication authenticates messages and does not encrypt them; no encryption of DNP3 is stated. |
| Micro870 Controllers | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro870 Controllers | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro870 Controllers | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 1768 Controllers | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 1768 Controllers | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 1768 Controllers | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 1768 Controllers | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 1768 Controllers | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 1768 Controllers | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 1768 Controllers | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 1768 Controllers | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro830 Controllers | dnp3_secure_authentication | - | unknown | 7 passages mention DNP3 Secure Authentication in the sources read (1 product page, 1 manual). The user manual read for this entry (2080-UM002) documents DNP3 Secure Authentication in the chapter titled for the Micro870 controller. Nothing is established for the Micro830.; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Micro830 Controllers | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro830 Controllers | ipsec | - | unknown | 1 passages mention IPsec in the sources read (1 product page, 1 manual). The user manual read for this entry (2080-UM002) documents DNP3 Secure Authentication in the chapter titled for the Micro870 controller. Nothing is established for the Micro830.; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Micro830 Controllers | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro830 Controllers | authentication | - | unknown | 11 passages mention authentication in the sources read (1 product page, 1 manual). The user manual read for this entry (2080-UM002) documents DNP3 Secure Authentication in the chapter titled for the Micro870 controller. Nothing is established for the Micro830.; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Micro830 Controllers | encryption | - | unknown | 5 passages mention encryption in the sources read (1 product page, 1 manual). The user manual read for this entry (2080-UM002) documents DNP3 Secure Authentication in the chapter titled for the Micro870 controller. Nothing is established for the Micro830.; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Micro830 Controllers | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page, 1 manual). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Micro830 Controllers | integrity | - | unknown | 5 passages mention integrity in the sources read (1 product page, 1 manual). The user manual read for this entry (2080-UM002) documents DNP3 Secure Authentication in the chapter titled for the Micro870 controller. Nothing is established for the Micro830.; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| MicroLogix 1100 Controllers | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1100 Controllers | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1100 Controllers | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1100 Controllers | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1100 Controllers | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1100 Controllers | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1100 Controllers | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1100 Controllers | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1200 Controllers | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1200 Controllers | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1200 Controllers | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1200 Controllers | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1200 Controllers | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1200 Controllers | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1200 Controllers | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MicroLogix 1200 Controllers | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| CompactLogix 5370 Controllers | dnp3_secure_authentication | EtherNet/IP and serial communication as described in the user manual | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| CompactLogix 5370 Controllers | tls | EtherNet/IP and serial communication as described in the user manual | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| CompactLogix 5370 Controllers | ipsec | EtherNet/IP and serial communication as described in the user manual | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| CompactLogix 5370 Controllers | cip_security | EtherNet/IP and serial communication as described in the user manual | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| CompactLogix 5370 Controllers | authentication | EtherNet/IP and serial communication as described in the user manual | unknown: complete document silent | The keyword search found no passage on authentication anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| CompactLogix 5370 Controllers | encryption | EtherNet/IP and serial communication as described in the user manual | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| CompactLogix 5370 Controllers | ssh | EtherNet/IP and serial communication as described in the user manual | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| CompactLogix 5370 Controllers | integrity | EtherNet/IP and serial communication as described in the user manual | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 1 complete manual(s), 272 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| SLC 500 Controllers | dnp3_secure_authentication | DF1, DH-485, DH+ and Ethernet communication as described in the manuals | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 3 complete manual(s), 1213 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| SLC 500 Controllers | tls | DF1, DH-485, DH+ and Ethernet communication as described in the manuals | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 3 complete manual(s), 1213 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| SLC 500 Controllers | ipsec | DF1, DH-485, DH+ and Ethernet communication as described in the manuals | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 3 complete manual(s), 1213 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| SLC 500 Controllers | cip_security | DF1, DH-485, DH+ and Ethernet communication as described in the manuals | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 3 complete manual(s), 1213 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| SLC 500 Controllers | authentication | - | unknown | 4 passages mention authentication in the sources read (4 manual, 1 product page, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SLC 500 Controllers | encryption | DF1, DH-485, DH+ and Ethernet communication as described in the manuals | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 3 complete manual(s), 1213 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| SLC 500 Controllers | ssh | DF1, DH-485, DH+ and Ethernet communication as described in the manuals | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 3 complete manual(s), 1213 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| SLC 500 Controllers | integrity | - | unknown | 3 passages mention integrity in the sources read (4 manual, 1 product page, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Bulletin 865 Motor-feeder Protection Relays | dnp3_secure_authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 1 complete manual(s), 296 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 865 Motor-feeder Protection Relays | tls | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 1 complete manual(s), 296 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 865 Motor-feeder Protection Relays | ipsec | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 1 complete manual(s), 296 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 865 Motor-feeder Protection Relays | cip_security | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 1 complete manual(s), 296 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 865 Motor-feeder Protection Relays | authentication | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on authentication anywhere in 1 complete manual(s), 296 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 865 Motor-feeder Protection Relays | encryption | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 1 complete manual(s), 296 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 865 Motor-feeder Protection Relays | ssh | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 1 complete manual(s), 296 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 865 Motor-feeder Protection Relays | integrity | Communication protocols of the device as described in its manual | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 1 complete manual(s), 296 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 857 Motor-feeder Protection Relays | dnp3_secure_authentication | IEC 61850, EtherNet/IP and serial protocols as described in the manuals | unknown: complete document silent | The keyword search found no passage on DNP3 Secure Authentication anywhere in 3 complete manual(s), 678 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 857 Motor-feeder Protection Relays | tls | IEC 61850, EtherNet/IP and serial protocols as described in the manuals | unknown: complete document silent | The keyword search found no passage on TLS anywhere in 3 complete manual(s), 678 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 857 Motor-feeder Protection Relays | ipsec | IEC 61850, EtherNet/IP and serial protocols as described in the manuals | unknown: complete document silent | The keyword search found no passage on IPsec anywhere in 3 complete manual(s), 678 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 857 Motor-feeder Protection Relays | cip_security | IEC 61850, EtherNet/IP and serial protocols as described in the manuals | unknown: complete document silent | The keyword search found no passage on CIP Security anywhere in 3 complete manual(s), 678 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 857 Motor-feeder Protection Relays | authentication | IEC 61850, EtherNet/IP and serial protocols as described in the manuals | unknown: complete document silent | The keyword search found no passage on authentication anywhere in 3 complete manual(s), 678 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 857 Motor-feeder Protection Relays | encryption | IEC 61850, EtherNet/IP and serial protocols as described in the manuals | unknown: complete document silent | The keyword search found no passage on encryption anywhere in 3 complete manual(s), 678 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 857 Motor-feeder Protection Relays | ssh | IEC 61850, EtherNet/IP and serial protocols as described in the manuals | unknown: complete document silent | The keyword search found no passage on SSH anywhere in 3 complete manual(s), 678 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| Bulletin 857 Motor-feeder Protection Relays | integrity | IEC 61850, EtherNet/IP and serial protocols as described in the manuals | unknown: complete document silent | The keyword search found no passage on integrity anywhere in 3 complete manual(s), 678 PDF pages in all. Silence in the manual is not a vendor statement that the capability is absent. |
| SEL-2431 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2431 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2431 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2431 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2431 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2431 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2431 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2431 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-3505/3505-3 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-3505/3505-3 | tls | - | unknown | 1 passages mention TLS in the sources read (1 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SEL-3505/3505-3 | tls | Encrypted communication listed under security features (interface not specified) | supported | The data sheet lists SSL/TLS and SSH under security features without tying them to a SCADA protocol, so this is filed as management access. |
| SEL-3505/3505-3 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-3505/3505-3 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-3505/3505-3 | authentication | - | unknown | 5 passages mention authentication in the sources read (1 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SEL-3505/3505-3 | authentication | User access to the controller | supported | User login. |
| SEL-3505/3505-3 | encryption | Remote serial links to field devices | conditional: external gateway only | Protection of serial links is offered through separate SEL encrypting devices, not by the controller itself. |
| SEL-3505/3505-3 | ssh | - | unknown | 1 passages mention SSH in the sources read (1 datasheet, 1 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SEL-3505/3505-3 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-3560 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-3560 | tls | Ethernet-tunneled serial SCADA protocols | supported | The flyer states optional encryption for Ethernet-tunneled serial SCADA protocols through SSH and SSL/TLS tunnelling. "Optional" is read as selectable by configuration; whether a licence is needed and the default are not stated. |
| SEL-3560 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-3560 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-3560 | authentication | - | unknown | 6 passages mention authentication in the sources read (1 document of unconfirmed type, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SEL-3560 | authentication | User access to the controller | supported | User login. |
| SEL-3560 | encryption | Ethernet-tunneled serial SCADA protocols | supported | The flyer states optional encryption for Ethernet-tunneled serial SCADA protocols through SSH and SSL/TLS tunnelling. "Optional" is read as selectable by configuration; whether a licence is needed and the default are not stated. |
| SEL-3560 | ssh | Ethernet-tunneled serial SCADA protocols | supported | The flyer states optional encryption for Ethernet-tunneled serial SCADA protocols through SSH and SSL/TLS tunnelling. "Optional" is read as selectable by configuration; whether a licence is needed and the default are not stated. |
| SEL-3560 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 document of unconfirmed type, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL Real-Time Automation Controller (RTAC) | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL Real-Time Automation Controller (RTAC) | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL Real-Time Automation Controller (RTAC) | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL Real-Time Automation Controller (RTAC) | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL Real-Time Automation Controller (RTAC) | authentication | - | unknown | 2 passages mention authentication in the sources read (2 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SEL Real-Time Automation Controller (RTAC) | authentication | Web HMI | supported | Login to the web HMI. The flyers read for this entry say nothing about the SCADA protocols. |
| SEL Real-Time Automation Controller (RTAC) | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL Real-Time Automation Controller (RTAC) | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL Real-Time Automation Controller (RTAC) | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-734/734T | dnp3_secure_authentication | - | unknown | Nothing could be read for this device: its documents are behind a sign-in or yielded no text. |
| SEL-734/734T | tls | - | unknown | Nothing could be read for this device: its documents are behind a sign-in or yielded no text. |
| SEL-734/734T | ipsec | - | unknown | Nothing could be read for this device: its documents are behind a sign-in or yielded no text. |
| SEL-734/734T | cip_security | - | unknown | Nothing could be read for this device: its documents are behind a sign-in or yielded no text. |
| SEL-734/734T | authentication | - | unknown | Nothing could be read for this device: its documents are behind a sign-in or yielded no text. |
| SEL-734/734T | encryption | - | unknown | Nothing could be read for this device: its documents are behind a sign-in or yielded no text. |
| SEL-734/734T | ssh | - | unknown | Nothing could be read for this device: its documents are behind a sign-in or yielded no text. |
| SEL-734/734T | integrity | - | unknown | Nothing could be read for this device: its documents are behind a sign-in or yielded no text. |
| SEL-735 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-735 | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-735 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-735 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-735 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-735 | encryption | Meter data to SCADA through a separate RTAC | conditional: external gateway only | Encryption is attributed to a separate SEL RTAC in front of the meter, not to the meter. |
| SEL-735 | ssh | - | unknown | 1 passages mention SSH in the sources read (2 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SEL-735 | integrity | - | unknown | 1 passages mention integrity in the sources read (2 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SEL-2664S | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2664S | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2664S | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2664S | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2664S | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2664S | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2664S | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-2664S | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-351A | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-351A | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-351A | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-351A | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-351A | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-351A | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-351A | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-351A | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-387 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-387 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-387 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-387 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-387 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-387 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-387 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-387 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-421 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-421 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-421 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-421 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-421 | authentication | IEC 61850 MMS server | supported | The data sheet states that the relay can require authentication of MMS clients when a setting in the CID file enables it. Nothing is stated about encryption of MMS or about DNP3. |
| SEL-421 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-421 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SEL-421 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 datasheet, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Easergy MiCOM C434 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Easergy MiCOM C434 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Easergy MiCOM C434 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Easergy MiCOM C434 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Easergy MiCOM C434 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Easergy MiCOM C434 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Easergy MiCOM C434 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Easergy MiCOM C434 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAGE Remote Terminal Units | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAGE Remote Terminal Units | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAGE Remote Terminal Units | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAGE Remote Terminal Units | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAGE Remote Terminal Units | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAGE Remote Terminal Units | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAGE Remote Terminal Units | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAGE Remote Terminal Units | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAITEL Remote Terminal Unit & Controller | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAITEL Remote Terminal Unit & Controller | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAITEL Remote Terminal Unit & Controller | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAITEL Remote Terminal Unit & Controller | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAITEL Remote Terminal Unit & Controller | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAITEL Remote Terminal Unit & Controller | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAITEL Remote Terminal Unit & Controller | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SAITEL Remote Terminal Unit & Controller | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SCADAPack 500E | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SCADAPack 500E | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SCADAPack 500E | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SCADAPack 500E | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SCADAPack 500E | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SCADAPack 500E | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SCADAPack 500E | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SCADAPack 500E | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION7550 RTU | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION7550 RTU | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION7550 RTU | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION7550 RTU | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION7550 RTU | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION7550 RTU | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION7550 RTU | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION7550 RTU | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic EM4200 Series Enercept | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic EM4200 Series Enercept | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic EM4200 Series Enercept | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic EM4200 Series Enercept | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic EM4200 Series Enercept | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic EM4200 Series Enercept | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic EM4200 Series Enercept | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic EM4200 Series Enercept | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM3000 Power Meters | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM3000 Power Meters | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM3000 Power Meters | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM3000 Power Meters | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM3000 Power Meters | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM3000 Power Meters | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM3000 Power Meters | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM3000 Power Meters | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM5000 Power Meters | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM5000 Power Meters | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM5000 Power Meters | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM5000 Power Meters | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM5000 Power Meters | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM5000 Power Meters | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM5000 Power Meters | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM5000 Power Meters | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM8000 Power Quality Meters | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM8000 Power Quality Meters | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM8000 Power Quality Meters | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM8000 Power Quality Meters | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM8000 Power Quality Meters | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM8000 Power Quality Meters | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM8000 Power Quality Meters | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic™ PM8000 Power Quality Meters | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PM800 series | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PM800 series | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PM800 series | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PM800 series | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PM800 series | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PM800 series | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PM800 series | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PM800 series | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Enercept | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Enercept | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Enercept | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Enercept | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Enercept | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Enercept | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Enercept | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Enercept | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Energy Meters | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Energy Meters | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Energy Meters | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Energy Meters | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Energy Meters | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Energy Meters | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Energy Meters | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic Energy Meters | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION6200 series | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION6200 series | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION6200 series | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION6200 series | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION6200 series | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION6200 series | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION6200 series | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| PowerLogic ION6200 series | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M171/M172 Logic Controller | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M171/M172 Logic Controller | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M171/M172 Logic Controller | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M171/M172 Logic Controller | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M171/M172 Logic Controller | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M171/M172 Logic Controller | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M171/M172 Logic Controller | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M171/M172 Logic Controller | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M241 Micro PLC | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M241 Micro PLC | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M241 Micro PLC | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M241 Micro PLC | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M241 Micro PLC | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M241 Micro PLC | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M241 Micro PLC | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M241 Micro PLC | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M258 Compact PLC for Machine Automation | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M258 Compact PLC for Machine Automation | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M258 Compact PLC for Machine Automation | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M258 Compact PLC for Machine Automation | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M258 Compact PLC for Machine Automation | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M258 Compact PLC for Machine Automation | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M258 Compact PLC for Machine Automation | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon M258 Compact PLC for Machine Automation | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon MCM | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon MCM | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon MCM | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon MCM | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon MCM | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon MCM | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon MCM | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon MCM | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Compact PLC | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Compact PLC | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Compact PLC | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Compact PLC | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Compact PLC | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Compact PLC | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Compact PLC | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Compact PLC | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon LMC058 / LMC078 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon LMC058 / LMC078 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon LMC058 / LMC078 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon LMC058 / LMC078 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon LMC058 / LMC078 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon LMC058 / LMC078 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon LMC058 / LMC078 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon LMC058 / LMC078 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon Premium PAC | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon Premium PAC | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon Premium PAC | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon Premium PAC | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon Premium PAC | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon Premium PAC | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon Premium PAC | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Modicon Premium PAC | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Twido - Programmable Controller | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Twido - Programmable Controller | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Twido - Programmable Controller | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Twido - Programmable Controller | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Twido - Programmable Controller | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Twido - Programmable Controller | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Twido - Programmable Controller | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Twido - Programmable Controller | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P59x | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P59x | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P59x | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P59x | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P59x | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P59x | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P59x | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P59x | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P841 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P841 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P841 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P841 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P841 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P841 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P841 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P841 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 80 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 80 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 80 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 80 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 80 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 80 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 80 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 80 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Vamp Arc Protection Relay System | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Vamp Arc Protection Relay System | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Vamp Arc Protection Relay System | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Vamp Arc Protection Relay System | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Vamp Arc Protection Relay System | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Vamp Arc Protection Relay System | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Vamp Arc Protection Relay System | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Vamp Arc Protection Relay System | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P22x | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P22x | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P22x | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P22x | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P22x | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P22x | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P22x | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P22x | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P521 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P521 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P521 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P521 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P521 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P521 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P521 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P521 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P821 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P821 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P821 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P821 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P821 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P821 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P821 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MiCOM P821 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 20 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 20 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 20 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 20 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 20 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 20 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 20 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Sepam series 20 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Bay controller – SIPROTEC 6MD86 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 document of unconfirmed type, 1 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Bay controller – SIPROTEC 6MD86 | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 document of unconfirmed type, 1 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Bay controller – SIPROTEC 6MD86 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 document of unconfirmed type, 1 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Bay controller – SIPROTEC 6MD86 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 document of unconfirmed type, 1 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Bay controller – SIPROTEC 6MD86 | authentication | - | unknown | 2 passages mention authentication in the sources read (2 document of unconfirmed type, 1 product page, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Bay controller – SIPROTEC 6MD86 | authentication | Network access (IEEE 802.1X) | supported | Authenticated network access is a property of the network port, not of a control protocol. |
| Bay controller – SIPROTEC 6MD86 | encryption | - | unknown | 1 passages mention encryption in the sources read (2 document of unconfirmed type, 1 product page, 1 datasheet). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Bay controller – SIPROTEC 6MD86 | encryption | DIGSI engineering tool connection | supported | Stated for the engineering tool connection of the SIPROTEC 5 family, not for the substation protocols. |
| Bay controller – SIPROTEC 6MD86 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 document of unconfirmed type, 1 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Bay controller – SIPROTEC 6MD86 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 document of unconfirmed type, 1 product page, 1 datasheet). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SICAM A8000 Series | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (3 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SICAM A8000 Series | tls | Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) | supported | The catalogue table lists TLS for IEC 60870-5-104, IEC 61850 and DNP3i under secure communication. Catalogue-level statement for the device family. |
| SICAM A8000 Series | ipsec | - | unknown | 11 passages mention IPsec in the sources read (3 document of unconfirmed type, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SICAM A8000 Series | ipsec | IP network layer | supported | IPsec encryption is named on the product page; which traffic it carries is a matter of configuration. |
| SICAM A8000 Series | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (3 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SICAM A8000 Series | authentication | - | unknown | 10 passages mention authentication in the sources read (3 document of unconfirmed type, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SICAM A8000 Series | encryption | Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) | supported | TLS is listed for the three protocols, and the catalogue names TLS encryption among the security features. |
| SICAM A8000 Series | ssh | - | unknown | 3 passages mention SSH in the sources read (3 document of unconfirmed type, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| SICAM A8000 Series | integrity | - | unknown | 1 passages mention integrity in the sources read (3 document of unconfirmed type, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Substation automation unit | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (3 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Substation automation unit | tls | Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) | supported | The catalogue table lists TLS for IEC 60870-5-104, IEC 61850 and DNP3i under secure communication. Catalogue-level statement for the device family. |
| Substation automation unit | ipsec | - | unknown | 11 passages mention IPsec in the sources read (3 document of unconfirmed type, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Substation automation unit | ipsec | IP network layer | supported | IPsec encryption is named on the product page; which traffic it carries is a matter of configuration. |
| Substation automation unit | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (3 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Substation automation unit | authentication | - | unknown | 10 passages mention authentication in the sources read (3 document of unconfirmed type, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Substation automation unit | encryption | Telecontrol and station protocols to master or slave (IEC 60870-5-104, IEC 61850, DNP3i) | supported | TLS is listed for the three protocols, and the catalogue names TLS encryption among the security features. |
| Substation automation unit | ssh | - | unknown | 3 passages mention SSH in the sources read (3 document of unconfirmed type, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Substation automation unit | integrity | - | unknown | 2 passages mention integrity in the sources read (3 document of unconfirmed type, 1 product page). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| MAB-Multipurpose-Automation-Box | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MAB-Multipurpose-Automation-Box | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MAB-Multipurpose-Automation-Box | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MAB-Multipurpose-Automation-Box | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MAB-Multipurpose-Automation-Box | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MAB-Multipurpose-Automation-Box | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MAB-Multipurpose-Automation-Box | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| MAB-Multipurpose-Automation-Box | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Power quality recorder - SICAM Q200 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Power quality recorder - SICAM Q200 | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Power quality recorder - SICAM Q200 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Power quality recorder - SICAM Q200 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Power quality recorder - SICAM Q200 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Power quality recorder - SICAM Q200 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Power quality recorder - SICAM Q200 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Power quality recorder - SICAM Q200 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SENTRON measuring devices for energy transparency | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Digital Transducer - SICAM T | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Digital Transducer - SICAM T | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Digital Transducer - SICAM T | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Digital Transducer - SICAM T | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Digital Transducer - SICAM T | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Digital Transducer - SICAM T | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Digital Transducer - SICAM T | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Digital Transducer - SICAM T | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1200 G2 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1200 G2 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1200 G2 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1200 G2 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1200 G2 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1200 G2 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1200 G2 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1200 G2 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 R/H CPUs - High Availability | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 R/H CPUs - High Availability | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 R/H CPUs - High Availability | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 R/H CPUs - High Availability | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 R/H CPUs - High Availability | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 R/H CPUs - High Availability | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 R/H CPUs - High Availability | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 R/H CPUs - High Availability | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 Software Controller | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 Software Controller | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 Software Controller | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 Software Controller | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 Software Controller | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 Software Controller | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 Software Controller | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-1500 Software Controller | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-400 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-400 | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-400 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-400 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-400 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-400 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-400 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIMATIC S7-400 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | tls | - | unknown | 2 passages mention TLS in the sources read (2 product page, 2 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | tls | DIGSI 5 engineering tool connection | supported | Stated for the engineering tool, family-wide. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | authentication | - | unknown | 64 passages mention authentication in the sources read (2 product page, 2 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | authentication | Network access (IEEE 802.1X) | conditional | Network access authentication from a firmware version. It is not authentication of a control protocol. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | encryption | - | unknown | 3 passages mention encryption in the sources read (2 product page, 2 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | encryption | DIGSI 5 engineering tool connection | supported | Stated for the engineering tool, not for the substation protocols. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page, 2 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | integrity | - | unknown | 2 passages mention integrity in the sources read (2 product page, 2 document of unconfirmed type). Those read for this draft concern management access, other products of the family or general statements; none establishes it for a control protocol of this device. AI draft: where there are many passages they were sampled, not read exhaustively. |
| Overcurrent and feeder protection – SIPROTEC 7SJ85 | integrity | DIGSI 5 engineering tool connection | supported | Stated for the TLS-secured connection to DIGSI 5, the web monitor or the cloud. |
| Reyrolle 7SR157: Check Synchronising | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR157: Check Synchronising | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR157: Check Synchronising | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR157: Check Synchronising | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR157: Check Synchronising | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR157: Check Synchronising | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR157: Check Synchronising | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR157: Check Synchronising | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR46: CT-powered overcurrent protection | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR46: CT-powered overcurrent protection | tls | - | unknown | No wording on TLS was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR46: CT-powered overcurrent protection | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR46: CT-powered overcurrent protection | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR46: CT-powered overcurrent protection | authentication | - | unknown | No wording on authentication was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR46: CT-powered overcurrent protection | encryption | - | unknown | No wording on encryption was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR46: CT-powered overcurrent protection | ssh | - | unknown | No wording on SSH was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| Reyrolle 7SR46: CT-powered overcurrent protection | integrity | - | unknown | No wording on integrity was found in the sources read for this device (1 product page, 1 document of unconfirmed type). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIPROTEC 7SY82 | dnp3_secure_authentication | - | unknown | No wording on DNP3 Secure Authentication was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIPROTEC 7SY82 | tls | - | unknown | No wording on TLS was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIPROTEC 7SY82 | ipsec | - | unknown | No wording on IPsec was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIPROTEC 7SY82 | cip_security | - | unknown | No wording on CIP Security was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIPROTEC 7SY82 | authentication | - | unknown | No wording on authentication was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIPROTEC 7SY82 | encryption | - | unknown | No wording on encryption was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIPROTEC 7SY82 | ssh | - | unknown | No wording on SSH was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |
| SIPROTEC 7SY82 | integrity | - | unknown | No wording on integrity was found in the sources read for this device (2 document of unconfirmed type, 1 product page). They are not a complete manual for it, so this does not establish that the capability is absent. |

## Unresolved cells

743 of 792 cells are unknown or not reviewed on every interface.

- Multilin C60/C95: dnp3_secure_authentication, tls, ipsec, cip_security, encryption, ssh, integrity
- Multilin D20E: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Multilin G100 Advanced Substation Gateway: dnp3_secure_authentication, ipsec, cip_security, integrity
- G500 Advanced Substation Gateway: dnp3_secure_authentication, ipsec, cip_security, integrity
- DART-Legacy: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Multilin D20MX - Advanced Substation Automation Controller: dnp3_secure_authentication, tls, ipsec, cip_security, encryption, integrity
- Multilin D400 Advanced Substation Gateway: dnp3_secure_authentication, ipsec, cip_security, encryption, integrity
- Multilin H500 - Legacy: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- EPM 2200 Digital Power Meter: dnp3_secure_authentication, tls, ipsec, cip_security, encryption, ssh, integrity
- EPM 6010 Building Automation Power Meter: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- iSTAT i400 Standard Transducers: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- iSTAT M2x2 Communicating Measurement Centre: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- EPM 4000 Sub-meter (Discontinued): dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- EPM 5300 Power Metering System: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- EPM 7100 Power Quality Meter: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- EPM 9900 Advanced Power Quality Meter: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- BiTRONICS 70 Series - Legacy: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- IFC Time-overcurrent Relay: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Multilin 339: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Multilin 850: Advanced Feeder Protection & Bay Controller: dnp3_secure_authentication, tls, ipsec, cip_security, encryption, ssh, integrity
- P64 MiCOM 5th Generation: dnp3_secure_authentication, tls, ipsec, cip_security, integrity
- DFP200 Digital Feeder Relay (Discontinued): dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- DLPD Digital Line Protection System: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- KAVS Check Synchronising Relay: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Multilin A60 - Legacy: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MBCI, MCRI, MRTP AND MVTW – Legacy: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MiCOM Agile P24x - Legacy: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MiCOM Agile P541 & P542 Line Differential Protection: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- TCCV Directional Overcurrent Relay: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- 1408 PowerMonitor 1000: dnp3_secure_authentication, ipsec, cip_security, authentication, encryption, ssh, integrity
- 1420 PowerMonitor 500: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- 1426 PowerMonitor 5000: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- CompactLogix 5380 Controllers: dnp3_secure_authentication, tls, ipsec, ssh
- ControlLogix 5590 Controllers: dnp3_secure_authentication, tls, ipsec, authentication, encryption, ssh, integrity
- LogixEdge Controllers: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Micro870 Controllers: tls, ipsec, cip_security, encryption, ssh, integrity
- CompactLogix 1768 Controllers: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Micro830 Controllers: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MicroLogix 1100 Controllers: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MicroLogix 1200 Controllers: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- CompactLogix 5370 Controllers: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SLC 500 Controllers: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Bulletin 865 Motor-feeder Protection Relays: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Bulletin 857 Motor-feeder Protection Relays: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SEL-2431: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SEL-3505/3505-3: dnp3_secure_authentication, ipsec, cip_security, ssh, integrity
- SEL-3560: dnp3_secure_authentication, ipsec, cip_security, integrity
- SEL Real-Time Automation Controller (RTAC): dnp3_secure_authentication, tls, ipsec, cip_security, encryption, ssh, integrity
- SEL-734/734T: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SEL-735: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, ssh, integrity
- SEL-2664S: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SEL-351A: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SEL-387: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SEL-421: dnp3_secure_authentication, tls, ipsec, cip_security, encryption, ssh, integrity
- Easergy MiCOM C434: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SAGE Remote Terminal Units: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SAITEL Remote Terminal Unit & Controller: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SCADAPack 500E: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- PowerLogic ION7550 RTU: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- PowerLogic EM4200 Series Enercept: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- PowerLogic™ PM3000 Power Meters: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- PowerLogic™ PM5000 Power Meters: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- PowerLogic™ PM8000 Power Quality Meters: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- PM800 series: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- PowerLogic Enercept: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- PowerLogic Energy Meters: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- PowerLogic ION6200 series: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Modicon M171/M172 Logic Controller: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Modicon M241 Micro PLC: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Modicon M258 Compact PLC for Machine Automation: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Modicon MCM: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Compact PLC: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Modicon LMC058 / LMC078: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Modicon Premium PAC: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Twido - Programmable Controller: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MiCOM P59x: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MiCOM P841: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Sepam series 80: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Vamp Arc Protection Relay System: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MiCOM P22x: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MiCOM P521: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- MiCOM P821: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Sepam series 20: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Bay controller – SIPROTEC 6MD86: dnp3_secure_authentication, tls, ipsec, cip_security, ssh, integrity
- SICAM A8000 Series: dnp3_secure_authentication, cip_security, authentication, ssh, integrity
- Substation automation unit: dnp3_secure_authentication, cip_security, authentication, ssh, integrity
- MAB-Multipurpose-Automation-Box: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SENTRON measuring devices for energy transparency: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Power quality recorder - SICAM Q200: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SENTRON measuring devices for energy transparency: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Digital Transducer - SICAM T: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SIMATIC S7-1200 G2: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SIMATIC S7-1500 R/H CPUs - High Availability: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SIMATIC S7-1500 Software Controller: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SIMATIC S7-400: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Overcurrent and feeder protection – SIPROTEC 7SJ85: dnp3_secure_authentication, ipsec, cip_security, ssh
- Reyrolle 7SR157: Check Synchronising: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- Reyrolle 7SR46: CT-powered overcurrent protection: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity
- SIPROTEC 7SY82: dnp3_secure_authentication, tls, ipsec, cip_security, authentication, encryption, ssh, integrity

## What was read

Extracted sources by vendor and document type. A type marked "suggested" is the tool's guess from the title, URL and opening text until a reviewer confirms it in the source notes. A vendor whose sources are mostly product pages and brochures has little that can settle a capability either way.

| Vendor | Document type | Sources | PDF pages |
|---|---|---|---|
| GE Vernova / Multilin | datasheet (suggested) | 25 | 239 |
| GE Vernova / Multilin | manual | 5 | 1695 |
| GE Vernova / Multilin | manual (suggested) | 12 | 5198 |
| GE Vernova / Multilin | not established | 28 | 56 |
| GE Vernova / Multilin | product page (suggested) | 93 | - |
| Rockwell Automation / Allen-Bradley | datasheet (suggested) | 1 | 15 |
| Rockwell Automation / Allen-Bradley | manual | 11 | 3189 |
| Rockwell Automation / Allen-Bradley | manual (suggested) | 17 | 4934 |
| Rockwell Automation / Allen-Bradley | not established | 13 | 225 |
| Rockwell Automation / Allen-Bradley | product page (suggested) | 15 | - |
| SEL | datasheet (suggested) | 7 | 160 |
| SEL | not established | 11 | 144 |
| Schneider Electric | product page (suggested) | 29 | - |
| Siemens | datasheet (suggested) | 1 | 8 |
| Siemens | not established | 20 | 1300 |
| Siemens | product page (suggested) | 20 | - |

## Sources examined

Type, number, revision and document date are what a reviewer confirmed or read off the document; "not established" and "suggested" mean nobody has yet. Types are listed in the README from most to least direct about what one product and firmware can do. Titles and PDF dates are what the file says about itself, and a PDF creation date is not necessarily a publication date.

Of 308 extracted sources, the 39 cited by a review row are listed here. sources.json lists all of them.

| Ref | Product | Document | Type | Number and revision | Document date | Retrieved | SHA-256 | URL |
|---|---|---|---|---|---|---|---|---|
| S1 | Multilin C60/C95 | Multilin C60/C95 / GE Vernova / Electrification | suggested: product page | not established | not established | 2026-10-13 | 5309146db1a81b72afcf2da4033331add22a169dec39a015e74360f3aa1d5bcf | https://www.gevernova.com/electrification/automation/protection-control-metering/controllers/multilin-c60c95 |
| S14 | Multilin G100 Advanced Substation Gateway | Multilin G100 Brochure, 12 PDF pages, PDF created 2025-06-17 | suggested: datasheet | not established | not established | 2026-10-13 | 82bff561bfbf9dfb951750faac5fdc91703c2f4eb0794780ecd09ca078222df6 | https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G100-Brochure-EN-33196-Hybrid-202504-R002.pdf |
| S20 | G500 Advanced Substation Gateway | Multilin G500 Brochure, 14 PDF pages, PDF created 2025-06-17 | suggested: datasheet | not established | not established | 2026-10-13 | 625c825ac70f491433ec62b8c2fadd8cd4fa7948da39fa9c3acaa84cb7a162f3 | https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G500-Advanced-Substation-Gateway-Brochure-EN-35437-Hybrid-202504-R002.pdf |
| S24 | Multilin D20MX - Advanced Substation Automation Controller | Multilin D20MX - Advanced Substation Automation Controller | suggested: product page | not established | not established | 2026-10-13 | 606ea8b8fa2eaeabed88c4174279160200b616ca85254f473e1555dc2da29317 | https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d20mx-substation-controller-legacy |
| S31 | Multilin D20MX - Advanced Substation Automation Controller | Multilin D20MX Brochure, 11 PDF pages, PDF created 2025-07-10 | suggested: datasheet | not established | not established | 2026-10-13 | e24d9829a26f745eec2f83f9a7aae68c4e2b949a5e9eb80b8d3ba5a47a7395e2 | https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-D20MX-Brochure-EN-12711G-Hybrid-202504-R001.pdf |
| S33 | Multilin D400 Advanced Substation Gateway | Multilin D400 Advanced Substation Gateway / GE Vernova / Electrification | suggested: product page | not established | not established | 2026-10-13 | 111484140771b5119fdf5785ea3f87928d9a96dbffc4663b4c603968db3b1b69 | https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d400-legacy |
| S52 | EPM 2200 Digital Power Meter | EPM 2200 Electronic Meter, 123 PDF pages, PDF created 2025-11-04 | manual, complete | not established | not established | 2026-10-13 | de86571fa14dce0e479e5a9aa116cd6967a4a779d6a5049651ec0e198cc0fe43 | https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm2200-a7-GEV.pdf |
| S75 | iSTAT M2x2 Communicating Measurement Centre | iSTAT M2x2 Standard Measurement Centre Manual, 72 PDF pages, PDF created 2025-04-04 | manual, complete | not established | not established | 2026-10-13 | 824751a3315820dc8c703d40eb51370f5dad9253b35f850fea287a3ccdd61750 | https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/M2x2-EN-M-F-new-GEV.pdf |
| S96 | EPM 9900 Advanced Power Quality Meter | Multilin™ EPM 9000 Series DNP Guide, 272 PDF pages, PDF created 2016-10-28 | manual, complete | not established | not established | 2026-10-13 | 3ee2beb473913a64c2f1bc631bea717a78b07fb7eb53b3a547e6486ae7823fbb | https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf |
| S113 | Multilin 850: Advanced Feeder Protection & Bay Controller | Multilin 850: Advanced Feeder Protection & Bay Controller / GE Vernova / Electrification | suggested: product page | not established | not established | 2026-10-13 | 2ae9e6218aa6c105e854b81b14ae784c5bffdef6f64c29dff8971538fc9311d6 | https://www.gevernova.com/electrification/automation/protection-control-metering/feeder-protection/multilin-850 |
| S127 | P64 MiCOM 5th Generation | Technical Manual, 672 PDF pages, PDF created 2024-08-06 | manual, complete | not established | not established | 2026-10-13 | f4622b24c3836f3be495cd4f8f007caab13e73ea95a514af31bb55dd66810aa5 | https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf |
| S154 | MiCOM Agile P24x - Legacy | untitled, 556 PDF pages, PDF created 2021-06-07 | manual, complete | not established | not established | 2026-10-13 | e4044ff020d15ee3e6a25143faeba5531594d404b9b354568b736ffce21a2979 | https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf |
| S166 | 1408 PowerMonitor 1000 | PowerMonitor 1000 Unit User Manual, publication 1408-UM002E-EN-P, 216 PDF pages, PDF created 2023-04-03 | manual, complete | not established | not established | 2026-10-13 | b9dc8c5001d967b5c4c256c494d6336e49456e0934a0a521c3c55122f0742135 | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1408-um002_-en-p.pdf |
| S172 | 1420 PowerMonitor 500 | PowerMonitor 500 Unit User Manual, Publication 1420-UM001G-EN-P, 108 PDF pages, PDF created 2018-04-19 | manual, complete | not established | not established | 2026-10-13 | ddf05d9724fd54e1519d3725262cf653021b7c70055ea9246e74722968235177 | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1420-um001_-en-p.pdf |
| S178 | 1426 PowerMonitor 5000 | PowerMonitor 5000 Unit User Manual, 406 PDF pages, PDF created 2022-10-28 | manual, complete | not established | not established | 2026-10-13 | 52590c7042e78060a3e52e8c4bf0ee9eb169223258f75da4d4170d448106d4ba | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1426-um001_-en-p.pdf |
| S182 | CompactLogix 5380 Controllers | CompactLogix 5380 Controllers / Rockwell Automation / US | suggested: product page | not established | not established | 2026-10-13 | aaee878babd4875dbce5f8fb92d0c4be18e7795df3186aa823cb22cbd4b628ed | https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/compactlogix-5380-controllers.html |
| S183 | CompactLogix 5380 Controllers | CompactLogix 5380 and Compact GuardLogix 5380 Controllers, 279 PDF pages, PDF created 2026-01-21 | suggested: manual | not established | not established | 2026-10-13 | ff0859a0af218eede722457f82308e3b540a4efc2c0e67f141736189e4ff7b3e | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/5069-um001_-en-p.pdf |
| S189 | ControlLogix 5590 Controllers | ControlLogix Controllers Brochure, 15 PDF pages, PDF created 2026-03-10 | suggested: datasheet | not established | not established | 2026-10-13 | 41b300314e61e97cec9a5032e290813688f008182933e4f2beda7d92dfb7d0f8 | https://literature.rockwellautomation.com/idc/groups/literature/documents/pp/1756-pp001_-en-p.pdf |
| S192 | Micro870 Controllers | Micro870 Controllers / Rockwell Automation / US | suggested: product page | not established | not established | 2026-10-13 | 9496a20d291df382e2f5e6ae4f233cf7612c9b2ecc88176f776fb6fcc6840bdd | https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/micro870-controllers.html |
| S202 | CompactLogix 5370 Controllers | CompactLogix 5370 Controllers User Manual, 272 PDF pages, PDF created 2023-04-26 | manual, complete | not established | not established | 2026-10-13 | 121a3688b4bb27c9f61db5fa7ec7c428fa3419dd8a00e230c6fa1f1e682229dd | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1769-um021_-en-p.pdf |
| S207 | SLC 500 Controllers | SLC 500 Modular Hardware Style User Manual, 296 PDF pages, PDF created 2008-06-20 | manual, complete | not established | not established | 2026-10-13 | c48aa3e480261c37022545e07fb9fa002ef0f1dcc07dffecb2fa257c623b9a49 | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um011_-en-p.pdf |
| S208 | SLC 500 Controllers | 1747-6.21, SLC 500 Fixed Hardware Style Installation and Operation Manual, 223 PDF pages | manual, complete | not established | not established | 2026-10-13 | dc80618c321d7baa993cab6eabbca91ee57c13f45598822ef7ad9c07614ed409 | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/1747-um009_-en-p.pdf |
| S209 | SLC 500 Controllers | SLC 500 Instruction Set Reference Manual, 694 PDF pages, PDF created 2008-11-20 | manual, complete | not established | not established | 2026-10-13 | 188c3d2a416fdb46970ed9ac41daa00316528ec698e55fba59376af52bd898e7 | https://literature.rockwellautomation.com/idc/groups/literature/documents/rm/1747-rm001_-en-p.pdf |
| S214 | Bulletin 865 Motor-feeder Protection Relays | Differential Protection Relay, Bulletin 865, Series A, 296 PDF pages, PDF created 2020-05-06 | manual, complete | not established | not established | 2026-10-13 | aad67a88438e1e4b25f520659c9877d9c4b9d55ee79e21c845bf564e867a9904 | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf |
| S216 | Bulletin 857 Motor-feeder Protection Relays | Bulletin 857/865 Protection Systems IEC 61850 Interface Configuration Instructions, 104 PDF pages, PDF created 2018-03-13 | manual, complete | not established | not established | 2026-10-13 | d85a90e0536232dc9d0ae66b22b2b3483342a6cdfcffc587610e1bd1d115632c | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um004_-en-p.pdf |
| S219 | Bulletin 857 Motor-feeder Protection Relays | Protection System for Feeder and Motor Protection, Bulletin 857 Series A, 504 PDF pages, PDF created 2020-06-10 | manual, complete | not established | not established | 2026-10-13 | 7819346e871e2162f6e4522740509d7f940d461ee7be70f5b76882eec383feac | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf |
| S220 | Bulletin 857 Motor-feeder Protection Relays | EtherNet/IP Configuration Details for 857/865 Protection System User Manual, 70 PDF pages, PDF created 2018-07-06 | manual, complete | not established | not established | 2026-10-13 | 23f796180a1947583684eda489a982f12a07a6430a3ca25e582030eb0a8676d7 | https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um005_-en-p.pdf |
| S223 | SEL-3505/3505-3 | SEL-3505/SEL-3505-3 Data Sheet, 16 PDF pages, PDF created 2000-03-01 | suggested: datasheet | not established | not established | 2026-10-13 | ce6200504e73b92fcfe98b5aafe916376ae1c6a8a738fc1510a195658e9edc06 | https://selinc.com/api/download/100620/ |
| S225 | SEL-3560 | untitled, 12 PDF pages, PDF created 2025-01-02 | not established | not established | not established | 2026-10-13 | dbccc3cb21530a77b87aa92120c632956721d3ce9b4830c326fc289fe6a01105 | https://selinc.com/api/download/124708/ |
| S227 | SEL Real-Time Automation Controller (RTAC) | untitled, 12 PDF pages, PDF created 2026-01-23 | not established | not established | not established | 2026-10-13 | 8e7993deb90fd53bd75eeb1344eb5f1dcc7782fcfce61ad6f6697d538064f8cc | https://selinc.com/api/download/111397/ |
| S230 | SEL-735 | untitled, 16 PDF pages, PDF created 2025-10-29 | not established | not established | not established | 2026-10-13 | 9529adc95bc0b5bb27b2aa8104318fcbba5d9b3c4a4e133a4c98def3380b6859 | https://selinc.com/api/download/128658/ |
| S237 | SEL-421 | SEL-421-4, -5 Data Sheet, 32 PDF pages, PDF created 2013-12-23 | suggested: datasheet | not established | not established | 2026-10-13 | 6ba9a29a501160165015de63a1ed0cd4df2bb48d89508eb98c9206cc8f8ffa36 | https://selinc.com/api/download/99010/ |
| S268 | Bay controller – SIPROTEC 6MD86 | Bay controller – SIPROTEC 6MD86 / Siemens | suggested: product page | not established | not established | 2026-10-13 | 10f585c2a94d9be825c56bcc289d6584153e2a99c1f77af2cf68fc46168b781f | https://www.siemens.com/en-us/products/siprotec/6md86/ |
| S269 | Bay controller – SIPROTEC 6MD86 | SIPROTEC 5 - Brochure (US Version), 8 PDF pages, PDF created 2017-11-07 | suggested: datasheet | not established | not established | 2026-10-13 | eaefff440a901a7b2ad0e8b99f900a525be03b7d8a5bdd361883218c16774499 | https://assets.new.siemens.com/siemens/assets/api/uuid:88ed23f5-d148-49a4-b830-6e301094e0ab/emdgb10022004ausbrochuresiprotec5us.pdf |
| S272 | SICAM A8000 Series | SICAM A8000 Series / Siemens | suggested: product page | not established | not established | 2026-10-13 | e498282efa5296491aa81d2748c6d3c9f60e1b4ebd53a4ad49879e66e496a1c0 | https://www.siemens.com/en-us/products/sicam/a8000/ |
| S273 | SICAM A8000 Series | Substation and Automation Catalog Edition 9, 240 PDF pages, PDF created 2026-08-04 | not established | not established | not established | 2026-10-13 | eacde7831087ddb6c0cc45d741cdfa4e3b760b301a4a9bb933a84a1a609c2910 | https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf |
| S276 | Substation automation unit | Substation automation unit / Siemens | suggested: product page | not established | not established | 2026-10-13 | aa3bfd8b779c1c5de17ec110f851746b9f2b389361baad7900b9a995a83c94e3 | https://www.siemens.com/en-us/products/sicam/a8000-cp-8050/ |
| S277 | Substation automation unit | Substation and Automation Catalog Edition 9, 240 PDF pages, PDF created 2026-08-04 | not established | not established | not established | 2026-10-13 | eacde7831087ddb6c0cc45d741cdfa4e3b760b301a4a9bb933a84a1a609c2910 | https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf |
| S299 | Overcurrent and feeder protection – SIPROTEC 7SJ85 | SIPROTEC 5 - Catalog, 456 PDF pages, PDF created 2020-12-21 | not established | not established | not established | 2026-10-13 | 7b63d02274b8497e00fa7f77c5d6c7814c53ad861d036f97784c775bce0923a4 | https://assets.new.siemens.com/siemens/assets/api/uuid:279cb01d-fd3b-4df4-8e04-f1fe98b81d6b/SIPROTEC-5-Catalog-EN.pdf |

## Sources without extracted text

| Product | URL | Outcome |
|---|---|---|
| Multilin C60/C95 | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=c60&type=3&node_id=4547 | link leads to a sign-in page; not requested |
| Multilin D20E | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=d20e&type=3&node_id=4553 | link leads to a sign-in page; not requested |
| Multilin G100 Advanced Substation Gateway | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=G100&type=3&node_id=4550 | link leads to a sign-in page; not requested |
| G500 Advanced Substation Gateway | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=G500&type=3&node_id=4551 | link leads to a sign-in page; not requested |
| Multilin D20MX - Advanced Substation Automation Controller | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=d20mx&type=3&node_id=4861 | link leads to a sign-in page; not requested |
| EPM 5300 Power Metering System | https://www.gevernova.com/electrification/resources?prod=em-epm5300p&type=1&node_id=4894 | duplicate of 2fc5afa65f7b428e93a4 |
| EPM 7100 Power Quality Meter | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=epm7100&type=3&node_id=4899 | link leads to a sign-in page; not requested |
| BiTRONICS 70 Series - Legacy | https://www.gevernova.com/electrification/resources?prod=70Series&type=1L&node_id=4840 | duplicate of 47b082bf505ce6aab8cd |
| IFC Time-overcurrent Relay | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=ifc&type=3&node_id=4499 | link leads to a sign-in page; not requested |
| Multilin 339 | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=339&type=3&node_id=4493 | link leads to a sign-in page; not requested |
| Multilin 850: Advanced Feeder Protection & Bay Controller | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=850&type=3&node_id=4480 | link leads to a sign-in page; not requested |
| P64 MiCOM 5th Generation | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=P64X&type=3&node_id=4110 | link leads to a sign-in page; not requested |
| KAVS Check Synchronising Relay | https://www.gevernova.com/electrification/resources?prod=KAVS&type=1&node_id=5127 | duplicate of fe58041dc24e293f8ef7 |
| Multilin A60 - Legacy | https://www.gevernova.com/electrification/resources?prod=A60&type=1&node_id=4846 | duplicate of 43b6c6e6b43572b7befb |
| Multilin A60 - Legacy | https://www.gevernova.com/electrification/resources?prod=A60&type=4&node_id=4846 | duplicate of 43b6c6e6b43572b7befb |
| MiCOM Agile P24x - Legacy | https://www.gevernova.com/electrification/passport/login?destination=/electrification/resources?prod=P24x&type=3&node_id=4489 | link leads to a sign-in page; not requested |
| MiCOM Agile P541 & P542 Line Differential Protection | https://www.gevernova.com/grid-solutions/sites/default/files/2025-12/GER-4938-P541-B.pdf | duplicate of 95e2e24b44a3cd3fbe6e |
| MiCOM Agile P541 & P542 Line Differential Protection | https://www.gevernova.com/grid-solutions/sites/default/files/2025-12/GER-4938-P542-B.pdf | duplicate of f4c1504a7e241dce82cb |
| SEL-2431 | https://selinc.com/api/download/3608/ | ValueError: login required: redirected to https://selinc.com/login/?returnUrl=https://selinc.com%2Fapi%2Fdownload%2F3608%2F |
| SEL-3505/3505-3 | https://selinc.com/api/download/100623/ | ValueError: login required: redirected to https://selinc.com/login/?returnUrl=https://selinc.com%2Fapi%2Fdownload%2F100623%2F |
| SEL-3560 | https://selinc.com/api/download/126035/ | ValueError: login required: redirected to https://selinc.com/login/?returnUrl=https://selinc.com%2Fapi%2Fdownload%2F126035%2F |
| SEL Real-Time Automation Controller (RTAC) | https://selinc.com/api/download/122716/ | ValueError: unsupported content type: application/x-zip-compressed |
| SEL-734/734T | https://selinc.com/api/download/3954/ | ValueError: login required: redirected to https://selinc.com/login/?returnUrl=https://selinc.com%2Fapi%2Fdownload%2F3954%2F |
| SEL-734/734T | https://selinc.com/api/download/1386/ | ValueError: no extractable text; OCR/manual review required |
| SEL-735 | https://selinc.com/api/download/97801/ | ValueError: login required: redirected to https://selinc.com/login/?returnUrl=https://selinc.com%2Fapi%2Fdownload%2F97801%2F |
| SEL-2664S | https://selinc.com/api/download/105260/ | ValueError: login required: redirected to https://selinc.com/login/?returnUrl=https://selinc.com%2Fapi%2Fdownload%2F105260%2F |
| SEL-351A | https://selinc.com/api/download/5520/ | ValueError: login required: redirected to https://selinc.com/login/?returnUrl=https://selinc.com%2Fapi%2Fdownload%2F5520%2F |
| SEL-387 | https://selinc.com/api/download/3636/ | ValueError: login required: redirected to https://selinc.com/login/?returnUrl=https://selinc.com%2Fapi%2Fdownload%2F3636%2F |
| SEL-421 | https://selinc.com/api/download/116330/ | ValueError: login required: redirected to https://selinc.com/login/?returnUrl=https://selinc.com%2Fapi%2Fdownload%2F116330%2F |
| SIMATIC S7-1200 G2 | https://www.siemens.com/catalog-st-70 | ValueError: robots unresolved: HTTP 403 |
| Reyrolle 7SR157: Check Synchronising | https://assets.new.siemens.com/siemens/assets/api/uuid:2ff7a1f9-2d04-4252-91c1-d11e6895ad51/Reyrolle-7SR157-Profile-EN.pdf | duplicate of 39a8e699a776cdf7bdba |

Review coverage: 792/792 product–capability cells. Unreviewed cells carry no result.

Evidence quotes: 49 of 49 rows with a result other than unknown carry a quote that was checked against the cited passage.

Unknown because a complete document is silent: 87 rows, each checked to cite only complete documents in which the search found no lead for that capability.

See findings.csv for source URLs, hashes, interface, firmware and review provenance, and devices.csv for lifecycle evidence. The percentages in the DNP3 section are shares of the devices in this run, not of installed devices or of traffic.
