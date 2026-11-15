Duenna Memory Collapse Job
Paper Design Draft 0.3

Status: Draft for final design acceptance
Design owner: Alex
Draft 0.2 prepared by: Remmy (from Alex's Draft 0.1, incorporating the nine accepted review findings and closing the seven open decisions of Draft 0.1 §13)
Draft 0.3 prepared by: Remmy (resolving the four material clarifications and one wording correction from the design owner's review of Draft 0.2)
Independent review of Draft 0.1: Remmy — SOUND WITH FINDINGS; all nine findings and all seven §13 positions accepted by the design owner
Review of Draft 0.2: Alex — SOUND WITH FINDINGS (four material clarifications, one wording correction)
Final design authority: Ben
Implementation status: Not authorized

1. Purpose

The Memory Collapse Job transforms a defined, immutable source record into a compact, structured working brief suitable for loading into an AI seat or operational context.

The job must reduce loaded context without destroying, modifying or replacing the source record.

The canonical source remains authoritative. A collapsed brief is a derived representation whose claims must be individually traceable to that source.

The job is intended to support:

Seat conversation history.

Session and day logs.

Project histories and decision records.

Event streams and other structured operational records.

Context rollover and recovery.

The job does not independently authorize actions, change project decisions, or determine whether an underlying claim is true beyond the evidence available in its source.

2. Governing principles

Source immutability: The worker has read-only access to canonical inputs.

Claim traceability: Every shipped claim resolves directly to one or more source locations.

Independent examination: A separate examiner checks the candidate brief against the source.

Lossless serialization: Encoding and decoding must reproduce every record field and value.

Visible failure: Incomplete, ambiguous or unverifiable work cannot silently become a loaded brief.

No invented continuity: Missing evidence remains missing; uncertainty is preserved.

Separation of meaning and encoding: The record's meaning must survive changes in serialization format, including a future EXON migration.

Atomic loading: A failed candidate cannot replace the last known-good loaded brief.

3. Job contract
3.1 Input contract

Each job receives a defined input package:

job_id: unique identifier.

source_id: stable identifier for the canonical source.

source_version: immutable version, commit or snapshot identifier.

source_hash: integrity hash of the exact source snapshot.

source_type: event stream, conversation, day log, or other declared type.

source_location: resolvable location of the source.

target_context: intended destination or seat.

output_budget: maximum permitted serialized brief size, measured in bytes of the serialized brief (see §5.3 for the byte definition). Token budgets are a derived, per-target view computed at load time; they are never the contract unit.

collapse_profile: versioned instructions defining the intended brief's purpose.

schema_version: required output schema version.

The input package must identify the exact source version being processed. A moving or mutable source reference without a fixed version is not sufficient.

Source-version identity is defined per source type:

Document or file: the repository commit or snapshot identifier, plus the SHA-256 hash of the exact snapshot bytes.

Event stream: the stream identifier, plus the identifier and hash of the head event at capture, plus the capture timestamp.

Conversation: the conversation identifier, plus the SHA-256 hash of the captured snapshot, plus the capture timestamp.

Day log or session record: the file identifier, plus the SHA-256 hash of the exact snapshot bytes, plus the capture timestamp.

A source whose version cannot be expressed in its type's format is not a valid job input.

3.2 Output contract

The worker produces:

A candidate brief.

A claim-level source reference for every claim.

A manifest describing the source, worker and schema versions.

A coverage report identifying material retained, excluded and unresolved.

A run result: SUCCESS, DEGRADED or FAILED.

The worker cannot mark its own output approved for loading.

3.3 Worker permissions

The worker may:

Read the designated source.

Retrieve material within the declared source boundary.

Produce claim records.

Produce a candidate manifest and coverage report.

Report uncertainty and omissions.

The worker may not:

Edit, truncate, delete or rewrite canonical source material.

Modify source indexes or event streams.

Change approved project decisions.

Mark its own candidate as examined or approved.

Replace an existing loaded brief.

Expand its input boundary without a new authorized job.

4. Output format
4.1 Locked serialization basis

Framing: JSON Lines, one JSON object per line.

Structural validation: JSON Schema Draft 2020-12.

Canonicalization: RFC 8785 JSON Canonicalization Scheme.

Claim vocabulary: Duenna-owned, explicitly versioned vocabulary.

FIPA ACL and KQML remain reference models for explicit communicative-act typing. Their performatives are not substituted for Duenna claim kinds.

EXON remains a future serialization target. This design must not depend on unfinished EXON behaviour.

4.2 JSON Lines structure

The brief consists of:

One header record.

One record per claim.

One coverage record.

One completion manifest.

Each line must independently parse as one JSON object. No Markdown, explanatory prose or code fences are permitted inside the serialized artifact.

The human-readable presentation is a derived view, not the canonical brief representation.

4.3 Header record

Required fields:

record_type: BRIEF_HEADER

schema_version

brief_id

job_id

source_id

source_version

source_hash

source_type

target_context

collapse_profile

worker_identity

created_at

output_budget

claim_count

4.4 Claim record

Required fields:

record_type: CLAIM

claim_id: deterministically derived (see below); unique within the brief and stable across regenerations of the same source snapshot.

record_kind: controlled Duenna claim-kind value.

epistemic_status: controlled status value.

statement: exact claim text.

source_refs: one or more direct source references.

temporal_status: current, historical, superseded or unknown.

Optional fields:

owner

related_claim_ids

valid_from

valid_until

notes

Conditionally required field:

successor_ref: required exactly when temporal_status is superseded (see the supersession rule below); otherwise absent.

Claim identity rule: a claim_id is derived from an identity tuple: the source_id, the claim's primary source reference, its record_kind, and a proposition discriminator.

The primary source reference is the first entry of the claim's source_refs array. The worker must place first the reference identifying the source location from which the proposition is drawn; any further references are supporting. (A claim whose first reference is not its proposition's location is malformed.)

The proposition discriminator is the ordinal of the proposition within its primary source location — the order in which propositions appear in the source at that location — never the order in which the worker emits claims. Reordering the worker's output cannot change any claim's identity.

The derivation is exact: claim_id is the lowercase hexadecimal SHA-256 of the RFC 8785 canonical serialization of the tuple object {"v": 1, "source_id": …, "primary_ref": …, "kind": …, "disc": …}, where primary_ref is the canonical serialization of the primary reference object (§4.7) and disc is the discriminator as an integer.

The derivation must not depend on the claim's wording: wording may legitimately improve between collapses of the same source, and the claim must keep its identity when it does. Two distinct propositions arising from the same source reference and record_kind receive distinct discriminators and therefore distinct IDs; they are never merged by the identity rule. Given an identical source snapshot, re-collapse reproduces the same claim IDs.

Supersession rule: when temporal_status is superseded, the field successor_ref is required. Its permitted forms are exactly two: (a) the claim_id of the superseding claim, when that claim appears in this brief; or (b) a source reference in the formal shape of §4.7, when the successor lies outside the brief's scope. A superseded claim whose successor_ref is absent, or matches neither form, fails validation (test B12). successor_ref is not permitted on a claim whose temporal_status is not superseded.

A claim must not combine unrelated assertions merely to save space. Where a sentence contains independently verifiable propositions, they should be separate claims.

4.5 Initial claim-kind vocabulary
Value	Meaning
FACT	Information directly established by the source
DECISION	An explicitly approved decision
CONSTRAINT	A binding restriction
COMMITMENT	An accepted obligation
TASK	An actionable item
QUESTION	An unresolved question
HYPOTHESIS	A proposition awaiting verification
DISPUTE	Conflicting evidence or interpretations
EVENT	A recorded occurrence
STATUS	A recorded state at a particular time

Unknown values are rejected unless introduced through an approved schema version.

4.6 Epistemic status vocabulary
Value	Meaning
ESTABLISHED	Directly supported by the cited source
REPORTED	The source records that someone made the statement
INFERRED	Interpretation derived from source material
PROVISIONAL	Not yet settled or approved
DISPUTED	Conflicting evidence exists
UNVERIFIED	The available source does not establish the claim

REPORTED must not be promoted to ESTABLISHED merely because it appears in an authoritative-looking conversation or document.

4.7 Source references

Each source reference must resolve directly, without requiring a search for the relevant passage.

A source reference is a structured object with four components:

ref_type: one of event, file, document, conversation, or another type introduced through an approved schema version.

source_id: the identifier of the canonical source.

source_version: the version identity of the source, in the per-type format of §3.1, against which the reference was resolved.

locator: a type-specific object identifying the exact location:

event: {event_id}.

file: {file_id, line_start, line_end}.

document: {document_id, page} or {document_id, paragraph}.

conversation: {conversation_id, message_id}.

Structural validity and resolvability are distinct conditions. A reference may be structurally valid (it conforms to this shape) yet unresolvable (the identified location does not exist in the declared source version). Schema validation establishes the first; only examination establishes the second. A source reference that cannot be resolved is an examination failure for the associated claim.

4.8 Coverage record

Required fields:

record_type: COVERAGE

source_scope

material_considered

material_retained

material_excluded

unresolved_material

coverage_limitations

The coverage record must disclose known omissions and retrieval limitations. It must not imply exhaustive coverage if the worker did not inspect the complete declared source.

4.9 Completion manifest

Required fields:

record_type: BRIEF_MANIFEST

brief_id

job_id

source_hash

schema_version

serialization_profile

worker_identity

worker_version

examiner_status

claim_count

serialized_size

hashing_profile

output_hash

job_outcome

The manifest is finalized by the supervisor after examination. The worker cannot assert a successful examination.

5. Serialization and integrity requirements
5.1 Lossless round-trip

For every header, claim, coverage and manifest record:

decode(encode(record)) must produce a field-identical record.

Field identity includes:

Identical field names.

Identical field values.

Identical value types.

Identical null values.

Identical array ordering.

Identical string content.

The test is performed on every brief, not merely on a sample of records.

Numeric discipline: the only numeric fields in any record are claim_count and serialized_size, each constrained by the schema to a safe-range integer. Every other value — including timestamps, hashes, versions and quantities appearing in claim content — is a string. Claim content always lives in the statement string, never in a numeric field.

String validity: a string containing a lone surrogate is invalid and fails validation. Lone surrogates in captured text are a capture-corruption signal; visible failure is preferred to silent portability loss. The characters U+2028 and U+2029 are permitted and are explicit round-trip test vectors (A8).

5.2 Canonicalization

RFC 8785 canonicalization is used for deterministic hashing of valid JSON data.

The schema must constrain data to values compatible with the canonicalization profile. Duplicate object keys are prohibited. Because most parsers collapse duplicate keys before a schema can see them, this prohibition is enforced at ingestion: the parser must reject any object containing a duplicate key, before schema validation (test A11). Numeric values must remain within the supported interoperable representation.

Canonicalization does not imply preservation of original JSON whitespace, key ordering or numeric lexical spelling. The lossless test concerns the defined record data model, not byte-for-byte reproduction of the original serialized input.

5.3 Hashing

Hashing Profile 1 (the locked profile for this design): the output hash is SHA-256 over the RFC 8785 canonical serializations of the header, claim and coverage records, taken in file order, each framed with a trailing newline. The completion manifest is excluded from its own output hash. The source hash is SHA-256 over the exact bytes of the declared source snapshot.

Byte representation: the serialized brief is the UTF-8 encoding of the records' canonical serializations, in file order (header, claims, coverage, manifest), each followed by exactly one newline character (U+000A), including the final record. No other whitespace or framing is present. serialized_size is the total byte length of the serialized brief under this definition, including the manifest record and the final newline. The output_budget (§3.1) is measured against serialized_size as so defined, which makes the byte budget independently reproducible.

The manifest must state the hashing profile and version (hashing_profile).

The source hash is independently checked against the declared immutable source snapshot before processing.

5.4 No silent transformation

The serialization layer must not:

Normalize claim text.

Remove whitespace inside strings.

Reorder arrays.

Coerce strings into numbers or booleans.

Drop null fields.

Replace unknown values with defaults.

Any schema migration or transformation must be explicit, versioned and independently testable.

6. Examination protocol

The examiner is separate from the collapse worker and receives:

The exact immutable source snapshot.

The candidate brief.

The schema and vocabulary versions.

The worker's coverage report.

The serialization test results.

The examiner independently checks each claim against its cited source.

6.1 Claim findings
Finding	Meaning
SUPPORTED	Source directly supports the claim
PARTIALLY_SUPPORTED	Only part of the claim is supported
CONTRADICTED	Source conflicts with the claim
UNTRACEABLE	Source reference cannot be resolved
INFERRED	Interpretation rather than direct evidence
OMITTED	Important source material is absent from the brief

The examiner must not silently rewrite or repair the candidate. Findings are returned as findings. A revised candidate requires a new examination.

6.2 Required examination checks

Source identity and hash match.

All records validate against the declared schema.

Every claim has a valid kind and epistemic status.

Every claim resolves to its cited source.

The source supports the actual wording of the claim.

Decisions, constraints, ownership and commitments are preserved.

Temporal status and supersession are represented correctly.

Disputes and uncertainty remain visible.

Coverage limitations are accurately disclosed.

Output budget is respected.

Lossless round-trip test passes.

Output hash and manifest agree with the candidate.

No canonical source modification occurred.

6.3 Examination outcome

PASS: All mandatory checks pass.

DEGRADED: The candidate is structurally valid but has disclosed limitations that prevent normal loading.

FAIL: A mandatory integrity, traceability, semantic or serialization requirement fails.

Only PASS candidates are eligible for normal loading.

A degraded brief may be retained for investigation but cannot silently substitute for the active approved brief.

7. Failure states
Failure	Required behaviour
Source unavailable	FAILED; no candidate loaded
Source hash mismatch	FAILED; integrity finding
Incomplete source retrieval	DEGRADED or FAILED, according to scope impact as graded by the examiner (the worker discloses retrieval limitations in the coverage record; it does not grade their impact)
Invalid schema	FAILED
Unknown claim kind	FAILED
Untraceable claim	FAILED
Contradicted mandatory claim	FAILED
Missing critical decision or constraint	FAILED
Round-trip mismatch	FAILED
Hash mismatch	FAILED
Budget cannot be met without violating requirements	FAILED
Examiner unavailable	Candidate remains unexamined; no load
Persistence failure	FAILED; existing approved brief remains untouched
Load failure	Existing approved brief remains active

Every failure records:

job_id

failure_code

failure_detail

Last confirmed processing stage

Relevant source and candidate identifiers

Whether a candidate artifact was retained

Whether the existing loaded brief was left unchanged

Failure records are retained independently of the candidate brief.

8. Load gate

The load gate is controlled by the supervisor, not the worker.

Loading requires:

Candidate completeness.

Successful schema validation.

Successful lossless round-trip.

Successful independent examination.

Matching source and output hashes.

A PASS outcome.

Successful persistence of the approved brief.

The supervisor performs an atomic replacement of the loaded working copy only after all conditions pass.

If any condition fails, the previous approved copy remains active.

The canonical source is never replaced or modified by this operation.

9. Acceptance test suite
A. Serialization and schema

A1: Valid header, claim, coverage and manifest records parse.

A2: Invalid JSON is rejected.

A3: Unknown schema versions are rejected.

A4: Unknown claim kinds are rejected.

A5: Required fields cannot be omitted.

A6: Null and missing values remain distinct.

A7: Arrays retain their order.

A8: Unicode, punctuation, newlines and escaped characters survive round-trip, including U+2028 and U+2029 as explicit vectors. A string containing a lone surrogate is rejected.

A9: Field-identical round-trip passes for every record.

A10: Canonical hashes reproduce independently.

A11: A record containing a duplicate object key is rejected at parse, before schema validation.

A12: Manifest exclusion: the output hash of a brief is unchanged when the manifest record is removed from the hashed set, and differs if any header, claim or coverage record is altered.

A13: Ordering sensitivity: exchanging the file order of two claim records changes the output hash.

A14: Framing: altering or omitting a record's trailing newline changes the output hash and fails the Profile 1 byte-representation check.

A15: The source hash is SHA-256 over the exact snapshot bytes: a copy of the snapshot differing only in whitespace produces a different source hash and is rejected as a version mismatch.

B. Traceability and examination

B1: Every claim resolves to its source.

B2: A missing source reference is rejected.

B3: A reference to the wrong source version is rejected.

B4: A claim that overstates its source is detected.

B5: A reported statement is not promoted to established fact.

B6: A disputed decision remains disputed.

B7: A superseded decision cannot appear current.

B8: An omitted critical constraint is detected.

B9: An examiner disagreement produces a finding, not an automatic edit.

B10: A revised candidate requires re-examination.

B11: A worker output that merges two independently verifiable propositions into a single claim is flagged by the examiner.

B12: A superseded claim without a valid successor_ref — neither a claim_id present in the brief nor a well-formed §4.7 source reference — is rejected.

C. Failure and load behaviour

C1: Source unavailability prevents loading.

C2: Hash mismatch prevents loading.

C3: Examiner unavailability prevents loading.

C4: Round-trip failure prevents loading.

C5: Budget failure is visible.

C6: Persistence failure leaves the existing approved brief unchanged.

C7: Failed candidate cannot replace the last known-good brief.

C8: Repeated job identifiers cannot silently overwrite prior results.

D. Immutability and reproducibility

D1: Worker cannot write to canonical source.

D2: Worker cannot modify source indexes.

D3: Source hash remains unchanged after processing.

D4: Identical inputs and versions produce reproducible record semantics.

D5: Manifest identifies worker, schema and source versions.

D6: An independent reviewer can reconstruct the examination from retained artifacts.

E. Compression quality

E1: Output remains within budget when mandatory information permits.

E2: Critical decisions, constraints, owners and commitments survive.

E3: Irrelevant material can be excluded without losing required operational context.

E4: Uncertainty and missing information remain explicit.

E5: A fresh seat can reconstruct the correct operational state from the brief and referenced sources.

E6: Compression does not introduce claims absent from the source.

All mandatory tests must pass for pilot acceptance. Compression-quality tests must use independently prepared reference cases rather than relying solely on the worker's own assessment.

10. Measurement and registry evidence

Each run produces separately measurable evidence:

Claim precision.

Claim traceability rate.

Critical information retention.

Contradiction detection.

Uncertainty calibration.

Compression ratio.

Budget compliance.

Reconstruction accuracy.

Serialization reliability.

Examination agreement.

These measures remain separate initially. No single composite score should conceal a serious failure in traceability, fidelity or critical information retention.

The Measured Profile Registry may consume these results only after the pilot establishes repeatable measurement conditions and independent ground truth.

11. EXON migration

EXON is a future format target, not a dependency of this design.

Migration must preserve:

Claim identifiers.

Claim kinds and epistemic statuses.

Exact claim text.

Source references.

Temporal status.

Relationships between claims.

Examination findings.

Source and output provenance.

A migration must pass semantic equivalence and round-trip tests against the established JSON representation before EXON-generated briefs can be loaded.

The original JSON brief remains preserved as the migration reference.

12. Scope and programme placement

Paper design: Accepted for drafting now.

Pilot: Proposed after Batch 6, subject to Ben's separate authorization.

Stage 6: No change to its existing authorization boundary.

Implementation: Not authorized by this document.

The pilot should begin with a bounded, immutable set of known records and independently prepared expected outputs. It should establish whether the worker can produce compact, faithful, mechanically verifiable briefs before any integration with routine context loading.

13. Settled design decisions (closed in Draft 0.2)

The seven items left open in Draft 0.1 are settled as follows, per the accepted review:

1. Vocabularies CONFIRMED: the ten claim kinds and six epistemic statuses of §4.5–4.6 are the initial locked vocabularies, extendable only through an approved schema version.

2. Source references CONFIRMED (§4.7 forms), extended by the per-type source-version formats of §3.1.

3. Hashing and framing LOCKED as Profile 1 (§5.3): SHA-256, RFC 8785 canonical records in file order, newline framing, manifest excluded from its own output hash; duplicate-rejecting parser at ingestion. The brief is assembled in full and then serialized; it is not streamed (the header's claim_count is knowable only whole).

4. Output budget is measured in BYTES of the serialized brief. Token budgets are a per-target derived view computed at load time, never the contract unit.

5. The minimum critical-information set is defined per collapse profile by claim class: all current DECISION, CONSTRAINT and COMMITMENT records in scope; all DISPUTE records; all QUESTION records touching an open commitment; and the source's most recent STATUS record. A brief missing any of these fails E2 by construction.

6. Examiner independence: a separate execution lane with a fresh context is the minimum requirement. A different model is NOT required for the pilot; whether same-model examination catches planted errors is itself pilot evidence. The examiner receives artifacts (candidate, coverage report, test results), never the worker's reasoning.

7. Retention: approved briefs are retained immutably and versioned, never overwritten — the load pointer moves, the artifacts do not. Rejected and degraded candidates are retained with their examination findings. Failure records are retained independently (§7). The pilot corpus is retained indefinitely.

End of Draft 0.3.

Change log, Draft 0.1 → Draft 0.2 (all changes trace to the accepted review findings):
F1 — Profile 1 hashing defined; manifest excluded from its own output hash (§5.3); hashing_profile added to the manifest (§4.9).
F2 — Duplicate keys enforced by a duplicate-rejecting parser at ingestion; test A11 added (§5.2, §9).
F3 — Numeric fields whitelisted to claim_count and serialized_size, safe-range integers; all other values are strings (§5.1).
F4 — Lone surrogates rejected at validation; U+2028/U+2029 named as A8 test vectors (§5.1, §9).
F5 — Deterministic claim identity: derived from source, primary source reference, record kind and proposition discriminator; never from claim wording (§4.4).
F6 — Superseded claims must name a successor by claim ID or source reference (§4.4).
F7 — Source-version identity defined per source type (§3.1).
F8 — Compound-claim control added as test B11 (§9).
F9 — The examiner grades scope impact; the worker discloses (§7).
§13 closed: the seven open decisions are recorded as settled in §13 of this draft.

Draft 0.2 returns to Ben for final design acceptance. It authorizes no implementation and no pilot.

Change log, Draft 0.2 → Draft 0.3 (all changes trace to the design owner's review of Draft 0.2):
R1 — successor_ref defined as a conditionally required field with exactly two permitted forms; test B12 added (§4.4, §9).
R2 — Claim identity made exact: the primary source reference is the first entry of source_refs; the discriminator is proposition order within the source location, never output order; claim_id derivation defined as SHA-256 over the canonical identity tuple (§4.4).
R3 — Profile 1 given direct acceptance tests (A12–A15) and a precise byte representation; serialized_size defined to include the manifest and the final newline (§5.3, §9).
R4 — Source references given a formal record shape (ref_type, source_id, source_version, locator); structural validity and resolvability explicitly distinguished (§4.7).
R5 — §3.1 budget wording brought into line with the settled decision: bytes are the contract unit; tokens are a derived load-time view (§3.1).

Draft 0.3 returns to Ben for final design acceptance after the design owner's verification of R1–R5. It authorizes no implementation and no pilot.

The draft is ready for Remmy's independent review. I have deliberately left the seven items in Section 13 open rather than silently deciding them.

Review boundary: Please assess the contract, schema feasibility, serialization edge cases and test coverage. No implementation or pilot begins until Ben accepts the completed design and separately authorizes the next stage.