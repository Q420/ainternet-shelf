"""Duenna Stage 6 — the historical checkers, transcribed
from the executed driver, and the reproduction driver for
the T02/T07/T09 disagreements (DR-14, DR-15, DR-17).

PROVENANCE. The executed stack is pinned by the attempt-3
run record itself: its RUN_STARTED event carries
configuration_hashes naming pilot_driver.py at sha256
304310e26e977d713d0cc2dc2007e490c8099a06897f720d96da6529c92169c7
and pilot_trees.json at
cd367933c261d1172d024c65d4469c8880965cf954ccfcb7ae93edce30e24673.
The examination-package copies of those files hash to
exactly those values (verified at build time; the
reproduction tests re-verify). The delivered instruction for
a MODEL step is, by the driver's own _model_step, exactly
the tree step's text as the system message plus the
canonical artefacts as the user message — no other format
material was delivered. The raw responses are carried
verbatim in the run record's MODEL_CALL_LINKED events;
evidence/attempt3_excerpts.json was extracted mechanically
from that record (never hand-copied).

THE TRANSCRIPTIONS. Each function below reproduces the
extraction logic of the corresponding checker in the pinned
driver, line-faithful in the comparison it performs:

- t02: op_t02_apply_precedence_check —
  ``re.search(r"STATUS:\\s*(OPEN|CLOSED)", raw)``; stated =
  group(1) or None; the step's expected value is the
  adjudication status the record's CHECK_RESULT carries.
- t07: op_t07_report_check —
  ``all(f"{ob}: {st}" in raw for ob, st in statuses.items())``
  over the deterministic statuses from STEP-03.
- t09: op_t09_state_decision_check —
  ``re.search(r"DECISION:\\s*(CLOSE|REJECT)", raw)``; stated
  = group(1) or None, compared with the worksheet decision.

A reproduction earns its name only if the transcribed
checker, run on the preserved response, reproduces the
recorded CHECK_RESULT's compared values exactly. The tests
assert that FIRST, before any attribution is drawn: if the
transcription did not reproduce the record, the stage would
be attributing its own retelling, not the disagreement.
"""

from __future__ import annotations

import re

from schema_contract import ResponseContract

# The response contracts the historical checkers in fact
# enforced, stated as K12 contracts: the demanded format,
# its literal markers (whose presence in a delivered
# instruction would show the format was prescribed), and the
# value domain.
T02_CONTRACT = ResponseContract(
    name="t02_apply_precedence (historical, pin 304310e2)",
    kind="regex", pattern=r"STATUS:\s*(OPEN|CLOSED)",
    markers=("STATUS:",), value_domain=("OPEN", "CLOSED"))

T07_CONTRACT = ResponseContract(
    name="t07_report (historical, pin 304310e2)",
    kind="lines", line_template="{key}: {value}",
    markers=("OB-1:", "OB-2:", "OB-3:"),
    value_domain=("OPEN", "CLOSED"))

T09_CONTRACT = ResponseContract(
    name="t09_state_decision (historical, pin 304310e2)",
    kind="regex", pattern=r"DECISION:\s*(CLOSE|REJECT)",
    markers=("DECISION:",), value_domain=("CLOSE", "REJECT"))


def t02_stated(raw: str):
    """Transcribed: op_t02_apply_precedence_check's
    extraction."""
    m = re.search(r"STATUS:\s*(OPEN|CLOSED)", raw)
    return m.group(1) if m else None


def t07_lines_match(raw: str, statuses: dict) -> bool:
    """Transcribed: op_t07_report_check's comparison."""
    return all(f"{ob}: {st}" in raw
               for ob, st in statuses.items())


def t09_stated(raw: str):
    """Transcribed: op_t09_state_decision_check's
    extraction."""
    m = re.search(r"DECISION:\s*(CLOSE|REJECT)", raw)
    return m.group(1) if m else None
