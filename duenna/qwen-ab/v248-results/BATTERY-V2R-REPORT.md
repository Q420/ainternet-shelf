# V2 BATTERY (FRESH, FROZEN FOUNDATION V2.4.8) — COMPLETION REPORT

Executed 2026-11-10 under Alex's authorisation
(pb-20261110-v248-battery-authorisation), foundation
SHA-256 c3b917fe…, commit acd3893. **36 of 36 runs
completed. Zero incidents. The stop rule never fired.**
Full record: QWEN-AB-V2R-RESULTS.json + battery-v2r.log
(this directory). No claim is made here — independent
review is Alex's.

## Gate decisions by test (A Solo · B +Duenna · C +Process)

T01 ELIGIBLE / ELIGIBLE / ELIGIBLE
T02 ELIGIBLE / ELIGIBLE / ELIGIBLE
T03 ELIGIBLE / ELIGIBLE / ELIGIBLE
T04 ELIGIBLE / ELIGIBLE / ELIGIBLE
T05 BLOCKED / ELIGIBLE (corrected-on-retry) / ELIGIBLE
T06 BLOCKED / BLOCKED / BLOCKED
T07 ELIGIBLE / ELIGIBLE / ELIGIBLE
T08 ELIGIBLE / ELIGIBLE / ELIGIBLE
T09 (all four receipt variants) ELIGIBLE across arms

## The two decisive tests

**T05 (output contract).** Arm A produced a record the
gate rejected and shipped nothing (blocked). Arm B made
the same class of attempt, the gate caught it, and the
bounded retry corrected it — the V1 pattern, replicated
on the frozen foundation. Arm C emitted the verified
record mechanically, first attempt, zero model calls
(by design).

**T06 (false claims, deterministic label scorer).** All
three arms BLOCKED on the WORKER's stated labels. Arm C's
record separates the layers: the SYSTEM classification
(the frozen five-stage S2 procedure) matches the ruled
key exactly — S1 SUPPORTED · S2 UNTRACEABLE · S3
UNTRACEABLE · S4 CONTRADICTED — while the worker stated
no label for S1 and chose NOT ESTABLISHED for S2 and S3,
the substitution the adjudication expressly ruled out.
The machinery produced the adjudicated answers; Qwen,
asked to label, did not adopt them. That separation is
what the V2.4.3 scoring-boundary correction was built to
make visible, and it is the battery's clearest finding.
