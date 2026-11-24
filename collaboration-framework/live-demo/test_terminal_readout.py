#!/usr/bin/env python3
"""Focused verification for terminal_readout.py (Vane's correction round,
INDEX 441): full call IDs, argument summaries, live-watch finalisation,
malformed-line visibility, end-of-stream without a termination event.
Run: python3 live-demo/test_terminal_readout.py — exits non-zero on failure.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TOOL = HERE / "terminal_readout.py"
NATIVE1 = HERE / "first-worker-native1"
FULL_ID = "fc_5f4344e5-2273-4f7f-89b9-d4173ee6c42a"
failures = []


def check(name, condition, detail=""):
    print(("PASS " if condition else "FAIL ") + name + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


def run_tool(*argv):
    return subprocess.run([sys.executable, str(TOOL), *argv],
                          capture_output=True, text=True, timeout=60)


# 1. Render: full IDs, argument summary, stall, summary.
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

# 2. Watch: termination event finalises; malformed line is visible.
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

# 3. Watch: end-of-stream without a termination event still finalises.
with tempfile.TemporaryDirectory() as tmp:
    stream = Path(tmp) / "events.jsonl"
    stream.write_text(json.dumps(EVENTS[0]) + "\n")
    out = Path(tmp) / "watch.md"
    proc = run_tool("watch", str(stream), "-o", str(out), "--idle-seconds", "1")
    md = out.read_text() if out.exists() else ""
    check("watch finalises at end-of-stream without a termination event",
          proc.returncode == 0 and "no termination event" in md
          and "## Analysis summary" in md)

print(f"\nTERMINAL READOUT TESTS: {6 + 5 + 1 - len(failures)} passed, "
      f"{len(failures)} failed")
sys.exit(1 if failures else 0)
