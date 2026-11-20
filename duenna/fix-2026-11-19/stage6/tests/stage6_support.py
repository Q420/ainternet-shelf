"""Stage 6 test support: paths, a fresh record, the issued
TEST authority, and the evidence loaders."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from record import EventRecord  # noqa: E402
from authority import (  # noqa: E402
    issue_authority, make_test_authority_record)

EVIDENCE = os.path.join(os.path.dirname(__file__), "..", "evidence")


def fresh_record(testcase):
    tmp = tempfile.TemporaryDirectory()
    testcase.addCleanup(tmp.cleanup)
    path = os.path.join(tmp.name, "record.jsonl")
    return EventRecord(path), path


def issued_authority():
    return issue_authority(make_test_authority_record())


def load_excerpts():
    with open(os.path.join(EVIDENCE, "attempt3_excerpts.json"),
              encoding="utf-8") as f:
        return json.load(f)


def load_g6_excerpts():
    with open(os.path.join(EVIDENCE, "g6_excerpts.json"),
              encoding="utf-8") as f:
        return json.load(f)


def load_trees():
    with open(os.path.join(EVIDENCE, "pilot_trees.json"),
              encoding="utf-8") as f:
        data = json.load(f)
    trees = data["trees"]
    if isinstance(trees, list):
        trees = {t["tree_id"]: t for t in trees}
    return {tid: [s["step_id"] for s in t["steps"]]
            for tid, t in trees.items()}
