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
    "tree": {"part-A": ["part-A1", "part-D"], "part-A1": [],
             "part-B": []},
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
      set(parts) == {"part-A", "part-A1", "part-B", "part-D"})
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
      view["current_state"]["claims"]["claim-1"]["status"] ==
      "disputed" and
      view["current_state"]["paused"]["part-B"]["joint"] == "joint-1")

# R8: nothing that is not in the record — provenance on EVERY
# rendered element, nested and derived included (round 1, point 1):
# walk the whole view collecting every sequence reference and check
# each against the record's own sequences; and assert presence on
# the element kinds the first version left bare.
seqs = {ev["event_seq"] for ev in events}


def collect_seqs(node, acc):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("event_seq", "status_seq", "lifecycle_seq",
                     "paused_at_seq", "position") and \
                    isinstance(v, int):
                acc.append(v)
            elif k == "event_seqs" and isinstance(v, list):
                acc.extend(v)
            else:
                collect_seqs(v, acc)
    elif isinstance(node, list):
        for item in node:
            collect_seqs(item, acc)
    return acc


all_seqs = collect_seqs(view, [])
check("every sequence reference in the view is a recorded event",
      all(s in seqs for s in all_seqs) and len(all_seqs) >= 12,
      f"{len(all_seqs)} references")
check("tree entries carry structure provenance",
      all(p["event_seq"] in seqs for p in view["tree"]))
c1_seq = next(ev["event_seq"] for ev in events
              if ev["type"] == "CONTRIBUTION" and
              ev["payload"].get("contribution_id") == "c1")
commission_seq = events[0]["event_seq"]
check("a contributed part's state provenance is the actual "
      "contribution event (round 2, point 1)",
      parts["part-A"]["state_event_seq"] == c1_seq and
      c1_seq != commission_seq)
check("a paused part's state provenance is its pause event",
      parts["part-B"]["state_event_seq"] ==
      parts["part-B"]["paused_at_seq"])
check("an open part's state provenance is the commissioning event",
      parts["part-A1"]["state_event_seq"] == commission_seq)
check("lifecycle carries the provenance of the event setting it",
      view["lifecycle_seq"] == events[0]["event_seq"])
check("current-state claims and pauses carry their provenance",
      view["current_state"]["claims"]["claim-1"]["event_seq"] in seqs
      and view["current_state"]["paused"]["part-B"]["event_seq"]
      in seqs)
check("unrecorded content appears nowhere in the view",
      "zebra-unicorn" not in json.dumps(view))

# R8 (round 1, point 2): the render derives its state from the
# events itself — a caller cannot inject invented state.
try:
    render_view(events, "crew-a", state={"lifecycle": "invented"})
    injected = True
except TypeError:
    injected = False
check("render_view accepts no caller-supplied state", not injected)

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

# R10 (round 1, point 3): a missing subject is not an invalid one.
# Historical comments, written straight to the record as a
# pre-amendment record could hold them:
store.append("COMMENT", "crew-a", [],
             {"subject_id": "part-A", "text": "about the part"})
store.append("COMMENT", "crew-b", [],
             {"subject_id": "ghost-9", "text": "about nothing"})
store.append("COMMENT", "crew-a", [], {"text": "no subject at all"})
store.commit()
view3 = render_view(store.all_events(), "crew-a")
unattached = {c["text"]: c for c in view3["unattached_comments"]}
check("a comment naming an invalid subject is not re-homed",
      "about the part" in unattached and
      "about nothing" in unattached)
check("the invalid relationship is explicit, provenance preserved",
      unattached["about the part"]["subject"] == "part-A" and
      unattached["about the part"]["subject_valid"] is False and
      unattached["about the part"]["event_seq"] in
      {ev["event_seq"] for ev in store.all_events()})
job_texts = [c["text"] for c in view3["job_comments"]]
attached_texts = [cm["text"] for c in view3["contributions"]
                  for cm in c["comments"]]
check("invalid-subject comments appear neither under the job nor "
      "attached", "about the part" not in job_texts and
      "about the part" not in attached_texts)
check("a comment with no subject at all renders under the job",
      "no subject at all" in job_texts)

# R8 (round 2, point 2): certification provenance exercised against
# a real certification, and lifecycle provenance across a transition
# beyond commissioning.
cert_ev = A(tok["exam-1"], "CERTIFICATION",
            {"coverage": "the rendered run, parts A and B"})
comp_ev = A(tok["crew-a"], "COMPLETION_CLAIMED", {})
view4 = render_view(store.all_events(), "exam-1")
certs = view4["current_state"]["certifications"]
check("the rendered certification count and sequences agree with "
      "the record's certification events",
      certs["count"] == 1 and
      certs["event_seqs"] == [cert_ev["event_seq"]])
check("lifecycle provenance follows the event establishing the "
      "current lifecycle value",
      view4["lifecycle"] == "completion_claimed" and
      view4["lifecycle_seq"] == comp_ev["event_seq"])

# R8 (round 3): a downstream-only commissioned part (part-D is in
# part-A's downstream list but is not a tree key) keeps commissioning
# structure provenance even after a contribution names it; its state
# provenance is that contribution.
c3_ev = A(tok["crew-b"], "CONTRIBUTION",
          {"contribution_id": "c3", "tree_part": "part-D",
           "text": "D drafted"})
view5 = render_view(store.all_events(), "crew-a")
part_d = next(p for p in view5["tree"] if p["part"] == "part-D")
check("a downstream-only part's structure provenance is the "
      "commissioning event",
      part_d["event_seq"] == commission_seq)
check("its contributed state provenance is the contribution event, "
      "independently", part_d["state"] == "contributed" and
      part_d["state_event_seq"] == c3_ev["event_seq"] and
      c3_ev["event_seq"] != commission_seq)

print()
if FAILURES:
    print(f"PIECE 3 TESTS: {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("PIECE 3 TESTS: ALL PASS")
