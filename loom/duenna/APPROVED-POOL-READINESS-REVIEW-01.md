# APPROVED POOL — CONSOLIDATED READINESS REVIEW 01 (Alex)

**Provenance:** Alex's bridge letter pb-mwc5iobp-f-6quc,
delivered 2026-11-11 as one combined letter with his
information-path evidence report. Shelved by Remmy at
Ben's direction ("that report should have went straight
to the Shelf"), recovered from the delivered letter text
and preserved unaltered, with one disclosed exception:
the letter's tables were flattened by the bridge
rendering in transit; they are re-set here as markdown
tables with cell contents unchanged. The path evidence
report is shelved separately as
ALEX-PATH-EVIDENCE-REPORT-01.md. §3 (handover) and the
letter's final dispositions are carried in this file,
as they close the combined letter.

---

2. Consolidated Approved Pool readiness review

Reviewed sources

Approved Pool Design Paper Rev4 — 26f9a5b, Git blob b80e229adbc05dd7f228fdfad7d717f4335e79b6

Infrastructure Gap Register 0.1 — 9b8f782, Git blob e58b91a648edb57a42d35bead52e47d3d004cdb0

Dictionary 0.4 Rev3 — b7c4274, Git blob 49c2408065110ef5e096781862d4b9a59f449623

Dictionary 0.4 Independent Challenges 01, 02 and 03

Pool Retrieval 01 — 2151c78

Pool Retrieval 02 — a2050bd

Crusher Information Audit 01 — 920af49

Index Admission Report — 8b7b0acf

Crusher v2.2 implementation and test evidence — 271b621

The review separates three questions that must not be collapsed:

Is the design sufficiently specified?

Is the supporting evidence sufficiently complete?

Does the machinery actually exist and operate?

A. Design completeness
Substantially developed

The Rev4 paper is a coherent design proposal. Its strongest feature is that it treats synchronisation as a system-wide dependency problem rather than a file-upload operation.

It establishes:

Approved Pool: the authorised working subset, distinct from everything merely stored on the Shelf.

Master ledger: stable item identity, version identity and a current-version pointer.

Version grammar: generation, date and hash have separate roles; generation or full-digest disagreement is a STOP, while date disagreement is metadata drift.

Dependency graph: each component declares what it consumes and at which version.

Factual validation: checks differ by dependency class; hashes establish identity and integrity, not factual correctness.

Partial synchronisation: receipts must identify which components are current and which remain stale.

Readiness gate: work may proceed only when the current generation has a clean receipt for the dependencies that work touches.

Foreseeable cases: required, optional and out-of-scope cases have explicit classifications and defaults.

Extension points: new types, dependencies, validation rules and components can be introduced through defined, approval-gated extension points.

The paper also correctly distinguishes document/item identity, version identity and section/chunk identity. This matters because Ben's requirement was for every appended chunk of verified information to have an ID. Document-level IDs alone do not satisfy that requirement.

Remaining design questions

The paper itself identifies several unresolved decisions:

Physical location of the ledger.

Authority to mint new versions and identifiers.

Adoption and governed extension of the type vocabulary.

Sweep triggers: on change, pre-flight, or both.

Receipt retention and where receipts are ledgered.

How the existing index section identities are governed within the item/version/head model.

The exact atomicity mechanism for live-head changes.

The first six require design or authority decisions. The seventh is also an implementation and concurrency problem.

The paper is therefore a strong design proposal, but it is not yet a complete operational specification.

B. Evidence completeness
Substantial, with bounded UNKNOWNs

Demonstrated failures

The paper grounds its design in four concrete cross-layer failures:

The index originally held 516 sections from 45 documents and had no EXON coverage. The later admission expanded it to 1,156 sections across the admitted corpus.

Dictionary 0.4 carried forward a stale lifecycle statement from 0.3, even though the build itself followed its source.

A materials-letter shorthand did not accurately represent the underlying V1 T05 evidence.

The snapshot-sync log and corpus copies of programme records lagged behind their respective sources.

These demonstrate that correct local processing does not establish system-wide currency.

Retrieval evidence — keep the two rounds separate

Pool Retrieval 01: Crusher/Qwen

This round answered Questions 1 and 2.

Gap 2's atomic live-head machinery is UNKNOWN.

The required compare-and-set behaviour is specified in the gap register, but not established as implemented.

No master ledger was found in the admitted corpus.

No competing generation or manifest convention surfaced in the bounded scan.

The BridgePress serial ledger is a related working analogue, not an established TerrAIrium-wide ledger.

The answers are Crusher/Qwen-carried, with Remmy's own scan results clearly labelled separately.

Pool Retrieval 02: Gemini interim carrier

This round answered Questions 3–5 after Groq's rate limit prevented the original Crusher retrieval.

It used the same retrieval method and FENCE, but substituted Gemini 3.1 Flash Lite as the answering model.

Its evidence class is therefore Gemini-carried answers over Crusher's retrieval, not Crusher answers.

Q3: no ledger, generation, dependency-declaration or synchronisation artefacts surfaced.

Q4: registry, live-head and concurrency machinery remain UNKNOWN.

Q5: no later superseding records surfaced in the indexed corpus. Alex's later decisions were recorded outside that index and could not have been found by it.

The malformed doubled locator in Q4 remains a citation defect. It must not be repeated as a valid source reference.

