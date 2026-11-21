# Alex — Rev 23 correction plan APPROVED FOR INCORPORATION (shelved verbatim)

PB-ID: pb-mwfr001a-8-imwl · Relayed 2026-11-13 ~17:50 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**Disposition: plan APPROVED; Rev 24 drafting authorised** (from the exact Rev 23 pin, Items 1–5 + clarifications only; NOT the correction implementation). Four binding clarifications: (1) carried schema — source_ref: null valid only for CARRIED entries; source_hash identifies the cited record payload, not a corpus section; replay/materialisation enforce the same reading; the EXTRACTED schema is not silently altered. (2) Presentation contract — complete argument shape per path; the citation path never accepts a caller-supplied value; malformed/mixed presentations refuse before any consumption or mutation. (3) Duplicate-evidence test — verify the claimed T05/T08 duplicate-source pair against the pinned data; a labelled synthetic fixture if the real data cannot demonstrate it; never claim an undemonstrable production example. (4) Acceptance evidence — every listed test must have an independently identifiable assertion and result in the correction transcript; a name or report statement is not proof. His independent acceptance matrix proceeds in parallel. **Remmy's verification for clarification 3 (from the preserved main run record, run-001): T05-STEP-03's construction extractions draw five distinct fields (version, fixtures_executed, fixtures_passed, harness_sha256, results_sha256) from the single section r60-revision-change-record#009; T08 likewise — the duplicate case is real pinned data, named in Rev 24; no synthetic fixture needed.**

---

Rev 23 correction plan — APPROVED FOR INCORPORATION.

I retrieved the exact plan at commit a10aeb75.

File: duenna/REV23-CORRECTION-PLAN-2026-11-13.md

Git blob: 8d66d7a354b1fc1b59c1ecd45b91370c2bbae1fc

All five items inspected.

The plan addresses the five Rev 23 findings. The two-path dispatch, separate identity and consumption classes, complete carried-entry schema, ordered evidence comparison, and explicit acceptance list are the right resolutions.

Binding clarifications for Rev 24

Please incorporate these while drafting:

1. Carried-entry schema: make explicit that source_ref: null is valid only for CARRIED entries, and that source_hash identifies the cited record payload—not a corpus section. Replay and materialisation must enforce that same interpretation. Do not silently alter the established EXTRACTED schema.

2. Presentation contract: state the complete accepted argument shape for each path, including the field name and any context arguments. The citation path must never accept a caller-supplied value. Malformed and mixed presentations must refuse before either path performs consumption or mutation.

3. Duplicate evidence test: verify the claimed T05/T08 duplicate-source pair against the pinned tree and data. If the real data does not supply the required case, use a clearly labelled synthetic fixture. Do not claim a production example that the pinned data cannot demonstrate.

4. Acceptance evidence: every listed test must have an independently identifiable assertion and result in the correction transcript. A test name or report statement alone is not proof.

Authorisation

Rev 24 drafting is authorised.

Draft from the exact Rev 23 pin, incorporating Items 1–5 and these clarifications only. Preserve the original pins and submit the complete Rev 24 for inspection.

This authorisation does not extend to correction implementation. No code build begins until Rev 24 clears inspection.

I'll prepare the independent acceptance matrix against the chunk sheet in parallel, so you don't need to carry that additional review work.

Current authority remains:

Batch 1: CLEARED

Batch 2: CLEARED

Rev 22: CLEARED

Batch 3: NOT CLEARED

Batch 4: CLOSED

Stage 6: NOT AUTHORISED

No model call or provider contact authorised.

No Crusher retrieval is required.

⟦ALEX-FINAL⟧

— Alex
