# Pulse Bridge — Stage 1 Batch 1 — Evidence (Revision 4)

Supersedes Revision 3 (commit 965ae6bb616df94d774d6b2bea7f07220b7751a4);
all earlier revisions remain in git history at their commits.

**Revision crossing, stated plainly:** Alex's review
(pb-mwd0k57e) was of Revision 2 (commit f6fede75). Revision 3
(the claim-store hardening, Ben's fix-the-family ruling) was
already shelved when that review arrived and is NOT part of
what he reviewed. This Revision 4 is Revision 3 PLUS the
classification correction he requested from Revision 2.

**The correction:** required-string fields now classify
honestly. Genuinely absent (undefined) is *-missing; explicit
null, a non-string value, or an empty string is *-invalid.
Revision 2's branches collapsed explicit null into *-missing
for platform, messageId and occurrence (and conversation where
required), contradicting the fieldState distinction the same
revision introduced. A single helper (requiredStringReason)
now classifies all required-string fields uniformly. The
global-scope conversation: null allowance is preserved exactly:
explicit null there remains valid and encodes -1:; absent
remains conversation-missing; non-string remains
conversation-invalid. Six new fixtures assert the REASON
values, not only the status, as requested.

Alex's Rev2 review record: the three requested corrections
substantially in place; builders reject coercion; scope exact;
commit contained only the three batch paths. His evidence
note stands: the run output is Remmy-reported; he reviewed
source and fixtures against it and did not independently
execute the suite.

## Files and content hashes (SHA-256), Revision 4

- `identity.js` — 02ea08c0e97e918168a3eacfec6baf140d71ca5befa9dd2dbb018aefd68ee467
- `identity.fixtures.js` — 252a64b6f191b152b465fe4b3ccb7d0a3fd5de10e0eaae4b5a3e83ccc832039a

## Basis pins

Unchanged: Build Plan 01 blob
8196d44ea60541855b4c069ea8e46a811adad13c; Stage 0 Pack Rev06
commit 78bfe0008a536ca62ce7c16b7243729f0a50b738, blob
7685099a42e7a7ab566be7ea790fadae7c6a3c8a; Rev07 chunk commit
76c036ceba72df3726be183d28275692f0164a93, blob
2b4e3b3ebb343360514bfe4164941a27dd2078a9; source baseline
commit e4c855c06beaba449a47281292496bad81d3b468, blob
388754b23069b70f1f1a5b0dc001dc90b87950ce.

## Working-tree integrity

Additions remain exactly `identity.js` and
`tests-stage1/identity.fixtures.js`; no baseline file differs;
no wiring; manifest unchanged.

## Test evidence (tied to this exact revision)

Command: `node tests-stage1/identity.fixtures.js`
Runtime: Node v24.22.1. Exit code: 0. 44 fixtures: 38 of
Revision 3 plus 6 reason-classification fixtures.

```text
PASS  vector 1 (published): chatgpt native digest matches SS1.7
PASS  vector 1 (published): canonical preimage bytes are exact
PASS  vector 2 (published): metaai native digest matches SS1.7 (algorithm example)
PASS  occurrence form: module digest equals independent node-crypto digest of hand-written preimage
PASS  same source occurrence re-fetched derives the same PB-ID
PASS  sender/body are not identity inputs: same source key with different body metadata, same PB-ID
PASS  distinct occurrence IDs with identical sender/body derive different PB-IDs
PASS  same occurrence with edited payload keeps the same PB-ID (occurrence form)
PASS  conversation-scoped native ID with missing conversation is IDENTITY-UNKNOWN
PASS  globally scoped native ID with null conversation derives OK and encodes -1:
PASS  null conversation and empty conversation encode differently (-1: vs 0:) and derive different PB-IDs
PASS  native form with no message ID is IDENTITY-UNKNOWN (no discriminator)
PASS  native form with empty message ID is IDENTITY-UNKNOWN
PASS  occurrence form with missing occurrence discriminator is IDENTITY-UNKNOWN
PASS  occurrence form with missing conversation is IDENTITY-UNKNOWN
PASS  missing platform is IDENTITY-UNKNOWN
PASS  hash service failure is IDENTITY-UNKNOWN, never a throw (fail-closed)
PASS  UTF-8 byte lengths: precomposed e-acute counts 2 bytes
PASS  no Unicode normalisation: decomposed e-acute counts 3 bytes and derives a different PB-ID
PASS  supplementary-plane character counts UTF-8 bytes (4), not UTF-16 units (2)
PASS  whitespace inside a value is preserved, never trimmed or collapsed
PASS  delimiter-looking content inside a value cannot forge a field boundary
PASS  claim store: first claim is CLAIMED, identical re-claim is MATCH
PASS  forced digest collision: a second, different source key at the same PB-ID is IDENTITY-COLLISION and never overwrites
PASS  claim record retains canonical source-key material only — no body, no payload
PASS  missing conversation FIELD (absent, not null) under global scope is IDENTITY-UNKNOWN
PASS  explicit null conversation under global scope still derives OK (null is stated, not absent)
PASS  missing scope is IDENTITY-UNKNOWN — never silently defaulted
PASS  invalid scope values are IDENTITY-UNKNOWN (wrong case, non-string)
PASS  numeric message ID is rejected, never coerced to a string
PASS  numeric platform is rejected, never coerced
PASS  object conversation value is rejected, never coerced
PASS  explicitly undefined message ID is IDENTITY-UNKNOWN
PASS  occurrence form: missing conversation field is IDENTITY-UNKNOWN, distinct from a stated value
PASS  canonical builder itself refuses coercion: numeric field value throws TypeError
PASS  canonical builder refuses a missing (undefined) field but accepts explicit null
PASS  claim store refuses a non-string canonical, never coerces it into the record
PASS  claim store refuses a missing canonical and a non-string PB-ID
PASS  reason: explicit null platform is platform-invalid; absent platform is platform-missing
PASS  reason: explicit null message ID is message-id-invalid; empty message ID is message-id-invalid
PASS  reason: explicit null occurrence is occurrence-invalid; absent occurrence is occurrence-missing
PASS  reason: explicit null conversation under conversation scope is conversation-invalid
PASS  reason: empty conversation under conversation scope is conversation-invalid
PASS  reason: explicit null conversation in occurrence form is conversation-invalid

identity.fixtures: 44/44 passed, 0 failed
```

## Scope

Stage 1 scope item 1 (identity layer), corrected. Batch 2
waits for Alex's review of this revision. No live proof
claimed; Ben's live two-way walk remains the stage acceptance.

— Remmy, 2026-11-11.
