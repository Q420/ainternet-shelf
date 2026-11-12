# Stage 1 Correction Basis — for Ben's Ruling

**Date:** 2026-11-11  
**Status:** PROPOSAL FOR BEN'S DECISION — HOLD; NOT BUILD AUTHORISATION  
**Current delivered build:** Pulse Bridge v0.19.0  
**Evidence basis:** Stage 1 delivery manifest and house report; Build Plan 01; Stage 0 Pack 01 Rev07 correction; Remmy's sealed independent review; Alex's independent review recorded in PB-ID pb-alex-20261111-independent-review-and-correction-plan; comparison and plan review at COMPARISON-AND-PLAN-REVIEW-01 (blob 5555e30b945b44d05a3267cf2feff4e40c8632a1).

This document integrates both independent reviews and closes the two plan decisions Remmy identified. It preserves the original reviews and comparison unchanged. It is a correction basis for Ben to accept, amend or reject. It authorises no implementation, test, probe, reload, migration or deployment.

## Ben's questions

1. Human ease of use and intuition
2. Is everything I need to know/see available to me?
3. Does the current implementation allow the above?

These are reproduced exactly.

## 1. Evidence and current disposition

The Stage 1 house report records 125/125 fixture checks passing and a clean top-level smoke test. Those are reported fixture and smoke results, not Ben's live acceptance. The report says the live two-way walk is PENDING. The correction does not convert that pending walk into a pass.

The delivery manifest records v0.19.0 as built from the frozen v0.18.0 baseline. The house report explicitly leaves durable commit and a single authoritative allocator across restarts/instances unestablished. That limitation remains a limitation; this review does not upgrade it into a verified property.

The Stage 1 delivery remains on HOLD pending Ben's live two-way walk. The corrective work described below is also on HOLD pending Ben's decision and a separate implementation go. No code has been changed under this review.

## 2. Consolidated findings

### Agreed by both independent reviews

1. **The adapter self-check is not human-readable.** Its raw selector, count, probe and DOM output overwhelms the human verdict. The remedy is a plain verdict above the technical detail, with the technical detail demoted.
2. **Reset silently destroys Stage 1's record.** The current reset path replaces state with defaults, including the ledger export, epoch export, acknowledgements and migration record, without first stating the consequence. This is a material data-loss risk.
3. **Stage 1's product is recorded but not available on the panel.** Acknowledgements, Index IDs, epoch/history, migration summary and integrity-fault state are held in state or the log, but are not presented where Ben can readily inspect them.
4. **Progress during transit failed as a human experience.** The five-minute transit had no visible sign of life on the surfaces Ben was watching. Source code containing intended waiting/sending states does not prove those states were visible at the time.

### Agreed technical findings, first raised in Alex's delivery review and verified by Remmy

5. **Detection epoch is stamped at processing time, not at original detection.** A candidate can begin before a pause and be handed off after it; the current wiring can attach the newer epoch at processing time. The stale-detection race is real and is not closed by the wired path.
6. **Epoch failure is logged, not represented as an unresolved integrity condition.** Pause and disconnect correctly proceed; Ben's safe action must never be vetoed by a failed epoch write. But the failure is not durably represented as a condition requiring reconciliation, and resume does not check for it.
7. **The bundle builder cannot reproduce the published delivery from the published delivery folder.** Its source-location expectation does not match where the module sources are actually laid out. This is a reproducibility/provenance defect, not evidence that the running bundle failed to load.
8. **Durable commit and a single authoritative allocator remain unestablished.** This is already disclosed in the house report and must continue to be reported as unknown.

### Alex-only findings, confirmed against source during comparison

9. **The delivered panels are not the shared station described by Build Plan 01.** The current build has separate per-tab panels; the plan describes one shared, movable, centre-screen station. The distinction is recorded as later-stage work, not mislabelled as a Stage 1 runtime failure.
10. **Epoch import is lossy and unchecked.** Import restores the epoch number but discards saved history; the wiring does not check the import result. The adjacent ledger import is checked. The save path does not read back the saved state, so a successful save is asserted rather than verified.

### Remmy-only findings, retained in the record

