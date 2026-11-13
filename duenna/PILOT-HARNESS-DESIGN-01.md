# PILOT HARNESS DESIGN 01 — DRIVER, EXECUTION RECORD, AND MODEL-NEUTRAL TOOLS

**Pilot:** Nemotron governed-subject pilot (Plan 01, ADOPTED by Ben
2026-11-12; Alex adjudication pb-mwe90lo6)
**Stage:** 3 — Pilot Harness Design (Plan prerequisites #2 + #5, BLOCKING)
**Status:** DESIGN ONLY. No code is built, no model call is made or
authorised, no shelf file is modified, by this document. Stage 5
builds to this specification; Stage 6 execution is separately
authorised by Ben.
**Inputs:** Plan 01 (Stage 3 + Stage 4 sections, retained core,
exclusions, and the 2026-11-12 amendment recording Ben's index
rule); NEMOTRON-ADAPTER-DESIGN-01 (the harness consumes its single
operation `complete(step_inputs) -> {capture_record_id, raw_output}`
and its `ADAPTER-CAPTURE-01` records); V2-QUALIFICATION-01 (esp.
§2 model coupling, §3 the executed `reference_insert` finding, §5
declare-only changes); PILOT-MANIFEST-01 (the Stage 0 freeze:
12 pins).

**What the harness is.** The driver the V2 package never had
(Qualification §1: no driver exists; the trees are prose). It
executes the nine pinned process trees against the Nemotron
subject through the Stage 2 adapter, runs the five deterministic
tools in their model-neutral form (§3), enforces the
`reference_insert` provenance rule (§4), and writes the canonical
execution record (§2) from which an independent examiner
re-derives every outcome (§7). Scoring itself is Stage 4's: the
harness produces evidence, not verdicts.

**Standing constraint — Ben's index rule (Plan amendment,
2026-11-12 16:45 MST).** Index artefacts are system-written only.
No agent, tool, seat, or harness may edit an index — read access
only. This design complies in three places: the corpus question is
read-in-place vs pinned copy, never edit (§5); the harness
maintains **no index of its own** and writes to no index (§2.4);
the adapter likewise keeps no index (Adapter §3.3), and this
design does not create one on its behalf.

---

## 1. DRIVER SEMANTICS

### 1.1 What a tree is, to the driver

The governing tree text is the pinned `PROCESS-TREES.md`
(sha256 `5528ab69…`, Manifest row 3), read with one declared,
versioned interpretation note (Stage 5 artefact, re-frozen — see
§3.5): the trees' [MODEL] steps are specified there as "Qwen's";
the note restates them against the Stage 2 subject interface
(declared step inputs in, structured result out, raw
request/response captured by the adapter). That restatement is
Qualification §5 item 5; it is a declared interpretation, never a
silent edit of the pinned text, and the pinned text prevails on
any conflict.

Each tree is a sequence of steps with declared dependencies
("Depends:"). In all nine trees the dependency edges are a chain
(step *n* depends on step *n−1*, with T05-STEP-06 / T08-STEP-04
conditional on validation failure); the driver executes in
declared order and never reorders, parallelises, or skips a step
whose dependencies are satisfied. A step whose dependency failed
does not execute; the tree follows its failure path (§1.4).

### 1.2 Step types

| Type | Executor | Semantics |
|---|---|---|
| **[TOOL]** | The harness, deterministically | The step's named operation is one (or a declared sequence) of the five tools (§3.4), executed by harness code against the pinned inputs. Same inputs → same outputs, byte-for-byte. |
| **[MODEL]** | The subject, via the adapter only | The harness constructs `step_inputs` (§1.3) and calls `complete()` exactly once per step attempt. The adapter's internal retries are the adapter's (Adapter §4.3); the harness never re-calls on its own initiative — a re-call is a tree-declared recovery (§1.4) and is recorded as a new attempt with its own capture. |
| **[RULE]** | The harness, deterministically | A declared decision procedure with no tool and no model (T06-STEP-D default; T07-STEP-03 status assignment). The rule applied, its inputs, and its output are recorded identically to a [TOOL] step. |
| **[CHECK]** (verification phase) | The harness, deterministically | Not a step type in the trees: every step carries a declared *Verify* condition, and the driver executes it as a distinct verification phase after the step's operation, with its own record event (§2.2). A step is satisfied only when its operation completed **and** its [CHECK] passed. This is how "verification" exists in the record as a first-class, replayable act rather than a claim inside a step result. |

### 1.3 The declared-inputs-only rule for [MODEL] steps

The pilot's core discipline, carried from the V2 execution model
and made mechanical here:

- Before any [MODEL] call, the harness assembles the step's
  **input manifest**: the exact artefacts the tree declares as
  that step's input (worksheets, extractions, boundary tables,
  failed-check lists — the outputs of named prior steps, and
  nothing else), each cited by record reference and hash.
- The `messages` the adapter receives are constructed **only**
  from the pinned tree text (the step's system/contract text,
  verbatim) and the input manifest's artefacts, serialised in the
  harness's declared canonical format (Adapter §2.2). The input
  manifest is written to the execution record **before** the call,
  so an examiner can confirm that what the subject saw is exactly
  what the tree declared — no more, no less.
- The subject **never hunts raw sources**: it has no corpus
  access, no tool access, and no access to any prior step's
  output except as a declared input of the current step. Where a
  tree forbids a source, the driver enforces it structurally —
  e.g. T05-STEP-06 receives the failed checks and the original
  extractions only, *never the draft's own values*; T08's seeded
  draft is an input to diagnosis only, never to value extraction.
