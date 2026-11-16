# Watchdog contract v1.4 — re-check of the amended draft

Re-checked: watchdog/WATCHDOG-CONTRACT-v1.4-AMENDMENT-DRAFT.md on main @ cd58ca6, against my review at ea4253e1.

## Verdict

**PASS, with one wording fix (W1) and one build-spec condition (C6). The owner may freeze v1.4 once W1 is made. C6 goes into the build spec.**

## Conditions met

- **C1 (at-least-once):** the order is written out (fired → post → delivered), restart re-posts undelivered records, wake_id is in plain text, and the post-failure path is stated and has a fixture (item 4).
- **C2 (stale):** dropped from the channel, §9 untouched, stated in the text.
- **C3 (verification):** in the contract (item 5) and in acceptance item 2.
- **C4 (RB-50):** the reviewer note is carried into the text under Out of scope.
- **C5 (boundary):** acceptance item 5 is the fixture.

## W1 (wording, before freeze)

Acceptance item 3 says the re-offer path "presents acknowledged-state pending wakes in the checker's summary". Acknowledged events are not pending. It should read **unacknowledged** pending wakes, which matches the rest of the text.

## C6 (build spec, not a freeze blocker)

The `delivered` record must not collide with the outbox's wake_id dedupe. The Stage 5 outbox refuses a second record with the same wake_id, and its reader keeps only the first occurrence per wake_id. A delivered record keyed by the same wake_id would therefore be refused or hidden. The build spec must give delivered records their own key (for example `<wake_id>|delivered`) or a separate file, and must add a fixture that the delivered record is written and read back alongside its fired record.

## Next

Amend W1, owner confirms, v1.4 freezes. Build follows with C6 in its spec.
