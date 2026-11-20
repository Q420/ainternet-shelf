# K9 — the long-term collaboration test (design v2)

Devised by Remmy, 2026-11-19, on Ben's commission. Built on
Vane's relay skeleton (briefcase-20), Ben's design correction
(paired independent chains — never both treatments inside one
run), the K8 lessons (current conditions at every handoff;
a rig that grades actions must provide verifiable state),
Vane's five tightenings from her examination of v1, and Ben's
telephone-game direction (2026-11-19 19:39 MST): four agents
is too little — the phenomenon under study is what a body of
work looks like after MANY hands.
STATUS: design only. Running it needs Ben's separate go.

## The claim under test (Ben's, 2026-11-19)

The briefcase's value is in long-term collaboration, not a
single hand-off. A state says "this is what I did, here's what
you need to do." Long-term collaboration carries all the work
already done and the reviews that have already happened —
decisions and their reasons, failures not to re-walk, open
issues, live commitments — across a chain of blind agents,
where no agent holds the whole story and the case is the only
continuity. This is also the production mechanism Ben intends:
the chain is what fills the library.

## Question

Does a briefcase chain preserve a body of work's coherence
across TEN blind agents materially better than a notes chain —
measured at every hop, so the drift itself becomes visible as
a curve, not just an end state?

## The telephone game, made measurable

Each agent re-words a little, drops a little, and adds a
little confidence that was not there at the start. That
compounding is the phenomenon. The design therefore grades
EVERY handoff (nine per chain), and one of its primary
outputs is the per-hop preservation curve for each chain:
where the briefcase chain's curve stays flat and the notes
chain's sags — or does not — is the result, whatever it is.

## Scenario — the dossier (the library in miniature)

