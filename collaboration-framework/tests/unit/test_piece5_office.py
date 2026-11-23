"""Piece 5 tests — the office (SPEC SHEET §3.5, R14–R17, R32's
case half), against the thirteen acceptance tests of addendum 2 §G
as amended by addendum 3 §H; plus the examination round-1 tests
(the paired route under R30/R31).

Language note (examination round 1): the scope counts six semantic
R14 fields — tree and highlighted part form one combined field —
while the implementation stores and compares seven keys. Tests
below name keys where keys are what vary.

Run: PYTHONPATH=src python3 tests/unit/test_piece5_office.py
Exits 0 when every check passes.
"""
import copy
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "src"))

from framework.record import (FrameworkStore, CONSTITUTION_HASH,
                              effective_case, fold, version_issued)
from framework.doorway import (Doorway, DoorwayRefusal,
                               established_case_content)
from framework.driver import Driver
from framework.office import Office

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


class ScriptedModel:
    def __init__(self, script=None):
        self.script = list(script) if script else [[]]
        self.calls = []

    def __call__(self, package):
        self.calls.append(package)
        item = self.script.pop(0) if len(self.script) > 1 \
            else self.script[0]
        if isinstance(item, Exception):
            raise item
        return item


def fresh_store(briefs, extra_seats=None):
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    seats = {
        "orch-1": {"role": "orchestrator",
                   "identity_status": "declared"},
        "exam-1": {"role": "examiner", "identity_status": "declared"},
        "dir-1": {"role": "director", "identity_status": "declared"},
    }
    for seat in briefs:
        seats[seat] = {"role": "crew", "identity_status": "declared"}
    if extra_seats:
        seats.update(extra_seats)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": ["part-B"], "part-B": []},
        "seats": seats,
        "briefs": briefs,
    })
    store.commit()
    return store


FULL = {"part": "part-A", "assignment": "Draft the A section",
        "verification_list": ["check the figures"]}

briefs = {
    "crew-a": dict(FULL),
    "crew-b": {"part": "part-A", "assignment": "B section"},
    "crew-c": {"part": "part-Z", "assignment": "C section",
               "verification_list": ["check"]},
    "crew-d": {"part": "part-A", "verification_list": ["check"]},
    "crew-g": dict(FULL),
}
for i in range(1, 7):
    briefs[f"crew-f{i}"] = dict(FULL)

store = fresh_store(briefs)
d = Doorway(store)
office = Office(d)
tok = {s: d.issue_token(s)
       for s in list(briefs) + ["orch-1", "exam-1", "dir-1"]}


def A(token, type_, payload):
    return d.act(token, type_, payload, view_seq=store.head_seq())


def case_events(case_id=None, type_=None):
    out = []
    for ev in store.all_events():
        if type_ and ev["type"] != type_:
            continue
        if case_id and ev["payload"].get("case_id") != case_id:
            continue
        if ev["type"].startswith("CASE_"):
            out.append(ev)
    return out


A(tok["orch-1"], "MATERIAL_SEALED",
  {"material_id": "mat-1", "boundary": ["crew-a"]})

# ---------------- Test 8: wrong seat — nothing appended
head = store.head_seq()
r = office.issue_new(tok["orch-1"], "ghost-1")
check("T8 an uncommissioned seat's case fails preflight",
      r["ok"] is False and
      any("not commissioned" in p for p in r["problems"]))
check("T8 nothing was appended", store.head_seq() == head)

# ---------------- Test 1: invalid initial case — zero case events
r = office.issue_new(tok["orch-1"], "crew-b")
check("T1 a brief missing its verification list fails preflight",
      r["ok"] is False and
      any("verification_list" in p for p in r["problems"]))
check("T1 no case events exist for the invalid case",
      case_events("case-crew-b") == [] and case_events() == [])

# ---------------- Test 9: wrong tree part
r = office.issue_new(tok["orch-1"], "crew-c")
check("T9 a brief naming a part outside the tree fails preflight",
      r["ok"] is False and
      any("not in the case's tree" in p for p in r["problems"]))
check("T9 no case events exist for it",
      case_events("case-crew-c") == [])

# ---------------- Test 10: incomplete R14
r = office.issue_new(tok["orch-1"], "crew-d")
check("T10 a brief missing its assignment fails preflight",
      r["ok"] is False and
      any("assignment" in p for p in r["problems"]))
check("T10 no case events exist for it",
      case_events("case-crew-d") == [])

