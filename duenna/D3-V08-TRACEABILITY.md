# D3 v0.8 — STAGE 7 TRACEABILITY RECONCILIATION

Basis: approved Correction Matrix r4 (SHA-256 f6ddf789…) ·
Round 7 register (SHA-256 d71d0a79…) · frozen v0.7 (canonical
28718d26…, file a14cad05…, re-verified immutable at this
reconciliation) · working revision v0.8 (SHA-256 3e053efc…,
unchanged since Stage 5 rework approval) · change record
D3-V08-CHANGE-RECORD.md · fixture register (Stage 6, harness
v1.2, 25/25 PASS).

Every register slot R33–R65 is reconciled to exactly one
disposition below: 33 slots = 31 active findings + R58
(withdrawn) + R59 (numbering-history only). Kinds across the
31 active: 15 TEXT · 2 STATUS · 14 FIXTURE (the matrix's
counts, unchanged).

Controls honoured throughout: R44 closed only on its landed,
passing fixture · R58 withdrawn into R38 · R59 numbering
history only · R62 fixture-only (NO DEFECT FOUND is not proof
of satisfiability) · proposed requirements remain PROPOSED ·
UX-1…UX-5 remain UNRESOLVED · fixture success is never
promoted into normative approval · independent verification
of the v0.8 package remains explicitly PENDING (Alex's
Stage 7 review) — Alex's approvals of Stages 1–6 are recorded
as checkpoint acceptances of reported evidence, not as this
package's independent verification.

Status vocabulary: a finding is "implemented" when its
correction stands in the working revision (text/status) or
its fixture is built (fixture kind); "executed/passed" apply
to fixtures as run; nothing below claims "independently
verified".

## The reconciliation

- **R33** (TEXT, accepted proposal) — REQ-D-3, derivation
  step (0). Implemented (Stage 4). Fixture: none assigned;
  the admission rule is exercised inside the fold engine used
  by FX-R44/FX-R52. Limitation: no dedicated fixture.
- **R34** (TEXT) — REQ-A-1 Behaviour/Outputs. Implemented
  (Stage 3, register's correction; matrix-row erratum stands
  in the change record). Fixture: none assigned.
- **R35** (TEXT) — REQ-C-3, D3-CANON-1 (identity claim;
  duplicate-key layer). Implemented (Stage 5). Fixture: the
  duplicate-key mechanism is exercised by FX-R49b
  (registered under R49). Limitation: none outstanding.
