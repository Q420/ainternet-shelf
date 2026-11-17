# ALEX — FRAMEWORK REVAMP DESIGN REVIEW
**Date:** 2026-11-17  
**Reviewer:** Alex  
**Review target:** `record/FRAMEWORK-REVAMP-DESIGN-2026-11-17.md`  
**Target blob:** `4662f68ea100e3844cc1346717b113cc704230f1`  
**Target commit supplied:** `d09c805a`  
**Status:** REVIEW FILED — review only; no build or execution authority.

## 1. Overall finding

The paper is substantially faithful to the Step 6 architecture, the Briefcase design, the EXON rulings and the seven joint rulings. The major placements are sound:

- EXON and the Briefcase are mapped as supporting systems, not extra Step 6 components.
- The Distillery is split into Distiller (selection/packing) and Warehouse Worker (inspection/receipt).
- The Comparator is correctly placed as an independent comparison service, not an Examiner function or auditor. I agree with the paper's explicit adoption of that placement over the skeleton draft.
- The Library → Shelf → EXON cascade correctly follows joint 5.
- The process tree and dependency order are coherent, and the paper preserves the separation between component verification, interface-fixture verification and actual-composition verification.
- The paper correctly states that it authorises no build and that battery preparation and execution remain separate steps under the owner's sequence.

I found several points that should be corrected or made more precise before the paper is treated as a fully faithful consolidation. These are documentary/design corrections, not authority to implement anything.

## 2. Findings requiring correction or clarification

### 2.1 Stage 6 smoke date and custody description — factual correction

Section 2 says the smoke was a “2026-11-16” governed call. That is inaccurate in two ways.

The adjudication record identifies the actual run as `STAGE6SMOKE-20261117-001`, executed on 2026-11-17. It also explicitly labels the run `SUPERVISOR-LESS` and states that it was **not a custody-wrapped run**: there were no supervisor START/TERMINAL commitments. The approval was for exactly one supervisor-less smoke call. The twelve pass-bar checks did pass, so “Alex 12/12 PASS” is accurate.

Suggested replacement:

> “The pilot (harness, driver, adapter and supervisor) is the first working slice of this spine. Its Stage 6 smoke ran on 2026-11-17 as one authorised SUPERVISOR-LESS call (STAGE6SMOKE-20261117-001): full T04 traversal, RUN_CLOSED, and all 12 smoke pass-bar checks PASS. It was not a custody-wrapped governed run and is not a custody precedent.”

This correction matters because the paper's later custody ruling correctly says the smoke is a one-call exception. Section 2 must not describe the same event as a governed call.

### 2.2 Shelf and Duenna RECORD — distinguish the roles

Section 3 calls the Shelf, “in Step 6 terms,” the RECORD's “content face.” I would not leave that as an unqualified equivalence.

The joint 5 ruling establishes the Shelf as the fact layer: validated material is double-checked there and considered fact. Step 6 RECORD is Duenna's evidence-preservation component: it preserves original content, identities and digests append-only, and is the shared evidence boundary on which the other components depend. The ruling does not state that the Shelf and Duenna RECORD are the same store or the same architectural object.

They can be related: RECORD can preserve pinned Shelf/EXON artefacts, source identities, references, receipts and provenance. But the fact-source role of the Shelf should remain distinct from the evidence-substrate role of Duenna RECORD.

Suggested clarification:

> “The Shelf is the knowledge-side fact layer. Duenna RECORD can preserve the Shelf and EXON artefacts, their pins and provenance as evidence; this is a defined relationship, not an assertion that the Shelf and Duenna RECORD are identical.”

If “content face” is intended only as an analogy or interface description, say so explicitly.

### 2.3 Briefcase close — do not promote an unadopted cold-read proposal

Process-tree step 7 says, “The author does not self-certify the close.” That goes beyond the completed Briefcase design as filed.

