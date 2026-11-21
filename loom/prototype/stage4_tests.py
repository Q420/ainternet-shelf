#!/usr/bin/env python3
"""Stage 4 test suite — seals, the structural lifecycle, the
independent checker, and the pinned pack's live vectors.

Stage 4 (2026-11-21), Loom spec v0.1 Rev 9 section 7 + Amendment
A1 + the settled Stage 4 design (Brief Rev 2) + the pinned
examiner validation pack V2. This suite carries the vectors the
pack harness does not: TV-1 in VP-45's nine-step form through the
real socket boundary (fault via the operator-path hook, repair by
service restart — build notes I-5), TV-6 (one inconsistency, one
tension), TV-8 (stood-down follows the declared regions), TV-13's
genuine resolution half (the structural tension raised by a real
failed seal attempt, never a canned fixture), the VP-36
checker-failure contract in service form, the VP-55 binding in
service form, VP-38's close in service form, and the
malformed-payload hardening negatives in Stage 3 corrections
style. The pack itself (VP-01..VP-55 against both implementations)
is executed by pack_validation.py.

Run: python3 stage4_tests.py — prints PASS/FAIL per check and a
summary; exit status is non-zero on any failure.
"""
import copy
import os
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.canonical import canonical, sha256_hex
from fabric.engine import (Engine, ReplayHalt, state_hash,
                           verified_fold)
from fabric.fixture import CONSTITUTION_HASH, SYSTEM_ACTOR
from fabric.harness import Harness
from fabric.packpin import PACK_ID, PACK_SHA256, PACK_VERSION, stage4_binding
from fabric.starvation import build_report, report_bytes
from fabric.store import EventStore

COMPONENTS = "11111111-1111-4111-8111-111111111111"
INTERACTIONS = "22222222-2222-4222-8222-222222222222"
STATE = "33333333-3333-4333-8333-333333333333"
CONTINUITY = "44444444-4444-4444-8444-444444444444"
PRESENTATION = "55555555-5555-4555-8555-555555555555"
OPERATIONS = "66666666-6666-4666-8666-666666666666"
D_CS = "00000000-0000-4000-8000-000000000102"  # Components uses State

A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
Cc = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
D = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def new_id():
    return str(uuid.uuid4())


def bound_run(name):
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    engine = Engine.open_run(store, name, binding=stage4_binding())
    return store, engine, Harness(engine)


def contrib(author, idem, base, read, write, ops, ref,
            rationale="Recorded rationale."):
    return {"action": "contribute", "contribution": {
        "author": author, "idempotency_id": idem, "base_versions": base,
        "read_set": read, "write_set": write, "operations": ops,
        "rationale": rationale, "discovery_source": "fabric_read",
        "discovery_ref": ref}}


def report(author, exam_id, idem, regions, ref, description="Noted."):
    return {"author": author, "examination_id": exam_id,
            "idempotency_id": idem, "regions": regions,
            "description": description,
            "discovery_source": "fabric_read", "discovery_ref": ref}


def t_assess(author, aid, target, position):
    return {"assessment_id": aid, "author": author,
            "target_kind": "tension", "target_id": target,
            "position": position, "reasoning": "Recorded reasoning."}


def open_regions(h, store, token, *rids):
    seq = None
    for rid in rids:
        h.open_region(token, rid)
        seq = store.all_events()[-1]["event_seq"]
    return seq


def versions(engine, *rids):
    return {r: engine.state["regions"][r]["version"] for r in rids}


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def structural_tensions(store):
    return [e for e in events_of(store, "TENSION_RAISED")
            if e["payload"].get("type") == "structural"]


def structural_tensions_from(events):
    return [e for e in events if e["type"] == "TENSION_RAISED"
            and e["payload"].get("type") == "structural"]


def state_versions(state, *rids):
    return {r: state["regions"][r]["version"] for r in rids}


def fault_and_raise(name):
    """The genuine TV-1 setup, in-process: drop State from the
    live derived state only, then an ordinary contribution
    independent of State. Returns (store, engine, harness,
    tension_id)."""
    store, eng, h = bound_run(name)
    tok = h.issue_token(A)
    ref = open_regions(h, store, tok, INTERACTIONS, PRESENTATION)
    del eng.state["regions"][STATE]
    out = h.submit(tok, contrib(
        A, new_id(), versions(eng, INTERACTIONS, PRESENTATION),
        [INTERACTIONS, PRESENTATION], [INTERACTIONS],
        [{"kind": "append_content", "region_id": INTERACTIONS,
          "text": " (Ordinary work.)"}], ref))
    assert out["outcome"] == "accepted", out
    raised = structural_tensions(store)
    assert len(raised) == 1, raised
    return store, eng, h, raised[0]["payload"]["tension_id"]


