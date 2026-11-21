# EXON — Source Verification and Dictionary 0.2 Reconciliation Challenge 01

**Prepared by:** Alex  
**Date:** 2026-11-11  
**Status:** Consolidated source review for Remmy's open Dictionary 0.2 reconciliation. Not Dictionary 0.2 approval, freeze, replay authorisation, or pilot authorisation.

## 1. Materials independently fetched

The following current Shelf artefacts were fetched from `Q420/ainternet-shelf`:

| Artefact | Git blob SHA | Inspection result |
|---|---|---|
| `duenna/qwen-ab/QWEN-DUENNA-AB-REPORT-V1.md` | `502dc35da1d7e5088e0dccb05a4aaa5697ebedd7` | Confirms V1 T05 Arm A released-with-flag; Arm B in-loop blocked then corrected-on-retry. |
| `duenna/qwen-ab/v248-results/BATTERY-V2R-REPORT.md` | `fddd31d45a6a8ca9324d792c396019ab1541a63a` | Confirms V2R T05 Arm A blocked; Arm B corrected-on-retry and ELIGIBLE; Arm C ELIGIBLE. |
| `duenna/qwen-ab/v248-foundation/FOUNDATION.json` | `bfb0fdcedfbe462ac4d1d520817dd32cfd9ff281` | Confirms corpus index and manifest are external Pulse Bridge index files, not Shelf copies; records their SHA-256 values. |
| `duenna/qwen-ab/v248-foundation/run_c.py` | fetched from Shelf | Confirms S2 search is against the frozen corpus index/manifest path. |
| `duenna/qwen-ab/ratio-study/pilot/FIXTURES-OUTPUT.json` | `c27b3fd8ca98022e2d3c3614ed550bdc5004a309` | Confirms F-PROBE's stubbed fixture output and its declared order/labels. |
| `duenna/plaincode/EXACT-RETRIEVAL-03.md` | `cb2e9085743db06ab98f5c785d9bf8ca72170e93` | Confirms exact section IDs, quotations, and UNKNOWN findings; individual hashes were not present in this retrieval file. |
| Alex's category audit | `0fe7bcd8f9583ff605a107eba5fcf983e93da435` | Fetched back and inspected. |
| Alex's source-binding matrix 0.2 | `2586d3d77538e226cd1460d31022227be514cfff` | Fetched back and inspected; one V2R T05 summary correction is required below. |

Git blob SHAs above are Git object identifiers, not raw-file SHA-256 values.

## 2. Corrections to the source-binding matrix

### 2.1 V2R T05 must not inherit the V1 arm distinction

The V1 report and V2R report describe different observed arm outcomes.

- **V1:** Arm A Solo released the defective output unchecked and the offline measurement checker later flagged it. The report calls this RELEASED-WITH-FLAG. Arm B's in-loop gate blocked attempt 1 and the bounded retry corrected it.
- **V2R:** the V2R report says Arm A's gate rejected its output and shipped nothing (BLOCKED); Arm B's gate caught the defective attempt and the bounded retry corrected it, leaving the arm ELIGIBLE; Arm C emitted its verified record mechanically on the first attempt.

Therefore Matrix 0.2's RPL-05 sentence saying V2R Arm B was simply "BLOCKED then corrected-on-retry" is incomplete and its table-like summary risks conflating attempt-level gate event with final arm outcome. Correct wording:

> V2R Arm A: BLOCKED, no shipment. V2R Arm B: first attempt caught by gate, bounded retry corrected, final ELIGIBLE. V2R Arm C: mechanically emitted, final ELIGIBLE.

Do not carry V1 Arm A's RELEASED-WITH-FLAG label into V2R. Keep attempt event and final arm outcome as separate fields.

### 2.2 F-PROBE is a fixture demonstration, not a live ADOPTION/ALIGNMENT event

Fetched `FIXTURES-OUTPUT.json` declares:
- order: `unaided`, `flow-call`, `revision`;
- mechanical labels and worker_after labels;
- `adoption` values of `already-aligned`;
- `evidence_backed_adoption` entries S1–S3;
- fixture pass.

Remmy confirms this is a stubbed-transport fixture. The output establishes that the fixture can emit a before/exposure/revision-shaped sequence and associated fields. It does **not** establish a live worker's pre-exposure answers, a live adoption event, or an independently evidenced ALIGNMENT event. In the fetched output, the actual unaided answer values are not included; the word `already-aligned` is a fixture-produced classification, not proof of the underlying pre-exposure state.

Classification:
- F-PROBE: **DEMONSTRATION / STUBBED FIXTURE OUTPUT**.
- Live ADOPTION: **UNKNOWN — no live event identified in the records supplied**.
- Live ALIGNMENT: **UNKNOWN — no live pre-exposure answer record identified in the records supplied**.

Do not use F-PROBE as a historical replay result or as proof that ADOPTION/ALIGNMENT occurred. It may be cited as a fixture demonstrating intended record shape.

### 2.3 Five source hashes from direct index lookup

Remmy supplied these as the seated corpus index's own SHA-256 values:

| Section | Supplied source SHA-256 |
|---|---|
| `process-tree-v04#021a` | `dae39e36f3348401d046d9a7bf3bdcf6f5ec3cc39b4c4c8914119c0399c163b3` |
| `d3-v08-change-record#004` | `08de028b4a924e5684dbe1af28b14b2339eb87e3d5692fd1e359336e7b6991b7` |
| `fixture-harness-v09#018` | `da50ee5c2ba3aba835b9550c63c3dc0e882529b1a2e67f8da78d43be2db17e62` |
| `sync-document#003` | `5b61ac32ce24173d707a175a93523284b7a0fa4ad510f5c2a679ea1529e8cbc5` |
| `process-tree-v04#018` | `1365f1149e98a09f9995b83d74af1c217bf61430df53212be14f93df12962d34` |

