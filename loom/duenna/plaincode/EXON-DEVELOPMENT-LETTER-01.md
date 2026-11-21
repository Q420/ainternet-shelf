# EXON — Development Letter 01 (Alex, 2026-11-16)

**Provenance:** The first letter of the EXON development
workstream, opened on the owner's order of 2026-11-16 ("Now
take everything we have for EXON, create a new chat with Alex
and let's start developing") in the ChatGPT conversation
"EXON development" (6afab3af). The assignment pointed Alex at
the whole canonical corpus on the shelf and gave direct URLs
for the two audits Chart 0.1 could not retrieve. The send was
verified clean before dispatch (composer census taken,
content compared normalised against the composed letter — the
check added after the chart round's stale-draft contamination).
Collected by direct page read and filed verbatim below
(rendered-text capture; table layout flattened).

**Status:** Reconciliation of Chart 0.1 against the two audits,
plus eight decision-ready proposals. Submitted for owner
adjudication — no freeze, no definitions, no implementation.
The owner's rulings on the proposals govern the next letter.

---

EXON — Development Letter 01

Subject: Chart 0.1 reconciliation and decision proposals
Scope: Vocabulary admission and category architecture
Status: Submitted for owner adjudication. No freeze, definitions or implementation authorised by this letter.

Part One — Reconciliation against the two audits

The audits establish an important distinction: a vocabulary chart must account for three different kinds of language, not merely group words by similarity.

The three layers are:

Dictionary terms — words carrying operational meaning.

Schema vocabulary — structural keywords and enumerated values.

Ordinary prose — explanation, qualification, attribution and advisory language.

The audits also establish that proximity does not confer equivalence. Two words can belong to the same category without being interchangeable.

Here is the reconciliation of the material retrieved.

What the audits confirm

The four original Dictionary categories remain a viable starting taxonomy.

Authority and acts deserve explicit treatment as a category.

Every admitted dictionary term needs a nearest-neighbour distinction.

Schema values must be accounted for separately from dictionary terms.

Ordinary prose must not silently alter structured commitments.

FORM and MEANING must remain distinct.

Authority, delegation and mechanical binding are different concepts.

UNKNOWN, UNRESOLVED, CONTESTED and ABSENT cannot be collapsed.

BLOCKED, INCORRECT and RELEASED represent materially different outcomes.

ADOPTION and ALIGNMENT require exposure-bound evidence.

What they change

Chart concern

	

Audit consequence




Four dictionary categories

	

Retain as the starting taxonomy, but explicitly account for the other two language layers.




Fifth category question

	

Requires a genuine operational distinction, not simply another organisational grouping.




Authority vocabulary

	

Separate the right to act, the act of deciding and the transfer of authority.




Candidate admissions

	

Test each word against its actual effect on what a reader may conclude.




Schema terminology

	

Must not be accidentally admitted as dictionary vocabulary.




Quality and manner words

	

Do not exclude automatically; admit only where they carry a genuine operational distinction.

What the audits kill

These are not merely editorial corrections.

Treating MET as an ordinary dictionary term. It belongs to the criterion-result schema.

Treating UNTRACEABLE as synonymous with ABSENT, UNKNOWN or UNRESOLVED.

Treating a resolved reference as proof that its contents support a claim.

Treating a recorded check as proof of independent verification.

Treating a task identifier as proof of registration.

Treating intended supersession or registry behaviour as existing mechanical enforcement.

Treating repetition as an upgrade from REPORTED to VERIFIED.

Treating a green subset as proof of COMPLETE.

The cross-type audit also identifies STOP.reason_code as an incomplete closed vocabulary. Its values cannot be assumed to exist simply because the field exists.

Overall reconciliation: Chart 0.1 survives as a working vocabulary chart, but its admission decisions must be made with stricter attention to operational consequences and the boundary between dictionary and schema.

Sources: Cross-Type Vocabulary Audit 0.1 · Category and Neighbour-Boundary Audit 0.1.

Part Two — Decision-ready proposals

The admission test applied throughout:

Does admitting this word change what a reader is entitled to conclude from an EXON record?

If it merely describes an operation, duplicates an existing conclusion, or adds convenient terminology without changing interpretation, it does not earn dictionary status.

Proposal 1 — Fifth category
Owner decision required

Chart proposal: Process and transformations.

The category would accommodate concepts involving transformation, comparison, reconciliation and derivation across records.

Audit challenge: The Category-Neighbour Audit explicitly establishes four fixed dictionary categories. It does not endorse a fifth. It also says category membership is organisational, not semantic.

My revised recommendation is:

Do not admit a fifth category at this stage. Retain the four established categories.

Reasons:

DISTILLED can potentially belong to Evidence and claims.

COMPARED can potentially belong to Evidence and claims.

SETTLE belongs naturally with Authority and acts.

Neither transformation nor comparison automatically creates a new operational state.

The fifth category currently describes a family of activities rather than an established family of independently necessary dictionary terms.

Admission test: Not passed as a category. The category itself changes no reader conclusion.

Owner decision: retain four, or authorise a fifth category.

Proposal 2 — AUTHORISE versus RULING versus GRANT
Three-way distinction proposed

The Authority Precedent Study introduces an important correction to Chart 0.1.

These are potentially three different acts or concepts:

Term

	

Proposed operational distinction

	

What the reader may conclude




GRANT

	

Establishes a right to perform specified acts within specified scope

	

Authority has been conferred




AUTHORISE

	

Permits a particular action under applicable authority

	

This particular action has permission




RULING

	

Resolves a matter through an authoritative decision

	

An authoritative decision has been made

These distinctions matter because having authority, granting authority and deciding whether an action is permitted are not interchangeable.

Consider:

A person holds authority to approve research.

That person grants another seat limited research authority.

The receiving seat seeks permission to perform a particular action.

An authorised decision-maker issues the relevant ruling.

Each statement carries a different consequence.

Important existing infrastructure: Dictionary 0.4 already defines AUTHORITY as a recorded right to act. The field matrix already carries authority_ref for RULING, DELEGATION, REGISTER_TASK and CORRECTION. The precedent study therefore recommends extending the existing architecture, not building a competing authority system.

The study also warns that authority levels cannot automatically determine permissions. A higher position does not necessarily inherit every lower-level permission.

My recommendation:

GRANT: Admit as a candidate dictionary act.

AUTHORISE: Admit as a candidate dictionary act.

RULING: Retain its existing admission, but preserve its distinct decision function.

There is one important qualification: GRANT and AUTHORISE must not become synonyms. GRANT establishes rights; AUTHORISE permits a particular action under applicable rights.

Admission test: All three pass. Each changes what a reader may conclude.

Owner decision: accept or reject the proposed three-way distinction.

Proposal 3 — SETTLED
Admission recommended

SETTLED is a proposed outcome/state.

The question is whether it adds anything beyond COMPLETE, ACCEPT, RULING and UNRESOLVED.

I believe it does.

A matter can be:

Decided without its resulting obligations being discharged.

Accepted without every related issue being resolved.

Complete without every dispute surrounding it being settled.

SETTLED would express closure of a named outstanding matter.

It should not automatically mean that every associated obligation has been fulfilled or that every artefact has been accepted.

Admission test: Pass.

It changes the reader's conclusion about whether an outstanding matter remains open.

Recommendation: admit SETTLED under Outcomes and states.

Proposal 4 — DISTILLED
Conditional admission

DISTILLED describes information produced through a source-reducing or source-preserving transformation.

The important distinction is that a distilled representation is not necessarily the original evidence.

For example:

Original records contain ten observations.

A worker produces a condensed representation of those observations.

The representation preserves selected information but is not itself the original ten observations.

Would DISTILLED change what a reader may conclude?

Yes, if it identifies a transformed artefact whose contents must not be mistaken for the complete original source.

However, there is a boundary problem: the term must not imply that the transformation was accurate, complete or independently verified.

My recommendation:

Admit DISTILLED provisionally as an evidence/claim descriptor, provided its eventual definition preserves source provenance and makes no unsupported quality claim.

Admission test: Pass, subject to that boundary.

Proposal 5 — COMPARED
Admission not recommended

COMPARED indicates that two or more things have undergone comparison.

But what does that allow the reader to conclude?

Only that a comparison occurred.

It does not establish:

Agreement.

Disagreement.

Accuracy.

Equivalence.

Which source is correct.

Those conclusions require recorded comparison results and, where applicable, separate adjudication.

The act of comparing is not necessarily a meaningful operational state.

My recommendation:

Keep COMPARED as a possible schema value or process-record description. Do not admit it as a dictionary term at present.

Admission test: Not passed as currently proposed. It records an activity without establishing a distinct operational conclusion.

Proposal 6 — SETTLE
Admission recommended

SETTLE is the proposed act corresponding to SETTLED.

It would represent the authorised resolution of an outstanding matter.

The distinction from RULING is important:

RULING records an authoritative decision.

SETTLE records the act of bringing an outstanding matter to resolution.

A ruling might settle a dispute, but not every ruling necessarily does. Equally, settlement may involve a recorded disposition without introducing a new ruling.

The distinction must also preserve the possibility of unresolved reliance or outstanding obligations.

Admission test: Pass, provided settlement is not automatically treated as obligation satisfaction or universal closure.

Recommendation: admit SETTLE under Authority and acts.

Proposal 7 — REVOKE
Admission recommended

REVOKE comes from the Authority Precedent Study and was not adequately represented in Chart 0.1.

This is a material omission.

A language that can grant and delegate authority needs to distinguish the withdrawal of authority from its original grant.

REVOKE would represent the authorised withdrawal of previously granted rights.

Its nearest neighbours:

SUPERSEDE replaces a commitment.

STOP halts an operation.

REVOKE withdraws an authority grant.

These are materially different consequences.

The authority precedent also proposes recording a revocation_ref against the authority grant.

Importantly, the current infrastructure does not establish a complete machine-readable authority registry. Admitting REVOKE must not imply that such a registry or automatic revocation enforcement already exists.

Admission test: Pass.

Recommendation: admit REVOKE under Authority and acts.

Proposal 8 — WAKE
Admission not recommended

WAKE appears in Chart 0.1 as a possible operational act or lifecycle transition.

The problem is that the current canonical vocabulary does not establish a sufficiently distinct lifecycle model for this word.

What exactly is being awakened?

A task?

A suspended operation?

A worker?

A previously inactive commitment?

Without a named object and a distinct resulting state, WAKE risks becoming an informal synonym for START, RESUME or ACTIVATE.

There is no demonstrated need in the current field matrix or infrastructure-gap register that requires this word.

Admission test: Not passed on present evidence.

Recommendation: exclude from dictionary admission for now. Reconsider only if an actual EXON operation requires this distinction.

Consolidated owner decision sheet

These are proposals, not decisions already made.

Question

	

My recommendation




Fifth category

	

Retain four




GRANT

	

Admit




AUTHORISE

	

Admit




RULING

	

Retain




SETTLED

	

Admit




DISTILLED

	

Admit conditionally




COMPARED

	

Exclude from dictionary




SETTLE

	

Admit




REVOKE

	

Admit




WAKE

	

Exclude for now

Final observations for the owner

Three findings deserve particular attention.

1. Authority needs both positive and negative acts.

The existing vocabulary explains authority, delegation and decisions. REVOKE completes an important part of that conceptual picture.

2. Process descriptions should not automatically become operational language.

DISTILLED potentially changes the evidential interpretation of an artefact. COMPARED, as currently proposed, does not establish a sufficiently distinct conclusion.

3. Settlement and completion are not interchangeable.

This distinction could become particularly important when EXON begins representing obligations, decisions and their eventual disposition.

The governing principle remains the same: a word earns its place because removing it would make an operational distinction impossible or materially less precise.

Submission status

Letter 01 complete

Both audits retrieved and reconciled.

All eight decision areas presented.

Admission test applied individually.

Existing canonical decisions respected.

No definitions drafted.

No vocabulary frozen.

No implementation or validator work commenced.

Owner's next action: Rule on these proposals. Development of the next stage will follow those decisions, not anticipate them.

Sources: Dictionary Chart 0.1 · Dictionary 0.4 · Adjudicated Field Matrix · Infrastructure-Gap Register · Authority Precedent Study.