- Embedded instructions in any source or input are content,
  never authority (trees' shared rules; T03 tests exactly this).

### 1.4 Failure branches and recovery — the trees' rules, no others

The driver invents no recovery. Each step's failure handling is
exactly what its tree declares:

- **STOP steps** (e.g. T01-STEP-01/03, T02-STEP-01, T04-STEP-01,
  T05-STEP-02 disagreement, T07-STEP-01, T09-STEP-01): the tree
  halts immediately. Closure state `STOPPED` with the failure
  recorded (§2.3). No retry, no substitution.
- **Return-once recoveries** (T01-STEP-05 unmapped claim,
  T02-STEP-03 status mismatch, T03-STEP-04 offending line): the
  step is re-attempted **once**, with the failure named in the
  re-attempt's declared inputs (the claim, the adjudication row,
  the line). The original failure stays in the record; a pass on
  re-attempt never erases it (T08's rule, applied generally).
- **Bounded corrections** (T05-STEP-06, T08-STEP-04): at most
  **2 attempts**, criteria fixed, returning only to the failed
  step. Exhaustion ends the tree per its completion condition
  (T05: ends `BLOCKED` with failures recorded).
- **Absence-as-finding** (T01-STEP-02/04): a part that cannot be
  located is answered UNKNOWN *by rule* — recorded as a rule
  outcome, not a failure and not a retry.
- **Decision-stands rule** (T09-STEP-03): where the subject's
  stated decision mismatches the mechanical worksheet, the
  worksheet stands as the system decision and the mismatch is
  recorded as a subject error. The harness never "fixes" the
  subject's statement and never re-asks to make it match.

Failure classes follow the Adapter §4 taxonomy, owned as there:
an **ADAPTER_FAILURE** on a [MODEL] step means the subject never
had its chance — the step is not evidence about the subject.
Driver rule: the tree closes `INVALIDATED-INFRASTRUCTURE` for
that tree (§6.3) unless the tree declares a recovery that covers
it — none currently does. A **SUBJECT_FAILURE** follows the
tree's own failure branch above. A **GOVERNANCE_FAILURE** (a
[CHECK] FAIL, a worksheet REJECT, an insert refusal under §4) is
the machinery working: it is recorded, follows the tree's stated
path for failed verification, and is **never retried away and
never reclassified**.

### 1.5 What executing a tree produces

For each tree instance: a complete step-by-step section of the
run record — every step's trigger, inputs, operation, [CHECK]
result, recovery (if any), satisfaction or failure, and closure —
plus the tree's produced artefacts (answers, records, worksheets,
decisions) and, for every produced field, its ledger entry (§2.3).
The harness emits **no score and no pass/fail verdict for a
tree**: it emits the per-field and per-check outcomes from which
Stage 4's criteria derive a verdict.

---

## 2. CANONICAL EXECUTION RECORD — SCHEMA `PILOT-RUN-RECORD-01`

### 2.1 Form

One run = one record. The record is an **append-only sequence of
events** in a single JSON Lines file, `run-record.jsonl`: one
JSON object per line, written and flushed at the moment the event
occurs, never edited afterwards. A crash or stop therefore leaves
a record that is complete *up to the last flushed event* — the
partial-record semantics of §6.4 rest on this. Alongside it, the
run directory holds the adapter's capture files (§2.4) and a
mechanically derived ledger file (§2.3).

### 2.2 Event schema

Every event carries:

| Field | Content |
|---|---|
| `seq` | Integer, strictly increasing from 1 within the run; gaps are impossible by construction (single writer, append-only) and their presence voids the record. |
| `event_id` | `"<run_id>:<seq>"` — identity is positional and self-contained; no external registry is consulted or needed. |
| `run_id` | Harness-issued at run start: `<battery-id>-<UTC date>-<counter>` (e.g. `NP01-20261120-001`). |
| `recorded_at_utc` | ISO-8601 UTC timestamp of the event. |
| `event_type` | From the closed list in §2.3. |
| `tree_id` / `step_id` | The tree/step the event belongs to; `null` at run level. For T09, `tree_id` carries the variant (`T09/FR-A`). |
| `payload` | The event-type-specific content (§2.3) — always the **full** content, never a summary or a pointer to harness memory. |
| `prev_event_sha256` | sha256 of the previous event's canonical serialisation (genesis event: sha256 of the run's pinned-input manifest block, §2.5). |
| `event_sha256` | sha256 of this event's canonical serialisation with this field omitted. The chain makes silent insertion, deletion, or reordering of events detectable by any examiner (§7). |

### 2.3 Event types — the lifecycle vocabulary

The plan requires trigger / progress / satisfaction / failure /
closure semantics; they are event types, identically at step and
tree level:

**Run level**
- `RUN_STARTED` — payload: the full pinned-input block (§2.5) and
  the harness + tools + adapter configuration hashes.
- `RUN_STOPPED` — payload: stop reason (§6), the tree/step
  position, and which stop rule fired.
- `RUN_CLOSED` — payload: per-tree closure states, event count,
  record sha256 of the final event. Emitted on normal completion
  only; a stopped run has `RUN_STOPPED` as its terminal event
  instead. Exactly one terminal event exists in any record.

**Tree level**
- `TREE_TRIGGERED` — the tree instance begins; payload: tree id,
  variant if any, the tree text hash from the pinned set.