# ---------------- crew-a: a grounded case, generated from the record
r = office.issue_new(tok["orch-1"], "crew-a")
check("the office issues a grounded case for crew-a", r["ok"] is True)
content, ver_no = established_case_content(d.state(), "case-crew-a")
check("generated content is grounded in the recorded sources",
      ver_no == 1 and
      content["tree"] == {"part-A": ["part-B"], "part-B": []} and
      content["part"] == "part-A" and
      content["assignment"] == "Draft the A section" and
      content["verification_list"] == ["check the figures"] and
      content["evidence_boundary"] == ["mat-1"] and
      content["account"] == "crew-a" and
      "CONTRIBUTION" in content["authority"])

# ---------------- Test 3: duplicate verification — the first stands
first_verified = [ev for ev in case_events("case-crew-a", "CASE_VERIFIED")][0]
A(tok["orch-1"], "CASE_VERIFIED",
  dict(content, assignment="a later, different draft"))
content2, _ = established_case_content(d.state(), "case-crew-a")
folded = d.state()["cases"]["case-crew-a"]["versions"]["1"]
check("T3 a second verification replaces neither content nor position",
      content2["assignment"] == "Draft the A section" and
      folded["verified"] == first_verified["event_seq"])

# ---------------- crew-a v1 completes its route
A(tok["exam-1"], "CASE_JUDGED", {"case_id": "case-crew-a", "version": 1})
office.authorise(tok["orch-1"], "case-crew-a", 1)
eff = effective_case(d.state(), "crew-a")
check("crew-a's v1 stands issued", eff is not None and
      eff["version"] == 1)

# ---------------- Test 2: invalid correction — neither pair event
head = store.head_seq()
r = office.correct(tok["orch-1"], "case-crew-a", {"part": "part-Z"})
check("T2 a correction to a part outside the tree fails preflight",
      r["ok"] is False)
check("T2 neither CASE_CORRECTED nor a new CASE_VERIFIED was appended",
      store.head_seq() == head and
      case_events("case-crew-a", "CASE_CORRECTED") == [])

# ---------------- Test 6: forged classification refused at the doorway
forged = dict(content, version=2, representational=True,
              assignment="a semantic change wearing a false label")
try:
    A(tok["orch-1"], "CASE_CORRECTED", forged)
    refused = False
except DoorwayRefusal:
    refused = True
rejections = [ev for ev in store.all_events()
              if ev["type"] == "REJECTION" and
              ev["payload"].get("attempted_type") == "CASE_CORRECTED"]
check("T6 a forged classification is refused and the refusal recorded",
      refused and len(rejections) == 1 and
      case_events("case-crew-a", "CASE_CORRECTED") == [])

# ---------------- Test 11: version transition — acknowledgement first
model_a = ScriptedModel([[{"type": "CONTRIBUTION", "payload": {
    "contribution_id": "c1", "claim_id": "claim-1",
    "tree_part": "part-A", "text": "A, first draft"}}]])
driver_a = Driver(d, "crew-a", tok["crew-a"], model_a)
r = driver_a.wake_cycle()
check("the driver works under v1", r["woke"] is True and
      r["recorded"] and
      r["recorded"][0]["payload"]["case_version"] == 1)

r = office.correct(tok["orch-1"], "case-crew-a",
                   {"assignment": "Draft the A section, revised"})
check("the office's correction is classified semantic and paired",
      r["ok"] is True and r["representational"] is False and
      r["changed"] == ["assignment"] and
      r["verified_seq"] == r["corrected_seq"] + 1)
A(tok["exam-1"], "CASE_JUDGED", {"case_id": "case-crew-a", "version": 2})
office.authorise(tok["orch-1"], "case-crew-a", 2)
eff = effective_case(d.state(), "crew-a")
check("v2 stands issued over v1", eff is not None and
      eff["version"] == 2 and eff["acknowledged"] is False)

contribs_before = len([ev for ev in store.all_events()
                       if ev["type"] == "CONTRIBUTION"])
model_a.script = [
    [{"type": "CASE_ACKNOWLEDGED",
      "payload": {"case_id": "case-crew-a", "version": 2}}],
    [],
    [{"type": "CONTRIBUTION", "payload": {
        "contribution_id": "c2", "claim_id": "claim-2",
        "tree_part": "part-A", "text": "A, revised draft"}}],
]
r = driver_a.wake_cycle()
acks = [ev for ev in store.all_events()
        if ev["type"] == "CASE_ACKNOWLEDGED" and
        ev["payload"].get("version") == 2]
contribs_after = len([ev for ev in store.all_events()
                      if ev["type"] == "CONTRIBUTION"])
check("T11 the first wake under v2 records the acknowledgement only",
      len(acks) == 1 and contribs_after == contribs_before)
