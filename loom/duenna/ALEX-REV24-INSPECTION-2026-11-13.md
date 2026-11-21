# Alex — Rev 24 inspection: NOT CLEARED (shelved verbatim)

PB-ID: pb-mwfr4v06-9-1tyj · Relayed 2026-11-13 ~17:54 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**Disposition: Rev 24 NOT CLEARED (2 HIGH, 1 MEDIUM).** Substance accepted (ordered evidence comparison, carried schema, exclusivity, pin chain, acceptance list). **1 HIGH** — the carried interface is inconsistent with the frozen §3.2 inventory: §3.3 names reference_insert_carried while §3.2's five-tool inventory and logging contract know only reference_insert; settle one interface (second tool vs internal entry point vs tagged union) across §3.2, §3.3, registry, logging and replay, preserving the five-tool boundary unless deliberately amended; every carried call needs an unambiguous invocation identity and event pair. **2 HIGH** — two approved plan test obligations missing from §4(a)–(q): the cross-form refusal group and the cross-class independence group; structural prose is not proof; add named assertions with state-before/state-after checks. **3 MEDIUM** — §4(n) (C3-A2) under-enumerated: event_type against the closed §2.3 vocabulary and tree_id/step_id types + nullability not asserted. His chunk-sheet acceptance matrix is included in the verdict (C3-A2 incomplete; A5/A6/A7/B3/B6/B10 now explicit; the rest retained). **Next step: a short Rev 24 correction plan**, inspected before Rev 25 drafting. All pins immutable.

---

Rev 24 inspection — NOT CLEARED

I retrieved and inspected the exact specification at Shelf commit 871d90f7.

File: duenna/STAGE5-BUILD-SPEC-24.md

Git blob: b625f6777a8252bf4410ed862dc451ac4e40c244

Retrieved length: 6,806 lines plus terminal newline.

Rev 23 and earlier pins remain untouched.

I have not independently recomputed the claimed SHA-256.

Rev 24 incorporates the five planned corrections and all four clarifications in substantial part. The ordered evidence comparison, carried ledger schema, provenance exclusivity, pin-authority chain, and explicit acceptance list are meaningful improvements.

However, there are two HIGH issues and one MEDIUM issue remaining.

1. HIGH — the carried insertion interface is inconsistent with the frozen tool inventory

Rev 24 §3.3 defines:

reference_insert(field, process_step, operation_id)

reference_insert_carried(field, process_step, citation)

But §3.2 still defines the five-tool inventory and specifies only reference_insert as the insertion tool. Its signature remains the EXTRACTED form. The logging contract likewise names reference_insert, not reference_insert_carried.

This leaves an unresolved interface question:

Is reference_insert_carried a second externally callable tool?

Is it an internal entry point behind the existing reference_insert tool?

Or is it an alias for the same tool with a tagged-union argument contract?

These are materially different designs. If it is a sixth tool, the frozen five-tool inventory and logging contract are incomplete. If it is an internal entry point, the public tool contract and event identity must say so.

Required: define one consistent interface across §3.2, §3.3, the registry, logging contract, and replay. Preserve the five-tool boundary unless a deliberate specification amendment authorises a different inventory. Every successful and refused carried call must have an unambiguous invocation identity and event pair.

2. HIGH — two approved correction-plan test obligations are missing from the acceptance list

The plan explicitly required:

Cross-form refusal

An operation ID presented to the carried path refuses.

A citation presented to the extraction path refuses.

Neither path consumes or mutates anything.

Cross-class independence

Consuming an extraction operation does not consume a carried citation.

Consuming a carried citation does not consume an extraction operation.

Both orders are tested.

Rev 24 §4(a)–(q) includes citation reuse and the Batch 2 refusal battery, but does not explicitly require these two test groups.

The structural requirements in §3.3 describe the desired behaviour. They do not prove the implementation exhibits it.

Required: add separate, named acceptance assertions for both groups, with state-before/state-after checks and preserved transcript results.

3. MEDIUM — C3-A2's schema test is still not fully enumerated

The chunk sheet requires every event to carry the complete PILOT-RUN-RECORD-01 field set, including:

event_type from the closed §2.3 vocabulary.

tree_id and step_id.

prev_event_sha256 and event_sha256.

Rev 24 §4(n) specifies presence and types, but its explicit type list does not identify the required types or permitted nullability of tree_id and step_id, nor does it explicitly assert event_type against the closed vocabulary.

Required: enumerate those checks. A generic assertion that the schema is checked is not enough when the chunk sheet names the fields and their constraints.

Independent acceptance matrix — chunk sheet cross-check

I retrieved the actual Batch 3 chunk sheet and compared it with Rev 24 §4.

Chunk

	

Rev 24 disposition




C3-A1

	

Existing requirement retained; correction suite still needs preserved evidence




C3-A2

	

Incomplete Explicit schema assertions need the additions above




C3-A3

	

Existing qualified chain claim retained




C3-A4

	

Existing payload requirements retained




C3-A5

	

Ledger materialisation requirement retained; carried schema now defined




C3-A6

	

Before/after parent listing and commitments immutability explicitly required




C3-A7

	

Substitution, inventory, missing and extra-entry tests explicitly required




C3-A8

	

Existing canonicalisation requirements retained




C3-B1

	

Existing declared-order requirement retained




C3-B2

	

Existing step/check requirements retained




C3-B3

	

Exact manifest recomputation and comparison explicitly required




C3-B4

	

Existing failure-branch requirements retained




C3-B5

	

Existing no-verdict requirement retained




C3-B6

	

Separate TOOL/RULE and MODEL timeout tests, plus coherence invariant required




C3-B7

	

Existing lane-failure requirement retained




C3-B8

	

Existing snapshot-integrity requirement retained




C3-B9

	

Existing stop-finality requirement retained




C3-B10

	

Element-by-element Harness §6.4 comparison required




C3-C1–C4

	

Existing tree transcription, subset, stub and boundary requirements retained




C3-D1–D3

	

Existing bundle, pinning and no-subject-call rules retained

The correction list also now explicitly requires eight ledger entries per T05/T08 record, carried-field negative cases, ordered duplicate evidence checks, and the Batch 2 regression battery. Those are accepted as specification-level obligations, not yet demonstrated results.

Next step

Please prepare a short Rev 24 correction plan addressing these three findings before drafting another revision.

The plan should:

Settle the public versus internal carried-insertion interface and reconcile every affected section.

Add the missing cross-form and cross-class tests to the acceptance list.

Complete the C3-A2 field/type assertions.

Preserve Rev 24 and all earlier pins unchanged. I will inspect the plan before authorising Rev 25 drafting.

Authority remains unchanged:

Batch 1: CLEARED

Batch 2: CLEARED

Rev 22: CLEARED

Batch 3: NOT CLEARED

Batch 4: CLOSED

Stage 6: NOT AUTHORISED

No correction implementation, model call, or provider contact authorised.

No Crusher retrieval is needed; the governing sources are already on Shelf.

⟦ALEX-FINAL⟧

— Alex
