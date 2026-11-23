"""Piece A2 tests — grants and dispatch (agent layer; SPEC
SHEET Rev 6, R44–R48, R55's dispatch part), against the passed
scope PIECE-A2-SCOPE-2026-11-23.md (Rev 4) and its acceptance
sketch: the happy path end-to-end through request → dispatch →
start → outcome with a real file written; ungranted, unregistered,
ceiling-breaking and over-bound requests refused and recorded;
request identity bound to its contents (retry resolves, reuse
with altered contents refused); flaky failure, hang → uncertain,
execute-but-lose-the-report → uncertain → examiner reconciliation
(second reconciliation refused); the durable single-execution
boundary (crash after the claim, recovered by a second executor,
side effect at most once; an unclaimed intent recovered and
executed exactly once); attribution discipline (reconciliation
is the examiner's, outcomes the executor's, requests the
instance's own credential); the checker's dispatch
correspondence on doorway-bypassing histories; the two policy
copies' witnessed agreement; and replay executing nothing.
Correction round 1 adds: the registry version recorded in
every dispatch and verified by the checker; the checker's
verification of every event referent (a dispatch's tool
against its request's, a start's and an outcome's identity
against its dispatch's); and the start-ordering witness —
TOOL_STARTED recorded by the executing thread itself, already
standing in the record at the moment the operation body runs,
with a failed start report meaning the operation never runs.
Correction round 2 adds: genuinely serialized record access
(the store's own lock, held inside the store and across the
doorway's check-and-append) and the blocked-start witness —
a start step held past the operation deadline lands after
the uncertain outcome and so records no start and performs
nothing, with no concurrent use of the store connection.
Correction round 3 adds: the deadline recheck after the start
report — a start step blocked while holding the store lock
past the deadline leaves the start standing but the operation
unperformed, with exactly one uncertain outcome recorded and
a history the checker verifies.
Correction round 4 adds: the worker-finishes-first witness —
the executor's monotonic clock is an injected dependency, and
a controlled clock advanced past the deadline between the
start report and the worker's recheck lands execute()
deterministically in its caller-records-uncertain branch, a
path the real clock leaves to a microsecond race.

Run: PYTHONPATH=src python3 tests/unit/test_piece_a2_dispatch.py
Exits 0 when every check passes.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import onboarding as ob  # noqa: E402,F401
from framework import projection  # noqa: E402
from framework import tool_policy as fw_policy  # noqa: E402
from framework.doorway import Doorway, DoorwayRefusal  # noqa: E402
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (CONSTITUTION_HASH,  # noqa: E402
                              FrameworkStore)
import checker.tool_policy as ck_policy  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


DECL = "I am ExampleModel 4.2, served by Provider P, build 9917."
PROVIDER_ID = "example/model-4.2"
SKILLS = [{"name": "drafting", "version": "1.2.0"}]
FULL = {"part": "part-A", "assignment": "Draft the A section",
        "verification_list": ["check the figures"]}
TRACE = "commission brief, crew seat"
GRANTS = [
    {"tool": "sandbox.write",
     "scope_ceiling": {"path_prefix": "notes/"},
     "side_effect_class": "write", "bound": {"count": 3},
     "authority_trace": TRACE},
    {"tool": "sandbox.read",
     "scope_ceiling": {"path_prefix": "notes/"},
     "side_effect_class": "read", "bound": {"count": 3},
     "authority_trace": TRACE},
    {"tool": "sandbox.flaky",
     "scope_ceiling": {"path_prefix": "notes/"},
     "side_effect_class": "write", "bound": {"count": 4},
     "authority_trace": TRACE},
]
GRANTS_FLAKY2 = [
    {"tool": "sandbox.flaky",
     "scope_ceiling": {"path_prefix": "notes/"},
     "side_effect_class": "write", "bound": {"count": 2},
     "authority_trace": TRACE},
]
GRANTS_EVIL = [
    {"tool": "evil.tool", "scope_ceiling": {},
     "side_effect_class": "write", "bound": {"count": 1},
     "authority_trace": TRACE},
]


def identify():
    return {"declaration": DECL, "provider_model_id": PROVIDER_ID}


def fresh():
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": ["part-B"], "part-B": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
            "crew-2": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": dict(FULL), "crew-2": dict(FULL)},
    })
    store.commit()
    d = Doorway(store)
    office = Office(d)
    gen = Generator(d)
    tok = {s: d.issue_token(s) for s in
           ("orch-1", "exam-1", "dir-1", "crew-1", "crew-2")}
    return store, d, office, gen, tok


def issue_case(d, office, tok, seat):
    r = office.issue_new(tok["orch-1"], seat)
    assert r["ok"], r
    d.act(tok["exam-1"], "CASE_JUDGED",
          {"case_id": f"case-{seat}", "version": 1},
          view_seq=d.store.head_seq())
    office.authorise(tok["orch-1"], f"case-{seat}", 1)


def activate(store, d, office, gen, tok, seat="crew-1",
             grants=GRANTS):
    """The full A1 lifecycle for one seat slot, ending with an
    activated instance; returns (generate_result,
    instance_token)."""
    issue_case(d, office, tok, seat)
    gen.propose(tok["orch-1"], seat, part="part-A",
                role_requirements="a careful drafting model")
    r = gen.generate(tok["orch-1"], seat, identify,
                     skills=SKILLS, grants=grants)
    assert r["ok"], r
    gen.verify(tok["orch-1"], r["assembly_id"])
    d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
          gen.judgement(r["assembly_id"]),
          view_seq=store.head_seq())
    packed = gen.pack(tok["orch-1"], r["assembly_id"])
    gen.authorise(tok["orch-1"], r["assembly_id"])
    gen.activate(tok["orch-1"], r["assembly_id"])
    return r, packed["instance_token"]


def refused(fn):
    try:
        fn()
    except DoorwayRefusal:
        return True
    return False


def events_of(store, type_):
    return [e for e in store.all_events() if e["type"] == type_]


def last_rejection(store):
    evs = events_of(store, "REJECTION")
    return evs[-1] if evs else None


def make_executor(d, deadline=2.0, executor_id="executor-1"):
    base = tempfile.mkdtemp()
    sandbox = os.path.join(base, "sandbox")
    claims = os.path.join(base, "claims")
    ex = Executor(d, sandbox, claim_dir=claims, deadline=deadline,
                  executor_id=executor_id)
    return ex, sandbox, claims


def read_file(path):
    with open(path) as fh:
        return fh.read()


# -- T1: the happy path, end to end — request → check →
# dispatch → start → outcome, the file really written, then
# read back through the same sequence.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d)
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/a.txt", "content": "hello"},
                     "req-1")
check("T1 a granted request dispatches",
      res["ok"] and not res["duplicate"] and res["dispatch_id"])
did = res["dispatch_id"]
req_ev, disp_ev = events_of(store, "TOOL_REQUESTED")[-1], \
    events_of(store, "TOOL_DISPATCHED")[-1]
check("T1 attribution: the request is the instance's (as its "
      "slot), the dispatch intent the doorway's",
      req_ev["actor"] == "crew-1"
      and disp_ev["actor"] == "doorway"
      and req_ev["event_seq"] < disp_ev["event_seq"])
summary = ex.execute(did)
check("T1 execution records a result outcome",
      summary["ok"] and summary["outcome"] == "result")
start_ev, out_ev = events_of(store, "TOOL_STARTED")[-1], \
    events_of(store, "TOOL_OUTCOME")[-1]
check("T1 the start and outcome are the executor's, in order",
      start_ev["actor"] == "executor"
      and out_ev["actor"] == "executor"
      and disp_ev["event_seq"] < start_ev["event_seq"]
      < out_ev["event_seq"]
      and out_ev["payload"]["dispatch_id"] == did
      and out_ev["payload"]["outcome"] == "result")
check("T1 the sandbox file is really written",
      read_file(os.path.join(sandbox, "notes", "a.txt"))
      == "hello")
entry = d.state()["dispatches"][did]
check("T1 the fold derives the dispatch state",
      entry["outcome"] == "result"
      and entry["started_seq"] == start_ev["event_seq"]
      and entry["outcome_seq"] == out_ev["event_seq"])
res2 = d.request_tool(itok, "sandbox.read",
                      {"path": "notes/a.txt"}, "req-2")
summary2 = ex.execute(res2["dispatch_id"])
out2 = events_of(store, "TOOL_OUTCOME")[-1]
check("T1 a read through the same sequence returns the content",
      summary2["outcome"] == "result"
      and out2["payload"]["result"]["content"] == "hello")

# -- T2: an ungranted tool is refused and recorded, nothing
# dispatched; a granted-but-unregistered tool is refused by
# the registry.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
before = len(store.all_events())
check("T2 an ungranted tool is refused",
      refused(lambda: d.request_tool(
          itok, "shelf.read", {"path": "notes/a.txt"}, "req-u")))
rej = last_rejection(store)
check("T2 the refusal is recorded, naming the grant ground",
      len(store.all_events()) == before + 2
      and rej["payload"]["attempted_type"] == "TOOL_DISPATCHED"
      and "no grant for tool shelf.read" in rej["payload"]["ground"]
      and not events_of(store, "TOOL_DISPATCHED"))
check("T2 the refused request itself stands recorded (R55)",
      len(events_of(store, "TOOL_REQUESTED")) == 1
      and d.state()["tool_requests"][0]["dispatch_id"] is None)
r2, itok2 = activate(store, d, office, gen, tok, seat="crew-2",
                     grants=GRANTS_EVIL)
check("T2 a granted but unregistered tool is refused",
      refused(lambda: d.request_tool(
          itok2, "evil.tool", {"path": "notes/x"}, "req-e"))
      and "not in the tool registry" in
      last_rejection(store)["payload"]["ground"])

# -- T3: ceiling violations are refused and recorded; nothing
# is dispatched or written.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d)
check("T3 a path outside the grant's prefix is refused",
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "secret/x.txt", "content": "no"}, "req-c1"))
      and "ceiling prefix" in
      last_rejection(store)["payload"]["ground"])
check("T3 a path escaping the sandbox is refused",
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "../escape.txt", "content": "no"}, "req-c2"))
      and "normalised" in
      last_rejection(store)["payload"]["ground"])
check("T3 an unknown parameter fails closed",
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "notes/a.txt", "content": "no",
           "mode": "x"}, "req-c3"))
      and "not a parameter" in
      last_rejection(store)["payload"]["ground"])
check("T3 nothing dispatched, nothing written",
      not events_of(store, "TOOL_DISPATCHED")
      and not os.path.exists(os.path.join(sandbox, "secret"))
      and not os.path.exists(
          os.path.join(os.path.dirname(sandbox), "escape.txt")))

# -- T4: the bound counts dispatches — a failure and an
# uncertain outcome both keep their charge, and the next
# request past the bound is refused.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok,
                   grants=GRANTS_FLAKY2)
ex, sandbox, claims = make_executor(d, deadline=0.3)
res = d.request_tool(itok, "sandbox.flaky", {"mode": "fail"},
                     "req-f1")
s1 = ex.execute(res["dispatch_id"])
check("T4 the flaky failure records a failure outcome",
      s1["outcome"] == "failure"
      and d.state()["dispatches"][res["dispatch_id"]]["outcome"]
      == "failure")
res = d.request_tool(itok, "sandbox.flaky",
                     {"mode": "hang-past-deadline",
                      "hang_seconds": 2.0}, "req-f2")
s2 = ex.execute(res["dispatch_id"])
check("T4 a hang past the deadline records uncertain, "
      "never non-occurrence",
      s2["outcome"] == "uncertain"
      and d.state()["dispatches"][res["dispatch_id"]]["outcome"]
      == "uncertain")
before = len(store.all_events())
check("T4 the bound is exhausted with the uncertain dispatch "
      "still charged",
      refused(lambda: d.request_tool(
          itok, "sandbox.flaky", {"mode": "succeed"}, "req-f3"))
      and "bound" in last_rejection(store)["payload"]["ground"]
      and "exhausted" in
      last_rejection(store)["payload"]["ground"])
check("T4 exactly two dispatches stand",
      len(events_of(store, "TOOL_DISPATCHED")) == 2)

# -- T5: a retry resolves against the standing state — after
# dispatch and after outcome — and a retry in the
# recorded-but-undispatched interval records no second
# request.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d)
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/a.txt", "content": "hello"},
                     "req-1")
did = res["dispatch_id"]
before = len(store.all_events())
again = d.request_tool(itok, "sandbox.write",
                       {"path": "notes/a.txt", "content": "hello"},
                       "req-1")
check("T5 a retry after dispatch returns the standing "
      "dispatch, recording nothing",
      again["duplicate"] and again["dispatch_id"] == did
      and len(store.all_events()) == before)
ex.execute(did)
before = len(store.all_events())
again = d.request_tool(itok, "sandbox.write",
                       {"path": "notes/a.txt", "content": "hello"},
                       "req-1")
check("T5 a retry after outcome returns the standing outcome",
      again["duplicate"] and again["outcome"] == "result"
      and len(store.all_events()) == before
      and len(events_of(store, "TOOL_DISPATCHED")) == 1)
check("T5 a refused request retried records no second request",
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "secret/x.txt", "content": "no"}, "req-bad"))
      and refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "secret/x.txt", "content": "no"}, "req-bad"))
      and len([e for e in events_of(store, "TOOL_REQUESTED")
               if e["payload"]["request_id"] == "req-bad"]) == 1)

# -- T6: an identity reused with altered contents is refused
# and recorded; the original binding stands untouched.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/a.txt", "content": "hello"},
                     "req-1")
before = len(store.all_events())
check("T6 identity reuse with altered parameters is refused",
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "notes/a.txt", "content": "CHANGED"},
          "req-1"))
      and "cannot change its meaning" in
      last_rejection(store)["payload"]["ground"])
check("T6 the original binding and dispatch stand",
      len(store.all_events()) == before + 1
      and len(events_of(store, "TOOL_DISPATCHED")) == 1
      and d.state()["tool_requests"][0]["fingerprint"]
      == fw_policy.request_fingerprint(
          "sandbox.write",
          {"path": "notes/a.txt", "content": "hello"}))

# -- T7: execute-but-lose-the-report — the file is really
# written, the dispatch records uncertain, and only the
# examiner's reconciliation settles it; a second
# reconciliation is refused.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d)
res = d.request_tool(itok, "sandbox.flaky",
                     {"mode": "execute-but-lose-the-report",
                      "path": "notes/lost.txt",
                      "content": "payload"}, "req-lost")
did = res["dispatch_id"]
summary = ex.execute(did)
check("T7 the lost report records uncertain",
      summary["outcome"] == "uncertain"
      and d.state()["dispatches"][did]["uncertain_seq"]
      is not None)
check("T7 the execution really happened — the file stands",
      read_file(os.path.join(sandbox, "notes", "lost.txt"))
      == "payload")
d.act(tok["exam-1"], "TOOL_RECONCILED",
      {"dispatch_id": did, "outcome": "result",
       "evidence_ref": "sandbox file notes/lost.txt present "
                       "with the requested content"},
      view_seq=store.head_seq())
entry = d.state()["dispatches"][did]
check("T7 the examiner's reconciliation settles the dispatch",
      entry["reconciled_outcome"] == "result"
      and entry["reconciled_seq"] is not None)
before = len(store.all_events())
check("T7 a second reconciliation of a settled dispatch "
      "is refused and recorded",
      refused(lambda: d.act(
          tok["exam-1"], "TOOL_RECONCILED",
          {"dispatch_id": did, "outcome": "result",
           "evidence_ref": "again"},
          view_seq=store.head_seq()))
      and len(store.all_events()) == before + 1
      and store.all_events()[-1]["type"] == "REJECTION")
res = d.request_tool(itok, "sandbox.flaky", {"mode": "succeed"},
                     "req-ok")
ex.execute(res["dispatch_id"])
check("T7 a settled (result) dispatch is not reconcilable",
      refused(lambda: d.act(
          tok["exam-1"], "TOOL_RECONCILED",
          {"dispatch_id": res["dispatch_id"], "outcome": "result",
           "evidence_ref": "n/a"},
          view_seq=store.head_seq()))
      and "only an uncertain dispatch" in
      last_rejection(store)["payload"]["ground"])

# -- T8: the durable single-execution boundary — a crash
# after the execution claim (and after execution itself,
# before the outcome report) recovered by a SECOND executor:
# the side effect occurs at most once and the unknowable
# result stays uncertain. And the claim alone is the
# boundary: claimed-but-never-executed also recovers to
# uncertain, with no execution at all.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex1, sandbox, claims = make_executor(d, executor_id="executor-1")
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/crash.txt",
                      "content": "once"}, "req-crash")
did = res["dispatch_id"]
performed = []
orig_perform = ex1._perform


def counting_perform(tool, parameters):
    performed.append(tool)
    return orig_perform(tool, parameters)


ex1._perform = counting_perform
orig_outcome = d.record_tool_outcome


def crashing_outcome(*args, **kwargs):
    raise RuntimeError("simulated crash before the outcome "
                       "report")


d.record_tool_outcome = crashing_outcome
crashed = False
try:
    ex1.execute(did)
except RuntimeError:
    crashed = True
finally:
    d.record_tool_outcome = orig_outcome
check("T8 the crash lands after execution, before the outcome",
      crashed and performed == ["sandbox.write"]
      and read_file(os.path.join(sandbox, "notes", "crash.txt"))
      == "once"
      and d.state()["dispatches"][did]["outcome"] is None)
ex2 = Executor(d, sandbox, claim_dir=claims, deadline=2.0,
               executor_id="executor-2")
check("T8 the second executor cannot claim the claimed "
      "dispatch", ex2.claim(did) is False
      and ex1.claimed(did))
actions = ex2.recover()
check("T8 recovery records the unknowable result uncertain",
      actions == [{"dispatch_id": did,
                   "action": "recorded_uncertain"}]
      and d.state()["dispatches"][did]["outcome"] == "uncertain")
check("T8 the side effect occurred at most once",
      performed == ["sandbox.write"]
      and len(events_of(store, "TOOL_STARTED")) == 1
      and read_file(os.path.join(sandbox, "notes", "crash.txt"))
      == "once")
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/never.txt",
                      "content": "never"}, "req-never")
did2 = res["dispatch_id"]
check("T8 a claim alone is the boundary: claimed, never "
      "executed, recovers to uncertain with no side effect",
      ex1.claim(did2) is True
      and ex2.recover() == [{"dispatch_id": did2,
                             "action": "recorded_uncertain"}]
      and d.state()["dispatches"][did2]["outcome"] == "uncertain"
      and not os.path.exists(
          os.path.join(sandbox, "notes", "never.txt")))

# -- T9: an unclaimed standing intent is recovered and
# executed exactly once.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d)
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/late.txt",
                      "content": "recovered"}, "req-late")
did = res["dispatch_id"]
actions = ex.recover()
check("T9 recovery executes the unclaimed intent",
      actions == [{"dispatch_id": did, "action": "executed",
                   "outcome": "result"}]
      and read_file(os.path.join(sandbox, "notes", "late.txt"))
      == "recovered")
check("T9 exactly once: one start, one outcome",
      len(events_of(store, "TOOL_STARTED")) == 1
      and len(events_of(store, "TOOL_OUTCOME")) == 1
      and ex.recover() == [])

# -- T10: attribution discipline — reconciliation is the
# examiner's alone; starts and outcomes are the executor's
# alone; the dispatch intent is the doorway's alone. A seat
# act naming any of them is refused and recorded.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d, deadline=0.3)
res = d.request_tool(itok, "sandbox.flaky",
                     {"mode": "hang-past-deadline",
                      "hang_seconds": 2.0}, "req-hang")
did = res["dispatch_id"]
ex.execute(did)
check("T10 reconciliation by a non-examiner is refused",
      refused(lambda: d.act(
          tok["orch-1"], "TOOL_RECONCILED",
          {"dispatch_id": did, "outcome": "result",
           "evidence_ref": "orchestrator's say-so"},
          view_seq=store.head_seq()))
      and last_rejection(store)["payload"]["attempted_type"]
      == "TOOL_RECONCILED")
check("T10 an outcome recorded by a seat is refused",
      refused(lambda: d.act(
          tok["crew-1"], "TOOL_OUTCOME",
          {"dispatch_id": did, "outcome": "result"},
          view_seq=store.head_seq()))
      and last_rejection(store)["payload"]["attempted_type"]
      == "TOOL_OUTCOME")
check("T10 a start recorded by a seat is refused",
      refused(lambda: d.act(
          itok, "TOOL_STARTED", {"dispatch_id": did},
          view_seq=store.head_seq()))
      and last_rejection(store)["payload"]["attempted_type"]
      == "TOOL_STARTED")
check("T10 a dispatch intent recorded by a seat is refused",
      refused(lambda: d.act(
          tok["orch-1"], "TOOL_DISPATCHED",
          {"dispatch_id": "dispatch-x"}, view_seq=store.head_seq()))
      and last_rejection(store)["payload"]["attempted_type"]
      == "TOOL_DISPATCHED")
check("T10 the uncertain dispatch still stands unsettled",
      d.state()["dispatches"][did]["outcome"] == "uncertain"
      and d.state()["dispatches"][did]["reconciled_seq"] is None)

# -- T11: a request is the instance's own act — under its
# credential only, and only while that credential is active.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
gen.propose(tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a careful drafting model")
r = gen.generate(tok["orch-1"], "crew-1", identify,
                 skills=SKILLS, grants=GRANTS)
gen.verify(tok["orch-1"], r["assembly_id"])
d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
      gen.judgement(r["assembly_id"]), view_seq=store.head_seq())
packed = gen.pack(tok["orch-1"], r["assembly_id"])
check("T11 a request under a prepared credential is refused "
      "on the credential invariant",
      refused(lambda: d.request_tool(
          packed["instance_token"], "sandbox.write",
          {"path": "notes/a.txt", "content": "early"}, "req-p"))
      and "prepared" in
      last_rejection(store)["payload"]["ground"])
check("T11 a request under a seat token is refused",
      refused(lambda: d.request_tool(
          tok["crew-1"], "sandbox.write",
          {"path": "notes/a.txt", "content": "seat"}, "req-s"))
      and "instance's own credential" in
      last_rejection(store)["payload"]["ground"])
check("T11 no request was recorded for either refusal",
      not events_of(store, "TOOL_REQUESTED"))

# -- T12: the checker — the happy history verifies whole, and
# malformed histories appended past the doorway are reported
# by dispatch_correspondence, never read as valid.
def quiesce(store):
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def run_checker(store):
    quiesce(store)
    req = {"store_path": store.path, "run_id": "run-1",
           "snapshot": projection.snapshot(store)}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=SRC)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "checker"],
        input=json.dumps(req), capture_output=True, text=True,
        env=env, cwd=ROOT)
    return json.loads(proc.stdout)


def happy_world():
    store, d, office, gen, tok = fresh()
    r, itok = activate(store, d, office, gen, tok)
    ex, sandbox, claims = make_executor(d)
    res = d.request_tool(itok, "sandbox.write",
                         {"path": "notes/a.txt",
                          "content": "hello"}, "req-1")
    ex.execute(res["dispatch_id"])
    return store, d, tok, itok, res["dispatch_id"], sandbox


store, d, tok, itok, did, sandbox = happy_world()
verdict = run_checker(store)
c = verdict["checks"]
check("T12 the checker verifies the whole dispatch history",
      all(c[k]["result"] == "ok" for k in (
          "run_binding", "chain_hash", "chain_sequence",
          "replay", "projection_schema", "snapshot_schema",
          "replay_equality", "seal_correspondence",
          "assembly_correspondence", "dispatch_correspondence")),
      json.dumps(c))

store, d, tok, itok, did, sandbox = happy_world()
iid = d.state()["tool_requests"][0]["instance_id"]
store.append("TOOL_REQUESTED", "crew-1", [], {
    "instance_id": iid, "request_id": "req-x",
    "tool": "sandbox.delete", "parameters": {},
    "fingerprint": fw_policy.request_fingerprint(
        "sandbox.delete", {})})
store.append("TOOL_DISPATCHED", "doorway", [], {
    "instance_id": iid, "request_id": "req-x",
    "dispatch_id": "dispatch-99", "tool": "sandbox.delete"})
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T12 a dispatch with no grant in the sealed assembly "
      "is reported",
      dc["result"] == "divergent"
      and any(p["kind"] == "dispatch_without_grant"
              for p in dc["problems"]), json.dumps(dc))

store, d, tok, itok, did, sandbox = happy_world()
store.append("TOOL_STARTED", "executor", [], {
    "dispatch_id": did,
    "instance_id": d.state()["dispatches"][did]["instance_id"],
    "request_id": "req-1"})
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T12 a second start for one dispatch is reported",
      dc["result"] == "divergent"
      and any(p["kind"] == "second_start"
              for p in dc["problems"]), json.dumps(dc))

store, d, tok, itok, did, sandbox = happy_world()
store.append("TOOL_OUTCOME", "executor", [], {
    "dispatch_id": "dispatch-999", "outcome": "result"})
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T12 an outcome against no standing dispatch is "
      "reported",
      dc["result"] == "divergent"
      and any(p["kind"] == "outcome_without_dispatch"
              for p in dc["problems"]), json.dumps(dc))

store, d, tok, itok, did, sandbox = happy_world()
iid = d.state()["dispatches"][did]["instance_id"]
store.append("TOOL_REQUESTED", "crew-1", [], {
    "instance_id": iid, "request_id": "req-1",
    "tool": "sandbox.write",
    "parameters": {"path": "notes/a.txt", "content": "other"},
    "fingerprint": fw_policy.request_fingerprint(
        "sandbox.write",
        {"path": "notes/a.txt", "content": "other"})})
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T12 a request identity reused with different contents "
      "is reported",
      dc["result"] == "divergent"
      and any(p["kind"] == "request_identity_reused"
              for p in dc["problems"]), json.dumps(dc))

# -- T13: the two policy copies agree — the same pure contract
# at the doorway and in the checker — and the checker imports
# no executor.
BATTERY = [
    ("sandbox.write", {"path_prefix": "notes/"},
     {"path": "notes/a.txt", "content": "x"}),
    ("sandbox.write", {"path_prefix": "notes/"},
     {"path": "secret/a.txt", "content": "x"}),
    ("sandbox.write", {"path_prefix": "notes/"},
     {"path": "../a.txt", "content": "x"}),
    ("sandbox.write", {"path_prefix": "notes/"},
     {"path": "/abs/a.txt", "content": "x"}),
    ("sandbox.write", {"path_prefix": "notes/", "bogus": 1},
     {"path": "notes/a.txt", "content": "x"}),
    ("sandbox.write", {"path_prefix": "notes/"},
     {"path": "notes/a.txt", "content": "x", "mode": "y"}),
    ("sandbox.write", "case evidence",
     {"path": "notes/a.txt", "content": "x"}),
    ("sandbox.write", {"path_prefix": "notes/"},
     {"path": "notes/a.txt", "content": 7}),
    ("sandbox.read", {"path_prefix": "notes/"}, {}),
    ("sandbox.read", {}, {"path": "anywhere/a.txt"}),
    ("sandbox.flaky", {"path_prefix": "notes/"},
     {"mode": "hang-past-deadline", "hang_seconds": 1.5}),
    ("sandbox.flaky", {"path_prefix": "notes/"},
     {"mode": "explode"}),
    ("sandbox.flaky", {"path_prefix": "notes/"},
     {"mode": "succeed", "path": "elsewhere/a.txt"}),
    ("evil.tool", {}, {"path": "notes/a.txt"}),
]
agree = all(
    fw_policy.check_ceiling(t, c, p) == ck_policy.check_ceiling(
        t, c, p)
    and fw_policy.request_fingerprint(t, p)
    == ck_policy.request_fingerprint(t, p)
    for t, c, p in BATTERY)
check("T13 the doorway's and the checker's policy copies "
      "agree over the battery",
      agree and fw_policy.REGISTRY_VERSION
      == ck_policy.REGISTRY_VERSION
      == "tool-registry-v2")

# -- T13b (Piece A3-CAT): the agreement holds under each
# version's own view — the battery re-run under v1 and under
# v2 in both copies, an unknown version failing closed
# identically in both — and the worker-facing layer agrees:
# the same descriptions and parameter schemas in both copies
# under v2, and no layer at all under v1 (a fact about v1,
# witnessed, not assumed).
agree_versioned = all(
    fw_policy.check_ceiling(t, c, p, version=v)
    == ck_policy.check_ceiling(t, c, p, version=v)
    for t, c, p in BATTERY
    for v in ("tool-registry-v1", "tool-registry-v2"))
unknown_closed = (
    fw_policy.check_ceiling("sandbox.read", {}, {"path": "a"},
                            version="tool-registry-v99")
    == ck_policy.check_ceiling("sandbox.read", {},
                               {"path": "a"},
                               version="tool-registry-v99")
    and not fw_policy.check_ceiling(
        "sandbox.read", {}, {"path": "a"},
        version="tool-registry-v99")[0])
check("T13b the copies agree under both registry versions, "
      "and an unknown version fails closed in both",
      agree_versioned and unknown_closed
      and fw_policy.known_version("tool-registry-v1")
      and ck_policy.known_version("tool-registry-v2")
      and not fw_policy.known_version("tool-registry-v99")
      and not ck_policy.known_version(None))
facing_agree = all(
    fw_policy.worker_facing(t) == ck_policy.worker_facing(t)
    and fw_policy.worker_facing(t) is not None
    and fw_policy.worker_facing(t, "tool-registry-v1") is None
    and ck_policy.worker_facing(t, "tool-registry-v1") is None
    for t in ("sandbox.write", "sandbox.read", "sandbox.flaky"))
check("T13b the worker-facing layer agrees between the "
      "copies under v2, and neither copy has one under v1",
      facing_agree)
imports_executor = False
for fname in os.listdir(os.path.join(SRC, "checker")):
    if fname.endswith(".py"):
        text = open(os.path.join(SRC, "checker", fname)).read()
        for mod in re.findall(r"^(?:from|import)\s+([\w.]+)",
                              text, re.M):
            if "executor" in mod:
                imports_executor = True
check("T13 the checker imports no executor module",
      not imports_executor)

# -- T14: replay executes nothing — a checker run over a
# history containing dispatches leaves the sandbox
# byte-identical.
store, d, tok, itok, did, sandbox = happy_world()


def tree_bytes(root):
    out = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            p = os.path.join(dirpath, name)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root)] = fh.read()
    return out


before = tree_bytes(sandbox)
verdict = run_checker(store)
check("T14 the sandbox is byte-identical after a checker run",
      tree_bytes(sandbox) == before
      and verdict["checks"]["dispatch_correspondence"]["result"]
      == "ok")

# -- T15: TOOL_STARTED is the executing thread's own first
# act (correction round 1). The witness is a probe inside the
# operation body itself: at the moment the body runs, it reads
# the record and finds its dispatch's start already standing,
# the claim already at "begun", and its own side effect not
# yet made — the start precedes the execution it names, from
# inside the execution.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d)
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/witness.txt",
                      "content": "seen"}, "req-witness")
did = res["dispatch_id"]
witness = {}
orig_perform = ex._perform


def probing_perform(tool, parameters):
    started = [e for e in store.all_events()
               if e["type"] == "TOOL_STARTED"
               and e["payload"].get("dispatch_id") == did]
    witness["start_standing"] = len(started) == 1
    witness["claim_begun"] = ex.claim_phase(did) == "begun"
    witness["file_absent"] = not os.path.exists(
        os.path.join(sandbox, "notes", "witness.txt"))
    return orig_perform(tool, parameters)


ex._perform = probing_perform
summary = ex.execute(did)
check("T15 at the moment the operation body runs, its start "
      "already stands in the record",
      witness == {"start_standing": True, "claim_begun": True,
                  "file_absent": True}
      and summary["outcome"] == "result"
      and read_file(os.path.join(sandbox, "notes",
                                 "witness.txt")) == "seen",
      json.dumps(witness))

store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d)
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/never-started.txt",
                      "content": "nope"}, "req-nostart")
did = res["dispatch_id"]
orig_started = d.record_tool_started


def broken_started(dispatch_id):
    raise RuntimeError("start ledger unavailable")


d.record_tool_started = broken_started
try:
    summary = ex.execute(did)
finally:
    d.record_tool_started = orig_started
outcomes = events_of(store, "TOOL_OUTCOME")
check("T15 a start that cannot be recorded: the operation "
      "never executes, and a failure outcome names the ground",
      summary["outcome"] == "failure"
      and not events_of(store, "TOOL_STARTED")
      and len(outcomes) == 1
      and outcomes[0]["payload"]["outcome"] == "failure"
      and "start ledger unavailable"
      in outcomes[0]["payload"]["detail"]
      and not os.path.exists(
          os.path.join(sandbox, "notes", "never-started.txt"))
      and ex.claim_phase(did) == "reported"
      and ex.recover() == [])

# -- T16: the recorded dispatch contract is checker-verified
# (correction round 1) — the registry version stands in every
# doorway dispatch, and referent mismatches appended past the
# doorway are reported by dispatch_correspondence.
store, d, tok, itok, did, sandbox = happy_world()
disp = events_of(store, "TOOL_DISPATCHED")
check("T16 every doorway dispatch records the registry "
      "version that governed it",
      len(disp) == 1
      and disp[0]["payload"].get("registry_version")
      == fw_policy.REGISTRY_VERSION == "tool-registry-v2")


def append_request(store, iid, rid, tool, params):
    store.append("TOOL_REQUESTED", "crew-1", [], {
        "instance_id": iid, "request_id": rid, "tool": tool,
        "parameters": params,
        "fingerprint": fw_policy.request_fingerprint(
            tool, params)})


def append_dispatch(store, iid, rid, did, tool, version="keep"):
    payload = {"instance_id": iid, "request_id": rid,
               "dispatch_id": did, "tool": tool}
    if version == "keep":
        payload["registry_version"] = fw_policy.REGISTRY_VERSION
    elif version is not None:
        payload["registry_version"] = version
    store.append("TOOL_DISPATCHED", "doorway", [], payload)


store, d, tok, itok, did, sandbox = happy_world()
iid = d.state()["tool_requests"][0]["instance_id"]
append_request(store, iid, "req-y", "sandbox.write",
               {"path": "notes/b.txt", "content": "x"})
append_dispatch(store, iid, "req-y", "dispatch-y",
                "sandbox.read")
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T16 a dispatch whose tool differs from its request's "
      "is reported",
      dc["result"] == "divergent"
      and any(p["kind"] == "dispatch_tool_differs_from_request"
              for p in dc["problems"]), json.dumps(dc))

store, d, tok, itok, did, sandbox = happy_world()
iid = d.state()["tool_requests"][0]["instance_id"]
append_request(store, iid, "req-z", "sandbox.write",
               {"path": "notes/c.txt", "content": "x"})
append_dispatch(store, iid, "req-z", "dispatch-z",
                "sandbox.write")
store.append("TOOL_STARTED", "executor", [], {
    "dispatch_id": "dispatch-z", "instance_id": iid,
    "request_id": "req-WRONG"})
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T16 a start naming a different request than its "
      "dispatch's is reported",
      dc["result"] == "divergent"
      and any(p["kind"] == "start_referent_mismatch"
              for p in dc["problems"]), json.dumps(dc))

store, d, tok, itok, did, sandbox = happy_world()
iid = d.state()["tool_requests"][0]["instance_id"]
append_request(store, iid, "req-w", "sandbox.write",
               {"path": "notes/d.txt", "content": "x"})
append_dispatch(store, iid, "req-w", "dispatch-w",
                "sandbox.write")
store.append("TOOL_OUTCOME", "executor", [], {
    "dispatch_id": "dispatch-w",
    "instance_id": "instance-WRONG", "request_id": "req-w",
    "outcome": "result"})
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T16 an outcome naming a different instance than its "
      "dispatch's is reported",
      dc["result"] == "divergent"
      and any(p["kind"] == "outcome_referent_mismatch"
              for p in dc["problems"]), json.dumps(dc))

store, d, tok, itok, did, sandbox = happy_world()
iid = d.state()["tool_requests"][0]["instance_id"]
append_request(store, iid, "req-v", "sandbox.write",
               {"path": "notes/e.txt", "content": "x"})
append_dispatch(store, iid, "req-v", "dispatch-v",
                "sandbox.write", version=None)
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T16 a dispatch with no registry version recorded is "
      "reported",
      dc["result"] == "divergent"
      and any(p["kind"] == "dispatch_registry_version_mismatch"
              for p in dc["problems"]), json.dumps(dc))

store, d, tok, itok, did, sandbox = happy_world()
iid = d.state()["tool_requests"][0]["instance_id"]
append_request(store, iid, "req-v", "sandbox.write",
               {"path": "notes/e.txt", "content": "x"})
append_dispatch(store, iid, "req-v", "dispatch-v",
                "sandbox.write", version="tool-registry-v99")
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T16 a dispatch governed by a foreign registry "
      "version is reported",
      dc["result"] == "divergent"
      and any(p["kind"] == "dispatch_registry_version_mismatch"
              for p in dc["problems"]), json.dumps(dc))

# -- T16b (Piece A3-CAT, settlement (c)): a dispatch recorded
# under v1 is verified under v1 — preserved, never
# reinterpreted under the current contract. A lawful v1
# dispatch stands clean; a v1 dispatch whose request exceeds
# the ceiling is divergent under v1's own contract.
store, d, tok, itok, did, sandbox = happy_world()
iid = d.state()["tool_requests"][0]["instance_id"]
append_request(store, iid, "req-hist", "sandbox.write",
               {"path": "notes/hist.txt", "content": "x"})
append_dispatch(store, iid, "req-hist", "dispatch-hist",
                "sandbox.write", version="tool-registry-v1")
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T16b a lawful dispatch recorded under v1 verifies "
      "clean under v1",
      dc["result"] == "ok", json.dumps(dc))

store, d, tok, itok, did, sandbox = happy_world()
iid = d.state()["tool_requests"][0]["instance_id"]
append_request(store, iid, "req-hist2", "sandbox.read",
               {"path": "secret/e.txt"})
append_dispatch(store, iid, "req-hist2", "dispatch-hist2",
                "sandbox.read", version="tool-registry-v1")
store.commit()
dc = run_checker(store)["checks"]["dispatch_correspondence"]
check("T16b a v1 dispatch exceeding its ceiling is "
      "divergent under v1's own contract",
      dc["result"] == "divergent"
      and any(p["kind"] == "dispatch_exceeds_ceiling"
              for p in dc["problems"]), json.dumps(dc))

# -- T17: the blocked start (correction round 2). The
# worker's start step is held past the operation deadline:
# the calling thread's join times out and it records the
# uncertain outcome while the worker is still inside its
# start step. When the worker's start step finally runs,
# the outcome already stands — so no start is recorded,
# the operation never runs, and the two threads' record
# access, serialized by the store's own lock, never drives
# the connection concurrently.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d, deadline=0.3)
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/blocked.txt",
                      "content": "never"}, "req-blocked")
did = res["dispatch_id"]
performed = []
orig_perform = ex._perform


def counting_perform(tool, parameters):
    performed.append(tool)
    return orig_perform(tool, parameters)


ex._perform = counting_perform
orig_started = d.record_tool_started
start_step_done = threading.Event()


def blocked_started(dispatch_id):
    try:
        time.sleep(1.5)  # far past the 0.3s deadline
        return orig_started(dispatch_id)
    finally:
        start_step_done.set()


d.record_tool_started = blocked_started
try:
    summary = ex.execute(did)
finally:
    d.record_tool_started = orig_started
check("T17 with the start step blocked past the deadline, "
      "execute() completes cleanly and reports uncertain",
      summary["ok"] and summary["outcome"] == "uncertain")
worker_settled = start_step_done.wait(10)
starts = [e for e in events_of(store, "TOOL_STARTED")
          if e["payload"].get("dispatch_id") == did]
outcomes = [e for e in events_of(store, "TOOL_OUTCOME")
            if e["payload"].get("dispatch_id") == did]
check("T17 no TOOL_STARTED is recorded once the uncertain "
      "outcome stands — no start after an outcome",
      worker_settled and not starts and len(outcomes) == 1
      and outcomes[0]["payload"]["outcome"] == "uncertain")
check("T17 the operation body never ran",
      performed == []
      and not os.path.exists(
          os.path.join(sandbox, "notes", "blocked.txt")))
entry = d.state()["dispatches"][did]
check("T17 the dispatch stands uncertain in the fold, "
      "with no start",
      entry["outcome"] == "uncertain"
      and entry["started_seq"] is None)
ex2 = Executor(d, sandbox, claim_dir=claims, deadline=2.0,
               executor_id="executor-2")
check("T17 recovery accounts the dispatch exactly as it "
      "stands — nothing to redo, nothing to settle",
      ex2.recover() == []
      and ex.claim_phase(did) == "reported")
verdict = run_checker(store)
dc = verdict["checks"]["dispatch_correspondence"]
check("T17 the checker reports dispatch_correspondence ok "
      "over the blocked-start history",
      dc["result"] == "ok", json.dumps(dc))

# -- T18: the deadline recheck (correction round 3). T17
# delays the start step BEFORE the doorway method is entered,
# so the delayed worker never holds the store lock. Here the
# delay sits inside the store's append of the TOOL_STARTED
# event — a call the doorway makes from within its
# store.serialized() section — so the worker sleeps while
# HOLDING the serialization lock, past the deadline. The
# calling thread's join times out and its uncertain-outcome
# report waits on the same lock; when the start finally
# stands and the lock frees, the worker rechecks the deadline
# before performing: expired, so the operation body never
# runs, and the caller's uncertain outcome is the dispatch's
# one outcome, standing after the start.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, claims = make_executor(d, deadline=0.3)
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/late.txt",
                      "content": "never"}, "req-late")
did = res["dispatch_id"]
performed = []
orig_perform = ex._perform


def counting_perform2(tool, parameters):
    performed.append(tool)
    return orig_perform(tool, parameters)


ex._perform = counting_perform2
orig_append = store.append


def slow_started_append(type_, actor, affected, payload):
    if type_ == "TOOL_STARTED":
        # Inside the doorway's serialized start section:
        # this thread holds the store lock while it sleeps.
        time.sleep(1.5)  # far past the 0.3s deadline
    return orig_append(type_, actor, affected, payload)


store.append = slow_started_append
error = None
t0 = time.monotonic()
try:
    summary = ex.execute(did)
except Exception as exc:  # concurrent access would land here
    error = exc
    summary = {}
finally:
    store.append = orig_append
elapsed = time.monotonic() - t0
check("T18 with the start report blocked inside the store "
      "lock past the deadline, execute() completes cleanly "
      "and reports uncertain — and took the lock's time, not "
      "the deadline's, proving the caller waited on the lock "
      "rather than writing concurrently",
      error is None and summary.get("ok")
      and summary.get("outcome") == "uncertain"
      and elapsed >= 1.2,
      f"elapsed={elapsed:.2f} error={error!r}")
check("T18 the operation body did not run after the "
      "deadline",
      performed == []
      and not os.path.exists(
          os.path.join(sandbox, "notes", "late.txt")))
starts = [e for e in events_of(store, "TOOL_STARTED")
          if e["payload"].get("dispatch_id") == did]
outcomes = [e for e in events_of(store, "TOOL_OUTCOME")
            if e["payload"].get("dispatch_id") == did]
entry = d.state()["dispatches"][did]
check("T18 exactly one outcome stands — the uncertain one — "
      "after exactly one start, and the fold agrees",
      len(starts) == 1 and len(outcomes) == 1
      and outcomes[0]["payload"]["outcome"] == "uncertain"
      and starts[0]["event_seq"] < outcomes[0]["event_seq"]
      and entry["outcome"] == "uncertain"
      and entry["started_seq"] == starts[0]["event_seq"])
ex2 = Executor(d, sandbox, claim_dir=claims, deadline=2.0,
               executor_id="executor-2")
check("T18 the claim stands accounted and recovery has "
      "nothing to redo",
      ex.claim_phase(did) == "reported" and ex2.recover() == [])
verdict = run_checker(store)
dc = verdict["checks"]["dispatch_correspondence"]
check("T18 the checker reports dispatch_correspondence ok "
      "over the start-then-uncertain history",
      dc["result"] == "ok", json.dumps(dc))

# -- T19: the worker-finishes-first deadline branch
# (correction round 4). T17 and T18 witness the caller's
# timeout path; the other path — the worker completes its
# start report, finds the deadline already expired at its
# recheck, and finishes BEFORE the caller's join returns,
# leaving the caller to record the uncertain outcome
# itself — is a microsecond race under the real clock.
# The executor's clock is a dependency, so a controlled
# clock places the worker deterministically: the start
# report runs with the clock inside the deadline, and a
# hook on the start-report path advances the clock past
# the deadline after the real append, before the worker's
# recheck reads it. The worker then genuinely finishes —
# in real time, at once — the real join returns with the
# worker already dead, and execute() takes its
# deadline_expired caller branch. The witness for the
# branch is the outcome's own detail: the caller branch
# names the start-report ground; the timeout branch's
# detail ("the operation outlived the deadline") is a
# different sentence and never appears here.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
base = tempfile.mkdtemp()
sandbox = os.path.join(base, "sandbox")
claims = os.path.join(base, "claims")


class FakeClock:
    """A monotonic clock whose reading the test sets."""

    def __init__(self, now):
        self.now = now

    def __call__(self):
        return self.now


fake = FakeClock(1000.0)
ex = Executor(d, sandbox, claim_dir=claims, deadline=5.0,
              executor_id="executor-1", clock=fake)
res = d.request_tool(itok, "sandbox.write",
                     {"path": "notes/expired.txt",
                      "content": "never"}, "req-expired")
did = res["dispatch_id"]
performed = []
orig_perform = ex._perform


def counting_perform3(tool, parameters):
    performed.append(tool)
    return orig_perform(tool, parameters)


ex._perform = counting_perform3
orig_started = d.record_tool_started


def advancing_started(dispatch_id):
    # The real start report, taken with the clock still
    # inside the deadline (1000.0 < 1005.0); the clock is
    # then advanced far past it, so the worker's recheck —
    # its next clock read — finds the deadline expired.
    result = orig_started(dispatch_id)
    fake.now = 2000.0
    return result


d.record_tool_started = advancing_started
try:
    summary = ex.execute(did)
finally:
    d.record_tool_started = orig_started
starts = [e for e in events_of(store, "TOOL_STARTED")
          if e["payload"].get("dispatch_id") == did]
outcomes = [e for e in events_of(store, "TOOL_OUTCOME")
            if e["payload"].get("dispatch_id") == did]
check("T19 with the clock advanced past the deadline "
      "between the start report and the recheck, the "
      "worker finishes first and the caller records the "
      "uncertain outcome — its detail names the "
      "start-report ground the timeout path never writes",
      summary["ok"] and summary["outcome"] == "uncertain"
      and len(outcomes) == 1
      and "start report completed after the operation "
      "deadline" in outcomes[0]["payload"].get(
          "detail", ""),
      json.dumps(outcomes))
check("T19 the operation body never ran",
      performed == []
      and not os.path.exists(
          os.path.join(sandbox, "notes", "expired.txt")))
entry = d.state()["dispatches"][did]
check("T19 exactly one start stands, before the one "
      "outcome, and the fold agrees",
      len(starts) == 1 and len(outcomes) == 1
      and starts[0]["event_seq"] < outcomes[0]["event_seq"]
      and entry["outcome"] == "uncertain"
      and entry["started_seq"] == starts[0]["event_seq"])
ex2 = Executor(d, sandbox, claim_dir=claims, deadline=2.0,
               executor_id="executor-2")
check("T19 the claim stands reported and recovery has "
      "nothing to redo",
      ex.claim_phase(did) == "reported"
      and ex2.recover() == [])
verdict = run_checker(store)
dc = verdict["checks"]["dispatch_correspondence"]
check("T19 the checker reports dispatch_correspondence ok "
      "over the start-then-caller-uncertain history",
      dc["result"] == "ok", json.dumps(dc))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES:", *FAILURES, sep="\n  ")
    sys.exit(1)
print("ALL PASS")
