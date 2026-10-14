"""Bounded survey of what public vendor documents say about the security of IEDs.

It reads documents; it never contacts a device. Keyword hits are leads, never verdicts: a finding exists only as a
reviewed row that quotes its source. The modules, in the order the work flows:

    vocabulary           what is asked and the words an answer may use
    store, text          hashes, files, text matching
    fetch                the only code that talks to a vendor site
    extract              bytes to located text
    leads                where the terms occur
    crawl, runs          one config into one run; verify, replay, rebuild, recheck
    inventory, sampling  the vendor catalogues, and the sample drawn from them
    review, devices      what a reviewer may claim, and what it takes
    worksheet            what a reviewer reads
    findings             a run and its review, resolved once for everything the report shows
    tables, glance, charts, report  the data files, the charts, and REPORT.md
    cli                  the commands
"""
from .vocabulary import EXTRACTION, VERSION

__all__ = ['EXTRACTION', 'VERSION']
