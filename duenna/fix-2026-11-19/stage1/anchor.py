"""Duenna Stage 1 — external commitment anchor.

The hash chain in record.py proves order and content *as appended*
and detects naive edits, but it cannot by itself detect a wholesale
rewrite: an attacker (or a bug) can regenerate the whole record with
altered content and re-chain it consistently from genesis, and the
recomputed chain verifies cleanly.

The anchor is the external commitment that catches that. After a
closure append, the record's head state — its head digest and its
length — is committed to an anchor file at a SEPARATE path, outside
the record being validated:

    <record directory>/anchors/<record-name>.anchor.json

(e.g. stage1/anchors/<record-name>.anchor.json for a record living
in stage1/). The anchor is not supplied by the record: the writing
function below takes ONLY head state values (a digest and a length)
plus the destination path — it never opens or reads the record file.
A validator can therefore compare a fresh-read record's head against
a commitment made independently of that record's own contents.

Honesty boundary: an anchor that is missing or unreadable proves
nothing either way. The validator reports that state as
NOT_VERIFIED — distinct from PASS and from FAIL — and never rounds
it up to verified.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K9, G4),
PROCESS-TREE-AND-PLAN.md v2, Stage 1 (step 4).
"""

from __future__ import annotations

import json
import os

ANCHOR_SUFFIX = ".anchor.json"


def anchor_path_for(record_path: str, anchors_dir: str | None = None) -> str:
    """Return the anchor file path for the record at ``record_path``.

    The anchor lives in an ``anchors`` directory beside the record
    (or in ``anchors_dir`` when given) — always a separate path from
    the record file itself.
    """
    if anchors_dir is None:
        anchors_dir = os.path.join(
            os.path.dirname(os.path.abspath(record_path)), "anchors")
    base = os.path.basename(record_path)
    stem, _ext = os.path.splitext(base)
    return os.path.join(anchors_dir, stem + ANCHOR_SUFFIX)


def write_anchor(head_digest: str, length: int, anchor_path: str) -> dict:
    """Commit head state values to the anchor file at ``anchor_path``.

    This function's only inputs are the head state values
    (``head_digest``, ``length``) and the destination path. It does
    not read the record — the commitment is made from values handed
    to it, so what lands in the anchor cannot be influenced by the
    record file's contents at write time.

    The write is flushed and fsynced. Returns the anchor dict.
    """
    if not isinstance(head_digest, str) or not head_digest:
        raise ValueError("head_digest must be a non-empty string")
    if not isinstance(length, int) or length < 0:
        raise ValueError("length must be a non-negative int")
    anchor = {"head_digest": head_digest, "length": length}
    directory = os.path.dirname(os.path.abspath(anchor_path))
    os.makedirs(directory, exist_ok=True)
    tmp_path = anchor_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(anchor, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, anchor_path)
    return anchor


def commit_record_head(record, anchors_dir: str | None = None) -> str:
    """Anchor the current head of ``record`` (an EventRecord).

    Convenience wrapper for the post-closure step: reads the two
    head state values off the record object and hands ONLY those
    values to :func:`write_anchor`. Returns the anchor path.
    """
    anchor_path = anchor_path_for(record.path, anchors_dir)
    write_anchor(record.head_digest, record.length, anchor_path)
    return anchor_path


def read_anchor(anchor_path: str) -> dict | None:
    """Read an anchor file. Returns its dict, or None when the file
    is missing, unreadable, malformed, or lacks the head state
    fields — the caller reports that state as NOT_VERIFIED, never
    as a pass and never as a fail."""
    try:
        with open(anchor_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("head_digest"), str):
        return None
    if not isinstance(data.get("length"), int):
        return None
    return {"head_digest": data["head_digest"], "length": data["length"]}