- **R36** (TEXT) — REQ-K-3 (3). Implemented (Stage 3,
  register's correction). Fixture: the never-instance-free
  CREATION rule is exercised by FX-R63b (registered under
  R63).
- **R37** (TEXT) — REQ-K-3 (2). Implemented (Stage 3,
  register's correction). Fixture: block contiguity and
  order exercised by FX-R63a (registered under R63).
- **R38** (TEXT) — REQ-H-6 (LINK-entry mechanism; reciprocity
  completed in both creation orders in the Stage 5 rework).
  Implemented; approved by Alex in the rework review.
  R58 is folded here — no separate implementation exists.
  Fixture: acceptance fixtures (v) defect-first and (vi)
  evaluation-first are SPECIFIED in REQ-H-6's acceptance
  text; they were not in Stage 6's harness group list and
  are recorded as specified-not-executed. Limitation: that
  non-execution.
- **R39** (TEXT) — REQ-A-1 (bound-rule/instance boundary).
  Implemented (Stage 3). Fixture: none assigned.
- **R40** (FIXTURE) — REQ-A-1/A-2/A-3 acceptance. Fixtures
  FX-R40a–e executed, all PASS (FX-R40c and FX-R40e in their
  reworked procedural forms, Stage 6 rework + corrections).
  Implemented + executed + passed.
- **R41** (STATUS) — REQ-B-1 source/provenance line.
  Implemented (Stage 1): CONVERGED → PROPOSED on D3-R21
  alone; the pre-existing-evidence declaration is NOT
  promoted. Fixture: none (status correction).
- **R42** (TEXT) — REQ-K-1 (B-1 well-formedness at binding).
  Implemented (Stage 2). Guard held: K-1's satisfiability
  semantics (UX-4) untouched. Fixture: outcome side covered
  by R62's fixture (below).
- **R43** (TEXT) — REQ-B-2 (establishment vs transition).
  Implemented (Stage 4). Fixture: exercised within FX-R44's
  fold (registered under R44).
- **R44** (FIXTURE) — REQ-B-2 mixed channel, reverse
  direction. Fixture FX-R44 executed, PASS (artefact
  PROGRESS + event SATISFACTION → SATISFIED, stream
  unchanged). CLOSED on the basis of its landed, passing
  fixture, per Alex's Stage 7 control. No longer carried
  open.
- **R45** (STATUS) — REQ-C-2 source line + conditional
  reliance sentence. Implemented (Stage 1), both-or-neither
  with R41. Fixture: none (status correction).
- **R46** (TEXT) — REQ-C-1 (fold begins at the CREATION
  entry). Implemented (Stage 3). Fixture: the fold-side
  behaviour is exercised by FX-R47b (registered under R47).
- **R47** (FIXTURE) — REQ-B-6/C-1/C-2 acceptance. Fixtures
  FX-R47a–c executed, all PASS (FX-R47a in its reworked
  validation form). Implemented + executed + passed.
- **R48** (TEXT) — REQ-C-3, D3-CANON-1 exclusion boundary.
  Implemented (Stage 5), rewritten in the rework as a
  schema path allowlist (content_identity,
  predecessor_content_identity, extends_content_identity;
  envelope structurally separate; values never inspected);
  approved by Alex in the rework review. Fixture: NONE
  executed for the exclusion boundary itself (corrected at
  Alex's Stage 7 review, pb-mwaah8ga — an earlier wording
  credited the FX-R49 group with coverage it does not have).
  The FX-R49 group exercises CANON-1's canonicalisation —
  Unicode composition, duplicate-key rejection, member
  order, canonical numbers — but does not test the exclusion
  rule: not the three excluded top-level paths, not the
  citation-envelope boundary, not identically named nested
  payload keys remaining covered, not legitimate content
  values equal to the digest or a derivative. Limitation:
  R48's exclusion-boundary behaviour has no dedicated
  executed fixture; the correction stands as implemented
  text, approved in the rework review, unexecuted.
- **R49** (FIXTURE) — D3-CANON-1 fixture coverage. Fixtures
  FX-R49a–d executed, all PASS. Limitation (accepted,
  labelled in source and results): the harness serialiser
  is a limited reference implementation — number formatting
  verified against RFC 8785's example values; integer branch
  departs from the RFC's IEEE-754 model; extreme subnormals
  and the full string-escaping repertoire unexercised. Full
  RFC 8785 conformance is NOT claimed.
- **R50** (TEXT) — REQ-B-2 state-derivation paragraph +
  REQ-D-2 requirement sentence (derivation basis: closed
  record PLUS B-2 determinations, clarification not
  widening). Implemented (Stage 4). Fixture: none assigned.
- **R51** (TEXT) — REQ-D-3 step (2)/(4) (availability at fold
  position; channel (ii) from the start). Implemented
  (Stage 4). Fixture: exercised within FX-R44 and FX-R52
  (registered under those findings).
- **R52** (FIXTURE) — REQ-D-3 artefact-first terminal lock.
  Fixture FX-R52 executed, PASS. Implemented + executed +
  passed.
- **R53** (TEXT) — REQ-C-3 consumption-binding paragraph
  (evaluator consumes the identified closed record as a
  snapshot; mismatch fails verification). Implemented
  (Stage 5). Fixture: none executed — no harness fixture
  covers the consumption binding. Limitation: that
  non-execution, recorded plainly.
- **R54** (FIXTURE) — REQ-E-3 ambiguous/duplicate matching.
  Fixtures FX-R54a/b executed, PASS.
- **R55** (TEXT) — REQ-H-3 supersession annotation as a
  separate identity-bearing addition. Implemented
  (Stage 5). Fixture: none executed. Limitation: the
  annotation mechanism stands on text; no harness fixture.
- **R56** (FIXTURE) — REQ-E-6 prohibited substitutions +
  self-verification. Fixture FX-R56 executed, PASS. Guard:
  R56 does not resolve UX-1 (checker independence).
- **R57** (FIXTURE) — REQ-G-2 honesty credit independent of
  completion. Fixture FX-R57 executed, PASS.
- **R58** — WITHDRAWN by Alex as duplicating R38; folded
  into R38's REQ-H-6 mechanism. No separate disposition
  exists or is claimed. Identifier never reused.
- **R59** — NUMBERING-HISTORY ONLY. No final referent; the
  R60/R61 renumbering is recorded in the matrix and the
  change record. No correction or fixture attaches to R59.
- **R60** (FIXTURE) — REQ-I-2 checker-contract properties.
  Fixture FX-R60 executed, PASS (all five properties,
  including failure paths and the unpinned-version
  rejection). Guard: the fixtures do not promote the D3-R15
  dependency clause, which remains PROPOSED.
- **R61** (FIXTURE) — REQ-I-3 preservation outcomes
  (corruption case added). Fixture FX-R61 executed, PASS
  (deleted and corrupted payloads → INDETERMINATE /
  RECORD-PRESERVATION; never a pass; never AGENT).
- **R62** (FIXTURE) — REQ-K-1 outcome (i), NO DEFECT FOUND.
  Fixture (iv) stands in REQ-K-1's acceptance text; harness
  fixture FX-R62 executed, PASS, run as the distinct
  downstream K-1/B-1 test. Fixture-only correction: the
  outcome records absence of a demonstrated defect and is
  NOT proof of satisfiability (UX-4 untouched).
- **R63** (FIXTURE) — REQ-K-3 coverage. Fixtures FX-R63a/b
  executed, PASS (FX-R63b in its reworked validator form).
  Guard: not an endorsement of the proposed K-3 taxonomy.
- **R64** (FIXTURE) — REQ-K-4 checker verdicts as REPORTED
  evidence. Fixture FX-R64 executed, PASS (in its reworked
  validator form, including omitted-caveat, unrecorded-
  reliance and wrong-class failures). Guard: confers no
  checker independence; UX-1 untouched.
- **R65** (FIXTURE) — REQ-K-4 report content/provenance
  integrity. Fixture FX-R65 executed, PASS. Fixture-only:
  introduces no new normative D3 requirement (Alex's settled
  disposition).

## Package status (Blueprint §7 vocabulary)

- Proposed v0.8 revision: drafted and implemented (Stages
  1–5 + Stage 5 rework, all Alex-approved at checkpoint).
- Fixtures: implemented and executed; 25/25 PASS (Stage 6,
  approved by Alex after two rework rounds).
- Change record: complete through Stage 7.
- Traceability: this document — every slot reconciled.
- Independent verification of the v0.8 package: PENDING
  Alex's review of this Stage 7 delivery.
- D3 approval: NOT given; remains Alex's separate decision.
- Stage 2 (programme): not begun; execution NOT authorised.
- v0.7 and the execution contract: untouched throughout.
