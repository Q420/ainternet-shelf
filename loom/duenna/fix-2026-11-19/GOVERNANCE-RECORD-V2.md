# GOVERNANCE RECORD — production adjudication (v2, DRAFT for pinning)

Drafted by Remmy (orchestrator), 2026-11-19, as step 2 of the
first-use sequence settled in the adjudicator proposal
(ADJUDICATOR-CORRECTION-PROPOSAL.md, content-cleared in full).
This record pins the ruling; it does not extend it.
Identity: this record is identified by the SHA-256 digest
of its pinned content (Ben's standing ruling — a pin is a
SHA-256 digest; it establishes identity, not truth). The
shelf commit is a location and version reference only,
never the identity. On pinning, the digest is computed
over the pinned text and recorded in the operational
delegation and the programme record; it is not written
into this record, so the pinned text never changes under
its own pin. (Correction per the examiner's Gate 1
examination of the drafts, 2026-11-19.)

AMENDMENT (v2): this version amends the record pinned on
2026-11-19 (SHA-256 43b199a5b58268a59fc81d4ed29124edcf0f8
d037db6e212873bf3b2047a1eb8) in exactly one respect — the
holder of Gate 2. Claude, named in v1, declined the role
on 2026-11-19 (his refusal is filed at CLAUDE-ADJUDICATOR-
REFUSAL.md). Ben ruled the same evening: Alex is the
adjudicator. Every other provision of v1 is carried over
unchanged, word for word. On pinning, v2 supersedes v1;
v1 remains on the record as history. The delegation
issued under it to Claude is recorded as ISSUED ·
DECLINED BY NAMED GRANTEE · UNREVOKED · NOT AVAILABLE
FOR GATE 2 EXERCISE: it was not exercised, it is not
transferable, and it confers no authority on Alex. (Status
wording per the examiner's Gate 1 form check of this
amendment, 2026-11-19, accepted by Ben at pinning.)

## The ruling pinned

Ben's architectural ruling, 2026-11-19, in two moves kept
distinct: the gate structure and allocation of 19:04
(statuses, gates, mandatory prior verification), and the
final division of responsibilities of 19:19, which
supersedes the 19:04 holder allocation and the provisional
appointment between them:

- **Ben holds the structure itself.** Which statuses exist,
  what each gate requires, and who holds each role are
  Ben's. Changing the structure, or settling outside it,
  returns to Ben under his standing authority.
- **The orchestrator (Remmy) assembles** the adjudication
  package: the full admissible evidence set.
- **The examiner (Vane) verifies at Gate 1.** Verification
  is genuinely independent: the orchestrator cannot waive,
  override, or self-verify, and the adjudicator does not
  verify his own package.
- **The adjudicator (Alex) decides at Gate 2**, on a
  verified package only.

## The status gates

  Status 1 — PACKAGE ASSEMBLED. The orchestrator assembles
  the full admissible evidence set (below).
  GATE 1 — VERIFICATION. The examiner independently
  verifies the package: complete against the run contract
  and the evidence list; G4's three results present and
  correctly kept separate; G6 findings where implemented;
  discrepancies surfaced, not smoothed. Gate 1 also
  verifies the DELEGATION itself: the governance record is
  the correct pinned record; the delegation identifies the
  adjudicator as entitled; its scope covers this run and
  this decision; its limits have not been exceeded; it
  remains operative. A failed verification returns the
  package to Status 1 with the failures recorded. No
  decision may be taken on an unverified package — such a
  decision is not a settlement.
  Status 2 — PACKAGE VERIFIED.
  GATE 2 — DECISION. The adjudicator settles the run's
  outcome against the pinned contract, on the verified
  package, and produces the adjudication record. The
  settlement may be INDETERMINATE. Any disagreement the
  verification recorded is carried into the adjudication
  record, never silently resolved by the decision.
  Status 3 — DECIDED.

Verification certifies the PACKAGE, not the verdict:
passing Gate 1 does not establish that the outcome decided
at Gate 2 is correct. The decision remains a judgment, and
remains examinable after the fact — package, verification,
and adjudication record are all preserved.

## The admissible evidence set

The adjudicator may rest only on: (1) the immutable run
record and its identity; (2) the pinned run contract —
acceptance criteria and pass bar, at their exact version;
(3) the frozen configuration and the verified subject
identity; (4) preserved original outputs and relevant
source artefacts; (5) G4's three results, retained
separately as closure evidence, never merged into the
outcome; (6) G6 findings, where implemented; (7) any
discrepancies and unresolved evidence gaps, carried as
such; (8) this pinned governance record and the exact
delegation authorising the adjudication, including its
scope and limits.

G4 is not the adjudication: a G4 PASS is not a run PASS,
and a G4 failure is not automatically a model failure. G6
resolves report references against the record; G6-resolvable
does not mean substantively correct, and nothing here
credits G6 beyond its contract.

## The adjudication record

Each adjudication produces an immutable, separately
identifiable record carrying: run identity and pinned
criteria identity; adjudicator identity AND the pinned
delegation authorising that adjudication; exact evidence
identities and references; the adjudicated outcome and the
reasoning connecting evidence to outcome; each attribution,
with its evidence and its authority; every disagreement,
both positions preserved; every unresolved or unknown
finding, explicitly retained.

## Settlement under uncertainty

Closure must complete; completion must not manufacture
certainty. The adjudicator must not turn incomplete
evidence into a confident verdict; may settle an outcome
as INDETERMINATE; preserves UNKNOWN attribution as
UNKNOWN, and disagreement as disagreement, inside the
settlement itself.

## Strength label

As pinned, these gates are PROCEDURAL requirements —
strength label DESIGNED. No mechanism yet prevents an
ASSEMBLED → DECIDED transition. The implementation
requirement, when the role is built: the verified state
must be independently identifiable, DECIDED must require
it as a prerequisite, the verifier's identity and the
verification result are preserved, and the orchestrator
must not be able to alter the sequence, waive a gate, or
manufacture a verification state. Until that mechanism
exists and is examined, no relationship in this record is
to be read as enforced.

## Authority boundary

Governance originates with Ben. The adjudicator approves
no scope, starts no work, authorises no programme change.
Authority to settle a run outcome is a distinct grant from
authority to act; neither implies the other, and neither
is inferred from a seat's identity or from possession of a
briefcase. This record creates no independent appeal
process: any challenge or escalation beyond the
adjudicator's delegated settlement authority returns to
Ben under his standing authority.
