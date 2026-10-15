# DNP3 security in public vendor documentation

Status: **AI draft; author review pending**. Run `sample_targeted_2026-10-15` (tool 2.2.1, extraction rules 1.4.1); 821 review rows, 0 confirmed by a person.

## DNP3 security

Catalogue entries whose own retrieved documents name DNP3, grouped by documented security. An entry without an applicable security finding remains unknown. Absence from the retrieved documents establishes neither lack of support nor plaintext operation. Authentication does not establish encryption, and an integrity-only statement does not establish authentication. DNP3 Secure Authentication version 5 (SAv5) provides authentication rather than payload confidentiality. Protection described for another or an unspecified control protocol is kept separate from DNP3-specific protection. These are unweighted sample counts, not vendor-wide estimates, installed-device settings or traffic measurements.

Left out by the device notes, because DNP3 is named only in documents about other products: EPM 2200 Digital Power Meter, EPM 6010 Building Automation Power Meter, EPM 7100 Power Quality Meter, 1408 PowerMonitor 1000, 1420 PowerMonitor 500, 1426 PowerMonitor 5000, Micro830 Controllers.

| DNP3 security documented | Currently listed | Legacy | Lifecycle unknown | Total |
|---|---|---|---|---|
| DNP3 over TLS or IPsec documented | 5 of 24 (21%) | 1 of 7 (14%) | 0 of 1 (0%) | 6 of 32 (19%) |
| DNP3 authentication documented; encryption not established | 1 of 24 (4%) | 0 of 7 (0%) | 0 of 1 (0%) | 1 of 32 (3%) |
| Control-traffic encryption documented; DNP3 scope not established | 3 of 24 (12%) | 0 of 7 (0%) | 0 of 1 (0%) | 3 of 32 (9%) |
| External encryption documented; DNP3 scope not established | 2 of 24 (8%) | 0 of 7 (0%) | 0 of 1 (0%) | 2 of 32 (6%) |
| A specific DNP3 security feature explicitly unsupported | 1 of 24 (4%) | 0 of 7 (0%) | 0 of 1 (0%) | 1 of 32 (3%) |
| DNP3 security not established from retrieved documents | 12 of 24 (50%) | 6 of 7 (86%) | 1 of 1 (100%) | 19 of 32 (59%) |
| Devices whose documents name DNP3 | 24 | 7 | 1 | 32 |

