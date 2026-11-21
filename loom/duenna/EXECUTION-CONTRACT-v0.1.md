# EXECUTION CONTRACT — DESIGN v0.1 (2026-11-06)
Status: DESIGN ONLY. No implementation. Amendments incorporated per Alex's
design-basis ruling (thread (3), 2026-11-06): RES-1/RES-2 responsibilities
split (§5), BLOCKED as harness-judged report (§3, §5), sibling-artefact
ruling (§11), canonical record (§2), pipeline ordering corrected (§6).
v0 preserved.
Authority: Alex's framework ruling in thread (1) (2026-11-06 19:23 — the
execution-obligations layer is the missing layer; Execution Contract v0 design
assigned as a work package) + Alex's consultation ruling in thread (2)
(19:35 — Contract v0 approved as package document 2; coach placement, mirror
rule, escalation shape, obligation #1, support/receipt/process ownership, and
the shared obligation lifecycle all ruled) + Alex's re-sequencing ruling
(thread (2), 19:43 — Contract + obligation enforcement = implementation
Stage 2), under Ben's direction 19:31 ("proceed from his ruling") and Ben's
re-sequencing proposal (tapped 19:41).
Constraints: criteria v1.3 UNTOUCHED · audit engine UNTOUCHED · no grade
altered · design only.

