"""Native-offer probe tests — the machinery of
NATIVE-OFFER-PROBE-SCOPE Rev 2 (PASSED at INDEX 334),
built against stub raw calls only: no live provider
request is made anywhere in this suite.

- the baseline regenerates deterministically from the
  evidenced record by the real construction path, and
  reproduces the record's own LOOP_ITERATION
  commitments (its catalogue hash among them);
- the modified request differs from the baseline in
  exactly the tools field; the comparison artifact's
  hashes recompute and the precondition passes;
- a tampered baseline field fails the precondition,
  and the trial runner refuses before ANY provider
  request (the counting stub records zero requests);
- the comparison's own commitments are verified in
  full, not asserted: a recorded diff entry altered
  (differing_paths left correct), a tampered
  definitions_sha256, and a tampered recorded
  catalogue source hash each fail the precondition
  and refuse before any provider request;
- classification: an offered call with well-formed
  arguments is offered_tool_call; an offered call with
  malformed arguments is malformed, never a success;
  an unoffered call alone is unoffered_tool_attempt,
  including on the provider-refused error-body path;
  text beside a call is mixed; two calls of differing
  classes are mixed with the unoffered fact carried in
  the trial's flags and per-call records; a valid
  text-only answer is text_contract;
- exactly one request per trial across all five
  trials, tool-calling responses included — no
  follow-up generation ever;
- the paced repetition's pacing (INDEX 340), witnessed
  on an injected fake clock with no real waiting: the
  pacing path itself engaged, request starts recorded
  at least 65 seconds apart, the wait before each trial
  the shortfall from the previous start (a generation
  that takes fake time leaves a shorter wait; one
  longer than the floor leaves none), the starts and
  waits standing in the written evidence artifact, and
  a tampered comparison still refusing before any
  request — and before any pacing wait;
- the decision thresholds read as the scope states:
  offered majority locks the door hypothesis in as
  supported, unoffered carriers strengthen the deeper
  habit, a split is a split;
- the durable outputs carry the comparison artifact
  and the per-trial raw retention, and the evidence
  hash verifies over the written artifact.

Run: PYTHONPATH=src python3 \
    tests/unit/test_piece_native_offer_probe.py
Exits 0 when every check passes.
"""

import copy
import json
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from fabric.canonical import canonical, sha256_hex  # noqa: E402
from framework import native_probe as np  # noqa: E402

PIN = "openai/gpt-oss-120b"
EVIDENCED = os.path.join(
    ROOT, "live-demo", "first-worker-evidenced1")
FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name +
          (("  " + detail) if detail else ""))
    if not cond:
        FAILURES.append(name)


class StubRaw:
    """A raw-call stub in the probe's capture protocol:
    serves one capture (repeated) or a queue of captures,
    and records every request it receives."""

    def __init__(self, captures):
        self.captures = captures
        self.requests = []

    def __call__(self, request):
        self.requests.append(copy.deepcopy(request))
        if isinstance(self.captures, list):
            return self.captures[
                min(len(self.requests) - 1,
                    len(self.captures) - 1)]
        return self.captures


class FakeClock:
    """An injectable clock/sleeper pair for the pacing
    witnesses: sleeping advances the clock by the slept
    amount, instantly — the pacing path is exercised in
    full, with no real waiting."""

    def __init__(self, start=1_700_000_000.0):
        self.now = start
        self.sleeps = []

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

    def advance(self, seconds):
        self.now += seconds


class TimedStubRaw(StubRaw):
    """A StubRaw whose generation itself takes fake
    time: each call advances the fake clock by
    generation_seconds before returning its capture, so
    a pacing witness can show the wait is the shortfall
    from the previous request's start, not a flat delay
    after the generation completes."""

    def __init__(self, captures, clock, generation_seconds):
        super().__init__(captures)
        self.clock = clock
        self.generation_seconds = generation_seconds

    def __call__(self, request):
        capture = super().__call__(request)
        self.clock.advance(self.generation_seconds)
        return capture


