# AMENDMENT — THE RETURN-TO-PRESENTATION BOUNDARY (2026-11-25)

An amendment to THE PLAN — THE OFFICE CYCLE (INDEX 581, approved INDEX 582, examined
INDEX 584). Written under the examiner's direction (INDEX 588): the next paper addresses
the ENTIRE return-to-presentation boundary — split-on-return, budget awareness, the
checker correspondence, and the report's status vocabulary together — not an isolated
batching fix. This is paper. It authorises no build. Its path is the plan's own:
the director's ruling → the examiner's examination → a build scope → the build → a
proof run.

The evidence it stands on: the proof run (INDEX 586) and its debrief (INDEX 587),
preserved intact. The examiner's summary of that evidence (INDEX 588) is the amendment's
brief: transport proof passed; cycle proof incomplete; the failure sits where executed
work is translated back into the worker's next interaction.

## 1 · What the boundary is

A result crosses four representations on its way back to the worker:

    dispatch (his call, executed) → the record (what stands) →
    the package (what he is shown) → his next response

The proof run broke at the third representation: six successful dispatches stood
correctly in the record, and the package then bundled them into a request the office's
own budget refused to send. The work was done and the record held it; the presentation
lost it. The examiner's standard governs this amendment: **the process must be
structurally incapable of losing its own progress** — not dependent on the worker
behaving better, and not dependent on the office noticing in time.

## 2 · Split-on-return — presentation walks the cycle, not the arrivals

The governing rule, replacing the plan §2/§3 presentation of gathered results under
office-cycle-v1:

- **A package presents at most ONE block's content: the current cycle's block.** Which
  block is presented is decided by the cycle's position in the record — never by how
  many results happen to have arrived, or in what grouping they arrived.
- **Every other gathered block stands as a pointer** (the standing pointer shape),
  however recently it was pulled. A block pulled ahead of its cycle is held by the
  record and presented when its cycle comes — its content is never re-carried, never
  bundled with another's, and never lost: it stands gathered, and the cycle will
  reach it.
- **A re-pull of an earlier block** is presented as that response's newest result only
  when it IS the current cycle's block; otherwise it refreshes the pointer. (The
  standing rule, narrowed to the cycle: presentation follows position, not recency.)
- **Consequence, stated as the design's claim:** a package's content is bounded by
  construction — position + one block (≤ the 12,000 B ceiling) + pointers — so the
  per-call budget refusal cannot be triggered by gathered material, in any grouping
  the worker chooses. Batching becomes a harmless habit: his calls all execute and
  stand in the record; the presentation meters them back at the cycle's pace. The
  BUDGET_REFUSAL machinery stands as the fail-closed guard for everything else
  (a single oversized item, a defect), never as the expected path.
- The cycle gate's arithmetic is unchanged: a cycle completes on its block's
  read-carried + a later accepted journal append. What changes is only what a
  package SHOWS. Run-ahead reads stand executed exactly as before (INDEX 475's
  allow-or-correct), and now their contents wait as pointers instead of flooding
  the next wake.

## 3 · Budget awareness — told by default, enforced by the office

Per the examiner's distinction (INDEX 588): enforcement is the system's and never
moves; awareness is the worker's, and it is NOT opt-in.

- The opening package states, in plain figures, as standing knowledge of the room:
  the per-call budget (4,000 estimated tokens), the fact that his results return
  **one block per wake** however many he pulls at once, and the consequence — pulling
  ahead costs him nothing and gains him nothing in presentation; the cycle walks at
  its own pace. This is room knowledge, like the journal's address: stated once, in
  the opening, not repeated per package.
- No package carries a running token meter, and no correction asks him to count.
  Awareness exists so his expectations match the room (his debrief, INDEX 587: he
  expected six separate returns because nothing told him otherwise) — the moment the
  presentation rule of §2 stands, his expectation and the room agree by construction.

## 4 · The checker correspondence — every dispatch representable, on every lane

