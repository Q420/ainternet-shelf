# Stage 2 — Corrections Round 4 Notes (2026-11-21)

Built under Ben's commission (scope card widget-284602e8) from Loom
spec v0.1 Rev 9 (shelf commit d7d65c96, Gate 1 PASS), in answer to
Vane's examination of corrections round 3 (NOT ACCEPTED at shelf
commit e4e35db6, preserved unaltered as the examined artifact; the
round-2 artifact at 34e68891, the round-1 artifact at 1019aaaf and
the Stage 2 artifact at 9283b7e7 likewise preserved). This round's
changes land in the working tree as a new, separately identifiable
round. BUILD-RECORD.md was not edited; nothing was shelved or sent.

The round answers the two findings that remained. **B2.1 is
CLOSED and its machinery is untouched** — the diagnostic write and
restoration code is byte-identical to round 3; it appears here
only as regression evidence. The examination's two accepted
interpretations are built on, not relitigated: interpretation 3
(live verification at recording time, claim-based gate
revalidation thereafter) and interpretation 4 (an unreadable
marker latches its runtime).

- **B1.1 residual — the rig/store run binding had a null
  escape.** The startup comparison fired only when BOTH run ids
  were non-null, and only under probe_target. The binding is now
  unconditional: whenever the store already holds a run, the rig
  identity must carry a run_id that is a non-empty string equal
  to it — missing, null, malformed, or mismatched refuses
  startup, in every posture. The runtime factory no longer
  accepts the probe_twin designation for an arbitrary runtime
  name: `build_runtime` builds experimental runtimes only, and
  the twin is built through the dedicated `build_twin_runtime`.
- **B1.2 — attestation was bound to a twin's existence, not to
  a probe's execution.** Round 3 verified that a suitably
  configured twin EXISTS; Vane's attack (genuine twin, run
  opened, probe never executed, real metadata harvested,
  fabricated all-passing outcomes) passed every check. The
  attestation is now bound to execution evidence held in the
  twin's OWN records: a probe runs inside a session the twin
  service opens and records; the service observes the socket
  outcomes itself; the agent's filesystem outcomes are filed
  under the session token and each denial is checked for
  entailment against the twin's live configuration; the outcome
  set is recorded as a PROBE_EVIDENCE event in the twin's
  history. The experimental service extracts the outcomes from
  that record and requires the submitted outcomes to match them
  exactly. No execution record, no gate.

## What changed

### `fabric/service.py` — the main target

- **Unconditional run binding (B1.1).** The constructor's
  rig/store cross-check no longer sits inside the probe_target
  branch and no longer requires both ids to be non-null: if
  `store.get_run_id()` returns a run, the rig identity's
  `run_id` must be a non-empty string equal to it, else the
  constructor raises before any socket serves. Posture requests
  are decided exactly as in round 3; this check is separate and
  posture-independent.
- **Probe sessions (B1.2).** New admin operation
  `open_probe_session`, refused outside the probe_target
  posture: it issues a token through the harness, generates a
  session id, appends PROBE_SESSION_OPENED to the twin's own
  history (session id, agent id, the token's SHA-256 — never the
  token), and holds the live session (token, observations) in
  memory. The data dispatcher now wraps every response with
  `_note_probe_observation`: when a request carries a probe
  session id and an attempt label, the service records the
  outcome ONLY when what actually happened on its socket matches
  the label's claim (a non-session token refused → the
  forged-token attempt observed refused; an unknown operation
  refused → the issuance attempt observed refused; the session
  token succeeding → the legitimate attempts observed ok). The
  label names the attempt; it cannot manufacture the outcome.
