# BATCH 3 CHUNK SHEET — Record and driver

**Ben's method, adopted 2026-11-13:** Duenna breaks the spec
into workable chunks before the build, so no obligation lives
only as a clause inside a paragraph. Every chunk below is one
named obligation from STAGE5-BUILD-SPEC-22 (shelf pin
afae29fb, file sha256 0459f615…), with its locus, the artefact
that discharges it, and the check that proves it. The Batch 3
checkpoint report discharges this sheet line by line; a chunk
without its check passing is not done.

Batch 3 scope (§4): the record writer (PILOT-RUN-RECORD-01,
§3.4), the hash chain, `ledger.json` materialisation, and the
driver (§3.1) with budgets and stops. Checkpoint (§4): a
scratch run against the stub subject (§3.7) executes a
declared subset of trees end-to-end and produces a complete
record; the chain verifies; the materialised ledger
reproduces identically on re-extraction; stop finality and
the budget stops are demonstrated in scratch contexts (a run
stopped mid-tree leaves the Harness §6 partial-record shape).

## A. The record (§3.4)

- **C3-A1 — One run, one append-only JSONL file.**
  `run-record.jsonl`; one JSON object per line; written and
  flushed at the moment the event occurs; never edited
  afterwards. (§3.4 Form; lines 3631–3636.) *Artefact:*
  record writer. *Check:* scratch record read back; append
  behaviour shown by event order + flush points.
- **C3-A2 — Event schema PILOT-RUN-RECORD-01.** Every event
  carries `seq` (strictly increasing from 1; a gap voids the
  record), `event_id` `"<run_id>:<seq>"`, `run_id`
  (`<battery-id>-<UTC date>-<counter>`, A-1 grammar),
  `recorded_at_utc`, `event_type` (the closed Harness §2.3
  list, transcribed from the snapshot — no invented types),
  `tree_id`/`step_id`, `payload` (full content, never a
  summary or a pointer), `prev_event_sha256`,
  `event_sha256`. (§3.4; lines 3636–3643.) *Check:* schema
  assertion over every event of the scratch record.
- **C3-A3 — The chain's claim, stated qualified.** No
  artefact, comment, or report claims the chain defeats
  wholesale rewrite; that is the commitments' job (Batch 4).
  (§3.4; lines 3644–3651.) *Check:* wording audit of the
  batch's own artefacts and report.
- **C3-A4 — Event vocabulary with complete payloads.**
  `TOOL_INVOKED`/`TOOL_RETURNED` verbatim (nothing
  truncated); `MODEL_CALL_LINKED` carrying `{capture_id,
  record_sha256, request_sha256, response_sha256}` plus the
  verbatim `raw_output`; `CHECK_RESULT` with the declared
  verify condition quoted; `LEDGER_ENTRY` in the established
  schema plus the §3.3 provenance additions (`operation_id`,
  recomputation evidence). (§3.4; lines 3652–3661.) *Check:*
  payload-shape assertions per type present in the scratch
  run.
- **C3-A5 — `ledger.json` is a view, never a source.** It is
  materialised from the record by the declared mechanical
  extraction (all `LEDGER_ENTRY` payloads in `seq` order);
  re-running the extraction yields the identical file.
  (§3.4; lines 3658–3661; §4 checkpoint.) *Check:*
  extract twice, byte-compare; extract from a re-read
  record, byte-compare again.
- **C3-A6 — Organisation without an index.** `runs/<run_id>/`
  layout; discovery is the directory listing; linkage by
  reference and hash, never by index. The harness writes
  nothing outside the run directory and has no write path to
  `commitments/`. (§3.4; lines 3662–3668.) *Check:* the
  scratch run's writes confined to its run directory
  (before/after listing of the parent tree).
- **C3-A7 — Pinned-input block.** `RUN_STARTED` embeds the
  run's complete pin set — every artefact consumed, each as
  `{path, sha256}`, verified at pre-flight against
  PILOT-MANIFEST-01 + the re-freeze amendment; any mismatch
  and the run does not start. (§3.4; lines 3669–3674.)
  *Check:* a scratch pre-flight with one deliberately wrong
  pin refuses to start (no RUN_STARTED written).
- **C3-A8 — Canonical serialisation is RFC 8785, via the
  Batch 0 implementation pin.** JCS for every structured
  artefact the harness serialises and hashes (event
  preimages, ledger entries, the pinned-input block,
  registry-relevant records); the implementation is the one
  frozen at Batch 0 (name/version/hash in the re-freeze
  evidence) — no second JCS. Rejection rules: NaN/±Infinity,
  duplicate keys at parse, lone surrogates, and anything
  that cannot re-serialise to identical canonical bytes are
  rejected, never coerced. Raw bytes are never
  canonicalised: sha256 over bytes exactly as they lie.
  (§3.4; lines 3675–3726.) *Check:* the record's chain
  recomputes under the pinned implementation; a NaN-bearing
  payload is refused in a unit check.

## B. The driver (§3.1)

- **C3-B1 — Declared order, no improvisation.** Steps
  execute in the trees' declared order; the driver never
  reorders, parallelises, or skips a step whose dependencies
  are satisfied. A step whose dependency failed does not
  execute; the tree follows its failure path. (§3.1;
  lines 3448–3453.) *Check:* scratch-run event order equals
  the declared order; a forced dependency failure shows the
  dependent step absent and the failure path taken.
