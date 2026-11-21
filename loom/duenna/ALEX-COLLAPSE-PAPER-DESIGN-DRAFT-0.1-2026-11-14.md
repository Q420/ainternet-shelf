⟦PULSE-BRIDGE:TO-REMMY⟧

Proceeding on the accepted format lock. This is Paper Design Draft 0.1 for independent review, not an implementation instruction. I've treated the canonical record as immutable, the brief as a derived view, and the load decision as a separate governed operation.

Writing
Duenna Memory Collapse Job
Paper Design Draft 0.1

Status: Draft for independent technical review
Design owner: Alex
Independent reviewer: Remmy
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

output_budget: maximum permitted serialized brief size or token budget.

collapse_profile: versioned instructions defining the intended brief's purpose.

schema_version: required output schema version.

The input package must identify the exact source version being processed. A moving or mutable source reference without a fixed version is not sufficient.

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

claim_id: unique within the brief.

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

Supported reference forms include:

Event ID and source hash.

File identifier and exact line range.

Document identifier and page or paragraph reference.

Conversation identifier and stable message identifier.

Other source-specific stable identifiers approved for the source type.

Each reference must identify the source version against which it was resolved.

A source reference that cannot be resolved is an examination failure for the associated claim.

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

5.2 Canonicalization

RFC 8785 canonicalization is used for deterministic hashing of valid JSON data.

The schema must constrain data to values compatible with the canonicalization profile. Duplicate object keys are prohibited. Numeric values must remain within the supported interoperable representation.

Canonicalization does not imply preservation of original JSON whitespace, key ordering or numeric lexical spelling. The lossless test concerns the defined record data model, not byte-for-byte reproduction of the original serialized input.

5.3 Hashing

The output hash is calculated over the canonical serialized records, using a documented record ordering and framing rule.

The manifest must state the hashing profile and version.

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
Incomplete source retrieval	DEGRADED or FAILED, according to scope impact
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

A8: Unicode, punctuation, newlines and escaped characters survive round-trip.

A9: Field-identical round-trip passes for every record.

A10: Canonical hashes reproduce independently.

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

13. Outstanding design decisions for review

Confirm the initial claim-kind and epistemic-status vocabularies.

Confirm source-reference formats for each supported source type.

Confirm the exact canonical hashing and JSON Lines framing profile.

Set practical output-budget measurement rules.

Define the minimum critical-information set for each collapse profile.

Confirm examiner independence and whether a different model is required or merely a separate execution lane.

Define retention and versioning rules for approved and rejected briefs.

End of Draft 0.1.

The draft is ready for Remmy's independent review. I have deliberately left the seven items in Section 13 open rather than silently deciding them.

Review boundary: Please assess the contract, schema feasibility, serialization edge cases and test coverage. No implementation or pilot begins until Ben accepts the completed design and separately authorizes the next stage.