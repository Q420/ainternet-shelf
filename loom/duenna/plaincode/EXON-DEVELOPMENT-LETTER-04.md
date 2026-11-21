# EXON — Development Letter 04 (Alex, 2026-11-16)

**Provenance:** Fourth letter of the EXON development
workstream (ChatGPT conversation 6afab3af), sent on the
owner's direct order of 2026-11-16 ("Take this all to
Alex"). Letter 04 carried the owner's ruling on the
question Letter 03 returned: the dispositions get their
own words, both Rule 1 interferences closed by the
owner's coinages — FUTILE (tested and did not hold),
IMPOSSIBLE (was always hopeless), DENIED (set aside by
decision, though it may stand) — with DEPRECATED retained
from Alex's draft. It commissioned the four entries in
Dictionary 0.4 style, the '=' record updated to the final
vocabulary, and Dictionary 0.5 assembled as a draft for
owner review. Send verified clean (composer census +
normalised content comparison). Collected by bounded wait
and filed verbatim below (rendered-text capture).

**Status:** Dictionary 0.5 exists as the integrated draft
inside this letter (48 terms: the 0.4 base of 38 plus ten
admitted additions), presented as replacement and
insertion text against DICTIONARY-04.md, not as a
standalone document. Draft for owner review; nothing
frozen. Two reconciliation points are returned open:
the MALFORMED boundary change, and STOP schema / field
matrix reconciliation (no reason code invented). The
owner's HARDENED addition (a grade above VERIFIED, ruled
2026-11-16 01:15 MST) arrived after this letter was sent
and is not in the 0.5 draft; it rides in the next letter.

---

Letter 04 — Dictionary 0.5 draft

The owner has resolved the semantic collision by giving the dispositions their own words. The four meanings are now distinct:

FUTILE — this test failed the position.

IMPOSSIBLE — no test ever could establish the position; it was always hopeless.

DENIED — a decision set the position aside, whether or not it was true.

DEPRECATED — the former standing fact was replaced by a successor.

This preserves FAILED as a RESULT outcome and REJECTED as an existing RULING/ACCEPT decision. The disposition vocabulary no longer borrows either token.

1. Four new disposition entries

All four belong under Outcomes and states. They describe the disposition of a non-surviving comparison position, not the outcome of a RESULT or the decision value of a RULING or ACCEPT.

FUTILE

The identified position was tested by a named test and did not hold under that test.

FORM: basis_ref resolves to the test record, which identifies the tested position, method, and result.

MEANING: whether the test was applicable and adequately performed.

Boundary: FUTILE records failure under the identified test; it does not establish that the position could never hold. It is not FAILED, which remains a RESULT outcome. It is not IMPOSSIBLE.

IMPOSSIBLE

The identified position was incapable of holding; no test could establish it as a viable position. It was not merely unsuccessful under one test.

FORM: basis_ref resolves to the record or reasoning establishing the impossibility, with the constraints or facts on which that finding rests.

MEANING: whether those constraints genuinely make the position impossible.

Boundary: IMPOSSIBLE is stronger than FUTILE. FUTILE says this test did not support the position; IMPOSSIBLE says the position could not hold at all. It is not NOT_ESTABLISHED, which records that a procedure did not establish a claim without finding it false.

DENIED

The identified position was set aside by decision, whether or not the position itself may stand.

FORM: basis_ref resolves to the decision record identifying the position and the decision that set it aside.

MEANING: whether the decision was made by the appropriate authority and actually applies to the identified position.

Boundary: DENIED records what happened to the position in the decision; it does not declare the position false. It is not REJECTED, which retains its existing RULING and ACCEPT decision functions. It is not CONTRADICTED, which establishes falsity.

DEPRECATED

The identified position was formerly the standing fact and ceased to be so when a successor replaced it.

FORM: basis_ref resolves to the successor record that replaced the former standing fact.

MEANING: whether the successor genuinely replaces the former fact for the relevant scope.

Boundary: DEPRECATED describes the former fact's status; it is not SUPERSEDE, the act of prospectively replacing a commitment. It does not erase the former fact or establish that it was false.

2. Revised = record design

The owner's four dispositions replace the previous three-value vocabulary.

YAML
stance_entry:
  comparison:
    left_ref: <first document or position reference>
    right_ref: <second document or position reference>

    "=":
      survivor:
        ref: <surviving source reference>
        fact: <fact or position carried into the stance>

      non_survivor:
        ref: <other source reference>
        disposition:
          reason: <FUTILE | IMPOSSIBLE | DENIED | DEPRECATED>
          basis_ref: <supporting test, finding, decision, or successor>

The record rules are:

= sits beside the surviving fact within the stance entry.

The survivor carries the fact or position that the current stance adopts, with its source reference.

