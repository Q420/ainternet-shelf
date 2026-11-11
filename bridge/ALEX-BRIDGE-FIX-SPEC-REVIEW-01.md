# PULSE BRIDGE FIX SPECIFICATION 01 — ALEX'S INDEPENDENT REVIEW

**Status:** REVIEW COMPLETE — SPECIFICATION NOT CLEARED FOR BUILD; BEN'S CLARIFICATIONS REQUIRED  
**Reviewed artefact:** `bridge/BRIDGE-FIX-SPEC-01.md` at commit `34baaee`, Git blob `bfac750425ffa77fa0277d154865a593415f9800`  
**Basis independently inspected at the same commit:**
- `bridge/fence.js` — blob `3de08507fb7a38eefca411a9341b7eb5ed9bb405`
- `bridge/sendcore.js` — blob `3970724b2e037aa28d2c934d04dc889788e58190`
- `bridge/background.js` — blob `8a6d503d21b032121a1e17b5647876bcdd6b300b`
- `bridge/storage.js` — blob `3929360e6f5b646abde195ff35a447958ed386e6`
- `bridge/crusher.js` — blob `ca8ab8246333256f326b572786d31aef3ef489f`
- `bridge/letterbox.js` — blob `18bc9a2b9a4732492774ddfee50d7d93e2cd0092`
- `bridge/TEST-REPORT-v0.18.0.md` — blob `117f5684557fce46184781bb924872947d353d71`

**Evidence class:** Alex source-inspected the cited Shelf files at the pinned commit and reviewed the specification. No code was changed, no tests were run, no live two-surface behaviour was observed, and no build is authorised by this review.

---

## 1. Overall disposition

The specification captures the requested F-1 through F-10 work and correctly marks the Gemini sidebar hook as deferred and the message-substitution incident as Remmy-side rather than bridge transport. It is a useful scope document, but it is **not yet build-ready**.

The main blockers are semantic collisions with existing fence and pair-machine behaviour. They should be resolved in the specification before implementation, not left for a developer to interpret.

The highest-risk issue is F-2: the current fence represents both a non-veto HOLD and a proven NEGATIVE veto as `action: "hold"`. The proposed force-send says it overrides a fence HOLD. Unless the specification distinguishes those cases, force-send could override a proven stop condition, out-of-order message, or already-delivered status. That would conflict with Ben's STOP-above-quorum rule.

No build clearance is given.

---

## 2. Blocking clarifications

### B1 — F-2 force-send must distinguish HOLD from VETO

**Current source:** `fence.js` defines the fence as three conditions (button, serial, status). Any NEGATIVE vetoes; two positives and no negative permit send. `pbFenceVerdict()` returns `action: "hold"` both when a negative exists (with `veto`) and when the result is merely insufficient/unknown. The background checks the bridge pause before consulting the fence.

**Specification issue:** F-2 says force-send overrides a fence HOLD, while the same document says Ben's STOP stands above every mechanism. "HOLD" currently covers materially different cases.

**Required resolution before build:**
- Define separate outcomes for a non-veto hold (for example, insufficient positives/UNKNOWN) and a proven-negative veto.
- State exactly which non-veto holds Ben may override.
- State that force-send cannot override Ben's STOP, bridge pause/disconnect, a proven stop-face/generating condition, already-delivered/acknowledged status, abandoned status, or a superseded/out-of-order message unless Ben explicitly rules otherwise.
- Preserve the actor, reason, exact message ID, prior verdict and override result in the journal.

**Question for Ben:** Does force-send override only a non-veto HOLD, or may it override any fence HOLD including a proven NEGATIVE veto? My technical recommendation is non-veto HOLD only; STOP and proven negatives remain absolute.

### B2 — F-5 button UNKNOWN conflicts with the existing two-of-three rule

**Current source:** `fence.js` states: at least two positives and no negative means send; UNKNOWN does not count as a pass. Therefore, if button is UNKNOWN but serial and message status are both positive, the existing rule permits send. This is distinct from a button read incorrectly as NEGATIVE, which vetoes.

**Specification issue:** F-5 correctly requires absent/unreadable button to be UNKNOWN, never NEGATIVE. However, its regression requirement says the listed cases must each produce "hold-for-unknown with 20s recheck." That appears to require the button to be a mandatory condition, even where the other two conditions are positive. This differs from the stated two-of-three rule and from Ben's reported concern that the fence was not honouring that rule.

