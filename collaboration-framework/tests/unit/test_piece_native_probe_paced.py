"""Shared-core tests for the P1/P2 probes' machinery
— framework.native_probe_paced: the paced trial
runner and the two delivery-classification policies
the probes hold separately. Built against stub raw
calls only: no live provider request is made
anywhere in this suite.

Why this suite exists (the P1/P2 build examination's
correction): the pacing witnesses of the settled
38-check native-offer suite exercise the earlier
runner in framework.native_probe, not this new
shared implementation. The critical boundary
witnesses are therefore carried here, against
run_paced_trials itself, ported from that suite's
settled forms (INDEX 342/347/349):

- baseline spacing: starts exactly at the
  65-second monotonic floor, the first trial
  immediate, each wait the shortfall from the
  previous request's start;
- a non-empty precondition problem list refuses
  before any provider request and before any
  pacing wait;
- variable preparation cost: the runner's
  preparation step is wrapped so each call costs a
  deliberately variable amount of fake time — the
  recorded monotonic offsets must still EQUAL the
  raw-call seam's actual entry instants, and the
  recorded waits are the shortfalls measured after
  preparation (preparation inside the interval
  budget, outside the wait phase);
- wall-clock-read latency: a chronology read that
  itself costs monotonic time cannot enter the
  recorded offsets — the monotonic stamp is the
  final operation before invocation, so the offsets
  still equal the entry instants exactly;
- a sleeper that returns early: the runner
  re-measures after every sleep and waits again
  until the interval has actually elapsed;
- the two delivery policies are separate named
  policies, not one classifier: on the same
  invisible-refusal capture they classify
  differently (P1's refusal predicate says refused;
  P2's attribution rule says failed), and they
  agree where their contracts agree (an accepted
  body accepted; a visible refusal refused; a 429
  failed).

Run: PYTHONPATH=src python3 \
    tests/unit/test_piece_native_probe_paced.py
Exits 0 when every check passes.
"""

import copy
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import native_probe as np  # noqa: E402
from framework import native_probe_paced as paced  # noqa: E402

PIN = "openai/gpt-oss-120b"
FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail else ""))
    if not cond:
        FAILURES.append(name)


class FakeClock:
    """Injectable dual clocks: wall and monotonic
    advancing together under sleep, instantly — the
    pacing path exercised in full, no real waiting."""

    def __init__(self, start=1_700_000_000.0):
        self.wall_now = start
        self.mono_now = 0.0
        self.sleeps = []

    def wall(self):
        return self.wall_now

    def monotonic(self):
        return self.mono_now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.advance(seconds)

    def advance(self, seconds):
        self.wall_now += seconds
        self.mono_now += seconds


class EarlySleeper:
    """A sleeper that returns early: each call advances
    the clocks by at most max_advance seconds, however
    long a sleep was requested. The runner must not
    proceed on such a wait — it must measure the
    monotonic elapsed again and wait further."""

    def __init__(self, clock, max_advance=10.0):
        self.clock = clock
        self.max_advance = max_advance
        self.calls = []

    def __call__(self, seconds):
        self.calls.append(seconds)
        self.clock.advance(min(seconds, self.max_advance))


class BoundaryStubRaw:
    """A raw-call stub that records the monotonic
    instant each invocation actually enters the
    raw-call seam, so the witnesses can compare the
    runner's recorded starts against the invocation
    starts themselves."""

    def __init__(self, clock):
        self.clock = clock
        self.requests = []
        self.entry_starts = []

    def __call__(self, request):
        self.entry_starts.append(self.clock.monotonic())
        self.requests.append(copy.deepcopy(request))
        return {"body": None, "error_body": None,
                "http_status": None,
                "diagnostics": "stub capture",
                "metadata": {}}


def record_evidence(index, capture,
                    request_started_wall_at=None,
                    request_start_monotonic_offset_seconds=None,
                    pacing_wait_phase_seconds=0.0):
    """The minimal evidence builder the runner's
    contract requires: the pacing fields recorded
    verbatim, so the witnesses read exactly what the
    runner measured."""
    return {
        "trial": index,
        "request_started_wall_at": request_started_wall_at,
        "request_start_monotonic_offset_seconds":
            request_start_monotonic_offset_seconds,
        "pacing_wait_phase_seconds":
            pacing_wait_phase_seconds,
        "capture": capture,
    }


def request_plan(count=5):
    return [{"model": PIN,
             "messages": [{"role": "user",
                           "content": "stub trial"}]}
            for _ in range(count)]


def offsets(trials):
    return [t["request_start_monotonic_offset_seconds"]
            for t in trials]


