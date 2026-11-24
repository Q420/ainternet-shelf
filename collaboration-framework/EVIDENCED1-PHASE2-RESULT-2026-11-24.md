# Evidenced run — PHASE 2 RESULT: stalled at iteration 1, fully evidenced (2026-11-24)

Ran 2026-11-24 ~01:00 MST under the INDEX 328 judgement + receipt; harness exit 0. Recorded at INDEX 329. **Remmy verified first-hand** from the record, report.json, the captured artifact, and an independent checker run. The one authorised rerun is spent.

## The run
- **21 events.** The gates fired in their mandated order: ASSEMBLY_JUDGED (14, mode `text`, receipt canonical hash `26c55127…` bound) → PACKED (15) → ISSUE_AUTHORISED (16) → INSTANCE_ACTIVATED (17) → LOOP_ITERATION (18) → CALL_ENTERED (19) → **RESPONSE_EVIDENCE (20, outcome `captured`)** → LOOP_STALLED (21).
- **Outcome: stalled, iteration 1, 0 dispatches, no brief.** Stall ground `provider_failure` — provider_error: HTTP 400.
- **Checker: all checks ok, 0 problems** over the full 21-event record (Remmy-ran).

## What the worker did — from the captured evidence, not inference
The evidence regime's first live exercise worked end to end: the disposition was committed before the stall was adjudicated, and report.json's `evidence_summary` (the INDEX 323 correction) carries the entry — disposition `captured`, artifact sha256 `cdae339f…`, 275 L1 bytes, `stop_reason: eof`, `body_complete: true`, `artifact_check: "ok"` (report == record == filed artifact).

The captured body is the provider's refusal envelope: HTTP 400, code **`tool_use_failed`**, message **"Tool choice is none, but model called a tool"**, and the failed generation names the environment tool **`container.exec`**. In text mode — no tools offered, tool choice none — the model's first action was nevertheless a native environment-tool call, and the provider refused the response wholesale. This is the attempt-8 phenomenon (INDEX 265–266) recurring inside the worker loop under the judged mode — this time preserved byte-for-byte in `responses/iteration-18.json` (L1 raw + L2 envelope), diagnosable from evidence rather than reconstruction.

## What this establishes, and what it does not
- **Established:** the evidence piece does its job live (capture-before-effects, disposition lifecycle, summary, checker — all as passed at INDEX 320); the run's failure is fully attributable: the model's environment-tool reach fires even when the contract offers no tools at all. Ten runs have now ended before the assignment; this is the first whose decisive moment stands captured in full.
- **Not established:** composition competence — still untested; the worker has never yet produced an interpretable first action under any mode.
- **The open question is a direction question, not a loop decision:** Ben's conditional ruling (INDEX 267) — if the reach is uncorrectable, allow the tool and accept its output — now has ten runs of evidence behind it, this last one complete. Whether the reach is "uncorrectable," and what accepting the tool would mean inside the framework's grant discipline, is for the examiner's examination of this run and Ben's ruling. The loop takes no further run on its own authority.