The non-survivor remains identifiable as a comparison input.

Its disposition reason is mandatory and comes from the closed vocabulary.

Its basis_ref is mandatory and points to the specific basis appropriate to that reason.

A non-survivor is not deleted. Its disposition does not imply falsity unless the particular reason establishes that conclusion.

The comparison marker records that comparison occurred. It does not itself establish truth, support, verification, or authority.

The four reason-to-basis relationships are fixed:

Disposition

	

Required basis_ref




FUTILE

	

The test and its result




IMPOSSIBLE

	

The basis establishing impossibility




DENIED

	

The decision setting the position aside




DEPRECATED

	

The successor replacing the former standing fact

This remains a draft record convention. It does not claim that a corresponding schema validator or automated comparison mechanism exists.

3. Dictionary 0.5 — integrated draft

The complete document should retain the 0.4 base unchanged wherever no amendment is specified. Its source is the retrieved Shelf file DICTIONARY-04.md, blob 49c2408065110ef5e096781862d4b9a59f449623.

The following is the integrated replacement and insertion text for the new version. It is deliberately explicit about the places where 0.4's existing wording must change.

Writing
EXON DICTIONARY 0.5 — INTEGRATED DRAFT FOR OWNER REVIEW

Status: DRAFT. Not frozen, not approved. The freeze decision remains with Ben. No replay, validator, pilot, or implementation is authorised by this document.

Base: DICTIONARY-04.md, Shelf blob 49c2408065110ef5e096781862d4b9a59f449623.

Integration rule: All 0.4 material not expressly replaced or amended below is carried forward unchanged. The existing four dictionary categories and nine schema categories remain fixed.

Part I — Categories and counts

Layer A — Dictionary terms: four fixed categories.

Outcomes and states

Evidence and claims

Authority and acts

Messages and records

The 0.4 inventory of 38 terms is expanded by ten admitted terms, giving a draft inventory of 48 terms.

The ten additions are:

GRANT

AUTHORISE

SETTLED

DISTILLED

SETTLE

REVOKE

FUTILE

IMPOSSIBLE

DENIED

DEPRECATED

The = comparison marker is a record convention, not a dictionary term or fifth category.

Layer B — Schema keywords and enumerated values: the existing nine fixed categories are retained.

Layer C — Ordinary prose: the existing four fixed functional categories are retained.

Part III — The dictionary

All 0.4 entries remain unchanged except where expressly amended below. The following entries are added or replaced.

Outcomes and states

SETTLED — The named matter has reached a recorded resolution and is no longer open for decision in that matter.

FORM: the record identifies the matter and the act or decision by which it was resolved.

MEANING: whether the resolution genuinely determines the matter within the authority and scope applicable to it.

Boundary: SETTLED is a resulting state, not the act that produced it. It is not COMPLETE, which requires every element of a named set to be satisfied; not ACCEPTED, which is criteria-based artefact acceptance; and not RELEASED, which records an artefact entering its destination. SETTLED does not establish that an associated obligation is COMPLETE or discharged.

FUTILE — The identified position was tested by a named test and did not hold under that test.

FORM: basis_ref resolves to the test record, which identifies the tested position, method, and result.

MEANING: whether the test was applicable and adequately performed.

Boundary: FUTILE records failure under the identified test; it does not establish that the position could never hold. It is not FAILED, which remains a RESULT outcome. It is not IMPOSSIBLE.

IMPOSSIBLE — The identified position was incapable of holding; no test could establish it as a viable position. It was not merely unsuccessful under one test.

FORM: basis_ref resolves to the record or reasoning establishing the impossibility, with the constraints or facts on which that finding rests.

MEANING: whether those constraints genuinely make the position impossible.

Boundary: IMPOSSIBLE is stronger than FUTILE. FUTILE says this test did not support the position; IMPOSSIBLE says the position could not hold at all. It is not NOT_ESTABLISHED, which records that a procedure did not establish a claim without finding it false.

DENIED — The identified position was set aside by decision, whether or not the position itself may stand.

FORM: basis_ref resolves to the decision record identifying the position and the decision that set it aside.

MEANING: whether the decision was made by the appropriate authority and actually applies to the identified position.

Boundary: DENIED records what happened to the position in the decision; it does not declare the position false. It is not REJECTED, which retains its existing RULING and ACCEPT decision functions. It is not CONTRADICTED, which establishes falsity.

DEPRECATED — The identified position was formerly the standing fact and ceased to be so when a successor replaced it.

FORM: basis_ref resolves to the successor record that replaced the former standing fact.

MEANING: whether the successor genuinely replaces the former fact for the relevant scope.

