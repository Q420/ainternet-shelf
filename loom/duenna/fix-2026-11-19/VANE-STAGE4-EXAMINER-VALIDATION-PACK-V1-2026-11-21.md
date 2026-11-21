# Examiner Validation Pack — Stage 4, v1

**Authorship:** Vane (examiner side)  
**Status:** examiner-authored draft, submitted to Remmy for challenge; not yet pinned for implementation use  
**Date:** 2026-11-21  
**Authority set:** Loom specification v0.1 Rev 9 (blob `6a7e3d54b4b653ed6b8ca76392c59d283d8b2b1a`), Amendment A1 (blob `8af1afb609522b84c0b5f2ebac879059fadad84b`), and Stage 4 Design Brief Rev 2 (shelf head `6aee9455`). Rev 9 and A1 are separate authorities. This pack does not modify either.

## 1. Purpose and independence

This pack supplies examiner-authored expected outcomes for pre-open validation of the engine's seal path and the separately implemented checker. It is authored from the normative text above, not generated from, copied from, or inferred by inspecting either implementation.

Remmy is asked to examine, challenge, and propose corrections to this pack before it is pinned. Until that examination is complete and the pack is pinned, **no Stage 4 implementation build is authorized**.

The pack tests contract behaviour, not implementation structure. It does not prescribe class names, function names, database layout, internal data structures, or code reuse. An adapter may translate the abstract fixtures below into each implementation's native test interface, but it must not change the expected outcome.

## 2. Input model and terminology

Each case declares one or more of these inputs:

1. **Committed history H:** immutable, ordered event sequence through the last committed event. Unless a case says otherwise, H has a valid genesis, contiguous sequence numbers, valid event schemas, and a valid hash chain.
2. **Staged batch B:** candidate events for the transaction currently being evaluated. B is not yet committed. It is supplied explicitly to the checker, in order, and is evaluated after H. The checker must not pretend B is already in committed storage.
3. **Live snapshot L:** read-only snapshot of the actual live derived state at the attempt boundary, after applying B's state effects in the transaction's staged view. L is evidence, not authority.
4. **Replay state R:** state independently derived by folding H followed by B, as appropriate to the attempt boundary. The checker must independently derive R. It must not trust an engine-supplied state object as R.
5. **Seal attempt A:** the proposed attempt represented in B. A passing seal is anchored to the event position of its `SEAL_ATTEMPTED` event. Any structural tension event emitted after that event in the same atomic group is not retroactively part of the seal position.
6. **Affected set:** a set of record identities. Set equality is order-insensitive; canonical serialization/order must be deterministic. A check identity is the pair (check name, affected record set).

**Expected result vocabulary**

- `PASS`: the check/attempt succeeds and may issue a seal, subject to all other required checks.
- `FAIL(check, affected)`: the named check fails for the named affected set; no seal is issued.
- `HALT(seq, reason)`: replay stops at the first invalid event at sequence `seq`; state after that point is UNKNOWN.
- `MISMATCH`: the supplied live snapshot does not equal independently replay-derived state. The checker must not issue a seal.
- `NO_ATTEMPT`: no seal attempt is required by the trigger contract for this action.
- `REPLAY(original)`: an identical idempotent submission returns the original outcome and appends no event.

The exact event payload schema for Stage 4 event types is the implementation contract's responsibility. These cases define semantic expectations independently of payload field spelling. The implementation notes must map every case to exact serialized events and record that mapping before execution.

## 3. Fixed abstract fixture

Unless a case overrides it, use this minimal deterministic fixture:

- Six frozen regions: Components (C), Interactions (I), State (S), Continuity (N), Presentation (P), Operations (O), all at version 1.
- Existing active dependency C `uses` S.
- Existing active dependency N `constrains` I.
- No other dependency is present.
- No tensions exist.
- The constitution hash and genesis are fixed per test run and recorded in the test manifest.
- A1 is in force. An `IDLE` event is an evidence-only event whose actor is the authenticated idling agent; folding it changes event history but changes no fabric state.
- The S1 dangling-edge fixture uses dependency D-CS whose source is C and target is S. Its live-state-only fault removes S from the live region map while leaving D-CS active. H remains valid and still replays to a state in which S exists.

Names C, I, S, N, P, O are test aliases only. They are not alternative region identities in any production fixture.

## 4. Event-history and replay vectors

