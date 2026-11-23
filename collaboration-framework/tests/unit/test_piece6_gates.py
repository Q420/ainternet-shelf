"""Piece 6 tests — gates (SPEC SHEET §3.7, R21-R25), against the
seventeen acceptance tests of src/PIECE6-GATES-SCOPE-2026-11-22.md
§5 as approved to build (VANE-PIECE6-GATES-APPROVAL-2026-11-22.md).
Test 12 of the scope is the regression run over the earlier suites
and the substrate — carried in the submission round, not this file.

The tree: A (root) -> [B, C]; B -> [D]. Required joints: B, C, D.
The declaration names exactly those, plus assembly and completion.

Run: PYTHONPATH=src python3 tests/unit/test_piece6_gates.py
Exits 0 when every check passes.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "src"))

from framework.record import FrameworkStore, CONSTITUTION_HASH
from framework.doorway import Doorway, DoorwayRefusal
from framework.driver import Driver
from framework import onboarding as ob

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


TREE = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
GATES = {"assembly": "assembly", "completion": "completion",
         "B": "judgement", "C": "judgement", "D": "judgement"}
SEATS = {
    "orch-1": {"role": "orchestrator", "identity_status": "declared"},
    "exam-1": {"role": "examiner", "identity_status": "declared"},
    "dir-1": {"role": "director", "identity_status": "declared"},
    "crew-1": {"role": "crew", "identity_status": "declared"},
    "crew-2": {"role": "crew", "identity_status": "declared"},
}


def fresh(gates=GATES):
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    payload = {"run_id": "run-1", "tree": dict(TREE),
               "seats": dict(SEATS), "briefs": {}}
    if gates is not None:
        payload["gates"] = dict(gates)
    store.append("RUN_COMMISSIONED", "dir-1", [], payload)
    store.commit()
    d = Doorway(store)
    tok = {s: d.issue_token(s) for s in SEATS}
    return store, d, tok


def A(d, store, token, type_, payload):
    return d.act(token, type_, payload, view_seq=store.head_seq())


def refused(fn):
    try:
        fn()
        return False
    except DoorwayRefusal:
        return True


def outcome(d, store, tok, joint, result, **extra):
    payload = {"joint": joint, "outcome": result}
    payload.update(extra)
    return A(d, store, tok["exam-1"], "GATE_OUTCOME", payload)


def contrib(d, store, tok, who, cid, part):
    return A(d, store, tok[who], "CONTRIBUTION",
             {"contribution_id": cid, "tree_part": part,
              "text": f"work {cid}"})


def issue_case(d, store, tok):
    A(d, store, tok["orch-1"], "CASE_VERIFIED",
      {"case_id": "case-1", "version": 1})
    A(d, store, tok["exam-1"], "CASE_JUDGED",
      {"case_id": "case-1", "version": 1})
    return A(d, store, tok["orch-1"], "CASE_ISSUED", {
        "case_id": "case-1", "version": 1, "seat": "crew-1",
        "part": "B", "assignment": "Build the B part",
        "evidence_boundary": ["mat-1"],
        "verification_list": ["check B"],
        "account": "crew-1", "authority": "crew defaults"})


class StubModel:
    def __init__(self):
        self.calls = []

    def __call__(self, package):
        self.calls.append(package)
        return []


# -- T1: pre-assembly, work is refused and recorded; a wake
# attempted in the window is recorded as a REJECTION (G5).
store, d, tok = fresh()
issue_case(d, store, tok)
check("T1 CASE_ACKNOWLEDGED refused pre-assembly",
      refused(lambda: A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
                        {"case_id": "case-1", "version": 1})))
check("T1 CONTRIBUTION refused pre-assembly",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t1", "B")))
model = StubModel()
driver = Driver(d, "crew-1", tok["crew-1"], model)
r = driver.wake_cycle()
check("T1 the driver does not invoke the model pre-assembly",
      model.calls == [] and r["woke"] is False
      and r.get("blocked") == "assembly gate (R22)")
wakes = [ev for ev in store.all_events()
         if ev["type"] == "REJECTION"
         and ev["payload"].get("attempted_type") == "WAKE"]
check("T1 the blocked wake is recorded naming seat, part, R22",
      len(wakes) == 1 and wakes[0]["payload"]["seat"] == "crew-1"
      and wakes[0]["payload"]["part"] == "B"
      and "R22" in wakes[0]["payload"]["ground"])

# -- T2: gate-process acts record fine in the same window.
store, d, tok = fresh()
ob.onboard(d, tok["orch-1"], "crew-1", "model declaration")
issue_case(d, store, tok)
types = [ev["type"] for ev in store.all_events()]
check("T2 ONBOARDING and the office route record pre-assembly",
      "ONBOARDING" in types and "CASE_ISSUED" in types
      and "CASE_VERIFIED" in types and "CASE_JUDGED" in types)

# -- T3: after a valid set's assembly allow, briefing proceeds.
store, d, tok = fresh()
issue_case(d, store, tok)
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "B", "allow")
ev = A(d, store, tok["crew-1"], "CASE_ACKNOWLEDGED",
       {"case_id": "case-1", "version": 1})
check("T3 acknowledgement records once the run is open",
      ev["type"] == "CASE_ACKNOWLEDGED")
ev = contrib(d, store, tok, "crew-1", "c-t3", "B")
check("T3 work records once the run is open",
      ev["type"] == "CONTRIBUTION")

# -- T4: passage — a gated part and its downstream are held.
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
check("T4 contribution on a gated part refused before its outcome",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t4a", "B")))
check("T4 contribution on a downstream part refused likewise",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t4b", "D")))
outcome(d, store, tok, "B", "allow")
ev = contrib(d, store, tok, "crew-1", "c-t4c", "B")
check("T4 after allow, the part records", ev["type"] == "CONTRIBUTION")
check("T4 the downstream part is still held by its own gate",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t4d", "D")))
outcome(d, store, tok, "D", "allow")
ev = contrib(d, store, tok, "crew-1", "c-t4e", "D")
check("T4 after its own allow, the downstream part records",
      ev["type"] == "CONTRIBUTION")

# -- T5: R29 witness — passage open, no ordering within a part.
for first, second in (("crew-1", "crew-2"), ("crew-2", "crew-1")):
    store, d, tok = fresh()
    outcome(d, store, tok, "assembly", "allow")
    outcome(d, store, tok, "B", "allow")
    contrib(d, store, tok, first, f"c-t5-{first}", "B")
    contrib(d, store, tok, second, f"c-t5-{second}", "B")
    got = [ev for ev in store.all_events()
           if ev["type"] == "CONTRIBUTION"]
    check(f"T5 two seats contribute in one part, {first} first",
          len(got) == 2)

# -- T6: correct holds passage; re-judgement opens it; both
# outcomes stand in history.
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "B", "correct")
check("T6 passage stays blocked on correct",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t6", "B")))
A(d, store, tok["crew-1"], "COMMENT",
  {"on_job": True, "text": "correction noted"})
outcome(d, store, tok, "B", "allow")
ev = contrib(d, store, tok, "crew-1", "c-t6b", "B")
check("T6 a re-judged allow opens passage",
      ev["type"] == "CONTRIBUTION")
outs = [ev["payload"]["outcome"] for ev in store.all_events()
        if ev["type"] == "GATE_OUTCOME"
        and ev["payload"].get("joint") == "B"]
check("T6 both outcomes stand in history", outs == ["correct", "allow"])

# -- T7: escalate pauses part + downstream; the release is
# ruling-gated (R24).
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "C", "allow")
outcome(d, store, tok, "B", "escalate", tree_part="B")
check("T7 the escalated part is blocked",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t7a", "B")))
check("T7 its downstream is blocked",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t7b", "D")))
ev = contrib(d, store, tok, "crew-1", "c-t7c", "C")
check("T7 an unrelated branch continues",
      ev["type"] == "CONTRIBUTION")
check("T7 an allow is refused while no ruling stands",
      refused(lambda: outcome(d, store, tok, "B", "allow")))
A(d, store, tok["dir-1"], "RULING",
  {"joint": "B", "action": "return to the gate"})
outcome(d, store, tok, "B", "allow", released_set=["B", "D"])
ev = contrib(d, store, tok, "crew-1", "c-t7d", "B")
check("T7 after the ruling, the re-judged allow releases",
      ev["type"] == "CONTRIBUTION" and d.state()["paused"] == {})

# -- T8: stop that part — a later ruling supersedes; history
# keeps both (G3).
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "C", "escalate", tree_part="C")
A(d, store, tok["dir-1"], "RULING",
  {"joint": "C", "action": "stop that part"})
check("T8 an allow is refused while the stop ruling governs",
      refused(lambda: outcome(d, store, tok, "C", "allow")))
A(d, store, tok["dir-1"], "RULING", {"joint": "C", "action": "proceed"})
outcome(d, store, tok, "C", "allow", released_set=["C"])
ev = contrib(d, store, tok, "crew-1", "c-t8", "C")
check("T8 the superseding ruling lets the allow release",
      ev["type"] == "CONTRIBUTION")
rulings = [r for r in d.state()["rulings"] if r.get("joint") == "C"]
check("T8 both rulings remain in history",
      len(rulings) == 2
      and rulings[0]["action"] == "stop that part")

# -- T9: declaration validation — an incomplete set derives its
# defect and does not open, even under an assembly allow.
bad = {"assembly": "assembly", "completion": "completion",
       "B": "judgement", "C": "judgement"}
store, d, tok = fresh(gates=bad)
gs = d.state()["gate_set"]
check("T9 the incomplete set is invalid, defect naming D",
      gs["declared"] and not gs["valid"]
      and any(d_.startswith("D:") for d_ in gs["defects"]))
outcome(d, store, tok, "assembly", "allow")
check("T9 an assembly allow over an invalid set does not open",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t9", "C")))
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "C", "allow")
ev = contrib(d, store, tok, "crew-1", "c-t9b", "C")
check("T9 a complete set opens the run", ev["type"] == "CONTRIBUTION")

# -- T10: the completion sequence.
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "B", "allow")
check("T10 CERTIFICATION refused before any completion allow",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"coverage": "full"})))
A(d, store, tok["crew-1"], "COMPLETION_CLAIMED", {"text": "done"})
outcome(d, store, tok, "completion", "correct")
check("T10 a completion correct leaves certification blocked",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"coverage": "full"})))
ev = contrib(d, store, tok, "crew-1", "c-t10", "B")
check("T10 a completion correct returns the run to work",
      ev["type"] == "CONTRIBUTION")
A(d, store, tok["crew-1"], "COMPLETION_CLAIMED", {"text": "done again"})
outcome(d, store, tok, "completion", "allow")
ev = A(d, store, tok["exam-1"], "CERTIFICATION", {"coverage": "full"})
check("T10 certification records after claim + allow",
      ev["type"] == "CERTIFICATION")
ev = A(d, store, tok["orch-1"], "RUN_CLOSED", {})
check("T10 closure records after claim + allow",
      ev["type"] == "RUN_CLOSED")

# -- T11: holder_unavailable — a distinct derived state; an
# ESCALATION at the same joint still pauses (the two differ).
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "C", "allow")
A(d, store, tok["orch-1"], "HOLDER_UNAVAILABLE", {"joint": "B"})
st = d.state()
check("T11 the declaration derives the waiting state",
      st["waiting"]["holder_unavailable"] == ["B"])
ev = contrib(d, store, tok, "crew-1", "c-t11", "C")
check("T11 it pauses nothing and involves no ruling",
      ev["type"] == "CONTRIBUTION" and st["paused"] == {}
      and st["rulings"] == [])
outcome(d, store, tok, "B", "allow")
check("T11 the joint's recorded outcome clears it",
      d.state()["waiting"]["holder_unavailable"] == [])
store, d, tok = fresh()
A(d, store, tok["crew-1"], "ESCALATION",
  {"joint": "B", "tree_part": "B"})
st = d.state()
check("T11 an ESCALATION still pauses — a distinct state",
      set(st["paused"]) == {"B", "D"}
      and st["waiting"]["holder_unavailable"] == [])

# -- T13: assembly release is fail-closed (correction 1).
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "correct")
check("T13 an assembly correct leaves the run unusable",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t13", "B")))
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "escalate")
check("T13 an assembly escalate leaves the run unusable",
      refused(lambda: contrib(d, store, tok, "crew-1", "c-t13b", "B")))

# -- T14: awaiting_gate tracks passage, not paperwork
# (correction 2).
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "B", "correct")
w = d.state()["waiting"]
check("T14 a gate holding on correct still awaits resolution",
      "B" in w["awaiting_gate"])
outcome(d, store, tok, "B", "escalate", tree_part="B")
w = d.state()["waiting"]
check("T14 an unruled escalation awaits a ruling, distinctly",
      "B" in w["awaiting_ruling"] and "B" not in w["awaiting_gate"])

# -- T15: completion binding — an allow is never reusable
# (correction 3).
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "completion", "allow")
check("T15 an allow before any claim authorizes nothing",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"coverage": "full"})))
A(d, store, tok["crew-1"], "COMPLETION_CLAIMED", {"text": "done"})
check("T15 the early allow does not answer the later claim",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"coverage": "full"})))
outcome(d, store, tok, "completion", "allow")
ev = A(d, store, tok["exam-1"], "CERTIFICATION", {"coverage": "full"})
check("T15 an allow after the claim authorizes certification",
      ev["type"] == "CERTIFICATION")
A(d, store, tok["crew-1"], "COMPLETION_CLAIMED", {"text": "again"})
check("T15 a second claim is not covered by the first allow",
      refused(lambda: A(d, store, tok["exam-1"], "CERTIFICATION",
                        {"coverage": "full"})))
outcome(d, store, tok, "completion", "allow")
ev = A(d, store, tok["exam-1"], "CERTIFICATION", {"coverage": "full"})
check("T15 a fresh allow answers the second claim",
      ev["type"] == "CERTIFICATION")

# -- T16: an unresolvable work act is refused fail-closed
# (correction 4); a comment on the job resolves to the job.
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
store.append("CONTRIBUTION", "crew-1", [], {
    "contribution_id": "c-nopart", "claim_id": "claim-np",
    "text": "recorded without a part"})
store.commit()
before = len(d.state()["rejections"])
check("T16 a disagreement on an unresolvable claim is refused",
      refused(lambda: A(d, store, tok["crew-2"], "DISAGREEMENT",
                        {"claim_id": "claim-np",
                         "disagreement_id": "d-np"})))
check("T16 the refusal is recorded",
      len(d.state()["rejections"]) == before + 1)
ev = A(d, store, tok["crew-1"], "COMMENT",
       {"on_job": True, "text": "job-level note"})
check("T16 a comment on the job itself records once open",
      ev["type"] == "COMMENT")

# -- T17: correct as stated — the re-judgement names its basis
# (G3's precision).
store, d, tok = fresh()
outcome(d, store, tok, "assembly", "allow")
outcome(d, store, tok, "B", "escalate", tree_part="B")
A(d, store, tok["dir-1"], "RULING",
  {"joint": "B", "action": "correct as stated"})
check("T17 a re-judgement naming no basis is refused",
      refused(lambda: outcome(d, store, tok, "B", "allow")))
corr = A(d, store, tok["crew-1"], "COMMENT",
         {"on_job": True, "text": "the stated correction"})
check("T17 a basis naming acts from before the ruling is refused",
      refused(lambda: outcome(d, store, tok, "B", "allow",
                              correction_basis=[1])))
ev = outcome(d, store, tok, "B", "allow",
             correction_basis=[corr["event_seq"]],
             released_set=["B", "D"])
check("T17 a basis naming the post-ruling acts records",
      ev["type"] == "GATE_OUTCOME"
      and ev["payload"]["correction_basis"] == [corr["event_seq"]])

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES:", *FAILURES, sep="\n  ")
    sys.exit(1)
print("ALL PASS")
