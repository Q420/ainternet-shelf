# Package breakdown — attempt 6, iteration 2

The composition request Groq refused with HTTP 413, reconstructed from attempt 6's record with the loop's own package builder and rendered through the adapter exactly as a real call renders it (the transport's helper was stubbed in-process; **nothing was sent to any provider**). Method, provenance and deviations are recorded in full in `package-breakdown-attempt6.json`.

Frozen head: event seq 29 (cursor 16 → 29). Model: `openai/gpt-oss-120b`. loop.py sha256 `2c6f79b2984b62b1708438120df789f0e4ff7dd10c1acd664d6dbd08a1ed6706`, adapter.py sha256 `dbe5d07298596d03043f14da1699ad28a98ecfd6d86bf397d3ebde8736c2b05f`.

| # | Component | Bytes | % of final |
|---|-----------|------:|-----------:|
| 1 | Retrieved source content | 117,682 | 87.43% |
| 2 | Case view and assignment | 1,589 | 1.18% |
| 3 | Tool catalogue | 1,183 | 0.88% |
| 4 | Provenance and dispatch material | 12,305 | 9.14% |
| 5 | Framework / package overhead | 1,846 | 1.37% |
| 6 | **Final serialized request** | 134,605 | 100.0% |

Components 1–5 sum exactly to the final size; component 5 was also summed independently from its known parts and the residual is 0 bytes.

**The headline:** each of the three sources is carried **twice** — once inside `delta`'s TOOL_OUTCOME payload and once in `tool_results` — so the retrieved content's footprint is roughly double the 57,562 bytes the three source files occupy on disk (their content as recorded totals 57,179 characters; JSON escaping at both layers accounts for the rest of the carried size).

## Reconciliation against the historical 134,844 bytes

- INDEX 218's simulation body reproduced exactly: 134,844 bytes (matches: True).
- That figure carried the simulation's appended override ask (234 bytes as carried) and the longer Kimi model name; attempt 4's package rendered as a real call (no override) is 134,610 bytes.
- Attempt 6 measured: 134,605 bytes — exactly 5 bytes below attempt 4's real-call rendering, and the entire difference is the model name (`moonshotai/kimi-k3.1-pro`, 24 chars, vs `openai/gpt-oss-120b`, 19) sitting in the body skeleton. The two runs' packages are otherwise byte-for-byte equal in every component (per-component tables for both attempts are recorded in the JSON): same cursor range (16 → 29), same event shapes, fixed-length hashes/ids/timestamps, and `seconds_remaining` values of equal rendered length (548.0 vs 598.0). So the historical figure decomposes exactly: 134,605 (attempt 6) + 234 (the simulation's appended override ask) + 5 (model name) = 134,844. No unexplained residue.

One field is inexact by construction: `bounds.seconds_remaining` is the record-derived 598.0 (600s deadline minus the 2s activation-to-iteration-2 interval in the record's timestamps); the live monotonic value cannot be re-read, and its rendered digits may differ by a few bytes. Everything else is re-derived by the framework's own code from the record.
