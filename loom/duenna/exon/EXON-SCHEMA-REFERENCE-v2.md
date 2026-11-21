# EXON — how it's built and how it's used (plain version)

Refreshed 2026-11-11 to match **Dictionary 0.4** (draft,
in challenge — not frozen yet). The dictionaries
govern; this is the readable map of them.

## What EXON is for

The seats talk to each other in it — not to Ben. It's
for the load-bearing messages: rulings, acceptances,
results, delegations, stops, corrections. The point:
a receiver can tell *exactly* what is authorised,
claimed, or decided without interpreting anyone's
prose. If a message is malformed, the answer is a
STOP — nobody guesses what the sender "meant."

## The three layers

1. **The dictionary** — 38 meaning-words (below). One
   word, one meaning, everywhere it appears.
2. **The schema** — structural tokens and field
   values (MET, APPROVED, the reason codes…). A token
   means only what its field's list says.
3. **Ordinary prose** — explanations, colour,
   apologies. Zero operative force. Prose can never
   rescue a broken commitment.

Ben's two laws sit over all of it: the dictionary IS
the law book (out-of-definition use is invalid) — and
after a breach comes guidance, not punishment: a flag,
a second look, a correction.

## The envelope (every message carries these)

- **protocol_version** — which EXON version.
- **message_id** — this message's own identity.
- **message_type** — one of the nine types below.
- **sender_id / recipient_id** — who's talking.
- **task_id + task_registry_ref** — the task it acts
  under, and the registry version, pinned by hash
  {kind, id, hash}. No silently using "latest."
- **in_reply_to** — what it answers (changes nothing
  by itself).
- **supersedes** — a whole earlier commitment it
  replaces (only RULING, ACCEPT, REQUIREMENT,
  DELEGATION may carry it).
- **timestamp** — informational only. Never proof of
  order, authority, or anything else.
- **⚑** — the flag marker. A boolean. If it's on, a
  flag block rides with the message (see below).

## The nine message types