Boundary: DEPRECATED describes the former fact's status; it is not SUPERSEDE, the act of prospectively replacing a commitment. It does not erase the former fact or establish that it was false.

Evidence and claims

DISTILLED — An artefact produced by transforming identified source material into a reduced or otherwise transformed representation while retaining an explicit connection to its source.

FORM: source references, resulting artefact, and transformation method are recorded.

MEANING: whether the transformation preserves the information material to its stated purpose.

Boundary: DISTILLED does not establish accuracy, completeness, fidelity, support, or verification by itself. It does not establish permission to enter the canonical EXON Shelf. That crossing is subject to the comparison and Distillery doctrine.

Authority and acts

GRANT — To confer a defined right on a named seat or principal, within an expressly stated class of acts and scope, by an actor holding authority to grant it.

FORM: the grant record identifies the recipient, right or act class, scope, granting authority relied upon, and effective terms.

MEANING: whether the grantor held the authority to confer the right and whether the right falls within the stated scope.

Boundary: GRANT confers a right; AUTHORISE records permission for a particular act. It is not DELEGATION, which transfers a bounded task and its listed authority. A RULING decides a matter and does not, merely by being a RULING, confer a right.

AUTHORISE — To record permission for a named act by a named seat within a stated scope, under the authority applicable to that act.

FORM: the authorisation record identifies the permitted actor, act, scope, authority relied upon, and authorisation decision.

MEANING: whether the authority covers the permission and the act falls within scope.

Boundary: AUTHORISE grants permission for a particular act; GRANT confers a defined right. AUTHORISE is not AUTHORITY itself, which is the recorded right, and is not RULING, which records an authoritative decision. Authorisation does not prove that the act was performed.

SETTLE — To resolve a named outstanding matter by an act under the authority applicable to that matter, producing a recorded resolution.

FORM: the record identifies the matter, resolution, act or decision effecting it, and authority relied upon.

MEANING: whether the act validly resolves the matter within the applicable authority and scope.

Boundary: SETTLE is the resolving act; SETTLED is the resulting state. It is not RULING, although a RULING may be the means by which a matter is settled. It is not COMPLETE, which concerns satisfaction of every element in a named set. It is not REVOKE, which withdraws a previously granted right.

REVOKE — To withdraw, by an act under applicable authority, a right previously granted to a named recipient, within the stated scope.

FORM: the record identifies the original grant, recipient, right and scope withdrawn, authority relied upon, and effective point.

MEANING: whether the revoking actor held the authority and whether the revocation covers the stated scope.

Boundary: REVOKE withdraws a granted right; it is not SUPERSEDE, which replaces a commitment, STOP, which halts a named operation, or CORRECTION, which repairs an erroneous record. Revocation does not erase the original grant or establish that earlier acts were unauthorised. This definition does not imply that a dedicated authority registry or automated revocation mechanism exists.

Comparison record convention — =

The = marker records a comparison that forms part of the basis for a current stance.

The marker is placed inside the stance entry, immediately beside the fact or position that survived comparison.

Draft record shape:

stance_entry:
  comparison:
    left_ref: <first document or position reference>
    right_ref: <second document or position reference>

    "=":
      survivor:
        ref: <surviving source reference>
        fact: <fact or position carried into the stance>

      non_survivor:
        ref: <other source reference>
        disposition:
          reason: <FUTILE | IMPOSSIBLE | DENIED | DEPRECATED>
          basis_ref: <supporting test, finding, decision, or successor>

The survivor is the fact or position carried into the current stance. The non-survivor remains identifiable as a comparison input and carries a reason-classified disposition.

The disposition vocabulary is closed. A new disposition reason may be admitted only by ruling, and only where it changes what a reader may conclude.

The basis_ref is mandatory and must resolve to the basis appropriate to the selected disposition:

FUTILE — the test and its result.

IMPOSSIBLE — the basis establishing impossibility.

DENIED — the decision setting the position aside.

DEPRECATED — the successor replacing the former standing fact.

A non-survivor is not deleted. Its disposition does not, by itself, establish falsity. The comparison marker does not independently establish truth, support, verification, or authority.

This is a draft record convention. No existing message type, field matrix, or validator is claimed to implement it.

STOP — replacement entry

STOP — A recorded halt of a named operation, initiated only when falsity enters canonical Shelf content: either false content is written to the canonical fact Shelf, or false Shelf content is written into the canonical EXON Shelf.

The EXON Shelf is the operational language Shelf: its contents are what operations act upon. False content crossing into it is therefore a corrupted crossing.

FORM: the STOP record identifies the affected operation and the false canonical Shelf content that triggered the halt. The record identifies the relevant Shelf location and the basis establishing falsity. The STOP carries its release condition and the authority permitted to record its release.

