# Batch 5 Checkpoint — Correction 3 (Scanner Full-Grammar Validation)

Date: 2026-11-14
Filed by: Remmy (implementation)
Authority: Alex's Batch 5 correction-2 reinspection (reply to
RB-2026-11-14-07) — CLEARANCE DEFERRED, one remaining scanner
defect, correction specified exactly.

This filing supersedes the correction-2 bundle @ d6bbebee for
reinspection purposes. The original Batch 5 checkpoint
@ dde40a23 and corrections 1 (@ 2146563b) and 2 (@ d6bbebee)
remain untouched as history.

## 1. The finding

Alex confirmed correction 2's delimiter stack and
complete-consumption fixes as correctly implemented, and found
one narrower defect in the same scanner: it did not
independently validate the complete JSON grammar. Primitive
tokens were accepted as opaque runs of non-delimiter
characters (his example: `{"model":"expected","unrelated":truue}`
passes the structural walk, and because the unrelated member
is never compared, verify_envelope could still report
success). String escapes were skipped without validation,
unescaped control characters were not rejected, and nested
object/array syntax was walked by delimiter matching rather
than grammar. His distinction: the scanner must reject
malformed content ANYWHERE in the request, not just in the
envelope fields it compares.

## 2. The fix (envelope_fidelity.py only)

The scanner is now a recursive, complete JSON grammar
validator; source-span extraction and the byte comparisons
are unchanged.

- **Strings.** Escape syntax validated: after a backslash,
  only `"\/bfnrt` or `u` followed by exactly four hex digits
  is accepted; unescaped control characters (below U+0020)
  are rejected.
- **Primitives.** Literal tokens must be exactly `true`,
  `false` or `null` followed by a delimiter; numbers must
  match `-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?`
  followed by a delimiter — so `truue`, `01`, `1e` and `1.`
  all fail closed.
- **Nested composites.** Objects and arrays are scanned
  recursively with full member grammar (key string, colon,
  value, comma) — trailing commas, missing colons and
  missing commas are rejected anywhere in the document.
  A nesting-depth cap (200) fails closed.
- The correction-2 delimiter/consumption behaviour is
  preserved: mismatched delimiters and trailing content are
  still rejected (by the grammar scanner and the finish
  check respectively). No other behaviour changed: adapter,
  transport double, PILOT-JCS, frozen configuration and the
  runner are unmodified.

## 3. New negative controls (now 11) + positive control

Three controls added per Alex's specification, each passing
only when the verifier rejects its fixture:

- **invalid_primitive_in_nonmember** — `truue` as the value
  of an added non-envelope member; rejected by the scanner's
  own grammar validation.
- **invalid_escape_in_nonmember** — a `\x` escape in an
  added non-envelope member's string; rejected.
- **malformed_nested_object_syntax** — the colon of the
  first nested pair inside chat_template_kwargs removed;
  rejected.

Positive confirmation, as requested: a synthetic document
with varied JSON whitespace, bracket characters inside
strings, valid escapes (`\t`, `\u0041`), an exponent number
and correctly nested composites is ACCEPTED
(valid_complex_document_accepted, recorded in the artefact).

## 4. Verification [executed]

Standalone, before the suite: the real captured request
still verifies; 11/11 negative controls reject; Alex's
`truue` example is rejected by the scanner itself
("invalid value token"); the valid complex document is
accepted.

Full suite re-run WITH the timeout scenario
(`test_batch5.py --with-timeout`, the run of record):

- ok 16/16, retry-429 18/18, retry-500 18/18, fail-429 15/15,
  kwargs-400 15/15, notfound-404 14/14, mismatch 15/15,
  unparseable 15/15, redact-500 15/15, timeout 16/16 at the
  real pinned 120 s per-attempt timeout
- isolation PASS, redaction-sweep PASS
- c5-17 envelope fidelity: 10/10 scenarios, 11/11 negative
  controls, 1/1 positive controls
- ALL: PASS

(An earlier unflagged run the same afternoon omitted the
timeout scenario by invocation error; it is not cited as
evidence for this filing.)

## 5. Limitations (unchanged, carried from the checkpoint)

- Everything above ran against the transport double. No live
  provider call has been made or is authorised in Batch 5.
- The served-model question remains PINNED-LISTED /
  SERVED-UNVERIFIED; the helper path remains unexercised
  until Stage 6, by authority.
- Batch 6 remains gated on Alex's final Batch 5 clearance.
