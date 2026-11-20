# EXON — Historical Replay Matrix 0.2 (Source-Binding Revision)

**Prepared by:** Alex  
**Date:** 2026-11-11  
**Status:** Source-binding revision only. TEST DESIGN — NOT EXECUTED.  
**Supersedes:** No prior artefact. This is a new source-binding companion to EXON-HISTORICAL-REPLAY-MATRIX-01.md; the earlier matrix remains preserved.

## 1. Execution gate

Formal replay remains **NOT AUTHORISED / NOT OPEN**. Dictionary 0.2 must first be delivered as a whole revision, challenged, reconciled, and fixed/version-pinned. Ben must then authorise the replay stage. This document does not execute, simulate, or report any replay result.

## 2. Hash notation

- **SHA-256** means the raw artefact hash supplied by the canonical record or recorded inside the frozen foundation.
- **Git blob SHA** is Git's object identifier. It is not presented as a raw-file SHA-256.
- A PB-ID is an exact bridge-message locator, not a content hash.
- Where the retrieved material does not provide a source hash, the field is explicitly marked **NOT SUPPLIED**. No hash is inferred from a nearby file or from a Git blob id.

## 3. Twelve-case source-binding register

### RPL-01 — V1 acceptance: PARTIAL, superiority UNMET and excluded

**Claim under test:** a partial acceptance may include only criteria whose result is MET; an UNMET criterion is excluded from accepted_scope and does not become full acceptance.

**Locator supplied:** Alex letter PB-ID `pb-mwbjmwcc`; Shelf commit `f02ec0a193293c4154757e1e660b553e20498832`.

**Related artefact:** `duenna/qwen-ab/QWEN-AB-RESULTS.json`, SHA-256 `87cfa2cec10a663bf3f14c1768141009bde87bbeb9e600592dfbb59c33f9cf97`.

**Binding status: INCOMPLETE.** The fetched V1 results JSON contains no PARTIAL or UNMET occurrence and does not itself ground this acceptance demonstration. The PB-ID and commit identify the claimed historical reference, but the letter's canonical artefact and content hash have not been retrieved in this pass. Do not use the V1 results JSON as a substitute. Formal fixture construction waits for the exact letter artefact/hash or a canonical Shelf section that contains the demonstration.

### RPL-02 — S2 scoped source absence / UNTRACEABLE

**Primary result:** `duenna/qwen-ab/v248-results/QWEN-AB-V2R-RESULTS.json`, SHA-256 `fa99b69e08b624a1974ecec7a6f6412f003deca68e5e9ff1c640ec0edd0943a9`, zero-based `runs[17]` (T06 Arm C).

**Frozen foundation:** `duenna/qwen-ab/v248-foundation/FOUNDATION.json`, SHA-256 `c3b917fea035ffc6c3c6ac17e36daac1892482720052c18f0ed0e2b67ae97a9a`, commit `acd3893`.

**Search implementation and corpus scope pinned by that foundation:**
- `run_c.py`: SHA-256 `65de6defa5d3f7f6deb5548cff726f3bff4460101b9df35a7ab8b78eb8e91980`.
- frozen `sections.jsonl`: SHA-256 `9ad80622094187d01f44e6d0cdefcb05dd9d8bb3143c6ef48cb46408d88ca2de`.
- frozen `manifest.json`: SHA-256 `79e91a6d6f340ccac3b130e157b82c637e9b30dd761660ded60445bcde54a2d8`.
- The foundation authorisation binds SHA-256 `c3b917fea035ffc6c3c6ac17e36daac1892482720052c18f0ed0e2b67ae97a9a`.

**Locator:** V2R T06 Arm C, `runs[17].process.steps`, especially STEP-A S2; `runs[17].process.tool_log` records the S2 procedure and its search/candidate/admission/attribution stages.

