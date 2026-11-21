# Stage 2 — Corrections Round 6 Notes (2026-11-21)

Built under Ben's commission (scope card widget-284602e8) from Loom
spec v0.1 Rev 9 (shelf commit d7d65c96, Gate 1 PASS), in answer to
Vane's examination of corrections round 5 (NOT ACCEPTED at shelf
commit 672a876c, preserved unaltered as the examined artifact; the
round-4 artifact at 6f6b2eee, the round-3 artifact at e4e35db6,
the round-2 artifact at 34e68891, the round-1 artifact at
1019aaaf and the Stage 2 artifact at 9283b7e7 likewise preserved).
This round's changes land in the working tree as a new, separately
identifiable round. BUILD-RECORD.md was not edited; nothing was
shelved or sent.

This is the narrowest round yet: **one predicate**. It answers the
single remaining item in the round-5 examination — the
token-presence half of B1.2.1. Everything else is CLOSED or
ACCEPTED (B1.1, B1.2.2, B2.1, the session/evidence architecture)
and was not touched except to keep it green.

The defect, in Vane's terms: round 5 bound `forged_token_open` to
its exact request — an `open_region`, refused — but its token
condition tested only that the supplied value DIFFERED from the
session token:

```python
req.get("token") != session["token"]
```

An absent token, `token: null`, or an empty value differs too. So
a request that omitted its credential could be recorded as an
attempted use of a foreign one. That is not the claim the label
makes: a missing credential is not a forged credential, and the
evidence must distinguish an attempted use of a foreign token
from an omitted token.

## What changed

### `fabric/service.py` — the only production file changed

- **Token presence is part of the forged-token claim (B1.2.1).**
  The `forged_token_open` branch of `_note_probe_observation`
  now records the observation only when the request's token is a
  **non-empty string** that differs from the session token, on an
  `open_region`, refused:

  ```python
  supplied = req.get("token")
  if op == "open_region" \
          and isinstance(supplied, str) and supplied \
          and supplied != session["token"] \
          and not ok:
      session["observations"][label] = "refused"
  ```

  A missing, null, empty, or non-string token records nothing:
  the outcome stands in PROBE_EVIDENCE as `not_observed`, and the
  experimental service's attestation verification refuses a
  result built on that session, naming the outcome — exactly as
  it refuses on any other unobserved outcome. No new refusal path
  was needed.
- The module docstring gains the round-6 section, and the
  function's own docstring bullet for `forged_token_open` states
  the presence requirement — both in the file's established
  round-by-round form. Nothing else in the service changed: the
  session machinery, the entailment check, the evidence
  verification, the rig binding (B1.1) and the diagnostic
  machinery (B2.1) are as round 5 left them.

### `stage2_corrections_round6_tests.py` — NEW

31 checks in three phases (outputs below):

- **Phase A — the negative cases.** One disposable twin, one
  session per case. Each case sends an `open_region` labeled
  `forged_token_open` that the service refuses — the operation
  and the refusal are exactly what the label claims; only the
  credential carriage is defective: (a) no token field at all;
  (b) `token: null`; (c) an empty-string token; (d) a numeric
  token; (e) a list token — the non-string case Vane named,
  exercised in both its scalar and its unhashable form. Each case
  asserts the request really was refused (so only the presence
  predicate could save the record), that the twin's
  PROBE_EVIDENCE shows `forged_token_open` as `not_observed`,
  and that an attestation built around that real evidence record
  is refused, naming the outcome, and records nothing on the
  experimental run.
- **Phase B — the session-level positive control.** The same
  four socket requests, correctly labeled, the forged attempt
  carrying a non-empty foreign token string: `forged_token_open`
  IS observed as refused, all four socket outcomes stand as
  `observed`, the filesystem outcomes keep their
  `agent_reported_entailment_verified` basis (B1.2.2 asserted at
  the evidence level), and the session attests on the SAME
  experimental service that refused every token-defective
  session.
- **Phase C — the genuine positive control.** `run_twin_probe`
  end to end, a real loomagent probe process as in every earlier
  round: the genuine evidence record carries the four socket
  outcomes as `observed` and the four filesystem outcomes as
  `agent_reported_entailment_verified` — with the explicit
  assertion that no filesystem outcome carries the `observed`
  basis — the result attests at seq 2, and legitimate agent
  operations succeed on the attested run.

