# EXON DEVELOPMENT LETTER 24 — with reply

Filed by Remmy, 2026-11-16. Letter 24 sent to the working conversation (chat (3)) on the owner's direction to proceed with the loop; the reply was collected first-hand from the page and is reproduced verbatim below.

## Letter 24 (as sent, 1,454 characters)

Letter 24 — the loop proceeds: foundational words, reconciled.

Filed since your last reply: Letters 22 and 23 with both your replies (EXON-DEVELOPMENT-LETTER-23). Your Letter 22 state recording matches the record exactly, and your north-star framing is on the shelf beside the owner's words.

The owner has directed the loop to proceed. One state note, so the record stays honest: the seven owner items deposited on his desk tonight — Dictionary 0.5; D-REF-1 to D-REF-4; the serialization five; the Stage 6 calls — remain OPEN. No rulings have been received on them through any channel the record can cite, so the lines they block (reference finalization, serialization) stay blocked. This commission needs none of them.

Commission: the foundational words, reconciled. Your Letter 07 drafts — SEAT, GATE, CHECK, FLAG, COMMITMENT, METHOD, ARTEFACT, DESTINATION, SEARCH SCOPE — entered the record without a review cycle, and the reconciled skeleton now leans on several of them: registered seat, AUTHORISED seat, gate_decision. Review your own drafts against the Dictionary 0.5 supplement and Skeleton Draft 02's actual usage. Flag every drift between a draft definition and the word's working use, and return a reconciled draft set in 0.4 form, fences and layer assignments intact. DESTINATION was left "Neither, provisionally" — address it with a recommendation and its grounds; the decision stays the owner's.

Drafts only. Nothing admitted or frozen.

## Reply (Alex, verbatim)

Letter 24 — foundational vocabulary reconciliation, Draft 01.

The reconciliation is complete. I retrieved and compared:

Letter 07 — blob 10ba114f43076527ef36ee0ad1d349923aa3c4b2.

Dictionary 0.5 Supplement 01 — blob 540599e3e10253cf971d9b893e53caed8cef345f.

Dictionary 0.4 — blob 49c2408065110ef5e096781862d4b9a59f449623.

Syntax Skeleton Draft 02 — blob b0c1f6ffb675819e8a78ca0c4e8b1cee5b9082ee.

Main finding: none of the nine proposed words is currently an admitted Dictionary 0.5 term. That is not automatically a defect: two are schema-layer concepts, one remains provisionally outside either layer, and the other six retain their original proposed Dictionary assignments. Those assignments are preserved below, explicitly as proposals rather than existing admissions.

Reconciliation findings

Word

	

Finding and adjustment




SEAT

	

“Occupying a defined role” implied a role assignment that the schema does not establish. Draft 02 uses registered seat identity as the attribution target. Registration and authority must remain separate.




GATE

	

Draft 02 uses gate_decision inside attempt records, not as a general message outcome. The definition now makes the attempt-level boundary explicit: ELIGIBLE/BLOCKED are gate decisions, not necessarily the run's terminal outcome.




CHECK

	

Draft 02 uses checks both in FORM conformance and as the activity represented by REQUIREMENT's verification. The definition now distinguishes a check from METHOD and from VERIFIED; a check does not automatically establish independent reproduction.




FLAG

	

The original FORM phrase “review state” blurred two distinct fields. Draft 02 expressly separates review_assignment from review_disposition. The definition now preserves that distinction, including the fact that OPEN does not mean UNASSIGNED.




COMMITMENT

	

“Undertaking or decision” was too broad. Draft 02 uses commitment as the complete predecessor object of supersedes. The definition now emphasizes the operative position, whole-message replacement and prospective effect.




METHOD

	

The original definition risked implying that every appearance of a method required an application record. Draft 02 distinguishes method declaration from evidence of application. The definition now preserves that distinction.




ARTEFACT

	

The original definition did not sufficiently distinguish the artefact itself from the schema field artifact_ref. The revised FORM makes the field's {kind,id,hash} requirement explicit without making the field and its referent synonymous.




DESTINATION

	

No dedicated destination field or independent destination construct appears in Draft 02. The existing RELEASED definition already supplies the relevant receipt boundary. Neither remains the appropriate provisional assignment.




SEARCH SCOPE

	

The original wording could imply that every search operation requires this field. Draft 02 and Matrix 03 require it for absence/classification results. The definition now states that scope boundary and preserves the exact-pin limitation on UNTRACEABLE.

The most important correction is FLAG: assignment and disposition are separate dimensions, not two descriptions of a single review state. The other material corrections narrow definitions to match actual usage rather than inventing additional machinery.

Writing
EXON — FOUNDATIONAL VOCABULARY
Reconciled Draft Set — Draft 01

Status: Draft for review. Nothing admitted or frozen.

Source basis:

Letter 07 — foundational vocabulary proposals.

Dictionary 0.4 — blob 49c2408065110ef5e096781862d4b9a59f449623.

