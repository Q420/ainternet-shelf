"""Piece 6 (part 3) tests — orchestrator functions (SPEC SHEET
§3.8, R26/R35/R36), per the approved scope Rev 3
(src/PIECE6-ORCHESTRATOR-SCOPE-REV3-2026-11-22.md) and its
eleven acceptance points.

Run: PYTHONPATH=src python3 tests/unit/test_piece6_orchestrator.py
Exits 0 when every check passes.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "src"))

from framework import onboarding as ob
from framework.doorway import Doorway, DoorwayRefusal
from framework.driver import Driver
from framework.record import (FrameworkStore, CONSTITUTION_HASH,
                              effective_case)

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def refused(fn):
    try:
        fn()
    except DoorwayRefusal:
        return True
    return False


TREE = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
FULL_GATES = {"assembly": "assembly", "completion": "completion",
              "B": "judgement", "C": "judgement", "D": "judgement"}
SEATS = {
    "crew-1": {"role": "crew", "identity_status": "unverified"},
    "crew-2": {"role": "crew", "identity_status": "unverified"},
    "orch-1": {"role": "orchestrator",
               "identity_status": "unverified"},
    "exam-1": {"role": "examiner", "identity_status": "unverified"},
    "dir-1": {"role": "director", "identity_status": "unverified"},
}
CREW = [{"seat": s, "role": b["role"]} for s, b in SEATS.items()]


def fresh(gates=None, tree=None):
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    payload = {"run_id": "run-1", "tree": tree or TREE,
               "seats": SEATS}
    if gates is not None:
        payload["gates"] = gates
    store.append("RUN_COMMISSIONED", "dir-1", [], payload)
    store.commit()
    d = Doorway(store)
    tok = {s: d.issue_token(s) for s in SEATS}
    return store, d, tok


def A(d, store, token, type_, payload):
    return d.act(token, type_, payload, view_seq=store.head_seq())


def propose(d, store, tok, crew=None):
    seq = store.head_seq()  # the commission is event 1 in fresh()
    return A(d, store, tok["orch-1"], "ASSEMBLY_PROPOSED", {
        "commission_seq": 1, "tree_ref": 1, "gates_ref": 1,
        "crew": crew or CREW})


def record_for(d, store, tok, proposal_seq, gate_set=None,
               mapping=None, weighed=None):
    return A(d, store, tok["exam-1"], "ASSEMBLY_RECORD", {
        "proposal_seq": proposal_seq,
        "criteria_mapping": mapping or {
            part: f"criterion-{part}" for part in ("A", "B", "C", "D")},
        "gate_set": gate_set or dict(FULL_GATES),
        "identity_weighed": weighed or {
            s: "unverified" for s in SEATS}})


def outcome(d, store, tok, joint, result, **kw):
    payload = {"joint": joint, "outcome": result}
    payload.update(kw)
    return A(d, store, tok["exam-1"], "GATE_OUTCOME", payload)


def contrib(d, store, tok, seat, cid, part, claim=None):
    payload = {"contribution_id": cid, "tree_part": part,
               "text": "work"}
    if claim:
        payload["claim_id"] = claim
    return A(d, store, tok[seat], "CONTRIBUTION", payload)


def open_run(d, store, tok):
    prop = propose(d, store, tok)
    record_for(d, store, tok, prop["event_seq"])
    outcome(d, store, tok, "assembly", "allow")
    return prop


# -- T1 (acceptance 1): an assembly allow answers an examined
# assembly — proposal, then record bound to it, then allow.
store, d, tok = fresh(gates=FULL_GATES)
prop = propose(d, store, tok)
check("T1 an assembly allow with no record standing is refused",
      refused(lambda: outcome(d, store, tok, "assembly", "allow")))
record_for(d, store, tok, prop["event_seq"])
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "B", "allow")
ev = contrib(d, store, tok, "crew-1", "c-t1", "B")
check("T1 proposal -> record -> allow opens the run",
      ev["type"] == "CONTRIBUTION")

# -- T1b: a proposal answering the wrong commission is refused.
store, d, tok = fresh(gates=FULL_GATES)
check("T1b a proposal naming a wrong commission is refused",
      refused(lambda: A(d, store, tok["orch-1"], "ASSEMBLY_PROPOSED",
                        {"commission_seq": 99, "tree_ref": 99,
                         "gates_ref": 99, "crew": CREW})))

# -- T2 (acceptance 2): a re-proposal invalidates the earlier
# record's support AND the earlier allow.
store, d, tok = fresh(gates=FULL_GATES)
open_run(d, store, tok)
outcome(d, store, tok, "B", "allow")
outcome(d, store, tok, "assembly", "correct")
prop2 = propose(d, store, tok)
check("T2 after re-proposal the pre-run block has returned",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t2", "B")))
check("T2 the old record does not support an allow",
      refused(lambda: outcome(d, store, tok, "assembly", "allow")))
record_for(d, store, tok, prop2["event_seq"])
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "B", "allow")
ev = contrib(d, store, tok, "crew-1", "c-t2", "B")
check("T2 a fresh record + allow reopens the run",
      ev["type"] == "CONTRIBUTION")

# -- T3 (acceptance 3): record completeness is mechanical.
store, d, tok = fresh(gates=FULL_GATES)
prop = propose(d, store, tok)
mapping = {p: f"criterion-{p}" for p in ("A", "B", "C")}
check("T3 a record omitting a tree part is refused",
      refused(lambda: record_for(d, store, tok, prop["event_seq"],
                                 mapping=mapping)))
weighed = {s: "unverified" for s in SEATS if s != "crew-2"}
check("T3 a record omitting a proposed seat is refused",
      refused(lambda: record_for(d, store, tok, prop["event_seq"],
                                 weighed=weighed)))
weighed = {s: "unverified" for s in SEATS}
weighed["crew-1"] = "declared"
check("T3 a record misstating a derived status is refused",
      refused(lambda: record_for(d, store, tok, prop["event_seq"],
                                 weighed=weighed)))
bad_set = dict(FULL_GATES)
del bad_set["D"]
check("T3 a record carrying an incomplete gate set is refused",
      refused(lambda: record_for(d, store, tok, prop["event_seq"],
                                 gate_set=bad_set)))
check("T3 a record bound to no standing proposal is refused",
      refused(lambda: record_for(d, store, tok, 999)))

# -- T4 (acceptance 4): the operative set — the record's examined
# set governs once it stands; establishing it alone opens
# nothing; on re-proposal the operative set reverts to the
# declaration until the new record stands.
partial = {"assembly": "assembly", "completion": "completion",
           "B": "judgement", "C": "judgement"}  # D missing: invalid
store, d, tok = fresh(gates=partial)
st = d.state()
check("T4 the incomplete declaration is invalid as proposed",
      st["gate_set"]["declared"] and not st["gate_set"]["valid"])
prop = propose(d, store, tok)
record_for(d, store, tok, prop["event_seq"])  # full set examined
st = d.state()
check("T4 the record's examined set becomes operative and valid",
      st["gate_set"]["valid"]
      and st["gate_set"]["operative"] == FULL_GATES)
check("T4 establishing the operative set alone opens nothing",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t4", "B")))
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "B", "allow")
outcome(d, store, tok, "D", "allow")
ev = contrib(d, store, tok, "crew-1", "c-t4", "D")
check("T4 passage follows the operative set (D has a gate)",
      ev["type"] == "CONTRIBUTION")
prop2 = propose(d, store, tok)
st = d.state()
check("T4 on re-proposal the operative set reverts to the "
      "declaration",
      st["gate_set"]["operative"] == partial
      and not st["gate_set"]["valid"])
record_for(d, store, tok, prop2["event_seq"],
           gate_set=dict(FULL_GATES))
st = d.state()
check("T4 the new record's set replaces the old cleanly",
      st["gate_set"]["operative"] == FULL_GATES
      and st["gate_set"]["valid"])

# -- T5/T6 (acceptance 5-6): certification coverage — declared
# boundary validated; derived membership enforced exactly.
store, d, tok = fresh(gates=FULL_GATES)
open_run(d, store, tok)
outcome(d, store, tok, "B", "allow")
outcome(d, store, tok, "C", "allow")
ob.onboard(d, tok["orch-1"], "crew-1", "I am a test model.",
           identity_status="declared")
# §3.6's transition: onboarding kills the commission token; a
# fresh token binds to the onboarding identity.
tok["crew-1"] = d.issue_token("crew-1")
contrib(d, store, tok, "crew-1", "c-t5a", "B")
contrib(d, store, tok, "crew-1", "c-t5b", "B")
contrib(d, store, tok, "crew-2", "c-t5c", "C")
A(d, store, tok["crew-1"], "COMPLETION_CLAIMED", {"text": "done"})
A(d, store, tok["orch-1"], "RUN_READY_FOR_COMPLETION", {})
outcome(d, store, tok, "completion", "allow")
cert_b = {"covers_parts": ["B"],
          "identity_status": {"crew-1": "declared"}}
ev = A(d, store, tok["exam-1"], "CERTIFICATION", cert_b)
check("T5 a part certification states its contributors exactly "
      "(crew-1 once, though two contributions)",
      ev["type"] == "CERTIFICATION")
check("T5 an empty covers_parts list is refused",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"covers_parts": [], "identity_status": {}})))
check("T5 covers_parts naming an unknown part is refused",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"covers_parts": ["Z"],
                         "identity_status": {}})))
check("T5 duplicate covers_parts are refused",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"covers_parts": ["B", "B"],
                         "identity_status":
                             {"crew-1": "declared"}})))
check("T6 a certification omitting a covered contributor is "
      "refused",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"identity_status":
                             {"crew-1": "declared"}})))
check("T6 a certification misstating a status is refused",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"identity_status":
                             {"crew-1": "unverified",
                              "crew-2": "unverified"}})))
check("T6 a certification inventing a status outside its "
      "coverage is refused",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"covers_parts": ["B"],
                         "identity_status":
                             {"crew-1": "declared",
                              "crew-2": "unverified"}})))
ev = A(d, store, tok["exam-1"], "CERTIFICATION",
       {"identity_status": {"crew-1": "declared",
                            "crew-2": "unverified"}})
check("T6 whole-run coverage states every contributor, the "
      "unverified seat as unverified",
      ev["type"] == "CERTIFICATION")

# -- T7 (acceptance 7): readiness eligibility — a floor of one
# standing crew claim; the claim alone arms nothing.
store, d, tok = fresh(gates=FULL_GATES)
open_run(d, store, tok)
check("T7 readiness with no crew claim standing is refused",
      refused(lambda: A(d, store, tok["orch-1"],
                        "RUN_READY_FOR_COMPLETION", {})))
A(d, store, tok["crew-1"], "COMPLETION_CLAIMED", {"text": "done"})
ev = A(d, store, tok["orch-1"], "RUN_READY_FOR_COMPLETION", {})
check("T7 readiness records over a standing claim",
      ev["type"] == "RUN_READY_FOR_COMPLETION")
st = d.state()
check("T7 claims_by_part derives the claim's standing",
      st["claims_by_part"].get("(job)") is not None)
check("T7 the declaration alone does not certify",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"identity_status": {}})))

# -- T8 (acceptance 8): routing — referents validated, relevance
# enforced, latest route current, history retained.
store, d, tok = fresh(gates=FULL_GATES)
open_run(d, store, tok)
outcome(d, store, tok, "B", "allow")
contrib(d, store, tok, "crew-1", "c-t8", "B", claim="claim-t8")
A(d, store, tok["crew-2"], "DISAGREEMENT",
  {"claim_id": "claim-t8", "disagreement_id": "d-t8"})


def route(d, store, tok, seat, joint, did="d-t8"):
    return A(d, store, tok[seat], "COMMENT", {
        "on_job": True, "text": "routing",
        "routes_disagreement": did, "to_gate": joint})


check("T8 routing to an irrelevant gate is refused",
      refused(lambda: route(d, store, tok, "orch-1", "C")))
check("T8 routing an unrecorded disagreement is refused",
      refused(lambda: route(d, store, tok, "orch-1", "B",
                            did="d-nope")))
check("T8 routing by a non-orchestrator is refused",
      refused(lambda: route(d, store, tok, "crew-1", "B")))
route(d, store, tok, "orch-1", "B")
st = d.state()
check("T8 a valid route derives as current",
      st["routing"]["d-t8"]["joint"] == "B")
route(d, store, tok, "orch-1", "completion")
st = d.state()
check("T8 the latest valid route is current; history retained",
      st["routing"]["d-t8"]["joint"] == "completion"
      and len(st["routing_notes"]) == 2)

# -- T9 (acceptance 9): an orchestrator note wakes only the
# addressed seat's driver. (Undeclared run — the pre-gates path;
# the wake derivation is the piece's subject here.)
store, d, tok = fresh()
CASE = {"case_id": "case-1", "version": 1, "seat": "crew-1",
        "part": "B", "assignment": "Build B",
        "evidence_boundary": [], "verification_list": ["check B"],
        "account": "crew-1", "authority": "crew defaults"}
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-1", "version": 1})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-1", "version": 1})
A(d, store, tok["orch-1"], "CASE_ISSUED", dict(CASE))
CASE2 = dict(CASE, case_id="case-2", seat="crew-2", part="C",
             assignment="Build C", account="crew-2")
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-2", "version": 1})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-2", "version": 1})
A(d, store, tok["orch-1"], "CASE_ISSUED", dict(CASE2))


class Stub:
    def __init__(self):
        self.calls = []

    def __call__(self, package):
        self.calls.append(package)
        return []


m1, m2 = Stub(), Stub()
drv1 = Driver(d, "crew-1", tok["crew-1"], m1)
drv2 = Driver(d, "crew-2", tok["crew-2"], m2)
drv1.wake_cycle()
drv2.wake_cycle()
n1, n2 = len(m1.calls), len(m2.calls)
A(d, store, tok["orch-1"], "COMMENT",
  {"on_job": True, "to_seat": "crew-1", "text": "a note for you"})
r1 = drv1.wake_cycle()
check("T9 the addressed seat wakes on the note",
      r1["woke"] is True and len(m1.calls) == n1 + 1
      and any(r["kind"] == "orchestrator_note"
              for r in r1["reasons"]))
r2 = drv2.wake_cycle()
check("T9 no other seat wakes on the note",
      not any(r["kind"] == "orchestrator_note"
              for r in (r2.get("reasons") or [])))

# -- T9b (correction round 1): the wake privilege is the
# orchestrator's authorship, not the addressing. A crew-authored
# COMMENT addressed to another seat derives no such wake.
crew_note = A(d, store, tok["crew-2"], "COMMENT",
              {"on_job": True, "to_seat": "crew-1",
               "text": "a crew note, addressed but not "
                       "orchestration"})
r1 = drv1.wake_cycle()
check("T9b a crew-authored addressed comment derives no "
      "orchestrator_note wake",
      not any(r["kind"] == "orchestrator_note"
              and r["event_seq"] == crew_note["event_seq"]
              for r in (r1.get("reasons") or [])))

# -- T10 (acceptance 10): uncased provenance is position-
# sensitive; the pre-acknowledgement state is a separate fact.
store, d, tok = fresh(gates=FULL_GATES)
open_run(d, store, tok)
outcome(d, store, tok, "B", "allow")
outcome(d, store, tok, "C", "allow")
CASE_B = {"case_id": "case-b", "version": 1, "seat": "crew-1",
          "part": "B", "assignment": "Build B",
          "evidence_boundary": [], "verification_list": ["chk"],
          "account": "crew-1", "authority": "crew defaults"}
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-b", "version": 1})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-b", "version": 1})
A(d, store, tok["orch-1"], "CASE_ISSUED", dict(CASE_B))
contrib(d, store, tok, "crew-1", "c-pre", "B")
st = d.state()
check("T10 a contribution under a standing but unacknowledged "
      "case is cased and pre-acknowledgement",
      "c-pre" in st["pre_ack"].get("B", [])
      and "c-pre" not in st["uncased"].get("B", []))
A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
  {"case_id": "case-b", "version": 1})
contrib(d, store, tok, "crew-1", "c-post", "B")
contrib(d, store, tok, "crew-1", "c-nocase", "C")
st = d.state()
check("T10 after acknowledgement, contributions derive neither",
      "c-post" not in st["pre_ack"].get("B", [])
      and "c-post" not in st["uncased"].get("B", []))
check("T10 a contribution with no case standing is uncased",
      "c-nocase" in st["uncased"].get("C", []))
CASE_C = dict(CASE_B, case_id="case-c", part="C",
              assignment="Build C")
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-c", "version": 1})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-c", "version": 1})
A(d, store, tok["orch-1"], "CASE_ISSUED", dict(CASE_C))
A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
  {"case_id": "case-c", "version": 1})
contrib(d, store, tok, "crew-1", "c-cased", "C")
st = d.state()
check("T10 a later case never recases the earlier contribution",
      "c-nocase" in st["uncased"].get("C", []))
check("T10 a same-version second lineage does not govern "
      "while the first stands — the fold follows the driver's "
      "one effective case (round 3)",
      "c-cased" in st["uncased"].get("C", [])
      and effective_case(st, "crew-1")["case_id"] == "case-b")

# -- T11 (correction round 1): provenance selects the EFFECTIVE
# version at the contribution's position — a superseding
# version's unacknowledged state governs, not the acknowledged
# predecessor's.
store, d, tok = fresh(gates=FULL_GATES)
open_run(d, store, tok)
outcome(d, store, tok, "B", "allow")
CASE_V1 = {"case_id": "case-v", "version": 1, "seat": "crew-1",
           "part": "B", "assignment": "Build B",
           "evidence_boundary": [], "verification_list": ["chk"],
           "account": "crew-1", "authority": "crew defaults"}
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-v", "version": 1})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-v", "version": 1})
A(d, store, tok["orch-1"], "CASE_ISSUED", dict(CASE_V1))
A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
  {"case_id": "case-v", "version": 1})
contrib(d, store, tok, "crew-1", "c-v1", "B")
st = d.state()
check("T11 under acknowledged v1: cased, not pre-ack",
      "c-v1" not in st["uncased"].get("B", [])
      and "c-v1" not in st["pre_ack"].get("B", []))
CASE_V2 = dict(CASE_V1, version=2,
               verification_list=["chk", "chk again"],
               representational=False)
A(d, store, tok["orch-1"], "CASE_CORRECTED", dict(CASE_V2))
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-v", "version": 2})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-v", "version": 2})
A(d, store, tok["orch-1"], "CASE_ISSUED",
  {"case_id": "case-v", "version": 2})
contrib(d, store, tok, "crew-1", "c-v2pre", "B")
st = d.state()
check("T11 under unacknowledged v2: cased and pre-ack — the "
      "effective version governs",
      "c-v2pre" in st["pre_ack"].get("B", [])
      and "c-v2pre" not in st["uncased"].get("B", []))
check("T11 supersession never uncases the v1 contribution",
      "c-v1" not in st["uncased"].get("B", [])
      and "c-v1" not in st["pre_ack"].get("B", []))
A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
  {"case_id": "case-v", "version": 2})
contrib(d, store, tok, "crew-1", "c-v2post", "B")
st = d.state()
check("T11 after v2 acknowledgement: cased, not pre-ack",
      "c-v2post" not in st["pre_ack"].get("B", [])
      and "c-v2post" not in st["uncased"].get("B", []))

# -- T12 (correction round 2): the effective version is
# selected per case lineage BEFORE part coverage — a semantic
# correction that moves the case to another part retires the
# old version's coverage of its old part entirely.
store, d, tok = fresh(gates=FULL_GATES)
open_run(d, store, tok)
outcome(d, store, tok, "B", "allow")
outcome(d, store, tok, "C", "allow")
CASE_M1 = {"case_id": "case-m", "version": 1, "seat": "crew-1",
           "part": "B", "assignment": "Build B",
           "evidence_boundary": [], "verification_list": ["chk"],
           "account": "crew-1", "authority": "crew defaults"}
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-m", "version": 1})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-m", "version": 1})
A(d, store, tok["orch-1"], "CASE_ISSUED", dict(CASE_M1))
A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
  {"case_id": "case-m", "version": 1})
contrib(d, store, tok, "crew-1", "c-m1", "B")
st = d.state()
check("T12 under v1 (part B, acknowledged): cased for B",
      "c-m1" not in st["uncased"].get("B", [])
      and "c-m1" not in st["pre_ack"].get("B", []))
CASE_M2 = dict(CASE_M1, version=2, part="C",
               assignment="Build C", representational=False)
A(d, store, tok["orch-1"], "CASE_CORRECTED", dict(CASE_M2))
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-m", "version": 2})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-m", "version": 2})
A(d, store, tok["orch-1"], "CASE_ISSUED",
  {"case_id": "case-m", "version": 2})
contrib(d, store, tok, "crew-1", "c-m2b", "B")
contrib(d, store, tok, "crew-1", "c-m2c", "C")
st = d.state()
check("T12 the superseded version no longer covers B: the "
      "contribution is uncased for B",
      "c-m2b" in st["uncased"].get("B", [])
      and "c-m2b" not in st["pre_ack"].get("B", []))
check("T12 the effective version covers C, unacknowledged: "
      "cased and pre-ack for C",
      "c-m2c" in st["pre_ack"].get("C", [])
      and "c-m2c" not in st["uncased"].get("C", []))
check("T12 the v1-era contribution keeps its provenance",
      "c-m1" not in st["uncased"].get("B", [])
      and "c-m1" not in st["pre_ack"].get("B", []))
A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
  {"case_id": "case-m", "version": 2})
contrib(d, store, tok, "crew-1", "c-m3c", "C")
st = d.state()
check("T12 after v2 acknowledgement: cased for C, not pre-ack",
      "c-m3c" not in st["pre_ack"].get("C", [])
      and "c-m3c" not in st["uncased"].get("C", []))

# -- T13 (correction round 3): two lineages, different
# versions, different parts — fold provenance and the driver's
# effective assignment cannot diverge, because both are the
# one effective_case selection.
store, d, tok = fresh(gates=FULL_GATES)
open_run(d, store, tok)
outcome(d, store, tok, "B", "allow")
outcome(d, store, tok, "C", "allow")
CASE_A1 = {"case_id": "case-a2", "version": 1, "seat": "crew-1",
           "part": "B", "assignment": "Build B",
           "evidence_boundary": [], "verification_list": ["chk"],
           "account": "crew-1", "authority": "crew defaults"}
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-a2", "version": 1})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-a2", "version": 1})
A(d, store, tok["orch-1"], "CASE_ISSUED", dict(CASE_A1))
A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
  {"case_id": "case-a2", "version": 1})
CASE_A2 = dict(CASE_A1, version=2,
               verification_list=["chk", "chk again"],
               representational=False)
A(d, store, tok["orch-1"], "CASE_CORRECTED", dict(CASE_A2))
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-a2", "version": 2})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-a2", "version": 2})
A(d, store, tok["orch-1"], "CASE_ISSUED",
  {"case_id": "case-a2", "version": 2})
CASE_C1 = {"case_id": "case-c1", "version": 1, "seat": "crew-1",
           "part": "C", "assignment": "Build C",
           "evidence_boundary": [], "verification_list": ["chk"],
           "account": "crew-1", "authority": "crew defaults"}
A(d, store, tok["orch-1"], "CASE_VERIFIED",
  {"case_id": "case-c1", "version": 1})
A(d, store, tok["exam-1"], "CASE_JUDGED",
  {"case_id": "case-c1", "version": 1})
A(d, store, tok["orch-1"], "CASE_ISSUED", dict(CASE_C1))
A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
  {"case_id": "case-c1", "version": 1})
st = d.state()
eff = effective_case(st, "crew-1")
check("T13 the driver's effective case is lineage A at v2",
      eff["case_id"] == "case-a2" and eff["version"] == 2)
contrib(d, store, tok, "crew-1", "c-13c", "C")
contrib(d, store, tok, "crew-1", "c-13b", "B")
st = d.state()
check("T13 a contribution on C is uncased — the standing v1 "
      "for C does not govern while A/v2 is the effective case",
      "c-13c" in st["uncased"].get("C", []))
check("T13 a contribution on B is cased under A/v2 and "
      "pre-ack (v2 unacknowledged)",
      "c-13b" in st["pre_ack"].get("B", [])
      and "c-13b" not in st["uncased"].get("B", []))
A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
  {"case_id": "case-a2", "version": 2})
contrib(d, store, tok, "crew-1", "c-13b2", "B")
st = d.state()
check("T13 after A/v2 acknowledgement: cased, not pre-ack",
      "c-13b2" not in st["pre_ack"].get("B", [])
      and "c-13b2" not in st["uncased"].get("B", []))

print()
if FAILURES:
    print(f"PIECE 6 ORCHESTRATOR TESTS: {len(FAILURES)} FAILURE(S): "
          f"{FAILURES}")
    sys.exit(1)
print("PIECE 6 ORCHESTRATOR TESTS: ALL PASS")
