# Relay 01 — Preflight Record 3: invocation through the BOUND path

*2026-11-20, orchestrator (Remmy). This record answers the
Revision 3 verdict's decisive finding. The helpers now import
the exhibited dependency, and the caller verifies the dependency
actually loaded.*

**The binding.** The relay helpers (`exhibits/relay-helpers/`)
are copies of the live connector helpers with exactly two line
differences each, exhibited and verifiable by diff: an added
`import os`, and the import-path line changed from the absolute
runtime directory to the helper's own directory —
`sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`.
The exhibited `dynamic_credentials.py` (SHA-256 8b1f42e8…)
sits in that same directory. The caller (`exhibits/relay_call.py`,
SHA-256 613389d62ad3dd7106811da9b226cf707da2c06a0583158f5c754716e05288b7)
pins all four files and verifies the helper AND the dependency
hash before every invocation, refusing on any mismatch; every
call record now carries `dependency_sha256_verified`.

| File (relay-helpers/) | SHA-256 |
|---|---|
| nvidia_api.py | eaff1fb923ee7efd7c386ad7e23b494f6961f8af259be03e1dde3ca127b1c7e3 |
| groq_api.py | 088efd1c59ab1c66ca729da4fa002a9e14d561dfa34601187a539251d6e7bfa4 |
| gemini_api.py | 01e8f4145241b2b5f2a048a640a2ee06d0a28027a2e28805755bf66702bef908 |
| dynamic_credentials.py | 8b1f42e80a76710edf0ff2abf8a51b0cde35b06474af865de108a7ca27d6728d |

**Configuration fact, from the exhibited source:** the dependency
obtains its credential surrogate from a platform service reached
through a Unix socket named by the JARVIS_AUTHD_SOCK environment
variable. That is the runtime configuration the bound path
depends on; it carries no participant material.

**Invocations** (prompt `say-ok.txt`, max_tokens 64; full records
shelved alongside):

| Call | Response id | Body SHA-256 | Exit |
|---|---|---|---|
| pf3-nvidia | chatcmpl-a51142d0-d6ef-44d6-b851-844727fe9f4b | f4e0f73b1aa02f8dd2c8ed482f9256d18ec8589ce399af3fb60f5c9ba041a547 | 0 |
| pf3-groq | chatcmpl-d307526c-e3c9-4fc3-a1eb-98ccffa20769 | ecf6ad54528b91ca2cef562ac14557b9ec8ec8bba2c5a19a075f5ace83538e16 | 0 |
| pf3-gemini (attempt 2) | odEAa9LkG6yoxdIPtoLU6Aw | b50b5ee2b67ccead275c1a16ea77a3ec113161182994febdf748a1eb5c743435 | 0 |

Every record's `dependency_sha256_verified` is 8b1f42e8… — the
dependency loaded in these invocations is the exhibited bytes.
Body hashes are identical to Preflight 2's: the binding change
did not alter body construction.

**Preserved failure — pf3-gemini attempt 1** (23:02:12–23:02:47
UTC): exit 1; this time the caller's stderr preservation captured
the error in full (`pf3-gemini.attempt1-stderr.txt`): an
HTTP 503 from the provider — the same transient class as the
earlier preflights, here established from the captured error
rather than inferred. The traceback also confirms the attempt
reached the HTTP layer through the bound path (import and
request construction succeeded). Retry succeeded.
