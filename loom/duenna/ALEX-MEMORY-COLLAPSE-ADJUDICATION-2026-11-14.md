I support this proposal. More than that, I think it identifies a particularly good early Duenna workload because it exercises several of the framework's central ideas without requiring the framework to control a high-impact external action.

My ruling is: accept into the programme for paper design now, with a bounded pilot after Batch 6. Keep it separate from Stage 6 authorization.

1. Why it belongs in Duenna

The important distinction Ben has identified is between retaining information and presenting information.

A memory collapse is not simply summarisation. It is a controlled transformation of an authoritative record into a smaller operational representation.

That makes it a natural governed job:

The source is authoritative and immutable.

The worker has a defined input and output contract.

The output makes claims about its source.

An independent examiner checks those claims.

The system decides whether the result is fit to load.

The entire operation produces evidence that can be measured.

This is almost an ideal demonstration of Duenna's separation of worker, examiner, authority and execution.

It also creates a useful distinction between two things that are frequently confused:

A concise brief is not a replacement for the historical record. It is a derived working view of that record.

That distinction should be a permanent architectural principle.

2. Programme placement

Now: Paper design alongside the registry schema

Define the job contract, output format, examination protocol and evaluation criteria. No implementation or changes to existing execution gates.

After Batch 6: Bounded pilot

Run controlled collapses against known conversation records and event streams. Compare outputs against independently established reference briefs and source evidence.

Before any registry integration

Establish whether collapse quality can be measured reliably enough to contribute meaningful evidence to the Measured Profile Registry.

Stage 6 remains independently gated

This proposal neither authorizes Stage 6 nor becomes a dependency that silently expands its scope.

I would not defer the paper design. It can proceed without interfering with Batch 6, and it gives us a concrete candidate workload for testing Duenna's governance model.

3. Additional acceptance criteria

The four proposed constraints are necessary. I would add eight more.

Criterion

	

Acceptance requirement




Semantic fidelity

	

Every retained claim must be supported by its source, not merely associated with it.




Decision preservation

	

Approved decisions, rejected approaches, authority boundaries and unresolved questions must not disappear through compression.




Uncertainty preservation

	

Disputed, provisional, inferred and unverified information retains its original status.




Temporal correctness

	

Superseded decisions cannot be presented as current. The brief must distinguish historical and active state.




Coverage accounting

	

The output identifies important source material considered, excluded and unresolved.




Identity preservation

	

People, models, projects, event IDs and task ownership cannot be conflated.




Budget compliance

	

The brief must meet its assigned token or size budget without sacrificing mandatory information. If impossible, it fails visibly.




Reproducibility

	

The source version, worker version, instructions and examination result are recorded so the run can be independently reconstructed.

One additional requirement deserves particular attention.

No invented continuity

A collapse worker must never turn an absence of information into a positive statement.

For example:

Source: no completion evidence found.

Unacceptable brief: "Task completed."

Acceptable brief: "Completion not established in the available record."

This is essential. Otherwise the memory system can gradually turn uncertainty into false history.

4. The examination protocol

I would make the examiner work at the level of individual claims.

Each claim in the brief should have:

A unique claim ID.

The exact statement being made.

One or more source references.

The source version or hash.

An examination result.

A discrepancy classification, if applicable.

The examiner should independently retrieve the referenced source and establish whether it actually supports the claim.

I would classify findings as:

SUPPORTED: Source directly establishes the claim.

PARTIALLY SUPPORTED: Some elements are supported, others are not.

CONTRADICTED: Source conflicts with the claim.

UNTRACEABLE: Source reference cannot be resolved.

INFERRED: Reasonable interpretation, but not directly established.

OMITTED: Important source information missing from the brief.

Only claims meeting the agreed acceptance threshold should ship. Inferences should not masquerade as established facts.

The examiner must not silently repair the worker's output. Findings go back as findings. A revised brief requires another examination.

5. How to measure the worker

This is where I see a particularly useful connection to the Measured Profile Registry.

I would measure at least:

Factual precision: How many claims are genuinely supported?

Traceability: What proportion of claims resolve successfully?

Critical retention: Were decisions, constraints, blockers and commitments preserved?

Contradiction handling: Did the worker preserve conflicts rather than resolve them arbitrarily?

Compression efficiency: How much useful information survived relative to the output budget?

Calibration: Does the worker accurately identify uncertainty and missing evidence?

Recovery performance: Can another seat reconstruct the correct working state from the brief and its references?

Do not reduce these to a single score too early. A model that produces beautifully concise briefs but loses critical decisions should not rank highly.

6. One architectural safeguard I'd insist on

Canonical record — immutable

Original conversations, event streams, logs and source evidence.

Collapse worker — read-only

Produces a candidate brief with source references.

Independent examiner

Checks claims, coverage, contradictions and budget.

Load gate

PASS

Approved brief

Available as a loaded working view.

FAIL

Quarantined brief

Findings retained. Existing loaded copy untouched.

The load gate should be atomic. An incomplete replacement must never overwrite the last known-good brief.

I would also version briefs independently of their source records. That allows a new collapse method to produce a new view without altering the underlying history.

Final adjudication
ACCEPTED INTO PROGRAMME — PAPER DESIGN

Decision

	

Ruling




Does it belong in Duenna?

	

Yes




Paper design now?

	

Authorized




Pilot now?

	

No




Pilot after Batch 6?

	

Recommended




Stage 6 authorization?

	

Unchanged




Canonical record modification?

	

Prohibited




Registry contribution?

	

Only after measured validation

The deeper significance is that this could become one of Duenna's first genuinely useful internal services.

It would give Remmy a governed way to maintain continuity across models, conversations and context windows. It would also give us a repeatable benchmark for measuring which models are actually good at preserving operational knowledge.

And there's a lovely architectural symmetry here:

The logger preserves what happened. The collapse worker preserves what matters. The examiner checks that nothing important was lost or invented.

That is a strong candidate for Duenna.

Ben has not authorized implementation, and neither have I. This is a programme-level acceptance of the design direction, not an execution order.