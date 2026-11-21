#!/usr/bin/env python3
"""Pack validation — the pinned examiner validation pack V2,
executed against BOTH Stage 4 implementations.

Stage 4 (2026-11-21). The pack (VANE-STAGE4-EXAMINER-VALIDATION-
PACK, version v2, SHA-256 cce27ee7…, pinned at shelf commit
f69f3d7d) is the pre-open validation authority: both
implementations must pass it before any run opens, and any
disagreement between them is reported as a failure, never smoothed
(pack section 10; build notes section 4, whose mapping table —
recorded before execution — this runner implements).

The two implementations under validation:
- the ENGINE side: fabric.engine.verified_fold for replay cases
  and fabric.seal.evaluate_attempt for attempt cases;
- the CHECKER side: the fabric.checker process, driven over
  stdin/stdout in its fold and evaluate modes.

Canned histories are built once as serialized, hash-chained event
dicts (with the format primitives both sides share) and the
identical inputs are fed to both sides; the runner never lets one
implementation generate expected outputs for the other (pack
10.4). Live cases run through the Harness on Stage-4-bound runs.

Correction round (C-B4): live attempt cases no longer record a
proxy for either implementation. The harness's attempt_observer
captures each seal attempt's exact inputs (H, B, L, actor) at the
moment the checker is invoked, and the case replays those inputs
through BOTH fabric.seal.evaluate_attempt and the checker
process, recording both actual verdicts in the manifest. The
live-path assertions (attempt counts, recorded outcomes, the
tension lifecycle in the history) are kept alongside. Cases that
are genuinely single-subject are marked dual_applicable: false
in the manifest, with the justification, and VP-29 is computed
over the dual-applicable set only (see
STAGE4-CORRECTION-NOTES.md section 6, the revised mapping
recorded before this execution).

Output: a per-case manifest at pack-validation-manifest.json
(pack 10.3: pack id/version/hash, implementation identity and
build hash, case id, input fixture hash, observed vs expected,
pass/fail, diagnostic excerpt, halt sequence where applicable) and
a printed summary. Exit status is non-zero when any case fails or
the two implementations disagree anywhere.
"""
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric import starvation
from fabric.canonical import canonical, event_hash, sha256_hex
from fabric.engine import (Engine, ReplayHalt, state_hash,
                           verified_fold)
from fabric.fixture import CONSTITUTION_HASH, SYSTEM_ACTOR, genesis_payload
from fabric.harness import CheckerFailure, Harness
from fabric.packpin import (PACK_ID, PACK_SHA256, PACK_VERSION,
                            stage4_binding)
from fabric.seal import evaluate_attempt
from fabric.store import EventStore

ROOT = os.path.dirname(os.path.abspath(__file__))
CHECKER_CMD = [sys.executable, "-m", "fabric.checker"]

# Annex D region ids and the genesis dependency ids (fixture).
C = "11111111-1111-4111-8111-111111111111"   # Components
I = "22222222-2222-4222-8222-222222222222"   # Interactions
S = "33333333-3333-4333-8333-333333333333"   # State
N = "44444444-4444-4444-8444-444444444444"   # Continuity
P = "55555555-5555-4555-8555-555555555555"   # Presentation
O = "66666666-6666-4666-8666-666666666666"   # Operations
D_CI = "00000000-0000-4000-8000-000000000101"  # C uses I
D_CS = "00000000-0000-4000-8000-000000000102"  # C uses S ("D-CS")
D_NI = "00000000-0000-4000-8000-000000000103"  # N constrains I ("D-NI")
D_OI = "00000000-0000-4000-8000-000000000104"  # O uses I
D_SC = "00000000-0000-4000-8000-000000000202"  # S uses C (the plant)
D_CP = "00000000-0000-4000-8000-000000000201"  # C uses P
D_PS = "00000000-0000-4000-8000-000000000206"  # P uses S
D_CQ = "00000000-0000-4000-8000-000000000205"  # C uses Q (dangling)
Q = "99999999-9999-4999-8999-999999999999"     # not a region

AGENT_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
AGENT_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"

RESULTS = []