def body_capture(message, status=200):
    body = json.dumps({
        "id": "chatcmpl-stub", "model": PIN,
        "choices": [{"index": 0, "message": message}]})
    return {"body": body, "error_body": None,
            "http_status": status, "diagnostics": None,
            "metadata": {"id": "chatcmpl-stub",
                         "model": PIN}}


def call_message(name, arguments, content=None):
    return {"role": "assistant", "content": content,
            "tool_calls": [{
                "id": "fc1", "type": "function",
                "function": {"name": name,
                             "arguments": arguments}}]}


OFFERED_CALL = body_capture(call_message(
    "sandbox.list", json.dumps({"path": "sources"})))
MALFORMED_ARGS_CALL = body_capture(call_message(
    "sandbox.search", "{not json"))
UNOFFERED_CALL = body_capture(call_message(
    "container.exec", json.dumps({"cmd": ["bash"]})))
TEXT_AND_CALL = body_capture(call_message(
    "sandbox.search", json.dumps({"query": "stock"}),
    content=json.dumps({"outcome": "decline",
                        "reason": "stub"})))
TWO_CALLS = body_capture({
    "role": "assistant", "content": None,
    "tool_calls": [
        {"id": "fc1", "type": "function", "function": {
            "name": "sandbox.list",
            "arguments": json.dumps({"path": "sources"})}},
        {"id": "fc2", "type": "function", "function": {
            "name": "container.exec",
            "arguments": json.dumps({"cmd": ["bash"]})}}]})
TEXT_ONLY = body_capture({
    "role": "assistant",
    "content": json.dumps({"outcome": "yield",
                            "summary": "stub brief"})})
ERROR_UNOFFERED = {
    "body": None,
    "error_body": json.dumps({"error": {
        "message": "Tool choice is none, but model "
                   "called a tool",
        "code": "tool_use_failed",
        "failed_generation": json.dumps({
            "name": "container.exec",
            "arguments": {"cmd": ["bash", "-lc", "true"]}})}}),
    "http_status": 400, "diagnostics": None,
    "metadata": {}}

# ---------------------------------------------------------------
# The baseline, from the real evidenced record.
# ---------------------------------------------------------------
TMP = tempfile.mkdtemp(prefix="native-offer-witness-")
baseline, package, info = np.build_baseline(
    EVIDENCED, os.path.join(TMP, "w1"), PIN)
baseline2, _, _ = np.build_baseline(
    EVIDENCED, os.path.join(TMP, "w2"), PIN)
check("baseline regeneration is deterministic — the "
      "same canonical hash across two constructions",
      sha256_hex(canonical(baseline)) ==
      sha256_hex(canonical(baseline2)),
      sha256_hex(canonical(baseline))[:16])
events = np._read_source_record(EVIDENCED)
recorded = next(
    e["payload"] for e in events
    if e["type"] == "LOOP_ITERATION"
    and e["payload"].get("iteration") == 1)
check("the regeneration reproduces the record's own "
      "catalogue hash commitment",
      info["catalogue_hash"] == recorded["catalogue_hash"]
      and info["catalogue_hash_matches_record"],
      info["catalogue_hash"][:16])
check("the baseline request is the transport's "
      "construction — model, messages, temperature, and "
      "no tools or tool_choice field",
      set(baseline) == {"model", "messages", "temperature"}
      and baseline["model"] == PIN
      and baseline["temperature"] == 0.2)
check("the represented countdown stands as the full "
      "pinned deadline (the activation instant's value)",
      info["seconds_remaining_in_package"] == 600.0)

definitions, catalogue_source = \
    np.derive_offered_definitions(
        package, info["catalogue_hash"])
check("the offered definitions are exactly the three "
      "granted retrieval actions, in catalogue order",
      [d["function"]["name"] for d in definitions] ==
      ["sandbox.list", "sandbox.read_range",
       "sandbox.search"])