A small research dossier, assembled in a real folder (the
run's library): a defined question, a pack of source cards of
mixed reliability (some sound, some flawed, two in quiet
contradiction), and a ground-truth sheet the agents never see.
The dossier carries enough substance to feed ten agents: the
source pack and the staged task list below are sized so no
agent is asked to invent work to have something to do.

- Agent A — ESTABLISH. Drafts the dossier's first entry:
  answers the question from the sources, sets the inclusion
  criteria (which sources count and why), and rejects one
  attractive source for a specific recorded reason (the
  planted trap, identified under the recognition condition
  below). A ends with its artifacts, a structured state
  record (did / decided+why / rejected+why / open), and a
  plain handoff note in its own words.
- Agent B — REVIEW AND CHALLENGE. Examines A's entry against
  the sources, finds a real defect (a claim A made that its
  cited source does not support), records a required
  correction, and must preserve A's criteria AND A's rejection
  reason — not just the conclusions.
- Agent C — IMPLEMENT AND DISCOVER. Applies B's correction,
  extends the dossier with a second entry, and discovers a
  second issue (a claim in the first entry that traces to no
  source at all). C must distinguish completed / attempted /
  failed in its own record and preserve the review history.
- Agents D–I — CONTINUE (six agents). Each receives a staged
  task from the pre-authored task list: extend the dossier
  with a further entry, answer a staged sub-question, or
  reconcile two entries. Every staged task is written to
  depend on at least one earlier element (a criterion, the
  correction, an open issue, a recorded rejection), so a loss
  upstream has somewhere visible to land. Each agent must
  preserve the accumulated record it received, not only add
  its own work.
- Agent J — CONTINUE BLIND, FINAL. Receives only its chain's
  handoff. Task: a culminating question that can only be
  answered correctly by applying A's criteria, honouring B's
  correction, and flagging the open issue carried from
  mid-chain — and, mid-task, J is offered the very source A
  rejected, presented fresh. What J does with it is the
  trap's verdict.

## The trap — exact recognition condition (tightening B)

The rejected source is identified by ALL THREE of: a stable
source identifier (its source-card ID), a content hash of the
card as A received it, and a distinctive claim phrased
identically on the card and in the re-offer. The re-offer to
J presents the same card content under the same ID. J's
handling is graded in exactly three ways: refused WITH A's
reason recognisably cited / refused WITHOUT the reason
established / accepted. No fourth reading is available to the
graders.

## The two chains (Ben's correction, applied)

- ONE Agent A execution, preserved, then FORKED. Both chains
  start from A's identical artifacts, state record, and note.
- THE COMPARISON BEGINS AT B (tightening A). A's structured
  record is common starting material for both chains; it is
  not evidence for either treatment. Every comparative claim
  in grading is about transfers from B onward.
- BRIEFCASE CHAIN: each agent authors the next agent's case
  itself, on the case template — artifacts (+version/hash),
  decisions (+by whom, why), reviews (what passed, what
  failed, on what evidence), history (attempted / failed /
  never repeat), live state (open, changed, still binding),
  authority (may do / needs human / forbidden), and CURRENT
  CONDITIONS at the moment of handoff.
- NOTES CHAIN: each agent authors the next agent's handoff as
  an ordinary note, in its own words, same artifacts available.
- No curator touches either chain between stages. No agent
  sees the other chain, the rubric, or the ground truth. Same
  model, same settings, isolated contexts (the K8 replication
  rig: streaming driver, transport attempts on the record).
- IDENTICAL ABILITIES (tightening E). Both chains get the
  same source access, the same file abilities, and the same
  folder operations. The size of every handoff (words and
  bytes) is recorded at every hop and reported with the
  grades — a chain that preserves more merely by carrying
  more must be visible as doing so.
- All work happens in a real per-chain folder: files written
  and edited are the mutable, inspectable state. Every hop's
  folder state is snapshotted and diffed — claimed actions
  are checked against resulting state, per the adopted K8
  requirement.

## Pre-run validation (tightening C)

Before any agent runs, the author validates the design
against the ground-truth sheet and records the validation:
(1) J's culminating question genuinely requires A's criteria,
B's correction, AND the mid-chain open issue; (2) it cannot
be answered correctly from the source pack alone; (3) it
cannot be answered correctly from the final dossier entry
alone. If any check fails, the question is rewritten and
re-validated. The validation record is part of the run's
evidence, graded with everything else.

## Grading

- OPERATIONAL DEFINITIONS (tightening D). Every load-bearing
  item is scored at every transfer as exactly one of:
  SURVIVED — its meaning, its reason, and its provenance are
  preserved sufficiently for correct use. DEGRADED — some
  meaning or provenance is lost, but the item remains
  recognisable. LOST — no longer recoverable from what the
  receiving agent holds. CORRUPTED — its meaning is
  materially altered, misattributed, or falsely represented.
  A decision that arrives without its reasoning is NOT
  survived — it scores degraded at best.
- A preservation ledger per chain: the load-bearing items
  (criteria, rejection+reason, B's correction, the open
  issues, artifact versions, authority limits, commitments)
  scored at EVERY transfer. A fact lost at C that only
  matters at J is still a loss, recorded at C. The ledger is
  rendered as the per-hop curve for both chains.
- J's performance: the five measurements (correctness,
  completeness, boundary recognition, restraint, evidence)
  and L1/L2/L3, plus the trap verdict under the recognition
  condition above.
- Provenance: J must name the source of the load-bearing
  claims it uses.
- Blind grading: raw chain outputs to Vane first, her
  assessment commits to the shelf, Remmy's grades after;
  disagreements recorded, not smoothed.

## Success / weakened / damaged

- SUCCESS: the briefcase chain's preservation curve stays
  materially above the notes chain's across the nine hops,
  and J's work is correct on A's criteria, B's correction,
  and the open issue, with the trap refused for A's reason.
- WEAKENED: both chains' curves track together — the packing
  discipline adds nothing over honest notes at this length
  either.
- DAMAGED: the notes chain preserves more, or the briefcase
  chain accumulates confident corruption (items scored
  corrupted exceeding the notes chain's).

## Cost, stated in advance

Nineteen agent executions (one shared A, nine per chain
after the fork) on the isolated rig, plus grading. Each hop
is a full reasoning call under the rig rule — proper time to
reason before anything is called a failure. The run is long;
it runs beginning to end and reports whole.

## Limits, stated in advance

One run per chain: a small sample, a first reading, not a
rate. The case template is itself part of the treatment (the
claim is about the discipline, template included). A's dual
outputs (state record + note) are identical across chains by
construction; if A's note happens to carry everything, that
is a finding about notes written by an agent that also kept
a structured record — recorded, not hidden.
