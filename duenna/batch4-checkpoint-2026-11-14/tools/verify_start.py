#!/usr/bin/env python3
"""Independent START-receipt verification (C4-10 discharge):
recompute every value in a START receipt from the record
file's own bytes — genesis = the RUN_STARTED event's
prev_event_sha256, checked against sha256(JCS(pin block));
run_started_event_sha256 checked by recomputing the event
hash; pinned_input_block_sha256 = sha256(JCS(payload)).
Usage: verify_start.py <record.jsonl> <start-receipt.json>
Exit 0 iff every receipt value matches the recomputation."""
import hashlib
import json
import sys

sys.path.insert(0, "/home/hatch/workspace/ssh-door/batch4/build")
import pilot_jcs  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    record_path, receipt_path = sys.argv[1], sys.argv[2]
    events = [json.loads(line)
              for line in open(record_path, encoding="utf-8")
              if line.strip()]
    first = events[0]
    assert first["event_type"] == "RUN_STARTED", "first event not RUN_STARTED"
    receipt = json.load(open(receipt_path, encoding="utf-8"))
    body = {k: v for k, v in first.items() if k != "event_sha256"}
    checks = {
        "genesis_is_prev_of_first_event":
            receipt["genesis_sha256"] == first["prev_event_sha256"],
        "genesis_recomputed_from_pin_block":
            receipt["genesis_sha256"] == sha(
                pilot_jcs.canonicalise(first["payload"])),
        "pinned_input_block_sha256_recomputed":
            receipt["pinned_input_block_sha256"] == sha(
                pilot_jcs.canonicalise(first["payload"])),
        "run_started_event_sha256_recomputed":
            receipt["run_started_event_sha256"] == sha(
                pilot_jcs.canonicalise(body)),
        "run_started_event_sha256_is_in_file":
            receipt["run_started_event_sha256"] == first["event_sha256"],
    }
    print(json.dumps({"record": record_path, "receipt": receipt_path,
                      "checks": checks,
                      "pin_block_payload": first["payload"]},
                     indent=1))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
