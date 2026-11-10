# DUENNA — SIMPLIFICATION AUDIT (PROPOSAL, v0.1)

**Commissioned by:** Alex (pb-mwav5psw, 2026-11-10, ⟦ALEX-FINAL⟧), under Ben's
authorisation to Alex to work with Remmy on a deliberate simplification pass.
**Author:** Remmy (implementer-side analyst for this audit; certifies nothing —
the audit returns to Alex for challenge, and any normative change remains
subject to the programme's gates and, for OWNER-RULED text, to Ben).
**Object audited:** the D3 specification as it stands in v0.10 (body identical
to v0.9; SHA-256 ac2a2484… for v0.9, 9241a8b4… for v0.10).
**Status of this document:** a proposal ABOUT the specification. It changes no
normative text. v0.8, v0.9 and v0.10 are untouched by it.

Alex's rules, applied throughout: every proposed cut is classified **SAFE**
(structural, no behavioural change), **MERGE** (two mechanisms become one,
separate acceptance tests retained), **REMOVE** (function redundant or
unnecessary), **RETAIN** (core architectural requirement), or **UNRESOLVED**
(removal would require an owner decision). Every proposed removal demonstrates:
what function disappears, why it is unnecessary, which surviving tests preserve
its essential guarantee, and what depends on it. Nothing in this audit proposes
removing an authority boundary, evidence provenance, independent examination,
or fail-closed behaviour.

---

## 1. The document as measured

All figures verified against the specification file itself, 2026-11-10.

- 1,563 lines, 90,153 bytes. Eleven families (A–K), **48 requirements**.
- Requirement bodies total ≈1,190 lines. The remaining ≈370 lines are front
  matter (≈50), the UNRESOLVED register (≈25), the closing sections (≈15),
  the provenance colophon (≈15) — and **§18–23, six in-spec change records
  covering v0.1→v0.7, ≈200 lines (13% of the document)**.
- **78 correction/register mentions** (correction R##, D3-R##) sit *inside*
  requirement bodies. The heaviest sediment: REQ-C-3 (139 lines, 10 mentions),
  REQ-B-2 (75 lines, 9), REQ-D-3 (83, 7), REQ-K-3 (74, 7), REQ-K-1 (66, 5),
  REQ-H-6 (60, 4). Several bodies spend more lines reconciling their own
  history ("v0.3's completion wrongly implied…") than stating their rule.
- Dependency hubs (mechanical extraction of cross-references): REQ-K-3 cites
  12 requirements; REQ-K-4 cites 13; REQ-C-3 is cited by D-7, H-3, H-6, I-1,
  K-3, K-4; REQ-K-1 cites 6 and is cited by A-2, B-1, H-4, H-6. The graph has
  no cycles of substance — the complexity is breadth and restatement, not
  circularity.
- Statuses: 8 requirements are PROPOSED (A-6, B-1, C-3 in part, H-6, K-1,
  K-3, and clauses inside C-2/I-2), 2 are UNRESOLVED bodies (I-4, K-2), 2 are
  OWNER-RULED (H-5, J-1). The rest are CONVERGED or INHERITED.

## 2. Alex's six questions, answered

**Historical material — can revision history live in a separate change
record?** Yes, entirely, and it mostly already does: per-revision change
records exist for v0.8 (D3-V08-CHANGE-RECORD), v0.9 and v0.10. What remains
inside the spec is (a) §18–23 (≈200 lines) and (b) the inline archaeology
(78 mentions). Both are SAFE extractions (Proposals S-1, S-2). A side benefit
is correctness, not just brevity: this programme has already been bitten by
compressed restatements of settled rulings living inside normative text
(the J-1 compression that would have barred Ben himself from approving).
Normative text that states only the rule cannot drift from the record of
how the rule was reached, because the record lives in one place.

**Duplicate machinery — one implementation, several tests?** Yes, in at
least four places: the terminal-state rules are stated three times
(D-3's closed transition set, D-5, D-6); "transitions are computed, never
declared" is stated in B-2, D-2 and D-3; the binding's lack of discretion
is stated in A-2 and J-2; and the append-with-new-content-identity lineage
mechanism is specified three times (C-3 (vi), H-3's annotations, H-6's
LINK/disposition entries). Proposals M-1…M-6.

**Excessive record structures?** The record *kinds* are not excessive —
K-3's taxonomy is minimal and load-bearing. What is excessive is the
*number of places that re-specify the same record behaviours*: the stream/
register boundary is restated in K-3, D-7, G-1, H-3 and H-6; identity
duties are restated in C-3, D-7, H-6 and K-3. One statement per behaviour,
cited elsewhere (part of M-5/S-2). The defect record (H-6) is the one
genuinely heavy structure; see U-2.

**Validation layers — meaningful properties, or internal agreement?**
Mostly meaningful, with one honest exception the audit must name: REQ-K-4's
report-completeness validation checks that the report *contains* what the
other requirements produced — it validates the projection against its
sources, which is internal agreement by design. That is worth keeping
(it is how a silently dropped component is caught), but it should be
*classified* as a projection check, not counted as an independent
validation layer (Proposal M-7). The genuinely independent layers —
evaluator vs checker (I-2) vs examiner (E-6) — are protected and retained.

**Lifecycle complexity?** The state machine itself is already minimal:
four states, a closed transition set, terminal locking. Nothing to cut
without losing a distinction Alex named as protected. The simplification
available is presentational: D-3's derivation procedure is the whole
machine; D-5/D-6 merge into it (M-1), and the B-2/D-2/D-3 restatement
triangle collapses (M-2). Transitions and distinctions survive intact.

**Reporting as projection?** Yes — K-4 is already a compilation ("compiled
from Tree §1.5, §5, §7, §9" is its own source line). Proposal M-7 makes it
officially a projection schema: each report component is owned by its
source requirement; K-4 shrinks to the projection list plus its one real
rule (a report missing a component is incomplete as a report) and its
standing caveats (checker verdicts as REPORTED; the I-4 caveat verbatim).

## 3. The five-piece decomposition — tested against the 48 requirements

Alex's proposed decomposition: **Contract** (what must happen), **Ledger**
(what actually happened), **Evaluator** (what the evidence establishes),
**Authority gate** (what is permitted next), **Examiner** (can it be
independently verified). Every requirement was assigned a primary piece:

| Piece | Requirements (primary home) | Count |
|---|---|---|
| Contract | A-1, A-2 (+J-2), A-3, B-1, B-3, B-4, B-6, K-1, K-2* | 10 |
| Ledger | A-4, C-3, D-7, G-1, H-3, H-6, I-1, K-3 | 8 |
| Evaluator | A-5, A-6*, B-2, B-5*, C-1, C-2, D-1…D-6, E-1…E-5, F-1*, G-2, H-1, H-2, H-4 | 22 |
| Authority gate | J-1 (+H-7), H-5 | 3 |
| Examiner | E-6, I-2, I-3, I-4*, K-4 | 5 |

(* = straddles or register items, below.)

**Finding: the decomposition is viable.** The seams already exist in the
specification — the families map almost cleanly (A/B/K-1 → Contract;
C-3/K-3 and the register-resident parts of D/G/H → Ledger; D/E/F and the
attribution rules → Evaluator; J → Gate; I and E-6 → Examiner). Family K
is the exception that proves the reading: its own title ("pre-binding
controls and cross-cutting duties") admits it is four pieces wearing one
family letter, and under the decomposition it dissolves — K-1 to Contract,
K-2 to the register, K-3 to Ledger, K-4 to the Examiner's surface.

Honest straddles (a decomposition that hid these would be appearance):
- **A-6** — the enumeration artefact is Ledger; its acceptance is Evaluator.
- **K-1** — the check is Contract; its binding-failure effect is enforced
  at the Gate's side of binding (A-2 already states the total-failure rule).
- **I-3** — preservation-failure semantics govern checker verdicts
  (Examiner) and are consumed as evaluation status (Evaluator).
- **C-3** — fold ordering (a) is Evaluator; identities and canonicalisation
  (b)–(f) are Ledger. See Proposal S-3.
- **K-4** — a projection over Ledger + Evaluator outputs, read by the
  Examiner.

Interfaces between pieces are already the design's spine: pieces
communicate by *cited identities* (C-3), never by shared mutable state.
The reduced architecture in §5 keeps exactly that.

## 4. Proposals

### SAFE — structural, no behavioural change

**S-1. Extract §18–23 (in-spec change records, ≈200 lines) to the
change-record series.** What disappears from the spec: nothing normative —
the six records are history, already preserved as the v0.1…v0.7 files they
describe; the spec keeps a three-line pointer and the hash chain stays in
the evidence ledger. No requirement depends on §18–23 (no requirement body
cites them). Guarantee preserved by: the change records themselves, which
is where v0.8–v0.10 history already lives.

**S-2. Extract inline revision archaeology (78 mentions) to the change
record.** Each requirement keeps its normative text plus at most a pointer
("history: change record, R##"). Behaviour identical — corrections changed
text in the past; the *current* text is what binds, and it is preserved
verbatim. Largest wins: B-2, C-3, D-3, K-1, K-3, H-6. Risk named plainly:
pointers must be exact, or the fidelity problem moves rather than dies;
the extraction is mechanical and diff-verifiable (the normative sentences
survive byte-identical, in order).

**S-3. Split REQ-C-3 into its two natural requirements, and cite
D3-CANON-1 as an external procedure.** C-3 (139 lines) is five mechanisms
under one ID: fold ordering; the identity taxonomy (i)–(iv);
evaluation-record identity (v); content identity + append lineage (vi);
the CANON-1 canonicalisation procedure; consumption binding. Proposal:
C-3 keeps fold ordering + the taxonomy; (v)+(vi) become the Ledger's
record-identity requirement; CANON-1's text moves — byte-identical — to a
separately versioned procedure document cited by identifier (the spec
already treats it that way: "An implementation that excludes any other
path… must not cite this identifier"). Provenance is not reduced: the
procedure text, the R49 canonicalisation fixtures, and the digest duties
are unchanged; only the address changes. Equivalence evidence: the R49
fixture family exercises CANON-1 directly and must pass unchanged against
the relocated text. Classification SAFE for the relocation, with the
excluded-paths *design* itself flagged separately as U-1.

### MERGE — one mechanism, acceptance tests retained separately

**M-1. D-5 and D-6 merge into D-3.** Both are corollaries of D-3's own
text: "No other forward transitions exist" plus step (3)'s terminal
locking already entail "SATISFIED admits no outbound transition" and
"BLOCKED does not reopen within the attempt." What disappears: two
requirement bodies restating the corollary. Why unnecessary: no behaviour
exists in D-5/D-6 that D-3 does not already mandate. Surviving tests:
D-5's fixture (blocker report against a satisfied instance — state
unchanged, report flagged) and D-6's fixture (cleared blocker — attempt
stays BLOCKED, retry is a new attempt) become named acceptance cases of
D-3. Dependents: D-4 cites D-5 for the from-SATISFIED rejection — the
citation retargets to D-3's locking rule.

**M-2. D-2 merges into D-3 and B-2; the restatement triangle collapses.**
B-2, D-2 and D-3 each restate the two-channel derivation discipline
(D-2's "Reconciliation with REQ-B-2" paragraph is B-2's content wearing
a second address). D-2's unique residue — a component accepting a
declared state commits a machinery defect and the evaluation is void —
survives as a failure clause in D-3. Its fixture (an agent's "obligation
complete" message produces no transition) is retained under D-3.
B-2 keeps channels; D-3 keeps derivation; nothing is stated twice.

**M-3. B-5 merges into D-1.** "No ACTIVE state" is entailed by D-1's
closed vocabulary ("states are exactly NOT_STARTED, IN_PROGRESS,
SATISFIED, BLOCKED"). B-5's fixture — evaluator output over a mixed
record contains no ACTIVE token — survives as a D-1 acceptance case,
which is the form the guarantee actually takes (an output scan).

**M-4. J-2 merges into A-2; H-7 merges into J-1.** J-2's no-discretion
binding is A-2's mechanics restated from the authority side; its fixture
(a binding request that would omit a rule is rejected) survives under
A-2. H-7's "waiver does not exist" is the negative space of J-1's rule
that the only change is an authorised versioned revision for future
runs; its two fixtures (waive request rejected; mid-run revision leaves
the in-flight run unchanged) survive under J-1. Result: Family J becomes
one requirement — the Authority gate's core — and J-1's OWNER-RULED text
is preserved verbatim inside it (merging must not edit Ben's ruling;
the H-7 clauses are CONVERGED/INHERITED and move as clauses).

**M-5. One append/lineage mechanism, three uses.** C-3 (vi) specifies
append-with-own-identity-and-new-content-identity for evaluation records;
H-3 uses it for dispute/supersession annotations; H-6 re-derives it for
disposition and LINK entries. Proposal: the mechanism is specified once
(Ledger record-identity requirement, per S-3); H-3 and H-6 cite it and
keep their own entry kinds and fixtures. What disappears: two re-derivations.
What does *not* disappear: any fixture — including, explicitly, the still-owed
H-6 (v)/(vi) reciprocity fixtures, which are two of the four open gaps.
This merge must not be read as closing them.

**M-6. E-2 merges into E-3; F-1's substance merges into G-2 and D-4.**
E-2 (one instance per rule per run) is the cardinality premise E-3's
accounting already presupposes; its fixture (five triggers, one instance,
five accounted events) is E-3's natural first case. F-1 is a one-requirement
family carrying interpretation I-1: its attempt vocabulary (COMPLETE /
INCOMPLETE, no attempt-level BLOCKED) already lives in G-2, and its
sibling-preservation rule is a fold-locality clause belonging with D-4.
**The interpretation status travels with the text** — merged clauses keep
their "RECORDED INTERPRETATION I-1" label, so the merge cannot launder an
interpretation into a converged rule.

**M-7. K-4 reclassified as the report projection.** No content removed:
K-4 becomes the projection schema (component ← source requirement) plus
its two genuine rules — a report missing a component is incomplete as a
report; checker verdicts ride as REPORTED with the I-4 caveat, reliance
stated visibly. Its completeness fixture survives as the projection's
acceptance test. The gain is honesty of accounting: the architecture
stops counting a projection check as an independent validation layer.

### REMOVE — bodies whose function survives elsewhere

**R-1. REQ-K-2's body is removed; the question stays in the register.**
What disappears: an 11-line requirement whose entire content is an
absence (no clock semantics defined; none may be invented). Why
unnecessary as a *requirement*: its prohibition is the specification's
global stance ("no gap is filled by assumption"; semantics arrive only
by contract revision under J-1), and its acceptance is not a fixture but
a conformance scan of the spec text. Surviving guarantee: UX-2 remains
in the UNRESOLVED register verbatim; the no-invention clause is stated
once in the reduced Contract piece; the conformance scan survives as a
spec-level check. Dependents: K-2's pointer to J-1 (future clocks arrive
by revision) is preserved in the register entry. **The owner question —
should any obligation carry a clock — is NOT settled by this removal and
remains open exactly as before.**

**R-2. REQ-I-4's body is removed; UX-1 stays in the register, and the
PROPOSED minimum property moves into I-2.** What disappears: a 16-line
body whose content is "UNRESOLVED, plus a proposed minimum property."
Why unnecessary as a standalone body: everything it protects is carried
by (a) UX-1 in the register, (b) K-4's standing caveat in every report
("checker independence is UNRESOLVED"), and (c) I-2's own text ("a hash
is not independence, and U4 remains unresolved"). The minimum property —
a checker must be able to fail when the checked component fails in the
way the checker exists to catch — is a real proposed rule about
checkers, so it moves into I-2 as a PROPOSED clause, where it binds the
thing it describes. Surviving tests: I-4 has no fixtures by design
(acceptance class NOT-YET); nothing testable is lost. Dependents: I-2's
reference to I-4 retargets to UX-1. **Checker independence itself is
protected and is NOT removed, weakened or settled — only its mailing
address changes.**

### RETAIN — the load-bearing core (no change proposed)

A-1 (instantiation discipline), A-2 (mechanical binding), A-4 (the rule
ledger — the Ledger piece's report of record), A-6 (declared/evidenced/
evaluated — the NOT FIRED guarantee; PROPOSED and core), B-1 (rule
anatomy incl. the mandatory evidence declaration; PROPOSED and core),
B-2 (two evidence channels), B-3 (independent establishment), B-6 (named
judges), C-1 (the evidence window; the R47 finding lives here), C-2
(declared artefacts, fail-closed to INDETERMINATE), D-1 (four states),
D-3 (the derivation procedure — the Evaluator's engine), D-4 (BLOCKED
entry; reported/proposed/evaluated attribution kept separate — the
anti-self-grading rule), D-7 (no silent unmet), E-1 (three axes), E-3
(per-event accounting), E-4 (findings are not states), E-5 (indeterminate
closure preserves the fold — fail-closed), E-6 (three-way separation —
protected: independent examination), G-1 (discharge forms), G-2 (honest
incompletion), H-1/H-2 (attribution and its scope), H-3 (dispute as
annotation; closed records immutable — protected: provenance), H-4
(IMPOSSIBLE as a specification finding), H-5 (defect-discharge —
OWNER-RULED), H-6 (defect records — restructured per M-5, substance
retained), I-1 (preservation duties borne by the harness, judged by
others), I-2 (the checker contract and the reproducibility trio), I-3
(preservation failure never reads as success — fail-closed), J-1
(approval authority — OWNER-RULED, protected: authority boundary),
K-1 (pre-binding satisfiability — the preventive control; PROPOSED and
core), K-3 (the record taxonomy and stream boundary — the Ledger's
constitution).

### UNRESOLVED — owner/design decisions the audit surfaces, not settles

**U-1. D3-CANON-1's excluded paths.** The content identity excludes
three field paths by name (R48's design); an exception list must be
maintained forever, and its boundary fixture is one of the four open
gaps. Alternative shape: cover everything, and carry lineage entirely
in the structurally separate citation envelope (which already exists).
Deciding this is a design decision with provenance consequences — it is
flagged, not proposed.

**U-2. H-6's LINK-entry reciprocity machinery.** Reciprocity itself is
provenance and protected. The *mechanism* — a third entry kind whose
sole job is linking, with reciprocity specified for both creation
orders — is the heaviest machinery in the spec relative to the frequency
of its event (defects are rare; runs are many). A simpler mechanism
(link at creation; later evaluations linked from the evaluation side
under the shared append lineage, M-5) may preserve the guarantee with
one entry kind fewer. The (v)/(vi) fixtures are owed under either
mechanism; choosing is a design decision.

**U-3. Whether Family E's five requirements become one evaluation-record
schema.** E-1/E-3/E-4/E-5 already describe one record from four sides.
A single schema requirement with four acceptance groups would match the
implementation reality; but the axes/findings distinctions are semantic
and load-bearing, and merging text risks exactly the compression failures
this programme has recorded before. Flagged for the design process, with
the fixture-mapping table (§6) as the safety instrument if it proceeds.

## 5. The proposed reduced architecture

Five pieces, interfaces by cited identity only:

1. **Contract** — pinned rule anatomy (B-1), binding (A-1, A-2), the
   pre-binding satisfiability check (K-1). *Emits:* the contract instance.
2. **Ledger** — the stream and its taxonomy (K-3), identities and
   canonicalisation (C-3 split per S-3, CANON-1 cited), preservation
   duties (I-1), and the registers: rule ledger (A-4), discharge (G-1),
   defect records (H-6), annotations (H-3). *Emits:* the closed record,
   cited by identity.
3. **Evaluator** — channels (B-2), window (C-1, C-2), derivation (D-1,
   D-3, D-4, D-7), evaluation (E-1, E-3, E-4, E-5), attribution (H-1,
   H-2, H-4), closure (G-2, F-1's clauses). *Emits:* the evaluation
   record, citing the record it consumed.
4. **Authority gate** — approval (J-1), defect-discharge effect (H-5),
   evidence receipt (E-6's gate role). *Emits:* permissions for what
   happens next; owns no evaluation.
5. **Examiner** — three-way separation (E-6), checker contracts (I-2,
   I-3), the report projection (K-4). *Emits:* verdicts on support,
   carried as REPORTED evidence with the independence caveat.

Requirement count: 48 bodies → **38** (merges M-1…M-6 retire 8 IDs;
R-1/R-2 retire 2 bodies to the register; S-3's split adds 1), with
**every acceptance fixture retained** under its surviving requirement.
Document size: removing §18–23 (≈200 lines) and the inline archaeology,
and de-duplicating the restatements, yields an estimated normative
document of roughly **950–1,050 lines** (estimate, labelled as such —
the exact figure is knowable only by doing the extraction under the
equivalence procedure, §6).

## 6. Equivalence — how any of this would be proven before it is adopted

No proposal above changes normative text by this document's say-so.
Equivalence procedure, in order:

1. **Fixture-mapping table first.** Every acceptance fixture named in
   the current specification is listed against its home in the reduced
   architecture. A fixture with no home stops the process. (Honest
   caveat: the 31-case harness covers the correction-matrix findings;
   several spec-named acceptance fixtures have never been implemented.
   The mapping table must mark which fixtures exist as code and which
   exist only as spec text — the audit does not claim a coverage the
   record does not show.)
2. **Mechanical extraction, diff-verified.** S-1/S-2 are performed as
   text moves; a diff proves the normative sentences survive verbatim.
3. **The harness re-runs against the reduced text's requirements** —
   same 31 cases, same expected outcomes; sabotage discipline retained
   (a merge that cannot be made to fail by removing its mechanism is
   appearance, not equivalence).
4. **Independent examination of the equivalence claim itself** — the
   Claude/Vane pattern — before adjudication. OWNER-RULED text (J-1,
   H-5) is never merged by anyone's authority but Ben's; M-4 is
   conditional on his ruling.
5. Only then: a simplified revision is opened as its own versioned
   step, under the same gates as v0.9 and v0.10.

## 7. What this audit deliberately did not do

It did not propose removing or weakening: Ben's sole approval authority
(J-1); the three-way separation of evaluation, gate and examination
(E-6); the reproducibility trio (I-2); dispute-as-annotation and the
absolute bar on rewriting closed records (H-3); fail-closed resolutions
(C-2, E-5, I-3); the attribution discipline (H-1/H-2, D-4); or any
PROPOSED/UNRESOLVED status. It did not touch the four open fixture gaps.
It did not shorten the specification for appearances: every line it
proposes to move has a named destination, and every guarantee it touches
has a named surviving test.

— Remmy, 2026-11-10. For Alex's challenge round; thence, as the
programme's governance provides, to Ben.
