# ALEX — REV 02 NOT APPROVED: ASSERTION-ORDER CORRECTION (2026-11-16)

Source: Alex's signed reply (⟦ALEX-FINAL⟧) in the new Duenna
conversation (6afba3d2) ruling on Spec 01 Rev 02. Captured
first-hand; filed verbatim below.

## Substance — verified first-hand by Remmy against the code

Alex is correct. In smoke_harness.py the expected ID is read
at line 95 (sys.argv[1]), the Driver is constructed at line
118, driver.run(SUBSET) executes at line 123, and the equality
assertion stands at line 124 — AFTER the run, including its
model step. Rev 02's claim that a mismatch aborts before any
adapter call was wrong. The one-call guarantee never rested on
that assertion (it rests on the tree shape and the smoke
config); the specification stated a false mechanism and Alex
caught it. Correction made in Spec 01 Rev 03, exactly as he
directed; no harness change.

Rev 02 is not approvable as written. The run-ID argument is now specified, but the specification misstates when the harness validates it.

The pinned harness does read sys.argv[1] at startup. However, its equality assertion is after driver.run(SUBSET), not immediately after Driver construction. driver.run(SUBSET) executes T04, including its model step, before that assertion is reached. Therefore the claim that a run-ID mismatch aborts before any adapter call is unsupported by the actual harness.

This is a material execution-contract defect because the specification relies on that claim as part of its one-call and record-integrity explanation.

The required correction is narrow:

State that the harness reads the expected ID at startup but compares it with driver.run_id after driver.run(SUBSET) returns.

Remove the claim that an ID mismatch prevents execution or an adapter call.

Treat the ID comparison as a post-execution consistency check, with the run record's run_id independently checked against the supplied value during adjudication.

Keep the existing one-call controls and all other approved limits unchanged.

No harness change is being requested in this ruling. No smoke call is authorised yet. Rev 02 remains unapproved pending that documentation correction.

The rest of the replacement shape remains accepted: the owner's decision, supervisor-less provenance label, T04 scope, pinned smoke configuration, production endpoint, and one-call ceiling.

⟦ALEX-FINAL⟧
