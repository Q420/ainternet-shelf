# PULSE BRIDGE FIX SPECIFICATION 01 — ADDENDUM RE-REVIEW

**Status:** PARTIAL ACCEPTANCE OF CLARIFICATIONS — RETURN FOR REMAINING SPECIFICATION WORK; NOT CLEARED FOR BUILD  
**Base specification:** `bridge/BRIDGE-FIX-SPEC-01.md`, commit `34baaee`, blob `bfac750425ffa77fa0277d154865a593415f9800`  
**Alex's initial review:** `bridge/ALEX-BRIDGE-FIX-SPEC-REVIEW-01.md`, commit `476d673984a0c876c6c9ad28b3ba15bf9ecf9385`, blob `45bebf4fe2dc66d911b7e737a791c5611fe985f3`  
**Clarifications addendum:** `bridge/BRIDGE-FIX-SPEC-01-CLARIFICATIONS.md`, commit `4fdda24`, blob `b000cc9dc734f895852e99f47c0463598851d486`.

**Review basis:** Alex compared the addendum against the base specification, the initial review and the source pins recorded in the initial review. This is a document-level re-review. No source code was changed, no tests were run, no live two-surface behaviour was observed.

---

## 1. Disposition

The addendum resolves several of the semantic conflicts identified in the first review. It is a material improvement and should be incorporated into a revised, consolidated Bridge Fix Specification.

It does **not** yet close every issue required for build readiness. The following are resolved at design level, subject to incorporation and testable wording:
- F-2 force-send classes and never-bypass conditions;
- F-3 deliberate-pause versus crash/restart semantics, including dispatched-but-unconfirmed late confirmation;
- F-4 journal dispositions and persistence across restart;
- F-6 completeness metadata and incomplete-delivery disposition;
- F-8 constituent identity within an aggregate;
- F-10 one authoritative duplicate mechanism, with completed serials limited to pair bookkeeping.

Remaining issues:
- Ben's journal-survival ruling for deliberate pause is explicitly reserved and unresolved.
- The completeness trailer changes the letter protocol and is not adopted merely by appearing in the addendum.
- F-5 now says UNKNOWN means hold/recheck, but that must be reconciled explicitly with the base specification's two-positive/no-negative quorum rule.
- F-9 still lacks a precise pair-machine state/recovery contract for the 45-second defer ceiling.
- F-1 transit event semantics and F-7 composer ownership need exact implementation contracts.
- The proposed ordered multi-letter buffer needs a complete persistence/overflow/recovery contract before build.

No build clearance is given.

---

## 2. Finding-by-finding disposition

### F-2 — Force-send boundary: RESOLVED AT DESIGN LEVEL

The addendum restricts force-send to:
- fence HOLD caused by UNKNOWN with no veto;
- defer-ceiling return-to-queue;
- pair state unverifiable after restart.

It prohibits bypassing:
- Ben's STOP or paused/disconnected state;
- a proven negative veto / positively observed stop-face;
- already journalised delivered IDs;
- incomplete/truncated messages;
- superseded pairs.

This resolves B1. The distinction between non-veto HOLD and proven-negative veto is now explicit. The revised base specification must preserve the full enumerated never-bypass list and require an auditable actor, reason, message ID, prior verdict and override result. A force-send must not erase or rewrite the prior fence result.

### F-3 / F-8 — Event-class lifecycle: SUBSTANTIALLY RESOLVED

The addendum now distinguishes:
- deliberate pause/disconnect by Ben: purge queue, pair state, inbound cache and outbound buffer, with constituent IDs announced before destruction;
- crash/restart: persist and re-verify the buffer, then release only under F-8;
- restart while paused: recover into paused state without resurrecting purged work.

It also correctly recognises that an already-dispatched send cannot be recalled. Such an item becomes DISPATCHED-UNCONFIRMED; a late confirmation becomes DELIVERED-LATE; it is never resent.

This resolves the earlier contradiction between pause-purge and crash-persistence by assigning different semantics to different events. Two matters remain:
1. Ben's ruling on whether the ID-only journal survives deliberate pause remains open. The addendum does not decide it.
2. The revised specification must state the exact durable state retained for DISPATCHED-UNCONFIRMED and DELIVERED-LATE, and how it interacts with the journal-survival decision.

### F-4 — Journal dispositions: SUBSTANTIALLY RESOLVED

The addendum defines direction-specific entries and distinct dispositions ATTEMPTED, SENT, RECEIVED and DELIVERED, with RECEIVED-INCOMPLETE and DELIVERED-LATE sub-states. It says duplicate protection keys on DELIVERED inbound and SENT-or-later outbound, and that the journal persists across restart.

The revised specification must make the state transitions explicit and avoid ambiguous "SENT-or-later" shorthand where a disposition may be failed, quarantined or uncertain. In particular:
- RECEIVED-INCOMPLETE must remain eligible for a later complete re-evaluation under the same ID;
- DISPATCHED-UNCONFIRMED must never be resent;
- DELIVERED-LATE must close the uncertain delivery without creating a second send;
- journal eviction must be oldest-first, logged, and always described as a last-20-ID bounded protection window.

Journal survival across deliberate pause remains Ben's decision.

### F-5 — UNKNOWN button: CLARIFICATION RECORDED, QUORUM WORDING STILL NEEDS RECONCILIATION

The addendum records that absent/unreadable button state is UNKNOWN, never NEGATIVE; UNKNOWN produces a hold with recheck; only a positively observed stop-face produces a negative veto.

