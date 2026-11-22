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
# pause (R30), an allow releases it.
g = refused(lambda: A(d, tok["exam-1"], "GATE_OUTCOME",
                      {"joint": "joint-1", "outcome": "hold"}))
check("gate outcome 'hold' is refused (R22 vocabulary)",
      g is not None and "R22" in g, g or "")
A(d, tok["exam-1"], "GATE_OUTCOME",
  {"joint": "joint-1", "outcome": "escalate",
   "paused_set": ["part-A"], "downstream": {"part-A": ["part-A1"]}})
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
  {"joint": "joint-1", "outcome": "allow", "released_set": ["part-A"]})
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
