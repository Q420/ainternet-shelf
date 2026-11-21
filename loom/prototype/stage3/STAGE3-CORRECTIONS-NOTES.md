# STAGE 3 CORRECTIONS ROUND — B1: the fold refuses illegal transitions

Built 2026-11-21 as a separate, explicit correction round answering
the one blocking finding (B1) of Vane's Stage 3 implementation
examination (`VANE-STAGE3-EXAMINATION-2026-11-21.md`). The examined
Stage 3 artifact (shelf 1e69f5d3) is preserved unchanged; this
round's changes land in the working tree on top of it. The two
ACCEPTED items (the contribution-ID extension, TV-13's canned
fixture) are untouched except that their boundaries are re-asserted
below. BUILD-RECORD.md was not touched; nothing was shelved or
pushed; no message was sent.

## Wording alignment (Vane's documentation note)

The Stage 3 build is described consistently, here and going
forward, as **built to the settled Stage 3 design brief Rev 4** —
Rev 4 is the design authority. The build was dispatched against
Rev 3, and the one late correction between the two (the third
condition of the claim evidence predicate: every cited contribution
must be ACCEPTED) reached it through Vane's PIN before the build
was examined; the implementation and its tests conform to Rev 4.
STAGE3-BUILD-NOTES.md, which is part of the examined artifact,
keeps its original "built to Rev 3, as corrected by the PIN"
wording; this note is where the aligned description stands.

## The defect

The Stage 3 fold validated a TENSION_STATUS event only by checking
that its `from` matched the folded status, then assigned its `to`
unchecked. A hash-valid but protocol-invalid history could
therefore replay into a lifecycle state the constitution does not
permit: a semantic tension moving open → resolved directly, a
structural tension moving to `standing` or `examined`, a terminal
tension (resolved or standing) moving anywhere. Two adjacent gaps
of the same kind: TENSION_RAISED accepted any type/origin/initial-
status combination, and FACET_STATUS never validated its `to`
against section 5's six statuses. Agents cannot write these events
directly — but the event history is authoritative, and replay must
not derive an impossible state from it.

## The correction (fabric/engine.py only)

Three validations added to the fold, each raising `ReplayHalt` at
the offending sequence, in the same form as the pre-existing
from-status halt. No replay behaviour was weakened; the checker
was not made responsible for repairing invalid history (it is not
involved at all).

1. **TENSION_RAISED combinations.** `semantic` requires origin
   `contribution` or `examination`; `structural` requires origin
   `checker`; both require initial status `open`. An unknown type,
   a wrong origin for the type, or a non-open initial status halts
   replay at that event.
2. **TENSION_STATUS transitions, per type.** Semantic: open →
   examined, examined → resolved, examined → standing. Structural:
   open → resolved only. `resolved` and `standing` are terminal for
   both types. The check runs after the existing from-must-match
   check, against the folded tension's own type, so a transition
   whose `from` is honest but whose (from, to) pair is not in the
   type's table halts replay.
3. **FACET_STATUS enumeration.** The `to` value must be one of
   section 5's six: open, unexamined, claimed, complete, disputed,
   stood_down. Anything else halts replay; the existing from check
   is unchanged.

The permitted sets live in module-level tables in engine.py
(`_TENSION_RAISED_ORIGINS`, `_TENSION_TRANSITIONS`,
`_FACET_STATUSES`), next to ReplayHalt, so the lifecycle the fold
will reconstruct is stated in one place.

## Tests (stage3_corrections_tests.py — 37 checks, all passing)

**Negative replay tests.** Each illegal history is constructed
through the store's real append path (`EventStore.append`, the
same hash-chaining every legitimate event goes through), so the
chain verifies end to end — asserted explicitly via
`verify_chain` — and verified replay must still halt, at exactly
the offending sequence:

- semantic open → resolved directly (halt at seq 3);
- semantic resolved → examined, terminal (halt at seq 5, after two
  legal transitions);
