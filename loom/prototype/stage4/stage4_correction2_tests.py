#!/usr/bin/env python3
"""Stage 4 CORRECTION ROUND 2 test suite — the new tests for the
two corrections Vane's correction-round examination left open
(B2, B3), plus her post-dispatch requirement that the boundary
evidence be SAME-RUN. This file is new in correction round 2;
no prior suite was edited.

  C2-B2  The authoritative/snapshot boundary, made real
         throughout the service: with a region dropped from the
         operational live view (the TV-1 fault), agent-facing
         reads (view_pattern, open_region, read_breadth), the
         Stage 3 ladder's referential/state reads (examine,
         assess, claim_completion), admission, and commit
         planning all consume the authoritative history-derived
         fold; the live view feeds only the seal-attempt
         snapshot L, where the checker still sees the fault.
  SAME-RUN  One continuous lifecycle in a single run's history:
         fault -> authoritative reads + breadth -> contribution
         admitted -> attempt FAILs S1 in BOTH evaluators ->
         I-5 repair -> correcting contribution -> passing
         same-check attempt -> tension resolved. (Vane's
         addition: separate demonstrations are not enough.)
  C2-B2b The orphan-removal negative test: on a genesis
         carrying a dangling dependency, the endpoint cannot be
         opened, and a contribution attempting to remove that
         dependency is rejected — the S1 fixing half is
         formally non-constructible under the current protocol
         (Vane's ruling), recorded as such, never as passed.
  C2-B3  The legacy unbound opening is mechanically isolated:
         a raw admin request naming open_run_legacy_unbound is
         refused by the ordinary running service (the op is not
         dispatched there at all), the ordinary open_run still
         binds, and the legacy construction survives only in
         driver-side test support (fabric.runtime_setup).

Run: python3 stage4_correction2_tests.py — prints PASS/FAIL per
check and a summary; exit status is non-zero on any failure.
"""
import copy
import json
import os
import socket
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
from fabric.harness import Harness, HarnessRefusal
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
D_CQ = "00000000-0000-4000-8000-000000000205"  # Components uses Q
Q = "99999999-9999-4999-8999-999999999999"     # not a region

A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
E = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"
F = "ffffffff-ffff-4fff-8fff-ffffffffffff"
G = "12121212-1212-4212-8212-121212121212"
W = "34343434-3434-4343-8343-343434343434"
K = "56565656-5656-4565-8565-565656565656"
T = "78787878-7878-4787-8787-787878787878"

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def new_id():
    return str(uuid.uuid4())


# -- shared helpers -------------------------------------------------------

def bound_run(name):
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    engine = Engine.open_run(store, name, binding=stage4_binding())
    return store, engine, Harness(engine)


def custom_genesis_run(name, extra_deps=()):
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


def report(author, regions, ref, description="Noted."):
    return {"author": author, "examination_id": new_id(),
            "idempotency_id": new_id(), "regions": regions,
            "description": description,
            "discovery_source": "fabric_read", "discovery_ref": ref}


def open_regions(h, store, token, *rids):
    seq = None
    for rid in rids:
        h.open_region(token, rid)
        seq = store.all_events()[-1]["event_seq"]
    return seq


def auth_versions(h, *rids):
    st = h._authoritative_state()
    return {r: st["regions"][r]["version"] for r in rids}


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def structural_tensions(store):
    return [e for e in events_of(store, "TENSION_RAISED")
            if e["payload"].get("type") == "structural"]


def checker_eval(history, staged, snapshot, actor=None):
    req = {"mode": "evaluate",
           "constitution_hash": CONSTITUTION_HASH,
           "history": history, "staged_batch": staged,
           "snapshot": snapshot}
    if actor is not None:
        req["authenticated_actor"] = actor
    env = dict(os.environ)
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        CHECKER_CMD, input=json.dumps(req),
        capture_output=True, text=True, timeout=60, env=env, cwd=ROOT)
    if proc.returncode != 0:
        raise RuntimeError(f"checker failed: {proc.stderr[-300:]}")
    return json.loads(proc.stdout)


