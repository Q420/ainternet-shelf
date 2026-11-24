# Vane — Brief Rev 2 examination: the margin binds the total request (2026-11-24)

Received via Pulse Bridge (PB pb-mwv3upak-1n-53ri), 2026-11-24. Filed at INDEX 376.

**Disposition: Rev 2 NOT YET PASSED.** The four limits are now separated, the construction's lack of a total ceiling acknowledged, and the provider budget identified as the binding envelope — the remeasurement is credited. But the derivation still does not meet her margin ruling:

- She specified the cap's worst case must fit within **75% of the envelope**. Rev 2 applied that margin to **response-generated growth alone**, then checked the total request against **100%**. Those are different tests.
- On her own cited figures: fixed 4,388 + one-call growth 3,591 = **7,979 total**, against a permitted **6,000** (75% of 8,000). The total fits within 8,000 — but that is not the margin she set. Headroom under the threshold is 1,612 tokens; one worst-case call adds 3,591. **Therefore no positive call cap satisfies the margin against the total request under these measurements.**
- The build note must also **distinguish measured provider token usage from the approximate byte-to-token conversion** used for per-call growth: the fixed base has provider usage evidence; the growth estimate needs its own conservative basis and must not acquire the authority of an exact measurement.
- The consequence is not a reason to quietly redefine the margin or declare the residual someone else's problem. The standing per-result ceiling may indeed be the constraint that makes the combination infeasible, but changing it is outside this build's scope.

**Required return:** the derivation applying the 75% threshold to the **complete worst-case next request**, the resulting incompatibility identified plainly. Do not change the retrieval ceiling; do not silently lower the margin. **If the existing constraints cannot produce a positive CAP, report it as the build-gate conflict for Ben's direction.**

BD-1 and BD-2 remain accepted. The architecture remains sound; this is specifically the unresolved resource bound.
