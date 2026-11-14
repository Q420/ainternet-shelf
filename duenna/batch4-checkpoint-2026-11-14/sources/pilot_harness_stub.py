#!/usr/bin/python3
"""PILOT HARNESS ENTRY (Batch 4 stub) — the programme at the
launcher's compiled-in HARNESS_PATH for this batch.

Runs as pilot-harness, against the STUB subject only — no
subject call anywhere in Batch 4 (standing rule C4-D2). It
writes the run's canonical record with the Batch 3 record
writer (pilot_record, sha256 ed3f5c85...) into
runs/<run_id>/ and nothing outside the run directory.

Behaviour is keyed on the run-id battery segment:
  B4*       normal stub run: RUN_STARTED, one stub step,
            RUN_CLOSED, ledger.json materialised; exit 0.
  B4CRASH*  RUN_STARTED + one step event flushed, then the
            process kills itself with SIGKILL: termination
            with no terminal event (CRASH issuance path).
  B4FALSE*  like B4, but the RUN_STARTED pin block carries a
            falsified pin (C4-10 scratch): the supervisor's
            START receipt must commit the falsified block's
            actual bytes, self-computed.
"""
import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pilot_record import RunRecord, materialise_ledger  # noqa: E402

RUNS_ROOT = os.environ.get("PILOT_RUNS_ROOT", "/srv/nemotron-pilot/runs")

STUB_PINS = [
    {"path": "stub/subject.json",
     "sha256": "0000000000000000000000000000000000000000000000000000000000000001"},
    {"path": "stub/trees.json",
     "sha256": "0000000000000000000000000000000000000000000000000000000000000002"},
]


def utc_now():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


COMMITMENTS = os.path.join(os.path.dirname(RUNS_ROOT.rstrip("/")),
                           "commitments")
LAUNCHER_PATH = "/srv/nemotron-pilot/launcher"


def _errno_name(exc):
    import errno as _e
    return _e.errorcode.get(exc.errno, str(exc.errno))


def variant_vault(run_dir):
    """SE-7 (i) from inside the harness boundary: create,
    overwrite, delete, append against the commitments store
    must ALL fail at the OS boundary."""
    import glob
    import json
    results = []
    targets = sorted(glob.glob(os.path.join(COMMITMENTS, "*.start.json")))
    # the commitments directory is not listable from inside
    # this boundary (that is itself the custody property), so
    # fall back to a receipt name known to exist there
    receipt = targets[0] if targets else os.path.join(
        COMMITMENTS, "B4SMOKE-20261114-001.start.json")
    attempts = [
        ("create", os.path.join(COMMITMENTS, "probe-vault.tmp"), "w"),
        ("overwrite", receipt, "r+b"),
        ("append_issuance", os.path.join(COMMITMENTS,
                                         "issuance-record.jsonl"), "a"),
    ]
    for op, path, mode in attempts:
        try:
            with open(path, mode) as fh:
                fh.write(b"x")
            results.append({"op": op, "target": path,
                            "result": "SUCCEEDED — CUSTODY FAILURE"})
        except OSError as exc:
            results.append({"op": op, "target": path,
                            "result": _errno_name(exc)})
    try:
        os.unlink(receipt)
        results.append({"op": "delete", "target": receipt,
                        "result": "SUCCEEDED — CUSTODY FAILURE"})
    except OSError as exc:
        results.append({"op": "delete", "target": receipt,
                        "result": _errno_name(exc)})
    with open(os.path.join(run_dir, "artefacts",
                           "vault-attempts.json"), "w") as fh:
        json.dump(results, fh, indent=1)


def variant_fds(run_dir):
    """SE-7 (vi): enumerate retained descriptors first
    (targets + access modes), then probe writes on every
    descriptor number above the allowlist."""
    import fcntl
    import json
    fds = {}
    for name in os.listdir("/proc/self/fd"):
        fd = int(name)
        try:
            target = os.readlink(f"/proc/self/fd/{fd}")
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        except OSError as exc:
            # the enumeration's own descriptor is already
            # closed by the time it is examined
            fds[fd] = {"error": _errno_name(exc)}
            continue
        fds[fd] = {"target": target,
                   "accmode": fl & os.O_ACCMODE,
                   "append": bool(fl & os.O_APPEND)}
    probes = {}
    for fd in range(3, 17):
        try:
            os.write(fd, b"x")
            probes[fd] = "WRITABLE — ISOLATION FAILURE"
        except OSError as exc:
            probes[fd] = _errno_name(exc)
    with open(os.path.join(run_dir, "artefacts", "fds.json"),
              "w") as fh:
        json.dump({"retained": fds, "write_probes": probes},
                  fh, indent=1)


def variant_invoke(run_dir):
    """SE-7 (v) mid-run: the harness attempts to invoke the
    launcher to spawn a second process; the OS boundary
    must refuse."""
    import json
    import subprocess
    try:
        proc = subprocess.run(
            [LAUNCHER_PATH, "B4INVOKE-20261114-999"],
            capture_output=True, timeout=10)
        result = {"result": "EXECUTED — SEPARATION FAILURE",
                  "returncode": proc.returncode}
    except OSError as exc:
        result = {"result": _errno_name(exc)}
    with open(os.path.join(run_dir, "artefacts",
                           "invoke-attempt.json"), "w") as fh:
        json.dump(result, fh, indent=1)


def main():
    run_id = sys.argv[1]
    battery = run_id.split("-")[0]
    run_dir = os.path.join(RUNS_ROOT, run_id)
    os.makedirs(os.path.join(run_dir, "captures"), exist_ok=True)
    os.makedirs(os.path.join(run_dir, "artefacts"), exist_ok=True)
    pins = [dict(p) for p in STUB_PINS]
    if battery.startswith("B4FALSE"):
        pins[0] = {"path": "stub/subject.json",
                   "sha256": "ffffffffffffffffffffffffffffffff"
                             "ffffffffffffffffffffffffffffffff"}
    block = {"pins": pins, "stub": True,
             "subject": "STUB (no subject call, C4-D2)"}
    if battery.startswith("B4FDS"):
        # enumerate BEFORE the record file is opened: what
        # is retained at this point is exactly the inherited
        # set the exec left us
        variant_fds(run_dir)
    record = RunRecord(os.path.join(run_dir, "run-record.jsonl"),
                       run_id, block)
    record.emit("RUN_STARTED", block, recorded_at_utc=utc_now())
    if battery.startswith("B4VAULT"):
        variant_vault(run_dir)
    elif battery.startswith("B4INVOKE"):
        variant_invoke(run_dir)
    record.emit("STEP_TRIGGERED", {"step": "stub-step"},
                tree_id="stub-tree", step_id="stub-step",
                recorded_at_utc=utc_now())
    if battery.startswith("B4CRASH"):
        record.close()
        os.kill(os.getpid(), signal.SIGKILL)
        os._exit(137)
    record.emit("STEP_SATISFIED", {"step": "stub-step"},
                tree_id="stub-tree", step_id="stub-step",
                recorded_at_utc=utc_now())
    head = record.prev
    record.emit("RUN_CLOSED",
                {"tree_closures": {"stub-tree": "CLOSED"},
                 "event_count": record.seq + 1,
                 "record_sha256": head},
                recorded_at_utc=utc_now())
    record.close()
    with open(os.path.join(run_dir, "ledger.json"), "wb") as fh:
        fh.write(materialise_ledger(
            os.path.join(run_dir, "run-record.jsonl")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