def both_verdicts(captured):
    """One captured attempt's (H, B, L) through both evaluators,
    projected to outcome + failed checks."""
    def project(v):
        return {"outcome": v["outcome"],
                "failed": sorted(
                    (f["check"], tuple(f["affected"]))
                    for f in v["failed_checks"])}
    eng = project(evaluate_attempt(
        captured["history"], captured["staged"],
        captured["snapshot"],
        authenticated_actor=captured["authenticated_actor"]))
    chk = project(checker_eval(
        captured["history"], captured["staged"],
        captured["snapshot"],
        actor=captured["authenticated_actor"]))
    return eng, chk


# =====================================================================
# C2-B2 direct tests — the Stage 3 paths and planning under fault
# =====================================================================
store, eng, h = bound_run("c2b2-direct")
tok_f = h.issue_token(F)
ref_f = open_regions(h, store, tok_f, C, S)
# F writes State BEFORE the fault: the contribution a later
# completion claim will cite.
out = h.submit(tok_f, contrib(
    F, new_id(), {C: 1, S: 1}, [C, S], [S],
    [{"kind": "append_content", "region_id": S,
      "text": " (F's work.)"}], ref_f))
cid_f = out["contribution_id"]
assert out["outcome"] == "accepted", out
tok_e = h.issue_token(E)
open_regions(h, store, tok_e, I, N)

del eng.state["regions"][S]  # the fault: the live view only

check("C2-B2 setup: the fault stands in the live view only — "
      "the authoritative fold still holds State at version 2",
      S not in eng.state["regions"]
      and h._authoritative_state()["regions"][S]["version"] == 2)

pat = h.view_pattern(tok_e)
check("C2-B2 view_pattern: the faulted region still appears on "
      "the agent-facing pattern surface, at its authoritative "
      "version",
      any(r["region_id"] == S and r["version"] == 2
          for r in pat["regions"]))

tok_g = h.issue_token(G)
opened = h.open_region(tok_g, S)
check("C2-B2 open_region + read_breadth: a fresh agent can open "
      "the faulted region — served from the authoritative fold "
      "at version 2, its content carrying the pre-fault work — "
      "and the read stands in the breadth accounting (1/6, the "
      "denominator still six regions)",
      opened["version"] == 2
      and opened["content"].endswith(" (F's work.)")
      and h.read_breadth(G) == 1 / 6)

out = h.examine(tok_f, report(F, [C, S], ref_f,
                              "State's place in the pattern."))
tid_sem = out.get("tension_id")
check("C2-B2 examine: an examination whose region set INCLUDES "
      "the faulted region is recorded and creates its tension "
      "(the ladder's referential read — the frozen region set — "
      "comes from the authoritative fold)",
      out["outcome"] == "created" and tid_sem is not None,
      f"outcome={out}")

out = h.assess(tok_e, {"assessment_id": new_id(), "author": E,
                       "target_kind": "tension",
                       "target_id": tid_sem, "position": "remains",
                       "reasoning": "It remains."})
auth_tension = h._authoritative_state()["tensions"][tid_sem]
check("C2-B2 assess + commit planning: assessing the tension "
      "over the faulted region is recorded and its transition "
      "(open -> examined) is planned against the authoritative "
      "state — the planner reads State's title from the fold, "
      "where the live view has lost it",
      out["outcome"] == "recorded"
      and auth_tension["status"] == "examined",
      f"outcome={out}")

out = h.assess(tok_e, {"assessment_id": new_id(), "author": E,
                       "target_kind": "facet", "target_id": S,
                       "position": "examined",
                       "reasoning": "Reviewed at version 2.",
                       "version_reviewed": 2})
check("C2-B2 assess (facet): a facet assessment of the faulted "
      "region at its authoritative version is recorded (the "
      "ladder's state read — version_never_existed — consults "
      "the fold, not the dropped live record)",
      out["outcome"] == "recorded", f"outcome={out}")

