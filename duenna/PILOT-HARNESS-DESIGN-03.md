# PILOT HARNESS DESIGN 03 — DRIVER, EXECUTION RECORD, AND MODEL-NEUTRAL TOOLS (REV 03)

**Pilot:** Nemotron governed-subject pilot (Plan 01, ADOPTED by Ben
2026-11-12; Alex adjudication pb-mwe90lo6)
**Stage:** 3 — Pilot Harness Design (Plan prerequisites #2 + #5, BLOCKING)
**Status:** DESIGN ONLY. No code is built, no model call is made or
authorised, no shelf file is modified, by this document. Stage 5
builds to this specification; Stage 6 execution is separately
authorised by Ben.
**Revision:** Rev 03, issued in response to Alex's verification
verdict on Rev 02 (Rev 02 shelved at commit
`499cad0922d039ca84d2a891bbe3178b705a214d`; verdict pb-mweajgej,
2026-11-12). His verdict: corrections B, C, and E accepted;
correction F accepted with hosted status still unverified;
corrections A and D each carried **one** remaining defect. This
revision folds in exactly those two defects and nothing else.
Rev 01 remains unmodified and remains the inspected document of
record (inspected at shelf commit
`96c74478c576aadc150361998114c3b58a463f41`); Rev 02 remains
unmodified as the verified revision; this revision supersedes
Rev 02 as the design going forward and is itself subject to
Alex's verification of the correction pass before Stage 5.
Stage 5 and Stage 6 gates are untouched by this revision.
**What changed in Rev 03** (mapped to the verdict; see
REVISION-03-NOTE.md for the full mapping):
- **§2.6 — a third commitment: CRASH** (correction A, the crash
  case). The supervisor now issues a distinct CRASH commitment
  over a crashed run's partial record, externally committing it
  exactly as observed; closed portions of a partial run are
  examinable only under it, and it never closes the run or
  makes it scoreable as complete. §2.6 also gains the
  supervisor's **issuance record**, and §4.5 gains **SE-7**,
  carrying Alex's four Stage 5 proof obligations for the
  anchor.
- **§3.2 / §3.4 — the four extraction outcomes, stated once
  and identically** (correction D, the contradiction). Rev 02's
  table folded "matches that all fail the type test" into NOT
  FOUND while its own following prose called that case an
  extraction failure. Rev 03 states four outcomes — NOT FOUND /
  TYPE FAILURE / EXTRACTED / AMBIGUOUS — identically in the
  table, the prose, and §3.4's tool restatement.
- Cross-references updated to the Rev 03 companion documents
  (NEMOTRON-ADAPTER-DESIGN-03; PILOT-ACCEPTANCE-CRITERIA-03);
  the capture schema `ADAPTER-CAPTURE-02` is unchanged.
**Inputs:** Plan 01 (Stage 3 + Stage 4 sections, retained core,
exclusions, and the 2026-11-12 amendment recording Ben's index
rule); NEMOTRON-ADAPTER-DESIGN-03 (the harness consumes its single
operation `complete(step_inputs) -> {capture_record_id, raw_output}`
and its `ADAPTER-CAPTURE-02` records); V2-QUALIFICATION-01 (esp.
§2 model coupling, §3 the executed `reference_insert` finding, §5
declare-only changes); PILOT-MANIFEST-01 (the Stage 0 freeze:
12 pins); Alex's inspection verdict (2026-11-12) and his Rev 02
verification verdict (pb-mweajgej, 2026-11-12); INTERPRETATION-
NOTE-01 (the pinned model-neutral reading of the trees, §1.1).

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
design does not create one on its behalf. The trust-anchor
receipts (§2.6) comply by construction: a receipt is a
system-written, per-run, immutable artefact — it enumerates
nothing, catalogues nothing, and is not an index. The
supervisor's issuance record (§2.6) is likewise written only
by the supervisor — the system side of the boundary — and by
nothing else.

---

## 1. DRIVER SEMANTICS

### 1.1 What a tree is, to the driver

The governing tree text is the pinned `PROCESS-TREES.md`
(sha256 `5528ab69…`, Manifest row 3), read with the declared,
versioned interpretation note **INTERPRETATION-NOTE-01** — now an
existing pinned artefact, not a Stage 5 promise (Rev 02): the
trees' [MODEL] steps are specified there as "Qwen's"; the note
restates them against the Stage 2 subject interface (declared
step inputs in, structured result out, raw request/response
captured by the adapter). That restatement is Qualification §5
item 5; it is a declared interpretation, never a silent edit of
the pinned text, and the pinned text prevails on any conflict.
The note is pinned by sha256 at the Stage 5 re-freeze (§4.4) and
cited in every run's `RUN_STARTED` block (§2.5).

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
mechanically derived ledger file (§2.3). Outside the run
directory, and outside the harness's write reach, the run's
trust-anchor receipts are preserved (§2.6).

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
| `event_sha256` | sha256 of this event's canonical serialisation with this field omitted. The chain makes insertion, deletion, or reordering of events **detectable relative to the chain's own links** — and, with the §2.6 commitments, detectable absolutely. What the chain alone proves, and what it does not, is stated in §2.6 and governs over any looser reading of this sentence (Rev 02 qualification, per Alex's correction A). |

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
chained record, itself anchored externally (§2.6); **complete** —
every insert emits exactly one, and inserts are the only way a
field comes to exist (Plan/trees: "an output field exists only
because a step produced and verified it"); **inspectable** — the
run's `ledger.json` is materialised from the record by a declared
mechanical extraction (all `LEDGER_ENTRY` payloads, in `seq`
order — the record is canonical, the file is a view);
**reproducible** — re-running that extraction over the preserved
record yields the identical ledger, which is itself a replay
check (§7).

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
commitments/
  <run_id>.start.json       # START commitment receipt (§2.6)
  <run_id>.terminal.json    # TERMINAL commitment receipt (§2.6)
  <run_id>.crash.json       # CRASH commitment receipt (§2.6; crashed runs only)
  issuance-record.jsonl     # the supervisor's issuance record (§2.6)
```

- **Discovery is the directory listing.** Runs are found by
  listing `runs/`; a run's contents by listing its directory.
  `run_id` embeds battery, date, and a per-day counter so a
  listing sorts into run order with no metadata file.
- **Linkage is by reference, never by index:** events cite
  captures by `{capture_id, record_sha256}`; captures cite
  nothing back (Adapter §3.3); artefacts are cited from their
  producing event by filename + sha256; the commitments cite the
  record by hash and count, and the record never cites them
  back — the anchor must not depend on the thing it anchors.
- **Nothing outside the run directory is written by the
  harness.** In particular the harness never writes to the
  bridge index, the shelf, or any manifest; its inputs arrive
  read-only (§3, §5). The `commitments/` receipts and the
  issuance record are written by the run supervisor (the system
  component that launches and closes runs), **not** by harness
  code — the harness has no write path to `commitments/` (§2.6).

### 2.5 The pinned-input block

`RUN_STARTED`'s payload embeds the run's complete pin set: every
artefact the run consumed — plan, trees + interpretation note,
tools revision, extractor-rules data, pilot data files, corpus
snapshot (§5) — each as `{path, sha256}`, verified by the
harness at pre-flight against PILOT-MANIFEST-01 and its Stage 5
amendment (§4.4). Any mismatch: the run does not start (§6.2).
The block is also the hash-chain genesis (§2.2): the record is
bound to its exact inputs from its first event. Its hash is the
content of the START commitment (§2.6).

### 2.6 The external trust anchor — START, TERMINAL, and CRASH commitments (Rev 02; CRASH added Rev 03)

**The defect this answers (Alex's correction A).** A hash chain
proves internal consistency: alter one event and the links after
it break. It does not prove the record is the record that was
written. Anyone with write access to the whole record file can
rewrite every event and recalculate every hash, producing a
chain that verifies perfectly against a history that never
happened. Rev 01's wording — the chain makes silent rewriting
"detectable" — claimed more than the mechanism holds, and is
qualified by this section: **the chain detects accidental
corruption and ordinary, partial edits; the anchor is what
defeats wholesale rewrite.** START and TERMINAL are both
required for a closed run: neither is optional, and a run
without both is not scoreable as complete (Criteria Rev 03
§1.1). Rev 03 adds the third receipt kind the crash case
requires — the CRASH commitment, below: a crashed run has no
TERMINAL commitment by definition, and Rev 02 left its partial
record committed by nothing outside itself (Alex's Rev 02
verification, the one remaining gap in correction A).

**Form.** A commitment is a small JSON **receipt** — a separate,
immutable artefact, written once and never edited. Receipts are
**not an index** (Ben's rule; Alex's verdict makes the same
distinction): a receipt names exactly one run, enumerates
nothing, catalogues nothing, and is written by the system side
of the boundary, never by the harness and never by any agent,
tool, or seat.

**Custody.** The receipts live in `commitments/` (§2.4), outside
the run directory and outside every path the harness can write.
They are written by the **run supervisor** — the system
component that starts the harness process, observes its exit,
and closes the run — which is outside the harness's code and
privilege boundary. The supervisor reads from the harness only
what the harness cannot later change without detection: the
genesis hash at start (below) and the finished file at close.
How the supervisor is implemented is a Stage 5 build question;
the design requirement is the custody split itself: **the
harness must not be able to silently rewrite the evidence and
its verification anchor together**, because it holds only one
of them.

**The issuance record (Rev 03).** Custody must be provable, not
merely plausible from a file's location (Alex's Rev 02
verification). The supervisor therefore keeps its own
**issuance record**: an append-only record, held in supervisor
custody alongside the receipts (§2.4), in which every issuance
is entered as it happens — `{run_id, kind, issued_at_utc,
receipt_sha256}` for each START, TERMINAL, and CRASH commitment
it writes. The receipts are the artefacts; the issuance record
is the supervisor's own account of having issued them. An
examiner verifies a presented receipt **against the issuance
record** (§7 step 0): a receipt with no corresponding entry, or
whose hash differs from its entry, is not evidence — it is a
custody finding. The issuance record is written only by the
supervisor; the harness has no write path to it, and nothing
in this design permits any agent, tool, or seat to write it.
The Stage 5 proof obligations this creates are stated as SE-7
(§4.5). Alex has confirmed the custody split itself suffices
at the architecture level; no operating-system-level
prescription is added here, and none is required before
Stage 5.

**START commitment** — written by the supervisor when
`RUN_STARTED` is flushed, before any step executes. Content:
`{run_id, kind: "START", issued_at_utc, genesis_sha256,
run_started_event_sha256, pinned_input_block_sha256}` — where
`genesis_sha256` is the §2.2 genesis preimage (the pinned-input
manifest block's hash) and `pinned_input_block_sha256` is the
hash of the `RUN_STARTED` payload's pin block as written. The
START commitment fixes, from outside the record, *what the run
claimed its inputs were at the moment it began*, so a later
rewrite cannot quietly re-pin the run to different inputs.

**TERMINAL commitment** — written by the supervisor when the
run's terminal event (`RUN_CLOSED` or `RUN_STOPPED`) is flushed
and the record file is closed. Content: `{run_id, kind:
"TERMINAL", issued_at_utc, terminal_event_type,
final_event_sha256, event_count, record_file_sha256}` — the
sha256 taken over the record file's exact bytes as closed. The
TERMINAL commitment fixes *where the record ends and what it
weighs*: any event appended, removed, or altered after closure
breaks it, and a rewritten record with a recalculated chain
still breaks it, because the anchor value lives outside the
rewriter's reach.

**CRASH commitment (Rev 03)** — written by the supervisor when
it observes the harness process terminate **without** a
terminal event having been flushed: no `RUN_CLOSED`, no
`RUN_STOPPED`, and therefore no TERMINAL commitment. Content:
`{run_id, kind: "CRASH", issued_at_utc, record_file_sha256,
event_count, final_event_sha256, termination_observed}` — the
sha256 taken over the partial record file's exact bytes as
they lie when the termination is observed; the count of
complete events in that file; the last complete event's
`event_sha256`; and the supervisor's own record of the
termination it observed (when, and on what basis — the
process's exit, witnessed by the component that launched it).
The CRASH commitment's sole function is to **externally commit
the partial record exactly as observed after the crash**, so
the closed portions of that record (§6.4) rest on an anchor
the harness cannot rewrite, instead of on the partial chain
alone. It is bound by three prohibitions: it is **not** a
TERMINAL commitment and must never be presented as one; it
does **not** close the run and does **not** make the run
scoreable as complete — a crashed run's outcome is governed
by Criteria Rev 03 §7.1's INCONCLUSIVE rules, never by its
closed trees' verdicts alone; and it is issued **only** where
no TERMINAL commitment exists for the run — TERMINAL and CRASH
never coexist for one run, and a run presented with both is a
custody finding, not a curiosity.

**Absence is a signal.** If the harness process dies without a
terminal event, there is no TERMINAL commitment, and none may
be manufactured after the fact: the record is partial (§6.4),
and what the supervisor issues instead is the CRASH commitment
above, over the partial file as it lies. The distinction
between a closed run and a crashed one therefore never rests
on anything the harness says: a closed run carries TERMINAL; a
crashed run carries CRASH; the two never coexist. A partial
record offered with **neither** — no TERMINAL (it never
closed) and no CRASH (the supervisor never observed the
termination, or never issued) — has no external commitment to
its tail at all and fails verification outright: its closed
portions are **not** examinable, because nothing outside the
record vouches for them. Likewise, a record offered **with** a
closure claim but **without** a matching TERMINAL commitment
fails verification outright (Criteria Rev 03 §8). A START
commitment with no run record at all is a pre-flight artefact
of a run that never opened — reported as such, never scored.

**Verification.** Replay (§7) begins at the anchor: recompute
the genesis and pin-block hashes against the START commitment;
recompute the file hash, event count, and final-event hash
against the TERMINAL commitment — or, for a crashed run,
against its CRASH commitment, in which case examination covers
the record's closed portions only and the run is examinable
solely as a partial record (§6.4). Every receipt relied on is
checked against the supervisor's issuance record (above): the
anchor is the supervisor's act of issuance, not the receipt
file's location. Only then walk the chain. A record that fails
its commitments is not examined further — its evidence is void
from the first divergent byte, and the finding is about
custody, not about the subject.

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
**`EXTRACTOR-RULES-02`** (pilot data, JSON; Rev 02 revision of the
rules schema, adding the match semantics below): an array of rule
objects —

```
{ field, rule_id, pattern, group, value_type, version }
```

- `field` — the extractable field name the trees use
  (e.g. `fixtures_executed`, `harness_sha256`).
- `pattern` / `group` — the deterministic match over a section's
  text, exactly as V2's four code regexes behaved, now declared.
- `value_type` — `integer` | `hex64` | `string`; a type failure
  is the TYPE FAILURE outcome (below), recorded, never a silent
  coercion.
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

**Match semantics — explicit (Rev 02, Alex's correction D; the
four outcomes stated once and identically, Rev 03).** Applying
a rule means: find every match of `pattern` in the section
text; for each match, take `group` and test it against
`value_type`. A match whose group fails the type test is not a
valid match. The outcome is then decided by **whether the
pattern matched at all** and by the count of **valid matches**
— and by nothing else. There are exactly four outcomes:

| Condition | Outcome |
|---|---|
| **No pattern matches** | **NOT FOUND**: the result records the absence and its reason (`verification: "NOT FOUND"`). The evidence is not there. |
| **Matches exist, but all fail type validation** | **TYPE FAILURE**: the extraction fails; the result records the matched text and the type expected, and produces **no value** (`verification: "TYPE FAILURE"`). The evidence is there; the rule cannot correctly interpret it — a different defect from absence, with a different remedy, and never recorded as NOT FOUND. |
| **Exactly one valid match** | **EXTRACTED**: that match's value and evidence line are the result (`verification: "EXTRACTED"`). |
| **More than one valid match** | **AMBIGUOUS**: extraction produces no value. The result records every candidate (value + evidence line) and `verification: "AMBIGUOUS"`. |

- **TYPE FAILURE is an outcome, never a filter.** If the
  pattern matches and every matching group fails the
  `value_type` test, the outcome is TYPE FAILURE (above): the
  pattern *did* find something; the something cannot be read
  under the rule's declared type. It is not NOT FOUND, it is
  never rescued by loosening the type, and it produces no
  value, so it is **not insertable** (§4.2's acceptance set
  admits EXTRACTED only) and satisfies no step's extraction
  requirement — a step that receives it follows its tree's
  failure path with the TYPE FAILURE result recorded, visibly
  distinct from NOT FOUND because the remedies differ (absent
  value vs a type expectation the document defeats — the
  remedy is a rules amendment, pinned and re-frozen, or a
  finding about the document). If some matches are type-valid
  and others are not, the type-failing matches are recorded in
  the result as rejected candidates and the count above runs
  over the valid ones — with the rejection visible, never
  silent.
- **No silent selection, ever.** There is no first-match,
  last-match, longest-match, or any other tie-break anywhere in
  the extractor, the tools, or the harness. Determinism that
  picks the wrong evidence deterministically is exactly the
  failure this rule exists to prevent (Alex's correction D): two
  valid matches mean the *rule* is under-specified for the
  document, and the remedy is a rules amendment (a sharper
  pattern, pinned and re-frozen) — never a selection policy.
- **AMBIGUOUS and TYPE FAILURE are first-class result
  states**, carried in the tool-result schema's `verification`
  field alongside EXTRACTED / FOUND / NOT FOUND. Neither is
  **insertable** (§4.2's acceptance set admits EXTRACTED only),
  neither satisfies a step's extraction requirement, and a step
  that receives either follows its tree's failure path with the
  result recorded — the same honesty treatment as NOT FOUND,
  and visibly distinct from it and from each other, because the
  three have different remedies (absent value vs
  under-specified rule vs a type expectation the document
  defeats).

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
verification, failure_reason}` for tool results — with the
`verification` value set extended by §3.2 (`AMBIGUOUS`;
`TYPE FAILURE` alongside it, Rev 03); the ledger entry schema
unchanged (§2.3). What changes is only what
the tools stand on:

| Tool | Restatement |
|---|---|
| `shelf_lookup(source_ref)` | Resolves via `CorpusSource` (§3.1): corpus section → result with `verification: "FOUND"` and the section's recorded hash; `pilot-manifest:` ref → manifest row likewise. No live shelf, no absolute paths. |
| `source_extract(source_ref, field)` | Fetches the section via `CorpusSource`, applies the field's rule from `EXTRACTOR-RULES-02` (§3.2) under its declared match semantics; exactly one valid match → `verification: "EXTRACTED"` with the value and evidence line; no pattern match at all → `NOT FOUND` with the reason; matches exist but all fail type validation → `verification: "TYPE FAILURE"` with the matched text and expected type recorded and **no value**; multiple valid matches → `verification: "AMBIGUOUS"` with all candidates recorded and **no value**. No rule for the field → `NOT FOUND` by declared design. |
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
   are likewise never insertable, and neither are AMBIGUOUS
   or TYPE FAILURE results (§3.2). (Any future tree that
   genuinely needs section
   text as a field value must declare the exception in a
   tools-revision amendment before Stage 5 — none of the nine
   trees does; §8 Q3.)
2. **Issuance in this run** — the result's `operation_id` is
   present in the harness's **issuance registry** (below),
   unconsumed, and issued to the same tree/step context that now
   presents it.
3. **Recomputation at insert time** — all three checks pass
   (§4.2, recomputation).

**Issuance registry — semantics (Rev 02, Alex's correction B).**
The registry's properties are stated exactly, because one of
Rev 01's words overstated them: Rev 01 called the sequential
operation ids "unguessable." **They are not, and unpredictability
is not a security property of this design** — an `op-<seq>` id
can be guessed by anyone who can count, and the design must not
lean on its secrecy. The registry's actual properties are:

1. **The registry is private to the harness.** It is harness
   state, created and held by harness code, exposed to no caller
   and no subject. Nothing outside the harness can read it, and
   the only writes to it are the harness's own (§4.5 SE-3).
2. **An identifier alone cannot manufacture an entry.** An
   `operation_id` is a *reference*, not a capability: entries
   come into existence only when the harness itself executes a
   tool and registers its result (at the `TOOL_RETURNED` event
   for `source_extract`). Presenting a guessed, copied, or
   invented id that has no entry is a refusal (§4.3) — the id's
   guessability is irrelevant because guessing buys nothing.
3. **Every entry is bound to its context.** The registry records
   `{operation_id, tool, source_ref, source_hash, value,
   evidence_line, rule_id, issued_at_seq, tree_id, step_id}` —
   the result is bound to its run (the registry exists only
   within a run), its tree, its step, and the tool invocation
   that produced it. An entry presented from a different
   tree/step context than it was issued to is a refusal.
4. **Consumption is exactly-once.** An issued result may be
   inserted once (§4.2, consumption); the registry marks the
   entry consumed, and the mark is part of the entry.
5. **Registry state is independently reconstructable.** The
   registry is a *cache of the record*, not a second source of
   truth: every issuance is a `TOOL_RETURNED` event in the run
   record, every consumption a `LEDGER_ENTRY`, every refused
   presentation a `GOVERNANCE_EVENT`. An examiner rebuilds the
   registry from the event sequence alone (§7 step 4) and checks
   the live registry's decisions against the reconstruction —
   a registry that issued, consumed, or refused anything the
   record cannot reproduce is a finding against the build.

Operation ids are harness-issued and sequential within the run
(`op-<seq>`). An opaque or random id form is **permitted but
never load-bearing**: if Stage 5 prefers one for readability of
the record, it changes nothing above, and no inspection may
credit it as a security measure. **The dict never crosses the
boundary:** `reference_insert` accepts an `operation_id` (§3.4)
and looks the result up in the registry — a caller-built dict is
not a representable input to the pilot tool at all. This closes
probe case (c) structurally, not by validation: there is no
argument through which a fabricated value or hash can be
presented.

**Recomputation at insert time.** Before inserting, the harness
independently re-derives the result from the pinned sources:

1. Re-fetch the section via `CorpusSource`; recompute its
   sha256 and require equality with (a) the result's
   `source_hash` **and** (b) the section hash recorded in the
   pinned corpus snapshot. A moved or edited corpus fails here —
   the Stage 0 tripwire, enforced at the point of use.
2. Re-apply the field's extractor rule (from the pinned
   `EXTRACTOR-RULES-02`, same `rule_id`) to the re-fetched text
   under §3.2's match semantics; require exactly one valid match,
   the produced value to equal the result's `value` byte-for-byte,
   and the result's `evidence_line` to occur verbatim in the
   section text. (A rule that has drifted into ambiguity since
   issuance fails here as a refusal, not as a re-selection.)
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
against). At Stage 5 the revision, the extractor-rules data
(EXTRACTOR-RULES-02), the pilot data files, the corpus snapshot
(§5), INTERPRETATION-NOTE-01, and this design revision's
specification are pinned by sha256 in a **dated amendment to
PILOT-MANIFEST-01** — the Stage 0 freeze is amended, not
rewritten, and the run's `RUN_STARTED` block (§2.5) cites the
amendment. Alex's Stage 5 inspection examines the revision
against this section as its specification — including the
structural properties of §4.5.

### 4.5 Structural-enforcement requirements (Rev 02)

Alex's verdict (§3): the sabotage battery's four tests are
necessary, but build inspection must also establish that the
refusal mechanism is *structurally* enforced, not merely that
four examples fail. The properties inspection must establish
are therefore stated here as design requirements. Each is a
property of the built package's structure — of what code paths
exist and what they can reach — not of its behaviour on
selected inputs:

- **SE-1 — Sole issuer.** The harness is the only issuer of
  extraction results. A result exists, for insertion purposes,
  only as a registry entry created by the harness's own
  execution of `source_extract` (§4.2). No other component —
  adapter, subject, operator tooling, test scaffolding inside
  the run path — can create, mint, or import a result.
- **SE-2 — No caller-supplied provenance.** The insert
  operation's interface accepts no provenance from its caller:
  its only handle on a result is the `operation_id` (§3.4).
  Value, source, hash, evidence line, and verification state are
  all read from the registry and recomputed (§4.2); there is no
  parameter, field, or side channel through which a caller can
  supply or override any of them.
- **SE-3 — Registry beyond the subject's reach.** The registry
  cannot be modified by the subject. Structurally: the subject
  has no tool access, no corpus access, no filesystem or process
  access to harness state (§1.3); its outputs enter the harness
  only as preserved artefacts consumed by [CHECK] phases and
  tree-declared steps. There is no step type, input format, or
  adapter behaviour by which subject output can write a registry
  entry, alter one, or mark one consumed or unconsumed.
- **SE-4 — Recomputation against the pinned corpus, at insert
  and at examination.** Value and source are recomputed against
  the pinned corpus snapshot at insert time (§4.2) and again,
  independently, at replay (§7 step 4). The insert decision
  trusts nothing the original extraction merely recorded: not
  the value, not the hash, not the evidence line.
- **SE-5 — Single use.** A consumed operation cannot be used
  again (§4.2 consumption; §4.2 property 4). The consumption
  state is registry state reconstructable from the record
  (§4.2 property 5), so a replay that finds a second insertion
  of one `operation_id` has found a build defect, not a
  scoring question.
- **SE-6 — Refusal is sterile.** A refusal produces **no**
  ledger entry and **no usable value** (§4.3): the calling step
  receives the refusal object and nothing else; no field comes
  into existence; no artefact downstream of the step can cite
  the refused result as its source. Inspection confirms there
  is no fallback path — no default value, no cached result, no
  "insert anyway with a warning" branch — anywhere in the
  insert call graph.
- **SE-7 — Anchor custody is demonstrable (Rev 03).** The
  §2.6 trust anchor holds structurally, and Stage 5 must
  demonstrate it, not assert it (Alex's Rev 02 verification,
  carried verbatim in substance): **(i)** the harness cannot
  write, replace, or delete commitment receipts — no code path
  in the built harness reaches `commitments/` for writing, and
  adversarial tests that attempt receipt forgery, replacement,
  and deletion from inside the harness's privilege boundary
  fail; **(ii)** the supervisor independently records the
  START, TERMINAL, and CRASH commitments — issuance is the
  supervisor's own act, performed outside the harness's code
  and privilege boundary, never delegated to harness code and
  never performed over values the supervisor has not itself
  recomputed or observed; **(iii)** Stage 5 demonstrates the
  separation through inspection **and** adversarial tests —
  including the crash case: a harness killed mid-run receives
  a CRASH commitment over the partial file as it lies, and no
  TERMINAL commitment; **(iv)** the examiner verifies the
  supervisor's **issuance record** (§2.6), not merely a receipt
  sitting in a separate directory: every receipt presented at
  examination has a corresponding issuance entry, and every
  entry's hash matches its receipt. Alex has confirmed the
  custody split suffices at the architecture level; SE-7 is
  what Stage 5 must *prove* about the build, and no
  operating-system-level prescription is imposed here.

Stage 5 inspection tests SE-1…SE-7 against the built code, and
the Stage 4 criteria's sabotage battery (Criteria Rev 03 §4)
exercises them behaviourally. A build in which any SE property
holds only because no caller has tried to violate it has not
met this section.

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
further** — after which the supervisor issues the TERMINAL
commitment over the record as closed (§2.6), so a stopped run
is anchored exactly like a completed one.

**Partial records.** A stopped run's record is complete as a
record *of what happened*: every flushed event stands, the
hash chain verifies up to the terminal event, closed trees are
fully re-derivable (§7), and the open tree is re-derivable up
to its last completed step. What a partial record never does is
imply outcomes for steps that did not run: absence of an event
is the evidence. Stage 4's criteria (not this design) decide
what a partial run counts as — the harness's obligation is only
that the partiality is exact and visible. Where the harness
process dies *without* writing a terminal event, there is no
TERMINAL commitment and none is back-filled (§2.6); the
supervisor instead issues the CRASH commitment over the
partial file exactly as it lies, and the partial record is
examinable **only under that commitment** — closed trees
fully, the open tree to its last completed step — and never
as a complete run. A partial record carrying no CRASH
commitment has no external anchor and is not examinable
evidence at all (§2.6).

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
Stage 5 — never as a harness option at run time. (Stage 4
answered: the criteria were stated without one — Criteria §6 —
and the exclusion stands confirmed.)

---

## 7. REPLAY PROCEDURE — INDEPENDENT RE-DERIVATION

An examiner with the run directory, the run's commitment
receipts (§2.6), the pinned input set (PILOT-MANIFEST-01 +
Stage 5 amendment), and this design re-derives the run's
outcome without trusting the harness:

0. **Anchor verification (Rev 02; CRASH and the issuance
   record, Rev 03).** Before the record is trusted for
   anything: recompute the genesis hash and the `RUN_STARTED`
   pin-block hash against the START commitment; recompute the
   record file's sha256 over its exact bytes, the event count,
   and the final event's `event_sha256` against the TERMINAL
   commitment — or, for a crashed run (no terminal event),
   against the CRASH commitment, in which case examination is
   limited to the record's closed portions and the run is
   examinable only as a partial record (§2.6, §6.4). Every
   receipt relied on is verified against the supervisor's
   issuance record (§2.6, §4.5 SE-7): a receipt the issuance
   record does not show, or whose hash differs from its entry,
   is not evidence. Any mismatch — a claimed closure with no
   TERMINAL commitment, or a partial record with no CRASH
   commitment — ends the examination here: the record's
   evidence is void and the finding is a custody failure
   (§2.6), not a verdict about the run's contents. Only a
   record that passes its anchor is walked further.
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
   checked against re-execution. (Re-execution of
   `source_extract` runs under §3.2's match semantics — any
   extraction-outcome mismatch is a divergence like any other:
   an AMBIGUOUS or TYPE FAILURE recomputation where the record
   claims EXTRACTED, a TYPE FAILURE recomputation where the
   record claims NOT FOUND, or vice versa in any pairing.)
4. **Insert audit, with registry reconstruction (Rev 02).**
   Rebuild the issuance registry from the event sequence alone
   (§4.2 property 5): issuances from `source_extract`
   `TOOL_RETURNED` events, consumptions from `LEDGER_ENTRY`
   events, refusals from `INSERT_REFUSED` governance events.
   For every `LEDGER_ENTRY`: confirm its `operation_id` was
   issued to the same tree/step context before the insert,
   confirm the §4.2 recomputation from the pinned snapshot
   yields the inserted value and hash, and confirm single
   consumption against the reconstruction — not against the
   build's own registry state. For every `INSERT_REFUSED`
   governance event, confirm the refusal was warranted by the
   same recomputation. Any issuance, consumption, or refusal
   the record cannot reproduce is a build finding (§4.5).
5. **Subject artefacts, treated as artefacts.** For every
   [MODEL] step: follow `MODEL_CALL_LINKED` to the capture
   file; verify the capture's hashes, including every attempt's
   preserved body hash (Adapter §6.1, Rev 02); take
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

**Exactness statement.** Governance re-derivation (steps 0–4,
6) is **exact**: every input is pinned, every operation
deterministic, every subject contribution enters only as a
preserved byte string, and the record itself is anchored
outside its own custody (step 0). The one non-re-derivable
element in any run is *why the hosted model produced its
output* — which no design at this boundary can supply, and
which the pilot's question does not ask.

---

## 8. OPEN QUESTIONS — WITH RECOMMENDED DEFAULTS

1. **Corpus snapshot (§5).** Position taken: snapshot copied
   into the pilot set at Stage 5; read-in-place rejected.
   **Default:** confirm the snapshot. *For Alex to inspect;
   Ben's index rule is the constraint it answers.*
2. **Solo arm (§6.6).** Position taken: excluded; Stage 4
   confirmed the criteria need no effect measure.
   **Default:** exclude. *Closed unless reopened by amendment.*
3. **FOUND inserts (§4.2).** Rule as designed: EXTRACTED-only,
   no exceptions for the nine trees.
   **Default:** stand. Any tree needing section-text-as-value
   must declare it by amendment before Stage 5. *For Alex.*
4. **Adapter-failure handling (§6.3).** Tree invalidated, run
   continues; three invalidations stop the run.
   **Default:** stand. *For Alex.*
5. **Record format and anchor (§2.1, §2.6).** Append-only JSONL
   events with a per-event hash chain, the ledger materialised
   as a derived view, and — Rev 02, completed Rev 03 —
   START/TERMINAL commitment receipts in supervisor custody,
   plus the CRASH commitment anchoring a crashed run's partial
   record. Alex's correction A asked for the anchor, not a
   format change; the JSONL distinction of Rev 01 (the record
   enumerates nothing outside its own run, so it is not an
   index) stands, and the receipts are likewise per-run
   artefacts, not an index. His Rev 02 verdict (pb-mweajgej)
   accepted the custody split at architecture level and set
   its Stage 5 proof obligations, now stated in §2.6.
   **Default:** stand. *Proof obligations are §2.6's; for
   Alex's next review pass on the corrected sections.*
6. **Time budgets (§6.1).** 60 s tool step / 300 s model step /
   60 min tree / 4 h run.
   **Default:** stand. *For Alex; the run cap is Ben's if he
   wants a shorter leash on a scheduled battery.*
7. **Operation-id consumption (§4.2).** Single-use per field;
   reuse only by tree declaration (none currently).
   **Default:** stand. *For Alex.*
8. **Interpretation note for the trees (§1.1).** **Closed in
   Rev 02:** INTERPRETATION-NOTE-01 exists as a pinned artefact
   and is the note this design cites. *For Alex to verify the
   note's readings against the pinned trees — the verification
   his verdict offered to share.*
9. **Orphan captures (§6.2).** A capture written after its step
   timed out is cited by governance event, never retro-fitted.
   **Default:** stand. *For Alex.*
10. **Supervisor implementation (§2.6).** The custody split is
    specified and **accepted by Alex at architecture level**
    (pb-mweajgej — no OS-level prescription is owed before
    Stage 5); the supervisor's concrete form (launcher script,
    service, manual operator step with declared tooling) is a
    Stage 5 build decision, where §2.6's three proof
    obligations — the harness cannot write, replace, or delete
    receipts; the supervisor independently records START,
    TERMINAL, and CRASH; the examiner verifies the supervisor's
    issuance record — are discharged by inspection and
    adversarial tests. **Default:** the lightest form that
    keeps the write path outside the harness's privilege
    boundary, inspected like any other part of the package.
    *For Alex/Ben at Stage 5.*

---

## Scope notes

- This is a specification, not an implementation. Every
  mechanism named here — driver, registry, record writer,
  snapshot, supervisor receipts — is a Stage 5 build obligation,
  and Stage 5's independent inspection (Alex, per the plan)
  tests the built package against this document before any live
  execution.
- Design positions that go beyond the sources are marked as
  positions (§5, §6.6) and carried as open questions (§8);
  nothing in this document silently settles them.
- The exclusions of Plan 01 hold throughout: this harness is a
  bounded V2 process-harness experiment. It implements no
  general D3 obligation lifecycle, claims no v0.10 conformance,
  makes no role-enforcement claim from T04's behavioural
  refusal, and touches neither the ratio study nor live Shelf
  integration.
