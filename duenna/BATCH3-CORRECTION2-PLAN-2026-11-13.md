# BATCH 3 CORRECTION — ROUND 2 PLAN (2026-11-13)

**Standing:** Batch 3 correction bundle b3cc629d inspected by Alex
2026-11-13 (PB-ID pb-mwftwgkr-e-b6fd, ⟦ALEX-FINAL⟧) — NOT CLEARED on
four findings. The bundle and its pins stay immutable; accepted work
is not redone. This plan addresses exactly the four findings.
Remmy verified each finding against the artefacts before planning:
all four stand (driver constructor loads trees/data/corpus before
preflight, lines 106–134; `_pilot_root()` reads `config["pilot_root"]`,
line 158; `_load_authority()` anchors the authority to the hash
written in the local continuation, lines 163–187; the T06-E skip is
at test line 443; `schema_ok()` is invoked on the MAIN record only,
line 241; the C3-B10 check is the single compound assertion at test
lines 494–506).

**Files touched by this round (exhaustive):** `pilot_driver.py`
(findings 1 and 2), `test_batch3_correction.py` (findings 1–4),
`PILOT-PIN-AUTHORITY-01.json` (re-minted: driver and suite pins
move), one new re-freeze continuation
(CONTINUATION-BATCH3-CORRECTION-2), one new chunk sheet, one round-2
checkpoint report, one new bundle directory
duenna/batch3-correction2-2026-11-13/. `pilot_tools.py` and
`pilot_record.py` are NOT touched. No specification revision is
required by any item below; finding 2 states its reasoning.

## Item 1 — the pin authority governs the inputs actually consumed (HIGH)

**Root derivation.** `_pilot_root()` no longer reads configuration.
The root is derived from the driver artefact's own resolved
location: the correction build's fixed layout places the driver at
`<root>/batch3/correction/pilot_driver.py`, so the root is
`Path(__file__).resolve().parents[2]`. If `config` carries a
`pilot_root` that differs from the derived root, preflight refuses
(PILOT_ROOT_MISMATCH) before anything loads; an absent value is
fine — the derived root governs either way.

**Independent trust anchor.** The driver source carries one
constant, `EXPECTED_AUTHORITY_SHA256`, set at build time to the
minted authority's hash and recorded in the round-2 continuation,
which pins the driver's own sha256 in turn. `_load_authority()`
hashes the authority file and compares it to the constant — the
continuation is no longer the runtime anchor (it remains the
shelved record of the chain). The authority also carries the
driver's own entry; the driver hashes its own file and compares,
binding the pair in both directions. Stated boundary, for the
record: runtime self-defence covers substitution of inputs,
authority, or continuation under an intact pinned driver; a caller
who replaces the driver itself has replaced the artefact the shelf
pin chain identifies, which is caught by hash comparison against
the shelved continuation at inspection — the shelf, not the
runtime, is the root of trust, and the constant carries that trust
into the runtime.

**Binding and load order.** The constructor stores its arguments
and loads nothing. `run()` calls `preflight()` first; preflight
resolves every consumed path from the authority's entries under the
derived root — trees file, snapshot directory, the five Batch 1
data files, the stub script, pilot_record, pilot_tools, pilot_jcs —
verifies each file's hash against its entry, and only then does the
driver load trees, data, corpus and rules, from those resolved
paths. Constructor arguments `data_dir`, `trees_path`,
`snapshot_dir`: when supplied and not equal to the authority-
resolved path, preflight refuses (PATH_NOT_AUTHORITY) before any
load and before any run directory exists. One declared exception,
named in the open: the integrity demonstration's perturbed snapshot
copy is passed through a separately named configuration key,
`test_snapshot_dir`, used by that one test only; preflight still
verifies the canonical snapshot against the authority first, the
override and its divergent hash are recorded in RUN_STARTED's
`test_configuration`, and the run proceeds only to its expected
integrity stop. The key is a test mechanism and is labelled as one
in code, in the continuation, and in the report; if you judge it
too wide, the fallback is to stage the perturbation as an authority
variant entry minted for the scratch copy, at the cost of a second
authority mint per suite run — your ruling either way.

**Negative tests (each its own transcript line, each asserting
refusal AND no run directory created):**
- N1 alternate `data_dir`: a copied data directory with one byte
  changed in PILOT-DATA-EXPECTED-01.json → PATH_NOT_AUTHORITY.
- N2 alternate `trees_path`: a copied trees file → PATH_NOT_AUTHORITY.
- N3 alternate root: `config["pilot_root"]` pointing at a staged
  root holding an internally consistent forged authority +
  continuation pair → PILOT_ROOT_MISMATCH.