out = h.claim_completion(tok_f, {"claim": {
    "claim_id": new_id(), "facet": S, "facet_version": 2,
    "supporting_contributions": [cid_f],
    "rationale": "State carries F's recorded work."}})
claimed = [e for e in events_of(store, "COMPLETION_CLAIMED")
           if e["payload"]["outcome"] == "recorded"]
check("C2-B2 claim_completion: a claim on the faulted facet is "
      "recorded (referential and state reads on the fold), and "
      "its derived facet transition commits — the facet stands "
      "COMPLETE on the claim plus the independent examined "
      "review recorded above (section 5 precedence), so the "
      "corrupted live cache cannot veto a commit planned "
      "against the authoritative state",
      out["outcome"] == "recorded" and len(claimed) == 1
      and h._authoritative_state()["facet_status"].get(S)
      == "complete",
      f"outcome={out}")

# =====================================================================
# SAME-RUN boundary evidence — one run, every beat connected
# =====================================================================
store, eng, h = bound_run("c2b2-samerun")
tok_w = h.issue_token(W)
ref_w = open_regions(h, store, tok_w, I, P)
tok_k = h.issue_token(K)
ref_k = open_regions(h, store, tok_k, C, S)
tok_t = h.issue_token(T)
open_regions(h, store, tok_t, S)
state_content = h._authoritative_state()["regions"][S]["content"]

captured = []
h.attempt_observer = captured.append

# Beat 2 — the fault.
del eng.state["regions"][S]
check("SAME-RUN (2): the fault is in the live view only; the "
      "history still folds to a state holding State",
      S not in eng.state["regions"]
      and S in verified_fold(store.all_events(),
                             CONSTITUTION_HASH)["regions"])

# Beat 3 — agent-facing reads + breadth from the authoritative state.
pat = h.view_pattern(tok_w)
opened = h.open_region(tok_t, S)
check("SAME-RUN (3): with the fault standing, State still "
      "appears in view_pattern at version 1; the third agent's "
      "breadth stands at 1/6; a fresh open of State serves its "
      "authoritative content and version",
      any(r["region_id"] == S and r["version"] == 1
          for r in pat["regions"])
      and h.read_breadth(T) == 1 / 6
      and opened["version"] == 1
      and opened["content"] == state_content)

# Beat 4 — a contribution passes planning + admission unaffected.
out = h.submit(tok_w, contrib(
    W, new_id(), auth_versions(h, I, P), [I, P], [I],
    [{"kind": "append_content", "region_id": I,
      "text": " (Work under fault.)"}], ref_w))
check("SAME-RUN (4): the working agent's contribution is "
      "ACCEPTED while the fault stands (schema, staleness, "
      "whole-state admission, and commit planning all read the "
      "authoritative fold)",
      out["outcome"] == "accepted", f"outcome={out}")

# Beat 5 — the attempt on this same run FAILs S1 in both evaluators.
attempts = events_of(store, "SEAL_ATTEMPTED")
raised = structural_tensions(store)
eng_v, chk_v = both_verdicts(captured[0])
check("SAME-RUN (5): the recorded attempt FAILs S1 on "
      "{D-CS, State}; replaying the captured (H, B, L) through "
      "BOTH evaluators FAILs S1 with State affected in each; "
      "exactly one structural tension stands from the attempt",
      len(attempts) == 1
      and attempts[0]["payload"]["outcome"] == "fail"
      and attempts[0]["payload"]["failed_checks"] == [
          {"check": "S1", "affected": [D_CS, S]}]
      and eng_v == chk_v and eng_v["outcome"] == "fail"
      and ("S1", (D_CS, S)) in eng_v["failed"]
      and len(raised) == 1,
      f"engine={eng_v} checker={chk_v}")
tid_run = raised[0]["payload"]["tension_id"]

