# Batch 0 checkpoint report — ADDENDUM (F-2), dated 2026-11-12

Addendum to `BATCH0-CHECKPOINT-REPORT.md`. The original report is unchanged.

**F-2 is now DISPOSITIONED — ACCEPTED WITH EXPLICIT LIMITATIONS.**

The full GET /v1/models response body, not preserved as a file at design time (the report's F-2 preservation gap), was recovered from an independently preserved source — the recorded stdout of the 2026-11-12 16:25 MST connector call in the main session transcript — as the complete 83-object response content in helper-stdout serialisation. Alex inspected the recovered artefact and provenance (shelf commit 41f3661b) and issued his technical disposition (pb-mwemg570); Ben adopted it 2026-11-12 22:56 MST.

Record: `freeze/F2-DISPOSITION-2026-11-12.md` (classification RECOVERED-DESIGN-TIME-RESPONSE — COMPLETE-JSON-CONTENT — HELPER-STDOUT-SERIALISATION; both digests; provenance; the serialisation-fidelity and timing limitations preserved in substance) and `freeze/PILOT-MANIFEST-01-REFREEZE-AMENDMENT-2026-11-12-CONTINUATION-F2.md` (B5 reconciliation, B4 update to the recomputed `adapter_config_sha256` 6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb, supersession register).

The acceptance does not establish wire-byte identity or a contemporaneous raw-response hash, and the Stage 6 fresh-capture requirement is unchanged.

**The overall Batch 0 checkpoint remains NOT PASSED.** F-1 (setuid precondition fails on this host) and F-3 (custody trees not establishable on this volume) are still outstanding, and the build remains stopped.