modified = np.build_modified_request(baseline, definitions)
comparison = np.build_comparison(
    baseline, modified, definitions, catalogue_source,
    info)
check("the modified request differs from the baseline "
      "in exactly the tools field, tool choice omitted "
      "on both sides",
      comparison["differing_paths"] == ["tools"]
      and "tool_choice" not in modified
      and "tool_choice" not in baseline)
check("the comparison's hashes recompute and the "
      "precondition passes on the genuine triple",
      np.check_precondition(baseline, modified,
                            comparison) == [])

# ---------------------------------------------------------------
# Tampering fails the precondition, before any request.
# ---------------------------------------------------------------
tampered = copy.deepcopy(baseline)
tampered["messages"][1]["content"] += " tampered"
tampered_comparison = np.build_comparison(
    tampered, modified, definitions, catalogue_source,
    info)
problems = np.check_precondition(
    tampered, modified, tampered_comparison)
check("a tampered baseline field (an altered message) "
      "fails the precondition, naming the messages path",
      any("messages" in p for p in problems),
      "; ".join(problems)[:120])
stub = StubRaw(OFFERED_CALL)
refused = False
try:
    np.run_native_trials(stub, tampered, modified,
                         tampered_comparison)
except np.NativeProbeRefusal:
    refused = True
check("the runner refuses on the failed precondition "
      "before ANY provider request",
      refused and stub.requests == [])


def expect_refusal(name, tampered_comparison, marker):
    """A comparison artifact with one commitment
    tampered must fail the strengthened precondition —
    the problem naming the commitment — and the runner
    must refuse before ANY provider request (the
    counting stub records zero requests)."""
    problems = np.check_precondition(
        baseline, modified, tampered_comparison)
    stub = StubRaw(OFFERED_CALL)
    refused = False
    try:
        np.run_native_trials(stub, baseline, modified,
                             tampered_comparison)
    except np.NativeProbeRefusal:
        refused = True
    check(name,
          any(marker in p for p in problems)
          and refused and stub.requests == [],
          "; ".join(problems)[:120])


diff_tampered = copy.deepcopy(comparison)
diff_tampered["diff"][0]["modified"]["sha256"] = "f" * 64
expect_refusal(
    "a recorded diff entry altered (a side's hash "
    "flipped) while differing_paths stays correct fails "
    "the precondition and refuses before any request",
    diff_tampered, "diff entries")

defs_tampered = copy.deepcopy(comparison)
defs_tampered["definitions_sha256"] = "f" * 64
expect_refusal(
    "a tampered definitions_sha256 — no longer the "
    "canonical hash of the modified request's tools "
    "field — fails the precondition and refuses before "
    "any request",
    defs_tampered, "definitions hash")

catalogue_tampered = copy.deepcopy(comparison)
catalogue_tampered["catalogue_source"][
    "catalogue_hash"] = "f" * 64
expect_refusal(
    "a tampered recorded catalogue source hash — no "
    "longer agreeing with the baseline construction's "
    "catalogue commitment — fails the precondition and "
    "refuses before any request",
    catalogue_tampered, "catalogue source hash")

# ---------------------------------------------------------------
# Classification, on stub captures.
# ---------------------------------------------------------------
def run(captures):
    clock = FakeClock()
    stub = StubRaw(captures)
    trials = np.run_native_trials(
        stub, baseline, modified, comparison,
        clock=clock.time, sleeper=clock.sleep)
    return stub, trials


stub, trials = run(OFFERED_CALL)
check("an offered call with well-formed arguments is "
      "offered_tool_call × provider_accepted, per-call "
      "and aggregate",
      all(t["behaviour"] == "offered_tool_call"
          and t["delivery"] == "provider_accepted"
          and t["calls"][0]["classification"] ==
          "offered_tool_call" for t in trials))
counts, settled, reading = np.summarise_native(trials)
check("five offered calls settle and read as the "
      "locked-door hypothesis supported",
      settled == 5 and reading == "locked_door_supported")