- N4 in-place pair replacement: the real authority file and the
  real continuation both replaced together (continuation rewritten
  to name the forged authority's hash) in a staged copy of the
  freeze directory under the derived root → refusal on the embedded
  constant (AUTHORITY_ANCHOR_MISMATCH); the genuine files are
  restored by the test from its own copies and their hashes
  re-asserted afterwards.
- The existing (a)/(c)/(d) caller-pin tests stand unchanged.

## Item 2 — §4(p) covers every MODEL step, T06-E included (HIGH)

**Why no amendment is needed.** §4(p) requires recomputation "from
the cited producing outputs". Inspection of the driver shows the
underlying record gap: the T06 procedure steps (A source-location,
B contradiction, C support, D default) return their accumulated
`outcomes` map as step outputs, but `_tool_step` records only the
`progress` fragments as STEP_PROGRESS events — the outcomes map
itself, which is exactly the artefact T06-E's manifest carries,
never enters the record whole. The correction is therefore in the
driver, not the paper: each T06 procedure step additionally emits
its resulting outcomes map as a STEP_PROGRESS payload under the
key `outcomes`, in the same step, before its check adjudication.
STEP_PROGRESS payloads are the record's step-defined progress
channel; nothing in the frozen design or Rev 26 forbids the
payload carrying the step's produced map, and the other trees'
producing outputs already ride the record the same way.

**Test recompute.** `manifest_recompute` gains the T06-E branch:
the artefact is reconstructed as `{"outcomes": <the outcomes map
from the last T06 procedure step's STEP_PROGRESS before the MODEL
step>}`, deep-compared field by field against the outcomes the
A–D events jointly evidence (each statement's label cross-checked
against its producing step's own progress/extraction events), and
its canonical sha256 compared to the manifest entry — the same two
comparisons (deep equality + manifest hash) the (p) wording
requires, applied to the reconstructed artefact and the declared
inputs.

**Exhaustiveness.** The dispatch becomes an explicit table keyed by
tree family; the fall-through branch appends a problem
("unrecognised MODEL step") instead of skipping. A coverage
assertion closes the check: for every record the suite examines,
the count of MODEL STEP_TRIGGERED events equals the count
recomputed, asserted as its own transcript line per record. The
recompute runs over all seven records, not MAIN alone (the budget
runs' T02 MODEL steps included).

## Item 3 — §4(n) schema assertions over every record (MEDIUM)

`schema_ok()` is applied to all seven run records, one identifiable
transcript line per record. Two field assertions are added to the
existing rule set, which otherwise stands exactly as Rev 26 §4(n)
writes it (sixteen-type vocabulary, per-type nullability, the
three-row GOVERNANCE_EVENT mapping, payload object, 64-hex hash
fields): `run_id` asserted a string on every event and equal to the
record's run id; `recorded_at_utc` asserted to parse as ISO-8601
and to carry UTC (offset zero / Z suffix), per event. The C3-A1
sequence check is extended alongside to every record (contiguous
seq from 1, event_id form), each its own line, so no part of the
schema discharge rests on MAIN alone.

## Item 4 — §4(q) C3-B10 as the full §6.4 matrix (MEDIUM)

The single compound assertion is replaced by separately named
checks on the RUN-STOP record, one per §6.4 element:
- Q1 RUN_STOPPED is the terminal event; nothing follows it in the
  record (seq == event count).
- Q2 the stop reason is exactly RUN_BUDGET_EXCEEDED and the
  position is exact: the terminal event's seq and the elapsed
  accounting in its payload detail match the staged budgets
  (run_s 150, advance 40).
- Q3 no RUN_CLOSED anywhere in the record.
- Q4 the open tree (T05) is closed INCOMPLETE; every tree triggered
  before the stop has exactly one TREE_CLOSED.
- Q5 strict prefix: the open tree's completed steps, in record
  order, form a proper prefix of T05's declared step sequence in
  the pinned trees data — equal to its first k steps, k strictly
  less than the full count.
- Q6 no events for unrun steps: no event in the record carries a
  step_id of the open tree beyond the prefix, and no event carries
  a tree_id never triggered.
- Q7 chain condition: the hash chain verifies from genesis to the
  terminal event over the partial record exactly as it lies
  (verify_chain on the stopped record).
- Q8 partial materialisation: ledger.json materialises exactly the
  partial record's LEDGER_ENTRY payloads (retained from the current
  check, now its own line).
The same element treatment is applied in miniature to the LANE and
INTEGRITY stops where the elements exist there (terminality, no
RUN_CLOSED, chain) — named as retained checks, not new scope.

## Round-2 mechanics

On your approval: the chunk sheet for round 2 is drafted from this
plan and shelved BEFORE the build; Ben's build-go confirmation for
the round is placed on the record the same way as round 1 (his
2026-11-13 build go covers Batches 2–6 in order — the round-2
confirmation will be named explicitly rather than assumed). The
authority is re-minted (driver + suite pins), anchored by
CONTINUATION-BATCH3-CORRECTION-2; the suite runs in full (round-1
checks retained verbatim except where items 2–4 extend them); the
Batch 2 regression battery re-runs against the untouched corrected
tools. A new bundle is shelved at
duenna/batch3-correction2-2026-11-13/ with its own checkpoint
report discharging this plan item by item; b3cc629d is not modified
or re-used. Record-shape note, declared in advance: item 2 adds
STEP_PROGRESS events to T06 trees, so round-2 run records differ
from round-1 records wherever T06 runs — expected, and the
round-2 report will say so rather than let the counts surprise.

No other files, no other findings, no Batch 4 work, no subject
call. Submitted for your inspection and approval before any
implementation.
