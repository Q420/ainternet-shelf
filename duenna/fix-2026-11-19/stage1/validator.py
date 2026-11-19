"""Duenna Stage 1 — independent closure validator.

The validator is INDEPENDENT of the writer: it reads ONLY the record
file fresh from disk (never the writer's in-memory objects) and
reports G4's THREE INDEPENDENT RESULTS, never one collapsed boolean:

(i)   ``terminal_record`` — a CLOSURE event exists and is the last
      event in the record.
(ii)  ``account_completeness`` — the closure account is reconciled
      against the record itself: every FAILURE event in the record
      must appear in the closure account's failures list, matched by
      ``failure_id``. A FAILURE event missing from the account makes
      this FAIL, whatever the account declares about itself — a
      record must not certify its own completeness. An account that
      declares COMPLETE while naming unknowns also FAILs. An account
      whose status is INCOMPLETE is reported as INCOMPLETE — a
      distinct, honest result, neither a pass nor a failure.
(iii) ``chain_validity`` — ``record.verify_chain`` recomputed over
      the fresh-read events AND the fresh-read head (digest + length)
      compared against the external anchor (anchor.py, step 4). The
      chain alone cannot detect a wholesale re-chained rewrite; the
      anchor can. If the anchor file is missing or unreadable this
      dimension reports NOT_VERIFIED — a distinct, honest result,
      neither a pass nor a fail. A chain that fails recomputation,
      or a head that mismatches a readable anchor, is a FAIL.

Each result is reported on its own dimension: a record can pass one
and fail another, and the failing dimension is reported as such while
the record stands.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (G4, G5, K9),
PROCESS-TREE-AND-PLAN.md v2, Stage 1.
"""

from __future__ import annotations

import json
import os

from anchor import anchor_path_for, read_anchor
from record import verify_chain

PASS = "PASS"
FAIL = "FAIL"
INCOMPLETE = "INCOMPLETE"
NOT_VERIFIED = "NOT_VERIFIED"


def _read_events_fresh(path: str) -> tuple[list[dict], str | None]:
    """Read the record file fresh from disk.

    Returns (events, parse_error). On a parse error, events holds the
    events read before the bad line and parse_error names the problem;
    the caller reports chain validity as FAIL rather than guessing.
    """
    events: list[dict] = []
    if not os.path.exists(path):
        return events, f"record file not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                return events, f"line {lineno}: invalid JSON: {exc}"
    return events, None


def _check_terminal_record(events: list[dict]) -> tuple[str, dict]:
    closures = [ev for ev in events if ev.get("type") == "CLOSURE"]
    if not closures:
        return FAIL, {"closure_events": 0, "reason": "no CLOSURE event"}
    if events[-1].get("type") != "CLOSURE":
        return FAIL, {
            "closure_events": len(closures),
            "reason": "last event is not CLOSURE",
            "last_type": events[-1].get("type"),
        }
    return PASS, {"closure_events": len(closures),
                  "closure_seq": events[-1].get("seq")}