- `TREE_CLOSED` — payload: closure state — `COMPLETED` (all steps
  satisfied or rule-resolved), `BLOCKED` (tree's own failure
  ending, e.g. T05), `STOPPED` (a STOP step fired),
  `INVALIDATED-INFRASTRUCTURE` (adapter failure, §1.4),
  `INCOMPLETE` (the run stopped while this tree was open, §6.4).

**Step level**
- `STEP_TRIGGERED` — payload: step id, type ([TOOL]/[MODEL]/
  [RULE]), declared inputs (record references + hashes), and for
  [MODEL] steps the §1.3 input manifest.
- `STEP_PROGRESS` — payload: intermediate deterministic state an
  examiner needs but which is not an outcome: per-item progress
  in multi-item steps (T01's per-question-part location, T06's
  per-statement sub-steps A–D, T07's per-element matches, T09's
  per-requirement worksheet rows). One event per item; the
  worksheet rows *are* these events' payloads, in full.
- `TOOL_INVOKED` / `TOOL_RETURNED` — a pair per tool call.
  `TOOL_INVOKED` payload: `operation_id` (harness-issued, §4.2),
  tool name, arguments in full. `TOOL_RETURNED` payload: the
  tool's **complete returned payload, verbatim** — the full
  result object of §3.4's schema, including whole-section values
  where a tool returns them. Nothing is truncated in the record;
  bulk is accepted as the price of re-derivation (§7).
- `MODEL_CALL_LINKED` — payload: `{capture_id, record_sha256,
  request_sha256, response_sha256}` from the adapter capture
  (Adapter §3.3), plus the `raw_output` returned across the
  boundary, verbatim. The capture file itself lives in the run
  directory (§2.4); this event is the link, and the hashes make
  the link checkable.
- `CHECK_RESULT` — the [CHECK] phase outcome: the declared verify
  condition (quoted from the tree), what was compared, and
  `PASS` / `FAIL` with the deciding values. A FAIL here is a
  governance event in the §1.4 sense and is never overwritten by
  a later recovery's PASS — both stand.
- `RECOVERY_TAKEN` — payload: the tree rule invoked, the failed
  attempt's event reference, the attempt number, and the
  recovery's declared inputs.
- `STEP_SATISFIED` / `STEP_FAILED` — terminal step outcomes.
  `STEP_FAILED` payload: failure class (Adapter §4 taxonomy),
  the failing condition, and the tree branch taken next.
- `LEDGER_ENTRY` — §2.3's ledger, below.
- `GOVERNANCE_EVENT` — machinery-level findings that are not a
  single step's failure: an insert refusal (§4.3), a pin or hash
  mismatch detected mid-run (§6.2), a decision-stands ruling
  (T09). Payload: kind, full detail (claimed vs recomputed
  values where applicable), and the consequence taken.

**The ledger as process output.** Each successful
`reference_insert` emits one `LEDGER_ENTRY` event whose payload
is the ledger entry in the established schema — `{field, value,
process_step, source_ref, source_hash, operation, verification,
verification_method}` — **unchanged** from V2, plus the pilot's
provenance additions of §4.2 (`operation_id` of the inserted
result, and the recomputation evidence). This is the arrangement
Alex accepted: no standalone ledger artefact is required *if*
entries are preserved, complete, independently inspectable, and
reproducible. The design meets the four conditions thus:
**preserved** — entries are events in an append-only, hash-
chained record; **complete** — every insert emits exactly one,
and inserts are the only way a field comes to exist (Plan/
trees: "an output field exists only because a step produced and
verified it"); **inspectable** — the run's `ledger.json` is
materialised from the record by a declared mechanical extraction
(all `LEDGER_ENTRY` payloads, in `seq` order — the record is
canonical, the file is a view); **reproducible** — re-running
that extraction over the preserved record yields the identical
ledger, which is itself a replay check (§7).

### 2.4 Organisation without an index

Per Ben's rule, the harness maintains **no index**: no registry
file, no catalogue of runs, no database, nothing that enumerates
records and could be edited. Organisation is by filesystem
convention alone:

```
runs/
  <run_id>/
    run-record.jsonl        # the canonical record (§2.1)
    ledger.json             # derived view (§2.3)
    captures/
      <capture_id>.json     # adapter-written, one per call (Adapter §3.3)
    artefacts/
      <tree>--<step>--<name>  # produced artefacts too large or
                              # binary-adjacent for inline payloads,
                              # each cited from its event by name + sha256
```

- **Discovery is the directory listing.** Runs are found by
  listing `runs/`; a run's contents by listing its directory.
  `run_id` embeds battery, date, and a per-day counter so a
  listing sorts into run order with no metadata file.
- **Linkage is by reference, never by index:** events cite
  captures by `{capture_id, record_sha256}`; captures cite
  nothing back (Adapter §3.3); artefacts are cited from their
  producing event by filename + sha256.
- **Nothing outside the run directory is written by the
  harness.** In particular the harness never writes to the
  bridge index, the shelf, or any manifest; its inputs arrive
  read-only (§3, §5).

### 2.5 The pinned-input block

`RUN_STARTED`'s payload embeds the run's complete pin set: every
artefact the run consumed — plan, trees + interpretation note,
tools revision, extractor-rules data, pilot data files, corpus
snapshot (§5) — each as `{path, sha256}`, verified by the
harness at pre-flight against PILOT-MANIFEST-01 and its Stage 5
amendment (§4.4). Any mismatch: the run does not start (§6.2).
The block is also the hash-chain genesis (§2.2): the record is
bound to its exact inputs from its first event.

---

## 3. MODEL-NEUTRAL TOOLS — THE §5 DECLARATIONS, DESIGNED

Qualification §5 declared seven changes; this section designs
items 1–5 and 7 (item 6 is §4). All are **new, versioned pilot
artefacts** — the pinned V2 package is never edited into
neutrality in place (§4.4 covers re-freeze).

### 3.1 Corpus interface (retires `import run_ab` / `BY_ID`)

A single interface between the tools and any source universe:

```
CorpusSource.get_section(source_ref) -> { section_id, doc,
    heading_path, sha256, text } | NOT FOUND
CorpusSource.get_manifest_row(source_ref) -> { row fields } | NOT FOUND
```

- The interface is satisfied by exactly one implementation in
  this pilot: a reader over the pinned pilot corpus snapshot
  (§5) plus the pinned pilot manifest data (§3.3). Section
  records keep the corpus's own shape (each already carries its
  `section_id` and recorded `sha256` — Manifest §2).
