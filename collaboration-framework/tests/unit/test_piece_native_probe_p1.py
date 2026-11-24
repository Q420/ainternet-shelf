"""Native adapter probe P1 tests — the machinery of
NATIVE-ADAPTER-P1-PROBE-PROPOSAL Rev 1 (PASSED at
INDEX 358), built against stub raw calls only: no live
provider request is made anywhere in this suite.

- the construction reproduces from the evidenced
  record by the real construction path: the listing's
  sizes are the evidenced sandbox files' own sizes,
  the variant request differs from the baseline at
  exactly the task-context path, the narrowed
  definitions are exactly sandbox.list and
  sandbox.search with sandbox.read_range withheld;
- the two conditions differ at exactly the
  disable_tool_validation path — present and true on
  ON, absent on OFF, the tools fields identical — and
  each condition differs from the admitted native-
  offer request at exactly its admitted paths; the
  comparison's hashes recompute and the precondition
  passes on the genuine artifacts;
- tamper witnesses: a condition pair differing by
  anything beyond the flag (a changed temperature on
  ON) fails the precondition and the runner refuses
  before ANY provider request and before any pacing
  wait; a tampered narrowed-definitions hash refuses;
  a tampered recorded variant assignment refuses —
  the request's prompt is bound to the recorded text;
- classification: an accepted unoffered call (the
  withheld read_range; the shell) is
  unoffered_call_returned with the per-call record
  carrying its provider call ID; a refused response
  whose failed_generation carries the withheld name
  is provider_refused with attempt_visible yes and
  the attempt preserved as provider evidence; a
  refusal without it is provider_refused with
  attempt_visible no — a distinct observation; a 429
  is provider_failed, outside every denominator;
- the predeclared readings compute as stated: five
  returned unoffered calls establish behaviour (a)
  for their condition, five refusals with the attempt
  visible establish (b) for theirs, different
  established behaviours measure the flag's effect,
  and no attempt in either condition leaves the flag
  comparison inconclusive for the flag's effect;
- exactly one request per trial across all ten
  trials — five OFF requests then five ON requests,
  each the admitted condition request — and the
  pacing holds the 65-second monotonic floor across
  the condition boundary;
- the durable outputs carry the comparison and the
  per-trial evidence, and the evidence hash verifies
  over the written artifact.

Run: PYTHONPATH=src python3 \
    tests/unit/test_piece_native_probe_p1.py
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
from framework import native_probe_p1 as p1  # noqa: E402

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
    serves one capture (repeated) or a queue of
    captures, and records every request it receives."""

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
        self.wall_now += seconds
        self.mono_now += seconds


def body_capture(message, status=200):
    body = json.dumps({
        "id": "chatcmpl-stub", "model": PIN,
        "choices": [{"index": 0, "message": message}]})
    return {"body": body, "error_body": None,
            "http_status": status, "diagnostics": None,
            "metadata": {"id": "chatcmpl-stub",
                         "model": PIN}}


def call_message(name, arguments, call_id="fc1",
                 content=None):
    return {"role": "assistant", "content": content,
            "tool_calls": [{
                "id": call_id, "type": "function",
                "function": {"name": name,
                             "arguments": arguments}}]}


RETURNED_READ = body_capture(call_message(
    "sandbox.read_range",
    json.dumps({"path": "sources/stock-take.md",
                "start_line": 1, "end_line": 50}),
    call_id="fc-p1-read"))
RETURNED_SHELL = body_capture(call_message(
    "container.exec", json.dumps({"cmd": ["bash"]})))
OFFERED_CALL = body_capture(call_message(
    "sandbox.list",
    json.dumps({"path": "sources/stock-take.md"})))
REFUSED_VISIBLE = {
    "body": None,
    "error_body": json.dumps({"error": {
        "message": "Tool choice is none, but model "
                   "called a tool",
        "code": "tool_use_failed",
        "failed_generation": json.dumps({
            "name": "sandbox.read_range",
            "arguments": {
                "path": "sources/stock-take.md",
                "start_line": 1, "end_line": 50}})}}),
    "http_status": 400, "diagnostics": None,
    "metadata": {}}
REFUSED_INVISIBLE = {
    "body": None,
    "error_body": json.dumps({"error": {
        "message": "the request was refused",
        "code": "tool_use_failed"}}),
    "http_status": 400, "diagnostics": None,
    "metadata": {}}