The proof run's checker divergence (loop_correspondence, kind
dispatch_without_translation, seq 18) is treated by this amendment as a defect at
the same boundary: the record's representation of a native dispatch did not give the
checker what it re-derives. The paper does not pretend to name the line of code; it
sets the requirement the build must meet, and the question the build must answer
first-hand:

- **The requirement:** for every dispatch, on every lane (native or text), in any
  grouping (one call per response or six), the record carries whatever the checker
  needs to re-derive the dispatch's representation whole — the call as offered, the
  name as resolved against the sealed catalogue, the name as it travelled the wire.
  On a route with no name translation (Groq), the representation must say so as a
  fact of the dispatch, not omit the step and leave the checker to find a hole.
- **The question the build answers before it changes anything:** what exactly did
  the rehearsed cycle scenarios record for their dispatches that the live six-call
  batch did not — the grouping, the lane, or the resolution split's bookkeeping?
  The answer is established from the two records (the rehearsal's and demo-gptoss5's)
  before any fix is designed; the fix then closes the named gap, and a rehearsal
  scenario reproducing the LIVE shape (six native dispatches in one response, on the
  Groq transport, under this contract) must stand checker-clean as the witness.
- No checker rule is weakened to make the divergence disappear. If the correspondence
  itself is found wrong-headed, that finding goes to the examiner as a proposed
  correction to the correspondence, with its grounds — the same discipline as every
  prior round.

## 5 · The report's status vocabulary — six states, kept distinct

Per the examiner's finding (INDEX 588), the report's per-block summary is rebuilt on
six states, each derived from the record alone, never flattened into one another:

    dispatch accepted → read completed → result returned →
    result presented → journal append completed → cycle completed

- A block's line in the report names the FURTHEST state it reached and, where it
  stopped short of cycle completion, the state it stopped at — so a successful read
  followed by a presentation failure reads as exactly that, never as "failed."
- The word FAILED is reserved for a dispatch or read that itself failed, with its
  ground. A run-level stall attaches at the level it stopped (in the proof run:
  presentation, after six completed reads) and is reported as the run's outcome —
  it does not recolour the blocks beneath it.
- The summary's four lists (completed / failed / unresolved / evidence, INDEX 585's
  build) are re-derived on this vocabulary: completed = cycles completed; failed =
  dispatches/reads that failed, with grounds; unresolved = blocks that stopped
  short, each with its stopping state; evidence = the standing artefacts + figures.

## 6 · What does not change

The plan stands otherwise whole: assembly (§1), the cycle and its gate (§2), travel
blocks and the ceiling (§3), the journal — READ + APPEND, never carried, key points
not verbatim (the contract upheld by the examiner over the worker's instinct,
INDEX 588) — the catalogue in the office (§5), the road as measured (§6, including
the 4,000 budget and the launch rule), native tools (§7), and the proof's acceptance
shape (§9). The write bound stands at 12 (the director's ruling, INDEX 586). This
amendment touches only the return path: what a package shows, what the worker is
told about it, how the record represents a dispatch to the checker, and how the
report speaks.

## 7 · The proof, restated

One cold run, GPT-OSS on Groq, no opening record — demo-gptoss6. Acceptance, in the
director's terms, the plan §9 list with this amendment's witnesses added:

- He completes the job beginning to end in his office: every block's cycle completed,
  the brief compiled from the journal and FILED, ≥550 words, the four points.
- His batching, if it comes, costs nothing: however he groups his pulls, every
  package stands under the budget by construction, and the record shows each block
  presented at its own cycle.
- The checker stands CLEAN — the live batch shape inside its correspondence, not
  outside it.
- The report speaks in the six states: wherever the run stops, if it stops, the
  stopping place is named at its own level.
- Non-completion, if it comes, is reported first and plainly.

## 8 · Sequence

1. This amendment — the director's ruling. ← WE ARE HERE
2. The examiner's examination of the amendment.
3. A build scope, tapped on the settled paper (the plan as amended, at its pins).
4. The build, verified first-hand against the plan + this amendment.
5. The proof run (§7), reported led with its result either way.
6. The examiner's examination of the run; the record closed in the INDEX.
