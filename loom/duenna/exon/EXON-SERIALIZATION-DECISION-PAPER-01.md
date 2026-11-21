# EXON — CANONICAL SERIALIZATION AND HASHING — DECISION PAPER 01 (standalone filing)

Filed: 2026-11-16 (Remmy), extracted verbatim from Alex's reply to Development Letter 11 (filed in full as EXON-DEVELOPMENT-LETTER-11.md). Status as written by its author: DRAFT FOR OWNER REVIEW. The recommendation (JSON + RFC 8785 JCS + SHA-256 with explicit algorithm identifier) is Alex's; the five ruling questions in section 8 are the owner's. Nothing admitted or frozen.

---

EXON — CANONICAL SERIALIZATION AND HASHING
Decision Paper 01

Status: DRAFT FOR OWNER REVIEW
Purpose: Compare candidate representations and hashing approaches. Recommend a direction without selecting or freezing it.
Scope: Message serialization and record hashing only. This paper does not define the message envelope, message bodies, reference coordinate, locator policy, or final digest policy.

1. Decision to be made

EXON needs a representation that allows different implementations to:

Read the same structured message as the same data.

Produce identical bytes when calculating a record digest.

Preserve the distinction between absent fields, explicit null, strings, numbers, booleans, objects and ordered arrays.

Support exact record identity and predecessor-hash links.

Remain practical to inspect, exchange, store and validate.

The serialization format and the hash algorithm are separate decisions. A deterministic representation does not itself select a cryptographic hash function.

2. Existing constraints and precedent

The retrieved EXON material establishes several relevant constraints:

The common envelope includes protocol_version, message_id, message_type, sender_id, recipient_id, and optional relations including in_reply_to, supersedes and previous_record_hash.

timestamp is informational. It does not establish ordering, authority or supersession.

previous_record_hash identifies the predecessor in a sender's chain. It does not establish cross-chain order.

The established artefact reference is {kind, id, hash}.

Hash matching is required where the referenced target is immutable.

The Shelf admission manifest currently records SHA-256 file digests. Its JSON treatment preserves the raw file text: no field is flattened, normalised or discarded. This is an existing file-admission convention, not a canonical EXON message-serialization specification.

The matrix explicitly records that canonical serialized EXON examples were not retrieved. No existing message encoding should be treated as established precedent.

Important distinction: a raw file digest identifies exact file bytes. A canonical message digest would identify a structured message according to an agreed canonical representation. They are related, but not interchangeable.

3. Candidate representations
A. Ordinary JSON

Description: Store and transmit messages as ordinary UTF-8 JSON.

Advantages

Widely understood and supported.

Human-readable.

Directly represents the EXON field structures already described.

Straightforward integration with common programming languages and tooling.

Costs

JSON permits insignificant whitespace and does not make object member ordering semantically significant.

Different serializers can produce different bytes for equivalent data.

Duplicate object member names can be handled inconsistently by implementations.

Raw-byte hashing therefore makes harmless formatting or ordering changes produce a different digest.

Assessment: Good data representation, but insufficient by itself as a reproducible hashing format.

B. JSON with RFC 8785 JSON Canonicalization Scheme (JCS)

Description: Use JSON as the data model and RFC 8785 to produce deterministic canonical JSON bytes.

JCS specifies deterministic property sorting and serialization rules. Its output is intended to provide a repeatable representation suitable for cryptographic hashing and signing.

Advantages

Retains JSON's readability and broad tooling support.

Avoids dependence on whitespace and object member ordering.

Uses an existing published specification rather than a new EXON-specific canonicalizer.

Allows different implementations to calculate the same digest from the same structured message.

Costs and constraints

Duplicate property names must be rejected.

Values must conform to the I-JSON constraints used by JCS.

Numbers must be representable as IEEE 754 double-precision values. Larger integers or higher-precision values should be represented as strings.

Unicode strings are preserved as supplied; JCS does not normalize Unicode.

Canonical output omits insignificant whitespace, so it is less convenient to inspect directly than pretty-printed JSON.

Implementations must use conforming canonicalization libraries and shared test vectors.

Assessment: Strongest balance of interoperability, implementation cost and deterministic hashing for EXON's apparent requirements.

C. YAML

Description: Use YAML as the message representation.

Advantages

