#!/usr/bin/env python3
"""Focused verification for terminal_readout.py (Vane's correction rounds,
INDEX 441/443): full call IDs, argument summaries, recursive redaction of
arguments and results, live-watch finalisation only on an unambiguous
completion condition, idle never finalising, malformed-line visibility,
producer-closed finalisation. The report counts the checks it actually
executed. Run: python3 live-demo/test_terminal_readout.py.
"""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).parent
TOOL = HERE / "terminal_readout.py"
NATIVE1 = HERE / "first-worker-native1"
FULL_ID = "fc_5f4344e5-2273-4f7f-89b9-d4173ee6c42a"
SECRET = "s3cr3t-value-12345"
failures = []
executed = 0


def check(name, condition, detail=""):
    global executed
    executed += 1
    print(("PASS " if condition else "FAIL ") + name
          + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


def run_tool(*argv, timeout=60):
    return subprocess.run([sys.executable, str(TOOL), *argv],
                          capture_output=True, text=True, timeout=timeout)


EVENTS = [
    {"type": "CALL_ENTERED", "payload": {"iteration": 1}},
    {"type": "TRANSLATION_RECORDED", "payload": {"calls": [
        {"name": "sandbox.list", "provider_call_id": FULL_ID,
         "resolution": "resolved", "arguments_sha256": "6bd528b4"}]}},
    {"type": "TOOL_REQUESTED", "payload": {
        "tool": "sandbox.list", "request_id": "req-1",
        "parameters": {"path": "sources/stock-take.md"}}},
    {"type": "TOOL_DISPATCHED", "payload": {
        "tool": "sandbox.list", "dispatch_id": "dispatch-1"}},
    {"type": "TOOL_OUTCOME", "payload": {
        "outcome": "result", "result": {"content_bytes": 110}}},
    {"type": "LOOP_STALLED", "payload": {
        "ground": "provider_failure", "detail": "provider_error: HTTP 400"}},
]

# 1. Render of the real native1 export.
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "readout.md"
    proc = run_tool("render", str(NATIVE1), "-o", str(out))
    md = out.read_text() if out.exists() else ""
    check("render exits 0", proc.returncode == 0, proc.stderr[-200:])
    check("render keeps the full provider call ID", FULL_ID in md)
    check("render shows the requested argument summary",
          "sources/stock-take.md" in md and "requested" in md)
    check("render shows the stall with its ground",
          "stalled" in md and "provider_failure" in md)
    check("render writes an analysis summary", "## Analysis summary" in md)

# 2. Redaction: nested secrets in parameters and in results never render.
with tempfile.TemporaryDirectory() as tmp:
    export = Path(tmp) / "run-export.json"
    events = [
        {"type": "TOOL_REQUESTED", "payload": {
            "tool": "sandbox.read", "request_id": "req-9",
            "parameters": {"path": "sources/x.md",
                           "options": {"api_key": SECRET,
                                       "nested": [{"password": SECRET}]}}}},
        {"type": "TOOL_OUTCOME", "payload": {
            "outcome": "result",
            "result": {"content": "ok", "meta": {"token": SECRET}}}},
    ]
    export.write_text(json.dumps({"events": events}))
    out = Path(tmp) / "readout.md"
    proc = run_tool("render", str(export), "-o", str(out))
    md = out.read_text() if out.exists() else ""
    check("redaction: secret value appears nowhere in the transcript",
          proc.returncode == 0 and SECRET not in md)
    check("redaction: [redacted] marks both arguments and results",
          md.count("[redacted]") >= 2)
    check("redaction: non-secret parameters still summarised",
          "sources/x.md" in md)

# 3. Watch: termination finalises; malformed line is visible and counted.
with tempfile.TemporaryDirectory() as tmp:
    stream = Path(tmp) / "events.jsonl"
    lines = [json.dumps(e) for e in EVENTS]
    lines.insert(3, "{this is not json")
    stream.write_text("\n".join(lines) + "\n")
    out = Path(tmp) / "watch.md"
    proc = run_tool("watch", str(stream), "-o", str(out), "--idle-seconds", "2")
    md = out.read_text() if out.exists() else ""
    check("watch exits 0 on termination", proc.returncode == 0, proc.stderr[-200:])
    check("watch keeps the full provider call ID", FULL_ID in md)
    check("watch surfaces the malformed line visibly",
          "readout problem" in md and "malformed line 4" in md)
    check("watch finalises: fence closed + summary + ending",
          md.count("```") >= 2 and "## Analysis summary" in md
          and "run terminated in the record" in md)
    check("watch counts the malformed line in the summary",
          "readout_problem:malformed_line: 1" in md)

# 4. Watch: idle does NOT finalise; the producer's close line does.
with tempfile.TemporaryDirectory() as tmp:
    stream = Path(tmp) / "events.jsonl"
    stream.write_text(json.dumps(EVENTS[0]) + "\n")
    out = Path(tmp) / "watch.md"
    proc = subprocess.Popen(
        [sys.executable, str(TOOL), "watch", str(stream), "-o", str(out),
         "--idle-seconds", "1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(3)
    still_running = proc.poll() is None
    md_idle = out.read_text() if out.exists() else ""
    check("watch stays open through idle silence (no false finalisation)",
          still_running and "## Analysis summary" not in md_idle
          and "still watching" in md_idle)
    with stream.open("a") as fh:
        fh.write(json.dumps({"type": "READOUT_STREAM_CLOSED"}) + "\n")
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    md = out.read_text() if out.exists() else ""
    check("watch finalises on the producer's explicit close line",
          proc.returncode == 0 and "producer closed the stream" in md
          and "## Analysis summary" in md)

print(f"\nTERMINAL READOUT TESTS: {executed - len(failures)} passed, "
      f"{len(failures)} failed, of {executed} executed")
sys.exit(1 if failures else 0)
