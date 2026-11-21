# Stage 1 Batch 3 — Evidence (capture acknowledgement, epoch, owner review, migration)

Date: 2026-11-11 (America/Dawson_Creek)
Builder: Remmy, from Build Plan 01 S3 scope items 7-9 and the Stage 1 migration rules, read at the adopted pin (blob 8196d44e).
Batches 1-2 re-run for this batch: identity 44/44, ledger 56/56.

## Result

batch3.fixtures.js: **18/18 passed, 0 failed**.
Stage 1 running fixture total: **118/118**.

New files only: capture.js, migration.js, tests-stage1/batch3.fixtures.js. No baseline file differs; no adapter/background wiring (that is stage delivery work); manifest still 0.18.0 until Stage 1 delivery.

## Item 7 — capture acknowledgement (capture.js)

submitDetection resolves every handoff to exactly one of the plan's four outcomes, tied to the registration result: REGISTERED (verified new record), DUPLICATE (same source, same Index ID, one registration), NOT_REGISTERED (not admitted / unidentifiable / collision), REGISTRATION_UNKNOWN (read-back loss; resolves later by idempotency identity via resolveUnknown — never a second registration). A ledger INTEGRITY_FAULT maps to REGISTRATION_UNKNOWN with the reason carried: the outcome is not established, and UNKNOWN is the honest member of the four-outcome set.

The letterbox discipline is enforced by the session: retireHandoff succeeds only after a REGISTERED/DUPLICATE ack or an explicit recorded disposition (recordDisposition). An identity collision is a visible hold (NOT_REGISTERED + identity-collision, pending, flagged) — never a silent merge, never an invented identity; an unidentifiable source invents nothing.

## Item 8 — bridge epoch (capture.js)

createEpochStore: the epoch persists (export/import), only moves forward (import of a lower epoch is rejected), and stamps events. admit() rejects stale events and — fail-closed — events with no epoch ('epoch-missing'). A stale-stamped detection submitted to the capture session returns STALE and creates nothing: no registration, no pending entry. Pause/disconnect wiring calls advance() before dispatch eligibility changes; the store makes that advance atomic and exportable.

## Item 9 — owner-review backend (capture.js)

createOwnerReview over the ledger: listReviewItems returns HELD_FOR_REVIEW / REFUSED / REFUTED / SUPERSEDED records in registration order, each with identity and event count. hold() and decide() (hold/skip/discard/close/refute) append lifecycle events through the ledger — authority is verified at the ledger's boundary, this module asserts none (an unverified discard is refused and the item stays queued, fixture-proven). No method purges, retries, reclassifies or destroys: after a discard the record remains registered and retrievable by the message route. UI presentation remains Stage 3, per the plan.

## Migration inventory (migration.js)

inventoryLegacyState classifies the v0.18.0 state object (pulseBridgeStateV1) store by store without modifying it (fixture: deep-equal before/after) and without dropping anything — an unrecognised store is 'unclassified-preserved'. Legacy stores identified from the baseline source: detections, seen, delivered, deliveryFailed, deliveredIds, deliveryFailedIds, seenIds, fpToId, completedSerials, pair, bufferId, plus the non-message stores (registrations, paused, fileTransfers, rollovers, alerts, serialNext, log).

Rules applied per plan: the old bridge-assigned message_id is preserved as the legacy identity; no identity is invented for historical messages; a bare fingerprint with no fpToId mapping is 'uncertain', never upgraded; delivery follows the ledger's fact discipline (confirmed-delivered only from the old system's own carry records, proven-not-delivered from its failure records, unknown otherwise); delivery truth flows across the old system's own fpToId mapping; re-send is blocked for confirmed deliveries and wherever delivery history is uncertain — only a recorded proven-not-delivered entry is unblocked, and its route forward is a fresh managed registration. The active pair + buffer are inventoried as active-held for owner review, never auto-carried.

## Stage 1 status after batch 3

All three build batches are complete at the module level (identity 44, ledger 56, batch3 18). Remaining for Stage 1 delivery: wiring into the copied tree's background/letterbox paths, manifest bump to 0.19.0, the copied-folder ZIP and house test report, and Ben's live two-way walk, which is the stage acceptance gate. No outbound behaviour changes in this batch.
