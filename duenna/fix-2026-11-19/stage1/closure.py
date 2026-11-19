"""Duenna Stage 1 — closure writer.

The closure writer is invoked on EVERY controlled termination path
(normal completion, known failure, early stop, exception). It appends
exactly one CLOSURE event to the EventRecord, as the terminal event.

The CLOSURE event body carries the mandatory account (K9):

- ``account`` — the failure-account section:
    - ``failures``: a list of failure entries, each carrying
      ``failure_id``, ``description`` and ``attribution`` (one of
      SYSTEM / MODEL / INPUT / UNKNOWN), plus the ``authority`` under
      which the attribution was minted.
    - ``account_status``: ``COMPLETE`` or ``INCOMPLETE``. An account
      that names any unknowns is INCOMPLETE, never COMPLETE.
    - ``unknowns``: the things the account could not establish, named
      explicitly (empty when the account is COMPLETE).
    - ``authority``: the authority that minted the attributions.
- ``endings`` — the three endings stated separately:
  ``execution``, ``record`` and ``adjudication``. They are distinct
  facts and are never collapsed into one status.
- ``termination`` — which controlled termination path produced this
  closure.

TEST AUTHORITY FIXTURE: attributions in this harness are minted under
the clearly-marked TEST authority (``TEST_AUTHORITY`` below). That
fixture exercises the attribution *shape* only; it settles nothing
about the production adjudicator authority (DR-13 remains open).

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K9, K10, G4),
PROCESS-TREE-AND-PLAN.md v2, Stage 1.
"""

from __future__ import annotations

from typing import Any

from anchor import commit_record_head

# Clearly-marked TEST authority fixture. Not a production authority.
TEST_AUTHORITY = "TEST-FIXTURE"
AUTHORITY = TEST_AUTHORITY

VALID_ATTRIBUTIONS = ("SYSTEM", "MODEL", "INPUT", "UNKNOWN")
VALID_ACCOUNT_STATUSES = ("COMPLETE", "INCOMPLETE")


def make_failure(failure_id: str, description: str,
                 attribution: str | None = None,
                 authority: str = TEST_AUTHORITY) -> dict:
    """Build one failure entry for a FAILURE event / closure account.

    A missing attribution is recorded as UNKNOWN — the failure itself
    is never omitted for lack of an attribution.
    """
    if attribution is None:
        attribution = "UNKNOWN"
    if attribution not in VALID_ATTRIBUTIONS:
        raise ValueError(f"invalid attribution: {attribution!r}")
    return {
        "failure_id": failure_id,
        "description": description,
        "attribution": attribution,
        "authority": authority,
    }


def build_closure_body(termination: str,
                       failures: list[dict] | None = None,
                       execution: str = "COMPLETED",
                       adjudication: str = "NOT_REQUIRED",
                       unknowns: list[str] | None = None,
                       account_status: str | None = None,
                       authority: str = TEST_AUTHORITY) -> dict:
    """Build the CLOSURE event body with its mandatory account.

    If ``unknowns`` is non-empty the account is INCOMPLETE; asking for
    COMPLETE while naming unknowns is refused, because a record must
    not certify a completeness it simultaneously disclaims.
    """
    failures = list(failures or [])
    unknowns = list(unknowns or [])
    for failure in failures:
        if failure.get("attribution") not in VALID_ATTRIBUTIONS:
            raise ValueError(
                f"failure {failure.get('failure_id')!r} has invalid "
                f"attribution: {failure.get('attribution')!r}")
    if account_status is None:
        account_status = "INCOMPLETE" if unknowns else "COMPLETE"
    if account_status not in VALID_ACCOUNT_STATUSES:
        raise ValueError(f"invalid account_status: {account_status!r}")
    if account_status == "COMPLETE" and unknowns:
        raise ValueError(
            "account cannot declare COMPLETE while naming unknowns")
    return {
        "termination": termination,
        "account": {
            "failures": failures,
            "account_status": account_status,
            "unknowns": unknowns,
            "authority": authority,
        },
        "endings": {
            "execution": execution,
            "record": "CLOSED",
            "adjudication": adjudication,
        },
        "authority": authority,
    }


class ClosureWriter:
    """Appends the terminal CLOSURE event to an EventRecord.

    After the closure append, the record's head state is committed
    to the external anchor (anchor.py, Stage 1 step 4): immutability
    evidence lives outside the chain.
    """

    def __init__(self, record, authority: str = TEST_AUTHORITY,
                 anchors_dir: str | None = None):
        self.record = record
        self.authority = authority
        self.anchors_dir = anchors_dir

    def close(self, termination: str,
              failures: list[dict] | None = None,
              execution: str = "COMPLETED",
              adjudication: str = "NOT_REQUIRED",
              unknowns: list[str] | None = None,
              account_status: str | None = None) -> dict:
        """Append exactly one CLOSURE event; returns the event dict."""
        body = build_closure_body(
            termination,
            failures=failures,
            execution=execution,
            adjudication=adjudication,
            unknowns=unknowns,
            account_status=account_status,
            authority=self.authority,
        )
        event = self.record.append("CLOSURE", body)
        # External commitment: anchor the new head state outside the
        # record, so a wholesale re-chained rewrite is detectable.
        commit_record_head(self.record, self.anchors_dir)
        return event


def append_closure(record, termination: str, **kwargs) -> dict:
    """Convenience: append a CLOSURE event to ``record``."""
    return ClosureWriter(record).close(termination, **kwargs)
