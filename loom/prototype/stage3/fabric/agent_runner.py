"""Agent runner — the agent-side executable for the boundary runtime.

Runs INSIDE the agent OS context (as the loomagent identity). It is
copied, together with client.py, into the runtime's agent home at
setup; it imports nothing from the fabric package and holds nothing
but the data-socket path it is given.

Protocol: reads ONE JSON request from stdin —
  {"sock": <data socket path>, "op": <client method>, "token": ...,
   "args": {...}}
— performs it through FabricClient, and prints ONE JSON line:
  {"ok": true, "result": ...} or {"ok": false, "kind": ..., "error": ...}
The orchestrator (driver/tests) spawns it via runuser per call, so
every agent operation in the corrections tests is performed by a
genuine agent-identity process.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client import ClientRefusal, FabricClient  # noqa: E402

_OPS = ("view_pattern", "consult_index", "open_region", "submit",
        "read_breadth", "examine", "assess", "claim_completion")


def main() -> int:
    req = json.loads(sys.stdin.read())
    op = req["op"]
    if op not in _OPS:
        print(json.dumps({"ok": False, "kind": "unknown_op",
                          "error": f"runner has no operation {op}"}))
        return 0
    client = FabricClient(req["sock"])
    try:
        method = getattr(client, op)
        result = method(req["token"], **req.get("args", {}))
        print(json.dumps({"ok": True, "result": result}))
    except ClientRefusal as exc:
        print(json.dumps({"ok": False, "kind": exc.kind,
                          "error": exc.error}))
    except Exception as exc:  # transport-level failure
        print(json.dumps({"ok": False, "kind": "transport",
                          "error": f"{type(exc).__name__}: {exc}"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
