# AInglish DICTIONARY 0.1 — DRAFT FOR CHALLENGE

Drafted by Remmy from the failure record, under Ben's
direction (dictionary first). For Alex's independent
challenge; not frozen, not in force.

**Rules of the dictionary.**
1. One term, one meaning, across every message type and
   field. A term used outside its definition makes the
   commitment MALFORMED.
2. Every definition carries an operational anchor:
   FORM — a named mechanical test; MEANING — a named
   adjudication route. Where both apply, they are
   listed separately and a FORM pass never reports as
   a MEANING pass.
3. The dictionary governs commitments and load-bearing
   structured messages only. Prose is unrestricted.
4. The dictionary amends nothing retroactively. Where
   a definition conflicts with a frozen record's usage,
   the entry is flagged HISTORICAL CONFLICT: the frozen
   record keeps its meaning, the dictionary governs new
   commitments, and any change of effect follows the
   normal approval process.
5. Adjudication route, unless an entry says otherwise:
   programme matters — Alex, within his delegated
   classes; reserved matters (spend, outreach,
   publishes, accounts, Duenna rule changes) — Ben.
6. A term not in this dictionary may not appear in a
   commitment's operative fields.

## Outcomes and states

**BLOCKED** — A gate operating in the loop prevented
the artefact's release at the attempt it scored.
FORM: the run record shows the gate decision applied
before release AND the artefact absent from the
released outputs. NOT: an offline checker score of any
kind — that is INCORRECT. (The distinction this entry
exists to hold: V1 T05 Arm A vs Arm B.)
HISTORICAL CONFLICT: process-tree-v04#017 records an
instance-level usage supersedeable by Ben; frozen
records keep that meaning.

**INCORRECT** — The worker's output failed the
applicable check, whenever the check ran. FORM: a
scored record naming the check and the failure.
NOT: a claim about the worker beyond that output.

**RELEASED** — An artefact was permitted into its
destination. FORM: the destination's record names the
artefact and its hash. The consequence BLOCKED negates.

**COMPLETE** — Every element of the named set is
present or done. FORM: set enumeration with a count
that reconciles. NOT: substantially complete; no
degree of COMPLETE exists.

**PARTIAL** (of acceptance) — Acceptance of an
enumerated subset only. FORM: the accepted list is
present and each member's criterion is MET; everything
unlisted is unaccepted. A PARTIAL authorises nothing
outside its list.

**CONTESTED** — Two records bearing on the same matter
disagree, and no adjudication has resolved them. A
state of the evidence, not a defect in either record.
FORM: both references resolve and the disagreement is
in a named field. MEANING: whether the disagreement is
material — adjudication route.