- The tools import this interface and nothing else: no trial
  runner, no module-level corpus load from a home-tree path, no
  subject code. Importing the pilot tools executes no data load
  beyond reading the pinned snapshot the harness hands them.
- `source_ref` namespaces are declared: a bare section id
  resolves against the corpus; a `pilot-manifest:` prefix
  resolves against the pilot manifest data (replacing V2's live
  `shelf-manifest:` read of the shelf's MANIFEST.md by absolute
  path — Qualification §2, tools.py:22).

### 3.2 Extractor rules as versioned data (retires `_EXTRACTORS` in code)

`source_extract`'s rules leave the code entirely.
**`EXTRACTOR-RULES-01`** (pilot data, JSON): an array of rule
objects —

```
{ field, rule_id, pattern, group, value_type, version }
```

- `field` — the extractable field name the trees use
  (e.g. `fixtures_executed`, `harness_sha256`).
- `pattern` / `group` — the deterministic match over a section's
  text, exactly as V2's four code regexes behaved, now declared.
- `value_type` — `integer` | `hex64` | `string`; type failure is
  a failed extraction, recorded, not a silent coercion.
- The rule set is **versioned as data and pinned by hash**; the
  pilot's initial set covers the pilot's actual documents (the
  four V2 fields, plus each further field the trees name, each
  rule added by declaration — Qualification §5 item 3). A field
  with no rule is **NOT FOUND by declared design**, exactly as in
  V2, but now the absence is visible in data an examiner can
  read, not buried in code.
- Every extraction records the `rule_id` + rules-file hash in
  its result's provenance (§4.2), so an examiner re-runs the
  *same rule* at replay (§7).

### 3.3 Fixtures and ground truth as pinned pilot data (retires `run_ab` constants)

Everything V2 kept as module constants in the trial runner moves
into declared pilot data files, hashed and frozen at Stage 5:

| Pilot data file | Contents (from `run_ab.py`) |
|---|---|
| `PILOT-DATA-PACKS-01` | The tree input packs `P_T01…P_T09` — as data: per tree, the list of corpus section ids (and pilot-manifest refs) constituting its pack. Identical for every subject; this is what "same pinned task inputs reach the subject" means concretely (Plan Stage 4). |
| `PILOT-DATA-EXPECTED-01` | Ground truth: `EXPECTED_RECORD` (T05/T08) and every per-tree expected value a [CHECK] or `verify_field` compares against. |
| `PILOT-DATA-T09-01` | `OBLIGATION_T09` (the obligation spec) and `RECEIPTS` (FR-A / FR-B / FR-C / FR-VALID, verbatim). |
| `PILOT-DATA-FIXTURES-01` | The remaining declared fixtures: T08's seeded invalid draft; T04's arm instruction set / boundary-table source; T07's register fixture; T01's pack manifest reference (`QWEN-AB-EVIDENCE-MANIFEST`, Manifest row 12, cited by the trees). |

Data files carry their own version labels; the Stage 5 re-
freeze pins each by sha256 as an amendment to PILOT-MANIFEST-01
(§4.4). The trees' *text* does not change: where PROCESS-TREES
names a source ("register fixture", "pack fixture"), the data
file is that source, declared.

### 3.4 The five tools, restated against the interfaces

Result schema **unchanged** from V2-PACKAGE:
`{operation_id, tool, source_ref, source_hash, value,
verification, failure_reason}` for tool results; the ledger
entry schema unchanged (§2.3). What changes is only what the
tools stand on:

| Tool | Restatement |
|---|---|
| `shelf_lookup(source_ref)` | Resolves via `CorpusSource` (§3.1): corpus section → result with `verification: "FOUND"` and the section's recorded hash; `pilot-manifest:` ref → manifest row likewise. No live shelf, no absolute paths. |
| `source_extract(source_ref, field)` | Fetches the section via `CorpusSource`, applies the field's rule from `EXTRACTOR-RULES-01` (§3.2); success → `verification: "EXTRACTED"` with the evidence line; no rule or no match → `NOT FOUND` with the reason. |
| `reference_insert(field, process_step, operation_id)` | **Signature changed** — it takes the harness-issued `operation_id` of an extraction result, not a caller-supplied dict. Full rule: §4. |
| `verify_field(field, value, expected, method="source_equality")` | Unchanged semantics; `expected` now comes from `PILOT-DATA-EXPECTED-01` or a prior verified extraction, cited in the record — never from a runner constant. |
| `receipt_worksheet(obligation, receipt)` | Unchanged semantics; obligation and receipts are the `PILOT-DATA-T09-01` artefacts, cited by hash. |

