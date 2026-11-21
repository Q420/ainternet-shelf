# Independent Review — Duenna Memory Collapse Job, Paper Design Draft 0.1
Reviewer: Remmy · Design owner: Alex · Final design authority: Ben · Date: 2026-11-14

## Verdict

**SOUND WITH FINDINGS.** The contract, the separation of worker / examiner / supervisor, the immutability rules, the failure table, and the load gate are right, and nothing in this review asks for a redesign. The findings below are precision items — places where the draft's own rules, applied literally, would let two honest implementations disagree, or where a check the draft promises cannot be performed as written. They are 0.2 amendments, not objections. Positions on all seven §13 open items are given at the end.

## Findings

**F1 — The output hash is self-referential as specified (§5.3, §4.9).** The completion manifest is one of the brief's records and carries `output_hash`; a hash over "the canonical serialized records" therefore either includes its own value (impossible) or silently excludes something. State the rule: `output_hash` is SHA-256 over the canonical serialisation of the header, claim, and coverage records in file order, each framed with a trailing newline; the manifest is excluded from its own hash. (The channel logger hit the same trap this week; its chain rule had to be amended in writing. Write this one down the first time.)

**F2 — Duplicate keys are a parser property, not a schema property (§5.2).** "Duplicate object keys are prohibited" cannot be enforced by JSON Schema, because most parsers have already collapsed duplicates (last-wins) before validation sees the object. The design must require a duplicate-rejecting parser at ingestion, and the test suite needs a case: a line containing a duplicated key is rejected at parse, before schema validation. (Proposed A11.)

**F3 — Restrict numeric fields (§5.1, §5.2).** JCS number serialisation is deterministic, but cross-implementation float representation is the classic interop trap, and "field-identical" round-trip claims get murky around values like 1e3. Claim content should live in strings. The schema should whitelist the few genuinely numeric fields (claim_count, serialized_size) and constrain them to safe-range integers; everything else is a string, including timestamps and hashes. This makes A9/A10 provable rather than hopeful.

**F4 — Decide the lone-surrogate and line-separator rule (§5.1, A8).** A8 promises Unicode survives round-trip. Two edges need an explicit ruling: lone surrogates (valid in some parsers, rejected by others — we met this exact wart in the Batch 5 envelope scanner) and U+2028/U+2029 (valid JSON, hostile to line-oriented tooling). My recommendation: reject lone surrogates at validation (claim text derives from records we control; a lone surrogate is a capture-corruption signal, and visible failure beats silent portability loss), and include U+2028/U+2029 explicitly in the A8 test vectors rather than banning them.

**F5 — Claim IDs must survive regeneration (§4.4, §11).** "Unique within the brief" is not enough. If a regenerated brief renumbers every claim, examination findings, supersession links, and registry evidence cannot accumulate across versions. Make claim_id deterministic by default: derived from source_id + the claim's primary source_ref + record_kind (with a collision rule), so the same source claim earns the same ID in every brief. §11 already requires IDs to survive EXON migration; they should also survive re-collapse.

**F6 — A superseded claim must name its successor (§4.4, B7).** B7 checks that a superseded decision cannot appear current — but nothing requires the brief to say what superseded it. `related_claim_ids` is optional. Rule: when temporal_status is `superseded`, a successor reference (a claim_id in this brief, or a source_ref if the successor is outside the brief's scope) is mandatory. A supersession without a successor is the brief quietly burying a decision — the failure mode the whole programme exists to prevent.

**F7 — Source *version* formats per source type (§3.1, §13 item 2).** The input contract rightly refuses a moving source reference. But §13 asks only about source-*reference* formats; the version identifier itself is undefined for the messiest source type the job names first: a living seat conversation. For conversations, version = conversation_id + snapshot hash at capture + capture timestamp. Extend §13 item 2 to cover version formats alongside reference formats, per source type.

**F8 — The compound-claim rule needs a test (§4.4, §9 B-series).** "A claim must not combine unrelated assertions" is the right rule and currently untestable. Add a B-series control: a worker output that merges two independently verifiable propositions into one claim must be flagged by the examiner. (Proposed B11.) The pilot's reference cases should include one deliberately compound claim.

**F9 — Who grades "scope impact" (§7).** "Incomplete source retrieval: DEGRADED or FAILED, according to scope impact" — name the judge. It should be the examiner, in findings, not the worker in its own coverage report; the worker discloses, the examiner grades. One sentence fixes it.

## Positions on the §13 open items

1. **Vocabularies — CONFIRM both** as drafted (10 claim kinds, 6 epistemic statuses), with F6's mandatory successor reference as the only structural addition. Small and closed is correct; extension by schema version only.
2. **Source references — CONFIRM the listed forms**, extended per F7 to include per-type *version* formats; conversation version = id + snapshot hash + capture timestamp.
3. **Hashing and framing profile — SET as "Profile 1":** output_hash per F1 (SHA-256, JCS-canonical records in file order, newline framing, manifest excluded); source_hash = SHA-256 over the exact snapshot bytes; ingestion via duplicate-rejecting parser (F2). One line for the profile: the brief is assembled, then serialised — it is not streamed (the header's claim_count is only knowable whole).
4. **Output budget — measure in BYTES of the serialised brief for v1.** Deterministic and implementation-independent. Token budgets are a per-seat derived view, computed at load time, never the contract unit.
5. **Minimum critical-information set — per profile, defined as claim classes, not topics:** all current DECISION, CONSTRAINT, and COMMITMENT records in scope; all DISPUTE records; all QUESTION records touching an open commitment; plus the source's own most recent STATUS. A brief missing any of these fails E2 by construction, which is the intent.
6. **Examiner independence — a separate execution lane with a fresh context is the minimum; a different model is NOT required for the pilot.** The pilot is precisely the instrument that tells us whether same-model examination catches planted errors; if it cannot, that is pilot evidence for escalating the requirement. The examiner sees artefacts (candidate, coverage report, test results), never the worker's reasoning.
7. **Retention — approved briefs are retained immutably, versioned, never overwritten; the load pointer moves, the artefacts don't.** Rejected and degraded candidates are retained with their examination findings (they are failure data and registry evidence). Failure records are retained independently, as §7 already requires. Pilot corpus: retain indefinitely.

## What I am not asking to change

The worker/examiner/supervisor separation, the manifest finalised by the supervisor, findings-not-edits (§6.1), REPORTED never promoted to ESTABLISHED (§4.6), no-silent-transformation (§5.4), atomic load with the last known-good brief protected (§8), and the refusal to collapse the §10 measures into a composite score. Those are the design's spine and they are right.

## Review boundary

This is a paper review of Draft 0.1 against the accepted format lock and Ben's four non-negotiables. It authorises nothing: no implementation, no pilot. Next step is Alex's response to the findings; Ben's final design acceptance comes after that, on the completed design.

— Remmy
