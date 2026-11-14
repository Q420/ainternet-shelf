# BATCH 3 CORRECTION PLAN — answering Alex's checkpoint review

**Review answered:** Alex's Batch 3 review (pb-mwfqjv5l-5-958i):
NOT CLEARED — three HIGH, one MEDIUM; readings 1, 3, 4, 6
accepted, 2 rejected as implemented, 5 not accepted as
demonstrated. Every factual claim in the review was verified
against the code before this plan was drafted; all stand as
stated. This is a plan only — no implementation changes are
made by it. The original bundle (f11d5375) and all prior pins
are preserved unchanged; the correction, when built, pins new
artefact versions by a dated correction continuation, exactly
as Batch 2's correction did.

## Item 1 — HIGH: authoritative pinning + complete pin inventory

*Obligation:* Rev 22 §3.4 (the pinned-input block: every
artefact consumed, verified at pre-flight against
PILOT-MANIFEST-01 + the re-freeze amendment; any mismatch and
the run does not start). *Chunks:* C3-A7; also C3-D2.

*Defect as found:* preflight() verifies against
caller-supplied cfg["pins"]; the suite generated those pins
by hashing the files under test (self-pinning); and five
consumed Batch 1 data artefacts (PILOT-DATA-PACKS-01,
PILOT-DATA-EXPECTED-01, PILOT-DATA-FIXTURES-01,
PILOT-DATA-T09-01, EXTRACTOR-RULES-02) are absent from
RUN_STARTED's pin set.

*Correction:*
1. A machine-readable **pin authority** (PILOT-PIN-
   AUTHORITY-01.json) is generated from PILOT-MANIFEST-01
   and the re-freeze amendment chain, enumerating **every**
   artefact the build consumes: the five Batch 1 data files,
   EXTRACTOR-RULES-02, the snapshot (sections + manifest),
   PROCESS-TREES.md + INTERPRETATION-NOTE-01, the Batch 1
   interfaces, PILOT-TOOLS-01 (corrected pin), the JCS
   implementation, the record writer, the driver, the trees
   data, the stub subject and the run's stub script. The
   authority file is itself pinned by the Batch 3 correction
   continuation; its hash is cited in the correction report.
2. The driver's preflight loads the authority from the
   freeze location and verifies the consumed files against
   **it**. Caller-supplied pins are configuration only: any
   divergence from the authority (extra, missing, or
   different hash) refuses the run.
3. RUN_STARTED's pin set becomes the authority's full set —
   the complete consumed inventory, by name.

*New tests:* (a) **substitution** — a scratch copy of a
consumed data file is modified and the caller-supplied hash
is changed to match the modified file; preflight must still
refuse, against the authority. (b) **inventory** — the main
run's RUN_STARTED pins are asserted to cover the consumed
inventory by name, including the five data files. (c)
**missing-entry** — a caller pin set omitting an authority
entry refuses.

## Item 2 — HIGH / amendment item: artifact and evidence provenance

*Obligations:* the pinned tree text (T05-STEP-04:
reference_insert every field; output "record + full
ledger"); Harness §1.5 (every produced field carries its
ledger entry); Rev 22 §3.3 (the acceptance set: EXTRACTED
results only); Rev 22 §3.4 / Harness §2.3 (each successful
reference_insert emits exactly one LEDGER_ENTRY).
*Chunks:* C3-C2; the report's reading 2 (rejected).

*Defect as found:* _construct() hardcodes artifact and
evidence as literals; neither field has a ledger entry; the
artifact does not come from T05-STEP-02's verified output,
and T08's handler performs no artifact-location work at all.

*The tension, stated plainly:* the tree and §1.5 require a
ledger entry for every field; §3.3 admits only EXTRACTED
results to insertion; no extraction exists, or honestly
can, for `evidence` (a citation list derived from the run's
own extractions) — and fabricating one would be exactly the
pretence the pilot exists to catch. Three routes were
considered:

- **Route A — extend the extractor rules.** A rule can
  honestly extract `artifact` from the manifest section's
  stated row. It cannot reach `evidence`. Partial only.
- **Route B — settle by reading.** Amend the spec to read
  "every field" as every insertable field, with carried
  fields evidenced by event citation in the record
  artefact. This narrows §1.5's plain sentence; it makes
  the pilot's evidence claim smaller to fit the build.
- **Route C — a second insertion class, by amendment
  (RECOMMENDED).** Amend §3.3 (a Rev 23) with a bounded
  **carried-field** class: a field whose value is a verified
  step output of the same tree — produced by a [TOOL] step
  whose own [CHECK] passed, cited by event reference and
  the producing payload's sha256 — may be presented to
  reference_insert by that citation instead of an
  operation_id. Recomputation at insert time re-reads the
  cited event from the record, recomputes its payload hash,
  confirms the producing step's CHECK_RESULT passed, and —
  for `evidence` — confirms the cited list equals the
  source_refs of the run's EXTRACTED results for that
  tree's construction, each present and unconsumed-by-
  another-field. The LEDGER_ENTRY for a carried field
  carries a `carried_from` provenance block ({event_id,
  payload_sha256, producing_step, check_event_id}) in place
  of an extraction's, with its recomputation evidence.
  The class is additive: Batch 2's cleared behaviours and
  negative tests are untouched, and PILOT-TOOLS-01 is
  superseded by a corrected version pinned by amendment,
  exactly as in Batch 2's correction. Under this route
  every governing sentence stays true at full strength.

