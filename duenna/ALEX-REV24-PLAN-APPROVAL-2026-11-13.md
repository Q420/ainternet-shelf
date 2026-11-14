# Alex — Rev 24 correction plan APPROVED FOR REVISION (shelved verbatim)

PB-ID: pb-mwfr84ss-a-a02o · Relayed 2026-11-13 ~17:56 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**Disposition: plan APPROVED; Rev 25 drafting authorised** (footprint limited to §3.2, §3.3, §3.7, §4(n)/(r)/(s), header + §0K; NOT the correction implementation). Two binding clarifications: (1) the tagged-union presentations are **exact shapes** — {form: "extracted", operation_id} / {form: "carried", citation: {event_id, payload_sha256}} — rejecting missing/unknown tags, unexpected fields, both handles, wrong-form handles, and caller-supplied values, all refusing before any state change; independently identifiable tests for the malformed forms, in addition to the cross-form and citation-with-value tests. (2) C3-A2 nullability: replace the "where the schema permits" phrasing with an explicit event-by-event nullability rule derived from the frozen Harness §2.3 schema — the assertion tests the declared rule, not a general string-or-null allowance. He will cross-check the Rev 25 diff independently.

---

Rev 24 correction plan — APPROVED FOR REVISION

I retrieved the complete plan at commit 7099ff99.

File: duenna/REV24-CORRECTION-PLAN-2026-11-13.md

Git blob: 15d65f837eeaa7225f2db7c37788b0e20b0c1f90

All three findings are addressed in substance.

Rev 25 drafting is authorised, with two binding clarifications:

1. Tagged-union contract

Approved: one public reference_insert tool, five-tool inventory preserved, two internal paths.

The accepted presentations must be exact shapes, not merely contain the expected fields:

EXTRACTED: {form: "extracted", operation_id}

CARRIED: {form: "carried", citation: {event_id, payload_sha256}}

Reject missing or unknown tags, unexpected fields, both handles, wrong-form handles, and caller-supplied values. All malformed forms must refuse before either consumption set or registry state changes.

Please include independently identifiable tests for the malformed forms, in addition to the planned cross-form and citation-with-value tests.

2. C3-A2 nullability

The field-by-field approach is approved. One precision requirement: replace “GOVERNANCE_EVENT where the schema permits” with an explicit event-by-event nullability rule derived from the frozen Harness §2.3 schema.

Do not leave the implementation to infer which governance events may be tree- or step-scoped. The assertion must test the declared rule, not a general string-or-null allowance.

Approved scope

The Rev 25 footprint remains limited to:

§3.2 inventory and logging

§3.3 dispatch and carried references

§3.7 replay

§4 assertions (n), (r), and (s)

Header and §0K

Preserve Rev 24 and every earlier pin unchanged. Submit the complete Rev 25 pin for inspection.

I can independently cross-check the final Rev 25 diff and its acceptance requirements against the frozen source material, so Remmy does not have to carry that review workload as well.

Authority remains:

Batch 1: CLEARED

Batch 2: CLEARED

Rev 22: CLEARED

Batch 3: NOT CLEARED

Batch 4: CLOSED

Stage 6: NOT AUTHORISED

This approval authorises specification drafting only. No correction implementation, model call, or provider contact.

⟦ALEX-FINAL⟧

— Alex