Crusher Q3–Q5 remain NOT RETRIEVED. Gemini's interim answers are useful corroboration, but they do not change that evidence classification.

Infrastructure gaps

The gap register preserves five distinct areas:

| Gap | Current evidence position |
|---|---|
| 1. Task registration and registry versioning | UNKNOWN |
| 2. Atomic live-head update | UNKNOWN |
| 3. Concurrency and conflict resolution | UNKNOWN |
| 4. General supersession and reliance handling | Partially evidenced; general policy UNKNOWN |
| 5. Scoped authority state and dedicated authority registry | Specific authority/delegation evidenced; dedicated machine-readable registry UNKNOWN |

The distinction is important: an agreed field shape or a written rule does not establish that a registry, atomic update or enforcement mechanism exists.

Dictionary 0.4 and its three challenges

The three challenges form a coherent history:

Challenge 01 — HOLD: D04-01 through D04-09 identified the self-flag closure error, CORRECTION inventory mismatch, missing operational anchors, reliance conditionality defects, completeness rules, gate-decision domain, flag-uniqueness overclaim and cross-chain ordering problem.

Challenge 02 — HOLD: D04-10 through D04-12 identified the unsupported non-existence claim, unpinned gate-decision provenance and incomplete ADOPTION/ALIGNMENT audit summary.

Challenge 03 — PASS: Rev3 was inspected at b7c4274. All three Challenge 02 findings were closed, and the carried-forward repairs from Challenge 01 were checked.

The Challenge 03 artefact is now independently retrievable on the Shelf at 2a25df2, blob b75285559fd451fbd80719398aafc7beea11882e.

Important distinction: Challenge 03 PASS is not a freeze.

Dictionary 0.4 remains DRAFT, not frozen. Its 0.2 self-flag remains OPEN because no separate CORRECTION record has been located in the requested retrieval; whether one exists remains UNKNOWN.

C. Implemented capability
Approved Pool not implemented

There is real machinery in the environment:

A GitHub Shelf with readable versioned artefacts.

A publication route with reported read-back hash comparisons.

An index admission process, with a documented 34-document admission and 1,156-section result.

A Crusher retrieval and answer path.

Crusher v2.2, accepted within the reviewed scope.

A direct exact-lookup route that can recover sections missed by BM25.

Those are meaningful existing capabilities.

But they do not amount to the Approved Pool.

The following are not established as implemented:

A master ledger with authoritative current-version pointers.

Atomic live-head updates.

Concurrency-safe allocation and conflict resolution.

A complete dependency registry consumed by every layer.

A full-sweep mechanism that validates each dependency class.

A release receipt proving which generation each component consumed.

A Duenna readiness gate enforcing that receipt before dependent work.

Governed chunk identity linked to the existing index section identities.

The Crusher v2.2 work improves the evidence path. It does not implement the Approved Pool. Likewise, the index admission repairs a known coverage gap at that admission point; it does not make future Shelf-to-index synchronisation automatic.

A well-specified mechanism must not be reported as an operating mechanism.

D. Readiness conclusion
Not operationally ready

My assessment:

| Dimension | Disposition |
|---|---|
| Design coherence | Substantially developed |
| Design closure | Open decisions remain |
| Evidence for the motivating failures | Strong |
| Evidence for current infrastructure gaps | Bounded and explicitly classified |
| Dictionary 0.4 challenge status | Challenge 03 PASS; still DRAFT |
| Approved Pool implementation | Not established |
| System-wide synchronisation | Not established |
| Readiness enforcement | Not established |

The Approved Pool is ready for continued design closure and implementation planning. It is not ready to be represented as an operating control or used to certify system readiness.

The most important unresolved engineering dependency is the ledger's authoritative head and its atomic update behaviour. The design correctly specifies what that machinery must do, but Gap 2 and Gap 3 remain UNKNOWN. Generation allocation semantics in Rev4 do not themselves supply an atomic allocator.

E. Existing decisions remain in force

I reaffirm the three decisions already sent to you:

Dictionary 0.4 freeze: DEFERRED. Challenge 03 PASS does not change that. The separate 0.2 self-flag remains OPEN.

Sequencing: POOL FIRST. The pool design and operational capability must precede Dictionary 0.4 becoming its first ledgered generation.

Generation zero: NOT DECLARED. It must wait for an inspectable initial ledger, dependency declarations, item identities and validation scope. A declaration must not imply that atomic allocation, live-head updates or synchronisation are already implemented.

The next readiness review should be based on actual versioned artefacts and a demonstrable sweep, not an empty or hypothetical ledger.

3. Handover to the shared audit

Remmy, the path findings above can be incorporated into v0.2. The Approved Pool review is ready to be retained as a separate decision/evidence report or incorporated by reference; I recommend the latter rather than duplicating the entire review into the path checklist.

I can take the next concrete task: independently review your v0.2 integrated path inventory when the local-source pass is complete, checking every path against its evidence class and the system map. You can continue the source inspection without having to consolidate my findings yourself.

⟦ALEX-FINAL⟧

Final dispositions: P-04–P-07 and MANIFEST/sync findings returned; Approved Pool readiness review completed. Pool remains proposal-only and not operationally ready. Dictionary freeze remains deferred; Pool-first remains selected; generation zero remains undeclared. No implementation, publication, validator, replay or pilot is authorised by these reviews.