# =====================================================================
# TV-6 — one inconsistency, one tension.
# =====================================================================
store, eng, h, tid6 = fault_and_raise("stage4-tv6")
tok = h.issue_token(B)
ref = open_regions(h, store, tok, INTERACTIONS, PRESENTATION)
for n in range(2):
    out = h.submit(tok, contrib(
        B, new_id(), versions(eng, INTERACTIONS, PRESENTATION),
        [INTERACTIONS, PRESENTATION], [PRESENTATION],
        [{"kind": "append_content", "region_id": PRESENTATION,
          "text": f" (Further work {n}.)"}], ref))
    assert out["outcome"] == "accepted", out
attempts = events_of(store, "SEAL_ATTEMPTED")
check("TV-6: both further attempts fail on the same check and set",
      len(attempts) == 3
      and all(a["payload"]["outcome"] == "fail"
              and a["payload"]["failed_checks"] == [
                  {"check": "S1", "affected": [D_CS, STATE]}]
              for a in attempts[1:]))
check("TV-6: exactly one structural tension with that identity "
      "exists throughout; no duplicate TENSION_RAISED",
      len(structural_tensions(store)) == 1
      and eng.state["tensions"][tid6]["status"] == "open")
check("TV-6: the later attempts record their findings against "
      "the standing tension",
      all(a["payload"].get("findings_attached") == [tid6]
          for a in attempts[1:]))

