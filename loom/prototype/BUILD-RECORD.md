# Loom Prototype — Build Record

**Commission:** Ben's tap on scope card widget-284602e8, 2026-11-21 ~02:53 MST, confirmed in his words: "Commission the prototype — build the vertical slice from the Rev 9 spec."
**Specification of record:** Loom spec v0.1 Revision 9, shelf commit d7d65c96, blob 6a7e3d54b4b653ed6b8ca76392c59d283d8b2b1a — Gate 1 PASS (Vane, 2026-11-21).
**Scope (as commissioned):** the smallest executable vertical slice — six-region fixture, harness-enforced reads/writes, token-bound identities, typed operations, append-only hash-chained event history, deterministic replay, independent seal checker; Annex E vectors TV-1..TV-20 as executable tests; full lifecycle exercised mechanically; **no live agents in this phase**; Vane examines the implementation as it happens; corrections explicit and recorded; no silent patching.
**Working label:** the system carries the working name "Loom" until Ben rules on the permanent name.

## Standing safeguards (Vane's boundary examination, 2026-11-21 — recorded at her direction)

1. **Rev 9 is the authority.** Implementation choices must not quietly amend the specification. Where code exposes an ambiguity, it is recorded and brought forward for a ruling.
2. **Vectors are executable obligations.** TV-1 through TV-20 must be implemented as tests with observable outcomes. A test that merely repeats the implementation's own assumptions is not independent evidence.
3. **No live agents before mechanical lifecycle completion.** A hard phase boundary, not a preference.
4. **Independent seal checker means independent implementation.** A second entry point into shared engine logic would not satisfy the requirement.
5. **Corrections remain visible.** No silent patches, rebases, or retrospective rewriting of evidence.
Carried forward from the same examination: the harness and the independent checker are central trust-boundary requirements, not late integration details; and **Stage 2's boundary probe must establish that no agent-facing route can expose the sealed ground truth** — a security property to test, not a comment to trust.

## Observer interface (Ben's commission, 2026-11-21 ~02:55 MST, scope card widget-994c8413)

A read-only observer over the event history — Ben's window into the fabric — built as a standalone page in the Remarvis composition (Remmy's orb at the centre, the six region orbs around it, the crew orbs parked until their phase). Its data projection is the run's event history only, exported after hash-chain verification; sealed ground truth is never exported (it exists in no event). Folding the view into the live Remarvis page is a later, separate decision. v1 built and verified 2026-11-21 (see Stage 1 note); Vane has been invited to examine it as its own artefact.

## Stage 1 — core (2026-11-21): COMPLETE, smoke-verified

**Shelf commit (full SHA):** f01e492fa39e9334e354217915ef9723da83ee94. **Exact source paths** (all under the shelf repo Q420/ainternet-shelf, branch main): `loom/prototype/stage1/fabric/canonical.py` (blob b2eb53d2), `loom/prototype/stage1/fabric/fixture.py` (blob 7e300a4b), `loom/prototype/stage1/fabric/store.py` (blob 773efd41), `loom/prototype/stage1/fabric/engine.py` (blob f72a3624), `loom/prototype/stage1/fabric/__init__.py`, `loom/prototype/stage1/stage1_smoke.py` (blob eb04d10c). Blob identities re-verified against the working tree 2026-11-21 after Vane's examination could not resolve the abbreviated commit originally quoted here — the abbreviation was the defect; this amendment corrects it on the record.

Code: `fabric/canonical.py` (canonical serialisation + hash chain, §3), `fabric/fixture.py` (constitution text + hash; the six Annex D regions with both plants in their contents; genesis dependencies; sealed ground truth held outside anything the harness will serve), `fabric/store.py` (SQLite WAL append-only event store, 19 event types), `fabric/engine.py` (genesis, state derivation, deterministic replay, chain verification).

Observer v1 (same day): `observer/fabric-view.template.html` + `observer/export_events.py` in the working tree; the generated page was rendered and eyeballed — the web assembles from the genesis event, the chain badge reads verified, and the crew orbs sit parked and dim, as they should until their phase.

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
