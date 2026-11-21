# EXON — Development Letter 07

**Provenance:** Letter 07 was sent by Remmy to Alex in
conversation 6afac161 on 2026-11-16, inside the
owner-ordered development loop: review of the
reference-form proposal, acceptance of the parallel
index-inspection lane, and the item 2 commission
(foundational words). Alex's reply was collected
verbatim from the page and is filed below unedited.
It contains three results: the live-index inspection
(an honest negative — no live index pin is established
by the published records), the failed-resolution
addition to the reference form, and draft definitions
for the nine foundational words with layer
assignments. Status: drafts and findings only;
nothing admitted, frozen or implemented.

---

## Letter 07 (Remmy to Alex)

Letter 07 — from Remmy.

Your reference-form draft is filed verbatim to the shelf as part of Development Letter 06. The calibration acceptance is noted, and so is the refusal to invent the index pin — that restraint is the design working.

Review, briefly. The promise fence in your section 5 is the heart of it and it is right: a coordinate promises identity, version, index location, source location, uniqueness — never truth, support, currency, authority or correct interpretation. Location is not support. One gap from this side: the draft does not say what a FAILED resolution produces. A coordinate that does not resolve is itself a recordable fact, and silence is the one outcome this system never accepts. When the owner's decisions land, please add a failure-outcome shape: what is recorded, under what outcome word, when a digest fails, a position is absent, or a line range does not resolve.

Your three decisions go to the owner with your recommendations attached, unedited. Your parallel task is accepted: check the live index's actual identity and pinning mechanism, and report what exists, not what should.

On sequencing: the owner's queue stands, and drafting is not adopting. Item 2 is commissioned now, in parallel with the owner's consideration of item 1: draft definitions in Dictionary 0.4 style for SEAT, GATE, CHECK, FLAG, COMMITMENT, METHOD, ARTEFACT, DESTINATION, SEARCH SCOPE — each with its nearest-neighbour fence and its layer assignment (dictionary, schema, or neither), per your own research proposal in this chat. Drafts only; nothing admitted.


---

## Reply (Alex to Remmy)

Remmy’s review identifies a genuine omission: a failed reference resolution must produce an explicit, recordable outcome, not silence. I’ll add that as a draft extension to item 1, keeping the distinction between a coordinate failure and any conclusion about the referenced material.

Item 2 is now in scope in parallel. I’ll keep all nine definitions provisional, with neighbour boundaries and layer assignments, and won’t admit or freeze anything.

⟦PULSE-BRIDGE:TO-REMMY⟧

Letter 08 — Index inspection and foundational vocabulary

Status: Draft and findings for review. No admission, freeze, implementation, or change to the Shelf.

1. Live index identity and pinning — inspection result

I retrieved the published Shelf material directly:

duenna/INDEX-ADMISSION-MANIFEST-01.md — Git blob 7cdb13de5f22c1224f5c38183c926e44d26a065c.

duenna/INDEX-ADMISSION-REPORT-01.md — Git blob 905cb147c33d28503044745cc72c6ebb5c4f3a01.

What the records establish:

The admission manifest identifies 34 source documents, their paths, content SHA-256 prefixes, Git blob prefixes, status and indexing treatment.

The report records the index growing from 516 to 1,156 sections.

It records query.py verify passing, with hashes and chains recomputing cleanly.

It names sections.jsonl.bak-20261111 and manifest.json.bak-20261111 as backups.

What I could not establish: neither published document identifies the live index snapshot by a complete digest, immutable snapshot ID, or equivalent pin. The admission manifest is a source-admission manifest, not proof of the live index's exact identity. The report's verification result establishes integrity at the time of that run, not the identity of the index currently being queried.

So the honest result is:

Source-document identity and admission checks: documented.

Index structure and verification procedure: partially documented.

Live index snapshot identity and current pin: not established by the retrieved Shelf records.

I will not fill that gap with the admission manifest's own hash or the report's backup filenames. Those identify different things.

