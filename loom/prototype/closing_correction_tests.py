#!/usr/bin/env python3
"""Closing correction round — CC-3 negative cases + CC-1/CC-2
live binding checks.

Built 2026-11-21 against Vane's integrated examination of the
closing exercise (CLOSING EXERCISE NOT ACCEPTED, blocker B1+B2):
a checker-origin structural tension's origin_ref carried
"seal-attempt:<seq>" — not the UUID Rev 9 section 3 requires of
an id field — and neither fold validated the format; the
resolution evidence cited a sequence where the contract
requires the passing attempt's event ID.

CC-3 cases: hash-valid canned histories whose TENSION_RAISED
carries a malformed origin_ref must halt at the offending
sequence with schema_invalid in BOTH independent folds (the
engine's verified_fold and the checker's own fold). The
malformed value sits inside the hashed payload by construction
(each history's hashes recompute), so hash validity cannot save
it. The format-only line is shown from the other side: a
well-formed UUID naming no record in the history folds cleanly
in both — format is validated, existence is not the fold's to
judge.

Closing correction round 2 (CC2-B2) amends this suite: the
first round's lowercase-canonical rule was stricter than the
pinned contract establishes — Annex B's format: "uuid" names
the RFC 4122 textual form, whose hexadecimal digits are
case-insensitive, and the pinned text does not fix the
rendering's case. The upper-case history therefore moves from
the malformed set to a positive case below: it folds cleanly
in both folds. The malformed set keeps its other members.

CC-1/CC-2 case: one live bound run through the harness — the
raised tension's origin_ref is the failing attempt's actual
event_id, and the resolution evidence's seal_attempt_event_id
is the passing attempt's actual event_id (seal_attempt_seq
remains present as diagnostic).

Run: python3 closing_correction_tests.py — prints PASS/FAIL per
check; exit status is non-zero on any failure.
"""
import os
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fabric.checker as checker_mod
from fabric.canonical import event_hash
from fabric.engine import (Engine, ReplayHalt, state_hash,
                           verified_fold)
from fabric.fixture import (COMPONENTS, CONTINUITY, INTERACTIONS,
                            PRESENTATION, STATE, CONSTITUTION_HASH,
                            SYSTEM_ACTOR, genesis_payload)
from fabric.harness import Harness
from fabric.packpin import stage4_binding
from fabric.store import EventStore

D_CS = "00000000-0000-4000-8000-000000000102"  # Components uses State
A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
GOOD_REF = "97b88a7c-acc2-4962-b233-91a35b70b0c2"

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def new_id():
    return str(uuid.uuid4())


# -- canned hash-valid histories ------------------------------------

def chain(specs):
    events = []
    prev = CONSTITUTION_HASH
    for i, (t, actor, affected, payload) in enumerate(specs, 1):
        ev = {"event_seq": i, "event_id": new_id(), "type": t,
              "actor": actor, "affected": list(affected),
              "payload": payload, "prev_hash": prev}
        ev["hash"] = event_hash(prev, ev)
        events.append(ev)
        prev = ev["hash"]
    return events


def opened():
    return ("RUN_OPENED", SYSTEM_ACTOR, [], genesis_payload())


def structural_tension(tid, origin_ref, omit_ref=False):
    payload = {"tension_id": tid, "type": "structural",
               "regions": [STATE], "origin": "checker",
               "description": "Canned structural tension for the "
                              "closing correction round.",
               "status": "open", "check": "S1",
               "affected": [D_CS, STATE],
               "summary": "A canned structural tension."}
    if not omit_ref:
        payload["origin_ref"] = origin_ref
    return ("TENSION_RAISED", SYSTEM_ACTOR, [STATE], payload)


def engine_outcome(history):
    try:
        state = verified_fold(history, CONSTITUTION_HASH)
        return ("ok", state)
    except ReplayHalt as halt:
        return ("halt", halt.seq, halt.reason_class)


def checker_outcome(history):
    try:
        state = checker_mod._fold(history, CONSTITUTION_HASH)
        return ("ok", state)
    except checker_mod._Halt as halt:
        return ("halt", halt.seq, halt.reason_class)


def halt_case(name, history, seq):
    eng = engine_outcome(history)
    chk = checker_outcome(history)
    check(f"CC-3: {name} — engine fold halts schema_invalid at "
          f"seq {seq}",
          eng == ("halt", seq, "schema_invalid"), f"got {eng}")
    check(f"CC-3: {name} — checker fold halts schema_invalid at "
          f"seq {seq}",
          chk == ("halt", seq, "schema_invalid"), f"got {chk}")


# The exact defect Vane found, as a canned history: a sequence
# label where an id belongs, inside a hash-valid event.
halt_case("origin_ref 'seal-attempt:29' at seq 2",
          chain([opened(),
                 structural_tension("t-cc1", "seal-attempt:29")]), 2)

# The same defect one event later: the fold must halt AT the
# offending sequence, having folded the valid tension before it.
halt_case("origin_ref 'seal-attempt:29' at seq 3, after a valid "
          "tension at seq 2",
          chain([opened(),
                 structural_tension("t-cc2a", GOOD_REF),
                 structural_tension("t-cc2b", "seal-attempt:29")]), 3)

# A non-string origin_ref is not a UUID either.
halt_case("origin_ref carried as an integer",
          chain([opened(), structural_tension("t-cc3", 29)]), 2)

# A missing origin_ref fails the schema the same way.
halt_case("origin_ref missing",
          chain([opened(),
                 structural_tension("t-cc4", None, omit_ref=True)]),
          2)