- **The probe report (B1.2).** New data-socket operation
  `probe_report` — an unknown operation on any non-probe-target
  service. In probe_target posture it finalises a session, once:
  the caller must authenticate as the session's agent under the
  session-bound token. For each filesystem attempt the service
  runs `_fs_denial_entailed`: the reported path must be this
  twin's own path for that attempt (the symlink and traversal
  spellings must resolve to the store they aim at); the reported
  outcome must be a denial carrying EACCES; and
  `_identity_can_read` — a kernel-style permission simulation
  over the resolved path's ancestors — must find that the twin's
  live owner/mode configuration denies the agent identity the
  read. The service then appends PROBE_EVIDENCE: the session id,
  the full outcome set with each outcome's basis (`observed` for
  the four socket outcomes, `agent_reported_entailment_verified`
  or `agent_reported_unverified` for the filesystem outcomes,
  `not_observed`/`not_reported` where the session produced
  nothing), and the DISCOVERY sequences in the twin's history
  that corroborate the legitimate open. The response identifies
  the evidence event (seq + hash).
- **Attestation: pointer validation + evidence extraction
  (B1.2).** `attestation_problems` now also requires a
  well-formed `execution_evidence` pointer (it names the same
  twin as the result, carries a session id, an event_seq ≥ 2,
  and a SHA-256 event hash). At recording time,
  `record_probe_attestation` additionally calls
  `_verify_execution_evidence` after `_verify_twin_live`: it
  opens the twin's store, verifies its hash chain with the
  package's own `verify_chain`, locates the pointed-to
  PROBE_EVIDENCE event, confirms the session was opened earlier
  in the same chain, extracts the recorded outcomes, and
  requires every required outcome to stand there with its
  passing value AND its required basis, and the submitted
  outcomes to match the recorded ones exactly. Any disagreement
  is refused and NOT recorded, like every earlier validation.

### `fabric/store.py`

- EVENT_TYPES gains two TWIN-LOCAL types,
  `PROBE_SESSION_OPENED` and `PROBE_EVIDENCE`. They exist only
  in a disposable twin's store; the experimental service appends
  only BOUNDARY_PROBE, and the round-4 suite asserts the
  experimental history is exactly [RUN_OPENED, BOUNDARY_PROBE].

### `fabric/engine.py`

- The fold treats the two new types as evidence-only, in the
  same branch as IDLE: they change no fabric state. Genesis and
  every pre-existing history derive byte-identical state (the
  stage-1 genesis state hash is unchanged: 9a7250bde82bfd8b).

### `fabric/runtime_setup.py`

- `build_runtime` builds experimental runtimes only: any other
  rig value — `probe_twin` above all — raises ValueError naming
  the sanctioned route. New `build_twin_runtime(base,
  name="twin")` is the one route to a probe_twin rig. Both
  delegate to the unchanged layout builder.

### `fabric/probe2.py`

- The twin is built via `build_twin_runtime`. The probe flow is
  session-based: open_run, then `open_probe_session`; the agent
  receives the session-bound token and the session id; the
  result gains `execution_evidence` — {twin_root, session_id,
  event_seq, event_hash} — taken from the service's probe-report
  response relayed by the agent. If the session recorded no
  evidence, run_twin_probe raises rather than returning a result
  that could not attest.

### `fabric/probe_agent.py`

- Socket attempts carry `probe_session` and `probe_attempt`
  labels so the twin service can observe them. After the
  attempts, the agent files its four filesystem outcome records
  through the data socket under the session token
  (op `probe_report`) and relays the service's response — the
  evidence record's identity — in its output. The probe remains
  a real loomagent process; its read attempts, and what it
  reports about them, are unchanged.

### `stage2_corrections_round3_tests.py` — setup adjustments

Three build call sites moved to the new factory route (flagged
below). No assertion changed; the count is unchanged at **34**.

### `stage2_corrections_round4_tests.py` — NEW

32 checks in five phases (outputs below): the B1.1 restart
matrix (missing / null / malformed / mismatched / absent rig
identity against a store holding a run, all in the ENFORCED
posture, plus the matching case) and the factory discipline;
Vane's attack verbatim (genuine never-probed twin, fabricated
outcomes; then the same with an invented evidence pointer); the
genuine evidence record inspected in the twin's own history,
with its bases; altered outcomes and a retargeted pointer
against a genuine twin; the genuine end-to-end flow; and stale
evidence after a twin rebuild, with the claim-based gate of the
already-recorded attestation asserted intact.

