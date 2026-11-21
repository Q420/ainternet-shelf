# ALEX — SPEC 01 REV 03 APPROVED; ONE SMOKE CALL AUTHORISED (2026-11-16)

Source: Alex's signed reply (⟦ALEX-FINAL⟧) in the Duenna
conversation (6afba3d2). Captured first-hand; filed verbatim
below. The authorised call was executed under it the same
evening; the run evidence is filed at
duenna/stage6-smoke-run-2026-11-17/ (SUPERVISOR-LESS).

APPROVED

Rev 03 @ 0f54b998 is approved for exactly one supervisor-less Stage 6 smoke call.

I retrieved Rev 03 and compared it with Rev 02. The correction is confined to the stated invocation-contract clarification. It accurately describes the harness's execution order:

Expected run ID read at startup.

Driver executes T04.

Run-ID assertion occurs after driver.run(SUBSET) returns.

The assertion is a post-execution consistency check, not an execution gate.

Run-record ID is independently checked during adjudication.

One-call guarantee rests on T04's tree shape and the smoke configuration.

No harness change is required.

Authorisation remains strictly bounded:

One live call, T04 only.

Smoke config SHA-256: ebb83d772a69da867721990917fef2326516fe71ad075b5693bc15e6e2b4f9ed.

max_attempts=1, max_tokens=4355.

Production endpoint only.

Maximum total: 5,000 tokens.

No retry, paid substitution, or battery call.

All evidence and the run must be labelled SUPERVISOR-LESS.

Complete record, adapter captures, usage evidence, run summary and firing log to be filed for my adjudication.

The smoke is authorised, not yet passed. I will judge the result against the existing pass bar: full harness traversal and a complete, well-formed record. The battery remains unauthorised.

Remmy may now execute the single call under Rev 03.

⟦ALEX-FINAL⟧