FAILED_429 = {
    "body": None,
    "error_body": "Rate limit reached for model",
    "http_status": 429, "diagnostics": None,
    "metadata": {}}

# ---------------------------------------------------------------
# The construction, from the real evidenced record.
# ---------------------------------------------------------------
TMP = tempfile.mkdtemp(prefix="native-probe-p1-witness-")
prepared = p1.prepare(
    EVIDENCED, os.path.join(TMP, "w1"), PIN)
prepared2 = p1.prepare(
    EVIDENCED, os.path.join(TMP, "w2"), PIN)
comparison = prepared["comparison"]
check("the construction is deterministic — the same "
      "condition request hashes across two preparations",
      comparison["conditions"] ==
      prepared2["comparison"]["conditions"]
      and comparison["baseline_sha256"] ==
      prepared2["comparison"]["baseline_sha256"],
      comparison["conditions"]["off"]["request_sha256"][:16])
check("the pre-presented listing's sizes are the "
      "evidenced sandbox files' own sizes",
      all(entry["size_bytes"] == os.path.getsize(
          os.path.join(EVIDENCED, "sandbox",
                       entry["path"]))
          for entry in prepared["listing"])
      and [e["path"] for e in prepared["listing"]] ==
      list(p1.SOURCE_PATHS))
check("the variant assignment pre-presents the listing "
      "and requires the brief to rest on the full "
      "contents of the named source",
      "full contents of sources/stock-take.md"
      in prepared["assignment"]
      and all(entry["path"] in prepared["assignment"]
              for entry in prepared["listing"]))
check("the variant request differs from the baseline "
      "at exactly the task-context path",
      [e["path"] for e in np.diff_requests(
          prepared["baseline"],
          prepared["variant_request"])] ==
      ["messages[1].content"])
check("the narrowed definitions are exactly "
      "sandbox.list and sandbox.search, the withheld "
      "tool named in the narrowing record",
      [d["function"]["name"]
       for d in prepared["narrowed_definitions"]] ==
      ["sandbox.list", "sandbox.search"]
      and comparison["narrowing"]["withheld_tools"] ==
      ["sandbox.read_range"]
      and [d["function"]["name"]
           for d in prepared["full_definitions"]] ==
      ["sandbox.list", "sandbox.read_range",
       "sandbox.search"])
off, on = prepared["off_request"], prepared["on_request"]
check("the condition pair differs at exactly the "
      "validation-flag path — present and true on ON, "
      "absent on OFF, tools fields identical",
      [e["path"] for e in np.diff_requests(off, on)] ==
      ["disable_tool_validation"]
      and on["disable_tool_validation"] is True
      and "disable_tool_validation" not in off
      and canonical(on["tools"]) == canonical(off["tools"]))
check("each condition differs from the admitted "
      "native-offer request at exactly its admitted "
      "paths",
      comparison["vs_native_offer"]["off"]
      ["differing_paths"] ==
      ["messages[1].content", "tools"]
      and comparison["vs_native_offer"]["on"]
      ["differing_paths"] ==
      ["disable_tool_validation", "messages[1].content",
       "tools"])
check("the comparison's hashes recompute and the "
      "precondition passes on the genuine artifacts",
      p1.check_precondition(
          prepared["baseline"],
          prepared["native_modified"], off, on,
          comparison, prepared["package"],
          prepared["info"]["catalogue_hash"]) == [])

# ---------------------------------------------------------------
# Tampering fails the precondition, before any request.
# ---------------------------------------------------------------
def expect_refusal(name, tampered_prepared, marker):
    problems = p1.check_precondition(
        tampered_prepared["baseline"],
        tampered_prepared["native_modified"],
        tampered_prepared["off_request"],
        tampered_prepared["on_request"],
        tampered_prepared["comparison"],
        tampered_prepared["package"],
        tampered_prepared["info"]["catalogue_hash"])
    clock = FakeClock()
    stub = StubRaw(OFFERED_CALL)
    refused = False
    try:
        p1.run_p1_trials(
            stub, tampered_prepared,
            monotonic_clock=clock.monotonic,
            wall_clock=clock.wall, sleeper=clock.sleep)
    except p1.NativeProbeRefusal:
        refused = True
    check(name,
          any(marker in p for p in problems)
          and refused and stub.requests == []
          and clock.sleeps == [],
          "; ".join(problems)[:140])


