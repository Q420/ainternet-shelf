# STAGE 6 SMOKE ASSEMBLY — EVIDENCE FOR THE EXAMINER (2026-11-16)

Built under Alex's smoke-config ruling (record/ALEX-DUENNA-SMOKE-
CONFIG-RULING-2026-11-16.md). The assembly was verified end-to-end
against the transport double; NO live model call has been made.
Venue: this assembly runs on Remmy's VM, not the laptop room —
the sanctioned credential route (connector surrogate) and the
egress proxy live here; the harness and driver are the same
pinned artefacts (hashes in the dry-run record's pins).

## The eight required evidence items

1. **Frozen configuration** — adapter-config-f2-2026-11-12.
   canonical.json, sha256 6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb, source file unchanged
   (re-hashed at assembly time; the bundle is untouched).
2. **SMOKE CONFIG** — smoke-adapter-config.json (this folder).
   Exactly two field changes vs the frozen config:
   envelope.max_tokens 20480 → 4355; retry_policy.max_attempts
   2 → 1. Nothing else differs (full JSON comparison at build).
3. **Smoke config sha256 (independently recomputed)** —
   ebb83d772a69da867721990917fef2326516fe71ad075b5693bc15e6e2b4f9ed
4. **Exact request body** — the dry-run capture (dry-run/
   capture-final.json) carries request_raw verbatim: 926 bytes,
   2 messages (system + user). The live body is identical by
   construction (same tree, same snapshot, same envelope; only
   the endpoint differs).
5. **Input upper bound, framing included** — message content
   totals 597 bytes; content tokens ≤ content bytes (the
   byte-bound the examiner accepted). Chat-template framing
   allowance: 16 tokens per message × 2 + 16 per conversation
   = 48 (the template's actual per-message framing is a
   handful of special tokens; 16 is generous). **Input bound:
   645 tokens** for the complete rendered input.
6. **max_tokens calculation** — 5000 − 645 = **4355**, the
   value in the smoke config. One call only (item 7 + tree
   guarantee below), so input + maximum output ≤ 5000 holds
   for the whole smoke by construction.
7. **max_attempts = 1 in the actually loaded configuration** —
   load test: the constructed smoke Adapter reports
   retry.max_attempts == 1 and envelope.max_tokens == 4355
   from the loaded config (not from the file alone).
8. **Post-call usage** — the adapter captures response_usage
   verbatim in every capture record; the live run's capture
   will be compared against 5000 in the run evidence. (The
   dry run's usage figures are the double's canned values and
   are NOT evidence of live usage.)

## The loading path (examiner's requirement)

smoke_adapter.py (this folder) is the frozen pilot_adapter.py
with the differences shown in ADAPTER-VARIANT-DIFF.txt:
- PINNED_CONFIG_SHA256 → the smoke config's hash; ADAPTER_ID →
  pilot-adapter-stage6-smoke/1.0. The frozen check itself is
  unweakened — load tests: (a) the FROZEN adapter REJECTS the
  smoke config (divergence error, as designed); (b) frozen
  adapter + frozen config constructs normally; (c) the smoke
  adapter constructs in live mode with endpoint
  https://integrate.api.nvidia.com/v1/chat/completions
  (construction makes no network call); (d) the smoke variant
  still enforces the stage5 loopback guard in stage5 mode.
- Credential: for the production host only, the request
  carries the registered connector's dynamic credential
  surrogate (custom.nvidia), swapped for the real key on the
  approved request. No key is stored, read from disk, or
  placed in any file, header dump, or capture (the adapter's
  redaction patterns also cover Bearer/nvapi material).
- Proxy: the variant honours the environment proxy — on this
  host it is the egress and credential-swap route. Probe
  evidence (catalogue read): default opener → HTTP 200;
  no-proxy opener → SSL failure (direct egress is
  intercepted here). no_proxy bypasses the proxy for
  loopback, so double mode is unaffected. The frozen build's
  no-proxy rule stands untouched in the frozen adapter.

## Tree choice (disclosed)

T02 was assembled first and dry-run: its MODEL step carries
recovery return_once with max_attempts 2, and the dry run
indeed made 2 calls — a per-call ceiling could not bound the
smoke total without modelling the retry feedback. The smoke
tree is therefore **T04**: 3 steps (TOOL, TOOL, MODEL), its
MODEL step has recovery None → the driver's max_attempts
defaults to 1 → **exactly one adapter call, guaranteed by
the tree definition**. The final dry run (this folder)
confirms: 1 capture, T04 COMPLETED, complete run record.

## Run stack, as it will fire

smoke_harness.py (this folder): SMOKE_MODE=live →
stage5_mode=False, base_url https://integrate.api.nvidia.com/v1
(demonstrated at construction, item (c) above). The live run
executes under the pilot supervisor (START/TERMINAL
commitments) with the harness, the same pattern as the
correction runs, venue this VM. Battery_id STAGE6SMOKE.

## File hashes (this folder)

- smoke-adapter-config.json: sha256 ebb83d772a69da867721990917fef2326516fe71ad075b5693bc15e6e2b4f9ed
- smoke_adapter.py: sha256 10e0254d58f1a03ace9bf7e600dac519089110240e361cf06588ba40666f4e81
- smoke_harness.py: sha256 575bc50a05debc36f9b0146467a0b2642fdaa9813beea94618a5489286ff35c4
- ADAPTER-VARIANT-DIFF.txt: sha256 3ed4d469cfaf2ed16dc7c91d3907ddbc483eec427e62dea3b05ff9b72ac26208

## Still outstanding at this filing

Claude's formal §7 Step 6 disposition (the discharge-package
round is Remmy's next action). No smoke call is requested
until the examiner's final gate ruling.

## Erratum (2026-11-16, after the examiner's inspection)

smoke_harness.py: one stale docstring line described the tree
as T02; corrected to T04 (the executable selection and the
run record always identified T04 — documentation only, as the
examiner classified it). Corrected file sha256:
a2639808b624b6f7922ef043f52a493d03fd9106d173c17b9e3f8b293f822f33
(supersedes the hash listed above for smoke_harness.py; no
other file changed).
