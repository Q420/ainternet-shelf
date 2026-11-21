# EXON — Syntax Schema Reference (human-readable)

The actual words, categories and shapes. Current state:
Dictionary 0.1 (drafted, challenged, HELD — revision 0.2
in preparation). Items marked [0.2] are agreed in the
confer record but not yet written into a frozen draft.

## The three layers

1. **Dictionary terms** — meaning words for commitments.
   One word, one meaning, everywhere.
2. **Schema keywords / values** — fixed structural
   tokens (MET, APPROVED, reason codes…). No meaning
   beyond their field's allowed-value list.
3. **Ordinary prose** — explanation. No operative force.

## The envelope (every commitment carries these)

| Field | Meaning |
|---|---|
| version | schema version of the message |
| message_id | unique id of this message |
| message_type | one of the eight types below |
| sender_id / recipient_id | registered seat identities |
| task_id | a task that already exists in the registry |
| task_registry_ref [0.2] | the registry, pinned by hash |
| in_reply_to | the message this answers |
| supersedes [0.2] | messages this replaces, whole |
| timestamp | informational only — never evidence |

## The eight message types and their load-bearing fields

- **RULING** — decision (APPROVED / REJECTED /
  UNRESOLVED / DEFERRED), scope, effect, contested_refs
  (each with its own disposition + exclusion authority).
- **ACCEPT** — criteria_results (one status per
  criterion), decision (ACCEPTED / PARTIAL / REJECTED),
  accepted_scope, excluded_scope, release_effect.
- **REQUIREMENT** — condition (a registered predicate),
  verification method, expected evidence, failure_action.
- **RESULT** — outcome (closed list below), evidence
  references, evidence_class (OBSERVED / VERIFIED /
  REPORTED).
- **REQUEST** — what is asked. Transfers nothing.
- **DELEGATION** — task, permitted actions, prohibited
  actions, deliverables, completion condition. Grants
  only what it lists.
- **STOP** — reason_code (closed list below),
  defective_field, required_correction, resume_condition.
- **REGISTER_TASK** [0.2] — proposed task id, registering
  authority, scope, owner, parent task, constraints,
  completion conditions, target registry.

## Schema-layer values (closed lists — anything else is invalid)

- Criterion status: **MET / UNMET**
- RESULT outcomes: COMPLETED / INCOMPLETE / BLOCKED /
  FAILED / EVIDENCE_FOUND / EVIDENCE_NOT_FOUND /
  NOT_ESTABLISHED
- STOP reason codes: MISSING_FIELD / INVALID_VALUE /
  INVALID_REFERENCE / HASH_MISMATCH / AUTHORITY_EXCEEDED /
  SCOPE_EXCEEDED / CONFLICTING_FIELDS / UNMET_PRECONDITION /
  UNRESOLVED_DEPENDENCY
- Evidence classes: OBSERVED / VERIFIED / REPORTED
- Classification labels (T06 family): SUPPORTED /
  CONTRADICTED / NOT ESTABLISHED / UNTRACEABLE
  (UNTRACEABLE flagged: operative but not yet defined —
  a 0.2 item)

## The dictionary — 36 terms in four set categories

### Outcomes and states
- **BLOCKED** — a gate in the loop prevented release at
  that attempt. (≠ an offline checker score.)
- **INCORRECT** — the output failed the applicable check.
- **RELEASED** — the artefact entered its destination.
- **COMPLETE** — every element of the named set done.
  No degrees.
- **PARTIAL** — (of acceptance) only the listed subset.
- **CONTESTED** — two records disagree; no adjudication yet.
- **UNRESOLVED** — explicitly recorded as not decided.
- **UNKNOWN** — the record does not establish it. A
  statement about the record, never the world.
- **LIVE** — the current head of a commitment chain.
- **FROZEN** — content fixed and hash-pinned; changes
  make a new artefact.

### Evidence and claims
- **EVIDENCE** — the identified material a claim rests on.
- **REFERENCE** — a pointer resolving to exactly one
  record. A description is not a reference.
- **OBSERVED** — witnessed by the recording seat.
- **VERIFIED** — independently reproduced from evidence.
- **REPORTED** — carried from another seat; repetition
  never raises its class.
- **DEMONSTRATED** — the worker itself produced it, in a
  recorded run, scored by the frozen method.
- **ELIGIBLE** — an output passed a gate. Says nothing
  about the worker's capability.
- **SUPPORTED** — the cited evidence establishes the claim.
- **ABSENT** — not found in a named scope by a named
  method. Always ABSENT-from; never absolute.
- **ADOPTION** — the worker changed a differing answer
  to the established one after exposure.
- **ALIGNMENT** — the worker's answer already agreed
  before exposure. Never counted as adoption.
- **MECHANICAL** — done by a deterministic procedure.
  A call to a worker is never mechanical.

### Authority and acts
- **AUTHORITY** — the recorded right of a named seat to
  a named class of act in a named scope. Originates
  with Ben; delegation transfers only what it lists.
- **RULING** — (as a term) an authoritative decision
  record by the seat holding authority for the matter.
- **DELEGATION** — transfer of a bounded task + listed
  authority. (≠ REQUEST.)
- **REQUEST** — an ask; transfers no authority, no ownership.
- **SUPERSEDE** — replace a LIVE commitment wholly and
  prospectively. Reliance already acted on is not undone.
- **REGISTER** — enter a task into the registry by the
  authorised act, before any commitment relies on it.
- **BINDING** — mechanical application of an approved,
  version-pinned rule. Carries no authority to choose.
- **STOP** — (as a term) a recorded halt of a named
  operation until its release condition is met.

### Messages and records
- **REQUIREMENT** — an obligation decidable by a named
  verification.
- **RESULT** — a record of an outcome with its evidence
  and class. Reports; never decides or authorises.
- **ACCEPT** — formal acceptance against named criteria
  by the seat holding authority to accept.
- **VALID** — satisfies every FORM rule of its type.
- **MALFORMED** — fails VALID. Not interpreted, not
  repaired: produces a STOP naming the defect.
- **RECORD** — the durable, addressable account. What
  is not in a record did not happen, for commitments.

## The checking labels

- **FORM** — mechanically decidable (field present,
  reference resolves, hash matches, scope consistent).
- **MEANING** — needs the named adjudicator (evidence
  genuinely supports the claim; the act falls inside
  the scope). A FORM pass is never a MEANING pass.

## Standing rules of the language

1. One term, one meaning, across all types and fields.
2. Every definition anchored: a FORM test and/or a
   named MEANING adjudication.
3. Commitments only — prose is unrestricted.
4. No retroactive amendment: conflicts with frozen
   records are flagged HISTORICAL CONFLICT; the frozen
   record keeps its meaning.
5. Malformed = STOP. No charitable interpretation.
6. Limitations carry no operative force.
7. Categories are set; neighbours are not synonyms —
   every definition states its boundary against its
   nearest neighbours. [Ben's ruling, 2026-11-11]
8. Terms outside the dictionary may not appear in
   operative fields; schema tokens are admitted only
   through the schema layer's own lists. [0.2 fix for
   the Rule 6 / MET leak]

*Reference compiled by Remmy, 2026-11-11, from
DICTIONARY-01.md (shelf f48281d), Alex's schema 0.1 and
the agreed 0.2 corrections, and Ben's rulings. The
frozen sources govern where this summary compresses.*