### VP-01 — Valid genesis and empty fold
**Input:** H contains exactly one valid `RUN_OPENED` event. Its first `prev_hash` is the pinned constitution hash. No B. L equals R.  
**Expected:** replay succeeds; L = R; no structural check fails; a close-time attempt may pass. This is the baseline control.

### VP-02 — IDLE is durable evidence and state-neutral
**Input:** H is a valid run-open history. B contains one well-formed `IDLE` event with actor equal to an authenticated crew identity.  
**Expected:** fold accepts the event; event count and chain head advance; all fabric state fields remain byte-for-byte/equality identical to the pre-IDLE state. The event is retained in history and is not silently discarded.

### VP-03 — IDLE actor mismatch
**Input:** B contains an `IDLE` event whose actor differs from the authenticated identity for the submission.  
**Expected:** reject the attempted action under the applicable identity rule before acceptance. No accepted `IDLE` event is appended. No fabric state changes.

### VP-04 — Hash-link corruption
**Input:** H has valid event schemas and sequence numbers, but one event's `prev_hash` or recomputed event hash is wrong at sequence k.  
**Expected:** `HALT(k, hash_chain_invalid)`; no state after k is presented as valid; no seal is issued.

### VP-05 — Sequence gap
**Input:** H has valid individual hashes but omits or duplicates an event sequence position at k.  
**Expected:** `HALT(k, sequence_invalid)`; no seal is issued. A chain of individually hash-valid records is not sufficient if sequence continuity fails.

### VP-06 — Hash-valid, schema-invalid event
**Input:** H's event at k has a valid hash over its actual bytes and valid chain linkage, but its event type/payload fails the applicable event schema.  
**Expected:** `HALT(k, schema_invalid)`; no seal is issued. The implementation must not treat hash validity as schema validity.

### VP-07 — Hash-valid malformed tension type (unhashable)
**Input:** H contains a hash-valid `TENSION_RAISED` payload whose `type` value is an array or object, not a permitted string.  
**Expected:** `HALT(k, schema_invalid_or_protocol_invalid)` at k, with a controlled replay error. A native `TypeError`, uncaught exception, process crash, or later-sequence failure is a test failure. The implementation must name its stable controlled reason in the mapping table.

### VP-08 — Hash-valid malformed transition source (unhashable)
**Input:** H contains a hash-valid `TENSION_STATUS` payload whose `from` value is an array or object.  
**Expected:** controlled `HALT(k, schema_invalid_or_protocol_invalid)` at k. No native exception escapes.

### VP-09 — Hash-valid malformed transition target (unhashable)
**Input:** H contains a hash-valid `TENSION_STATUS` payload whose `to` value is an array or object.  
**Expected:** controlled `HALT(k, schema_invalid_or_protocol_invalid)` at k. No native exception escapes.

### VP-10 — Unknown tension type
**Input:** H contains a hash-valid `TENSION_RAISED` event with a scalar but unknown tension type.  
**Expected:** controlled `HALT(k, protocol_transition_invalid)`; no tension is admitted into derived state.

### VP-11 — Tension origin/type mismatch
**Input A:** semantic tension raised with origin `checker`.  
**Input B:** structural tension raised with origin `contribution` or `examination`.  
**Expected:** each history halts at the offending event. Only semantic tensions may originate from contribution or ExaminationReport; only structural tensions may originate from checker.

### VP-12 — Illegal semantic transition
**Input:** hash-valid semantic tension history attempts `open → resolved` without first entering `examined`, or attempts `resolved → examined`.  
**Expected:** `HALT(k, protocol_transition_invalid)` at the transition event.

### VP-13 — Illegal structural transition
**Input A:** structural `open → examined`.  
**Input B:** structural `open → standing`.  
**Input C:** structural `resolved → open`.  
**Expected:** each halts at the offending event. Structural tensions permit only `open → resolved`; resolved is terminal.

### VP-14 — Invalid facet status
**Input:** hash-valid `FACET_STATUS` names a target outside the six frozen regions or a status outside {open, unexamined, claimed, complete, disputed, stood_down}.  
**Expected:** controlled halt at the offending event; no invalid facet status enters replay state.

### VP-15 — A1 is separately bound at run open
**Input A:** `RUN_OPENED` binds Rev 9 plus A1; subsequent history contains a valid `IDLE`.  
**Input B:** `RUN_OPENED` binds Rev 9 alone; subsequent history contains `IDLE`.  
**Expected:** A accepts IDLE as an evidence-only event. B must not silently inherit A1; it rejects or halts on the event according to its pinned pre-A1 event schema. No run may change its authority set mid-run.

