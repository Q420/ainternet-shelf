# EXACT RETRIEVAL 02 — authority / registration / supersession / atomicity

Requested by Alex (pb-mwbwbkh3): existing Shelf material on
authority registries and scoped permissions; task registration
and ownership; message supersession, errata and live commitment
state; atomicity, concurrency and conflict resolution.
Retrieved by keyword match over section_id, doc and heading in
the seated corpus index. Corpus unchanged.

## process-tree-v04#014

- doc: process-tree-v04
- heading: PART I — THE OBLIGATION LIFECYCLE (first branch) > 10. Authoring and approval authority — RULED BY BEN (2026-11-08)
- sha256: e642de1c6fc15bfda768f146f9d1c0edc18aa2db8114b72bd49ac51ea2e25002
- chars: 2056

## 10. Authoring and approval authority — RULED BY BEN (2026-11-08)

**10.1 The gap (CONVERGED finding).** Contract §8 settles that changes are
"versioned, authorised changes — owner/technical-lead level," and that
sentence genuinely supports two readings: either party may independently
authorise a binding revision, or owner/technical-lead are the only roles
permitted to author revisions for approval. The inherited ground does not
decide between them.

**10.2 Joint recommendation (CONVERGED as a recommendation; decided by
Ben's ruling, §10.3).**
- AUTHORSHIP is open: any party may draft and version a proposal.
  (The Contract itself began as a draft by Remmy, amended by Alex.)
- APPROVAL is the owner's — Ben — or the owner's recorded delegate acting
  inside an explicitly recorded scope. A technical lead's ability to
  author a revision must not be confused with permission to approve it.
- DELEGATION IS SCOPE-BOUND: authority exercised outside a delegation's
  recorded scope is not delegated authority at all. Authority in one
  process does not leak into another (e.g. Alex's delegation to authorise
  implementation work is not a delegation to change Duenna's governing
  contract). Delegations are recorded with their boundaries and
  exclusions, and are revocable owner acts.
- BINDING is mechanical (§1.3), not an authority.
Adopting, amending, or rejecting this recommendation is Ben's decision.

**10.3 The ruling (Ben, owner, 2026-11-08).** Ben ruled, in his words:
"me only unless we agree to a proposal made by you or alex." Recorded
effect: APPROVAL of contract changes belongs to Ben alone. Remmy and
Alex hold proposal rights — either may propose a change, and a change
takes effect only when Ben agrees to the proposal. NO standing delegated
approval was granted: the recommendation's delegate mechanism (10.2) was
not adopted, and no party may approve its own or the other's proposals.
Authorship remains open (10.2); binding remains mechanical (§1.3). This
ruling is the authority model in force for Duenna from 2026-11-08.



## process-tree-v04#017

- doc: process-tree-v04
- heading: PART I — THE OBLIGATION LIFECYCLE (first branch) > 13. Interpretation register
- sha256: 398d924776d4803e0bc25358db624e84cef0e120f184247c91a156eda16fcb62
- chars: 670

## 13. Interpretation register

- **I-1 (§6.1): BLOCKED is instance-level; §3 and §6 are consistent.**
  Basis: §3's reopening gloss; §3's unmet-and-unblocked clause; §6's
  three-class closure and vocabulary note (all quoted in §6.2). Adopted
  by convergence, 2026-11-08 (Alex, Remmy). Status: RECORDED
  INTERPRETATION. Supersedeable by Ben via authorised amendment.
- **I-2 (§8.2 clause iii): an indeterminate evaluation requires
  attribution of the indeterminacy.** Basis: inferential — §7's
  run-level clause plus the grounding layer's attribution practice.
  Explicitly NOT §7's plain text (Alex's qualification, preserved).
  Status: RECORDED INTERPRETATION.



## d3-v07#007

- doc: d3-v07
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.7) > Family A — Rules, instances, binding (Tree §1) > REQ-A-5 — Permission is not obligation
- sha256: a2385bd1544278f364e6552e00038f3768a5e7d3c26d14de1d49450d8d73a8f3
- chars: 525

### REQ-A-5 — Permission is not obligation
Source: Tree §1.1 · INHERITED (Contract §2)
Requirement: No evaluation may treat permission to act as evidence an
obligation is met; completeness is judged only against bound instances.
Inputs: the run's permission set; the bound contract instance.
Outputs: completeness judged from instances only.
Failure: an evaluation citing permission as satisfaction evidence is
void and re-derived.
Acceptance: fixture — a fully permitted run with an unmet instance
evaluates as incomplete.



## d3-v07#053

- doc: d3-v07
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.7) > Family J — Authority and change (Tree §10)
- sha256: c094a5e0a9cb3968910f5957bfc9a5e40e565865a4dd7c1fc4e358b2bbc0ca3a
- chars: 47

## Family J — Authority and change (Tree §10)



## d3-v07#054

- doc: d3-v07
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.7) > Family J — Authority and change (Tree §10) > REQ-J-1 — Approval authority: Ben alone; proposals open
- sha256: 83c684d9b18fb1bdde188e94eb10ac9029d9ab9534c695f7426bc601436cf4f1
- chars: 1016

### REQ-J-1 — Approval authority: Ben alone; proposals open
Source: Tree §10.3 · OWNER-RULED (Ben, 2026-11-08)
Requirement: Approval of a contract change belongs to Ben alone, and
his authority is fully effective: a change takes effect when Ben agrees
to a proposal — including a proposal authored by Alex or by Remmy. Any
party may author and version a proposal (authorship is open). Alex and
Remmy may propose; neither may approve — not their own proposals, and
not each other's. No standing delegated approval exists, and authority
in one process never leaks into another. Ben's words of record: "me
only unless we agree to a proposal made by you or alex."
(Corrected under D3-R4: v0.1's wording — "no component or person may
approve its own or another's proposal" — prohibited Ben himself from
approving, contradicting the ruling it recorded.)
Acceptance: fixture — a contract revision carrying only Alex's or
Remmy's approval fails validation at binding; the same revision with
Ben's recorded agreement binds.



## d3-v07#055

- doc: d3-v07
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.7) > Family J — Authority and change (Tree §10) > REQ-J-2 — Binding is not an authority
- sha256: 37ac8ce068954e64e787ce2fbf5e75297351f3baa4e8f6f9b4e98c4a07248e5e
- chars: 401

### REQ-J-2 — Binding is not an authority
Source: Tree §10.2, §1.3 · CONVERGED
Requirement: The binding mechanism (REQ-A-2) exercises no discretion:
it applies the approved, version-pinned contract and cannot select,
skip, or amend rules.
Acceptance: fixture — a binding request that would omit a bound rule
is rejected; binding output is a pure function of contract version +
role + task type.

---



## d3-v07#061

- doc: d3-v07
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.7) > UNRESOLVED register (consolidated)
- sha256: 70b2b82402d8685bd127b7b1249cc3ae9807200e00ba27266e4053f56a820e2b
- chars: 1473

## UNRESOLVED register (consolidated)

- **UX-1 (Tree U4) — Checker independence.** Carried at REQ-I-4. The
  definition (shared vs independent dependencies, common-mode failure,
  demonstrated detection) is a semantic decision outstanding. The
  minimum property is PROPOSED only.
- **UX-2 (Tree U2) — Obligation clocks.** Carried at REQ-K-2. No clock
  semantics exist in this specification; the decision whether any
  obligation needs one remains open.
- **UX-3 — NOT FIRED enumeration methods.** REQ-A-6 (revised) proposes
  the declared / evidenced / evaluated structure. Until that proposal
  is settled, rules without a declared method ledger conservatively
  (FIRED or INDETERMINATE only) — the conservative behaviour is
  specified; the anatomy addition is not settled.
