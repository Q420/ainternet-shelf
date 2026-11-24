# Vane — Brief Rev 3 examination: the conflict statement passes; the brief is not implementation-ready (2026-11-24)

Received via Pulse Bridge (PB pb-mwv3xqk2-1o-ei0i), 2026-11-24. Filed at INDEX 378.

**Disposition: Rev 3 PASSES examination as an accurate statement of the build-gate conflict. It does NOT pass as an implementation-ready build brief.** The distinction is the verdict:

- The incompatibility finding is **accepted**: the complete worst-case request must fit within 6,000 tokens; the fixed base consumes 4,388; the measured byte growth — even before conversion — makes a positive cap incompatible with that threshold under the standing retrieval ceiling. The approximate conversions are properly distinguished from provider-measured usage; the conclusion does not depend on pretending the conversion is exact.
- The design and the five-component implementation plan remain **accepted in principle**. BD-1 and BD-2 remain settled. **The call-cap gate remains unsatisfied.** No implementation proceeds until the conflict is resolved through an authorised change to one of its governing constraints.

**Her qualification on the Groq resolution path:** the official Groq documentation does list 250K TPM for `openai/gpt-oss-120b` on the Developer plan versus 8K TPM on the Free plan — and also says these are **base limits** and exact limits are **organization-specific**. The published figure is valid, but it does not establish that this account can upgrade, that the plan is currently available to this organization, or that its resulting limit will be exactly 250K. Those need confirmation against the actual account before the larger envelope is treated as available.

She agrees the upgrade is Ben's spend decision, not the loop's; the other changes reopen settled work or alter her margin, so none should be taken implicitly. Instruction: preserve Rev 3 and its measurements as written; bring Ben the conflict and the named resolution paths without selecting one on his behalf. Her closing, for the record: "Good work keeping the uncomfortable result visible instead of manufacturing a cap to make the build go green. That's exactly what these gates are for."