A(tok["crew-b"], "CONTRIBUTION",
  {"contribution_id": "cb1", "tree_part": "part-A",
   "text": "B's take on A, for the revised draft"})
r = driver_a.wake_cycle()
check("T11 work resumes under v2 from a fresh package",
      r["woke"] is True and r["recorded"] and
      r["recorded"][0]["payload"]["case_version"] == 2)

# ---------------- Test 7: field-by-field classification (office route)
FIELD_CHANGES = [
    ("assignment", "a wholly new assignment"),
    ("tree", {"part-A": ["part-B"], "part-B": [], "part-C": []}),
    ("part", "part-B"),
    ("evidence_boundary", ["mat-1", "mat-2"]),
    ("verification_list", ["check the figures", "check the totals"]),
    ("authority", ["CONTRIBUTION"]),
]
for i, (field, value) in enumerate(FIELD_CHANGES, start=1):
    seat = f"crew-f{i}"
    rr = office.issue_new(tok["orch-1"], seat)
    A(tok["exam-1"], "CASE_JUDGED",
      {"case_id": f"case-{seat}", "version": 1})
    office.authorise(tok["orch-1"], f"case-{seat}", 1)
    rr = office.correct(tok["orch-1"], f"case-{seat}", {field: value})
    recorded = [ev for ev in case_events(f"case-{seat}", "CASE_CORRECTED")]
    A(tok["exam-1"], "CASE_NOTIFIED",
      {"case_id": f"case-{seat}", "version": 2})
    office.authorise(tok["orch-1"], f"case-{seat}", 2)
    eff = effective_case(d.state(), seat)
    check(f"T7 changing only {field} classifies semantic, and a "
          f"notification cannot issue it",
          rr["ok"] is True and rr["changed"] == [field] and
          rr["representational"] is False and
          recorded and
          recorded[0]["payload"]["representational"] is False and
          eff is not None and eff["version"] == 1)

# ---------------- Test 7 (account): the doorway recompute itself
office.issue_new(tok["orch-1"], "crew-g")
A(tok["exam-1"], "CASE_JUDGED", {"case_id": "case-crew-g", "version": 1})
office.authorise(tok["orch-1"], "case-crew-g", 1)
g_content, _ = established_case_content(d.state(), "case-crew-g")
try:
    A(tok["orch-1"], "CASE_CORRECTED",
      dict(g_content, version=2, account="crew-a",
           representational=True))
    refused = False
except DoorwayRefusal:
    refused = True
check("T7 an account-only change labelled representational is refused",
      refused)
A(tok["orch-1"], "CASE_CORRECTED",
  dict(g_content, version=2, account="crew-a", representational=False))
recorded = [ev for ev in case_events("case-crew-g", "CASE_CORRECTED")]
check("T7 the same change labelled semantic is recorded as such",
      len(recorded) == 1 and
      recorded[0]["payload"]["representational"] is False)

# ---------------- Test 13: the atomic pair rolls back whole
head_before = store.head_seq()
state_before = json.dumps(d.state()["cases"], sort_keys=True)
original_append = store.append


def exploding_append(type_, actor, affected, payload):
    if type_ == "CASE_VERIFIED":
        raise RuntimeError("injected failure between the appends")
    return original_append(type_, actor, affected, payload)


store.append = exploding_append
try:
    office.correct(tok["orch-1"], "case-crew-a",
                   {"assignment": "a change that must not half-land"})
    raised = False
except RuntimeError:
    raised = True
finally:
    store.append = original_append
check("T13 a failure inside the pair surfaces", raised)
check("T13 head and case state stand exactly as before the pair",
      store.head_seq() == head_before and
      json.dumps(d.state()["cases"], sort_keys=True) == state_before)
check("T13 no partial CASE_CORRECTED for v3 stands",
      [ev for ev in case_events("case-crew-a", "CASE_CORRECTED")
       if ev["payload"].get("version") == 3] == [])
A(tok["crew-a"], "COMMENT", {"on_job": True, "text": "still here"})
check("T13 the store carries no pending partial transaction",
      store.head_seq() == head_before + 1)

# ---------------- Test 12: replay consistency
s1 = fold(store.all_events(), store.get_run_id())
s2 = fold(store.all_events(), store.get_run_id())
check("T12 replaying the record folds to the same case state",
      json.dumps(s1["cases"], sort_keys=True) ==
      json.dumps(s2["cases"], sort_keys=True))