## 5. Structural check vectors

### VP-16 — S1 dependency integrity: missing endpoint
**Input:** L contains an active dependency whose source or target is absent from L's frozen region set; R is otherwise valid.  
**Expected:** `FAIL(S1, {dependency, missing endpoint})`; no seal. The affected set names the dependency and the missing endpoint identity deterministically.

### VP-17 — S1 accepts a valid dependency
**Input:** L contains an active dependency whose two endpoints both exist in the frozen region set and whose record is internally well-formed.  
**Expected:** S1 passes. This is a positive control against an implementation that rejects all dependencies.

### VP-18 — S2 version monotonicity: regression
**Input:** B or the candidate state would lower a region version below the version established by the accepted history.  
**Expected:** the candidate is rejected before it can become an accepted commit under the ordinary contribution protocol; if such a state is nevertheless presented as L, the checker reports a mismatch or S2 failure and issues no seal. The engine must not normalize the regression away.

### VP-19 — S2 version monotonicity: valid advance
**Input:** an accepted content/dependency operation advances the affected region version(s) monotonically according to Rev 9.  
**Expected:** S2 passes. Dependency operations advance both endpoints; no endpoint may remain at an older version when the operation contract requires advancement.

### VP-20 — S3 pattern acyclicity: cycle
**Input:** L contains a directed cycle across `uses`, `constrains`, and/or `extends` edges.  
**Expected:** `FAIL(S3, {all records participating in the detected cycle})`; no seal. The reported affected set is deterministic even if several traversals discover the cycle in different orders.

### VP-21 — S3 acyclic graph
**Input:** L contains multiple valid edges, including convergent paths, but no directed cycle.  
**Expected:** S3 passes. A graph with multiple incoming edges is not itself a cycle.

### VP-22 — S4 remains at schema/targeting layer
**Input:** a contribution violates declared operation scope (for example, a content operation targets a region outside write_set) but does not otherwise create a live-state invariant violation.  
**Expected:** contribution is rejected under Rev 9's schema/targeting validation. No accepted commit occurs and therefore no post-commit seal attempt is triggered. S4 is not invented as a fourth seal check.

### VP-23 — Rejected contribution does not trigger a seal
**Input:** a contribution is rejected as stale, schema-invalid, or structural before acceptance.  
**Expected:** `NO_ATTEMPT` for the post-accepted-commit trigger. A separate run-close attempt may still be required. No `SEAL_ATTEMPTED` event is appended merely because a rejection occurred.

## 6. Checker input and independence vectors

### VP-24 — Candidate batch is explicit and included
**Input:** H is valid. B contains an accepted contribution that monotonically updates a region and the associated staged state. L is the post-B staged snapshot.  
**Expected:** checker independently folds H + B, derives R, and evaluates the attempt at the candidate position. It must not evaluate H alone or use a stale pre-B snapshot. If L = R and S1–S3 pass, the attempt may pass.

### VP-25 — Omitted candidate batch
**Input:** same as VP-24, but the checker is deliberately given H and L while B is omitted.  
**Expected:** checker must refuse to certify the attempt because the candidate position cannot be reconstructed from the supplied committed history. No seal. A checker that silently treats L as authority fails.

### VP-26 — Live snapshot diverges from replay state
**Input:** H + B independently fold to R. L differs from R in one region record, version, or dependency record, while all supplied hashes for H remain valid.  
**Expected:** `MISMATCH`; no seal. The checker reports the differing record identities. It must not repair L, trust L, or issue a seal based only on H's valid chain.

### VP-27 — Snapshot agrees with replay but has S1 fault
**Input:** H + B themselves fold to a state R containing a dangling dependency due to an invalid event history that is nevertheless hash-valid. L = R.  
**Expected:** history replay must halt at the invalid event if the fault violates event protocol/schema. If the history is valid but state is structurally inconsistent by a permitted transition path, S1 fails. In neither case may a seal issue. This vector distinguishes replay validity from structural validity.

### VP-28 — Checker cannot import engine/harness logic
**Input:** static dependency/import audit of the checker process and its runtime module graph.  
**Expected:** no import or call path into engine or harness implementation logic. Canonical JSON and hash primitives are the only permitted shared code. A test double may instrument imports, but the audit must cover transitive imports, not only direct imports.

### VP-29 — Independent implementation agreement
**Input:** the complete pinned pack is executed against engine and checker independently.  
**Expected:** identical contract-level outcomes for every case. Internal diagnostics may differ, but pass/fail, halt position/reason class, affected identities, tension lifecycle, and seal eligibility must agree. Any disagreement blocks RUN_OPENED.

