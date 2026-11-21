#!/usr/bin/env python3
"""Closing exercise — the Annex E TV-1..TV-20 evidence package.

Fresh execution of all twenty test vectors from Annex E of the
Loom spec v0.1 Rev 9, run as part of the prototype's commissioned
closing exercise (2026-11-21), after Stage 4 acceptance. Every
vector is executed HERE, in this exercise, against the accepted
Stage 4 code — no historical counts are copied. Configurations
mirror the accepted suites: the Stage 2/3 contract vectors run on
unbound runs (the ladder and commit protocol are binding-
independent); TV-1, TV-6, TV-8, TV-13 and TV-16 run on Stage
4-bound runs, where the seal machinery the vectors exercise
exists — TV-13 and TV-16 in their genuine form (a structural
tension raised by a real failed seal attempt, never a canned
record).

Run: python3 closing_tv_tests.py — prints PASS/FAIL per check,
grouped by vector; exit status is non-zero on any failure.
"""
import copy
import os
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.engine import Engine, state_hash, verified_fold
from fabric.fixture import (COMPONENTS, CONTINUITY, INTERACTIONS,
                            OPERATIONS, PRESENTATION, STATE,
                            CONSTITUTION_HASH, SYSTEM_ACTOR)
from fabric.harness import Harness, TransportRefusal
from fabric.packpin import stage4_binding
from fabric.store import EventStore

D_CS = "00000000-0000-4000-8000-000000000102"  # Components uses State
UNKNOWN = "77777777-7777-4777-8777-777777777777"

A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
C = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
D = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
E = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"
F = "ffffffff-ffff-4fff-8fff-ffffffffffff"

failures = []
TV_RESULTS = {}


