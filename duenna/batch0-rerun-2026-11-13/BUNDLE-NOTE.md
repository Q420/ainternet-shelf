# BATCH 0 RE-RUN — EVIDENCE BUNDLE NOTE

**What this is:** the complete evidence of the Batch 0 re-run of
the Stage 5 build (Spec Rev 13 at pin bab720b2, §4), executed
2026-11-13 in the Ubuntu room on Ben's laptop — the environment
Alex accepted for this re-run in pb-mwep7new.

**Verdict: BATCH 0 RE-RUN — PASSED** (see the checkpoint report).
F-1 and F-3, the findings that stopped the original Batch 0 run
on Remmy's VM, are resolved in this environment by re-execution.
The original NOT PASSED checkpoint stands as history.

## Contents

- `BATCH0-RERUN-CHECKPOINT-REPORT-2026-11-13.md` — the
  checkpoint report: verdict and item-by-item state.
- `BATCH0-RERUN-TRANSCRIPT.log` — the complete run transcript
  (Steps 1–10), as streamed live to `/home/ben/batch0-rerun.log`
  in the room. **The in-room log was fetched back after the run
  and is byte-identical to this file: 9,715 bytes, sha256
  `6da814297fd5347e5afb0e50518747c3fd1ff2c68f29da5479629192015e35df`
  (both copies computed).** What Ben watched is what is shelved.
- `batch0-rerun.sh` — the runner script that produced the
  transcript (evidence-gathering only; the verdict is the
  report's, not the script's).
- `freeze-manifest.sha256` — the sha256 manifest the staged
  frozen artefacts were verified against in-room (28 files, all
  OK at Step 1).
- `expected-hashes.txt` — the pin values the run checked against,
  computed from the source files on the VM at staging time.
- `SHA256SUMS` — hashes of this bundle's files.

## Authority chain

- Build authorisation: Ben's Stage 5 build go, 2026-11-12 22:22
  MST ("Alex approves it, I approve it", fenced to that decision).
- Environment acceptance: Alex, pb-mwep7new, 2026-11-13, on the
  acceptance-probe bundle shelved at 844439bc.
- Re-run authorisation: Ben's go, 2026-11-13 ~00:13 MST (scope
  card tap + his words), recorded in the scope ledger.

## Standing notes

- Zero provider contact; Nemotron not called; no index written.
- The pilot accounts (pilot-supervisor uid 999, pilot-harness
  uid 997) pre-existed in the room from the acceptance probe;
  their creation record is the probe's shelved transcript. The
  build-root custody trees were established by this re-run.
- Exhibits left in place in the room: the build root
  `/srv/nemotron-pilot/` (freeze copy, runs/, commitments/ 0700,
  the compiled probe), the RFC source staging under
  /root/workspace/snapshotter/, and `/home/ben/batch0-rerun.log`.
