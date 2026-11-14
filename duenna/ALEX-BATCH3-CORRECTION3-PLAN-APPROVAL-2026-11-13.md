# Alex — Batch 3 Correction 3 Plan Approval (relayed verbatim, 2026-11-13 ~19:48 MST)

PB-ID: pb-mwfv87qi-k-bei8

BATCH 3 CORRECTION 3 PLAN — APPROVED FOR IMPLEMENTATION

I retrieved and inspected the round-3 plan and checked its proposed corrections against the Rev 26 requirements and the round-2 evidence described in the plan.

All five items are approved:

§4(p): Independently derive declared inputs from pinned data and run artefacts, then deep-compare them with the reconstructed MODEL outputs. T06_KEY must come from the pinned EXPECTED file, not a suite-local copy. Do not silently weaken a comparison if independent derivation proves impossible.

§4(r): Restore the exact seven numbered malformed-presentation cases, each independently asserted. Retain the three additional round-2 cases as unnumbered extras.

§4(n): Assert type(seq) is int across every record.

§4(o): Compare content hashes, inspect the actual parent listing, and verify the real commitments/ directory remains unchanged. No probe stand-in.

Generator documentation: Correct the fixture description to match the actual byte operation.

Fixture ruling: Accepted. The round-2 deviation preserves the intended integrity test while keeping the pre-staged JSONL corpus loadable. The documentation correction is sufficient; no authority re-mint is warranted.

Build-go ruling: No fresh Ben approval is required. This is a narrowly bounded correction to the same Batch 3 checkpoint's evidence, under the existing round-2 build go. That permission does not extend to changing the driver, authority, tools, record implementation, or expanding the correction scope.

Implementation boundaries:

Only the suite and generator docstring may change.

Preserve the round-2 bundle and all its pins.

Issue the new continuation with the suite and generator pins.

No Stage 5 execution, subject call, Batch 4 opening, or Stage 6 authorisation.

When the bundle is shelved, I can take the independent review of the new tests, transcript, records, and commitments evidence off your hands where possible.

⟦ALEX-FINAL⟧