def run_shared(clock, stub, sleeper=None):
    return paced.run_paced_trials(
        stub, request_plan(), [], record_evidence,
        monotonic_clock=clock.monotonic,
        wall_clock=clock.wall,
        sleeper=sleeper if sleeper is not None
        else clock.sleep)


# ---------------------------------------------------------------
# Baseline pacing, against this shared implementation.
# ---------------------------------------------------------------
clock = FakeClock()
stub = BoundaryStubRaw(clock)
trials = run_shared(clock, stub)
check("paced trials on the shared runner start "
      "exactly at the 65-second monotonic floor, the "
      "first trial immediate, each wait the full "
      "shortfall from the previous start",
      offsets(trials) == [0.0, 65.0, 130.0, 195.0, 260.0]
      and [t["pacing_wait_phase_seconds"] for t in trials]
      == [0.0, 65.0, 65.0, 65.0, 65.0]
      and len(stub.requests) == 5,
      f"offsets={offsets(trials)}")

# ---------------------------------------------------------------
# The precondition refuses before any request, and
# before any pacing wait.
# ---------------------------------------------------------------
clock = FakeClock()
stub = BoundaryStubRaw(clock)
refused = False
try:
    paced.run_paced_trials(
        stub, request_plan(), ["a tampered comparison"],
        record_evidence, monotonic_clock=clock.monotonic,
        wall_clock=clock.wall, sleeper=clock.sleep)
except np.NativeProbeRefusal:
    refused = True
check("a non-empty precondition problem list refuses "
      "before any provider request — and before any "
      "pacing wait is taken",
      refused and stub.requests == []
      and stub.entry_starts == [] and clock.sleeps == [])

# ---------------------------------------------------------------
# Measurement boundary: variable preparation cost
# (INDEX 347/348). The real preparation step is
# wrapped so each call advances the fake clock by a
# deliberately VARIABLE amount before delegating to
# it; the runner's sequencing, waiting, stamping and
# invoking are the production code throughout.
# ---------------------------------------------------------------
PREP_SCHEDULE = [0.0, 40.0, 5.0, 50.0, 10.0]
prep_clock = FakeClock()
prep_stub = BoundaryStubRaw(prep_clock)
real_prepare = paced._prepare_request
prep_costs = []


def costly_prepare(request):
    cost = PREP_SCHEDULE[len(prep_costs)]
    prep_costs.append(cost)
    prep_clock.advance(cost)
    return real_prepare(request)


paced._prepare_request = costly_prepare
try:
    prep_trials = run_shared(prep_clock, prep_stub)
finally:
    paced._prepare_request = real_prepare

entry_gaps = [b - a for a, b in zip(
    prep_stub.entry_starts, prep_stub.entry_starts[1:])]
check("deliberately variable pre-call preparation "
      "overhead (0/40/5/50/10 fake seconds across "
      "consecutive trials) cannot compress the spacing "
      "at the call boundary — every consecutive pair "
      "of ACTUAL invocation starts, recorded by the "
      "stub as it is entered, is at least the "
      "65-second floor apart, the recorded offsets "
      "ARE the invocation starts, and the recorded "
      "waits are the shortfalls measured AFTER "
      "preparation (25/60/15/55 against preparation "
      "costs 40/5/50/10, instant generation)",
      prep_costs == PREP_SCHEDULE
      and len(prep_stub.entry_starts) == 5
      and all(gap >= np.MIN_TRIAL_START_INTERVAL_SECONDS
              for gap in entry_gaps)
      and offsets(prep_trials)
      == [e - prep_stub.entry_starts[0]
          for e in prep_stub.entry_starts]
      and [t["pacing_wait_phase_seconds"]
           for t in prep_trials]
      == [0.0, 25.0, 60.0, 15.0, 55.0],
      f"entries={prep_stub.entry_starts} "
      f"offsets={offsets(prep_trials)}")

# ---------------------------------------------------------------
# INDEX 349: the monotonic stamp is the FINAL
# operation before invocation — the chronology
# (wall) read happens before it, never between the
# stamp and the call. Witnessed with a wall read
# that itself COSTS monotonic time (a slow
# chronology read, 7 fake seconds): if anything sat
# between the stamp and the invocation, the stub's
# recorded entry instants would fall after the
# recorded offsets by that cost; with the stamp
# last, they are exactly equal.
# ---------------------------------------------------------------
slow_clock = FakeClock()
slow_stub = BoundaryStubRaw(slow_clock)
WALL_READ_COST = 7.0