- **RULING** — a decision by the seat holding
  authority. decision: APPROVED / REJECTED /
  UNRESOLVED (open, no trigger) / DEFERRED (must name
  its decision_trigger — what it's waiting for).
- **ACCEPT** — formal acceptance against criteria.
  Every criterion gets MET / UNMET / UNASSESSED, and
  the three decisions are locked to the scopes:
  ACCEPTED = everything MET, full release;
  PARTIAL = a proper subset of MET criteria only,
  released with exclusions; REJECTED = nothing
  accepted, no release. Any other combination is
  malformed.
- **REQUIREMENT** — an obligation: an owner, a
  bounded observable condition, a named verification,
  the evidence it should produce, and a failure_action
  (HALT_AND_STOP / RECORD_AND_CONTINUE /
  ESCALATE_TO_OWNER). Carries no evidence fields of
  its own — evidence comes later, in results.
- **RESULT** — a report. outcome is the FINAL outcome
  of the run: COMPLETED / INCOMPLETE / BLOCKED /
  FAILED / EVIDENCE_FOUND / EVIDENCE_NOT_FOUND /
  NOT_DETERMINED. If a gate blocked an attempt and a
  retry fixed it, the blocked attempt lives in
  attempt_events — the outcome still says how the run
  ended. One field, one job: that's the fix for the
  night "blocked" meant two things at once.
- **REQUEST** — an ask. Carries no authority fields;
  if it tries to, it's malformed.
- **DELEGATION** — hands over a task: task_ref, the
  delegate as owner, permitted and prohibited
  actions, deliverables, the completion condition,
  and the delegator's authority_ref. Grants only what
  it lists — asking is not authorising.
- **STOP** — halts a named operation. reason_code
  from the closed list of nine; resume_condition (what
  must be true) kept separate from
  release_authority_ref (who may lift it) — a
  condition being met never lifts a stop by itself.
- **REGISTER_TASK** — proposes a new task into the
  registry: proposed id, scope, owner, constraints,
  completion conditions, and the target registry —
  pinned even though no task exists yet.
- **CORRECTION** — repairs a wrong record. Names the
  target record and claim, the wrong value verbatim,
  and either the corrected value or withdrawn (never
  both). Says who wrote the original, who's
  correcting, on what authority, on what basis — and
  gives every known reliance on the wrong value a
  disposition: STANDS / REASSESS / RETRACTED /
  PENDING (PENDING must say what it's waiting on).
  The original is never edited; the correction is a
  new record linked to it.

## Classifications (RESULT only, never outcomes)

- **SUPPORTED** — the evidence establishes the claim.
- **CONTRADICTED** — the evidence establishes it false.
- **NOT_ESTABLISHED** — the procedure ran to the end
  and did not establish it. Silence after a full run.
- **UNTRACEABLE** — the procedure couldn't even trace
  it inside the pinned corpus. Not the same as absent,
  unknown, or unresolved — each of those is its own
  word with its own test.

## The flag ⚑ (Ben's symbol)

Any authorised seat can flag any record — including
its own. Raising one needs no proof, just unease.
What it creates is exactly one obligation: an
independent second look, recorded. It does not halt
anything, invalidate anything, or change any evidence
class. Flags on the same claim merge into one
obligation; a different claim starts a new one. Every
flag ends in exactly one of two ways: CLEARED, or
CORRECTED (by a CORRECTION record). A flag never
closes itself, and a bad-faith flag still gets its
second look — conduct is a separate matter.

## How a message actually looks

A RESULT reporting a gated run, in spirit:

    type: RESULT
    task: the v2 battery
    outcome: COMPLETED
    attempt_events: [1: BLOCKED at the gate,
                     2: released after retry]
    evidence_class: OBSERVED
    evidence: the run's results file, hash-pinned

One read tells you: the run finished, the gate bit
once on the way, and where the proof lives. Under the
old habit that same run got described three different
ways by three different fields, and we spent a night
finding out which one was lying.

## FORM and MEANING

Every rule is one or the other, and says which.
**FORM** — mechanically decidable: field present,
reference resolves, hash matches, combination legal.
**MEANING** — a named adjudicator decides: the
evidence genuinely supports the claim; the act really
falls inside the authority's scope. A FORM pass is
never a MEANING pass. (Today both are checked by the
seats by hand; the checker — Ben's "verificationist" —
is a parked idea for after the freeze.)

## The 38 dictionary terms (glosses)

**Outcomes and states:** BLOCKED (a gate stopped the
release at that attempt) · INCORRECT (failed its
check) · RELEASED (entered its destination — an
event, not a permission) · ELIGIBLE (passed a gate —
the permission side) · COMPLETE (every element of a
named set satisfied) · PARTIAL (acceptance of a
listed subset only — never a completeness score) ·
CONTESTED (records disagree, unadjudicated) ·
UNRESOLVED (recorded as not decided; carries no
trigger and no reliance effect) · UNKNOWN (the record
doesn't establish it — a statement about the record,
never the world) · LIVE (current head of a chain) ·
FROZEN (fixed and hash-pinned).

**Evidence and claims:** EVIDENCE · REFERENCE (a
pointer to exactly one record) · OBSERVED (witnessed
by the recording seat) · VERIFIED (independently
reproduced) · REPORTED (carried from another seat —
repetition never upgrades it) · DEMONSTRATED (the
worker produced it in a scored run) · SUPPORTED ·
CONTRADICTED · ABSENT (not found in a named scope by
a named method — always absent-*from*) · ADOPTION
(changed a differing answer after exposure) ·
ALIGNMENT (already agreed before exposure — never
counted as adoption) · MECHANICAL (a deterministic
procedure did it; a model call is never mechanical).

**Authority and acts:** AUTHORITY (a recorded right,
named seat, named act class, named scope) · RULING ·
DELEGATION · REQUEST · SUPERSEDE (whole, prospective,
reliance already acted on is not undone) · REGISTER ·
BINDING (mechanical application of a pinned rule —
carries no choice) · STOP.

**Messages and records:** REQUIREMENT · RESULT ·
ACCEPT · CORRECTION (the repair act — its
WITHDRAWN is an encoding inside it, never a
disposition of anything else) · VALID (passes every
FORM rule of its type) · MALFORMED (fails VALID —
answered with a STOP, never interpreted) · RECORD
(the durable account; what's not in one didn't
happen, for commitments).

*Compiled by Remmy from Dictionary 0.4 (shelf
3216dfb, sha fc31da8e…) and the adjudicated merged
field matrix. Human-readable summary — the
dictionary governs wherever this compresses.*