def build_hash(*paths):
    h = hashlib.sha256()
    for path in paths:
        with open(os.path.join(ROOT, path), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()


ENGINE_BUILD = build_hash("fabric/engine.py", "fabric/seal.py",
                          "fabric/canonical.py")
CHECKER_BUILD = build_hash("fabric/checker.py", "fabric/canonical.py")


# -- canned histories ---------------------------------------------------

def chain(specs):
    """Serialize (type, actor, affected, payload) specs into a
    hash-chained event list, exactly as the store appends them."""
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


def opened_payload(binding="stage4", extra_deps=(), replace_deps=None):
    payload = genesis_payload()
    if replace_deps is not None:
        payload["dependencies"] = replace_deps
    payload["dependencies"] = payload["dependencies"] + list(extra_deps)
    if binding == "stage4":
        payload.update(stage4_binding())
    elif binding == "rev9-only":
        payload["authority_set"] = {
            "spec": "loom-spec-v0.1-rev9", "amendments": []}
    return payload


def ropened(binding="stage4", **kw):
    return ("RUN_OPENED", SYSTEM_ACTOR, [],
            opened_payload(binding, **kw))


def staged_from(specs, head_seq):
    """Staged-batch event dicts continuing a history at head_seq."""
    out = []
    for j, (t, actor, affected, payload) in enumerate(specs, 1):
        out.append({"event_seq": head_seq + j,
                    "event_id": str(uuid.uuid4()), "type": t,
                    "actor": actor, "affected": list(affected),
                    "payload": payload, "prev_hash": "", "hash": ""})
    return out


def chained_pair(base_specs, staged_specs):
    """(history, staged, full): the base history chained, the
    staged batch as the chained tail of the full history — so the
    snapshot L = fold(full) is computable, and the staged events
    carry the seqs (and hashes) they would hold at commit."""
    history = chain(base_specs)
    full = chain(base_specs + staged_specs)
    return history, full[len(history):], full


def contribution_payload(author, ops, assigned=None, cid=None):
    contribution = {
        "author": author, "idempotency_id": str(uuid.uuid4()),
        "base_versions": {}, "read_set": [], "write_set": [],
        "operations": ops, "rationale": "Canned pack fixture.",
        "discovery_source": "fabric_read", "discovery_ref": 1}
    return {"contribution": contribution,
            "contribution_id": cid or str(uuid.uuid4()),
            "assigned_dependency_ids": assigned or {}}


def accept_spec(author, ops, assigned=None, cid=None):
    return ("CONTRIBUTION_ACCEPTED", author, [],
            contribution_payload(author, ops, assigned, cid))


def tension_raised(tid, ttype, regions, origin, status="open",
                   check=None, affected=None, origin_ref="canned"):
    payload = {"tension_id": tid, "type": ttype, "regions": regions,
               "origin": origin, "origin_ref": origin_ref,
               "description": "Canned pack fixture tension.",
               "status": status,
               "summary": "A canned tension for pack validation."}
    if check is not None:
        payload["check"] = check
        payload["affected"] = affected
    return ("TENSION_RAISED", SYSTEM_ACTOR, regions, payload)


def tension_status(tid, frm, to):
    return ("TENSION_STATUS", SYSTEM_ACTOR, [tid],
            {"tension_id": tid, "from": frm, "to": to,
             "evidence": {"canned": True},
             "summary": "A canned tension transition."})


# -- implementation adapters ---------------------------------------------

def engine_fold(history):
    try:
        state = verified_fold(history, CONSTITUTION_HASH)
        return {"result": "ok", "state_hash": state_hash(state)}
    except ReplayHalt as halt:
        return {"result": "halt", "seq": halt.seq,
                "reason_class": halt.reason_class}


def checker_run(request):
    env = dict(os.environ)
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(CHECKER_CMD, input=json.dumps(request),
                          capture_output=True, text=True, timeout=60,
                          env=env, cwd=ROOT)
    if proc.returncode != 0:
        raise RuntimeError(
            f"checker process failed rc={proc.returncode}: "
            f"{proc.stderr.strip()[-300:]}")
    return json.loads(proc.stdout)


def checker_fold(history, expected_pack_sha256=None):
    request = {"mode": "fold", "constitution_hash": CONSTITUTION_HASH,
               "history": history}
    if expected_pack_sha256 is not None:
        request["expected_pack_sha256"] = expected_pack_sha256
    out = checker_run(request)
    if out.get("ok"):
        result = {"result": "ok", "state_hash": out["state_hash"]}
    else:
        result = {"result": "halt", "seq": out["halt"]["seq"],
                  "reason_class": out["halt"]["reason_class"]}
    if "pack_binding" in out:
        result["pack_binding"] = out["pack_binding"]
    return result


def verdict_contract(verdict):
    """The contract-level projection of an attempt verdict — the
    fields VP-29 requires to agree (outcome, failed checks and
    affected identities, raises, attachments, resolutions, seal
    eligibility and contents)."""
    if verdict is None:
        return None
    out = {"outcome": verdict["outcome"],
           "failed_checks": sorted(
               (f["check"], tuple(f["affected"]))
               for f in verdict["failed_checks"]),
           "raises": sorted(
               (r["check"], tuple(r["affected"]))
               for r in verdict["raises"]),
           "attachments": sorted(verdict["attachments"]),
           "resolutions": sorted(
               r["tension_id"] for r in verdict["resolutions"]),
           "divergence": sorted(
               (d["registry"], d["id"]) for d in verdict["divergence"]),
           "seal": None}
    if verdict.get("seal") is not None:
        seal = verdict["seal"]
        out["seal"] = {
            "contributions": list(
                seal["contributions_since_last_seal"]),
            "questions": sorted(
                (q["tension_id"], q["status"],
                 tuple(q["examined_by"])
                 if isinstance(q["examined_by"], list)
                 else q["examined_by"])
                for q in seal["outstanding_semantic_questions"]),
            "semantic_clearance": seal["semantic_clearance"]}
    if verdict["outcome"] == "halt":
        out["halt"] = {"seq": verdict["halt"]["seq"],
                       "reason_class": verdict["halt"]["reason_class"]}
    if verdict["outcome"] == "refused":
        out["reason"] = verdict.get("reason", "")
    return out


def engine_eval(history, staged, snapshot, actor=None):
    return verdict_contract(evaluate_attempt(
        history, staged, snapshot,
        authenticated_actor=actor))


def checker_eval(history, staged, snapshot, actor=None, omit=False):
    request = {"mode": "evaluate",
               "constitution_hash": CONSTITUTION_HASH,
               "history": history, "snapshot": snapshot}
    if not omit:
        request["staged_batch"] = staged
    if actor is not None:
        request["authenticated_actor"] = actor
    return verdict_contract(checker_run(request))


def fold_of(history):
    return verified_fold(history, CONSTITUTION_HASH)


# -- case recording --------------------------------------------------------

def record(case, expected, engine_obs, checker_obs, passed,
           fixture, diagnostic="", dual_applicable=True,
           dual_note=""):
    RESULTS.append({
        "pack": {"id": PACK_ID, "version": PACK_VERSION,
                 "sha256": PACK_SHA256},
        "case": case,
        "fixture_hash": sha256_hex(canonical(fixture)),
        "builds": {"engine": ENGINE_BUILD, "checker": CHECKER_BUILD},
        "expected": expected,
        "observed": {"engine": engine_obs, "checker": checker_obs},
        "result": "pass" if passed else "FAIL",
        "diagnostic": diagnostic,
        # Correction round (C-B4): every entry declares whether
        # it is a dual-applicable case (both implementations'
        # verdicts over identical inputs, compared by VP-29).
        # Single-subject cases say so, with the justification —
        # they are never represented as dual agreement.
        "dual_applicable": dual_applicable,
        "dual_note": dual_note,
    })
    print(f"{'PASS' if passed else 'FAIL'}  {case}  {diagnostic}")


def fold_case(case, history, expect, diagnostic=""):
    """A replay case run against both folds. expect is either
    ("ok",) or ("halt", seq, reason_class)."""
    eng = engine_fold(history)
    chk = checker_fold(history)
    if expect[0] == "ok":
        ok = eng["result"] == "ok" and chk["result"] == "ok" \
            and eng["state_hash"] == chk["state_hash"]
        expected = {"result": "ok"}
    else:
        ok = eng == {"result": "halt", "seq": expect[1],
                     "reason_class": expect[2]} \
            and chk == eng
        expected = {"result": "halt", "seq": expect[1],
                    "reason_class": expect[2]}
    record(case, expected, eng, chk, ok, {"history": history},
           diagnostic or (f"engine={eng} checker={chk}"
                          if not ok else ""))
    return ok


def eval_case(case, history, staged, snapshot, expect_fn, expected,
              fixture_extra=None, actor=None):
    """An attempt case run against both evaluators. expect_fn maps
    the agreed contract dict to a bool."""
    eng = engine_eval(history, staged, snapshot, actor)
    chk = checker_eval(history, staged, snapshot, actor)
    agree = eng == chk
    ok = agree and expect_fn(eng)
    fixture = {"history": history, "staged": staged,
               "snapshot": snapshot}
    if fixture_extra:
        fixture.update(fixture_extra)
    record(case, expected, eng, chk, ok, fixture,
           "" if ok else f"agree={agree} engine={eng} checker={chk}")
    return eng


# -- replay cases (VP-01, VP-02, VP-04..VP-15) -----------------------------

def run_fold_cases():
    h1 = chain([ropened()])
    fold_case("VP-01-fold", h1, ("ok",))
    # VP-01's attempt half: PASS with a seal over the genesis state.
    eval_case("VP-01", h1, [], fold_of(h1),
              lambda v: v["outcome"] == "pass" and v["seal"] is not None,
              {"outcome": "pass", "seal": "issued"})

    idle = ("IDLE", AGENT_A, [], {"summary": "Agent A idles."})
    h2 = chain([ropened(), idle])
    eng = engine_fold(h2)
    chk = checker_fold(h2)
    base = engine_fold(h1)
    ok = eng["result"] == chk["result"] == "ok" \
        and eng["state_hash"] != base["state_hash"]  # last_seq differs
    # States identical except last_seq: compare hashes with seq masked.
    s1 = fold_of(h1)
    s2 = fold_of(h2)
    s2_masked = dict(s2, last_seq=s1["last_seq"])
    ok = ok and state_hash(s2_masked) == state_hash(s1)
    record("VP-02", {"result": "ok",
                     "note": "state identical except last_seq"},
           eng, chk, ok, {"history": h2})

    disc = ("DISCOVERY", AGENT_A, [C],
            {"path": f"region:{C}", "summary": "A read Components."})
    h_tamper = chain([ropened(), disc])
    h_tamper[1]["prev_hash"] = "0" * 64
    fold_case("VP-04", h_tamper, ("halt", 2, "hash_chain_invalid"))

    h_dup = chain([ropened(), disc])
    dup = copy.deepcopy(h_dup[1])
    h_dup.append(dup)
    fold_case("VP-05", h_dup, ("halt", 3, "sequence_invalid"))

    t_missing = tension_raised("t-vp06", "semantic", [C], "contribution")
    del t_missing[3]["status"]
    fold_case("VP-06", chain([ropened(), t_missing]),
              ("halt", 2, "schema_invalid"))

    t_array = tension_raised("t-vp07", "semantic", [C], "contribution")
    t_array[3]["type"] = ["semantic"]
    fold_case("VP-07", chain([ropened(), t_array]),
              ("halt", 2, "schema_invalid"))

    t_ok = tension_raised("t-vp08", "semantic", [C], "contribution")
    bad_from = tension_status("t-vp08", {"x": 1}, "examined")
    fold_case("VP-08", chain([ropened(), t_ok, bad_from]),
              ("halt", 3, "schema_invalid"))

    bad_to = tension_status("t-vp08", "open", ["resolved"])
    fold_case("VP-09", chain([ropened(), t_ok, bad_to]),
              ("halt", 3, "schema_invalid"))

    t_unknown = tension_raised("t-vp10", "unknown-kind", [C],
                               "contribution")
    fold_case("VP-10", chain([ropened(), t_unknown]),
              ("halt", 2, "schema_invalid"))

    t_sem_checker = tension_raised("t-vp11a", "semantic", [C], "checker")
    fold_case("VP-11a", chain([ropened(), t_sem_checker]),
              ("halt", 2, "protocol_transition_invalid"))
    t_struct_contrib = tension_raised("t-vp11b", "structural", [C],
                                      "contribution", check="S1",
                                      affected=[D_CS, S])
    fold_case("VP-11b", chain([ropened(), t_struct_contrib]),
              ("halt", 2, "protocol_transition_invalid"))

    t12 = tension_raised("t-vp12", "semantic", [C], "contribution")
    fold_case("VP-12a", chain([ropened(), t12,
                               tension_status("t-vp12", "open",
                                              "resolved")]),
              ("halt", 3, "protocol_transition_invalid"))
    fold_case("VP-12b", chain([
        ropened(), t12, tension_status("t-vp12", "open", "examined"),
        tension_status("t-vp12", "examined", "resolved"),
        tension_status("t-vp12", "resolved", "examined")]),
        ("halt", 5, "protocol_transition_invalid"))

    t13 = tension_raised("t-vp13", "structural", [S], "checker",
                         check="S1", affected=[D_CS, S])
    fold_case("VP-13a", chain([ropened(), t13,
                               tension_status("t-vp13", "open",
                                              "examined")]),
              ("halt", 3, "protocol_transition_invalid"))
    fold_case("VP-13b", chain([ropened(), t13,
                               tension_status("t-vp13", "open",
                                              "standing")]),
              ("halt", 3, "protocol_transition_invalid"))
    fold_case("VP-13c", chain([
        ropened(), t13, tension_status("t-vp13", "open", "resolved"),
        tension_status("t-vp13", "resolved", "open")]),
        ("halt", 4, "protocol_transition_invalid"))

    facet_bogus = ("FACET_STATUS", SYSTEM_ACTOR, [C],
                   {"region_id": C, "from": "open", "to": "bogus",
                    "summary": "Canned facet status."})
    fold_case("VP-14a", chain([ropened(), facet_bogus]),
              ("halt", 2, "schema_invalid"))
    facet_outside = ("FACET_STATUS", SYSTEM_ACTOR, [Q],
                     {"region_id": Q, "from": "open", "to": "claimed",
                      "summary": "Canned facet status."})
    fold_case("VP-14b", chain([ropened(), facet_outside]),
              ("halt", 2, "protocol_transition_invalid"))

    fold_case("VP-15a", chain([ropened(), idle]), ("ok",))
    fold_case("VP-15b", chain([ropened("rev9-only"), idle]),
              ("halt", 2, "schema_invalid"))


# -- attempt cases over canned inputs (VP-03, VP-16..VP-21,
#    VP-24..VP-27, VP-39..VP-44, VP-47) ---------------------------------

def run_eval_cases():
    h0 = chain([ropened()])
    r0 = fold_of(h0)

    # VP-03 — a staged IDLE naming another actor is refused at the
    # admission boundary by both evaluators (I-6).
    idle_b = staged_from([("IDLE", AGENT_B, [],
                           {"summary": "B idles."})], 1)
    eng = engine_eval(h0, idle_b, copy.deepcopy(r0), actor=AGENT_A)
    chk = checker_eval(h0, idle_b, copy.deepcopy(r0), actor=AGENT_A)
    record("VP-03", {"outcome": "refused"}, eng, chk,
           eng == chk and eng["outcome"] == "refused",
           {"history": h0, "staged": idle_b})

    # VP-16 — L missing region S: FAIL(S1, {D-CS, S}).
    l16 = copy.deepcopy(r0)
    del l16["regions"][S]
    eval_case("VP-16", h0, [], l16,
              lambda v: v["outcome"] == "fail"
              and v["failed_checks"] == [("S1", (D_CS, S))]
              and v["seal"] is None,
              {"outcome": "fail", "failed_checks": [["S1", [D_CS, S]]]})

    # VP-17 — L = R: S1 accepts the valid dependencies (PASS).
    eval_case("VP-17", h0, [], copy.deepcopy(r0),
              lambda v: v["outcome"] == "pass"
              and v["failed_checks"] == [],
              {"outcome": "pass"})

    # VP-18 — L with C's version lowered: FAIL(S2, {C}) under
    # the settled ruling (correction round, C-B1): the pack text
    # left the case conditional ("if S2 does fail on L, FAIL(S2)
    # governs"); the ruling defines a version regression against
    # replay as exactly an S2 failure on L. I-3's MISMATCH
    # reading is superseded.
    l18 = copy.deepcopy(r0)
    l18["regions"][C]["version"] = 0
    eval_case("VP-18", h0, [], l18,
              lambda v: v["outcome"] == "fail"
              and v["failed_checks"] == [("S2", (C,))]
              and v["raises"] == [("S2", (C,))]
              and v["seal"] is None,
              {"outcome": "fail",
               "failed_checks": [["S2", [C]]]})

    # VP-18-hi — L with C's version RAISED: unexplained
    # higher-version divergence is MISMATCH, never an S2
    # failure (the ruling's lower-bound-only precision).
    l18h = copy.deepcopy(r0)
    l18h["regions"][C]["version"] = 7
    eval_case("VP-18-hi", h0, [], l18h,
              lambda v: v["outcome"] == "mismatch"
              and v["failed_checks"] == []
              and ("regions", C) in v["divergence"]
              and v["seal"] is None,
              {"outcome": "mismatch",
               "note": "higher-version divergence, no S2 finding"})

    # VP-18-prec — divergence (S absent) combined with an S1
    # failure and an S2 regression on L: FAIL governs over
    # MISMATCH, with both findings recorded (the C1 precedence).
    l18p = copy.deepcopy(r0)
    del l18p["regions"][S]
    l18p["regions"][C]["version"] = 0
    eval_case("VP-18-prec", h0, [], l18p,
              lambda v: v["outcome"] == "fail"
              and v["failed_checks"] == [("S1", (D_CS, S)),
                                          ("S2", (C,))]
              and v["seal"] is None,
              {"outcome": "fail",
               "failed_checks": [["S1", [D_CS, S]], ["S2", [C]]]})

    # VP-19 — staged advance: add C->P and append content on I.
    _, b19, full19 = chained_pair([ropened()], [accept_spec(AGENT_A, [
        {"kind": "add_dependency",
         "dependency": {"source": C, "target": P, "kind": "uses"}},
        {"kind": "append_content", "region_id": I,
         "text": " (Advanced.)"}], assigned={"0": D_CP})])
    l19 = fold_of(full19)
    eval_case("VP-19", h0, b19, l19,
              lambda v: v["outcome"] == "pass"
              and l19["regions"][C]["version"] == 2
              and l19["regions"][P]["version"] == 2
              and l19["regions"][I]["version"] == 2,
              {"outcome": "pass", "note": "endpoints advanced"})

    # VP-20 — L carries the plant dep S->C active: FAIL(S3, cycle).
    l20 = copy.deepcopy(r0)
    l20["dependencies"][D_SC] = {
        "dependency_id": D_SC, "source": S, "target": C,
        "kind": "uses", "status": "active"}
    eval_case("VP-20", h0, [], l20,
              lambda v: v["outcome"] == "fail"
              and v["failed_checks"] == [("S3", (D_CS, D_SC))]
              and v["seal"] is None,
              {"outcome": "fail",
               "failed_checks": [["S3", [D_CS, D_SC]]]})

    # VP-21 — convergent genesis deps, no cycle: PASS.
    convergent = [
        {"dependency_id": "00000000-0000-4000-8000-000000000203",
         "source": P, "target": S, "kind": "uses", "status": "active"},
        {"dependency_id": "00000000-0000-4000-8000-000000000204",
         "source": I, "target": S, "kind": "uses", "status": "active"}]
    h21 = chain([ropened(extra_deps=convergent)])
    eval_case("VP-21", h21, [], fold_of(h21),
              lambda v: v["outcome"] == "pass"
              and v["failed_checks"] == [],
              {"outcome": "pass"})

    # VP-24 — explicit staged batch, L = fold(H+B): PASS + seal.
    _, b24, full24 = chained_pair([ropened()], [accept_spec(AGENT_A, [
        {"kind": "append_content", "region_id": I,
         "text": " (Candidate.)"}])])
    eval_case("VP-24", h0, b24, fold_of(full24),
              lambda v: v["outcome"] == "pass"
              and v["seal"] is not None,
              {"outcome": "pass", "seal": "issued"})

    # VP-25 — the batch omitted: refused on both sides.
    eng = verdict_contract(evaluate_attempt(h0, None, r0))
    chk = checker_eval(h0, None, r0, omit=True)
    record("VP-25", {"outcome": "refused"}, eng, chk,
           eng == chk and eng["outcome"] == "refused",
           {"history": h0, "staged": None})

    # VP-26 — L diverges from R in P's content: MISMATCH naming P.
    l26 = fold_of(full24)
    l26["regions"][P]["content"] = "Altered content."
    eval_case("VP-26", h0, b24, l26,
              lambda v: v["outcome"] == "mismatch"
              and ("regions", P) in v["divergence"]
              and v["seal"] is None,
              {"outcome": "mismatch", "divergence_names": P})

    # VP-27 — genesis asserts a dangling dep C->Q; replay succeeds;
    # S1 fails on L = R.
    dangling = {"dependency_id": D_CQ, "source": C, "target": Q,
                "kind": "uses", "status": "active"}
    h27 = chain([ropened(extra_deps=[dangling])])
    eval_case("VP-27", h27, [], fold_of(h27),
              lambda v: v["outcome"] == "fail"
              and v["failed_checks"] == [("S1", (D_CQ, Q))]
              and v["seal"] is None,
              {"outcome": "fail", "failed_checks": [["S1", [D_CQ, Q]]]})

    # VP-47 — the genesis content carries the planted semantic
    # contradiction; structure is sound: PASS, no raises.
    eval_case("VP-47", h0, [], copy.deepcopy(r0),
              lambda v: v["outcome"] == "pass" and v["raises"] == [],
              {"outcome": "pass", "raises": []})

    # -- structural lifecycle over canned inputs (VP-39..VP-44) ----
    t_id = "t-structural-s1"
    h_t = chain([ropened(), tension_raised(
        t_id, "structural", [S], "checker", check="S1",
        affected=[D_CS, S], origin_ref="seal-attempt:0")])
    r_t = fold_of(h_t)

    # VP-39 — same identity, deps enumerated in the other order:
    # the finding attaches; nothing raises.
    l39 = copy.deepcopy(r_t)
    del l39["regions"][S]
    l39["dependencies"] = dict(reversed(list(
        l39["dependencies"].items())))
    eval_case("VP-39", h_t, [], l39,
              lambda v: v["outcome"] == "fail"
              and v["attachments"] == [t_id] and v["raises"] == []
              and v["resolutions"] == [],
              {"outcome": "fail", "attachments": [t_id]})

    # VP-40 — a second dangling dep is a different identity: it
    # raises; the standing tension's finding attaches to it.
    l40 = copy.deepcopy(r_t)
    del l40["regions"][S]
    del l40["regions"][I]
    eval_case("VP-40", h_t, [], l40,
              lambda v: v["outcome"] == "fail"
              and v["attachments"] == [t_id]
              and ("S1", (D_NI, I)) in v["raises"]
              and v["resolutions"] == [],
              {"outcome": "fail", "attachments": [t_id],
               "raises_include": [["S1", [D_NI, I]]]})

    # VP-41 — a different dep to S was removed; D-CS still dangles:
    # the tension is not resolved; its finding attaches.
    h_t2 = chain([
        ropened(),
        accept_spec(AGENT_A, [
            {"kind": "add_dependency",
             "dependency": {"source": P, "target": S, "kind": "uses"}}],
            assigned={"0": D_PS}),
        tension_raised(t_id, "structural", [S], "checker",
                       check="S1", affected=[D_CS, S],
                       origin_ref="seal-attempt:0")])
    l41 = fold_of(h_t2)
    del l41["regions"][S]
    l41["dependencies"][D_PS]["status"] = "removed"
    eval_case("VP-41", h_t2, [], l41,
              lambda v: v["outcome"] == "fail"
              and v["attachments"] == [t_id]
              and v["resolutions"] == [],
              {"outcome": "fail", "attachments": [t_id],
               "resolutions": []})

    # VP-42 — the correcting batch removes D-CS: resolution, PASS.
    h_t_specs = [ropened(), tension_raised(
        t_id, "structural", [S], "checker", check="S1",
        affected=[D_CS, S], origin_ref="seal-attempt:0")]
    _, b42, full42 = chained_pair(h_t_specs, [accept_spec(AGENT_A, [
        {"kind": "remove_dependency", "dependency_id": D_CS}])])
    eval_case("VP-42", h_t, b42, fold_of(full42),
              lambda v: v["outcome"] == "pass"
              and v["resolutions"] == [t_id]
              and v["seal"] is not None,
              {"outcome": "pass", "resolutions": [t_id]})

    # VP-43 — S still missing (S1 still fails; S2 passes): the
    # tension remains open.
    l43 = copy.deepcopy(r_t)
    del l43["regions"][S]
    eval_case("VP-43", h_t, [], l43,
              lambda v: v["outcome"] == "fail"
              and v["attachments"] == [t_id]
              and v["resolutions"] == []
              and all(f[0] != "S2" for f in v["failed_checks"]),
              {"outcome": "fail", "attachments": [t_id]})

    # VP-44 — a content correction that does not repair the set:
    # the finding attaches; no transition is inferred.
    _, b44, full44 = chained_pair(h_t_specs, [accept_spec(AGENT_A, [
        {"kind": "append_content", "region_id": C,
         "text": " (Attempted repair.)"}])])
    l44 = fold_of(full44)
    del l44["regions"][S]
    eval_case("VP-44", h_t, b44, l44,
              lambda v: v["outcome"] == "fail"
              and v["attachments"] == [t_id]
              and v["resolutions"] == [],
              {"outcome": "fail", "attachments": [t_id]})


# -- live cases through the harness (VP-22, VP-23, VP-28,
#    VP-30..VP-38, VP-45, VP-46, VP-48, VP-49) ---------------------------

def bound_run(name):
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    engine = Engine.open_run(store, name, binding=stage4_binding())
    return store, engine, Harness(engine)


def contrib(author, idem, base, read, write, ops, ref):
    return {"action": "contribute", "contribution": {
        "author": author, "idempotency_id": idem, "base_versions": base,
        "read_set": read, "write_set": write, "operations": ops,
        "rationale": "Recorded rationale.",
        "discovery_source": "fabric_read", "discovery_ref": ref}}


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


def live_record(case, expected, ok, store, diagnostic=""):
    """Record a live-path case that has NO seal attempt to
    evaluate (VP-22, VP-23: a rejected contribution stages no
    attempt, so no (H, B, L) attempt input exists). Such cases
    are marked not dual-applicable, with the justification in
    the manifest — they are never represented as dual
    agreement (correction round, C-B4)."""
    history = store.all_events()
    record(case, expected,
           {"history_types": [e["type"] for e in history]},
           {"note": "no seal attempt is staged for a rejected "
                    "contribution; there is no (H, B, L) attempt "
                    "input to evaluate"},
           ok, {"history": history}, diagnostic,
           dual_applicable=False,
           dual_note="no attempt is staged for a rejected "
                     "contribution; the case's subject is the "
                     "seal-trigger contract on the live path")


def dual_attempt_record(case, expected, attempts, expect_fn,
                        live_ok, store, diagnostic=""):
    """Record a live attempt case with BOTH implementations'
    actual verdicts (correction round, C-B4): each captured
    attempt's exact (H, B, L) — taken by the harness's
    attempt_observer at the moment the live checker was invoked
    — is replayed through fabric.seal.evaluate_attempt and the
    checker process. The manifest records both verdicts, the
    expected outcome, and the fixture hash over the captured
    inputs; the case passes only when the live-path assertions
    also hold AND the two verdicts agree AND they match the
    case's expectation."""
    pairs = []
    agree = True
    for att in attempts:
        eng = engine_eval(att["history"], att["staged"],
                          att["snapshot"],
                          att["authenticated_actor"])
        chk = checker_eval(att["history"], att["staged"],
                           att["snapshot"],
                           att["authenticated_actor"])
        agree = agree and eng == chk
        pairs.append((eng, chk))
    eng_obs = pairs[0][0] if len(pairs) == 1 \
        else [p[0] for p in pairs]
    chk_obs = pairs[0][1] if len(pairs) == 1 \
        else [p[1] for p in pairs]
    verdicts = [p[0] for p in pairs]
    ok = live_ok and agree and bool(expect_fn(verdicts))
    fixture = {"attempts": attempts,
               "live_history": store.all_events()}
    record(case, expected, eng_obs, chk_obs, ok, fixture,
           "" if ok else f"agree={agree} live_ok={live_ok} "
                         f"engine={eng_obs} checker={chk_obs} "
                         f"{diagnostic}")


def run_live_cases():
    # VP-22 — a targeting violation is rejected `schema`; no attempt.
    store, eng, h = bound_run("vp22")
    tok = h.issue_token(AGENT_A)
    ref = open_regions(h, store, tok, C, S)
    out = h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), {C: 1, S: 1}, [C, S], [C],
        [{"kind": "append_content", "region_id": S,
          "text": " (Out of scope.)"}], ref))
    live_record("VP-22", {"outcome": "schema", "attempts": 0},
                out["outcome"] == "schema"
                and events_of(store, "SEAL_ATTEMPTED") == [],
                store)

    # VP-23 — a stale rejection triggers no attempt.
    store, eng, h = bound_run("vp23")
    tok = h.issue_token(AGENT_A)
    ref = open_regions(h, store, tok, C, S)
    out = h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), {C: 99, S: 1}, [C, S], [C],
        [{"kind": "append_content", "region_id": C,
          "text": " (Stale.)"}], ref))
    live_record("VP-23", {"outcome": "stale", "attempts": 0},
                out["outcome"] == "stale"
                and events_of(store, "SEAL_ATTEMPTED") == [],
                store)

    # VP-28 — the checker's transitive module graph, audited in a
    # subprocess, plus a static scan of its imports.
    audit = subprocess.run(
        [sys.executable, "-c",
         "import sys, fabric.checker; "
         "print(','.join(sorted(m for m in sys.modules "
         "if m.startswith('fabric'))))"],
        capture_output=True, text=True, cwd=ROOT,
        env={**os.environ, "PYTHONPATH": ROOT,
             "PYTHONDONTWRITEBYTECODE": "1"})
    modules = audit.stdout.strip().split(",") if audit.stdout.strip() \
        else []
    with open(os.path.join(ROOT, "fabric", "checker.py"),
              encoding="utf-8") as fh:
        checker_src = fh.read()
    imported = set(re.findall(
        r"^\s*(?:from|import)\s+(\.?[A-Za-z_][\w.]*)",
        checker_src, re.M))
    fabric_imports = {m.lstrip(".") for m in imported
                      if m.startswith("fabric")
                      or m.startswith(".")}
    static_ok = fabric_imports == {"fabric.canonical"}
    record("VP-28", {"modules": ["fabric", "fabric.canonical",
                                 "fabric.checker"]},
           {"modules": modules, "static_scan_ok": static_ok},
           {"modules": modules, "static_scan_ok": static_ok},
           modules == ["fabric", "fabric.canonical", "fabric.checker"]
           and static_ok,
           {"audit_stdout": audit.stdout},
           "" if modules == ["fabric", "fabric.canonical",
                             "fabric.checker"] and static_ok
           else f"modules={modules} static_ok={static_ok}",
           dual_applicable=False,
           dual_note="single-subject case: the audit examines "
                     "the checker alone (I-13, accepted at "
                     "examination); the two columns carry the "
                     "one audit result, not two verdicts")

    # VP-30 — one accepted contribution, exactly one attempt, PASS.
    store, eng, h = bound_run("vp30")
    captured = []
    h.attempt_observer = captured.append
    tok = h.issue_token(AGENT_A)
    ref = open_regions(h, store, tok, I, P)
    out = h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, P), [I, P], [I],
        [{"kind": "append_content", "region_id": I,
          "text": " (One.)"}], ref))
    attempts = events_of(store, "SEAL_ATTEMPTED")
    dual_attempt_record(
        "VP-30", {"attempts": 1, "outcome": "pass",
                  "dual_verdicts": "pass, agreeing"},
        captured,
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "pass"
        and vs[0]["seal"] is not None,
        out["outcome"] == "accepted" and len(attempts) == 1
        and attempts[0]["payload"]["outcome"] == "pass"
        and len(captured) == 1,
        store)

    # VP-31 + VP-33 — live-state fault: the attempt still occurs,
    # fails S1, raises the structural tension; a further
    # contribution still gets its attempt.
    store, eng, h = bound_run("vp31")
    captured = []
    h.attempt_observer = captured.append
    tok = h.issue_token(AGENT_A)
    ref = open_regions(h, store, tok, I, P)
    del eng.state["regions"][S]  # the fault: live state only
    out = h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, P), [I, P], [I],
        [{"kind": "append_content", "region_id": I,
          "text": " (Independent.)"}], ref))
    attempts = events_of(store, "SEAL_ATTEMPTED")
    raised = [e for e in events_of(store, "TENSION_RAISED")
              if e["payload"].get("type") == "structural"]
    first = attempts[0]["payload"] if attempts else {}
    ok31 = out["outcome"] == "accepted" and len(attempts) == 1 \
        and first.get("outcome") == "fail" and len(raised) == 1
    out2 = h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, P), [I, P], [P],
        [{"kind": "append_content", "region_id": P,
          "text": " (Still attempted.)"}], ref))
    attempts = events_of(store, "SEAL_ATTEMPTED")
    ok31 = ok31 and out2["outcome"] == "accepted" \
        and len(attempts) == 2
    dual_attempt_record(
        "VP-31", {"attempts": 2, "first_outcome": "fail",
                  "structural_raised": 1,
                  "dual_verdicts": "fail(S1), then fail(S1) "
                                   "attached, agreeing"},
        captured[:2],
        lambda vs: len(vs) == 2
        and vs[0]["outcome"] == "fail"
        and vs[0]["failed_checks"] == [("S1", (D_CS, S))]
        and vs[0]["raises"] == [("S1", (D_CS, S))]
        and vs[1]["outcome"] == "fail"
        and vs[1]["failed_checks"] == [("S1", (D_CS, S))]
        and len(vs[1]["attachments"]) == 1,
        ok31 and len(captured) >= 2, store,
        "" if ok31 else f"attempts={len(attempts)} "
                        f"raised={len(raised)}")
    ok33 = first.get("outcome") == "fail" \
        and first.get("failed_checks") == [
            {"check": "S1", "affected": [D_CS, S]}] \
        and "seal" not in first
    dual_attempt_record(
        "VP-33", {"outcome": "fail",
                  "failed_checks": [["S1", [D_CS, S]]],
                  "seal": "absent",
                  "dual_verdicts": "fail(S1), agreeing"},
        captured[:1],
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "fail"
        and vs[0]["failed_checks"] == [("S1", (D_CS, S))]
        and vs[0]["seal"] is None,
        ok33 and len(captured) >= 1, store)

    # VP-32 — continuation of the VP-31 run: repair (I-5) and the
    # correcting contribution; the group ends SEAL_ATTEMPTED then
    # TENSION_STATUS with the attempt's seq in the evidence.
    eng.state = verified_fold(store.all_events(), CONSTITUTION_HASH)
    tok2 = h.issue_token(AGENT_B)
    ref2 = open_regions(h, store, tok2, C, S)
    out = h.submit(tok2, contrib(
        AGENT_B, str(uuid.uuid4()), versions(eng, C, S), [C, S],
        [C, S], [{"kind": "remove_dependency", "dependency_id": D_CS}],
        ref2))
    evs = store.all_events()
    tail = evs[-2:]
    ok32 = out["outcome"] == "accepted" \
        and [e["type"] for e in tail] == [
            "SEAL_ATTEMPTED", "TENSION_STATUS"] \
        and tail[0]["payload"]["outcome"] == "pass" \
        and tail[1]["payload"]["to"] == "resolved" \
        and tail[1]["payload"]["evidence"]["seal_attempt_seq"] \
        == tail[0]["event_seq"]
    t32 = raised[0]["payload"]["tension_id"] if raised else None
    dual_attempt_record(
        "VP-32", {"order": ["SEAL_ATTEMPTED", "TENSION_STATUS"],
                  "evidence_seq": "the attempt's",
                  "dual_verdicts": "pass with the resolution, "
                                   "agreeing"},
        captured[2:3],
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "pass"
        and vs[0]["resolutions"] == [t32],
        ok32 and len(captured) == 3, store,
        "" if ok32 else f"tail={[e['type'] for e in tail]}")

    # VP-45 — the nine-step genuine lifecycle, in-process form.
    store, eng, h = bound_run("vp45")
    captured = []
    h.attempt_observer = captured.append
    steps = []
    steps.append(verified_fold(store.all_events(),
                               CONSTITUTION_HASH) is not None)  # (1)
    head_before = store.all_events()[-1]["hash"]
    del eng.state["regions"][S]  # inject: L only
    replayed = verified_fold(store.all_events(), CONSTITUTION_HASH)
    steps.append(store.all_events()[-1]["hash"] == head_before
                 and S in replayed["regions"])  # (2)
    tok = h.issue_token(AGENT_A)
    ref = open_regions(h, store, tok, I, P)
    out = h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, P), [I, P], [I],
        [{"kind": "append_content", "region_id": I,
          "text": " (Ordinary.)"}], ref))
    attempts = events_of(store, "SEAL_ATTEMPTED")
    raised = [e for e in events_of(store, "TENSION_RAISED")
              if e["payload"].get("type") == "structural"]
    steps.append(out["outcome"] == "accepted"
                 and attempts[-1]["payload"]["outcome"] == "fail"
                 and attempts[-1]["payload"]["failed_checks"] == [
                     {"check": "S1", "affected": [D_CS, S]}]
                 and "seal" not in attempts[-1]["payload"]
                 and len(raised) == 1
                 and raised[0]["payload"]["origin"] == "checker")  # (3)
    t_id45 = raised[0]["payload"]["tension_id"] if raised else None
    steps.append(eng.state["tensions"][t_id45]["status"] == "open"
                 if t_id45 else False)  # (4) open, not blocking
    eng.state = verified_fold(store.all_events(), CONSTITUTION_HASH)
    tok2 = h.issue_token(AGENT_B)
    ref2 = open_regions(h, store, tok2, C, S)
    out = h.submit(tok2, contrib(
        AGENT_B, str(uuid.uuid4()), versions(eng, C, S), [C, S],
        [C, S], [{"kind": "remove_dependency", "dependency_id": D_CS}],
        ref2))
    steps.append(out["outcome"] == "accepted")  # (5) genuine correction
    attempts = events_of(store, "SEAL_ATTEMPTED")
    steps.append(attempts[-1]["payload"]["outcome"] == "pass")  # (6)
    steps.append(attempts[-1]["payload"]["seal"]["position"]
                 == attempts[-1]["event_seq"])  # (7)
    status = [e for e in events_of(store, "TENSION_STATUS")
              if e["payload"]["tension_id"] == t_id45]
    steps.append(bool(status)
                 and status[-1]["payload"]["to"] == "resolved"
                 and status[-1]["payload"]["evidence"]
                 ["seal_attempt_seq"] == attempts[-1]["event_seq"])  # (8)
    tail = store.all_events()[-2:]
    steps.append([e["type"] for e in tail] == [
        "SEAL_ATTEMPTED", "TENSION_STATUS"])  # (9)
    dual_attempt_record(
        "VP-45", {"steps": "1-9 in order",
                  "dual_verdicts": "fail(S1), then pass with "
                                   "the resolution, agreeing"},
        captured,
        lambda vs: len(vs) == 2
        and vs[0]["outcome"] == "fail"
        and vs[0]["failed_checks"] == [("S1", (D_CS, S))]
        and vs[1]["outcome"] == "pass"
        and vs[1]["resolutions"] == [t_id45],
        all(steps) and len(captured) == 2, store,
        "" if all(steps) else f"steps={steps}")

    # VP-34 + VP-46 — semantic questions recorded, never cleared.
    store, eng, h = bound_run("vp34")
    captured = []
    h.attempt_observer = captured.append
    toks = {a: h.issue_token(a) for a in (AGENT_A, AGENT_B)}
    ref_a = open_regions(h, store, toks[AGENT_A], I, N)
    out = h.submit(toks[AGENT_A], contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, N), [I, N], [],
        [{"kind": "raise_tension",
          "tension": {"type": "semantic", "regions": [I, N],
                      "description": "Stateless vs pinned."}}], ref_a))
    t1 = events_of(store, "TENSION_RAISED")[-1]["payload"]["tension_id"]
    ref_b = open_regions(h, store, toks[AGENT_B], P, O)
    out = h.submit(toks[AGENT_B], contrib(
        AGENT_B, str(uuid.uuid4()), versions(eng, P, O), [P, O], [],
        [{"kind": "raise_tension",
          "tension": {"type": "semantic", "regions": [P, O],
                      "description": "A second question."}}], ref_b))
    t2 = events_of(store, "TENSION_RAISED")[-1]["payload"]["tension_id"]
    agent_c = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
    tok_c = h.issue_token(agent_c)
    open_regions(h, store, tok_c, P, O)
    out = h.assess(tok_c, {"assessment_id": str(uuid.uuid4()),
                           "author": agent_c, "target_kind": "tension",
                           "target_id": t2, "position": "clarifies",
                           "reasoning": "Examined and clarified."})
    assessed_ok = out["outcome"] == "recorded" \
        and eng.state["tensions"][t2]["status"] == "examined"
    out = h.submit(toks[AGENT_A], contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, N), [I, N], [I],
        [{"kind": "append_content", "region_id": I,
          "text": " (Content.)"}], ref_a))
    attempts = events_of(store, "SEAL_ATTEMPTED")
    seal = attempts[-1]["payload"].get("seal") or {}
    questions = {q["tension_id"]: q for q in
                 seal.get("outstanding_semantic_questions", [])}
    ok34 = assessed_ok and out["outcome"] == "accepted" \
        and attempts[-1]["payload"]["outcome"] == "pass" \
        and questions.get(t1, {}).get("status") == "open" \
        and questions.get(t1, {}).get("examined_by") == "unexamined" \
        and questions.get(t2, {}).get("status") == "examined" \
        and questions.get(t2, {}).get("examined_by") == [agent_c] \
        and seal.get("semantic_clearance") is False \
        and eng.state["tensions"][t1]["status"] == "open" \
        and eng.state["tensions"][t2]["status"] == "examined"
    dual_attempt_record(
        "VP-34", {"seal": "issued", "questions": "both, marked",
                  "statuses": "unchanged",
                  "dual_verdicts": "pass; the seal lists both "
                                   "questions with the same marks, "
                                   "agreeing"},
        captured[2:3],
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "pass"
        and vs[0]["seal"] is not None
        and vs[0]["seal"]["questions"] == sorted([
            (t1, "open", "unexamined"),
            (t2, "examined", (agent_c,))])
        and vs[0]["seal"]["semantic_clearance"] is False,
        ok34 and len(captured) == 3, store,
        "" if ok34 else f"questions={questions} "
                        f"assessed_ok={assessed_ok}")
    first_seal = next(
        (a for a in attempts if a["payload"].get("seal")), None)
    fq = {q["tension_id"]: q for q in (first_seal["payload"]["seal"]
          ["outstanding_semantic_questions"] if first_seal else [])}
    ok46 = bool(first_seal) and fq.get(t1, {}).get("status") == "open" \
        and eng.state["tensions"][t1]["status"] == "open"
    dual_attempt_record(
        "VP-46", {"seal": "issued", "tension_status": "open",
                  "dual_verdicts": "pass; the first seal lists "
                                   "T1 open, agreeing"},
        captured[0:1],
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "pass"
        and vs[0]["seal"] is not None
        and vs[0]["seal"]["questions"] == [
            (t1, "open", "unexamined")],
        ok46 and len(captured) == 3, store)

    # VP-35 — contributions-since-last-seal boundary (new in the
    # correction round: round 1's manifest contained no VP-35
    # record at all). Two accepted contributions, each followed
    # by a passing attempt: seal 1 lists exactly the first
    # contribution; seal 2 exactly the second.
    store, eng, h = bound_run("vp35")
    captured = []
    h.attempt_observer = captured.append
    tok = h.issue_token(AGENT_A)
    ref = open_regions(h, store, tok, I, P)
    out1 = h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, P), [I, P], [I],
        [{"kind": "append_content", "region_id": I,
          "text": " (First.)"}], ref))
    out2 = h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, P), [I, P], [P],
        [{"kind": "append_content", "region_id": P,
          "text": " (Second.)"}], ref))
    cid1 = out1.get("contribution_id")
    cid2 = out2.get("contribution_id")
    attempts = events_of(store, "SEAL_ATTEMPTED")
    live35 = out1["outcome"] == "accepted" \
        and out2["outcome"] == "accepted" and len(attempts) == 2 \
        and attempts[0]["payload"]["seal"][
            "contributions_since_last_seal"] == [cid1] \
        and attempts[1]["payload"]["seal"][
            "contributions_since_last_seal"] == [cid2]
    dual_attempt_record(
        "VP-35", {"seal_1_lists": "[cid1]", "seal_2_lists": "[cid2]",
                  "dual_verdicts": "pass with the same lists, "
                                   "agreeing"},
        captured,
        lambda vs: len(vs) == 2
        and vs[0]["outcome"] == "pass"
        and vs[0]["seal"]["contributions"] == [cid1]
        and vs[1]["outcome"] == "pass"
        and vs[1]["seal"]["contributions"] == [cid2],
        live35 and len(captured) == 2, store)

    # VP-36 — checker process failure: CheckerFailure, no partial
    # group, history unchanged.
    store, eng, h = bound_run("vp36")
    captured = []
    h.attempt_observer = captured.append
    h.checker_command = ["/bin/false"]
    tok = h.issue_token(AGENT_A)
    ref = open_regions(h, store, tok, I, P)
    n_before = len(store.all_events())
    raised_cf = False
    try:
        h.submit(tok, contrib(
            AGENT_A, str(uuid.uuid4()), versions(eng, I, P), [I, P], [I],
            [{"kind": "append_content", "region_id": I,
              "text": " (Doomed.)"}], ref))
    except CheckerFailure:
        raised_cf = True
    dual_attempt_record(
        "VP-36", {"exception": "CheckerFailure",
                  "history": "unchanged",
                  "dual_verdicts": "the doomed attempt's inputs, "
                                   "evaluated by both evaluators "
                                   "in working form: agreeing"},
        captured,
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "pass",
        raised_cf and len(store.all_events()) == n_before
        and len(captured) == 1,
        store)

    # VP-37 — an examiner-side accepted commit with no attempt:
    # close makes exactly one close-time attempt, then RUN_CLOSED.
    store, eng, h = bound_run("vp37")
    captured = []
    h.attempt_observer = captured.append
    eng.commit_events([accept_spec(AGENT_A, [
        {"kind": "append_content", "region_id": I,
         "text": " (Examiner-side.)"}])])
    out = h.close_run()
    evs = store.all_events()
    dual_attempt_record(
        "VP-37", {"close_attempts": 1, "then": "RUN_CLOSED",
                  "dual_verdicts": "pass on (H, B=[], L), "
                                   "agreeing"},
        captured,
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "pass",
        out["close_attempt_events"] == 1
        and [e["type"] for e in evs[-2:]] == [
            "SEAL_ATTEMPTED", "RUN_CLOSED"]
        and len(captured) == 1,
        store)

    # VP-38 — the final commit already had its attempt: close adds
    # no second attempt.
    store, eng, h = bound_run("vp38")
    captured = []
    h.attempt_observer = captured.append
    tok = h.issue_token(AGENT_A)
    ref = open_regions(h, store, tok, I, P)
    h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, P), [I, P], [I],
        [{"kind": "append_content", "region_id": I,
          "text": " (Sealed.)"}], ref))
    n_attempts = len(events_of(store, "SEAL_ATTEMPTED"))
    out = h.close_run()
    dual_attempt_record(
        "VP-38", {"close_attempts": 0, "then": "RUN_CLOSED",
                  "dual_verdicts": "the final commit's attempt: "
                                   "pass, agreeing; no second "
                                   "attempt was evaluated at close"},
        captured,
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "pass",
        out["close_attempt_events"] == 0
        and len(events_of(store, "SEAL_ATTEMPTED")) == n_attempts
        and store.all_events()[-1]["type"] == "RUN_CLOSED"
        and len(captured) == 1,
        store)

    # VP-48 — an assessment targeting an open structural tension is
    # rejected structural_target; nothing is recorded; the tension
    # stands open.
    store, eng, h = bound_run("vp48")
    captured = []
    h.attempt_observer = captured.append
    tok = h.issue_token(AGENT_A)
    open_regions(h, store, tok, C, S)  # A discovers S before the fault
    tok_b = h.issue_token(AGENT_B)
    ref = open_regions(h, store, tok_b, I, P)
    del eng.state["regions"][S]
    h.submit(tok_b, contrib(
        AGENT_B, str(uuid.uuid4()), versions(eng, I, P), [I, P], [I],
        [{"kind": "append_content", "region_id": I,
          "text": " (Faulted.)"}], ref))
    raised = [e for e in events_of(store, "TENSION_RAISED")
              if e["payload"].get("type") == "structural"]
    t_id48 = raised[0]["payload"]["tension_id"]
    out = h.assess(tok, {"assessment_id": str(uuid.uuid4()),
                         "author": AGENT_A, "target_kind": "tension",
                         "target_id": t_id48, "position": "clarifies",
                         "reasoning": "An attempt to assess structure."})
    dual_attempt_record(
        "VP-48", {"outcome": "rejected",
                  "reason": "structural_target",
                  "dual_verdicts": "the faulted attempt: fail(S1) "
                                   "with the raise, agreeing"},
        captured,
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "fail"
        and vs[0]["failed_checks"] == [("S1", (D_CS, S))]
        and vs[0]["raises"] == [("S1", (D_CS, S))],
        out["outcome"] == "rejected"
        and out.get("reason") == "structural_target"
        and eng.state["assessments"] == {}
        and eng.state["tensions"][t_id48]["status"] == "open"
        and len(captured) == 1,
        store)

    # VP-49 — facets unexamined at genesis; a passing attempt seals
    # and changes no facet status; no completion is inferred.
    store, eng, h = bound_run("vp49")
    captured = []
    h.attempt_observer = captured.append
    tok = h.issue_token(AGENT_A)
    ref = open_regions(h, store, tok, I, P)
    facets_before = copy.deepcopy(eng.state["facet_status"])
    out = h.submit(tok, contrib(
        AGENT_A, str(uuid.uuid4()), versions(eng, I, P), [I, P], [I],
        [{"kind": "append_content", "region_id": I,
          "text": " (Content.)"}], ref))
    attempts = events_of(store, "SEAL_ATTEMPTED")
    group = store.all_events()[
        [e["type"] for e in store.all_events()].index(
            "CONTRIBUTION_ACCEPTED"):]
    facet_positions = [i for i, e in enumerate(group)
                       if e["type"] == "FACET_STATUS"]
    attempt_position = [i for i, e in enumerate(group)
                        if e["type"] == "SEAL_ATTEMPTED"]
    dual_attempt_record(
        "VP-49", {"seal": "issued",
                  "facet_status": "section-5 derivation only",
                  "dual_verdicts": "pass, agreeing"},
        captured,
        lambda vs: len(vs) == 1 and vs[0]["outcome"] == "pass"
        and vs[0]["seal"] is not None,
        out["outcome"] == "accepted"
        and attempts[-1]["payload"]["outcome"] == "pass"
        and eng.state["facet_status"] == {I: "unexamined"}
        and all(fp < attempt_position[0]
                for fp in facet_positions)
        and len(captured) == 1,
        store)


