# Stage 2 — Corrections Round 2 Notes (2026-11-21)

Built under Ben's commission (scope card widget-284602e8) from Loom
spec v0.1 Rev 9 (shelf commit d7d65c96, Gate 1 PASS), in answer to
Vane's examination of the Stage 2 corrections round (NOT ACCEPTED
at shelf commit 1019aaaf, preserved unaltered as the examined
artifact; the Stage 2 artifact at 9283b7e7 likewise preserved).
This round's changes land in the working tree as a new, separately
identifiable round. BUILD-RECORD.md was not edited; nothing was
shelved or sent.

The round closes the two blockers, both of which were about
whether the safeguards are enforced by the system itself rather
than demonstrated by the test sequence:

- **B1 — probe attestation is not an admission gate.** The service
  now enforces the attestation as a prerequisite to admission:
  no token issued and no agent operation admitted until a valid,
  successful attestation stands at seq 2, and the attestation
  handler validates the supplied result (required outcomes,
  provenance, result hash) before recording anything.
- **B2 — failure-of-failure does not survive service restart.**
  The unrecorded-failure diagnostic is now a durable stop marker:
  a fresh service restores the terminal latch from it at startup,
  before serving, and reports the run `failed_unrecorded`. The
  diagnostic-cannot-be-written case is implemented and its limit
  stated plainly (interpretation 7).

## What changed

### `fabric/service.py` — the main target

- **The admission gate (B1).** `_attested()` derives the gate
  state from the history on every consultation: RUN_OPENED at
  seq 1 and a BOUNDARY_PROBE at seq 2 whose recorded probe result
  re-validates (see below) and whose recorded `probe_result_hash`
  recomputes from the canonical result. `_admission_open()` is
  consulted by the admin `issue_token` operation (refused with an
  explicit error unless the gate holds) and by every data-socket
  operation (refused with kind `not_attested` — deliberately
  distinct from the `refusal` kind a token failure produces, so a
  gate refusal and a token refusal are distinguishable in
  evidence). Because the state is history-derived, it survives
  restarts and never merely trusts that the recording path
  validated.
- **Attestation validation (B1).** The module-level
  `attestation_problems(result)` checks: every required outcome
  present with its passing value (`direct_read_store`,
  `direct_read_ground_truth`, `alternate_path_symlink`,
  `alternate_path_traversal` = `denied`; `forged_token_open`,
  `issuance_attempt_on_data_socket` = `refused`;
  `legitimate_pattern_view`, `legitimate_region_open` = `ok`);
  the result's three summary flags true; and the provenance (the
  `twin_config` stat record) present with its six boundary
  entries. `record_probe_attestation` runs this validation BEFORE
  recording: a failed, malformed, or incomplete result is refused
  at the admin path and NOT recorded — the run remains
  unattested. If the caller supplies a `probe_result_hash`, it
  must recompute from the canonical result or the attestation is
  likewise refused unrecorded; when none is supplied the service
  computes it as before (the probe2 flow). Placement (seq 2,
  immediately after RUN_OPENED) is enforced as in round 1.
- **Latch restoration (B2).** The constructor scans the service
  failures directory before any socket serves. A diagnostic
  record of kind `unrecordable_run_failure` whose `run_id`
  matches this store's run restores the terminal latch:
  `_latched` set, the latch evidence taken from the record, and
  NO RUN_FAILED event invented — the history stays exactly as
  the failed append left it.
- **Status vocabulary (B2).** `run_status` is now one of
  `failed` (RUN_FAILED in history), `failed_unrecorded` (latched,
  whether latched in-process or restored), `unopened`,
  `unattested` (opened, no valid attestation yet), `open`
  (admission gate satisfied). The misleading round-1 combination
  (`latched_unrecorded_failure: true` with `run_status: "open"`)
  is retired. Status additionally reports `posture`, `attested`,
  `diagnostic_written` (a durable diagnostic marker exists —
  written by this process or restored from disk), and
  `diagnostic_restored` (this process's latch came from the
  startup scan).
