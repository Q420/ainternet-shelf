"""Native adapter probe P2 tests — the machinery of
NATIVE-ADAPTER-P2-PROBE-PROPOSAL Rev 1 (PASSED at
INDEX 358), built against stub raw calls only: no live
provider request is made anywhere in this suite.

- the construction reproduces from the evidenced
  record by the real construction path: the listing's
  sizes are the evidenced sandbox files' own sizes,
  the variant assignment requires the brief to rest
  on the two named sources each in full, and the
  request differs from the admitted native-offer
  request at exactly the task-context path, its tools
  field byte-unchanged (the full catalogue offered);
- tamper witnesses: a request whose tools field
  differs from the native-offer construction fails
  the precondition and the runner refuses before ANY
  provider request and before any pacing wait; a
  tampered recorded diff entry refuses; a tampered
  recorded variant assignment refuses — the request's
  prompt is bound to the recorded text;
- classification: two read calls addressing the two
  required sources are multi_call with the
  two-independent-openings shape, every call's
  provider call ID, name, arguments and emitted order
  preserved; two calls of another shape are reported
  as that shape, a mixture including an unoffered
  name as that mixture; one call is single_call with
  the required source it addresses recorded; a
  malformed single call is malformed; a refusal
  delivers no countable response;
- the predeclared readings compute as stated: three
  or more multi_call trials live-evidence multi-call
  emission; five single_call trials read as the
  first-response observation only; a split is a
  split; a majority of no-call trials is a
  construction finding, inconclusive for the
  multi-call question;
- exactly one request per trial across all five
  trials, and the pacing holds the 65-second
  monotonic floor;
- the durable outputs carry the comparison and the
  per-trial evidence — the envelope standing in the
  artifact — and the evidence hash verifies over the
  written artifact.

Run: PYTHONPATH=src python3 \
    tests/unit/test_piece_native_probe_p2.py
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
from framework import native_probe_p2 as p2  # noqa: E402

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


def calls_message(calls, content=None):
    return {"role": "assistant", "content": content,
            "tool_calls": [{
                "id": call_id, "type": "function",
                "function": {"name": name,
                             "arguments": arguments}}
                for call_id, name, arguments in calls]}


def read_args(path):
    return json.dumps({"path": path, "start_line": 1,
                       "end_line": 50})


TWO_READS = body_capture(calls_message([
    ("fc1", "sandbox.read_range",
     read_args("sources/stock-take.md")),
    ("fc2", "sandbox.read_range",
     read_args("sources/a3-pass.md"))]))
TWO_SAME_SOURCE = body_capture(calls_message([
    ("fc1", "sandbox.read_range",
     read_args("sources/stock-take.md")),
    ("fc2", "sandbox.read_range",
     json.dumps({"path": "sources/stock-take.md",
                 "start_line": 51, "end_line": 100}))]))
MULTI_WITH_UNOFFERED = body_capture(calls_message([
    ("fc1", "sandbox.list",
     json.dumps({"path": "sources/stock-take.md"})),
    ("fc2", "container.exec",
     json.dumps({"cmd": ["bash"]}))]))
SINGLE_READ = body_capture(calls_message([
    ("fc1", "sandbox.read_range",
     read_args("sources/a3-pass.md"))]))
SINGLE_LIST = body_capture(calls_message([
    ("fc1", "sandbox.list",
     json.dumps({"path": "sources/index-tail.md"}))]))
MALFORMED_SINGLE = body_capture(calls_message([
    ("fc1", "sandbox.search", "{not json")]))
TEXT_ONLY = body_capture({
    "role": "assistant",
    "content": json.dumps({"outcome": "yield",
                            "summary": "stub brief"})})
REFUSAL = {
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

# ---------------------------------------------------------------
# The construction, from the real evidenced record.
# ---------------------------------------------------------------
TMP = tempfile.mkdtemp(prefix="native-probe-p2-witness-")
prepared = p2.prepare(
    EVIDENCED, os.path.join(TMP, "w1"), PIN)
comparison = prepared["comparison"]
request = prepared["request"]
check("the pre-presented listing's sizes are the "
      "evidenced sandbox files' own sizes",
      all(entry["size_bytes"] == os.path.getsize(
          os.path.join(EVIDENCED, "sandbox",
                       entry["path"]))
          for entry in prepared["listing"]))
check("the variant assignment requires the brief to "
      "rest on the two named sources, each read in "
      "full, and pre-presents the listing",
      "two sources, each read in full: "
      "sources/stock-take.md and sources/a3-pass.md"
      in prepared["assignment"]
      and all(entry["path"] in prepared["assignment"]
              for entry in prepared["listing"]))
check("the request differs from the admitted "
      "native-offer request at exactly the task-"
      "context path, its tools field byte-unchanged "
      "from the native-offer construction",
      comparison["vs_native_offer"]["differing_paths"]
      == ["messages[1].content"]
      and canonical(request["tools"]) ==
      canonical(prepared["native_modified"]["tools"])
      and comparison["definitions_sha256"] ==
      sha256_hex(canonical(request["tools"])))
check("the request sends neither tool_choice nor the "
      "validation flag — the flag is P1's variable",
      "tool_choice" not in request
      and "disable_tool_validation" not in request)
check("the comparison's hashes recompute and the "
      "precondition passes on the genuine artifacts",
      p2.check_precondition(
          prepared["baseline"],
          prepared["native_modified"], request,
          comparison, prepared["package"],
          prepared["info"]["catalogue_hash"]) == [])

# ---------------------------------------------------------------
# Tampering fails the precondition, before any request.
# ---------------------------------------------------------------
def expect_refusal(name, tampered_prepared, marker):
    problems = p2.check_precondition(
        tampered_prepared["baseline"],
        tampered_prepared["native_modified"],
        tampered_prepared["request"],
        tampered_prepared["comparison"],
        tampered_prepared["package"],
        tampered_prepared["info"]["catalogue_hash"])
    clock = FakeClock()
    stub = StubRaw(TWO_READS)
    refused = False
    try:
        p2.run_p2_trials(
            stub, tampered_prepared,
            monotonic_clock=clock.monotonic,
            wall_clock=clock.wall, sleeper=clock.sleep)
    except p2.NativeProbeRefusal:
        refused = True
    check(name,
          any(marker in p for p in problems)
          and refused and stub.requests == []
          and clock.sleeps == [],
          "; ".join(problems)[:140])


tools_cut = copy.deepcopy(request)
tools_cut["tools"] = tools_cut["tools"][:2]
cut_comparison = p2.build_comparison(
    prepared["baseline"], prepared["native_modified"],
    tools_cut, prepared["definitions"],
    prepared["catalogue_source"], prepared["info"],
    prepared["assignment"], prepared["listing"],
    prepared["package"]["case"]["assignment"])
expect_refusal(
    "a tools difference — the request offering two "
    "definitions where the native-offer construction "
    "offers three — fails the precondition and "
    "refuses before any request",
    dict(prepared, request=tools_cut,
         comparison=cut_comparison),
    "tools field differs")

diff_tampered = copy.deepcopy(comparison)
diff_tampered["vs_native_offer"]["diff"][0][
    "modified"]["sha256"] = "f" * 64
expect_refusal(
    "a recorded diff entry altered (a side's hash "
    "flipped) fails the precondition and refuses "
    "before any request",
    dict(prepared, comparison=diff_tampered),
    "diff entries do not equal")

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
    "the request's prompt is bound to the recorded "
    "text — and refuses before any request",
    dict(prepared, comparison=assignment_tampered),
    "is not the rendering of the recorded variant "
    "assignment")

# ---------------------------------------------------------------
# Classification, on stub captures.
# ---------------------------------------------------------------
def classify(capture):
    return p2.classify_p2_capture(capture)


result = classify(TWO_READS)
check("two read calls addressing the two required "
      "sources are multi_call with the two-"
      "independent-openings shape — every call's ID, "
      "name, arguments and emitted order preserved",
      result["behaviour"] == "multi_call"
      and result["shape"] == "two_independent_openings"
      and result["call_count"] == 2
      and [(c["id"], c["ordinal"], c["name"])
           for c in result["calls"]] ==
      [("fc1", 0, "sandbox.read_range"),
       ("fc2", 1, "sandbox.read_range")]
      and result["sources_addressed"] ==
      ["sources/a3-pass.md", "sources/stock-take.md"])

result = classify(TWO_SAME_SOURCE)
check("two calls on one source are multi_call of "
      "another shape — reported, not flattened into "
      "the count",
      result["behaviour"] == "multi_call"
      and result["shape"] == "other_shape")

result = classify(MULTI_WITH_UNOFFERED)
check("a multi-call response including an unoffered "
      "name is multi_call with the mixture shape, the "
      "unoffered fact carried in the flags",
      result["behaviour"] == "multi_call"
      and result["shape"] ==
      "mixture_including_unoffered"
      and result["has_unoffered_call"])

result = classify(SINGLE_READ)
check("one call is single_call, the required source "
      "it addresses recorded",
      result["behaviour"] == "single_call"
      and result["addresses_required_source"] ==
      "sources/a3-pass.md"
      and result["calls"][0]["id"] == "fc1")

result = classify(SINGLE_LIST)
check("a single call addressing no required source "
      "is single_call with that fact recorded",
      result["behaviour"] == "single_call"
      and result["addresses_required_source"] is None)

result = classify(MALFORMED_SINGLE)
check("a single call with malformed arguments is "
      "malformed, never a single_call success",
      result["behaviour"] == "malformed"
      and result["call_count"] == 1)

result = classify(TEXT_ONLY)
check("a valid text-only answer is text_contract",
      result["behaviour"] == "text_contract"
      and result["call_count"] == 0)

result = classify(REFUSAL)
check("a refusal delivers no countable response — "
      "no_observable_behaviour × provider_refused — "
      "with the attributable attempt preserved in the "
      "per-call records",
      result["behaviour"] == "no_observable_behaviour"
      and result["delivery"] == "provider_refused"
      and result["call_count"] == 1
      and result["calls"][0]["name"] ==
      "sandbox.read_range")

# ---------------------------------------------------------------
# The run and the predeclared readings, on stub queues
# over a fake clock.
# ---------------------------------------------------------------
def run(captures):
    clock = FakeClock()
    stub = StubRaw(captures)
    trials = p2.run_p2_trials(
        stub, prepared, monotonic_clock=clock.monotonic,
        wall_clock=clock.wall, sleeper=clock.sleep)
    return clock, stub, trials


clock, stub, trials = run([TWO_READS] * 5)
counts, settled, reading = p2.summarise_p2(trials)
check("five two-call responses live-evidence "
      "multi-call emission, the reading computed over "
      "the settled delivered trials",
      reading == "multi_call_live_evidenced"
      and settled == 5
      and counts["behaviour"]["multi_call"] == 5)
check("exactly one request per trial — five requests, "
      "each the admitted request, tool-calling "
      "responses triggering no follow-up",
      len(stub.requests) == 5 and all(
          canonical(r) == canonical(request)
          for r in stub.requests))
starts = [t["request_start_monotonic_offset_seconds"]
          for t in trials]
check("the pacing holds the 65-second monotonic "
      "floor, the first trial immediate",
      starts == [0.0, 65.0, 130.0, 195.0, 260.0],
      f"offsets={starts}")

_, _, trials = run([SINGLE_READ] * 5)
counts, settled, reading = p2.summarise_p2(trials)
check("five single-call responses read as the "
      "first-response observation only",
      reading == "single_call_first_response_only"
      and counts["behaviour"]["single_call"] == 5)

_, _, trials = run([TWO_READS, SINGLE_READ, TWO_READS,
                    SINGLE_READ, SINGLE_READ])
counts, settled, reading = p2.summarise_p2(trials)
check("a split — two multi, three single — is "
      "reported as exactly that",
      reading == "split_reported"
      and counts["behaviour"]["multi_call"] == 2
      and counts["behaviour"]["single_call"] == 3)

_, _, trials = run([TEXT_ONLY, TEXT_ONLY, TEXT_ONLY,
                    SINGLE_READ, SINGLE_READ])
counts, settled, reading = p2.summarise_p2(trials)
check("a majority of no-call trials is a "
      "construction finding — inconclusive for the "
      "multi-call question",
      reading == "construction_inconclusive"
      and counts["behaviour"]["text_contract"] == 3)

# ---------------------------------------------------------------
# The durable outputs.
# ---------------------------------------------------------------
_, _, trials = run([TWO_READS] * 5)
evidence = p2.probe_evidence_object(comparison, trials)
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
      == p2.p2_evidence_hash(evidence))
check("the written evidence preserves the envelope — "
      "each trial's calls with their IDs and emitted "
      "order, and the multi-call shape",
      all([(c["id"], c["ordinal"])
           for c in t["calls"]] ==
          [("fc1", 0), ("fc2", 1)]
          and t["shape"] == "two_independent_openings"
          for t in
          loaded["probe-evidence.json"]["trials"]))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES")
    sys.exit(1)
print("ALL PASS")
