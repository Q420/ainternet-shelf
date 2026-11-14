# Batch 5 Checkpoint — Correction 4 (ASCII Digits in Numbers)

Date: 2026-11-14
Filed by: Remmy (implementation)
Authority: Alex's Batch 5 correction-3 reinspection (reply to
RB-2026-11-14-08) — CLEARANCE DEFERRED, one remaining grammar
defect, correction specified exactly.

This filing supersedes the correction-3 bundle @ 873935a8 for
reinspection purposes. The original Batch 5 checkpoint
@ dde40a23 and corrections 1 (@ 2146563b), 2 (@ d6bbebee)
and 3 (@ 873935a8) remain untouched as history.

## 1. The finding

Alex confirmed correction 3 substantially: recursive grammar
validation, escape validation, exact literals, complete
consumption, preserved source spans, all controls passing,
full suite including the timeout scenario. One defect
remained: `_scan_primitive()` consumed number digits with
Python's `str.isdigit()`, which accepts non-ASCII digits
(e.g. Arabic-Indic U+0662) that JSON's number grammar does
not permit — in integer, fraction and exponent positions.

## 2. The fix (envelope_fidelity.py only)

All five `str.isdigit()` uses in number scanning replaced
with an explicit ASCII check (`"0" <= c <= "9"`). Nothing
else changed: the recursive grammar design Alex called
sound stands as filed in correction 3, and test_batch5.py
is byte-identical to the correction-3 filing.

## 3. New negative controls (now 14)

Three added per Alex's specification, each in an added
non-envelope member, each passing only when the verifier
rejects its fixture:

- **non_ascii_digit_integer** — `1` followed by U+0662.
- **non_ascii_digit_fraction** — `1.5` followed by U+0665.
- **non_ascii_digit_exponent** — `1e1` followed by U+0662.

Ordinary ASCII numbers — negatives, fractions, exponents —
remain accepted: the real captured request still verifies
and the correction-3 positive control still passes.

## 4. Verification [executed]

Standalone, before the suite: real capture verifies;
14/14 negative controls reject; Alex's Unicode-digit
example is rejected by the scanner itself
("invalid number token").

Full suite re-run WITH the timeout scenario
(`test_batch5.py --with-timeout`, the run of record):

- ok 16/16, retry-429 18/18, retry-500 18/18, fail-429 15/15,
  kwargs-400 15/15, notfound-404 14/14, mismatch 15/15,
  unparseable 15/15, redact-500 15/15, timeout 16/16 at the
  real pinned 120 s per-attempt timeout
- isolation PASS, redaction-sweep PASS
- c5-17 envelope fidelity: 10/10 scenarios, 14/14 negative
  controls, 1/1 positive controls
- ALL: PASS

## 5. Limitations (unchanged, carried from the checkpoint)

- Everything above ran against the transport double. No live
  provider call has been made or is authorised in Batch 5.
- The served-model question remains PINNED-LISTED /
  SERVED-UNVERIFIED; the helper path remains unexercised
  until Stage 6, by authority.
- Batch 6 remains gated on Alex's final Batch 5 clearance.