Highly readable.

Supports comments and convenient hand-authored documents.

Can represent nested structures and collections.

Costs

YAML's richer syntax introduces more parsing and interpretation choices.

Comments, aliases, tags and scalar interpretation complicate a tightly controlled message format.

A separate restricted profile and conversion process would be needed to produce reliable canonical bytes.

EXON would still need a canonical representation for hashing.

Assessment: Useful for configuration and human-authored material, but not recommended as the authoritative message format.

D. Deterministic CBOR

Description: Use CBOR with the deterministic encoding requirements in RFC 8949.

Advantages

Compact binary representation.

Published deterministic encoding rules.

Supports explicit data types and byte strings.

Suitable for machine-to-machine exchange and deterministic hashing.

Costs

Not naturally human-readable.

Requires binary inspection and debugging tools.

Requires an agreed CBOR profile, including decisions about tags and permitted data types.

Adds implementation and maintenance costs compared with JSON.

Human-readable presentation would require a separate rendering layer.

Assessment: Technically sound, especially where compact binary transport matters, but unnecessarily costly for the current EXON stage.

E. A custom EXON serialization

Description: Define a new canonical textual or binary representation specifically for EXON.

Advantages

Complete control over syntax and canonical form.

Could be tailored closely to EXON's eventual grammar.

Costs

Requires a new serialization specification in addition to the message grammar.

Requires independent parsers, serializers, canonicalizers and test fixtures.

Creates compatibility and maintenance responsibilities.

Risks making EXON's first implementation dependent on a custom format before its grammar is settled.

Assessment: Premature. It creates additional language and implementation work without a demonstrated requirement.

F. JSON Lines / NDJSON

Description: Store or transport one JSON message per line.

Advantages

Convenient append-oriented record storage.

Easy to inspect and process as a stream.

Simple record framing.

Costs

Does not itself canonicalize each JSON message.

Raw-line hashes remain sensitive to formatting and property ordering.

Requires an additional canonicalization rule if used with cryptographic digests.

Assessment: Potentially useful as a transport or storage framing convention, not as the canonical representation itself.

4. Hashing candidates

The following are hash-function choices independent of the serialization decision.

SHA-256

Produces a 256-bit digest.

Broadly implemented and supported.

Already used for Shelf file digests.

Specified in NIST's Secure Hash Standard.

Assessment: Recommended starting choice for EXON, subject to the owner's digest-policy ruling.

SHA-512/256

Produces a 256-bit digest using the SHA-512 family.

Standardized and supported by the Secure Hash Standard.

Offers a distinct construction from SHA-256.

Assessment: Technically valid, but offers no clear practical advantage for the current EXON requirements.

SHA3-256

Produces a 256-bit digest.

Standardized in the SHA-3 family.

Provides an alternative construction to SHA-2.

Assessment: Valid alternative, but adds no necessary capability for the present scope.

SHA-1 / Git object identifiers

Git object identifiers in the current Shelf include SHA-1-based blob identifiers. These are useful for identifying Git objects within the repository.

They should not be silently treated as EXON content digests. The Shelf already distinguishes Git blob identity from the SHA-256 digest of the file content.

Assessment: Retain Git object identifiers as repository provenance. Do not adopt SHA-1 as the EXON message-digest recommendation.

5. Hashing model — proposed

If the owner accepts canonical JSON, the proposed calculation is:

Construct the complete structured message.

Validate the message against the applicable EXON schema.

Canonicalize the message using the selected canonicalization specification.

Encode the canonical result as UTF-8 bytes.

Calculate the selected digest over those bytes.

Represent the digest with an explicit algorithm identifier.

Illustrative representation:

sha256:<64 lowercase hexadecimal characters>

This is an example of a self-identifying digest label, not an adopted EXON field value.

Record-hash boundary

The digest must not hash itself.

The proposed digest input includes the complete message, including previous_record_hash where present. The digest value calculated for the current record is external metadata or a reference value; it is not inserted into its own digest input.

This avoids circular hashing while allowing each record to commit to its predecessor.

What a digest establishes

A matching digest can establish that the bytes or canonical structured content being checked match the identified digest.

It does not, by itself, establish:

Who authored the record.

Whether the sender had authority.

Whether the record is true or supported.

Whether a referenced source is trustworthy.

