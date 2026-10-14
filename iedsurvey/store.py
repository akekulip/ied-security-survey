"""Hashes, timestamps and the one way files are read and written: UTF-8, LF, atomically."""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


def digest(b):
    return hashlib.sha256(b).hexdigest()


# Hashed when the tool starts, so a manifest names the code that ran even if a file is edited during a long crawl.
# One hash over every module of the package, in name order.
SCRIPT_SHA256 = digest(b''.join(p.read_bytes() for p in sorted(Path(__file__).parent.glob('*.py'))))


def now():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def dump(path, obj):
    # UTF-8 and LF on every platform; replaced atomically so an interrupted checkpoint is never half a file.
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    for attempt in range(5):
        try:
            return os.replace(tmp, path)
        except PermissionError:  # Sync clients and scanners briefly lock freshly written files on Windows.
            if attempt == 4:
                raise
            time.sleep(0.2 * (attempt + 1))