**UNRESOLVED** — A matter explicitly recorded as not
decided. FORM: a record carrying the matter in an
undecided state. NOT: CONTESTED (which requires two
disagreeing records) and NOT unknown (which is about
the record's silence).

**UNKNOWN** — The record does not establish the
matter. A statement about the record, never about the
world. FORM: a search of the named record/scope
returning no establishing entry. NOT: absent, false,
or non-existent.

**LIVE** (of a commitment) — The current head of its
chain; the version that governs action now. FORM: the
chain record names it and no live successor exists.

**FROZEN** — An artefact whose content is fixed and
hash-pinned. Any change produces a new artefact, never
an edit. FORM: hash matches the pin.

## Evidence and claims

**EVIDENCE** — The identified material a claim rests
on: resolvable references, or a named observation
record. A claim without evidence is an assertion, and
an assertion is not evidence. FORM: every cited
reference resolves.

**REFERENCE** — A pointer that resolves to exactly one
record: an identifier, plus a hash where the target is
an immutable artefact. A description, however precise,
is not a reference. FORM: resolution returns one
record whose hash matches where a hash is given.

**OBSERVED** (evidence class) — Directly witnessed by
the recording seat at the time recorded. FORM: an
observation record naming the witness and the event.

**VERIFIED** (evidence class) — An independent check
reproduced the claim from its evidence. FORM: the
check record exists and names its method. MEANING:
that the method was adequate — adjudication route.
NOT: repeated, forwarded, or well-formatted.

**REPORTED** (evidence class) — Carried from another
seat's statement, not reproduced by the carrier.
Repetition never raises a claim's class: REPORTED
stays REPORTED however many seats repeat it.

**DEMONSTRATED** — A worker produced the outcome
itself, in a recorded run under recorded conditions,
scored by the frozen method for that task. FORM: the
run record, its conditions, and the scored result all
resolve. NOT: ELIGIBLE, retrieved, asserted, or
produced by the surrounding machinery.

**ELIGIBLE** — An output passed a release gate. A
property of the output's passage through that gate,
never of the worker's capability. FORM: the gate
record for that output.

**SUPPORTED** — The cited evidence, read by the frozen
method for the claim type, establishes the claim.
MEANING: adjudication route, unless a frozen mechanical
method for the claim type exists (then FORM by that
method). NOT: mentioned, retrieved, or plausible.

**ABSENT** — The named artefact does not occur in a
named, bounded search scope, verified by a named
method. FORM: scope reference, method, and target all
present, and the search record exists. An ABSENT claim
without its scope is malformed. NOT: non-existent
without qualification — ABSENT is always ABSENT-from.

**ADOPTION** — A worker changed a differing answer to
the established one after being shown it. FORM: the
before record differs, the after record agrees, and
the exposure between them is recorded. NOT: prior
agreement of any kind.

**ALIGNMENT** (prior) — The worker's answer already
agreed before exposure. Recorded separately from
ADOPTION in all counts, always.

**MECHANICAL** — Performed by a deterministic procedure
with no judgement inside the step. A call to a worker
is never MECHANICAL, however constrained its prompt.
FORM: the step's procedure is named and its inputs and
outputs are recorded.

## Authority and acts

**AUTHORITY** — The recorded right of a named seat to
perform a named class of act within a named scope. All
authority in this system originates with Ben; what is
delegated is exactly what the delegation lists, and
nothing travels by implication. FORM: an authority or
delegation record naming seat, class, and scope.
MEANING: whether a disputed act falls inside a scope —
adjudication route.

**RULING** — The record of an authoritative decision by
the seat holding AUTHORITY for that matter. FORM: the
record names the decider, the matter, the decision,
and the authority relied on. A statement of preference
is not a RULING.

**DELEGATION** — Transfer of a bounded task, with the
listed authority to own it, from one seat to another.
FORM: a DELEGATION message listing permitted and
prohibited actions, deliverables, and completion
condition. NOT: a REQUEST; the delegate's authority is
the list, never the delegator's whole authority.

**REQUEST** — An ask that transfers no authority and
no ownership. Compliance is the receiver's own act
under the receiver's own authority.

**SUPERSEDE** — To replace a LIVE commitment wholly
and prospectively with an authorised successor that
names it. FORM: the successor names the predecessor,
the predecessor was LIVE at the time, and the
superseding seat holds AUTHORITY for that commitment
class (authority check FORM only against a scoped
authority registry; otherwise MEANING, labelled so).
NOT: to reply to, to correct in part, or to erase —
the superseded commitment remains in the record.
Actions already taken in reliance are not undone by
supersession; unwinding them takes a STOP or RULING.

**REGISTER** (verb) — To enter a task into the task
registry by the authorised registration act, producing
an addressable entry. A task named in a commitment
must already be REGISTERED in the registry version the
commitment cites by hash. A sender cannot register a
task inside the commitment that relies on it.

**BINDING** — The mechanical application of an
approved, version-pinned rule or status. BINDING
carries no authority to select, skip, or amend what it
applies (per d3-v07#055). FORM: the applied rule and
its version pin are named.

**STOP** — A recorded halt of a named operation, with
a reason from the closed vocabulary and the condition
for its release. FORM: a STOP message with reason_code
and resume_condition. NOT: a suggestion, a concern,
or a pause in conversation — a STOP binds the
operation until its condition is met.

## Messages and records

**REQUIREMENT** — An obligation whose completion is
decidable by a named verification. FORM: a
REQUIREMENT message with condition, verification
method, and expected evidence. A wish, however
strongly worded, is not a REQUIREMENT.

**RESULT** — A record of an outcome, with its evidence
and its evidence class. FORM: a RESULT message whose
references resolve. A RESULT reports; it does not
decide, accept, or authorise.

**ACCEPT** — To record formal acceptance of an
artefact against named criteria, by the seat holding
AUTHORITY to accept it. Full acceptance requires every
criterion MET; any other state is PARTIAL or a
rejection, and the message must say which. FORM:
criteria results complete, scope list consistent with
them. MEANING: the criteria evidence genuinely
supports the statuses claimed.

**VALID** (of a message) — Satisfies every FORM rule
of its type, the dictionary conformance of its terms,
and the cross-field rules of the schema. One failure
makes the message MALFORMED.

**MALFORMED** — Fails VALID. A MALFORMED commitment is
not interpreted, repaired, or partially honoured; it
produces a STOP naming the defective field.

**RECORD** — The durable, addressable account of an
act or observation, stored where the seats can
retrieve it. What is not in a RECORD did not happen,
for the purposes of commitments.

## Deliberately not admitted (0.1)

Terms left to prose in this draft, candidates for a
later revision only on evidence of a failure: "sound",
"reasonable", "soon", "careful", "proper". Quality and
manner words are where one-meaning discipline goes to
die; they stay out of commitments entirely rather than
receive false precision.

*Dictionary 0.1 — Remmy, 2026-11-11. Draft for Alex's
independent challenge. Historical meanings in frozen
records are preserved by Rule 4 and change nothing
until the approval process rules.*
