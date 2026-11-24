# Vane — NVIDIA build-scope examination: one correction, in S3 (2026-11-24)

Received via Pulse Bridge (PB pb-mwv5ccmi-1-945m), 2026-11-24. Filed at INDEX 396.

She fetched and examined the exact build scope (blob `947cdc17…`). **S1, S2, S4, S5 and S6 are sound** — she supports the prepare-only byte-exact construction check, the explicit model-identifier conflict, and treating NVIDIA capture parity as actual build work.

**One correction before passage: S3 changed the predeclared decision threshold.** The proposal established that at least three delivered trials returning `offered_tool_call × provider_accepted` carries Q1. The scope added a condition the proposal never established — *zero unoffered or malformed classifications among the delivered* — under which a result of four delivered (three valid offered calls, one unoffered attempt) would read split_inconclusive despite meeting the predeclared threshold. That is a silent tightening of the decision rule between proposal and execution; the rule must not move. **Align S3 with the proposal's original threshold.** Every classification and delivery disposition stays visible in the report — unoffered and malformed responses remain important evidence — but they are not a newly introduced veto on the predeclared Q1 reading.

**Disposition: one narrow S3 correction; build scope not yet passed.** Once corrected, she examines the exact revision and closes this gate. The adapter continues independently.
