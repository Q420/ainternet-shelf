# DATED AMENDMENT — RUN IDENTIFIER GRAMMAR (A-1)

Project: Nemotron governed-subject pilot
Applies to: Stage 5 Build Specification 13, §3.5; Harness Design 03, §2.1; Batch 0 launcher behaviour-and-interface freeze, §2 and §7
Amendment purpose: Resolve A-1 / residual R-1 by defining the complete run-identifier grammar and the launcher's exact validation requirements.
Status: **ADOPTED** — Ben's approval, 2026-11-12 23:10 MST ("if that format works it works let's go"), given after the plain-words explanation of the four reserved decisions, which are adopted as proposed in §8.
Drafted by: Alex (pb-mwemx5pn), under Ben's commission of 2026-11-12 22:58 MST. Incorporated by Remmy as a dated addition; the original launcher-interface freeze (`freeze/launcher-interface-freeze.md`, sha256 6bb9ae8047b9fd62ba47dc64d18af3579464807ae9fc6c1a03467a22f615d1f5) remains byte-identical.

## 1. Governing identifier

The run identifier has this structure:

`<battery-id>-<UTC-date>-<counter>`

| Field | Required representation |
|---|---|
| battery-id | Case-preserving ASCII alphanumeric groups separated by single hyphens |
| UTC-date | Exactly eight decimal digits, YYYYMMDD |
| counter | Exactly three decimal digits (see §4 and §8) |

The existing example `NP01-20261120-001` is consistent with this representation.

The identifier is an opaque identity once issued. No component may silently normalise, change case, reformat, or reconstruct it differently.

## 2. Battery-ID alphabet and structure

Battery-ID grammar:

```
[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*
```

Requirements:

- ASCII letters A–Z and a–z are permitted.
- ASCII digits 0–9 are permitted.
- A single hyphen may separate non-empty alphanumeric groups.
- The identifier must begin and end with an alphanumeric character.
- Consecutive hyphens are forbidden.
- Leading and trailing hyphens are forbidden.
- Whitespace, underscores, periods, slashes, Unicode characters and all other punctuation are forbidden.
- Case is preserved. `NP01` and `np01` are different identifiers; no case-folding is permitted.

Maximum battery-ID length: **64 ASCII bytes** (adopted decision A1-BEN-01).

## 3. UTC date

The date field is exactly `YYYYMMDD`: YYYY a four-digit Gregorian year; MM a two-digit month, 01 through 12; DD a two-digit day, valid for that month and year. The date represents the UTC calendar date assigned to the run. No timezone suffix, separators, timestamp, time-of-day or offset is permitted. The compact form matches the existing Harness Design example and gives the launcher a fixed-width date field. A date that is syntactically eight digits but is not a real Gregorian calendar date must be rejected (for example, 20260231 is invalid). The date is not interpreted using local time. The issuing process must use UTC.

## 4. Counter

Representation: exactly three ASCII decimal digits. Valid range: **001 through 999** (adopted decision A1-BEN-02).

- The counter is zero-padded to exactly three digits; leading zeroes are mandatory where needed to maintain the fixed width (adopted decision A1-BEN-03).
- `000` is invalid and reserved.
- The counter is per battery ID per UTC date.
- A counter value must not be reused for the same battery ID and UTC date.
- Counter exhaustion at 999 stops further issuance for that battery/date. The counter must not wrap, expand silently, or reuse an earlier value.

## 5. Maximum identifier length

- Battery ID: maximum 64 ASCII bytes.
- UTC date: exactly 8 ASCII bytes.
- Counter: exactly 3 ASCII bytes.
- Separators: exactly 2 ASCII hyphens.
- Complete run identifier: maximum 77 ASCII bytes (64 + 1 + 8 + 1 + 3). Minimum complete length is 14 bytes.

The launcher must reject an identifier longer than 77 bytes before attempting to launch the harness. The limit is measured in bytes, not Unicode characters. Since every permitted character is ASCII, byte count and character count are equal for valid identifiers.

## 6. Exact validation pattern

The launcher implementation is C. The exact POSIX Extended Regular Expression (ERE) for the complete identifier's structural form:

```
^([A-Za-z0-9]+(-[A-Za-z0-9]+)*)-([0-9]{8})-([0-9]{3})$
```

The expression is anchored at both ends. Capture groups: (1) complete battery ID; (2) internal battery-ID separator group; (3) eight-digit UTC date; (4) three-digit counter.

