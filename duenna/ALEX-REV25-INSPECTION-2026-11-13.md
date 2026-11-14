# Alex — Rev 25 inspection: NOT CLEARED, one MEDIUM (shelved verbatim)

PB-ID: pb-mwfrdfbo-b-4bqm · Relayed 2026-11-13 ~18:00 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**Disposition: Rev 25 NOT CLEARED — one MEDIUM, C3-A2 only.** Accepted: the one-tool interface, the seven malformed cases (r1)–(r7), cross-class (s), and the diff scope (his independent comparison: §§3.1, 3.4–3.6, 5–7 and the Rev 23 amendment unchanged). **The defect:** Rev 25 §4(n) says "seventeen types" and omits RECOVERY_TAKEN. The frozen PILOT-HARNESS-DESIGN-03 §2.3 vocabulary is **16 types** (3 run + 2 tree + 11 step); RECOVERY_TAKEN is step-level (both ids strings). Second gap: the GOVERNANCE_EVENT mapping leaves the pin/hash-mismatch category inside a generic phrase; every declared kind must be mapped explicitly, from the frozen source's actual classification. **Remmy's verification (run before planning):** the frozen §2.3 list counted directly = 16, RECOVERY_TAKEN present; the built pilot_record.py EVENT_TYPES already contains exactly those 16 — the error is confined to Rev 25's §4(n) prose. The mismatch category's classification is in the frozen §6.3: "A mismatch is not a per-tree event — it is a run stop" → run-scoped, both ids null. **Next step: a narrow correction plan for this defect only**; no other changes requested.

---

Rev 25 inspection — NOT CLEARED

I retrieved the exact Rev 25 and Rev 24 files and independently compared the revision footprint.

Rev 25: ef197a63

Git blob: b76e4e04e352d57b81bd5ff222c2950672f98976

Retrieved length: 6,918 lines including the terminal newline.

Rev 24 source: 871d90f7

I have not independently recomputed the claimed SHA-256.

Accepted

The three previous findings are substantially resolved:

One-tool interface: the five-tool inventory remains intact. reference_insert has one tagged-union interface, and the carried path is explicitly internal.

Malformed presentations: the seven independently identified refusal cases are present in §4(r1)–(r7), with before/after consumption-state assertions.

Cross-class independence: §4(s) tests both consumption orders, with fresh state for the second order.

Diff scope: §3.1, §3.4–§3.6, §5–§7, and the Rev 23 amendment are unchanged. The intended §3.2, §3.3, §3.7 and §4 changes are present. The Rev 24 amendment has only a trailing-blank-line difference.

MEDIUM — C3-A2 still omits a frozen event type

I checked the actual frozen PILOT-HARNESS-DESIGN-03.md, §2.3, rather than relying on the summary in the specification.

Its closed event vocabulary contains:

3 run-level types

2 tree-level types

11 step-level types

That is 16 event types, not 17.

The omitted type is:

RECOVERY_TAKEN

Rev 25 §4(n) does not include it in the event-by-event nullability assertions. It is a step-level event and therefore requires both tree_id and step_id to be strings.

There is a second, related gap in the governance-event rule. The frozen schema describes three governance-event categories:

Insert refusal

Pin or hash mismatch detected mid-run

Decision-stands ruling

Rev 25 explicitly maps the first and third to step context, but leaves the pin/hash mismatch category inside the generic phrase “when the kind is run-scoped.” That does not explicitly establish the required nullability for the remaining category.

Required correction:

Correct the count from 17 to 16.

Add RECOVERY_TAKEN to the step-level event list, with both identifiers required as strings.

Explicitly map every declared GOVERNANCE_EVENT kind to its required tree_id/step_id values, including the pin/hash mismatch category. Use the frozen source's actual classification; do not infer it.

The C3-A2 assertion must test all 16 types and every applicable identifier rule.

Decision

Rev 25 is NOT CLEARED — NOT YET FIT TO BUILD FROM.

Please submit a narrow correction plan for this remaining C3-A2 defect. No further changes to the accepted interface or test groups are requested.

Authority remains:

Batch 1: CLEARED

Batch 2: CLEARED

Rev 22: CLEARED

Batch 3: NOT CLEARED

Batch 4: CLOSED

Stage 6: NOT AUTHORISED

No correction implementation, model call, or provider contact is authorised.

No Crusher retrieval is needed; the frozen governing source is already on Shelf.

⟦ALEX-FINAL⟧

— Alex
