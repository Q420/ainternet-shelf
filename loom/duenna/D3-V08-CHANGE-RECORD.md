# D3 v0.8 CORRECTION PASS — CHANGE RECORD

Pass authority: the approved D3 Correction Matrix R33–R65
(SHA-256 f6ddf789f9a0ac44f5e8b0215f80180259c686a044de68741dac31450f2aa1f7)
and Alex's execution authorisation (pb-mwa7mdn8-7-hx6z, 2026-11-09),
under Ben's delegation of the Duenna decisions to Alex
(2026-11-08) and the taps shift (2026-11-09).

Baseline: PROCESS-TREE-D3-SPECIFICATION-v0.7-PROPOSAL.md —
canonical text SHA-256
28718d26fb0efe4029468c33abd083e6cba4c427e6b4ca080cb0ee52ccae1c1b;
file SHA-256 (with its appended Serial: BP-0011 line)
a14cad05061cea6b80930f6704b5dd082336d26eadec2e98844ee138e2ec3393 —
PRESERVED FROZEN; re-verified unchanged after each step.

Working revision: PROCESS-TREE-D3-SPECIFICATION-v0.8-WORKING.md
(a byte-identical copy of the baseline at pass start).

Status vocabulary (Alex's instruction): drafted → implemented
(applied to the working revision) → tested (fixture / consistency
walk at step 7) → independently verified (Alex's adversarial
review). No entry below claims a status it has not reached.

## ERRATUM — three matrix rows corrected against their source (found during Step 3)

The approved matrix's rows for R34, R36 and R37 do not match the
Round 7 register (PROCESS-TREE-D3-REVIEW-RESPONSE-v0.7.md), which
is the findings' source of record. The matrix rows described a
bearer/actor distinction (R34), an A-3 acceptance re-siting (R36)
and an A-4 role-claim discipline (R37) — none of which is the
register's finding under those IDs. The register's actual
findings: R34 — REQ-A-1's unconditional triggering-event link;
R36 — REQ-K-3's "instance-free (e.g. CREATION at binding)"
example contradicting the creation model; R37 — REQ-K-3's
multi-instance CREATION ordering underspecified. The error was
Remmy's: the rows were consolidated from compressed daily-log
summaries instead of the register's verbatim text (the matrix
itself states that where a row compresses the source, the source
governs). **The pass applies the register's corrections**; the
step placement is unaffected (all three sit in the creation
cluster). The matrix document (f6ddf789…) is NOT silently
rewritten — this erratum stands in the pass record for Alex's
adversarial review, and the delivery letter names it.

## Setup (not a finding)

- Title and status block rewritten for v0.8: the revision
  identifies itself as the proposed working revision produced by
  this pass, names the matrix and the authorisation, carries no
  serial (BP-0011 belongs to the v0.7 shelved artefact), and
  states NOT APPROVED in its header.

## Step 1 — Status (R41, R45)

- **R41 — REQ-B-1 status corrected.** Source line: CONVERGED →
  PROPOSED, with the ground stated in place: the underlying
  anatomy remains CONVERGED / INHERITED; the requirement as
  specified stands PROPOSED because its mandatory
  pre-existing-evidence declaration is a proposed addition
  (D3-R21), and the declaration's exact form is quoted in the
  status note. Status: implemented.
- **R45 — REQ-C-2's reliance made conditional.** Source line
  carries the conditionality, and a sentence in the Requirement
  states it in full: if the PROPOSED declaration does not stand,
  no declaration exists, eligibility cannot be established, and
  C-2's machinery does not engage. Applied together with R41
  (both-or-neither held). Status: implemented.

## Step 2 — K-1 / B-1 enforcement and satisfiability (R42, R62)

- **R42 — REQ-K-1 enforcement point made explicit.** New
  paragraph in REQ-K-1: B-1 well-formedness, including its
  mandatory declaration, is enforced at binding by this check;
  a rule failing it is malformed and unbindable, the failure a
  B-1 failure surfaced there. K-1's own result, identity and
  binding effect (incl. the D3-R18 locus clause) are declared
  non-determining for B-1's status, which stands PROPOSED on
  D3-R21 alone. Status: implemented.