# -- starvation cases (VP-50..VP-54) --------------------------------------

def starvation_events(specs):
    return [{"event_seq": i, "event_id": str(uuid.uuid4()),
             "type": t, "actor": a, "affected": [],
             "payload": p, "prev_hash": "", "hash": ""}
            for i, (t, a, p) in enumerate(specs, 1)]


def starvation_cli(events):
    path = os.path.join(tempfile.mkdtemp(), "history.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(events, fh)
    proc = subprocess.run(
        [sys.executable, "-m", "fabric.starvation", path],
        capture_output=True, text=True, cwd=ROOT,
        env={**os.environ, "PYTHONPATH": ROOT,
             "PYTHONDONTWRITEBYTECODE": "1"})
    if proc.returncode != 0:
        raise RuntimeError(f"starvation CLI failed: {proc.stderr[-300:]}")
    return proc.stdout.strip().encode("utf-8")


def starvation_case(case, events, expect_fn, expected):
    api = starvation.build_report(events)
    api_bytes = starvation.report_bytes(events)
    cli_bytes = starvation_cli(events)
    ok = api_bytes == cli_bytes and expect_fn(api)
    record(case, expected,
           {"report": api, "bytes_sha256": sha256_hex(api_bytes)},
           {"bytes_sha256": sha256_hex(cli_bytes),
            "byte_identical": api_bytes == cli_bytes},
           ok, {"events": events},
           "" if ok else f"api={api}",
           dual_applicable=False,
           dual_note="the starvation report is one derived-report "
                     "implementation by design (I-12, accepted "
                     "at examination); the agreement property is "
                     "byte-identity of the module API and its "
                     "standalone CLI over the same input, "
                     "asserted inside the case")


def run_starvation_cases():
    a, b, c = AGENT_A, AGENT_B, "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
    evs50 = starvation_events([
        ("CONTRIBUTION_ACCEPTED", a, {"summary": "x"}),
        ("IDLE", a, {"summary": "x"}),
        ("CONTRIBUTION_REJECTED", b, {"outcome": "stale", "diff": []}),
        ("CONTRIBUTION_REJECTED", b, {"outcome": "schema"}),
        ("IDLE", c, {"summary": "x"}),
        ("IDLE", c, {"summary": "x"}),
    ])
    starvation_case("VP-50", evs50,
                    lambda r: set(r["agents"]) == {a, b, c}
                    and r["agents"][b]["accepted_commits"] == 0
                    and r["agents"][c]["wakes"] == 2,
                    {"agents": "A, B, C all present"})

    evs51 = starvation_events([
        ("CONTRIBUTION_REJECTED", a, {"outcome": "stale", "diff": []}),
        ("CONTRIBUTION_REJECTED", a, {"outcome": "schema"}),
        ("CONTRIBUTION_ACCEPTED", a, {"summary": "x"}),
        ("CONTRIBUTION_REJECTED", a, {"outcome": "stale", "diff": []}),
    ])
    starvation_case("VP-51", evs51,
                    lambda r: r["agents"][a]
                    ["max_consecutive_rejections"] == 2
                    and r["agents"][a]["consecutive_rejections"] == 1,
                    {"max_run": 2, "current_run": 1})

    evs52 = starvation_events([
        ("CONTRIBUTION_REJECTED", b, {"outcome": "stale", "diff": []}),
        ("IDLE", b, {"summary": "x"}),
        ("CONTRIBUTION_REJECTED", b, {"outcome": "schema"}),
    ])
    starvation_case("VP-52", evs52,
                    lambda r: "wakes_between_successful_commits"
                    in r["agents"][b]
                    and r["agents"][b]
                    ["wakes_between_successful_commits"] is None
                    and r["agents"][b]["time_to_first_success"] is None
                    and r["agents"][b]["total_rejections"] == 2
                    and r["agents"][b]["changed_read_diff_sizes"] == [0],
                    {"nulls": "present, never omitted, never zero"})

    diff = lambda n: [{"region_id": f"r{i}"} for i in range(n)]
    evs53 = starvation_events([
        ("CONTRIBUTION_REJECTED", a, {"outcome": "stale", "diff": diff(0)}),
        ("CONTRIBUTION_REJECTED", a, {"outcome": "stale", "diff": diff(1)}),
        ("CONTRIBUTION_REJECTED", a, {"outcome": "stale", "diff": diff(3)}),
    ])
    starvation_case("VP-53", evs53,
                    lambda r: r["agents"][a]
                    ["changed_read_diff_sizes"] == [0, 1, 3]
                    and r["agents"][a]["changed_read_diff_unit"]
                    == "regions",
                    {"sizes": [0, 1, 3], "unit": "regions"})

    evs54 = evs50 + [{"event_seq": 99, "event_id": str(uuid.uuid4()),
                      "type": "RUN_CLOSED", "actor": SYSTEM_ACTOR,
                      "affected": [], "payload": {"summary": "x"},
                      "prev_hash": "", "hash": ""}]
    first = starvation.report_bytes(evs54)
    second = starvation.report_bytes(copy.deepcopy(evs54))
    cli = starvation_cli(evs54)
    record("VP-54", {"bytes": "identical across runs"},
           {"sha256": sha256_hex(first)},
           {"sha256": sha256_hex(cli)},
           first == second == cli, {"events": evs54},
           dual_applicable=False,
           dual_note="the starvation report is one derived-report "
                     "implementation by design (I-12, accepted "
                     "at examination); the case IS the "
                     "byte-identity property across the module "
                     "API and its standalone CLI")


# -- VP-55 and VP-29 -------------------------------------------------------

def run_binding_cases():
    store = EventStore(os.path.join(tempfile.mkdtemp(), "vp55.db"))
    blocked = False
    try:
        Engine.open_run(store, "vp55-wrong",
                        binding=stage4_binding(pack_sha256="0" * 64))
    except ValueError:
        blocked = True
    store2 = EventStore(os.path.join(tempfile.mkdtemp(), "vp55b.db"))
    engine = Engine.open_run(store2, "vp55-right",
                             binding=stage4_binding())
    opened = store2.all_events()[0]["payload"]
    pack = opened.get("validation_pack", {})
    eng_ok = blocked and pack.get("id") == PACK_ID \
        and pack.get("version") == PACK_VERSION \
        and pack.get("sha256") == PACK_SHA256
    history = store2.all_events()
    match = checker_fold(history, expected_pack_sha256=PACK_SHA256)
    mismatch = checker_fold(history, expected_pack_sha256="0" * 64)
    chk_ok = match.get("pack_binding", {}).get("matches") is True \
        and mismatch.get("pack_binding", {}).get("matches") is False \
        and mismatch.get("pack_binding", {}).get("bound_sha256") \
        == PACK_SHA256
    record("VP-55", {"opening": "blocked on wrong digest",
                     "run_opened_names": "id, version, sha256"},
           {"blocked": blocked, "bound_pack": pack},
           {"match": match.get("pack_binding"),
            "mismatch": mismatch.get("pack_binding")},
           eng_ok and chk_ok, {"history": history},
           dual_applicable=False,
           dual_note="the binding contract, not an attempt case: "
                     "the engine side is exercised at opening "
                     "(digest guard) and the checker side in fold "
                     "mode (bound-digest report); the cross-side "
                     "property — both honour the one pinned "
                     "digest — is asserted inside the case")


def main():
    run_fold_cases()
    run_eval_cases()
    run_live_cases()
    run_starvation_cases()
    run_binding_cases()
    # VP-29 — agreement across the whole pack, recomputed over
    # the full dual-applicable set (correction round, C-B4):
    # every manifest entry either declares dual_applicable and
    # has its two recorded verdict columns compared dict-for-dict
    # here, or is explicitly marked not dual-applicable with its
    # justification in the entry. An entry that is neither
    # compared nor marked fails this case — no silent exclusions.
    # The exclusions are exactly: VP-22, VP-23 (no attempt is
    # staged for a rejected contribution), VP-28 (checker-only
    # subject, I-13), VP-50..VP-54 (single derived-report
    # implementation, I-12), VP-55 (binding contract asserted
    # cross-side inside the case).
    compared = []
    excluded = []
    unmarked = []
    disagreements = []
    for entry in RESULTS:
        if entry["case"] == "VP-29":
            continue
        if entry["dual_applicable"]:
            compared.append(entry["case"])
            if entry["observed"]["engine"] \
                    != entry["observed"]["checker"]:
                disagreements.append(entry["case"])
        elif entry.get("dual_note"):
            excluded.append(entry["case"])
        else:
            unmarked.append(entry["case"])
    record("VP-29", {"disagreements": [],
                     "compared": "the full dual-applicable set",
                     "exclusions_named": excluded},
           {"disagreements": disagreements,
            "compared": compared, "excluded": excluded,
            "unmarked": unmarked},
           {"disagreements": disagreements,
            "compared": compared, "excluded": excluded,
            "unmarked": unmarked},
           not disagreements and not unmarked,
           {"cases": len(RESULTS), "compared": compared,
            "excluded": excluded},
           "" if not disagreements and not unmarked
           else f"disagreements: {disagreements} "
                f"unmarked: {unmarked}",
           dual_applicable=False,
           dual_note="VP-29 is the agreement computation itself, "
                     "not a case it compares")
    manifest_path = os.path.join(ROOT, "pack-validation-manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump({"pack": {"id": PACK_ID, "version": PACK_VERSION,
                            "sha256": PACK_SHA256},
                   "cases": RESULTS}, fh, indent=2, sort_keys=True)
    failed = [r["case"] for r in RESULTS if r["result"] != "pass"]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} cases pass; "
          f"manifest at {manifest_path}")
    if failed:
        print("FAILED:", ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