**Question for Ben:** When button status is UNKNOWN, should the fence:
- preserve the two-of-three rule (send if serial and message status are positive, with no negative); or
- require button status itself to become positively readable before sending, holding and rechecking every 20 seconds?

The specification must choose one explicitly. Do not implement both interpretations in different paths.

Also define the exact difference between:
- button positively observed as STOP (NEGATIVE);
- button absent/unreadable (UNKNOWN);
- button positively observed as SEND (POSITIVE).

### B3 — F-3 purge must preserve uncertain external side effects

**Current source:** the pair machine persists one active pair, its call/reply/pending reply and a one-message buffer. Crusher distinguishes pre-send failures from post-click UNVERIFIED outcomes. After the send click, it does not treat a missing receipt as proof that nothing happened.

**Specification issue:** F-3 says pause/disconnect removes in-flight items and that resume starts from a purged state. A message already clicked into an external destination cannot be recalled by clearing local state. If its delivery is uncertain, deleting its identity and evidence can make a duplicate possible after resume.

**Required resolution before build:**
- Define "in-flight" by stage: queued/not engaged, typed/not clicked, clicked/awaiting receipt, confirmed, failed, unknown.
- Purge local pending work and page caches as authorised, but do not erase the durable evidence/identity of a post-click uncertain send.
- Preserve enough ID-only journal state to prevent accidental replay where Ben's retention ruling requires it.
- Resume must not silently resurrect a pre-purge queued item, nor silently forget an item that may already have reached the destination.
- The F-4 journal exception and the fate of existing serial/order state must be resolved together.

### B4 — F-4/F-10 journal must be reconciled with existing ledgers and caps

**Current source:** `storage.js` currently has distinct structures: `seenIds`, `deliveredIds`, `deliveryFailedIds`, legacy fingerprint ledgers, `completedSerials`, active detections, and pair/buffer state. Current caps include 300 for seen/delivered IDs, 50 for detections and completed serials, and 300 for legacy seen/delivered arrays. `fence.js` caps completed serials at 50.

**Specification issue:** F-4 proposes one 20-message, ID-only, both-directions ring journal as the primary duplicate guard; F-10 says the old completed-serial registry must be re-specified against it and no cache survives purge except the named journal. The specification does not yet define migration, precedence, or the relationship between message-ID duplicate protection and serial ordering.

**Required resolution before build:**
- Define journal insertion points and statuses for outgoing and incoming IDs.
- Define when an ID is considered SENT, DELIVERED, RECEIVED, QUARANTINED, FAILED or merely OBSERVED; do not conflate sent with delivered.
- Define precedence between the journal, active pair, buffer, `seenIds`, `deliveredIds`, `deliveryFailedIds` and `completedSerials`.
- Decide whether the existing completed-serial structure is retired, derived, or retained for ordering only. The serial counter/order mechanism is not the same thing as a duplicate-ID cache.
- Define migration of existing records into the new journal without falsely marking uncertain/failed messages delivered.
- State exactly what the 20-entry eviction window can and cannot guarantee.

### B5 — F-6 truncated delivery must not poison a later complete retry

**Specification issue:** F-6 says a truncated payload is quarantined and refused as a whole, while F-4 says an incoming ID already recorded as delivered must not be presented again. The specification must ensure that observing/quarantining a truncated message does not mark its ID as successfully delivered and then cause a later complete copy with the same ID to be discarded as a duplicate.

**Required resolution before build:**
- Separate observed/quarantined ID from successfully delivered/accepted ID.
- Preserve both lengths and the same message ID.
- Define whether a later complete payload with that ID may be re-evaluated and accepted.
- Define how divergent complete copies with the same ID are handled (conflict/UNKNOWN, not silent overwrite).

### B6 — F-8 buffer semantics exceed the current one-message buffer

**Current source:** `storage.js` and `background.js` describe a single `bufferId` (newest wins), plus one pending-reply slot. Retiring a pair promotes that one buffered message into the next pair. F-8 instead requires multiple outbound messages to be buffered in order and released as one message after the reply.

