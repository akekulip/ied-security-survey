"""What the survey asks and the words it may answer with: capabilities, lead patterns, results, lifecycle states."""

import re


VERSION = '2.2.0'


# Bumped only when extraction or lead rules change. Replay compares this, so a report-only release keeps runs replayable.
EXTRACTION = '1.4.0'


# Review cells. Changing this tuple changes every denominator; lead groups below may grow freely.
CAPABILITIES = ('dnp3_secure_authentication', 'tls', 'ipsec', 'cip_security', 'authentication', 'encryption', 'ssh', 'integrity')


# The three properties asked about for every protocol and interface. The other cells are the mechanisms that may provide them.
PROPERTIES = ('authentication', 'integrity', 'encryption')


# A capability named in a sentence that denies it. Encryption wording is left to plaintext_statement where both apply.
TERM = r'(?:m?TLS|SSL|DTLS|IP\s?sec|SSH|MACsec|secure\s+authentication|authentication|encryption|CIP\s+Security)'


DEFAULT = r'(?:by\s+default|default\s+(?:setting|state|value|configuration)|factory[\s-]+defaults?|out\s+of\s+the\s+box)'


NEEDS = r'requires?|required|optional(?:ly)?|licen[sc]e[sd]?|order(?:ing)?\s+(?:code|option)'


PATTERNS = {
    'dnp3_secure_authentication': r'secure\s+auth\w*|\b(?-i:SA)\s*v\d\b|\bDNP\s*3?.{0,80}?\b(?-i:SA)\b|\bIEC\s*62351-5\b',
    'tls': r'\bm?TLS(?:\s?v?\d(?:\.\d)?)?\b|transport\s+layer\s+security|\bSSL\b',
    'ipsec': r'\bIP\s?sec\b|\bIP\s+security\b|\b(?-i:IKE)(?:v[12])?\b',
    # ODVA's CIP Security, not NERC CIP: the two share an acronym and nothing else.
    'cip_security': r'(?-i:(?<!NERC[\s-])\bCIP\s+Security(?![a-z]))',
    'authentication': r'\bauthenticat\w*|\bRADIUS\b|\b802\.1X\b|\bLDAP\b|\bKerberos\b|\bTACACS\b',
    'encryption': r'\b(?:un|non-?)?encrypt\w*|\bDTLS\b|\bAES\b|\bcipher\w*',
    'ssh': r'\bSSH\b|secure\s+shell',
    # "Integrity poll" is a DNP3 data request and "signal integrity" is electrical, so the bare word is not a lead.
    # "Digitally signed" is left out as well: it is nearly always said of firmware, which is no protocol's integrity.
    'integrity': r'\b(?:message|data|packet|frame|communications?|cryptographic)\s+integrity\b'
                 r'|\bintegrity\s+(?:and|or)\s+(?:confidentiality|authenticity|authentication)\b'
                 r'|\b(?:confidentiality|authenticity|authentication)\s*(?:,|and|or)\s*integrity\b'
                 r'|\bintegrity\s+(?:check\w*|protect\w*|verif\w*)|\bHMAC\b|\b(?-i:[GC]MAC)\b'
                 r'|\bmessage\s+authentication\s+codes?\b',
    # Lead-only groups below: shown to the reviewer, never review cells. A capability group above holds only terms
    # that name that capability, so a VPN recommendation is not filed as IPsec, nor SFTP as SSH.
    'vpn': r'\bVPN\b',
    'sftp': r'\bSFTP\b',
    'plaintext_statement': r'\bunencrypted\b|\bnon-?encrypted\b|\bnot\s+(?:be\s+|been\s+|being\s+)?encrypted\b'
                           r'|\bno\s+encryption\b|\bwithout\s+encryption\b'
                           r'|\bplain\s?-?text\b|\bclear\s?-?text\b|\bin\s+the\s+clear\b',
    # Explicit denials are searched for as deliberately as claims; they are the only route to explicitly_unsupported.
    'non_support_statement': rf'\b{TERM}\b[^.]{{0,60}}?\b(?:is|are|was|were)\s+not\s+(?:used|supported|available|implemented|provided|offered)\b'
                             rf"|(?:\b(?:does|do|did|will)\s+not|\b(?:does|do|did|wo)n['\u2019]t)\s+(?:support|provide|implement|offer|use|include)\b[^.]{{0,60}}?\b{TERM}\b"
                             rf'|\b{TERM}\b[^.\w]{{0,6}}(?:not\s+supported|unsupported|not\s+available)\b'
                             r'|\bno\s+(?:support\s+for\s+)?(?:m?TLS|SSL|DTLS|IP\s?sec|SSH|MACsec|secure\s+authentication|authentication|CIP\s+Security)\b',
    # Where a document may say how a capability ships and what it needs. Places to read for the default
    # configuration, support conditions and activation requirements of a finding; never findings themselves.
    'default_statement': rf'\b{TERM}\b[^.]{{0,80}}?\b{DEFAULT}\b|\b{DEFAULT}\b[^.]{{0,80}}?\b{TERM}\b',
    'requirement_statement': rf'\b{TERM}\b[^.]{{0,60}}?\b(?:{NEEDS}|option\s+(?:board|card|code)|add-?on'
                             r'|firmware\s+(?:version|revision|release)?\s*[\w.]+\s+(?:or|and)\s+(?:later|higher|above|newer))\b'
                             rf'|\b(?:{NEEDS})\b[^.]{{0,60}}?\b{TERM}\b',
    'macsec': r'\bMACsec\b|\b802\.1AE\b',
    'iec_62351': r'\bIEC(?:/TS)?\s*62351(?:-\d+)?\b',
}