MEANING: whether the content is genuinely false and whether it entered a canonical Shelf.

Boundary: a failed test, a FUTILE disposition, a DENIED disposition, a DEPRECATED disposition, a flag, a concern, or a failure that has not entered canonical Shelf content does not by itself initiate STOP. Escalation follows reliance, not vocabulary.

The comparator guards the crossing. The Distillery is the crossing and carries this safety doctrine. The comparison record identifies the surviving position and the reason the other side did not survive.

This definition does not claim that the comparator, Distillery, or automated STOP enforcement has been implemented.

MALFORMED — replacement boundary

MALFORMED — A message fails VALID. It is not interpreted, repaired, or partially honoured.

Boundary: MALFORMED is a conformance failure, not a finding that false content has entered a canonical Shelf. A conformance failure alone does not initiate STOP under the STOP threshold. The response to a malformed message must not be described as STOP unless the canonical-Shelf falsity condition has also occurred.

Part II and Part IV carry-forward

The 0.4 field matrix and nine message definitions are carried forward as the current baseline. The = record convention is not silently represented as an already-adjudicated matrix change. Its fields and legal message-type placement require reconciliation with the authoritative field matrix before they can be treated as operative schema.

The existing STOP fields, reason-code vocabulary, and message definition remain subject to reconciliation with the new STOP threshold. No new STOP reason-code value is invented here.

Part V — Flag lifecycle

Carry forward unchanged from 0.4.

A flag continues to create an independent second-look obligation. It does not halt an operation, invalidate content, change an evidence class, or confer authority by itself. A flag is not a STOP trigger.

Part VI — FORM / MEANING audit

Carry forward the 0.4 audit table, with these additional checks:

Check	FORM establishes	MEANING still decides
FUTILE	test record and result resolve	test applicability and adequacy
IMPOSSIBLE	impossibility basis resolves	whether the basis establishes impossibility
DENIED	decision record resolves	authority and application of the decision
DEPRECATED	successor record resolves	whether it replaces the former standing fact
= comparison	both inputs, survivor, non-survivor, disposition and basis resolve	whether the survivor and disposition are justified
STOP	false canonical Shelf content and affected operation are identified	whether the content is false and has entered the canonical Shelf
Part VII — Enforcement honesty

Carry forward the 0.4 gap-register and enforcement-honesty statements unchanged, with this addition:

The comparator and Distillery doctrine specifies the intended safety boundary for crossing into canonical EXON. It does not establish that the crossing guard, Distillery process, Shelf write control, or STOP enforcement exists. No mechanical enforcement claim is made until the relevant mechanism is retrieved or built, version-pinned, and independently tested.

Submission status: Dictionary 0.5 is a draft for owner review. Nothing is frozen. No validator, replay, pilot, or implementation is authorised by this document.

4. Change list against 0.4

Area

	

Change in 0.5




Part I

	

Dictionary count increases from 38 to 48; four categories remain fixed.




Outcomes and states

	

Adds SETTLED, FUTILE, IMPOSSIBLE, DENIED, DEPRECATED.




Evidence and claims

	

Adds DISTILLED with the owner's crossing boundary.




Authority and acts

	

Adds GRANT, AUTHORISE, SETTLE, REVOKE.




Comparison

	

Adds the = record convention with survivor, non-survivor, closed disposition reason, and mandatory basis_ref.




STOP

	

Replaces the general halt threshold with the canonical-Shelf falsity threshold; records the comparator and Distillery roles.




MALFORMED

	

Removes the automatic implication that a malformed message necessarily produces STOP.




Part VI

	

Adds FORM/MEANING checks for the new terms and comparison record.




Part VII

	

Adds enforcement honesty for the comparator and Distillery.




Part II / Part IV

	

Carried forward as baseline pending reconciliation with the field matrix.

5. Two material reconciliation points returned for review

There are two existing 0.4 statements that the owner's doctrine necessarily changes:

MALFORMED currently says the governing procedure produces STOP. That cannot remain as written if STOP has only one initiating condition. The draft changes the boundary so malformed content alone does not trigger STOP.

The existing STOP schema permits an optional reason_ref, and its reason-code set is already closed. The new doctrine needs the false canonical Shelf content identified as the basis for the halt. I have not invented a tenth reason code or silently rewritten the field matrix. The matrix must be reconciled before the new STOP record can be treated as schema-complete.

There is also a deliberate distinction between the dictionary draft and implementation: the = record convention is specified here, but its final legal placement in the field matrix remains to be adjudicated.

Submission status: the four disposition entries, comparison design, six Letter 02 definitions, Letter 03 DISTILLED/STOP refinements, and the affected 0.4 boundaries are drafted. The four-category structure and all earlier owner rulings are preserved. Nothing is frozen.