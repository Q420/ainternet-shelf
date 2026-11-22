"""Piece 2 tests — record + doorway (SPEC SHEET §3.1–3.2, §7 items).

Includes correction round 1 (Vane's examination, 2026-11-22): R1 run
binding, §4 comment/evidence authority, record-grounded gate for
stood_down, mandatory view position (R31), R22 outcome vocabulary.

Run: PYTHONPATH=src python3 tests/unit/test_piece2_record_doorway.py
Exits 0 when every check passes.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "src"))

from framework.record import (FrameworkStore, CONSTITUTION_HASH, fold,
                              replay, state_hash, verify_chain,
                              verify_run_binding)
from framework.doorway import Doorway, DoorwayRefusal

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


def refused(fn):
    try:
        fn()
        return None
    except DoorwayRefusal as r:
        return r.ground


def fresh():
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": ["part-A1"], "part-A1": [], "part-B": [],
                 "part-P": [], "part-Q": [], "part-Z": []},
        "seats": {
            "crew-a": {"role": "crew", "identity_status": "declared"},
            "crew-b": {"role": "crew", "identity_status": "declared"},
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner", "identity_status": "declared"},
            "exam-2": {"role": "examiner", "identity_status": "declared"},
            "dir-1": {"role": "director", "identity_status": "declared"},
        },
    })
    store.commit()
    d = Doorway(store)
    tok = {s: d.issue_token(s)
           for s in ("crew-a", "crew-b", "orch-1", "exam-1", "exam-2",
                     "dir-1")}
    return store, d, tok


def A(d, token, type_, payload):
    """Act from the current head view (R31: a view position always)."""
    return d.act(token, type_, payload, view_seq=d.store.head_seq())


store, d, tok = fresh()

# ---------------------------------------------------------- R1: binding
check("every event carries its run id (R1)",
      verify_run_binding(store.all_events(), "run-1"))

# ---------------------------------------------------------- R2: status
A(d, tok["crew-a"], "CONTRIBUTION",
  {"contribution_id": "c1", "claim_id": "claim-1", "tree_part": "part-B"})
st = d.state()
check("claim stands claimed on contribution",
      st["claims"]["claim-1"]["status"] == "claimed")

g = refused(lambda: A(d, tok["crew-a"], "CLAIM_STATUS",
                      {"claim_id": "claim-1", "to": "verified"}))
check("author promoting own claim to verified is refused",
      g is not None, g or "")
g = refused(lambda: A(d, tok["orch-1"], "CLAIM_STATUS",
                      {"claim_id": "claim-1", "to": "verified"}))
check("orchestrator promoting to verified is refused", g is not None)
rej = [r for r in d.state()["rejections"]
       if r["attempted"] == "CLAIM_STATUS"]
check("both refusals recorded as REJECTION events", len(rej) == 2)

g = refused(lambda: A(d, tok["exam-1"], "CLAIM_STATUS",
                      {"claim_id": "claim-1", "to": "verified"}))
check("examiner cannot verify a claim with no evidence",
      g is not None and "evidence" in g, g or "")

# Correction 3: evidence attachment is crew's act alone (§4).
g = refused(lambda: A(d, tok["exam-1"], "CLAIM_STATUS",
                      {"claim_id": "claim-1", "to": "evidenced",
                       "evidence": ["event:c1"]}))
check("examiner attaching evidence is refused (matrix)",
      g is not None and "crew" in g, g or "")

A(d, tok["crew-a"], "CLAIM_STATUS",
  {"claim_id": "claim-1", "to": "evidenced", "evidence": ["event:c1"]})
check("author attaching evidence moves claim to evidenced",
      d.state()["claims"]["claim-1"]["status"] == "evidenced")

A(d, tok["exam-1"], "CLAIM_STATUS",
  {"claim_id": "claim-1", "to": "verified"})
check("examiner verifies an evidenced claim",
      d.state()["claims"]["claim-1"]["status"] == "verified")

# disputed follows a recorded disagreement, never a direct transition
A(d, tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "c2", "claim_id": "claim-2", "tree_part": "part-B"})
g = refused(lambda: A(d, tok["crew-a"], "CLAIM_STATUS",
                      {"claim_id": "claim-2", "to": "disputed"}))
check("direct transition to disputed is refused", g is not None)
A(d, tok["orch-1"], "DISAGREEMENT",
  {"disagreement_id": "dg-1", "claim_id": "claim-2"})
check("recorded disagreement moves claim to disputed",
      d.state()["claims"]["claim-2"]["status"] == "disputed")
check("disagreement stands open",
      d.state()["disagreements"]["dg-1"]["status"] == "open")

# stood_down: author, or examiner at a gate — the gate grounded in
# the record (correction 4), never a caller-supplied flag.
g = refused(lambda: A(d, tok["crew-a"], "CLAIM_STATUS",
                      {"claim_id": "claim-2", "to": "stood_down"}))
check("non-author standing down a claim is refused", g is not None)
g = refused(lambda: A(d, tok["exam-1"], "CLAIM_STATUS",
                      {"claim_id": "claim-2", "to": "stood_down"}))
check("examiner standing down with no gate named is refused",
      g is not None)
g = refused(lambda: A(d, tok["exam-1"], "CLAIM_STATUS",
                      {"claim_id": "claim-2", "to": "stood_down",
                       "gate_joint": "joint-never-held"}))
check("examiner naming an unrecorded gate is refused",
      g is not None and "record" in g, g or "")
A(d, tok["exam-2"], "GATE_OUTCOME",
  {"joint": "joint-g1", "outcome": "allow"})
g = refused(lambda: A(d, tok["exam-1"], "CLAIM_STATUS",
                      {"claim_id": "claim-2", "to": "stood_down",
                       "gate_joint": "joint-g1"}))
check("a gate recorded by another examiner does not ground it",
      g is not None)
A(d, tok["exam-1"], "GATE_OUTCOME",
  {"joint": "joint-g2", "outcome": "correct"})
A(d, tok["exam-1"], "CLAIM_STATUS",
  {"claim_id": "claim-2", "to": "stood_down", "gate_joint": "joint-g2"})
check("examiner at her own recorded gate stands the claim down",
      d.state()["claims"]["claim-2"]["status"] == "stood_down")
A(d, tok["crew-a"], "CONTRIBUTION",
  {"contribution_id": "c2b", "claim_id": "claim-2b",
   "tree_part": "part-B"})
A(d, tok["crew-a"], "CLAIM_STATUS",
  {"claim_id": "claim-2b", "to": "stood_down"})
check("the claim's author stands it down",
      d.state()["claims"]["claim-2b"]["status"] == "stood_down")

# ------------------------------------------------- R6/§4: authority
g = refused(lambda: A(d, tok["crew-a"], "FINDING", {"text": "x"}))
check("crew recording a finding is refused (matrix)", g is not None)
g = refused(lambda: A(d, tok["exam-1"], "RULING", {"text": "x"}))
check("examiner recording a ruling is refused (matrix)", g is not None)
A(d, tok["dir-1"], "RULING", {"text": "proceed"})
check("director records a ruling", len(d.state()["rulings"]) == 1)
# Correction 2: comment authority is crew's alone (§4).
g = refused(lambda: A(d, tok["orch-1"], "COMMENT", {"text": "hi"}))
check("orchestrator commenting is refused (matrix)",
      g is not None and "§4" in g, g or "")
g = refused(lambda: A(d, tok["exam-1"], "COMMENT", {"text": "hi"}))
check("examiner commenting is refused (matrix)", g is not None)

# ---------------------------------------------------------- R5: binding
g = refused(lambda: A(d, "bogus-token", "COMMENT", {"text": "hi"}))
check("unbound token is refused", g is not None and "R5" in g, g or "")
last_rej = d.state()["rejections"][-1]
check("unbound refusal is recorded naming no seat",
      last_rej["seat"] is None)

# ------------------------------------------- R31: view position (corr. 5)
n_rej = len(d.state()["rejections"])
g = refused(lambda: d.act(tok["crew-a"], "COMMENT", {"text": "x"}))
check("an act with no view position is refused",
      g is not None and "R31" in g, g or "")
check("the no-view refusal is recorded",
      len(d.state()["rejections"]) == n_rej + 1)
g = refused(lambda: d.act(tok["crew-a"], "COMMENT", {"text": "x"},
                          view_seq=10 ** 6))
check("a view position beyond the head is refused",
      g is not None and "R31" in g, g or "")

# ------------------------------------------------------- R7: boundary
A(d, tok["orch-1"], "MATERIAL_SEALED",
  {"material_id": "mat-1", "boundary": ["exam-1"]})
g = refused(lambda: d.read_sealed(tok["crew-a"], "mat-1"))
check("out-of-boundary read is refused", g is not None and "R7" in g,
      g or "")
ok = d.read_sealed(tok["exam-1"], "mat-1")
check("in-boundary read succeeds", ok["within_boundary"] is True)
check("the refused read is recorded",
      any(r["attempted"] == "READ_SEALED"
          for r in d.state()["rejections"]))

# ------------------------------------- R22/R30: outcomes and the pause
# Correction 6: "hold" is not an outcome; an escalation records the
# pause (R30), an allow releases it. The pause's set is computed from
# the commissioned tree (round 2); the act names the affected part.
g = refused(lambda: A(d, tok["exam-1"], "GATE_OUTCOME",
                      {"joint": "joint-1", "outcome": "hold"}))
check("gate outcome 'hold' is refused (R22 vocabulary)",
      g is not None and "R22" in g, g or "")
A(d, tok["exam-1"], "GATE_OUTCOME",
  {"joint": "joint-1", "outcome": "escalate", "tree_part": "part-A"})
g = refused(lambda: A(d, tok["crew-a"], "CONTRIBUTION",
                      {"contribution_id": "c3", "tree_part": "part-A"}))
check("act on a paused part is blocked", g is not None and "R30" in g,
      g or "")
g = refused(lambda: A(d, tok["crew-a"], "CONTRIBUTION",
                      {"contribution_id": "c4", "tree_part": "part-A1"}))
check("act on a downstream part is blocked", g is not None)
A(d, tok["crew-a"], "CONTRIBUTION",
  {"contribution_id": "c5", "tree_part": "part-B"})
check("act on an unrelated branch validates normally",
      "c5" in d.state()["contributions"])
check("paused set is recorded in state", "part-A" in d.state()["paused"])
A(d, tok["exam-1"], "GATE_OUTCOME",
  {"joint": "joint-1", "outcome": "allow",
   "released_set": ["part-A", "part-A1"]})
A(d, tok["crew-a"], "CONTRIBUTION",
  {"contribution_id": "c6", "tree_part": "part-A"})
check("released part acts again after allow",
      "c6" in d.state()["contributions"])

# ------------------------------------------------------- R31: staleness
head = store.head_seq()
A(d, tok["crew-b"], "COMMENT", {"subject_id": "c5", "text": "noted"})
ev = store.all_events()[-1]
check("current-view act carries no stale flag",
      "stale_basis" not in ev["payload"])
old_view = head  # c5's subject was touched by the comment above
g = refused(lambda: d.act(tok["crew-a"], "COMMENT",
                          {"subject_id": "c5", "text": "reply"},
                          view_seq=old_view))
check("act on a subject changed since its view is refused",
      g is not None and "R31" in g, g or "")
d.act(tok["crew-a"], "COMMENT",
      {"subject_id": "c6", "text": "fresh subject, old view"},
      view_seq=old_view)
ev = store.all_events()[-1]
check("behind-view act on an unchanged subject is flagged stale-basis",
      ev["payload"].get("stale_basis") is True)

# --------------------------------------- correction round 2 (Vane)
# Gap 1 (R1): a commissioning payload naming a different run than the
# event's own run is refused at append; the fold reports the event's
# run, never the payload's.
s2, d2, t2 = fresh()
n_events = len(s2.all_events())
try:
    s2.append("RUN_COMMISSIONED", "dir-1", [],
              {"run_id": "run-OTHER", "seats": {}})
    mismatch_appended = True
except AssertionError:
    mismatch_appended = False
check("a commission naming a different run is refused at append (R1)",
      not mismatch_appended and len(s2.all_events()) == n_events)
from framework.record import apply_event, empty_state
crafted = {"event_seq": 1, "event_id": "x", "run_id": "run-1",
           "type": "RUN_COMMISSIONED", "actor": "dir-1", "affected": [],
           "payload": {"run_id": "run-OTHER", "seats": {}},
           "ts": "t", "prev_hash": "", "hash": "h"}
check("the fold reports the event's run, not the payload's (R1)",
      apply_event(empty_state(), crafted)["run_id"] == "run-1")

# Gap 2 (R30): with a tree in the record, the paused set is computed
# from it — a supplied set that disagrees is refused; the computed set
# (part + transitive downstream) is what is recorded and enforced.
path3 = os.path.join(tempfile.mkdtemp(), "run.db")
s3 = FrameworkStore(path3)
s3.insert_run("run-1", CONSTITUTION_HASH)
s3.append("RUN_COMMISSIONED", "dir-1", [], {
    "run_id": "run-1",
    "tree": {"part-A": ["part-A1"], "part-A1": ["part-A2"],
             "part-B": []},
    "seats": {
        "crew-a": {"role": "crew", "identity_status": "declared"},
        "exam-1": {"role": "examiner", "identity_status": "declared"},
    },
})
s3.commit()
d3 = Doorway(s3)
tk3 = {s: d3.issue_token(s) for s in ("crew-a", "exam-1")}
g = refused(lambda: A(d3, tk3["exam-1"], "GATE_OUTCOME",
                      {"joint": "j-tree", "outcome": "escalate",
                       "tree_part": "part-A",
                       "paused_set": ["part-A"]}))
check("a supplied paused set missing downstream is refused (R30)",
      g is not None and "computed" in g, g or "")
A(d3, tk3["exam-1"], "GATE_OUTCOME",
  {"joint": "j-tree", "outcome": "escalate", "tree_part": "part-A"})
paused_ev = s3.all_events()[-1]
check("the recorded paused set is computed from the tree (R30)",
      paused_ev["payload"]["paused_set"] ==
      ["part-A", "part-A1", "part-A2"] and
      paused_ev["payload"]["paused_set_basis"] ==
      "computed_from_recorded_tree")
g = refused(lambda: A(d3, tk3["crew-a"], "CONTRIBUTION",
                      {"contribution_id": "cx", "tree_part": "part-A2"}))
check("a transitive downstream part is blocked (R30)", g is not None)
A(d3, tk3["crew-a"], "CONTRIBUTION",
  {"contribution_id": "cy", "tree_part": "part-B"})
check("an unrelated branch still validates (R30)",
      "cy" in d3.state()["contributions"])

# Gap 3 (R31): staleness covers the tree part and the case — an act
# from a view predating a change to either is refused.
s4, d4, t4 = fresh()
A(d4, t4["orch-1"], "CASE_ISSUED",
  {"case_id": "case-1", "version": 1, "seat": "crew-a"})
view_before = s4.head_seq()
A(d4, t4["orch-1"], "CASE_CORRECTED",
  {"case_id": "case-1", "version": 2, "seat": "crew-a"})
g = refused(lambda: d4.act(t4["crew-a"], "COMMENT",
                           {"case_id": "case-1", "text": "on the case"},
                           view_seq=view_before))
check("an act on a case changed since its view is refused (R31)",
      g is not None and "R31" in g, g or "")
A(d4, t4["crew-a"], "CONTRIBUTION",
  {"contribution_id": "cz", "tree_part": "part-Z"})
view_before = s4.head_seq()
A(d4, t4["crew-b"], "CONTRIBUTION",
  {"contribution_id": "cz2", "tree_part": "part-Z"})
g = refused(lambda: d4.act(t4["crew-a"], "COMMENT",
                           {"tree_part": "part-Z", "text": "on the part"},
                           view_seq=view_before))
check("an act on a tree part changed since its view is refused (R31)",
      g is not None and "R31" in g, g or "")

# --------------------------------------- correction round 3 (Vane)
# Her second examination of c2949563 (five points): points 1 and 3
# and the subject coverage of 4 were already closed by round 2 at
# 981a0a96; this round closes release binding, negative view
# positions, set-membership staleness, and the jointed pause.
s5, d5, t5 = fresh()
g = refused(lambda: d5.act(t5["crew-a"], "COMMENT", {"text": "x"},
                           view_seq=-1))
check("a negative view position is refused (R31)",
      g is not None and "R31" in g, g or "")

A(d5, t5["exam-1"], "GATE_OUTCOME",
  {"joint": "j-one", "outcome": "escalate", "tree_part": "part-P"})
g = refused(lambda: A(d5, t5["exam-1"], "GATE_OUTCOME",
                      {"joint": "j-two", "outcome": "allow",
                       "released_set": ["part-P"]}))
check("an allow at another joint cannot release the pause (R30)",
      g is not None and "not bound" in g, g or "")
check("the pause survives the unbound release attempt",
      "part-P" in d5.state()["paused"])
g = refused(lambda: A(d5, t5["crew-a"], "CONTRIBUTION",
                      {"contribution_id": "cp", "tree_part": "part-P"}))
check("the part is still blocked after the unbound release",
      g is not None)
g = refused(lambda: A(d5, t5["exam-1"], "GATE_OUTCOME",
                      {"joint": "j-one", "outcome": "allow",
                       "released_set": ["part-never"]}))
check("releasing a part that is not paused is refused (R30)",
      g is not None)
A(d5, t5["exam-1"], "GATE_OUTCOME",
  {"joint": "j-one", "outcome": "allow", "released_set": ["part-P"]})
check("an allow at the pausing joint releases it",
      "part-P" not in d5.state()["paused"])

g = refused(lambda: A(d5, t5["crew-a"], "ESCALATION",
                      {"paused_set": ["part-Q"],
                       "tree_part": "part-Q"}))
check("a pause recorded without its joint is refused (R30)",
      g is not None and "joint" in g, g or "")

view_q = s5.head_seq()
A(d5, t5["exam-1"], "GATE_OUTCOME",
  {"joint": "j-nine", "outcome": "escalate", "tree_part": "part-Q"})
g = refused(lambda: d5.act(t5["crew-a"], "COMMENT",
                           {"subject_id": "part-Q", "text": "about Q"},
                           view_seq=view_q))
check("an act on a subject touched only via a recorded paused set "
      "is refused (R31)", g is not None and "R31" in g, g or "")

# --------------------------------------- correction round 4 (Vane)
# The one remaining defect: the no-tree fallback. With no tree in
# the record, a pause cannot have its set computed — the doorway
# fails closed and records the rejection. A caller-supplied set is
# not a substitute, labelled or not.
path6 = os.path.join(tempfile.mkdtemp(), "run.db")
s6 = FrameworkStore(path6)
s6.insert_run("run-1", CONSTITUTION_HASH)
s6.append("RUN_COMMISSIONED", "dir-1", [], {
    "run_id": "run-1",
    "seats": {
        "crew-a": {"role": "crew", "identity_status": "declared"},
        "exam-1": {"role": "examiner", "identity_status": "declared"},
    },
})
s6.commit()
d6 = Doorway(s6)
t6 = {s: d6.issue_token(s) for s in ("crew-a", "exam-1")}
g = refused(lambda: A(d6, t6["exam-1"], "GATE_OUTCOME",
                      {"joint": "j-x", "outcome": "escalate",
                       "paused_set": ["part-A"],
                       "downstream": {"part-A": []}}))
check("a pause with a caller-supplied set and no tree is refused "
      "(R30)", g is not None and "no tree" in g, g or "")
g = refused(lambda: A(d6, t6["exam-1"], "GATE_OUTCOME",
                      {"joint": "j-x", "outcome": "escalate",
                       "tree_part": "part-A"}))
check("a pause naming a part with no tree to compute from is "
      "refused (R30)", g is not None and "no tree" in g, g or "")
check("no paused state was established by the refused pauses",
      d6.state()["paused"] == {})
check("both no-tree refusals are recorded",
      len([r for r in d6.state()["rejections"]
           if r["attempted"] == "GATE_OUTCOME"]) == 2)
A(d6, t6["crew-a"], "ESCALATION", {"joint": "j-x", "note": "a "
                                   "question, pausing nothing"})
check("an escalation that pauses nothing still records with no "
      "tree", len(d6.state()["escalations"]) == 1)

# --------------------------------------- correction round 5 (Vane)
# The named root must be established by the recorded tree: a pause
# naming a part the tree does not contain is refused and recorded.
# A leaf that appears only as a recorded downstream still counts —
# it is established by the tree.
path7 = os.path.join(tempfile.mkdtemp(), "run.db")
s7 = FrameworkStore(path7)
s7.insert_run("run-1", CONSTITUTION_HASH)
s7.append("RUN_COMMISSIONED", "dir-1", [], {
    "run_id": "run-1",
    "tree": {"root-1": ["leaf-1"], "root-2": []},
    "seats": {
        "crew-a": {"role": "crew", "identity_status": "declared"},
        "exam-1": {"role": "examiner", "identity_status": "declared"},
    },
})
s7.commit()
d7 = Doorway(s7)
t7 = {s: d7.issue_token(s) for s in ("crew-a", "exam-1")}
g = refused(lambda: A(d7, t7["exam-1"], "GATE_OUTCOME",
                      {"joint": "j-g", "outcome": "escalate",
                       "tree_part": "ghost-part"}))
check("a pause naming a part absent from the tree is refused (R30)",
      g is not None and "not in the recorded tree" in g, g or "")
check("the ghost pause established no paused state",
      d7.state()["paused"] == {})
A(d7, t7["exam-1"], "GATE_OUTCOME",
  {"joint": "j-g", "outcome": "escalate", "tree_part": "leaf-1"})
leaf_ev = s7.all_events()[-1]
check("a leaf established only as a downstream can be paused, "
      "computed set is itself (R30)",
      leaf_ev["payload"]["paused_set"] == ["leaf-1"])
g = refused(lambda: A(d7, t7["crew-a"], "CONTRIBUTION",
                      {"contribution_id": "cl", "tree_part": "leaf-1"}))
check("the leaf part is blocked once paused (R30)", g is not None)

# --------------------------------------- correction round 6 (Vane)
# A pause-less escalation records normally whether or not a tree is
# present (round 4 established it with no tree; the tree branch must
# not refuse it). A pause-bearing act under a tree still requires
# the named, validated part. (d7/s7 carry a recorded tree; leaf-1
# stands paused from round 5.)
n_esc = len(d7.state()["escalations"])
A(d7, t7["crew-a"], "ESCALATION",
  {"joint": "j-q", "note": "a question, pausing nothing"})
check("a pause-less escalation records normally with a tree "
      "present (R30)", len(d7.state()["escalations"]) == n_esc + 1)
check("the pause-less escalation paused nothing new",
      set(d7.state()["paused"]) == {"leaf-1"})
A(d7, t7["exam-1"], "GATE_OUTCOME",
  {"joint": "j-q", "outcome": "escalate"})
check("an escalate outcome pausing nothing records with a tree "
      "present (R30)", set(d7.state()["paused"]) == {"leaf-1"})
g = refused(lambda: A(d7, t7["exam-1"], "GATE_OUTCOME",
                      {"joint": "j-q", "outcome": "escalate",
                       "paused_set": ["root-1"]}))
check("a pause-bearing act under a tree still requires the named "
      "part (R30)", g is not None and "names the affected" in g,
      g or "")

# ------------------------------------------------------------ R4: replay
events = store.all_events()
check("hash chain verifies", verify_chain(events))
check("run binding still verifies over the whole history",
      verify_run_binding(events, "run-1"))
h1 = state_hash(fold(events, "run-1"))
store2 = FrameworkStore(store.path)
h2 = state_hash(replay(store2))
check("replay from a reopened store reproduces state exactly", h1 == h2)
check("every event carries a timestamp (R1)",
      all(ev["ts"] for ev in events))

print()
if FAILURES:
    print(f"PIECE 2 TESTS: {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("PIECE 2 TESTS: ALL PASS")
