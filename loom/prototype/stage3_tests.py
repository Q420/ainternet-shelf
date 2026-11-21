"""Stage 3 tests: the noticing and judgment half of the fabric —
examination reports, assessments, completion claims — built to the
settled Stage 3 design brief Rev 3, with Annex E vectors TV-3, TV-4,
TV-5, TV-9 .. TV-20 implemented as named, executable tests.

TV-13 is implemented for its Stage-3 half only: the vector's setup
(a structural tension raised by a failed seal attempt) belongs to
Stage 4's seal machinery (TV-1), which does not exist yet. The
structural tension record is therefore stood up as a canned history
(the examiner-side device Annex E itself uses for the checker pack:
a TENSION_RAISED event with origin "checker", committed by the
driver through the engine's append path — never through an agent
operation), and the Stage-3 behaviour the vector pins (the
structural_target rejection path) is asserted against it. The
vector's second half — a passing seal attempt resolving the
tension — is DEFERRED to Stage 4 and printed as such; it is not
counted as a pass.

Run: python3 stage3_tests.py
"""
import copy
import os
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fabric.engine import Engine, state_hash, verify_chain
from fabric.fixture import (COMPONENTS, CONTINUITY, INTERACTIONS,
                            OPERATIONS, PRESENTATION, STATE,
                            CONSTITUTION_HASH, SYSTEM_ACTOR)
from fabric.harness import Harness, TransportRefusal
from fabric.store import EventStore

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        failures.append(name)


def new_id():
    return str(uuid.uuid4())


def fresh_run(name):
    store = EventStore(os.path.join(tempfile.mkdtemp(), name + ".db"))
    engine = Engine.open_run(store, name)
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
         "description": description, "discovery_source": "fabric_read",
         "discovery_ref": ref}
    if related is not None:
        r["related_tension"] = related
    return r


def t_assess(author, aid, target, position, supersedes=None):
    a = {"assessment_id": aid, "author": author,
         "target_kind": "tension", "target_id": target,
         "position": position, "reasoning": "Recorded reasoning."}
    if supersedes is not None:
        a["supersedes"] = supersedes
    return a


def f_assess(author, aid, target, position, version, supersedes=None):
    a = {"assessment_id": aid, "author": author,
         "target_kind": "facet", "target_id": target,
         "position": position, "reasoning": "Recorded reasoning.",
         "version_reviewed": version}
    if supersedes is not None:
        a["supersedes"] = supersedes
    return a


def claim_env(cid, facet, version, cited, rationale="Work is done."):
    return {"claim": {"claim_id": cid, "facet": facet,
                      "facet_version": version,
                      "supporting_contributions": cited,
                      "rationale": rationale}}


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def last_seq(store):
    return store.all_events()[-1]["event_seq"]


def open_regions(h, store, token, *rids):
    """Open regions for an agent; return the last DISCOVERY seq."""
    seq = None
    for rid in rids:
        h.open_region(token, rid)
        seq = last_seq(store)
    return seq


def resolve_tension(h, store, eng, tokens, tension_id, regions,
                    modifier, assessors):
    """Drive a semantic tension to resolved under section 4's
    protocol: the modifier (who has read only the first region)
    modifies its content; two distinct non-author assessors then
    record addressed. Returns (modifying_contribution_id, [ids])."""
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
    ids = []
    for agent in assessors:
        aid = new_id()
        out = h.assess(tokens[agent],
                       t_assess(agent, aid, tension_id, "addressed"))
        assert out["outcome"] == "recorded", out
        ids.append(aid)
    return out, ids


A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
C = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
D = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
E = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"
F = "ffffffff-ffff-4fff-8fff-ffffffffffff"
G = "12121212-1212-4121-8121-121212121212"
H = "34343434-3434-4343-8343-343434343434"
UNKNOWN = "77777777-7777-4777-8777-777777777777"

# =====================================================================
# TV-3 — completion evidence must bind to the facet (plus the PIN:
# condition (1), a cited contribution must be ACCEPTED; condition
# (3), the version the latest cited contribution left)
# =====================================================================
store, eng, h = fresh_run("stage3-tv3")
toks = {x: h.issue_token(x) for x in (A, B, E, F, G)}

seq_a = open_regions(h, store, toks[A], STATE)
out = h.submit(toks[A], contrib(
    A, new_id(), {STATE: 1}, [STATE], [STATE],
    [{"kind": "replace_content", "region_id": STATE,
      "new_content": "State v2."}], seq_a))
