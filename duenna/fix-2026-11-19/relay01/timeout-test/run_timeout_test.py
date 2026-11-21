#!/usr/bin/env python3
"""Reproducible exercise of relay_call.py's outer-timeout recording branch.

Method: import the exhibited caller file unmodified, replace the
subprocess.run it calls with a stub that raises
subprocess.TimeoutExpired carrying partial stdout/stderr (exactly what
a real outer-ceiling kill delivers), run the caller's main() for one
invocation, then verify the record it wrote: outer_timeout true,
helper_exit_code null, partial bytes preserved with matching hashes,
caller exit code 1.

Usage: python3 run_timeout_test.py <caller_path> <out_dir>
The caller's own pin checks run against the real helpers beside it,
so <caller_path> must be the exhibits/relay_call.py in place.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys


def main():
    caller_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    user_file = os.path.join(out_dir, "user.txt")
    with open(user_file, "w") as f:
        f.write("Reply with exactly: OK\n")

    spec = importlib.util.spec_from_file_location("relay_call", caller_path)
    rc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rc)

    partial_out = b'{"partial": '
    partial_err = b"helper was mid-read"

    def fake_run(*a, **k):
        raise subprocess.TimeoutExpired(cmd=a[0], timeout=k.get("timeout"),
                                        output=partial_out, stderr=partial_err)

    orig_run = rc.subprocess.run
    rc.subprocess.run = fake_run
    sys.argv = ["relay_call.py", "--provider", "nvidia",
                "--model", "moonshotai/kimi-k3.1-pro",
                "--out", out_dir, "--label", "outer-timeout-branch",
                "--max-tokens", "64", "--user", user_file]
    try:
        code = rc.main()
    except SystemExit as e:
        code = e.code
    finally:
        rc.subprocess.run = orig_run

    rec = json.load(open(os.path.join(out_dir,
                                      "outer-timeout-branch.record.json")))
    checks = {
        "caller_exit_code_is_1": code == 1,
        "outer_timeout_true": rec["outer_timeout"] is True,
        "helper_exit_code_null": rec["helper_exit_code"] is None,
        "partial_response_preserved":
            open(os.path.join(out_dir,
                              "outer-timeout-branch.resp.json"),
                 "rb").read() == partial_out,
        "partial_stderr_preserved":
            open(os.path.join(out_dir,
                              "outer-timeout-branch.stderr.txt"),
                 "rb").read() == partial_err,
        "response_hash_matches":
            rec["response_sha256"] ==
            hashlib.sha256(partial_out).hexdigest(),
        "stderr_hash_matches":
            rec["stderr_sha256"] ==
            hashlib.sha256(partial_err).hexdigest(),
        "caller_identity_bound":
            rec["caller_sha256"] ==
            hashlib.sha256(open(caller_path, "rb").read()).hexdigest(),
    }
    print(json.dumps(checks, indent=1))
    print("TEST RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
