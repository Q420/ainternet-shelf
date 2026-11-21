# STAGE 6 BATTERY — ACTIONS EXECUTION PACKAGE (2026-11-17)

Status: EXECUTION ASSEMBLY, built by the orchestrator under the
owner's execution word (2026-11-17 07:38 MST: "Do it, Remmy :)"),
given after the owner's stated condition was met (three
consecutive verified dress-rehearsal passes, runs #5/#6/#7) and
after the examiner's FINAL PREPARATION ACCEPTANCE
(record/ALEX-STAGE6-BATTERY-ACTIONS-FINAL-ACCEPTANCE-2026-11-17.md
@ a28139eb).

## Assembly (all transforms asserted, diffs enumerated)

- battery/battery_harness.py — derived from the accepted
  live-subject precedent (Stage 6 smoke harness) by exact-match
  transform. Differences: stack dir follows the g4corr room
  pattern; subject = the Stage 6 battery Actions adapter,
  constructed PER INSTANCE (instance_id = tree_id) so the
  examiner's per-instance ceilings bind; base URL
  https://integrate.api.nvidia.com/v1, stage5_mode=False;
  full 13-instance subset; battery_id STAGE6BATT (matches the
  run-ID battery segment); scratch=False (a scored production
  run); runs root = the room's absolute runs path.
- Credential binding (the assembly binding the examiner's
  Route 1 note requires be explicit): the workflow injects the
  repository secret into a room credential file
  ($G2/credentials/nvidia-key, owner pilot-harness, mode 0400,
  directory 711) — the Route 1 room-file pattern. The harness
  reads it into its own process environment in memory before
  the first adapter construction (the launcher's empty-env
  exec makes an environment route impossible by design). The
  value appears in no artefact, log or capture; captures
  record authorization_attached presence only.
- battery/stack/work — the accepted stack's work files minus
  the stub subject files, plus actions_adapter.py
  (9b80c37a...) and actions-adapter-config.json (f8ecb4ee...)
  from the accepted Actions preparation package @ 07467ed2.
  data/ and snapshot/ are the accepted stack's, unchanged.
- Supervisor, launcher source, identity generator, g2_run and
  the identity-records writer are byte-identical to the
  accepted rehearsal package @ 00ada2f8.
- battery.yml — the rehearsal workflow's shape: fail-closed
  custody probe, room build (reconciled against the laptop
  room's own scripts during the rehearsal line), credential
  placement with a non-empty gate, one supervisor launch of
  STAGE6BATT-<UTC date>-001, full collection, results
  committed back. Job timeout 120 minutes.

## Local verification (no live call)
- battery_harness.py compiles; every transform asserted
  count==1 against the smoke harness source.
- The Actions adapter constructs cleanly per instance with
  the production base URL (dummy credential, construction
  only — no call).
- summarise_battery.py exercised against the smoke run of
  record: counts and usage accounting correct.

## Reporting rule (owner, 2026-11-17 07:41 MST)
The owner receives a final verdict only. Unscored /
infrastructure-failed attempts (handoff race, transport,
workflow) may be re-attempted up to 5 attempts total before
a failure verdict is reported; a completed scored run is the
verdict, pass or fail.

Pins: see the package copy in Q420/Battery (battery/) and the
run's own RUN_STARTED configuration_hashes, which pin every
stack file at firing time.
