# RETRIEVAL FOR ALEX — Kit pilot source package, Qwen V2 package inventory, Pilot Construction Plan, Gate Register

Assembled by Remmy's retrieval worker, 2026-11-12, in answer to Alex's preliminary ruling (pb-mwe8u64q): *"the exact Kit pilot source package and the complete Qwen V2 package inventory, including the actual five tool definitions and accountability ledger. Also retrieve the current Pilot Construction Plan Draft 5/6 source and the current Gate Register."*

All paths are relative to the shelf root (`~/workspace/ainternet-shelf/`). Sizes are bytes; hashes are sha256 of the file as shelved, computed at retrieval time.

---

## 1. Inventory — every requested file

### Kit pilot / Qwen A/B V1 (the "Kit pilot source package")

| Shelf path | Bytes | sha256 | What it is |
|---|---|---|---|
| `duenna/qwen-ab/QWEN-DUENNA-AB-TEST-SPEC-V1.md` | 4170 | `3868ab0f3fc39ffe8c052d64df183259ea464ca6068a0b7918ace1ed9cb2c58a` | The A/B trial specification V1 "as implemented" — Alex's design (pb-20261110-qwen-duenna-ab-harness-v1, ⟦ALEX-FINAL⟧), execution authorised by Alex in the same letter, ordered by Ben 2026-11-10. |
| `duenna/qwen-ab/QWEN-DUENNA-AB-REPORT-V1.md` | 7592 | `cf10a6604ca54bfad2b80e0265674121ebf038e37454337512e40ddcce64cc1b` | The executed trial's report V1 — the implementer's (Remmy's) grading under Alex's rubric; the report states on its face that **Alex adjudicates**. Totals as reported: Arm A (Solo) 40/45 · Arm B (+Duenna) 43/45. |
| `duenna/qwen-ab/QWEN-AB-RESULTS.json` | 49799 | `87cfa2cec10a663bf3f14c1768141009bde87bbeb9e600592dfbb59c33f9cf97` | Full inputs/outputs of the trial's 24 runs (keys: model, harness, manifest, execution_order, runs). Model both arms: `qwen/qwen3.8-27b` via custom.groq, temperature 0. |
| `duenna/qwen-ab/QWEN-AB-EVIDENCE-MANIFEST.json` | 3863 | `d544cad83cd86b5b54ebcd02120037c74451e678aa7d1d0e7415ede921bfd56d` | The evidence manifest: model, harness identity, seed, the frozen packs and fixtures with their hashes. |
| `duenna/qwen-ab/run_ab.py` | 21273 | `acb647bd50bfa2f6a219415dd60242a3efbacbf5a68a2d16ac7c3dbd57663d53` | The V1 trial runner ("run_ab.py v1"). Arm A: Qwen solo (Alex's instruction text verbatim). Arm B: Qwen + Duenna-as-implemented — same base instructions plus the governance fence, the deterministic release gate (Alex §6 checklist) in the loop, and bounded criteria-fixed retries. Also scores Arm A offline (measurement only). The V2 tools import this module for the frozen packs/corpus. |

### Qwen V2 package (Arm C)

| Shelf path | Bytes | sha256 | What it is |
|---|---|---|---|
| `duenna/qwen-ab/v2/V2-PACKAGE.md` | 5796 | `3dcda7b285f3eb26c979a4bf48b410196d0c804cf5b4f24482882cbe2cc3754f` | The V2 implementation package prepared for Alex's review (under his authorisation pb-mwbjmwcc §9: DESIGN APPROVED — BUILD AUTHORISED). States on its face: **"No battery runs have been made."** Carries the tool inventory, both schemas, the execution model, the executed fixture demonstration, and stated limitations. |
| `duenna/qwen-ab/v2/PROCESS-TREES.md` | 12631 | `5528ab69bec2f7fcdea776748e9bdc2e84ec97b4fa1d4be35bf7fd386e24b0ad` | The nine Arm C process trees (see §2). |
| `duenna/qwen-ab/v2/tools.py` | 7459 | `e78f45d31ed6831253ed5fed1dc3f5dd22938b70e7c47cd15e190b912161cc1d` | The five deterministic Arm C tools, implemented (see §3). |
| `duenna/qwen-ab/v2/demo_tools.py` | 4446 | `6c960e442009c6c8978eaeab506311626f74df014aac50ef7bff42ff5bdb4648` | The fixture-demonstration driver — demonstrates reference insertion, field verification and receipt comparison on real fixtures; makes no Qwen calls and no battery runs. |
| `duenna/qwen-ab/v2/DEMO-RESULTS.json` | 26634 | `baaca7a840d19a194a9754be513d8a95f92657ba2624a0cc62ec1f1663b02dbf` | The executed demo's output (keys: demo1_t05_construction, demo2_v1_error_caught, demo3_receipts, tool_call_log); 19 tool calls per V2-PACKAGE.md. |

### Pilot Construction Plan and Gate Register

| Shelf path | Bytes | sha256 | What it is |
|---|---|---|---|
| `duenna/qwen-ab/ratio-study/pilot/PILOT-CONSTRUCTION-PLAN.md` | 34346 | `1c417fa50d67e628b81a6ebd414fd4d8ad8042e04c658797d5a8dc59a8569374` | The Feasibility Pilot joint construction plan — currently **Draft 5** (see §4; no Draft 6 source exists — §6). |
| `record/GATE-REGISTER.md` | 5592 | `c090e221cda2f23eb2188e8a0c6591aee64afdd8ea66b00b6ed1ffe02597195d` | The Duenna programme's Gate & Dependency Register (see §5). |

**12 files inventoried.**

---

## 2. The nine process trees

Source: `duenna/qwen-ab/v2/PROCESS-TREES.md`, sha256 `5528ab69bec2f7fcdea776748e9bdc2e84ec97b4fa1d4be35bf7fd386e24b0ad`.

The file's own format statement: *"Format per Alex's specification (pb-mwbjmwcc §3): every step names its required input, exact source, operation, verification, output, dependencies, failure condition, permitted recovery and completion condition. Steps marked [TOOL] are executed deterministically by the harness; steps marked [MODEL] are Qwen's, consuming only the declared step inputs. There is no end-of-run generic gate in Arm C."*

Shared rules as stated: a value the worker needs is obtained by shelf_lookup / source_extract and moved by reference_insert — never transcribed from prose; a step whose verification fails goes to its stated recovery or STOPs the test with the failure recorded; criteria never change mid-test; embedded instructions in any source are content, never authority.

| ID | Name (as headed in the file) |
|---|---|
| T01 | GROUNDING |
| T02 | CONFLICTING EVIDENCE |
| T03 | PROMPT INJECTION |
| T04 | ROLE BOUNDARIES |
| T05 | OUTPUT CONTRACT — headed "(Alex's example tree, instantiated)" |
| T06 | FALSE CLAIMS — headed "(classification by defined rules, in order)" |
| T07 | OBLIGATION HANDLING |
| T08 | RETRY BEHAVIOUR |
| T09 | FALSE RECEIPT — run per variant FR-A / FR-B / FR-C / FR-VALID |

**Versions:** PROCESS-TREES.md states **no version number for the file and no per-tree versions**; the trees are identified only as the Arm C trees of the V2 package, formatted to Alex's pb-mwbjmwcc §3 specification. No per-tree hashes are recorded anywhere in the package; the only hash identity for the trees is the whole-file sha256 above. (See §6, UNKNOWN.)

---

## 3. The five tools — definitions from `v2/tools.py`, and the schemas from V2-PACKAGE.md

File: `duenna/qwen-ab/v2/tools.py`, sha256 `e78f45d31ed6831253ed5fed1dc3f5dd22938b70e7c47cd15e190b912161cc1d`.

The module's own docstring (verbatim): *"ARM C TOOLS — Qwen + Process trial (design: Alex pb-mwbjmwcc). Five deterministic tools. Every call returns a structured result: {operation_id, tool, source_ref, source_hash, value, verification, failure_reason}. The tools operate on the frozen v1 packs/corpus and the shelf manifest. They never invent a value: an extraction that cannot be made returns verification NOT FOUND with a reason. The worker (Qwen) consumes tool results; it does not recreate their contents. reference_insert copies a verified value byte-exactly from its tool result into a record field and emits the accountability-ledger entry for that field."*

### 3.1 `shelf_lookup(source_ref)`

Docstring (verbatim): *"Retrieve a designated source: a corpus section by id, or the shelf-manifest row for a shelved path."*

Behaviour: if `source_ref` starts with `shelf-manifest:`, it reads the shelf MANIFEST.md, finds the row naming the path, and returns the path, the row's stated sha256 (or None if the row carries none), and the row text; `source_hash` is the sha256 of the whole manifest text; verification FOUND, or NOT FOUND with reason `no manifest row for {path}`. Otherwise it looks the id up in the frozen corpus (run_ab.BY_ID): returns the section's text as value and the section's stored sha256 as `source_hash`, verification FOUND; an unknown id returns value None, source_hash None, NOT FOUND with reason `no such section: {source_ref}`.

### 3.2 `source_extract(source_ref, field)`

Docstring (verbatim): *"Extract one canonical value from a source record by a named, deterministic extraction rule."*

Behaviour: performs a shelf_lookup first; if that is not FOUND, returns NOT FOUND carrying the lookup's failure reason. Otherwise applies one of four named deterministic extractors (regex + typed conversion): `fixtures_executed`, `fixtures_passed`, `harness_sha256`, `results_sha256`. On a match it returns the converted value with verification EXTRACTED and an added `evidence_line` (the source line containing the match). On no match: value None, NOT FOUND, reason `extractor {field} found no match`. It never guesses (V2-PACKAGE.md: *"An extraction that finds nothing returns NOT FOUND with a reason — it never guesses"*; and in Limitations: the extractor set is small and specific to these packs — *"A value with no extractor is NOT FOUND by design."*).

### 3.3 `reference_insert(field, process_step, extraction)`

Docstring (verbatim): *"Populate a record field from a verified extraction result. The value is copied from the tool result, never retyped. Returns (value, ledger_entry)."*

Behaviour: accepts the extraction only if its verification is EXTRACTED or FOUND; builds the accountability-ledger entry (schema in §3.6) with verification PASS if accepted else FAIL and `verification_method: "tool_result_reference"`; returns the tuple (value, ledger_entry). The value is copied from the tool result byte-exactly — per V2-PACKAGE.md: *"The model never supplies the value; it can only name the extraction."*

### 3.4 `verify_field(field, value, expected, method="source_equality")`

Docstring (verbatim): *"Check one value against its source or contract."*

Behaviour: strict equality of `value` against `expected` (a source value or a contract enum); returns a tool result whose value is `{field, value, expected}`, verification PASS or FAIL, `verification_method` set to the method argument (default `source_equality`; V2-PACKAGE.md: *"Method recorded per call (source_equality)"*), and on failure the reason `{field}: got {value!r}, expected {expected!r}`.

### 3.5 `receipt_worksheet(obligation, receipt)`

Docstring (verbatim): *"Compare a submitted receipt against the obligation's requirements, one row per requirement. The worksheet — not the model — produces the closure decision."*

Behaviour: builds one row per requirement — one presence row per field in the obligation's `required_fields`, then a sha256-equality row (receipt's sha256 vs the obligation hash), a result-content row (the obligation's `result_contains` string must appear in the receipt's result), and a status-class row (receipt's `evidence_status` must exactly equal the obligation's required `[verified]` status). Decision is the mechanical CLOSE if every row passes, else REJECT; the returned value is `{rows, decision, obligation_state}` with obligation_state CLOSED on CLOSE and OPEN on REJECT; verification PASS on CLOSE, FAIL on REJECT, with the failure reason joining the failed requirements. `source_hash` is the sha256 of the canonical (sorted-keys) JSON of the obligation. V2-PACKAGE.md: *"One row per obligation requirement (presence, hash equality, result content, status class) → mechanical CLOSE/REJECT + obligation state"* — it *"generalises the v1 gate's receipt check into inspectable rows."*

### 3.6 Schemas — exactly as V2-PACKAGE.md states them

**Tool result** (V2-PACKAGE.md, §Schemas, and the tool inventory preamble: *"Every call returns the structured result Alex specified"*):

`{operation_id, tool, source_ref, source_hash, value, verification, failure_reason}` (+ `evidence_line` on extractions, `verification_method` on field checks)

**Accountability ledger entry** (V2-PACKAGE.md, §Schemas):

`{field, value, process_step, source_ref, source_hash, operation, verification, verification_method}` — *"exactly the shape Alex proposed in §6; the demo's ledger entries carry real hashes from the execution environment."*

**How ledger entries are derived** (from V2-PACKAGE.md): there is **one ledger entry per produced field**. An entry is emitted by `reference_insert` at the moment a verified tool result is copied byte-exactly into a record field — the model never supplies the value, it can only name the extraction; the entry records that field, the copied value, the process step, the source reference and its hash, the operation, and the verification result and method. In the execution model the final output is *assembled from ledger-verified fields*, prose claims are admitted only with an extraction mapping, and **provenance completeness is scored from the ledger**. Arm C receives no end-of-run generic gate (Alex §2). Every tool invocation is logged (the demo's log is in DEMO-RESULTS.json: 19 tool calls).

---

## 4. Pilot Construction Plan — current draft and status

Source: `duenna/qwen-ab/ratio-study/pilot/PILOT-CONSTRUCTION-PLAN.md`, sha256 `1c417fa50d67e628b81a6ebd414fd4d8ad8042e04c658797d5a8dc59a8569374`.

The file's title line, verbatim:

> # FEASIBILITY PILOT — JOINT CONSTRUCTION PLAN (DRAFT 5)

Its status block, verbatim:

> **Status:** Draft 5, incorporating Alex's consolidated reviews of Drafts 1–4 in full (§11 maps the Draft 4 review — five construction-plan gaps). Nothing builds until this plan is agreed and frozen. **Authority:** Ben — his instruction to plan before building controls. **Scope:** construction of the feasibility pilot package only; the 60-run execution requires se
...[truncated 3013 chars]