- **Diagnostic write failure.** Fault injection is now a
  comma-separated set of named faults (round 1's single-member
  usage is unchanged). The new member `diagnostic_write` makes
  the diagnostic write raise OSError inside `_write_diagnostic`;
  the write path records the outcome in `_diagnostic_written`
  (true on success, false on failure) instead of silently
  swallowing it. The latch holds either way in-process.
- **Posture.** `LOOM_SERVICE_POSTURE` selects the service
  posture: `enforced` (default; the gate has no exceptions) or
  `probe_target` (the disposable twin's bootstrap posture —
  interpretation 1). A probe-target service's gate does not
  block, and its `record_probe_attestation` is refused outright:
  a probe target never carries an attestation. The posture is
  reported in status.

### `fabric/runtime_setup.py`

- `start_service` gains a `posture=None` parameter, passed to the
  service as `LOOM_SERVICE_POSTURE`. No other change.

### `fabric/probe2.py`

- The twin's service is started with `posture="probe_target"`,
  and the probe result gains `"service_posture": "probe_target"`
  in its provenance (so the attestation the experimental run
  records states, in its own payload, the posture of the service
  the probe ran against). The probe flow is otherwise unchanged.

### `stage2_corrections_tests.py` — setup adjustments

Three edits, each flagged again below under "Setup adjustments".
The check count is unchanged: **53**.

### `stage2_corrections_round2_tests.py` — NEW

27 checks in three phases: B1 gate negatives and the intact
success path (Phase A), B2 restart durability (Phase B), and the
diagnostic-unwritable case plus its characterised limit
(Phase C). Outputs below.

No other file changed. `engine.py`, `harness.py`, `store.py`,
`fixture.py`, `client.py`, `agent_runner.py`, `probe_agent.py`,
`probe.py`, `canonical.py` are untouched in this round. No new
event types were added, and no event payload changed shape (the
attestation payload carries the same fields; the probe result it
embeds gained the `service_posture` provenance field).

## Interpretations — recorded, not silently amended