Briefcase design §7's worked example has the agent perform the reverse one-turn-sufficiency check and, if satisfied, mark the briefcase status `completed`. The design requires retained outputs, manifest and provenance, selective historical indexing, and a fresh context for the next agent. It does not establish an independent close certifier.

The Kit session in Briefcase §8 records a possible cold-read close as a **candidate discussion**, not an adopted requirement. It should not silently become a mandatory independent close gate in this paper.

Suggested distinction:

> “The agent may submit its close declaration and manifest after the reverse sufficiency check. The declaration records the agent's completion claim; it does not independently verify the truth or quality of the work. Any independent cold-read/close certification remains a separate design decision.”

This preserves the difference between an agent recording its own workflow status and an agent certifying its own evidence as true.

### 2.4 Warehouse Worker fidelity — make the mechanical/judgment boundary explicit

Section 4.3 correctly incorporates joint 7's mechanical receipt, Comparator re-performance, second independent implementation, declined judgment claims, pin-seeded 1-in-5 sampling, escalation triggers and fixed gate condition.

One phrase still risks overstatement: the WW “verifies its fidelity against the pinned source.” Under joint 7, the WW receipt is mechanical. Byte/hash equality, enumeration, presence, counts, address resolution, schema and pin correctness are mechanical respects. Semantic equivalence of distilled text, fairness of a summary and adequacy of selection require judgment; those claims are declined in the receipt and routed to the owner. The Comparator does not make those semantic judgments either.

Please qualify “fidelity” here as **mechanical fidelity**. Otherwise a reader could infer that the WW certifies semantic correctness, which joint 7 expressly avoids.

### 2.5 Process-tree step 5 — Comparator produces the diff; F5 applies the gate

Step 5 says the Comparator re-performs the comparison “(the gate).” That shorthand blurs a boundary that §4.3 otherwise gets right.

The Comparator emits the re-performable diff and no verdict. The gate is the fixed owner-defined function of that diff, applied as an F5 enforcement edge. The Comparator is not itself the gate and does not decide release.

Suggested replacement:

> “The WW emits its mechanical receipt. The Comparator independently re-performs the source/shipment comparison and emits the diff. The fixed F5 enforcement rule applies the owner-defined gate condition to that diff; the Comparator issues no verdict.”

## 3. Step 6 carried items — one omission in §10

The paper's §10 correctly carries forward the Step 6 stream-entry correction, checker-verdict correction, discharge-record supersession, LINK equivalence and provisional identity taxonomy.

The Step 6 architecture also explicitly carries two unresolved audit items that are absent from the paper's §10 list:

- **CANON-1 excluded paths** (U-1).
- **Family E schema** (U-3).

Please add both to the carry-forward list, with their existing unresolved status. The revamp need not solve them; it should make clear they remain carried by the Step 6/Step 7 line and are not silently closed by this paper.

## 4. Seven-joint reconciliation

I checked the paper against the complete owner rulings record. All seven are represented correctly in substance:

1. **Pins/minting:** SHA-256 of document content is the ID and pin; names are labels; editions supersede by ID chain; both locators remain.
2. **Dictionary:** next revision carries SUCCESS, DESTINATION, YES, PREVAIL and the adopted category/collision splits; the six foundational proposals remain unadmitted; Dictionary 0.5 remains unchanged until admission.
3. **Packing:** orchestrator decides required case contents per task; Distiller follows that decision.
4. **Gate:** direct factual comparison to source.
5. **Taxonomy:** Library → validated → Shelf (double-checked/fact) → EXON (distilled, addressed operational form of Shelf fact); Comparator terminus retained.
6. **Custody:** Ben's laptop/laptop room; VM excluded for custody-grade runs due to NoNewPrivs; supervisor-less smoke remains a one-call exception.
7. **Receipt re-performance:** mechanical receipt; Comparator re-performs directly from source and shipment; independent second implementation checks the tooling; judgment claims are declined/escalated; 1-in-5 pin-seeded sample with full escalation on mechanical unmatched item or dispute; gate is the fixed function of the diff, with matched defined by hash equality at pinned address and no undeclared gaps.