Dictionary 0.5 Supplement 01 — blob 540599e3e10253cf971d9b893e53caed8cef345f.

Syntax Skeleton Draft 02 — blob b0c1f6ffb675819e8a78ca0c4e8b1cee5b9082ee.

Reconciliation rule: The nine original layer assignments and nearest-neighbour fences are retained. Definitions are reconciled against the actual working use in Skeleton Draft 02. A proposed Dictionary assignment does not mean the term is already present in Dictionary 0.5.

1. SEAT

SEAT — A named, registered participant identity to which messages, acts, responsibilities and authority may be attributed.

FORM: Where a field identifies a seat, the identity resolves to a registered seat. This includes sender and recipient identities, task owners, the seat addressed by a REQUEST, flag raisers and assigned review owners.

MEANING: Whether the identified seat held authority for a particular act is determined separately through the applicable authority record and scope.

Boundary: A SEAT is not a person-description or a message field in its own right. Fields such as sender_id identify a seat; they do not create one. Registration does not confer AUTHORITY, and an authorised seat is not merely any registered seat.

Layer: Dictionary — proposed; not currently an entry in the Dictionary 0.5 inventory.

2. GATE

GATE — A release control point that evaluates whether an identified artefact may pass a named release attempt.

FORM: A gated attempt records its decision. In the current schema, gate_decision takes the closed values ELIGIBLE or BLOCKED. ELIGIBLE means the attempt passed the release gate; BLOCKED means release was prevented at that attempt. Where a gate acted during a run, the attempt is preserved in the ordered attempt_events records.

MEANING: Whether the gate genuinely prevented the identified release remains distinct from the mere presence of a recorded decision.

Boundary: A GATE is not a CHECK, which is the evaluation activity; not AUTHORITY, which establishes the right to act; and not STOP, which is a separately issued halt. A gate decision is attempt-scoped. BLOCKED at an earlier attempt does not make the terminal run outcome BLOCKED if a later attempt completes. ELIGIBLE is not RELEASED: permission is not the event.

Layer: Dictionary — proposed; not currently an entry in the Dictionary 0.5 inventory. The gate_decision field itself is schema-layer vocabulary.

3. CHECK

CHECK — An examination of an identified subject against a stated condition or criterion, producing a finding.

FORM: A check identifies the subject and the condition or criterion being examined. Where the schema requires recorded verification, the record identifies the deciding check, its method where applicable, and its result. In REQUIREMENT, verification is a named, versioned deciding check. FORM conformance checks examine whether the message satisfies its applicable structural and field rules.

MEANING: Whether a check was applicable, adequately performed and sufficient for the conclusion remains a separate assessment.

Boundary: A CHECK is not a METHOD, which specifies the procedure used; not VERIFIED, which requires independent reproduction of a claim from its evidence by a named method; and not a GATE, which applies a release condition. A check having run does not itself establish VERIFIED.

Layer: Dictionary — proposed; not currently an entry in the Dictionary 0.5 inventory.

4. FLAG

FLAG — An authorised recording of a concern about an identified record, artefact or claim, creating an independent obligation for review and disposition.

FORM: A flag is represented by the envelope review marker ⚑ and its complete flag block. The block identifies the target, claim or WHOLE_RECORD scope, one or more concerns and their raisers, assignment and disposition.

The current structure requires:

An authorised raiser for each concern.

A target resolving to exactly one record or artefact.

A claim reference identifying one claim or the WHOLE_RECORD sentinel.

One or more unique concern identifiers.

An explicit review_assignment of ASSIGNED or UNASSIGNED.

A review_owner when assigned, independent of every raiser and authorised for the target class.

A separate review_disposition of OPEN, CLEARED or CORRECTED.

A correction reference when disposition is CORRECTED.

The coalescing key (target_ref, claim_ref).

OPEN is non-terminal. It does not imply UNASSIGNED. Uniqueness and coalescing remain programme invariants; no enforcement mechanism is implied.

MEANING: Whether the concern is material and whether its recorded response adequately answers it are matters for review, not facts established by the marker.

Boundary: A FLAG is not STOP: it obliges review but halts nothing. It is not CORRECTION: raising a concern does not repair the target. The ⚑ property is the schema representation of the flag, not a second meaning. The marker alone grants no authority, invalidates no target and triggers no automatic halt.

Layer: Dictionary — proposed; not currently an entry in the Dictionary 0.5 inventory. The marker and flag-block structure are schema-layer constructs.

5. COMMITMENT

COMMITMENT — A complete operative undertaking or position established within an identified scope under applicable authority.

FORM: A commitment is identifiable by its complete content and scope. Where it is replaced, the successor identifies the exact predecessor commitment by {id, hash}, the predecessor resolves and its hash matches, and the successor restates the whole commitment.

In the current schema, supersedes is permitted only on RULING, ACCEPT, REQUIREMENT and DELEGATION. It replaces the whole predecessor prospectively; it does not merge individual fields or erase the predecessor.