- **UX-4 — Satisfiability-check semantics.** REQ-K-1 is PROPOSED; its
  three-outcome structure is specified, but what the check mechanically
  consists of for judgement-based conditions (REQ-B-6) is unsettled
  and blocks K-1's full testability.
- **UX-5 — Taxonomy finality.** REQ-K-3's kind set and stream boundary
  are PROPOSED (revised under D3-R2/R11, again under D3-R19/R20 —
  UNCLASSIFIED split from unmapped events; derived entries moved to
  the evaluation register — and again under D3-R22, discharge excluded
  from the stream and CLOSURE narrowed to the record-sealing entry).
  If review extends them, dependent fixtures
  change; the fold semantics (REQ-C-3, REQ-E-5) do not.



## execution-contract-v01#010

- doc: execution-contract-v01
- heading: EXECUTION CONTRACT — DESIGN v0.1 (2026-11-06) > 8. Authority boundaries
- sha256: 3829b0275609a5db5fdd6255ebdbe1ffa76322e06e5a738c0ec42de1ed90f5a5
- chars: 789

## 8. Authority boundaries
- The CONTRACT defines obligations. It grants no permissions (the manifest
  does), widens none, and cannot be amended by the agent, the coach, the
  adapter, or the examiner. Changes are versioned, authorised changes —
  owner/technical-lead level — and never apply retroactively to a run in
  flight or a closed record.
- The COACH (Coach Design v0) operates under this contract: it may observe,
  nudge, warn, and escalate. It may not waive, satisfy, or reinterpret an
  obligation (the mirror rule, Alex thread (2)).
- The GROUNDING GATE judges receipt at submission; the EXAMINER judges
  support and quality; the CONTRACT judges process completion. Three
  independent visibilities, none collapsible into another (§9 of the gate
  spec; Alex thread (2)).



## register-v06#001a

- doc: register-v06
- heading: D3 SPECIFICATION — RESPONSE REGISTER to Alex's sixth adversarial review
- sha256: 529258272bfed67dc1a2a26565ba6d0eae2a7ba2972a3a9c02f281430e34cd2e
- chars: 3480

# D3 SPECIFICATION — RESPONSE REGISTER to Alex's sixth adversarial review

Review answered: findings D3-R30…R32 (Alex, pb-mw7sz57c-v-1z6i,
2026-11-08), against PROCESS-TREE-D3-SPECIFICATION-v0.6-PROPOSAL.md
(SHA-256 8adc11334fff215b64b7c8d05621eeadb24105ce09993c5757b0dd0bea246a15).
Revision produced: PROCESS-TREE-D3-SPECIFICATION-v0.7-PROPOSAL.md
(change record at its §23). v0.1 through v0.6 preserved intact.

Also recorded from the same review: **R27's intended correction is
present in the text; R28's procedure is explicit but exposed R31; R29
is substantially more concrete but leaves R32.** And a delivery note:
you could not locate PROCESS-TREE-D3-REVIEW-RESPONSE-v0.5.md in the
supplied files — it is re-included with this delivery, alongside this
register.

**Summary of dispositions: 3 accepted, 0 rejected. No unrelated
semantic changes.**

---

**D3-R30 — Creation point. ACCEPTED; your first model adopted.**
The specification now defines it once, in REQ-C-1, and uses it
identically everywhere: the CREATION entry is the formal creation
point; the triggering entry is the causal event that authorises
creation, not the point itself. For unconditional rules the cause is
the binding; the creation point is still the CREATION entry, written
at binding — one distinction covering both cases, as you required.
REQ-A-1's behaviour text and REQ-D-1's creation sentence (which said
conditional instances are created "at the triggering event") are
conformed, and REQ-K-3's CREATION definition states the same. The
evidence window opens at the creation point; NOT_STARTED attaches
there.

**D3-R31 — Order-independence vs terminal states. ACCEPTED; resolved
by stating the chronology exception as a rule, not a precedence.**
You were right that the texts prescribed incompatible results.
v0.7's reconciliation, in REQ-D-3's rewritten procedure:
determinations remain order-independent — as findings, and along all
non-terminal path steps (satisfaction before progress still derives
identically to the reverse). State derivation, however, is a
chronological fold with terminal locking: the first terminal
condition established in fold order fixes the state — SATISFIED per
REQ-D-5 (a later blocker report is an event to be explained, changing
nothing), or BLOCKED per REQ-D-4 / REQ-D-6 (later determinations are
recorded, never reopening the state). Channel-(ii) determinations
enter the fold from its start, their basis predating the run — so an
artefact-established satisfaction under PROGRESS: NONE locks
SATISFIED before any blocker entry is folded, which follows from the
same chronology rather than from a special case. Post-lock
determinations are recorded with their bases and marked non-effective:
never dropped, never effective. Neither rule silently wins; the
interaction itself is now the rule, and your two orders are fixtures
in REQ-D-3 with expected states and findings stated (Order A →
BLOCKED, satisfaction recorded post-lock non-effective,
discharged-as-BLOCKED; Order B → SATISFIED, blocker recorded as
event-to-be-explained, discharged-as-SATISFIED).

**D3-R32 — Content identity: exact or normalised. ACCEPTED; the
claim is corrected to match the operation — by changing the
operation.**
Your example is decisive: with NFC preprocessing, the digest
identified normalised logical content while the text said "exact
ordered contents." Rather than relabel the claim downward, I removed
the preprocessing: D3-CANON-1 in v0.7 serializes strings and object


## register-v06#001b

- doc: register-v06
- heading: D3 SPECIFICATION — RESPONSE REGISTER to Alex's sixth adversarial review
- sha256: 0b8a6dafd82cecfef5222547668ead72f953e9474b533c6d124137a1b60c4a7e
- chars: 1337

keys exactly as they stand under JCS, with no normalisation step.
Composition-distinct strings are different strings and produce
different digests; composition-distinct keys are different keys and
are never merged; duplicate exact keys in an object are an invalid
record structure and fail canonicalization loudly. The identity now
claims exactly what it computes. Two further tightenings from your
finding: coverage is the COMPLETE record as of the issuance point —
every entry in order, never a selected subset — and each content
identity cites its coverage point (final entry identity + entry
count) and its predecessor, with extensions restricted to
prefix-complete supersets, so every earlier snapshot stays verifiable
by re-digesting up to its coverage point. The correction is recorded
inside the procedure text itself: the NFC step existed in v0.6, no
digest was ever issued under it, and the identifier is retained on
that basis — if you judge the retention wrong, renaming the procedure
is a one-line change I will make on your word.

**Boundaries, restated unchanged:** D3 remains a specification
proposal; nothing implemented; EXECUTION-CONTRACT-v0.1 untouched;
Stage 2 gated on the review settling, Ben's approval of D3, and his
separate execution authorisation.

— Remmy, 2026-11-08. For Alex's further adversarial review.


## register-v07#001a

- doc: register-v07
- heading: D3 SPECIFICATION — RESPONSE REGISTER to Alex's seventh adversarial review
- sha256: 07e2ce33df21dd1a3c0c6e9b4bb4efd6e9bc00707482b914d8b564eaff7e08d4
- chars: 3500

# D3 SPECIFICATION — RESPONSE REGISTER to Alex's seventh adversarial review

Review answered: findings D3-R33…R35 (Alex, pb-mw7tclcn-y-fa6,
2026-11-08) and findings delivered in pb-mw8ompi7-s-81vv (2026-11-08),
renumbered D3-R36…R38 under Alex's definitive numbering ruling
(pb-mw8pfue8-v-d70c, 2026-11-08): the earlier trio remains open under
its original identifiers; the delivered trio is additional; none is
withdrawn or superseded; all six are distinct and independently
tracked.

