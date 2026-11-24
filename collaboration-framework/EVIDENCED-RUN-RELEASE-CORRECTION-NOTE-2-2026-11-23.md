# Evidenced run — release correction note 2: phase-2 staged-file verification (2026-11-23)

Answering the release examination round 2 (INDEX 324). Recorded at INDEX 325. **Remmy verified first-hand:** the new helper stands in the harness with both call sites, and the extended witness suite re-run and counted — **23 checks, ALL PASS**.

## The correction

A new helper, `_staged_source_problem(manifest, sandbox)` (first_worker_run.py:462), walks every manifest entry, resolves the file under the given sandbox, and returns a problem string naming the offending file — `staged <path> is missing from the sandbox` or `staged <path> no longer hashes to the manifest` — or `None`. In `run_probe_phase2()` it is called **immediately after the manifest-identity check and before the adapter is built**, giving the ordering: receipt validation → receipt retention → manifest-hash identity → **per-file staged verification** → adapter → judgement → activation. A problem prints the harness's ABORT form to stderr and returns 1, as the receipt and manifest refusals do.

**Reuse, by extraction.** The fresh path's per-file check was an inline loop, not a callable; it was lifted into the helper and both call sites now use it — one logic, two callers (fresh path :997, phase 2 :1575). Two deliberate consequences, stated in the helper's docstring: the fresh path's mismatch ABORT text is reproduced byte-for-byte; and the missing-file case is now an explicit existence test returning a named problem — `_sha256_file()` raises on a missing file, so in the fresh path a missing file was previously an unhandled crash and is now a clean refusal (in practice unreachable there, since `stage()` has just copied the files; recorded here so the behaviour change is on the record, not silent).

## The witnesses (7 new checks; suite now 23, ALL PASS)

- **Control:** the suite's existing good-path stub run stands as the control — its record carries ASSEMBLY_JUDGED and INSTANCE_ACTIVATED, which stand only past the new check.
- **Altered file:** stub phase 1 completes; one staged source (`sources/a3-pass.md`) is appended to, manifest.json untouched; phase 2 with a correct receipt refuses rc 1, stderr naming the file, **no ASSEMBLY_JUDGED, no activation**.
- **Missing file:** the same staged source deleted after phase 1; phase 2 refuses rc 1 naming the file, no judgement, no activation.

All other live-demo suites at baseline (probe receipt 13, connector 55, Groq 68, helper-raw 11, helper-bounded 17); `--verify-config` exit 0 in retrieval and probed modes. No live run of any phase was made — stub-helper runs only, in throwaway directories the suite cleans up.
