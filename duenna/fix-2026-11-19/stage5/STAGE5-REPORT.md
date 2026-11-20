# Duenna Stage 5 — Operation Identity and Recovery Report

Date: 2026-11-20
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 5; ID-SYSTEM-DESIGN-DRAFT-V3.md (K4, G3, P3)
Build location: ~/workspace/duenna-fix/stage5/ (Python standard library only)
Approval: Ben, 2026-11-20 (Stages 2–9 approved; Stage 5 built from the plan, after Stage 4 cleared Gate 1)

## Status of this report

The Stage 5 harness is built and its full test suite passes
(26/26, below), with the Stage 1 (68/68), Stage 2 (27/27),
Stage 3 (38/38) and Stage 4 (36/36) suites green as
regression. This report is EVIDENCE for the examiner, not a
verdict: a builder's green run establishes that the mechanism
behaves as specified on the exercised cases; whether Stage 5
passes is the examiner's determination (Gate 1 discipline),
not this report's. Nothing here declares Stage 5 complete.

## What was built

- `operations.py` — operation identity and PURE input
  construction (K4's construction half, P3). An operation's
  identity is a canonical function of its (run, step, slot)
  triple: a digest over the triple's canonical encoding,
  computed — not issued — so any process, at any time,
  rebuilding a step's inputs derives the identical identities.
  `build_inputs` is pure: it reads no state, writes no state,
  mints nothing and consumes nothing; repeated calls return
  equal operations. An `Operation` is immutable (the Stage 3
  seal discipline), its payload held as its canonical
  encoding and handed out as fresh copies, its payload digest
  part of its presented form.
- `receiver.py` — the insertion receiver (K4's
  receiver-recognised form, G3). The receiver holds NO
  consumption state in memory. Its durable state is two
  artefacts: the Stage 1 record, carrying `INSERTION_APPLIED`
  and `OPERATION_CONSUMED` events (consumption as recorded
  state, established only by reading the record back through
  the verified snapshot), and an effect store — one file per
  applied operation, written atomically at a rename boundary
  (temp file, fsync, `os.replace`, directory fsync). Every
  presentation first runs Stage 3's shared
  `verify_record_current` (chain recomputation AND terminal
  binding); an integrity failure raises `InsertionRefused`
  carrying `record_chain_verification_failed` and writes
  nothing — no effect, no event.
- `receiver_probe.py` — a standalone receiver program, the
  vehicle for the restart proofs (below). It is launched as a
  subprocess, is handed only a spec file (durable paths,
  action, the operation's run/step/slot/payload), rebuilds
  the operation through the pure constructor inside its own
  process, and prints its outcome as JSON.

## The mechanism

A fresh application performs, in order: (1) write the effect
file (atomic at the rename); (2) append `INSERTION_APPLIED`;
(3) append `OPERATION_CONSUMED`. K4's specified failure modes
land in the windows between these steps, and recognition —
not re-application — closes each one:

- A presentation whose identity is recorded CONSUMED returns
  ALREADY_SATISFIED citing the recorded consumption event
  (seq and digest); nothing is appended and no effect is
  rewritten. The answer is read off the record.
- A presentation whose effect has landed but whose recording
  is incomplete (either window after step 1) is recognised
  as the operation's single application: the receiver appends
  whichever of `INSERTION_APPLIED` / `OPERATION_CONSUMED` is
  missing (an applied event appended in recovery is marked
  `recovered: true`), returns ALREADY_SATISFIED with
  `transition_completed: true`, and applies nothing.
- An interruption mid-insertion leaves only an orphaned temp
  file — the receiver's scratch, never an application. A
  retry discards it (found by the same temp name, including
  from a new process) and applies cleanly.
- The payload is bound to the identity at presentation: if
  any durable trace of an identity exists, it names the
  payload digest that was applied; the same identity arriving
  with a different payload digest is refused
  (`payload_conflict`), never satisfied and never applied.
  A changed input cannot ride a consumed or applied identity.
- One divergence is surfaced rather than repaired: a record
  claiming `INSERTION_APPLIED` whose effect file is absent
  cannot arise from any crash in the apply order (the effect
  is written before the event), so the receiver raises
  `InsertionDivergence` and writes nothing.

## Test 5 — the acceptance cases, each with its outcome

**Retry after partial insertion.** The crash hook kills the
presentation mid-effect-write, before the rename: no effect
exists, one orphan temp file does, recorded state is
UNCONSUMED. The retry returns APPLIED, the orphan is gone,
exactly one effect file stands, state CONSUMED. PASS.

**Interruption between insertion and state recording.** Two
windows, tested separately. (a) Crash after the effect write,
before any recording: the retry returns ALREADY_SATISFIED
with `transition_completed`, the effect count stays 1, the
record gains exactly one `INSERTION_APPLIED` (marked
recovered) and one `OPERATION_CONSUMED`. (b) Crash after the
applied event, before consumption: recorded state before the
retry is APPLIED_UNCONSUMED; the retry returns
ALREADY_SATISFIED with `transition_completed`, appends only
the consumption event, applies nothing. PASS (both windows).

**Retry after recovery — recognition after an actual process
restart.** The restart is a genuine process boundary, effected
by subprocess: `receiver_probe.py` is a separate program run
under `sys.executable`; it shares no object, no memory and no
channel with the presenting process — its only inputs are the
spec file and the durable artefacts, and it rebuilds the
presented operation through the pure constructor in its own
process, as a restarted driver's retry would. Three cases:
(i) an operation consumed before the restart is recognised by
the fresh process — ALREADY_SATISFIED citing the SAME
consumption event (seq and digest) the original process
produced; the effect count and the consumption-event count
stay 1; a probe state query returns CONSUMED. (ii) A crash
between insertion and recording, then a fresh-process retry:
ALREADY_SATISFIED with `transition_completed`, one effect,
one consumption event; a second fresh-process presentation
changes nothing further and cites the same consumption event.
(iii) A crash mid-insertion, then a fresh-process retry:
APPLIED, the dead process's orphan discarded by the same temp
name, exactly one effect. No case substitutes an in-process
re-creation for the restart. PASS.

**Re-presentation of consumed and unconsumed operations.**
Consumed: ALREADY_SATISFIED, citing the recorded event, with
the record's length and the effect count both unchanged —
including when the presented operation is a REBUILT one (the
retry path's reconstruction, DR-01's exact shape): it is
recognised as itself, not reconstructed as new and not
refused as a duplicate. Unconsumed: an operation never
presented applies cleanly (APPLIED), both in the original
process and, after a restart, in a fresh one — recognition of
other consumed operations produces no false refusal, and
recognition is per-identity (a consumed operation's sibling
still reports UNCONSUMED until presented). PASS.

**The properties, jointly.** Across every case above: no
operation's effect is ever applied twice (effect-file counts
asserted everywhere); no genuinely unconsumed operation is
refused (fresh presentations assert APPLIED in-process and
across the restart); no consumed operation is reconstructed
as new (identity is a function of the triple, and the rebuilt
operation is the one recognised).

## Supporting cases

- Pure construction: identity is a function of the triple
  alone (all three parts bind; the payload does not);
  repeated builds are equal; a build leaves the durable state
  byte-identical; reconstruction after consumption yields the
  same operation.
- Payload binding: a changed payload under a consumed
  identity, and under an applied-but-unconsumed identity in
  the crash window, are both refused with `payload_conflict`
  and write nothing; the honest retry still completes after
  the crash-window refusal.
- Record discipline: an event body edited on disk with its
  stored digest retained → presentation refused with
  `record_chain_verification_failed`, the tampered file
  byte-identical afterwards, no effect written. The record
  truncated to empty → refused by terminal binding
  (`terminal_mismatch`), the emptied file left exactly empty.
- Divergence: a hand-made applied-but-effect-missing state →
  `InsertionDivergence`, nothing written.

**Countercheck.** In a scratch copy with the receiver's
recognition neutralised (the recorded-state lookup and the
effect read in `present()` bypassed, so every presentation is
treated as fresh), exactly 9 of the 26 tests fail — both
re-presentation cases, both payload-binding cases, the
divergence case, both interruption-completion cases, and both
restart-recognition cases — and the other 17 pass. The
assertions bite on precisely the recognition mechanism; the
cases that do not depend on recognition (pure construction,
fresh application, partial insertion, record discipline,
no-false-refusal) are unaffected, as they should be.

## Fixture judgements, marked as such

- THE CRASH HOOK IS A TEST FIXTURE. A receiver may be built
  with a hook invoked at the named points of the apply
  sequence (`mid_effect`, `after_effect`, `after_applied`);
  the tests raise `SimulatedCrash` at one chosen point to
  place the durable state in exactly the window K4 specifies,
  then discard the receiver. It simulates the failure modes;
  it is not part of the mechanism, and a receiver built
  without it never raises `SimulatedCrash`.
- THE EFFECT STORE IS A TEST-FIXTURE-CLASS STAND-IN for the
  insertion target (the pilot's ledger), in the same fixture
  class as Stage 3's caller-supplied lane: the properties
  under test are recognition, exactly-once application and
  recorded consumption, not any real ledger's semantics. The
  payload spec handed to `build_inputs` is likewise
  caller-supplied data, as Stage 3's draft configuration was.
- No other fixture judgements were needed: identity,
  consumption and the failure modes come entire from K4/G3
  and DR-01.

## Counts

Stage 5: 26/26 (operations 9, insertion 10, recovery 7).
Regressions: Stage 1, 68/68; Stage 2, 27/27; Stage 3, 38/38;
Stage 4, 36/36. `stage1/`, `stage2/`, `stage3/` and `stage4/`
unmodified — Stage 5 imports Stage 1's record and Stage 3's
`verify_record_current` as they stand.

## Register effect — DR-01

What this stage's evidence establishes, within the harness:
the DR-01 mechanism is answered at both of its boundaries.
At construction: input construction is pure and operation
identity is a canonical function of (run, step, slot), so a
retry's reconstruction yields the consumed operation itself —
it cannot be made to appear new (demonstrated, including
after consumption). At insertion: consumption is recorded
state on a durable record, the receiver recognises a
re-presentation from the durable artefacts alone, and that
recognition is demonstrated across an actual process restart,
with no duplicate side effect, no false refusal, and the
K4-specified crash windows (mid-insertion; between insertion
and state recording) each closed by recognition rather than
re-application. DR-01 is therefore advanced ON DEMONSTRATION
within the harness scope, subject to the examiner's Gate 1
determination.

What it does not establish: the historical pilot code
(`pilot_driver.py` / `pilot_tools.py`) is untouched and
unre-run — this is a mechanism demonstration against the
register's identity requirement, not a repair of the battery
harness or a re-run of attempt 3; no live insertion target is
exercised (the effect store is a fixture, above); and
concurrent presenters of one operation are outside the
specified cases (the programme's single-writer discipline is
assumed, as in every earlier stage).
