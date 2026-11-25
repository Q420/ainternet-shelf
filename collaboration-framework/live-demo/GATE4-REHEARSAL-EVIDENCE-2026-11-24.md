# Gate 4 — doorway connection, offline rehearsal: evidence (2026-11-24)

Gate 4 of the demonstration preparation paper
(DEMONSTRATION-PREPARATION-2026-11-24.md §3.6): the doorway
connection for the room configuration — exactly one offered
tool, `container.exec` `{cmd: [string, …]}`, granted alone,
dispatched through the native adapter/doorway path to the
stocked demonstration room — rehearsed whole, offline, with a
stub at the real NVIDIA connector seam. **No provider was
contacted; no live run was made.** The evidence pack stands at
`live-demo/gate4-rehearsal/` (the run record, the seam
captures, the stocking record, the room's final state, the
decision receipt, the terminal readout, report.json). The
witness suite is `live-demo/test_gate4_rehearsal.py`
(**77/77 checks, ALL PASS**, run twice on the final code);
the driver is `live-demo/gate4_rehearsal.py`.

## The rehearsal sequence and its outcomes

A scripted stand-in model drove the real loop / adapter /
doorway / rig path through eight iterations, after a probe
stage whose five scripted trials settled 5/5
`native_catalogue × provider_accepted` (recommendation:
native; the rehearsal's receipt judges native — see "Not
established" for what that judgement is and is not):

| # | Stand-in's act | Outcome |
|---|---|---|
| 1 | `container.exec` `["/bin/cat", "sources/stock-take.md"]` | dispatch-1, result: exit 0, `completed`, the stock-take's full text (untruncated) |
| 2 | `container.exec` bash writing + reading back `/room/scratch/draft.txt` | dispatch-2, result: exit 0, `completed`, draft text returned |
| 3 | `container.exec` python writing `/room/scratch/brief.md` | dispatch-3, result: exit 0, `completed` |
| 4 | `sandbox.read` (ungranted name) | **refused at translation**: resolution `unknown`, refusal class `unknown_tool`; no TOOL_REQUESTED, no dispatch |
| 5 | `container.exec` with `cmd` as a string, not an array | resolved valid at translation; **refused at the doorway**: one REJECTION, ground "container.exec requires its cmd parameter to be a non-empty array of strings (R44)"; no dispatch |
| 6 | `container.exec` `["/bin/cat", "sources/a3-pass.md"]`, the room's reaper forged beforehand | dispatch-4, **result** (not failure): `termination: precondition-failed: rig-integrity`, exit_status null, no output — the room's refusal travelled back in the contract |
| 7 | `container.exec` `["/usr/bin/sha256sum", "sources/index-tail.md"]`, reaper restored | dispatch-5, result: exit 0, `completed`, stdout the source's in-room SHA-256 `eb16b56b…` |
| 8 | yield (text contract) | loop ends `yield`, ok, 8 iterations, 70 events in the record |

## The ten hops, with their evidence

| # | Hop | Evidence in the pack |
|---|---|---|
| 1 | Assembly judged and issued | ASSEMBLY_GENERATED declares `catalogue_contract: exec-v4` and grants exactly the one exec grant; the case carries bounds {12 steps, 600 s} and a boundary naming manifest `bd6f3cae…`; ASSEMBLY_JUDGED is native, its `decision_receipt_hash` = SHA-256 of the canonical retained receipt (`decision-receipt.json`); ASSEMBLY_PACKED seals native |
| 2 | Stocking | `stocking.json`: manifest identity `bd6f3cae…` (the released source set), per-source hashes matching the manifest, smoke set 8/8 ok, deliverable absent at stocking's end, 2 smoke executions standing in the room state before any worker execution |
| 3 | The outbound request, as transmitted | `captures.jsonl` — the stub at the real seam recorded every request's exact bytes (base64 + SHA-256): identify 308 B; the five probe requests 1,534 B each; iterations 1–8: 6,972 / 40,465 / 16,245 / 17,457 / 12,990 / 14,548 / 16,452 / 16,791 B. Every iteration request carries `tools` = exactly one definition, `container.exec`, bearing the registry's own worker-facing description. The transmitted definition's `parameters` is the empty object schema the closed adapter builds from the catalogue's list-form schema (see "Not established") |
| 4 | The response, as received | RESPONSE_EVIDENCE `captured` for all 8 iterations; each filed artifact under `run/responses/` cross-checks ok against its disposition (hash + L1 agreement) |
| 5 | Classification and translation | 7 TRANSLATION_RECORDED events (iterations 1–7; the yield carries none), each bound to its iteration's artifact hash, each stamped registry v4; iteration 4's call refused `unknown_tool`; iteration 5's resolved valid |
| 6 | The doorway dispatch decision | 5 TOOL_DISPATCHED, all `container.exec`, all stamped `tool-registry-v4`; exactly 1 REJECTION (hop table row 5 above); 6 TOOL_REQUESTED (the translation refusal produced none) |
| 7 | The room execution | `room-state.json`: 7 executions — the 2 smoke executions, then the 5 worker executions reconciling 1:1 with the 5 dispatches by command array, in order; exactly 1 `rig_integrity_events` entry; the tampered execution's record refused, `failed_precondition: rig-integrity`, rc null. The host witness's independent views are the rig/Track G suites' evidence (INDEX 461/464), not re-taken here |
| 8 | The result's carriage back | Iteration 2's captured request bytes contain provider call ID `fc-g4-1` and, in the package's `tool_results` carriage, dispatch-1's result object — `"exit_status": 0` and the stock-take's own first line (standing JSON-escaped in the rendered record, as the package renders it); iteration 8's request likewise carries `fc-g4-7` and dispatch-5's hash output |
| 9 | The deliverable at the wall | `scratch/brief.md` hashed host-side from the tree before teardown: SHA-256 `0041ab583ff46def6cdf518207e5e9a4d40fe06b3b3e218e9ddc6f9e94655e14` — equal to the scripted brief's hash, as report.json records |
| 10 | Reconstruction | The independent checker over the record: **11/11 checks ok** (run_binding, chain_hash, chain_sequence, replay, projection_schema, snapshot_schema, replay_equality, seal_correspondence, assembly_correspondence, dispatch_correspondence, loop_correspondence) |

## The result contract, verified end to end

Every exec TOOL_OUTCOME's result carries **exactly** the
paper §2.3's ten fields — `exit_status`, `stdout`,
`stdout_bytes_total`, `stdout_truncated`, `stderr`,
`stderr_bytes_total`, `stderr_truncated`, `termination`,
`cpu_seconds_charged`, `duration_seconds` — with standing
types, asserted per dispatch by the witness suite. The
source read's totals equal its carried byte count
(untruncated); the tampered execution's outcome is a
`result` whose termination names the failed precondition;
no outcome is a failure or a crash for a room refusal.

## The terminal readout

`terminal-readout.md` in the pack renders from the
rehearsal's export through `live-demo/terminal_readout.py`:
the five `container.exec` dispatches appear with their
provider call IDs, the refusals and the yield as themselves.
The witness suite also re-renders the export independently
and asserts no error.

## A rehearsal finding, recorded

The pack's first invocation passed the driver a **relative**
work path: the rig refused every smoke execution on its
storage-backing precondition — the live mount table records
absolute paths, so a relative tree path cannot be verified
against it — and the stocking failed closed, exactly as the
rig is built to do. The driver now resolves its work path to
an absolute path before stocking; the refusal itself is the
rig's fail-closed behaviour standing as designed, not a rig
defect.

## What this rehearsal does NOT establish

- **Provider behaviour.** The stub proves the seam's
  construction and carriage — the exact bytes the real
  transports build, and the result's return into the next
  request — not that the NVIDIA route delivers a well-formed
  `container.exec` call when the tool is offered. **Track A's
  residual delivery uncertainty (INDEX 433) stands until the
  live run.**
- **The live mode judgement.** The probe evidence and the
  native judgement here are rehearsal furniture: a scripted
  stand-in examiner's receipt, filed so the record's
  probe-governed shape stands complete. The live run's
  judgement is the examiner's at the release gate (gate 5),
  with the route's catalogue identity checked there under
  the flagged-conflict rule.
- **Hop 3's field set for this route** is the offered
  definition (asserted present in every transmitted body).
  BD-1's `disable_tool_validation` is a Groq-route field;
  it is not committed for the NVIDIA route and is not
  asserted here.
- **§2.5's room-record reference** is carried by the pack's
  reconciliation (room executions ↔ dispatches by command
  array and order, hop 7), not by an extra field inside the
  worker-facing result: the TOOL_OUTCOME result is exactly
  the §2.3 object, nothing added.
- **Composition competence** — as everywhere on this line,
  untested: the stand-in is scripted, and the brief's text
  is furniture whose hash, not whose accuracy, is asserted.

## Suites

- Witness suite (this gate): **77/77 ALL PASS**, twice on
  the final code; zero leftovers after each run (room tree
  gone, no mount standing, no bwrap process).
- Adapter suite (`test_piece_native_adapter.py`): ALL PASS.
- Harness pacing suite (`test_harness_pacing.py`): ALL PASS.
- Rig suite (`test_rig.py`): **34 passed, 0 failed of 34**.
- Track G suite (`test_track_g.py`): **22 passed, 0 failed
  of 22**.
- The wider unit sweep also stands green; the probe suite
  stands at its known 54 pass / 3 ruled-superseded failures
  (INDEX 403), unchanged.

---

## Addendum — the Gate 5 schema qualification, resolved (2026-11-24)

Vane's Gate 4 closure (INDEX 469) carried one qualification
to the Gate 5 ledger: the transmitted function definition
for `container.exec` bore an empty parameters schema,
`{"type": "object", "properties": {}}`. The registry
supplies `cmd` as list-form parameter metadata, but the
adapter passed through only a dictionary-form schema and
otherwise substituted the empty object — so the
provider-facing definition did not itself declare the `cmd`
property the prompt catalogue describes and the doorway
enforces. The rehearsal's witness asserted the empty
schema; it was not to be mistaken for a complete typed
signature. This addendum records the correction. The pack
at `live-demo/gate4-rehearsal/` was regenerated whole by a
fresh rehearsal run under the corrected definition (never
hand-edited); the outcome stands as before — yield, 8
iterations, 70 events, the brief's hash unchanged
(`0041ab58…`).

**The fix** (`src/framework/adapter.py`): a dictionary-form
parameters value still stands exactly as the catalogue
carries it, and an absent one still carries the empty
object schema — but list-form metadata is now translated,
field for field, by `_native_parameters_schema`: one
property per declared parameter, the declaration's meaning
standing as the property's description, and the required
declarations as the schema's `required` list, in
declaration order. The translation is general over the
registry's one schema form; nothing in it names
`container.exec`.

**The corrected schema, as transmitted** (iteration 1's
captured request in the regenerated pack; every iteration
request carries the same definition):

```json
"parameters": {
  "type": "object",
  "properties": {
    "cmd": {"description": "the command to execute, as an array of strings: the program followed by its arguments"}
  },
  "required": ["cmd"]
}
```

The definition now declares `cmd`, as required, with its
form stated in the property's description — the registry's
own words.

**The limit, named:** the registry's parameter metadata
carries no machine-readable types — `worker_facing` and
the translation boundary's validator both settle the
declaration form as exactly name / required / meaning — so
no JSON type is asserted for any property: `cmd`'s
array-of-strings form stands in its description's words,
and the doorway's ceiling check, not the transmitted
schema, remains what enforces the shape. Asserting a typed
`{"type": "array", "items": {"type": "string"}}` for `cmd`
would require either a per-tool hardcode in the adapter —
invention the adapter's settled discipline forbids — or a
registry-format extension across both `tool_policy` copies
and the checker's own validator, neither of which this
correction undertakes. Whether the description-carried form
suffices for the live route is the release examination's
question, as the qualification itself framed it.

**Proof and suites** (all on the final code): before/after
capture of the adapter's derivation over representative
packages — dictionary-form definitions byte-identical,
no-parameters definitions byte-identical, list-form
definitions changed in `parameters` only (name and
description untouched). Gate 4 witness: **77/77 ALL PASS,
twice**, its hop-3 assertions now asserting the corrected
schema (the empty-schema assertion replaced, not kept
alongside; the expectation is built from the registry's
worker-facing layer, not from the adapter's output). Native
adapter suite: ALL PASS. Native-offer probe suite: ALL
PASS. A3-CAT catalogue suite: ALL PASS. Rig suite: **34
passed, 0 failed of 34**. Track G suite: **22 passed, 0
failed of 22**. Also run: the native-probe P1, P2 and paced
suites, ALL PASS; the assembly probe suite stands at its
unchanged 54 pass / 3 ruled-superseded failures (verified
identical with and without this change — §6, P10, P7, the
INDEX 403 three).

**One consequence, stated plainly:** the NVIDIA-route
probe build (closed, INDEX 404) binds its construction to
the pre-correction derivation's hashes in its scope, and
its suite now refuses the construction reproduction — the
derived definitions hash to `30a01adf…` and the modified
request to `884e06f5…`, not the bound `6f3331ac…` /
`0229b0f0…` (baseline reproduced without this change: ALL
PASS). The bound hashes were **not** re-pinned here:
re-pinning would falsify that build's examined scope. The
probe's live run was never released — the demonstration
paper folded its route into this gate line — and the
rehearsal above now witnesses the same seam on the real
path. The probe construction's disposition under the
corrected derivation is the examiner's to rule.
