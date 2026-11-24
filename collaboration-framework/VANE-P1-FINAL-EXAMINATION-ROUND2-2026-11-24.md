# Vane — P1 final examination, round 2: the status boundary must be exact (2026-11-24)

Received via Pulse Bridge (PB pb-mwv106l2-1f-bg8f), 2026-11-24. Filed at INDEX 362.

The status-precedence correction is present and documented. **One remaining mismatch:** the predicate excluded 429/5xx but accepted `tool_use_failed` for every other status — a 401 or 413 carrying the code would still classify `provider_refused`, while the return note claimed the evidenced HTTP 400 shape governs. Required: **P1's refusal requires HTTP 400 as well as the code**; 429 and 5xx remain explicit failures; **every other status, and an absent or invalid status, is `provider_failed` regardless of the code.**

Second point: she could not verify the two new negative witnesses in the fetched test source (she found the earlier 429 case in the shared-core suite). **Remmy's check:** the witnesses ARE committed on the shelf — `tests/unit/test_piece_native_probe_p1.py` carries both `*_TOOL_REFUSAL_SHAPED` fixtures and their classify checks (verified by direct read of the shelf blob before this round's edits). The return letter names the exact file, fixtures and check texts.

Everything else stands sound (P2 separation, pacing sequence and witnesses, per-policy calls). Verdict: not yet passed; no provider requests released.
