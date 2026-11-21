# Stage 2 — Corrections Round 3 Notes (2026-11-21)

Built under Ben's commission (scope card widget-284602e8) from Loom
spec v0.1 Rev 9 (shelf commit d7d65c96, Gate 1 PASS), in answer to
Vane's examination of corrections round 2 (NOT ACCEPTED at shelf
commit 34e68891, preserved unaltered as the examined artifact; the
round-1 artifact at 1019aaaf and the Stage 2 artifact at 9283b7e7
likewise preserved). This round's changes land in the working tree
as a new, separately identifiable round. BUILD-RECORD.md was not
edited; nothing was shelved or sent.

The round closes the three findings, all of which were about
whether the round-2 safeguards are properties of the system or
conventions of its deployment:

- **B1.1 — probe_target was an unrestricted admission bypass.**
  The posture is now bound to a rig identity the environment
  variable cannot forge: a service honours the probe_target
  request only when its own runtime was BUILT as a probe twin.
  An experimental runtime refuses the posture at startup.
- **B1.2 — provenance was checked for presence, not validity.**
  Provenance values are now validated (owner name, uid, mode;
  probe posture; service build identity), and at recording time
  the experimental service live-verifies the claim against the
  twin runtime as it actually stands — rig identity, the twin
  store's run, live stats, the twin's live code copy. A
  fabricated all-passing result does not open the gate.
- **B2.1 — diagnostic writing and restoration must fail closed.**
  The diagnostic is written atomically (temporary file, flush +
  fsync, atomic rename, directory fsync), and an unreadable or
  malformed candidate marker is an uncertain failure condition:
  startup latches closed and reports the marker state honestly.

## What changed

### `fabric/runtime_setup.py`

- **`build_runtime(base, name, rig="experimental")`** gains the
  rig parameter and writes the **rig identity record**,
  `service/rig.json` (loomfab, 600), at build time — before any
  service starts: `{"rig": ..., "runtime_root": <abs path>,
  "run_id": None}`. The run id is filled in by the service when
  it opens the run (the store's run does not exist at build
  time). `runtime_paths` gains `rig_path`.
- **`stat_record`** entries now carry the owner **uid** alongside
  the owner name and mode (`{owner, uid, mode}`), so attestation
  validation can check the recorded owner identity numerically.
  This is the change that required the flagged adjustments to the
  round-1 suite (below).

### `fabric/probe2.py`

- The twin is built with `rig="probe_twin"` — the only runtime
  in the system built that way.
- The probe result gains **`twin_root`** (the twin runtime's
  absolute root) and **`service_code_hashes`** (the twin service
  code copy's per-file SHA-256 set, from
  `runtime_setup.code_copy_hashes` — the same identity the
  runtime evidence already computes). The attestation now
  identifies the twin and its build, so the experimental service
  can verify the claim against the world.

### `fabric/service.py` — the main target

- **Rig identity and posture authorisation (B1.1).** The
  constructor reads its own runtime's `service/rig.json`.
  `LOOM_SERVICE_POSTURE=probe_target` is a request: it is
  honoured solely when the rig identity parses, says
  `probe_twin`, and names this runtime's root. A missing,
  unreadable, or mismatched identity — or, on a restart, a rig
  whose recorded run id disagrees with the store's run — raises
  in the constructor: the process exits before any socket
  serves, with the refusal recorded in the service log. There is
  no silent fallback: a refused posture is a refused service.
  When the service opens a run it records the run id into its
  rig identity (`_record_rig_run_id`), so identity and store
  agree from then on. Status reports the verified `rig`.
- **Provenance value validation (B1.2).** `attestation_problems`
  now checks, per required entry, the recorded owner name AND
  uid AND mode against the boundary's established values
  (`EXPECTED_PROVENANCE`; the expected uids are resolved from
  the account database — loomfab/loomagent — not hardcoded
  numbers); requires `service_posture == "probe_target"`;
  requires `twin_root` to identify the twin; and requires the
  claimed `service_code_hashes` to equal the service's OWN build
  identity (the per-file hashes of the code copy this process is
  running, taken once at startup).