- **C3-B2 — Step types and the [CHECK] phase.** [TOOL] and
  [RULE] steps execute deterministically in harness code;
  [MODEL] steps call `complete()` exactly once per step
  attempt with the assembled `step_inputs`; every step's
  declared Verify condition executes as a distinct [CHECK]
  phase with its own record event. A step is satisfied only
  when its operation completed AND its [CHECK] passed.
  (§3.1; lines 3454–3461.) *Check:* per-step event triples
  in the scratch record; one `complete()` per attempt.
- **C3-B3 — Declared-inputs-only assembly.** Before any
  [MODEL] call the driver assembles the step's input
  manifest — exactly the artefacts the tree declares, each
  cited by record reference and hash — and writes it to the
  record BEFORE the call. Messages are constructed only from
  the pinned tree text (verbatim) and the manifest's
  artefacts, serialised in the §3.4 canonical form. Tree
  source prohibitions enforced structurally (T05-STEP-06
  never receives the draft's own values; T08's seeded draft
  is diagnosis input only). (§3.1; lines 3462–3472.)
  *Check:* manifest event precedes its MODEL_CALL_LINKED;
  manifest contents equal the tree's declared inputs.
- **C3-B4 — Failure branches: the trees' rules, no others.**
  STOP steps halt the tree; return-once recoveries re-attempt
  once with the failure named in the re-attempt's declared
  inputs; bounded corrections (T05-STEP-06, T08-STEP-04) at
  most 2 attempts; absence-as-finding answers UNKNOWN by
  rule; the T09 decision-stands rule. An ADAPTER_FAILURE
  closes the tree INVALIDATED-INFRASTRUCTURE unless a tree
  declares a covering recovery (none does). A
  GOVERNANCE_FAILURE is recorded and follows the tree's
  failed-verification path — never retried away, never
  reclassified. (§3.1; lines 3473–3483.) *Check:* the
  stub's scripted malformed/refusal cases drive the
  corresponding branches in scratch runs.
- **C3-B5 — No verdicts.** The driver emits the record and
  nothing else: no score, no pass/fail for any tree.
  (§3.1; lines 3484–3486.) *Check:* driver outputs audited —
  the record only.
- **C3-B6 — Budgets.** [TOOL]/[RULE] step 60 s; [MODEL] step
  300 s; tree 3,600 s; run 4 h wall clock. (§3.1; lines
  3487–3491.) *Check:* a scratch context with a shrunk
  budget demonstrates the stop firing (budgets are
  configuration under the pinned values, shrunk only in
  scratch configuration, visibly labelled).
- **C3-B7 — The lane-failure rule.** The 3rd
  INVALIDATED-INFRASTRUCTURE closure stops the run.
  (§3.1; line 3489.) *Check:* scratch run scripting three
  adapter failures stops after the third closure.
- **C3-B8 — The integrity rule.** The snapshot hash is
  re-verified at every TREE_TRIGGERED. (§3.1; line 3490.)
  *Check:* a perturbed scratch snapshot halts the run at
  the next trigger.
- **C3-B9 — Stop finality.** After RUN_STOPPED, nothing
  further is written. (§3.1; lines 3490–3491.) *Check:*
  every stop demonstration's record ends at RUN_STOPPED.
- **C3-B10 — The partial-record shape.** A run stopped
  mid-tree leaves the partial-record shape of Harness §6
  (budgets and stops), read from the pinned snapshot's
  Harness text at build time — the shape is transcribed,
  not assumed. (§4 checkpoint; line ~5963.) *Check:* the
  stopped scratch run's record matches that shape element
  for element.

## C. Trees as data, and the stub (§3.1, §3.7)

- **C3-C1 — Tree definitions are transcribed data.** The
  driver executes the pinned trees (PROCESS-TREES.md) as
  read under INTERPRETATION-NOTE-01; their step structure —
  order, types, Verify conditions, failure branches — is
  transcribed into a data artefact pinned by hash, never
  re-invented in driver code. (§3.1; lines 3443–3447.)
  *Check:* transcription spot-verified against the
  snapshot's tree text for every tree in the declared
  subset.
- **C3-C2 — The declared subset.** The checkpoint's subset
  is declared in the checkpoint report before the run; it
  must exercise [TOOL], [RULE], and [MODEL] steps, at
  least one [CHECK] failure branch, and at least one
  insert (a genuine LEDGER_ENTRY) end-to-end.
- **C3-C3 — The stub subject, labelled.** A scripted stub
  behind the adapter's harness-facing boundary, returning
  declared outputs per (tree, step) from a pinned stub
  script, including the scripted cases verification needs
  (well-formed; malformed; refusal-shaped;
  truncation-shaped). It is selected by pinned test
  configuration in scratch contexts only; the run's
  RUN_STARTED block pins the stub configuration as such;
  scratch records are labelled and never offered as run
  evidence. (§3.7; lines 5755–5782.) *Check:* the scratch
  record's RUN_STARTED names the stub configuration.
- **C3-C4 — The Batch 3 / Batch 5 boundary, named.** §3.7's
  full capture contract (genuine ADAPTER-CAPTURE-02 records
  through the real adapter) completes with the adapter at
  Batches 5–6. Batch 3 exercises the harness side —
  linkage, MODEL_CALL_LINKED, step handling — against the
  stub at the boundary; nothing in Batch 3's report claims
  the adapter's capture path. The reading is stated here
  for Alex's checkpoint review rather than silently
  decided.

## D. Standing batch rules (carried from Batches 1–2)

- **C3-D1 — Records ride with the bundle.** Every scratch
  record the checkpoint cites is shelved in the bundle,
  verbatim, with its hash.
- **C3-D2 — Artefacts pinned by a dated continuation** of
  the re-freeze amendment; prior pins untouched.
- **C3-D3 — No subject call.** The only subject in Batch 3
  is the scripted stub. No provider contact of any kind.
