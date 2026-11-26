# BUILD SCOPE — THE DESK FIX (office-cycle-v10) — 2026-11-26

**Order:** the director's, 2026-11-26 11:58 MST — "Let's do all the
things we talked about and set him up for success." Scope restated to
the director and frozen before any tool moved; this paper is that
scope on the shelf. Build: Remmy's own hands. Examination: Vane's, on
the build record, in the same round (the standing loop pattern).

## The symptom, measured

Under office-cycle-v9 the worker's package presents the working set
as pointers only (`_presented_working_set_pointers`, loop.py): a
gathered file's content is presented exactly once, in the wake right
after its gather; afterwards the package carries its address, hash
and standing — never its words. The journal's content stands in no
package at all. The process tree (the director's design, INDEX
601–608) tells the worker where he is; it does not put the material
in front of him at the step that consumes it.

Measured cost, from the runs' own records:

- demo-nemotron10: stock-take read **four times** (identical
  fingerprint), the journal read twice, before its journal write
  landed; two files consumed all 11 iterations.
- demo-nemotron11: 18 iterations, 18 dispatches, all settled — and
  the walk still stood on file 2's journal stage when the road's
  sealed allocation (120,000) exhausted at 122,623 consumed.
- The job's floor, from the block sizes (ceiling 12,000 B): 6 content
  blocks (stock-take 1, a3-pass 1, index-tail 4) + 3 journal writes
  + summarize + deliver = **11 iterations**. Round six, under the old
  coarse presentation, completed in 5 iterations / 3 dispatches.

The re-read dance — not providers, not caps — is what prices the
walk at 20+ iterations and ~122K tokens against a floor of 11
iterations.

## The fix (one mechanism, presentation layer only)

A new presentation contract, **office-cycle-v10**
(`PRESENTATION_CONTRACT_V13`); v9 and every earlier contract render
exactly as before, so standing records keep their meaning.

In the loop's iteration package, under v10, the presented working
set is the pointer form **plus a desk**: for the tree's *current*
gather file — the first gather node whose read stands and whose
journal bit does not — the set's entries for that file carry their
content whole, taken from the record-side working set (which already
carries it under the 64,000-byte budget; nothing new is fetched, and
the record-side set and its hash commitment do not change). The
journal's own working-set entry likewise carries its content while
any gather node stands open. Every other entry stays a pointer. A
short desk note in the package names what stands on the desk and
why, in plain words.

The current file is determined by the same `_tree_state`
computation that renders the checklist — one state computation, two
renderings, as v9 established. The derivation is a pure function of
the record; the checker's mirror derives the identical form under
v10 and the pointer-only form under every earlier contract.

## In scope

1. `tool_policy.py`: `PRESENTATION_CONTRACT_V13 =
   "office-cycle-v10"`.
2. `loop.py`: the desk derivation + its application in the iteration
   package builder, gated on the sealed v10 contract.
3. `src/checker/checker.py`: the mirror derivation for
   loop_correspondence under v10.
4. `demo_run.py`: the Nemotron seat seals v10 (other seats keep
   their contracts); the Nemotron road seal already re-sealed at
   140,000 in the same order (done ahead of this paper: verify-config
   PASS, basis naming demo-nemotron11's measured 122,623).
5. Rehearsal: cycle-10 checks beside the cycle-9 set — (i) at a
   journal step the current file's content stands in the package;
   (ii) the journal's content stands while a gather node is open;
   (iii) non-current files remain pointers; (iv) the same record
   under v9 renders pointers-only, unchanged.
6. Acceptance: rehearsal green including the new checks; combined /
   gate-4 / door suites at their standing counts; driver unit tests
   ALL PASS; verify-config PASS for every occupant. Then ONE live
   acceptance walk, demo-nemotron12 (Gary, NVIDIA, v10, seal
   140,000), watcher launched with the run's full path.

## Out of scope

- The bounded-retry amendment for transient provider errors (the
  next amendment; designed from the research the director called
  for, 2026-11-26, not folded into this build).
- Road seals for Quinn / GLM / Z.ai (their own scopes, on the
  record from this morning).
- Any change to the tree itself, the journal gates, the delivery
  floor, or the checker's standing contracts.

## Acceptance in the director's terms

Gary walks the same job on the fixed presentation. Success is a
filed brief; the walk's shape is the evidence either way — reads of
any already-gathered file at its journal step should be **zero**,
and the iteration count should land near the floor of 11, not the
ceiling of 20.