- **Live twin verification (B1.2).** `record_probe_attestation`,
  after the object-level validation and before recording, calls
  `_verify_twin_live`: the named twin must not be this service's
  own runtime; its rig identity must say `probe_twin`, name the
  claimed root, and name the twin store's actual run (read from
  the twin's store); every claimed provenance entry must equal a
  live stat of the twin's paths; and the twin's live service
  code copy must hash to the claimed build identity. Any
  disagreement is refused and NOT recorded, exactly like a
  malformed result.
- **Atomic diagnostic write (B2.1).** `_write_diagnostic` writes
  to `unrecorded-failure-<stamp>.json.tmp` in the failures
  directory, flushes and fsyncs the file, renames onto the final
  path, and fsyncs the directory. The final path only ever holds
  a complete diagnostic, or none.
- **Fail-closed restoration (B2.1).** `_restore_latch` treats a
  candidate marker (the diagnostic naming pattern, including a
  stranded `.json.tmp` from an interrupted write) that is
  unreadable or malformed as an **uncertain failure condition**:
  the latch is restored for this runtime, no event is invented,
  and status reports `diagnostic_state: "unreadable"` with
  `diagnostic_written` and `diagnostic_restored` both false — a
  clean diagnostic is never claimed, and "no marker" is never
  claimed either. Status gains the `diagnostic_state` field
  overall: `"none" | "written" | "restored" | "unreadable"`.
  Well-formed diagnostics for a different run, and files that
  are not diagnostic candidates, keep being ignored (round-2
  interpretation 5 preserved).

### `stage2_corrections_round3_tests.py` — NEW

34 checks in three phases (outputs below): B1.1 confinement
(startup refusal on an experimental runtime, on a flipped rig,
and on a missing rig; the genuine twin rig honoured, its
bootstrap admission intact, its attestation refusal intact);
B1.2 adversarial provenance (wrong uid, permissive mode, wrong
build identity, wrong posture, the experimental runtime named as
its own twin, a fully fabricated all-passing result — all
refused and unrecorded, gate closed throughout; a live-mismatch
case where the twin's layout is changed after the probe; then
the genuine result attests and legitimate operations succeed);
B2.1 (atomic write leaves exactly one complete diagnostic and
no stranded temporary; the genuine restart behaviour unchanged;
a truncated marker fails closed with every route refused and no
event invented; non-candidates and another run's diagnostic do
not latch).

No other file changed. `engine.py`, `harness.py`, `store.py`,
`fixture.py`, `client.py`, `agent_runner.py`, `probe_agent.py`,
`probe.py`, `canonical.py` are untouched in this round. No new
event types were added, and no event payload changed shape (the
attestation payload carries the same fields; the probe result it
embeds gained `twin_root` and `service_code_hashes`, and its
`twin_config` entries gained `uid`).

## Interpretations — recorded, not silently amended

1. **Refusal means refusal to start.** Where the brief offered
   "startup refusal or enforced behaviour" for an experimental
   runtime started with the probe_target request, this round
   implements the stronger branch: the constructor raises and
   the process exits before serving. Silently starting enforced
   would leave the operator believing the bootstrap posture was
   in effect; a service that cannot establish its rig does not
   serve at all in that posture. (A service started WITHOUT the
   request on the same runtime runs enforced, as before — the
   round-3 suite proves the gate on exactly that runtime.)
2. **The rig identity's run id is recorded by the service at
   open_run.** The brief's design has rig.json carry the store's
   run id, written at setup; but no run exists at setup — the
   store is created by the service and the run by `open_run`.
   So `build_runtime` writes the record with `run_id: null`, and
   the service — the only writer that knows the run id at the
   moment it exists — fills it in when it opens the run. The
   startup cross-check (rig run vs store run) therefore binds on
   restarts, and the B1.2 twin check binds at attestation time,
   which are the two moments the identity is actually consulted.