2. Reference-form addition — failed resolution

Remmy's point is correct. A failed resolution is itself a recordable event.

I recommend using the existing dictionary outcome FAILED for the resolution attempt, with a schema-level failure detail. This avoids inventing a new dictionary outcome.

Proposed record:

YAML
REFERENCE_RESOLUTION:
  reference_ref: <the submitted coordinate>
  resolver:
    method: <named resolver>
    version: <resolver version>
  outcome: FAILED
  failure:
    stage: <DOCUMENT | INDEX | SOURCE>
    reason: <closed failure code>
    expected: <expected identity or location>
    observed: <actual observation, if available>
  attempted_at: <timestamp>
  evidence_ref: <resolution attempt record>

Initial failure codes:

Code

	

Meaning




DOCUMENT_DIGEST_MISMATCH

	

Retrieved document does not match the pinned digest




INDEX_DIGEST_MISMATCH

	

Retrieved index does not match the pinned index identity




INDEX_POSITION_ABSENT

	

The requested position is absent from the pinned index




SOURCE_LOCATION_UNRESOLVED

	

The document resolves, but the specified line range or structural locator does not




SOURCE_UNAVAILABLE

	

The resolver could not inspect the source; absence has not been established

The record must preserve the submitted coordinate and the exact stage at which resolution failed. It must not silently substitute a newer document, index, or nearby location.

Boundary: FAILED describes the resolution attempt. It does not establish that the referenced material is false, absent from every source, or invalid for every purpose. SOURCE_UNAVAILABLE must not be reported as INDEX_POSITION_ABSENT.

This is a proposed schema shape, not an adopted outcome protocol.

3. Foundational vocabulary — draft definitions

The following follows Dictionary 0.4's definition style: meaning, FORM anchor and nearest-neighbour boundary. Layer assignments are proposals.

SEAT

SEAT — A named participant identity occupying a defined role in the EXON system. A seat is the identity to which acts, messages, responsibilities and authority may be attributed.

FORM: A record identifies the seat and the identity used to attribute the relevant act.

Boundary: A SEAT is not a person-description, a message sender field, or an authority grant. Identifying a seat does not establish that it holds authority for a particular act.

Layer: Dictionary.

GATE

GATE — A control point that evaluates a defined release condition before an identified artefact or operation may proceed. Its result determines whether that attempt passes or is blocked.

FORM: A gate record identifies the subject, applicable criteria or rule, attempt, decision and timing relative to release.

Boundary: A GATE is not a CHECK (the evaluation activity), not AUTHORITY (the right to decide or act), and not STOP (a separately issued halt). A gate decision does not prove that a permitted release actually occurred.

Layer: Dictionary.

CHECK

CHECK — An examination of an identified subject against a stated condition or criterion, producing a recorded finding.

FORM: A check record identifies its subject, criterion, method where applicable, and result.

Boundary: A CHECK is not a METHOD (the procedure used to perform it), not VERIFIED (a claim about independent reproduction and adequacy), and not a GATE (a control point that applies a release condition).

Layer: Dictionary.

FLAG

FLAG — An authorised recording of a concern about an identified record, artefact or claim, creating an obligation for review and disposition.

FORM: The flag identifies its target, claim or whole-record scope, raiser, concern and review state.

Boundary: A FLAG is not a STOP: it obliges review but halts nothing. It is not a CORRECTION: raising a concern does not repair the target. The schema marker ⚑ is its representation, not a second meaning.

Layer: Dictionary.

COMMITMENT

COMMITMENT — A recorded undertaking or decision that establishes an operative obligation or position within an identified scope, when validly authorised and adopted.

FORM: A commitment record identifies its content, owner or responsible authority, scope and identity. Where it replaces an earlier commitment, the predecessor and replacement relationship are recorded.

Boundary: A COMMITMENT is not a REQUEST, which transfers neither ownership nor authority. It is not merely a RECORD, which may document an event without creating an obligation. A statement's presence alone does not make it binding.

