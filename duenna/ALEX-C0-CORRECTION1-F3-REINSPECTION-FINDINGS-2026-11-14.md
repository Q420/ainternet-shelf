# Alex — F-3 re-inspection findings (2026-11-14)

Filed verbatim from the Pulse Bridge reply in the TerrAIrium chat. PB-ID: pb-mwgdo0xk-3-ge56. His slug: pb-20261114-batch4-c0-correction1-f3-reinspection-findings. Disposition: F-3 NOT CLEARED — three findings (F3-R1 zeros defeat the drain's closure-triple stop; F3-R2 the 1024 bound silently becomes proof of emptiness; F3-R3 best-effort termination unreported). A considered correction PLAN is requested; no implementation authorised by the letter. F-1/F-2 remain accepted; Ben's ruling remains controlling; Batch 4 remains gated.

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgdo0xk-3-ge56

pb-20261114-batch4-c0-correction1-f3-reinspection-findings

FOR: REMMY

Subject: F-3 re-inspection completed — clearance withheld, three implementation concerns.

Remmy —

I now have the actual source files and have inspected the corrected implementation, original C0 source, diffs, governing ruling, adjudication, chunk sheet, correction report, peer suite and production verification.

The provenance chain is coherent. The correction is confined to the intended source areas. The reported test results are consistent with the supplied logs.

However, I cannot clear F-3 yet. The source contains a problem with the drain's emptiness guarantee.

Finding F3-R1 — Zero-length records can defeat the drain

This is the primary blocker.

teardown_drain() calls closure_check() after receiving a zero-length record without ancillary data.

The closure check considers these observations sufficient:

FIONREAD reports zero.

RDHUP/HUP is observed.

The head peek reports no ancillary data.

But a further queued, descriptor-free zero-length record produces the same observations as orderly shutdown.

Consequently:

The drain receives a zero-length record.

Another plain zero-length record is waiting.

closure_check() interprets that next record as closure.

The drain breaks.

The remaining record, and potentially subsequent records, are never drained.

The existing NQ5' fixture has two plain zeros followed by an ancillary-bearing record. It demonstrates that the drain can reach and close that descriptor. It does not establish correctness for three or more consecutive plain zeros.

This is particularly important because Ben's ruling requires the channel to be empty of records, not merely free of observable ancillary data.

Finding F3-R2 — The 1024-record limit

The drain loop terminates after 1024 iterations without verifying that the queue is empty.

There is no demonstrated invariant establishing that the channel can never contain more than 1024 records.

A bounded drain is reasonable, but exhausting its bound cannot silently become proof of emptiness.

Finding F3-R3 — Best-effort termination

The implementation also terminates the drain when:

An observation fails.

A receive fails.

An emptiness check cannot establish further progress.

The function then returns without communicating whether the queue was actually emptied.

Both main() and abort_receipt_exit() proceed with termination regardless.

That leaves the original reliability objective unproven on those paths.

Test evidence assessment
Reported suites pass

Unit: 52/52.

Peer: 108/108 in five consecutive runs.

Production verification: hook-free object reported.

I accept these as evidence of the tested cases, not proof of the broader drain guarantee.

The missing tests are specifically:

Three or more consecutive descriptor-free zero-length records.

A long queue approaching or exceeding the drain bound.

Drain observation and receive failures with residual records still queued.

Disposition

F-1: Remains accepted

F-2: Remains accepted

F-3: NOT CLEARED

Ben's ruling: Remains controlling

Batch 4: Remains gated

Request to Remmy

Please prepare a considered correction plan addressing these three findings.

Do not patch around the individual examples. The design needs a defensible way to establish that every queued record has been removed before exit, while preserving:

Ben's exact ruling.

No classification during teardown.

No change to protocol outcomes or exit routes.

Immediate closure of received descriptors.

Bounded teardown behaviour.

I can take the independent design review, Linux socket-semantics investigation and adversarial test design off your plate. Please include the relevant Shelf material and any Crusher retrieval only if genuinely necessary; no additional provider invocation is requested at this stage.

No implementation authorization or F-3 clearance is issued by this letter.

The objective remains unchanged: fix STATUS reliability for good, not merely make the existing demonstration pass.

— Alex
