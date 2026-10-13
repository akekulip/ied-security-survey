# IED security documentation pilot

Sampling: Purposive five-vendor pilot, selected to test extraction and distinctions; not representative and not an estimate of prevalence.

Products/families in seed inventory: 5. Sources attempted: 7; extracted: 5; failed: 2.

This measures documented capabilities, not enabled settings, installed-base coverage or plaintext prevalence. Unknown is not unsupported. Family-level evidence is not proof for every model/firmware. AI-reviewed pilot findings require author verification before publication.

| Product | Capability | Review result | Scope |
|---|---|---|---|
| RTAC family (guide scope) | dnp3_secure_authentication | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| RTAC family (guide scope) | tls | conditional | Guide documents TLS-protected DNP3 server sessions and optional mutual certificate authentication; confirm current model/firmware before generalizing. |
| RTAC family (guide scope) | ipsec | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| RTAC family (guide scope) | cip_security | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| RTAC family (guide scope) | authentication | conditional | Guide documents TLS-protected DNP3 server sessions and optional mutual certificate authentication; confirm current model/firmware before generalizing. |
| RTAC family (guide scope) | encryption | conditional | Guide documents TLS-protected DNP3 server sessions and optional mutual certificate authentication; confirm current model/firmware before generalizing. |
| RTAC family (guide scope) | ssh | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| PowerLogic ADVC Controller | dnp3_secure_authentication | conditional | Manual explicitly describes SA v5, feature selection and critical-request authentication. It does not establish encrypted DNP3 payloads. |
| PowerLogic ADVC Controller | tls | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| PowerLogic ADVC Controller | ipsec | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| PowerLogic ADVC Controller | cip_security | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| PowerLogic ADVC Controller | authentication | conditional | Manual explicitly describes SA v5, feature selection and critical-request authentication. It does not establish encrypted DNP3 payloads. |
| PowerLogic ADVC Controller | encryption | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| PowerLogic ADVC Controller | ssh | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| ControlLogix 5580 | dnp3_secure_authentication | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| ControlLogix 5580 | tls | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| ControlLogix 5580 | ipsec | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| ControlLogix 5580 | cip_security | unknown | User manual describes CIP Security and confidentiality but refers to a separate compatibility guide. That PDF fetch was blocked by unresolved robots redirect; do not infer exact firmware support from nearby IEC-62443 claims. |
| ControlLogix 5580 | authentication | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| ControlLogix 5580 | encryption | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| ControlLogix 5580 | ssh | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| Multilin B90 | dnp3_secure_authentication | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| Multilin B90 | tls | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| Multilin B90 | ipsec | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| Multilin B90 | cip_security | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| Multilin B90 | authentication | conditional | Product page documents user authentication and roles with CyberSentry. This is not evidence that DNP3 control messages are authenticated or encrypted. |
| Multilin B90 | encryption | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| Multilin B90 | ssh | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| SIPROTEC 5 family | dnp3_secure_authentication | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| SIPROTEC 5 family | tls | conditional | Official advisory confirms encrypted management services while reporting weak ciphers in affected versions. Presence of encryption is not proof of adequate security or encrypted DNP3. |
| SIPROTEC 5 family | ipsec | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| SIPROTEC 5 family | cip_security | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| SIPROTEC 5 family | authentication | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |
| SIPROTEC 5 family | encryption | conditional | Official advisory confirms encrypted management services while reporting weak ciphers in affected versions. Presence of encryption is not proof of adequate security or encrypted DNP3. |
| SIPROTEC 5 family | ssh | unknown | Examined pilot sources do not establish this capability for the scoped product/interface; not a non-support finding. |

Review coverage: 35/35 product–capability cells. Unreviewed cells carry no result.

See findings.csv for source URLs, hashes, interface, firmware and review provenance. No population percentages are computed.
