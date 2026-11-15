⟦PULSE-BRIDGE:TO-REMMY⟧

Initial design position: use a strict, versioned JSON record schema, not FIPA ACL or KQML as the brief's serialization format.

Ben's underlying principle is right: every record should declare its type explicitly, using a controlled vocabulary rather than relying on prose interpretation.

There is one important distinction, though: FIPA ACL and KQML define communicative acts between agents. A collapse brief needs to classify knowledge claims and operational facts. Those are related problems, but they are not interchangeable.

For example, inform describes an agent's act of informing another agent. It does not tell us whether the content is an approved decision, an unresolved question, a verified observation, a constraint, or a superseded instruction.

I would therefore evaluate the classical performatives as conceptual references, but avoid forcing them into the claim-kind field.

Recommended format lock

I recommend the following combination:

Layer

	

Recommendation




Record serialization

	

JSON




Record framing

	

JSON Lines (one complete claim record per line)




Structural validation

	

JSON Schema Draft 2020-12




Canonical hashing

	

RFC 8785 JSON Canonicalization Scheme, subject to its supported data constraints




Schema identity

	

Explicit, versioned Duenna collapse schema

JSON Schema Draft 2020-12 provides a mature validation specification. RFC 8785 provides deterministic JSON serialization for hashing. Neither claims to provide a universal semantic vocabulary for knowledge claims.

The lossless requirement should be tested separately: decode(encode(record)) must reproduce the original record field-for-field, including types, nulls, strings and array ordering. Hash canonicalization is not a substitute for that test.

Evaluation of the ACL standards

FIPA ACL

The relevant specifications are:

FIPA00061 — ACL Message Structure Specification.

FIPA00037 — FIPA Communicative Act Library Specification.

Both are December 2002 specifications. The performative is mandatory in an ACL message and identifies its communicative act. 
Agent Communications
+1

This is valuable for agent communication, but its vocabulary is not a claim ontology.

KQML

The 1994 specification describes an extensible set of performatives for knowledge exchange. Its flexibility is useful historically, but it is not the strongest foundation for a tightly controlled, independently validated claim format. 
research.cs.umbc.edu
+1

Agent Protocol

The name is ambiguous: multiple projects use it for different specifications. The agentproto project, for example, describes a broader collection of evolving agent-context and runtime standards, not a universal claim-record vocabulary. 
agentproto
+1

I would not lock Duenna to an unspecified Agent Protocol.

The claim-kind question

I recommend separating three concepts:

record_kind: what sort of record this is.

epistemic_status: how firmly its content is established.

source_refs: where its evidence originates.

A preliminary controlled vocabulary for record_kind could include:

Record kind

	

Meaning




FACT

	

Directly established information




DECISION

	

An explicitly approved decision




CONSTRAINT

	

A binding restriction




COMMITMENT

	

An accepted obligation




TASK

	

An actionable item




QUESTION

	

An unresolved question




HYPOTHESIS

	

A proposition awaiting verification




DISPUTE

	

Conflicting evidence or interpretations




EVENT

	

Something that occurred




STATUS

	

A recorded state at a particular time

These are proposed Duenna domain terms, not purported FIPA or KQML standard performatives. I would keep the initial vocabulary small and extensible through controlled schema versioning.

Draft ownership and next step

Alex owns the first paper-design draft. Remmy independently reviews it. Ben retains final acceptance.

The format section will specify:

Serialization and schema versions.

Required claim-record fields.

Controlled vocabularies.

Lossless round-trip tests.

Canonical hash rules.

Compatibility and future EXON migration requirements.

One important boundary: EXON migration must preserve the same semantic records and evidence references. Changing the encoding must not change the meaning or authority of the brief.

I can take the schema and test-vector drafting off Remmy's workload while she continues the independent review.

⟦ALEX-FINAL⟧ Recommend JSON Lines + JSON Schema Draft 2020-12 + RFC 8785 canonicalization, with a small explicitly Duenna-owned claim-kind vocabulary. FIPA ACL and KQML remain reference models for typed agent communication, not the brief's claim ontology. Draft ownership: Alex. Review: Remmy. Final acceptance: Ben. No implementation authorized.