- semantic standing → open, terminal (halt at seq 5);
- structural open → standing (halt at seq 3);
- structural open → examined (halt at seq 3);
- structural resolved → open, terminal (halt at seq 4);
- TENSION_RAISED: semantic type with checker origin (seq 2);
- TENSION_RAISED: structural type with contribution origin
  (seq 2);
- TENSION_RAISED: non-open initial status (seq 2);
- TENSION_RAISED: unknown tension type (seq 2);
- FACET_STATUS to a status outside the six (seq 2).

**Positive controls.** The legal transitions still fold at the
fold level: semantic open → examined → resolved; semantic open →
examined → standing; structural open → resolved; a FACET_STATUS to
a status inside the six. (The harness-level lifecycle positives
stand unmodified in stage3_tests.py.)

**Resolution-anchor test (Vane's secondary note, not a blocker).**
Pins build-notes item 5: the resolution anchor is the LATEST
accepted contribution that content-modified at least one of the
tension's regions after it was raised. Scenario: an examination
creates a tension over {Interactions, Continuity}; a first
modification lands on Interactions; an `addressed` is recorded
(the tension examines); a SECOND modification lands on Continuity;
a second `addressed` is recorded — and the tension must NOT
resolve, because only the second `addressed` stands after the
latest modification (under a first-modification anchor the two
would have resolved it). A third `addressed` then resolves it,
and the TENSION_STATUS evidence names the LATEST modifying
contribution and exactly the two post-anchor assessments.

**Accepted-boundary re-assertion.** The contribution-ID extension
keeps its accepted boundary: a stale rejection's citable ID does
NOT appear in the engine's accepted-contributions state — checked
against the live state and against a fresh replay — while the
accepted contribution's ID does. (Stage 3's own suite did not
assert this engine-state boundary; it is asserted here.)

## Regression position

All ten pre-existing suites pass unmodified, counts exact:
stage3_tests 71, round6 31, round5 37, round4 32, round3 34,
round2 27, stage2_corrections_tests 53, stage2_tests 40,
stage1_smoke 18 (genesis state hash unchanged:
9a7250bde82bfd8b…), observer/test_export_safety 11. With this
round's 37, the full run is 391 checks, all passing. No assertion
was weakened or removed; no existing suite was edited.

## Verbatim suite outputs

Appended below, unedited, from the final full run of all eleven
suites.

### stage3_corrections_tests

