"""Duenna Stage 1 — independent closure validator.

The validator is INDEPENDENT of the writer: it reads ONLY the record
file fresh from disk (never the writer's in-memory objects) and
reports G4's THREE INDEPENDENT RESULTS, never one collapsed boolean:

(i)   ``terminal_record`` — exactly one CLOSURE event exists and it
      is the last event in the record (C1, Vane examination). A parse
      or structural failure makes this FAIL explicitly, because the
      actual terminal state is then unknown (C4).
(ii)  ``account_completeness`` — the closure account must first
      satisfy its own documented schema (C6): ``account_status``
      present and valid, ``unknowns`` present as a list of non-empty
      strings, an INCOMPLETE account naming at least one unknown,
      and the minting ``authority`` present on the account and on
      each failure entry. A malformed account is rejected (FAIL),
      never merely classified. The account is then reconciled
      against the record itself: FAILURE events in the record and
      failures in the closure account must match as exact sets with
      non-empty unique failure_ids, required fields validated, and
      description/attribution/authority matching the FAILURE event
      as source of truth (C2; authority added by the hardening
      follow-up — presence is not consistency). Wherever a value
      must name something, a WHITESPACE-ONLY value (a string of
      nothing but whitespace) is rejected: it is present, but it
      names nothing. Original values are always preserved in the
      details for evidence. Omitted, extra, duplicate or altered entries
      FAIL, whatever the account declares. An account that declares
      COMPLETE while naming unknowns also FAILs. A well-formed
      account whose status is INCOMPLETE is reported as INCOMPLETE.
(iii) ``chain_validity`` — ``record.verify_chain`` recomputed over
      the fresh-read events AND the fresh-read head compared against
      the external anchor. Missing/unreadable anchor -> NOT_VERIFIED.

Structurally malformed events (valid JSON with missing/mistyped
fields) yield a structured FAIL, never a crash (C4).

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (G4, G5, K9),
PROCESS-TREE-AND-PLAN.md v2, Stage 1; Vane examination C1/C2/C4/C5
and his corrected-implementation examination (C6).
"""

from __future__ import annotations

import json
import os
from collections import Counter

from anchor import anchor_path_for, read_anchor
from record import verify_chain, _is_structurally_valid_event

PASS = "PASS"
FAIL = "FAIL"
INCOMPLETE = "INCOMPLETE"
NOT_VERIFIED = "NOT_VERIFIED"

VALID_ATTRIBUTIONS = ("SYSTEM", "MODEL", "INPUT", "UNKNOWN")
VALID_ACCOUNT_STATUSES = ("COMPLETE", "INCOMPLETE")