### 3.5 Logging contract (Qualification §5 item 7)

The canonical record owns the log — closing V2's gap (its log
existed only because demo code kept one, and `reference_insert`,
the ledger-emitting operation, was not in it). Contract: **every**
tool invocation, including `reference_insert` and including
refused inserts, produces its `TOOL_INVOKED`/`TOOL_RETURNED`
pair (§2.3); every insert additionally produces its
`LEDGER_ENTRY` or `GOVERNANCE_EVENT` (§4.3). There is no tool
call in a pilot run that is not in the record.

---

## 4. THE `reference_insert` PROVENANCE RULE — PILOT TOOLS REVISION

### 4.1 The defect being fixed (executed, Qualification §3)

V2's `reference_insert` accepts any caller-supplied dict whose
`verification` field claims `"EXTRACTED"` or `"FOUND"`
(tools.py:95) and emits a ledger entry stamped `PASS`. The
Stage 1 probe executed the consequences: a raw FOUND lookup
inserted as verified evidence; a hand-fabricated dict —
invented value 12345, invented hash `ffff…` — inserted with the
fabricated hash recorded as provenance. The function never
refuses; the only guard is a label downstream code must check
itself. The package's own demo relied on the hole (4 of its 8
ledger fields were hand-built dicts).

### 4.2 The rule

**Acceptance set.** `reference_insert` may insert **only** a
result that satisfies all of:

1. `verification == "EXTRACTED"` — issued by `source_extract`.
   **FOUND results may never be inserted as a field value.** A
   lookup establishes that a source exists; it extracts nothing,
   and V2's whole-section-text-as-value insertion (probe case
   (b)) is precisely the failure being closed. NOT FOUND results
   are likewise never insertable. (Any future tree that
   genuinely needs section text as a field value must declare
   the exception in a tools-revision amendment before Stage 5 —
   none of the nine trees does; §8 Q3.)
2. **Issuance in this run** — the result's `operation_id` is
   present in the harness's **issuance registry** (below),
   unexpired, and issued to the same tree/step context that now
   presents it.
3. **Recomputation at insert time** — all three checks pass
   (§4.2, recomputation).

**Issuance registry.** The harness — never the subject, never
caller code — registers every tool result it obtains: when a
`TOOL_RETURNED` event is written for `source_extract`, the
registry records `{operation_id, tool, source_ref, source_hash,
value, evidence_line, rule_id, issued_at_seq, tree_id,
step_id}`. Operation ids are harness-issued, sequential within
the run (`op-<seq>`), and unguessable by construction of the
flow: the only way an id enters the registry is the harness's
own tool execution. **The dict never crosses the boundary:**
`reference_insert` accepts an `operation_id` (§3.4) and looks
the result up in the registry — a caller-built dict is not a
representable input to the pilot tool at all. This closes probe
case (c) structurally, not by validation: there is no argument
through which a fabricated value or hash can be presented.

**Recomputation at insert time.** Before inserting, the harness
independently re-derives the result from the pinned sources:

1. Re-fetch the section via `CorpusSource`; recompute its
   sha256 and require equality with (a) the result's
   `source_hash` **and** (b) the section hash recorded in the
   pinned corpus snapshot. A moved or edited corpus fails here —
   the Stage 0 tripwire, enforced at the point of use.
2. Re-apply the field's extractor rule (from the pinned
   `EXTRACTOR-RULES-01`, same `rule_id`) to the re-fetched text;
   require the produced value to equal the result's `value`
   byte-for-byte, and the result's `evidence_line` to occur
   verbatim in the section text.
3. Require the registry entry's recorded value/hash to equal
   the presented ones (no mutation between issuance and
   insertion — the registry holds the harness's own copy, so
   this compares the presentation against the harness's record,
   not against itself).

**Consumption.** An issued result may be inserted **once**, for
one field. The registry marks the `operation_id` consumed; a
second presentation is a refusal (§4.3) unless the tree declares
the reuse (none currently does; §8 Q7). Legitimate multi-field
use of one source is served by *separate extractions* — cheap,
deterministic, and each independently recomputed.

### 4.3 Failure behaviour — refusal is a governance event

- On any failed condition, `reference_insert` **refuses**: it
  returns a refusal object (`{refused: true, reason, claimed,
  recomputed}`), emits **no** ledger entry, and returns **no**
  value to the calling step. There is no PASS/FAIL *label* for
  downstream code to forget to check — the V2 mechanism that
  made the defect silent is removed; refusal is the absence of
  the artefact the step needs.
- The harness records a `GOVERNANCE_EVENT` (kind
  `INSERT_REFUSED`) with the full claimed-vs-recomputed detail —
  a refusal is a finding about the machinery or its caller,
  preserved with the same permanence as a success.
- The calling step then follows its tree's failure branch
  (§1.4): typically STOP or BLOCKED with the failure recorded.
  Recovery, where the tree allows any, is only via a **fresh
  `source_extract`** in the same run producing a newly issued
  result. A refused insert is never retried with a repaired,
  edited, or re-labelled presentation — the harness holds no
  code path that constructs a substitute result.

### 4.4 Versioning and re-freeze

