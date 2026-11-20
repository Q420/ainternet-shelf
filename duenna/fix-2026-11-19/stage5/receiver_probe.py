"""Duenna Stage 5 — the recovery probe: a standalone receiver
process, used by the tests to prove recognition AFTER AN
ACTUAL PROCESS RESTART (his Test 5, the plan's load-bearing
requirement).

The probe is a complete, separate program. It is launched by
the recovery tests as a subprocess (``sys.executable
receiver_probe.py <spec.json>``) and it knows NOTHING except
what it is handed on its command line and what it reads from
the durable artefacts:

- argv: the path of a JSON spec file naming the record path,
  the effect-store directory, the action (``present`` or
  ``state``), and the operation's (run, step, slot, payload) —
  the operation is REBUILT through the pure constructor
  (operations.build_operation) inside this process, exactly as
  a restarted driver's retry would rebuild its inputs (P3).

- the record file and the effect-store directory on disk.

No environment variable, pipe, or shared memory carries any
state from the presenting process: if recognition works here,
it works because the receiver's idempotency record persisted
with the record and the effect store, not because any process
remembered anything (K4: "held only in the process that
crashed, it solves nothing").

Output: one JSON object on stdout — the presentation result
or recorded state, or a refusal/divergence report — and exit
code 0 for every governed outcome (a refusal is an outcome,
not a crash of the probe). An unexpected exception escapes
and the exit code is non-zero, which the tests treat as a
failure of the probe, never as an outcome.
"""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "..", "stage1"))
sys.path.insert(0, os.path.join(_HERE, "..", "stage3"))

from record import EventRecord  # noqa: E402

from operations import build_operation  # noqa: E402
from receiver import (InsertionDivergence, InsertionRefused,  # noqa: E402
                      Receiver)


def main(argv) -> int:
    with open(argv[1], "r", encoding="utf-8") as f:
        spec = json.load(f)
    record = EventRecord(spec["record_path"])
    receiver = Receiver(record, spec["effects_dir"])
    operation = build_operation(spec["run"], spec["step"],
                                spec["slot"], spec["payload"])
    try:
        if spec["action"] == "present":
            result = receiver.present(operation)
        elif spec["action"] == "state":
            result = receiver.state_of(operation.operation_id)
        else:
            raise ValueError(f"unknown action: {spec['action']!r}")
    except InsertionRefused as exc:
        result = {"outcome": "REFUSED",
                  "operation_id": exc.operation_id,
                  "details": exc.details}
    except InsertionDivergence as exc:
        result = {"outcome": "DIVERGENCE",
                  "operation_id": exc.operation_id,
                  "details": exc.details}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
