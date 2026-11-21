# Alex — T02 Recovery-Row Alignment Plan: TECHNICALLY APPROVED (relayed verbatim, 2026-11-13 ~21:02 PST)

PB-ID: pb-mwg00qk0-v-inua

T02 Recovery-Row Alignment Plan — TECHNICALLY APPROVED.

I fetched and inspected the plan at commit 7764ae67 (blob 64824906d4d0ad57fb685b4b7e235380aae14339). The diagnosis is sound. This is a genuine second producer of the same adjudication-row value, and the Correction 6 inventory missed it. The existing fixed-order guard makes current outputs correct, but does not satisfy the approved design rule that both producers locate the row by its declared class.

Approved scope: change only op_t02_apply_precedence_check() — replace state["t02_rows"][2] with state["t02_rows"][state["t02_classes"].index("adjudicator")]; leave every other driver function unchanged; leave the suite and its independent derivations unchanged; pin the revised driver externally through CONTINUATION-BATCH3-CORRECTION-7; preserve Correction 6 and all earlier bundles, records, findings and frozen artefacts; produce fresh runs, ledgers, provenance and a new Correction 7 evidence bundle; verify recovery payload content remains semantically identical and that the revised lookup is genuinely class-derived.

Authority ruling: Ben's Correction 6 build-go does not cover this additional code site. A fresh, explicit Ben build-go is required before implementation. Please put the narrow one-tap build-go card to Ben. No driver edits or implementation before that go is recorded. I can independently inspect the one-line diff, new pin, and resulting evidence after the build. No Crusher retrieval is required. Batch 3 remains NOT CLEARED. This plan approval does not authorise Stage 5 subject execution, Batch 4, or Stage 6.

⟦ALEX-FINAL⟧
