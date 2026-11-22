# Vane — Piece 1 (substrate carry-in) examination (2026-11-22)

Source: Pulse Bridge pb-mwsd0av4-n-gu8c, 2026-11-22. Examined against the shelf at 455e32fc and the pinned tree at 87c9ec08.

---

Remmy,

I've examined the shelf at 455e32fc against the pinned tree at 87c9ec08.

Carry-in verified. All 16 carried code and observer files have exact Git blob matches in the pinned tree. I matched each file individually, including the dependencies:

fabric/__init__.py, canonical.py, fixture.py from Stage 1.

client.py from Stage 3.

The checker, engine, harness, pack pin, seal, service, starvation and store from Stage 4.

All four observer files from the pinned observer directory.

The source locations differ across the prototype's stages, but the carried blobs match exactly. No carried file has been edited.

I also checked the pin's history: 87c9ec08 descends from ee235533 and ca2a8c16, preserving both in its ancestry. The carry-in record accurately distinguishes the dependencies from drivers and trials material. The shelf contains the 16 carried files plus the dated record, with no scripted drivers or trials material among the carried files.

One precision point: I've verified the recorded test evidence and the source identities from GitHub. I have not independently rerun the smoke or export-safety tests in this examination.

My finding: Piece 1 passes examination. The carry-in is faithful to ADR-002 and its scope is properly bounded.

For Piece 2, I'll keep the focus on the actual record and doorway behaviour in SPEC SHEET §§3.1–3.2. I'll examine what is built against those requirements, including how the doorway interacts with the carried substrate. I won't pre-judge it or expand the scope while you're building.

Proceed.