LEADS = {k: re.compile(v, re.I | re.S) for k, v in PATTERNS.items()}


# A lead in these groups also needs the qualifying term close by.
NEAR = {'dnp3_secure_authentication': re.compile(r'\bDNP|\b1815\b|62351-5', re.I)}


# "If the device does not support ..." states a condition, not a fact about the product.
HYPOTHETICAL = re.compile(r'\b(?:if|whether|unless|when|where|in\s+case)\b[^.]{0,60}$', re.I)


DENIALS = ('plaintext_statement', 'non_support_statement')


STATEMENTS = DENIALS + ('default_statement', 'requirement_statement')


# The same four results for every device, whatever its lifecycle.
STATUSES = ('supported', 'conditional', 'explicitly_unsupported', 'unknown')


# Why a reviewed cell is unknown. The second is checked by the tool: a complete document was searched and is silent.
# Only the kinds of document below can carry that, and silence is still not a vendor statement of non-support.
UNKNOWN_REASONS = ('not_enough_evidence', 'complete_document_silent', 'sources_conflict')


COMPLETE_TYPES = ('device_profile', 'conformance_statement', 'manual')


# Statuses written before 1.6.0 are read as unknown with the reason they stood for.
FORMER = {'not_documented': 'complete_document_silent', 'conflicting': 'sources_conflict'}


# Decided by dated vendor evidence only.
LIFECYCLES = ('currently_supported', 'discontinued_supported', 'discontinued_support_not_stated', 'end_of_support', 'unknown')


# The states a config may count as legacy. Each is the vendor's own dated word that the product has been withdrawn, so
# a device still on sale, or one whose state nobody could establish, is legacy under no definition.
LEGACY_STATES = ('discontinued_supported', 'discontinued_support_not_stated', 'end_of_support')


# What legacy covers where a config defines it in words alone, as every config written before 2.0 does.
LEGACY_DEFAULT = ('end_of_support',)


FORMER_LIFECYCLES = ('active', 'legacy', 'discontinued')


LIFECYCLE_WORDS = {'discontinued_supported': 'discontinued, still supported',
                   'discontinued_support_not_stated': 'discontinued, support not stated'}


SUPPORT_BASES = ('built_in', 'firmware_upgrade', 'optional_module', 'licence', 'external_gateway', 'not_stated')


DEFAULT_STATES = ('enabled', 'disabled', 'undocumented')


ACTIVATION_NEEDS = ('configuration', 'certificates_or_keys', 'compatible_master', 'licence_key', 'other', 'none_stated')


# What a vendor document can never show. Anything but unknown needs evidence from where the device is installed.
DEPLOYMENT_STATES = ('unknown', 'enabled', 'disabled')


EVIDENCE_ABOUT = ('capability', 'conditions', 'default', 'activation')


IDENTITY_LEVELS = ('family', 'model', 'catalogue_number')


# A reviewer who has not looked yet says so. It is not the same as "the documents do not say".
NOT_ASSESSED = 'not_assessed'


# Roughly from most to least direct about what one product and firmware can do. Guidance for the reviewer, not a score.
DOC_TYPES = ('device_profile', 'conformance_statement', 'security_guide', 'manual', 'datasheet', 'product_page',
             'advisory', 'other')


# The distinction the study turns on: protection of control traffic is not protection of management access.
INTERFACE_CLASSES = ('control_protocol', 'management', 'network')


REVIEW_STATUSES = ('draft', 'confirmed')


# Pointers only: which mechanism rows a reader should look at when no explicit property row exists.
RELATES = {'encryption': ('tls', 'ipsec', 'cip_security', 'ssh'),
           'authentication': ('dnp3_secure_authentication', 'tls', 'ipsec', 'cip_security', 'ssh'),
           'integrity': ('dnp3_secure_authentication', 'tls', 'ipsec', 'cip_security', 'ssh')}


def life_words(status):
    return LIFECYCLE_WORDS.get(status, (status or 'not recorded').replace('_', ' '))


def legacy_states(definitions):
    """The lifecycle states a definitions block counts as legacy, in lifecycle order; none where legacy is not defined.

    A definition changed after results were seen has to say so: each revision gives its date, the change, and what had
    been counted by then.
    """
    definitions = definitions or {}
    chosen = definitions.get('legacy_statuses', list(LEGACY_DEFAULT) if definitions.get('legacy') else [])
    if not isinstance(chosen, list) or set(chosen) - set(LEGACY_STATES) or bool(chosen) != bool(definitions.get('legacy')):
        raise ValueError(f'definitions: legacy_statuses lists one or more of {", ".join(LEGACY_STATES)}, and legacy '
                         f'says in words what they mean')
    for r in definitions.get('revisions') or []:
        if not isinstance(r, dict) or not all(isinstance(r.get(k), str) and r[k].strip() for k in ('date', 'change', 'known_then')):
            raise ValueError('definitions: each revision gives date, change and known_then (what had been counted when '
                             'it was made)')
    return tuple(k for k in LIFECYCLES if k in chosen)


def lead_type(feature):
    # A statement is something a document says in so many words. It is never a measurement of how equipment is deployed.
    return 'capability' if feature in CAPABILITIES else 'statement' if feature in STATEMENTS else 'related'


CATEGORIES = ('protective_relay', 'controller_rtu', 'plc', 'meter')
