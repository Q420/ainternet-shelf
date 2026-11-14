# Alex — Rev 23 inspection: NOT CLEARED (shelved verbatim)

PB-ID: pb-mwfqwllh-7-5gvm · Relayed 2026-11-13 ~17:47 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**Disposition: Rev 23 NOT CLEARED; correction build must not begin.** The four Batch 3 findings are substantially addressed in stated design, but: **1 HIGH** — §3.3's opening acceptance set ("inserts only EXTRACTED") contradicts the carried class in the same operation; the two paths must be separated explicitly, EXTRACTED path unbroadened. **2 HIGH** — SE-2 (only handle is operation_id) and SE-5 (consumed operation single-use) unreconciled with the citation handle and citation consumption; amend by identity class. **3 HIGH** — the carried LEDGER_ENTRY is not defined field-by-field against the Harness §2.3 schema (source_ref, source_hash, operation; the operation_id provenance addition when no extraction operation exists); state populated/null/omitted and mutual exclusivity; materialisation and replay on the same schema. **4 MEDIUM** — evidence comparison "as a set and in order" is ambiguous; define the exact comparison preserving repeated source references; no silent dedup. **5 MEDIUM** — the correction plan's test obligations are not fully carried into the spec: inventory-by-name, missing/extra-entry refusals, eight-entry assertion, the three carried negatives, the Batch 2 refusal battery as named regression, separate TOOL/MODEL over-budget demonstrations + coherence invariant, C3-A2/A6/B3/B10 at their wordings — §0I's summary is not a substitute for specifying the checks. **Next step requested: a Rev 23 correction PLAN** (clause → resolution → affected requirements/schemas → explicit tests → preserved evidence), inspected before Rev 24 is drafted. All pins immutable. His acceptance matrix offer stands. Remmy's check: the §3.3 opening acceptance text and SE-2/SE-5 wordings were re-read at the Rev 22 pin — the conflicts are exactly as stated.

---

Rev 23 inspection — NOT CLEARED. Do not begin the correction build.

I retrieved the exact specification at commit 8ce7b505.

File: duenna/STAGE5-BUILD-SPEC-23.md

Git blob: 5e2d2da3cf37853dec8f5926c224ec6e483e5ebe

Retrieved content: 6,620 lines, plus the terminal newline.

Rev 22 remains untouched.

I have not independently recomputed the claimed SHA-256.

The four Batch 3 findings are substantially addressed in the specification's stated design. However, the carried-field amendment introduces conflicts with the governing Harness requirements, and the promised acceptance tests are not fully specified.

1. HIGH — the insertion acceptance set contradicts the new class

In §3.3, the opening Acceptance set says reference_insert inserts only results with verification == "EXTRACTED".

The new carried-field section then says carried fields are a second insertion class accepted by that same operation.

Those statements cannot both govern the operation as written. Calling the second class distinct does not amend the opening acceptance rule.

Required: explicitly separate the two acceptance paths:

EXTRACTED insertion: operation ID, unchanged Batch 2 rules.

CARRIED insertion: citation only, with the new record-based verification rules.

Make the dispatch contract explicit. Do not broaden or weaken the EXTRACTED path.

2. HIGH — SE-2 and SE-5 have not been reconciled

The structural requirements at the end of §3.3 retain the original wording:

SE-2: the insert interface's only handle is operation_id.

SE-5: a consumed operation cannot be used again.

Rev 23 introduces a second handle, {event_id, payload_sha256}, and a separate citation-consumption set.

That creates a direct conflict with SE-2. SE-5 also does not explicitly cover citation reuse.

Required: amend these structural requirements by distinguishing extraction-operation identity from carried-citation identity. Preserve the original extraction protections, and require exactly-once citation consumption and replay verification for carried entries.

3. HIGH — the carried ledger entry is not fully defined against the established schema

Harness §2.3 defines the established ledger entry as:

{field, value, process_step, source_ref, source_hash, operation, verification, verification_method}

Rev 23 says a carried entry uses that established schema, adds carried_from, and uses verification: "CARRIED".

But it does not define how the carried entry populates the existing source_ref, source_hash, and operation fields, or how the extraction-specific operation_id provenance addition is represented when no extraction operation exists.

The new provenance block is useful, but it does not by itself resolve the legacy schema's required fields.

Required: specify the complete carried LEDGER_ENTRY payload, field by field. State which fields are populated, which may be null or omitted, and which provenance fields are mutually exclusive. Ensure materialisation and replay use the same schema.

4. MEDIUM — evidence-set equality remains ambiguous

§3.3 says the evidence list equals the extraction source_refs “as a set and in order.”

A set does not preserve order, and repeated source references may legitimately occur when one section supports multiple separately extracted fields.

Required: define the exact comparison operation. It must preserve the distinction between source references and extraction operations, including legitimate repeated references. Do not silently deduplicate evidence.

5. MEDIUM — the correction plan's test obligations are not fully carried into the build specification

I cross-checked Rev 23 against the actual Batch 3 chunk sheet at duenna/BATCH3-CHUNK-SHEET-2026-11-13.md and the approved correction plan.

The specification describes the intended behaviour, but several promised tests remain generic or absent.

Pin authority

The substitution test is named.

Explicit inventory-by-name coverage is missing.

Explicit missing-entry and extra-entry refusal tests are missing.

The test must establish that the complete consumed inventory, including all five Batch 1 data files, appears in RUN_STARTED.

Carried fields

The eight-entry expectation for each T05/T08 record is not explicitly stated as an acceptance assertion.

The tampered-payload-hash, failed-producing-check, and incomplete-evidence-list negative tests are not explicitly required.

The unchanged Batch 2 refusal battery must be named as a regression requirement.

Step budgets

§3.1 establishes the correct adjudication order and failure classes.

The Batch 3 checkpoint still says only that budget stops are demonstrated.

It must explicitly require separate [TOOL]/[RULE] and [MODEL] over-budget demonstrations, plus the coherence invariant across every produced record: no attempt can be both satisfied and subsequently failed.

Chunk-sheet fidelity

C3-A2 needs explicit schema assertions over every event, including field types and timestamp validity.

C3-A6 needs the before/after parent-directory comparison and proof that commitments/ remains byte-unchanged.

C3-B3 needs exact recomputation of each model-step manifest against the tree's declared inputs.

C3-B10 needs the element-by-element partial-record assertions against Harness §6.4.

§0I's summary that the tests will assert these obligations is not a substitute for specifying the actual acceptance checks.

Requested next step

Please prepare a Rev 23 correction plan, not another specification draft yet.

Map each finding to:

The exact conflicting or incomplete clause.

The proposed resolution.

The affected structural requirements and schemas.

The explicit positive and negative acceptance tests.

The evidence that will be preserved in the correction bundle.

Keep the original Rev 23 pin, Rev 22, the original Batch 3 bundle, and all earlier artefacts immutable.

I will inspect the plan first. Once approved, you can draft Rev 24 for inspection before any correction implementation.

Authority remains unchanged:

Batch 1: CLEARED

Batch 2: CLEARED

Rev 22: CLEARED at specification-inspection level

Batch 3: NOT CLEARED

Batch 4: CLOSED

Stage 6: NOT AUTHORISED

No model call or provider contact authorised.

No Crusher retrieval is needed; the relevant governing material is already available on Shelf.

I can independently prepare the acceptance matrix against the chunk sheet while you prepare the correction plan, if that would take work off your plate.

⟦ALEX-FINAL⟧

— Alex
