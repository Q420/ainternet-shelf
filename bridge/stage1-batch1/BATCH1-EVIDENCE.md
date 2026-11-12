# Pulse Bridge — Stage 1 Batch 1 — Evidence

Revision under review: the two files shelved alongside this
evidence in `bridge/stage1-batch1/` at the same commit.

## Files and content hashes (SHA-256)

- `identity.js` — d31c4ee2ed7c987522d5de3d208ad4dbeb120eaf1853385fb1cd026879e61911
- `identity.fixtures.js` — 29bad2afd38a9e3bf7596413219c090eecbd96bbb64c454238d479903d060dca

## Basis pins

- Build Plan 01 (shelf): blob 8196d44ea60541855b4c069ea8e46a811adad13c (verified equal to the adopted pin before building).
- Stage 0 Pack Rev06: commit 78bfe0008a536ca62ce7c16b7243729f0a50b738, blob 7685099a42e7a7ab566be7ea790fadae7c6a3c8a; Rev07 correction chunk: commit 76c036ceba72df3726be183d28275692f0164a93, blob 2b4e3b3ebb343360514bfe4164941a27dd2078a9.
- Source baseline: BRIDGE-STAGE-1-SOURCE-BASELINE-01, commit e4c855c06beaba449a47281292496bad81d3b468, blob 388754b23069b70f1f1a5b0dc001dc90b87950ce.

## Working-tree integrity

The build tree is a fresh copy of baseline-v0.18.0 (all 18 file
hashes re-verified identical in the copy before building).
After batch 1, a recursive diff against the baseline shows NO
baseline file differing; the only additions are `identity.js`
and `tests-stage1/identity.fixtures.js`. No wiring into
background or adapters; no outbound behaviour changed; manifest
unchanged (version bump belongs to stage delivery).

## Test evidence (tied to this exact revision)

Command: `node tests-stage1/identity.fixtures.js`
Runtime: Node v24.22.1. Exit code: 0.
The fixtures were run against the shelved files' identical
twins in the build tree (SHA-256 above) at the time of shelving.

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

identity.fixtures: 25/25 passed, 0 failed
```

## Scope of this batch

Stage 1 scope item 1 only: the PB-ID source-identity layer.
Remaining Stage 1 batches: (2) registration ledger, Index ID
allocator, idempotency, lifecycle, R-2, two index routes;
(3) capture acknowledgement, epoch, owner-review backend,
migration inventory. No live proof is claimed by this evidence;
Ben's live two-way walk is the stage acceptance, still ahead.

— Remmy, 2026-11-11.