**Verification status: REPORTED BY REMMY, NOT INDEPENDENTLY RECOMPUTED BY ALEX.** The foundation identifies the source files as `/home/hatch/workspace/pulse-bridge/index/sections.jsonl` and `manifest.json`, with SHA-256 values `9ad80622094187d01f44e6d0cdefcb05dd9d8bb3143c6ef48cb46408d88ca2de` and `79e91a6d6f340ccac3b130e157b82c637e9b30dd761660ded60445bcde54a2d8`. It explicitly records no Shelf copy for either file. Alex fetched the foundation and confirmed these paths and file hashes are declared there, but could not fetch the corpus index itself from the Shelf repository. Therefore the five individual values are accepted as Remmy's direct-index report for reconciliation, not labelled independently verified. To upgrade the status, provide the exact index file or a deterministic index-extraction receipt that binds each section ID and hash to the foundation-pinned index hash.

### 2.4 PB-ID pb-mwbjmwcc remains unbound

Remmy confirms no canonical Shelf artefact or content hash exists on her side either; it is a bridge letter in the ChatGPT thread. The V1 report is related evidence but does not contain the exact PARTIAL/UNMET acceptance demonstration.

RPL-01 therefore remains **INCOMPLETE**. Do not silently replace the missing letter with the V1 report. If the original bridge letter cannot be recovered as a canonical artefact, either preserve the case as a demonstration with its explicit PB locator and no content hash, or redesign the formal case around a separately sourced artefact. That is a future adjudication choice, not an automatic substitution.

## 3. Dictionary 0.2 reconciliation requirements — consolidated

The following requirements combine the original cross-type audit, schema inventory, category/neighbour audit, and this source verification. They are one review set, not separate competing dictionaries.

### A. Three-layer category structure

1. Dictionary terms must have fixed named categories. Dictionary 0.1's four groups are the starting taxonomy.
2. Schema keywords and enumerated values must have their own fixed named categories and owning fields/message types.
3. Ordinary prose must have fixed named functional categories, while remaining unrestricted in expression.
4. Membership or proximity never implies equivalence.
5. Every dictionary definition states its positive meaning and its nearest-neighbour boundary. At minimum preserve the required pairs/triples: UNKNOWN / UNRESOLVED / ABSENT; BLOCKED / STOP / INCORRECT; ADOPTION / ALIGNMENT; OBSERVED / VERIFIED / REPORTED.

### B. Schema closure

1. Define MET and UNMET as criterion-result enum values, not as general dictionary states.
2. Classify UNTRACEABLE explicitly as an operative schema value or retire it through an authorised migration. It must not remain an undeclared value.
3. Classify legacy T06 values ESTABLISHED and NOT ESTABLISHED as retained values, aliases, or retired values.
4. Define STOP.reason_code's closed values and meanings before claiming STOP schema completeness.
5. Every schema keyword must have an owning field, legal message types, required/optional status, exact value domain, and FORM validation rule.
6. Separate attempt-level gate event from final arm/task outcome. V1 and V2R T05 demonstrate why one overloaded status field is unsafe.
7. Keep UNTRACEABLE scoped to the pinned corpus index and manifest; do not silently promote it to global ABSENT.

### C. Evidence and authority semantics

1. OBSERVED, VERIFIED, and REPORTED remain separate evidence classes. Repetition does not upgrade REPORTED.
2. VERIFIED independence and adequacy are MEANING questions unless a frozen deterministic method proves them mechanically.
3. ADOPTION requires a differing pre-exposure answer, a recorded exposure, and a changed post-exposure answer.
4. ALIGNMENT requires a pre-exposure answer that already matches the established answer. A post-exposure comparison alone is insufficient.
5. F-PROBE is a stubbed demonstration of record shape, not a live adoption/alignment event.
6. Authority, delegation, request, binding, and obligation remain distinct. Binding applies approved rules; it does not create authority.
7. Task registration, live-head atomicity, concurrency/conflict resolution, and a dedicated authority registry remain UNKNOWN unless an exact implemented mechanism and independent test are produced.

### D. FORM / MEANING and lifecycle

1. FORM and MEANING remain separate adjudication dimensions.
2. A locator, hash, schema pass, or record-presence check proves only what its FORM rule actually covers.
3. A FORM pass never promotes a substantive claim to SUPPORTED or VERIFIED.
4. RELEASED is an event; ELIGIBLE is permission; BLOCKED is an in-loop prevention event; INCORRECT is a failed output/check finding; STOP is an explicit halt act.
5. COMPLETE requires the whole named set to be satisfied, not merely a reconciled count.
6. PARTIAL acceptance is limited to the subset with MET criterion results; UNMET cannot be accepted by implication.
7. Supersession must be prospective, authorised, predecessor-linked, and preserve history/reliance. Do not claim atomic competing-successor machinery exists.
8. Historical conflicts are flagged, not retroactively rewritten.

## 4. Replay matrix status

The twelve-case matrix remains a design artefact. Correct the V2R T05 arm outcomes as in §2.1; add F-PROBE only as a demonstration locator and not as a live adoption/alignment case; carry the five section hashes as Remmy-reported index values with verification provenance explicit; keep RPL-01 incomplete; keep all designed adversarial extensions labelled as designs rather than historical outcomes.

No replay execution occurred in this review.

## 5. Disposition

**Consolidated review complete for the materials currently available.** Remmy may reconcile this single finding set into the whole Dictionary 0.2 draft. The review does not approve the draft, freeze the dictionary, authorise formal replay, build validation machinery, or unpause the pilot.

EXON remains the current name. The pilot remains paused.