## 7. Seal trigger, transaction, and structural tension vectors

### VP-30 — Accepted commit triggers exactly one attempt
**Input:** one accepted contribution, no other accepted contribution in the atomic group.  
**Expected:** exactly one post-commit `SEAL_ATTEMPTED` event in that atomic group. The attempt is unconditional, even when a structural tension is already open.

### VP-31 — Open structural tension does not gate attempt
**Input:** H contains one open structural tension. A new ordinary contribution is accepted.  
**Expected:** a seal attempt still occurs. The tension's existence does not suppress, delay, or condition the attempt.

### VP-32 — Attempt event position precedes structural status event
**Input:** a candidate attempt passes the same check that previously raised an open structural tension.  
**Expected:** event order is `SEAL_ATTEMPTED` first, then `TENSION_STATUS(open→resolved)` with evidence referencing that attempt. The seal covers the `SEAL_ATTEMPTED` position only. The later status event is in the same atomic group but not retroactively covered by the seal.

### VP-33 — Fail produces no seal
**Input:** at least one structural check fails.  
**Expected:** `SEAL_ATTEMPTED(outcome=fail)` records every failed check and affected set; no seal record is issued for that position.

### VP-34 — Pass records semantic questions without clearing them
**Input:** all structural checks pass; one semantic tension is open and another is examined.  
**Expected:** seal may issue. Its record lists both outstanding semantic questions with their examination attribution/status, and explicitly states that the seal grants no semantic clearance. Neither tension changes status merely because a seal passed.

### VP-35 — Contributions-since-last-seal boundary
**Input:** two accepted commits, each followed by a passing seal.  
**Expected:** first seal lists contributions since genesis/previous seal according to the contract's defined initial boundary; second seal lists only contributions after the first seal. No contribution is omitted or counted twice. The build notes must state the initial boundary explicitly.

### VP-36 — Atomic group rollback
**Input:** accepted contribution and derived transitions are staged; checker process fails or the transaction cannot append the attempt/status events.  
**Expected:** the atomic group does not partially commit. No visible accepted contribution may remain without its required post-commit attempt record. Failure handling must be explicit and durable under the existing run-failure contract; it must not silently retry or leave a partial group.

### VP-37 — Close-time attempt when last commit was not followed
**Input:** run reaches close with an accepted final commit for which no attempt exists.  
**Expected:** one unconditional close-time attempt occurs against the final staged/closed state.

### VP-38 — No duplicate close-time attempt
**Input:** the final accepted commit was already followed by its attempt.  
**Expected:** close does not append a redundant second attempt solely because the run is closing.

### VP-39 — Structural tension identity is order-insensitive
**Input:** first failure identity is (S1, {dependency D, endpoint S}); later failure reports the same check and same records in reversed enumeration order.  
**Expected:** same identity; one open structural tension only; later finding attaches to it; no duplicate raise.

### VP-40 — Different affected set is a different identity
**Input:** two failures have the same check name but different affected record sets.  
**Expected:** distinct identities and distinct structural tensions. The second failure must not be merged into the first.

### VP-41 — Same-check resolution requires original affected set
**Input:** open tension T records identity (S1, {D1, S}). A later attempt passes S1 for {D2, S} but still fails S1 for {D1, S}.  
**Expected:** T remains open. Passing a different affected set cannot resolve it.

### VP-42 — Same-check resolution on original set
**Input:** open tension T records identity (S1, {D1, S}). A later attempt reruns S1 against exactly {D1, S} and establishes that inconsistency no longer exists.  
**Expected:** T transitions open→resolved, with the passing attempt event id as evidence. No assessment is involved.

### VP-43 — A different check passing cannot resolve
**Input:** T is (S1, {D1, S}); later S2 passes, while S1 is not re-run or still fails.  
**Expected:** T remains open. Resolution is check-specific.

### VP-44 — Repeat failure after correction is not silently ignored
**Input:** T is open; a correction appears to repair its affected set, but a subsequent same-check attempt still detects the original inconsistency.  
**Expected:** T remains open and the finding attaches to T. No transient pass or status transition may be inferred from an unverified state.

