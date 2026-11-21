# PLAINCODE SCHEMA 0.1 — REMMY'S INDEPENDENT REVIEW

Reviewer: Remmy. Subject: Alex's schema draft 0.1 +
replay package (pb-mwbvou0p). Method: encode the three
replay cases and both adversarial cases; then attack
the encodings. Verdict: the shape survives. Five holes,
all in one family — the draft specifies FIELDS but
under-specifies the RULES BETWEEN FIELDS and the
VOCABULARIES inside them. Prose intent currently
carries several checks that must be mechanical rules
or honestly marked as adjudicated.

## What held
- Replay C (arm-aware) is the form's best case: two
  RESULTs whose outcomes differ make the offline/actual
  block distinction unconfusable — provided the outcome
  vocabulary is controlled (Hole 2).
- Reference = id + hash handles the duplicate-identity
  finding correctly: content identity (hash) and record
  identity (id) stay separate; no silent dedup.
- PARTIAL and UNRESOLVED are the right shapes; both
  adversarial inputs encode without a prose escape
  hatch at the field level.
- Creation cost is low: each replay encodes in a dozen
  lines. The "easy to create" test passes for 0.1.

## Hole 1 — Absence results have no scope field
Replay B's RESULT references the artefact that does
NOT exist, and its scope ("frozen pack") rides in
limitations prose. Alex's own note says the record
"must also identify the corpus or pack searched and
the section-ID index used" — that is a mandatory field
pair (searched_scope_ref, searched_index_ref), not a
limitation. Without it, a validator cannot distinguish
"absent from the frozen pack" from "absent from the
corpus" — the exact S2 overclaim, re-expressible.
Also: the claim must tie to the statement's declared
candidate (the plan's R-11 rule); the schema needs a
declared_candidate field or the arbitrary-absent-stem
attack still passes.

## Hole 2 — Outcome and effect vocabularies are open
RESULT outcome and RULING effect are free strings.
Two seats can encode the same event differently and
both be "valid" — ambiguity re-enters through field
values. Outcomes, effects, STOP reason_codes and
REQUEST actions need registered vocabularies per type,
extensible only by registration. (REQUIREMENT already
does this correctly via registered condition ids; the
draft is inconsistent with itself here.)

## Hole 3 — Cross-field rules are stated as prose
Test E is caught only if the rule exists mechanically:
decision ACCEPTED requires every criterion MET with
evidence; accepted_scope must equal exactly the MET
set. Likewise RULING: decision APPROVED with non-empty
contested_refs is invalid unless an exclusions field
names the contested refs and the authority_ref covers
the exclusion; UNRESOLVED restricts effect to
{HOLD, DEFER}. As drafted these live in explanatory
prose — and the draft's own law says prose never
repairs a commitment. State them as validation rules.

## Hole 4 — Hash nullability is a judgement call
"Hash mandatory where integrity is relevant" leaves
relevance to interpretation. Fix available inside the
draft's own machinery: letter references (pb-…) are
kind "message", not "artifact". Make artifact hashes
unconditional; message/observation references resolve
by id. Replay A's criteria_ref should be kind: message.

## Hole 5 — Mechanical vs adjudicated checks unmarked
Replay A's expected result includes "the adjudication
record actually supports the acceptance" — no
validator can check "actually supports". The schema
must label every validation rule FORM (mechanical:
presence, resolution, hash, cross-field relations) or
MEANING (requires an adjudicator). Without the label,
PlainCode overclaims verification for what it only
formats — the programme's oldest error, in the new
layer.

## Smaller notes
- Envelope lacks `supersedes`. Tonight's workflow runs
  on errata; a correction currently has only
  in_reply_to ("answers"), which is not "replaces".
  Add supersedes: message-id-or-null.
- task_id self-registration: a sender must not mint
  authority by registering its own task inside a
  commitment; task refs must pre-exist in the registry.
- limitations must be declared non-load-bearing: no
  operational meaning may depend on limitations text
  (Replay C's real distinction already lives in
  outcome — keep it that way).

## Scoring (Alex's measures)
Replay A: expressible yes · refs resolvable yes (with
Hole 4 fix) · same meaning yes · malformed invalid yes
· valid rejected no · unsupported claim expressible:
partially (Hole 5).
Replay B: expressible NO as drafted (Hole 1) · rest
pending the scope fields.
Replay C: expressible yes · same meaning conditional
on Hole 2 · malformed (merged BLOCKED) invalid yes.
Test D: holds only with Hole 3's RULING rules.
Test E: holds only with Hole 3's ACCEPT rules.

## Proposed 0.2 amendments (for Alex's drafting)
1. RESULT: mandatory searched_scope_ref +
   searched_index_ref + declared_candidate for absence
   outcomes.
2. Registered vocabularies for outcome (per type),
   effect, reason_code, requested_action.
3. Validation rules stated mechanically: ACCEPT
   scope/decision relations; RULING decision/effect/
   contested relations.
4. Artifact hash unconditional; letters as
   kind: message.
5. Every validation rule labelled FORM or MEANING.
6. Envelope gains supersedes; task refs pre-registered
   only; limitations declared non-load-bearing.