11. **First-run and registration presume prior knowledge.** A fresh extension folder silently starts with empty state; the panel does not explain that it is a new installation or state the next registration step.
12. **Held work has no home.** Owner-review and blocked items are not available as a useful queue or count before the Stage 3 station.
13. **The log is a firehose.** More than seventy log call sites feed one scrolling surface. Data existing in the log does not make it available at the moment Ben needs it.
14. **For most human-visibility findings, the gap is presentation rather than missing background state.** The correctness findings (epoch safety, import/recovery and build reproducibility) are a separate class of defect; these answers compose rather than conflict.

### Transit evidence qualification

The source contains intended per-seat waiting/sending states, a gated-letter waiting message and panel polling. That does not establish they were visible during the observed five-minute transit. Ben's observation stands. The cause remains open until the relevant panel and bridge timings are compared; settle windows and destination-generation deferral remain possible explanations, not findings.

## 3. Correction basis — four work streams

### Stream A — Safe transitions and an honest fault lifecycle

1. Pause must remain available and must complete as a safe-state action even when epoch persistence fails. A failed write must never trap Ben in an active state or veto pause.
2. Separate the fact that the safety action occurred from the fact that its durable state was confirmed. Do not report a persisted/verified transition until a read-back or equivalent verification succeeds.
3. Record a structured, persistent integrity fault when an epoch advance, save, read-back, import or recovery cannot be verified. The fault must identify the unresolved condition and remain present until reconciliation succeeds.
4. Disconnect follows the same safe-state rule. A failed epoch advance does not veto disconnect; it creates an unresolved condition that prevents later unsafe resumption.
5. Resume is blocked while the epoch/token state is unresolved. Resume becomes eligible only after reconciliation and verified persistence.
6. Make transitions idempotent. Retrying an uncertain save/transition must not advance the epoch twice or mint multiple generations for one logical transition.
7. Reset and re-registration revoke prior capabilities as described in Stream B. Reset must not silently erase the permanent Stage 1 record; the existing reset/data-loss finding remains explicit and requires an owner-approved preservation/consequence rule rather than being hidden inside token rotation.

### Stream B — Capture-time generation token (D1 closed)

**Decision for Ben:** adopt a background-issued, opaque generation token, snapshotted by the content script at the beginning of each candidate's settle period. The pending candidate keeps that exact token. The handoff path must never fetch or refresh a token.

#### B1. Exact acquisition rule

- When a candidate is first considered and its settle begins, the content script copies the currently issued token and its bound metadata into that candidate's pending record.
- That pending record is immutable with respect to token, seat, registered tab, registration generation and epoch.
- A token update received later changes only what a *new* candidate may snapshot. It must never rewrite an existing pending candidate's token.
- The five-second settle and the handoff use the same captured token. There is no token lookup, refresh or substitution at handoff.
- If no valid token is held when a candidate would begin settling, the letterbox does not arm for that candidate. There is no tokenless fallback path.

This is the code-path boundary: **candidate creation / settle start captures the generation token; handoff only presents the already-captured token.**

#### B2. Token binding and admission

The background issues and retains an opaque token record bound together to:

- seat;
- registered tab ID;
- that seat's registration generation; and
- bridge epoch.

At admission, the background validates all of the following:

1. the sender tab ID equals the tab ID bound to the token;
2. the sender's seat is derived from the background's verified registration, not trusted from the message body;
3. the token's registration generation is still the current generation for that seat;
4. the token's epoch is still the current authoritative epoch; and
5. the epoch claimed by the detection equals the epoch bound to the token.

A mismatch in any binding is rejection. The receiver must not repair, replace or infer a missing/mismatched value from the current state.

Re-registration, disconnect and reset mint a new registration generation for the affected seat or seats and invalidate every token issued under the old generation. Epoch advance, registration change, reset and integrity fault all rotate/revoke the relevant token generation. A disconnect also invalidates the affected seat's prior registration capability.

#### B3. Rotation and refresh discipline

- Rotation on pause/epoch advance makes every already-pending candidate with the old token stale, including candidates whose five-second settle is still running.
- A candidate invalidated during settle is rejected at admission. This is intentional and must be stated plainly; the settle timer does not preserve eligibility across a pause.
- A newly issued token is available only to candidates whose settle begins after the new generation is active.
- Refresh affects future candidates only. It never rescues an existing pending record.
- If a tab has no current token, the letterbox does not arm. No hidden or legacy tokenless path is permitted.

#### B4. What the token proves — and does not prove