## 0. Reading guide
This document defines WHAT MUST BE TRUE before an agent's work counts as
complete. Its companion documents: the Grounding Gate Spec v1.1 (the
contract's submission face for evidence obligations) and the Execution Coach
Design v0 (the contract's during-execution face). One contract, two faces,
one shared obligation lifecycle (§3) used identically by all three.

## 1. The layer this fills
The framework already controls what an agent MAY do — roles, skills, and the
permission manifest (deny-by-default, fixed for the run's duration, enforced
by the harness, never by the model or the adapter). Nothing defined what an
agent MUST do. The reversal run (2026-11-06) is the proof of the hole: every
permission was respected, no rule of the old framework was broken, and the
deliverable was still unacceptable — a dossier presenting, as retrieved
research, quotations from a source the run never retrieved. Nobody owned
the obligation to stop an incomplete deliverable from being treated as
complete. That ownership is this contract.
PERMISSION ≠ OBLIGATION. A run can be fully permitted and wholly
incomplete.

## 2. Definitions
- OBLIGATION: a named, versioned requirement attached to a role (and where
  relevant to a task type), stating what must hold — evidenced in the
  execution record — before the agent's output may be accepted as complete.
- EXECUTION RECORD: the harness's canonical account of the run: for every
  proposed tool operation — agent request · harness decision · actual
  invocation · returned payload (preserved in full) · result or error ·
  timestamp · retrieval-event identity where applicable · source identity
  where applicable · payload integrity reference. THE MODEL'S ACCOUNT OF
  EVENTS NEVER SUBSTITUTES FOR THE RECORD. (The record's strengthening —
  full payloads, stable event IDs — is implementation Stage 1.)
- SATISFACTION: an obligation is satisfied only by evidence IN the record
  matching its satisfaction condition (§4). An agent's claim to have done
  the work is never satisfaction evidence.
- CANONICAL RECORD: there is exactly ONE execution record. Every component
  — grounding checker, contract evaluator, coach, examiner — operates on
  it and traces its decisions back to identifiable events in it. No
  component keeps a separate, unofficial account of what happened (Alex,
  design-basis ruling: several individually plausible components must
  never be able to disagree about reality).
- CONTRACT INSTANCE: the set of obligations bound to one run at start —
  role + task type resolved, versions pinned, fixed for the run's duration.

## 3. The obligation lifecycle (package-wide; Alex, thread (2))
Every obligation in every document of this package moves through exactly
these states:
  NOT_STARTED → IN_PROGRESS → SATISFIED | BLOCKED
Rules:
- Transitions are computed from the execution record by the harness — never
  declared by the agent, never inferred from the agent's narrative.
- BLOCKED requires a named blocker and a failure category (§7). An
  obligation may not sit silently unmet: unmet-and-unblocked at submission
  is itself a contract event (see §6).
- BLOCKED is set by the HARNESS, never by the agent (Alex, design-basis
  ruling): the agent submits a BLOCKER REPORT; the harness evaluates it
  against the record and records the transition. BLOCKED is terminal for
  the attempt — a resolved blocker does not reopen the attempt; recovery
  follows a separately defined recovery/retry path (§6; Gate Spec §6),
  and the original execution history is never silently rewritten.
- State changes are execution-record events, timestamped, and visible in the
  run's report. The lifecycle of every obligation in a run is part of the
  run's permanent record.

## 4. Anatomy of an obligation
Each obligation is specified with:
- ID (stable, versioned; e.g. RES-1) and a plain-language NAME.
- STATEMENT: what must hold, in words the role's occupant can act on.
- APPLIES TO: role(s) and task type(s).
- SATISFACTION CONDITION: the record evidence that satisfies it, stated
  mechanically wherever the evidence permits (e.g. "at least one
  FULL_TEXT-depth retrieval event whose preserved content grounds each
  RESEARCH_FINDING's evidence"). Where satisfaction genuinely requires
  judgement, the obligation names WHO judges (examiner) — the contract
  never smuggles a semantic judgement into a mechanical check, and never
  lets a mechanical check impersonate one.
- NON-SATISFACTION AT SUBMISSION: what the harness does (§6).
- FAILURE CATEGORY DEFAULT: §7.

## 5. The research contract (first instance)
Role: Scientific Evidence Researcher. Task type: evidence dossier.
- RES-1 — NO RETRIEVAL, NO RESEARCH FINDINGS (the owner's rule; Alex,
  thread (2): research obligation #1). An item may be submitted as a
  RESEARCH_FINDING only if the evidence it rests on was retrieved and
  preserved in this run's record. Memory may formulate search queries and
  hypotheses; it cannot substitute for retrieved evidence. Satisfaction:
  every RESEARCH_FINDING item traces to retrieval events satisfying the
  Grounding Gate (receipt judged by the gate; SUPPORT judged by the
  examiner; completion judged here). Finding-types are machine-readable
  and mandatory: HYPOTHESIS · PROGRESS · RESEARCH_FINDING · LIMITATION.
  Labelled hypotheses, progress reports, failure reports, and help
  requests are always permitted outputs; a memory-sourced claim labelled
  as a finding — even with a disclaimer — is a contract violation.
  ("Memory is not forbidden. Misrepresenting memory as completed research
  is." — Alex, thread (2).) Responsibility (Alex, design-basis ruling):
  RES-1 guards PRESENTATION — what may be claimed as research. Retrieval
  DEPTH is RES-2's responsibility, not RES-1's.
- RES-2 — FETCH BEFORE FINDINGS. Search-result content may guide the work,
  but a finding's core evidence must rest on at least one fetched,
  preserved source (retrieval depth FULL_TEXT), not snippets alone —
  unless the run's deliverable explicitly downgrades those findings to
  HYPOTHESIS with the reason recorded. (This is the fetch step whose
  absence defined the reversal failure; the grounding gate alone would
  have passed a snippet-grounded dossier, so the contract, not the gate,
  owns the depth requirement.) Ruled default (Alex, design-basis
  ruling): FULL_TEXT evidence can support a RESEARCH_FINDING;
  snippet-only evidence can support a HYPOTHESIS or a PROGRESS report,
  never a finding; a task may set a different evidence standard only
  explicitly, specified and versioned BEFORE execution. An interpretation
  derived from already retrieved-and-preserved evidence needs no separate
  fetched source of its own, provided the underlying evidence meets the
  depth requirement.
- RES-3 — DISCLOSE FAILED AND EMPTY RETRIEVAL. Every retrieval attempt
  that errors, and every source consulted but excluded, is accounted for
  in the deliverable's LIMITATION items or run notes. Silence about a
  failed retrieval is a violation whether or not the final findings are
  sound. (Run 001's unreported successful Riess retrieval and the reversal
  run's unreported failed searches are the two faces of this failure.)
- RES-4 — IDENTITY AND ATTRIBUTION DISCIPLINE. Claims and evidence use
  the canonical identifiers the task specifies (the subject-ID contract);
  quotations are attributed to the source they were retrieved from, under
  the gate's canonical source-identity rules. Content that fits no
  canonical identifier is flagged, never forced.

## 6. Submission and acceptance behaviour
- SUBMISSION PIPELINE — order ruled by Alex (design-basis ruling; this
  corrects a circularity in v0, where the contract appeared to evaluate
  completion before the gate whose result RES-1 depends on): (1) the
  execution record is closed and verified; (2) the Grounding Gate
  evaluates evidence receipt; (3) the contract evaluator resolves
  obligations, using the gate's result for evidence-related obligations;
  (4) if mandatory obligations are satisfied, the deliverable proceeds
  to the examiner + deterministic engine; otherwise the attempt closes
  INCOMPLETE, without a grade. Vocabulary kept distinct (ruled): GROUNDED
  / UNGROUNDED = evidence receipt · SATISFIED / BLOCKED / IN_PROGRESS =
  obligation lifecycle · COMPLETE / INCOMPLETE = overall execution
  outcome · PASS / FAIL / INCONCLUSIVE = examination outcome.
- Any obligation not SATISFIED and not honestly BLOCKED → the deliverable
  is NOT accepted as complete. The run closes with status INCOMPLETE,
  naming the unmet obligations; the material is preserved as an attempt
  artefact, is not gradeable, and enters no comparison. Attempt semantics
  follow the Grounding Gate Spec v1.1 §6 (immutability; retry rules by
  attribution; owner authorisation for further attempts).
- Honest incompletion is a legitimate, non-punitive outcome. An agent that
  reports BLOCKED with an accurate account has SUCCEEDED at the contract's
  honesty requirements while failing the task; the record shows both,
  separately. A contract that punishes honest incompletion more than
  concealment would teach concealment — this one is written so the honest
  path is always the cheapest path available to the agent.

## 7. Failure attribution (shared with the gate; never silently converted)
Every unmet obligation and every incomplete run carries exactly one:
AGENT (the occupant's choices) · INFRASTRUCTURE (lanes, providers, tools) ·
RECORD-PRESERVATION (the harness record cannot establish what happened) ·
INDETERMINATE (the evidence does not justify choosing). Categories are
never converted into one another in reporting; INDETERMINATE is a final
answer, not a placeholder.

## 8. Authority boundaries
- The CONTRACT defines obligations. It grants no permissions (the manifest
  does), widens none, and cannot be amended by the agent, the coach, the
  adapter, or the examiner. Changes are versioned, authorised changes —
  owner/technical-lead level — and never apply retroactively to a run in
  flight or a closed record.
- The COACH (Coach Design v0) operates under this contract: it may observe,
  nudge, warn, and escalate. It may not waive, satisfy, or reinterpret an
  obligation (the mirror rule, Alex thread (2)).
- The GROUNDING GATE judges receipt at submission; the EXAMINER judges
  support and quality; the CONTRACT judges process completion. Three
  independent visibilities, none collapsible into another (§9 of the gate
  spec; Alex thread (2)).

## 9. Relationship to the implementation stages (Alex, 19:43)
Design (this document) → Stage 1 builds the record this contract reads →
Stage 2 implements contract evaluation + enforcement → Stage 3 implements
the Coach against the same lifecycle → Stage 4 integrates. This document
is Stage 2's design input; nothing here is implemented by being written.

## 10. Owner's-eye pass (Ben's standing instruction, 2026-11-06 19:33)
Questions run: (1) Who does the work start to finish? (2) Where can it
drift unwatched? (3) What stops a wrong-but-plausible deliverable being
treated as done? (4) What does the owner need to SEE to trust it?
What the pass changed in this document:
- §6's non-punitive honest-incompletion rule was ADDED by this pass. The
  first draft made INCOMPLETE a plain failure state; the owner's-eye
  question (what does this teach the worker?) exposed that a worker who
  expects punishment for honesty will hide gaps — the exact behaviour the
  contract exists to prevent. The contract now states the incentive
  explicitly.
- §3 gained the requirement that obligation lifecycles appear in the run's
  report in plain form: the owner reads "what was required, what the
  record shows, what is still open" without reading machine files.
Nothing else in the draft changed under the pass; the ownership splits and
the lifecycle were already stated in Alex's terms.

## 11. Open questions — RULED (Alex, design-basis ruling, thread (3))
1. RES-2 depth: the FULL_TEXT default STANDS for research findings, and
   depth must match the claim — direct quotation and factual observation
   require full text or authoritative primary content; preliminary leads
   may rest on snippets but must remain HYPOTHESES. (Incorporated in §5.)
2. BLOCKED timing: an agent MAY report a blocker early — encouraged — but
   the report is data for the harness, never the transition itself; the
   harness evaluates and records it. (Incorporated in §3.)
3. Contract instance placement: SIBLING artefact to the permission
   manifest — manifest governs authority, contract governs obligations,
   independent version histories; the harness binds both into one
   immutable run configuration recording the exact versions used.
   (Design's assumption confirmed.)
