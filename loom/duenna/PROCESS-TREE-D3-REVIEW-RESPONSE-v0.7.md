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

## Register boundary

This register records verified findings and proposed corrections.
It changes no specification text, approves nothing, and authorises
nothing. The next steps remain governed, in order: Alex's review of
this register; Ben's decision on a v0.8 revision step; Ben's approval
of D3; Ben's separate authorisation of Stage 2 execution.
