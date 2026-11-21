#!/usr/bin/env python3
"""TEST-ONLY slow/partial write injector (Rev 26 §5 G2; Rev 12 Item 6).

This module is the torn-write test's slow/partial write path. It exists
ONLY in the scratch/test build configuration, included by the build
tool when the build-time flag PILOT_TORN_WRITE_INJECTOR is set. The
scoreable build refuses that flag and never ships this module; its
absence from a scoreable package is demonstrated by the build's
recorded flag state, not asserted.

The injector writes a payload to a target file in deterministic
fragments — optionally stopping mid-payload, leaving a torn tail —
so the examiner's torn-tail handling (Step 0) and the supervisor's
crash semantics can be exercised on demand.
"""
import time
from pathlib import Path


def torn_write(target, payload: bytes, fragments, delay_s=0.0, complete=True):
    """Write `payload` to `target` in `fragments` byte-count pieces.

    fragments: list of byte counts summing to <= len(payload).
    complete=False stops after the fragments are written, leaving the
    remainder unwritten (a torn tail). Returns the bytes written.
    """
    written = 0
    with open(target, "wb") as f:
        for n in fragments:
            chunk = payload[written:written + n]
            if not chunk:
                break
            f.write(chunk)
            f.flush()
            written += len(chunk)
            if delay_s:
                time.sleep(delay_s)
        if complete and written < len(payload):
            f.write(payload[written:])
            written = len(payload)
    return written


def torn_line(target, line: bytes, cut: int, delay_s=0.0):
    """Write exactly `cut` bytes of a record line, then stop — the
    canonical torn-tail fixture."""
    return torn_write(target, line, [cut], delay_s=delay_s, complete=False)