This rule, the §3 interfaces, and the §3.4 signature change
constitute a declared **tools revision** — working label
**PILOT-TOOLS-01** — built at Stage 5 as a *new* artefact, never
an edit of the pinned `tools.py` (sha256 `e78f45d3…`, which
remains the qualified V2 baseline this design is measured
against). At Stage 5 the revision, the extractor-rules data,
the pilot data files, the corpus snapshot (§5), and the §1.1
interpretation note are pinned by sha256 in a **dated amendment
to PILOT-MANIFEST-01** — the Stage 0 freeze is amended, not
rewritten, and the run's `RUN_STARTED` block (§2.5) cites the
amendment. Alex's Stage 5 inspection (§8 of the plan's staging)
examines the revision against this section as its specification.

---

## 5. CORPUS ACCESS DECISION — PINNED SNAPSHOT, NOT READ-IN-PLACE

**Position: the pilot runs against a pinned snapshot of the
corpus, copied into the pilot set at Stage 5 build time. Read-
in-place is rejected as the pilot's evidence base.** This is a
design decision presented for Alex's inspection, as tasked.

**What the choice is.** The corpus is two files under
`~/workspace/pulse-bridge/index/` — `sections.jsonl`
(3,709,804 bytes; 1,156 sections) and `manifest.json`
(50,881 bytes) — plus the shelf `MANIFEST.md` rows the tools
read (Manifest rows 9–11). Ben's rule settles what is *not* in
question: no stage edits any of these; the Stage 0 pins are the
tripwire either way. The question is only where the harness
reads from.

**Reasoning for the snapshot:**

1. **The evidence base must not be able to move mid-programme.**
   The index folder is live infrastructure of another system
   (the bridge). The plan's own amendment states the tripwire
   consequence: *any* system-side index change — legitimate,
   unrelated to the pilot, made for bridge reasons — surfaces
   as a pin mismatch and forces a re-freeze. Read-in-place
   makes the pilot's foundation hostage to another programme's
   housekeeping for the whole pilot lifetime; a mismatch
   discovered mid-battery would void runs through no fault of
   the pilot. A snapshot converts an uncontrolled dependency
   into a pinned input like every other.
2. **The copy is permitted, and is not an index edit.** Copying
   is a **read** of the index (allowed: read access only) plus
   the creation of a **new pilot file** (an ordinary pilot
   artefact, frozen and hashed like the data files of §3.3).
   Nothing is written to the index; the rule's letter and its
   purpose — the index changes only by the system's own hand —
   are both honoured. The snapshot is not an index and the
   harness maintains no index over it (§2.4): it is a data file,
   read through `CorpusSource`.
3. **Self-containment is what Alex's standard requires.** The
   Stage 0 finding was that the corpus "is not on the Shelf at
   all" — the pilot's inputs reaching outside its own pinned
   set, to absolute home-tree paths (Qualification §2: the
   package is executable *here*, portability NOT ESTABLISHED).
   A pilot whose examiner must re-derive outcomes (§7) from
   preserved inputs cannot have its largest input living at an
   absolute path in another programme's directory. The snapshot
   (working label `PILOT-CORPUS-SNAPSHOT-01`: the two index
   files' bytes, plus the pilot-manifest rows replacing the
   live MANIFEST.md read) makes the pinned set closed.
4. **Duplication cost is trivial and bounded.** ~3.76 MB, frozen
   once. The corpus is a *frozen* programme record (Manifest
   §2) — it is not expected to change, and if the system does
   change it, that change is a fact about the programme record,
   handleable by a declared re-snapshot + re-freeze amendment,
   never by silent drift under a running pilot.

**What read-in-place would have had for it:** no duplication,
and reads always see the system's current record. Weighed and
found insufficient: "current" is precisely what a frozen-input
pilot must not chase (Plan: "inputs are frozen and pinned
instead" of live integration), and the §4.2 recomputation check
would turn every legitimate index update into an insert refusal
mid-run.

**Snapshot discipline:** at Stage 5, the snapshot is taken by
read-only copy, its sha256 computed and checked **equal in
content-addressed terms** — i.e. each section's recorded hash
and the files' Stage 0 pins (`b107e892…`, `c93eaa19…`) are
verified against the source at copy time; equality of the
copies to the Stage 0 pins is recorded in the re-freeze
amendment (§4.4). Thereafter the source files are out of the
pilot's runtime path entirely; §4.2's recomputation runs
against the snapshot.

---

## 6. STOP CONDITIONS AND RUN SHAPE

### 6.1 Time budgets (informed by the adapter's worst case)

One `complete()` call's worst case is ≈ **245 s** (Adapter §7
Q6: 2 attempts × 120 s helper timeout + 5 s fixed retry delay).
The harness adds no timeout of its own *inside* a call — the
adapter's policy bounds it — but budgets around it:

| Level | Budget | Basis |
|---|---|---|
| [TOOL] / [RULE] step | 60 s | Deterministic, in-memory over a ~3.7 MB snapshot; two orders of magnitude of headroom. Exceeding it means the machinery, not the data, is broken. |
| [MODEL] step | 300 s | Adapter worst case 245 s + harness serialisation/record margin. |
| Corpus load + pre-flight pin verification | 120 s | Hashing ~3.76 MB plus the §2.5 pin set. |
| Tree | 3,600 s (60 min) | The most [MODEL]-heavy trees (T05 with 2-attempt correction, T08 likewise) bound at ≈ 3 calls ≈ 13 min of pure adapter worst case; 60 min absorbs [TOOL] work and record writing with wide margin. |
| Run | 4 h wall clock | 13 tree instances (§6.5); worst-case adapter time if every [MODEL] step ran to its cap ≈ 90 min; the cap exists to bound a pathological run, not to pressure a normal one. |