That resolves the false-negative classification and the veto semantics. However, the base specification still states that two positives and no negative permit send. With serial and message status positive and button UNKNOWN, that quorum would be satisfied. The addendum's explicit UNKNOWN → HOLD instruction appears to establish a more restrictive rule.

The consolidated specification must say plainly which rule governs:
- **Option recorded in the addendum:** UNKNOWN button always causes a non-veto HOLD and recheck, even if the other two conditions are positive.
- **Alternative implied by the base quorum:** two positives and no negative permit send despite the third condition being UNKNOWN.

I will not silently infer that the old quorum rule has been amended. The addendum states Ben's F-5 confirmation is recorded; please ensure the exact chosen rule is stated as Ben's ruling in the revised specification, including whether it supersedes the generic two-of-three formula for this condition. No implementation should choose between these by interpretation.

### F-6 — Completeness contract: TECHNICALLY SPECIFIED, PROTOCOL ADOPTION OPEN

The addendum requires a declared total character length, block count and full body SHA-256, verified before presentation. Mismatch means quarantine and RECEIVED-INCOMPLETE, never DELIVERED.

This resolves the earlier ambiguity between quarantining a truncated message and poisoning a later complete copy. The revised specification must additionally define:
- exact trailer grammar and canonical byte/character encoding;
- whether hashes cover the exact body bytes before or after newline normalisation;
- duplicate complete copies with same ID and same digest;
- same ID with divergent complete digest (conflict, not overwrite);
- later complete retry after RECEIVED-INCOMPLETE;
- how block count and character length are measured.

The addendum explicitly says trailer adoption is a protocol decision for Ben and Alex, not assumed. It is therefore not yet authorised for implementation.

### F-8 — Aggregate identity: PARTIALLY RESOLVED

The aggregate manifest lists each constituent PB-ID in order; each constituent is journalised individually; acknowledgements and deduplication resolve per constituent; aggregate transport ID is routing-only.

The consolidated specification must still define:
- exact manifest syntax and integrity binding;
- constituent content integrity (not IDs alone);
- aggregate partial-send/partial-receive behaviour;
- constituent order and duplicate handling;
- what happens if one constituent is incomplete or conflicts;
- how the persistent buffer handles overflow and recovery.

The addendum resolves identity layering, not the complete buffer implementation contract.

### F-9 — 45-second defer and restart: NOT YET RESOLVED

The addendum permits force-send for a "defer-ceiling return-to-queue" but does not define the actual pair-machine state at the 45-second ceiling.

Required before build:
- whether the same pair remains active, is parked, or is closed/requeued;
- exact state name and allowed transitions;
- preservation of PB-ID and attempt history;
- whether the one-active-pair rule remains;
- whether a buffered outbound aggregate can progress while the current pair is deferred;
- restart recovery when pair state cannot be verified;
- treatment of UNKNOWN composer state end-to-end.

"Return to queue" cannot remain metaphorical where the existing system is a pair machine rather than a general FIFO queue.

### F-1 — Transit animation: OPEN

The addendum does not define the lifecycle event that starts transit or distinguishes sent, received and confirmed. The animation must be driven by evidenced state transitions and must not visually imply delivery merely because a send attempt or animation completed.

### F-7 — Composer ownership: OPEN

The addendum does not add the required ownership contract. The revised specification must name the exact composer identity/selector rule for the bridge destination, make Ben's manual composer read-only to bridge automation, and fail closed if the intended composer is missing or ambiguous. A global fallback must not select another composer.

### F-10 — Duplicate mechanism: RESOLVED AT DESIGN LEVEL

The 20-ID review journal is the sole authoritative duplicate mechanism in both directions. The 50-entry completed-serial registry is pair bookkeeping only and makes no duplicate-protection claim. Its cap bounds pair-history depth and must be described honestly.

The revised specification must retain this separation and ensure no legacy seen/delivered/fingerprint cache continues to act as a second, undeclared dedupe authority. Migration and precedence for legacy state must be specified before implementation.

---

## 3. Required next revision

Remmy should consolidate the base specification and addendum into one revised specification, preserving the addendum as a linked source record rather than leaving two competing documents.

The revision must include:
1. explicit F-5 ruling against the two-of-three wording;
2. Ben's deliberate-pause journal-survival decision, or mark it unresolved and block the relevant implementation scope;
3. F-6 trailer grammar and protocol-adoption decision;
4. complete F-8 aggregate/buffer state and recovery contract;
5. F-9 exact pair-machine state model;
6. F-1 lifecycle event mapping;
7. F-7 composer ownership and fail-closed selection;
8. F-4 journal state-transition table, including incomplete, dispatched-unconfirmed and late-confirmation cases;
9. F-10 legacy-state migration and one-authority dedupe rule;
10. a traceability matrix mapping F-1…F-10 to source, requirements, fixture tests, persistence/restart tests and Ben-observed live tests.

The independent reviewer must then inspect the consolidated specification and matrix. No build should begin merely because the clarifications addendum is accepted.

---

## 4. Final disposition

**PARTIAL ACCEPTANCE — CLARIFICATIONS INCORPORATED IN PRINCIPLE; CONSOLIDATED SPECIFICATION REQUIRED.**

The addendum resolves the central force-send safety conflict and the pause-versus-crash lifecycle contradiction. It does not grant build authority. The outstanding protocol, pair-state, composer-ownership and journal-survival matters must be resolved in the specification first.

*End of addendum re-review.*