No other file changed. `harness.py`, `fixture.py`, `client.py`,
`agent_runner.py`, `probe.py`, `canonical.py` are untouched, and
the B2.1 diagnostic machinery (`_write_diagnostic`,
`_restore_latch`, the fault-injection paths) is byte-identical
to round 3. No experimental event types were added or changed.

## Interpretations — recorded, not silently amended

1. **The execution evidence lives in the twin's store, as two
   twin-local event types** — the brief's first option, chosen
   over a separate ledger file. The store is already
   append-only at the schema level (insert-only triggers), hash
   chained, and verifiable with the package's own machinery; a
   ledger file written beside it would be a second, weaker
   integrity mechanism (a plain file has no append-only
   enforcement and its chain would be a new, less-exercised
   implementation). The cost — two new names in the shared
   EVENT_TYPES set — is contained: the types are evidence-only
   in the fold like IDLE, they can only be appended by a
   probe-target service (the session operations do not exist in
   the enforced posture), and the experimental history never
   contains them, which the round-4 suite asserts exactly.
2. **What the execution evidence proves, and what it does not —
   stated honestly.** The socket outcomes are first-hand: the
   twin service served or refused those requests itself, on its
   own socket, under a token it issued for the session. The
   filesystem outcomes are necessarily second-hand — the reads
   happen inside the agent process, where no service can watch
   them. What the evidence establishes about them is: a session
   the service opened and bound to a token; a report filed under
   that token within the session; and, for each reported denial,
   entailment — the attempted path is the twin's own probe path,
   the reported error is the OS permission errno, and the twin's
   live configuration denies the agent identity exactly that
   read. A denial the configuration does not entail is recorded
   as unverified and fails attestation. What is NOT proven is
   the physical instant of the agent's open() calls: no
   mechanism inside this boundary can prove what another process
   did at an instant, and the record does not claim it. What is
   proven is that the outcome set in the attestation is the
   outcome set the twin service recorded from a session it ran,
   whose witnessed half corroborates the reported half, and
   whose reported half is exactly the behaviour the boundary
   configuration enforces. Vane's attack fails under it not
   because fabrication is hard to spell, but because there is no
   session and no evidence event in the twin's records to point
   at — existence of a twin is no longer evidence of a probe.
