# REMMY — REVIEW OF ALEX'S RAW-RESULT SCHEMA 0.1 (Capability Trials, Document 3 of 3)

Date: 2026-11-15. Reviewer: Remmy. Document under review:
ALEX-CAPABILITY-TRIALS-RAW-RESULT-SCHEMA-0.1-2026-11-15.md (Alex's reply to
RB-2026-11-15-32), checked against ALEX-CAPABILITY-TRIALS-CHALLENGE-SPEC-0.1
(Document 1) and the RB-32 assignment.

## Verdict: SOUND WITH FINDINGS

The schema does the job the assignment set: one immutable record per attempt,
scoreable later without re-running, capture kept strictly separate from
scoring. The findings below are corrections and tightenings, not objections.

## Confirmed against Document 1

- Failure vocabulary is verbatim: MODEL_REASONING, MODEL_INSTRUCTION,
  MODEL_FORMAT, PROVIDER_TRANSPORT, TIMEOUT_TRUNCATION, CHECKER, HARNESS,
  GROUNDING, UNRESOLVED — all nine, exact.
- Pilot arithmetic matches Document 1 (§"six distinct challenge items in
  each of the three groups"): 3 groups × 6 challenges × 3 replicates × 4
  configurations = 216.
- Configuration identity: exact_version is mandatory in every record, and
  the frozen per-record snapshot (rather than a mutable registry lookup) is
  the right call — the registry's first frozen field is honoured.
- A response never received is a first-class state (NOT_RECEIVED +
  unavailable_reason), never an empty success. Corrections are additional
  records, never silent replacements. Both match programme practice.
- The review boundary is honest: structural validation vs evidence-integrity
  checks are kept separate, in his §12 and in the boundary note.

## Findings

- F1 — Provenance objects must be required, not optional. In the challenge
  object, variant_provenance and authorship are absent from `required`, so a
  record can omit both silently. His own §4 says "Record:" — and the inner
  fields already carry the honest states (NOT_ASSESSED, UNASSIGNED, nulls).
  Make both objects required so an unresolved decision is visible in every
  record rather than missing from it. Absence should be a state, not an
  omission.
- F2 — Rationale must ride with a classification. failure_rationale is
  optional even when failure_classification is non-null, though §6's prose
  says the record preserves the rationale and its supporting evidence
  reference. Require the rationale whenever a classification is asserted
  (an if/then at the top level expresses this), and name the classification's
  evidence route — an evidence_refs entry or a dedicated field.
- F3 — Fix the attempt_id grammar now. attempt_id is an unconstrained
  string; stream-level uniqueness is correctly an acceptance check (§12),
  but the construction rule should be stated in the document before capture
  begins. His illustrative A-001-R1-QWEN shows the intended shape — promote
  it to a stated rule or a pattern.
- F4 — evidence_refs needs a stated floor. The array may be empty (the
  illustrative record ships []). My recommendation: declare empty conforming,
  explicitly — the mandatory challenge artifact_ref plus the in-record
  input/raw_response already guarantee the adjudication route — but the
  document should say so, one way or the other.
- F5 (minor) — No session/run grouping field. If the 216 attempts execute
  across more than one sitting, a run/session identifier groups records
  without timestamp archaeology. Cheap now, expensive later.
- F6 (minor) — configuration.settings is an unconstrained object. That is
  this schema's right boundary, but the document should say the harness
  freezes the settings keys (temperature, token limits, reasoning flags) —
  two configurations differing only inside settings must not silently share
  a configuration_id.
- Passing note: the $id is a placeholder domain (pulsehq.example); replace
  with the programme's shelf URI at freeze.

## Disposition requested

Schema 0.2 (or recorded amendments) accepting F1–F3 and ruling F4–F6; then
Document 2 — the A+F Pilot Rubric — is the next assignment, triggered by
RB-33: correctness/discovery scoring for A, F1 seeded-error scoring, F2
self-correction scoring, against Document 1 and the frozen schema. Paper
only; no pilot execution is authorised or sought.
