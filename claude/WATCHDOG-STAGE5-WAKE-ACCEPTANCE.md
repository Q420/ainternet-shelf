# Watchdog Stage 5 (contract Stage 6) — wake layer: ACCEPTED

Re-check of B1 against main @ f445fd08.

- Fired set is rebuilt from the outbox only; the cache union is removed from init and refresh (verified by grep).
- Torn-tail probe: after a partial last line and two consumes, the key has exactly one readable wake (`k2|wake|1`).
- Wake suite from a clean export: 41 fixtures, 0 failed.

S1–S3 accepted as stated in the fix note: the checker is at-least-once for display (no second outbox record), rotation is bounded by the one-unacknowledged-event refusal, and alerts with no ledger event are kept.

Stage 5 (contract Stage 6, wake layer) is closed. Live arming remains gated on the owner's §11 values, including `idle_after_s`, and on the §13 acceptance stage. The checker hook stays un-enabled.