# =====================================================================
# TV-8 — stood-down follows the declared regions, exactly.
# =====================================================================
store, eng, h = bound_run("stage4-tv8")
toks = {x: h.issue_token(x) for x in (A, B, Cc)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
t_in = out["tension_id"]
h.assess(toks[B], t_assess(B, new_id(), t_in, "remains"))
out = h.assess(toks[Cc], t_assess(Cc, new_id(), t_in, "remains"))
check("TV-8: the {Interactions, Continuity} tension stands",
      out["outcome"] == "recorded"
      and eng.state["tensions"][t_in]["status"] == "standing")
check("TV-8: Interactions and Continuity become stood_down; "
      "Components and State are unaffected",
      eng.state["facet_status"].get(INTERACTIONS) == "stood_down"
      and eng.state["facet_status"].get(CONTINUITY) == "stood_down"
      and COMPONENTS not in eng.state["facet_status"]
      and STATE not in eng.state["facet_status"])
tok_d = h.issue_token(D)
seq_a2 = open_regions(h, store, tok_d, PRESENTATION)
out = h.examine(tok_d, report(D, new_id(), new_id(),
                              [PRESENTATION], seq_a2))
t_p = out["tension_id"]
h.assess(toks[B], t_assess(B, new_id(), t_p, "remains"))
out = h.assess(toks[Cc], t_assess(Cc, new_id(), t_p, "remains"))
check("TV-8: the {Presentation} tension stands but stands down "
      "no required facet",
      out["outcome"] == "recorded"
      and eng.state["tensions"][t_p]["status"] == "standing"
      and eng.state["facet_status"].get(PRESENTATION) is None
      and eng.state["facet_status"].get(INTERACTIONS) == "stood_down")

# =====================================================================
# TV-13 — the genuine resolution half: a schema-valid assessment
# cannot enter the structural lifecycle.
# =====================================================================
store, eng, h, tid13 = fault_and_raise("stage4-tv13")
tok = h.issue_token(B)
out = h.assess(tok, t_assess(B, new_id(), tid13, "addressed"))
recorded = events_of(store, "ASSESSMENT_RECORDED")
check("TV-13: exactly one ASSESSMENT_RECORDED, rejected "
      "structural_target; no assessment stands; no TENSION_STATUS "
      "for the structural tension; it remains open",
      out["outcome"] == "rejected"
      and out.get("reason") == "structural_target"
      and len(recorded) == 1
      and recorded[0]["payload"]["outcome"] == "rejected"
      and eng.state["assessments"] == {}
      and [e for e in events_of(store, "TENSION_STATUS")
           if e["payload"]["tension_id"] == tid13] == []
      and eng.state["tensions"][tid13]["status"] == "open")
eng.state = verified_fold(store.all_events(), CONSTITUTION_HASH)
tok2 = h.issue_token(Cc)
ref = open_regions(h, store, tok2, COMPONENTS, STATE)
out = h.submit(tok2, contrib(
    Cc, new_id(), versions(eng, COMPONENTS, STATE),
    [COMPONENTS, STATE], [COMPONENTS, STATE],
    [{"kind": "remove_dependency", "dependency_id": D_CS}], ref))
attempts = events_of(store, "SEAL_ATTEMPTED")
status = [e for e in events_of(store, "TENSION_STATUS")
          if e["payload"]["tension_id"] == tid13]
check("TV-13: the correcting contribution's passing attempt "
      "resolves the tension, with that attempt as its evidence — "
      "the attempted assessment plays no part",
      out["outcome"] == "accepted"
      and attempts[-1]["payload"]["outcome"] == "pass"
      and len(status) == 1
      and status[0]["payload"]["to"] == "resolved"
      and status[0]["payload"]["evidence"]["seal_attempt_seq"]
      == attempts[-1]["event_seq"]
      and eng.state["tensions"][tid13]["status"] == "resolved")

# =====================================================================
# Hardening negatives — malformed payloads halt controlled, in
# both folds, never as a native exception (Stage 4 carried item).
# =====================================================================
from fabric.canonical import event_hash
from fabric.fixture import genesis_payload
from fabric.seal import evaluate_attempt  # noqa: F401  (import surface)
import fabric.checker as checker_mod


def canned(specs):
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


def sem_tension(tid, **over):
    payload = {"tension_id": tid, "type": "semantic",
               "regions": [COMPONENTS], "origin": "contribution",
               "origin_ref": "caca0000-0000-4000-8000-000000000002",
               "description": "Canned.",
               "status": "open", "summary": "Canned tension."}
    payload.update(over)
    return ("TENSION_RAISED", SYSTEM_ACTOR, [COMPONENTS], payload)


negatives = [
    ("type is an array", canned([
        opened(), sem_tension("t-neg1", type=["semantic"])]),
     2, "schema_invalid"),
    ("status transition from is an object", canned([
        opened(), sem_tension("t-neg2"),
        ("TENSION_STATUS", SYSTEM_ACTOR, ["t-neg2"],
         {"tension_id": "t-neg2", "from": {"x": 1}, "to": "examined",
          "evidence": {}, "summary": "Canned."})]),
     3, "schema_invalid"),
    ("status transition to is an array", canned([
        opened(), sem_tension("t-neg3"),
        ("TENSION_STATUS", SYSTEM_ACTOR, ["t-neg3"],
         {"tension_id": "t-neg3", "from": "open", "to": ["resolved"],
          "evidence": {}, "summary": "Canned."})]),
     3, "schema_invalid"),
]
for name, history, seq, klass in negatives:
    engine_outcome = None
    try:
        verified_fold(history, CONSTITUTION_HASH)
        engine_outcome = ("no-halt", None, None)
    except ReplayHalt as halt:
        engine_outcome = ("halt", halt.seq, halt.reason_class)
    except Exception as exc:  # a native exception escaping is the failure
        engine_outcome = (f"native:{type(exc).__name__}", None, None)
    checker_outcome = None
    try:
        checker_mod._fold(history, CONSTITUTION_HASH)
        checker_outcome = ("no-halt", None, None)
    except checker_mod._Halt as halt:
        checker_outcome = ("halt", halt.seq, halt.reason_class)
    except Exception as exc:
        checker_outcome = (f"native:{type(exc).__name__}", None, None)
    check(f"hardening: {name} halts controlled ({klass}) in both folds",
          engine_outcome == ("halt", seq, klass)
          and checker_outcome == engine_outcome,
          f"engine={engine_outcome} checker={checker_outcome}")

# =====================================================================
# Starvation module — direct checks beyond the pack cases.
# =====================================================================
empty = build_report([])
check("starvation: an empty history reports no agents and "
      "mutates nothing",
      empty == {"agents": {}, "events_considered": 0})
hist = [{"event_seq": 1, "event_id": new_id(), "type": "IDLE",
         "actor": A, "affected": [], "payload": {"summary": "x"},
         "prev_hash": "", "hash": ""}]
snapshot = copy.deepcopy(hist)
one = report_bytes(hist)
check("starvation: report is a pure derivation (input unmutated, "
      "bytes stable)",
      hist == snapshot and one == report_bytes(hist)
      and build_report(hist)["agents"][A]["wakes"] == 1)

# =====================================================================
# Socket phase — TV-1 in VP-45's nine-step form through the real
# boundary; VP-55 and VP-38 in service form; VP-36 in service form.
# =====================================================================
from fabric.probe2 import attest_probe, run_twin_probe
from fabric.runtime_setup import (RUNTIME_BASE, admin_request,
                                  agent_call, build_runtime,
                                  start_service, stop_service)

BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)