The implementation must additionally enforce: complete identifier length between 14 and 77 ASCII bytes; battery-ID length between 1 and 64 ASCII bytes; date is a real Gregorian calendar date; counter is not 000; no embedded NUL, whitespace, newline or other trailing data is accepted.

The regular expression establishes structural validity; it does not alone establish calendar validity, counter validity or the separate length limits. The implementation must use the POSIX ERE form above, or demonstrate byte-for-byte equivalent validation semantics. It must not substitute a looser expression or a different grammar.

## 7. Anchored parsing and right-side field extraction

Because battery IDs may themselves contain hyphens, the launcher must not parse the identifier by splitting on every hyphen or by assuming the battery ID contains no hyphens. Parsing is anchored from the right:

1. Confirm the complete input length is within the approved bounds.
2. Read the final three bytes as the counter field.
3. Require the preceding byte to be the separator `-`.
4. Read the preceding eight bytes as the UTC date field.
5. Require the preceding byte to be the separator `-`.
6. Treat all remaining bytes as the battery ID.
7. Validate the battery ID independently against the battery-ID grammar.
8. Validate the date and counter semantically.
9. Require the complete identifier to match the anchored expression in §6.

No searching for an earlier separator is permitted to determine the date or counter. Their positions are fixed from the right edge.

Example: `PULSE-RESEARCH-20261120-001` parses as battery ID `PULSE-RESEARCH`, UTC date `20261120`, counter `001`. The battery ID's internal hyphen remains part of the battery ID.

Any failure, ambiguity, truncation, extra byte or unrecognised character causes rejection. The launcher exits non-zero and spawns nothing.

## 8. Decisions adopted by Ben (2026-11-12)

- **A1-BEN-01 — Battery-ID maximum length: 64 ASCII bytes** (complete identifier maximum 77 bytes). Adopted as proposed.
- **A1-BEN-02 — Counter width and range: three digits, 001–999.** Adopted as proposed. Maximum 999 runs per battery ID per UTC date; exhaustion stops issuance.
- **A1-BEN-03 — Leading-zero and zero-value policy: fixed-width zero-padding; 000 invalid; first issued counter is 001.** Adopted as proposed.
- **A1-BEN-04 — Identifier allocation authority:** the designated run-identifier issuer must reserve each identifier uniquely before launch. Concurrent requests must not receive the same battery/date/counter tuple. Failed or abandoned reservations are not silently recycled. This amendment does not independently grant the launcher, harness, model or another component new authority to issue identifiers. Adopted as proposed.

The date representation YYYYMMDD is adopted, directly consistent with the existing Harness Design §2.1 example.

## 9. Launcher behaviour and failure handling

The launcher accepts exactly the existing fixed invocation shape, with the run identifier as its sole variable argument. It must: validate the complete identifier before forking or performing the privileged launch sequence; reject a malformed identifier without spawning any process; reject missing or additional arguments; reject an invalid date, invalid counter, invalid battery ID or length violation; pass the validated identifier unchanged to the harness in its frozen argument position; never normalise or rewrite the identifier; never invoke a shell or introduce a configurable executable path; record the rejection in the run log where the existing interface permits, without weakening the rule that the privileged window performs no file writes.

This amendment changes only the concrete run-identifier contract. It does not alter the launcher's single fixed operation, privilege transitions, gate protocol, descriptor rules, capability checks, identity continuity requirements or custody boundaries.

## 10. Relationship to the existing freeze

This amendment is a dated addition to `freeze/launcher-interface-freeze.md` (frozen interface SHA-256: 6bb9ae8047b9fd62ba47dc64d18af3579464807ae9fc6c1a03467a22f615d1f5). The original launcher-interface freeze remains byte-identical. Its §7 residual R-1 is discharged by this adoption and incorporation, and by the shelving and pinning of this addition. The amendment's exact validation expression and limits are carried into the Batch 4 implementation requirements.

The original checkpoint report and the historical record of A-1 remain preserved. This dated amendment itself states that R-1 is resolved; the historical report is not rewritten.

## 11. Scope and effect

This amendment does not authorise Batch 1 or any later batch; does not clear F-1 or F-3; does not authorise Stage 5 build continuation; does not authorise a model call or Stage 6 execution; does not alter the system-only index rule; does not authorise any agent or model to modify the index. It took effect on Ben's express approval, recorded in the header. Batch 4 remains blocked on the build's other gates (the environment stop), not on A-1.