def _check_account_completeness(events: list[dict]) -> tuple[str, dict]:
    closures = [ev for ev in events if ev.get("type") == "CLOSURE"]
    if not closures:
        return FAIL, {"reason": "no CLOSURE event; no account to reconcile"}
    closure = closures[-1]
    body = closure.get("body") or {}
    account = body.get("account")
    if not isinstance(account, dict):
        return FAIL, {"reason": "CLOSURE event has no account section"}

    # Reconcile the record's FAILURE events against the account, by id.
    record_failure_ids = [
        (ev.get("body") or {}).get("failure_id")
        for ev in events if ev.get("type") == "FAILURE"
    ]
    account_failures = account.get("failures")
    if not isinstance(account_failures, list):
        return FAIL, {"reason": "account has no failures list",
                      "record_failure_ids": record_failure_ids}
    account_failure_ids = [f.get("failure_id") for f in account_failures
                           if isinstance(f, dict)]
    omitted = [fid for fid in record_failure_ids
               if fid not in account_failure_ids]

    details = {
        "record_failure_ids": record_failure_ids,
        "account_failure_ids": account_failure_ids,
        "omitted_failure_ids": omitted,
        "account_status": account.get("account_status"),
        "unknowns": account.get("unknowns"),
    }

    # An omitted FAILURE event fails this dimension whatever the
    # account declares — completeness is established by reconciliation
    # against the record, never by the closure's own declaration.
    if omitted:
        details["reason"] = "FAILURE event(s) missing from closure account"
        return FAIL, details

    status = account.get("account_status")
    unknowns = account.get("unknowns") or []
    if status == "COMPLETE" and unknowns:
        details["reason"] = "account declares COMPLETE while naming unknowns"
        return FAIL, details
    if status == "INCOMPLETE":
        details["reason"] = "account declares itself INCOMPLETE"
        return INCOMPLETE, details
    if status != "COMPLETE":
        details["reason"] = f"unrecognised account_status: {status!r}"
        return FAIL, details
    return PASS, details


def _check_chain_validity(events: list[dict],
                          parse_error: str | None,
                          anchor_path: str) -> tuple[str, dict]:
    if parse_error is not None:
        return FAIL, {"reason": parse_error, "anchor_path": anchor_path}
    ok, bad_seq = verify_chain(events)
    if not ok:
        return FAIL, {"first_bad_seq": bad_seq, "anchor_path": anchor_path}
    # Chain recomputes — now the external commitment. The anchor is
    # NOT supplied by the record: it was committed separately, from
    # head state values only, at closure time.
    anchor = read_anchor(anchor_path)
    if anchor is None:
        return NOT_VERIFIED, {
            "reason": "anchor file missing or unreadable; integrity "
                      "not verified",
            "anchor_path": anchor_path,
            "events_checked": len(events),
        }
    head_digest = events[-1].get("digest") if events else "GENESIS"
    head = {"head_digest": head_digest, "length": len(events)}
    if head["head_digest"] != anchor["head_digest"] or \
            head["length"] != anchor["length"]:
        return FAIL, {
            "reason": "head state does not match external anchor "
                      "(possible wholesale re-chained rewrite)",
            "anchor_path": anchor_path,
            "record_head": head,
            "anchor": anchor,
        }
    return PASS, {"events_checked": len(events),
                  "anchor_path": anchor_path, "anchor": anchor}


def validate_record(path: str, anchor_path: str | None = None,
                    anchors_dir: str | None = None) -> dict:
    """Validate the record file at ``path``, fresh from disk.

    Returns a dict with G4's three independent results —
    ``terminal_record``, ``account_completeness`` and
    ``chain_validity`` — each one of PASS / FAIL (account completeness
    may also be INCOMPLETE; chain validity may also be
    NOT_VERIFIED when the external anchor is unavailable), plus a
    ``details`` dict per dimension.

    The anchor is looked up at ``anchor_path`` when given, else at
    the default separate anchor path for this record (see anchor.py).
    """
    if anchor_path is None:
        anchor_path = anchor_path_for(path, anchors_dir)
    events, parse_error = _read_events_fresh(path)
    terminal, terminal_details = _check_terminal_record(events)
    account, account_details = _check_account_completeness(events)
    chain, chain_details = _check_chain_validity(events, parse_error,
                                                 anchor_path)
    return {
        "terminal_record": terminal,
        "account_completeness": account,
        "chain_validity": chain,
        "details": {
            "terminal_record": terminal_details,
            "account_completeness": account_details,
            "chain_validity": chain_details,
        },
    }


class RecordValidator:
    """Thin class wrapper around :func:`validate_record`."""

    def __init__(self, path: str, anchor_path: str | None = None,
                 anchors_dir: str | None = None):
        self.path = path
        self.anchor_path = anchor_path
        self.anchors_dir = anchors_dir

    def validate(self) -> dict:
        return validate_record(self.path, anchor_path=self.anchor_path,
                               anchors_dir=self.anchors_dir)