Budgets are harness configuration, pinned in `RUN_STARTED`
(§2.5) — changing them is an amendment, not a run-time knob.

### 6.2 Per-step stops

- A [TOOL]/[RULE] step exceeding its budget, erroring, or
  producing a result its [CHECK] cannot evaluate: step fails
  (class: governance/infrastructure as applicable), tree takes
  its failure branch.
- A [MODEL] step: adapter failure → §1.4 (tree
  `INVALIDATED-INFRASTRUCTURE`). Subject failure → the tree's
  branch. A call still outstanding at the step budget: the
  harness records `STEP_FAILED` (adapter timeout class) and
  does not wait further; the late capture, if the adapter
  eventually writes one, is an orphan — cited by a
  `GOVERNANCE_EVENT` if observed, never retro-fitted into the
  step's outcome.
- An insert refusal (§4.3): governance event; the step fails
  for want of its artefact; tree branch applies.

### 6.3 Per-tree stops

- The tree's own STOP steps and exhausted recoveries (§1.4) —
  closure `STOPPED` / `BLOCKED`.
- Tree budget exceeded → closure `STOPPED`, reason
  `TREE_TIMEOUT`, current step position recorded.
- Adapter-failure invalidation (§1.4) → closure
  `INVALIDATED-INFRASTRUCTURE`. **The run continues** to the
  next tree: trees are independent tests over independent
  packs, and one tree's dead lane is not another tree's
  evidence. Exception: **three** invalidated trees in one run
  is a lane-level fact, not three accidents — the run stops
  (§6.4) with reason `LANE_FAILURE`.
- Corpus/pin integrity: the harness re-verifies the corpus
  snapshot's hash at every `TREE_TRIGGERED` (cheap: one file).
  A mismatch is not a per-tree event — it is a run stop (§6.4),
  because every subsequent tree's evidence base is void.

### 6.4 Per-run stops and partial records

Run-stopping conditions: (a) pre-flight — any pin in §2.5
mismatches, or the pinned model id is absent from the Stage 6
pre-flight catalogue (Adapter §1.4): **the run does not start**
and no record is opened; the failure is reported, not recorded
as a run. (b) Mid-run — corpus snapshot hash mismatch at a tree
boundary; `LANE_FAILURE` (three invalidations); run budget
exceeded; harness-internal error that makes further events
untrustworthy. On any mid-run stop: the harness writes
`RUN_STOPPED` (reason + position), closes the currently open
tree as `INCOMPLETE` if it has no closure, and **writes nothing
further**. 

**Partial records.** A stopped run's record is complete as a
record *of what happened*: every flushed event stands, the
hash chain verifies up to the terminal event, closed trees are
fully re-derivable (§7), and the open tree is re-derivable up
to its last completed step. What a partial record never does is
imply outcomes for steps that did not run: absence of an event
is the evidence. Stage 4's criteria (not this design) decide
what a partial run counts as — the harness's obligation is only
that the partiality is exact and visible.

### 6.5 Battery shape

- **One run = one full pass** over the battery, trees in id
  order: T01, T02, T03, T04, T05, T06, T07, T08, then T09 as
  **four tree instances** (FR-A, FR-B, FR-C, FR-VALID) — 13
  tree instances total. Tree instances are independent: §6.3's
  continue rule applies across all of them.
- Repetitions, run count, and cross-run aggregation are Stage 6
  authorisation matters (Plan Stage 6), not design choices
  here; the design assumes nothing beyond the single pass.

### 6.6 Solo (ungoverned) arm — EXCLUDED

**Position: the pilot battery is the governed arm only. No solo
arm is designed, and none runs under this plan unless Stage 4
reopens the question.** Reasoning:

1. **The pilot's research question does not require it.** The
   question (Plan §1) is whether a different model can *operate
   through* the governance machinery without being trusted to
   report its own compliance — a question about the machinery's
   hold on a new subject, answered from the governed record:
   did the pinned inputs reach the subject, did verification
   bind, did failures stay failures. Alex's condition for
   retaining a solo arm is *where the research question
   requires measuring governance's effect* (Plan Stage 3); an
   effect-size comparison (governed vs ungoverned score delta)
   is the **ratio study's** question — which stays paused and
   untouched (Plan exclusions), and importing its arm structure
   here would blur exactly the boundary Alex drew.
2. **A solo arm is not even well-defined for most of this
   battery.** The trees' outputs *are* harness artefacts —
   ledgers, verified records, worksheets (§1.5). Ungoverned,
   T05's "record" is whatever the model types; there is no
   identical-inputs comparison to make, because the governed
   output's identity is its evidence trail. Kit's V1 A/B already
   established the solo-vs-governed contrast for the predecessor
   subject at the level where it is meaningful.
3. **Cost and confound.** A solo arm doubles adapter calls on a
   ~40-requests/minute free-tier lane and doubles the surface
   Stage 4 must keep unconfused — spend the pilot's bound on
   depth of governance evidence instead.

**Declared trigger for revisiting:** if Stage 4's acceptance
criteria cannot be stated without a governance-effect measure,
the arm question returns to Alex/Ben as an amendment *before*
Stage 5 — never as a harness option at run time.

---

## 7. REPLAY PROCEDURE — INDEPENDENT RE-DERIVATION

