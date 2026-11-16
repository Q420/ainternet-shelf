# STAGE 6 PRE-FLIGHT — REMMY'S EVIDENCE ASSEMBLY (2026-11-16)

Assembled against Alex's nine-point pre-flight gate (Duenna conversation,
2026-11-16). Alex's side (points 2 and 3: the V3 reconciliation and the
Stage 5 package inspection) proceeds in parallel; this note is Remmy's
half plus the stale-point list for point 2. Nothing here fires anything.

## Point 1 — Authority and scope: CONFIRMED

Controlling records: Step 1 acceptance (record/ALEX-DUENNA-STEP1-
ACCEPTANCE-2026-11-16.md); Step 2 acceptance (record/ALEX-DUENNA-STEP2-
ACCEPTANCE-2026-11-16.md); Step 3 acceptance (record/ALEX-DUENNA-STEP3-
ACCEPTANCE-2026-11-16.md) — correction round COMPLETE. Stage 6 calls:
record/STAGE6-CALLS-DECIDED-2026-11-16.md @ cfe9af58 — smoke authorised
(one minimal call, after Steps 2–3, before the battery); smoke cap
5,000 tokens total; battery 50,000 per instance; BUDGET_EXHAUSTED is
not a pass; 3+ exhaustions halt for review; no paid route; recorder is
the examiner run record adjudicated by Alex; smoke pass = full harness
traversal + a complete, well-formed record; battery bar set by Alex at
the smoke gate. Stage 6 initiated by the owner 2026-11-16 13:45 MST;
sequence confirmed by the owner 2026-11-16 16:16 MST (pre-flight →
smoke as the viability test → framework revamp after).

## Point 4 — Live catalogue: CLEARED

Full live GET /v1/models response captured 2026-11-16 via the
registered NVIDIA connector route (integrate.api.nvidia.com):
33 models visible to the key; response body sha256
4fce0a3d2db34f16f2ce1c33f233e3d3b2e4399d5c6de36096e0b39f4a84441a
(capture preserved with this assembly). The pinned model
nvidia/nemotron-3-nano-omni-30b-a3b-reasoning IS present. No STOP.

## Point 5 — Adapter configuration: VERIFIED

Frozen config: package/adapter/adapter-config-f2-2026-11-12.canonical
.json, sha256 6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba1266299-
99a1f21eb. Values match the frozen set exactly: model
nvidia/nemotron-3-nano-omni-30b-a3b-reasoning; temperature 0.6;
top_p 0.95; max_tokens 20480; stream false; chat_template_kwargs
{enable_thinking: true, reasoning_budget: 16384}; canonicalisation
RFC 8785. Retry policy: max 2 attempts, byte-identical resend,
retryable classes 429/5xx/timeout/connection_error; 120 s per attempt.

## Point 6 — Execution path: VERIFIED, one run-configuration condition

pilot_adapter.py pins PRODUCTION_ENDPOINT =
https://integrate.api.nvidia.com/v1/chat/completions. The adapter
takes base_url at construction; in stage5_mode it refuses any
non-loopback base_url (the Stage 5 transport-double safety). The
smoke run must therefore be assembled with stage5_mode OFF and
base_url = the production endpoint — a run-assembly fact to be
confirmed in the run stack before firing, not a code change. No
alternate model, endpoint, or paid route exists in the adapter.

## Point 7 — Harness and examiner readiness: CONFIRMED

The full harness path has traversed end-to-end three times (G4,
G4CORR-20261115-001, G4CORR-20261116-003) producing complete,
well-formed run records; the examiner machinery re-derived the
correction run independently, and Step 3 reproduced the suite and
the examination byte-identically from the shelf alone. The adapter
captures every response verbatim with its usage block
(response_usage) in the capture record. The smoke uses this same
harness + examiner path with the live adapter configuration above.

## Point 8 — Budget enforcement: FINDING — no token-cap machinery exists

The driver's budgets are TIME budgets (tool_step_s, model_step_s,
run_s, tree_s → RUN_BUDGET_EXCEEDED). No token ceiling exists
anywhere in the package. Token usage IS captured verbatim per call
(adapter response_usage), so the 5,000-token smoke cap can be
accounted exactly from the record — but enforcement would be
post-hoc (accounting + verdict: over cap = BUDGET_EXHAUSTED, not a
pass), not preventive. The envelope's max_tokens (20480) means a
single call could in principle exceed 5,000 total tokens. For the
joint gate: does post-hoc accounting against the captured usage
satisfy "enforced and recorded" for a single minimal call, or is a
preventive mechanism required first? Examiner's call.

## Point 9 — Repetition conditions + crash components: CONFIRMED UNCHANGED

The four crash-evidence components (event writer; supervisor
crash-detection/CRASH issuance; commitment format; examiner
anchor-verification) live in the checkpoint bundle's package. Step 3
verified the bundle against its freeze manifest: sha256sum -c
150/150 — every bundle file, the four components included, matches
its freeze-time hash. The correction round's changes are enumerated
and outside the four components: one stub_script.json field (Step 2),
the manifest listing itself (Step 3 repair i), and the new repro
package folder (Step 3 repair ii). Tools, rules, and the pilot
snapshot are unchanged since Stage 5; the S1–S5 repetition rule
therefore has nothing new to repeat on. (Alex's Stage 5 inspection,
point 3, cross-checks this from his side.)

## Point 2 support — Pack V3 stale points (for Alex's reconciliation)

- Item 6 (line 51): "Smoke call — OPEN OWNER DECISION" — superseded
  by STAGE6-CALLS-DECIDED @ cfe9af58: authorised, capped, pass bar set.
- "Still open" list (lines 62–72): smoke authorisation + pass bar —
  decided; the "cannot start" condition resting on them is lifted
  for the smoke (the battery remains gated at the smoke gate).
- Step 2 / Step 3 items written while pending — both steps are now
  complete and accepted (see Point 1 records).
Everything else in V3 (Rev 26 governing; the pinned model; the
13-instance battery) stands.

## Open for the joint gate

1. Point 8 mechanism (above) — examiner's call.
2. Alex's points 2–3 results, and his repetition/scheduling
   qualification from the reconciliation reply.
3. Run-stack assembly confirmation for point 6's condition
   (stage5_mode off, production base_url) — assembled and shown
   before firing.