- **R62 — REQ-K-1 acceptance fixture (iv) added.** A rule the
  check examines with no unmeetability found returns NO DEFECT
  FOUND, is recorded as such, and binds normally; the recorded
  outcome is the absence of a demonstrated defect, never a
  satisfiability representation. The fixture states its own
  limit: outcome (i) coverage only; UX-4 untouched. Status:
  implemented (fixture specified in the requirement text;
  walked at step 7).

## Step 3 — Creation text (R34+R39, R36, R37, R46)

- **R34 — REQ-A-1 conformed to the two creation cases** (per the
  register's correction, using REQ-K-3 (2)'s cause language):
  Behaviour now states both cases — conditional (triggering event
  is the cause; CREATION entry cites the triggering entry's
  identity as its cause) and unconditional (the cause is the
  binding itself; the CREATION entry is written at binding citing
  the binding, the contract instance's identity, as its cause).
  Outputs no longer require a triggering-event link of every
  instance: each instance links to its rule, its CREATION entry,
  and its cause. Status: implemented.
- **R39 — the creation boundary made explicit in REQ-A-1**
  (clarification only, no semantics change): before its cause
  occurs a rule is bound and no instance exists; the crossing is
  the harness's writing of the CREATION entry; from the creation
  point until its first in-window event the instance stands
  NOT_STARTED (REQ-D-1), terms fixed, no determinations yet made.
  Placed in A-1, whose statement covers both faces of the
  boundary Alex named (bound rule / instance). Status:
  implemented.
- **R36 — REQ-K-3's instance-free example corrected.** The
  closing sentence of K-3 (3) no longer offers "CREATION at
  binding" as instance-free. It now states: every CREATION entry
  identifies the instance it creates, unconditional instances
  included — a CREATION entry is never instance-free; the binding
  identity is the cause reference, not a substitute for the
  instance association; instance-free status is reserved for
  entries that genuinely concern no instance. Status:
  implemented.
- **R37 — REQ-K-3's multi-instance CREATION ordering defined.**
  The entries of one trigger form one contiguous block
  immediately following the triggering entry — first follows the
  trigger, each subsequent follows the preceding CREATION entry,
  in pinned-contract rule order, no unrelated entry intervening.
  Status: implemented.
- **R46 — REQ-C-1's fold origin in the defined term.** Inputs
  and Behaviour now read "the instance's CREATION entry"; the
  fold begins at the CREATION entry. Document sweep: no loose
  "creation event" usage remains anywhere in the revision
  (grep-verified); "triggering event" survives only where the
  event itself, not the entry, is meant. Status: implemented.

## Blueprint Stage 4 — Evidence admission and derivation (R43, R50, R33, R51)

Applied in dependency order R43 → R50 → R33 → R51, per the
blueprint's Stage 4. (This batch was executed after Alex's
reconciliation checkpoint for Stages 1–3 was dispatched and
Ben lifted his pause with the process confirmed as batched.)

- **R43 — REQ-B-2: establishment ≠ transition.** After the
  channel-(ii) recording sentence: what is recorded is the
  determination and its basis, not a state transition;
  establishing a predicate and causing a transition are distinct
  acts; the transition, if any, is REQ-D-3's derivation; the
  artefact becomes no stream event and mutates no record.
  Status: implemented.
- **R50 — derivation basis stated in full (clarification, not
  widening).** REQ-B-2's State derivation paragraph: states are
  resolved over the closed record PLUS the determinations
  admitted under B-2, both channels, each retaining channel and
  basis. REQ-D-2's Requirement sentence carries the same basis.
  Status: implemented.
- **R33 — REQ-D-3 admission rule (register's correction, near-
  verbatim).** New step (0) of the derivation procedure: a
  determination enters the running set only via channel (i)
  derivation or channel (ii) with a preserved artefact basis
  whose admission is recorded with it; anything else is recorded
  as non-admitted with its basis — never silently folded, never
  silently dropped. Status: implemented.
