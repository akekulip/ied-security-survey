# Second pass over the draft review and the paper's sources (2026-10-14)

A second reading, by the same AI assistant that drafted the review. It checks the draft against the retained documents and checks the outside sources the paper cites. It is not the author's confirmation and not an independent review.

Run: `C:\Users\Philip\ied_survey_data\runs\sample_2026-10-13_v2_0` (99 devices). Review: `reviews_ai_draft.json` in this folder.

## What was checked

1. **Every result for a control protocol (11 devices).** Each quoted passage was re-read in the full page or block it comes from. The aim was to confirm that it names the protocol, that it concerns the device's own interface, and that the result follows from the words.
2. **Every other security passage the search found (511 capability leads at 386 places, in the documents of 31 devices).** Each was read to see whether the draft missed a protection of control traffic. The 77 passages on VPN, SFTP and IEC 62351 were read too.
3. **The lifecycle evidence of all 31 discontinued devices.** Each is the vendor's own sentence or label on the product page, retrieved 2026-10-13.
4. **The 16 documents taken as complete manuals** (12 devices): their title, length and number of empty pages.
5. **The outside sources cited in the paper**, against the documents themselves (below).

## Results

| Claim | Holds? | Basis |
|---|---|---|
| Encryption of control traffic is documented for 6 of 99 devices, all currently sold | Yes, for the documents retrieved; a lower bound (see below) | GE G100 and G500: "Secure tunneling from master station via TLS for DNP3/TCP, Modbus/TCP and IEC 104" (brochures, p. 1). Siemens SICAM A8000 and CP-8050: TLS listed for IEC 60870-5-104, IEC 61850 and DNP3i (catalogue, p. 12). SEL-3560: "Optional encryption for Ethernet-tunneled serial SCADA protocols … SSH … TLS tunneling" (SEL publication 124708, p. 2). Rockwell CompactLogix 5380: CIP Security with data confidentiality, from firmware 34.011 (user manual p. 28; product page). The CompactLogix result is conditional. GE's and Siemens' statements are brochure or catalogue level for the family. |
| Authentication without encryption for 2 more | Yes | Rockwell Micro870: "enhanced protocol authentication in DNP3 with Secure Authentication version 5 (SAv5)" (product page). SEL-421: "When enabled via a setting in the Configured IED Description (CID) file, the relay requires authentication from any client requesting to initiate an MMS session" (data sheet p. 13). |
| A mechanism named without its properties: 1 | Yes | Rockwell ControlLogix 5590: "Integrated CIP Security" (brochure p. 5). |
| Protection only through a separate device: 2 | Yes | SEL-3505 with separate SEL encrypting devices (data sheet p. 6); SEL-735 behind an SEL RTAC (SEL publication 128658, p. 13). |
| No further protection of control traffic was missed | Yes, with one note | All other passages concern user login, RADIUS/LDAP, role-based access, 802.1X network access, SNMPv3, engineering-tool links (DIGSI, S1 Agile), web pages, firmware signing, storage encryption, or other products of a family. The note is the GE D400 entry in the next row. |
| None of the 31 discontinued devices documents protection of its control traffic | Yes, as worded | 3 have a complete manual that documents none (GE EPM 9900 DNP guide; Rockwell 857 and 865 manuals). 2 document protection of management access only (GE D20MX, D400). For 26 the public documents settle nothing. **Note:** the D400 brochure also lists a "Simple VPN server", and a diagram labels a link "Modbus TCP/SSH Over VPN Tunnel". Neither says which traffic the VPN carries, so the device stays unsettled for encryption. The paper should not write "none of the discontinued devices has any protection". |
| The 31 discontinued devices are discontinued | Yes | Vendor wording on each product page, for example "Manufacturing for the D400 has been discontinued", "discontinued and no longer available for sale" (Rockwell), "Discontinued" (Schneider product ranges), "Obsolete December 2016" (Twido). |
| The 16 documents are complete manuals | Plausible; author to confirm | Each is a full user or technical manual, or for the EPM 9900 the full DNP3 guide, at 70 to 694 pages. The "complete manual documents none" label covers 12 devices, and each is checked mechanically: no lead for the capability anywhere in the cited manuals. |
| 69 of 99 devices: the public documents settle nothing | Yes | 39 currently sold, 26 discontinued, 4 of unknown state. |

## The counts are lower bounds

