"""Piece A3 tests — the bounded loop (agent layer; SPEC SHEET
Rev 6, R49–R51 and R55's loop increment), against the passed
scope PIECE-A3-SCOPE-2026-11-23.md (Rev 5) and its §8 acceptance
list, with scripted fake models against the real doorway and
executor and the A2 sandbox registry:

- the uptake witness: a tool result the loop's own dispatch
  produced is presented in the next package and visibly changes
  the next response (write → read-back → yield);
- iteration accounting for bare calls: decline, yield and
  provider failure each stand accounted by their LOOP_ITERATION;
- the step-ceiling stall at exactly the ceiling; the deadline
  enforced from the remaining budget — a call that cannot begin
  never begins, and a response arriving after expiry is not
  effected; bounds pinned against a mid-activation correction;
- doorway temporal admission: expiry refused and recorded, a
  forged later caller deadline powerless, an earlier hint
  refusing sooner, and no regime where the case carries no
  bounds;
- an uncertain outcome presented as uncertain, and a yield
  taken with the uncertainty standing;
- the stall withheld until in-flight dispatch accounting
  closes, a late outcome settling the uncertainty after the
  stall and accepted by the checker, and post-stall instance
  activity refused;
- the stall grounds distinguished (malformed / provider /
  runtime failure, the last by a forced package-assembly
  error); terminal exclusivity rejected whole;
- cursor integrity across interleaved outcomes; a case
  without bounds cannot loop; the restart witness (a fresh
  doorway over the same store and anchor state enforces the
  original deadline; the anchor binding removed, admission
  closes); runtime replaceability — the same scenario under a
  second trivial callable producing identical record effects;
- the checker's loop correspondence, ok on these histories
  and divergent on hand-appended violations; the two schema
  copies' agreement on the new state; replay executing
  nothing.

Cases are established through the office's real route
(generate → verify → judge → authorise, and correct for a
correction): loop_bounds is case content (correction round
1), named by the commission's recorded briefs, carried by
office.generate into the issued case, and changed — where a
test changes it — by office.correct. No case in this suite
is established by hand-built content — except the
correction-round-2 witnesses (T20), which establish cases
by direct store appends precisely because the route refuses
the malformed bounds they carry: the record can still be
made to hold them, and the strict contract must fail closed
there too. Round 2 also witnesses (T21) that a seat
credential cannot assert instance provenance: a
caller-supplied instance_id is stripped on the seat route,
so provenance in the record is doorway-established or
absent.

Run: PYTHONPATH=src python3 tests/unit/test_piece_a3_loop.py
Exits 0 when every check passes.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import projection  # noqa: E402
from framework.adapter import (AdapterFailure,  # noqa: E402
                               OpenAICompatibleAdapter)
from framework.doorway import (Doorway, DoorwayRefusal,  # noqa: E402
                               classify_case_change,
                               established_case_content)
from framework.executor import Executor  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (CONSTITUTION_HASH,  # noqa: E402
                              FrameworkStore, fold)
import checker.schema as ck_schema  # noqa: E402

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
BOUNDS = {"step_ceiling": 5, "deadline_seconds": 60}


def identify():
    return {"declaration": DECL, "provider_model_id": PROVIDER_ID}


def fresh(bounds=BOUNDS):
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    brief = dict(FULL)
    if bounds is not None:
        brief["loop_bounds"] = dict(bounds)
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
        "briefs": {"crew-1": dict(brief), "crew-2": dict(brief)},
    })
    store.commit()
    d = Doorway(store)
    office = Office(d)
    gen = Generator(d)
    tok = {s: d.issue_token(s) for s in
           ("orch-1", "exam-1", "dir-1", "crew-1", "crew-2")}
    return store, d, office, gen, tok


def issue_case(d, office, tok, seat):
    """The Piece 5 route, as the A1 suite walks it: office
    generation + verification (the draft assembled from the
    recorded commission — loop_bounds included where the
    brief names them), the examiner's judgement, the
    orchestrator's authorisation."""
    r = office.issue_new(tok["orch-1"], seat)
    assert r["ok"], r
    d.act(tok["exam-1"], "CASE_JUDGED",
          {"case_id": f"case-{seat}", "version": 1},
          view_seq=d.store.head_seq())
    office.authorise(tok["orch-1"], f"case-{seat}", 1)