check("exactly one request per trial — five requests "
      "for five trials, each the modified request, tool "
      "calls triggering no follow-up",
      len(stub.requests) == 5 and all(
          canonical(r) == canonical(modified)
          for r in stub.requests))

_, trials = run(MALFORMED_ARGS_CALL)
check("an offered call with malformed arguments is "
      "malformed — per call and aggregate — and never "
      "counts as a successful offered call",
      all(t["behaviour"] == "malformed"
          and t["calls"][0]["classification"] ==
          "malformed" for t in trials)
      and np.summarise_native(trials)[0]["behaviour"]
      ["offered_tool_call"] == 0)

_, trials = run(UNOFFERED_CALL)
check("an unoffered call alone is "
      "unoffered_tool_attempt, its fact in the flags",
      all(t["behaviour"] == "unoffered_tool_attempt"
          and t["has_unoffered_call"] for t in trials))

_, trials = run(TEXT_AND_CALL)
check("text-contract content beside a native call is "
      "mixed, the call's own classification preserved",
      all(t["behaviour"] == "mixed"
          and t["text_form"] == "text_contract"
          and t["calls"][0]["classification"] ==
          "offered_tool_call" for t in trials))

_, trials = run(TWO_CALLS)
check("two calls of differing classes are mixed, with "
      "both per-call records standing and the unoffered "
      "fact carried, not concealed",
      all(t["behaviour"] == "mixed"
          and [c["classification"] for c in t["calls"]]
          == ["offered_tool_call",
              "unoffered_tool_attempt"]
          and t["has_unoffered_call"]
          and t["has_offered_call"] for t in trials))

_, trials = run(TEXT_ONLY)
check("a valid text-only answer is text_contract",
      all(t["behaviour"] == "text_contract"
          and t["calls"] == [] for t in trials))

_, trials = run(ERROR_UNOFFERED)
counts, settled, reading = np.summarise_native(trials)
check("the provider-refused error body attributes the "
      "unoffered attempt — unoffered_tool_attempt × "
      "provider_refused — and five carriers strengthen "
      "the deeper-habit reading",
      all(t["behaviour"] == "unoffered_tool_attempt"
          and t["delivery"] == "provider_refused"
          for t in trials)
      and reading == "deeper_habit_strengthened")

_, trials = run([OFFERED_CALL, UNOFFERED_CALL, TEXT_ONLY,
                 OFFERED_CALL, MALFORMED_ARGS_CALL])
counts, settled, reading = np.summarise_native(trials)
check("a split result is reported as a split — no "
      "reading forced",
      reading == "split_inconclusive"
      and counts["behaviour"]["offered_tool_call"] == 2
      and counts["behaviour"]["unoffered_tool_attempt"]
      == 1 and counts["behaviour"]["text_contract"] == 1
      and counts["behaviour"]["malformed"] == 1)

# ---------------------------------------------------------------
# Pacing: the paced repetition (INDEX 340), on a fake
# clock — the pacing path itself, no real waiting.
# ---------------------------------------------------------------
def paced_run(captures, generation_seconds=0.0):
    clock = FakeClock()
    stub = TimedStubRaw(captures, clock, generation_seconds)
    trials = np.run_native_trials(
        stub, baseline, modified, comparison,
        clock=clock.time, sleeper=clock.sleep)
    return clock, stub, trials


_, _, trials = paced_run(OFFERED_CALL)
starts = [t["request_started_at"] for t in trials]
waits = [t["pacing_wait_seconds"] for t in trials]
check("paced trials record request starts at least the "
      "65-second floor apart, strictly sequential, the "
      "first trial starting immediately",
      waits[0] == 0.0 and all(
          b - a >= np.MIN_TRIAL_START_INTERVAL_SECONDS
          for a, b in zip(starts, starts[1:])),
      f"starts={starts}")
