# EXAMINER-INTERFACE-01 — pilot_examiner.py operator interface

Pinned at C6-4 (Batch 6). The examiner is a single-file Python 3 module +
CLI. It shares no code with the driver, adapter, or supervisor beyond the
pinned pilot_jcs.py (RFC 8785) and the pinned tool artefacts it invokes as
inputs for Step 3 re-execution (build/tools/, hashes in the checkpoint
manifest).

## Commands

- `step0 --record F --receipts-dir D --issuance F`
  Step 0 anchor & issuance verification. Exit 0 with a JSON verdict on
  success; exit 3 with {"step0": "CUSTODY-FAILURE", "reason": …} when the
  record's custody fails; exit 1 on examiner error.
- `step1 --record F` — Step 1 chain integrity; prints
  {walked, divergence}.
- `step2 --record F [--authority F …] [--freeze-manifest F …]
  [--snapshot DIR]` — Step 2 input identity; prints the classification
  (STUB or PILOT), pins checked, and findings.
- `examine --record F --receipts-dir D --issuance F [options]` — the full
  examination, Steps 0–6, as one JSON verdict. Options: --authority,
  --freeze-manifest, --snapshot (enables Steps 3–4 with --tools-dir,
  --data-dir, --rules), --captures-dir + --config (Step 5 file captures),
  --trees (Step 6). Exit 0 = examination completed (divergences and
  findings are data inside the verdict, not process failures); exit 3 =
  custody failure (no further step runs); exit 1 = examiner error.

## Rules of the house

- The examiner writes only to its own scratch (Step 3's replay record,
  created in a temporary directory). It never writes into a run's record,
  receipts, captures, or commitments.
- A custody failure at Step 0 ends the examination: nothing downstream of
  a broken anchor is examined.
- Divergences localise to the first divergent event (seq) wherever the
  step's semantics allow.
