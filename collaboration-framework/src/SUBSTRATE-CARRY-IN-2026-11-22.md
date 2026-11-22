# Substrate carry-in — Stage 2, piece 1 (2026-11-22)

**Authority:** Ben's design ruling 2026-11-21 12:12 MST (COLLABORATION Rev 5 + SPEC SHEET Rev 5 approved; plan Stage 2 open) and his start order 2026-11-22 14:28 MST ("Let's start"). Pin: ADR-002 — the accepted prototype at shelf commit 87c9ec08, local source `~/workspace/loom-prototype/`.

**What was carried** (verbatim, layout preserved under `src/`; every file byte-identical to the pinned original, verified by git blob hash):

- `src/fabric/` — `__init__.py`, `canonical.py` (canonical serialisation + hashing), `store.py` (append-only event store), `engine.py` (genesis, state derivation, verified replay — both folds), `harness.py` (seat harness: token-bound identity, mediated access), `service.py` (the fabric's OS-boundary service), `client.py` (agent-side client), `checker.py` (the independent checker), `seal.py`, `starvation.py`.
- `src/observer/` — `export_events.py`, `fabric-view.html`, `fabric-view.template.html`, `test_export_safety.py`.

**Dependencies carried with them, recorded plainly:** `fabric/fixture.py` and `fabric/packpin.py`. The engine, harness and service import them (constitution/genesis constants; the examiner-pack pin), so the named components cannot run without them. They are not scripted drivers and not trials material. Their prototype-specific content (the fixture's sealed ground truth; the Stage 4 pack pin) is carried as-is at the pin; replacing it under this project's design is later build work, not part of this piece.

**What was NOT taken** (per ADR-002): the scripted drivers and probe/exercise machinery — `agent_runner.py`, `probe.py`, `probe2.py`, `probe_agent.py`, `runtime_setup.py`, the `boundary-runtime/` evidence folder, the stage/closing exercise scripts and test suites, `make_demo_run.py`, `pack_validation.py`, run databases — and all `trials/` material (parked by Ben's order, 2026-11-21). The observer design variations (`observer/variations/`) were also left behind: the accepted observer is the export + view carried above.

**Verification (run against the carried tree, 2026-11-22):**

- All 16 carried files byte-identical to the pinned originals (git blob hashes compared).
- The prototype's Stage 1 smoke (store/engine/canonical: replay reproduces live state, hash chain verifies, store refuses UPDATE/DELETE/REPLACE, tamper detected) — **ALL PASS** with the carried tree on the path.
- The observer's export-safety suite — **ALL PASS** against the carried tree.
- `checker`, `harness`, `client`, `seal`, `starvation` import cleanly from the carried tree.
- Known behaviour, not a defect: `fabric/service.py` looks up the OS user `loomfab` at import — the prototype's dedicated service identity, which does not exist on this machine. The pinned original behaves identically (control-checked); the service runs under its own OS identity in the boundary runtime, by design.

**Not yet done:** this piece is the substrate only. The record + doorway behaviour the framework design adds on top of it (SPEC SHEET §3.1–3.2 as specified for this framework, the bubble, live seat drivers, office + onboarding, gates) are the following Stage 2 pieces, one at a time. Nothing in the carried code was edited.