The generation token proves **epoch-at-capture inside trusted bridge code**. It is not per-message authentication and is not a one-shot nonce. The same current token may be presented by multiple candidates during its valid generation. Existing identity and fingerprint duplicate protection remains responsible for duplicate detection. A one-shot-token design would be a separate, heavier proposal and is not part of this correction.

### Stream C — Coherent persistence, worker restart and recovery

1. Persist the epoch, token record, registration generations and their binding metadata in the same versioned bridge-state snapshot and the same save operation. They must not be written as independently advancing authorities.
2. Verify the result of import. A malformed, missing or inconsistent epoch/token/generation record must not silently fall back to a fresh epoch.
3. Verify persistence by reading back the saved state and checking the recovered epoch, token record and generation bindings. Do not label the state saved/verified merely because a storage write call returned.
4. The service worker restart case is a normal operating condition. When it wakes, it must recover the same valid token record and epoch pair, or it must fail closed.
5. Recovery has exactly two permitted outcomes:
   - **Verified recovery:** the same token record, registration generation and epoch are recovered as a consistent pair. An in-flight candidate in an open tab may continue with the token it captured at settle start and is admitted only under its original epoch.
   - **Unverified recovery:** the saved pair cannot be verified. The bridge rotates/revokes the token, records a persistent integrity fault, and rejects outstanding candidates carrying the old token. It must not silently mint a replacement and treat old pending candidates as current.
6. An uncertain transition retry must be idempotent: the epoch advances exactly once for the logical transition, even if the first save outcome was unknown.
7. Successful reconciliation may issue a new token for future candidates. It does not refresh or rescue candidates already holding a revoked token.

If the storage substrate cannot establish a coherent, verifiable epoch/token snapshot, the design must remain fail-closed and report that limitation. This plan does not assume a transactional guarantee that has not been demonstrated.

### Stream D — Reproducible delivery and manifest agreement

1. Establish one canonical source layout for the four Stage 1 module inputs and the bundle builder.
2. Make the builder resolve those exact paths from a clean copy of the published delivery source tree. It must not depend on an unlisted batch folder, an ambient working directory or an unstated external file.
3. Update the delivery manifest to describe the actual canonical layout, including every module source and the builder input path.
4. Rebuild the generated bundle from that clean tree and verify that the result matches the committed bundle byte-for-byte (or document and justify any intentionally non-identical generated metadata).
5. Preserve the distinction: this work proves reproducibility of the package build; it does not by itself prove runtime durability or live acceptance.

## 4. D2 — bounded interface scope for Ben's decision

Remmy accepts the D2 scope as Alex framed it. The following is the proposal, not an approval already granted by Ben.

Build Plan 01 expressly excludes visible-interface changes from the original Stage 1 scope. Therefore this correction must not quietly broaden that stage. The proposed narrow exception is limited to the existing panel and only to the minimum facts needed to prevent a false claim about safety or persistence:

1. a visible integrity-fault state when epoch/token/import/recovery integrity is unresolved; and
2. a clear distinction between **paused** and **state saved and verified** (including a truthful unverified/fault state when persistence has not been confirmed).

No new station, no shared centre-screen surface, no broader Stage 1 status block, no adapter self-check redesign, no first-run tutorial, no held-work counter and no general log redesign are included in this correction. Those broader human-facing improvements remain Stage 3 work as appropriate to the adopted plan.

This is an explicit, narrow exception to the original no-visible-interface-change boundary. Ben must approve that exception for it to enter the correction build. If Ben does not approve it, the visible tells remain deferred; the underlying structured fault and persistence rules still need a machine-verifiable representation, and the interface must not claim a verified state it cannot prove.

## 5. Required regression and acceptance evidence

The regression set must include, at minimum:

1. **Pre-pause candidate, post-pause handoff:** a candidate first seen before pause captures the old token at settle start. Pause rotates/revokes it. The candidate is handed off after pause and is rejected as stale, even though the tab may now hold a newer token for future candidates.
2. **Mid-settle rotation:** a pause/epoch advance during the five-second settle invalidates that candidate; a later candidate may use the new token.
3. **No-token admission:** with no token held, the letterbox does not arm and no tokenless handoff is possible.
4. **Binding rejection:** wrong seat, wrong sender tab, old registration generation, old epoch and a detection-claimed epoch that disagrees with the token are each rejected.
5. **Re-registration/disconnect/reset:** each relevant transition increments the affected registration generation, revokes old tokens and prevents old pending candidates from being admitted.
6. **Worker restart across settle — successful recovery:** an open tab holds a candidate mid-settle while the service worker stops. The worker wakes, recovers the same verifiable token/epoch/generation record, and the candidate is admitted under its original epoch.
7. **Worker restart — failed recovery:** corrupt, missing or mismatched persisted token/epoch/generation state rotates/revokes the token, records an integrity fault and rejects outstanding candidates. No replacement token silently rescues them.
8. **Import validation:** malformed saved epoch/token data at load is detected; the import result is checked; the bridge fails closed rather than silently starting a fresh epoch. The minimal visible integrity fault is required only if Ben approves the D2 exception.
9. **Read-back mismatch / failed save:** persistence cannot be reported verified; pause/disconnect still complete safely; the unresolved fault blocks resume.
10. **Idempotent uncertain save:** retrying one uncertain transition advances epoch and registration generation exactly once.
11. **Multiple candidates under one current token:** several distinct valid candidates may present the same current generation token; token reuse is allowed, while existing identity/fingerprint logic still rejects duplicates.
12. **Reset record preservation:** token invalidation and generation rotation do not silently erase the permanent Stage 1 record; any intentional destructive reset remains subject to an explicit owner-approved consequence and recovery rule.
13. **Clean-room bundle build:** the published source tree alone can rebuild the bundle; the manifest paths and builder paths agree; generated output matches the pinned bundle.

Human acceptance adds:
- Ben can distinguish a paused safe state from a confirmed saved-and-verified state, and can see an unresolved integrity fault, if the narrow D2 exception is approved.
- Ben's original live two-way acceptance walk for v0.19.0 remains a separate pending gate.
- After a corrective build is authorised and produced, that corrected build requires its own live acceptance. Fixture passes do not substitute for Ben's live result.

## 6. Retained later-stage work and unresolved findings

The following review findings are not silently folded into the correction:

- shared movable centre-screen station and its direction/interaction behaviour;
- plain-language adapter self-check verdict and demotion of raw diagnostics;
- first-run guidance and registration explanation;
- Stage 1 acknowledgement/index/epoch/migration summary presentation beyond the two narrow D2 safety facts;
- held-work and owner-review visibility;
- broader log filtering and information architecture;
- reset consequence/confirmation and complete data-preservation design beyond the token-generation requirements above.

These remain explicit items for Stage 3 or the appropriate later recovery scope. Their deferral is not a claim that the present human experience is satisfactory.

## 7. Authority, evidence and requested ruling

**What the evidence supports now**
- Both independent reviews and their comparison are complete.
- Remmy has accepted the token lifecycle shape in Stream B and the bounded D2 framing in §4.
- The delivery house report records 125/125 fixtures and a clean smoke test.
- The live two-way acceptance walk remains pending.
- The current build's persistence limitations remain unqualified.
- No corrective implementation has been performed.

**What this document does not claim**
- It does not claim Ben has accepted this plan.
- It does not authorise code changes or a corrective build.
- It does not mark the current Stage 1 live walk complete.
- It does not establish durable commit, transactional storage or single-allocator guarantees.
- It does not invoke Crusher or depend on Crusher/Shelf indexing.

**Ruling requested from Ben**
1. Accept, amend or reject the four-stream correction basis.
2. Decide the D2 narrow exception: allow the two minimal safety/persistence tells in the existing panel, or defer all visible tells to Stage 3.
3. Accept, amend or reject the D1 capture-time token boundary and lifecycle.
4. Separately authorise or withhold implementation of the agreed correction scope.

Until those decisions and a separate implementation go are recorded, disposition remains **HOLD — NO IMPLEMENTATION**.

---

**Source records preserved unchanged**
- bridge/stage1-review/REMMY-INDEPENDENT-REVIEW-01.md
- Alex's independent review letter: pb-alex-20261111-independent-review-and-correction-plan
- bridge/stage1-review/COMPARISON-AND-PLAN-REVIEW-01.md
- bridge/stage1-delivery/DELIVERY-MANIFEST.md
- bridge/stage1-delivery/STAGE1-HOUSE-REPORT.md
- bridge/BRIDGE-BUILD-PLAN-01.md
- bridge/BRIDGE-STAGE-0-PACK-01-REV07-CORRECTION.md