3. **Live verification happens at recording time only.** The
   gate's per-consultation re-validation (`_attested`) checks the
   recorded claim's VALUES (outcomes, provenance values,
   posture, build identity vs this service's own build, result
   hash) but does not re-stat the twin: the twin is disposable
   and may legitimately have been rebuilt by a later probe, and
   gate state must not flip because scaffolding was recycled.
   The live check is what makes the RECORDING an act of
   verification; the recorded event is thereafter the evidence,
   re-validated as a claim each time the gate is consulted.
4. **An unreadable candidate latches THIS runtime.** A malformed
   marker's run cannot be determined — that is precisely the
   uncertainty — so the conservative reading is that it might be
   this run's, and this runtime stays closed. The cost is a
   false latch on a runtime whose failures directory was
   corrupted by something else; the alternative (round 2's
   skip-and-continue) reopens a run that may have failed
   unrecordably. Fail-closed wins. A stranded `.json.tmp` is
   treated as a candidate for the same reason: it exists only
   because a diagnostic write was interrupted mid-failure.
5. **`diagnostic_written` stays false for the unreadable case.**
   A file exists, but no COMPLETE diagnostic is known to exist;
   claiming `diagnostic_written: true` would assert the very
   thing that could not be read. The marker's existence and
   unreadability are carried by `diagnostic_state:
   "unreadable"` instead — the status distinguishes "no marker",
   "marker written", "marker restored", and "marker unreadable"
   without conflating them.
6. **Expected uids are resolved, not hardcoded.** Validation
   compares the recorded uid against `pwd.getpwnam("loomfab")` /
   `("loomagent")` resolved at import. On this machine those are
   1000/1001 (as the brief states); resolving by name keeps the
   check about the identities themselves if the numbers ever
   differ, and the recorded stat entries carry both name and uid
   so either can be audited.
7. **The twin store is read through EventStore, not a raw
   read-only connection.** `_verify_twin_live` opens the twin's
   store with the package's own EventStore to read its run id.
   The twin service is stopped by attestation time (probe2's
   flow), both services run as the same loomfab identity, and
   EventStore appends nothing — it only ensures the schema
   exists. A raw `mode=ro` sqlite open was rejected: a WAL store
   whose writer has just exited can refuse read-only opens over
   recovery files, which would fail genuine attestations for a
   storage-mechanics reason unrelated to the evidence.

## Setup adjustments to existing suites

One file adjusted: `stage2_corrections_tests.py` (the round-1
suite). No assertion was weakened or removed; the check count is
unchanged at **53**.

1. **Four exact-equality checks on stat records gained the
   `uid` conjunct.** Phase 0's "service directory is loomfab-only
   (700)", "ground-truth file is loomfab 600", and "socket
   directory is traverse-only (711)", and Phase 1's "twin store
   file was loomfab 600 during the probe", compared a stat entry
   to `{"owner": ..., "mode": ...}` exactly. Because
   `stat_record` now records the uid as well (required by B1.2 —
   the validator checks the recorded owner uid, so the record
   must carry one), each expected dict gained `"uid": 1000` as
   an ADDED conjunct. The assertions are strictly stronger than
   before: every previously checked value is still checked.

No other existing suite needed adjustment. In particular the
round-2 suite (27 checks) passes unmodified against the
round-3 service: its genuine twin result flows through the new
value validation and live verification unchanged, and its
restart and no-marker flows are untouched by B2.1 (the atomic
write produces the same final artifact; the fault-injected
write still produces none).

One build correction during this round, recorded visibly: the
first round-3 suite run failed its final check because the test
planted the different-run diagnostic as a root-owned file the
loomfab service could not read (this sandbox's umask makes
root-created files 660 root) — the service, correctly per B2.1,
treated an unreadable candidate as an uncertain failure and
latched. The planting was fixed to make the file loomfab-owned
and readable, as a real diagnostic would be; the check then
exercises the intended case (a READABLE marker for another run)
and passes. The service's behaviour on the unreadable planting
was the correction working, not a defect.

## Test outputs (final runs, 2026-11-21)

All six suites were run end-to-end in the order below; every
suite passes in full. The round-3 suite was additionally run
repeatedly during the build with identical results.

### `python3 stage2_corrections_round3_tests.py` — 34/34 PASS

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
