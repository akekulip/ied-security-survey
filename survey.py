#!/usr/bin/env python3
"""Bounded public-document survey. Keyword hits are leads, never support verdicts.

The tool is the iedsurvey package next to this file. This file keeps `python survey.py <command>` working and lets
`import survey` reach every name the single-file version had.
"""
import re  # noqa: F401
import sys  # noqa: F401

from iedsurvey.vocabulary import *  # noqa: F401,F403
from iedsurvey.store import *  # noqa: F401,F403
from iedsurvey.text import *  # noqa: F401,F403
from iedsurvey.fetch import *  # noqa: F401,F403
from iedsurvey.extract import *  # noqa: F401,F403
from iedsurvey.leads import *  # noqa: F401,F403
from iedsurvey.crawl import *  # noqa: F401,F403
from iedsurvey.runs import *  # noqa: F401,F403
from iedsurvey.review import *  # noqa: F401,F403
from iedsurvey.devices import *  # noqa: F401,F403
from iedsurvey.charts import *  # noqa: F401,F403
from iedsurvey.findings import *  # noqa: F401,F403
from iedsurvey.report import report  # noqa: F401
from iedsurvey.inventory import *  # noqa: F401,F403
from iedsurvey.sampling import *  # noqa: F401,F403
from iedsurvey.worksheet import *  # noqa: F401,F403
from iedsurvey.cli import *  # noqa: F401,F403
from iedsurvey.cli import main

if __name__ == '__main__':
    main()