# ---------------- Tests 4 & 5: exact issuance order (manual route)
store2 = fresh_store({"crew-x": dict(FULL)})
d2 = Doorway(store2)
tok2 = {s: d2.issue_token(s) for s in ("orch-1", "exam-1", "crew-x")}


def A2(token, type_, payload):
    return d2.act(token, type_, payload, view_seq=store2.head_seq())


# Test 4: judgement recorded before the verification it answers.
A2(tok2["exam-1"], "CASE_JUDGED", {"case_id": "case-y", "version": 1})
A2(tok2["orch-1"], "CASE_VERIFIED",
   {"case_id": "case-y", "version": 1, "seat": "crew-x"})
A2(tok2["orch-1"], "CASE_ISSUED",
   {"case_id": "case-y", "version": 1, "seat": "crew-x"})
ver_y = d2.state()["cases"]["case-y"]["versions"]["1"]
check("T4 a judgement preceding its verification does not issue",
      version_issued(ver_y, 1) is False)

# Test 5: notification preceding verification, representational route.
A2(tok2["orch-1"], "CASE_VERIFIED",
   {"case_id": "case-x", "version": 1, "seat": "crew-x"})
A2(tok2["exam-1"], "CASE_JUDGED", {"case_id": "case-x", "version": 1})
A2(tok2["orch-1"], "CASE_ISSUED",
   {"case_id": "case-x", "version": 1, "seat": "crew-x"})
A2(tok2["orch-1"], "CASE_CORRECTED",
   {"case_id": "case-x", "version": 2, "seat": "crew-x",
    "representational": True})
A2(tok2["exam-1"], "CASE_NOTIFIED", {"case_id": "case-x", "version": 2})
A2(tok2["orch-1"], "CASE_ISSUED",
   {"case_id": "case-x", "version": 2, "seat": "crew-x"})
A2(tok2["orch-1"], "CASE_VERIFIED", {"case_id": "case-x", "version": 2})
ver_x2 = d2.state()["cases"]["case-x"]["versions"]["2"]
eff_x = effective_case(d2.state(), "crew-x")
check("T5 a notification preceding its verification does not issue, "
      "even once the set is complete",
      version_issued(ver_x2, 2) is False and eff_x is not None and
      eff_x["version"] == 1)

# ---------------- Examination round 1: the pair under R30 / R31
store3 = fresh_store({"crew-p": dict(FULL)})
d3 = Doorway(store3)
office3 = Office(d3)
tok3 = {s: d3.issue_token(s) for s in ("crew-p", "orch-1", "exam-1")}


def A3(token, type_, payload):
    return d3.act(token, type_, payload, view_seq=store3.head_seq())


def pair_refusal(fn):
    try:
        fn()
        return None
    except DoorwayRefusal as refusal:
        return str(refusal)


office3.issue_new(tok3["orch-1"], "crew-p")
A3(tok3["exam-1"], "CASE_JUDGED", {"case_id": "case-crew-p", "version": 1})
office3.authorise(tok3["orch-1"], "case-crew-p", 1)

A3(tok3["exam-1"], "GATE_OUTCOME",
   {"joint": "j-p", "outcome": "escalate", "tree_part": "part-A"})
head = store3.head_seq()
g = pair_refusal(lambda: office3.correct(
    tok3["orch-1"], "case-crew-p", {"assignment": "paused draft"}))
rejections3 = [ev for ev in store3.all_events()
               if ev["type"] == "REJECTION" and
               ev["payload"].get("attempted_type") == "CASE_CORRECTED"]
check("R1-T1 a correction pair for a paused part is refused, "
      "recorded, and appends neither pair event",
      g is not None and "R30" in g and len(rejections3) == 1 and
      store3.head_seq() == head + 1 and
      [ev for ev in store3.all_events()
       if ev["type"] == "CASE_CORRECTED"] == [])
A3(tok3["exam-1"], "GATE_OUTCOME",
   {"joint": "j-p", "outcome": "allow",
    "released_set": ["part-A", "part-B"]})

A3(tok3["exam-1"], "GATE_OUTCOME",
   {"joint": "j-p2", "outcome": "escalate", "tree_part": "part-A"})
verified_before = len([ev for ev in store3.all_events()
                       if ev["type"] == "CASE_VERIFIED" and
                       ev["payload"].get("case_id") == "case-crew-p"])
rejections_before = len([ev for ev in store3.all_events()
                         if ev["type"] == "REJECTION"])
g = pair_refusal(lambda: office3.correct(
    tok3["orch-1"], "case-crew-p", {"part": "part-B"}))
