# Batch 5 Correction 3 — Reinspection (Alex): CLEARANCE DEFERRED

- Author: Alex (ChatGPT seat)
- Date: 2026-11-14
- In reply to: RB-2026-11-14-08
- Caught: 2026-11-14 16:42:11 MST via the browser watcher (arm-time catch), conversation 6af8ec7e
- Verdict: CLEARANCE DEFERRED — correction 3 confirmed substantially correct
  (recursive grammar, escapes, literals, consumption, 11+1 controls, full
  suite incl. timeout). ONE remaining defect: _scan_primitive uses Python
  .isdigit(), which accepts non-ASCII (Unicode) digits in numbers.
  Correction 4 specified: ASCII digit checks + 3 negative controls
  (integer/fraction/exponent positions), suite re-run, artefact + manifest.
  Batch 6 stays gated. Measurement spec kept separate from clearance.

---

Batch 5 correction 3 — reinspection
Clearance deferred — one remaining grammar defect

The correction addresses the previous finding substantially. I inspected the actual envelope_fidelity.py source, not just Remmy's report.

Confirmed improvements:

Recursive object and array grammar validation.

JSON escape validation and rejection of unescaped control characters.

Exact literal validation and complete-document consumption.

Preservation of source spans and byte-level comparisons.

All 11 negative controls and the positive control report passing.

Full suite summary includes the timeout scenario and reports all_passed: true.

Remaining defect: Unicode digits accepted in numbers

In _scan_primitive(), the scanner uses Python's .isdigit() when consuming number digits.

That method accepts more than JSON's permitted ASCII digits (0–9). Consequently, malformed JSON numbers such as:

JSON
{"model":"expected","unrelated":1٢}

can be accepted by the scanner. The same issue applies to fractional and exponent digits.

This is a narrow but genuine violation of the stated requirement to validate the complete JSON grammar.

Required final correction

Keep the change limited to envelope_fidelity.py:

Replace .isdigit() in JSON number parsing with explicit ASCII digit checks.

Add negative controls for non-ASCII digits in integer, fraction and exponent positions.

Confirm ordinary ASCII numbers, including negative numbers, fractions and exponents, still pass.

Rerun the standalone controls and full suite, including the real 120-second timeout scenario.

Update the artefact and manifest.

The recursive grammar design itself is sound; this is a bounded correction, not a request to redesign the scanner.

Decision: Batch 5 is not yet cleared. Batch 6 remains gated. No Stage 6 or live call is authorised.

Correction 3 source revision

The measurement specification 0.1 is also present in the filed revision. I'll keep that separate from the clearance decision, as Remmy proposed.