def check(tv, name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {tv}: {name}  {detail}")
    TV_RESULTS.setdefault(tv, []).append(bool(cond))
    if not cond:
        failures.append(f"{tv}: {name}")


def new_id():
    return str(uuid.uuid4())


def fresh_run(name):
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    engine = Engine.open_run(store, name)
    return store, engine, Harness(engine)


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


def report(author, exam_id, idem, regions, ref, description="Noted.",
           related=None):
    r = {"author": author, "examination_id": exam_id,
         "idempotency_id": idem, "regions": regions,
         "description": description,
         "discovery_source": "fabric_read", "discovery_ref": ref}
    if related is not None:
        r["related_tension"] = related
    return r


def t_assess(author, aid, target, position):
    return {"assessment_id": aid, "author": author,
            "target_kind": "tension", "target_id": target,
            "position": position, "reasoning": "Recorded reasoning."}


def f_assess(author, aid, target, position, version):
    return {"assessment_id": aid, "author": author,
            "target_kind": "facet", "target_id": target,
            "position": position, "reasoning": "Recorded reasoning.",
            "version_reviewed": version}


def claim_env(cid, facet, version, cited, rationale="Work is done."):
    return {"claim": {"claim_id": cid, "facet": facet,
                      "facet_version": version,
                      "supporting_contributions": cited,
                      "rationale": rationale}}


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def open_regions(h, store, token, *rids):
    seq = None
    for rid in rids:
        h.open_region(token, rid)
        seq = store.all_events()[-1]["event_seq"]
    return seq


def versions(engine, *rids):
    return {r: engine.state["regions"][r]["version"] for r in rids}


def resolve_tension(h, store, eng, tokens, tension_id, regions,
                    modifier, assessors):
    m_token = tokens[modifier]
    first = regions[0]
    seq = open_regions(h, store, m_token, first)
    current = eng.state["regions"][first]["version"]
    out = h.submit(m_token, contrib(
        modifier, new_id(), {first: current}, [first], [first],
        [{"kind": "replace_content", "region_id": first,
          "new_content": "Revised content addressing the tension."}],
        seq))
    assert out["outcome"] == "accepted", out
    for agent in assessors:
        out = h.assess(tokens[agent],
                       t_assess(agent, new_id(), tension_id, "addressed"))
        assert out["outcome"] == "recorded", out


def fault_and_raise(name):
    """The genuine TV-1 setup: drop State from the live derived
    state only; an ordinary contribution independent of State is
    accepted and its seal attempt fails S1, raising the structural
    tension. Returns (store, engine, harness, tension_id)."""
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
    raised = [e for e in events_of(store, "TENSION_RAISED")
              if e["payload"].get("type") == "structural"]
    assert len(raised) == 1, raised
    return store, eng, h, raised[0]["payload"]["tension_id"]


def repair_and_correct(store, eng, h, tension_id):
    """I-5 repair (the derived state rebuilt from verified replay)
    + the correcting contribution removing the dangling dependency
    D-CS. Returns the correcting submission's outcome dict."""
    eng.state = verified_fold(store.all_events(), CONSTITUTION_HASH)
    tok = h.issue_token(B)
    ref = open_regions(h, store, tok, COMPONENTS, STATE)
    return h.submit(tok, contrib(
        B, new_id(), versions(eng, COMPONENTS, STATE),
        [COMPONENTS, STATE], [COMPONENTS, STATE],
        [{"kind": "remove_dependency", "dependency_id": D_CS}], ref))


# =====================================================================
# TV-1 — structural lifecycle is not circular (bound, genuine)
# =====================================================================
store, eng, h, tid1 = fault_and_raise("closing-tv1")
attempts = events_of(store, "SEAL_ATTEMPTED")
raised = [e for e in events_of(store, "TENSION_RAISED")
          if e["payload"].get("type") == "structural"]
check("TV-1", "the accepted commit fires a SEAL_ATTEMPTED "
      "unconditionally; outcome fail, naming S1 and the affected "
      "dependency",
      len(attempts) == 1 and attempts[0]["payload"]["outcome"] == "fail"
      and attempts[0]["payload"]["failed_checks"] == [
          {"check": "S1", "affected": [D_CS, STATE]}]
      and "seal" not in attempts[0]["payload"])
check("TV-1", "a structural tension is raised (origin checker, "
      "status open, identity = (S1, that dependency))",
      len(raised) == 1 and raised[0]["payload"]["origin"] == "checker"
      and raised[0]["payload"]["check"] == "S1"
      and raised[0]["payload"]["affected"] == [D_CS, STATE]
      and eng.state["tensions"][tid1]["status"] == "open")
out = repair_and_correct(store, eng, h, tid1)
attempts = events_of(store, "SEAL_ATTEMPTED")
status = [e for e in events_of(store, "TENSION_STATUS")
          if e["payload"]["tension_id"] == tid1]
check("TV-1", "the correcting contribution is accepted despite "
      "the open tension; a further attempt fires, passes, and seals",
      out["outcome"] == "accepted" and len(attempts) == 2
      and attempts[-1]["payload"]["outcome"] == "pass"
      and attempts[-1]["payload"]["seal"]["position"]
      == attempts[-1]["event_seq"])
check("TV-1", "the structural tension resolves with the passing "
      "attempt's event id as its evidence",
      len(status) == 1 and status[0]["payload"]["to"] == "resolved"
      and status[0]["payload"]["evidence"]["seal_attempt_seq"]
      == attempts[-1]["event_seq"]
      and eng.state["tensions"][tid1]["status"] == "resolved")

# =====================================================================
# TV-2 — agents cannot create structural tensions (unbound)
# =====================================================================
store, eng, h = fresh_run("closing-tv2")
tok = h.issue_token(A)
seq = open_regions(h, store, tok, STATE)
n_events = len(store.all_events())
out = h.submit(tok, contrib(
    A, new_id(), {STATE: 1}, [STATE], [],
    [{"kind": "raise_tension",
      "tension": {"type": "structural", "regions": [STATE],
                  "description": "Forged."}}], seq))
check("TV-2", "raise_tension type structural is schema-invalid; "
      "exactly one CONTRIBUTION_REJECTED; no tension of any kind",
      out["outcome"] == "schema"
      and len(store.all_events()) == n_events + 1
      and events_of(store, "CONTRIBUTION_REJECTED")[-1]["payload"]
          ["outcome"] == "schema"
      and eng.state["tensions"] == {})

# =====================================================================
# TV-3 — completion evidence must bind to the facet (unbound)
# =====================================================================
store, eng, h = fresh_run("closing-tv3")
toks = {x: h.issue_token(x) for x in (A, B, E)}
seq_a = open_regions(h, store, toks[A], STATE)
h.submit(toks[A], contrib(
    A, new_id(), {STATE: 1}, [STATE], [STATE],
    [{"kind": "replace_content", "region_id": STATE,
      "new_content": "State v2."}], seq_a))
out = h.submit(toks[A], contrib(
    A, new_id(), {STATE: 2}, [STATE], [STATE],
    [{"kind": "replace_content", "region_id": STATE,
      "new_content": "State v3."}], seq_a))
c_state = out["contribution_id"]
seq_e = open_regions(h, store, toks[E], COMPONENTS)
out = h.submit(toks[E], contrib(
    E, new_id(), {COMPONENTS: 1}, [COMPONENTS], [COMPONENTS],
    [{"kind": "append_content", "region_id": COMPONENTS,
      "text": " (Extended.)"}], seq_e))
c_other = out["contribution_id"]
check("TV-3", "setup: State at version 3 via C-state; C-other "
      "touched only Components",
      eng.state["regions"][STATE]["version"] == 3)
out = h.claim_completion(toks[A], claim_env(new_id(), STATE, 3,
                                            [c_other]))
h.assess(toks[B], f_assess(B, new_id(), STATE, "examined", 3))
check("TV-3", "a claim citing only unrelated work is "
      "evidence-invalid and counts as no claim: State is "
      "unexamined, not claimed or complete",
      out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "unexamined")
out = h.claim_completion(toks[A], claim_env(new_id(), STATE, 3,
                                            [c_state]))
check("TV-3", "the binding claim, with B's assessment standing, "
      "completes State",
      out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "complete")

# =====================================================================
# TV-4 — semantic recurrence does not reopen (unbound)
# =====================================================================
store, eng, h = fresh_run("closing-tv4")
toks = {x: h.issue_token(x) for x in (A, B, C, D, E, F)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a,
                                "Stateless vs pinned sessions."))