# Beat 6 — the I-5 repair: explicit replay rebuild, history untouched.
hashes_before = [e["hash"] for e in store.all_events()]
eng.state = verified_fold(store.all_events(), CONSTITUTION_HASH)
check("SAME-RUN (6): the repair re-derives the live view from "
      "verified replay; the history is byte-identical across it; "
      "the tension stands open in the rebuilt state — the "
      "rebuild itself corrects nothing",
      [e["hash"] for e in store.all_events()] == hashes_before
      and S in eng.state["regions"]
      and eng.state["tensions"][tid_run]["status"] == "open")

# Beat 7 — the correcting contribution; the passing same-check attempt.
out = h.submit(tok_k, contrib(
    K, new_id(), {C: 1, S: 1}, [C, S], [C, S],
    [{"kind": "remove_dependency", "dependency_id": D_CS}], ref_k))
attempts = events_of(store, "SEAL_ATTEMPTED")
status = [e for e in events_of(store, "TENSION_STATUS")
          if e["payload"]["tension_id"] == tid_run]
check("SAME-RUN (7): the correcting contribution is accepted; "
      "its attempt passes the SAME check (S1, re-run on the "
      "original affected set); the tension resolves with that "
      "attempt's sequence as evidence",
      out["outcome"] == "accepted"
      and attempts[-1]["payload"]["outcome"] == "pass"
      and len(status) == 1
      and status[0]["payload"]["to"] == "resolved"
      and status[0]["payload"]["evidence"]["check"] == "S1"
      and status[0]["payload"]["evidence"]["seal_attempt_seq"]
      == attempts[-1]["event_seq"])

# Beat 8 — continuity over the single history.
evs = store.all_events()
types = [e["type"] for e in evs]
i_acc = [i for i, t in enumerate(types)
         if t == "CONTRIBUTION_ACCEPTED"]
i_att = [i for i, t in enumerate(types) if t == "SEAL_ATTEMPTED"]
i_raise = types.index("TENSION_RAISED")
i_res = types.index("TENSION_STATUS")
folded = verified_fold(evs, CONSTITUTION_HASH)
check("SAME-RUN (8): one run, one history — the beats interleave "
      "in order (accepted contribution -> failed attempt -> "
      "tension raised -> accepted correction -> passing attempt "
      "-> resolution), two attempts in total, and the whole "
      "chain verifies end to end with the tension resolved in "
      "the fold",
      types[0] == "RUN_OPENED" and len(i_acc) == 2
      and len(i_att) == 2
      and i_acc[0] < i_att[0] < i_raise < i_acc[1] < i_att[1] < i_res
      and folded["tensions"][tid_run]["status"] == "resolved")

# =====================================================================
# C2-B2b — the orphan-removal negative test
# =====================================================================
store, eng, h = custom_genesis_run("c2b2b-orphan", extra_deps=[{
    "dependency_id": D_CQ, "source": C, "target": Q,
    "kind": "uses", "status": "active"}])
tok = h.issue_token(A)
ref = open_regions(h, store, tok, C, I)

refused = False
try:
    h.open_region(tok, Q)
except HarnessRefusal:
    refused = True
check("C2-B2b: the dangling endpoint cannot enter any read set "
      "— opening Q is refused at the interface (no discovery "
      "exists for a non-region)",
      refused and Q not in h.read_record.get(A, {}))

out = h.submit(tok, contrib(
    A, new_id(), {C: 1}, [C], [C],
    [{"kind": "remove_dependency", "dependency_id": D_CQ}], ref))
rej = events_of(store, "CONTRIBUTION_REJECTED")[-1]["payload"]
check("C2-B2b: a contribution attempting to REMOVE the dangling "
      "dependency is REJECTED (schema: the removal's endpoints "
      "cannot both enter the read/write sets, cross-field rule "
      "(iii)); nothing is accepted; the dependency still stands "
      "active in the authoritative state — the S1 fixing half "
      "is formally non-constructible, and this test records the "
      "boundary, not a pass of that half",
      out["outcome"] == "schema" and rej["outcome"] == "schema"
      and events_of(store, "CONTRIBUTION_ACCEPTED") == []
      and h._authoritative_state()["dependencies"][D_CQ]["status"]
      == "active",
      f"outcome={out}")

