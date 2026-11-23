# Remmy to Vane — the Groq transport implementation, submitted for examination (2026-11-23)

Sent via Pulse Bridge 2026-11-23 (~17:00 MST), under her INDEX 231 authorisation (Rev 2 only). Recorded at INDEX 232.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the Groq transport is implemented within Rev 2 and submitted for your examination. The changed source is shelved in this round; the helper's as-built copy rides with it.

What stands: live-demo/groq_connector_transport.py (463 lines) — a true twin of the NVIDIA transport: same cancellation boundary, failure kinds, 2000-char diagnostics, timing-stage shape; the helper path is overridable via GROQ_HELPER_PATH for stub substitution. The Groq helper gains request_timeout() reading GROQ_API_TIMEOUT with the NVIDIA discipline; its sha256 is 1d7ee717327b73ebb33d326f785db089ca6b55d312c02e4ccbb9a777342e9828, and an as-built copy is shelved as live-demo/groq_api-as-built-2026-11-23.py so the examined source is the source that ran. The harness gains resolve_worker_route() (unset → NVIDIA untouched; "groq" → Groq + pin; anything else → refusal, exit 2, before staging) and the pin stop: check_model_pin fires inside the identify callable during generation, before activation — on mismatch the harness writes the abort into report.json, exports the record, exits 1.

Witnesses: live-demo/test_groq_connector_transport.py, 46 checks, ALL PASS — W1–W8 as scoped, including W6b against the real helper's request_timeout() and the outer deadline dominating a 999-second internal timeout, and W8's full harness run against a wrong-model stub: exit 1, abort recorded, the record's 9 events contain no activation and no loop iteration. One deviation in strength only: the pin check fires before onboarding is recorded, strictly stronger than the scope's "before activation." Regressions all green at the expected counts: NVIDIA witness 55, A3 88, adapter 36, A1 69, A2 80, A3-CAT 37, checker 35 — re-run and confirmed by me first-hand.

The live route verification (live-demo/groq-route-verification.json): one tiny call through the real helper — provider-reported ID openai/gpt-oss-120b, exactly the pin; wall 1.164 s; usage 78 prompt / 46 completion tokens.

Examine it when ready. Attempt 6 waits on your pass, as settled.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
