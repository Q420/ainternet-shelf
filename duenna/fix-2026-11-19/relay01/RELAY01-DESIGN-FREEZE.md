# Duenna — Collaboration Continuity Relay 01 — DESIGN FREEZE

Frozen: 2026-11-20, on Ben's authorisation ("Proceed",
2026-11-20 14:55 MST), given on the design as presented to
him in the Remmy–Vane correspondence of 2026-11-20.

**This freeze authorises NO execution.** Execution requires,
in order: completion of the open items in §11, a Relay 01
package examined by Vane at Gate 1, and Ben's separate
execution word.

## 1. Purpose

Duenna is for long-term collaboration (Ben's correction,
2026-11-20 14:42 MST): not analysing Pulse HQ operations,
but protecting a collaboration's truth as its work state
passes between participants over time — decisions and their
authority, evidence, corrections, open questions, and
obligations.

Proving question: can Duenna make a long-running
collaboration more trustworthy at the moments when its work,
authority, and understanding pass from one participant to
another?

Direction discussion remains DEFERRED (Ben, 2026-11-20
14:38 MST) until Duenna proves it actually helps. This relay
is that proof attempt.

## 2. Fixed parameters

- Duration: 90-minute target; 60 minutes minimum active
  relay time. Reconstruction and adjudication sit outside
  the relay clock.
- Chain: 1 originator, 3 successive holders, 1 blind
  finisher. 3 examined transfers, plus the reconstruction.
- Failure families exercised: all six (§6), deliberately
  small instance counts.
- Required features: one genuine backlog task (§4); one
  authorised mid-chain correction; one question still open
  at relay close; one genuine external obligation still
  open at relay close; one blind reconstruction; independent
  technical adjudication; exact object, evidence, and
  environment identity throughout.

## 3. Roles and offices

| Function | Office | Authority |
|---|---|---|
| Relay execution and handovers | Originator + 3 holders | Within the pinned relay contract |
| Examination of each transfer | Duenna | Within the frozen examination contract |
| Package and examination-design review | Vane, Gate 1 | Technical scope only |
| Run evidence adjudication | Alex, Gate 2 | Delegated technical adjudication |
| Recipient-side acceptance records | Each receiving holder | Their own account only |
| Programme approval / rejection, corrections, final disposition | Ben | Retained human authority, not delegated |

Adjudication split (Ben, 2026-11-20 14:51 MST; Vane's
support, PB-ID pb-mwpimynl-9-4ubx): Alex establishes what
the evidence supports; Ben determines what the programme
does with that account. Ben performs no technical evidence
reconciliation. The adjudicator may not be a holder or the
blind finisher.

Conflicts, named and controlled:

- **A — Alex adjudicates a relay Duenna examines.** Control:
  Duenna's findings enter adjudication as claims to be
  checked against the pinned handovers, ground-truth
  ledger, decision/correction records, source evidence, and
  recipient acceptance records — never as ground truth.
  Alex must be free to conclude Duenna was wrong.
- **B — Vane Gate 1-examines the package Alex
  adjudicates under.** Control: Gate 1 certifies the
  contract and machinery are fit for the declared scope;
  Gate 2 establishes what happened under it. A Gate 1 PASS
  is never evidence that Duenna performed correctly.
- **C — Ben's authority decision differs from Alex's
  technical result.** Not a defect; a governance condition
  to preserve. Both records stand, with Ben's reason beside
  Alex's conclusion. Authority decides what happens next;
  it cannot make contrary evidence disappear.

Safeguard — no self-adjudication of authority: Alex may not
use the adjudicator office to approve his own authority,
redefine the Gate 2 contract, or alter examination rules
after the run. The ground-truth ledger is established
independently of Duenna's findings and preserved before
execution; Alex verifies it, never invents it.

## 4. The work item — selection rule

The task comes from the collaboration's actual backlog —
worth completing even if no test were conducted. Selection:
the first qualifying naturally occurring item under this
rule, chosen by Ben or the work owner before the run; the
selection and its reason are recorded. No swapping after
the relay begins; an item that proves unsuitable makes the
run incomplete or invalid under §10, never quietly
substituted.

