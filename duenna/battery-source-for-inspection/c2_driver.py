#!/usr/bin/env python3
"""(c2) construction-check driver — Actions venue (examiner
disposition, 2026-11-17). Runs the pinned Actions adapter
once against the loopback capture service and combines the
adapter's capture record with the server's verdict into
prep-results/c2-result.json (booleans and identifiers
only). Exits non-zero if any check fails — the check is
fail-closed. No live call is made: the adapter's base URL
is the loopback capture service, in stage5 isolation
mode, which refuses any non-loopback endpoint."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from actions_adapter import Adapter


def main():
    port = os.environ["C2_PORT"]
    secret = (os.environ.get("NVIDIA_API_KEY") or "").strip()
    if not secret:
        print("credential variable unset or empty")
        return 1
    captures = os.path.join(HERE, "c2-captures")
    adapter = Adapter(
        config_path=os.path.join(HERE,
                                 "actions-adapter-config.json"),
        captures_dir=captures,
        base_url=f"http://127.0.0.1:{port}",
        stage5_mode=True,
        instance_id="T04",
        credential_env="NVIDIA_API_KEY")
    out = adapter.complete({
        "correlation_id": "C2-CHECK-ACTIONS-20261117",
        "tree_id": "C2",
        "step_id": "C2-STEP-01",
        "messages": [{"role": "user", "content": "ping"}],
    })
    cap_path = os.path.join(captures,
                            out["capture_record_id"] + ".json")
    cap_bytes = open(cap_path, "rb").read()
    capture = json.loads(cap_bytes.decode("utf-8"))
    verdict = json.loads(
        open(os.environ["C2_SERVER_VERDICT"]).read())
    checks = {
        "endpoint_was_loopback_capture":
            capture["endpoint"].startswith("http://127.0.0.1:")
            and capture["endpoint"].endswith("/chat/completions"),
        "request_reached_capture_endpoint":
            verdict["endpoint_path"].endswith("/chat/completions"),
        "authorization_present": verdict["authorization_present"],
        "scheme_bearer": verdict["scheme_bearer"],
        "value_matched_injected_secret":
            verdict["value_matched_injected_secret"],
        "adapter_recorded_authorization_attached":
            capture["authorization_attached"] is True,
        "transport_outcome_response_received":
            capture["transport_outcome"] == "RESPONSE_RECEIVED",
        "secret_absent_from_capture_record":
            secret.encode("utf-8") not in cap_bytes,
        "credential_recorded_by_server":
            verdict["credential_recorded"],
    }
    passed = all(v is True for k, v in checks.items()
                 if k != "credential_recorded_by_server") \
        and checks["credential_recorded_by_server"] is False
    result = {
        "check": "c2-adapter-construction-actions",
        "passed": passed,
        "checks": checks,
        "capture_record_id": out["capture_record_id"],
        "adapter_id": capture["adapter_id"],
        "adapter_config_sha256": capture["adapter_config_sha256"],
    }
    outdir = os.path.join(HERE, "prep-results")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "c2-result.json"), "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