**Scope correction:** the pinned code searches the **frozen corpus index and admission manifest**, not only the three-document T06 evidence pack. The admissible scope is exactly the frozen `sections.jsonl` plus `manifest.json` above, no wider. The result is UNTRACEABLE within that bounded corpus procedure. It is not a claim of global non-existence and must not be relabelled ABSENT without the dictionary's bounded-search requirements being met.

### RPL-03 — V1 T05 Arm A: INCORRECT + RELEASED, not in-loop BLOCKED

**Primary result:** V1 results JSON, SHA-256 `87cfa2cec10a663bf3f14c1768141009bde87bbeb9e600592dfbb59c33f9cf97`, zero-based `runs[11]` (T05 Arm A).

**Interpretive source:** `duenna/qwen-ab/QWEN-DUENNA-AB-REPORT-V1.md`, Git blob SHA `502dc35da1d7e5088e0dccb05a4aaa5697ebedd7`, in Shelf commit `f02ec0a193293c4154757e1e660b553e20498832`.

**Grounded distinction:** the report says Arm A's defective first-attempt record was shipped unchecked and later flagged by the offline measurement checker (outcome class RELEASED-WITH-FLAG). The JSON's `final_gate_decision: BLOCKED` is the offline measurement checker result, not an in-loop gate that prevented release. Correct semantic reading: the output was INCORRECT and RELEASED. It was not BLOCKED in the dictionary's in-loop sense.

### RPL-04 — V1 T05 Arm B: in-loop BLOCKED, then corrected on retry

**Primary result:** same V1 results JSON SHA-256 as RPL-03, zero-based `runs[12]` (T05 Arm B).

**Interpretive source:** same V1 report and commit as RPL-03.

**Grounded distinction:** attempt 1 was blocked by the in-loop gate; the bounded retry corrected the record and passed. This is the positive BLOCKED control. Do not collapse the first-attempt gate event into the final corrected outcome.

### RPL-05 — T05 cross-arm and V2R replication

**V1 pair:** V1 results JSON SHA-256 `87cfa2cec10a663bf3f14c1768141009bde87bbeb9e600592dfbb59c33f9cf97`, `runs[11]` Arm A and `runs[12]` Arm B; V1 report Git blob SHA `502dc35da1d7e5088e0dccb05a4aaa5697ebedd7`.

**V2R replication:** V2R results JSON SHA-256 `fa99b69e08b624a1974ecec7a6f6412f003deca68e5e9ff1c640ec0edd0943a9`, `runs[12]` Arm A, `runs[13]` Arm B, `runs[14]` Arm C. Interpretive report: `duenna/qwen-ab/v248-results/BATTERY-V2R-REPORT.md`, Git blob SHA `fddd31d45a6a8ca9324d792c396019ab1541a63a`. Frozen foundation SHA-256 as in RPL-02.

**Grounded distinction:** V2R report records A BLOCKED, B BLOCKED then corrected-on-retry, C mechanically emitted on first attempt. Preserve arm identity, attempt number, artefact identity, and gate event. A result from one arm must never be used to label another arm.

### RPL-06 — Enumeration completeness: declared, evidenced, evaluated

**Exact source sections:**
- `d3-v07#008`, SHA-256 `458a030b6159cbe683df9bb4f5780839dadc94b6cbf6356f8e8842eb2a4c54e5`.
- `d3-v09-specification#008`, same SHA-256 `458a030b6159cbe683df9bb4f5780839dadc94b6cbf6356f8e8842eb2a4c54e5`.

**Shelf retrieval locator:** `duenna/plaincode/EXACT-RETRIEVAL-01.md`, commit `e2d70a6`.

**Grounded distinction:** declaration, application evidence, and evaluation are three separate requirements. Missing any one yields INDETERMINATE, never NOT FIRED. The two section IDs are distinct records with byte-identical content/hash; preserve both identities.

### RPL-07 — Available fixtures do not imply unavailable fixtures passed