**Required resolution before build:**
- Define the buffer as a persistent ordered collection, not the current single `bufferId`.
- Define whether the released message is one composite envelope with a batch ID and embedded original IDs, or one text payload preserving each original PB-ID as independently identifiable submessages.
- Preserve each original message's identity, order, author, content and provenance; dedup/retry must not operate only on the composite ID.
- Define overflow, restart recovery, partial write, duplicate release and superseded-pair behaviour.
- Clarify whether this changes the one-active-pair/newest-wins rule or is a bounded exception to it.

### B7 — F-9 "head of queue" must be mapped to the pair machine

**Current source:** v0.18.0 is built around one active pair and a one-message buffer, not a general FIFO queue. `sendcore.js` currently waits up to 45 seconds while the composer reports generating, then returns a failed result with "nothing engaged, typed or clicked." Crusher's lifecycle has GATED/STOPPED/RETRY_WAIT and explicit recovery behaviour.

**Specification issue:** F-9 says the letter returns to the "head of the queue" at the 45-second ceiling. There is no ordinary multi-item queue head in the current pair model.

**Required resolution before build:**
- Define whether the current pair remains open and its current letter is re-armed, parked as GATED/RETRY_WAIT/STOPPED, or returned to a newly specified ordered queue.
- Preserve its PB-ID and attempt history; do not create a new identity for the same letter.
- State whether the one-message buffer can progress while the active pair is deferred.
- Define restart recovery and the exact visible state/timer.
- Treat UNKNOWN composer state separately from positively generating and positively ready state. The current `pbWaitForDestinationIdle()` loop waits only while the state is "generating"; an UNKNOWN state exits that loop as if not generating. The later send path has further checks, but the specification should state the required end-to-end fail-closed behaviour for UNKNOWN rather than relying on incidental later failure.

---

## 3. Additional implementation clarifications

### F-1 — transit animation
Bind the animation to actual lifecycle events, not queue insertion or a guessed direction. Define whether "transit starts" means send attempt, confirmed click, or a later transport event. The visual must distinguish in-transit, confirmed, and failed/unknown outcomes. It must not imply successful delivery merely because the animation completed.

### F-7 — composer ownership
The acceptance criterion is correct and important. Specify the exact ownership/identity rule for Ben's manual typing composer and the bridge's destination composer. Test that the bridge never types, clears, pastes into, focuses or otherwise mutates Ben's active manual composer. Also test that a global fallback selector cannot select a different composer when the intended named composer is missing or ambiguous.

### F-10 — bounded detection claim
The 20-ID journal is a bounded duplicate guard, not lifetime deduplication. The UI/log must state the exact window and what happens after eviction. Do not describe it as preventing all duplicates. Reconcile it with the existing 50-entry completed-serial record and the active-pair history-absorption path; do not leave two overlapping systems with different retention semantics and no declared authority.

### Whole-spec acceptance
The whole-spec live walk names F-1, F-2, F-3, F-5 and F-7. Keep the individual F-item acceptance tests for all ten items. The test plan should separately label fixture-only checks, controlled restart/persistence checks, and Ben-observed live two-surface checks. A fixture pass cannot be described as live acceptance. The v0.18.0 report itself records that live proof had not yet been established and that its recovery R9 case was a timing flake under load.

---

## 4. Recommended order before any build

1. Ben rules on B1 (force-send boundary) and B2 (UNKNOWN button versus two-of-three).
2. Remmy/Alex revise the specification to resolve B3–B7 and the F-1/F-7/F-10 implementation contracts.
3. Build a traceability matrix mapping each F-item to source location, changed behaviour, fixture cases, persistence/restart cases and live acceptance.
4. Have an independent reviewer inspect the revised specification and test matrix.
5. Only then seek Ben's explicit build authorisation under the normal gate.

No code changes, tests, extension reloads or live actions are authorised by this review.

---

## 5. Review conclusion

**Disposition: RETURN FOR SPECIFICATION CLARIFICATION.**

The requested work is identifiable, but F-2 and F-5 currently admit incompatible interpretations of the existing safety fence. F-3/F-4/F-6/F-8/F-9/F-10 also need lifecycle and persistence contracts before implementation. Resolving these in the paper first is cheaper and safer than discovering them as build-time patches.

*End of independent review. No build authority granted.*
