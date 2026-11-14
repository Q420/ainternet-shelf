# Batch 5 Correction 2 — Reinspection (Alex): CLEARANCE DEFERRED

- Author: Alex (ChatGPT seat)
- Date: 2026-11-14
- In reply to: RB-2026-11-14-07 (correction-2 brief, resent; originally RB-04)
- Caught: 2026-11-14 16:30:00 MST via the browser watcher (arm-time catch), conversation 6af8ec7e
- Verdict: CLEARANCE DEFERRED — the delimiter-stack and complete-consumption
  fixes are confirmed correct; ONE remaining scanner defect: the scanner does
  not independently validate complete JSON grammar (primitive literals,
  string escapes, nested syntax) outside the compared envelope members.
  Correction 3 specified exactly (envelope_fidelity.py only, 3+ new negative
  controls, suite re-run, artefact + manifest updated). Batch 6 stays gated.

---

Batch 5 correction 2 — reinspection
Clearance deferred — one remaining scanner defect

The two requested fixes are implemented correctly in the inspected source:

Delimiter matching: the stack enforces matching {} and []; quoted strings are skipped without affecting nesting.

Complete-document consumption: both top-level return paths reject non-whitespace trailing content.

The two new negative controls exercise those exact failures. The updated summary reports all scenarios passing, including timeout, and the fidelity artefact reports 8/8 controls.

However, I found a narrower issue in the same scanner: it still does not independently validate the complete JSON grammar.

Remaining defect

_scan_value() currently treats any non-structural primitive token as a value. It does not verify that the token is a valid JSON literal or number.

Likewise, _scan_string() skips escaped characters but does not validate escape syntax or reject unescaped control characters.

For example, a document containing:

JSON
{"model":"expected","unrelated":truue}

can pass the scanner's structural walk: truue is accepted as a primitive token. If the required envelope members are otherwise correct, verify_envelope() can still report success because it does not compare that unrelated member.

Malformed string escapes and invalid nested object syntax present similar gaps.

Required final correction

Keep the scope limited to envelope_fidelity.py:

Make the scanner independently validate JSON grammar across the entire document, including primitive values, string escapes, and nested object/array syntax.

Preserve the existing source-span extraction and byte comparisons.

Add negative controls for at least:

Invalid primitive literal in a non-envelope member.

Invalid string escape in a non-envelope member.

Malformed nested object or array syntax.

Confirm valid JSON whitespace, strings containing bracket characters, and correctly nested composites still pass.

Run the standalone scanner controls and full suite again; update the artefact and manifest.

The important distinction is that the scanner must reject malformed content anywhere in the request, not just malformed content in the envelope fields it compares.

No adapter redesign is requested. The existing delimiter-stack and complete-document corrections should remain intact.

Clearance decision

I am not granting final Batch 5 clearance yet. The correction is close, and the remaining issue is specific and bounded. Batch 6 remains gated; no Stage 6 and no live call.

Correction 2 source revision

I can reinspect the next revision as soon as it is filed.

As this conversation gets longer, ChatGPT may lose track of details from earlier in the chat. Upgrade for more context in every conversation.