ref2 = open_regions(h, store, tok, I)
out = h.submit(tok, contrib(
    A, new_id(), {C: 1, I: 1}, [C, I], [I],
    [{"kind": "append_content", "region_id": I,
      "text": " (Unrelated work.)"}], ref2))
check("C2-B2b (preserved rejection half): the poisoned genesis "
      "still blocks every non-fixing contribution at whole-state "
      "admission (structural S1)",
      out["outcome"] == "structural"
      and events_of(store, "CONTRIBUTION_REJECTED")[-1]["payload"]
      ["invariant"] == "S1")

# =====================================================================
# C2-B3 — the ordinary service refuses the legacy operation
# =====================================================================
from fabric.runtime_setup import (RUNTIME_BASE, admin_request,
                                  build_runtime, start_service,
                                  stop_service)

BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)


def raw_admin(p, req):
    """A request straight to the admin socket — deliberately NOT
    fabric.runtime_setup.admin_request, whose test-support
    reroute for the legacy op is exactly what must not be able
    to disguise the service's own answer."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(15.0)
        s.connect(p["admin_sock"])
        s.sendall((json.dumps(req) + "\n").encode("utf-8"))
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    return json.loads(buf.decode("utf-8"))


def raw_history(p):
    return raw_admin(p, {"op": "history"})["result"]["events"]


exp = build_runtime(BASE, "c2b3refuse")
proc = start_service(exp)
try:
    resp = raw_admin(exp, {"op": "open_run_legacy_unbound",
                           "run_id": "c2b3-refused"})
    check("C2-B3: the ordinary running Stage 4 service REFUSES "
          "open_run_legacy_unbound as a normal admin request — "
          "the operation is not dispatched there at all — and "
          "no run opens",
          resp.get("ok") is False
          and resp.get("kind") == "unknown_op"
          and raw_history(exp) == [],
          f"resp={resp}")
    resp = raw_admin(exp, {"op": "open_run", "run_id": "c2b3"})
    hist = raw_history(exp)
    check("C2-B3: the same service's ordinary open_run still "
          "opens — and binds the pinned pack",
          resp.get("ok") is True and len(hist) == 1
          and binding_is_stage4(hist[0]["payload"])
          and hist[0]["payload"]["validation_pack"]["sha256"]
          == PACK_SHA256)
finally:
    stop_service(proc, exp)

exp = build_runtime(BASE, "c2b3support")
proc = start_service(exp)
try:
    resp = admin_request(exp, {"op": "open_run_legacy_unbound",
                               "run_id": "c2b3-support"})
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    check("C2-B3: the legacy construction survives ONLY in "
          "driver-side test support — reached through the "
          "already-imported admin_request helper, it opens an "
          "UNBOUND run and names itself, while the service "
          "itself (previous test) refuses the same request",
          resp.get("ok") is True
          and resp["result"].get("legacy_unbound") is True
          and len(hist) == 1
          and "validation_pack" not in hist[0]["payload"]
          and not binding_is_stage4(hist[0]["payload"]))
finally:
    stop_service(proc, exp)

store_b, eng_b, _ = bound_run("c2b3-genesis-bound")
store_u = EventStore(os.path.join(tempfile.mkdtemp(), "c2u.db"))
eng_u = Engine.open_run(store_u, "c2b3-genesis-unbound")
check("C2-B3/genesis: the genesis state hash is the pinned "
      "constant under both the bound opening and the "
      "test-support legacy unbound opening",
      state_hash(eng_b.state) == GENESIS_HASH
      and state_hash(eng_u.state) == GENESIS_HASH)

print()
print("STAGE 4 CORRECTION ROUND 2 TESTS:",
      "ALL PASS" if not failures else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