**Exact source:** `duenna-step7-plan#006`, SHA-256 `6bd6a147abeab7877723a87985b93a58b65cfb7f5d08d0aab5faf1d8d83b251e`.

**Supporting baseline source:** `duenna-step7-plan#002`, SHA-256 `9a424e4917f90177ee808f7bf5b6ba0ebd41c395299b42abad8d63fa76d860cf`.

**Shelf retrieval locator:** `duenna/plaincode/EXACT-RETRIEVAL-01.md`, commit `e2d70a6`.

**Grounded distinction:** available and unavailable/separately gated fixtures must be reported separately; a green available subset never implies the outstanding set passed. Nothing proceeds on a red baseline.

### RPL-08 — Permission is not obligation satisfaction

**Exact source:** `d3-v07#007`, SHA-256 `a2385bd1544278f364e6552e00038f3768a5e7d3c26d14de1d49450d8d73a8f3`.

**Shelf retrieval locator:** `duenna/plaincode/EXACT-RETRIEVAL-02.md`, commit `25378b3`.

**Grounded distinction:** permission to act is not evidence that a bound obligation is met. A fully permitted run with an unmet instance remains incomplete.

### RPL-09 — REPORTED repetition does not upgrade evidence class

**Primary fixture:** V1 evidence manifest `duenna/qwen-ab/QWEN-AB-EVIDENCE-MANIFEST.json`; T09-FR-C pack SHA-256 `53170d5e00f046ca2f3de631533664f5c00630e8f9f32b3628c2b10c612ebb07`; pack items `obligation-spec` and `receipt-FR-C`.

**Result locator:** V1 results JSON SHA-256 `87cfa2cec10a663bf3f14c1768141009bde87bbeb9e600592dfbb59c33f9cf97`, `runs[21]` (T09-FR-C Arm A) and `runs[22]` (T09-FR-C Arm B).

**Grounded distinction:** the receipt's `[reported]` class fails the obligation's `[verified]` requirement. **Limitation:** this historical case proves REPORTED is not VERIFIED; it does not itself test repeated transmission. The repeated-seat adversarial variant remains a designed extension, not a historical result.

### RPL-10 — VERIFIED requires independence; record presence is not enough

**Exact source:** `vane-examination-report-v24#001b`, SHA-256 `3ff112582fa0d728a1889514fb6b9f9a02f4f8486912488e6fd804cb925161d9`.

**Corroborating source:** `r60-revision-change-record#009`, SHA-256 `5db36f75948ce78dc24e930f48db783de0f224ecf727353b01d8328161e0af15`.

**Result locator:** V2R results JSON SHA-256 `fa99b69e08b624a1974ecec7a6f6412f003deca68e5e9ff1c640ec0edd0943a9`, `runs[17]` (T06 Arm C), especially S4 and its source-extraction trace.

**Grounded distinction:** the identity sabotage was not executed by the implementer and was assigned to independent examination. The result record is not independent execution evidence. This is a negative proof/control; it does not establish that a qualifying independent verification occurred.

### RPL-11 — Errata, preservation, reliance, and supersession limits

**Shelf retrieval locator:** `duenna/plaincode/EXACT-RETRIEVAL-03.md`, Git blob SHA `cb2e9085743db06ab98f5c785d9bf8ca72170e93`, commit `cf6f2fe`.

**Exact section IDs named in the retrieval:**
- `process-tree-v04#021a` — errata preserves corrected entries rather than deleting originals.
- `d3-v08-change-record#004` — conditional reliance precedent.
- `fixture-harness-v09#018` — checker verdicts carried as REPORTED; checker reliance must be recorded.

**Source-hash status: INCOMPLETE.** The retrieved Exact Retrieval 03 text supplies these exact section IDs and quotations but does not supply their individual source SHA-256 values. The retrieval document's Git blob SHA is not a substitute for those source hashes. Obtain exact source hashes before formal fixture construction.