An examiner with the run directory, the pinned input set
(PILOT-MANIFEST-01 + Stage 5 amendment), and this design
re-derives the run's outcome without trusting the harness:

1. **Record integrity.** Walk `run-record.jsonl`: verify `seq`
   continuity from 1, recompute each `event_sha256`, and verify
   the `prev_event_sha256` chain back to the genesis block.
   Any break voids the affected tail as evidence.
2. **Input identity.** Recompute the sha256 of every artefact
   in the `RUN_STARTED` pin block (§2.5) against the pinned set.
   Confirm the catalogue evidence and model pin (Adapter §6.1)
   for every linked capture.
3. **Deterministic re-execution.** Re-run every [TOOL] and
   [RULE] step and every [CHECK] phase from the recorded inputs
   (the pinned snapshot, rules data, and pilot data make this
   possible offline): each recomputed tool result must equal
   its `TOOL_RETURNED` payload byte-for-byte; each recomputed
   check outcome must equal its `CHECK_RESULT`. Deterministic
   machinery leaves no room for "trust the log" — the log is
   checked against re-execution.
4. **Insert audit.** For every `LEDGER_ENTRY`: confirm its
   `operation_id` was issued (a matching `source_extract`
   `TOOL_RETURNED` precedes it in the record), confirm the §4.2
   recomputation from the pinned snapshot yields the inserted
   value and hash, and confirm single consumption. For every
   `INSERT_REFUSED` governance event, confirm the refusal was
   warranted by the same recomputation.
5. **Subject artefacts, treated as artefacts.** For every
   [MODEL] step: follow `MODEL_CALL_LINKED` to the capture
   file; verify the capture's hashes (Adapter §6.1.1–3); take
   `response_raw` as the subject's preserved output — a fixed
   artefact — and re-derive every downstream verdict (checks,
   worksheet decisions, status assignments, ledger fields) from
   it by the deterministic machinery. **The subject is never
   re-sampled at replay.** Re-issuing a request would produce a
   new sample, not evidence about this run (Adapter §6.2), and
   this procedure neither needs nor permits it.
6. **Outcome reconstruction.** Recompute each tree's closure
   from its step outcomes under §1.4's rules, and the run's
   terminal state from the tree closures. The reconstruction
   matches the record, or the discrepancy — localised by the
   chain to the first divergent event — is the finding.

**Exactness statement.** Governance re-derivation (steps 1–4,
6) is **exact**: every input is pinned, every operation
deterministic, every subject contribution enters only as a
preserved byte string. The one non-re-derivable element in any
run is *why the hosted model produced its output* — which no
design at this boundary can supply, and which the pilot's
question does not ask.

---

## 8. OPEN QUESTIONS — WITH RECOMMENDED DEFAULTS

1. **Corpus snapshot (§5).** Position taken: snapshot copied
   into the pilot set at Stage 5; read-in-place rejected.
   **Default:** confirm the snapshot. *For Alex to inspect;
   Ben's index rule is the constraint it answers.*
2. **Solo arm (§6.6).** Position taken: excluded.
   **Default:** exclude; revisit only if Stage 4 cannot state
   its criteria without an effect measure. *For Alex/Ben.*
3. **FOUND inserts (§4.2).** Rule as designed: EXTRACTED-only,
   no exceptions for the nine trees.
   **Default:** stand. Any tree needing section-text-as-value
   must declare it by amendment before Stage 5. *For Alex.*
4. **Adapter-failure handling (§6.3).** Tree invalidated, run
   continues; three invalidations stop the run.
   **Default:** stand. *For Alex.*
5. **Record format (§2.1).** Append-only JSONL events with a
   per-event hash chain; ledger materialised as a derived view.
   **Default:** stand (JSONL rejected for *captures* by the
   Adapter design for index-adjacency reasons; for the run
   record the chain + single-writer append is the integrity
   mechanism itself, and the record is a run artefact, not an
   index — it enumerates nothing outside its own run).
   *For Alex to confirm the distinction holds.*
6. **Time budgets (§6.1).** 60 s tool step / 300 s model step /
   60 min tree / 4 h run.
   **Default:** stand. *For Alex; the run cap is Ben's if he
   wants a shorter leash on a scheduled battery.*
7. **Operation-id consumption (§4.2).** Single-use per field;
   reuse only by tree declaration (none currently).
   **Default:** stand. *For Alex.*
8. **Interpretation note for the trees (§1.1).** The [MODEL]
   steps' restatement against the adapter interface as a
   separate versioned note, pinned text prevailing.
   **Default:** note, not a trees revision — the trees are the
   pilot's starting test specification and stay byte-pinned.
   *For Alex (it is Qualification §5 item 5, his declaration).*
9. **Orphan captures (§6.2).** A capture written after its step
   timed out is cited by governance event, never retro-fitted.
   **Default:** stand. *For Alex.*

---

## Scope notes

- This is a specification, not an implementation. Every
  mechanism named here — driver, registry, record writer,
  snapshot — is a Stage 5 build obligation, and Stage 5's
  independent inspection (Alex, per the plan) tests the built
  package against this document before any live execution.
- Design positions that go beyond the sources are marked as
  positions (§5, §6.6) and carried as open questions (§8);
  nothing in this document silently settles them.
- The exclusions of Plan 01 hold throughout: this harness is a
  bounded V2 process-harness experiment. It implements no
  general D3 obligation lifecycle, claims no v0.10 conformance,
  makes no role-enforcement claim from T04's behavioural
  refusal, and touches neither the ratio study nor live Shelf
  integration.
