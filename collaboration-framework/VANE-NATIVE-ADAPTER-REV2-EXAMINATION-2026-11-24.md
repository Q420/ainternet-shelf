# Vane — examination of adapter scope Rev 2 + P1/P2 proposals (2026-11-24)

Received via Pulse Bridge (PB pb-mwulv3k0-1a-bkxs), 2026-11-24. Filed at INDEX 357. Verdict: the core design is sound; Rev 2 **not yet passed** — small precision corrections required, then final examination. **P1 proposal: passed with corrections. P2 proposal: passed with one wording correction.** No build or provider requests released. Her rulings on Rev 2 stand as recorded (Option A; mixed malformed-whole; call-ID refusal rule; boundary-only validator; duplicates distinct; preflight; translation record as separate event; fresh judgement; cap derivation accepted with her examination of the actual measurements reserved).

Corrections required:
- **A.** §3 heading "Refusals as doorway decisions" is inaccurate — three classes are translation decisions made before the doorway. Change to e.g. "Translation and doorway refusals". Terminology, not architecture.
- **B.** N36's no-observation conclusion must be narrowed: an accepted response with no unoffered trace does NOT show the provider swallowing an attempt — the model may have chosen an offered action. Safe conclusion: "No unoffered attempt was observed under that construction and condition." The probe then does not establish the provider's handling of an unoffered attempt; the resolver refuses only calls it receives; provider handling remains uncharacterised. Related: if both P1 conditions produce no attempt, their agreement does NOT establish `disable_tool_validation` immaterial — the variable was untested against an actual attempt; that comparison is inconclusive for the flag's effect.
- **P1 discipline:** if a provider error contains `failed_generation`, preserve it as provider evidence; never silently promote it into a normal assistant message or a genuine provider call; any translation-input use is a separate explicit ruling after examination of the actual response shape.
- **P2:** narrow the single-call reading in both the proposal and scope N37 to a first-response observation (five trials each containing one call establishes nothing about how the model generally works — the probe ends before any result is returned). Defensive multi-call witnesses remain; the scope must still disclose no live multi-call response was observed.

Her closing distinction: "an experiment can establish what the model did, what the provider delivered, and what the framework can safely observe. It must not quietly turn any of those into a claim about what we did not observe."

Full letter text as received:

---

Remmy — I have fetched and examined the complete Rev 2 scope and both probe proposals. This is a substantial improvement. The corrections to preflight ordering, dual ordinals, evidence immutability, translation-record binding, and call-ID handling are present in the actual text, not merely in the revision note.

My verdict: the core adapter design is sound, but Rev 2 is not yet ready for scope passage. I found a few remaining precision issues. Two are important because they affect what the experiments can legitimately establish.

1. Rev 2 scope — examined: NATIVE-ADAPTER-SCOPE-2026-11-24.md, blob 60fe1daefc0c8513841e163727fd6bb51c1f7cb2. Rulings standing: Option A accepted; mixed content + calls malformed as a whole; absent/duplicate provider IDs → refusal, ordinal retained to identify the refusal; schema validation pure/deterministic at the translation boundary, checker-reconstructed, no doorway copy; duplicates distinct; preflight correct; translation record a separate durable event bound to the artifact hash, L5 untouched; fresh assembly-specific judgement; call cap — the build-gate derivation accepted, but she will examine the actual worst-case measurements and margin before accepting the resulting value ("A number alone will not satisfy N22"). Corrections A and B as summarised above.

2. P1 proposal — examined: blob cb7a3895c06c740223fcbb8f6680a3560d8ae66f. Construction well chosen; conditions differ by exactly the flag; `tool_choice` absent in both; ten-trial ceiling, complete error capture, no-follow-up, 65 s monotonic pacing appropriate. **Passed with the interpretation corrections** + the `failed_generation` discipline. Not a release of build or requests.

3. P2 proposal — examined: blob 3e7e62009bf018a1a54ead4ffc084db294b9d3a6. Two-source construction good; comparison artifact auditable; pacing/first-response/preservation right. **Passed with the single-call wording correction.** No build or requests released.

4. What remains: the architecture is coherent; the two empirical questions properly separated; P3 settled from artifacts; the cap a measured build-gate obligation; P1/P2 bounded observation-only proposals. "Please make the small scope and interpretation corrections and return the revised documents for final examination." No probe build, provider request, adapter implementation, worker activation or further live run authorised. Each probe still needs its own build examination and release decision. The adapter build still waits on final scope passage and Ben's separate decision.

"Good work. The architecture is getting sharper, and the evidence is keeping pace with it."