# A condition pair differing by anything beyond the flag.
on_warm = copy.deepcopy(on)
on_warm["temperature"] = 0.9
warm_comparison = p1.build_comparison(
    prepared["baseline"], prepared["native_modified"],
    off, on_warm, prepared["full_definitions"],
    prepared["narrowed_definitions"],
    prepared["narrowing"], prepared["catalogue_source"],
    prepared["info"], prepared["assignment"],
    prepared["listing"],
    prepared["package"]["case"]["assignment"])
expect_refusal(
    "a condition pair differing by anything beyond "
    "the flag (a changed temperature on ON) fails the "
    "precondition and refuses before any request",
    dict(prepared, on_request=on_warm,
         comparison=warm_comparison),
    "condition pair differs")

defs_tampered = copy.deepcopy(comparison)
defs_tampered["narrowed_definitions_sha256"] = "f" * 64
expect_refusal(
    "a tampered narrowed-definitions hash — no longer "
    "the canonical hash of the OFF request's tools "
    "field — fails the precondition and refuses "
    "before any request",
    dict(prepared, comparison=defs_tampered),
    "narrowed definitions hash")

assignment_tampered = copy.deepcopy(comparison)
assignment_tampered["construction"][
    "variant_assignment"] += " Tampered."
assignment_tampered["construction"][
    "variant_assignment_sha256"] = sha256_hex(canonical(
        assignment_tampered["construction"]
        ["variant_assignment"]))
expect_refusal(
    "a tampered recorded variant assignment (its hash "
    "recomputed to match) fails the precondition — "
    "the requests' prompts are bound to the recorded "
    "text — and refuses before any request",
    dict(prepared, comparison=assignment_tampered),
    "is not the rendering of the recorded variant "
    "assignment")


# ---------------------------------------------------------------
# Classification, on stub captures.
# ---------------------------------------------------------------
def classify(capture):
    return p1.classify_p1_capture(capture)


result = classify(RETURNED_READ)
check("an accepted call to the withheld read_range is "
      "unoffered_call_returned × provider_accepted, "
      "its per-call record carrying the provider call "
      "ID and emitted ordinal",
      result["behaviour"] == "unoffered_call_returned"
      and result["delivery"] == "provider_accepted"
      and result["calls"][0]["name"] ==
      "sandbox.read_range"
      and result["calls"][0]["id"] == "fc-p1-read"
      and result["calls"][0]["ordinal"] == 0
      and result["calls"][0]["classification"] ==
      "unoffered_tool_attempt"
      and result["attempt_visible"] is None)

result = classify(RETURNED_SHELL)
check("an accepted shell call is likewise an "
      "unoffered call returned — any unoffered name, "
      "not only the withheld one",
      result["behaviour"] == "unoffered_call_returned"
      and result["has_unoffered_call"])

result = classify(OFFERED_CALL)
check("an accepted offered call is offered_tool_call",
      result["behaviour"] == "offered_tool_call"
      and not result["has_unoffered_call"])

result = classify(REFUSED_VISIBLE)
check("a refusal whose failed_generation carries the "
      "withheld name is provider_refused with "
      "attempt_visible yes — the attempt preserved as "
      "provider evidence, attributed from the error "
      "body, never promoted to a delivered call",
      result["delivery"] == "provider_refused"
      and result["attempt_visible"] is True
      and result["withheld_name_visible"] is True
      and result["failed_generation_names"] ==
      ["sandbox.read_range"]
      and result["behaviour"] == "unoffered_tool_attempt"
      and result["calls"][0]["source"] == "error_body"
      and result["calls"][0]["id"] is None)

result = classify(REFUSED_INVISIBLE)
check("a refusal without the attempt visible is "
      "provider_refused with attempt_visible no — a "
      "distinct observation from no attempt at all",
      result["delivery"] == "provider_refused"
      and result["attempt_visible"] is False
      and result["behaviour"] ==
      "no_observable_behaviour"
      and result["calls"] == [])

result = classify(FAILED_429)
check("a 429 is provider_failed — a delivery "
      "failure, not a model observation",
      result["delivery"] == "provider_failed")

# ---------------------------------------------------------------
# The run and the predeclared readings, on stub queues
# over a fake clock.
# ---------------------------------------------------------------
def run(captures):
    clock = FakeClock()
    stub = StubRaw(captures)
    trials = p1.run_p1_trials(
        stub, prepared, monotonic_clock=clock.monotonic,
        wall_clock=clock.wall, sleeper=clock.sleep)
    return clock, stub, trials


