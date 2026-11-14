# BATCH 3 CORRECTION ROUND 2 — CHUNK SHEET (2026-11-13)

Drafted from the approved round-2 plan (b156816a + Revs 2–4,
approval 54dea7ee) before the build. Each chunk names its plan
locus, the artefact it lands in, and the check that discharges it.
The round-2 checkpoint report discharges this sheet line by line.

## Authority and bootstrap (plan Item 1 + Rev 2 R1/R2 + Rev 3 R2 + Rev 4)

- **CC2-1 — Acyclic anchor.** Authority inventories consumed inputs
  ONLY (no driver, no suite). Driver embeds
  EXPECTED_AUTHORITY_SHA256; continuation pins authority + driver +
  suite + runner hashes. *Check:* construction order in
  gen_authority.py + continuation; N4 refusal.
- **CC2-2 — Root derivation + load order.** Root from the driver
  file's location; mismatched caller pilot_root refuses
  (PILOT_ROOT_MISMATCH); constructor loads nothing; preflight
  verifies then loads. *Check:* N3 refusal; retained runs pass.
- **CC2-3 — Path binding.** Every consumed path resolved from the
  authority; differing caller data_dir/trees_path/snapshot_dir
  refuses PATH_NOT_AUTHORITY before any load or run directory.
  *Check:* N1, N2 refusals with no run dir.
- **CC2-4 — Bootstrap loading.** Stdlib-only module scope; pinned
  modules loaded post-preflight by importlib file-location from
  exact verified paths, dependency order; any pre-existing
  pinned-name sys.modules entry refuses PROCESS_MODULE_PRELOADED.
  *Check:* P3 refusal; P1 provenance paths.
- **CC2-5 — Binding contract.** Seven symbols bound from the
  bootstrap's dependencies object into driver attributes
  (RunRecord, canonical, sha256_hex, materialise_ledger,
  CorpusSource, PilotTools, StubSubject); all call sites through
  the bound attributes; dynamic import at old line 317 removed.
  *Check:* greppable invariants asserted in the suite; P2 identity
  results (incl. materialise_ledger, tools' extract, record's JCS).
- **CC2-6 — Subject boundary.** Runner passes data only (script
  authority name + configuration name); the driver instantiates
  the subject post-bootstrap from the bound StubSubject.
  *Check:* P2 subject-class identity result.
- **CC2-7 — Subprocess scenarios + provenance.** Every driver run
  executes in a fresh interpreter via the scenario runner, which
  writes a bootstrap provenance report per run. *Check:* reports
  present for all seven runs; P1/P2 asserted from them; P4
  poisoned-copy run unaffected.
- **CC2-8 — INTEGRITY-FIXTURE-01.** Authority variant entry minted
  by deterministic reproduction (canonical snapshot + the declared
  two-byte sections mutation); canonical verified first, fixture
  verified against the variant, bound by name only, variant
  identity + hash in RUN_STARTED test_configuration. *Check:* the
  INTEGRITY run stops on the mismatch with the variant recorded.

## Record and test depth (plan Items 2–4)

- **CC2-9 — T06 outcomes in the record.** Each T06 procedure step
  emits its accumulated outcomes map as a STEP_PROGRESS payload.
  *Check:* (p) T06-E recompute passes from cited events.
- **CC2-10 — Exhaustive (p).** Explicit dispatch table; fall-through
  is a failure; recompute over all seven records; per-record
  coverage assertion (MODEL triggered == recomputed). *Check:*
  coverage lines per record; no skip anywhere in the code path.
- **CC2-11 — Schema over all records (n).** schema assertions over
  every event of all seven records, one line per record, adding
  run_id-string and recorded_at_utc ISO-8601/UTC assertions;
  sequence check extended to every record. *Check:* seven schema
  lines + seven sequence lines.
- **CC2-12 — §6.4 matrix (q).** Q1–Q8 as separate named assertions
  on the RUN-STOP record; retained miniature elements on the LANE
  and INTEGRITY stops. *Check:* Q1–Q8 lines in the transcript.

## Standing rules

- **CC2-13 — Retained acceptance.** Round-1 checks (a)–(s) retained
  except where CC2-9..12 extend them; Batch 2 regression battery
  re-run against the untouched corrected tools (§4(j) with the
  declared T1/T2 translation, distinction preserved). *Check:*
  regression result line in the round-2 transcript/report.
- **CC2-14 — Bundle completeness.** Report + artefacts + authority
  + continuation + suite + runner + generator + transcript + all
  seven records WITH ledgers AND provenance reports shelved at
  duenna/batch3-correction2-2026-11-13/. b3cc629d untouched.
  *Check:* bundle listing in the report.
