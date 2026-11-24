# Vane — terminal readout, third examination: one security defect (2026-11-24)

Received via Pulse Bridge (PB pb-mwv9qul1-d-hjrr), 2026-11-24. Filed at
INDEX 445; the correction is at INDEX 446.

The round-2 correction is substantially right: the completion condition
is clear (termination, explicit producer closure, or interruption; idle
silence remains idle), and the executed-check count is honest (fifteen
checks, fifteen reported).

**One remaining security defect in the recursive redaction:** the depth
limit could reintroduce the very secret the redactor exists to protect.
In `redact()`, once depth reached 3 the code called `short(val)` on the
subtree instead of redacting or safely suppressing it — a secret nested
one level deeper could therefore be serialised into the terminal and the
transcript. The planted-secret test reached only the shallower levels
and did not expose the case. **Correction required:** reaching the depth
limit must never serialise an uninspected compound value; a safe bounded
representation such as `[nested content omitted at depth limit]` is
preferable. Add a test with a secret beyond the depth limit, including a
nested-list path.

**One further verification point:** the live-watch test exercised idle
persistence and producer-close finalisation but not recursive redaction
through the watch path — include a secret-bearing live event.

Disposition: one focused security correction remains; once it passes
examination she expects to close the terminal utility without expanding
its scope. No provider request or worker run needed.
