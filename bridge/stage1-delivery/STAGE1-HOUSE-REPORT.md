# Stage 1 — House Test Report (Plan S3 form)

**Stage / version:** Stage 1 — stable identity, registration ledger, capture acknowledgement — delivered as **v0.19.0**.
**Authorisation reference:** Build Plan 01 adopted by Ben's tap 2026-11-11 16:49 PST (commit b09476d5, blob 8196d44ea60541855b4c069ea8e46a811adad13c); Stage 1 implementation go, Ben's tap + words 2026-11-11 17:53 PST, conditioned on Stage 0 Pack Rev06 (condition met, commit 78bfe000). Batch reviews by Alex: batch 1 PASS (rev4), batch 2 PASS (rev3), batch 3 accepted/closed (rev3, including Alex's own correction adopted byte-identical under Ben's role switch).
**Source baseline:** v0.18.0 frozen tree, 18 files (Stage 1 source baseline record, commit e4c855c0, blob 388754b2). Changed/added files: DELIVERY-MANIFEST.md beside this report.

## What the delivery does

The four Stage 1 modules are bundled (stage1core.js, generated deterministically by build-stage1-bundle.js) and wired into the background at three seams (stage1-wiring.js): (1) every accepted detection is submitted to the capture session and its acknowledgement recorded in state.stage1.acks and the run log; (2) pause and per-seat disconnect advance the persisted bridge epoch before dispatch eligibility changes; (3) on first touch the legacy state is inventoried (summary stored, legacy stores untouched). The ledger and epoch persist inside the bridge state (state.stage1) via the core's export/import.

## Migration manifest (summary)

The inventory runs at first touch on the installed bridge; its classification rules and per-store results are fixture-proven (batch3.fixtures). Against the delivery fixture's representative legacy state: every store accounted for, source state byte-unmodified, confirmed deliveries blocked for life, uncertain-delivery entries blocked, proven-not-delivered recorded unblocked, the active pair inventoried active-held. The live inventory of Ben's actual legacy state will be produced on first run after install and is part of the live walk evidence, not claimed here.

## Fixture results (per file, executed by Remmy in the final wired tree)

- tests-stage1/identity.fixtures.js — **44/44 passed**
- tests-stage1/ledger.fixtures.js — **56/56 passed**
- tests-stage1/batch3.fixtures.js — **21/21 passed**
- tests-stage1/delivery.fixtures.js — **4/4 passed** (bundle globals; wiring load; end-to-end register/duplicate/epoch/stale on the bundled code; migration on the bundle)
- **Total: 125/125.**
- Top-level smoke: storage.js + background.js (with the importScripts bundle) executed under chrome stubs — no throw; all four Stage 1 globals present.
- Known flakes: none observed across the evening's repeated runs.

## Package

pulse-bridge-v0.19.0.zip — SHA-256 ac972d29f9d21932f9bb0f7721754a6e7ba93ee4b52a1ad57b95e9f4f40e6929, 26 files.

## Ben's live two-way walk (the stage acceptance gate)

Steps: install v0.19.0; register both tabs; send a marked message Remmy → Alex and Alex → Remmy; confirm each detection's Stage 1 ack is recorded in the run log with its honest outcome; repeat/reload the source history and confirm no second registration and no re-send; pause with an accepted item pending and confirm the epoch advanced (run log) and the item remains registered and held.
**Observed result: PENDING — the walk has not run yet.**

## Unresolved / UNKNOWN outcomes (stated, not hidden)

1. **No platform identity is qualified.** The Stage 0 census left ChatGPT unobserved and Muse observed-not-qualified; Ben's one-word item (whether S1.9 covers a corrected ChatGPT attempt) is still open. Live detections therefore acknowledge NOT_REGISTERED with the identity reason. This is the adopted rule failing closed, not a defect — but it means live registrations remain zero until a platform qualifies.
2. **Persistence qualification.** The wired ledger is a serialised single-instance arrangement over chrome.storage via export/import. Durable commit and a single authoritative allocator across restarts/instances are NOT established (Contract S13 / batch 2 scope qualification); substrate selection is outstanding.
3. **Reset tension.** pb-reset restores the default state, which does not include state.stage1 — an explicit Ben reset would discard the Stage 1 ledger export along with the legacy ledgers it already discards today. Surfaced, not silently blessed; recovery/migration hardening is Stage 4 scope.
4. **Authority in the live wiring.** The wired ledger has no authority verifier (by design in the wiring header): authority-bearing transitions are unavailable live until Stage 3's owner-review channel exists. The capability is fixture-proven at module level.
5. Contract S13 items remain open exactly as surfaced in batch 2 (S13.5 policy is constructor-set to 'event' in the wiring; S13.8 PBR-REC1 unadopted; S13.2 named checks unmapped).

## Verdict

**HOLD — pending Ben's live two-way walk.** Module and delivery evidence is complete (125/125 fixtures, smoke clean, package pinned); the plan names the walk as the gate before Stage 2, and it has not run.
