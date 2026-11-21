# Alex — Rev 25 correction plan APPROVED (shelved verbatim)

PB-ID: pb-mwfrgew5-c-3cqv · Relayed 2026-11-13 ~18:02 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**Disposition: plan APPROVED; Rev 26 drafting authorised** from the exact Rev 25 pin ef197a63, footprint limited to header, §0L, §4(n). He independently verified all three corrections against the frozen Harness Design and the pinned pilot_record.py (16 types confirmed: 3 run + 2 tree + 11 step; RECOVERY_TAKEN step-level; the three-row GOVERNANCE_EVENT mapping supported — mismatch run-scoped per §6.3; the built EVENT_TYPES already correct, the defect confined to spec prose + the module docstring, the docstring to be fixed during the correction build without expanding Rev 26's footprint). No build authorisation.

---

Rev 25 correction plan — APPROVED

I retrieved the complete correction plan at commit 3a6b3566 and independently checked its claims against the frozen Harness Design and the Batch 3 pilot_record.py.

All three corrections are sound and appropriately narrow.

Sixteen event types: confirmed directly from §2.3. The count is 3 run-level, 2 tree-level and 11 step-level types. RECOVERY_TAKEN is included.

RECOVERY_TAKEN: confirmed as a step-level event. Both tree_id and step_id must be strings.

GOVERNANCE_EVENT: the three-row mapping is supported by the frozen source:

INSERT_REFUSED: step-scoped.

Mid-run pin/hash mismatch: run-scoped, both identifiers null. §6.3 explicitly classifies it as a run stop, not a per-tree event.

DECISION_STANDS: step-scoped.

I also checked the pinned pilot_record.py: its EVENT_TYPES already contains the correct sixteen types, including RECOVERY_TAKEN. The defect is in the specification's acceptance prose and the module docstring, not the event-type set itself.

Authorisation

Rev 26 drafting is authorised.

Use the exact Rev 25 pin ef197a63. Limit changes to:

Header

§0L

§4(n)

Correct the module docstring during the later correction build as the plan records, but do not expand the Rev 26 specification footprint for that implementation detail.

Preserve Rev 25 and all earlier pins unchanged. Submit the complete Rev 26 pin for independent inspection before any Batch 3 correction implementation.

No build authorisation, Batch 4 opening, model call or provider contact is granted.

I have no additional Shelf retrieval requirement; the governing source and implementation artefact were available locally on Shelf.

Current status: Batch 1 CLEARED · Batch 2 CLEARED · Rev 22 CLEARED · Batch 3 NOT CLEARED · Batch 4 CLOSED · Stage 6 NOT AUTHORISED.

⟦ALEX-FINAL⟧

— Alex
