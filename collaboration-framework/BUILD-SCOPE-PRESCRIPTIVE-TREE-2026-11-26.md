# BUILD SCOPE — THE PRESCRIPTIVE TREE + BOUNDED RETRY (office-cycle-v11) — 2026-11-26

**Order:** the director's design, stated 2026-11-26 12:32 MST —
"every step in the process tree should be telling him what to do at
that step so there's no way that it should vary how many steps to
complete the task because it's all laid out for him in the process
tree: read append read append draft your brief" — and his go,
"Proceed," 2026-11-26 12:33 MST, on Remmy's restatement of this
scope in chat. Build: Remmy's own hands, after the examiner's
examination of this scope. No build is authorised by this paper.

## The symptom, measured

The process tree (v9) and the desk (v10) tell the worker where he
is and put the material in front of him at the step that consumes
it. They ADVISE. The doorway still honours any granted act at any
step, so the worker's path through the tree varies — and the
variance is priced in steps and in tokens.

- demo-nemotron13 (v10, desk corrected, seal 140,000): 12
  iterations and 122,537 counted tokens consumed to finish ONE
  file and stand at the second file's journal step. Seven reads
  served two files, including re-reads of a3-pass that stopped
  only when the read grant itself closed them (the tree's own
  workaround note records it). The job's floor is 11 iterations;
  the clean full walk (demo-nemotron9) cost 122,575 tokens TOTAL.
  Gary spent a whole walk's budget reaching file two.
- The same walk under v9 (demo-nemotron11) took 18 iterations.
  Round six, under the old coarse presentation, took 5. The
  sequence is fixed — read, append, read, append, read, append,
  draft, deliver — but nothing binds the worker to it.

A second, distinct symptom rides alongside: a run dies whole on
ONE transient provider failure. demo-nemotron10 (provider failure,
iteration 11), demo-gemini4 (HTTP 503, fourth call),
demo-nemotron13 (provider failure at iteration 12 — the call
returned at 177 seconds of a 300-second allowance; the timeout did
not cut it; the provider failed inside its window). The resilience
research (2026-11-26, `research_notes/
agent-run-resilience-free-tiers-20261126-1858`) establishes the
field's pattern: retry the call, not the job, at exactly one
layer, bounded, with backoff.

## The change

### Part A — the tree prescribes

Under a new presentation contract (office-cycle-v11), the process
tree's current node carries the step's prescribed act, and the
doorway enforces it:

- Each tree node names its act class. A gather node: read the
  current file (whole, or its next block by ranges — the worker
  still chooses the shape; the desk serves either). A journal
  node: write the journal bit for the file on the desk. The
  summarize node: the contribute response. The deliver node is
  terminal.
- A dispatch that is not the current node's prescribed act is
  refused BEFORE execution, by the doorway, with a speaking
  refusal that names the current step and its prescribed act
  ("your step is 2.2, journal sources/a3-pass.md; the act is the
  journal write") — the v9 speaking-refusal machinery, carrying
  the prescription.
- The package's next_step line and the tree text state the same
  prescription, so what he is told and what is enforced are one
  fact from the one computation.
- Reading ahead is refused like any off-step act: the sequence
  is the prescription. This is a deliberate narrowing of the
  worker's freedom inside the job, traded for a fixed walk —
  named here so the examiner and the director rule it with eyes
  open.

### Part B — a dropped call is re-asked

At the loop's provider-call site — exactly one layer; the
connector helpers' own retries stay as they are and are counted
in the record's evidence either way:

- Retryable: no usable response — transport timeout, connection
  drop, HTTP 429 or 5xx. A captured, well-formed model response
  is NEVER retried; a decline is an answer.
- Bound: 3 attempts per step (the original call plus 2 retries),
  exponential backoff with jitter between attempts, honouring a
  provider's Retry-After when one is sent.
- Attempts are not iterations: a retry re-asks the SAME step's
  call with the SAME package; the 20-step ceiling counts steps,
  not attempts.
- Every attempt counts on the road (each is a rendered request)
  and stands in the record as its own event, with its ground and
  the wait that followed it. The record stays the checkpoint.

## The layer touched

The doorway's dispatch decision and the cycle package, under the
tree-bearing contract family only; the loop's provider-call site
for Part B. Sealed as office-cycle-v11. v9 and v10 records,
contracts and runs stand untouched.

## What this does NOT touch

The grant model (the shared read pool stays shared — the
examiner's caution on INDEX 608 stands; prescription makes the
pool's spend predictable instead of renegotiating it). The road,
its seals, the 20-step ceiling, the working-set budget, the task,
the sources, the delivery floor. The checker's derivation of
cycle packages (deferred under the standing strip ruling).
Text-mode refusal delivery (a known pre-existing limitation,
unchanged by this scope).

## What stays wrong if it works perfectly

A provider outage longer than the retry window still ends a run
— later, and with the attempts on the record. The model's
judgement inside a step (what its summary says) is untouched.
The brief's quality is not this scope's claim. Prescription
fixes the walk's SHAPE; it does not make any single step cheaper
than the desk already made it.

## Decisions named for the examiner

1. Attempts ≠ iterations (Part B) — the ceiling counts steps.
2. At a journal node, journal READS are also off-step (the desk
   carries the standing journal; a read is variance, not need).
3. Reading ahead is refused, not merely unadvised.
4. The retry bound (3 attempts) and the retryable set
   (timeout / drop / 429 / 5xx only).
5. Within a gather node, whole-read and range-read are both the
   prescribed act — the worker keeps the shape choice.

## Acceptance

Stage 1 (rehearsal, scripted stand-ins, no live call): the
standing suites stay green untouched; new v11 scenarios witness —
(a) the prescribed walk completes at the floor count; (b) an
off-step dispatch (a re-read at a journal node; a write at a
gather node; a read-ahead) is refused before execution, the
refusal naming the step and its act; (c) a call dropped once at
a step is re-asked and the run completes, with both attempts on
the record; (d) a call dropped at every attempt ends the run
with the attempts recorded, ground provider failure; (e) no v11
machinery in v9/v10 packages.

Stage 2 (live): one Gary run on v11 at the standing seals.
Success is a filed brief; the walk's shape — iterations at or
near the floor of 11, zero off-step dispatches executed — is the
evidence either way.

**Trade flag:** this scope displaces the filing batch (INDEX 610
and the older owed entries) and the AIvory S4/S5 papers again.
The director accepted the same displacement for the desk build;
it is named again here because it compounds.

**Status: scope filed for the examiner's examination. Build
waits on her ruling.**
