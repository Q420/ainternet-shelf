# ADR-003 — The record service extends the substrate as new code

**Date: 2026-11-22. Status: recorded during plan Stage 2, Piece 2, under Ben's design ruling of 2026-11-21 and his loop approval of 2026-11-22. Surfaced to Vane with the Piece 2 examination, not decided silently (SPEC SHEET §2, §8).**

**The finding.** The carried substrate store (`fabric/store.py`, Piece 1) asserts its prototype event vocabulary inside `append()` — a module-level `EVENT_TYPES` set of the prototype exercise's types (RUN_OPENED, CONTRIBUTION_ACCEPTED, …). The framework's event vocabulary (SPEC SHEET §3.1, R3) cannot pass through it. Editing the carried file would break the ADR-002 pin discipline; mapping framework events onto prototype type names would mislabel the record.

**The decision.** The framework record service is new code in `src/framework/record.py`, exactly as §3.1's heading provides ("Record service — substrate, extended"). It reuses the substrate's canonical hashing (`fabric.canonical`: `canonical`, `sha256_hex`, `event_hash`) and its storage discipline — same schema shape, insert-only triggers, hash-chain rule — and extends the vocabulary to the framework's types, adding the per-event timestamp R1 requires. The carried substrate files are untouched; the prototype store remains as carried for the prototype machinery.

**Consequence.** Two stores exist side by side, sharing hashing: the prototype's (carried, pinned) and the framework's (new, this project). The independent checker (§3.10, a later piece) verifies the framework record from the record alone; it shares no code with this record service beyond the canonical hashing both stand on.
