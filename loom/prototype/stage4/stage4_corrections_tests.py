#!/usr/bin/env python3
"""Stage 4 CORRECTION round test suite — the new tests for the
four corrections Vane's Stage 4 examination required (B1–B4;
rulings in VANE-STAGE4-S2-BINDING-RULINGS-2026-11-21.md). This
file is new in the correction round; no prior suite was edited.

  C-B1  S2 evaluated against the live snapshot L under the
        settled lower-bound definition (L_r < R_r ⇒ FAIL(S2,
        {r})), implemented independently in both evaluators —
        exercised here against BOTH fabric.seal.evaluate_attempt
        and the checker process on identical (H, B, L) inputs:
        regression, equality, unexplained higher-version
        divergence, combined divergence + S1 failure (FAIL
        governs), and the S2 structural lifecycle (attach /
        resolve by re-running the check).
  C-B2  Whole-state S1/S3 admission restored on the
        authoritative history-derived fold: a violation standing
        in the authoritative state blocks non-fixing
        contributions and admits the fixing one (S3 fully; the
        S1 fixing half is not constructible through the protocol
        — see STAGE4-CORRECTION-NOTES.md); introducing
        contributions are rejected; TV-1's fault, standing in L
        only, blocks nothing at admission while the checker
        still sees it; repair by replay rebuild leaves the
        history untouched and the resolution is earned by the
        correcting contribution's passing attempt.
  C-B3  Service binding mandatory: the negative tests — a
        normal open_run cannot suppress or bypass binding by
        omitting the former flag, falsifying it, or naming a
        wrong digest — plus the isolated legacy path's boundary,
        and the genesis hash under both openings.
  C-B4  is carried by the reworked pack harness
        (pack_validation.py) itself; this suite does not
        duplicate it.

Run: python3 stage4_corrections_tests.py — prints PASS/FAIL per
check and a summary; exit status is non-zero on any failure.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.canonical import event_hash
from fabric.engine import (Engine, apply_event, empty_state,
                           state_hash, verified_fold)
from fabric.fixture import (CONSTITUTION_HASH, SYSTEM_ACTOR,
                            genesis_payload)
from fabric.harness import Harness
from fabric.packpin import (PACK_SHA256, binding_is_stage4,
                            stage4_binding)
from fabric.seal import evaluate_attempt
from fabric.store import EventStore

ROOT = os.path.dirname(os.path.abspath(__file__))
CHECKER_CMD = [sys.executable, "-m", "fabric.checker"]
GENESIS_HASH = "9a7250bde82bfd8bd220b6013f38b4ce289a702fe86119f2723616055c070b1f"

C = "11111111-1111-4111-8111-111111111111"   # Components
I = "22222222-2222-4222-8222-222222222222"   # Interactions
S = "33333333-3333-4333-8333-333333333333"   # State
N = "44444444-4444-4444-8444-444444444444"   # Continuity
P = "55555555-5555-4555-8555-555555555555"   # Presentation
O = "66666666-6666-4666-8666-666666666666"   # Operations
D_CS = "00000000-0000-4000-8000-000000000102"  # Components uses State
D_SC = "00000000-0000-4000-8000-000000000202"  # State uses Components
D_CQ = "00000000-0000-4000-8000-000000000205"  # Components uses Q
Q = "99999999-9999-4999-8999-999999999999"     # not a region

A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def new_id():
    return str(uuid.uuid4())


# -- shared helpers (stage4_tests.py idiom) ------------------------------

def bound_run(name):
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    engine = Engine.open_run(store, name, binding=stage4_binding())
    return store, engine, Harness(engine)


def custom_genesis_run(name, extra_deps=()):
    """A run whose RUN_OPENED asserts extra dependencies at
    genesis (the authoritative state then carries whatever those
    assertions imply — a dangling dependency, a cycle)."""
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    payload = genesis_payload()
    payload["dependencies"] = payload["dependencies"] \
        + [dict(d) for d in extra_deps]
    payload.update(stage4_binding())
    store.insert_run(name, CONSTITUTION_HASH)
    ev = store.append("RUN_OPENED", SYSTEM_ACTOR, [], payload,
                      prev_hash=CONSTITUTION_HASH)
    store.set_genesis_state_hash(
        name, state_hash(apply_event(empty_state(), ev)))
    store.commit()
    engine = Engine(store)
    return store, engine, Harness(engine)


def contrib(author, idem, base, read, write, ops, ref,
            rationale="Recorded rationale."):
    return {"action": "contribute", "contribution": {
        "author": author, "idempotency_id": idem, "base_versions": base,
        "read_set": read, "write_set": write, "operations": ops,
        "rationale": rationale, "discovery_source": "fabric_read",
        "discovery_ref": ref}}


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


def last_rejection(store):
    return events_of(store, "CONTRIBUTION_REJECTED")[-1]["payload"]


# -- C-B1: canned (H, B, L) against both evaluators ----------------------

def chain(specs):
    events = []
    prev = CONSTITUTION_HASH
    for i, (t, actor, affected, payload) in enumerate(specs, 1):
        ev = {"event_seq": i, "event_id": str(uuid.uuid4()),
              "type": t, "actor": actor, "affected": list(affected),
              "payload": payload, "prev_hash": prev}
        ev["hash"] = event_hash(prev, ev)
        events.append(ev)
        prev = ev["hash"]
    return events


def opened_spec():
    payload = genesis_payload()
    payload.update(stage4_binding())
    return ("RUN_OPENED", SYSTEM_ACTOR, [], payload)


def s2_tension_spec(tid):
    return ("TENSION_RAISED", SYSTEM_ACTOR, [C], {
        "tension_id": tid, "type": "structural", "regions": [C],
        "origin": "checker", "origin_ref": "seal-attempt:2",
        "description": "Canned S2 tension for the correction "
                       "round's lifecycle test.",
        "status": "open", "check": "S2", "affected": [C],
        "summary": "A canned structural tension (S2)."})


def checker_eval(history, staged, snapshot):
    env = dict(os.environ)
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        CHECKER_CMD,
        input=json.dumps({"mode": "evaluate",
                          "constitution_hash": CONSTITUTION_HASH,
                          "history": history,
                          "staged_batch": staged,
                          "snapshot": snapshot}),
        capture_output=True, text=True, timeout=60, env=env, cwd=ROOT)
    if proc.returncode != 0:
        raise RuntimeError(f"checker failed: {proc.stderr[-300:]}")
    return json.loads(proc.stdout)


def both(history, staged, snapshot):
    """The same (H, B, L) through both evaluators, projected to
    the fields the correction asserts on."""
    def project(v):
        return {
            "outcome": v["outcome"],
            "failed": sorted((f["check"], tuple(f["affected"]))
                             for f in v["failed_checks"]),
            "raises": sorted((r["check"], tuple(r["affected"]))
                             for r in v["raises"]),
            "attachments": sorted(v["attachments"]),
            "resolutions": sorted(r["tension_id"]
                                  for r in v["resolutions"]),
            "divergence": sorted((d["registry"], d["id"])
                                  for d in v["divergence"]),
            "seal": v["seal"] is not None}
    eng = project(evaluate_attempt(history, staged, snapshot))
    chk = project(checker_eval(history, staged, snapshot))
    return eng, chk


H1 = chain([opened_spec()])
R1 = verified_fold(H1, CONSTITUTION_HASH)

# Regression: L's Components version (0) is below replay's (1).
live = copy.deepcopy(R1)
live["regions"][C]["version"] = 0
eng, chk = both(H1, [], live)
check("C-B1 regression: L_r < R_r fails S2 on L in BOTH evaluators "
      "(FAIL(S2, {Components}), tension raised, no seal)",
      eng == chk and eng["outcome"] == "fail"
      and eng["failed"] == [("S2", (C,))]
      and eng["raises"] == [("S2", (C,))] and eng["seal"] is False,
      f"engine={eng} checker={chk}" if eng != chk or
      eng["outcome"] != "fail" else "")

# Equality: L is exactly R — no S2 finding; the attempt passes.
eng, chk = both(H1, [], copy.deepcopy(R1))
check("C-B1 equality: L == R produces no S2 finding in either "
      "evaluator (attempt passes)",
      eng == chk and eng["outcome"] == "pass"
      and eng["failed"] == [] and eng["seal"] is True)

# Higher version: L_r > R_r is divergence, never an S2 failure.
live = copy.deepcopy(R1)
live["regions"][C]["version"] = 7
eng, chk = both(H1, [], live)
check("C-B1 higher version: unexplained L_r > R_r is MISMATCH in "
      "both evaluators, with no failed check",
      eng == chk and eng["outcome"] == "mismatch"
      and eng["failed"] == []
      and ("regions", C) in eng["divergence"])

# Combined: divergence (State absent) plus an S1 failure on L plus
# an S2 regression — FAIL governs over MISMATCH, both findings
# recorded.
live = copy.deepcopy(R1)
del live["regions"][S]
live["regions"][C]["version"] = 0
eng, chk = both(H1, [], live)
check("C-B1 precedence: divergence + S1 failure + S2 regression "
      "on L yields FAIL (not MISMATCH) in both evaluators, with "
      "both findings",
      eng == chk and eng["outcome"] == "fail"
      and eng["failed"] == [("S1", (D_CS, S)), ("S2", (C,))],
      f"engine={eng} checker={chk}" if eng != chk else "")

# The S2 structural lifecycle: an open S2 tension attaches while
# the regression stands and resolves when a later attempt's L no
# longer regresses — the resolution re-runs the S2 check itself.
tid_s2 = new_id()
H2 = chain([opened_spec(), s2_tension_spec(tid_s2)])
R2 = verified_fold(H2, CONSTITUTION_HASH)
live = copy.deepcopy(R2)
live["regions"][C]["version"] = 0
eng, chk = both(H2, [], live)
check("C-B1 lifecycle: while the regression stands, the S2 "
      "finding ATTACHES to the open S2 tension in both evaluators "
      "(no duplicate raise, no resolution)",
      eng == chk and eng["outcome"] == "fail"
      and eng["attachments"] == [tid_s2] and eng["raises"] == []
      and eng["resolutions"] == [])
eng, chk = both(H2, [], copy.deepcopy(R2))
check("C-B1 lifecycle: when L no longer regresses, the passing "
      "attempt RESOLVES the S2 tension in both evaluators (the "
      "re-run compares L_r against the replay-established R_r)",
      eng == chk and eng["outcome"] == "pass"
      and eng["resolutions"] == [tid_s2])

# -- C-B2 (i): violations standing in the authoritative state -------------

# S1 carried at genesis: a dependency on Q, which is not a region.
store, eng, h = custom_genesis_run("cb2-s1", extra_deps=[{
    "dependency_id": D_CQ, "source": C, "target": Q,
    "kind": "uses", "status": "active"}])
tok = h.issue_token(A)
ref = open_regions(h, store, tok, I)
out = h.submit(tok, contrib(
    A, new_id(), {I: 1}, [I], [I],
    [{"kind": "append_content", "region_id": I,
      "text": " (Unrelated work.)"}], ref))
rej = last_rejection(store)
check("C-B2 (i) S1: with a dangling dependency standing in the "
      "authoritative state, a non-fixing contribution is REJECTED "
      "at admission as structural S1 (whole-state check)",
      out["outcome"] == "structural" and rej["invariant"] == "S1"
      and rej["records"]["dependency_id"] == D_CQ
      and events_of(store, "CONTRIBUTION_ACCEPTED") == [])

# S3 carried at genesis: State uses Components closes a cycle
# with the standing Components uses State.
store, eng, h = custom_genesis_run("cb2-s3", extra_deps=[{
    "dependency_id": D_SC, "source": S, "target": C,
    "kind": "uses", "status": "active"}])
tok = h.issue_token(A)
ref = open_regions(h, store, tok, I)
out = h.submit(tok, contrib(
    A, new_id(), {I: 1}, [I], [I],
    [{"kind": "append_content", "region_id": I,
      "text": " (Unrelated work.)"}], ref))
rej_event = events_of(store, "CONTRIBUTION_REJECTED")[-1]
rej = rej_event["payload"]
check("C-B2 (i) S3: with a cycle standing in the authoritative "
      "state, a non-fixing contribution is REJECTED at admission "
      "as structural S3 (whole-state check)",
      out["outcome"] == "structural" and rej["invariant"] == "S3"
      and {C, S} <= set(rej_event["affected"])
      and rej["records"]["cycle"] == [C, S, C],
      f"rejection={rej}")
tok_b = h.issue_token(B)
ref_b = open_regions(h, store, tok_b, C, S)
out = h.submit(tok_b, contrib(
    B, new_id(), {C: 1, S: 1}, [C, S], [C, S],
    [{"kind": "remove_dependency", "dependency_id": D_SC}], ref_b))
check("C-B2 (i) S3: the FIXING contribution (removing the "
      "cycle's asserted dependency) is ADMITTED",
      out["outcome"] == "accepted"
      and h._authoritative_state()["dependencies"][D_SC]["status"]
      == "removed")
out = h.submit(tok, contrib(
    A, new_id(), {I: 1}, [I], [I],
    [{"kind": "append_content", "region_id": I,
      "text": " (Work after the fix.)"}], ref))
check("C-B2 (i) S3: once the authoritative state is repaired, "
      "ordinary contributions are admitted again (the violation "
      "was carried by the state, not attributed per-submission)",
      out["outcome"] == "accepted")

# -- C-B2 (ii): introducing contributions are rejected --------------------

store, eng, h = bound_run("cb2-intro")
tok = h.issue_token(A)
ref = open_regions(h, store, tok, C, S)
out = h.submit(tok, contrib(
    A, new_id(), {C: 1, S: 1}, [C, S], [C, S],
    [{"kind": "add_dependency",
      "dependency": {"source": S, "target": C, "kind": "uses"}}], ref))
rej = last_rejection(store)
check("C-B2 (ii) S3: a contribution introducing a cycle (the "
      "Annex D plant) is rejected as structural S3",
      out["outcome"] == "structural" and rej["invariant"] == "S3")
out = h.submit(tok, contrib(
    A, new_id(), {C: 1, S: 1}, [C, S], [C, S],
    [{"kind": "remove_dependency", "dependency_id": D_CS}], ref))
check("C-B2 (ii) setup: removing the standing dependency is "
      "admitted (versions advance to 2)",
      out["outcome"] == "accepted")
out = h.submit(tok, contrib(
    A, new_id(), {C: 2, S: 2}, [C, S], [C, S],
    [{"kind": "remove_dependency", "dependency_id": D_CS}], ref))
rej = last_rejection(store)
check("C-B2 (ii) S1: removing an already-removed dependency is "
      "rejected as structural S1 (the premise form)",
      out["outcome"] == "structural" and rej["invariant"] == "S1")
tok_b = h.issue_token(B)
ref_b = open_regions(h, store, tok_b, C)
out = h.submit(tok_b, contrib(
    B, new_id(), {C: 2}, [C], [C],
    [{"kind": "add_dependency",
      "dependency": {"source": C, "target": Q, "kind": "uses"}}],
    ref_b))
check("C-B2 (ii) S1: a contribution adding a dependency on a "
      "non-region is rejected (caught at the schema step's frozen "
      "set, before the structural step is reached)",
      out["outcome"] == "schema")

# -- C-B2 (iii)+(iv): TV-1's fault stands in L only ------------------------

store, eng, h = bound_run("cb2-tv1")
tok_b = h.issue_token(B)
ref_b = open_regions(h, store, tok_b, C, S)
tok = h.issue_token(A)
ref = open_regions(h, store, tok, I, P)
del eng.state["regions"][S]  # the fault: the live view only
out = h.submit(tok, contrib(
    A, new_id(), versions(eng, I, P), [I, P], [I],
    [{"kind": "append_content", "region_id": I,
      "text": " (Independent work.)"}], ref))
attempts = events_of(store, "SEAL_ATTEMPTED")
raised = structural_tensions(store)
check("C-B2 (iii): with the fault standing in L only, the "
      "independent triggering contribution is ADMITTED (admission "
      "reads the clean authoritative fold)",
      out["outcome"] == "accepted")
check("C-B2 (iv): the checker still sees the fault in L — the "
      "attempt fails S1 on {D-CS, State} and exactly one "
      "structural tension is raised",
      len(attempts) == 1
      and attempts[0]["payload"]["outcome"] == "fail"
      and attempts[0]["payload"]["failed_checks"] == [
          {"check": "S1", "affected": [D_CS, S]}]
      and len(raised) == 1)
out = h.submit(tok_b, contrib(
    B, new_id(), {C: 1, S: 1}, [C, S], [C],
    [{"kind": "append_content", "region_id": C,
      "text": " (Work that read the faulted region.)"}], ref_b))
attempts = events_of(store, "SEAL_ATTEMPTED")
check("C-B2 (iii): a contribution whose READ SET includes the "
      "faulted region is also admitted while the fault stands "
      "(schema frozen set and staleness read the authoritative "
      "fold); its attempt attaches to the standing tension "
      "instead of raising a second one",
      out["outcome"] == "accepted" and len(attempts) == 2
      and len(structural_tensions(store)) == 1
      and attempts[-1]["payload"].get("findings_attached") == [
          raised[0]["payload"]["tension_id"]],
      f"outcome={out.get('outcome')} attempts={len(attempts)}")

# -- C-B2 (v): repair is a replay rebuild; resolution is earned -----------

store, eng, h = bound_run("cb2-repair")
tok = h.issue_token(A)
ref = open_regions(h, store, tok, I, P)
del eng.state["regions"][S]
out = h.submit(tok, contrib(
    A, new_id(), versions(eng, I, P), [I, P], [I],
    [{"kind": "append_content", "region_id": I,
      "text": " (Triggering work.)"}], ref))
tid = structural_tensions(store)[0]["payload"]["tension_id"]
hashes_before = [e["hash"] for e in store.all_events()]
eng.state = verified_fold(store.all_events(), CONSTITUTION_HASH)
check("C-B2 (v): the repair (explicit replay rebuild, I-5) "
      "leaves the history byte-identical and re-derives the live "
      "state from verified replay — the tension stands open in "
      "the rebuilt state; the rebuild itself corrects nothing",
      [e["hash"] for e in store.all_events()] == hashes_before
      and S in eng.state["regions"]
      and eng.state["tensions"][tid]["status"] == "open")
tok_b = h.issue_token(B)
ref_b = open_regions(h, store, tok_b, C, S)
out = h.submit(tok_b, contrib(
    B, new_id(), {C: 1, S: 1}, [C, S], [C, S],
    [{"kind": "remove_dependency", "dependency_id": D_CS}], ref_b))
attempts = events_of(store, "SEAL_ATTEMPTED")
status = [e for e in events_of(store, "TENSION_STATUS")
          if e["payload"]["tension_id"] == tid]
check("C-B2 (v): the correcting contribution is admitted and "
      "its passing attempt resolves the tension, with the "
      "attempt's own sequence as the resolution evidence (the "
      "same check, S1, re-run on the original affected set)",
      out["outcome"] == "accepted"
      and attempts[-1]["payload"]["outcome"] == "pass"
      and len(status) == 1
      and status[0]["payload"]["to"] == "resolved"
      and status[0]["payload"]["evidence"]["seal_attempt_seq"]
      == attempts[-1]["event_seq"]
      and status[0]["payload"]["evidence"]["check"] == "S1")

# -- C-B3: mandatory binding on the service path ---------------------------

from fabric.runtime_setup import (RUNTIME_BASE, admin_request,
                                  build_runtime, start_service,
                                  stop_service)

BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)


def service_history(exp):
    return admin_request(exp, {"op": "history"})["result"]["events"]


def open_and_payload(exp, request):
    resp = admin_request(exp, request)
    hist = service_history(exp)
    return resp, (hist[0]["payload"] if hist else None)


exp = build_runtime(BASE, "cb3omit")
proc = start_service(exp)
try:
    resp, payload = open_and_payload(
        exp, {"op": "open_run", "run_id": "cb3-omit"})
    check("C-B3 negative: open_run with the former flag OMITTED "
          "still binds the pinned pack (binding is not opt-in)",
          resp.get("ok") is True and payload is not None
          and binding_is_stage4(payload)
          and payload["validation_pack"]["sha256"] == PACK_SHA256)
finally:
    stop_service(proc, exp)

exp = build_runtime(BASE, "cb3false")
proc = start_service(exp)
try:
    resp, payload = open_and_payload(
        exp, {"op": "open_run", "run_id": "cb3-false",
              "bind_stage4": False})
    check("C-B3 negative: open_run with the former flag set FALSE "
          "still binds the pinned pack (the flag is ignored)",
          resp.get("ok") is True and payload is not None
          and binding_is_stage4(payload)
          and payload["validation_pack"]["sha256"] == PACK_SHA256)
finally:
    stop_service(proc, exp)

exp = build_runtime(BASE, "cb3digest")
proc = start_service(exp)
try:
    resp, payload = open_and_payload(
        exp, {"op": "open_run", "run_id": "cb3-digest",
              "bind_stage4": False, "pack_sha256": "0" * 64})
    check("C-B3 negative: a wrong pack digest blocks the opening "
          "even when binding is (purportedly) opted out — no run "
          "opens",
          resp.get("ok") is False and payload is None)
finally:
    stop_service(proc, exp)

exp = build_runtime(BASE, "cb3legacy")
proc = start_service(exp)
try:
    resp, payload = open_and_payload(
        exp, {"op": "open_run_legacy_unbound",
              "run_id": "cb3-legacy"})
    check("C-B3 legacy boundary: the isolated legacy path opens "
          "an UNBOUND run (no validation pack in RUN_OPENED) and "
          "names itself in its result — it is a separate op, not "
          "an option of open_run",
          resp.get("ok") is True
          and resp["result"].get("legacy_unbound") is True
          and payload is not None
          and "validation_pack" not in payload
          and not binding_is_stage4(payload))
finally:
    stop_service(proc, exp)

# Genesis state hash: identical under bound and unbound openings,
# and equal to the pinned constant.
store_b, eng_b, _ = bound_run("cb3-genesis-bound")
store_u = EventStore(os.path.join(tempfile.mkdtemp(), "cbu.db"))
eng_u = Engine.open_run(store_u, "cb3-genesis-unbound")
check("C-B3/genesis: the genesis state hash is the pinned "
      "constant under both the bound and the legacy unbound "
      "opening (binding does not alter genesis state)",
      state_hash(eng_b.state) == GENESIS_HASH
      and state_hash(eng_u.state) == GENESIS_HASH)

print()
print("STAGE 4 CORRECTIONS TESTS:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