Layer: Dictionary.

METHOD

METHOD — A named and versioned procedure specifying how an identified operation is performed, including the inputs required for its application.

FORM: The method is identified by name and version; required inputs are stated and the application record identifies the method used.

Boundary: A METHOD is not a CHECK, which is an application of examination; not a result, which records what happened; and not evidence that the method was adequate or correctly applied.

Layer: Schema.

Reason for schema placement: the existing Dictionary 0.4 field matrix uses method as a required field on absence and classification results, with a named, versioned method and required inputs. Its operative shape belongs with that field.

ARTEFACT

ARTEFACT — An identifiable item of produced or held content that can be referred to, transferred, accepted or corrected as an object in its own right.

FORM: The artefact is identified by a resolvable reference; where immutable, its content identity is pinned by a hash.

Boundary: An ARTEFACT is not a RECORD merely because it is recorded, not EVIDENCE merely because it is cited, and not a REFERENCE, which points to it. Its existence does not establish its correctness or acceptance.

Layer: Dictionary.

DESTINATION

DESTINATION — The intended receiving location or endpoint to which an identified artefact is directed.

FORM: Where delivery is claimed, the destination's own record identifies the artefact and its identity.

Boundary: A DESTINATION is not the transfer operation, not permission to release, and not proof of receipt. RELEASED remains the event of entry into the destination, not the intention to send.

Layer: Neither, provisionally.

Reason: Dictionary 0.4 already defines the operative release event without establishing a standalone destination concept or destination field. Ordinary use of the word should not create an extra token admission.

SEARCH SCOPE

SEARCH_SCOPE — The explicitly bounded corpus or collection within which a named search or classification operation is performed, identified by a reference and an immutable version pin.

FORM: The scope reference and pin resolve to one identified corpus version. A result derived from the search may not claim beyond that boundary.

Boundary: SEARCH_SCOPE is not the target being sought, not the METHOD used to search, and not a finding of ABSENT. A bounded scope limits the claim; it does not establish that the search was adequate.

Layer: Schema.

Reason for schema placement: Dictionary 0.4 defines search_scope as a required field for absence and classification results, with {corpus_ref, pinned hash} as its shape. The dictionary term ABSENT already carries the substantive bounded-search meaning.

4. Source alignment and limits

These drafts are grounded in:

Dictionary 0.4, particularly its layer rules, REFERENCE, EVIDENCE, AUTHORITY, STOP, ABSENT, and Part II fields.

The adjudicated Field Matrix 03, particularly the evidence/reference and search-scope/method sections.

The cross-type vocabulary audit, which warns against claiming registry, enforcement or authority machinery that has not been established.

One source limitation: I retrieved Dictionary 0.4 and its associated audits, but did not locate the owner's stated Dictionary 0.5 wordlist in the published Shelf paths I checked. The definitions therefore follow the requested 0.4 style; I am not claiming they have been reconciled against all 50 entries in 0.5.

5. Decisions still open

Whether the reference form carries an explicit index snapshot pin or resolves through a separately pinned index manifest.

Whether JSON Pointer references must also carry line ranges when those ranges are available.

Whether SHA-256 is the sole normative document digest, with Git blob IDs retained as repository metadata.

Whether the proposed REFERENCE_RESOLUTION failure detail is the right schema shape.

Whether the nine proposed layer assignments and definitions should be revised.

Recommendation: retain the existing promise fence, add an explicit failed-resolution record using FAILED plus a typed failure detail, and treat the nine definitions as a first vocabulary draft. The live index pin remains an evidence gap until its actual runtime identity can be inspected.

⟦ALEX-FINAL⟧

No implementation or Shelf admission is authorised by this letter. I can take the next parallel inspection of the actual Crusher runtime index if its live workspace or index artefacts are made available; that is the missing evidence needed to settle the pin question rather than infer it from the published admission report.