c_state_1 = out["contribution_id"]
out = h.submit(toks[A], contrib(
    A, new_id(), {STATE: 2}, [STATE], [STATE],
    [{"kind": "replace_content", "region_id": STATE,
      "new_content": "State v3."}], seq_a))
c_state = out["contribution_id"]  # the contribution that left State at v3
check("TV-3 setup: State advanced to version 3",
      eng.state["regions"][STATE]["version"] == 3)

seq_e = open_regions(h, store, toks[E], COMPONENTS)
out = h.submit(toks[E], contrib(
    E, new_id(), {COMPONENTS: 1}, [COMPONENTS], [COMPONENTS],
    [{"kind": "append_content", "region_id": COMPONENTS,
      "text": " (Extended.)"}], seq_e))
c_other = out["contribution_id"]

# PIN condition (1) setup: a REJECTED contribution, citable by id.
seq_g = open_regions(h, store, toks[G], PRESENTATION)
out = h.submit(toks[G], contrib(
    G, new_id(), {PRESENTATION: 1}, [PRESENTATION], [PRESENTATION],
    [{"kind": "append_content", "region_id": PRESENTATION,
      "text": " (G's work.)"}], seq_g))
seq_f = open_regions(h, store, toks[F], PRESENTATION)
out = h.submit(toks[F], contrib(
    F, new_id(), {PRESENTATION: 1}, [PRESENTATION], [PRESENTATION],
    [{"kind": "append_content", "region_id": PRESENTATION,
      "text": " (F's overtaken work.)"}], seq_f))
rej = events_of(store, "CONTRIBUTION_REJECTED")[-1]
c_rejected = rej["payload"].get("contribution_id")
check("PIN setup: a rejected contribution carries a citable id",
      out["outcome"] == "stale" and isinstance(c_rejected, str))

# The claim citing only the rejected contribution: RECORDED (the
# citation resolves — the contribution is on record), and counts
# as no claim, because condition (1) requires ACCEPTED.
n_claimed = len(events_of(store, "COMPLETION_CLAIMED"))
out = h.claim_completion(toks[A], claim_env(
    new_id(), PRESENTATION, 2, [c_rejected]))
check("PIN (1): a claim citing a REJECTED contribution is recorded "
      "and counts as no claim",
      out["outcome"] == "recorded"
      and len(events_of(store, "COMPLETION_CLAIMED")) == n_claimed + 1
      and events_of(store, "COMPLETION_CLAIMED")[-1]["payload"]
          ["outcome"] == "recorded"
      and eng.state["facet_status"].get(PRESENTATION) == "unexamined")

# TV-3 proper: A's claim for State citing only C-other (accepted,
# but it never touched State) is recorded and counts as no claim.
out = h.claim_completion(toks[A], claim_env(
    new_id(), STATE, 3, [c_other]))
check("TV-3: claim citing only unrelated work is recorded",
      out["outcome"] == "recorded")
out = h.assess(toks[B], f_assess(B, new_id(), STATE, "examined", 3))
check("TV-3: B's current-version review is recorded",
      out["outcome"] == "recorded")
check("TV-3: State is unexamined, not claimed or complete",
      eng.state["facet_status"].get(STATE) == "unexamined")

# PIN condition (3): citing the right contribution at the wrong
# version — C-state left State at 3, not 2 — counts as no claim.
out = h.claim_completion(toks[A], claim_env(
    new_id(), STATE, 2, [c_state]))
check("PIN (3): a claim at a version the cited work did not leave "
      "counts as no claim",
      out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "unexamined")

# Then: A claims citing C-state at facet_version 3 — evidence-valid;
# with B's review standing, State becomes complete.
out = h.claim_completion(toks[A], claim_env(
    new_id(), STATE, 3, [c_state]))
fs = [e for e in events_of(store, "FACET_STATUS")
      if e["payload"]["region_id"] == STATE]
check("TV-3: the binding claim completes State (claim + review)",
      out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "complete"
      and fs[-1]["payload"]["to"] == "complete")
check("TV-3: replay reproduces claims, assessments, facet state",
      state_hash(eng.replay()) == state_hash(eng.state))

# =====================================================================
# TV-4 — semantic recurrence does not reopen
# =====================================================================
store, eng, h = fresh_run("stage3-tv4")
toks = {x: h.issue_token(x) for x in (A, B, C, D, E, F)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a,
                                "Stateless vs pinned sessions."))
T = out["tension_id"]
resolve_tension(h, store, eng, toks, T, [INTERACTIONS, CONTINUITY],
                B, (C, D))
