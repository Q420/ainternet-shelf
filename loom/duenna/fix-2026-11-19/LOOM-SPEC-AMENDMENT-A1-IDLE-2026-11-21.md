# Amendment A1 — IDLE event type

A between-run amendment to the Loom specification v0.1 Rev 9 (shelf commit d7d65c96, Gate 1 PASS).

- **Amends:** §3's event enumeration and §4's idle outcome.
- **Change:** adds one event type, `IDLE` — actor: the idling agent; evidence-only in the fold; no fabric-state change — so that an agent's decision to take no action is durably recorded in the event history, as §4 requires of the idle outcome. Nothing else in Rev 9 changes.
- **Authority:** Ben's delegation, 2026-11-21 03:40 MST ("You guys decide what's best for the overall project"); the decision settled by Remmy and Vane under that delegation; Vane's concurrence recorded on her examination of the Stage 2 corrections round, 2026-11-21.
- **Effective point:** runs opened from the Stage 2 corrections round (shelf commit 1019aaaf) forward. The Rev 9 artifact is preserved unaltered and does not contain IDLE; no run or record before the effective point is rewritten or re-described. A run binds to the specification-and-amendment set in force at its `RUN_OPENED`.
- **Reason:** Rev 9 §4 names idle a legitimate, recorded outcome, but the Rev 9 event enumeration provides no type for it — a contract gap found during Stage 2 implementation (Vane finding 3B). The pre-amendment implementation held idle in an in-memory harness log, which is not durable event history.
