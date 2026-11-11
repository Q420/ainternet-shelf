# V2 BATTERY — FROZEN FOUNDATION MANIFEST

Prepared 2026-11-10 under Alex's ruling (response to
pb-20261110-battery-voided-report). Machine-readable form:
FOUNDATION.json (this directory; the runner's copy sits
beside run_v2.py and is byte-identical).

## The boundary, enforced

run_v2.py recomputes the sha256 of every component below
at startup and ABORTS on any mismatch. On a technical
failure it records the incident, writes
BATTERY-STOPPED.lock, and every later launch refuses while
the lock exists. No patching, resuming, skipping, or
carrying forward after a failure — removing the lock is
the physical trace of a new adjudication ruling.

## Components (hashes in FOUNDATION.json)

- tools24.py — Arm C tools, v2.4 (single locate fix)
- run_c.py — Arm C driver (calls the reviewed tools; the
  voided run's driver-level substitute is removed)
- run_v2.py — the runner (this enforcement included)
- run_ab.py — Arms A/B harness: frozen packs, tasks, gate
- query.py — the BM25 ranker the tools' locate uses
- PROCESS-TREES.md (v2) + PROCESS-TREES-V21.md +
  TREES-V24-AMENDMENTS.md — the process trees as amended
- DEMO24-RESULTS.json — the v2.4 fixture evidence
- corpus sections.jsonl + manifest.json — hash-listed
  without shelf copies; corpus integrity is additionally
  established by query.py verify (PASS)

Copies of every code/document component are shelved in
this directory so each hash is independently verifiable
from the shelf alone.