check("with an instant generation, the wait before each "
      "later trial is the full interval — the shortfall "
      "from the previous request's start",
      waits == [0.0, 65.0, 65.0, 65.0, 65.0],
      f"waits={waits}")

_, _, trials = paced_run(OFFERED_CALL, generation_seconds=20.0)
starts = [t["request_started_at"] for t in trials]
waits = [t["pacing_wait_seconds"] for t in trials]
check("a generation that itself takes 20 seconds leaves "
      "a 45-second wait — the shortfall, not a flat 65 "
      "after completion — and starts stay 65 apart",
      waits == [0.0, 45.0, 45.0, 45.0, 45.0] and all(
          b - a == 65.0
          for a, b in zip(starts, starts[1:])),
      f"waits={waits} starts={starts}")

_, _, trials = paced_run(OFFERED_CALL, generation_seconds=90.0)
starts = [t["request_started_at"] for t in trials]
waits = [t["pacing_wait_seconds"] for t in trials]
check("a generation longer than the floor leaves no "
      "wait at all — the next start is already past it",
      waits == [0.0] * 5 and all(
          b - a == 90.0
          for a, b in zip(starts, starts[1:])),
      f"waits={waits} starts={starts}")

_, _, trials = paced_run(OFFERED_CALL, generation_seconds=20.0)
paced_evidence = np.probe_evidence_object(comparison,
                                          trials)
paced_dir = os.path.join(TMP, "out-paced")
np.write_outputs(paced_dir, comparison, paced_evidence)
with open(os.path.join(paced_dir, "probe-evidence.json"),
          encoding="utf-8") as fh:
    written_trials = json.load(fh)["trials"]
written_starts = [t["request_started_at"]
                  for t in written_trials]
check("the written evidence artifact carries each "
      "trial's request start and applied wait — the "
      "spacing verifiable from the artifact alone",
      all(t["pacing_wait_seconds"] == 45.0
          for t in written_trials[1:])
      and written_trials[0]["pacing_wait_seconds"] == 0.0
      and all(b - a >=
              np.MIN_TRIAL_START_INTERVAL_SECONDS
              for a, b in zip(written_starts,
                              written_starts[1:])),
      f"starts={written_starts}")

clock = FakeClock()
stub = StubRaw(OFFERED_CALL)
refused = False
try:
    np.run_native_trials(stub, baseline, modified,
                         diff_tampered,
                         clock=clock.time,
                         sleeper=clock.sleep)
except np.NativeProbeRefusal:
    refused = True
check("the paced runner still refuses on a tampered "
      "comparison before any provider request — and "
      "before any pacing wait is taken",
      refused and stub.requests == []
      and clock.sleeps == [])

# ---------------------------------------------------------------
# The durable outputs.
# ---------------------------------------------------------------
_, trials = run(TWO_CALLS)
evidence = np.probe_evidence_object(comparison, trials)
out_dir = os.path.join(TMP, "out")
written = np.write_outputs(out_dir, comparison, evidence)
loaded = {}
for path in written:
    with open(path, encoding="utf-8") as fh:
        loaded[os.path.basename(path)] = json.load(fh)
check("the outputs write and read back — comparison "
      "and probe evidence, hashes standing",
      set(loaded) == {"comparison.json",
                      "probe-evidence.json"}
      and loaded["comparison.json"]["baseline_sha256"]
      == comparison["baseline_sha256"]
      and loaded["probe-evidence.json"]["evidence_hash"]
      == np.native_evidence_hash(evidence))
check("the written evidence retains the raw provider "
      "body whole, per trial",
      all(t["provider_body"] == TWO_CALLS["body"]
          and t["provider_body_complete"]
          for t in
          loaded["probe-evidence.json"]["trials"]))
check("per-call classifications stand in the written "
      "evidence — the thresholds reconstruct from the "
      "artifact alone",
      all([c["classification"] for c in t["calls"]] ==
          ["offered_tool_call", "unoffered_tool_attempt"]
          for t in
          loaded["probe-evidence.json"]["trials"]))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