1. **The probe bootstrap (this round's central interpretation).**
   B1's validation list and B1's gate, taken together, contain a
   strict cycle: a complete attestation result must contain
   legitimate-access outcomes, which are gathered with a token
   issued by the twin's service; issuing that token is an
   admission; admission (under the gate) requires a complete
   attestation to already stand. Exactly one admission must
   therefore precede the first attestation — no ordering of the
   existing operations escapes this. The design confines that
   one admission to the disposable twin, as an explicit startup
   posture rather than an operator's sequence: probe2 starts the
   twin's service with `LOOM_SERVICE_POSTURE=probe_target`, in
   which the gate does not block and attestation recording is
   refused, so a probe target's history is scaffolding that can
   never present itself as an attested run. The posture is
   visible in the twin service's status and recorded in the
   probe result's provenance, which the experimental run's
   attestation carries. Every service not explicitly started as
   a probe target — the experimental service above all — runs in
   the enforced posture, where the gate has no exceptions. This
   mirrors the accepted round-1 seam for fault injection
   (a startup environment variable, not a socket operation; the
   agent-facing surface did not grow). The alternative —
   dropping the legitimate-access outcomes from attestation
   validation so the twin could be attested by a tokenless
   probe — was rejected: it would weaken exactly the validation
   B1 requires.
2. **A failed attestation is refused and unrecorded** (the
   brief's stated interpretation): there is no event type for a
   refused attestation and this round adds none; the refusal is
   an admin-path response, and admission simply stays blocked
   until a valid successful attestation stands.
3. **The gate re-validates from history** rather than trusting a
   flag set at record time. A seq-2 payload whose outcomes fail
   or whose hash does not recompute does not open the gate, even
   if it was written into the store by some other path.
4. **`issue_token` is gated on attestation only, not on failure
   state.** A token issued on a failed-but-attested run is inert:
   the data dispatcher refuses on the recorded failure before
   anything else. This preserves the round-1 suite's restart
   flow, which issues a token on a failed run precisely to prove
   operations refuse. Issuance is an operator operation;
   admission of agent activity is what the gate governs.
5. **Latch restoration matches on `run_id`.** The diagnostic
   records the run it belongs to; the startup scan restores the
   latch only from a diagnostic naming this store's run. An
   unreadable file, a different kind, or a different run's
   diagnostic is not treated as this run's stop marker.
6. **Status `unattested`.** An opened run with no valid
   attestation reported `run_status: "open"` in round 1; it now
   reports `unattested`. No round-1 assertion covered that state,
   so nothing was weakened — the vocabulary is strictly more
   honest.
7. **The diagnostic-cannot-be-written limit, plainly:** with no
   durable marker there is NO durable stop. If the diagnostic
   write fails, the latch holds only in the current process; a
   fresh service on that runtime has nothing to restore, reports
   the (attested) run `open`, and admits agents again. The
   record must not pretend otherwise: in-process status reports
   `failed_unrecorded` with `diagnostic_written: false`, and the
   round-2 suite characterises the restart behaviour as an
   explicit test (Phase C, "B2 limit: ...") instead of leaving
   the limit implicit.

## Setup adjustments to the existing corrections suite

Each was required by the new enforcement; no assertion was
weakened or removed, and the suite still runs 53 checks.

1. **Phase 6 (faulttest) attests before token issuance.** An
   `attest_probe(flt, result)` call was inserted after
   `open_run`, recording the Phase 1 twin-probe result through
   the faulttest admin path (same boundary configuration).
   Reason: B1's gate refuses issuance before attestation; the
   round-1 flow issued first. This is the adjustment the round-2
   brief anticipated.
2. **Phase 6 exact-history assertion updated.** The expected
   history changed from `["RUN_OPENED", "DISCOVERY"]` to
   `["RUN_OPENED", "BOUNDARY_PROBE", "DISCOVERY"]` — the
   attestation inserted by adjustment 1 is now legitimately part
   of that history. The assertion's substance — no RUN_FAILED
   event was fabricated — is unchanged.
3. **Phase 6 status assertion updated and strengthened.** B2
   mandated retiring the `latched + run_status "open"`
   combination, so the assertion now expects
   `run_status == "failed_unrecorded"`, and additionally
   `diagnostic_written is True` (a conjunct added, none
   removed).

## Test outputs (final runs, 2026-11-21)

All five suites were run end-to-end in the order below; every
suite passes in full. The round-2 suite and the corrections suite
were additionally run repeatedly during the build with identical
results.

### `python3 stage2_corrections_round2_tests.py` — 27/27 PASS

```
PASS  B1: token issuance before the run is opened is refused  
PASS  B1 setup: the run opens (genesis)  
PASS  B1: token issuance before attestation is refused  
PASS  B1: a foreign token before attestation is refused on the gate (not_attested)  
PASS  B1: a forged token before attestation is refused on the gate (not_attested)  
PASS  B1: status reports the unattested run honestly  
PASS  B1: a failed attestation is refused and NOT recorded  
PASS  B1: issuance still refused after a failed attestation  
PASS  B1: a malformed attestation (missing outcome) is refused and NOT recorded  
PASS  B1: an incomplete attestation (no provenance) is refused and NOT recorded  
PASS  B1: a wrong result hash is refused and NOT recorded  
PASS  B1: a valid attestation is recorded at seq 2  
PASS  B1: status reports the attested, open run  
PASS  B1: a second attestation is refused (placement)  
PASS  B1: after attestation, issuance and legitimate operations succeed  
PASS  B1: region open serves genesis content after attestation  
PASS  B1: the same foreign token after attestation is refused as a token (refusal), not on the gate  
PASS  B2: the breaching submission is answered run_failed_unrecorded  
PASS  B2: in-process status is failed_unrecorded with a durable marker written  
PASS  B2: after restart the latch is restored from the diagnostic (failed_unrecorded)  
PASS  B2: after restart every agent-facing route is refused  
PASS  B2: after restart the history still holds no RUN_FAILED  
PASS  B2: with the diagnostic unwritable the breach is still answered run_failed_unrecorded  
PASS  B2: the latch holds in-process with no durable marker  
PASS  B2: status honestly shows failed_unrecorded with diagnostic_written false  
PASS  B2: no diagnostic file exists in the failures directory  
PASS  B2 limit: with no durable marker the stop does not survive restart (nothing claims otherwise)  

STAGE 2 CORRECTIONS ROUND 2 TESTS: ALL PASS
```

### `python3 stage2_corrections_tests.py` — 53/53 PASS (regression)

```
PASS  service directory is loomfab-only (700)  
PASS  ground-truth file is loomfab 600  
PASS  socket directory is traverse-only (711)  
PASS  agent home belongs to loomagent  
PASS  twin layout equals experimental layout (owners + modes)  
PASS  service code copy is byte-identical to the tree  
PASS  ground-truth file carries exactly the fixture's sealed document  
PASS  probe: direct_read_store denied by the OS  PermissionError: Permission denied
PASS  probe: direct_read_ground_truth denied by the OS  PermissionError: Permission denied
PASS  probe: alternate_path_symlink denied by the OS  PermissionError: Permission denied
PASS  probe: alternate_path_traversal denied by the OS  PermissionError: Permission denied
PASS  probe: forged token refused  
PASS  probe: issuance attempt on the data socket refused (no route)  
PASS  probe: legitimate pattern view succeeds (isolated, not disabled)  
PASS  probe: legitimate region open succeeds  
PASS  probe verdicts: reads denied, attacks refused, legitimate ok  
PASS  twin store file was loomfab 600 during the probe  
PASS  twin config matches experimental layout on shared entries  
PASS  before: experimental run unopened, zero events  
PASS  experimental run opens (genesis)  
PASS  attestation appended as seq 2  
PASS  history is exactly RUN_OPENED + BOUNDARY_PROBE  
PASS  attestation is a system event carrying the probe provenance  
PASS  attestation payload carries a plain-words summary  
PASS  probe introduced no DISCOVERY events into the history  
PASS  probe left the read record empty  
PASS  agent pattern view through the socket  
PASS  agent region open serves genesis content  
PASS  agent read breadth is 1/6 after one open  
PASS  idle through the socket returns a durable event sequence  
PASS  IDLE event is in the history, by the agent, with a summary  
PASS  second agent opens State  
PASS  breaching submission refused as run_failed  
PASS  RUN_FAILED is recorded once, as a system event  
PASS  RUN_FAILED payload carries the breach evidence  
PASS  post-breach: every agent-facing route refuses, for every agent  
PASS  service status reports the failed run  
PASS  after restart the run is still failed (state from history)  
PASS  after restart, agent operations still refuse  
PASS  replay of the experimental history yields the failed state  
PASS  experimental chain verifies end to end  
PASS  the failed run's fabric content is untouched (all regions v1)  
PASS  unrecordable failure: breach response says so  
PASS  unrecordable failure: service stays latched closed  
PASS  unrecordable failure: NO RUN_FAILED event was fabricated  
PASS  status distinguishes the unrecordable failure (latched)  
PASS  diagnostic record written to the service failures directory  
PASS  diagnostic record carries breach + append error + timestamp  
PASS  in-process idle appends a durable IDLE event  
PASS  in-process idle is replay-safe  
PASS  RUN_FAILED folds to failed state, live and on replay  
PASS  harness over a failed history refuses agent operations  
PASS  healthy genesis state carries no failure keys  

STAGE 2 CORRECTIONS TESTS: ALL PASS
```

### `python3 stage2_tests.py` — 40/40 PASS (regression)

```
PASS  wrong-token read refused  
PASS  read serves the region's content  
PASS  read recorded as a DISCOVERY event  
PASS  re-open of a read region allowed  
PASS  third distinct region read refused (breadth cap)  
PASS  read breadth is 2/6 < 0.5  
PASS  breadth allowance is per agent  
PASS  pattern serves no content  
PASS  index consultation recorded, breadth untouched  
PASS  replay equals live state after reads  
PASS  chain verifies after reads  
PASS  boundary probe: every route failed to expose sealed material  17 routes
PASS  boundary probe recorded as a BOUNDARY_PROBE event  
PASS  probe record itself carries no sealed material  
PASS  probe left the fabric untouched  
PASS  identity mismatch rejected and recorded  
PASS  schema-invalid contribution rejected (missing rationale)  
PASS  TV-2: raise_tension type structural is schema-invalid  
PASS  cross-field: write_set outside read_set is schema-invalid  
PASS  cross-field: unknown region id is schema-invalid  
PASS  cross-field: duplicate content target is schema-invalid  
PASS  discovery_ref naming another agent is schema-invalid  
PASS  discovery_ref naming no event is schema-invalid  
PASS  hard line: claiming an unmade read stops the run  
PASS  hard line: omitting a made read stops the run  
PASS  valid contribution commits; region version bumps  
PASS  replay equals live state after a commit  
PASS  overtaken contribution rejected stale, with the changed-read diff  
PASS  order: stale plant proposal rejected stale, not structural  
PASS  order: schema-invalid plant proposal rejected schema, not stale  
PASS  Annex D plant rejected structural, naming S3  
PASS  TV-7 setup: contribution X accepted  
PASS  TV-7(i): identical resubmission returns the original outcome, no new event  
PASS  TV-7(ii): different content under the same key conflicts  
PASS  add_dependency commits; both endpoint versions advance  
PASS  remove_dependency commits; both endpoint versions advance again  
PASS  raise_tension commits; semantic tension stands open  
PASS  every Stage 2 event payload carries a plain-words summary  29 events
PASS  replay equals live state at the end of Run C  
PASS  chain verifies at the end of Run C  

STAGE 2 TESTS: ALL PASS
```

### `python3 stage1_smoke.py` — 18/18 PASS (regression)

```
PASS  genesis is the only event  
PASS  genesis type RUN_OPENED  
PASS  genesis prev_hash is the constitution hash  
PASS  six regions at v1  
PASS  four genesis dependencies  
PASS  replay reproduces live state exactly  9a7250bde82bfd8b
PASS  hash chain verifies  
PASS  empty history is not a valid chain  
PASS  genesis state is deterministic across runs  
PASS  UPDATE on events is refused by the store  
PASS  DELETE on events is refused by the store  
PASS  history intact after refused mutations  
PASS  INSERT OR REPLACE by event_seq is refused  
PASS  INSERT OR REPLACE by event_id is refused  
PASS  original event byte-for-byte unchanged after REPLACE attempts  
PASS  replay halts on a second RUN_OPENED  replay halted at seq 2: RUN_OPENED is only valid at sequence 1
PASS  tampered payload detected at seq 1  
PASS  engine refuses state from a tampered history  replay halted at seq 1: event hash does not recompute

STAGE 1 SMOKE: ALL PASS
```

### `python3 observer/test_export_safety.py` — 11/11 PASS (regression)

```
PASS  export of a sound run succeeds  
PASS  source database unchanged by export  
PASS  page was produced  
PASS  empty store refused  
PASS  empty file unchanged by refusal  
PASS  missing store refused  
PASS  missing file not created by refusal  
PASS  export with adversarial payload succeeds  
PASS  breakout sequence is not present as markup  
PASS  page has exactly one script element  
PASS  adversarial string round-trips as data  

OBSERVER EXPORT SAFETY: ALL PASS
```
