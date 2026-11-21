"""Stage 5 — shared test support: receiver construction over a
temporary durable state, the crash-hook factory (TEST FIXTURE:
places the durable state in one of K4's specified crash
windows), effect-store inspection, and the recovery-probe
runner (an ACTUAL process restart: a subprocess whose only
knowledge is the durable artefacts and the presented
operation's spec).
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from record import EventRecord  # noqa: E402
from receiver import Receiver, SimulatedCrash  # noqa: E402

PROBE = os.path.join(os.path.dirname(__file__), "..", "receiver_probe.py")

RUN = "run-stage5"
STEP = "step-01"
PAYLOADS = {"harness_sha256": {"kind": "hash", "target": "harness"},
            "results_sha256": {"kind": "hash", "target": "results"}}


def make_receiver(tmpdir, crash_hook=None):
    """A receiver over fresh durable state in tmpdir:
    (record, receiver, record_path, effects_dir)."""
    record_path = os.path.join(tmpdir, "record.jsonl")
    effects_dir = os.path.join(tmpdir, "effects")
    record = EventRecord(record_path)
    receiver = Receiver(record, effects_dir, crash_hook=crash_hook)
    return record, receiver, record_path, effects_dir


def crash_at(point):
    """A crash hook raising SimulatedCrash at exactly one named
    point of the apply sequence (mid_effect / after_effect /
    after_applied), passing the others."""
    def hook(p):
        if p == point:
            raise SimulatedCrash(p)
    return hook


def effect_files(effects_dir):
    """The applied effects: final-named effect files only.
    Orphaned temp files (an interrupted insertion's scratch)
    are NOT effects and are listed separately by
    orphan_files()."""
    if not os.path.isdir(effects_dir):
        return []
    return sorted(n for n in os.listdir(effects_dir)
                  if n.startswith("op-") and n.endswith(".json"))


def orphan_files(effects_dir):
    if not os.path.isdir(effects_dir):
        return []
    return sorted(n for n in os.listdir(effects_dir)
                  if n.startswith(".tmp-"))


def run_probe(tmpdir, record_path, effects_dir, action, operation):
    """Run the recovery probe as a NEW PROCESS and return its
    JSON outcome. The probe rebuilds the operation from its
    (run, step, slot, payload) spec inside its own process —
    nothing is handed over except the spec and the durable
    paths."""
    spec = {"record_path": record_path,
            "effects_dir": effects_dir,
            "action": action,
            "run": operation.run_id,
            "step": operation.step_id,
            "slot": operation.slot,
            "payload": operation.payload}
    fd, spec_path = _mkstemp(tmpdir)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(spec, f)
    proc = subprocess.run([sys.executable, PROBE, spec_path],
                          capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise AssertionError(
            f"probe failed (exit {proc.returncode}): {proc.stderr}")
    return json.loads(proc.stdout)


_counter = [0]


def _mkstemp(tmpdir):
    _counter[0] += 1
    path = os.path.join(tmpdir, f"probe-spec-{_counter[0]}.json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    return fd, path