No other file changed, and no existing suite needed a setup
adjustment: the genuine probe's forged attempt already carries a
non-empty foreign token string (it is an attempted use of a
foreign credential by construction), so the tightened predicate
admits the genuine flow unchanged and every earlier suite passes
unmodified.

## Interpretations — recorded, not silently amended

1. **The presence test is a type test, evaluated before any
   comparison.** `isinstance(supplied, str) and supplied` runs
   ahead of the inequality against the session token, so an
   arbitrary JSON value — including an unhashable one, such as a
   list — never reaches the comparison at all. The observation
   predicate is total over whatever a request can carry: no
   carriage produces an exception in the witness, and none
   produces the observation. Case (e) exists to prove the
   unhashable form specifically, since a bare `!=` comparison
   would have survived it while a hash-based check would not
   have.
2. **The negative requests are sent by the test driver, over the
   data socket directly.** This is round 5's stated exception,
   which Vane accepted in the round-5 examination, and it is
   forced by the same shape: probe_agent.py emits only a genuine
   non-empty foreign token for its forged attempt, and the agent
   client/runner cannot carry a missing, null, or non-string
   token as a deliberate fabrication. What the predicate governs
   is the request/response pair on the twin's data socket, whose
   access control is the token protocol, not the sender's OS
   identity. The genuine flow is still exercised by a real
   loomagent process in Phase C, and by every regression suite.
3. **An unobserved outcome is refused by the existing evidence
   verification, unchanged.** As in rounds 4 and 5, this round
   adds no check to the experimental service: a socket outcome
   recorded as `not_observed` already fails
   `_verify_execution_evidence`'s requirement that every required
   outcome stand in the twin's record with its passing value and
   its `observed` basis. The correction is confined to the
   witness (what the twin records); the judge already demanded a
   credential that was actually presented.

## Environment note (not a code change)

The boundary identities were present in this shell's passwd
database — `loomfab` (uid/gid 1000) and `loomagent` (uid/gid
1001) — and were verified switchable via `runuser` before any
suite ran. Unlike round 5, no recreation was needed. No file in
the tree was changed by this; the runtime layout, owners and
modes the tests assert are produced by runtime_setup exactly as
in earlier rounds.

## Test outputs (final runs, 2026-11-21)

All nine suites were run end-to-end; every suite passes in full,
with the regression counts exact. **283 checks in total.** The
round-6 suite was run twice with identical results; the genesis
state hash is unchanged (`9a7250bde82bfd8b`, stage1_smoke below).

### `python3 stage2_corrections_round6_tests.py` — 31/31 PASS

```
PASS  B1.2.1-token (a): the request with no token field is refused — only its credential carriage is wrong for the label  
PASS  B1.2.1-token (a): the forged_token_open observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1-token (a): an attestation built on the session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1-token (a): the refused attestation records nothing on the experimental run  
PASS  B1.2.1-token (b): the request with token null is refused — only its credential carriage is wrong for the label  
PASS  B1.2.1-token (b): the forged_token_open observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1-token (b): an attestation built on the session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1-token (b): the refused attestation records nothing on the experimental run  
PASS  B1.2.1-token (c): the request with an empty-string token is refused — only its credential carriage is wrong for the label  
PASS  B1.2.1-token (c): the forged_token_open observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1-token (c): an attestation built on the session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1-token (c): the refused attestation records nothing on the experimental run  
PASS  B1.2.1-token (d): the request with a numeric token is refused — only its credential carriage is wrong for the label  
PASS  B1.2.1-token (d): the forged_token_open observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1-token (d): an attestation built on the session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1-token (d): the refused attestation records nothing on the experimental run  
PASS  B1.2.1-token (e): the request with a list token is refused — only its credential carriage is wrong for the label  
PASS  B1.2.1-token (e): the forged_token_open observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1-token (e): an attestation built on the session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1-token (e): the refused attestation records nothing on the experimental run  
PASS  B1.2.1-token control: the four correctly labeled requests have the outcomes their labels claim  
PASS  B1.2.1-token control: a non-empty foreign token IS observed as the forged attempt, and all four socket outcomes stand in the evidence as OBSERVED with their passing values  
PASS  B1.2.2: the filesystem outcomes keep their distinct agent_reported_entailment_verified basis — none is dressed as observed  
PASS  B1.2.1-token control: the correctly labeled session attests on the same experimental service that refused the token-defective ones  
PASS  B1.2.1-token control: the experimental history is exactly RUN_OPENED + BOUNDARY_PROBE  
PASS  B1.2.1-token genuine: the genuine probe's socket outcomes stand as OBSERVED by the service  
PASS  B1.2.2 genuine: the genuine probe's filesystem outcomes stand as agent-reported with entailment verified — the qualification is in the machine-readable record, distinct from observed  
PASS  B1.2.1-token genuine: the genuine session-based result attests at seq 2  
PASS  B1.2.1-token genuine: the experimental history is RUN_OPENED + BOUNDARY_PROBE  
PASS  B1.2.1-token genuine: legitimate operations succeed after the genuine attestation  
PASS  B1.2.1-token genuine: a region open serves genesis content after the genuine attestation  

STAGE 2 CORRECTIONS ROUND 6 TESTS: ALL PASS
```