T = out["tension_id"]
resolve_tension(h, store, eng, toks, T, [INTERACTIONS, CONTINUITY],
                B, (C, D))
n_tstatus = len([e for e in events_of(store, "TENSION_STATUS")
                 if e["payload"]["tension_id"] == T])
n_events = len(store.all_events())
seq_e = open_regions(h, store, toks[E], CONTINUITY)
out = h.submit(toks[E], contrib(
    E, new_id(), {CONTINUITY: 1}, [CONTINUITY], [CONTINUITY],
    [{"kind": "replace_content", "region_id": CONTINUITY,
      "new_content": "Sessions are pinned again."}], seq_e))
new_events = store.all_events()[n_events:]
check("TV-4", "a later contribution modifying a named region "
      "causes no transition on the resolved tension, no engine "
      "event concerning it, no new tension",
      out["outcome"] == "accepted"
      and eng.state["tensions"][T]["status"] == "resolved"
      and len([e for e in events_of(store, "TENSION_STATUS")
               if e["payload"]["tension_id"] == T]) == n_tstatus
      and not any(T in e["affected"] for e in new_events)
      and len(eng.state["tensions"]) == 1)
seq_c = open_regions(h, store, toks[C], INTERACTIONS, CONTINUITY)
out = h.examine(toks[C], report(C, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_c,
                                "The contradiction has recurred.",
                                related=T))
T2 = out.get("tension_id")
check("TV-4", "an ExaminationReport over the same set (terminal "
      "original) creates a NEW tension T2 at open, origin "
      "examination, referencing T",
      out["outcome"] == "created" and T2 is not None and T2 != T
      and eng.state["tensions"][T2]["status"] == "open"
      and eng.state["tensions"][T2]["origin"] == "examination"
      and eng.state["tensions"][T]["status"] == "resolved")