def _read_events_fresh(path: str) -> tuple[list[dict], str | None]:
    """Read the record file fresh from disk.

    Returns (events, parse_error). On a parse or structural error,
    events holds the events read before the bad line and parse_error
    names the problem; callers report structured FAIL rather than
    guessing or crashing.
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
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                return events, f"line {lineno}: invalid JSON: {exc}"
            if not _is_structurally_valid_event(obj):
                return events, (
                    f"line {lineno}: structurally malformed event: "
                    f"missing or mistyped fields in {obj!r:.200}"
                )
            events.append(obj)
    return events, None


def _check_terminal_record(events: list[dict], parse_error: str | None = None) -> tuple[str, dict]:
    # C4: parse/structural failure explicitly accounts here -- the
    # terminal state is unknown, so it cannot PASS on a parsed prefix.
    if parse_error is not None:
        return FAIL, {"closure_events": len([ev for ev in events if isinstance(ev, dict) and ev.get("type") == "CLOSURE"]),
                      "reason": f"parse failure: {parse_error}; terminal state unknown",
                      "parse_error": parse_error}
    closures = [ev for ev in events if isinstance(ev, dict) and ev.get("type") == "CLOSURE"]
    if not closures:
        return FAIL, {"closure_events": 0, "reason": "no CLOSURE event"}
    # C1: exactly one CLOSURE required
    if len(closures) != 1:
        return FAIL, {
            "closure_events": len(closures),
            "reason": f"expected exactly one CLOSURE event, found {len(closures)}",
        }
    if not events or events[-1].get("type") != "CLOSURE":
        return FAIL, {
            "closure_events": len(closures),
            "reason": "last event is not CLOSURE",
            "last_type": events[-1].get("type") if events else None,
        }
    return PASS, {"closure_events": len(closures),
                  "closure_seq": events[-1].get("seq")}


def _duplicates(ids):
    c = Counter(ids)
    return sorted([k for k, v in c.items() if v > 1], key=lambda x: str(x))


def _has_content(value) -> bool:
    """Whether a value actually names something.

    The term is WHITESPACE-ONLY (Ben's ruling, 2026-11-19, on Vane's
    C6-examination observation): a string of nothing but whitespace
    is present, and passes a plain non-empty check, but names
    nothing — so wherever the schema requires a value to name
    something (an unknown, an authority, a failure_id, a
    description), a whitespace-only value is rejected. The check
    never trims the value itself: the original is preserved in the
    details for evidence.
    """
    return isinstance(value, str) and bool(value.strip())


def _check_account_completeness(events: list[dict], parse_error: str | None = None) -> tuple[str, dict]:
    if parse_error is not None:
        return FAIL, {"reason": f"parse failure: {parse_error}; account cannot be reconciled",
                      "parse_error": parse_error}
    closures = [ev for ev in events if isinstance(ev, dict) and ev.get("type") == "CLOSURE"]
    if not closures:
        return FAIL, {"reason": "no CLOSURE event; no account to reconcile"}
    closure = closures[-1]
    body = closure.get("body") or {}
    if not isinstance(body, dict):
        return FAIL, {"reason": "CLOSURE body is not an object"}
    account = body.get("account")
    if not isinstance(account, dict):
        return FAIL, {"reason": "CLOSURE event has no account section"}

    # C6 (Vane, corrected-implementation examination): the account
    # itself must satisfy its documented schema (closure.py, K9),
    # independently of whether its failures reconcile. C2 proves
    # recorded failures are reconciled; C6 proves the account
    # satisfies its declared contract. A malformed account is
    # rejected below, never merely classified as incomplete.
    schema_invalid = []
    status_field = account.get("account_status")
    if status_field not in VALID_ACCOUNT_STATUSES:
        schema_invalid.append(
            {"reason": f"account_status missing or invalid: {status_field!r}"})
    if "unknowns" not in account:
        schema_invalid.append({"reason": "account unknowns missing"})
    elif not isinstance(account.get("unknowns"), list):
        schema_invalid.append(
            {"reason": f"account unknowns is not a list: {account.get('unknowns')!r}"})
    else:
        for u in account["unknowns"]:
            if not _has_content(u):
                schema_invalid.append(
                    {"reason": f"account unknowns entry must name something (a non-empty string, not whitespace-only): {u!r}"})
        if status_field == "INCOMPLETE" and not account["unknowns"]:
            schema_invalid.append(
                {"reason": "account declares INCOMPLETE without naming any unknowns"})
    account_authority = account.get("authority")
    if not _has_content(account_authority):
        schema_invalid.append(
            {"reason": "account authority must name an authority (a non-empty string, not whitespace-only)"})

    # Collect record FAILURE events as source of truth
    record_entries = []
    record_failure_ids = []
    record_by_id = {}
    record_invalid = []
    for ev in events:
        if not isinstance(ev, dict) or ev.get("type") != "FAILURE":
            continue
        b = ev.get("body")
        if not isinstance(b, dict):
            record_invalid.append({"reason": "FAILURE body is not an object", "body": b})
            record_failure_ids.append(None)
            continue
        fid = b.get("failure_id")
        record_failure_ids.append(fid)
        record_entries.append(b)
        # Validate required fields (whitespace-only names nothing)
        if not _has_content(fid):
            record_invalid.append({"failure_id": fid, "reason": "record failure_id must be a string naming something (non-empty, not whitespace-only)"})
        if not _has_content(b.get("description")):
            record_invalid.append({"failure_id": fid, "reason": "record description must be a string naming something (non-empty, not whitespace-only)"})
        if b.get("attribution") not in VALID_ATTRIBUTIONS:
            record_invalid.append({"failure_id": fid, "reason": f"record attribution invalid: {b.get('attribution')!r}"})
        if not _has_content(b.get("authority")):
            record_invalid.append({"failure_id": fid, "reason": "record failure authority must be a string naming an authority (non-empty, not whitespace-only)"})
        if isinstance(fid, str) and fid:
            # Keep first as source of truth for altered comparison; duplicates handled separately
            if fid not in record_by_id:
                record_by_id[fid] = b

    account_failures = account.get("failures")
    if not isinstance(account_failures, list):
        return FAIL, {"reason": "account has no failures list",
                      "record_failure_ids": record_failure_ids}
    account_failure_ids = []
    account_by_id = {}
    account_invalid = []
    for f in account_failures:
        if not isinstance(f, dict):
            account_invalid.append({"reason": "account failure entry is not an object", "entry": f})
            account_failure_ids.append(None)
            continue
        fid = f.get("failure_id")
        account_failure_ids.append(fid)
        if not _has_content(fid):
            account_invalid.append({"failure_id": fid, "reason": "account failure_id must be a string naming something (non-empty, not whitespace-only)"})
        if not _has_content(f.get("description")):
            account_invalid.append({"failure_id": fid, "reason": "account description must be a string naming something (non-empty, not whitespace-only)"})
        if f.get("attribution") not in VALID_ATTRIBUTIONS:
            account_invalid.append({"failure_id": fid, "reason": f"account attribution invalid: {f.get('attribution')!r}"})
        # C6: the documented schema requires the minting authority
        # on each account failure entry as well.
        if not _has_content(f.get("authority")):
            account_invalid.append({"failure_id": fid, "reason": "account failure authority must be a string naming an authority (non-empty, not whitespace-only)"})
        if isinstance(fid, str) and fid and fid not in account_by_id:
            account_by_id[fid] = f

    duplicate_record = _duplicates([x for x in record_failure_ids if isinstance(x, str) and x])
    duplicate_account = _duplicates([x for x in account_failure_ids if isinstance(x, str) and x])

    # Exact-set reconciliation
    record_set = set([x for x in record_failure_ids if isinstance(x, str) and x])
    account_set = set([x for x in account_failure_ids if isinstance(x, str) and x])
    omitted = [fid for fid in record_failure_ids if fid not in account_failure_ids]
    # Preserve original omitted semantics (list in record order) for regression fixture,
    # but also compute set-based omitted/extra
    omitted_set = sorted(record_set - account_set)
    extra = sorted(account_set - record_set)
    extra_failure_ids = extra

    # Altered: description/attribution/authority differ from the
    # FAILURE event as source of truth. Authority joined the
    # comparison in the hardening follow-up (Vane's C6-examination
    # observation: presence is not consistency — an account entry
    # minted under a different authority than its source event is
    # an altered entry, even when both values are present).
    altered = []
    altered_details = []
    for fid in sorted(record_set & account_set):
        rec = record_by_id.get(fid, {})
        acc = account_by_id.get(fid, {})
        if rec.get("description") != acc.get("description") or rec.get("attribution") != acc.get("attribution") or rec.get("authority") != acc.get("authority"):
            altered.append(fid)
            altered_details.append({"failure_id": fid, "record": {"description": rec.get("description"), "attribution": rec.get("attribution"), "authority": rec.get("authority")}, "account": {"description": acc.get("description"), "attribution": acc.get("attribution"), "authority": acc.get("authority")}})

    details = {
        "record_failure_ids": record_failure_ids,
        "account_failure_ids": account_failure_ids,
        "omitted_failure_ids": omitted,
        "extra_failure_ids": extra_failure_ids,
        "duplicate_record_failure_ids": duplicate_record,
        "duplicate_account_failure_ids": duplicate_account,
        "altered_failure_ids": altered,
        "altered_details": altered_details,
        "record_invalid": record_invalid,
        "account_invalid": account_invalid,
        "account_schema_invalid": schema_invalid,
        "account_status": account.get("account_status"),
        "unknowns": account.get("unknowns"),
    }

    if schema_invalid:
        details["reason"] = "closure account fails its documented schema (C6)"
        return FAIL, details
    if record_invalid:
        details["reason"] = "record FAILURE event(s) have invalid required fields"
        return FAIL, details
    if account_invalid:
        details["reason"] = "account failure entr(ies) have invalid required fields"
        return FAIL, details
    if duplicate_record:
        details["reason"] = "duplicate failure_id(s) in record"
        return FAIL, details
    if duplicate_account:
        details["reason"] = "duplicate failure_id(s) in account"
        return FAIL, details
    if omitted:
        details["reason"] = "FAILURE event(s) missing from closure account"
        return FAIL, details
    if extra:
        details["reason"] = "account contains failure(s) not in record"
        return FAIL, details
    if altered:
        details["reason"] = "account failure description/attribution/authority differs from record FAILURE event"
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
    try:
        ok, bad_seq = verify_chain(events)
    except Exception as exc:
        return FAIL, {"reason": f"chain verification crashed: {exc}", "anchor_path": anchor_path}
    if not ok:
        return FAIL, {"first_bad_seq": bad_seq, "anchor_path": anchor_path}
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
    """
    if anchor_path is None:
        anchor_path = anchor_path_for(path, anchors_dir)
    events, parse_error = _read_events_fresh(path)
    terminal, terminal_details = _check_terminal_record(events, parse_error)
    account, account_details = _check_account_completeness(events, parse_error)
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
