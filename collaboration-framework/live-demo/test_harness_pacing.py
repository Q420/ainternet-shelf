"""Witnesses for the iteration pacing mechanism (first
live demonstration release examination, INDEX 412,
phase-2 matter 1): the IterationPacer the harness's
phase-2 path places around the adapter as the loop's
model callable.

Every witness runs offline on a simulated monotonic
clock — no real 65-second waits, no provider request.
The pacer is exercised exactly as the loop exercises
its model: called with (package, budget=..., deadline=
..., mode=...) where deadline is the activation's
absolute monotonic deadline.

The witnesses establish:
- the first call of a run is not delayed;
- ordinary spacing: a successive call starts no
  earlier than 65 s after the previous call's START,
  including when the previous call itself consumed
  time (start-to-start, not end-to-start);
- variable preparation time: a long gap between calls
  needs no additional wait; a short gap waits only the
  remainder;
- expiry during a pacing wait: the deadline passes
  while waiting, the wrapped model is never invoked,
  and the refusal is an AdapterFailure the loop
  answers with its standing deadline path;
- a wait that ends before the deadline proceeds;
- transparency: attribute reads and writes through
  the pacer land on the wrapped model (the loop's
  evidence and flag-staging seams), the mode argument
  is forwarded untouched, and a failure from the
  wrapped model propagates unretried — its start
  still paces the next call.

Run: PYTHONPATH=src python3 \
    live-demo/test_harness_pacing.py
Exits 0 when every check passes.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from framework.adapter import AdapterFailure  # noqa: E402
import first_worker_run as harness  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail else ""))
    if not cond:
        FAILURES.append(name)


class FakeClock:
    """A monotonic clock advanced only by sleep() and
    by the test itself: deterministic, and a sleep
    request is recorded so the wait itself is
    witnessed, not inferred."""

    def __init__(self, start=1000.0):
        self.now = float(start)
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

    def advance(self, seconds):
        self.now += seconds


class StubModel:
    """The wrapped callable: records each invocation's
    start on the fake clock, consumes a fixed span per
    call, and carries the attribute surface the loop
    touches (evidence seam, flag staging, model name)."""

    def __init__(self, clock, consume=0.0, fail=False):
        self.clock = clock
        self.consume = consume
        self.fail = fail
        self.starts = []
        self.modes = []
        self.model = "stub/model"
        self.last_response_evidence = "unset"
        self.staged_flag = "unstaged"

    def stage_disable_tool_validation(self, value):
        self.staged_flag = value

    def __call__(self, package, budget=None, deadline=None,
                 mode=None):
        self.starts.append(self.clock.now)
        self.modes.append(mode)
        self.clock.advance(self.consume)
        if self.fail:
            raise AdapterFailure("provider_error", "boom")
        return {"outcome": "yield"}


def pacer_for(clock, stub):
    return harness.IterationPacer(
        stub, monotonic_clock=clock.monotonic,
        sleeper=clock.sleep)


# --------------------------------------- first call free
def test_first_call_not_delayed():
    clock = FakeClock()
    stub = StubModel(clock)
    pacer = pacer_for(clock, stub)
    pacer({}, budget=600.0, deadline=1600.0)
    check("the first call of a run is not delayed: it "
          "starts at once and no sleep is requested",
          stub.starts == [1000.0] and clock.sleeps == [],
          f"starts={stub.starts} sleeps={clock.sleeps}")


# -------------------------------------- ordinary spacing
def test_ordinary_spacing():
    clock = FakeClock()
    stub = StubModel(clock, consume=10.0)
    pacer = pacer_for(clock, stub)
    pacer({}, budget=600.0, deadline=1600.0)
    pacer({}, budget=590.0, deadline=1600.0)
    check("ordinary spacing: the second call starts "
          "exactly 65 s after the first call's START, "
          "though the first call itself consumed 10 s — "
          "the wait is the 55 s remainder, start-to-start",
          stub.starts == [1000.0, 1065.0]
          and clock.sleeps == [55.0],
          f"starts={stub.starts} sleeps={clock.sleeps}")
    pacer({}, budget=580.0, deadline=1600.0)
    check("the spacing binds every successive pair: "
          "the third call starts 65 s after the second",
          stub.starts == [1000.0, 1065.0, 1130.0],
          f"starts={stub.starts}")


# ------------------------------ variable preparation time
def test_variable_preparation():
    clock = FakeClock()
    stub = StubModel(clock)
    pacer = pacer_for(clock, stub)
    pacer({}, budget=600.0, deadline=2000.0)
    clock.advance(200.0)
    pacer({}, budget=400.0, deadline=2000.0)
    check("variable preparation: a 200 s gap between "
          "calls needs no additional wait at all",
          stub.starts == [1000.0, 1200.0]
          and clock.sleeps == [],
          f"starts={stub.starts} sleeps={clock.sleeps}")
    clock2 = FakeClock()
    stub2 = StubModel(clock2)
    pacer2 = pacer_for(clock2, stub2)
    pacer2({}, budget=600.0, deadline=2000.0)
    clock2.advance(20.0)
    pacer2({}, budget=580.0, deadline=2000.0)
    check("variable preparation: a 20 s gap waits only "
          "the 45 s remainder",
          stub2.starts == [1000.0, 1065.0]
          and clock2.sleeps == [45.0],
          f"starts={stub2.starts} sleeps={clock2.sleeps}")


# ------------------------------ expiry during the wait
def test_expiry_during_wait():
    clock = FakeClock()
    stub = StubModel(clock)
    pacer = pacer_for(clock, stub)
    pacer({}, budget=30.0, deadline=1030.0)
    failure = None
    try:
        pacer({}, budget=0.0, deadline=1030.0)
    except AdapterFailure as f:
        failure = f
    check("expiry during a pacing wait: the wait runs "
          "to the 65 s boundary (1065), past the 1030 "
          "deadline, and the wrapped model is NEVER "
          "invoked for the second call",
          stub.starts == [1000.0]
          and clock.now == 1065.0,
          f"starts={stub.starts} now={clock.now}")
    check("the refusal is an AdapterFailure carrying "
          "no response — the loop answers a failure "
          "after expiry with its standing deadline "
          "path, and no provider request was made",
          failure is not None
          and failure.kind == "no_response"
          and "no provider request" in failure.detail,
          f"failure={failure!r}")


def test_wait_ending_before_deadline_proceeds():
    clock = FakeClock()
    stub = StubModel(clock)
    pacer = pacer_for(clock, stub)
    pacer({}, budget=600.0, deadline=1600.0)
    result = pacer({}, budget=535.0, deadline=1600.0)
    check("a pacing wait that ends before the deadline "
          "proceeds: the second call is made at the "
          "boundary and its outcome returned untouched",
          stub.starts == [1000.0, 1065.0]
          and result == {"outcome": "yield"},
          f"starts={stub.starts} result={result}")


# ---------------------------------------- transparency
def test_transparency():
    clock = FakeClock()
    stub = StubModel(clock)
    pacer = pacer_for(clock, stub)
    pacer({}, budget=600.0, deadline=1600.0, mode="native")
    check("the call's arguments are forwarded "
          "untouched: the mode the loop handed the "
          "model is the mode the wrapped model received",
          stub.modes == ["native"],
          f"modes={stub.modes}")
    pacer.last_response_evidence = None
    check("attribute writes through the pacer land on "
          "the wrapped model (the loop's evidence seam "
          "reset), and reads come from it",
          stub.last_response_evidence is None
          and pacer.model == "stub/model",
          f"evidence={stub.last_response_evidence!r} "
          f"model={pacer.model!r}")
    pacer.stage_disable_tool_validation(True)
    check("the BD-1 flag staging seam is reachable "
          "through the pacer and lands on the wrapped "
          "model",
          stub.staged_flag is True,
          f"staged={stub.staged_flag!r}")


def test_failure_propagates_unretried():
    clock = FakeClock()
    stub = StubModel(clock, fail=True)
    pacer = pacer_for(clock, stub)
    raised = []
    for _ in range(2):
        try:
            pacer({}, budget=600.0, deadline=2000.0)
        except AdapterFailure as f:
            raised.append(f.kind)
    check("a failure from the wrapped model propagates "
          "unretried — one invocation per loop call, no "
          "second attempt — and the failed call's start "
          "still paces the next call",
          raised == ["provider_error", "provider_error"]
          and stub.starts == [1000.0, 1065.0],
          f"raised={raised} starts={stub.starts}")


def main():
    test_first_call_not_delayed()
    test_ordinary_spacing()
    test_variable_preparation()
    test_expiry_during_wait()
    test_wait_ending_before_deadline_proceeds()
    test_transparency()
    test_failure_propagates_unretried()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