Whether two different sender chains have a valid global ordering.

Whether an append was atomic or protected against concurrent writes.

Those remain separate identity, authority, evidence and infrastructure concerns.

6. Recommendation

Recommend JSON as the EXON data representation, with RFC 8785 JCS as the canonical serialization used for message hashing.

Recommend SHA-256 as the initial digest algorithm, with an explicit algorithm identifier in every digest reference.

The reasons are:

JSON already fits the structured field model in the EXON drafts.

JCS supplies a published deterministic serialization rather than requiring a custom canonicalizer.

SHA-256 is already used for Shelf file digests and has broad implementation support.

This approach is easier to inspect, implement and maintain than a binary-first or custom representation.

It avoids adding a new language-specific serialization layer before the EXON grammar is settled.

This is a recommendation only. It does not select the owner's digest policy or close any of the three reference-form decisions.

7. Dependencies and boundaries to preserve

The following must remain explicit when this recommendation is considered:

Matter	Status
JSON as the data representation	Recommendation only
RFC 8785 JCS as canonical serialization	Recommendation only
SHA-256 for message digests	Recommendation only; owner ruling required
Digest identifier and textual encoding	Proposed sha256: prefix; not adopted
Raw file SHA-256 for existing Shelf admission	Existing convention
Git blob identifier	Repository identity; not interchangeable with raw file SHA-256
Index pin mechanism	Owner decision remains open
Source locator policy	Owner decision remains open
Reference digest policy	Owner decision remains open
Timestamp representation	Not decided by this paper
Missing versus explicit null semantics	Must be defined by the schema
Unknown-field handling	Must be defined by the grammar/schema
Message field order	Canonicalizer handles object member order; schema semantics remain separate
Array order	Preserved; never sorted unless the owning schema explicitly defines a set
Canonical test vectors	Not yet established

The recommendation must not silently settle any of the three owner decisions concerning reference form.

8. Proposed owner ruling

The owner is asked to rule on:

Whether JSON is the authoritative EXON data representation.

Whether RFC 8785 JCS should be the canonical serialization.

Whether SHA-256 should be the initial message-digest algorithm.

Whether digest values should carry an explicit algorithm identifier such as sha256:.

Whether canonical bytes are the authoritative stored message representation, with pretty-printed JSON treated only as a human-readable view.

The fifth question matters because JCS output is compact and whitespace-free. A separate readable rendering may be desirable, but it must not be confused with the canonical bytes used for hashing.

No implementation, validator, canonical fixture, admission or freeze is proposed by this paper.

9. Standards and source material

RFC 8259 — The JavaScript Object Notation (JSON) Data Interchange Format

RFC 8785 — JSON Canonicalization Scheme

RFC 8949 — Concise Binary Object Representation (CBOR)

NIST FIPS 180-4 — Secure Hash Standard

EXON Shelf sources inspected

duenna/plaincode/DICTIONARY-04.md — blob 49c2408065110ef5e096781862d4b9a59f449623

duenna/INDEX-ADMISSION-MANIFEST-01.md — blob 7cdb13de5f22c1224f5c38183c926e44d26a065c

duenna/plaincode/EXON-FIELD-MATRIX-02-ALEX-CONSOLIDATED-RECONCILIATION-DRAFT.md — blob d25f4b5ef1794793a65396c33c0acfc359e3e604

duenna/plaincode/EXON-FIELD-MATRIX-02-REMMY-INDEPENDENT-REPAIR.md — blob da5df6d7f559df842c21c87881f5ef03dca87e1c

duenna/plaincode/EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-DRAFT.md — blob 87c23499596902b084a89cb203d093e62236d8e3

Disposition: Item 4 drafted for owner review. Items 1–3 remain held pending Remmy's cleanly identified Matrix 03 and subsequent verification. Nothing admitted or frozen.

Standards basis: JCS is specifically designed to provide invariant JSON bytes for hashing; it imposes constraints on duplicate keys, numbers and Unicode handling. Deterministic CBOR is also standardized, but has a higher human-inspection cost. 
rfc-editor.org
+2
 NIST specifies SHA-256 within its Secure Hash Standard. 
nist.gov

Letter 12 disposition: Item 4 is drafted and returned for your review. No Shelf mutation, admission or freeze has been made.