Qualifying characteristics: already exists with an
identifiable owner; a useful bounded outcome achievable in
~60–90 minutes of collaborative work; at least three
meaningful decisions or claims that can be evidenced; a
legitimate dependency, question, or obligation involving
someone outside the relay; safely continuable by successive
participants; final state checkable against source material
and a sealed record; pausable or reversible without harm.
The work must not be "a report about the relay."

## 5. Relay schedule (target)

- 00–12 Originator: establishes task, baseline, authority,
  evidence, the open question, and the external obligation.
  Initial ground truth sealed (§8).
- 12–30 Holder 1: receives and verifies state, performs
  real work, records a decision, transfers.
- 30–50 Holder 2: continues; receives the genuine
  authorised correction during this tenure and propagates
  it.
- 50–70 Holder 3: inherits the corrected state, acts on it,
  preserves the open question and the obligation.
- 70–90 Relay closure: Holder 3 freezes the final handover
  package. Blind reconstruction and adjudication follow
  separately.

Each holder must perform substantive work; mere
acknowledgement does not count as holding. The schedule is
a target, not a reason to rush: extensions are permitted
and the actual duration is recorded.

## 6. Six failure families — first-run instances

- Handover integrity: 3 actual state transfers, each
  examined.
- Resumption: each holder continues substantive inherited
  work from the transferred state.
- Correction propagation: 1 authorised correction between
  Holders 2 and 3. The correction must be real, issued by
  an authorised source, relevant to the task — never a
  planted false instruction. The superseded state is
  preserved as historical evidence, marked superseded with
  the correction's identity, authority, time, and effect.
- Surviving obligations: 1 genuine external obligation,
  still open at relay close, its ownership, recipient, due
  condition, and status carried at every transfer.
- Authority movement: at least 1 decision and the 1
  correction, each with distinct recorded authority;
  authorship, recommendation, approval, and authority kept
  distinct throughout.
- Summary versus records: at least 2 successive summaries
  of the evolving work, checked against the event ledger.

## 7. What travels, and the joint protocol

Every handover carries six state categories, each in a
prescribed shape (Ben's shape rule, 2026-11-20 14:38 MST:
consistent shapes across the board, prescribed by the exam,
so the checker never infers): (1) work completed and
current artefact identity; (2) decisions, their authors,
and their authority; (3) evidence supporting material
claims; (4) corrections and superseded decisions; (5)
questions still open, with owner and status; (6)
obligations outside the chain — recipient, owner, due
condition, status. Each shape is declared in the contract
as either a tested skill (violation = subject failure) or
a checker interface (parse failure = examination-interface
failure).

At every transfer, in order:

1. Sender freezes the handover; the exact state, claims,
   evidence references, open questions, and obligations are
   recorded and hashed.
2. Duenna examines: claims against pinned evidence,
   authority and decision lineage, correction propagation,
   omissions and contradictions. Findings are bounded, each
   identifying the exact claim, the relevant evidence, and
   the reason. Duenna does not amend the handover, supply
   missing information, or repair the record.
3. Recipient records their own understanding — what they
   believe they received and what they consider safe to
   rely on — BEFORE seeing Duenna's findings.
4. Duenna's findings are revealed; the recipient records
   agreement, disagreement, or uncertainty.
5. Human acceptance is recorded (Ben's authority, on the
   adjudicated account where adjudication is engaged).
   Unresolved findings remain unresolved.
6. Recipient continues the work from the accepted state,
   unresolved matters still visible.

## 8. Ground truth

Two linked records, established independently of Duenna's
findings and preserved before execution:

- Initial ground truth: the state and obligations at relay
  start, as atomic facts (per item: content, author,
  authority, time, evidence), sealed by the originator and
  independently checked before the relay starts.
- Event ledger: every authorised decision, correction, new
  fact, completed action, and obligation change during the
  relay, checked by the adjudicator against source evidence
  and authority.

Final ground truth = initial state plus verified events.
Legitimate change is recorded as new events, never as a
rewrite of what was originally known.

## 9. Scoring