```
PASS  B1 semantic open->resolved: the constructed history is hash-valid  
PASS  B1 semantic open->resolved: replay halts at the offending event  halted at seq 3: TENSION_STATUS for 949baf0a-957f-4e19-998e-527e0914f279 moves a semantic tension from 'open' to 'resolved': not a permitted transition for its type (resolved and standing are terminal)
PASS  B1 semantic resolved->examined (terminal): the constructed history is hash-valid  
PASS  B1 semantic resolved->examined (terminal): replay halts at the offending event  halted at seq 5: TENSION_STATUS for 0ef8d92a-609d-483e-858c-46bad46a51b3 moves a semantic tension from 'resolved' to 'examined': not a permitted transition for its type (resolved and standing are terminal)
PASS  B1 semantic standing->open (terminal): the constructed history is hash-valid  
PASS  B1 semantic standing->open (terminal): replay halts at the offending event  halted at seq 5: TENSION_STATUS for 1fd664ce-4174-4714-8cdc-5b5681c2f13b moves a semantic tension from 'standing' to 'open': not a permitted transition for its type (resolved and standing are terminal)
PASS  B1 structural open->standing: the constructed history is hash-valid  
PASS  B1 structural open->standing: replay halts at the offending event  halted at seq 3: TENSION_STATUS for f420e04f-2a01-4ae7-b184-64d3c8e05842 moves a structural tension from 'open' to 'standing': not a permitted transition for its type (resolved and standing are terminal)
PASS  B1 structural open->examined: the constructed history is hash-valid  
PASS  B1 structural open->examined: replay halts at the offending event  halted at seq 3: TENSION_STATUS for 87b1ab41-eabb-45a4-86c5-d70967c6d894 moves a structural tension from 'open' to 'examined': not a permitted transition for its type (resolved and standing are terminal)
PASS  B1 structural resolved->open (terminal): the constructed history is hash-valid  
PASS  B1 structural resolved->open (terminal): replay halts at the offending event  halted at seq 4: TENSION_STATUS for a094b220-c758-49a8-b9d4-6f6767670195 moves a structural tension from 'resolved' to 'open': not a permitted transition for its type (resolved and standing are terminal)
PASS  B1 raised: semantic with checker origin: the constructed history is hash-valid  
PASS  B1 raised: semantic with checker origin: replay halts at the offending event  halted at seq 2: TENSION_RAISED for a semantic tension names origin 'checker'; permitted origins are contribution, examination
PASS  B1 raised: structural with contribution origin: the constructed history is hash-valid  
PASS  B1 raised: structural with contribution origin: replay halts at the offending event  halted at seq 2: TENSION_RAISED for a structural tension names origin 'contribution'; permitted origins are checker
PASS  B1 raised: non-open initial status: the constructed history is hash-valid  
PASS  B1 raised: non-open initial status: replay halts at the offending event  halted at seq 2: TENSION_RAISED names initial status 'examined'; a tension is raised open
PASS  B1 raised: unknown tension type: the constructed history is hash-valid  
PASS  B1 raised: unknown tension type: replay halts at the offending event  halted at seq 2: TENSION_RAISED names unknown tension type 'bogus'
PASS  B1 facet status outside the six: the constructed history is hash-valid  
PASS  B1 facet status outside the six: replay halts at the offending event  halted at seq 2: FACET_STATUS for 22222222-2222-4222-8222-222222222222 names to-status 'bogus'; the permitted facet statuses are open, unexamined, claimed, complete, disputed, stood_down
PASS  B1 control: semantic open->examined->resolved folds  
PASS  B1 control: semantic open->examined->standing folds  
PASS  B1 control: structural open->resolved folds  
PASS  B1 control: a facet status inside the six folds  
PASS  anchor setup: the examination created the tension  
PASS  anchor setup: the first modification was accepted  
PASS  anchor: the first addressed is recorded and examines  
PASS  anchor setup: the second modification was accepted  
PASS  anchor: an addressed before the latest modification does not count toward resolution  
PASS  anchor: two addressed after the latest modification resolve  
PASS  anchor: the resolution evidence names the LATEST modifying contribution  
PASS  boundary setup: a stale rejection carries a citable id  
PASS  boundary: the rejected id is NOT in the accepted-contributions state (live)  
PASS  boundary: the rejected id is NOT in the accepted-contributions state (replay)  
PASS  boundary: replay still reproduces the live state  

STAGE 3 CORRECTIONS TESTS: ALL PASS
```

### stage3_tests