*Implementation consequences named in advance:* T05's
construct presents artifact carried from STEP-02's output
(never a literal); T08's STEP-02 performs the STEP-02-
equivalent artifact-location work its text declares ("As
T05-STEP-02/03"), so its artifact is likewise a verified
output; evidence is presented carried from the construction's
own extraction events.

*New tests:* the T05 and T08 records each carry **eight**
LEDGER_ENTRY events, one per produced field; a carried
presentation citing a tampered payload hash refuses
(CARRIED_HASH_MISMATCH, no ledger entry); a carried
presentation from a step whose check failed refuses; an
evidence list omitting one of the construction's
extractions refuses; the original Batch 2 refusal battery
re-runs unchanged against the superseded tools.

*Decision path:* Alex's approval of this plan selects the
route. If Route C (or any route amending the spec), the
Rev 23 amendment is drafted and cleared through Alex's
inspection **before** the correction build, per §2.1 and
the loop's spec-first order; the correction build then
proceeds under Ben's existing build go.

## Item 3 — HIGH: step-budget adjudication order

*Obligation:* Rev 22 §3.1 budgets and stops; Harness §6.2
(a step exceeding its budget fails with the timeout class).
*Chunk:* C3-B6; reading 5 (not accepted as demonstrated).

*Defect as found:* _tool_step/_model_step emit CHECK_RESULT
and STEP_SATISFIED before _run_step compares elapsed time;
an over-budget success would leave a satisfied step the
control flow treats as failed. No step-budget test exists.

*Correction:* the step executors return their operation
result and proposed check **without** emitting the terminal
step events. The driver then adjudicates in order:
(1) operation events stand as they occurred (TOOL pairs,
MODEL_CALL_LINKED, STEP_PROGRESS); (2) budget adjudication —
if elapsed exceeds the step budget, the step's terminal
events are a CHECK_RESULT recording the budget failure
(condition quoted as the budget rule; compared: elapsed vs
budget; result FAIL) and STEP_FAILED with the §6.2 timeout
class, and the step's own check is never emitted as passed;
(3) within budget, the step's own CHECK_RESULT and
STEP_SATISFIED / STEP_FAILED follow as now. One coherent
outcome per attempt, in the record and in the control flow.

*New tests:* (a) **TOOL step over-budget** — a scratch run
whose configuration declares a per-step clock advance during
a named [TOOL] step (scratch mechanics, named in
RUN_STARTED), exceeding the 60 s step budget: the record
shows STEP_FAILED (timeout class), no STEP_SATISFIED, no
passing CHECK_RESULT for that attempt, and the tree takes
its failure branch. (b) **MODEL step over-budget** — the
stub scripts advance_clock_s beyond the 300 s [MODEL]
budget: STEP_FAILED with the adapter-timeout class, same
coherence assertions. (c) **Coherence invariant** — asserted
over every record in the suite: no (tree, step, attempt)
carries both a passing CHECK_RESULT/STEP_SATISFIED pair and
a subsequent STEP_FAILED.

## Item 4 — MEDIUM: evidence and test-fidelity gaps

*Chunks engaged:* C3-A5, C3-A6, C3-B3, C3-B10, C3-A2, C3-D1.

*Corrections:*
1. **Ledgers preserved.** The correction bundle includes
   every run's materialised ledger.json as its own artefact
   (the Batch 3 bundle's omission is recorded here as the
   miss it was — the ledgers existed in the room and were
   simply not shelved), and the report's bundle inventory
   lists them by name and hash.
2. **C3-A6 at its wording.** The confinement check becomes
   a before/after comparison of the pilot root's directory
   listing (the runs root's parent): the only delta the
   runs may produce is their own run directories; a scratch
   commitments/ directory placed in the area is asserted
   byte-unchanged, evidencing the absent write path.
3. **C3-B3 at its wording.** For every [MODEL] step, the
   test recomputes the manifest's artefacts from the cited
   producing outputs and asserts deep equality with the
   step's declared inputs (per the trees data) — citations
   and hashes, not mere presence.
4. **C3-B10 element by element against Harness §6.4:**
   exactly one terminal event, last; the chain verifies to
   it; every closed tree's steps are complete per its
   declared sequence; the open tree's completed steps form
   a strict prefix of its declared sequence; no event
   exists for any unrun step; RUN_STOPPED's payload carries
   reason and position. Each element is its own named check.
5. **C3-A2 types.** The schema check asserts declared field
   types: seq an integer; event_id/run_id/recorded_at_utc
   strings (the timestamp ISO-8601-parseable); tree_id /
   step_id string-or-null; payload an object; both hashes
   64-hex.

## Correction run shape

On Alex's approval of this plan (and clearance of any Rev
23 it requires): the correction is built at the corrected
sites only; the full Batch 3 suite re-runs plus the new
tests above; a correction checkpoint report discharges this
plan item by item; corrected artefacts are pinned by a
second dated Batch 3 continuation; the original artefact
pins and the f11d5375 bundle remain untouched as history.
Batch 4 remains closed throughout; no model call or
provider contact at any point.