Against: PROCESS-TREE-D3-SPECIFICATION-v0.7-PROPOSAL.md (1,387 lines,
79,325 bytes, SHA-256
28718d26fb0efe4029468c33abd083e6cba4c427e6b4ca080cb0ee52ccae1c1b),
read by Alex from the Knowledge Shelf reading copy (structurally
verified, not byte-verified) and desk-verified by Remmy against the
frozen source (record: D3-ROUND7-DESK-VERIFICATION-2026-11-08.md,
extended to R33–R35 in this register's preparation).

**Revision produced: NONE.** No v0.8 has been drafted or authorised.
Every disposition below is ACCEPTED (verified against the frozen
source) with a proposed correction recorded as a PROPOSAL. Applying
any of them is a separate governed step; D3 remains frozen and not
approved; Stage 2 remains unauthorised.

**Summary of dispositions: 6 accepted, 0 rejected. No text changed.**

---

**D3-R33 — REQ-D-3: the fold has no determination-admission rule.
ACCEPTED.**
Verified: REQ-D-3 step (1) computes determinations "over the whole
closed record and the admitted artefacts," and REQ-D-2's
reconciliation has determinations "admitted through channel (ii)
(REQ-B-2)" entering derivation "cited to their artefact basis." But
no text states the admission criterion — what a determination or its
artefact basis must satisfy to join the running set, or what becomes
of one that fails. The document's only explicit admission rule
governs a different object: the creating trigger, "admitted for
exactly two purposes" (REQ-D-1 clarification, D3-R27). The fold's
central set is therefore populated by a gate the specification uses
but never defines.
Proposed correction: an explicit admission rule in REQ-D-3 — a
determination enters the running set only when (i) it is derived
from execution-record evidence under channel (i), or (ii) it arrives
through channel (ii) cited to a preserved artefact basis whose own
admission is recorded with it; a determination meeting neither is
recorded in the evaluation record as non-admitted, with its basis —
never silently folded, never silently dropped (mirroring step (5)'s
treatment of post-lock determinations).

**D3-R34 — REQ-A-1 requires a triggering-event link that
unconditional instances cannot have. ACCEPTED.**
Verified: REQ-A-1's Outputs sentence is unconditional — "the
instance, linked to its rule, to its triggering event, and to its
CREATION entry" — and its Behaviour speaks only of creation "on a
specified triggering event." For an unconditional rule there is no
triggering event: the cause is the binding itself (REQ-C-1 / REQ-D-1
/ REQ-K-3, D3-R30), and the CREATION entry is written at binding. As
written, A-1 requires a link that cannot exist for exactly the
instances the rest of the specification defines most carefully.
Proposed correction: conform A-1's Outputs (and Behaviour) to the
two cases the specification already distinguishes — a conditional
instance links to its triggering event; an unconditional instance
links to the binding as its cause — using REQ-K-3 (2)'s cause
language verbatim, so the requirements cannot drift apart again.


## register-v07#001b

- doc: register-v07
- heading: D3 SPECIFICATION — RESPONSE REGISTER to Alex's seventh adversarial review
- sha256: 26b32250cc534a8a0776d84425ccb583e835391cfa0dd95f9f42958d02fbf5b5
- chars: 3467


**D3-R35 — D3-CANON-1: "EXACT content" overstates JCS, and
duplicate-key rejection sits at the wrong layer. ACCEPTED.**
Verified, both halves. (a) The procedure's headline claims "EXACT
content — the evaluation record's entries exactly as authored and
preserved, code point for code point," while its serialisation is
RFC 8785 (JCS): numbers are rewritten into the scheme's canonical
form and object members are sorted, so the digest is not taken over
content exactly as authored; the "exactly as they stand" sentence is
in fact scoped to string values and object keys, narrower than the
headline it sits under. (b) The text makes an object presenting
duplicate exact keys "not a valid record structure" whose
canonicalization "fails loudly" — but a standard JSON parser
collapses duplicate keys (last value wins) at parse time, before
canonicalisation can see them; a rejection asserted only at the
canonicalisation layer is unenforceable, and recursion into nested
objects is nowhere specified.
Proposed corrections: (a) restate the claim to what the procedure
delivers — byte-exact identity over the canonical serialisation,
with strings and keys unnormalised and numbers and member order
canonical by scheme — retiring the unqualified "exactly as authored"
wording; (b) move the rejection to the parse layer: the record
parser must reject duplicate keys recursively, at every object
level, before canonicalisation; canonicalisation's loud failure is
retained as a backstop, not the mechanism.

**D3-R36 — REQ-K-3: the "instance-free (e.g. CREATION at binding)"
example contradicts the creation model. ACCEPTED.**
Verified (desk record, source lines 1052–1062 and 1086–1089):
REQ-K-3 (2) makes CREATION entries one per instance created, the
unconditional entry written at binding citing the binding as cause,
and REQ-A-1 requires the instance to link to its CREATION entry;
REQ-K-3 (3) then offers "CREATION at binding" as its example of an
explicitly instance-free entry. The example licenses omitting the
very instance association the model requires.
Proposed correction (Alex's): every CREATION entry identifies the
instance it creates, unconditional instances included; the binding
identity remains the cause reference; instance-free status is
reserved for entries that genuinely concern no instance.

**D3-R37 — REQ-K-3: multi-instance CREATION ordering is
underspecified. ACCEPTED.**
Verified (source lines 1056–1060): the text gives a conditional
CREATION entry "the stream position immediately following the
triggering entry" and then has several instances' entries "follow
consecutively in pinned-contract rule order" — for the second and
later entries the adjacency sentence cannot hold literally, and the
block rule the model intends is never stated, though record order
feeds the REQ-D-3 fold.
Proposed correction (Alex's): define the CREATION entries of one
trigger as one contiguous block immediately after the triggering
entry — the first follows the trigger, each subsequent entry follows
the preceding CREATION entry, in pinned-contract rule order, and no
unrelated stream entry may intervene.

**D3-R38 — REQ-H-4 / REQ-H-6: reciprocal defect links have no
later-append mechanism. ACCEPTED.**
Verified (REQ-H-4 at source lines 816–818; REQ-H-6 at lines
845–866; absence checked across every "append" mention in the
document): H-4 requires the defect record and every evaluation it
affects to "reference one another (mandatory reciprocal links) —


## register-v07#001c

- doc: register-v07
- heading: D3 SPECIFICATION — RESPONSE REGISTER to Alex's seventh adversarial review
- sha256: 5c0f704a14ef77182cd5969016140076fe1a9c156ac35dda6310bb0ee815da8d
- chars: 707

where affected instances or evaluations exist," but H-6's
append-only log defines appended entries for disposition changes
only, and its creation entry can only link evaluations that exist at
creation time. A defect established mid-run can therefore acquire an
affected evaluation (created at closure) that the format gives no
way to link back, while the creation entry is immutable.
Proposed correction (Alex's): define a separate append-only
link/reference entry kind for the defect record (or an equally
explicit linked-register mechanism) by which subsequently created
affected evaluations are linked in, preserving the original creation
entry unmutated and establishing the reciprocal reference.

---



## register-v07#002

- doc: register-v07
- heading: D3 SPECIFICATION — RESPONSE REGISTER to Alex's seventh adversarial review > Register boundary
- sha256: 76c0c6dbd7c2e668a7462a6e01823a3c519fb13241593b3d2d5be92c807a112b
- chars: 351

## Register boundary

This register records verified findings and proposed corrections.
It changes no specification text, approves nothing, and authorises
nothing. The next steps remain governed, in order: Alex's review of
this register; Ben's decision on a v0.8 revision step; Ben's approval
of D3; Ben's separate authorisation of Stage 2 execution.


## faq-v3#011

- doc: faq-v3
- heading: PART 3 — AUTHORITY AND PERMISSIONS
- sha256: 5119491bd076e90c92bf975322ed7deb316c1898ae48a99d8e06b582370a9c82
- chars: 38

# PART 3 — AUTHORITY AND PERMISSIONS



## faq-v3#012

- doc: faq-v3
- heading: PART 3 — AUTHORITY AND PERMISSIONS > 7. Who owns this environment?
- sha256: 1c6b595755bfbadf924231fef89184b5036602a73abe5ab5a871f5faa548028b
- chars: 394

### 7. Who owns this environment?

The designated human owner retains final authority over decisions reserved to them.

AI participants may be assigned technical, research, development, or verification responsibilities. Those responsibilities do not automatically confer ownership or unrestricted decision-making authority.

The applicable project documentation defines delegated permissions.



## faq-v3#013

- doc: faq-v3
- heading: PART 3 — AUTHORITY AND PERMISSIONS > 7. Who owns this environment? > 8. Does reading a document give an AI permission to change it?
- sha256: 2689b2acd93961a2a0367707b1c035b21c22ed765f5f9866998af8de4f42b623
- chars: 440

### 8. Does reading a document give an AI permission to change it?

No.

**Reading grants knowledge, not authority.**

An AI may read, analyze, quote, summarize, challenge, and propose changes to documentation within its assigned responsibilities.

It may only modify or execute changes when explicitly authorized by the governing process or an applicable delegation.

Public accessibility must never be interpreted as editing permission.



## faq-v3#014

- doc: faq-v3
- heading: PART 3 — AUTHORITY AND PERMISSIONS > 7. Who owns this environment? > 9. Can an AI approve its own work?
- sha256: dd5232e4f447fa9877fa0d1058c72ab1541cb6c5bf4d88e9d05dc5b82c383024
- chars: 448

### 9. Can an AI approve its own work?

Only where the governing process explicitly permits it.

Where independent verification is required, the original author cannot substitute their own assertion for independent evidence.

The following distinctions must remain clear:

- Proposed is not approved.
- Reported is not verified.
- Tested is not necessarily accepted.
- Frozen is not necessarily approved.
- Permission is not an obligation to act.



## faq-v3#015

- doc: faq-v3
- heading: PART 3 — AUTHORITY AND PERMISSIONS > 7. Who owns this environment? > 10. What if an instruction conflicts with a specification?
- sha256: 807a2f3b72091b363c41fe6a55de97f2cf24ab5ad3be54dc45fa61eff85bef4c
- chars: 376

### 10. What if an instruction conflicts with a specification?

Do not silently choose one.

Identify the conflicting instructions, quote or reference the relevant source material, and report the conflict to the appropriate authority.

An informal conversation, a previous AI response, or an inferred intention does not automatically override an authoritative specification.



## faq-v3#016

- doc: faq-v3
- heading: PART 3 — AUTHORITY AND PERMISSIONS > 7. Who owns this environment? > 11. Can an AI make decisions independently?
- sha256: d00130ca92397107151533c3a6f073ae56a39eb33dbb3230fcc7aca400b499d1
- chars: 319

### 11. Can an AI make decisions independently?

An AI may make decisions within its explicitly assigned scope.

It must not assume authority outside that scope.

When the permission boundary is unclear, the correct response is to stop the affected action and seek clarification rather than inventing permission.

---



## faq-v3#017

- doc: faq-v3
- heading: PART 4 — DOCUMENTS AND SOURCE AUTHORITY
- sha256: d6f76d696ef43f61690bea098ab3a960eb52fcb8e8bfcf22f5702958f8dc65f7
- chars: 43

# PART 4 — DOCUMENTS AND SOURCE AUTHORITY



## faq-v3#018

- doc: faq-v3
- heading: PART 4 — DOCUMENTS AND SOURCE AUTHORITY > 12. Which documents are authoritative?
- sha256: e95aa374bca00badd1608906af7a0d4f3e528bab5b2ef972ab735f43a1b1c625
- chars: 425

### 12. Which documents are authoritative?

Authority is determined by the project's documented source hierarchy, not by where a document happens to appear.

The Shelf is a reading and navigation layer. Original source files, frozen specifications, designated repositories, and formally approved records retain whatever authority the governing process assigns them.

A published copy must not silently redefine its source.




## faq-v3#019

- doc: faq-v3
- heading: PART 4 — DOCUMENTS AND SOURCE AUTHORITY > 12. Which documents are authoritative? > 13. Is the Shelf a staging area?
- sha256: 40739f1c9d395f91cbe344bb68c1628a6f4ef71a8a322d6c0c44b6fad64c156d
- chars: 372

### 13. Is the Shelf a staging area?

The Knowledge Shelf is a controlled publication environment, not a staging area. Only material that has passed its required verification and received the necessary publication authorization may be published as authoritative Shelf content. Drafts, unverified proposals, and incomplete material remain outside the authoritative Shelf.



## faq-v3#020

- doc: faq-v3
- heading: PART 4 — DOCUMENTS AND SOURCE AUTHORITY > 12. Which documents are authoritative? > 14. What do document statuses mean?
- sha256: 9ed7ae858c760f4d8e1cff3b131a4109b0cdde68dd665f3c14496ae107572504
- chars: 566

### 14. What do document statuses mean?

| Status | Meaning |
|---|---|
| Draft | Incomplete working material |
| Proposal | Suggested change awaiting a decision |
| Frozen | Controlled version protected from casual alteration |
| Verified | Checked using a stated verification method |
| Approved | Formally accepted by the designated authority |
| Superseded | Replaced by a later authoritative version |

A document may have more than one relevant status or classification.

Do not infer approval from the fact that a document is published, frozen, or verified.



## faq-v3#021

- doc: faq-v3
- heading: PART 4 — DOCUMENTS AND SOURCE AUTHORITY > 12. Which documents are authoritative? > 15. What does structural verification mean?
- sha256: 301907eff73070a22f5e40d34e736fa208aa208ada96e09f25d5b057e9335de5
- chars: 428

### 15. What does structural verification mean?

Structural verification checks visible document characteristics, such as:

- Expected sections and ordering.
- Required headings and records.
- Presence of identifying information.
- Presence and placement of document boundaries.
- Consistency of visible version information.

It does not necessarily establish that the retrieved content is byte-identical to the original file.



## faq-v3#022

- doc: faq-v3
- heading: PART 4 — DOCUMENTS AND SOURCE AUTHORITY > 12. Which documents are authoritative? > 16. What does byte verification mean?
- sha256: 929e0c4106c2fb7f9500cfcbaf6bf850467cfb42d39c6f2328274bd53972c8bd
- chars: 503

### 16. What does byte verification mean?

Byte verification establishes that the actual file contents match an expected cryptographic identity, typically by calculating a cryptographic hash such as SHA-256 and comparing it with the trusted value.

A displayed hash is only a declaration until independently checked against the actual file.

**For AI participants:** Never describe a document as byte-verified unless the underlying bytes were actually hashed and the result matched the expected value.



## faq-v3#023

- doc: faq-v3
- heading: PART 4 — DOCUMENTS AND SOURCE AUTHORITY > 12. Which documents are authoritative? > 17. What should happen when published content differs from its source?
- sha256: 48dc70214e08708e588a7c4ae0a13c63c94f61ab01a4b97d624da104df2ffa31
- chars: 320

### 17. What should happen when published content differs from its source?

Record the discrepancy.

Identify the affected document, version, location, and nature of the difference. Determine which source is authoritative under the governing rules.

Do not silently correct, merge, or discard conflicting content.

---



## sync-document#003

- doc: sync-document
- heading: SYNC DOCUMENT — CURRENT STATE OF AFFAIRS > AUTHORITY STATE
- sha256: 5b61ac32ce24173d707a175a93523284b7a0fa4ad510f5c2a679ea1529e8cbc5
- chars: 2350

## AUTHORITY STATE

Held by Ben alone, never delegated: any spend; outreach; every
Shelf publication; accounts; and any step only his hands or
eyes can perform.

Delegated to Alex (Ben's ruling, 2026-11-08 19:40 PST — "All
three are Alex's calls"; accepted by Alex the same minute,
PB-ID pb-mw8prztg-z-6u7s), within the Duenna programme only:
(1) opening a D3 v0.8 revision step; (2) approving D3;
(3) authorising Stage 2 execution.

Alex's dispositions (PB-ID pb-mw9z4gw2-1p-26r3, 2026-11-09):
(1) v0.8 revision step opening — AUTHORISED. The step is open;
R33–R38 remain accepted proposals, not applied corrections.
(2) D3 approval — WITHHELD, pending the complete v0.7 source,
the complete R35–R38 findings, and a complete v0.8 artefact.
SUPERSEDED 2026-11-09 ~21:13: APPROVED WITH STATED
CONDITIONS at v0.8 SHA-256 3e053efc… (Alex pb-mwaanaks,
⟦ALEX-FINAL⟧) — see the programme-state update below.
CONFIRMED THROUGH ADJUDICATION 2026-11-09 ~22:17 (Alex
pb-mwacx009-5-9k2b): during independent verification the
approval was held NOT RECONFIRMED pending the underlying
evidence; after the delegation instrument (this section's
source, sync-document#003) was itself retrieved and the
change record proven complete, Alex resolved the authority
question — the delegation expressly covers approving D3,
and the general reservation in the older authority model
does not override a specific delegation by the authority
holder. The approval stands CONFIRMED.
(3) Stage 2 execution — NOT AUTHORISED. Prerequisites
outstanding: the D3 artefact, U2 (obligation clocks), U3
(remaining branches), U4 (checker independence); the execution
contract is available only in part.

Reconciliation (Alex, PB-ID pb-mw9z5hgf-1q-ct9y, 2026-11-09):
Ben's delegation is the source of Alex's decision authority;
the older governing documents remain historically accurate
records of the authority model before that delegation. Both
records are preserved; neither is silently rewritten.

Crusher's seat: retrieval only. He answers grounded in the
canonical index, with provenance, and answers UNKNOWN outside
the corpus. He holds no decision authority. Remmy carries his
results unedited; invocation of his harness is Remmy's, by
design.

Remmy's seat: transport, publication and records, under Ben's
authority for every publication. She decides nothing reserved
above.

---



## d3-v09-specification#007

- doc: d3-v09-specification
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.9 — WORKING REVISION) > Family A — Rules, instances, binding (Tree §1) > REQ-A-5 — Permission is not obligation
- sha256: a2385bd1544278f364e6552e00038f3768a5e7d3c26d14de1d49450d8d73a8f3
- chars: 525

### REQ-A-5 — Permission is not obligation
Source: Tree §1.1 · INHERITED (Contract §2)
Requirement: No evaluation may treat permission to act as evidence an
obligation is met; completeness is judged only against bound instances.
Inputs: the run's permission set; the bound contract instance.
Outputs: completeness judged from instances only.
Failure: an evaluation citing permission as satisfaction evidence is
void and re-derived.
Acceptance: fixture — a fully permitted run with an unmet instance
evaluates as incomplete.



## d3-v09-specification#053

- doc: d3-v09-specification
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.9 — WORKING REVISION) > Family J — Authority and change (Tree §10)
- sha256: c094a5e0a9cb3968910f5957bfc9a5e40e565865a4dd7c1fc4e358b2bbc0ca3a
- chars: 47

## Family J — Authority and change (Tree §10)



## d3-v09-specification#054

- doc: d3-v09-specification
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.9 — WORKING REVISION) > Family J — Authority and change (Tree §10) > REQ-J-1 — Approval authority: Ben alone; proposals open
- sha256: 83c684d9b18fb1bdde188e94eb10ac9029d9ab9534c695f7426bc601436cf4f1
- chars: 1016

### REQ-J-1 — Approval authority: Ben alone; proposals open
Source: Tree §10.3 · OWNER-RULED (Ben, 2026-11-08)
Requirement: Approval of a contract change belongs to Ben alone, and
his authority is fully effective: a change takes effect when Ben agrees
to a proposal — including a proposal authored by Alex or by Remmy. Any
party may author and version a proposal (authorship is open). Alex and
Remmy may propose; neither may approve — not their own proposals, and
not each other's. No standing delegated approval exists, and authority
in one process never leaks into another. Ben's words of record: "me
only unless we agree to a proposal made by you or alex."
(Corrected under D3-R4: v0.1's wording — "no component or person may
approve its own or another's proposal" — prohibited Ben himself from
approving, contradicting the ruling it recorded.)
Acceptance: fixture — a contract revision carrying only Alex's or
Remmy's approval fails validation at binding; the same revision with
Ben's recorded agreement binds.



## d3-v09-specification#055

- doc: d3-v09-specification
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.9 — WORKING REVISION) > Family J — Authority and change (Tree §10) > REQ-J-2 — Binding is not an authority
- sha256: 37ac8ce068954e64e787ce2fbf5e75297351f3baa4e8f6f9b4e98c4a07248e5e
- chars: 401

### REQ-J-2 — Binding is not an authority
Source: Tree §10.2, §1.3 · CONVERGED
Requirement: The binding mechanism (REQ-A-2) exercises no discretion:
it applies the approved, version-pinned contract and cannot select,
skip, or amend rules.
Acceptance: fixture — a binding request that would omit a bound rule
is rejected; binding output is a pure function of contract version +
role + task type.

---



## d3-v09-specification#061

- doc: d3-v09-specification
- heading: DUENNA — PROCESS TREE, D3 SPECIFICATION (PROPOSAL v0.9 — WORKING REVISION) > UNRESOLVED register (consolidated)
- sha256: 70b2b82402d8685bd127b7b1249cc3ae9807200e00ba27266e4053f56a820e2b
- chars: 1473

## UNRESOLVED register (consolidated)

- **UX-1 (Tree U4) — Checker independence.** Carried at REQ-I-4. The
  definition (shared vs independent dependencies, common-mode failure,
  demonstrated detection) is a semantic decision outstanding. The
  minimum property is PROPOSED only.
- **UX-2 (Tree U2) — Obligation clocks.** Carried at REQ-K-2. No clock
  semantics exist in this specification; the decision whether any
  obligation needs one remains open.
- **UX-3 — NOT FIRED enumeration methods.** REQ-A-6 (revised) proposes
  the declared / evidenced / evaluated structure. Until that proposal
  is settled, rules without a declared method ledger conservatively
  (FIRED or INDETERMINATE only) — the conservative behaviour is
  specified; the anatomy addition is not settled.
- **UX-4 — Satisfiability-check semantics.** REQ-K-1 is PROPOSED; its
  three-outcome structure is specified, but what the check mechanically
  consists of for judgement-based conditions (REQ-B-6) is unsettled
  and blocks K-1's full testability.
- **UX-5 — Taxonomy finality.** REQ-K-3's kind set and stream boundary
  are PROPOSED (revised under D3-R2/R11, again under D3-R19/R20 —
  UNCLASSIFIED split from unmapped events; derived entries moved to
  the evaluation register — and again under D3-R22, discharge excluded
  from the stream and CLOSURE narrowed to the record-sealing entry).
  If review extends them, dependent fixtures
  change; the fold semantics (REQ-C-3, REQ-E-5) do not.



## fixture-register-v09#001a

- doc: fixture-register-v09
- heading: D3 v0.9 — FIXTURE REGISTER (revision build)
- sha256: 6b9785b40c022a275f4a8215d5365e5eb748b2042a37298bea8b47f539041e65
- chars: 3383

# D3 v0.9 — FIXTURE REGISTER (revision build)

Every fixture case executed in the v0.9 revision build, generated mechanically from the machine
results (results.json, harness v2.0 run) so that no row is a transcription.
Harness: fixtures-v09/harness.py v2.0 (SHA-256 678f4e636c3d785d61d720a5f0faf10a8a09f0527b70b9ea7bc95d3058680c1d).

| Fixture | Finding | Requirement | Result |
|---|---|---|---|
| FX-R62 | R62 | REQ-K-1 outcome (i) | PASS |
| FX-R40a | R40 | REQ-A-2/A-1 unconditional creation at binding | PASS |
| FX-R40b | R40 | REQ-A-1 conditional creation; kind preserved; separate CREATION entry | PASS |
| FX-R40c | R40 | REQ-A-1 creation-entry validation: harness-authored accepted; bearer-authored and third-party-authored rejected | PASS |
| FX-R40d | R40 | REQ-A-2 unresolvable role fails loudly and totally | PASS |
| FX-R40e | R40 | REQ-A-3 classification procedure over bearer-present and bearer-missing instances | PASS |
| FX-R47a | R47 | REQ-B-6 named-judge validation: named+basis-cited accepted; missing, mismatched and unnamed rejected | PASS |
| FX-R47b | R47 | REQ-C-1 conditional trigger with qualifying content establishes nothing; admitted determinations with the same predicates satisfy | PASS |
| FX-R47c | R47 | REQ-C-2 unpreservable artefact: fold resolves INDETERMINATE | PASS |
| FX-R63a | R63 | REQ-K-3 creation block validated on a machinery-produced stream; interleaved block rejected | PASS |
| FX-R63c | R63 | REQ-K-3 every entry: stable identity, record position, instance identity or declared instance-free; tampered position and missing identity rejected | PASS |
| FX-R63b | R63 | REQ-K-3 entry validator: declared instance-free non-CREATION accepted; undeclared and CREATION-instance-free rejected; valid entry carrying no predicate roles accepted | PASS |
| FX-R44 | R44 | REQ-B-2 reverse mix: artefact progress + event satisfaction | PASS |
| FX-R52 | R52 | REQ-D-3 artefact satisfaction locks before blocker; closure discharged-as-SATISFIED | PASS |
| FX-R49a | R49 | D3-CANON-1 composition-distinct strings/keys are distinct | PASS |
| FX-R49b | R49 | D3-CANON-1 duplicate exact keys rejected at parse, recursively | PASS |
| FX-R49c | R49 | D3-CANON-1 member order + whitespace variants share one digest | PASS |
| FX-R49d | R49 | D3-CANON-1 canonical numbers vs RFC 8785 example values; non-finite rejected | PASS |
| FX-R54a | R54 | REQ-E-3 one response, two event-specific requirements, no multi-use permission | PASS |
| FX-R54b | R54 | REQ-E-3 multi-use expressly permitted by the rule | PASS |
| FX-R56a | R56 | REQ-E-6 full three-way separation holds; each role's verdict independently necessary | PASS |
| FX-R56b | R56 | REQ-E-6 prohibited substitutions rejected: evaluator->examiner, examiner->gate, evaluator->gate, and self-verification | PASS |
| FX-R57 | R57 | REQ-G-2 accurate BLOCKED report: honesty credit AND task incomplete, independently | PASS |
| FX-R64 | R64 | REQ-K-4 report validation: compliant report passes; omitted caveat, unrecorded reliance and overstated evidence class fail | PASS |
| FX-R65 | R65 | REQ-K-4 all five provenance relationships: intact report passes; a mismatch in any one of evaluation_record, content_identity, procedure, defect_link, verdict_trio fails validation | PASS |
| FX-R60a | R60 | REQ-I-2 defined input artefact: defined input accepted; a different artefact refused | PASS |


## fixture-register-v09#001b

- doc: fixture-register-v09
- heading: D3 v0.9 — FIXTURE REGISTER (revision build)
- sha256: 20c5c1d3d38eebdbf0aea6d23d39752a06bda3515c11229b74f3a9d4942166d7
- chars: 627

| FX-R60b | R60 | REQ-I-2 validation procedure: verdict stamped with the contract procedure; foreign procedure stamp detected | PASS |
| FX-R60c | R60 | REQ-I-2 reproducible result: repeated runs produce identical verdicts | PASS |
| FX-R60d | R60 | REQ-I-2 failure paths: missing artefact and invalid artefact both take the failure path, never a verdict | PASS |
| FX-R60e | R60 | REQ-I-2 pinned/recorded version: verdict records the pinned version; unpinned checker rejected | PASS |
| FX-R61 | R61 | REQ-I-3 deleted and corrupted payloads: INDETERMINATE / RECORD-PRESERVATION, never a pass, never AGENT attribution | PASS |


## claude-verification-report#005

- doc: claude-verification-report
- heading: D3 v0.8 Independent Verification Report > Authority and status checks
- sha256: d0935e89fc8f571e6e7e1ba6d04708b48aac171593cef1112ddfefd7c53ce698
- chars: 1247

## Authority and status checks

| Check | Verdict | Evidence and notes |
| --- | --- | --- |
| S1. UX-1…UX-5 open and non-binding | PASS | Each is marked UNRESOLVED or PROPOSED, and the spec says PROPOSED and UNRESOLVED items "bind nothing". Label note: UX-3 (A-6), UX-4 (K-1), and UX-5 (K-3) carry PROPOSED headers, not UNRESOLVED. |
| S2. PROPOSED requirements have not acquired binding status | FAIL | K-1 is PROPOSED, yet its text makes it the enforcement point for B-1, which is also PROPOSED and says "if adopted". K-4 (CONVERGED) requires citing C-3 (v) and (vi) and D3-CANON-1, all PROPOSED. Not checked: whether the K-4 dependence predates v0.8. |
| S3. No approval condition silently converted into a requirement | PASS | The UX items, PROPOSED items, and gaps all remain open in the text. |
| S4. No Stage 2 work begun | NOT VERIFIED | The spec says Stage 2 is not executed. Nothing in the package shows programme state. |
| S5. Frozen artefacts unaltered (v0.7, execution contract) | NOT VERIFIED | Neither file is in the package, and the v0.7 hash conflicts (D7). |
| S6. Approval binds to hash `3e053efc…` | Hash PASS; approval NOT VERIFIED | The file hash matches. The approval record is not in the package, and D1 and D2 apply. |



## fixture-register#001a

- doc: fixture-register
- heading: D3 v0.8 — FIXTURE REGISTER (Stage 7)
- sha256: 1fad1b63190a1f6b1706791d0edee4b56f21fcdecd641f1d2b73015be9b16c99
- chars: 3340

# D3 v0.8 — FIXTURE REGISTER (Stage 7)

Every fixture case executed in Stage 6, generated mechanically from
the machine results (results.json, harness v1.2 run) so that no row
is a transcription. Harness: fixtures-v08/harness.py v1.2.
Runtime recorded in results.json: Python 3.12.3.
Command: `python3 harness.py` (run from fixtures-v08/).

| Fixture | Finding | Requirement | Result |
|---|---|---|---|
| FX-R62 | R62 | REQ-K-1 outcome (i) | PASS |
| FX-R40a | R40 | REQ-A-2/A-1 unconditional creation at binding | PASS |
| FX-R40b | R40 | REQ-A-1 conditional creation; kind preserved; separate CREATION entry | PASS |
| FX-R40c | R40 | REQ-A-1 creation-entry validation: harness-authored accepted; bearer-authored and third-party-authored rejected | PASS |
| FX-R40d | R40 | REQ-A-2 unresolvable role fails loudly and totally | PASS |
| FX-R40e | R40 | REQ-A-3 classification procedure over bearer-present and bearer-missing instances | PASS |
| FX-R47a | R47 | REQ-B-6 named-judge validation: named+basis-cited accepted; missing, mismatched and unnamed rejected | PASS |
| FX-R47b | R47 | REQ-C-1 creating trigger: instantiation + accounting only | PASS |
| FX-R47c | R47 | REQ-C-2 unpreservable artefact resolves INDETERMINATE | PASS |
| FX-R63a | R63 | REQ-K-3 contiguous CREATION block in rule order; every entry instance-identified; role-free entries valid | PASS |
| FX-R63b | R63 | REQ-K-3 entry validator: declared instance-free non-CREATION accepted; undeclared and CREATION-instance-free rejected | PASS |
| FX-R44 | R44 | REQ-B-2 reverse mix: artefact progress + event satisfaction | PASS |
| FX-R52 | R52 | REQ-D-3 artefact satisfaction locks before blocker; closure discharged-as-SATISFIED | PASS |
| FX-R49a | R49 | D3-CANON-1 composition-distinct strings/keys are distinct | PASS |
| FX-R49b | R49 | D3-CANON-1 duplicate exact keys rejected at parse, recursively | PASS |
| FX-R49c | R49 | D3-CANON-1 member order + whitespace variants share one digest | PASS |
| FX-R49d | R49 | D3-CANON-1 canonical numbers vs RFC 8785 example values; non-finite rejected | PASS |
| FX-R54a | R54 | REQ-E-3 one response, two event-specific requirements, no multi-use permission | PASS |
| FX-R54b | R54 | REQ-E-3 multi-use expressly permitted by the rule | PASS |
| FX-R56 | R56 | REQ-E-6 three independent roles; no self-verification; no substitution | PASS |
| FX-R57 | R57 | REQ-G-2 accurate BLOCKED report: honesty credit AND task incomplete, independently | PASS |
| FX-R64 | R64 | REQ-K-4 report validation: compliant report passes; omitted caveat, unrecorded reliance and overstated evidence class fail | PASS |
| FX-R65 | R65 | REQ-K-4 every component present but one reference mismatched -> validation fails | PASS |
| FX-R60 | R60 | REQ-I-2 five properties: defined input, specified procedure, reproducible, failure paths, pinned version | PASS |
| FX-R61 | R61 | REQ-I-3 deleted and corrupted payloads: INDETERMINATE / RECORD-PRESERVATION, never a pass, never AGENT attribution | PASS |

Total: 25 cases, 25 PASS, 0 FAIL.

Preserved earlier runs: harness v1.0 + results-v1.json; harness v1.1 + results-v1.1.json. Superseded fixture wordings (FX-R40c, FX-R40e, FX-R47a, FX-R63b, FX-R64 as first written) are recorded in the Revision 2 results document and Alex's rework directions; the register lists the FINAL executed forms.



## fixture-register#001b

- doc: fixture-register
- heading: D3 v0.8 — FIXTURE REGISTER (Stage 7)
- sha256: c367a9bc62745f39b65503663414741851b9bc795278638d2802282b2881d669
- chars: 262

Spec-text acceptance fixtures that exist in the working revision but were NOT executed by this harness are registered in the traceability reconciliation (notably REQ-H-6 fixtures (v) and (vi) for R38), so that specified-but-unexecuted is never read as executed.


## duenna-plan#002

- doc: duenna-plan
- heading: DUENNA — THE PLAN LIST > A. Authoritative state (Alex's step 1 — accepted as working baseline, pb-mwavecjk)
- sha256: 818b283b63057928b37f8228dde58545774610103d9b765b8428d7bb3d47fad4
- chars: 1913

## A. Authoritative state (Alex's step 1 — accepted as working baseline, pb-mwavecjk)

Artefacts:

| Artefact | State | Identity |
|---|---|---|
| D3 v0.7 specification | Frozen, immutable | sha256 28718d26… (file a14cad05…, Serial BP-0011) |
| D3 v0.8 specification | APPROVED WITH STATED CONDITIONS (Alex, confirmed); immutable | sha256 3e053efc… |
| D3 v0.9 specification | Examined; **NOT APPROVED**; verification gate OPEN | sha256 ac2a2484… |
| D3 v0.10 specification | Built under Alex's adjudication; **NOT APPROVED**; awaiting independent re-examination | sha256 9241a8b4… |
| Fixture harness | v2.1 (fixtures-v010); 31 cases, all preserved from v0.9 | sha256 efe69df6…; results ad4dc137… |
| EXECUTION-CONTRACT-v0.1 | Untouched | sha256 c7e68901… |
| Simplification audit | Delivered; INPUT to planning, not a plan | sha256 13984600… |

Gate and authority:

- **Verification gate: OPEN.** v0.9 dispositions (Alex, pb-mwauqmco):
  R42 PASS, R47 FAIL, R56 PASS, R60 FAIL, R63 PASS, R65 FAIL; S2 a
  clarification, not a failure.
- **Stage 2: not authorised** in either sense (Contract design authorised
  2026-11-08, unstarted; execution not authorised).
- **Delegation in force:** Alex holds three calls — opening revision
  steps, approving D3, authorising Stage 2 execution. Spend, outreach,
  every publish, and accounts remain Ben's alone. Inside the programme
  loop, Alex's clearances initiate Remmy's steps; results are reported
  to Ben. (Alex's step-2 qualification, pb-mwavecjk: external authority
  means Ben's final authority over normative changes with delegated
  execution intact — not Ben personally approving every action.)
- **Adjudicators:** Alex (delegated, has ruled on v0.9). Grok — appointed
  second adjudicator by Ben; his ruling on the v0.9 gate is
  **outstanding**.
- **Examiners of record:** Claude (primary reviewer, v0.8 and v0.9) and
  Vane (independent examiner, v0.9).



## duenna-plan#007

- doc: duenna-plan
- heading: DUENNA — THE PLAN LIST > C. Open items register
- sha256: 77d919d250eae20a48beb6d5307942f70085bdbef6c07e18496319dc31737cae
- chars: 2464

## C. Open items register

| # | Item | State | Whose move |
|---|---|---|---|
| C-1 | Fixture gap R38 — reciprocal-link fixtures (v)/(vi) | OPEN, unverified | Separate authorised package only |
| C-2 | Fixture gap R48 — canonicalisation exclusion boundary | OPEN, unverified | Separate authorised package only |
| C-3 | Fixture gap R53 — consumption binding | OPEN, unverified | Separate authorised package only |
| C-4 | Fixture gap R55 — supersession annotation | OPEN, unverified | Separate authorised package only |
| C-5 | UX-1…UX-5 (checker independence; clocks; enumeration methods; satisfiability semantics; taxonomy finality) | OPEN; PROPOSED/UNRESOLVED statuses unchanged | Design process / Ben where reserved |
| C-6 | Grok's second adjudication (v0.9 gate) | OUTSTANDING | Grok, via Ben |
| C-7 | Documentary qualification — approval/authorisation letters are bridge records, not enclosed in any package | Standing; Alex's document-form adjudication: checkable in-package via the enclosed v0.8 spec; letters not re-litigated | Record |
| C-8 | Alex's old-window clusters 3–5 (implementation/fixture examination) | HELD at Alex's instruction | Alex |
| C-9 | DT3 — identical invented-URL test through Alex's seat (retrieval research) | UNTESTED | Ben to run |
| C-10 | Daily snapshot retry authorisation (Vane retrieval) | Card presented, untapped | Ben |
| C-11 | Discovery experiment (snapshot indexing) | Planted 2026-11-10 04:27; running on indexer time | Time; probe later |
| C-12 | AInternet per-seat pages (Alex's page, Vane's page) | Never made; scope card untapped | Ben |
| C-13 | Zombie forum-mongo-1 container sweep | Harmless, still restarting | Ben's hands (Docker Desktop) |
| C-14 | WordPress shelf suspension appeal | Unfiled; forum is the working replacement surface | Ben's hands |
| C-15 | **Forum backup (Ben's order, 2026-11-10 ~07:14):** back up the programme record to Ben's forum — FINAL job, after the Alex loop ends; get as far as possible; test with Qwen (Crusher) if possible | **COMPLETE (2026-11-10):** 12 documents as topics 4–15 in the Examination Room, all fetch-back verified; index topic 16 posted, verified, PINNED. Qwen test: Crusher answered the v0.8 FAIL question correctly with provenance (R42/R47/R56/R60/R63/R65; all six present in the forum ledger copy); corpus VERIFY PASS; corpus does NOT yet cover the adjudication/v0.10 material (UNKNOWN, correctly) — corpus admission is a separate decision | Remmy |



## duenna-step4-examination#007

- doc: duenna-step4-examination
- heading: DUENNA — STEP 4 EXAMINATION MATERIAL (duplicates · F5 edges · correction destinations) > Part 1 — The six duplicate pairs, examined against Alex's five checks > Pair 5 — REQ-J-2 (binding is not an authority) → REQ-A-2
- sha256: 5750d8d2d437b34d047af2327ac2f86e37f173257b5d5028ad14dcc3aa37e172
- chars: 941

### Pair 5 — REQ-J-2 (binding is not an authority) → REQ-A-2
1. J-2's guarantee: the binding mechanism exercises no discretion — it
   applies the approved, version-pinned contract and cannot select,
   skip or amend rules.
2. A-2's guarantee: deterministic resolution (identical inputs yield the
   identical contract instance), no mid-run rebinding, total failure
   rather than partial instances. Discretion-free binding is A-2's
   mechanics stated from the authority side.
3. Surviving requirement: A-2. 4. Surviving test: J-2's fixture retained
   under A-2 — and it *adds* sharpness: A-2's current fixtures prove
   byte-identical instances and mid-run stability; J-2's (a binding
   request that would omit a bound rule is rejected; output is a pure
   function of version + role + task type) tests the omission case they
   don't. 5. References: J-2 cites A-2; nothing cites J-2.
   **Verdict: all five checks pass. Clean merge.**



## duenna-step4-examination#009

- doc: duenna-step4-examination
- heading: DUENNA — STEP 4 EXAMINATION MATERIAL (duplicates · F5 edges · correction destinations) > Part 2 — F5: authority edges (response to Alex's strongest objection)
- sha256: e05cdc195c356a251f5847d988f75a024db3626762185c2eda54b68a8b247401
- chars: 2372

## Part 2 — F5: authority edges (response to Alex's strongest objection)

Alex's objection is sustained in part, and the mapping's claim is
corrected: F5 is not a shell with no edges. The precise model, with the
distinction that keeps enforcement from becoming discretion:

- **Governance edges (external, change what the pipeline runs on):**
  contract approval (J-1 → the rule-set F1 binds); supersession rulings
  (J-1 / H-3 → appended to the record, never edits). Decisions originate
  outside the machinery, always.
- **Enforcement edges (mechanical checks at pipeline points, verifying a
  permission state that is pinned in an approved artefact):** A-2 binds
  only an approved, version-pinned contract — approval is checked *as
  data* at F1's door; H-5's defect-discharge takes effect only when the
  pinned contract version contains the A1 revision — a version check,
  not a judgement; the E-6 gate judges evidence receipt against
  contract-set criteria before downstream stages rely on a result.
- **No decision edges:** no stage originates a permission, an approval
  or a waiver. Where a check fails, the machinery stops or refuses
  (fail-closed); it never substitutes its own permission.

Alex's three questions, answered in the model's terms: *Who may
establish or change a binding rule?* Ben, by J-1 — a governance edge.
*Who may initiate an instance?* No one's discretion: binding and record
events initiate mechanically; the authority was exercised upstream, in
approving the contract that defines the triggers. *What
determines whether downstream execution may proceed following a
verified result?* The gate evaluates evidence receipt against the
criteria established by the approved contract (E-6). The contract
defines the consequence of that result; the machinery applies it.
The gate originates no permission. (Question and answer corrected to
Alex's replacement wording on his verification of this document,
2026-11-10 — the original phrasing framed the gate as permitting,
the ambiguity retired in Part 2's model.)

Adopted formulation: **F5 is externally governed, mechanically enforced
authority** (Alex's words), with governance and enforcement edges drawn
explicitly in the dependency graph and decision edges absent by
construction. The mapping document's "orthogonal" is corrected to:
*orthogonal in decision, connected in enforcement.*



## duenna-step6-architecture#004

- doc: duenna-step6-architecture
- heading: DUENNA — STEP 6: THE SMALLEST VIABLE ARCHITECTURE > The consolidation register this architecture assumes
- sha256: cd4a02a4fc004d9ed615f752953639249987099fbda039db214f09e2437d25d0
- chars: 1303

## The consolidation register this architecture assumes

Five merges, with their conditions as settled in steps 4–5 —
conditions are requirements of the merges, not notes:

1. B-5 → D-1, with the surviving fixture scanning evaluator OUTPUT.
2. D-5 → D-3, machinery-defect residue labelled computation-layer
   in D-3's failure text; fixture asserts a machinery defect
   produces no F4 disposition.
3. D-6 → D-3, recovery sentence carried VERBATIM into G-2/F-1
   attempt material and present there normatively; dual-pointer
   tombstone.
4. D-2 split, AS CORRECTED AT STEP 5: B-2 receives the
   agent-declared-state clause only; D-3 retains the
   machinery-defect, voiding and re-derivation consequence; the
   fixture mapping names both survivors and which assertion each
   owns; tombstone and clause-level inventory preserve every part's
   destination.
5. J-2 → A-2, clean; the omission case joins A-2's fixtures.

Pair 6 stays OUT: H-7 is a standalone requirement in the proposal;
J-1 is owner-ruled and untouched. Net effect on the proposal:
48 requirement bodies → 43. C-3 remains one requirement with
obligations grouped by function, its machinery distributed across
RECORD (identity), EVALUATOR (fold order) and EXAMINER SURFACE
(re-derivation) as implementation placement, not as a split.



## alex-combined-adjudication-v010#006

- doc: alex-combined-adjudication-v010
- heading: ALEX — COMBINED TRACK 1 ADJUDICATION, D3 v0.10 > Authority status
- sha256: ceb366f10ac59b2c6a2b042a95fc7c66893deeb0e085734239d318d48582273f
- chars: 495

## Authority status

Full adjudication COMPLETE · R60 revision step OPEN · Remmy's
implementation AUTHORISED (two corrections only) · independent
re-examination REQUIRED · **v0.10 NOT APPROVED** · Stage 0 still
requires Ben's scope-card tap · Stage 2 NOT AUTHORISED · Grok's
adjudication outstanding and does NOT gate this decision. Ben
retains final authority over approval and the reserved gates.

Alex's closing principle, verbatim: "We are testing evidence,
not the appearance of evidence."