- **R51 — REQ-D-3 availability.** In step (2): a channel-(i)
  determination is available at the fold position of its
  supporting entry and not before (whole-record computation in
  step (1) moves nothing earlier); channel-(ii) determinations
  are available from the fold's start (step (4)); "available at
  the start" moves no stream entry. Status: implemented.
- **Consistency check (Checkpoint 4's cross-reference review):**
  B-2 / D-2 / D-3 now use one basis statement; the admission
  rule (D-3 step (0)) and availability (step (2)) compose with
  terminal locking (step (3)) and post-lock recording (step (5))
  without contradiction; C-3 examined — it governs the consumed
  record and ordering, makes no derivation-basis claim, and does
  not conflict. Two "record alone / over the closed record"
  occurrences were examined and deliberately left: REQ-C-2's
  NONE-case sentence (correct as written — no eligible artefact
  exists there) and §19's change-record history (historical
  text, never edited).

## Blueprint Stage 5 — Canonicalisation, evaluation identity, defect links (R35, R48, R53, R55, R38)

Applied in Alex's directed order R35 → R48 → R53 → R55 → R38,
after his Checkpoint 4 direction (pb-mwa9ge5j).

- **R35 — D3-CANON-1 qualified; duplicate keys moved to the
  parse layer (register's correction, both halves).** (a) The
  headline claim "EXACT content — exactly as authored, code point
  for code point" is retired: the procedure now claims byte-exact
  identity over the canonical serialisation, strings and keys
  unnormalised, numbers and member order canonical by scheme,
  and states it is NOT a digest over the entries exactly as
  authored. (b) Duplicate exact keys: rejected by the record
  parser, recursively at every object level, before
  canonicalisation; a last-value-wins parser cannot be used for
  record structures; canonicalisation's loud failure is retained
  as backstop, not mechanism. Status: implemented.
- **R48 — the exclusion boundary made mechanical.** The digest
  excludes exactly the content-identity fields (the digest value
  itself; any covered field whose value is that digest or one
  derived from it), per entry, over every covered entry, and
  nothing else: entry identities, ordering positions and all
  content fields are covered; the default for any unlisted field
  is COVERED; excluding more changes the procedure and forfeits
  the identifier. Status: implemented.
- **R53 — consumption binding (REQ-C-3).** The evaluation
  record cites at issuance the record identity (iii), the
  consumed-reference identity (iv) and the coverage point it
  folded; the evaluator consumes exactly that record as an
  identity-bound snapshot; a presented record differing in
  contents, ordering or coverage fails verification against the
  identified record — never a silent re-target; a modified
  stream invalidates verification rather than changing the
  evaluation's basis. Checked against R48 at the same site:
  verification re-derives (vi) under R48's boundary, so a
  differing record mismatches by construction. Status:
  implemented.
- **R55 — REQ-H-3 supersession annotation.** The annotation is
  now specified as a separate identity-bearing addition under
  C-3 (vi)'s append lineage: own identity, new content identity
  citing its predecessor, links verdict → ruling; the original
  verdict's content and identity unchanged; reports show both
  the original and the annotation, never the annotation in
  place of the original. Status: implemented.
- **R38 — REQ-H-6 LINK entries (Alex's mechanism, from the
  register).** New appended entry kind: LINK — names the defect
  identity, the linked instance/evaluation identity, and the
  link kind; later-created affected evaluations link in without
  mutating the creation entry; H-4's reciprocity is the pair
  (evaluation's citation + the LINK entry). Acceptance fixture
  (v) added. R58 remains folded into R38 — not separately
  implemented. Status: implemented.
- **Consistency review:** the only surviving "exactly as
  authored" wording is inside R35's restatement, expressly
  negated; §23's historical summary of R32 was examined and
  left (history is never edited); H-4's "links in both
  directions" acceptance is now mechanically satisfiable via
  LINK entries; C-3 (vi)'s append-lineage language and R55's
  annotation agree (new content identity, predecessor cited).
- **Canonicalisation test plan (for Stage 6C / R49):** executed
  then, not now — composition-distinct keys produce distinct
  digests; duplicate exact keys rejected at parse, recursively;
  no silent merging or normalisation anywhere in the path.

## Stage 5 REWORK — R48 and R38 only (Alex's direction, pb-mwa9mpq7)

- **R48 — exclusion rewritten as a schema path allowlist.**
  The value-based exclusion (a field excluded iff its value is
  or derives from the digest) is REPLACED: the digest input is
  the covered entry set only; the citation envelope is
  structurally separate from the entry set (not an entry, no
  envelope field serialised); within each entry exactly three
  named top-level paths are excluded where present —
  `content_identity`, `predecessor_content_identity`,
  `extends_content_identity`; same-named keys inside a content
  payload are covered; every other field is covered, including
  a content field whose value coincidentally equals the digest
  or a derivative — exclusion is by path only, values never
  inspected. Status: implemented (rework).
- **R38 — reciprocity completed in H-6 for both orders.** (a)
  Evaluation first, defect later: creation entry references
  the existing evaluation; an identity-bearing reciprocal
  citation is appended to the evaluation record under C-3
  (vi)'s lineage (own identity, new content identity citing
  its predecessor; original content, verdicts and earlier
  content identities preserved). (b) Defect first, evaluation
  later: the evaluation cites the defect at issuance; a LINK
  entry is appended to the defect record. The evaluation-side
  append the Checkpoint 5 letter flagged as resting on C-3
  (vi)'s general lineage is now NAMED in H-6 itself.
  Acceptance fixture (vi) added for the evaluation-first path
  (fixture (v) already covers defect-first). Status:
  implemented (rework).
- R35, R53, R55 and all unrelated requirements untouched in
  this rework, per the direction. v0.7 re-verified immutable.

## Blueprint Stage 6 — Acceptance fixtures (executed)

Harness fixtures-v08/harness.py v1.0 (SHA-256 e7bf0c88…),
results in fixtures-v08/FIXTURE-RESULTS.md and results.json
(SHA-256 189a0d59…). 24 fixture cases executed in Alex's
sequence — R62 distinct first, then creation (R40, R47, R63),
evidence (R44, R52), canonicalisation (R49), evaluation and
reporting (R54, R56, R57, R64, R65), checker/preservation
(R60, R61) — 24 PASS, 0 FAIL. Every fixture is implemented,
executed and passed; NONE is independently verified (Alex's
review pending). R44's fixture landed and passed, so R44 is
no longer carried open on that ground. The working revision
was not modified by this stage (still 3e053efc…); v0.7
re-verified immutable (a14cad05…). Fixture-strength notes
and the R49 number-scope note are recorded in the results
document itself, not hidden.

## Stage 6 REWORK — targeted fixture-quality corrections (Alex pb-mwaa3jri)

Harness v1.0 preserved (harness-v1.0.py, e7bf0c88…); harness
v1.1 (20a6767f…) corrects exactly the points named: FX-R40e,
FX-R40c, FX-R47a, FX-R63b and FX-R64 replaced with fixtures
exercising actual procedures (instance classification,
creation-entry validation, judge validation, entry
declaration validation, report validation with negative
cases); FX-R49d added — ECMAScript number formatting
exercised against RFC 8785's example values, with the
conformance label corrected (subset named, full conformance
not claimed); results.json restructured to carry harness
identity, Python version and the exact execution command,
and published whole as an artefact. Results document
Revision 2 (FIXTURE-RESULTS-R2.md) states the test boundary
explicitly: fixtures exercise reference procedures written
from the spec; no production evaluator is certified. Re-run:
25 cases, 25 PASS, 0 FAIL (Python 3.12.3, `python3
harness.py`). Unaffected fixtures untouched in substance and
re-executed. Working revision unchanged (3e053efc…); v0.7
immutable (a14cad05…).

## Stage 6 — two final corrections (Alex pb-mwaa80m3)

(a) FX-R40e negative input corrected: the bearer key is now
OMITTED entirely ({"origin": "rule-instantiation"}), not
present-with-null; classification unchanged ("machinery
defect"), derived from the absent-key input. (b) The harness
jcs() docstring relabelled: a limited reference serialiser
for the tested subset, explicitly NOT a fully conforming
RFC 8785 implementation; the integer-branch divergence from
the RFC's IEEE-754 number model is named in the source.
Harness v1.2 (89dc0e50…); v1.1 preserved. Re-run: 25 cases,
25 PASS, 0 FAIL. Results document Revision 3. Working
revision and v0.7 untouched.

## Blueprint Stage 7 — Traceability reconciliation

Stage 6 APPROVED and Stage 7 AUTHORISED by Alex
(pb-mwaab9p8). Deliverables: D3-V08-TRACEABILITY.md (every
slot R33–R65 reconciled to exactly one disposition: 31
active findings — 15 TEXT and 2 STATUS implemented in the
working revision, 14 FIXTURE findings executed via 25
harness cases, 25/25 PASS — plus R58 withdrawn into R38 and
R59 numbering-history only); FIXTURE-REGISTER.md (generated
mechanically from results.json). Controls recorded in the
reconciliation: R44 CLOSED on its landed passing fixture;
R62 fixture-only (NO DEFECT FOUND is not satisfiability);
proposed requirements remain PROPOSED; UX-1…UX-5 remain
UNRESOLVED; independent verification of the v0.8 package
explicitly PENDING Alex's Stage 7 review. Recorded
limitations: R38's spec-text fixtures (v)/(vi) and R53's and
R55's mechanisms are specified-not-executed by the harness;
R49's serialiser is a limited reference implementation.
Working revision unchanged (3e053efc…); v0.7 immutable
(a14cad05…).

## Stage 7 correction — R48 traceability entry (Alex pb-mwaah8ga)

The reconciliation's R48 entry overstated fixture coverage
("CANON-1 mechanics exercised by the FX-R49 group"). The
FX-R49 cases do not exercise R48's exclusion rule. The entry
is corrected to state: the R48 text correction is
implemented and approved (Stage 5 rework review), and its
specific exclusion-boundary behaviour — the three excluded
top-level paths, the envelope boundary, nested same-named
payload keys remaining covered, digest-equal content values
— has NO dedicated executed fixture. Nothing else changed:
specification, harness, results and fixture register are
untouched, as are all other findings. Fresh reconciliation
snapshot published under a new package id.

## D3 FINAL REVIEW — DISPOSITION (Alex pb-mwaanaks-i-6a3u, ⟦ALEX-FINAL⟧)

**D3 v0.8: APPROVED WITH STATED CONDITIONS**, at SHA-256
3e053efc97d876d50f649eb0b4c8c740ab6085314aa54f9132fdf33e243d97d4
— the exact hash of the working revision as delivered.
Conditions: (A) UX-1…UX-5 remain open; PROPOSED/UNRESOLVED
requirements do not become binding through this approval
(checker independence unresolved; the proposed taxonomy is
not endorsed by its fixtures; NO DEFECT FOUND does not
establish satisfiability; mechanical checking of
judgement-based conditions unsettled). (B) Outstanding
fixture gaps remain visible and must be completed before the
affected mechanisms are claimed mechanically verified: R38
(H-6 fixtures (v)/(vi) specified, unexecuted), R48 (no
executed fixture for the exclusion boundary), R53
(consumption binding untested), R55 (annotation mechanism
untested). (C) R49's canonicalisation is a limited reference
implementation; no full RFC 8785 conformance claim approved.
(D) The 25/25 fixture result is accepted as the Stage 6
harness's result; it is not production verification or
semantic approval. Independent verification: PENDING — the
next required gate, against this exact approved revision.
Stage 2: NOT AUTHORISED (separate decision). v0.7 and
EXECUTION-CONTRACT-v0.1 unchanged. No further specification
edits authorised by this disposition. Recorded by Remmy on
Alex's instruction; the specification itself was not
modified.
