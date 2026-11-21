# Stage 6 Battery — Actions Dress Rehearsal Package (2026-11-17)

Assembled by the orchestrator under the owner's go (2026-11-17
06:23 MST) for the examiner's further venue check (disposition
@ 77c1018): repeat the 13-instance no-live dress rehearsal on
GitHub Actions under the production supervisor, launcher and
harness. The subject is the scripted stub; no live model is
called and no external request is made.

## The stack — verified against the run of record

rehearsal/stack/ is the restoration stack (work, data,
snapshot; 18 files), byte-identical to the stack the accepted
laptop rehearsal G4CORR-20261117-001 ran under: every
configuration hash in that run's RUN_STARTED event matches the
file assembled here, including stub_script.json
ee94e02d496d1defe7b1a287f1a838221f9fdcf8e352b365a04a2cd6ba37a5a6.
Note for the examiner: that stub_script differs from the G4
examination manifest pin (ee8bfa6e…) in its "calls" entry only —
the Step 2 FR-B restoration post-dates the examination
manifest, and the run-of-record pin above is the rehearsal's
own record.

## The chain

- rehearsal/g4corr_harness.py —
  6516961739624870d640cb5e1fef5d496c1018e8ee40c7f3080fc8d3154b7ae1
  (the G4 correction harness; matches the correction bundle
  manifest).
- rehearsal/pilot_supervisor.py —
  c8a11370d06af5755d1cfa9af62d01065f7b95f926c1bb351bad9466b7dfb5a2
  (the Batch 6 checkpoint package's supervisor — the only
  supervisor copy held locally).
- rehearsal/launcher-c3.c —
  001543f39b4d557f1bd157209a316c38104d4f7f37a42b6fab8ad664894de0de
  (the checkpoint package's launcher source, compiled in the
  workflow with the staging build line: -O2 -DPILOT_TEST_HOOKS,
  HARNESS_PATH set to the room's harness, identity header from
  the generator below). Disclosed seam: the laptop staging
  compiled a file named launcher-build.c; its byte-equivalence
  to this source is NOT verified — the source used here is the
  checkpoint package of record and accepts the staging build
  line and identity contract exactly.
- rehearsal/gen_identity_records.sh —
  deeec851d363cc8a787436719a71eba5b7dcbcfde0c4d6cd953addfb40a9c7fb
  (identical in the Batch 4 and corrected trees).
- rehearsal/g2_run.py —
  39c8f5025b5ae1f63e9481b599559da356d3a4b2b5b4d1557e984b19c4cf2aea
  (the room runner: drops to pilot-supervisor and execs the
  supervisor against the room).
- rehearsal/write_identity_records.py and
  rehearsal/summarise_run.py are new glue written for this
  venue: the first is the staging identity-records writer
  verbatim in behaviour; the second summarises the finished
  run (event counts, record sha256) for the results commit.

## The workflow

battery-rehearsal.yml (placed at .github/workflows/ in
Q420/Battery): fail-closed custody probe; room built at
/srv/nemotron-pilot/batch6-g2 with the pilot-supervisor and
pilot-harness system users, the launcher compiled and set
root:pilot-supervisor 4710, identity records regenerated for
the installed harness and interpreter; one rehearsal run
fired under a G4CORR run ID (a fresh runner room starts its
own sequence at 001 — the venue is labelled in every result);
the run directory, receipts, stdio log, room stack hashes and
a summary are committed back to the repo under
rehearsal-results/.

Comparison target (laptop rehearsal G4CORR-20261117-001):
483 events, 13 TREE_CLOSED, RUN_CLOSED present.