**Grounded limit:** these precedents do not establish a general supersession policy, atomic live-head update, or concurrency/conflict-resolution mechanism. The latter mechanisms remain UNKNOWN.

### RPL-12 — Task registration and authority resolution are not self-authenticating

**Primary retrieval locator:** `duenna/plaincode/EXACT-RETRIEVAL-03.md`, Git blob SHA `cb2e9085743db06ab98f5c785d9bf8ca72170e93`, commit `cf6f2fe`.

**Gap register:** `duenna/plaincode/INFRASTRUCTURE-GAP-REGISTER-01.md`, Git blob SHA `e58b91a648edb57a42d35bead52e47d3d004cdb0`.

**Exact authority references named in the retrieval:** `sync-document#003` (current authority state and specific Duenna delegation); `process-tree-v04#018` (structural authority model); `d3-v07#055`, SHA-256 `37ac8ce068954e64e787ce2fbf5e75297351f3baa4e8f6f9b4e98c4a07248e5e` (binding is not authority).

**Grounded limit:** Crusher's exact answer for task registration/versioning is UNKNOWN. A task_id does not prove registration; an authority reference does not prove that a complete machine-readable authority registry exists. `sync-document#003` records current state and specific delegation, not a general registry.

**Source-hash status: PARTIAL.** Individual hashes for `sync-document#003` and `process-tree-v04#018` are not supplied in Retrieval 03. Do not invent them.

## 4. Binding status summary

| Case | Source binding | Limitation |
|---|---|---|
| RPL-01 | INCOMPLETE | PB-ID and commit supplied; canonical letter artefact/hash not retrieved. V1 results JSON is not the acceptance proof. |
| RPL-02 | BOUND | Frozen corpus scope pinned by foundation, index/manifest hashes, run_c.py hash, and result locator. Scope is corpus index + manifest, not just T06 pack. |
| RPL-03 | BOUND | V1 result locator plus report interpretation distinguishes offline flag from actual release. |
| RPL-04 | BOUND | V1 result locator plus report identifies in-loop block and corrected retry. |
| RPL-05 | BOUND | V1 and V2R result hashes, indices, reports, and foundation pin. |
| RPL-06 | BOUND | Exact source sections and SHA-256 supplied. |
| RPL-07 | BOUND | Exact source sections and SHA-256 supplied. |
| RPL-08 | BOUND | Exact source section and SHA-256 supplied. |
| RPL-09 | PARTIAL | REPORTED versus VERIFIED is grounded; repetition adversary is design-only. |
| RPL-10 | PARTIAL | Grounded negative evidence; no successful independent verification event. |
| RPL-11 | PARTIAL | Exact section IDs and quotations; individual source SHA-256 values not supplied. |
| RPL-12 | PARTIAL | UNKNOWN and gap register grounded; hashes for some exact authority sections not supplied. |

## 5. Required source closure before execution

1. Retrieve the canonical artefact behind PB-ID `pb-mwbjmwcc` and its content hash. Confirm it contains the PARTIAL/UNMET acceptance case; do not infer from the V1 results JSON.
2. Retrieve the individual source SHA-256 values for `process-tree-v04#021a`, `d3-v08-change-record#004`, `fixture-harness-v09#018`, `sync-document#003`, and `process-tree-v04#018`.
3. Preserve the RPL-09 repetition variant as a designed adversarial fixture, not a historical case.
4. Preserve RPL-10 as a negative control unless a source for an actual independent reproduction is retrieved.
5. Keep the RPL-02 S2 scope exactly to the frozen corpus index and admission manifest hashes; never widen it to the world or all Shelf material.

**Disposition:** the matrix is now bound to the exact source artefacts and locators available in the trigger materials. Cases with missing canonical hashes or missing historical proof are explicitly left incomplete. This is not a claim that all twelve cases are fully source-closed. No formal replay has been executed.
