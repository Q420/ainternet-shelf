"""Piece 4 tests — live seat drivers (SPEC SHEET §3.4, R11–R13,
with R15/R16 issuance, R32 acknowledgement, R33 seat_stalled).

Run: PYTHONPATH=src python3 tests/unit/test_piece4_driver.py
Exits 0 when every check passes.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "src"))

from framework.record import FrameworkStore, CONSTITUTION_HASH, fold
from framework.doorway import Doorway
from framework.driver import Driver

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


class ScriptedModel:
    def __init__(self, response=None):
        self.response = response if response is not None else []
        self.calls = []

    def __call__(self, package):
        self.calls.append(package)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


path = os.path.join(tempfile.mkdtemp(), "run.db")
store = FrameworkStore(path)
store.insert_run("run-1", CONSTITUTION_HASH)
store.append("RUN_COMMISSIONED", "dir-1", [], {
    "run_id": "run-1",
    "tree": {"part-A": [], "part-B": []},
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


def A(token, type_, payload):
    return d.act(token, type_, payload, view_seq=store.head_seq())


CASE_A = {"case_id": "case-a", "version": 1, "seat": "crew-a",
          "part": "part-A", "assignment": "Draft the A section",
          "evidence_boundary": ["mat-1"],
          "verification_list": ["check the figures"],
          "account": "crew-a", "authority": "crew defaults"}

model_a = ScriptedModel()
driver_a = Driver(d, "crew-a", tok["crew-a"], model_a)

# ------------------------------------------- R15: issuance route
A(tok["orch-1"], "CASE_VERIFIED", {"case_id": "case-a", "version": 1})
r = driver_a.wake_cycle()
check("no wake on a case with only verification standing",
      r["woke"] is False and model_a.calls == [])
A(tok["exam-1"], "CASE_JUDGED", {"case_id": "case-a", "version": 1})
r = driver_a.wake_cycle()
check("no wake before authorisation, CASE_ISSUED absent",
      r["woke"] is False and model_a.calls == [])
A(tok["orch-1"], "CASE_ISSUED", dict(CASE_A))
model_a.response = [{"type": "CONTRIBUTION", "payload": {
    "contribution_id": "c1", "claim_id": "claim-1",
    "tree_part": "part-A", "text": "A, first draft"}}]
r = driver_a.wake_cycle()
check("a fully-issued case wakes the model", r["woke"] is True)
pkg = model_a.calls[-1]
check("the wake package carries the case as recorded",
      pkg["case"]["assignment"] == "Draft the A section" and
      pkg["case_version"] == 1)
check("the initial prompt is the assignment itself",
      [x["kind"] for x in pkg["prompt"]["reasons"]] == ["assignment"])
check("the model never receives the seat's token (R12)",
      tok["crew-a"] not in json.dumps(pkg))
check("proposed acts return through the doorway, case-stamped",
      r["recorded"] and r["recorded"][0]["type"] == "CONTRIBUTION"
      and r["recorded"][0]["actor"] == "crew-a" and
      r["recorded"][0]["payload"]["case_version"] == 1)
r = driver_a.wake_cycle()
check("no second wake on the same recorded events",
      r["woke"] is False)

# ------------------------------------- R11: relevance of triggers
A(tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "cb1", "tree_part": "part-B", "text": "B work"})
r = driver_a.wake_cycle()
check("another part's contribution does not wake this seat",
      r["woke"] is False)
A(tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "cb2", "tree_part": "part-A",
   "text": "B's take on A"})
model_a.response = [{"type": "COMMENT", "payload": {
    "contribution_id": "cb2", "text": "noted"}}]
r = driver_a.wake_cycle()
check("a contribution on the seat's part wakes it, to answer",
      r["woke"] is True and
      "contribution_to_answer" in
      [x["kind"] for x in r["reasons"]])
A(tok["crew-b"], "COMMENT",
  {"contribution_id": "c1", "text": "tighten the intro"})
model_a.response = []
r = driver_a.wake_cycle()
check("a comment on the seat's own contribution wakes it",
      r["woke"] is True and
      "comment_on_your_contribution" in
      [x["kind"] for x in r["reasons"]])

# --------------------------- R11: the case's evidence boundary
A(tok["orch-1"], "MATERIAL_SEALED",
  {"material_id": "mat-1", "boundary": ["crew-a", "exam-1"]})
A(tok["orch-1"], "MATERIAL_SEALED",
  {"material_id": "mat-2", "boundary": ["crew-a"]})
A(tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "cb3", "tree_part": "part-A", "text": "more A"})
model_a.response = []
r = driver_a.wake_cycle()
pkg = model_a.calls[-1]
sealed_ids = [s["material_id"] for s in pkg["view"]["sealed"]]
check("the wake view honours the case's evidence boundary",
      sealed_ids == ["mat-1"], str(sealed_ids))

# ------------------------------------- R12: authority at the door
model_a.response = [{"type": "GATE_OUTCOME", "payload": {
    "joint": "joint-1", "outcome": "allow"}}]
A(tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "cb4", "tree_part": "part-A", "text": "A again"})
r = driver_a.wake_cycle()
check("a proposal outside the seat's authority is refused at the "
      "doorway, not recorded",
      r["recorded"] == [] and r["refused"] and
      "§4" in r["refused"][0]["ground"])

# --------------------------- R16/R32: correction, acknowledgement
A(tok["orch-1"], "CASE_CORRECTED",
  dict(CASE_A, version=2, assignment="Draft A, revised",
       representational=False))
A(tok["orch-1"], "CASE_VERIFIED", {"case_id": "case-a", "version": 2})
A(tok["orch-1"], "CASE_ISSUED",
  {"case_id": "case-a", "version": 2, "seat": "crew-a"})
A(tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "cb5", "tree_part": "part-A", "text": "A v2 era"})
model_a.response = []
r = driver_a.wake_cycle()
check("an incompletely-issued correction does not displace the "
      "standing case", r["woke"] is True and
      model_a.calls[-1]["case_version"] == 1)
A(tok["exam-1"], "CASE_JUDGED", {"case_id": "case-a", "version": 2})
model_a.response = [{"type": "CONTRIBUTION", "payload": {
    "contribution_id": "c9", "tree_part": "part-A",
    "text": "work on v2 without acknowledging"}}]
r = driver_a.wake_cycle()
check("R32: work on an unacknowledged new version is held, "
      "nothing recorded", r["recorded"] == [] and
      r["held"] == ["CONTRIBUTION"])
model_a.response = [
    {"type": "CONTRIBUTION", "payload": {
        "contribution_id": "c10", "tree_part": "part-A",
        "text": "work under v2"}},
    {"type": "CASE_ACKNOWLEDGED", "payload": {
        "case_id": "case-a", "version": 2}},
]
r = driver_a.wake_cycle()
check("the seat's own acknowledgement is carried, recorded before "
      "its other acts",
      [e["type"] for e in r["recorded"]] ==
      ["CASE_ACKNOWLEDGED", "CONTRIBUTION"] and
      r["recorded"][1]["payload"]["case_version"] == 2)

# --------------------- R16: the representational route, by record
A(tok["orch-1"], "CASE_CORRECTED",
  dict(CASE_A, version=3, assignment="Draft A, revised",
       representational=True))
A(tok["orch-1"], "CASE_VERIFIED", {"case_id": "case-a", "version": 3})
A(tok["exam-1"], "CASE_NOTIFIED", {"case_id": "case-a", "version": 3})
A(tok["orch-1"], "CASE_ISSUED",
  {"case_id": "case-a", "version": 3, "seat": "crew-a"})
model_a.response = [{"type": "CASE_ACKNOWLEDGED", "payload": {
    "case_id": "case-a", "version": 3}}]
r = driver_a.wake_cycle()
check("a representational correction issues on verification + "
      "notification + authorisation (no judgement)",
      r["woke"] is True and
      model_a.calls[-1]["case_version"] == 3 and
      r["recorded"][0]["type"] == "CASE_ACKNOWLEDGED")
A(tok["orch-1"], "CASE_CORRECTED",
  dict(CASE_A, version=4, assignment="Draft A, re-scoped",
       representational=False))
A(tok["orch-1"], "CASE_VERIFIED", {"case_id": "case-a", "version": 4})
A(tok["exam-1"], "CASE_NOTIFIED", {"case_id": "case-a", "version": 4})
A(tok["orch-1"], "CASE_ISSUED",
  {"case_id": "case-a", "version": 4, "seat": "crew-a"})
A(tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "cb6", "tree_part": "part-A", "text": "A v4 era"})
model_a.response = []
r = driver_a.wake_cycle()
check("a semantic correction is not issued by the notification "
      "route (route follows the recorded classification)",
      r["woke"] is True and model_a.calls[-1]["case_version"] == 3)

# ------------------------------------------- R13/R33: failures
CASE_B = {"case_id": "case-b", "version": 1, "seat": "crew-b",
          "part": "part-B", "assignment": "Draft the B section",
          "account": "crew-b", "authority": "crew defaults"}
A(tok["orch-1"], "CASE_VERIFIED", {"case_id": "case-b", "version": 1})
A(tok["exam-1"], "CASE_JUDGED", {"case_id": "case-b", "version": 1})
A(tok["orch-1"], "CASE_ISSUED", dict(CASE_B))
bad = ScriptedModel(RuntimeError("provider down"))
driver_b = Driver(d, "crew-b", tok["crew-b"], bad)
r = driver_b.wake_cycle()
check("a provider error is a recorded driver failure",
      r["failed"] == "provider_error")
state = fold(store.all_events())
fail_ev = store.all_events()[r["failure_event"] - 1]
check("the failure event is doorway-authored, naming seat and kind",
      fail_ev["type"] == "DRIVER_FAILURE" and
      fail_ev["actor"] == "doorway" and
      fail_ev["payload"]["seat"] == "crew-b" and
      fail_ev["payload"]["origin"] == "driver_report")
check("the seat stands seat_stalled; no pause tree is created",
      state["stalled"]["crew-b"]["kind"] == "provider_error" and
      state["paused"] == {})
check("no contribution was fabricated for the stalled seat",
      all(info["author"] != "crew-b" or
          cid in ("cb1", "cb2", "cb3", "cb4", "cb5", "cb6")
          for cid, info in state["contributions"].items()))
r = driver_b.wake_cycle()
check("a stalled seat is not woken again",
      r["woke"] is False and "stalled" in r)
view_b = fold(store.all_events())
from framework.bubble import render_view
vb = render_view(store.all_events(), "exam-1")
check("the bubble renders the stalled seat by its state",
      vb["current_state"]["stalled_seats"]["crew-b"]["kind"] ==
      "provider_error")

model_a.response = "not a list of acts"
A(tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "cb7", "tree_part": "part-A", "text": "wake A"})
r = driver_a.wake_cycle()
check("malformed model output is a recorded driver failure",
      r["failed"] == "malformed_output" and
      fold(store.all_events())["stalled"]["crew-a"]["kind"] ==
      "malformed_output")

print()
if FAILURES:
    print(f"PIECE 4 TESTS: {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("PIECE 4 TESTS: ALL PASS")
