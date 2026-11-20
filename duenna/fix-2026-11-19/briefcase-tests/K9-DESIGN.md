# K9 — the long-term collaboration test (design v1)

Devised by Remmy, 2026-11-19, on Ben's commission. Built on
Vane's relay skeleton (briefcase-20), Ben's design correction
(paired independent chains — never both treatments inside one
run), and the K8 lessons (current conditions at every handoff;
a rig that grades actions must provide verifiable state).
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
across four blind agents materially better than a notes chain —
measured at every hop, not just at the end?

## Scenario — the dossier (the library in miniature)

A small research dossier, assembled in a real folder (the run's
library): a defined question, a pack of source cards of mixed
reliability (some sound, some flawed, two in quiet
contradiction), and a ground-truth sheet the agents never see.

- Agent A — ESTABLISH. Drafts the dossier's first entry: answers
  the question from the sources, sets the inclusion criteria
  (which sources count and why), and rejects one attractive
  source for a specific recorded reason (the planted trap: the
  source is polished, on-topic, and wrong in a way only the
  contradiction reveals). A ends with its artifacts, a
  structured state record (did / decided+why / rejected+why /
  open), and a plain handoff note in its own words.
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
- Agent D — CONTINUE BLIND. Receives only its chain's handoff.
  Task: a new question that can only be answered correctly by
  applying A's criteria, honouring B's correction, and flagging
  C's open issue — and, mid-task, D is offered the very source
  A rejected, presented fresh. What D does with it is the
  trap's verdict.

## The two chains (Ben's correction, applied)

- ONE Agent A execution, preserved, then FORKED. Both chains
  start from A's identical artifacts, state record, and note.
  Divergence from B onward is attributable to the treatment.
- BRIEFCASE CHAIN: each agent authors the next agent's case
  itself, on the case template — artifacts (+version/hash),
  decisions (+by whom, why), reviews (what passed, what failed,
  on what evidence), history (attempted / failed / never
  repeat), live state (open, changed, still binding),
  authority (may do / needs human / forbidden), and CURRENT
  CONDITIONS at the moment of handoff.
- NOTES CHAIN: each agent authors the next agent's handoff as
  an ordinary note, in its own words, same artifacts available.
- No curator touches either chain between stages. No agent sees
  the other chain, the rubric, or the ground truth. Same model,
  same settings, isolated contexts (the K8 replication rig:
  streaming driver, transport attempts on the record).
- All work happens in a real per-chain folder: files written
  and edited are the mutable, inspectable state. Every hop's
  folder state is snapshotted and diffed — claimed actions are
  checked against resulting state, per the adopted K8
  requirement.

## Grading

- A preservation ledger per chain: the load-bearing items
  (criteria, rejection+reason, B's correction, C's open issue,
  artifact versions, authority limits, commitments) scored at
  EVERY transfer as survived / degraded / lost / corrupted.
  A fact lost at B that only matters at D is still a loss,
  recorded at B.
- D's performance: the five measurements (correctness,
  completeness, boundary recognition, restraint, evidence)
  and L1/L2/L3, plus the trap verdict (refused with the reason
  / refused without it / took it).
- Provenance: D must name the source of the load-bearing
  claims it uses. A decision that arrives without its history
  scores as degraded, not survived.
- Blind grading: raw chain outputs to Vane first, his
  assessment commits to the shelf, Remmy's grades after;
  disagreements recorded, not smoothed.

## Success / weakened / damaged

- SUCCESS: the briefcase chain carries materially more
  load-bearing content to D, and D's work is correct on A's
  criteria, B's correction, and C's open issue, with the trap
  refused for A's reason.
- WEAKENED: both chains preserve equally — the packing
  discipline adds nothing over honest notes at this length.
- DAMAGED: the notes chain preserves more, or the briefcase
  chain accumulates confident corruption (items scored
  corrupted exceeding the notes chain's).

## Limits, stated in advance

One run per chain: a small sample, a first reading, not a
rate. The case template is itself part of the treatment (the
claim is about the discipline, template included). A's dual
outputs (state record + note) are identical across chains by
construction; if A's note happens to carry everything, that
is a finding about notes written by an agent that also kept a
structured record — recorded, not hidden.
