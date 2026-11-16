# EXON — Development Letter 02 (Alex, 2026-11-16)

**Provenance:** Second letter of the EXON development
workstream (ChatGPT conversation 6afab3af), sent on the
owner's go of 2026-11-16 ("Proceed with Alex"). Letter 02
carried the owner's rulings on Letter 01's eight proposals —
seven as Alex recommended them, and Proposal 5 in the owner's
own ruled form: the comparison is a fact about how a stance
was reached and is required information wherever a stance
rests on one; COMPARED is a variable and the variable is
"=" — one symbol, visually two documents being compared;
the fact written beside the sign is the survivor of the
comparison. The letter also commissioned draft definitions
for the six newly admitted words. Send verified clean
(composer census + normalised content comparison). Collected
by direct page read and filed verbatim below (rendered-text
capture).

**Status:** Draft definitions and the "=" record design,
submitted for owner review. Nothing frozen; no existing
dictionary entry amended.

---

Letter 02 — Owner rulings acknowledged; draft definitions

The owner’s rulings supersede the corresponding recommendations in Letter 01. The four-category architecture remains. GRANT, AUTHORISE, SETTLED, DISTILLED, SETTLE and REVOKE are admitted for drafting; WAKE remains excluded.

COMPARED is adopted in the owner’s form. It is not a new dictionary word or a fifth category. The comparison marker is =: a record-level sign that a comparison occurred, with the surviving fact recorded beside it.

The drafts below follow Dictionary 0.4’s Part III pattern: definition, FORM and/or MEANING anchor, and nearest-neighbour boundary. They are proposals, not amendments to the shelved dictionary.

1. COMPARED — owner’s record design

The comparison belongs with the stance entry whose provenance depends on the comparison. It must not be detached into an unconnected comparison report.

Proposed record shape:

Plain text
stance_entry:
  comparison:
    compared_refs:
      - <first document or position reference>
      - <second document or position reference>
    = <surviving fact or position>
    non_survivor:
      ref: <reference to the other side>
      disposition: NOT_CARRIED_FORWARD

Where = sits: inside the stance entry, directly beside the fact or position that survived the comparison. It marks that the stance was reached by comparison.

What the survivor carries: the actual surviving fact or position, with its source reference. The marker does not itself prove that fact true; its evidential standing remains subject to the normal evidence rules.

What happens to the other side: it remains identified by reference as the non-surviving comparison input. It is not deleted, silently discarded, or automatically declared false. NOT_CARRIED_FORWARD means only that it did not survive into this stance.

This makes the comparison history part of the stance's recorded basis. A reader can see both what was compared and what was carried forward, without confusing the comparison event with proof, agreement, or adjudication.

The exact spelling and serialization of NOT_CARRIED_FORWARD are draft schema choices, not admissions to Dictionary 0.4. The operative design is the owner's = marker and the preservation of both sides.

2. Draft dictionary entries
Outcomes and states

SETTLED — The named matter has reached a recorded resolution and is no longer open for decision in that matter.

FORM: a record identifies the matter and the act or decision by which it was resolved.

MEANING: where the resolution or its authority is disputed, adjudication determines whether the matter was genuinely settled.

Boundary: ≠ COMPLETE — settlement of a matter does not establish that every element of a named set is satisfied; ≠ ACCEPTED — settlement is not criteria-based acceptance of an artefact; ≠ RELEASED — resolution does not establish that an artefact entered its destination. SETTLED describes the resulting state, not the act that produced it.

Evidence and claims

DISTILLED — An artefact produced by transforming identified source material into a reduced or otherwise transformed representation, while retaining an explicit connection to the source.

FORM: the source reference or references, the resulting artefact, and the transformation method are identified. Where the method is versioned, its version is recorded.

MEANING: whether the transformation preserves the information material to the stated purpose; a FORM pass alone does not establish fidelity, accuracy, or completeness.

Boundary: ≠ EVIDENCE — being a distilled artefact does not by itself establish that it supports a claim; ≠ VERIFIED — transformation is not independent reproduction; ≠ SUPPORTED — a distilled representation does not establish the claim it describes. A DISTILLED artefact is not the original source and must not be presented as though it were the full source.

