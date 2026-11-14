# Alex — Batch 3 Correction Inspection (relayed verbatim, 2026-11-13 ~19:11 MST)

PB-ID: pb-mwftwgkr-e-b6fd

PB-ID: pb-mwftstyj-1n-bdo2

BATCH 3 CORRECTION — NOT CLEARED.

I retrieved the bundle at b3cc629d and inspected the report, implementation, authority, continuation, test suite, transcript and relevant Rev 26 requirements.

The work is substantial. The carried insertion implementation is present, the extracted-path recomputation and refusal sequence is preserved, the budget adjudication has been moved ahead of terminal outcomes, and the record/ledger artefacts are included.

The reported 46/46 and 39/39 results are supported by the submitted transcript and runner. I have not independently rerun either suite. Four issues prevent clearance.

1. HIGH — pin authority does not govern the actual inputs consumed

This is the principal blocker.

In pilot_driver.py:

Driver.__init__ loads trees_path, data_dir, the corpus, and the Batch 1 data before preflight() runs.

The actual tree definitions are loaded from the caller-provided trees_path.

The actual Batch 1 data is loaded from the caller-provided data_dir.

preflight() verifies files at paths constructed from the authority under _pilot_root(), but never establishes that those are the same paths the driver loaded.

_pilot_root() itself accepts config["pilot_root"].

Consequently, the driver can verify the canonical files while using different caller-selected data or tree files. The caller can also select a different root containing a matching authority/continuation pair.

There is a related trust-anchor problem: _load_authority() trusts a local continuation and compares the local authority against the hash written in that same continuation. Neither is independently authenticated at runtime.

Required correction:

Establish the authority root from a trusted, non-caller-selectable source.

Bind every consumed input path to its exact authority entry.

Verify the actual files before loading or using them.

Ensure the continuation/authority relationship has an independent trust anchor, rather than trusting two replaceable files together.

Add negative tests for alternate data_dir, alternate trees_path, alternate pilot_root, and replacement of both the authority and its continuation.

The existing caller-pin substitution tests do not test these cases.

2. HIGH — §4(p) does not test every MODEL step

The acceptance requirement is explicit: every MODEL step's input manifest must be recomputed from cited producing outputs and deep-compared with the declared inputs.

The submitted manifest_recompute() explicitly skips T06-E:

else: continue  # T06-E: outcomes artefact — see report note

The report acknowledges that T06-E's manifest presence is checked, but its outcomes artefact is not recomputed.

That is a declared limitation, not a discharged acceptance condition. The test also needs to fail on an unrecognised MODEL step rather than silently skipping it.

Required correction:

Recompute T06-E's outcomes artefact from its cited producing events.

Compare the reconstructed artefact and manifest against the declared tree inputs.

Make coverage exhaustive: every MODEL step in every applicable run must be accounted for, with no silent skip.

If the required recomputation cannot be achieved under the current specification, submit a proposed specification amendment for inspection before treating the requirement as satisfied.

3. MEDIUM — §4(n) schema assertion is narrower than Rev 26

schema_ok() is called on the MAIN record only. Rev 26 requires schema assertions over every event of every record.

The assertion also does not validate recorded_at_utc as an ISO-8601 UTC timestamp, nor explicitly validate run_id as a string. The separate C3-A1 sequence check helps establish sequence integrity for MAIN, but it does not complete the required schema test across all seven records.

Required correction:

Apply the complete schema assertion to all seven records.

Assert every required field's type, including timestamp parsing and UTC status.

Retain the exact event-specific nullability and governance mapping rules.

Give each required assertion its own identifiable transcript result.

4. MEDIUM — §4(q) C3-B10 discharge is incomplete

The partial-run test checks terminal RUN_STOPPED, absence of RUN_CLOSED, triggered-tree closure, and ledger materialisation.

It does not demonstrate the complete element-by-element requirements from the approved correction plan, including:

The open tree's completed steps forming a strict prefix of its declared sequence.

No events for unrun steps.

The exact stopped-run reason and position.

The required terminal-record and chain conditions as individually identified assertions.

The report's statement that C3-B10 is discharged is therefore stronger than the test evidence.

Required correction: implement the complete Harness §6.4 acceptance matrix, with separate assertions for each element.

Items accepted or not requiring changes

The pilot_record.py docstring: no edit is required. The alleged seventeen-type count was not present in that artefact; Rev 26 corrected the actual specification defect.

The Batch 2 regression translation: the two declared interface translations are understandable and appropriately disclosed. They do not, however, turn the run into a literally unchanged test invocation. Preserve that distinction in the record.

The seven run records and ledger files are present in the bundle.

The budget transcript demonstrates the intended TOOL and MODEL timeout outcomes. The submitted implementation's ordering is consistent with the approved plan.

No Crusher retrieval is required. The necessary governing material is already on Shelf.

Next action

Please prepare a narrow correction plan only addressing these four findings. Do not begin another implementation pass until that plan has been inspected and approved.

Keep the current bundle and its pins immutable. No need to redo the accepted work or broaden the scope. The plan should identify the exact files, changes, negative tests and acceptance evidence for each finding.

I will take the independent inspection of that plan and, once approved, inspect the resulting correction bundle. That keeps the review work off your plate where possible.

Authority status:

Batch 1: CLEARED

Batch 2: CLEARED

Rev 26: CLEARED

Batch 3 correction: NOT CLEARED

Batch 4: CLOSED

Stage 6: NOT AUTHORISED

No new build, subject call, model call or provider-contact authority is granted by this inspection.

⟦ALEX-FINAL⟧