def activate(store, d, office, gen, tok, seat="crew-1",
             grants=GRANTS):
    """The full A1 lifecycle for one seat slot, ending with an
    activated instance whose pinned case carries the bounds
    fresh() commissioned; returns (generate_result,
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


def loop_state(store):
    return fold(store.all_events(),
                store.get_run_id())["loop_activations"]


def make_executor(d, deadline=2.0, executor_id="executor-1"):
    base = tempfile.mkdtemp()
    sandbox = os.path.join(base, "sandbox")
    claims = os.path.join(base, "claims")
    ex = Executor(d, sandbox, claim_dir=claims, deadline=deadline,
                  executor_id=executor_id)
    return ex, sandbox, claims


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


def loop_check(store):
    return run_checker(store)["checks"]["loop_correspondence"]


class Script:
    """A scripted fake model: each step is a response dict, an
    exception to raise, or a function of the package. Every
    call is captured with the budget it was handed."""

    def __init__(self, steps):
        self.steps = list(steps)
        self.calls = []

    def __call__(self, package, budget=None):
        self.calls.append({"package": package, "budget": budget})
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        if callable(step):
            return step(package)
        return step


def contribute(text="draft text", cid="c-1"):
    return {"outcome": "proposals", "proposals": [{
        "type": "CONTRIBUTION",
        "payload": {"contribution_id": cid, "tree_part": "part-A",
                    "text": text}}]}


def tool_req(tool, parameters):
    return {"outcome": "tool_requests",
            "tool_requests": [{"tool": tool,
                               "parameters": parameters}]}


def yield_(summary="the work stands"):
    return {"outcome": "yield", "summary": summary}


def decline(reason="outside my capability"):
    return {"outcome": "decline", "reason": reason}


# -- T1: the uptake witness — write, then the write's own
# recorded outcome presented in the next package changes what
# the model does next (it reads the file back), then yield.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, _claims = make_executor(d)
seen = {}


def step2(package):
    seen["pkg2"] = package
    results = package["tool_results"]
    assert results and results[-1]["outcome"] == "result", results
    return tool_req("sandbox.read", {"path": "notes/a.txt"})


def step3(package):
    seen["pkg3"] = package
    results = package["tool_results"]
    assert results and \
        results[-1]["result"]["content"] == "hello loop", results
    return yield_("wrote the note and read it back")


model = Script([
    tool_req("sandbox.write", {"path": "notes/a.txt",
                               "content": "hello loop"}),
    step2, step3])
res = Loop(d, itok, model, executor=ex).run()
check("T1: the loop runs write → read-back → yield and returns "
      "the yield as its outcome",
      res["ok"] and res["outcome"] == "yield" and
      res["summary"] == "wrote the note and read it back")
check("T1: the write really happened in the sandbox",
      open(os.path.join(sandbox, "notes", "a.txt")).read() ==
      "hello loop")
iters = events_of(store, "LOOP_ITERATION")
check("T1: three iterations stand recorded, one per call, in "
      "order, under the loop identity",
      len(iters) == 3 and
      [e["payload"]["iteration"] for e in iters] == [1, 2, 3] and
      all(e["actor"] == "loop" for e in iters))
check("T1: the second package presents the first iteration's "
      "event and the write's outcome — the uptake the read-back "
      "answers",
      any(e["type"] == "LOOP_ITERATION" and
          e["event_seq"] == iters[0]["event_seq"]
          for e in seen["pkg2"]["delta"]) and
      seen["pkg2"]["tool_results"][-1]["outcome"] == "result")
check("T1: the remaining budget reaches the callable as a call "
      "parameter, outside the package it sees",
      model.calls[0]["budget"] is not None and
      0 < model.calls[0]["budget"] <= 60 and
      "budget" not in model.calls[0]["package"])
check("T1: the iteration payloads carry the pinned bounds and "
      "the activation binding",
      all(e["payload"]["step_ceiling"] == 5 and
          e["payload"]["deadline_seconds"] == 60 and
          e["payload"]["case_version"] == 1 for e in iters))
check("T1: the checker verifies the loop correspondence of "
      "the happy history",
      loop_check(store)["result"] == "ok")

# -- T2: iteration accounting for bare calls — a decline, a
# yield and a provider failure each stand accounted by the
# iteration recorded before their call; a decline records
# nothing of its own.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
before = len(store.all_events())
res = Loop(d, itok, Script([decline()])).run()
check("T2: a bare decline ends the loop as a caller-reported "
      "outcome — the iteration stands, nothing else is recorded "
      "for the decline",
      res["ok"] and res["outcome"] == "decline" and
      len(events_of(store, "LOOP_ITERATION")) == 1 and
      len(events_of(store, "LOOP_STALLED")) == 0 and
      len(store.all_events()) == before + 1)

store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
res = Loop(d, itok, Script([yield_()])).run()
check("T2: a bare yield ends the loop with its iteration "
      "accounted and no yield act recorded (the act is A5's)",
      res["ok"] and res["outcome"] == "yield" and
      len(events_of(store, "LOOP_ITERATION")) == 1 and
      len(events_of(store, "LOOP_STALLED")) == 0)

store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
res = Loop(d, itok, Script([RuntimeError("provider down")])).run()
stalls = events_of(store, "LOOP_STALLED")
check("T2: a provider failure stalls as provider_failure with "
      "the bare call accounted",
      not res["ok"] and res["ground"] == "provider_failure" and
      len(events_of(store, "LOOP_ITERATION")) == 1 and
      len(stalls) == 1 and
      stalls[0]["payload"]["iterations"] == 1 and
      stalls[0]["actor"] == "loop")

# -- T3: the step-ceiling stall, at exactly the ceiling.
store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 2, "deadline_seconds": 60})
r, itok = activate(store, d, office, gen, tok)
model = Script([contribute(cid="c-1"), contribute(cid="c-2"),
                contribute(cid="c-3")])
res = Loop(d, itok, model).run()
stalls = events_of(store, "LOOP_STALLED")
check("T3: the loop stalls at exactly the pinned ceiling — "
      "two iterations, two contributions, the third call never "
      "made",
      not res["ok"] and res["ground"] == "step_ceiling" and
      len(events_of(store, "LOOP_ITERATION")) == 2 and
      len(events_of(store, "CONTRIBUTION")) == 2 and
      len(model.calls) == 2 and len(stalls) == 1 and
      stalls[0]["payload"]["iterations"] == 2)
check("T3: the checker verifies the ceiling history",
      loop_check(store)["result"] == "ok")

# -- T4: the deadline, enforced from the remaining budget.
store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 5, "deadline_seconds": 0.3})
r, itok = activate(store, d, office, gen, tok)
time.sleep(0.45)
model = Script([contribute()])
res = Loop(d, itok, model).run()
check("T4: a loop starting after expiry cannot begin — "
      "deadline stall, zero iterations, the model never called",
      not res["ok"] and res["ground"] == "deadline" and
      res["iterations"] == 0 and len(model.calls) == 0 and
      len(events_of(store, "LOOP_ITERATION")) == 0 and
      events_of(store, "LOOP_STALLED")[0]["payload"]
      ["iterations"] == 0)

store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 5, "deadline_seconds": 0.5})
r, itok = activate(store, d, office, gen, tok)


def slow(package):
    time.sleep(0.8)
    return contribute()


res = Loop(d, itok, Script([slow])).run()
check("T4: a response arriving after the deadline is not "
      "effected — deadline stall, the contribution never lands",
      not res["ok"] and res["ground"] == "deadline" and
      len(events_of(store, "LOOP_ITERATION")) == 1 and
      len(events_of(store, "CONTRIBUTION")) == 0)

# The adapter's budget contract (Piece A3): a call that cannot
# begin within budget does not begin; the new outcomes cross
# the real adapter under the established strict validation.
adapter = OpenAICompatibleAdapter(
    endpoint="http://127.0.0.1:9/unreachable", model="m",
    api_key="k", timeout=5.0)
try:
    adapter({"seat": "crew-1"}, budget=0)
    budget_refused = False
except AdapterFailure as failure:
    budget_refused = failure.kind == "no_response"
check("T4: the adapter refuses a call whose budget is already "
      "exhausted — it does not begin", budget_refused)

adapter = OpenAICompatibleAdapter(model="m", api_key="k")
adapter._call = lambda messages: (
    json.dumps({"outcome": "yield", "summary": "standing"}),
    "m")
pkg = {"seat": "crew-1", "case_id": "case-crew-1",
       "case_version": 1, "position": 3, "case": {}}
out = adapter(pkg, budget=30)
check("T4: a yield crosses the real adapter as the yield "
      "outcome, budget accepted as a call parameter",
      out == {"outcome": "yield", "summary": "standing"})
adapter._call = lambda messages: (
    json.dumps({"outcome": "contribute", "text": "words",
                "tool_requests": [{"tool": "sandbox.read",
                                   "parameters":
                                       {"path": "notes/a.txt"}}]}),
    "m")
out = adapter(pkg, budget=30)
check("T4: a contribution carrying tool requests crosses the "
      "adapter whole — proposals plus requests",
      out["outcome"] == "proposals" and
      out["tool_requests"] == [{"tool": "sandbox.read",
                                "parameters":
                                    {"path": "notes/a.txt"}}])
adapter._call = lambda messages: (
    json.dumps({"outcome": "yield", "summary": "s",
                "tool_requests": []}), "m")
try:
    adapter(pkg, budget=30)
    combo_refused = False
except AdapterFailure as failure:
    combo_refused = failure.kind == "malformed_response"
check("T4: a yield combined with anything is malformed whole "
      "at the adapter", combo_refused)

# -- T5: bounds pinning — a mid-activation correction carrying
# larger bounds governs nothing; the pinned version's ceiling
# stops the loop.
store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 1, "deadline_seconds": 60})
r, itok = activate(store, d, office, gen, tok)
corr = office.correct(
    tok["orch-1"], "case-crew-1",
    {"loop_bounds": {"step_ceiling": 9,
                     "deadline_seconds": 600}})
check("T5: the correction rides the office's real route — "
      "classified semantic on the bounds change, version 2 "
      "established carrying the larger bounds",
      corr["ok"] and corr["version"] == 2 and
      corr["changed"] == ["loop_bounds"] and
      established_case_content(d.state(), "case-crew-1")[0]
      ["loop_bounds"] == {"step_ceiling": 9,
                          "deadline_seconds": 600})
model = Script([contribute(cid="c-1"), contribute(cid="c-2")])
res = Loop(d, itok, model).run()
iters = events_of(store, "LOOP_ITERATION")
check("T5: the pinned version's bounds govern the whole "
      "activation — the loop stalls at ceiling 1, not the "
      "corrected version's 9",
      not res["ok"] and res["ground"] == "step_ceiling" and
      len(iters) == 1 and
      iters[0]["payload"]["step_ceiling"] == 1 and
      iters[0]["payload"]["case_version"] == 1)
check("T5: the checker verifies the pinned-bounds history "
      "(its pinned bounds come from the assembly's version, "
      "not the latest)",
      loop_check(store)["result"] == "ok")

# -- T6: doorway temporal admission — derived by the doorway,
# unforgeable by the caller.
store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 5, "deadline_seconds": 0.4})
r, itok = activate(store, d, office, gen, tok)
time.sleep(0.55)
check("T6: after expiry the doorway refuses the dispatch and "
      "records the refusal — no dispatch stands",
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "notes/a.txt", "content": "x"}, "req-late")) and
      len(events_of(store, "TOOL_DISPATCHED")) == 0 and
      any(e["payload"].get("attempted_type") == "TOOL_DISPATCHED"
          and "deadline" in e["payload"]["ground"]
          for e in events_of(store, "REJECTION")))
check("T6: a forged later caller deadline does not extend "
      "the doorway's derived deadline",
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "notes/a.txt", "content": "x"}, "req-forged",
          budget_hint=9999)) and
      len(events_of(store, "TOOL_DISPATCHED")) == 0)

store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
check("T6: an earlier caller hint refuses sooner, and a "
      "non-numeric hint fails closed — neither moves the "
      "derived deadline",
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "notes/a.txt", "content": "x"}, "req-hint",
          budget_hint=0)) and
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "notes/a.txt", "content": "x"}, "req-hint-2",
          budget_hint="plenty")) and
      len(events_of(store, "TOOL_DISPATCHED")) == 0)
res_ok = d.request_tool(itok, "sandbox.write",
                        {"path": "notes/a.txt", "content": "x"},
                        "req-fine", budget_hint=30)
check("T6: within budget, admission passes as before",
      res_ok["ok"] and len(events_of(store, "TOOL_DISPATCHED"))
      == 1)

store, d, office, gen, tok = fresh(bounds=None)
r, itok = activate(store, d, office, gen, tok)
res_ok = d.request_tool(itok, "sandbox.write",
                        {"path": "notes/a.txt", "content": "x"},
                        "req-plain")
check("T6: where the pinned case carries no bounds, no "
      "temporal regime stands — admission is the grant "
      "check's alone, as in A2", res_ok["ok"])

# -- T7: an uncertain outcome presented as uncertain; a yield
# taken with the uncertainty standing.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, _sandbox, _claims = make_executor(d, deadline=0.3)
seen = {}


def step2_uncertain(package):
    seen["pkg"] = package
    return yield_("yielding with the uncertainty standing")


model = Script([
    tool_req("sandbox.flaky",
             {"path": "notes/u.txt", "mode": "hang-past-deadline",
              "hang_seconds": 1.2}),
    step2_uncertain])
res = Loop(d, itok, model, executor=ex).run()
check("T7: the loop yields with the dispatch's uncertainty "
      "standing — accounted, not resolved, not waited out",
      res["ok"] and res["outcome"] == "yield" and
      len(events_of(store, "LOOP_STALLED")) == 0)
check("T7: the uncertain outcome is presented as uncertain — "
      "in the settled results and in the standing dispatch "
      "state, never upgraded",
      seen["pkg"]["tool_results"][-1]["outcome"] == "uncertain"
      and seen["pkg"]["standing_dispatches"][-1]["outcome"] ==
      "uncertain" and
      seen["pkg"]["standing_dispatches"][-1]
      ["reconciled_outcome"] is None)

# -- T8: the stall withheld until in-flight accounting closes;
# a late outcome settles the uncertainty after the stall; no
# instance activity after the stall.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
res_r = d.request_tool(itok, "sandbox.write",
                       {"path": "notes/a.txt", "content": "x"},
                       "req-open")
check("T8: the stall route itself refuses while a dispatch "
      "of the instance stands without an outcome",
      refused(lambda: d.record_loop_stalled(
          r["assembly_id"], "deadline")) and
      len(events_of(store, "LOOP_STALLED")) == 0)
d.record_tool_outcome(res_r["dispatch_id"], "uncertain",
                      detail="accounting witness")
check("T8: with accounting closed the stall route records",
      d.record_loop_stalled(r["assembly_id"], "deadline")
      ["type"] == "LOOP_STALLED")

store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 5, "deadline_seconds": 0.5})
r, itok = activate(store, d, office, gen, tok)
ex, _sandbox, _claims = make_executor(d, deadline=2.0)
model = Script([
    tool_req("sandbox.flaky",
             {"path": "notes/h.txt", "mode": "hang-past-deadline",
              "hang_seconds": 3.0}),
    contribute()])
res = Loop(d, itok, model, executor=ex).run()
stalls = events_of(store, "LOOP_STALLED")
outcomes = events_of(store, "TOOL_OUTCOME")
did = res["dispatched"][0]["dispatch_id"]
check("T8: the deadline stall is recorded only after the "
      "in-flight dispatch's outcome lands — outcome first, "
      "stall after",
      not res["ok"] and res["ground"] == "deadline" and
      len(stalls) == 1 and len(outcomes) == 1 and
      outcomes[0]["payload"]["outcome"] == "uncertain" and
      outcomes[0]["event_seq"] < stalls[0]["event_seq"] and
      len(model.calls) == 1)
check("T8: after the stall, the instance's own act and "
      "request are refused and recorded",
      refused(lambda: d.act(
          itok, "CONTRIBUTION",
          {"contribution_id": "late", "tree_part": "part-A",
           "text": "too late", "case_id": "case-crew-1",
           "case_version": 1}, view_seq=store.head_seq())) and
      refused(lambda: d.request_tool(
          itok, "sandbox.read", {"path": "notes/h.txt"},
          "req-after-stall")))
late = d.record_tool_outcome(did, "result",
                             result={"mode": "hang-past-deadline"})
check("T8: a delayed report attributable to the stalled "
      "activation's uncertain dispatch still lands after the "
      "stall, and the checker accepts the history — the late "
      "settlement is accounting, not activity",
      late["type"] == "TOOL_OUTCOME" and
      loop_check(store)["result"] == "ok")

# -- T9: the stall grounds distinguished.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
res = Loop(d, itok, Script([
    {"outcome": "yield", "summary": "s",
     "tool_requests": [{"tool": "sandbox.read",
                        "parameters": {"path": "notes/a.txt"}}]}
])).run()
check("T9: a yield combined with tool requests is rejected "
      "whole — malformed_response stall, nothing dispatched",
      not res["ok"] and res["ground"] == "malformed_response"
      and len(events_of(store, "TOOL_DISPATCHED")) == 0 and
      len(events_of(store, "LOOP_ITERATION")) == 1)

store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
res = Loop(d, itok, Script([
    {"outcome": "decline", "reason": "no",
     "proposals": []}])).run()
check("T9: a decline combined with proposals is rejected "
      "whole — malformed_response stall",
      not res["ok"] and res["ground"] == "malformed_response")

store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
loop = Loop(d, itok, Script([contribute()]))


def broken_package(ctx):
    raise RuntimeError("package assembly broke")


loop._build_package = broken_package
res = loop.run()
check("T9: a failure in the loop's own package construction "
      "stalls as runtime_failure and counts no iteration",
      not res["ok"] and res["ground"] == "runtime_failure" and
      len(events_of(store, "LOOP_ITERATION")) == 0 and
      events_of(store, "LOOP_STALLED")[0]["payload"]
      ["iterations"] == 0)

# -- T10: cursor integrity across interleaved outcomes.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, _sandbox, _claims = make_executor(d)
start_head = store.head_seq()
seen = {}


def mixed(package):
    return {"outcome": "proposals",
            "proposals": [{
                "type": "CONTRIBUTION",
                "payload": {"contribution_id": "c-mix",
                            "tree_part": "part-A",
                            "text": "with a write"}}],
            "tool_requests": [{
                "tool": "sandbox.write",
                "parameters": {"path": "notes/m.txt",
                               "content": "mix"}}]}


def step2_cursor(package):
    seen["pkg2"] = package
    return contribute(cid="c-2")


def step3_cursor(package):
    seen["pkg3"] = package
    return yield_()


Loop(d, itok, Script([mixed, step2_cursor, step3_cursor]),
     executor=ex).run()
iters = events_of(store, "LOOP_ITERATION")
la = loop_state(store)[r["assembly_id"]]
check("T10: cursor ranges chain without gaps or overlaps in "
      "the fold, each opening where the previous closed, the "
      "first at the loop's starting head",
      [i["cursor_from"] for i in la["iterations"]] ==
      [start_head] + [i["cursor_to"] for i in la["iterations"]][:-1]
      and all(i["cursor_to"] >= i["cursor_from"]
              for i in la["iterations"]))
d2seqs = [e["event_seq"] for e in seen["pkg2"]["delta"]]
d3seqs = [e["event_seq"] for e in seen["pkg3"]["delta"]]
check("T10: every event is presented exactly once as new "
      "across the deltas, and each iteration event is presented "
      "in the following iteration's delta",
      not set(d2seqs) & set(d3seqs) and
      iters[0]["event_seq"] in d2seqs and
      iters[1]["event_seq"] in d3seqs and
      any(e["type"] == "TOOL_OUTCOME"
          for e in seen["pkg2"]["delta"]) and
      any(e["type"] == "CONTRIBUTION"
          for e in seen["pkg2"]["delta"]))
check("T10: the checker verifies the cursor history",
      loop_check(store)["result"] == "ok")

# -- T11: a case without bounds cannot loop; neither can a
# seat credential or an unactivated instance.
store, d, office, gen, tok = fresh(bounds=None)
r, itok = activate(store, d, office, gen, tok)
model = Script([contribute()])
res = Loop(d, itok, model).run()
check("T11: no bounds, no loop — refused before the first "
      "model call, nothing recorded",
      not res["ok"] and res["outcome"] == "not_run" and
      len(model.calls) == 0 and
      len(events_of(store, "LOOP_ITERATION")) == 0 and
      len(events_of(store, "LOOP_STALLED")) == 0)
res = Loop(d, tok["crew-1"], model).run()
check("T11: a seat credential does not run a loop — the loop "
      "runs only under an instance's own credential",
      not res["ok"] and res["outcome"] == "not_run" and
      len(model.calls) == 0)

# -- T12: the restart witness — a fresh doorway over the same
# store recovers the anchor; the original deadline is
# enforced, never re-based; the anchor binding removed,
# admission closes.
store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 5, "deadline_seconds": 0.8})
r, itok = activate(store, d, office, gen, tok)
iid = r["instance_id"]
d2 = Doorway(store)
remaining2, problem2 = d2.activation_remaining(iid)
check("T12: a fresh doorway over the same store recovers the "
      "activation anchor — the remaining budget is the "
      "original deadline's, already partly spent",
      problem2 is None and remaining2 is not None and
      0 < remaining2 < 0.8)
time.sleep(0.95)
remaining3, _p = d2.activation_remaining(iid)
tok2 = d2.issue_instance_token(iid)
check("T12: after the original deadline passes, the fresh "
      "doorway enforces it — no fresh deadline is granted by "
      "the restart, and admission refuses",
      remaining3 is not None and remaining3 <= 0 and
      refused(lambda: d2.request_tool(
          tok2, "sandbox.write",
          {"path": "notes/a.txt", "content": "x"}, "req-restart")))
os.remove(d._anchor_path)
remaining4, problem4 = d.activation_remaining(iid)
check("T12: with the anchor binding removed, the deadline "
      "cannot be established — admission fails closed rather "
      "than substituting a clock or a fresh deadline",
      problem4 is not None and
      refused(lambda: d.request_tool(
          itok, "sandbox.write",
          {"path": "notes/a.txt", "content": "x"}, "req-naked")))

# -- T13: runtime replaceability — the same scripted scenario
# under a second, trivial callable produces identical record
# effects (R51).
def scenario(model):
    store, d, office, gen, tok = fresh()
    r, itok = activate(store, d, office, gen, tok)
    ex, _s, _c = make_executor(d)
    res = Loop(d, itok, model, executor=ex).run()
    effects = [(e["type"], e["actor"]) for e in store.all_events()
               if e["type"] in ("LOOP_ITERATION", "LOOP_STALLED",
                                "CONTRIBUTION", "TOOL_REQUESTED",
                                "TOOL_DISPATCHED", "TOOL_STARTED",
                                "TOOL_OUTCOME")]
    return res, effects


def scripted_model():
    return Script([
        tool_req("sandbox.write", {"path": "notes/a.txt",
                                   "content": "hello loop"}),
        yield_()])


class TrivialModel:
    """A second callable of a different kind: a plain object
    answering from a table, no script machinery."""

    def __init__(self):
        self.n = 0

    def __call__(self, package, budget=None):
        self.n += 1
        if self.n == 1:
            return {"outcome": "tool_requests",
                    "tool_requests": [{
                        "tool": "sandbox.write",
                        "parameters": {"path": "notes/a.txt",
                                       "content": "hello loop"}}]}
        return {"outcome": "yield", "summary": "the work stands"}


res1, effects1 = scenario(scripted_model())
res2, effects2 = scenario(TrivialModel())
check("T13: the same scenario under a second trivial callable "
      "produces identical record effects — the loop's record "
      "does not depend on which runtime drives it",
      res1["outcome"] == res2["outcome"] == "yield" and
      effects1 == effects2 and len(effects1) > 0)

# -- T14: the checker's loop correspondence against
# hand-appended violations (the doorway bypassed, as in the
# A1/A2 checker witnesses).
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
Loop(d, itok, Script([contribute(), yield_()])).run()
check("T14: the checker is ok on the doorway-produced history "
      "before violations are appended",
      loop_check(store)["result"] == "ok")
aid = r["assembly_id"]
iid = r["instance_id"]
state = d.state()
entry = state["assemblies"][aid]
store.append("LOOP_ITERATION", "loop", [iid], {
    "assembly_id": aid, "instance_id": iid,
    "activated_seq": entry["activated_seq"],
    "case_id": entry["case_id"],
    "case_version": entry["case_version"], "iteration": 7,
    "step_ceiling": 5, "deadline_seconds": 60,
    "cursor_from": 0, "cursor_to": 0})
store.commit()
lc = loop_check(store)
kinds = {p["kind"] for p in lc.get("problems", [])}
check("T14: a hand-appended iteration with broken numbering "
      "and a broken cursor chain is divergent, naming both",
      lc["result"] == "divergent" and
      "iteration_numbering" in kinds and
      "cursor_chain_broken" in kinds)

store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
store.append("LOOP_STALLED", "crew-1", [r["instance_id"]], {
    "assembly_id": r["assembly_id"],
    "instance_id": r["instance_id"],
    "activated_seq":
        d.state()["assemblies"][r["assembly_id"]]
        ["activated_seq"],
    "case_id": "case-crew-1", "case_version": 1,
    "ground": "deadline", "iterations": 0})
store.commit()
lc = loop_check(store)
kinds = {p["kind"] for p in lc.get("problems", [])}
check("T14: a stall recorded under a seat's actor — not the "
      "loop identity — is divergent",
      lc["result"] == "divergent" and
      "stall_wrong_actor" in kinds)

# -- T15: the schema copies agree on the new state, and replay
# executes nothing.
check("T15: the two projection schemas remain canonically "
      "identical with the loop state and the case bounds in "
      "both",
      json.dumps(projection.SCHEMA, sort_keys=True) ==
      json.dumps(ck_schema.SCHEMA, sort_keys=True) and
      "loop_activations" in projection.SCHEMA["f"] and
      "loop_bounds" in
      projection.SCHEMA["f"]["cases"]["v"]["f"]["versions"]
      ["v"]["f"]["content"]["v"]["f"])

store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
ex, sandbox, _claims = make_executor(d)
Loop(d, itok, Script([
    tool_req("sandbox.write", {"path": "notes/a.txt",
                               "content": "hello loop"}),
    yield_()]), executor=ex).run()


def tree_bytes(root):
    out = {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            p = os.path.join(base, name)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root)] = fh.read()
    return out


before = tree_bytes(sandbox)
verdict = run_checker(store)
check("T15: the checker's replay of a loop history executes "
      "nothing — the sandbox is byte-identical afterwards, "
      "and the verdict's loop correspondence is ok",
      tree_bytes(sandbox) == before and
      verdict["checks"]["loop_correspondence"]["result"] ==
      "ok")

# -- T16 (correction round 1): the act's view basis is the
# frozen package head — the view the model actually received.
# (a) An unrelated contribution landing between the freeze
# and adjudication does not refuse the act, and the act's
# recorded basis is the frozen position, not the submission
# head: it stands flagged stale_basis, where the submission
# head would have recorded a fictional current basis.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)


def step_unrelated(package):
    d.act(tok["crew-2"], "CONTRIBUTION",
          {"contribution_id": "c-other", "tree_part": "part-B",
           "text": "another seat's work on another part"},
          view_seq=store.head_seq())
    return contribute(cid="c-1")


res = Loop(d, itok, Script([step_unrelated, yield_()])).run()
mine = [e for e in events_of(store, "CONTRIBUTION")
        if e["payload"].get("contribution_id") == "c-1"]
check("T16: an unrelated contribution between freeze and "
      "submission does not refuse the act — it stands, made "
      "from its frozen basis (flagged stale_basis, not "
      "re-based to the submission head)",
      res["ok"] and res["outcome"] == "yield" and
      len(mine) == 1 and
      mine[0]["payload"].get("stale_basis") is True and
      any(e["payload"].get("contribution_id") == "c-other"
          for e in events_of(store, "CONTRIBUTION")))
check("T16: the checker verifies the frozen-basis history",
      loop_check(store)["result"] == "ok")

# (b) A genuine subject change between the freeze and
# adjudication — the case itself corrected — still refuses
# the act under R31, at the frozen view position.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)


def step_correcting(package):
    office.correct(tok["orch-1"], "case-crew-1",
                   {"assignment": "Draft the A section — "
                                  "revised"})
    return contribute(cid="c-1")


res = Loop(d, itok, Script([step_correcting, yield_()])).run()
frozen_head = events_of(store, "LOOP_ITERATION")[0]["payload"][
    "cursor_to"]
r31 = [e for e in events_of(store, "REJECTION")
       if e["payload"].get("attempted_type") == "CONTRIBUTION"
       and "R31" in e["payload"].get("ground", "")]
check("T16: a genuine subject change after the freeze "
      "refuses the act under R31 — the contribution never "
      "lands, and the refusal records the frozen view "
      "position it was judged against",
      res["ok"] and res["outcome"] == "yield" and
      len(events_of(store, "CONTRIBUTION")) == 0 and
      len(r31) == 1 and
      r31[0]["payload"].get("view_seq") == frozen_head and
      any("R31" in f.get("ground", "") for f in res["refused"]))

# -- T17 (correction round 1): instance provenance — acts
# under an instance credential are attributable to the
# instance; after a stall they are refused, while the seat's
# own acts are untouched, in the doorway and in the checker.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
iid = r["instance_id"]
Loop(d, itok, Script([contribute(cid="c-1"), yield_()])).run()
mine = [e for e in events_of(store, "CONTRIBUTION")
        if e["payload"].get("contribution_id") == "c-1"]
check("T17: an act recorded under the instance credential "
      "carries the instance's provenance in the record",
      len(mine) == 1 and
      mine[0]["payload"].get("instance_id") == iid and
      mine[0]["actor"] == "crew-1")

store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
iid = r["instance_id"]
res_r = d.request_tool(itok, "sandbox.write",
                       {"path": "notes/a.txt", "content": "x"},
                       "req-open")
d.record_tool_outcome(res_r["dispatch_id"], "uncertain",
                      detail="accounting witness")
d.record_loop_stalled(r["assembly_id"], "deadline")
check("T17: after the stall, the instance's own act is "
      "refused and recorded, while the seat's own act — under "
      "its plain credential, carrying no provenance — still "
      "records",
      refused(lambda: d.act(
          itok, "CONTRIBUTION",
          {"contribution_id": "late", "tree_part": "part-A",
           "text": "too late", "case_id": "case-crew-1",
           "case_version": 1}, view_seq=store.head_seq())) and
      d.act(tok["crew-1"], "CONTRIBUTION",
            {"contribution_id": "seat-work",
             "tree_part": "part-A", "text": "the seat's own"},
            view_seq=store.head_seq())["type"] == "CONTRIBUTION")
check("T17: the checker accepts that history — the seat's "
      "post-stall act is not the instance's activity",
      loop_check(store)["result"] == "ok")
store.append("CONTRIBUTION", "crew-1", ["case-crew-1"], {
    "contribution_id": "sneaked", "tree_part": "part-A",
    "text": "an instance act after its stall",
    "case_id": "case-crew-1", "case_version": 1,
    "instance_id": iid})
store.commit()
lc = loop_check(store)
kinds = {p["kind"] for p in lc.get("problems", [])}
check("T17: a hand-appended post-stall act carrying the "
      "instance's provenance is divergent in the checker — "
      "instance_act_after_stall — while the seat act above "
      "was not flagged",
      lc["result"] == "divergent" and
      "instance_act_after_stall" in kinds)

# -- T18 (correction round 1): loop_bounds through the real
# case route — carried by generate into the issued case,
# classified on correction, and refused malformed at the
# office and doorway boundaries, never stripped.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
content, ver_no = established_case_content(d.state(),
                                           "case-crew-1")
check("T18: the issued case's content carries the brief's "
      "loop_bounds — the office route delivered them, at "
      "version 1",
      ver_no == 1 and content.get("loop_bounds") == BOUNDS)
head_before = store.head_seq()
bad = office.correct(
    tok["orch-1"], "case-crew-1",
    {"loop_bounds": {"step_ceiling": 0,
                     "deadline_seconds": 60}})
bad2 = office.correct(
    tok["orch-1"], "case-crew-1",
    {"loop_bounds": {"step_ceiling": 3}})
check("T18: malformed bounds are refused at the office "
      "boundary — a zero ceiling and a missing deadline both "
      "fail preflight, and nothing is appended for either",
      not bad["ok"] and not bad2["ok"] and
      any("loop_bounds" in p for p in bad["problems"]) and
      any("loop_bounds" in p for p in bad2["problems"]) and
      store.head_seq() == head_before)
check("T18: malformed bounds are refused at the doorway "
      "boundary too — a correction carrying them does not "
      "record, and the refusal stands",
      refused(lambda: d.act(
          tok["orch-1"], "CASE_CORRECTED",
          {"case_id": "case-crew-1", "version": 2,
           "loop_bounds": {"step_ceiling": "five",
                           "deadline_seconds": 60},
           "representational": False},
          view_seq=store.head_seq())) and
      any("loop_bounds" in e["payload"].get("ground", "")
          for e in events_of(store, "REJECTION")))

# -- T19 (correction round 1): the iteration/deadline
# boundary — expiry before the iteration event counts no
# iteration; expiry after it still invokes the callable,
# with the exhausted budget, and no provider request begins.
store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 5, "deadline_seconds": 0.45})
r, itok = activate(store, d, office, gen, tok)
model = Script([contribute()])
loop = Loop(d, itok, model)
real_build = loop._build_package


def slow_build(ctx):
    time.sleep(0.6)
    return real_build(ctx)


loop._build_package = slow_build
res = loop.run()
stalls = events_of(store, "LOOP_STALLED")
check("T19: package construction crossing the deadline "
      "counts no iteration — the doorway's recording decision "
      "refuses the event (recorded), the model is never "
      "called, and the deadline stall stands at zero",
      not res["ok"] and res["ground"] == "deadline" and
      len(events_of(store, "LOOP_ITERATION")) == 0 and
      len(model.calls) == 0 and len(stalls) == 1 and
      stalls[0]["payload"]["iterations"] == 0 and
      any(e["payload"].get("attempted_type") == "LOOP_ITERATION"
          and "deadline" in e["payload"].get("ground", "")
          for e in events_of(store, "REJECTION")))

store, d, office, gen, tok = fresh(
    bounds={"step_ceiling": 5, "deadline_seconds": 0.45})
r, itok = activate(store, d, office, gen, tok)
adapter = OpenAICompatibleAdapter(model="m", api_key="k")
provider_calls = []


def provider(messages):
    provider_calls.append(messages)
    return (json.dumps({"outcome": "yield",
                        "summary": "standing"}), "m")


adapter._call = provider
budgets = []


def expiring_model(package, budget=None):
    budgets.append(budget)
    return adapter(package, budget=budget)


real_record = d.record_loop_iteration


def record_then_expire(*args, **kwargs):
    ev = real_record(*args, **kwargs)
    time.sleep(0.6)
    return ev


d.record_loop_iteration = record_then_expire
res = Loop(d, itok, expiring_model).run()
stalls = events_of(store, "LOOP_STALLED")
check("T19: expiry immediately after the iteration event "
      "still invokes the callable — with the exhausted "
      "budget — and the adapter begins no provider request; "
      "the iteration stands counted and the stall is the "
      "deadline's",
      not res["ok"] and res["ground"] == "deadline" and
      len(budgets) == 1 and budgets[0] is not None and
      budgets[0] <= 0 and provider_calls == [] and
      len(events_of(store, "LOOP_ITERATION")) == 1 and
      len(stalls) == 1 and
      stalls[0]["payload"]["iterations"] == 1)

# -- T20 (correction round 2): the strict bounds contract
# everywhere — malformed bounds recorded directly into a
# case (the route refused them, so the record is built by
# direct appends, as a malformed history would stand)
# establish no regime: the loop cannot run on the
# activation, and the checker names the pinned bounds
# malformed rather than treating them as a governing
# contract or as simply no bounds.
def issue_case_direct(store, office, seat, bounds):
    """The case lifecycle appended directly to the store —
    the doorway bypassed — with the given loop_bounds in the
    verified content. The payloads are the office route's
    own shapes; only the route is skipped."""
    content = office.generate(seat)
    content["loop_bounds"] = bounds
    store.append("CASE_VERIFIED", "orch-1", [], content)
    store.append("CASE_JUDGED", "exam-1", [],
                 {"case_id": f"case-{seat}", "version": 1})
    store.append("CASE_ISSUED", "orch-1", [],
                 {"case_id": f"case-{seat}", "version": 1,
                  "seat": seat})
    store.commit()


def activate_direct(store, d, office, gen, tok, bounds,
                    seat="crew-1"):
    """The A1 lifecycle over a directly-established case."""
    issue_case_direct(store, office, seat, bounds)
    gen.propose(tok["orch-1"], seat, part="part-A",
                role_requirements="a careful drafting model")
    r = gen.generate(tok["orch-1"], seat, identify,
                     skills=SKILLS, grants=GRANTS)
    assert r["ok"], r
    gen.verify(tok["orch-1"], r["assembly_id"])
    d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
          gen.judgement(r["assembly_id"]),
          view_seq=store.head_seq())
    packed = gen.pack(tok["orch-1"], r["assembly_id"])
    gen.authorise(tok["orch-1"], r["assembly_id"])
    gen.activate(tok["orch-1"], r["assembly_id"])
    return r, packed["instance_token"]


MALFORMED_BOUNDS = [
    ("a zero step ceiling",
     {"step_ceiling": 0, "deadline_seconds": 60}),
    ("a zero deadline",
     {"step_ceiling": 5, "deadline_seconds": 0}),
    ("a negative deadline",
     {"step_ceiling": 5, "deadline_seconds": -30}),
    ("a NaN deadline",
     {"step_ceiling": 5, "deadline_seconds": float("nan")}),
    ("an infinite deadline",
     {"step_ceiling": 5, "deadline_seconds": float("inf")}),
]
for label, bad_bounds in MALFORMED_BOUNDS:
    store, d, office, gen, tok = fresh(bounds=None)
    r, itok = activate_direct(store, d, office, gen, tok,
                              bad_bounds)
    model = Script([contribute()])
    res = Loop(d, itok, model).run()
    check(f"T20: malformed pinned bounds ({label}) establish "
          "no regime — the loop cannot run on the activation, "
          "no iteration and no stall stand",
          not res["ok"] and res["outcome"] == "not_run" and
          len(model.calls) == 0 and
          len(events_of(store, "LOOP_ITERATION")) == 0 and
          len(events_of(store, "LOOP_STALLED")) == 0)
    lc = loop_check(store)
    kinds = {p["kind"] for p in lc.get("problems", [])}
    check(f"T20: the checker names the malformed pinned "
          f"bounds ({label}) divergent — "
          "pinned_bounds_malformed — rather than a governing "
          "contract or plain no-bounds",
          lc["result"] == "divergent" and
          "pinned_bounds_malformed" in kinds)

store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
bad_inf = office.correct(
    tok["orch-1"], "case-crew-1",
    {"loop_bounds": {"step_ceiling": 3,
                     "deadline_seconds": float("inf")}})
check("T20: the office route refuses an infinite deadline "
      "as it refuses NaN — preflight names the bounds and "
      "nothing is appended",
      not bad_inf["ok"] and
      any("loop_bounds" in p for p in bad_inf["problems"]))
check("T20: the doorway route refuses an infinite deadline "
      "too — a correction carrying one does not record, and "
      "the refusal stands",
      refused(lambda: d.act(
          tok["orch-1"], "CASE_CORRECTED",
          {"case_id": "case-crew-1", "version": 2,
           "loop_bounds": {"step_ceiling": 3,
                           "deadline_seconds": float("inf")},
           "representational": False},
          view_seq=store.head_seq())) and
      any("loop_bounds" in e["payload"].get("ground", "")
          for e in events_of(store, "REJECTION")))

# -- T21 (correction round 2): a seat credential cannot
# assert instance provenance — a caller-supplied instance_id
# under the seat's plain credential is stripped before the
# act records, so the record cannot falsely attribute the
# act to the (stalled) instance it names; the pair route
# strips it identically.
store, d, office, gen, tok = fresh()
r, itok = activate(store, d, office, gen, tok)
iid = r["instance_id"]
res_r = d.request_tool(itok, "sandbox.write",
                       {"path": "notes/a.txt", "content": "x"},
                       "req-open")
d.record_tool_outcome(res_r["dispatch_id"], "uncertain",
                      detail="accounting witness")
d.record_loop_stalled(r["assembly_id"], "deadline")
ev = d.act(tok["crew-1"], "CONTRIBUTION",
           {"contribution_id": "seat-mislabelled",
            "tree_part": "part-A",
            "text": "the seat's own work, mislabelled with "
                    "the stalled instance's id",
            "instance_id": iid},
           view_seq=store.head_seq())
check("T21: an act under the plain seat credential carrying "
      "the stalled instance's id still records as the seat's "
      "own act — with the supplied instance_id stripped, so "
      "no provenance attributing it to the instance stands",
      ev["type"] == "CONTRIBUTION" and
      ev["actor"] == "crew-1" and
      "instance_id" not in ev["payload"])
check("T21: the checker does not flag the stripped act — "
      "the history's loop correspondence is ok, the stall "
      "notwithstanding",
      loop_check(store)["result"] == "ok")
state = d.state()
current, _v = established_case_content(state, "case-crew-1")
draft = dict(current)
draft["version"] = 2
draft["instance_id"] = iid
draft["representational"] = not classify_case_change(
    current, draft)
ev1, ev2 = d.submit_pair(
    tok["orch-1"],
    [("CASE_CORRECTED", draft),
     ("CASE_VERIFIED", {"case_id": "case-crew-1", "version": 2,
                        "instance_id": iid})],
    view_seq=store.head_seq())
check("T21: the pair route strips a supplied instance_id "
      "identically — neither recorded half of the correction "
      "carries it",
      "instance_id" not in ev1["payload"] and
      "instance_id" not in ev2["payload"])

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