The sample read a few public documents per device, and a vendor may document more than those say. One case is known. For the SEL RTAC, the sample retrieved two flyers (SEL publications 111397 and 129976) and a ZIP file it cannot read, and the draft places the RTAC under "management access only". The five-product pilot, however, retrieved an SEL application guide, publication 112760, "Configuring a DNP3 Server to Support TLS One-Way Authentication in ACSELERATOR RTAC". In that guide the pilot review quotes "After the X.509 certificate is activated, it is a simple step to encrypt the server communications" for the DNP3 server to the SCADA master. A review row may cite only sources of its own run, so the sample's count stays at 6. The paper should say "at least 6", or "in the documents retrieved". A second crawl pass that seeds each sampled device with its vendor's application guides and manuals would raise recall.

## Found on the way: a security setting that is off by default, in a document of the crawl

The Rockwell user manual for the Micro830, Micro850 and Micro870 controllers (publication 2080-UM002S-EN-E, April 2026) was fetched for the Micro830 entry. Its Micro870 DNP3 chapter, p. 89, says:

> "Enable Secure Authentication The valid selections are Enabled (Checked) and Disabled (Unchecked). Default value is Disabled (Unchecked)."

URL: https://literature.rockwellautomation.com/idc/groups/literature/documents/um/2080-um002_-en-e.pdf, retrieved 2026-10-13. The SHA-256 is in the run's `sources.json`. A review row may cite only sources of its own catalogue entry, so the Micro870 row notes this in its rationale and its `default_state` stays "not assessed".

## Outside sources, checked against the documents

| Source | What it says, verbatim | Where |
|---|---|---|
| NIST SP 800-82 Rev. 3, *Guide to Operational Technology (OT) Security*, September 2023 | Row "Installed security capabilities are not enabled by default", described as "Security capabilities that were installed with the product are useless if they are not enabled or at least identified as being disabled." | Table 18, "Software development vulnerabilities and predisposing conditions", printed p. 177 |
| same | "Many OT protocols have no authentication at any level." / "OT protocols often have few or no security capabilities, such as authentication and encryption" / "Integrity checks are not built into most OT protocols, so adversaries could manipulate communications undetected." | Table 19, "Communication and network configuration vulnerabilities and predisposing conditions", printed p. 178 |
| same | "Legacy systems often lack resources that are common on modern IT systems. Many systems may also lack desired features, including encryption capabilities, error logging, and password protection." | Section on OT special considerations, "Resource constraints", printed p. 29 |
| CISA, *Barriers to Secure OT Communication: Why Johnny Can't Authenticate*, 10 February 2026 | "the control systems community has not widely adopted the secure versions of these protocols" | p. 4 |
| same | "Secure versions of industrial protocols have existed since the early 2000s (e.g., … DNP3 … to DNP3 Secure Authentication version 5 [DNP3-SAv5], Common Industrial Protocol [CIP] to CIP Security …). However, many OT systems built in 2026 still rely on protocol implementations designed decades ago" | p. 5 |
| same | Method: individual and group interviews with OT asset owners and operators in the Water and Wastewater, Transportation, Chemical, Energy, and Food and Agriculture sectors. No number of interviews is given. | p. 5 |
| same | Barriers: costs (retrofitting legacy infrastructure, hardware for cryptography, certificate management or licence fees, training); disagreement about whether secure communication would disrupt operations (p. 11); "Almost every operator interviewed mentioned challenges with deploying and maintaining PKI" | pp. 8, 11, 12 |
| same | "The long lifecycle of OT ensures that industry will be mitigating insecure-by-design legacy protocols for decades." / "Despite decades of availability, secure versions of industrial protocols remain underutilized in OT environments." | p. 15 |
| ABB, AC500 V3 DNP3 Outstation online help, page "Secure Authentication" | "By default, “Secure Authentication” is disabled"; it can be enabled "from settings for each master session in the session interface" | https://help.plc.abb.com/AB281_en/adcfee22f1883359ea6f8c9974f7ea51_4_en_us.html, read 2026-10-14 |

Retrieved 2026-10-14:

- NIST PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-82r3.pdf, SHA-256 `608f554514d381853e24e0b33123b7080fbd757826f460032690aade63394616`.
- CISA PDF: https://www.cisa.gov/sites/default/files/2026-02/Barriers-to-Secure-Communication-Why-OT-Johnny-Cant-Authenticate_508_2.pdf, SHA-256 `c1f3945b3fef398c103710071712bb5ec0190f12ce5b0843e34e0ef116d7806d`. The CISA PDF downloaded directly; no copy from another site was needed.

What these sources do not establish: none of them measures how much deployed ICS traffic is plaintext. NIST is guidance. CISA's findings come from interviews, not a census of enabled settings.

## Still for the author

- Confirm or correct the 11 devices with results and the 12 "complete manual" calls. The author's name in the `reviewer` field, with `review_status: confirmed`, is what turns a draft row into a finding.
- Decide whether the GE D400 VPN server should be read as protection of control traffic. It is not, as the draft stands.