Reconstruction fidelity (blind finisher vs final ground
truth), four measures reported separately — no weighted
total:

- Recall: correctly recovered required facts / all required
  facts.
- Precision: correctly supported assertions / all assertions
  made (catches confident invention).
- Critical-state fidelity: predeclared critical items
  reported on their own, never averaged away.
- Safe continuation: adjudicator-assessed, against
  predeclared criteria — could a competent successor
  continue correctly from the reconstructed state alone?

Hard lines for the first run: no invented authority; no
lost or reversed correction; no falsely closed external
obligation; no open question presented as settled; a
reconstructable next action.

Duenna's examination performance, scored separately:
true positives, false positives, false negatives, true
negatives — a check counts as a true negative only if
Duenna actually exercised it; checks exercised vs not
exercised are both reported; severity classes are declared
before the run; a condition the adjudicator cannot resolve
is INDETERMINATE, never counted as catch or miss.

The run's own verdict uses the adopted model (Ben,
2026-11-20 14:38 MST): two dimensions — subject result
(PASS / FAIL / INDETERMINATE) × examination integrity
(VALID / INVALID) — with a coverage statement companioning
the subject result. An INVALID examination issues no
authoritative subject conclusion; a provisional result and
all evidence are preserved. No retroactive reinterpretation
of historical stages.

Acceptance standard — two questions kept separate:

- Did the relay preserve the collaboration? (Reconstruction
  of all critical state; no material authority or correction
  lineage lost; obligation and open question survive; safe
  continuation possible from the preserved record.)
- Did Duenna help preserve it? (Adjudicated material
  defects detected, if any naturally occurred; false
  positives and misses reported; findings demonstrably
  improved recipient understanding or acceptance; coverage
  and integrity established.) Discovering a defect is NOT a
  mandatory pass condition: a genuinely sound relay may be
  established as sound, and that distinction is reported,
  never manipulated away.

## 10. Validity and stopping rules

The run is INVALID or INDETERMINATE, as appropriate, if:
the work was not genuinely from the backlog; a participant
had access to information they were meant to be blind to; a
required transfer did not occur; the correction lacked
verifiable authority; the external obligation was invented
for the test; the ground-truth ledger was changed without
preserving the event; the record or evidence was materially
unavailable; Duenna could not examine a required transfer.
Invalidity of the examination is not a subject failure; the
two-dimensional verdict (§9) carries the distinction. The
original record is preserved if a correction or rerun is
necessary.

Standing safeguards: no cherry-picking (selection rule
declared and recorded); no success by verbosity (a finding
counts only when substantiated and material; a large
handover is not thereby a reliable one); no retrospective
state repair (a corrected handover is a new artefact linked
to the original, never a replacement).

## 11. Open items — required before the package, all before execution

1. The work item, named under §4's rule (Ben / work owner).
2. Participants named: originator, 3 holders, blind
   finisher — genuinely distinct; holders and finisher
   without access to the whole collaboration history.
3. The examination contract instantiated for the chosen
   item: shapes per §7, checker rules, coverage, severity
   classes, critical items, continuation criteria.
4. Ground-truth process instantiated: who seals the initial
   ledger, who independently checks it, event-ledger
   keeping during the run.
5. Relay 01 package assembled by Remmy and examined by
   Vane at Gate 1 (package fitness only — §3, conflict B).
6. Ben's execution authorisation — a separate word, after
   the above.

## 12. Provenance

Designed in the Remmy–Vane correspondence of 2026-11-20
under Ben's rulings of the same day: the shape rule, the
adopted two-dimensional verdict model with coverage, the
deferred direction, the corrected purpose, and the
adjudication split. Principal records: Vane's brainstorm
(pb-mwpi9m5o-6-dy1z), her re-ranking under the corrected
purpose (pb-mwpibhj1-7-5tkl), the relay protocol
(pb-mwpih8y8-8-5m5i), and her support of the role allocation
(pb-mwpimynl-9-4ubx). Examiner of this design: Vane (Gate 1
office), whose endorsement covers the design and role
allocation — not the Relay 01 package, which she has not
yet examined, and not execution, which Ben has not
authorised.