# A well-formed UUID folds cleanly in both implementations, and
# the folded record carries it verbatim.
hist = chain([opened(), structural_tension("t-cc6", GOOD_REF)])
eng = engine_outcome(hist)
chk = checker_outcome(hist)
check("CC-3: a well-formed UUID origin_ref folds cleanly in "
      "both folds, the record carrying it verbatim",
      eng[0] == "ok" and chk[0] == "ok"
      and eng[1]["tensions"]["t-cc6"]["origin_ref"] == GOOD_REF
      and chk[1]["tensions"]["t-cc6"]["origin_ref"] == GOOD_REF)

# CC2-B2: the rendering's case is not fixed by the pinned
# format: "uuid" contract — an upper-case rendering of a UUID
# is a valid RFC 4122 textual representation and folds cleanly
# in both folds, the record carrying it verbatim. (Round 1's
# suite halted on this history under a lowercase-canonical rule
# the pinned text does not establish; that rule is withdrawn
# and the case stands here, on the accepting side.)
hist = chain([opened(),
              structural_tension("t-cc5", GOOD_REF.upper())])
eng = engine_outcome(hist)
chk = checker_outcome(hist)
check("CC2-B2: an upper-case UUID origin_ref folds cleanly in "
      "both folds, the record carrying it verbatim",
      eng[0] == "ok" and chk[0] == "ok"
      and eng[1]["tensions"]["t-cc5"]["origin_ref"]
      == GOOD_REF.upper()
      and chk[1]["tensions"]["t-cc5"]["origin_ref"]
      == GOOD_REF.upper())

# The format-only line: a well-formed UUID naming NO record in
# the history is not the fold's to refuse — format is validated,
# existence is not judged here.
ghost = new_id()
hist = chain([opened(), structural_tension("t-cc7", ghost)])
eng = engine_outcome(hist)
chk = checker_outcome(hist)
check("CC-3: a UUID-shaped reference to a nonexistent record "
      "folds cleanly in both folds (format validated, existence "
      "not judged)",
      eng[0] == "ok" and chk[0] == "ok"
      and eng[1]["tensions"]["t-cc7"]["origin_ref"] == ghost)

# -- CC-1/CC-2: the live binding through the harness -----------------

store = EventStore(os.path.join(tempfile.mkdtemp(), "cc-live.db"))
eng = Engine.open_run(store, "cc-live", binding=stage4_binding())
h = Harness(eng)


def events_of(type_):
    return [e for e in store.all_events() if e["type"] == type_]


def open_regions(token, *rids):
    seq = None
    for rid in rids:
        h.open_region(token, rid)
        seq = store.all_events()[-1]["event_seq"]
    return seq


def contrib(author, idem, base, read, write, ops, ref):
    return {"action": "contribute", "contribution": {
        "author": author, "idempotency_id": idem,
        "base_versions": base, "read_set": read, "write_set": write,
        "operations": ops, "rationale": "Recorded rationale.",
        "discovery_source": "fabric_read", "discovery_ref": ref}}


def versions(*rids):
    return {r: eng.state["regions"][r]["version"] for r in rids}


tok = h.issue_token(A)
ref = open_regions(tok, INTERACTIONS, PRESENTATION)
del eng.state["regions"][STATE]  # the fault: live state only
out = h.submit(tok, contrib(
    A, new_id(), versions(INTERACTIONS, PRESENTATION),
    [INTERACTIONS, PRESENTATION], [INTERACTIONS],
    [{"kind": "append_content", "region_id": INTERACTIONS,
      "text": " (Ordinary work.)"}], ref))
attempts = events_of("SEAL_ATTEMPTED")
raised = [e for e in events_of("TENSION_RAISED")
          if e["payload"].get("type") == "structural"]
check("CC-1: the checker-raised tension's origin_ref is the "
      "failing attempt's actual event_id",
      out["outcome"] == "accepted" and len(attempts) == 1
      and len(raised) == 1
      and raised[0]["payload"]["origin_ref"]
      == attempts[0]["event_id"],
      f"origin_ref={raised[0]['payload']['origin_ref'] if raised else None} "
      f"attempt={attempts[0]['event_id'] if attempts else None}")
tid = raised[0]["payload"]["tension_id"] if raised else None
check("CC-1: the folded tension record carries the same "
      "origin_ref (the fold passes the binding through)",
      tid is not None
      and eng.state["tensions"][tid]["origin_ref"]
      == attempts[0]["event_id"])

eng.state = verified_fold(store.all_events(), CONSTITUTION_HASH)
tok2 = h.issue_token(B)
ref2 = open_regions(tok2, COMPONENTS, STATE)
out = h.submit(tok2, contrib(
    B, new_id(), versions(COMPONENTS, STATE), [COMPONENTS, STATE],
    [COMPONENTS, STATE],
    [{"kind": "remove_dependency", "dependency_id": D_CS}], ref2))
attempts = events_of("SEAL_ATTEMPTED")
status = [e for e in events_of("TENSION_STATUS")
          if e["payload"]["tension_id"] == tid]
evidence = status[0]["payload"]["evidence"] if status else {}
check("CC-2: the resolution evidence's seal_attempt_event_id "
      "is the passing attempt's actual event_id",
      out["outcome"] == "accepted" and len(status) == 1
      and attempts[-1]["payload"]["outcome"] == "pass"
      and evidence.get("seal_attempt_event_id")
      == attempts[-1]["event_id"],
      f"evidence={evidence}")
check("CC-2: seal_attempt_seq remains in the evidence as "
      "diagnostic, naming the same attempt",
      evidence.get("seal_attempt_seq") == attempts[-1]["event_seq"])

print()
if failures:
    print(f"CLOSING CORRECTION TESTS: {len(failures)} FAILURES: "
          f"{failures}")
    sys.exit(1)
print("CLOSING CORRECTION TESTS: ALL PASS")