### VP-45 — TV-1 full genuine lifecycle
**Input sequence:** valid H replays to a consistent R; inject the S1 dangling-edge fault into L only by removing region S while leaving D-CS active; accept an ordinary contribution independent of S; evaluate B and L; then accept a genuine correcting contribution removing D-CS; evaluate the next B and L.  
**Expected sequence:** (1) replay before injection succeeds; (2) replay after injection still succeeds and remains unchanged; (3) first attempt fails S1 for D-CS and missing S, issues no seal, raises one checker-origin open structural tension; (4) open tension does not block correction or the next attempt; (5) correction is a genuine accepted contribution; (6) second attempt re-runs S1 against the original affected set and passes; (7) seal issues at its attempt position; (8) tension resolves with that attempt id as evidence; (9) event ordering and atomicity conform to VP-32. Any simulated status change without a passing same-check result fails this vector.

## 8. Facet, semantic-boundary, and authority vectors

### VP-46 — Seal does not change semantic tension status
**Input:** an open or examined semantic tension exists; all structural checks pass.  
**Expected:** seal may issue and records the tension as an outstanding semantic question. Tension status is unchanged.

### VP-47 — Checker cannot raise semantic tension
**Input:** checker finds a semantic contradiction in content but no structural invariant failure.  
**Expected:** checker raises no tension. Semantic tension creation remains an agent ExaminationReport or accepted contribution action under Rev 9.

### VP-48 — Engine cannot resolve structural tension through assessment
**Input:** an Assessment targets an open structural tension.  
**Expected:** Assessment is rejected with `structural_target`; no Assessment record and no structural status transition. Only a same-check passing seal attempt resolves it.

### VP-49 — Seal cannot certify completion or truth
**Input:** every structural check passes, but one required facet is unexamined or has an outstanding semantic tension.  
**Expected:** seal may issue; facet status remains governed only by Rev 9 §5; no completion or semantic truth certification is inferred.

## 9. Starvation report vectors

### VP-50 — Report includes every agent
**Input:** three authenticated crew agents; agent A has commits, agent B has only rejections, agent C has only IDLE events.  
**Expected:** report contains A, B, and C. No agent disappears because it lacks a successful commit.

### VP-51 — Consecutive rejection count resets only on defined progress
**Input:** sequence for A: rejection, rejection, accepted commit, rejection.  
**Expected:** report shows consecutive rejection run of 2 before the commit and 1 after it. Build notes must define whether other event types, including IDLE, affect this counter; the chosen rule must be deterministic and applied consistently.

### VP-52 — No-successful-commit metrics are defined
**Input:** B has rejections and IDLE events but no accepted commit.  
**Expected:** wakes-between-successful-commits and time-to-first-success are represented using an explicit not-yet-observed/null-or-censored convention, not omitted and not fabricated as zero. Rejection counts, consecutive rejections, and changed-read diffs remain reported.

### VP-53 — Changed-read diff sizes are derived from rejection evidence
**Input:** stale rejections contain changed-read diffs of sizes 0, 1, and 3 under the implementation's documented counting unit.  
**Expected:** report reproduces those values and documents the unit (regions, not bytes or tokens, unless the contract explicitly chooses otherwise). No recomputation from current state may rewrite historical diff sizes.

### VP-54 — Deterministic report
**Input:** same closed event history is supplied twice.  
**Expected:** byte-identical normalized report, including agent ordering and null/censored conventions. Report is derived only; no authoritative event or fabric state is mutated.

## 10. Pack execution and reporting contract

1. Both implementations receive the same immutable pack bytes and the same case inputs.
2. Each case is isolated. A case cannot inherit mutable state from a preceding case unless its setup explicitly says it is a continuation sequence.
3. Every case records: pack id/version/hash; implementation identity and build hash; case id; input fixture hash; observed result; expected result; pass/fail; diagnostic excerpt; and, for replay halts, exact offending sequence.
4. The runner must not let one implementation generate expected outputs for the other.
5. The pack's expected outcomes are normative. If Remmy identifies an ambiguity or defect, the pack is revised and re-hashed before either implementation is validated. No in-place edits after validation begins.
6. A passing pack does not prove semantic correctness, live-agent competence, full lifecycle completion, or overall commissioned-slice acceptance. It establishes only agreement with these specified mechanical contracts.
7. No run opens unless both implementations pass every required pre-open case. Any exception requires an explicit, versioned amendment to the pack and renewed examination; no case may be waived informally.

## 11. Authorship declaration

I authored this pack from the text of Rev 9, Amendment A1, and Stage 4 Design Brief Rev 2. I did not derive expected outcomes from the engine or checker source. The pack is submitted to Remmy for adversarial examination. It is not yet a pinned authority and does not authorize a build.

