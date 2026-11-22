"""Piece 3 tests — the bubble (SPEC SHEET §3.3, R8–R10).

Run: PYTHONPATH=src python3 tests/unit/test_piece3_bubble.py
Exits 0 when every check passes.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "src"))

from framework.record import FrameworkStore, CONSTITUTION_HASH
from framework.doorway import Doorway, DoorwayRefusal
from framework.bubble import BubbleRefusal, post_comment, render_view

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


def refused(fn, exc=DoorwayRefusal):
    try:
        fn()
        return None
    except exc as r:
        return r.ground


path = os.path.join(tempfile.mkdtemp(), "run.db")
store = FrameworkStore(path)
store.insert_run("run-1", CONSTITUTION_HASH)
store.append("RUN_COMMISSIONED", "dir-1", [], {
    "run_id": "run-1",
    "tree": {"part-A": ["part-A1"], "part-A1": [], "part-B": []},
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


A(tok["crew-a"], "CONTRIBUTION",
  {"contribution_id": "c1", "claim_id": "claim-1",
   "tree_part": "part-A", "text": "first draft of A"})
A(tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "c2", "tree_part": "part-B",
   "text": "B sketched"})
A(tok["crew-b"], "COMMENT",
  {"contribution_id": "c1", "text": "tighten the second paragraph"})
A(tok["crew-a"], "COMMENT", {"on_job": True, "text": "job note"})
A(tok["orch-1"], "DISAGREEMENT",
  {"disagreement_id": "dg-1", "claim_id": "claim-1"})
A(tok["exam-1"], "GATE_OUTCOME",
  {"joint": "joint-1", "outcome": "escalate", "tree_part": "part-B"})
A(tok["orch-1"], "MATERIAL_SEALED",
  {"material_id": "mat-1", "boundary": ["exam-1"]})

events = store.all_events()
view = render_view(events, "crew-a")

# ------------------------------------------------------------- R8
check("view position is the record head",
      view["position"] == store.head_seq())
parts = {p["part"]: p for p in view["tree"]}
check("tree renders every recorded part",
      set(parts) == {"part-A", "part-A1", "part-B"})
check("a contributed part renders contributed",
      parts["part-A"]["state"] == "contributed")
check("a paused part renders paused, naming its joint",
      parts["part-B"]["state"] == "paused" and
      parts["part-B"]["paused_by_joint"] == "joint-1")
check("an untouched part renders open",
      parts["part-A1"]["state"] == "open")
check("contributions render in record order",
      [c["contribution_id"] for c in view["contributions"]] ==
      ["c1", "c2"])
c1 = view["contributions"][0]
check("a contribution carries its claim and the claim's status",
      c1["claim"]["claim_id"] == "claim-1" and
      c1["claim"]["status"] == "disputed")
check("a comment renders attached to the contribution it answers",
      len(c1["comments"]) == 1 and
      c1["comments"][0]["text"] == "tighten the second paragraph")
check("a job comment renders under the job, not a contribution",
      len(view["job_comments"]) == 1 and
      view["job_comments"][0]["text"] == "job note")
check("disagreements render with their status",
      view["disagreements"][0]["disagreement_id"] == "dg-1" and
      view["disagreements"][0]["status"] == "open")
check("gate outcomes render at their joints",
      view["gates"][0]["joint"] == "joint-1" and
      view["gates"][0]["outcome"] == "escalate")
check("the current recorded state renders",
      view["current_state"]["claims"]["claim-1"] == "disputed" and
      view["current_state"]["paused"] == {"part-B": "joint-1"})

# R8: nothing that is not in the record — every rendered element
# carries an event_seq that exists, and unrecorded content is absent.
seqs = {ev["event_seq"] for ev in events}
rendered_seqs = (
    [c["event_seq"] for c in view["contributions"]] +
    [cm["event_seq"] for c in view["contributions"]
     for cm in c["comments"]] +
    [cm["event_seq"] for cm in view["job_comments"]] +
    [x["event_seq"] for x in view["disagreements"]] +
    [x["event_seq"] for x in view["gates"]])
check("every rendered element's provenance is in the record",
      all(s in seqs for s in rendered_seqs) and rendered_seqs)
check("unrecorded content appears nowhere in the view",
      "zebra-unicorn" not in json.dumps(view))

# ------------------------------------------------------------- R9
crew_json = json.dumps(view)
check("a scoped view omits out-of-boundary sealed material entirely",
      "mat-1" not in crew_json and view["sealed"] == [])
exam_view = render_view(events, "exam-1")
check("the examiner's view spans the run (sealed material visible)",
      any(s["material_id"] == "mat-1" for s in exam_view["sealed"]))
orch_view = render_view(events, "orch-1")
check("the orchestrator's view spans the run",
      any(s["material_id"] == "mat-1" for s in orch_view["sealed"]))
dir_view = render_view(events, "dir-1")
check("the director's bubble view is scoped like crew (R9, as "
      "flagged)", "mat-1" not in json.dumps(dir_view))

# ------------------------------------------- R10: the writable side
ev = post_comment(d, tok["crew-b"], view["position"],
                  "agreed — tightening now", contribution_id="c1")
check("a bubble comment is recorded through the doorway",
      ev["type"] == "COMMENT" and ev["actor"] == "crew-b")
view2 = render_view(store.all_events(), "crew-a")
c1b = view2["contributions"][0]
check("the recorded comment renders attached on re-render",
      len(c1b["comments"]) == 2 and
      c1b["comments"][1]["text"] == "agreed — tightening now")
g = refused(lambda: post_comment(d, tok["crew-a"], view2["position"],
                                 "floating words"), BubbleRefusal)
check("the bubble refuses a comment naming no subject",
      g is not None and "R10" in g, g or "")
n_events = len(store.all_events())
try:
    post_comment(d, tok["crew-a"], view2["position"], "floating")
except BubbleRefusal:
    pass
check("the refused bubble comment recorded nothing",
      len(store.all_events()) == n_events)
g = refused(lambda: post_comment(d, tok["orch-1"], view2["position"],
                                 "orchestrator note",
                                 contribution_id="c1"))
check("no act in the bubble bypasses the record's authority "
      "(orchestrator comment refused by the doorway)",
      g is not None and "§4" in g, g or "")

# R10 at the doorway (Piece 3 amendment): a comment must name a
# contribution standing in the record, or the job itself.
g = refused(lambda: A(tok["crew-a"], "COMMENT",
                      {"subject_id": "part-A", "text": "on a part"}))
check("the doorway refuses a comment naming a tree part (R10)",
      g is not None and "R10" in g, g or "")
g = refused(lambda: A(tok["crew-a"], "COMMENT",
                      {"contribution_id": "nope", "text": "ghost"}))
check("the doorway refuses a comment naming no standing "
      "contribution (R10)", g is not None)
A(tok["crew-a"], "COMMENT",
  {"subject_id": "run-1", "text": "on the job, by run id"})
check("a comment naming the job by its run id records",
      store.all_events()[-1]["type"] == "COMMENT")

print()
if FAILURES:
    print(f"PIECE 3 TESTS: {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("PIECE 3 TESTS: ALL PASS")