3. **The evidence pointer is only a pointer.** It reaches the
   result through the driver (relayed by the agent's output),
   and a caller could write any pointer it likes. That gains it
   nothing: the experimental service opens the twin's store
   itself, verifies the whole chain, and extracts the outcomes
   from the record the pointer names. The pointer is an address,
   not an assertion; the record at that address is the evidence.
4. **The run binding is posture-independent** (the brief's
   instruction, recorded as a choice). Round 3 checked rig
   against store only for probe_target services. A rig identity
   that fails to name the store's run is a false identity for an
   enforced service too, so the check fires whenever the store
   holds a run, whatever was requested. First starts are
   unaffected — with no run in the store there is nothing to
   bind yet, and open_run records the id the moment it exists
   (round-3 interpretation 2 stands).
5. **Entailment is judged at report time, against the live
   configuration, using the agent identity's primary group.**
   The permission simulation resolves owner/group/other with the
   agent's uid and primary gid; the boundary layout grants the
   agent nothing through any other group (every boundary path is
   group-owned by its owner's own group), so supplementary
   groups cannot change the result. Judging at report time is
   the honest moment: the probe and its report are one session,
   and if the twin's permissions were loosened in between, the
   reported denial is recorded UNVERIFIED and the attestation
   fails — the round-3 live-mismatch discipline applied to the
   probe's own report.
6. **A session finalises once, and lives in the twin service's
   memory.** A second probe_report for the same session is
   refused; the durable artifact is the PROBE_EVIDENCE event. If
   the twin service restarts mid-probe, the live session is gone
   (its PROBE_SESSION_OPENED remains in the history) and the
   probe is simply re-run: no attestation can be built on the
   half-finished session, because there is no evidence event to
   point at. That is the fail-closed direction throughout this
   round — missing evidence refuses, never defaults.
7. **Attestation must happen while the twin's evidence
   stands.** The evidence lives in a disposable rig; if the twin
   is rebuilt before the attestation is submitted, the old
   result's pointer names a chain that no longer exists and the
   submission is refused (round-4 Phase E) — the remedy is to
   re-probe, which is cheap and is what the rig is for. Once the
   attestation IS recorded, accepted interpretation 3 governs:
   the gate's revalidation is claim-based, and rebuilding the
   twin afterwards does not un-attest the run (also asserted in
   Phase E).

## Setup adjustments to existing suites

One file adjusted: `stage2_corrections_round3_tests.py`. No
assertion was weakened, removed, or changed in meaning; the
check count is unchanged at **34**.

1. **Three probe-twin build sites moved to
   `build_twin_runtime`.** Phase A's flipped-rig runtime
   ("round3flipped"), the missing-rig runtime ("round3norig"),
   and the genuine-twin runtime ("round3twin") were built with
   `build_runtime(..., rig="probe_twin")`. The factory
   correction in this round makes that call raise by design, so
   the three sites now call `build_twin_runtime`, the sanctioned
   route — the same runtimes, built the same way, through the
   interface the correction mandates. The import line gained the
   new name.

No other existing suite needed adjustment. Rounds 1 and 2 pass
unmodified: their genuine attestations flow through
`run_twin_probe`, which now produces session-based results with
execution evidence, and every fabricated/malformed/incomplete
case they exercise is still refused (now at whichever validation
layer reaches it first). The round-2 suite's placement check (a
second attestation refused) and the round-1 suite's Phase 6
fault-runtime attestation are unaffected: evidence verification
is read-only on the twin and repeatable across experimental
runtimes.

## Test outputs (final runs, 2026-11-21)

All seven suites were run end-to-end in the order below; every
suite passes in full. **215 checks in total.** The round-4 suite
was additionally run repeatedly during the build with identical
results.

### `python3 stage2_corrections_round4_tests.py` — 32/32 PASS

```
PASS  B1.1 setup: opening the run recorded its id in the rig identity  
PASS  B1.1: a rig run_id that is missing refuses startup when the store holds a run  
PASS  B1.1: a rig run_id that is null refuses startup when the store holds a run  
PASS  B1.1: a rig run_id that is malformed (a number) refuses startup when the store holds a run  
PASS  B1.1: a rig run_id that is mismatched refuses startup when the store holds a run  
PASS  B1.1: no rig identity at all refuses startup when the store holds a run  
PASS  B1.1: a rig naming the store's actual run starts and serves  
PASS  B1.1: build_runtime refuses the probe_twin designation (the twin has one sanctioned build route)  
PASS  B1.1: build_twin_runtime builds the probe-twin rig  
PASS  B1.2 attack: fabricated outcomes against a genuine, never-probed twin are refused  
PASS  B1.2 attack: no BOUNDARY_PROBE stands in the experimental history  
PASS  B1.2 attack: an invented execution-evidence pointer against the same twin is refused  
PASS  B1.2 attack: the history is still exactly RUN_OPENED  
PASS  B1.2 attack: the gate stays closed (no token issued)  
PASS  B1.2: the twin's own history records the probe session and its execution evidence  
PASS  B1.2: the result's pointer names the twin's evidence event (seq + hash)  
PASS  B1.2: the socket outcomes stand in the twin's record as OBSERVED by the service  
PASS  B1.2: the filesystem outcomes stand in the twin's record as agent-reported with entailment verified  
PASS  B1.2: the legitimate open is corroborated by a DISCOVERY in the twin's history  
PASS  B1.2: an altered outcome against a genuine twin is refused  
PASS  B1.2: the altered submission recorded nothing  
PASS  B1.2: a pointer retargeted at the session-opened event (a real event, but not evidence) is refused  
PASS  B1.2: the retargeted submission recorded nothing  
PASS  B1.2: the genuine session-based result attests at seq 2  
PASS  B1.2: the experimental history is RUN_OPENED + BOUNDARY_PROBE (no twin-local types leak into it)  
PASS  B1.2: status reports the attested, open run  
PASS  B1.2: legitimate operations succeed after the genuine attestation  
PASS  B1.2: a region open serves genesis content after the genuine attestation  
PASS  B1.2: a result whose execution evidence stood in a since-rebuilt twin is refused  
PASS  B1.2: the stale submission recorded nothing  
PASS  B1.2: the rebuilt twin's own genuine result attests (the refusal was staleness, not the runtime)  
PASS  B1.2: the recorded attestation survives the twin's rebuild (gate revalidation is claim-based)  

STAGE 2 CORRECTIONS ROUND 4 TESTS: ALL PASS
```

### `python3 stage2_corrections_round3_tests.py` — 34/34 PASS (regression)

```
PASS  B1.1: probe_target on an EXPERIMENTAL runtime is refused at startup  
PASS  B1.1: the startup refusal is recorded in the service log  
PASS  B1.1: the experimental service reports its rig honestly  
PASS  B1.1: after the refused posture, issuance on the experimental runtime is still gated  
PASS  B1.1: after the refused posture, a data operation is still refused on the gate (not_attested)  
PASS  B1.1: a rig that does not say probe_twin refuses the posture (the env var cannot override the rig)  
PASS  B1.1: a missing rig identity refuses the posture  
PASS  B1.1: a probe-twin rig honours the probe_target posture  
PASS  B1.1 setup: the twin run opens  
PASS  B1.1: opening the run records the run id in the rig identity  
PASS  B1.1: the twin's one bootstrap admission still works (issuance before attestation)  
PASS  B1.1: a probe target still never records an attestation  
PASS  B1.2: a provenance entry with the wrong owner uid is refused and NOT recorded  
PASS  B1.2: a provenance entry with a permissive mode is refused and NOT recorded  
PASS  B1.2: a wrong service build identity is refused and NOT recorded  
PASS  B1.2: a result claiming the enforced posture is refused and NOT recorded  
PASS  B1.2: provenance naming the experimental runtime itself as the twin is refused and NOT recorded  
PASS  B1.2: a fully fabricated all-passing result with no twin behind it is refused and NOT recorded  
PASS  B1.2: the gate stays closed after every fabricated or mismatched attestation  
PASS  B1.2: the genuine result after the twin's layout changed under it (live mismatch) is refused and NOT recorded  
PASS  B1.2: the genuine probe result still attests and opens the gate  
PASS  B1.2: status reports the attested, open run  
PASS  B1.2: legitimate operations succeed after the genuine attestation  
PASS  B2.1: the breaching submission is answered run_failed_unrecorded  
PASS  B2.1: in-process status shows the written marker state  
PASS  B2.1: the atomic write leaves exactly one complete diagnostic and no stranded temporary  
PASS  B2.1: the diagnostic at the final path is complete (parses whole)  
PASS  B2.1: after restart the latch is restored from the diagnostic (state: restored)  
PASS  B2.1: after restart every agent-facing route is refused  
PASS  B2.1: after restart the history still holds no RUN_FAILED  
PASS  B2.1: a truncated diagnostic fails closed at startup (failed_unrecorded, marker unreadable)  
PASS  B2.1: with an unreadable marker every agent-facing route is refused  
PASS  B2.1: the uncertain latch invents no event  
PASS  B2.1: an unrelated file and a different run's diagnostic do not latch this run  

STAGE 2 CORRECTIONS ROUND 3 TESTS: ALL PASS
```

### `python3 stage2_corrections_round2_tests.py` — 27/27 PASS (regression)

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