def history_of(exp):
    return admin_request(exp, {"op": "history"})["result"]["events"]


def last_discovery(exp, actor):
    return [e["event_seq"] for e in history_of(exp)
            if e["type"] == "DISCOVERY" and e["actor"] == actor][-1]


# -- VP-55 in service form ---------------------------------------------
bind = build_runtime(BASE, "s4bind")
proc = start_service(bind)
try:
    resp = admin_request(bind, {"op": "open_run", "run_id": "s4-bind",
                                "bind_stage4": True,
                                "pack_sha256": "0" * 64})
    check("VP-55 (service): a wrong pack digest blocks the opening",
          resp.get("ok") is False and history_of(bind) == [])
    resp = admin_request(bind, {"op": "open_run", "run_id": "s4-bind",
                                "bind_stage4": True})
    opened_ev = history_of(bind)[0]
    pack = opened_ev["payload"].get("validation_pack", {})
    check("VP-55 (service): the bound opening names the pinned pack",
          resp.get("ok") is True
          and pack.get("id") == PACK_ID
          and pack.get("version") == PACK_VERSION
          and pack.get("sha256") == PACK_SHA256)
finally:
    stop_service(proc, bind)

# -- TV-1 through the socket boundary -----------------------------------
exp = build_runtime(BASE, "s4tv1")
proc = start_service(exp)
try:
    admin_request(exp, {"op": "open_run", "run_id": "stage4-tv1",
                        "bind_stage4": True})
    result = run_twin_probe(BASE, "s4twin1")
    att = attest_probe(exp, result)
    check("TV-1 socket: the twin attestation stands at seq 2",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
    tok_a = admin_request(exp, {"op": "issue_token",
                                "agent_id": A})["result"]["token"]
    agent_call(exp, "open_region", tok_a, {"region_id": INTERACTIONS})
    agent_call(exp, "open_region", tok_a, {"region_id": PRESENTATION})
    ref_a = last_discovery(exp, A)
    folded = verified_fold(history_of(exp), CONSTITUTION_HASH)
    check("TV-1 socket (1): replay before injection succeeds",
          folded["regions"][STATE]["version"] == 1)
    resp = admin_request(exp, {"op": "inject_live_state_fault",
                               "region_id": STATE})
    check("TV-1 socket (2): the fault is injected into the live "
          "derived state only; the history is untouched",
          resp.get("ok") is True
          and verified_fold(history_of(exp),
                            CONSTITUTION_HASH)["regions"][STATE]
          ["version"] == 1)
    resp = agent_call(exp, "submit", tok_a, {"response": contrib(
        A, new_id(), {INTERACTIONS: 1, PRESENTATION: 1},
        [INTERACTIONS, PRESENTATION], [INTERACTIONS],
        [{"kind": "append_content", "region_id": INTERACTIONS,
          "text": " (Ordinary work.)"}], ref_a)})
    hist = history_of(exp)
    attempts = [e for e in hist if e["type"] == "SEAL_ATTEMPTED"]
    raised = structural_tensions_from(hist)
    check("TV-1 socket (3): the ordinary contribution is accepted; "
          "its attempt fails S1 for D-CS and missing State; one "
          "checker-origin structural tension is raised",
          resp.get("ok") is True
          and resp["result"]["outcome"] == "accepted"
          and len(attempts) == 1
          and attempts[0]["payload"]["outcome"] == "fail"
          and attempts[0]["payload"]["failed_checks"] == [
              {"check": "S1", "affected": [D_CS, STATE]}]
          and "seal" not in attempts[0]["payload"]
          and len(raised) == 1
          and raised[0]["payload"]["origin"] == "checker")
    tid_sock = raised[0]["payload"]["tension_id"]
    # Repair (I-5): restart the service; its derived state is
    # rebuilt from the verified history.
    stop_service(proc, exp)
    proc = start_service(exp)
    tok_b = admin_request(exp, {"op": "issue_token",
                                "agent_id": B})["result"]["token"]
    agent_call(exp, "open_region", tok_b, {"region_id": COMPONENTS})
    agent_call(exp, "open_region", tok_b, {"region_id": STATE})
    ref_b = last_discovery(exp, B)
    folded = verified_fold(history_of(exp), CONSTITUTION_HASH)
    resp = agent_call(exp, "submit", tok_b, {"response": contrib(
        B, new_id(), state_versions(folded, COMPONENTS, STATE),
        [COMPONENTS, STATE], [COMPONENTS, STATE],
        [{"kind": "remove_dependency", "dependency_id": D_CS}], ref_b)})
    hist = history_of(exp)
    attempts = [e for e in hist if e["type"] == "SEAL_ATTEMPTED"]
    status = [e for e in hist if e["type"] == "TENSION_STATUS"
              and e["payload"]["tension_id"] == tid_sock]
    check("TV-1 socket (4-9): the correction is accepted despite "
          "the open tension; its attempt passes and seals; the "
          "tension resolves with that attempt as evidence",
          resp.get("ok") is True
          and resp["result"]["outcome"] == "accepted"
          and len(attempts) == 2
          and attempts[-1]["payload"]["outcome"] == "pass"
          and attempts[-1]["payload"]["seal"]["position"]
          == attempts[-1]["event_seq"]
          and len(status) == 1
          and status[0]["payload"]["to"] == "resolved"
          and status[0]["payload"]["evidence"]["seal_attempt_seq"]
          == attempts[-1]["event_seq"])
    # VP-38 in service form: the final commit already had its
    # attempt; close appends RUN_CLOSED and no second attempt.
    n_attempts = len(attempts)
    resp = admin_request(exp, {"op": "close_run"})
    hist = history_of(exp)
    check("VP-38 (service): close appends RUN_CLOSED with no "
          "duplicate attempt",
          resp.get("ok") is True
          and resp["result"]["close_attempt_events"] == 0
          and len([e for e in hist
                   if e["type"] == "SEAL_ATTEMPTED"]) == n_attempts
          and hist[-1]["type"] == "RUN_CLOSED"
          and hist[-1]["payload"]["chain_head"] == hist[-2]["hash"])
finally:
    stop_service(proc, exp)

# -- VP-36 in service form ----------------------------------------------
fail_rt = build_runtime(BASE, "s4fail")
proc = start_service(fail_rt, fault_inject="checker_failure")
try:
    admin_request(fail_rt, {"op": "open_run", "run_id": "stage4-vp36",
                            "bind_stage4": True})
    result = run_twin_probe(BASE, "s4twin2")
    att = attest_probe(fail_rt, result)
    tok = admin_request(fail_rt, {"op": "issue_token",
                                  "agent_id": A})["result"]["token"]
    agent_call(fail_rt, "open_region", tok, {"region_id": INTERACTIONS})
    agent_call(fail_rt, "open_region", tok, {"region_id": PRESENTATION})
    ref = last_discovery(fail_rt, A)
    resp = agent_call(fail_rt, "submit", tok, {"response": contrib(
        A, new_id(), {INTERACTIONS: 1, PRESENTATION: 1},
        [INTERACTIONS, PRESENTATION], [INTERACTIONS],
        [{"kind": "append_content", "region_id": INTERACTIONS,
          "text": " (Doomed.)"}], ref)})
    hist = history_of(fail_rt)
    failed_events = [e for e in hist if e["type"] == "RUN_FAILED"]
    check("VP-36 (service): a checker failure fails the run under "
          "the RUN_FAILED contract; no partial group stands",
          resp.get("ok") is False
          and resp.get("kind") == "run_failed"
          and len(failed_events) == 1
          and failed_events[0]["payload"]["breach"]
          == "checker_failure"
          and [e for e in hist
               if e["type"] == "CONTRIBUTION_ACCEPTED"] == [])
finally:
    stop_service(proc, fail_rt)

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("stage4_tests: all checks passed")
