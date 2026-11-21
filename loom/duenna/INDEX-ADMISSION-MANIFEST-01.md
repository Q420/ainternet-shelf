# EXON / QWEN A/B — CRUSHER INDEX ADMISSION MANIFEST 01

Produced before indexing, per Alex's clearance
pb-20261111-exon-index-admission-clearance (2026-11-11),
carrying Ben's indexing proposal. Sources are the
approved Shelf copies (Q420/ainternet-shelf), fetched
and verified: every file's computed git blob SHA
matches the shelf's own header for that file
(34 of 34 MATCH; full hashes in the
admission script's sidecar record).

Treatments: **markdown** = the established mechanism
(heading ranges, S1 line slices ≤3500 chars, chained
digests). **json-runs** = one section per run record
(locator = JSON Pointer in heading_path, e.g.
`/runs/17`), all run fields preserved intact, plus a
document-level section carrying every non-run
top-level key. **json-components** = one section per
component (locator `/components/<name>`) plus a
document-level section. **json-doc** = the whole small
document as document-level sections. JSON canonical
form is the raw file text (digest = file sha256);
no field is flattened, normalised, or discarded.

| doc_id | Shelf path | file sha256 / git blob | status | treatment |
|---|---|---|---|---|
| exon-dictionary-01 | `duenna/plaincode/DICTIONARY-01.md` | 80bf7062fce5… / blob f1640c6cda… (MATCH) | historical — superseded draft | markdown |
| exon-dictionary-02 | `duenna/plaincode/DICTIONARY-02.md` | 0adbb72e5964… / blob 4e886812d3… (MATCH) | historical — superseded draft | markdown |
| exon-dictionary-03 | `duenna/plaincode/DICTIONARY-03.md` | eae03759a9ea… / blob 232f7e170c… (MATCH) | historical — superseded by 0.4 | markdown |
| exon-dictionary-04 | `duenna/plaincode/DICTIONARY-04.md` | 0717bb6c3b37… / blob 49c2408065… (MATCH) | canonical candidate — Rev 3, challenge-passed, unfrozen | markdown |
| exon-dictionary-03-reconciliation | `duenna/plaincode/EXON-DICTIONARY-03-TOKEN-FIELD-RECONCILIATION-01.md` | 6868d089e0de… / blob 0873b5dadc… (MATCH) | historical — design record | markdown |
| exon-dictionary-03-challenge | `duenna/plaincode/EXON-DICTIONARY-03-INDEPENDENT-CHALLENGE-01.md` | b34c38ad8348… / blob 1b0a740dd1… (MATCH) | historical — evidence | markdown |
| exon-dictionary-04-challenge-01 | `duenna/plaincode/EXON-DICTIONARY-04-INDEPENDENT-CHALLENGE-01.md` | d8095ba52830… / blob b7d7e17a0a… (MATCH) | historical — evidence | markdown |
| exon-dictionary-04-challenge-02 | `duenna/plaincode/EXON-DICTIONARY-04-INDEPENDENT-CHALLENGE-02.md` | 7389712f1125… / blob 9e07bc9fdf… (MATCH) | historical — evidence | markdown |
| exon-field-matrix-01 | `duenna/plaincode/EXON-FIELD-MATRIX-01.md` | 4816adc3ed3e… / blob 4ee9408932… (MATCH) | historical — superseded draft | markdown |
| exon-field-matrix-01-review | `duenna/plaincode/EXON-FIELD-MATRIX-01-INDEPENDENT-CONSISTENCY-REVIEW-01.md` | cc502ecc2ae2… / blob ec0ba3e4ce… (MATCH) | historical — evidence | markdown |
| exon-field-matrix-02-alex | `duenna/plaincode/EXON-FIELD-MATRIX-02-ALEX-CONSOLIDATED-RECONCILIATION-DRAFT.md` | a143a1ae8405… / blob d25f4b5ef1… (MATCH) | historical — parallel repair | markdown |
| exon-field-matrix-02-remmy | `duenna/plaincode/EXON-FIELD-MATRIX-02-REMMY-INDEPENDENT-REPAIR.md` | df1351e1b05c… / blob da5df6d7f5… (MATCH) | historical — parallel repair | markdown |
| exon-field-matrix-03-merged | `duenna/plaincode/EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-DRAFT.md` | 4aba92137495… / blob 87c2349959… (MATCH) | canonical — accepted matrix | markdown |
| exon-infrastructure-gap-register | `duenna/plaincode/INFRASTRUCTURE-GAP-REGISTER-01.md` | 38a7ddb33475… / blob e58b91a648… (MATCH) | canonical — register | markdown |
| exon-flag-correction-proposal | `duenna/plaincode/EXON-FLAG-CORRECTION-SCHEMA-PROPOSAL-01.md` | a7beba251293… / blob 76da6e8aa5… (MATCH) | canonical — design record | markdown |
| exon-schema-layer-inventory | `duenna/plaincode/EXON-SCHEMA-LAYER-INVENTORY-01.md` | 5f323e71e5cc… / blob c0198b020d… (MATCH) | historical — evidence | markdown |
| exon-cross-type-audit | `duenna/plaincode/EXON-CROSS-TYPE-VOCABULARY-AUDIT-01.md` | b346334dcfd8… / blob 30bcda495e… (MATCH) | historical — evidence | markdown |
| exon-category-neighbour-audit | `duenna/plaincode/EXON-CATEGORY-NEIGHBOUR-BOUNDARY-AUDIT-01.md` | 06a7359512ff… / blob 0fe7bcd8f9… (MATCH) | historical — evidence | markdown |
| exon-replay-matrix-01 | `duenna/plaincode/EXON-HISTORICAL-REPLAY-MATRIX-01.md` | ab2335d4d36f… / blob d60ef8eb09… (MATCH) | historical — evidence | markdown |
| exon-replay-matrix-02 | `duenna/plaincode/EXON-HISTORICAL-REPLAY-MATRIX-02.md` | fac8cb832f3d… / blob 2586d3d775… (MATCH) | historical — evidence | markdown |
| exon-source-verification-d02-challenge | `duenna/plaincode/EXON-SOURCE-VERIFICATION-AND-DICTIONARY-02-CHALLENGE-01.md` | 110a001903a5… / blob 4d93343620… (MATCH) | historical — evidence | markdown |
| exon-exact-retrieval-01 | `duenna/plaincode/EXACT-RETRIEVAL-01.md` | c1a325d581aa… / blob 2e8b172484… (MATCH) | historical — evidence | markdown |
| exon-exact-retrieval-02 | `duenna/plaincode/EXACT-RETRIEVAL-02.md` | 27da3850e4f7… / blob 50d21e26aa… (MATCH) | historical — evidence | markdown |
| exon-exact-retrieval-03 | `duenna/plaincode/EXACT-RETRIEVAL-03.md` | b03f3ded640e… / blob cb2e908574… (MATCH) | historical — evidence | markdown |
| qwen-ab-report-v1 | `duenna/qwen-ab/QWEN-DUENNA-AB-REPORT-V1.md` | cf10a6604ca5… / blob 502dc35da1… (MATCH) | canonical — closed baseline report | markdown |
| qwen-ab-evidence-manifest | `duenna/qwen-ab/QWEN-AB-EVIDENCE-MANIFEST.json` | d544cad83cd8… / blob 314b575161… (MATCH) | canonical — battery evidence manifest | json-doc |
| qwen-ab-results-v1 | `duenna/qwen-ab/QWEN-AB-RESULTS.json` | 87cfa2cec10a… / blob 2218d1768c… (MATCH) | canonical — closed baseline results | json-runs |
| qwen-ab-v2r-results | `duenna/qwen-ab/v248-results/QWEN-AB-V2R-RESULTS.json` | fa99b69e08b6… / blob 34be60d1e6… (MATCH) | canonical — completed battery results | json-runs |
| qwen-ab-v2r-report | `duenna/qwen-ab/v248-results/BATTERY-V2R-REPORT.md` | d9fbd7638bf5… / blob fddd31d45a… (MATCH) | canonical — battery report | markdown |
| qwen-ab-v2r-authorisation | `duenna/qwen-ab/v248-results/ALEX-AUTHORISATION.json` | b9f63478a85c… / blob f4907b66dd… (MATCH) | historical — spent authorisation artefact | json-doc |
| qwen-ab-v2-voided-notice | `duenna/qwen-ab/v2-battery-voided/VOIDED.md` | ab39c7ee6288… / blob c0ec69988f… (MATCH) | canonical — incident record (battery VOID) | markdown |
| qwen-ab-spec-v1 | `duenna/qwen-ab/QWEN-DUENNA-AB-TEST-SPEC-V1.md` | 3868ab0f3fc3… / blob 420683eb8d… (MATCH) | canonical — V1 battery spec (closed) | markdown |
| qwen-ab-v2r-log | `duenna/qwen-ab/v248-results/battery-v2r.log` | 0075210814ac… / blob 9bb5462e78… (MATCH) | canonical — battery execution log | markdown |
| qwen-ab-foundation-v248 | `duenna/qwen-ab/v248-foundation/FOUNDATION.json` | c3b917fea035… / blob bfb0fdcedf… (MATCH) | canonical — V2.4.8 battery foundation (v9) | json-components |

## Exclusions, recorded

- `duenna/qwen-ab/v2-battery-voided/QWEN-AB-V2-RESULTS.json`
  — the VOID Battery 2 result records. EXCLUDED from
  indexing under the clearance's boundary: voided
  runs must not be retrievable as valid results. The
  VOID notice itself (VOIDED.md) IS admitted as the
  incident record.
- No other scoped source was excluded. The V1 spec
  and the v2.4.8 foundation were located on the shelf
  (QWEN-DUENNA-AB-TEST-SPEC-V1.md;
  v248-foundation/FOUNDATION.json, sha256 c3b917fe…,
  matching the foundation of record) and are admitted
  above.

## Historical-status rule

Historical versions and challenges are admitted AS
historical evidence, each under its own doc_id with
its status stated here and in the index manifest.
Retrieval of a historical text is not retrieval of
the current candidate; the canonical candidate for
the dictionary is exon-dictionary-04 and for the
field matrix exon-field-matrix-03-merged.
