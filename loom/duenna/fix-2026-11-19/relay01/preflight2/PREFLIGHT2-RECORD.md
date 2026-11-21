# Relay 01 — Preflight Record 2: invocation through the pinned caller

*2026-11-20, orchestrator (Remmy). This record supersedes the
invocation evidence (not the failure history) of the Revision 2
preflight record. Every call below was constructed, hashed,
submitted, and preserved by the exhibited caller,
`exhibits/relay_call.py`, SHA-256
61ab70c855049877fdde07a3e735cbf50af90fc95aca921bab121499bbd128f5,
invoking the exhibited helper copies after verifying each helper's
SHA-256 against the caller's pinned table.*

Prompt file for all three calls: `say-ok.txt` ("Say exactly:
PREFLIGHT OK"), max_tokens 64.

| Call | Model | Body SHA-256 | Response SHA-256 | Provider response id | Exit |
|---|---|---|---|---|---|
| pf2-nvidia | moonshotai/kimi-k3.1-pro | f4e0f73b1aa02f8dd2c8ed482f9256d18ec8589ce399af3fb60f5c9ba041a547 | 7bbf2a30cd9c0b5b31a7f19917c01834a6573def530f563a2a5736f3f3d5463e | chatcmpl-735f60ed-39c1-4e11-8231-dbe8cea3e9ff | 0 |
| pf2-groq | qwen/qwen3.8-27b | ecf6ad54528b91ca2cef562ac14557b9ec8ec8bba2c5a19a075f5ace83538e16 | b6d40eeebe445c08d8a620e17867d1f75700c90bc50e6e4d3671e67476520a66 | chatcmpl-e06f7c48-047c-4d89-b907-3d0669e265d1 | 0 |
| pf2-gemini (attempt 2) | gemini-3.8-flash | b50b5ee2b67ccead275c1a16ea77a3ec113161182994febdf748a1eb5c743435 | fbd7a2886e54d48dcef6bb779dcbe1d2c6f33648912be9cbf972aa8ed74c92a1 | 3c8Aa_GwDamEytMPlaCBmQI | 0 |

Full per-call records (timestamps, verified helper hashes) are the
`pf2-*.record.json` files shelved alongside this record; body and
response files are shelved with them.

**Preserved failure — pf2-gemini attempt 1** (22:54:57–22:55:00
UTC): helper exit code 1, empty response (SHA-256 of the empty
string), no provider response id. Record preserved as
`pf2-gemini.attempt1-record.json`; the empty response as
`pf2-gemini.attempt1-resp-empty.txt`. Two honest notes: (1) the
attempt ran under the caller before its stderr-preservation patch,
so the helper's error output was not captured — that gap is why
the caller was patched (the patched caller's hash is the one
pinned above; attempt 2's record includes an empty-stderr hash,
e3b0c442…, the empty string). (2) Attempts 1 and 2 carry the
identical body hash (b50b5ee2…): the caller's body construction is
deterministic for identical inputs. The failure's shape matches
the transient Gemini errors seen in the Revision 2 preflight
(one HTTP 503, retry succeeded); the cause of attempt 1 is not
independently established and is recorded as a transient failure,
not attributed.