def costly_wall():
    slow_clock.advance(WALL_READ_COST)
    return slow_clock.wall()


slow_trials = paced.run_paced_trials(
    slow_stub, request_plan(), [], record_evidence,
    monotonic_clock=slow_clock.monotonic,
    wall_clock=costly_wall, sleeper=slow_clock.sleep)
slow_gaps = [b - a for a, b in zip(
    slow_stub.entry_starts, slow_stub.entry_starts[1:])]
check("the monotonic stamp is the final operation "
      "before invocation: with a wall read that itself "
      "costs 7 fake seconds, the recorded offsets "
      "still EQUAL the stub's recorded entry instants "
      "exactly — nothing, not even the chronology "
      "read, sits between the stamp and the call — "
      "and every entry gap holds the 65-second floor",
      offsets(slow_trials)
      == [e - slow_stub.entry_starts[0]
          for e in slow_stub.entry_starts]
      and all(gap >= np.MIN_TRIAL_START_INTERVAL_SECONDS
              for gap in slow_gaps),
      f"offsets={offsets(slow_trials)} "
      f"entries={slow_stub.entry_starts}")

# ---------------------------------------------------------------
# A sleeper that returns early must be re-measured
# (INDEX 342): the runner waits again until the
# monotonic interval has actually elapsed.
# ---------------------------------------------------------------
clock = FakeClock()
early = EarlySleeper(clock, max_advance=10.0)
stub = BoundaryStubRaw(clock)
trials = run_shared(clock, stub, sleeper=early)
check("a sleeper that returns early — advancing time "
      "by at most 10 seconds per call — does not let "
      "the shared runner proceed: it waits again until "
      "the monotonic interval has actually elapsed "
      "(many sleep calls, every start offset at least "
      "65 from the previous, the recorded wait the "
      "actual monotonic wait)",
      len(early.calls) > 5
      and all(b - a >=
              np.MIN_TRIAL_START_INTERVAL_SECONDS
              for a, b in zip(offsets(trials),
                              offsets(trials)[1:]))
      and trials[1]["pacing_wait_phase_seconds"] >= 65.0,
      f"calls={early.calls} offsets={offsets(trials)}")

# ---------------------------------------------------------------
# The two delivery policies are separate: no single
# classifier serves both probes.
# ---------------------------------------------------------------
INVISIBLE_REFUSAL = {
    "body": None,
    "error_body": json.dumps({"error": {
        "message": "the request was refused",
        "code": "tool_use_failed"}}),
    "http_status": 400, "diagnostics": None,
    "metadata": {}}
VISIBLE_REFUSAL = {
    "body": None,
    "error_body": json.dumps({"error": {
        "message": "Tool choice is none, but model "
                   "called a tool",
        "code": "tool_use_failed",
        "failed_generation": json.dumps({
            "name": "sandbox.read_range",
            "arguments": {"path": "sources/stock-take.md"}})}}),
    "http_status": 400, "diagnostics": None,
    "metadata": {}}
FAILED_429 = {
    "body": None,
    "error_body": "Rate limit reached for model",
    "http_status": 429, "diagnostics": None,
    "metadata": {}}
ACCEPTED = {"body": "{}", "error_body": None,
            "http_status": 200, "diagnostics": None,
            "metadata": {}}

check("the same invisible-refusal capture classifies "
      "DIFFERENTLY under the two policies — P1's "
      "refusal predicate reads the tool_use_failed "
      "shape and says provider_refused, while P2's "
      "attribution rule finds no attributable attempt "
      "and says provider_failed: no single classifier "
      "silently serves both probes",
      paced.delivery_of_refusal_predicate(
          INVISIBLE_REFUSAL) == "provider_refused"
      and paced.delivery_of_attribution(
          INVISIBLE_REFUSAL) == "provider_failed")
check("the two policies agree where their contracts "
      "agree: a refusal with a visible attributable "
      "attempt is provider_refused under both, a 429 "
      "is provider_failed under both, an accepted "
      "body is provider_accepted under both",
      paced.delivery_of_refusal_predicate(
          VISIBLE_REFUSAL) == "provider_refused"
      and paced.delivery_of_attribution(
          VISIBLE_REFUSAL) == "provider_refused"
      and paced.delivery_of_refusal_predicate(
          FAILED_429) == "provider_failed"
      and paced.delivery_of_attribution(
          FAILED_429) == "provider_failed"
      and paced.delivery_of_refusal_predicate(
          ACCEPTED) == "provider_accepted"
      and paced.delivery_of_attribution(
          ACCEPTED) == "provider_accepted")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
