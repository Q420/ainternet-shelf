# Loom Prototype — Build Record

**Commission:** Ben's tap on scope card widget-284602e8, 2026-11-21 ~02:53 MST, confirmed in his words: "Commission the prototype — build the vertical slice from the Rev 9 spec."
**Specification of record:** Loom spec v0.1 Revision 9, shelf commit d7d65c96, blob 6a7e3d54b4b653ed6b8ca76392c59d283d8b2b1a — Gate 1 PASS (Vane, 2026-11-21).
**Scope (as commissioned):** the smallest executable vertical slice — six-region fixture, harness-enforced reads/writes, token-bound identities, typed operations, append-only hash-chained event history, deterministic replay, independent seal checker; Annex E vectors TV-1..TV-20 as executable tests; full lifecycle exercised mechanically; **no live agents in this phase**; Vane examines the implementation as it happens; corrections explicit and recorded; no silent patching.
**Working label:** the system carries the working name "Loom" until Ben rules on the permanent name.

## Stage 1 — core (2026-11-21): COMPLETE, smoke-verified

Code: `fabric/canonical.py` (canonical serialisation + hash chain, §3), `fabric/fixture.py` (constitution text + hash; the six Annex D regions with both plants in their contents; genesis dependencies; sealed ground truth held outside anything the harness will serve), `fabric/store.py` (SQLite WAL append-only event store, 19 event types), `fabric/engine.py` (genesis, state derivation, deterministic replay, chain verification).

Evidence — `stage1_smoke.py`, run 2026-11-21, **9/9 PASS**:
- genesis is a single RUN_OPENED event carrying the complete genesis state in its payload;
- its prev_hash is the constitution's SHA-256 (the constitution is frozen and hashed into the run before anything else exists — the machinery's first act binds it to the constitution);
- six regions at version 1; four genesis dependencies;
- replay from the event history alone reproduces the live state hash exactly (9a7250bde82bfd8b…);
- the hash chain verifies end to end;
- a second fresh run derives the identical genesis state (determinism);
- an out-of-band payload alteration is detected at exactly the altered sequence.

## Next stages

- **Stage 2:** harness (token identities, read record, discovery events, boundary probe) + the contribution commit protocol (§4 order: identity/schema → staleness → structural → commit) + operation targeting and cross-field rules; vectors TV-7, TV-2 (schema side), the Annex D structural-plant rejection.
- **Stage 3:** the ExaminationReport action, Assessments, the §3 validation ladder (incl. identity_collision), tension protocols, completion evidence; vectors TV-3, TV-4, TV-5, TV-9–TV-20.
- **Stage 4:** weave seals + the independently implemented checker; vectors TV-1, TV-6, TV-8; full-suite run and the examination package to Vane.
