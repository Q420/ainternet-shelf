"""Chain simulation — transport and latency measurement
for the first-worker run's call chain (INDEX 214/215).

Why this exists. Attempts 3 and 4 each died at the
worker's second step — the composition call — on a clock
nobody had listed: first the adapter's 120s span, then a
second hardcoded 120s inside the connector helper. The
repair (INDEX 215) put the helper on the caller's
effective allowance. Before another commissioned attempt
is spent, this script measures the repaired chain itself,
outside any run: no framework store is written, no run
directory is created, nothing is assembled or activated,
no worker identity exists here. It is transport and
latency evidence only — never worker-work evidence.

Three experiments, three repetitions each, every result
reported with the median:

1. A tiny prompt end to end (one word asked) — the
   baseline route and queue latency, at the scale of the
   worker's first-iteration call.
2. The COMPLETE rendered model request of attempt 4's
   iteration 2 — system instructions, case, view/delta,
   the three full tool results, the tool catalogue, the
   response contract — with only the final ask changed
   (an appended instruction to disregard the assignment
   and reply with the single word "ready"). This measures
   the cost of presenting the real input, and doubles as
   the request-identity check: the provider-reported
   prompt_tokens must land near the expected ~15–18K; a
   far smaller number means the payload did not travel
   intact and is flagged loudly.
3. A small prompt asking for ~1,000 tokens of output —
   the generation rate.

The projection (stated in the results): the composition
call's projected seconds = experiment 2's median wall
(the full input presented, a one-word answer) + 1000 /
experiment 3's median generation rate (the brief's
~1,000 output tokens at the measured rate). The
whole-assignment projection = experiment 1's median
(an iteration-1-scale call) + the projected composition,
against the 600s activation budget; identify() is
measured once and reported separately — it happens
before activation, is governed by the adapter timeout,
and is never charged to the activation budget.

Every call goes through the exact route attempt 5 will
use: the framework adapter configured from the
environment exactly as live-demo/first_worker_run.py
configures it, its transport carried by the registered
connector helper through live-demo/connector_transport.py.
The calls are made at the transport seam (adapter._call)
so the RAW provider JSON — including `usage` — is
captured from the helper's actual stdout (an instrumented
_Popen inside this process only; the chain itself is
unmodified). The interface is non-streaming: the whole
response arrives at once, so time-to-first-response
cannot be separated from total response time here.

Run it:  ADAPTER_TIMEOUT=300 PYTHONPATH=src \
             python3 live-demo/chain_simulation.py
Options: --reps N (default 3), --results PATH (default
live-demo/chain-simulation-results.json), --stub (a
self-test mode: the helper subprocess is replaced by a
fake returning canned provider JSON instantly — the
whole pipeline runs, no provider is called, and the
results are marked as stub evidence).
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.adapter import (AdapterFailure,  # noqa: E402
                               OpenAICompatibleAdapter,
                               _render_prompt)
from framework.doorway import Doorway  # noqa: E402
from framework.loop import Loop  # noqa: E402
from framework.record import FrameworkStore  # noqa: E402

import connector_transport  # noqa: E402
from connector_transport import (  # noqa: E402
    install_connector_transport)

MODEL_DEFAULT = "moonshotai/kimi-k3.1-pro"
CONNECTOR_HELPER = os.path.expanduser(
    "~/workspace/custom-connectors/custom.nvidia/bin/"
    "nvidia_api.py")
ATTEMPT4_DIR = os.path.join(ROOT, "live-demo",
                            "first-worker-attempt4")
DEFAULT_RESULTS = os.path.join(ROOT, "live-demo",
                               "chain-simulation-results.json")

# The request-identity expectation for experiment 2
# (INDEX 215): the complete rendered iteration-2 request
# carries ~15–18K provider-counted prompt tokens. A count
# far below the floor means the large tool results did
# not travel intact.
EXPECTED_PROMPT_TOKENS = (15000, 18000)
IDENTITY_FLOOR = 12000

# The decision rule's margin (INDEX 215): the projection
# must sit beneath the 300s per-call ceiling with a
# credible margin — stated here as at least 60s — with
# the 600s activation deadline respected across the
# assignment.
PER_CALL_CEILING = 300.0
ACTIVATION_BUDGET = 600.0
CREDIBLE_MARGIN = 60.0
BRIEF_OUTPUT_TOKENS = 1000

OVERRIDE_ASK = (
    "\n\nMEASUREMENT OVERRIDE: this presentation is a "
    "latency measurement, not the assignment. Disregard "
    "the assignment above entirely and reply with the "
    "single word \"ready\" and nothing else — no JSON, "
    "no punctuation, no other text.")


# ----------------------------------------------------- raw capture
class _RecordingProc:
    """A transparent wrapper around the helper process
    the transport spawns: delegates everything, records
    the stdout bytes of communicate() so the caller can
    read the RAW provider JSON (including `usage`) the
    helper actually returned. Instrumentation inside
    this process only — the chain is unmodified."""

    def __init__(self, real, sink):
        self._real = real
        self._sink = sink

    def communicate(self, input=None, timeout=None):
        out, err = self._real.communicate(input=input,
                                          timeout=timeout)
        self._sink.append(out)
        return out, err

    def __getattr__(self, name):
        return getattr(self._real, name)


class _FakeProc:
    """The --stub self-test's helper stand-in: answers
    instantly with a canned provider body."""

    def __init__(self, body):
        self._body = body
        self.returncode = None
        self.pid = 0
        self.stdin = None
        self.stdout = None
        self.stderr = None

    def communicate(self, input=None, timeout=None):
        # A small fixed delay, so the self-test's wall
        # clocks are nonzero and the rate/projection
        # arithmetic is genuinely exercised.
        time.sleep(0.05)
        self.returncode = 0
        return self._body, b""

    def poll(self):
        return self.returncode

    def send_signal(self, sig):
        pass


def _canned_body(model):
    return json.dumps({
        "id": "chatcmpl-stub", "model": model,
        "choices": [{"index": 0, "message": {
            "role": "assistant",
            "content": "I am a stub declaration. ready"}}],
        "usage": {"prompt_tokens": 1234,
                  "completion_tokens": 42,
                  "total_tokens": 1276}}).encode("utf-8")


# ------------------------------------------------------ one call
def make_caller(adapter, sink):
    """call(messages) -> one measurement dict: the call
    made at the transport seam (adapter._call, exactly
    what the loop's callable reaches), the wall-clock
    seconds, and the raw provider JSON captured from the
    helper's stdout for THIS call."""

    def call(messages):
        del sink[:]
        started = time.perf_counter()
        failure = None
        content = provider_model_id = None
        try:
            content, provider_model_id = adapter._call(
                messages)
        except AdapterFailure as exc:
            failure = {"kind": exc.kind,
                       "detail": exc.detail}
        except Exception as exc:  # noqa: BLE001 — measured,
            # never hidden
            failure = {"kind": type(exc).__name__,
                       "detail": str(exc)}
        wall = time.perf_counter() - started
        raw = None
        if sink:
            try:
                raw = json.loads(
                    sink[-1].decode("utf-8", "replace"))
            except ValueError:
                raw = None
        usage = (raw or {}).get("usage") or {}
        return {
            "wall_seconds": round(wall, 3),
            "ok": failure is None,
            "failure": failure,
            "content_preview":
                (content[:80] if isinstance(content, str)
                 else None),
            "provider_model_id": provider_model_id,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens":
                usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "raw_usage_captured": bool(usage),
        }

    return call


def run_reps(call, messages, reps):
    out = []
    for i in range(1, reps + 1):
        result = call(messages)
        result = {"rep": i, **result}
        out.append(result)
        print(f"    rep {i}: wall="
              f"{result['wall_seconds']}s "
              f"prompt_tokens={result['prompt_tokens']} "
              f"completion_tokens="
              f"{result['completion_tokens']}"
              + ("" if result["ok"] else
                 f" FAILURE={result['failure']}"))
    return out


def median_of(reps, key):
    values = [r[key] for r in reps
              if r.get("ok") and r.get(key) is not None]
    return statistics.median(values) if values else None


# --------------------------------------- experiment 2's package
def _parse_ts(text):
    return datetime.fromisoformat(
        text.replace("Z", "+00:00"))


def reconstruct_iteration2():
    """The package attempt 4's iteration 2 was built
    from, reconstructed with the loop's OWN package
    construction (Loop._build_package, unmodified)
    against a COPY of attempt 4's store, the copy's view
    of the record filtered to the exact head the package
    was frozen at (iteration 2's recorded cursor_to).
    The original store is only ever read (a sqlite
    read-only connection for the facts, file copies for
    the doorway); no event is written anywhere.

    One field cannot be re-derived from the live clock:
    bounds.seconds_remaining was the doorway's monotonic
    remainder at build time, and the activation's
    monotonic anchor belongs to a finished process. It
    is reconstructed from the record's own timestamps —
    the pinned deadline (600s) minus the recorded
    activation-to-iteration-2 interval (52s) = 548s,
    the value the live remainder equalled within a
    second — by standing the record-derived value in
    for doorway.activation_remaining during this one
    construction. That substitution, and the filtered
    copy, are the reconstruction's whole deviation from
    the live path; both are reported in the results."""
    store_path = os.path.join(ATTEMPT4_DIR, "run.db")
    conn = sqlite3.connect(f"file:{store_path}?mode=ro",
                           uri=True)
    try:
        rows = conn.execute(
            "SELECT event_seq, type, ts, payload FROM "
            "events ORDER BY event_seq").fetchall()
    finally:
        conn.close()
    events = [{"event_seq": seq, "type": typ, "ts": ts,
               "payload": json.loads(payload)}
              for seq, typ, ts, payload in rows]
    activated = next(e for e in events
                     if e["type"] == "INSTANCE_ACTIVATED")
    iter2 = next(e for e in events
                 if e["type"] == "LOOP_ITERATION"
                 and e["payload"].get("iteration") == 2)
    iter1 = next(e for e in events
                 if e["type"] == "LOOP_ITERATION"
                 and e["payload"].get("iteration") == 1)
    cursor_from = iter2["payload"]["cursor_from"]
    cursor_to = iter2["payload"]["cursor_to"]
    deadline_seconds = iter2["payload"]["deadline_seconds"]
    elapsed = (_parse_ts(iter2["ts"])
               - _parse_ts(activated["ts"])).total_seconds()
    remaining = deadline_seconds - elapsed
    instance_id = iter2["payload"]["instance_id"]
    assembly_id = iter2["payload"]["assembly_id"]

    tmp = tempfile.mkdtemp(prefix="chain-sim-attempt4-")
    try:
        copy_path = os.path.join(tmp, "run.db")
        for suffix in ("", "-wal", "-shm"):
            if os.path.exists(store_path + suffix):
                shutil.copyfile(store_path + suffix,
                                copy_path + suffix)
        anchors = store_path + ".anchors.json"
        if os.path.exists(anchors):
            shutil.copyfile(anchors,
                            copy_path + ".anchors.json")
        store = FrameworkStore(copy_path)
        doorway = Doorway(store)
        frozen = [e for e in store.all_events()
                  if e["event_seq"] <= cursor_to]
        store.all_events = lambda: list(frozen)
        doorway.activation_remaining = \
            lambda iid: (remaining, None)
        state = doorway.state()
        _aid, entry = doorway._assembly_entry_of_instance(
            state, instance_id)
        seat = entry.get("seat")
        ctx = {
            "instance_id": instance_id,
            "assembly_id": assembly_id,
            "seat": seat,
            "role": (state["seats"].get(seat)
                     or {}).get("role"),
            "case_id": entry.get("case_id"),
            "case_version": entry.get("case_version"),
            "content": copy.deepcopy(
                doorway._pinned_case_content(state, entry)),
            "activated_seq": entry.get("activated_seq"),
            "bounds": doorway._pinned_loop_bounds(
                state, entry),
            "cursor": cursor_from,
            "iterations": 1,
            "recorded": [],
            "refused": [],
            "dispatched": [],
        }
        package, head = Loop(doorway, None,
                             None)._build_package(ctx)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if head != cursor_to:
        raise RuntimeError(
            f"reconstruction froze at head {head}, not "
            f"iteration 2's recorded {cursor_to}")
    provenance = {
        "source_store": store_path,
        "method": "the loop's own _build_package against "
                  "a copy of attempt 4's store, the "
                  "copy's record filtered to iteration "
                  "2's recorded cursor_to (the head the "
                  "package was frozen at); no event "
                  "written anywhere",
        "cursor_from": cursor_from,
        "cursor_to": cursor_to,
        "frozen_head": head,
        "seconds_remaining": {
            "value": remaining,
            "provenance": "record-derived: the pinned "
                          "deadline_seconds minus the "
                          "recorded activation-to-"
                          "iteration-2 timestamp interval "
                          f"({elapsed:.0f}s); the live "
                          "monotonic remainder it stands "
                          "in for equalled this within a "
                          "second",
        },
        "deviations": [
            "bounds.seconds_remaining is the "
            "record-derived value above, not a live "
            "monotonic reading (the activation's anchor "
            "belongs to a finished process and cannot "
            "be re-read)",
            "the package is built against a filtered "
            "copy of the record, not the live store — "
            "the loop's construction itself is "
            "unmodified and the original store is "
            "untouched",
        ],
    }
    return package, provenance


def build_exp2_messages(package, model):
    """The messages the adapter's __call__ would send
    for this package — its system message verbatim, its
    rendered prompt verbatim (_render_prompt) — with
    the ONE change the measurement makes: the override
    ask appended to the user content. Returns
    (messages, rendered_body_bytes), the byte count
    being the exact serialized request the transport
    hands the helper."""
    prompt = _render_prompt(package)
    messages = [
        {"role": "system",
         "content": "You are a seat in a recorded "
                    "collaborative run. Answer exactly "
                    "as the contract specifies."},
        {"role": "user", "content": prompt + OVERRIDE_ASK},
    ]
    body = json.dumps({"model": model,
                       "messages": messages,
                       "temperature": 0.2}).encode("utf-8")
    return messages, len(body)


# ----------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Chain simulation: transport and "
                    "latency measurement for the "
                    "first-worker call chain (INDEX "
                    "214/215). No run is commissioned; "
                    "no store is written.")
    parser.add_argument("--reps", type=int, default=3,
                        help="repetitions per experiment "
                             "(default 3)")
    parser.add_argument("--results", default=DEFAULT_RESULTS,
                        help="results JSON path (default "
                             "live-demo/chain-simulation-"
                             "results.json)")
    parser.add_argument("--stub", action="store_true",
                        help="self-test mode: the helper "
                             "subprocess is replaced by "
                             "a fake returning canned "
                             "provider JSON instantly; no "
                             "provider is called")
    args = parser.parse_args(argv)
    if args.reps < 1:
        parser.error("--reps must be at least 1")

    adapter = OpenAICompatibleAdapter(
        endpoint=os.environ.get(
            "ADAPTER_ENDPOINT",
            "https://integrate.api.nvidia.com/v1/chat/"
            "completions"),
        model=os.environ.get("ADAPTER_MODEL",
                             MODEL_DEFAULT),
        timeout=float(os.environ.get("ADAPTER_TIMEOUT",
                                     "120")))
    install_connector_transport(adapter, CONNECTOR_HELPER,
                                adapter.model)

    sink = []
    real_popen = connector_transport._Popen
    if args.stub:
        body = _canned_body(adapter.model)
        connector_transport._Popen = \
            lambda *a, **kw: _RecordingProc(
                _FakeProc(body), sink)
    else:
        def recording_popen(*a, **kw):
            return _RecordingProc(real_popen(*a, **kw),
                                  sink)
        connector_transport._Popen = recording_popen
    try:
        call = make_caller(adapter, sink)

        results = {
            "kind": "chain simulation — transport and "
                    "latency evidence (not worker-work "
                    "evidence; no run commissioned, no "
                    "store written, no assembly or "
                    "activation)",
            "recorded_at": datetime.now(
                timezone.utc).isoformat(),
            "stub_mode": bool(args.stub),
            "configuration": {
                "endpoint": adapter.endpoint,
                "model": adapter.model,
                "adapter_timeout_seconds": adapter.timeout,
                "helper": CONNECTOR_HELPER,
                "transport": "live-demo/"
                             "connector_transport.py "
                             "(connector helper route, "
                             "INDEX 192/215)",
                "repetitions_per_experiment": args.reps,
                "interface": "non-streaming — the whole "
                             "response arrives at once, "
                             "so time-to-first-response "
                             "cannot be separated from "
                             "total response time "
                             "through this interface",
            },
        }

        # identify(): the adapter's own identity call,
        # measured once. It happens BEFORE activation in
        # a run, is governed by the adapter timeout, and
        # is never charged to the activation budget —
        # reported separately, as its own clock (INDEX
        # 215). Afterwards the adapter's operation
        # deadline is cleared so the direct seam calls
        # below fall back to the configured span, as the
        # witness's direct calls do.
        print("identify() — pre-activation, its own "
              "clock:")
        started = time.perf_counter()
        identify_failure = None
        identity = None
        try:
            identity = adapter.identify()
        except AdapterFailure as exc:
            identify_failure = {"kind": exc.kind,
                                "detail": exc.detail}
        identify_wall = time.perf_counter() - started
        adapter._deadline = None
        usage = {}
        if sink:
            try:
                usage = (json.loads(sink[-1].decode(
                    "utf-8", "replace")) or {}).get(
                        "usage") or {}
            except ValueError:
                usage = {}
        results["identify_pre_activation"] = {
            "wall_seconds": round(identify_wall, 3),
            "ok": identify_failure is None,
            "failure": identify_failure,
            "provider_model_id":
                (identity or {}).get("provider_model_id"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens":
                usage.get("completion_tokens"),
            "note": "pre-activation; governed by the "
                    "adapter timeout, NOT charged to "
                    "the 600s activation budget",
        }
        print(f"    wall={identify_wall:.3f}s "
              f"ok={identify_failure is None}")

        # -- Experiment 1: the tiny prompt.
        print("experiment 1 — tiny prompt, baseline:")
        exp1_messages = [{"role": "user", "content":
                          "Reply with the single word: "
                          "ready"}]
        exp1 = run_reps(call, exp1_messages, args.reps)
        exp1_median = median_of(exp1, "wall_seconds")
        results["experiment_1_tiny_prompt"] = {
            "description": "a tiny prompt end to end — "
                           "baseline route and queue "
                           "latency, at the scale of the "
                           "worker's first-iteration "
                           "call",
            "messages": exp1_messages,
            "reps": exp1,
            "median_wall_seconds": exp1_median,
        }

        # -- Experiment 2: the full iteration-2 request.
        print("experiment 2 — attempt 4's iteration-2 "
              "request at full weight, one word asked:")
        package, provenance = reconstruct_iteration2()
        exp2_messages, body_bytes = build_exp2_messages(
            package, adapter.model)
        exp2 = run_reps(call, exp2_messages, args.reps)
        exp2_median = median_of(exp2, "wall_seconds")
        token_counts = [r["prompt_tokens"] for r in exp2
                        if r.get("prompt_tokens")
                        is not None]
        identity_check = {
            "expected_prompt_tokens": list(
                EXPECTED_PROMPT_TOKENS),
            "observed_prompt_tokens": token_counts,
            "verdict": "not established — no provider "
                       "token count was captured",
        }
        if token_counts:
            low = min(token_counts)
            if low < IDENTITY_FLOOR:
                identity_check["verdict"] = (
                    "⚠ FLAG: a repetition reported "
                    f"{low} prompt tokens, far below "
                    f"the expected "
                    f"{EXPECTED_PROMPT_TOKENS[0]}–"
                    f"{EXPECTED_PROMPT_TOKENS[1]} — the "
                    "payload did NOT travel intact on "
                    "that repetition")
            elif all(EXPECTED_PROMPT_TOKENS[0]
                     <= n <= EXPECTED_PROMPT_TOKENS[1]
                     for n in token_counts):
                identity_check["verdict"] = (
                    "the complete request travelled "
                    "intact on every repetition (counts "
                    "inside the expected range)")
            else:
                identity_check["verdict"] = (
                    "counts outside the expected range "
                    "but above the intactness floor — "
                    "the payload travelled; the range "
                    "expectation, not the request, is "
                    "what differs")
        results["experiment_2_full_input"] = {
            "description": "the complete rendered "
                           "model request of attempt "
                           "4's iteration 2, with only "
                           "the final ask changed (an "
                           "appended override: disregard "
                           "the assignment, reply with "
                           "the single word 'ready')",
            "reconstruction": provenance,
            "rendered_request_bytes": body_bytes,
            "appended_override": OVERRIDE_ASK.strip(),
            "reps": exp2,
            "median_wall_seconds": exp2_median,
            "request_identity_check": identity_check,
        }
        if "FLAG" in identity_check["verdict"]:
            print("    " + identity_check["verdict"])

        # -- Experiment 3: the generation rate.
        print("experiment 3 — ~1,000 tokens of output, "
              "generation rate:")
        exp3_messages = [{
            "role": "user",
            "content": "Write a numbered list of 100 "
                       "short, distinct one-line tips "
                       "for staying focused while "
                       "working, numbered 1 to 100, "
                       "one tip per line. Do not add "
                       "any introduction or "
                       "conclusion."}]
        exp3 = run_reps(call, exp3_messages, args.reps)
        for rep in exp3:
            if rep.get("ok") and rep.get(
                    "completion_tokens") and rep.get(
                    "wall_seconds"):
                rep["generation_rate_tokens_per_second"] = \
                    round(rep["completion_tokens"]
                          / rep["wall_seconds"], 3)
            else:
                rep["generation_rate_tokens_per_second"] = \
                    None
        exp3_median_wall = median_of(exp3, "wall_seconds")
        rates = [r["generation_rate_tokens_per_second"]
                 for r in exp3
                 if r.get(
                     "generation_rate_tokens_per_second")
                 is not None]
        exp3_median_rate = (statistics.median(rates)
                            if rates else None)
        results["experiment_3_generation"] = {
            "description": "a small prompt asking for "
                           "roughly 1,000 tokens of "
                           "output — the generation "
                           "rate (completion tokens / "
                           "wall seconds, per rep)",
            "messages": exp3_messages,
            "reps": exp3,
            "median_wall_seconds": exp3_median_wall,
            "median_generation_rate_tokens_per_second":
                exp3_median_rate,
        }

        # -- The projection.
        projection = {
            "formula": "projected composition seconds = "
                       "median(experiment 2 wall) + "
                       f"{BRIEF_OUTPUT_TOKENS} / "
                       "median(experiment 3 generation "
                       "rate)",
            "brief_output_tokens_assumed":
                BRIEF_OUTPUT_TOKENS,
        }
        if exp2_median is not None and exp3_median_rate:
            composition = exp2_median + \
                BRIEF_OUTPUT_TOKENS / exp3_median_rate
            projection["composition_seconds"] = round(
                composition, 3)
            projection["per_call_ceiling_seconds"] = \
                PER_CALL_CEILING
            projection["margin_seconds"] = round(
                PER_CALL_CEILING - composition, 3)
            if composition >= PER_CALL_CEILING:
                reading = ("NO credible margin: the "
                           "projection meets or exceeds "
                           "the 300s per-call ceiling — "
                           "do not spend a commissioned "
                           "attempt discovering it")
            elif projection["margin_seconds"] \
                    >= CREDIBLE_MARGIN:
                reading = ("credible margin beneath "
                           "the 300s per-call ceiling")
            else:
                reading = ("beneath the 300s ceiling "
                           "but WITHOUT the stated "
                           f"{CREDIBLE_MARGIN:.0f}s "
                           "credible margin — thin")
            projection["decision_reading"] = reading
            if exp1_median is not None:
                whole = exp1_median + composition
                projection["whole_assignment"] = {
                    "formula": "median(experiment 1 "
                               "wall) + projected "
                               "composition seconds",
                    "seconds": round(whole, 3),
                    "activation_budget_seconds":
                        ACTIVATION_BUDGET,
                    "within_budget":
                        whole < ACTIVATION_BUDGET,
                    "note": "identify() excluded — "
                            "pre-activation, its own "
                            "clock (see "
                            "identify_pre_activation)",
                }
        else:
            projection["composition_seconds"] = None
            projection["decision_reading"] = (
                "not established — an experiment "
                "produced no successful measurement to "
                "project from")
        results["projection"] = projection
    finally:
        connector_transport._Popen = real_popen

    with open(args.results, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)
        fh.write("\n")

    identify_wall = results[
        "identify_pre_activation"]["wall_seconds"]
    proj = results["projection"]
    whole = proj.get("whole_assignment") or {}
    print()
    print("CHAIN SIMULATION — SUMMARY")
    print(f"  model: {adapter.model}  "
          f"adapter timeout: {adapter.timeout}s  "
          f"stub: {args.stub}")
    print(f"  identify() (pre-activation): "
          f"{identify_wall}s")
    print(f"  experiment 1 median wall: "
          f"{exp1_median}s")
    print(f"  experiment 2 median wall: "
          f"{exp2_median}s  (rendered request: "
          f"{body_bytes} bytes)")
    print(f"  experiment 2 identity check: "
          f"{identity_check['verdict']}")
    print(f"  experiment 3 median rate: "
          f"{exp3_median_rate} tokens/s")
    print(f"  projected composition: "
          f"{proj.get('composition_seconds')}s "
          f"(ceiling {PER_CALL_CEILING:.0f}s, margin "
          f"{proj.get('margin_seconds')}s)")
    if whole:
        print(f"  projected whole assignment: "
              f"{whole['seconds']}s of "
              f"{ACTIVATION_BUDGET:.0f}s budget "
              f"(within: {whole['within_budget']})")
    print(f"  decision reading: "
          f"{proj['decision_reading']}")
    print(f"  results: {args.results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