| Legacy | Lifecycle | Vendor | Model | Type | DNP3 security | Source |
|---|---|---|---|---|---|---|
| no | currently listed | GE Vernova / Multilin | G500 Advanced Substation Gateway | controller / RTU | DNP3 over TLS or IPsec documented | [S22 pdf-page:1](https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G500-Advanced-Substation-Gateway-Brochure-EN-35437-Hybrid-202504-R002.pdf) |
| no | currently listed | GE Vernova / Multilin | Multilin G100 Advanced Substation Gateway | controller / RTU | DNP3 over TLS or IPsec documented | [S16 pdf-page:1](https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-G100-Brochure-EN-33196-Hybrid-202504-R002.pdf) |
| no | currently listed | SEL | SEL Real-Time Automation Controller (RTAC) | controller / RTU | DNP3 over TLS or IPsec documented | [S236 pdf-page:10](https://selinc.com/api/download/112760/) |
| no | currently listed | Siemens | SICAM A8000 Series | controller / RTU | DNP3 over TLS or IPsec documented | [S286 pdf-page:12](https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf) |
| no | currently listed | Siemens | Substation automation unit | controller / RTU | DNP3 over TLS or IPsec documented | [S290 pdf-page:12](https://assets.new.siemens.com/siemens/assets/api/uuid:df58aadc-aa55-4293-a4a7-ceecdfc5b530/Substation-Automation-Catalog.pdf) |
| yes | discontinued, support not stated | GE Vernova / Multilin | Multilin D400 Advanced Substation Gateway | controller / RTU | DNP3 over TLS or IPsec documented | [S43 pdf-page:1](https://www.gevernova.com/electrification/sites/default/files/2025-09/Multilin-D400-Brochure-EN-12806D-Hybrid-202505-001.pdf) |
| no | currently listed | Rockwell Automation / Allen-Bradley | Micro870 Controllers | PLC | DNP3 authentication documented; encryption not established | [S198 html-block:61](https://www.rockwellautomation.com/en-us/products/hardware/programmable-controllers/micro870-controllers.html) |
| no | currently listed | SEL | SEL-3560 | controller / RTU | Control-traffic encryption documented; DNP3 scope not established | [S232 pdf-page:2](https://selinc.com/api/download/124708/) |
| no | currently listed | Siemens | Bay controller – SIPROTEC 6MD86 | controller / RTU | Control-traffic encryption documented; DNP3 scope not established | [S284 pdf-page:59](https://cache.industry.siemens.com/dl/files/375/109768375/att_1150302/v1/SIP5_Security_V09.60_Manual_C081-C_en.pdf) |
| no | currently listed | Siemens | Overcurrent and feeder protection – SIPROTEC 7SJ85 | protective relay | Control-traffic encryption documented; DNP3 scope not established | [S318 pdf-page:59](https://cache.industry.siemens.com/dl/files/375/109768375/att_1150302/v1/SIP5_Security_V09.60_Manual_C081-C_en.pdf) |
| no | currently listed | SEL | SEL-3505/3505-3 | controller / RTU | External encryption documented; DNP3 scope not established (conditional: Needs separate SEL serial or wireless encrypting devices.) | [S230 pdf-page:6](https://selinc.com/api/download/100620/) |
| no | currently listed | SEL | SEL-735 | meter | External encryption documented; DNP3 scope not established (conditional: Needs a separate SEL Real-Time Automation Controller as gateway.) | [S238 pdf-page:13](https://selinc.com/api/download/128658/) |
| no | currently listed | GE Vernova / Multilin | Multilin C60/C95 | controller / RTU | A specific DNP3 security feature explicitly unsupported | [S7 pdf-page:235](https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/c60/C60-1601-0100-85x-AP1-GEV.pdf) |
| no | currently listed | GE Vernova / Multilin | Multilin 339 | protective relay | DNP3 security not established from retrieved documents | [S112](https://www.gevernova.com/electrification/automation/protection-control-metering/motor-protection/multilin-339); [S116](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-339-Brochure-EN-12779O-Hybrid-202504-R003.pdf) |
| no | currently listed | GE Vernova / Multilin | Multilin 850: Advanced Feeder Protection & Bay Controller | protective relay | DNP3 security not established from retrieved documents | [S122](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-850-Brochure-PO-32050-Hybrid-202509-R001.pdf); [S123](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-850P-Brochure-EN-12739L-Hybrid-202504-R001.pdf); [S124](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-850-Brochure-GE-32050-Hybrid-202509-R002.pdf) (+3 more) |
| no | currently listed | GE Vernova / Multilin | Multilin D20E | controller / RTU | DNP3 security not established from retrieved documents | [S11](https://www.gevernova.com/electrification/sites/default/files/2025-11/Multilin-D20E-Brochure-EN-32042-Hybrid-202504-R002.pdf); [S12](https://www.gevernova.com/electrification/sites/default/files/2025-05/994-0145-D20E-Ethernet-IO-Module-Instruction-Manual-V100-R5.pdf) |
| no | currently listed | GE Vernova / Multilin | P64 MiCOM 5th Generation | protective relay | DNP3 security not established from retrieved documents | [S133](https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/p64-tm-en-1-gev.pdf); [S134](https://www.gevernova.com/electrification/sites/default/files/2025-09/MiCOM-Agile-P64-Brochure-EN-35502-Hybrid-202504-R002.pdf) |
| no | currently listed | GE Vernova / Multilin | iSTAT M2x2 Communicating Measurement Centre | meter | DNP3 security not established from retrieved documents | [S81](https://www.gevernova.com/electrification/sites/default/files/2025-11/iSTAT-M232-Communicating-Measurement-Centre-Brochure-EN-33180-Hybrid-202505-R002.pdf) |
| no | currently listed | SEL | SEL-2431 | controller / RTU | DNP3 security not established from retrieved documents | [S228](https://selinc.com/api/download/2835/); [S229](https://selinc.com/api/download/2910/) |
| no | currently listed | SEL | SEL-2664S | protective relay | DNP3 security not established from retrieved documents | [S239](https://selinc.com/api/download/105257/); [S240](https://selinc.com/api/download/104471/) |
| no | currently listed | SEL | SEL-351A | protective relay | DNP3 security not established from retrieved documents | [S241](https://selinc.com/api/download/5523/); [S242](https://selinc.com/api/download/5532/) |
| no | currently listed | SEL | SEL-387 | protective relay | DNP3 security not established from retrieved documents | [S243](https://selinc.com/api/download/292/); [S244](https://selinc.com/api/download/236/) |
| no | currently listed | SEL | SEL-421 | protective relay | DNP3 security not established from retrieved documents | [S245](https://selinc.com/api/download/99010/); [S246](https://selinc.com/api/download/222/); [S247](https://selinc.com/api/download/120794/) |
| no | currently listed | Siemens | Digital Transducer - SICAM T | meter | DNP3 security not established from retrieved documents | [S308](https://assets.new.siemens.com/siemens/assets/api/uuid:09a829eb-0676-4680-8f95-1adaba01a911/SICAM-PQ-Catalog.pdf) |
| no | currently listed | Siemens | Power quality recorder - SICAM Q200 | meter | DNP3 security not established from retrieved documents | [S299](https://assets.new.siemens.com/siemens/assets/api/uuid:09a829eb-0676-4680-8f95-1adaba01a911/SICAM-PQ-Catalog.pdf); [S300](https://assets.new.siemens.com/siemens/assets/api/uuid:16e30661-1286-49b8-b194-94516bb56fa6/SICAM-Q200-Profile-EN.pdf); [S301](https://cache.industry.siemens.com/dl/files/897/109744897/att_1053741/v1/SICAM_Q200_7KG97_CM_US.pdf) (+1 more) |
| yes | discontinued, support not stated | GE Vernova / Multilin | EPM 5300 Power Metering System | meter | DNP3 security not established from retrieved documents | [S84](https://www.gevernova.com/electrification/automation/protection-control-metering/epm-5300-legacy) |
| yes | discontinued, support not stated | GE Vernova / Multilin | EPM 9900 Advanced Power Quality Meter | meter | DNP3 security not established from retrieved documents | [S95](https://www.gevernova.com/electrification/automation/protection-control-metering/epm-9900-advanced-power-quality-meter-legacy); [S96](https://www.gevernova.com/electrification/resources?prod=epm9900&type=3&node_id=4903); [S100](https://www.gevernova.com/electrification/sites/default/files/resources/products/manuals/epm/epm9000-dnp-a1-GEV.pdf) (+2 more) |
| yes | discontinued, support not stated | GE Vernova / Multilin | Multilin D20MX - Advanced Substation Automation Controller | controller / RTU | DNP3 security not established from retrieved documents | [S26](https://www.gevernova.com/electrification/automation/protection-control-metering/multilin-d20mx-substation-controller-legacy); [S31](https://www.gevernova.com/electrification/sites/default/files/2025-12/Multilin-D20-Analog-Input-Module-Brochure-EN-12792-Hybrid-202505-R002.pdf); [S32](https://www.gevernova.com/electrification/sites/default/files/2025-12/Multilin-D20-Combination-Module-Brochure-EN-12802A-Hybrid-202505-R002.pdf) (+4 more) |
| yes | discontinued, support not stated | Rockwell Automation / Allen-Bradley | Bulletin 857 Motor-feeder Protection Relays | protective relay | DNP3 security not established from retrieved documents | [S226](https://literature.rockwellautomation.com/idc/groups/literature/documents/um/857-um001_-en-p.pdf) |
| yes | discontinued, support not stated | Rockwell Automation / Allen-Bradley | Bulletin 865 Motor-feeder Protection Relays | protective relay | DNP3 security not established from retrieved documents | [S221](https://literature.rockwellautomation.com/idc/groups/literature/documents/um/865-um001_-en-p.pdf) |
| yes | discontinued, support not stated | Schneider Electric | PowerLogic ION7550 RTU | controller / RTU | DNP3 security not established from retrieved documents | [S252](https://www.se.com/us/en/product-range/1872-powerlogic-ion7550-rtu/) |
| unknown | unknown | GE Vernova / Multilin | MiCOM Agile P24x - Legacy | protective relay | DNP3 security not established from retrieved documents | [S160](https://www.gevernova.com/electrification/sites/default/files/2026-02/P24x-TM-EN-J82-GEV.pdf) |

## The DNP3 table

One line per catalogue entry and DNP3 interface, from the reviewed interface table. Authentication, integrity and encryption are separate results; protection documented for other interfaces is listed apart. Every column, with full quotes and hashes, is in `dnp3_table.csv`.

| Vendor | Model | Lifecycle | Legacy | Authentication | Integrity | Encryption | Scope | Default | Security documented for other interfaces | Review |
|---|---|---|---|---|---|---|---|---|---|---|
| GE Vernova | Multilin C60/C95 | currently listed | no | unknown | unknown | explicitly unsupported | control protocol | - | Modbus TCP over Ethernet, with CyberSentry (control protocol): control protocol, conditions apply; User access to the relay (AAA server) (management): management, support basis not assessed | draft |
| GE Vernova | Multilin D20E | currently listed | no | not established | not established | not established | - | - | none | draft |
| GE Vernova | Multilin G100 Advanced Substation Gateway | currently listed | no | unknown; see tls (supported) | unknown; see tls (supported) | supported | control protocol, support basis not assessed | not assessed | User access to the gateway (management): management, support basis not assessed; Remote access to substation devices through the gateway (management): management, support basis not assessed | draft |
| GE Vernova | G500 Advanced Substation Gateway | currently listed | no | unknown; see tls (supported) | unknown; see tls (supported) | supported | control protocol, support basis not assessed | not assessed | User access to the gateway (management): management, support basis not assessed; Remote access to substation devices through the gateway (management): management, support basis not assessed | draft |
| GE Vernova | Multilin D20MX - Advanced Substation Automation Controller | discontinued, support not stated | yes | not established | not established | not established | - | - | User access to the controller (management): management, built in; Firmware and configuration file transfer (management): management, support basis not assessed | draft |
| GE Vernova | Multilin D400 Advanced Substation Gateway | discontinued, support not stated | yes | unknown; see tls (supported) | unknown; see tls (supported) | supported | control protocol, support basis not assessed | not assessed | Pass-through and terminal server access to substation devices (management): management, support basis not assessed; User access to the gateway (management): management, support basis not assessed | draft |
| GE Vernova | iSTAT M2x2 Communicating Measurement Centre | currently listed | no | not established | not established | not established | - | - | none | draft |
| GE Vernova | EPM 5300 Power Metering System | discontinued, support not stated | yes | not established | not established | not established | - | - | none | draft |
| GE Vernova | EPM 9900 Advanced Power Quality Meter | discontinued, support not stated | yes | unknown | unknown | unknown | control protocol | - | none | draft |
| GE Vernova | Multilin 339 | currently listed | no | not established | not established | not established | - | - | none | draft |
| GE Vernova | Multilin 850: Advanced Feeder Protection & Bay Controller | currently listed | no | not established | not established | not established | - | - | User access to the relay (AAA server) (management): management, support basis not assessed | draft |
| GE Vernova | P64 MiCOM 5th Generation | currently listed | no | not established | not established | not established | - | - | User access to the IED (front panel, S1 Agile, network ports) (management): management, support basis not assessed; S1 Agile engineering tool connection (management): management, support basis not assessed | draft |
| GE Vernova | MiCOM Agile P24x - Legacy | unknown | unknown | not established | not established | not established | - | - | none | draft |
| Rockwell Automation | Micro870 Controllers | currently listed | no | supported | unknown; see dnp3_secure_authentication (supported) | unknown | control protocol, built in | disabled | none | draft |
| Rockwell Automation | Bulletin 865 Motor-feeder Protection Relays | discontinued, support not stated | yes | not established | not established | not established | - | - | none | draft |
| Rockwell Automation | Bulletin 857 Motor-feeder Protection Relays | discontinued, support not stated | yes | not established | not established | not established | - | - | none | draft |
| SEL | SEL-2431 | currently listed | no | not established | not established | not established | - | - | none | draft |
| SEL | SEL-3505/3505-3 | currently listed | no | not established | not established | not established | - | - | Remote serial links to field devices (control protocol): control protocol, separate device; Encrypted communication listed under security features (interface not specified) (management): management, support basis not assessed; User access to the controller (management): management, support basis not assessed | draft |
| SEL | SEL-3560 | currently listed | no | not established | not established | not established | - | - | Ethernet-tunneled serial SCADA protocols (control protocol): control protocol, support basis not assessed; User access to the controller (management): management, support basis not assessed | draft |
| SEL | SEL Real-Time Automation Controller (RTAC) | currently listed | no | unknown; see tls (supported) | unknown; see tls (supported) | supported | control protocol, built in | not assessed | Web HMI (management): management, support basis not assessed | draft |
| SEL | SEL-735 | currently listed | no | not established | not established | not established | - | - | Meter data to SCADA through a separate RTAC (control protocol): control protocol, separate device | draft |
| SEL | SEL-2664S | currently listed | no | not established | not established | not established | - | - | none | draft |
| SEL | SEL-351A | currently listed | no | not established | not established | not established | - | - | none | draft |
| SEL | SEL-387 | currently listed | no | not established | not established | not established | - | - | none | draft |
| SEL | SEL-421 | currently listed | no | not established | not established | not established | - | - | IEC 61850 MMS server (control protocol): control protocol, support basis not assessed | draft |
| Schneider Electric | PowerLogic ION7550 RTU | discontinued, support not stated | yes | not established | not established | not established | - | - | none | draft |
| Siemens | Bay controller – SIPROTEC 6MD86 | currently listed | no | not established | not established | not established | - | - | IEC 61850 MMS (Secure MMS, direct TLS connections) (control protocol): control protocol, support basis not assessed; DIGSI engineering tool connection (management): management, support basis not assessed; Network access (IEEE 802.1X) (network): network, support basis not assessed | draft |
| Siemens | SICAM A8000 Series | currently listed | no | unknown; see tls (supported) | unknown; see tls (supported) | supported | control protocol, support basis not assessed | not assessed | IP network layer (network): network, support basis not assessed | draft |
| Siemens | Substation automation unit | currently listed | no | unknown; see tls (supported) | unknown; see tls (supported) | supported | control protocol, support basis not assessed | not assessed | IP network layer (network): network, support basis not assessed | draft |
| Siemens | Power quality recorder - SICAM Q200 | currently listed | no | not established | not established | not established | - | - | none | draft |
| Siemens | Digital Transducer - SICAM T | currently listed | no | not established | not established | not established | - | - | none | draft |
| Siemens | Overcurrent and feeder protection – SIPROTEC 7SJ85 | currently listed | no | not established | not established | not established | - | - | IEC 61850 MMS (Secure MMS, direct TLS connections) (control protocol): control protocol, support basis not assessed; DIGSI 5 engineering tool connection (management): management, support basis not assessed; Network access (IEEE 802.1X) (network): network, conditions apply | draft |

## Unresolved evidence

19 of 32 DNP3 entries have no established DNP3 security finding. Each stays unknown: neither unsupported nor plaintext.

| Vendor | Model | Lifecycle | Documents read | Documents naming DNP3 | Not obtained |
|---|---|---|---|---|---|
| GE Vernova | Multilin D20E | currently listed | 5 | S11, S12 | 1 behind a sign-in |
| GE Vernova | Multilin D20MX - Advanced Substation Automation Controller | discontinued, support not stated | 11 | S26, S31, S32, S33, S34, S35, S36 | 2 behind a sign-in, 2 beyond the page budget |
| GE Vernova | iSTAT M2x2 Communicating Measurement Centre | currently listed | 7 | S81 | none |
| GE Vernova | EPM 5300 Power Metering System | discontinued, support not stated | 4 | S84 | none |
| GE Vernova | EPM 9900 Advanced Power Quality Meter | discontinued, support not stated | 9 | S95, S96, S100, S101, S103 | none |
| GE Vernova | Multilin 339 | currently listed | 5 | S112, S116 | 4 behind a sign-in |
| GE Vernova | Multilin 850: Advanced Feeder Protection & Bay Controller | currently listed | 11 | S122, S123, S124, S125, S126, S127 | 8 behind a sign-in |
| GE Vernova | P64 MiCOM 5th Generation | currently listed | 7 | S133, S134 | 6 behind a sign-in |
| GE Vernova | MiCOM Agile P24x - Legacy | unknown | 8 | S160 | 1 behind a sign-in |
| Rockwell Automation | Bulletin 865 Motor-feeder Protection Relays | discontinued, support not stated | 3 | S221 | none |
| Rockwell Automation | Bulletin 857 Motor-feeder Protection Relays | discontinued, support not stated | 6 | S226 | none |
| SEL | SEL-2431 | currently listed | 2 | S228, S229 | 1 behind a sign-in |
| SEL | SEL-2664S | currently listed | 2 | S239, S240 | 1 behind a sign-in |
| SEL | SEL-351A | currently listed | 2 | S241, S242 | 1 behind a sign-in |
| SEL | SEL-387 | currently listed | 2 | S243, S244 | 1 behind a sign-in |
| SEL | SEL-421 | currently listed | 3 | S245, S246, S247 | 1 behind a sign-in |
| Schneider Electric | PowerLogic ION7550 RTU | discontinued, support not stated | 3 | S252 | none |
| Siemens | Power quality recorder - SICAM Q200 | currently listed | 5 | S299, S300, S301, S302 | none |
| Siemens | Digital Transducer - SICAM T | currently listed | 2 | S308 | 1 not retrieved |

## Defaults, activation and conditions stated for the control protocols of the DNP3 entries

Those naming DNP3 first. A statement about another protocol (for example IEC 61850 MMS) is not about DNP3.

- Micro870 Controllers, DNP3 outstation (slave) communication, DNP3 Secure Authentication and authentication: default: "Enable Secure Authentication The valid selections are Enabled (Checked) and Disabled (Unchecked). Default value is Disabled (Unchecked)." (S200 pdf-page:89)
- Micro870 Controllers, DNP3 outstation (slave) communication, DNP3 Secure Authentication and authentication: activation: "Select 2 for Secure Authentication version 2 and select 5 for Secure Authentication version 5. Default value is 2." (S200 pdf-page:89)
- Micro870 Controllers, DNP3 outstation (slave) communication, DNP3 Secure Authentication and authentication: activation: "In Connected Components Workbench software, you can create the user keys in the DNP3 Slave configuration page." (S200 pdf-page:91)
- SEL Real-Time Automation Controller (RTAC), DNP3 server to SCADA client (Serial Tunneling Mode SSL/TLS), TLS and encryption: activation: "After the X.509 certificate is activated, it is a simple step to encrypt the server communications." (S236 pdf-page:10)
- SEL-3505/3505-3, Remote serial links to field devices, encryption: conditions: "By including SEL serial and wireless encrypting devices" (S230 pdf-page:6)
- SEL-735, Meter data to SCADA through a separate RTAC, encryption: conditions: "provides secure, encrypted communications and works as a remote intelligence gateway" (S238 pdf-page:13)
- SEL-421, IEC 61850 MMS server, authentication: activation: "When enabled via a setting in the Configured IED Description (CID) file" (S245 pdf-page:13)
- Bay controller – SIPROTEC 6MD86, IEC 61850 MMS (Secure MMS, direct TLS connections), TLS and encryption: default: "Each enabled IEC 61850 interface is listed with the default value Non-Secure. The default setting is the default compatibility mode using TCP communication via the unsecure port 102." (S284 pdf-page:59)
- Bay controller – SIPROTEC 6MD86, IEC 61850 MMS (Secure MMS, direct TLS connections), TLS and encryption: activation: "To enable the secure mode using secure TLS communication via port 3782, set the interface to Secure- TLS" (S284 pdf-page:59)
- Overcurrent and feeder protection – SIPROTEC 7SJ85, IEC 61850 MMS (Secure MMS, direct TLS connections), TLS and encryption: default: "Each enabled IEC 61850 interface is listed with the default value Non-Secure. The default setting is the default compatibility mode using TCP communication via the unsecure port 102." (S318 pdf-page:59)
- Overcurrent and feeder protection – SIPROTEC 7SJ85, IEC 61850 MMS (Secure MMS, direct TLS connections), TLS and encryption: activation: "To enable the secure mode using secure TLS communication via port 3782, set the interface to Secure- TLS" (S318 pdf-page:59)
- Multilin C60/C95, Modbus TCP over Ethernet, with CyberSentry, encryption: conditions: "CyberSentry security — Advanced security available using a software option." (S7 pdf-page:17)
- Multilin C60/C95, Modbus TCP over Ethernet, with CyberSentry, encryption: activation: "CyberSentry security settings are configured under Settings > Product Setup > Security." (S7 pdf-page:235)

Deployment is unknown for every entry: no installation evidence was collected. These are counts of sampled catalogue entries, not of vendors, installed devices or network traffic.