```
PASS  TV-3 setup: State advanced to version 3  
PASS  PIN setup: a rejected contribution carries a citable id  
PASS  PIN (1): a claim citing a REJECTED contribution is recorded and counts as no claim  
PASS  TV-3: claim citing only unrelated work is recorded  
PASS  TV-3: B's current-version review is recorded  
PASS  TV-3: State is unexamined, not claimed or complete  
PASS  PIN (3): a claim at a version the cited work did not leave counts as no claim  
PASS  TV-3: the binding claim completes State (claim + review)  
PASS  TV-3: replay reproduces claims, assessments, facet state  
PASS  TV-4 setup: the tension reached resolved  
PASS  TV-4: a later contribution does not reopen or touch T  
PASS  TV-4: recurrence creates a NEW tension via examination  
PASS  TV-5 setup: a post-raise modification is on record  
PASS  TV-5: clarifies moves open -> examined, evidence = assessment  
PASS  TV-5: one addressed + clarifies never resolves  
PASS  TV-9(i): a facet target with position addressed is schema-invalid  
PASS  TV-9(ii): a tension target with position examined is schema-invalid  
PASS  TV-10(i): a FacetAssessment omitting version_reviewed is schema-invalid  
PASS  TV-10(ii): a TensionAssessment carrying version_reviewed is schema-invalid  
PASS  TV-10(iii): a FacetAssessment targeting a Tension is target_unresolved  
PASS  TV-10(iii): a TensionAssessment targeting a Region is target_unresolved  
PASS  TV-11 setup: State stands at version 5  
PASS  TV-11: an evidence-valid claim stands at version 5  
PASS  TV-11: a review of version 3 is valid history, not currency  
PASS  TV-11: a review at the current version completes the facet  
PASS  TV-11: replay reproduces the facet accounting  
PASS  TV-12(i): a first examination creates a tension  
PASS  TV-12(ii): examining an unopened region is rejected  
PASS  TV-12(iii): an identical live set is noted_existing  
PASS  TV-12(iv): after resolution, the same set creates anew  
PASS  TV-13: a valid assessment of a structural tension is rejected structural_target  
DEFERRED  TV-13 (resolution half): a passing seal attempt resolving S requires Stage 4's seal machinery (TV-1); not built, not counted as a pass.
PASS  TV-16: identity_mismatch (step 1) precedes structural_target (step 5)  
PASS  TV-14 setup: two contribution tensions over one set stand  
PASS  TV-14: the examination notes against BOTH tensions  
PASS  TV-15 setup: the original report is created  
PASS  TV-15(i): an identical resubmission returns the original outcome and appends no event  
PASS  TV-15(ii): a malformed object is recorded rejected, raw submission preserved  
PASS  TV-15(iii): a non-object submission is a transport refusal, no event, harness log only  
PASS  section 4: same key, different content is idempotency_conflict  
PASS  TV-17: unknown_region (step 4) precedes discovery_unverifiable (step 6)  
PASS  TV-18(i): an omitted idempotency key proceeds to Schema  
PASS  TV-18(ii): a malformed assessment_id proceeds to Schema  
PASS  TV-19 setup: A's report is recorded under examination_id X  
PASS  TV-19: another author's reuse of X is identity_collision  
PASS  TV-19: the identity's own author is bound by the collision rule too  
PASS  TV-20 setup: A's assessment is recorded under S  
PASS  TV-20(i): another author's reuse of S is identity_collision  
PASS  TV-20(ii): the author's own reuse with different content is id_conflict  
PASS  machinery: two standing remains move the tension to standing  
PASS  machinery: standing names the required facets it stands down  
PASS  machinery: a valid claim at the current version claims  
PASS  machinery: a standing dispute outranks the claim  
PASS  machinery: superseding the dispute with a review completes  
PASS  claim contract: a claimant field is schema_invalid (the schema admits none)  
PASS  claim contract: a non-object claim field is recordable schema_invalid, raw value preserved  
PASS  claim contract: a non-object top level is a transport refusal, no event  
PASS  claim contract: identical replay returns the original outcome, no event  
PASS  claim contract: same claimant, same id, different content is id_conflict  
PASS  claim contract: another claimant reusing the id is identity_collision  
PASS  claim contract: an unknown facet is target_unresolved  
PASS  claim contract: an unknown cited contribution is contribution_unresolved  
PASS  claim contract: a future facet_version is version_never_existed  
PASS  machinery: replay reproduces the whole Stage 3 record  
PASS  machinery: the chain verifies over the Stage 3 history  
PASS  socket: examine is refused before attestation  
PASS  socket: the twin attestation stands at seq 2  
PASS  socket: examine through the boundary creates a tension  
PASS  socket: assess through the boundary is recorded  
PASS  socket: the contribution commits through the boundary  
PASS  socket: claim_completion through the boundary records and claims the facet  
PASS  socket: a non-object request line is a transport refusal  

STAGE 3 TESTS: ALL PASS
```

### stage2_corrections_round6_tests

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

### stage2_corrections_round5_tests

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

### stage2_corrections_round4_tests

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

### stage2_corrections_round3_tests

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

### stage2_corrections_round2_tests

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

### stage2_corrections_tests

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

### stage2_tests

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
PASS  every Stage 2 event payload carries a plain-words summary  31 events
PASS  replay equals live state at the end of Run C  
PASS  chain verifies at the end of Run C  

STAGE 2 TESTS: ALL PASS
```

### stage1_smoke

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

### test_export_safety

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

