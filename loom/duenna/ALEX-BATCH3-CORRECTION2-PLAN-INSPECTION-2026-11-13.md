# Alex — Batch 3 Correction 2 Plan Inspection (relayed verbatim, 2026-11-13 ~19:16 MST)

PB-ID: pb-mwfu2g1j-f-5nrz

BATCH 3 CORRECTION 2 PLAN — NOT APPROVED YET.

I inspected the exact plan at commit b156816ad9fa9b88f896be2d8cbdc4ba13cefbc7, against Rev 26 and the submitted source artefacts.

The plan is substantially stronger. All four findings are addressed directly, the scope is controlled, and I agree that finding 2 is a record/implementation gap rather than a reason to amend Rev 26. The seven-record coverage, explicit T06-E reconstruction, per-record schema assertions and named §6.4 checks are the right direction.

Two issues need resolving before I can approve implementation.

1. HIGH — the proposed hash relationship is circular.

The plan says:

pilot_driver.py embeds EXPECTED_AUTHORITY_SHA256.

The authority contains the SHA-256 of pilot_driver.py.

The driver verifies its own hash against that authority entry.

Those dependencies form a cycle:

driver hash → authority contents → authority hash → driver contents

With ordinary SHA-256 over the complete files, neither final hash can be minted independently of the other. This is not just a sequencing problem; changing either file changes the other file's expected hash.

Please specify a workable, reproducible bootstrap construction. The cleanest option may be to let the driver embed the authority hash, while the driver's own integrity remains externally checked against the Shelf-pinned continuation during inspection. Alternatively, define an explicit canonicalisation scheme that excludes the embedded constant when calculating the driver's authority-entry hash. Do not leave the build process to resolve this implicitly.

2. HIGH — module imports still precede preflight.

The inspected driver imports pilot_jcs, pilot_record and corpus_source at module scope. Those imports execute before Driver.run() can call preflight.

The plan verifies those modules' hashes during preflight, but that is too late if their code has already been imported and executed.

The correction plan must explicitly require that non-standard, locally pinned modules are loaded only after successful preflight. Standard-library imports needed to perform preflight can remain at module scope. The verified paths must be the paths subsequently imported; no second caller-controlled resolution.

One narrower ruling requested — test_snapshot_dir.

I do not approve a general caller-selectable snapshot override merely because it is labelled test-only. It creates a second path around the canonical authority binding.

Please use the named authority-variant fallback, or constrain the override to a fixed, explicitly identified integrity-test fixture that cannot be repurposed to select arbitrary content. The canonical snapshot must still be verified first, and the variant's identity and hash must be recorded.

Accepted plan direction

Item 2: no Rev 26 amendment; preserve the complete T06 outcomes map as record evidence and recompute T06-E from cited outputs.

Item 3: all seven records, all events, complete field and timestamp checks.

Item 4: Q1–Q8 as separate assertions, with the additional retained checks for the other stop cases.

Preserve b3cc629d and all historical pins. Do not redo accepted work or widen the correction.

Please issue a narrow plan revision addressing those points only. No implementation yet.

I can take the independent review of that revised plan and, once approved, the resulting bundle. That should save you another full cross-check pass.

Authority remains unchanged: Batch 1 CLEARED; Batch 2 CLEARED; Rev 26 CLEARED; Batch 3 correction NOT CLEARED; Batch 4 CLOSED; Stage 6 NOT AUTHORISED.

⟦ALEX-FINAL⟧
