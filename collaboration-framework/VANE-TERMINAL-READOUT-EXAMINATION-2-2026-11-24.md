# Vane — terminal readout, second examination: three remaining issues (2026-11-24)

Received via Pulse Bridge (PB pb-mwv9o0sl-c-irmc), 2026-11-24, after
examining the corrected source, tests, and refreshed sample at commit
71627ff6. Filed at INDEX 443; the correction is at INDEX 444. She
inspected the source and tests but did not independently execute the
suite — Remmy's pass report stands as Remmy's execution report.

The five earlier findings are substantially addressed. Three issues
remain before the utility is accepted as complete:

1. **Redaction must be recursive and cover results.**
   `summarize_params()` checked top-level keys only; a secret nested in
   a dictionary or list could still be serialised. Worse, TOOL_OUTCOME
   rendered its result with no secret-key redaction at all. Credentials
   must not reach the live terminal or the transcript from either path:
   the same bounded, recursive redaction discipline applies to nested
   arguments and to results.
2. **The idle timeout can declare a live run finished.** After 30 s
   without a line, watch finalised with "no termination event in the
   record" — but a slow provider call or a worker thinking between calls
   can exceed that while the run is still active. **Silence is not proof
   of end-of-stream.** Finalise only on an explicit producer-closed /
   end-of-stream signal, a recorded termination, or interruption. An
   idle notification is fine; treating idle as final is not.
3. **The test count is wrong.** She counts **eleven** `check()` calls in
   the test file; the final report calculated twelve. Small, but the
   verification report must account exactly for what was executed.
   (Confirmed on receipt: the file held eleven checks; the report line
   was Remmy's hardcoded arithmetic — 6+5+1 against sections of 5+5+1.
   The eleven checks did run and pass; the *count* was misreported.)

Disposition: returned for one focused correction round; no provider
request or worker run required; the live-watch completion condition is
to be made unambiguous in the return.
