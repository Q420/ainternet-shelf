# ADR-002 — The substrate pin

**Date: 2026-11-21. Status: recorded at the opening of plan Stage 2, under Ben's design ruling of 2026-11-21 (COLLABORATION Rev 5 + SPEC SHEET Rev 5 approved).**

ADR-001 decided the substrate: reuse the accepted prototype's record half; replace its scripted drivers with live seats. This ADR pins *which* accepted state that is, per SPEC SHEET §8 ("the substrate pin — recorded as an ADR before code").

**The pin:** the accepted vertical-slice implementation as it stands at the close of the integrated evidence gate — shelf line `loom/prototype/` at commit **87c9ec08** (closing correction round 2, accepted), preserving **ee235533** (the closing exercise) and **ca2a8c16** (correction round 1) unchanged in its history. Local source of record: `~/workspace/loom-prototype/`. Gate record: `~/workspace/loom-prototype/BUILD-RECORD.md` — "INTEGRATED EVIDENCE GATE PASSED — CLOSING CORRECTION ROUND 2 ACCEPTED (Vane, 2026-11-21 ~08:11 MST): the commissioned vertical slice is COMPLETE."

**What the build takes from the pin:** the record service (event store, hash chain, both folds), the seat harness, the observer, and the independent checker — per SPEC SHEET §2. **What it does not take:** the scripted drivers (replaced by live seat drivers, SPEC SHEET §3.4), and the prototype's conformance/trials material (parked by Ben's order, 2026-11-21).

The pinned artifacts are not edited in place. The framework build works in this project's `src/` from the design; where substrate code is carried in, it is carried at this pin and the carrying is recorded.
