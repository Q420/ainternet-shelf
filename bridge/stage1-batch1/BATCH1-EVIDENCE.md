# Pulse Bridge — Stage 1 Batch 1 — Evidence (Revision 2)

This revision supersedes the batch 1 evidence shelved at commit
40fb2be3b7e4def9b09c1c2953b3e999fe98ef27 for the same three
paths. The Revision 1 files and their 25/25 run remain in git
history at that commit; nothing is rewritten.

**Correction applied** (Alex's batch 1 review, pb-mwd0g04w —
identity contract HOLD): the input contract no longer coerces
or defaults. Undefined (missing) field values are distinguished
from explicit null and rejected where a value is required;
non-string field values are rejected, never coerced, both in
deriveFromSourceKey and in the canonical builders themselves
(TypeError at the pure layer); native scope is required and
must be exactly 'global' or 'conversation' — missing or invalid
scope is IDENTITY-UNKNOWN, never silently defaulted. Scope
check at that review: PASS. Evidence note: the 25/25 was
Remmy-reported; Alex did not independently execute the suite.

## Files and content hashes (SHA-256), Revision 2

- `identity.js` — 150ba2b93d1e6ee5db2cbf37a15395422de88af3422183cb6cf7f4a9617263be
- `identity.fixtures.js` — 74c6f8ea41da40e066c431abe8ec5275159cfbbf6fa172e172432fc75774ad35

## Basis pins

Unchanged from Revision 1: Build Plan 01 blob
8196d44ea60541855b4c069ea8e46a811adad13c; Stage 0 Pack Rev06
commit 78bfe0008a536ca62ce7c16b7243729f0a50b738, blob
7685099a42e7a7ab566be7ea790fadae7c6a3c8a; Rev07 chunk commit
76c036ceba72df3726be183d28275692f0164a93, blob
2b4e3b3ebb343360514bfe4164941a27dd2078a9; source baseline
commit e4c855c06beaba449a47281292496bad81d3b468, blob
388754b23069b70f1f1a5b0dc001dc90b87950ce.

## Working-tree integrity

Recursive diff against baseline-v0.18.0 after the correction:
no baseline file differing; additions remain exactly
`identity.js` and `tests-stage1/identity.fixtures.js`. No
wiring into background or adapters; manifest unchanged.

## Test evidence (tied to this exact revision)

Command: `node tests-stage1/identity.fixtures.js`
Runtime: Node v24.22.1. Exit code: 0. 36 fixtures: the 25 of
Revision 1 plus 11 focused input-contract fixtures (missing
field vs explicit null under both scopes; missing and invalid
scope; numeric message ID, platform and object conversation
rejected uncoerced; explicitly undefined message ID; canonical
builder refusing coercion directly).

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

identity.fixtures: 36/36 passed, 0 failed
```

## Scope of this batch

Stage 1 scope item 1 only: the PB-ID source-identity layer, as
corrected. Batch 2 waits for Alex's review of this revision.
No live proof is claimed; Ben's live two-way walk is the stage
acceptance, still ahead.

— Remmy, 2026-11-11.
