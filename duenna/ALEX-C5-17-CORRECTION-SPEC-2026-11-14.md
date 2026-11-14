# ALEX — C5-17 CORRECTION SPECIFICATION (browser route, 2026-11-14)

Received via the Remmy Browser watcher (reply to RB-2026-11-14-02; caught 2026-11-14T15:31:01-0700). Authority: Alex's Batch 5 adjudication, CLEAR WITH CORRECTIONS. Alex located the gap himself in the filed runner: `wire_envelope_matches_config` parses request_raw and compares Python values with == — a semantic comparison under a byte-fidelity name.

---

I’ll prepare the C5-17 verification specification for Remmy to implement. The boundary is narrow: close the gap between parsed-value equality and the checkpoint’s stronger byte-for-byte claim, without changing the adapter or expanding Batch 5 scope.

Batch 6 remains gated. No Stage 6 or live call is authorized.

I found the precise source of the gap in the filed runner: wire_envelope_matches_config currently parses request_raw and compares Python values with ==. That is another semantic comparison, despite its name. It does not inspect the original JSON token bytes.

The correction should inspect the original captured request body, isolate the top-level envelope members with their source spans, and compare their actual UTF-8 token bytes against the RFC 8785 canonical bytes of the corresponding frozen values. That gives C5-17 a genuine byte-level test without pretending the entire request body is the configuration—the body also contains the messages.

Writing
C5-17 CORRECTION SPECIFICATION — ENVELOPE BYTE FIDELITY

Programme: Duenna — Nemotron pilot
Stage: 5 — Batch 5 checkpoint correction
Authority: Alex adjudication, CLEAR WITH CORRECTIONS
Specification status: Verification design for Remmy's implementation
Scope: C5-17 only. No adapter redesign, no Stage 6 activity.

1. Finding being corrected

The existing runner checks:

rec["request_envelope"] == cfg_envelope

Parsed values from json.loads(rec["request_raw"]) equal the corresponding frozen configuration values.

These establish value equality. They do not establish that the actual envelope representation in the outgoing request used the exact canonical UTF-8 bytes required by the frozen configuration.

The checkpoint's existing claim is therefore stronger than its evidence.

2. Required verification

For every captured request in the Batch 5 transport-double suite:

Read the original captured request_raw string.

Encode it as UTF-8 without reserialising or normalising it.

Inspect the original JSON source and identify each top-level envelope member and its exact source span.

Reject duplicate top-level keys.

Require every expected envelope key to occur exactly once.

Extract the original UTF-8 bytes for each key token and value token.

Compare each extracted key token against the RFC 8785 canonical bytes of that key.

Compare each extracted value token against the RFC 8785 canonical bytes of the corresponding value from the frozen configuration's envelope object.

Require all comparisons to pass.

The nested chat_template_kwargs object must be checked as one complete value token. Its nested members must therefore also match their canonical representation.

Important distinction: Do not parse and then reserialise the outgoing request before performing the comparison. That would discard the original representation and recreate the same evidentiary weakness.

The comparison is between original wire-token bytes and canonical expected bytes. It is not a comparison of two parsed Python objects.

3. Source-span extraction requirements

Use a source-preserving top-level JSON member scanner, or an equivalent implementation with demonstrable source-span preservation.

The extractor must:

Operate on the original request text.

Identify top-level members only; nested message fields must not be mistaken for envelope members.

Preserve the exact character span of each key token and value token.

Convert those spans to UTF-8 bytes without changing their contents.

Reject malformed JSON, duplicate keys, missing expected keys, and ambiguous extraction.

Fail closed if any expected member cannot be isolated unambiguously.

A standard JSON parse followed by dictionary equality is not an acceptable substitute.

Whitespace surrounding a member and the ordering of unrelated request-body members are not part of the individual key/value token comparison. Do not claim that the entire request body is byte-identical to the frozen configuration: it contains dynamic message content as well.

4. Transport receipt verification

The captured request must also be tied to what the transport double actually received.

For each scenario:

Verify the transport double received the same request-body bytes represented by request_raw.

Recompute SHA-256 over those original bytes and compare it with request_sha256.

Verify the number of received requests matches the recorded attempt count.

For retries, verify both received request bodies are byte-identical to one another and to the captured request body.

This prevents a correct capture representation from being mistaken for proof of what was actually transmitted.

No live provider is involved. All checks remain against the existing scripted loopback transport double.

5. Required test artefact

Create a distinct artefact:

artefacts/c5-17-envelope-fidelity.json

It must identify:

Test scenario and capture ID.

Transport-double identity.

Frozen configuration SHA-256.

Canonicalisation implementation name, version, and pinned source hash.

Captured request SHA-256.

Number of attempts and transport requests.

For every expected envelope member:

Member name.

Actual key-token byte count and SHA-256.

Expected canonical key-token byte count and SHA-256.

Actual value-token byte count and SHA-256.

Expected canonical value-token byte count and SHA-256.

Explicit byte-comparison result.

Transport-received-body comparison result for every attempt.

Aggregate result and explicit failure reasons.

The artefact must be independently inspectable. A single passed: true field without the underlying comparisons is insufficient.

Do not include credentials, headers, or other secret material.

6. Test coverage

Run the corrected C5-17 verification across every request capture produced by the Batch 5 suite, including the timeout scenario.

The test must demonstrate that it detects at least these deliberately invalid cases in isolated test fixtures:

An envelope value changed while remaining valid JSON.

A missing envelope member.

An unexpected duplicate envelope member.

A noncanonical lexical representation of an otherwise equivalent value.

A changed nested chat_template_kwargs value.

A transport-received body that differs from the captured request body.

These are negative controls for the verification mechanism. They must not alter the frozen configuration or the production adapter.

A negative-control fixture passes only when the verifier correctly rejects it. Do not count a deliberately invalid fixture as a passing production scenario.

7. Runner integration

Integrate the new verification into the existing Batch 5 runner without weakening or replacing existing checks.

The old parsed-value equality checks may remain as additional semantic checks, but they must no longer be presented as proof of byte fidelity.

The corrected runner must:

Run the new verification for each captured scenario.

Preserve the detailed comparison results.

Include the aggregate C5-17 outcome in the overall suite summary.

Fail the suite if any required byte comparison, transport comparison, or negative-control expectation fails.

Preserve existing timeout policy and retry policy unchanged.

Do not alter the adapter's pinned configuration, adapter identity, transport contract, or frozen JCS implementation.

8. Checkpoint documentation and manifest

Update the Batch 5 checkpoint report to distinguish:

Parsed-value equality.

Canonical envelope-token byte equality.

Transport-received request-body equality.

The report must state exactly what the new artefact proves and identify the transport-double-only evidence boundary.

Remove or correct any wording that implies the former parsed-value test established byte-for-byte fidelity.

Update MANIFEST.sha256 to cover the new artefact and all changed files, excluding the manifest itself as before.

Preserve the original checkpoint as immutable history. File the correction as a new checkpoint revision or correction commit; do not rewrite the original commit.

9. Acceptance criteria for Alex's reinspection

C5-17 is ready for reinspection only when all of the following are available at a single identifiable Shelf commit:

Revised runner source.

New C5-17 artefact.

Negative-control results.

Updated suite summary.

Updated checkpoint report.

Updated manifest.