clock, stub, trials = run(
    [RETURNED_READ] * 5 + [REFUSED_VISIBLE] * 5)
counts, settled, readings = p1.summarise_p1(trials)
check("five returned unoffered calls establish "
      "behaviour (a) for OFF; five refusals with the "
      "attempt visible establish (b) for ON; the "
      "different established behaviours measure the "
      "flag's effect",
      readings["per_condition"]["off"]["reading"] ==
      "behaviour_a_established"
      and readings["per_condition"]["on"]["reading"] ==
      "behaviour_b_established"
      and readings["cross_condition"] ==
      "flag_effect_measured",
      json.dumps(readings)[:160])
check("exactly one request per trial — ten requests, "
      "the first five the OFF request, the last five "
      "the ON request, no follow-up generation",
      len(stub.requests) == 10
      and all(canonical(r) == canonical(off)
              for r in stub.requests[:5])
      and all(canonical(r) == canonical(on)
              for r in stub.requests[5:]))
starts = [t["request_start_monotonic_offset_seconds"]
          for t in trials]
check("the pacing holds the 65-second monotonic "
      "floor across all ten trials, the condition "
      "boundary included, the first trial immediate",
      starts[0] == 0.0 and all(
          b - a >= np.MIN_TRIAL_START_INTERVAL_SECONDS
          for a, b in zip(starts, starts[1:])),
      f"offsets={starts}")
check("the trials carry their conditions in order — "
      "five OFF then five ON",
      [t["condition"] for t in trials] ==
      ["off"] * 5 + ["on"] * 5)

_, _, trials = run([OFFERED_CALL] * 10)
counts, settled, readings = p1.summarise_p1(trials)
check("no unoffered attempt in either condition: "
      "each condition reads no attempt observed, and "
      "the flag comparison is inconclusive for the "
      "flag's effect — agreement in non-observation "
      "establishes nothing about the flag",
      readings["per_condition"]["off"]["reading"] ==
      "no_unoffered_attempt_observed"
      and readings["per_condition"]["on"]["reading"] ==
      "no_unoffered_attempt_observed"
      and readings["cross_condition"] ==
      "inconclusive_for_flag_effect")

_, _, trials = run(
    [RETURNED_READ, RETURNED_READ, OFFERED_CALL,
     OFFERED_CALL, OFFERED_CALL] + [OFFERED_CALL] * 5)
counts, settled, readings = p1.summarise_p1(trials)
check("two returned unoffered calls in OFF is a "
      "split — no reading forced past the thresholds",
      readings["per_condition"]["off"]["reading"] ==
      "split_no_reliable_observation"
      and readings["per_condition"]["off"]
      ["unoffered_call_returned"] == 2)

_, _, trials = run([FAILED_429] * 5 + [OFFERED_CALL] * 5)
counts, settled, readings = p1.summarise_p1(trials)
check("delivery failures stand outside the readings' "
      "denominator: five 429s leave OFF with no "
      "delivered trials and no reading manufactured "
      "from them",
      readings["per_condition"]["off"]["delivered"] == 0
      and readings["per_condition"]["off"]["reading"] ==
      "no_delivered_trials"
      and counts["delivery"]["provider_failed"] == 5)

# ---------------------------------------------------------------
# The durable outputs.
# ---------------------------------------------------------------
_, _, trials = run(
    [RETURNED_READ] * 5 + [REFUSED_VISIBLE] * 5)
evidence = p1.probe_evidence_object(comparison, trials)
out_dir = os.path.join(TMP, "out")
written = np.write_outputs(out_dir, comparison, evidence)
loaded = {}
for path in written:
    with open(path, encoding="utf-8") as fh:
        loaded[os.path.basename(path)] = json.load(fh)
check("the outputs write and read back — comparison "
      "and probe evidence, the evidence hash verifying "
      "over the written artifact",
      set(loaded) == {"comparison.json",
                      "probe-evidence.json"}
      and loaded["probe-evidence.json"]["evidence_hash"]
      == p1.p1_evidence_hash(evidence))
check("the written evidence preserves the refusal "
      "evidence and the returned call's provider ID — "
      "the readings reconstructable from the artifact "
      "alone",
      loaded["probe-evidence.json"]["trials"][5]
      ["attempt_visible"] is True
      and loaded["probe-evidence.json"]["trials"][0]
      ["calls"][0]["id"] == "fc-p1-read"
      and loaded["probe-evidence.json"]["readings"]
      ["cross_condition"] == "flag_effect_measured")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