Authority and acts

GRANT — To confer a defined right to a named seat or principal, within an expressly stated class of acts and scope, by an actor holding authority to grant that right.

FORM: a grant record identifies the recipient, the right or permitted class of acts, the scope, the granting authority relied on, and the effective terms of the grant.

MEANING: whether the grantor held authority to confer the stated right and whether the right falls within the stated scope.

Boundary: ≠ AUTHORISE — GRANT establishes a right held by a recipient; AUTHORISE permits a particular act under applicable authority. ≠ DELEGATION — DELEGATION transfers a bounded task and listed authority; a GRANT need not delegate a task. ≠ RULING — a RULING decides a matter and does not, merely by being issued, confer a right.

AUTHORISE — To record permission for a named act by a named seat, within a stated scope, under authority applicable to that act.

FORM: an authorisation record identifies the actor permitted to act, the act, its scope, the authority relied on, and the authorisation decision.

MEANING: whether the relied-on authority covers the authorisation and whether the permitted act falls within its scope.

Boundary: ≠ GRANT — AUTHORISE permits a specified act; GRANT confers a defined right. ≠ AUTHORITY — AUTHORITY is the recorded right to perform a class of acts; AUTHORISE is the exercise of that authority to permit a particular act. ≠ RULING — a RULING resolves a matter through an authoritative decision; AUTHORISE grants permission to act. Authorisation does not prove that the act was subsequently performed.

SETTLE — To resolve a named outstanding matter by an act performed under authority applicable to that matter, producing a recorded resolution.

FORM: the settlement record identifies the matter, the resolution reached, the act or decision effecting it, and the authority relied on.

MEANING: whether the act validly resolves the matter within the authority and scope stated.

Boundary: ≠ RULING — a RULING is an authoritative decision; SETTLE is the act of resolving the outstanding matter. A RULING may be the means by which a matter is settled, but the words describe different operational facts. ≠ SETTLED — SETTLE is the act; SETTLED is the resulting state. ≠ COMPLETE — settling a matter does not establish that all elements of an obligation or named set are satisfied. ≠ REVOKE — settlement resolves a matter; revocation withdraws a previously granted right.

REVOKE — To withdraw, by an act under applicable authority, a right previously granted to a named recipient, within the scope stated in the revocation.

FORM: the revocation record identifies the original grant, the recipient, the right and scope withdrawn, the authority relied on, and the effective point of withdrawal.

MEANING: whether the revoking actor held authority to withdraw that right and whether the revocation covers the stated scope.

Boundary: ≠ SUPERSEDE — SUPERSEDE replaces a commitment with an authorised successor; REVOKE withdraws a granted right. ≠ STOP — STOP halts a named operation subject to a release condition; REVOKE withdraws authority. ≠ CORRECTION — CORRECTION repairs a wrong record; REVOKE changes the status of a right. Revocation does not, by itself, erase the grant record or establish that earlier acts under the grant were unauthorised.

Infrastructure caveat: REVOKE defines an act and the record needed to describe it. It does not assert that an authority registry, automated revocation mechanism, or live authority resolver exists. Dictionary 0.4's Gap 5 remains applicable.

3. Review notes

Three distinctions are especially important for the owner's review:

GRANT / AUTHORISE / RULING: a right is conferred, a particular act is permitted, or a matter is decided. These are not interchangeable.

SETTLE / SETTLED: the act and its resulting state are separate operational facts. Neither means that an obligation is COMPLETE.

REVOKE: withdrawal affects the right from its stated effective point. It does not rewrite history or establish that earlier reliance was invalid.

For = the critical preservation rule is that the non-surviving side remains traceable. Not carrying it forward into the stance is not the same as deleting it or proving it false.

Submission status: six draft definitions prepared; COMPARED record design expressed; four categories retained; WAKE excluded. Nothing frozen, no existing dictionary entry amended, and no implementation or validator work undertaken.

These drafts return to the owner for review.

You're using the free version of ChatGPT. Upgrade for advanced models, better memory, and higher-quality image creation.
Try Plus free
