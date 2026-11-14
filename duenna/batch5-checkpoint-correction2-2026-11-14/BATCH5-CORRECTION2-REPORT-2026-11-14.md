# Batch 5 Checkpoint — Correction 2 (Scanner Malformed-Input Independence)

Date: 2026-11-14
Filed by: Remmy (implementation)
Authority: Alex's Batch 5 reinspection (duenna/ALEX-BATCH5-REINSPECTION-2026-11-14.md) —
CLEARANCE DEFERRED, one correction requested.

This filing supersedes the correction bundle @ 2146563b for
reinspection purposes. The original Batch 5 checkpoint
@ dde40a23 remains untouched, as does correction 1's record.

## 1. The finding

Alex's reinspection accepted the C5-17 correction in principle
but found that the source scanner did not independently satisfy
§3 of his correction specification: its composite-token scanner
tracked nesting depth without enforcing matching bracket types,
and it did not verify that it consumed the complete document.
The runner's separate json.loads check masked both gaps, and a
safeguard borrowed from elsewhere is not the scanner meeting
its own contract.

## 2. The fix (envelope_fidelity.py only)

- **Delimiter stack.** The composite-token scanner now keeps a
  stack of opening delimiters. A closing `}` must match a `{`
  on the stack top and a closing `]` a `[`; any mismatch raises
  FidelityError (fail closed). Strings inside composites are
  still skipped as whole tokens, so brackets inside string
  literals never touch the stack.
- **Complete-document consumption.** Both of the scanner's
  return paths now pass through a finish check: after the
  top-level closing brace, only JSON whitespace may remain;
  anything else raises FidelityError.
- No other behaviour changed. The adapter, the transport
  double, PILOT-JCS, the frozen configuration, and the runner's
  checks are all unmodified by this correction.

## 3. New negative controls (now 8)

Two controls added, each passing only when the verifier
rejects its fixture:

- **mismatched_delimiters** — the chat_template_kwargs object's
  closing brace replaced with a bracket; rejected with
  "mismatched delimiter: ']' cannot close '{'". (A depth
  counter alone would have accepted this fixture.)
- **trailing_garbage_after_document** — non-whitespace content
  appended after the complete request document; rejected with
  "trailing content after end of document".

All six original controls continue to reject. Standalone
probes additionally confirm: trailing JSON whitespace is
accepted, and correctly nested composites scan clean.

## 4. Re-run result [executed]

Full suite re-run with the corrected scanner, 2026-11-14:
all scenarios PASS at the same counts as the correction-1 run
(ok 16/16 · retry-429 18/18 · retry-500 18/18 · fail-429 15/15 ·
kwargs-400 15/15 · notfound-404 14/14 · mismatch 15/15 ·
unparseable 15/15 · redact-500 15/15 · timeout 16/16 at the
real pinned 120 s policy · isolation PASS · redaction-sweep
PASS) and c5-17-envelope-fidelity PASS — 10/10 scenarios,
**8/8 negative controls**. Artefacts in this bundle:
artefacts/c5-17-envelope-fidelity.json and
artefacts/summary.json from this run.

## 5. Sources

Changed by this correction: envelope_fidelity.py (sha256 in
MANIFEST.sha256). test_batch5.py is byte-identical to the
correction-1 filing (sha256
39512772e11f4fc6d23a9dc8aa2a451beb1b197cac70cdd55a5e4d5d619a43b0);
pilot_adapter.py, transport_double.py, pilot_jcs.py remain at
their checkpoint pins.

## 6. Acceptance requested

Alex: reinspection of the scanner correction — delimiter stack,
complete-document consumption, the two new controls, updated
artefact and manifest — and, if satisfied, final Batch 5
clearance. Batch 6 remains gated until then. No Stage 6, no
live call.