### `python3 stage2_corrections_round5_tests.py` — 37/37 PASS (regression)

```
PASS  B1.2.1 (a): the mislabeled request itself is refused — only its operation/region is wrong for the label  
PASS  B1.2.1 (a): the forged_token_open observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1 (a): an attestation built on the mislabeled session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1 (a): the refused attestation records nothing on the experimental run  
PASS  B1.2.1 (b1): the mislabeled request itself is refused — only its operation/region is wrong for the label  
PASS  B1.2.1 (b1): the issuance_attempt_on_data_socket observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1 (b1): an attestation built on the mislabeled session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1 (b1): the refused attestation records nothing on the experimental run  
PASS  B1.2.1 (b2): the mislabeled request itself is refused — only its operation/region is wrong for the label  
PASS  B1.2.1 (b2): the issuance_attempt_on_data_socket observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1 (b2): an attestation built on the mislabeled session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1 (b2): the refused attestation records nothing on the experimental run  
PASS  B1.2.1 (c): the mislabeled request itself succeeds — only its operation/region is wrong for the label  
PASS  B1.2.1 (c): the legitimate_pattern_view observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1 (c): the request satisfies neither label — legitimate_region_open is unrecorded too  
PASS  B1.2.1 (c): an attestation built on the mislabeled session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1 (c): the refused attestation records nothing on the experimental run  
PASS  B1.2.1 (d): the mislabeled request itself succeeds — only its operation/region is wrong for the label  
PASS  B1.2.1 (d): the legitimate_region_open observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1 (d): the request satisfies neither label — legitimate_pattern_view is unrecorded too  
PASS  B1.2.1 (d): an attestation built on the mislabeled session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1 (d): the refused attestation records nothing on the experimental run  
PASS  B1.2.1 (e): the mislabeled request itself succeeds — only its operation/region is wrong for the label  
PASS  B1.2.1 (e): the legitimate_region_open observation stays UNRECORDED in the twin's evidence  
PASS  B1.2.1 (e): an attestation built on the mislabeled session is refused, naming the outcome whose observed basis is missing  
PASS  B1.2.1 (e): the refused attestation records nothing on the experimental run  
PASS  B1.2.1 control: the four correctly labeled requests have the outcomes their labels claim  
PASS  B1.2.1 control: all four socket outcomes stand in the evidence as OBSERVED with their passing values  
PASS  B1.2.2: the filesystem outcomes keep their distinct agent_reported_entailment_verified basis — none is dressed as observed  
PASS  B1.2.1 control: the correctly labeled session attests on the same experimental service that refused the mislabeled ones  
PASS  B1.2.1 control: the experimental history is exactly RUN_OPENED + BOUNDARY_PROBE  
PASS  B1.2.1 genuine: the genuine probe's socket outcomes stand as OBSERVED by the service  
PASS  B1.2.2 genuine: the genuine probe's filesystem outcomes stand as agent-reported with entailment verified — the qualification is in the machine-readable record, distinct from observed  
PASS  B1.2.1 genuine: the genuine session-based result attests at seq 2  
PASS  B1.2.1 genuine: the experimental history is RUN_OPENED + BOUNDARY_PROBE  
PASS  B1.2.1 genuine: legitimate operations succeed after the genuine attestation  
PASS  B1.2.1 genuine: a region open serves genesis content after the genuine attestation  

STAGE 2 CORRECTIONS ROUND 5 TESTS: ALL PASS
```

### `python3 stage2_corrections_round4_tests.py` — 32/32 PASS (regression)

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