check("TV-4 setup: the tension reached resolved",
      eng.state["tensions"][T]["status"] == "resolved")
n_tstatus = len([e for e in events_of(store, "TENSION_STATUS")
                 if e["payload"]["tension_id"] == T])
n_events = len(store.all_events())

seq_e = open_regions(h, store, toks[E], CONTINUITY)
out = h.submit(toks[E], contrib(
    E, new_id(), {CONTINUITY: 1}, [CONTINUITY], [CONTINUITY],
    [{"kind": "replace_content", "region_id": CONTINUITY,
      "new_content": "Sessions are pinned again."}], seq_e))
new_events = store.all_events()[n_events:]
check("TV-4: a later contribution does not reopen or touch T",
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
check("TV-4: recurrence creates a NEW tension via examination",
      out["outcome"] == "created" and T2 is not None and T2 != T
      and eng.state["tensions"][T2]["status"] == "open"
      and eng.state["tensions"][T2]["origin"] == "examination"
      and eng.state["tensions"][T]["status"] == "resolved")

# =====================================================================
# TV-5 — clarifies examines but never resolves
# =====================================================================
store, eng, h = fresh_run("stage3-tv5")
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
check("TV-5 setup: a post-raise modification is on record",
      out["outcome"] == "accepted")

aid_a = new_id()
out = h.assess(toks[C], t_assess(C, aid_a, T, "clarifies"))
ts = events_of(store, "TENSION_STATUS")
check("TV-5: clarifies moves open -> examined, evidence = assessment",
      out["outcome"] == "recorded"
      and eng.state["tensions"][T]["status"] == "examined"
      and ts[-1]["payload"]["to"] == "examined"
      and ts[-1]["payload"]["evidence"]["assessment_id"] == aid_a)
out = h.assess(toks[D], t_assess(D, new_id(), T, "addressed"))
out2 = h.assess(toks[E], t_assess(E, new_id(), T, "clarifies"))
check("TV-5: one addressed + clarifies never resolves",
      out["outcome"] == "recorded" and out2["outcome"] == "recorded"
      and eng.state["tensions"][T]["status"] == "examined")

# =====================================================================
# TV-9 / TV-10 — cross-kind positions and version-field discipline
# =====================================================================
store, eng, h = fresh_run("stage3-tv9-10")
toks = {x: h.issue_token(x) for x in (A, B)}
out = h.assess(toks[A], {"assessment_id": new_id(), "author": A,
                         "target_kind": "facet", "target_id": STATE,
                         "position": "addressed",
                         "reasoning": "Wrong kind of position.",
                         "version_reviewed": 1})
ev = events_of(store, "ASSESSMENT_RECORDED")[-1]
check("TV-9(i): a facet target with position addressed is "
      "schema-invalid",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid"
      and ev["payload"]["outcome"] == "rejected"
      and eng.state["assessments"] == {})
out = h.assess(toks[A], {"assessment_id": new_id(), "author": A,
                         "target_kind": "tension",
                         "target_id": new_id(),
                         "position": "examined",
                         "reasoning": "Wrong kind of position."})
check("TV-9(ii): a tension target with position examined is "
      "schema-invalid",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid"
      and eng.state["assessments"] == {})

out = h.assess(toks[A], {"assessment_id": new_id(), "author": A,
                         "target_kind": "facet", "target_id": STATE,
                         "position": "examined",
                         "reasoning": "Missing version_reviewed."})
check("TV-10(i): a FacetAssessment omitting version_reviewed is "
      "schema-invalid",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid")
out = h.assess(toks[A], {"assessment_id": new_id(), "author": A,
                         "target_kind": "tension",
                         "target_id": new_id(), "position": "remains",
                         "reasoning": "Carrying a forbidden field.",
                         "version_reviewed": 1})
check("TV-10(ii): a TensionAssessment carrying version_reviewed is "
      "schema-invalid",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid")

seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
T = out["tension_id"]
out = h.assess(toks[B], f_assess(B, new_id(), T, "examined", 1))
check("TV-10(iii): a FacetAssessment targeting a Tension is "
      "target_unresolved",
      out["outcome"] == "rejected"
      and out["reason"] == "target_unresolved")
out = h.assess(toks[B], t_assess(B, new_id(), STATE, "addressed"))
check("TV-10(iii): a TensionAssessment targeting a Region is "
      "target_unresolved",
      out["outcome"] == "rejected"
      and out["reason"] == "target_unresolved")

# =====================================================================
# TV-11 — a stale facet assessment is history, not currency
# =====================================================================
store, eng, h = fresh_run("stage3-tv11")
toks = {x: h.issue_token(x) for x in (A, B)}
seq_a = open_regions(h, store, toks[A], STATE)
c_last = None
for v in (1, 2, 3, 4):
    out = h.submit(toks[A], contrib(
        A, new_id(), {STATE: v}, [STATE], [STATE],
        [{"kind": "replace_content", "region_id": STATE,
          "new_content": f"State v{v + 1}."}], seq_a))
    c_last = out["contribution_id"]
check("TV-11 setup: State stands at version 5",
      eng.state["regions"][STATE]["version"] == 5)
out = h.claim_completion(toks[A], claim_env(new_id(), STATE, 5,
                                            [c_last]))
check("TV-11: an evidence-valid claim stands at version 5",
      out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "claimed")
out = h.assess(toks[B], f_assess(B, new_id(), STATE, "examined", 3))
check("TV-11: a review of version 3 is valid history, not currency",
      out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "claimed")
out = h.assess(toks[B], f_assess(B, new_id(), STATE, "examined", 5))
check("TV-11: a review at the current version completes the facet",
      out["outcome"] == "recorded"
      and eng.state["facet_status"].get(STATE) == "complete")
check("TV-11: replay reproduces the facet accounting",
      state_hash(eng.replay()) == state_hash(eng.state))

# =====================================================================
# TV-12 — the examination action: creation, read-record binding,
# duplicates, recurrence
# =====================================================================
store, eng, h = fresh_run("stage3-tv12")
toks = {x: h.issue_token(x) for x in (A, B, C, D, E, F)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
exam_id = new_id()
out = h.examine(toks[A], report(A, exam_id, new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
T = out.get("tension_id")
evs = store.all_events()
rec = events_of(store, "EXAMINATION_RECORDED")[-1]
raised = events_of(store, "TENSION_RAISED")[-1]
check("TV-12(i): a first examination creates a tension",
      out["outcome"] == "created" and T is not None
      and raised["event_seq"] == rec["event_seq"] + 1
      and eng.state["tensions"][T]["status"] == "open"
      and eng.state["tensions"][T]["origin"] == "examination"
      and eng.state["tensions"][T]["origin_ref"] == exam_id
      and rec["payload"]["read_versions"]
          == {INTERACTIONS: 1, CONTINUITY: 1})

seq_b = open_regions(h, store, toks[B], COMPONENTS)
out = h.examine(toks[B], report(B, new_id(), new_id(),
                                [INTERACTIONS], seq_b))
check("TV-12(ii): examining an unopened region is rejected",
      out["outcome"] == "rejected"
      and out["reason"] == "region_not_in_read_record"
      and len(eng.state["tensions"]) == 1)

seq_c = open_regions(h, store, toks[C], INTERACTIONS, CONTINUITY)
out = h.examine(toks[C], report(C, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_c))
check("TV-12(iii): an identical live set is noted_existing",
      out["outcome"] == "noted_existing"
      and out["matched_tensions"] == [T]
      and len(eng.state["tensions"]) == 1)

resolve_tension(h, store, eng, toks, T, [INTERACTIONS, CONTINUITY],
                D, (E, F))
out = h.examine(toks[C], report(C, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_c,
                                "It has recurred.", related=T))
T2 = out.get("tension_id")
check("TV-12(iv): after resolution, the same set creates anew",
      out["outcome"] == "created" and T2 is not None and T2 != T
      and eng.state["tensions"][T2]["status"] == "open"
      and eng.state["tensions"][T]["status"] == "resolved")

# =====================================================================
# TV-13 (Stage-3 half) and TV-16 — the structural lifecycle stays
# closed to assessments. The structural tension is a CANNED record
# (see the module docstring): Stage 4 owns the seal machinery that
# raises one in a live run.
# =====================================================================
store, eng, h = fresh_run("stage3-tv13-16")
S_ID = new_id()
eng.commit_events([(
    "TENSION_RAISED", SYSTEM_ACTOR, [STATE],
    {"tension_id": S_ID, "type": "structural", "regions": [STATE],
     "origin": "checker",
     "origin_ref": "caca0000-0000-4000-8000-000000000001",
     "description": "Canned structural tension: the TV-1 setup is "
                    "Stage 4 machinery.",
     "status": "open",
     "summary": "A structural tension stands open (canned record "
                "for the Stage 3 examination of TV-13/TV-16)."})])
h2 = Harness(eng)  # registries rebuilt over the canned history
toks = {x: h2.issue_token(x) for x in (A, B)}

n_events = len(store.all_events())
out = h2.assess(toks[A], t_assess(A, new_id(), S_ID, "addressed"))
rec = events_of(store, "ASSESSMENT_RECORDED")
check("TV-13: a valid assessment of a structural tension is "
      "rejected structural_target",
      out["outcome"] == "rejected"
      and out["reason"] == "structural_target"
      and len(rec) == 1 and len(store.all_events()) == n_events + 1
      and eng.state["assessments"] == {}
      and events_of(store, "TENSION_STATUS") == []
      and eng.state["tensions"][S_ID]["status"] == "open")
print("DEFERRED  TV-13 (resolution half): a passing seal attempt "
      "resolving S requires Stage 4's seal machinery (TV-1); not "
      "built, not counted as a pass.")

out = h2.assess(toks[B], t_assess(A, new_id(), S_ID, "addressed"))
rec = events_of(store, "ASSESSMENT_RECORDED")
check("TV-16: identity_mismatch (step 1) precedes structural_target "
      "(step 5)",
      out["outcome"] == "rejected"
      and out["reason"] == "identity_mismatch"
      and len(rec) == 2
      and rec[-1]["payload"]["reason"] == "identity_mismatch"
      and eng.state["assessments"] == {}
      and eng.state["tensions"][S_ID]["status"] == "open")

# =====================================================================
# TV-14 — multi-match noted_existing
# =====================================================================
store, eng, h = fresh_run("stage3-tv14")
toks = {x: h.issue_token(x) for x in (A, B, C)}
raised_ids = []
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
raised = events_of(store, "TENSION_RAISED")
raised_ids = [e["payload"]["tension_id"] for e in raised]
check("TV-14 setup: two contribution tensions over one set stand",
      len(raised_ids) == 2
      and all(eng.state["tensions"][t]["status"] == "open"
              for t in raised_ids))
seq_c = open_regions(h, store, toks[C], INTERACTIONS, CONTINUITY)
out = h.examine(toks[C], report(C, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_c))
check("TV-14: the examination notes against BOTH tensions",
      out["outcome"] == "noted_existing"
      and out["matched_tensions"] == raised_ids
      and len(eng.state["tensions"]) == 2
      and events_of(store, "TENSION_STATUS") == [])

# =====================================================================
# TV-15 — exactly one event: idempotency and the malformed edges
# =====================================================================
store, eng, h = fresh_run("stage3-tv15")
toks = {x: h.issue_token(x) for x in (A,)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
K = new_id()
R = report(A, new_id(), K, [INTERACTIONS, CONTINUITY], seq_a)
out = h.examine(toks[A], R)
n_events = len(store.all_events())
check("TV-15 setup: the original report is created",
      out["outcome"] == "created")
out2 = h.examine(toks[A], copy.deepcopy(R))
check("TV-15(i): an identical resubmission returns the original "
      "outcome and appends no event",
      out2["outcome"] == "created"
      and out2.get("idempotent_replay") is True
      and out2["tension_id"] == out["tension_id"]
      and len(store.all_events()) == n_events
      and len(events_of(store, "EXAMINATION_RECORDED")) == 1)
bad = {"author": A, "examination_id": new_id(),
       "idempotency_id": new_id(), "description": "Missing regions.",
       "discovery_source": "fabric_read", "discovery_ref": seq_a}
out = h.examine(toks[A], bad)
rec = events_of(store, "EXAMINATION_RECORDED")
check("TV-15(ii): a malformed object is recorded rejected, raw "
      "submission preserved",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid"
      and len(rec) == 2 and rec[-1]["payload"]["report"] == bad
      and len(eng.state["tensions"]) == 1)
n_events = len(store.all_events())
n_log = len(h.log)
try:
    h.examine(toks[A], ["not", "a", "json", "object"])
    check("TV-15(iii): a non-object submission is a transport "
          "refusal", False)
except TransportRefusal:
    check("TV-15(iii): a non-object submission is a transport "
          "refusal, no event, harness log only",
          len(store.all_events()) == n_events
          and len(h.log) == n_log + 1
          and h.log[-1]["kind"] == "transport_refusal")
# Supplementary (section 4 idempotency): the same key with
# different content conflicts, and records the conflict.
out = h.examine(toks[A], report(A, new_id(), K, [INTERACTIONS],
                                seq_a, "Different content, same key."))
check("section 4: same key, different content is "
      "idempotency_conflict",
      out["outcome"] == "rejected"
      and out["reason"] == "idempotency_conflict")

# =====================================================================
# TV-17 — validation precedence, ExaminationReport
# =====================================================================
store, eng, h = fresh_run("stage3-tv17")
toks = {x: h.issue_token(x) for x in (B,)}
seq_b = open_regions(h, store, toks[B], COMPONENTS)
out = h.examine(toks[B], report(B, new_id(), new_id(),
                                [INTERACTIONS, UNKNOWN], 9999))
rec = events_of(store, "EXAMINATION_RECORDED")
check("TV-17: unknown_region (step 4) precedes "
      "discovery_unverifiable (step 6)",
      out["outcome"] == "rejected" and out["reason"] == "unknown_region"
      and len(rec) == 1 and eng.state["tensions"] == {})

# =====================================================================
# TV-18 — the malformed-key edge (ladder step 2)
# =====================================================================
store, eng, h = fresh_run("stage3-tv18")
toks = {x: h.issue_token(x) for x in (A,)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS)
no_key = {"author": A, "examination_id": new_id(),
          "regions": [INTERACTIONS], "description": "No key.",
          "discovery_source": "fabric_read", "discovery_ref": seq_a}
out = h.examine(toks[A], no_key)
check("TV-18(i): an omitted idempotency key proceeds to Schema",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid"
      and out.get("idempotent_replay") is not True)
out = h.assess(toks[A], {"assessment_id": "not-a-uuid", "author": A,
                         "target_kind": "facet", "target_id": STATE,
                         "position": "examined",
                         "reasoning": "Malformed key.",
                         "version_reviewed": 1})
check("TV-18(ii): a malformed assessment_id proceeds to Schema",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid")

# =====================================================================
# TV-19 — record-identity collision, ExaminationReport
# =====================================================================
store, eng, h = fresh_run("stage3-tv19")
toks = {x: h.issue_token(x) for x in (A, B)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
X, K = new_id(), new_id()
out = h.examine(toks[A], report(A, X, K, [INTERACTIONS, CONTINUITY],
                                seq_a))
T = out["tension_id"]
check("TV-19 setup: A's report is recorded under examination_id X",
      out["outcome"] == "created")
seq_b = open_regions(h, store, toks[B], INTERACTIONS, CONTINUITY)
out = h.examine(toks[B], report(B, X, new_id(),
                                [INTERACTIONS, CONTINUITY], seq_b,
                                "A different report, the same id."))
check("TV-19: another author's reuse of X is identity_collision",
      out["outcome"] == "rejected"
      and out["reason"] == "identity_collision"
      and len(eng.state["tensions"]) == 1
      and eng.state["tensions"][T]["status"] == "open")
out = h.examine(toks[A], report(A, X, new_id(), [INTERACTIONS],
                                seq_a, "My own id, fresh key."))
check("TV-19: the identity's own author is bound by the collision "
      "rule too",
      out["outcome"] == "rejected"
      and out["reason"] == "identity_collision")

# =====================================================================
# TV-20 — record-identity collision, Assessment, vs id_conflict
# =====================================================================
store, eng, h = fresh_run("stage3-tv20")
toks = {x: h.issue_token(x) for x in (A, B)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
T = out["tension_id"]
S = new_id()
out = h.assess(toks[A], t_assess(A, S, T, "clarifies"))
check("TV-20 setup: A's assessment is recorded under S",
      out["outcome"] == "recorded")
out = h.assess(toks[B], t_assess(B, S, T, "remains"))
check("TV-20(i): another author's reuse of S is identity_collision",
      out["outcome"] == "rejected"
      and out["reason"] == "identity_collision")
out = h.assess(toks[A], t_assess(A, S, T, "addressed"))
check("TV-20(ii): the author's own reuse with different content "
      "is id_conflict",
      out["outcome"] == "rejected" and out["reason"] == "id_conflict"
      and eng.state["assessments"][S]["position"] == "clarifies")

# =====================================================================
# Supplementary — the settled machinery the vectors do not isolate:
# standing + the stood-down mapping, the disputed precedence, and
# the claim contract's edges (claim settlement items 1-3).
# =====================================================================
store, eng, h = fresh_run("stage3-machinery")
toks = {x: h.issue_token(x) for x in (A, B, C, D, E)}
seq_a = open_regions(h, store, toks[A], INTERACTIONS, CONTINUITY)
out = h.examine(toks[A], report(A, new_id(), new_id(),
                                [INTERACTIONS, CONTINUITY], seq_a))
T = out["tension_id"]
h.assess(toks[B], t_assess(B, new_id(), T, "remains"))
out = h.assess(toks[C], t_assess(C, new_id(), T, "remains"))
check("machinery: two standing remains move the tension to standing",
      out["outcome"] == "recorded"
      and eng.state["tensions"][T]["status"] == "standing")
check("machinery: standing names the required facets it stands down",
      eng.state["facet_status"].get(INTERACTIONS) == "stood_down"
      and eng.state["facet_status"].get(CONTINUITY) == "stood_down"
      and STATE not in eng.state["facet_status"])

seq_d2 = open_regions(h, store, toks[D], STATE)
out = h.submit(toks[D], contrib(
    D, new_id(), {STATE: 1}, [STATE], [STATE],
    [{"kind": "replace_content", "region_id": STATE,
      "new_content": "State, completed work."}], seq_d2))
c_state = out["contribution_id"]
h.claim_completion(toks[D], claim_env(new_id(), STATE, 2, [c_state]))
check("machinery: a valid claim at the current version claims",
      eng.state["facet_status"].get(STATE) == "claimed")
disputed_id = new_id()
h.assess(toks[B], f_assess(B, disputed_id, STATE, "disputed", 2))
check("machinery: a standing dispute outranks the claim",
      eng.state["facet_status"].get(STATE) == "disputed")
h.assess(toks[B], f_assess(B, new_id(), STATE, "examined", 2,
                           supersedes=disputed_id))
check("machinery: superseding the dispute with a review completes",
      eng.state["facet_status"].get(STATE) == "complete")

# The claim contract's edges.
seq_d = open_regions(h, store, toks[D], PRESENTATION)
out = h.submit(toks[D], contrib(
    D, new_id(), {STATE: 2, PRESENTATION: 1}, [STATE, PRESENTATION],
    [PRESENTATION],
    [{"kind": "append_content", "region_id": PRESENTATION,
      "text": " (D's work.)"}], seq_d))
c_pres = out["contribution_id"]
env = claim_env(new_id(), PRESENTATION, 2, [c_pres])
env["claim"]["claimant"] = D
out = h.claim_completion(toks[D], env)
check("claim contract: a claimant field is schema_invalid (the "
      "schema admits none)",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid")
n_events = len(store.all_events())
out = h.claim_completion(toks[D], {"claim": "not-an-object"})
rec = events_of(store, "COMPLETION_CLAIMED")[-1]
check("claim contract: a non-object claim field is recordable "
      "schema_invalid, raw value preserved",
      out["outcome"] == "rejected" and out["reason"] == "schema_invalid"
      and rec["payload"]["claim"] == "not-an-object"
      and len(store.all_events()) == n_events + 1)
try:
    h.claim_completion(toks[D], ["not", "an", "envelope"])
    check("claim contract: a non-object top level is a transport "
          "refusal", False)
except TransportRefusal:
    check("claim contract: a non-object top level is a transport "
          "refusal, no event",
          len(store.all_events()) == n_events + 1)
K_claim = new_id()
env = claim_env(K_claim, PRESENTATION, 2, [c_pres])
out = h.claim_completion(toks[D], env)
n_events = len(store.all_events())
out2 = h.claim_completion(toks[D], copy.deepcopy(env))
check("claim contract: identical replay returns the original "
      "outcome, no event",
      out["outcome"] == "recorded"
      and out2.get("idempotent_replay") is True
      and len(store.all_events()) == n_events)
out = h.claim_completion(toks[D], claim_env(
    K_claim, PRESENTATION, 2, [c_pres], rationale="Different words."))
check("claim contract: same claimant, same id, different content "
      "is id_conflict",
      out["outcome"] == "rejected" and out["reason"] == "id_conflict")
out = h.claim_completion(toks[E], claim_env(
    K_claim, PRESENTATION, 2, [c_pres], rationale="Another's words."))
check("claim contract: another claimant reusing the id is "
      "identity_collision",
      out["outcome"] == "rejected"
      and out["reason"] == "identity_collision")
out = h.claim_completion(toks[D], claim_env(
    new_id(), UNKNOWN, 1, [c_pres]))
check("claim contract: an unknown facet is target_unresolved",
      out["outcome"] == "rejected"
      and out["reason"] == "target_unresolved")
out = h.claim_completion(toks[D], claim_env(
    new_id(), PRESENTATION, 2, [new_id()]))
check("claim contract: an unknown cited contribution is "
      "contribution_unresolved",
      out["outcome"] == "rejected"
      and out["reason"] == "contribution_unresolved")
out = h.claim_completion(toks[D], claim_env(
    new_id(), PRESENTATION, 99, [c_pres]))
check("claim contract: a future facet_version is "
      "version_never_existed",
      out["outcome"] == "rejected"
      and out["reason"] == "version_never_existed")
check("machinery: replay reproduces the whole Stage 3 record",
      state_hash(eng.replay()) == state_hash(eng.state))
ok, bad = verify_chain(store.all_events(), CONSTITUTION_HASH)
check("machinery: the chain verifies over the Stage 3 history",
      ok and bad is None)

# =====================================================================
# Socket phase — the three operations on the data socket, through
# the real two-OS-context boundary: refused before attestation,
# admitted after, performed by a genuine loomagent process.
# =====================================================================
from fabric.probe2 import attest_probe, run_twin_probe
from fabric.runtime_setup import (RUNTIME_BASE, _line_request,
                                  admin_request, agent_call,
                                  build_runtime, start_service,
                                  stop_service)

BASE = RUNTIME_BASE
os.makedirs(BASE, exist_ok=True)
exp = build_runtime(BASE, "s3exp")
proc = start_service(exp)
try:
    admin_request(exp, {"op": "open_run", "run_id": "stage3-socket"})
    resp = agent_call(exp, "examine", "no-token-yet",
                      {"report": report(A, new_id(), new_id(),
                                        [INTERACTIONS], 1)})
    check("socket: examine is refused before attestation",
          resp.get("ok") is False
          and resp.get("kind") == "not_attested")
    result = run_twin_probe(BASE, "s3twin")
    att = attest_probe(exp, result)
    check("socket: the twin attestation stands at seq 2",
          att.get("ok") is True and att["result"]["event_seq"] == 2)
    tok_a = admin_request(exp, {"op": "issue_token",
                                "agent_id": A})["result"]["token"]
    agent_call(exp, "open_region", tok_a, {"region_id": INTERACTIONS})
    opened = agent_call(exp, "open_region", tok_a,
                        {"region_id": CONTINUITY})
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    a_disc = [e["event_seq"] for e in hist
              if e["type"] == "DISCOVERY" and e["actor"] == A][-1]
    resp = agent_call(exp, "examine", tok_a,
                      {"report": report(A, new_id(), new_id(),
                                        [INTERACTIONS, CONTINUITY],
                                        a_disc)})
    check("socket: examine through the boundary creates a tension",
          resp.get("ok") is True
          and resp["result"]["outcome"] == "created")
    tid = resp["result"]["tension_id"]
    resp = agent_call(exp, "assess", tok_a,
                      {"assessment": t_assess(A, new_id(), tid,
                                              "clarifies")})
    check("socket: assess through the boundary is recorded",
          resp.get("ok") is True
          and resp["result"]["outcome"] == "recorded")
    resp = agent_call(exp, "submit", tok_a, {"response": contrib(
        A, new_id(), {INTERACTIONS: 1, CONTINUITY: 1},
        [INTERACTIONS, CONTINUITY], [INTERACTIONS],
        [{"kind": "replace_content", "region_id": INTERACTIONS,
          "new_content": "Interactions, revised by the crew."}],
        a_disc)})
    check("socket: the contribution commits through the boundary",
          resp.get("ok") is True
          and resp["result"]["outcome"] == "accepted")
    cid = resp["result"]["contribution_id"]
    resp = agent_call(exp, "claim_completion", tok_a,
                      {"claim": claim_env(new_id(), INTERACTIONS, 2,
                                          [cid])["claim"]})
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    fs = [e for e in hist if e["type"] == "FACET_STATUS"
          and e["payload"]["region_id"] == INTERACTIONS]
    check("socket: claim_completion through the boundary records "
          "and claims the facet",
          resp.get("ok") is True
          and resp["result"]["outcome"] == "recorded"
          and fs and fs[-1]["payload"]["to"] == "claimed")
    n_hist = len(hist)
    resp = _line_request(exp["data_sock"], ["not", "an", "object"])
    hist = admin_request(exp, {"op": "history"})["result"]["events"]
    check("socket: a non-object request line is a transport refusal",
          resp.get("ok") is False
          and resp.get("kind") == "transport_refusal"
          and len(hist) == n_hist)
finally:
    stop_service(proc, exp)

print()
print("STAGE 3 TESTS:", "ALL PASS" if not failures
      else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
