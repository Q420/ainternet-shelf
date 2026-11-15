# Watchdog Stage 3 — review (detector + judge, offline first), 7e451dec

Reviewed: watchdog/watchdog_detector.py, test_watchdog_detector.py,
WATCHDOG-STAGE3-BUILD-NOTE.md. Basis: contract v1.1 as amended by v1.2.

## Verdict: CONDITIONAL. Three rulings, four must-fix items.

## Rulings on the build note's flagged decisions

**D1 — Keyword gate home: the registry, not a detector-local table.**
A gate that decides which turns can ever be judged is part of the job's
precondition. A detector-local KEYWORDS_BY_JOB can change without the
registry's immutability pin noticing, which breaks §2. Ruling: the gate
belongs in the job record as `gate_terms`, set before activation and pinned
with the record. That is a contract amendment, v1.3. Until v1.3 lands, a job
with no pinned gate is judged on every seat turn. That costs judge calls,
not correctness, and the detector must log it.

**D2 — Gated-out turns: RESET, not skip.** The detector's `continue` on a
keyword miss lets two YES turns with a gated-out turn between them count as
consecutive. Contract v1.1 §6 and the amendment ruling 1a say a non-qualifying
completed assistant turn resets the count. §13 ("no match → judge never called")
is still honoured: the reset needs no judge call. Ruling: a gated-out completed
seat turn resets the streak, recorded as `gate_reset`, not as a judged NO.
That needs an explicit reset method in the ledger, reviewed with the fix.

**D5 — Credentials: the connector's secure route governs.** §11 says
"environment at runtime"; the NVIDIA connector doc says never put a key in an
environment variable. An env-first path is exactly what the connector forbids,
so it is removed. Ruling: credentials only through the connector's secure route.
§11 is amended to say so (owner confirms the text). The hard-coded
/opt/muse helper path is a dependency to document, not a silent import.

**D4, D7, D8 — accepted.** ID-less keys are fine for the corpus, because the
live pool now captures ids. pair_unknown is a sound defensive branch. Buffer
size 25 is a default, and the owner sets it.

**D6 — stale window: must be in the detector (see M-S3-4).**

## Must fix

**M-S3-1.** Gated-out turns must reset the streak (D2). Fixture:
YES, gated-out, YES does not fire; the reset appears as gate_reset, not NO.

**M-S3-2.** The gate must be pinned with the job (D1). Until v1.3, a job's
gate must not be editable while active. Fixture: a changed gate on an active
job is refused, or no gate is applied and that is logged.

**M-S3-3.** Remove the env-first credential path (D5). Fixture: an
environment variable present does not change the route.

**M-S3-4.** Stale window (§9) must hold the streak in the detector. §9 says
a stale window raises an operational alert and HOLDS the streak, and the
detector is the only judge caller, so it has to enforce this. Watermark
source: the pool-state per-seat watermark. Fixture: a stale watermark judges
nothing, holds the streak, and alerts.

## Should fix (before live)

**S-S3-5.** turn_index is derived by the reader, but §1 says the pool assigns
it at capture. A derived index shifts if a turn is missing from the file. Offline,
keep the derivation as provisional, and have the reader refuse a non-contiguous
file. Before live, the pool must write turn_index.

## Requested
Resubmit with M-S3-1 to M-S3-4 fixed and fixtured, S-S3-5 at least
provisional with the refusal in place, and the v1.3 and §11 text drafted for
the owner. Then Stage 3 is accepted offline.