check("R1-T2 a correction pair for a part downstream of a pause "
      "is refused and recorded, neither pair event appended",
      g is not None and "R30" in g and
      len([ev for ev in store3.all_events()
           if ev["type"] == "REJECTION"]) == rejections_before + 1 and
      [ev for ev in store3.all_events()
       if ev["type"] == "CASE_CORRECTED"] == [] and
      len([ev for ev in store3.all_events()
           if ev["type"] == "CASE_VERIFIED" and
           ev["payload"].get("case_id") == "case-crew-p"]) ==
      verified_before)
A3(tok3["exam-1"], "GATE_OUTCOME",
   {"joint": "j-p2", "outcome": "allow",
    "released_set": ["part-A", "part-B"]})

p_content, _ = established_case_content(d3.state(), "case-crew-p")
view_before = store3.head_seq()
A3(tok3["orch-1"], "CASE_VERIFIED",
   {"case_id": "case-crew-p", "version": 1})
g = pair_refusal(lambda: d3.submit_pair(
    tok3["orch-1"],
    [("CASE_CORRECTED", dict(p_content, version=2,
                             assignment="revised",
                             representational=False)),
     ("CASE_VERIFIED", {"case_id": "case-crew-p", "version": 2})],
    view_seq=view_before))
check("R1-T3 a pair whose case changed since its view is refused "
      "and recorded (R31)",
      g is not None and "R31" in g and
      [ev for ev in store3.all_events()
       if ev["type"] == "CASE_CORRECTED"] == [])

view2 = store3.head_seq()
A3(tok3["crew-p"], "CONTRIBUTION",
   {"contribution_id": "cp1", "tree_part": "part-B",
    "text": "unrelated to the case and its part"})
ev1, ev2 = d3.submit_pair(
    tok3["orch-1"],
    [("CASE_CORRECTED", dict(p_content, version=2,
                             assignment="revised",
                             representational=False)),
     ("CASE_VERIFIED", {"case_id": "case-crew-p", "version": 2})],
    view_seq=view2)
check("R1-T4 a behind-head view with no subject change is "
      "admitted, flagged stale_basis on both pair events",
      ev1["payload"].get("stale_basis") is True and
      ev2["payload"].get("stale_basis") is True)

# Round-2 test corrections: part-specific staleness, and a real
# rollback exercise against the corrected route (T13 stands above
# on the first store; this is its counterpart on this store).
p2_content, _ = established_case_content(d3.state(), "case-crew-p")
view_part = store3.head_seq()
A3(tok3["crew-p"], "CONTRIBUTION",
   {"contribution_id": "cp2", "tree_part": "part-A",
    "text": "work on the case's part, after the pair's view"})
rejections_before = len([ev for ev in store3.all_events()
                         if ev["type"] == "REJECTION"])
g = pair_refusal(lambda: d3.submit_pair(
    tok3["orch-1"],
    [("CASE_CORRECTED", dict(p2_content, version=3,
                             assignment="revised again",
                             representational=False)),
     ("CASE_VERIFIED", {"case_id": "case-crew-p", "version": 3})],
    view_seq=view_part))
check("R1-T5 a pair whose part changed since its view — the case "
      "itself unchanged — is refused and recorded (R31)",
      g is not None and "R31" in g and "part-A" in g and
      len([ev for ev in store3.all_events()
           if ev["type"] == "REJECTION"]) == rejections_before + 1 and
      [ev for ev in store3.all_events()
       if ev["type"] == "CASE_CORRECTED" and
       ev["payload"].get("version") == 3] == [])

head_before = store3.head_seq()
state_before = json.dumps(d3.state()["cases"], sort_keys=True)
original_append3 = store3.append


def exploding_append3(type_, actor, affected, payload):
    if type_ == "CASE_VERIFIED":
        raise RuntimeError("injected failure between the appends")
    return original_append3(type_, actor, affected, payload)


store3.append = exploding_append3
try:
    office3.correct(tok3["orch-1"], "case-crew-p",
                    {"assignment": "a change that must not half-land"})
    raised = False
except RuntimeError:
    raised = True
finally:
    store3.append = original_append3
check("R1-T6 a failure inside the corrected route's pair surfaces",
      raised)
check("R1-T6 head and case state stand exactly as before the pair",
      store3.head_seq() == head_before and
      json.dumps(d3.state()["cases"], sort_keys=True) == state_before)
A3(tok3["crew-p"], "COMMENT", {"on_job": True, "text": "still here"})
check("R1-T6 the store carries no pending partial transaction",
      store3.head_seq() == head_before + 1)

print()
if FAILURES:
    print(f"PIECE 5 TESTS: {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("PIECE 5 TESTS: ALL PASS")
