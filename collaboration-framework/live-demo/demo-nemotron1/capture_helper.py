#!/usr/bin/env python3
"""The demonstration run's capture pass-through helper.

Stands at the connector helper seam — invoked exactly
as the real helper is ([python, helper, mode, model],
the request JSON on stdin) — records the exact request
bytes to the captures file (DEMO_RUN_CAPTURES) in the
gate 4 rehearsal's record shape, then delegates to the
REAL NVIDIA connector helper (DEMO_RUN_DELEGATE_HELPER)
with the same arguments and bytes, the environment
inherited whole, stdout and stderr inherited untouched,
and exits with the delegate's exit code. A pure
pass-through: it alters nothing it carries. If the
capture cannot be written the delegate is never invoked
— no unwitnessed transmitted request."""
import base64
import hashlib
import json
import os
import subprocess
import sys


def main():
    mode = sys.argv[1]
    model = sys.argv[2]
    body = sys.stdin.buffer.read()
    captures_path = os.environ["DEMO_RUN_CAPTURES"]
    delegate = os.environ.get(
        "DEMO_RUN_DELEGATE_HELPER") or os.path.expanduser(
        "~/workspace/custom-connectors/custom.nvidia/bin/"
        "nvidia_api.py")
    index = 0
    try:
        with open(captures_path, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    if json.loads(line).get("mode") == mode:
                        index += 1
                except ValueError:
                    continue
    except OSError:
        index = 0
    with open(captures_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "mode": mode, "model": model, "index": index,
            "request_sha256":
                hashlib.sha256(body).hexdigest(),
            "request_bytes": len(body),
            "request_b64": base64.b64encode(
                body).decode("ascii")}) + "\n")
    try:
        proc = subprocess.run(
            [sys.executable, delegate, mode, model],
            input=body)
    except OSError as exc:
        sys.stderr.write(
            f"demo capture helper: the delegate helper "
            f"could not be started: {exc}\n")
        return 3
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
