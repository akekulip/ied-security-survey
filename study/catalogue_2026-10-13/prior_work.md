# Prior work for the documentation survey (2026-10-15)

What earlier work supports, and what it does not. None of it measures how much deployed DNP3 or other control traffic is
unprotected, and neither does this survey.

| Source | What it supports | What it does not | Checked |
|---|---|---|---|
| CISA, *Barriers to Secure OT Communication: Why Johnny Can't Authenticate*, 10 February 2026, with OT manufacturers and standards bodies. https://www.cisa.gov/resources-tools/resources/barriers-secure-ot-communication-why-johnny-cant-authenticate | Qualitative evidence, from interviews with OT asset owners and operators, on why technologies that secure legacy industrial protocols are not widely adopted, from design through deployment and operation | A count of plaintext traffic or of unprotected devices | Resource page read 2026-10-15 (title, date, interview method). The full PDF was not re-read. |
| M. Clark, participant's account of the CISA work, automation.com. https://www.automation.com/article/why-johnny-can-t-authenticate-but-asset-owners-can-secure-ot-deployments | That asset owners in several sectors were interviewed and named adoption barriers (per the 2026-10-15 audit) | A deployment measurement; its product recommendations are not evidence | Not re-checked: the site answered 403 on 2026-10-15 |
| NIST SP 800-82 Rev. 3, *Guide to Operational Technology (OT) Security*, September 2023 (Stouffer et al.). https://csrc.nist.gov/pubs/sp/800/82/r3/final | The constraints on adding security to OT and legacy systems while keeping their performance, reliability and safety requirements | A measured share of insecure IEDs | Publication record read 2026-10-15; the legacy constraints are in the body, not the abstract |
| Erba, Müller, Tippenhauer, *Security Analysis of Vendor Implementations of the OPC UA Protocol for Industrial Control Systems*, arXiv:2104.06051, 2021 | A precedent for examining vendors' security implementations systematically: 38 of 48 public OPC UA products and libraries had at least one security issue | DNP3, IEDs, or how often security is enabled in the field | Abstract read 2026-10-15 |
| Vendor documents in this survey's run, for example Rockwell 2080-UM002 (Micro830/850/870), printed p. 89 | That a DNP3 security feature can ship disabled and needs configuration: capability, default and deployment are different questions | What operators enable | The quote is checked against the retained text by the report (see `paper_2026-10-15/`) |

Not identified: the CMU paper Dr. Lin mentioned. Do not cite another paper in its place.

The audit also cites ABB AC500 instructions for a DNP3 Secure Authentication default. No ABB device is in this
survey's sample or run, so that statement rests on the audit's reading, not on this survey's evidence. Check it against
the ABB document before citing it.

Wording to avoid: dating DNP3 Secure Authentication or CIP Security to "the early 2000s" as a whole. Name the version
(for example SAv5, IEEE 1815-2012), and say "SAv5 authenticates without encrypting" rather than making that true of
every DNP3 security revision.
