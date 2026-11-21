# ALEX — SPEC 01 EXAMINATION: NOT APPROVED AS FILED, ONE CORRECTION (2026-11-16)

Source: Alex's signed reply (⟦ALEX-FINAL⟧) in the Duenna
conversation (6afb8904) examining the replacement execution
specification. Captured first-hand; filed verbatim below.
(Capture note: one displayed line in his reply — the harness's
argv read — did not survive page extraction; the substance is
confirmed against the harness source itself,
smoke_harness.py line 95: expected_run_id = sys.argv[1].)

## Substance

Owner authority: accepted. Replacement scope: accepted.
Provenance limitation and the SUPERVISOR-LESS label: accepted.
One executable mismatch: the specification's §3 did not state
the invocation contract — who supplies the expected run ID as
sys.argv[1] now that the supervisor is removed. Documentation
correction required (not a harness modification); smoke
authorisation withheld pending it. The correction was made in
Spec 01 Rev 02 and returned for his final ruling.

Examination result: NOT APPROVED AS FILED

The owner has supplied the authority I required. The replacement specification also makes the custody loss explicit rather than disguising the supervisor-less run as equivalent evidence. Those are both satisfied.

I accept the proposed scope of the replacement: one live T04 call, unchanged smoke configuration, one-call limit, 5,000-token ceiling, no retry, no paid substitution, no battery call, and Alex's adjudication. The SUPERVISOR-LESS provenance label is appropriate and must remain attached to the run and every later citation.

There is, however, one executable mismatch to resolve.

Required correction: invocation contract

The pinned smoke_harness.py begins by reading:

It later checks that the driver's generated driver.run_id matches that value.

Under the former supervisor arrangement, the supervisor supplied the expected run ID. The replacement specification removes that supervisor, but §3 says the driver derives the run ID without explaining how the required command-line argument is supplied.

As written, the direct invocation is incomplete. Running the script without that argument fails before the driver completes.

The specification needs to state the exact invocation contract: how the run ID is generated or obtained, how it is passed as sys.argv[1], and how the resulting driver ID is checked against it. This should be a documentation correction to the execution specification, not a harness modification.

Disposition

Owner authority for the supervisor-less shape: accepted.

Replacement execution scope: accepted.

Provenance limitation: accepted.

One-call and budget constraints: retained.

Invocation contract: unresolved.

Smoke authorisation: withheld pending that correction.

No firing, no additional model call, and no change to the underlying smoke assembly. Once the invocation contract is explicit, bring the revised specification back for the final ruling.

⟦ALEX-FINAL⟧
