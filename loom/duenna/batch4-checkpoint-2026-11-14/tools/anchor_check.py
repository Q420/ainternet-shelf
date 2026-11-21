#!/usr/bin/env python3
"""PROTOTYPE ANCHOR CHECK — §3.5 point 9 / SE-7 (iv) shape.

Examiner step 0, prototype form (the §3.7 examiner tooling
itself is Batch 6): a receipt is evidence only if it has a
corresponding entry in the supervisor's issuance record
whose receipt_sha256 matches the receipt file's own bytes.
A receipt with no entry, or a hash mismatch, is rejected
as a custody finding — never accepted as an anchor.

Usage: anchor_check.py <commitments-dir> <receipt-file>
Exit 0 = ACCEPTED (anchored), 1 = REJECTED (custody finding).
"""
import hashlib
import json
import os
import sys


def main():
    commitments, receipt_path = sys.argv[1], sys.argv[2]
    with open(receipt_path, "rb") as fh:
        blob = fh.read()
    receipt = json.loads(blob.decode("utf-8"))
    digest = hashlib.sha256(blob).hexdigest()
    entries = []
    with open(os.path.join(commitments, "issuance-record.jsonl"),
              "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                entries.append(json.loads(line))
    match = [e for e in entries
             if e.get("run_id") == receipt.get("run_id")
             and e.get("kind") == receipt.get("kind")
             and e.get("receipt_sha256") == digest]
    verdict = {
        "receipt": receipt_path,
        "run_id": receipt.get("run_id"),
        "kind": receipt.get("kind"),
        "receipt_sha256_computed": digest,
        "issuance_entries_for_run": len(
            [e for e in entries
             if e.get("run_id") == receipt.get("run_id")]),
        "anchored": bool(match),
        "verdict": ("ACCEPTED" if match
                    else "REJECTED — custody finding: no matching "
                         "issuance entry"),
    }
    print(json.dumps(verdict, indent=1))
    return 0 if match else 1


if __name__ == "__main__":
    sys.exit(main())