# =====================================================================
# TV-5 — clarifies examines but never resolves (unbound)
# =====================================================================
store, eng, h = fresh_run("closing-tv5")
toks = {x: h.issue_token(x) for x in (A, B, C, D, E)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
T = out["tension_id"]
seq_b = open_regions(h, store, toks[B], INTERACTIONS)
out = h.submit(toks[B], contrib(
    B, new_id(), {INTERACTIONS: 1}, [INTERACTIONS], [INTERACTIONS],
    [{"kind": "replace_content", "region_id": INTERACTIONS,
      "new_content": "Interactions, revised."}], seq_b))
aid_a = new_id()
out = h.assess(toks[C], t_assess(C, aid_a, T, "clarifies"))
ts = events_of(store, "TENSION_STATUS")
check("TV-5", "clarifies moves open -> examined, evidence = the "
      "assessment",
      out["outcome"] == "recorded"
      and eng.state["tensions"][T]["status"] == "examined"
      and ts[-1]["payload"]["to"] == "examined"
      and ts[-1]["payload"]["evidence"]["assessment_id"] == aid_a)
out = h.assess(toks[D], t_assess(D, new_id(), T, "addressed"))
out2 = h.assess(toks[E], t_assess(E, new_id(), T, "clarifies"))
check("TV-5", "one addressed + a further clarifies never "
      "resolves: the tension remains examined",
      out["outcome"] == "recorded" and out2["outcome"] == "recorded"
      and eng.state["tensions"][T]["status"] == "examined")

# =====================================================================
# TV-6 — one inconsistency, one tension (bound, genuine)
# =====================================================================
store, eng, h, tid6 = fault_and_raise("closing-tv6")
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
check("TV-6", "both further attempts fail on the same check and "
      "affected set",
      len(attempts) == 3
      and all(a["payload"]["outcome"] == "fail"
              and a["payload"]["failed_checks"] == [
                  {"check": "S1", "affected": [D_CS, STATE]}]
              for a in attempts[1:]))
check("TV-6", "exactly one structural tension with that identity "
      "exists throughout; no duplicate TENSION_RAISED; the later "
      "attempts record their findings against the standing tension",
      len([e for e in events_of(store, "TENSION_RAISED")
           if e["payload"].get("type") == "structural"]) == 1
      and eng.state["tensions"][tid6]["status"] == "open"
      and all(a["payload"].get("findings_attached") == [tid6]
              for a in attempts[1:]))

# =====================================================================
# TV-7 — idempotency: identical returns, different conflicts
# =====================================================================
store, eng, h = fresh_run("closing-tv7")
tok = h.issue_token(E)
seq_e = open_regions(h, store, tok, PRESENTATION)
K = "70707070-7070-4070-8070-707070707070"
x = contrib(E, K, {PRESENTATION: 1}, [PRESENTATION], [PRESENTATION],
            [{"kind": "append_content", "region_id": PRESENTATION,
              "text": " (Extended.)"}], seq_e)
out = h.submit(tok, x)
n_events = len(store.all_events())
out2 = h.submit(tok, copy.deepcopy(x))
check("TV-7", "(i) an identical resubmission under K returns the "
      "original outcome and appends no event",
      out["outcome"] == "accepted"
      and out2["outcome"] == "accepted"
      and out2.get("idempotent_replay") is True
      and len(store.all_events()) == n_events)
y = contrib(E, K, {PRESENTATION: 1}, [PRESENTATION], [PRESENTATION],
            [{"kind": "append_content", "region_id": PRESENTATION,
              "text": " (Different.)"}], seq_e)
out = h.submit(tok, y)
check("TV-7", "(ii) different content under K is rejected "
      "idempotency_conflict; Y is not applied",
      out["outcome"] == "idempotency_conflict"
      and eng.state["regions"][PRESENTATION]["version"] == 2
      and "Different" not in eng.state["regions"][PRESENTATION]
          ["content"])

# =====================================================================
# TV-8 — stood-down follows the declared regions, exactly (bound)
# =====================================================================
store, eng, h = bound_run("closing-tv8")
toks = {x: h.issue_token(x) for x in (A, B, C, D)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
t_in = out["tension_id"]
h.assess(toks[B], t_assess(B, new_id(), t_in, "remains"))
out = h.assess(toks[C], t_assess(C, new_id(), t_in, "remains"))
check("TV-8", "the {Interactions, Continuity} tension stands; "
      "both required facets become stood_down; Components and "
      "State are unaffected",
      out["outcome"] == "recorded"
      and eng.state["tensions"][t_in]["status"] == "standing"
      and eng.state["facet_status"].get(INTERACTIONS) == "stood_down"
      and eng.state["facet_status"].get(CONTINUITY) == "stood_down"
      and COMPONENTS not in eng.state["facet_status"]
      and STATE not in eng.state["facet_status"])
seq_d = open_regions(h, store, toks[D], PRESENTATION)
out = h.examine(toks[D], report(D, new_id(), new_id(),
                                [PRESENTATION], seq_d))
t_p = out["tension_id"]
h.assess(toks[B], t_assess(B, new_id(), t_p, "remains"))
out = h.assess(toks[C], t_assess(C, new_id(), t_p, "remains"))
check("TV-8", "the {Presentation} tension stands but stands down "
      "no required facet (Presentation is optional)",
      out["outcome"] == "recorded"
      and eng.state["tensions"][t_p]["status"] == "standing"
      and eng.state["facet_status"].get(PRESENTATION) is None
      and eng.state["facet_status"].get(INTERACTIONS) == "stood_down")

# =====================================================================
# TV-9 / TV-10 — cross-kind positions; version-field discipline
# =====================================================================
store, eng, h = fresh_run("closing-tv9-10")
toks = {x: h.issue_token(x) for x in (A, B)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
T = out["tension_id"]
out = h.assess(toks[A], {"assessment_id": new_id(), "author": A,
                         "target_kind": "facet", "target_id": STATE,
                         "position": "addressed",
                         "reasoning": "Wrong kind of position.",
                         "version_reviewed": 1})
check("TV-9", "(i) a facet target with position addressed is "
      "schema-invalid; not recorded",
      out["outcome"] == "rejected"
      and out["reason"] == "schema_invalid"
      and eng.state["assessments"] == {})
out = h.assess(toks[A], {"assessment_id": new_id(), "author": A,
                         "target_kind": "tension", "target_id": T,
                         "position": "examined",
                         "reasoning": "Wrong kind of position."})
check("TV-9", "(ii) a tension target with position examined is "
      "schema-invalid; not recorded",
      out["outcome"] == "rejected"
      and out["reason"] == "schema_invalid"
      and eng.state["assessments"] == {})
out = h.assess(toks[A], {"assessment_id": new_id(), "author": A,
                         "target_kind": "facet", "target_id": STATE,
                         "position": "examined",
                         "reasoning": "Missing the version field."})
check("TV-10", "(i) a FacetAssessment omitting version_reviewed "
      "is schema-invalid; not recorded",
      out["outcome"] == "rejected"
      and out["reason"] == "schema_invalid"
      and eng.state["assessments"] == {})
bad = t_assess(A, new_id(), T, "clarifies")
bad["version_reviewed"] = 1
out = h.assess(toks[A], bad)
check("TV-10", "(ii) a TensionAssessment carrying version_reviewed "
      "is schema-invalid; not recorded",
      out["outcome"] == "rejected"
      and out["reason"] == "schema_invalid"
      and eng.state["assessments"] == {})
out = h.assess(toks[A], f_assess(A, new_id(), T, "examined", 1))
check("TV-10", "(iii) a FacetAssessment whose target resolves to "
      "a Tension is invalid at target resolution; not recorded",
      out["outcome"] == "rejected" and eng.state["assessments"] == {})
out = h.assess(toks[A], t_assess(A, new_id(), STATE, "clarifies"))
check("TV-10", "(iii) a TensionAssessment whose target resolves "
      "to a Region is invalid at target resolution; not recorded",
      out["outcome"] == "rejected" and eng.state["assessments"] == {})

# =====================================================================
# TV-11 — a stale facet assessment is history, not currency
# =====================================================================
store, eng, h = fresh_run("closing-tv11")
toks = {x: h.issue_token(x) for x in (A, B)}
seq_a = open_regions(h, store, toks[A], STATE)
c_last = None
for v in (1, 2, 3, 4):
    out = h.submit(toks[A], contrib(
        A, new_id(), {STATE: v}, [STATE], [STATE],
        [{"kind": "replace_content", "region_id": STATE,
          "new_content": f"State v{v + 1}."}], seq_a))
    c_last = out["contribution_id"]
out = h.claim_completion(toks[A], claim_env(new_id(), STATE, 5,
                                            [c_last]))
check("TV-11", "setup: State at version 5; an evidence-valid "
      "claim stands at version 5",
      eng.state["regions"][STATE]["version"] == 5
      and out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "claimed")
out = h.assess(toks[B], f_assess(B, new_id(), STATE, "examined", 3))
check("TV-11", "a review of version 3 is valid and recorded — "
      "and State does NOT become complete on its basis",
      out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "claimed")
out = h.assess(toks[B], f_assess(B, new_id(), STATE, "examined", 5))
check("TV-11", "a review at the current version completes the "
      "facet (claim + independent current-version review)",
      out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "complete")

# =====================================================================
# TV-12 — the examination action: creation, read-record binding,
# duplicates, recurrence (unbound)
# =====================================================================
store, eng, h = fresh_run("closing-tv12")
toks = {x: h.issue_token(x) for x in (A, B, C, D, E, F)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
exam_id = new_id()
out = h.examine(toks[A], report(A, exam_id, new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
T = out.get("tension_id")
rec = events_of(store, "EXAMINATION_RECORDED")[-1]
raised = events_of(store, "TENSION_RAISED")[-1]
check("TV-12", "(i) a first examination creates a tension: "
      "EXAMINATION_RECORDED outcome created, followed by "
      "TENSION_RAISED (origin examination, origin_ref = the "
      "examination id), T at open",
      out["outcome"] == "created" and T is not None
      and raised["event_seq"] == rec["event_seq"] + 1
      and eng.state["tensions"][T]["status"] == "open"
      and eng.state["tensions"][T]["origin"] == "examination"
      and eng.state["tensions"][T]["origin_ref"] == exam_id)
seq_b = open_regions(h, store, toks[B], COMPONENTS)
out = h.examine(toks[B], report(B, new_id(), new_id(),
                                [INTERACTIONS], seq_b))
check("TV-12", "(ii) examining a region outside the filer's read "
      "record is rejected; no tension is created",
      out["outcome"] == "rejected"
      and out["reason"] == "region_not_in_read_record"
      and len(eng.state["tensions"]) == 1)
seq_c = open_regions(h, store, toks[C], INTERACTIONS, CONTINUITY)
out = h.examine(toks[C], report(C, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_c))
check("TV-12", "(iii) an identical live set is noted_existing, "
      "referencing T; no second tension exists",
      out["outcome"] == "noted_existing"
      and out["matched_tensions"] == [T]
      and len(eng.state["tensions"]) == 1)
resolve_tension(h, store, eng, toks, T, [INTERACTIONS, CONTINUITY],
                D, (E, F))
out = h.examine(toks[C], report(C, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_c,
                                "It has recurred.", related=T))
T2 = out.get("tension_id")
check("TV-12", "(iv) after T reaches resolved, the same set "
      "creates anew: T2 at open, distinct from T",
      out["outcome"] == "created" and T2 is not None and T2 != T
      and eng.state["tensions"][T2]["status"] == "open"
      and eng.state["tensions"][T]["status"] == "resolved")

# =====================================================================
# TV-13 — a schema-valid assessment cannot enter the structural
# lifecycle (bound, genuine, BOTH halves in one case)
# =====================================================================
store, eng, h, tid13 = fault_and_raise("closing-tv13")
tok = h.issue_token(B)
out = h.assess(tok, t_assess(B, new_id(), tid13, "addressed"))
recorded = events_of(store, "ASSESSMENT_RECORDED")
check("TV-13", "exactly one ASSESSMENT_RECORDED, outcome "
      "rejected, reason structural_target; no assessment record; "
      "no TENSION_STATUS for S; S remains open",
      out["outcome"] == "rejected"
      and out.get("reason") == "structural_target"
      and len(recorded) == 1
      and recorded[0]["payload"]["outcome"] == "rejected"
      and eng.state["assessments"] == {}
      and [e for e in events_of(store, "TENSION_STATUS")
           if e["payload"]["tension_id"] == tid13] == []
      and eng.state["tensions"][tid13]["status"] == "open")
out = repair_and_correct(store, eng, h, tid13)
attempts = events_of(store, "SEAL_ATTEMPTED")
status = [e for e in events_of(store, "TENSION_STATUS")
          if e["payload"]["tension_id"] == tid13]
check("TV-13", "the correcting contribution's passing attempt "
      "resolves S with that attempt as its evidence — the "
      "attempted assessment plays no part",
      out["outcome"] == "accepted"
      and attempts[-1]["payload"]["outcome"] == "pass"
      and len(status) == 1
      and status[0]["payload"]["to"] == "resolved"
      and status[0]["payload"]["evidence"]["seal_attempt_seq"]
      == attempts[-1]["event_seq"])

# =====================================================================
# TV-14 — multi-match noted_existing (unbound)
# =====================================================================
store, eng, h = fresh_run("closing-tv14")
toks = {x: h.issue_token(x) for x in (A, B, C)}
for agent in (A, B):
    seq = open_regions(h, store, toks[agent], INTERACTIONS, CONTINUITY)
    out = h.submit(toks[agent], contrib(
        agent, new_id(), {INTERACTIONS: 1, CONTINUITY: 1},
        [INTERACTIONS, CONTINUITY], [],
        [{"kind": "raise_tension",
          "tension": {"type": "semantic",
                      "regions": [INTERACTIONS, CONTINUITY],
                      "description": "Stateless vs pinned."}}], seq))
    assert out["outcome"] == "accepted", out
raised_ids = [e["payload"]["tension_id"]
              for e in events_of(store, "TENSION_RAISED")]
seq_c = open_regions(h, store, toks[C], INTERACTIONS, CONTINUITY)
out = h.examine(toks[C], report(C, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_c))
check("TV-14", "one EXAMINATION_RECORDED, outcome noted_existing, "
      "matched_tensions = [T1, T2] (both, deterministically); no "
      "third tension; neither tension changes status",
      len(raised_ids) == 2
      and out["outcome"] == "noted_existing"
      and out["matched_tensions"] == raised_ids
      and len(eng.state["tensions"]) == 2
      and events_of(store, "TENSION_STATUS") == [])

# =====================================================================
# TV-15 — exactly one event: the idempotency and malformed edges
# =====================================================================
store, eng, h = fresh_run("closing-tv15")
toks = {x: h.issue_token(x) for x in (A,)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
K = new_id()
R = report(A, new_id(), K, [INTERACTIONS, CONTINUITY], seq_a)
out = h.examine(toks[A], R)
n_events = len(store.all_events())
out2 = h.examine(toks[A], copy.deepcopy(R))
check("TV-15", "(i) an identical resubmission under K returns the "
      "original outcome; no new EXAMINATION_RECORDED is appended; "
      "the event count for R remains exactly one",
      out["outcome"] == "created"
      and out2["outcome"] == "created"
      and out2.get("idempotent_replay") is True
      and out2["tension_id"] == out["tension_id"]
      and len(store.all_events()) == n_events
      and len(events_of(store, "EXAMINATION_RECORDED")) == 1)
bad = {"author": A, "examination_id": new_id(),
       "idempotency_id": new_id(), "description": "Missing regions.",
       "discovery_source": "fabric_read", "discovery_ref": seq_a}
out = h.examine(toks[A], bad)
rec = events_of(store, "EXAMINATION_RECORDED")
check("TV-15", "(ii) an object omitting regions is recorded "
      "exactly once, rejected schema_invalid, the raw submission "
      "preserved in the payload; no tension is created",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid"
      and len(rec) == 2 and rec[-1]["payload"]["report"] == bad
      and len(eng.state["tensions"]) == 1)
n_events = len(store.all_events())
n_log = len(h.log)
try:
    h.examine(toks[A], ["not", "a", "json", "object"])
    check("TV-15", "(iii) a non-object submission is refused at "
          "the interface as a transport error", False)
except TransportRefusal:
    check("TV-15", "(iii) a non-object submission is refused at "
          "the interface as a transport error; no event is "
          "appended; the refusal appears only in the harness log",
          len(store.all_events()) == n_events
          and len(h.log) == n_log + 1
          and h.log[-1]["kind"] == "transport_refusal")

# =====================================================================
# TV-16 — validation precedence, Assessment (bound, genuine
# structural tension): identity_mismatch (step 1) precedes
# structural_target (step 5)
# =====================================================================
store, eng, h, tid16 = fault_and_raise("closing-tv16")
tok = h.issue_token(B)
# B's token, but the document claims author A — and its target is
# the open structural tension: both failures apply at once.
out = h.assess(tok, t_assess(A, new_id(), tid16, "addressed"))
recorded = events_of(store, "ASSESSMENT_RECORDED")
check("TV-16", "exactly one ASSESSMENT_RECORDED, rejected with "
      "reason identity_mismatch; the structural-target check is "
      "never evaluated; no assessment record; the tension is "
      "untouched",
      out["outcome"] == "rejected"
      and out["reason"] == "identity_mismatch"
      and len(recorded) == 1
      and recorded[0]["payload"]["reason"] == "identity_mismatch"
      and eng.state["assessments"] == {}
      and eng.state["tensions"][tid16]["status"] == "open")

# =====================================================================
# TV-17 — validation precedence, ExaminationReport (unbound):
# unknown_region (step 4) precedes discovery_unverifiable (step 6)
# =====================================================================
store, eng, h = fresh_run("closing-tv17")
toks = {x: h.issue_token(x) for x in (B,)}
seq_b = open_regions(h, store, toks[B], COMPONENTS)
out = h.examine(toks[B], report(B, new_id(), new_id(),
                                [INTERACTIONS, UNKNOWN], 9999))
rec = events_of(store, "EXAMINATION_RECORDED")
check("TV-17", "exactly one EXAMINATION_RECORDED, rejected with "
      "reason unknown_region; discovery validation is never "
      "reached; no tension is created",
      out["outcome"] == "rejected" and out["reason"] == "unknown_region"
      and len(rec) == 1 and eng.state["tensions"] == {})

# =====================================================================
# TV-18 — the malformed-key edge (ladder step 2) (unbound)
# =====================================================================
store, eng, h = fresh_run("closing-tv18")
toks = {x: h.issue_token(x) for x in (A,)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS)
no_key = {"author": A, "examination_id": new_id(),
          "regions": [INTERACTIONS], "description": "No key.",
          "discovery_source": "fabric_read", "discovery_ref": seq_a}
out = h.examine(toks[A], no_key)
check("TV-18", "(i) an ExaminationReport omitting idempotency_id "
      "proceeds to Schema and is rejected schema_invalid — not an "
      "idempotency outcome of any kind",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid"
      and out.get("idempotent_replay") is not True)
out = h.assess(toks[A], {"assessment_id": "not-a-uuid", "author": A,
                         "target_kind": "facet", "target_id": STATE,
                         "position": "examined",
                         "reasoning": "Malformed key.",
                         "version_reviewed": 1})
check("TV-18", "(ii) an Assessment whose assessment_id is "
      "malformed takes the same path: schema_invalid at step 3",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid")

# =====================================================================
# TV-19 — record-identity collision, ExaminationReport (unbound)
# =====================================================================
store, eng, h = fresh_run("closing-tv19")
toks = {x: h.issue_token(x) for x in (A, B)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
X, K = new_id(), new_id()
out = h.examine(toks[A], report(A, X, K, [INTERACTIONS, CONTINUITY],
                                seq_a))
T = out["tension_id"]
seq_b = open_regions(h, store, toks[B], INTERACTIONS, CONTINUITY)
out = h.examine(toks[B], report(B, X, new_id(),
                                [INTERACTIONS, CONTINUITY], seq_b,
                                "A different report, the same id."))
check("TV-19", "another author's reuse of examination_id X is "
      "rejected identity_collision; no second record claims X; "
      "A's report and its tension are untouched",
      out["outcome"] == "rejected"
      and out["reason"] == "identity_collision"
      and len(eng.state["tensions"]) == 1
      and eng.state["tensions"][T]["status"] == "open")
out = h.examine(toks[A], report(A, X, new_id(), [INTERACTIONS],
                                seq_a, "My own id, fresh key."))
check("TV-19", "the identity's own author, reusing X under a "
      "fresh key, is bound by the collision rule exactly the same",
      out["outcome"] == "rejected"
      and out["reason"] == "identity_collision")

# =====================================================================
# TV-20 — record-identity collision, Assessment, vs id_conflict
# =====================================================================
store, eng, h = fresh_run("closing-tv20")
toks = {x: h.issue_token(x) for x in (A, B)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
T = out["tension_id"]
S = new_id()
out = h.assess(toks[A], t_assess(A, S, T, "clarifies"))
out = h.assess(toks[B], t_assess(B, S, T, "remains"))
check("TV-20", "(i) another author's reuse of assessment_id S is "
      "rejected identity_collision — assessment_id is globally "
      "unique",
      out["outcome"] == "rejected"
      and out["reason"] == "identity_collision")
out = h.assess(toks[A], t_assess(A, S, T, "addressed"))
check("TV-20", "(ii) the author's own reuse of S with different "
      "content is rejected id_conflict — the two reasons never "
      "compete for the same case; the original record stands",
      out["outcome"] == "rejected" and out["reason"] == "id_conflict"
      and eng.state["assessments"][S]["position"] == "clarifies")

# =====================================================================
print()
all_tv = [f"TV-{i}" for i in range(1, 21)]
missing = [t for t in all_tv if t not in TV_RESULTS]
for t in all_tv:
    res = TV_RESULTS.get(t, [])
    print(f"{t}: {sum(res)}/{len(res)} checks pass"
          if res else f"{t}: NOT EXECUTED")
if missing:
    print("NOT EXECUTED:", ", ".join(missing))
    failures.append("missing vectors: " + ", ".join(missing))
if failures:
    print(f"\n{len(failures)} FAILURES: {failures}")
    sys.exit(1)
print(f"\nclosing_tv_tests: all {sum(len(v) for v in TV_RESULTS.values())} "
      f"checks passed across TV-1..TV-20")
