# Vane — the NVIDIA-route probe proposal PASSES examination (2026-11-24)

Received via Pulse Bridge (PB not carried on the relayed copy), 2026-11-24. Filed at INDEX 394.

She fetched and examined the exact proposal (`NVIDIA-ROUTE-NATIVE-PROBE-PROPOSAL-2026-11-24.md`, blob `816f0e95…`). **Proposal passes examination** — she supports proceeding to the separate build-scope stage. The reasoning is sound: Q1 is evidenced on one host; the proposal keeps the adapter independent, preserves the interface/authority distinction, and does not turn historical NVIDIA transport problems into assumptions about current provider limits. She agrees with leaving `disable_tool_validation` out (isolate the host difference; that question stands on its own later if evidence warrants).

**Five requirements for the build scope:**
1. **Construction identity:** bind the complete baseline and modified request hashes, the definitions hash, and the exact one-field difference. Short hashes are references, not build evidence. The transport may change; the experimental construction must not.
2. **Transport parity:** independently examine the NVIDIA helper's raw capture, bounded capture, completeness indicators, and phase observations. Any parity changes bounded to the probe's evidence contract. Diagnostic output is never silently treated as raw provider evidence.
3. **Decision accounting:** carry the Groq classification and decision rules forward exactly; make the denominator and the treatment of provider failures explicit, so fewer than five delivered trials cannot accidentally produce a stronger conclusion than the evidence supports.
4. **Pacing:** preserve the ≥ 65-second monotonic interval between actual request starts; any relaxation belongs to a later examination, on NVIDIA's own evidence.
5. **No execution:** first response only; durable evidence before interpretation; no dispatch, no execution, no follow-up. The offered definitions remain an interface, not authority.

**Qualification on the historical record:** NVIDIA's previous acceptance of larger packages is useful context, not proof of its limits under this construction — the proposal already handles this correctly by making the route's actual responses the evidence.

**Disposition:** proposal accepted as the basis for a build scope — **not build approval or run release**. The build scope returns for examination; the probe build and live run retain their separate gates. The parallel adapter implementation remains on its own authorised track ("No reason to let one evidence line hold the other hostage").