No joint is reopened by this review.

## 5. Briefcase design and composition review

The paper preserves the central Briefcase design:

- task-scoped case per assignment, clean start and no inherited working mind;
- Shelf as source, case as task-specific map/slice rather than a second source of truth;
- Required / Available / Historical categories;
- on-demand retrieval and selective historical dereference;
- one-turn sufficiency;
- task-specific packing decided by the orchestrator;
- durable outputs, manifest and provenance, with transient context discarded;
- modular verification through pinned, versioned seam contracts and independent fixtures.

The principal seams listed in §7 cover the important composition boundaries: Duenna ↔ Distillery/Briefcase; Briefcase ↔ EXON; Distiller ↔ WW; WW ↔ RECORD; Comparator ↔ RECORD/EXON; EVALUATOR ↔ external evidence; and EXAMINER ↔ evidence paths.

The paper also correctly refrains from promoting the other Kit-session candidates into requirements: coverage fences, sealed deliverable/residue layers, address-class trust distinctions, Tests A/B, mutation testing and correlated-failure exercises remain discussion candidates unless separately adopted. The cold-read close is the exception noted in §2.3: its candidate status should be preserved rather than made normative by implication.

## 6. Final disposition

**Substantive architecture: accepted.** I do not dispute the Comparator placement, the Distiller/WW split, EXON's supporting-language/addressing role, or the overall process and implementation dependency order.

**Corrections requested:** §2 smoke provenance; §3 Shelf/RECORD distinction; §5 step 5 gate ownership; §5 step 7 close-certification status; §4.3 mechanical-only WW fidelity wording; and §10's two omitted Step 6 carried items (CANON-1 excluded paths and Family E schema).

These changes do not require redesigning the paper or reopening any of the seven rulings. They preserve the agreed architecture and prevent a few important distinctions from being blurred.

This review is not an amendment to Rev 26, an implementation specification, a build authorisation, or battery authority. The paper's own no-build status remains in force.

## 7. Source record and pins consulted

- `record/FRAMEWORK-REVAMP-DESIGN-2026-11-17.md` — blob `4662f68ea100e3844cc1346717b113cc704230f1`, supplied commit `d09c805a`.
- `record/REVAMP-JOINT-RULINGS-2026-11-17.md` — blob `0b969cb11b8e15d736a880405bdda9c9d076570a`.
- `record/DUENNA-STEP6-ARCHITECTURE.md` — blob `a21cb431cd6c97c17cfb999caae106909ec1a3c9`.
- `record/AGENT-BRIEFCASE-DESIGN-2026-11-16.md` — blob `33d647a0c22f0fdd58e8716ad7363c12b1b19ea3`.
- `record/ALEX-STEP6-REVAMP-INDEPENDENT-MAP-2026-11-17.md` — blob `5a4e819998c782ce2e2fa02d7ef3b087269fd5df`.
- `record/ALEX-DUENNA-SMOKE-ADJUDICATION-2026-11-16.md` — blob `5e34ce683c3951f10f2441a70b8fb0b0c703d344`.
- `record/ALEX-DUENNA-REV03-APPROVAL-2026-11-16.md` — blob `7b4dbe42ad8862925c002baf403039d57e89be2a`.
- `record/CLAUDE-WW-RECEIPT-REPERFORMANCE-DISCUSSION-2026-11-17.md` — blob `fee30de235e3ed95c1ba4c73fe8f48a8e6ff71c7`.
- `duenna/plaincode/EXON-DELEGATED-RULINGS-2026-11-16.md` — blob `bd47763389abcdd2ea837f575db47479ce2e58f0`.
- `duenna/plaincode/EXON-OWNER-RULINGS-2026-11-16-ADDENDUM-02.md` — blob `cecf55f67991b37cd7632835f131d49d1254ac88`.
