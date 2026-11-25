#!/usr/bin/env python3
"""The gate 4 rehearsal's stub helper: stands in for the
NVIDIA connector helper at its own seam. Invoked exactly as
the real helper is — [python, helper, "chat"|"chat-raw-
bounded", model], the request JSON on stdin — it records the
exact request bytes to the captures file (hop 3's evidence),
performs any scripted room action, and answers from the
script: the provider JSON itself for "chat"; for
"chat-raw-bounded", the bounded envelope the real helper
frames, wrapping the same provider JSON. No network, no
credential, no provider."""
import base64
import hashlib
import json
import os
import sys

FORGED_REAPER = (
    "# forged reaper - gate 4 rehearsal tamper\n"
    "# (never executed: the room's rig-integrity "
    "precondition refuses first)\n")


def main():
    mode = sys.argv[1]
    model = sys.argv[2]
    body = sys.stdin.buffer.read()
    with open(os.environ["GATE4_STUB_SCRIPT"],
              encoding="utf-8") as fh:
        script = json.load(fh)
    state_path = os.environ["GATE4_STUB_STATE"]
    try:
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        state = {}
    index = int(state.get(mode, 0))
    state[mode] = index + 1
    with open(state_path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    with open(os.environ["GATE4_STUB_CAPTURES"], "a",
              encoding="utf-8") as fh:
        fh.write(json.dumps({
            "mode": mode, "model": model, "index": index,
            "request_sha256": hashlib.sha256(body).hexdigest(),
            "request_bytes": len(body),
            "request_b64": base64.b64encode(body).decode(
                "ascii")}) + "\n")
    steps = script.get(mode) or []
    if index >= len(steps):
        sys.stderr.write(
            f"gate4 stub: script exhausted for mode {mode} "
            f"at index {index}\n")
        return 3
    step = steps[index]
    action = step.get("action")
    if action in ("tamper_reaper", "restore_reaper"):
        target = os.path.join(os.environ["GATE4_ROOM_TREE"],
                              "rig", "reaper.py")
        if action == "tamper_reaper":
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(FORGED_REAPER)
        else:
            with open(os.environ["GATE4_REAPER_BACKUP"],
                      "rb") as fh:
                genuine = fh.read()
            with open(target, "wb") as fh:
                fh.write(genuine)
    payload = json.dumps(step["respond"]).encode("utf-8")
    if mode == "chat-raw-bounded":
        envelope = {
            "phase": "response_received", "status": 200,
            "body_b64": base64.b64encode(payload).decode(
                "ascii"),
            "body_complete": True, "stop_reason": "eof",
            "error_kind": None, "read_error_kind": None}
        sys.stdout.write(json.dumps(envelope))
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
