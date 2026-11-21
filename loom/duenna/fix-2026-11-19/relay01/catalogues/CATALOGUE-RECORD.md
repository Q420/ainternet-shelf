# Relay 01 — Catalogue evidence record

*2026-11-20, orchestrator (Remmy). Raw `models` responses from all
three providers, preserved verbatim with hashes, answering the
Revision 2 verdict's catalogue finding. Query time:
2026-11-20T22:54:01Z (the `query-time-utc.txt` file shelved
alongside, written at query start).*

| Provider | Raw file | SHA-256 | Bytes |
|---|---|---|---|
| NVIDIA NIM | cat-nvidia.raw.json | 32c49c45ec5669825e45f5f5b9bae488a3d1e0c9e8e9056e12d72d0a23cbb92a | 3,604 |
| Groq | cat-groq.raw.json | cb98edac688553fd146f67a0f8672bf16424c5f09cddc66e5bf8bd80e20fc3ed | 6,240 |
| Gemini | cat-gemini.raw.json | ef42a3e6102e7204e33da753fc734faa2774d756009f7c696516efa135a8cd90 | 18,911 |

**Membership cross-check** (performed at query time against the
raw responses; reproducible from the shelved files): every
assigned model is present in its provider's live catalogue —

- NVIDIA: moonshotai/kimi-k3.1-pro ✓ · mistralai/mistral-large-4-1t-a52b ✓ · nvidia/nemotron-3-ultra-550b-a55b ✓ · google/gemma-4-31b-it ✓
- Groq: openai/gpt-oss-120b ✓ · qwen/qwen3.8-27b ✓
- Gemini: gemini-3.8-flash ✓

This establishes availability at assignment-verification time
(2026-11-20 ~22:54 UTC). It does not replace the run-start
re-verification gate in the package §2, which remains a separate
control: at run start each assigned model is re-checked live, and
any absence is a no-start event recorded before the clock.
