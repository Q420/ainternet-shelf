"""Piece 2 tests — record + doorway (SPEC SHEET §3.1–3.2, §7 items).

Run: PYTHONPATH=src python3 tests/unit/test_piece2_record_doorway.py
Exits 0 when every check passes.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "src"))

from framework.record import (FrameworkStore, CONSTITUTION_HASH, fold,
                              replay, state_hash, verify_chain)
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
            "dir-1": {"role": "director", "identity_status": "declared"},
        },
    })
    store.commit()
    d = Doorway(store)
    tok = {s: d.issue_token(s)
           for s in ("crew-a", "crew-b", "orch-1", "exam-1", "dir-1")}
    return store, d, tok


# ---------------------------------------------------------- R2: status
store, d, tok = fresh()
d.act(tok["crew-a"], "CONTRIBUTION",
      {"contribution_id": "c1", "claim_id": "claim-1",
       "tree_part": "part-B"})
st = d.state()
check("claim stands claimed on contribution",
      st["claims"]["claim-1"]["status"] == "claimed")

g = refused(lambda: d.act(tok["crew-a"], "CLAIM_STATUS",
                          {"claim_id": "claim-1", "to": "verified"}))
check("author promoting own claim to verified is refused", g is not None,
      g or "")
g = refused(lambda: d.act(tok["orch-1"], "CLAIM_STATUS",
                          {"claim_id": "claim-1", "to": "verified"}))
check("orchestrator promoting to verified is refused", g is not None)
rej = [r for r in d.state()["rejections"]
       if r["attempted"] == "CLAIM_STATUS"]
check("both refusals recorded as REJECTION events", len(rej) == 2)

g = refused(lambda: d.act(tok["exam-1"], "CLAIM_STATUS",
                          {"claim_id": "claim-1", "to": "verified"}))
check("examiner cannot verify a claim with no evidence",
      g is not None and "evidence" in g, g or "")

d.act(tok["crew-a"], "CLAIM_STATUS",
      {"claim_id": "claim-1", "to": "evidenced",
       "evidence": ["event:c1"]})
check("author attaching evidence moves claim to evidenced",
      d.state()["claims"]["claim-1"]["status"] == "evidenced")

d.act(tok["exam-1"], "CLAIM_STATUS",
      {"claim_id": "claim-1", "to": "verified"})
check("examiner verifies an evidenced claim",
      d.state()["claims"]["claim-1"]["status"] == "verified")

# disputed follows a recorded disagreement, never a direct transition
d.act(tok["crew-b"], "CONTRIBUTION",
      {"contribution_id": "c2", "claim_id": "claim-2",
       "tree_part": "part-B"})
g = refused(lambda: d.act(tok["crew-a"], "CLAIM_STATUS",
                          {"claim_id": "claim-2", "to": "disputed"}))
check("direct transition to disputed is refused", g is not None)
d.act(tok["orch-1"], "DISAGREEMENT",
      {"disagreement_id": "dg-1", "claim_id": "claim-2"})
check("recorded disagreement moves claim to disputed",
      d.state()["claims"]["claim-2"]["status"] == "disputed")
check("disagreement stands open",
      d.state()["disagreements"]["dg-1"]["status"] == "open")

# stood_down: author, or examiner at a gate — no one else
g = refused(lambda: d.act(tok["crew-a"], "CLAIM_STATUS",
                          {"claim_id": "claim-2", "to": "stood_down"}))
check("non-author standing down a claim is refused", g is not None)
g = refused(lambda: d.act(tok["exam-1"], "CLAIM_STATUS",
                          {"claim_id": "claim-2", "to": "stood_down"}))
check("examiner standing down away from a gate is refused",
      g is not None)
d.act(tok["exam-1"], "CLAIM_STATUS",
      {"claim_id": "claim-2", "to": "stood_down", "at_gate": True})
check("examiner at a gate stands the claim down",
      d.state()["claims"]["claim-2"]["status"] == "stood_down")

# ------------------------------------------------- R6/§4: authority
g = refused(lambda: d.act(tok["crew-a"], "FINDING", {"text": "x"}))
check("crew recording a finding is refused (matrix)", g is not None)
g = refused(lambda: d.act(tok["exam-1"], "RULING", {"text": "x"}))
check("examiner recording a ruling is refused (matrix)", g is not None)
d.act(tok["dir-1"], "RULING", {"text": "proceed"})
check("director records a ruling",
      len(d.state()["rulings"]) == 1)

# ---------------------------------------------------------- R5: binding
g = refused(lambda: d.act("bogus-token", "COMMENT", {"text": "hi"}))
check("unbound token is refused", g is not None and "R5" in g, g or "")
last_rej = d.state()["rejections"][-1]
check("unbound refusal is recorded naming no seat",
      last_rej["seat"] is None)

# ------------------------------------------------------- R7: boundary
d.act(tok["orch-1"], "MATERIAL_SEALED",
      {"material_id": "mat-1", "boundary": ["exam-1"]})
g = refused(lambda: d.read_sealed(tok["crew-a"], "mat-1"))
check("out-of-boundary read is refused", g is not None and "R7" in g,
      g or "")
ok = d.read_sealed(tok["exam-1"], "mat-1")
check("in-boundary read succeeds", ok["within_boundary"] is True)
check("the refused read is recorded",
      any(r["attempted"] == "READ_SEALED"
          for r in d.state()["rejections"]))

# ---------------------------------------------------------- R30: pause
d.act(tok["exam-1"], "GATE_OUTCOME",
      {"joint": "joint-1", "outcome": "hold",
       "paused_set": ["part-A"], "downstream": {"part-A": ["part-A1"]}})
g = refused(lambda: d.act(tok["crew-a"], "CONTRIBUTION",
                          {"contribution_id": "c3",
                           "tree_part": "part-A"}))
check("act on a paused part is blocked", g is not None and "R30" in g,
      g or "")
g = refused(lambda: d.act(tok["crew-a"], "CONTRIBUTION",
                          {"contribution_id": "c4",
                           "tree_part": "part-A1"}))
check("act on a downstream part is blocked", g is not None)
d.act(tok["crew-a"], "CONTRIBUTION",
      {"contribution_id": "c5", "tree_part": "part-B"})
check("act on an unrelated branch validates normally",
      "c5" in d.state()["contributions"])
check("paused set is recorded in state",
      "part-A" in d.state()["paused"])
d.act(tok["exam-1"], "GATE_OUTCOME",
      {"joint": "joint-1", "outcome": "allow",
       "released_set": ["part-A"]})
d.act(tok["crew-a"], "CONTRIBUTION",
      {"contribution_id": "c6", "tree_part": "part-A"})
check("released part acts again after allow",
      "c6" in d.state()["contributions"])

# ------------------------------------------------------- R31: staleness
head = store.head_seq()
d.act(tok["crew-b"], "COMMENT",
      {"subject_id": "c5", "text": "noted"}, view_seq=head)
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