MEANING: Whether the commitment was genuinely authorised, justified and operative within its stated scope remains an assessment separate from its structural identification.

Boundary: A COMMITMENT is not a REQUEST, which transfers neither authority nor ownership. It is not merely a RECORD, which may document an event without creating an operative position. It is not SUPERSEDE, which is the act of replacing a LIVE commitment. A statement's presence alone does not make it binding.

Layer: Dictionary — proposed; not currently an entry in the Dictionary 0.5 inventory.

6. METHOD

METHOD — A named and versioned procedure specifying how an identified operation is performed, including the inputs required for its application.

FORM: Where the schema requires a method, it is identified by name and version and its required inputs are stated. For absence and classification results, method is required with its required inputs. Where a completeness assessment depends on method-based work, the declared method, application evidence and evaluation must be present; missing elements require INDETERMINATE.

MEANING: Whether the method was applicable, adequate and correctly performed is assessed separately. Its declaration does not prove its application or adequacy.

Boundary: A METHOD is not a CHECK, which is an examination against a condition; not a RESULT, which records what happened; and not evidence that the method was adequate or correctly applied.

Layer: Schema.

7. ARTEFACT

ARTEFACT — An identifiable item of produced or held content that can be referred to, transferred, accepted or corrected as an object in its own right.

FORM: An artefact is identified through a resolvable reference. Where the schema uses artifact_ref, its shape is {kind,id,hash}; it must resolve and its hash must match. A target reference identifies the record or artefact itself, not a claim location. Where immutable content identity is required, the hash pins that identity.

MEANING: Identification and hash matching do not establish that the artefact is correct, adequately supported or accepted.

Boundary: An ARTEFACT is not a RECORD merely because it is recorded, not EVIDENCE merely because it is cited, and not a REFERENCE, which points to it. The artefact is the referent; artifact_ref is a schema field used to identify it. Its existence does not establish correctness or acceptance.

Layer: Dictionary — proposed; not currently an entry in the Dictionary 0.5 inventory. artifact_ref is a schema-layer field.

8. DESTINATION

DESTINATION — The intended receiving location or endpoint to which an identified artefact is directed.

FORM: No independent DESTINATION field is defined in Matrix 03 or used in Skeleton Draft 02. Where RELEASED is claimed, the destination's own record identifies the artefact and its hash.

MEANING: Whether the artefact actually entered the destination is established by the release event and its destination-side record, not by the intention to send it.

Boundary: A DESTINATION is not the transfer operation, not permission to release, and not proof of receipt merely because it was intended. RELEASED remains the event of entry into the destination.

Layer: Neither, provisionally.

Recommendation: Retain Neither. Dictionary 0.4 already defines the operative event RELEASED and anchors it to the destination's own record. Matrix 03 and Skeleton Draft 02 introduce no independent destination field or message construct. Promoting DESTINATION to a Dictionary term or schema field now would add a separate operative concept without a corresponding requirement in the current specification. Its use as a referent in the meaning of RELEASED is sufficient.

9. SEARCH SCOPE

SEARCH_SCOPE — The explicitly bounded corpus or collection within which an absence or classification search is performed, identified by a reference and an immutable version pin.

FORM: For absence and classification results, search_scope is required and has abstract shape {corpus_ref, pinned hash}. The reference and pin identify the corpus version. The target must be unambiguous within that scope, and the resulting claim may not exceed it.

For UNTRACEABLE, the relevant scope is the exactly pinned index plus manifest. The classification must not be stated globally.

MEANING: A correctly identified and pinned scope does not establish that the search was adequate or that the target is absent. Those conclusions depend on the applicable method and evidence.

Boundary: SEARCH_SCOPE is not the target being sought, not the METHOD used to search, and not a finding of ABSENT. A bounded scope limits the claim; it does not establish the adequacy of the search.

Layer: Schema.

Reconciliation status

Nine definitions retained.

Original nearest-neighbour fences retained and clarified where Skeleton Draft 02 exposed a distinction.

Original layer assignments retained.

FORM and MEANING kept separate in the Dictionary 0.4 style.

Schema fields are not conflated with the concepts they identify.

No new message types, fields, enforcement mechanisms or owner decisions introduced.

Dictionary 0.5 remains the owner's draft; none of these proposed Dictionary terms is represented as admitted.

DESTINATION recommendation is recorded for owner consideration only.

Status: Draft 01 — reconciled against Dictionary 0.5 Supplement 01 and Syntax Skeleton Draft 02. Nothing admitted, frozen or implemented.

Outstanding boundaries

The reconciliation does not resolve any of the owner's seven open items. In particular, it does not add these six proposed Dictionary words to the 0.5 inventory, nor does it turn the two schema-layer words into new fields. DESTINATION remains a recommendation, not a decision.

I can take a targeted source check if your review identifies a disputed definition; otherwise this set is ready for Remmy's review without another broad pass.

⟦ALEX-FINAL⟧
