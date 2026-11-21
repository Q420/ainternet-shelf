# Alex — Batch 3 correction plan APPROVED FOR SPECIFICATION REVISION (shelved verbatim)

PB-ID: pb-mwfqohrk-6-6i21 · Relayed 2026-11-13 ~17:41 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**Disposition: plan APPROVED; Item 2 Route C selected (carried-field insertion class).** Binding clarifications for Rev 23: (1) pin authority bootstrap chain (derived from the frozen manifest chain; its hash in the correction continuation; pre-flight validates the authority against the frozen chain, never caller configuration; caller cannot choose/replace the authority location; inventory distinguishes file pins from the snapshot's constituent pins; substitution test required). (2) Carried fields: distinct from EXTRACTED (never broaden the word); the carried value must be durably present in the record — define exactly which event holds it; citation bound to same run/tree/producing step/successful CHECK; canonical payload hashing + exact value comparison; refusal object, reason codes, event pair, no-ledger/no-value; replay reconstruction defined; Batch 2 semantics preserved; "unconsumed-by-another-field" defined precisely (source references vs extraction operation IDs vs their consumption distinguished; a carried evidence list cites extraction provenance without consuming operations twice); T05/T08 STEP-02 produce the artifact by lookup+verification, no hardcoded values. (3) Step budgets: exact §6.2 timeout classes (tool/rule vs model/adapter distinguished); no satisfaction-then-budget-failure sequence. (4) Ledgers preserved as named artefacts; strengthened tests assert the actual chunk obligations. Authorised: draft Rev 23 for inspection — specification only, NOT the correction build. He will inspect the exact Rev 23 pin first; his independent acceptance matrix proceeds in parallel. f11d5375, Batch 2 pins, Rev 22 and all frozen artefacts unchanged.

---

Batch 3 correction plan — APPROVED FOR SPECIFICATION REVISION.

Item 2: Route C selected. The carried-field insertion class is the right direction. It preserves the full-ledger requirement without pretending that non-extraction values are extraction results. It also preserves the existing Batch 2 extraction contract rather than weakening it.

The plan's four items are accepted as the correction scope, with the following binding clarifications for Rev 23.

Rev 23 requirements

1. Pin authority — bootstrap trust

The authority file must not become its own trust anchor. Rev 23 must specify the complete chain:

The authority is derived from the frozen PILOT-MANIFEST-01 and re-freeze amendments.

Its own hash is recorded in the correction continuation.

Pre-flight validates that authority against the frozen chain, not against caller-supplied configuration.

Caller configuration cannot choose or replace the authority location.

The run's pin inventory includes every consumed artefact, including all five data files, and distinguishes file pins from the snapshot's constituent pins.

The substitution test must demonstrate that changing both a file and its caller-supplied hash still fails.

2. Carried-field insertion — provenance must survive replay

Route C is approved, but Rev 23 must settle these details explicitly:

Define the carried-field class as distinct from EXTRACTED insertion. Do not silently broaden the meaning of EXTRACTED.

Define exactly which event contains the carried value. A citation to transient in-memory output is insufficient; the value and its hash must be durably present in the append-only record.

Bind the citation to the same run, tree, producing step, and successful CHECK.

Define canonical payload hashing and exact value comparison.

Define the refusal object, reason codes, event pair, and no-ledger/no-value behaviour.

Define how replay reconstructs and independently verifies carried-field provenance.

Preserve Batch 2's existing extraction, consumption, and refusal semantics unchanged.

One important point: the plan's phrase “unconsumed-by-another-field” needs precise definition. The same source section may legitimately support several separately extracted fields. Do not accidentally prohibit that. Distinguish source references, extraction operation IDs, and consumption of those operation IDs. A carried evidence list may cite prior extraction provenance without consuming those extraction operations a second time.

T05-STEP-02 and T08-STEP-02 must each produce the artifact through the declared source lookup and verification work. No hardcoded artifact values.

3. Step budgets

Accepted. Rev 23 should identify the exact timeout failure classes against §6.2, including the distinction between a tool/rule budget failure and a model/adapter timeout. The event sequence must never contain a successful satisfaction followed by a budget failure for the same attempt.

4. Evidence and test fidelity

Accepted. Preserve the materialised ledgers as named bundle artefacts. The strengthened tests must assert the actual chunk-sheet obligations, not merely that a file or event exists.

Authority and next action

You are authorised to draft Rev 23 and submit it for inspection.

This approval is for the specification amendment only. It does not authorise the correction implementation. I will inspect the exact Rev 23 pin before any correction build proceeds.

The original f11d5375 bundle, Batch 2 pins, Rev 22 and all prior frozen artefacts remain unchanged. No Crusher retrieval is needed; the relevant sources are already on Shelf.

I will prepare the independent Rev 22/chunk-sheet acceptance matrix in parallel and use it to inspect the Rev 23 amendment.

Current state:

Batch 1 — CLEARED

Batch 2 — CLEARED

Batch 3 — CORRECTION PLAN APPROVED; Rev 23 pending inspection

Batch 4 — CLOSED

Stage 6 — NOT AUTHORISED

No model call or provider contact authorised.

⟦ALEX-FINAL⟧

— Alex
