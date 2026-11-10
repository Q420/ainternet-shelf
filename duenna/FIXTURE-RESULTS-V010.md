# D3 v0.10 — FIXTURE RESULTS (revision build)

**Harness:** fixtures-v010/harness.py v2.1, SHA-256 efe69df64a964bf5fb45cc2234c539908e3b7e600cd209de5867ccf0ad78ee6c
**Run:** `python3 harness.py` from fixtures-v010/ (Python 3.12.3)
**Results file:** results.json, SHA-256 ad4dc13754c543520dea2b93c80165df85595a18e873438f2d600779e355ce38
**Outcome: 31 fixtures executed, 31 PASS, 0 FAIL**

Authorised by Alex's adjudication of the v0.9 verification gate (pb-mwauqmco,
2026-11-10, ⟦ALEX-FINAL⟧), which confirmed FAIL on R47, R60 and R65 and opened
a revision step limited to those three findings. The complete suite was
re-run — every carried-over fixture plus the three repaired ones — not only the
repaired tests. The v0.9 harness (v2.0) and its results are preserved untouched
in fixtures-v09/; the v0.9 specification is preserved untouched (SHA-256
ac2a2484dd4e170948f868d4ac1680221fbcd3a905c75d1d2da21f4d0d0485dc); the v0.8
specification is immutable (SHA-256
3e053efc97d876d50f649eb0b4c8c740ab6085314aa54f9132fdf33e243d97d4).

TEST BOUNDARY: these fixtures exercise small reference procedures written from
the specification text. They validate the mechanical coherence of the SPECIFIED
RULES as implemented in these reference procedures. No separate production
evaluator exists in this stage, and nothing here certifies one. A harness run
is an implementer-reported execution result, not independent verification —
this package returns for independent examination.

## What changed for the three findings

- **R47** — the fold now EXAMINES trigger-carried content: it reads each
  entry's content_predicates and records them in its result as
  examined_trigger_content; admission remains the only path into the running
  set. FX-R47b asserts the examination record itself (qualifying content read
  and establishing nothing), a mutation control (the same trigger with its
  content removed — the examination record empties and the outcome is
  unchanged), and the channel control (the same predicates as admitted
  determinations satisfy). In the v0.9 form this fixture passed vacuously:
  the fold never read the content the case claimed to test.
- **R60** — the CheckerContract now EXECUTES its validation procedure
  (_preservation_check recomputes the payload digest against the digest
  pinned in the contract) instead of recording a procedure name, and every
  verdict carries REQ-I-2's full reproducibility trio: declared version,
  implementation hash (SHA-256 of the procedure's own source), and input
  artefact identity. A new validate_verdict() rejects any verdict missing or
  mismatching an element; FX-R60b exercises acceptance of a genuine verdict
  and rejection of a forged procedure stamp, a missing implementation hash,
  an altered implementation hash, a missing input identity, and a missing
  version.
- **R65** — the validator now establishes completeness as well as
  correctness: it requires exactly the five required references (none
  missing, none unexpected) and cross-checks components_present against the
  required set before comparing values. FX-R65 exercises, on top of the five
  original mismatch cases, the deletion of each of the five references in
  turn, an empty references dict, an unexpected extra reference, and a
  components_present that disagrees with the required set. In the v0.9 form
  a report with an empty references dict passed this validator.

## Sabotage evidence (repairs verified to bite)

Each repair was additionally tested by disabling its mechanism in a scratch
copy of the harness and re-running the suite (implementer-run, 2026-11-10;
scratch copies discarded after the runs):

- **M1** — fold's trigger-content examination removed: **FX-R47b FAILS**
  (examination record empty; outcome assertions still hold). 30 PASS / 1 FAIL.
- **M2** — verdict validation's implementation-hash checks disabled:
  **FX-R60b FAILS** (missing and altered implementation hashes are ACCEPTED).
  30 PASS / 1 FAIL.
- **M3** — R65 validator's missing-reference check disabled: **FX-R65 FAILS**
  (all five deletion cases and the empty-references case return PASS — the
  original v0.9 defect, reproduced under the repaired test). 30 PASS / 1 FAIL.

In each variant exactly the repaired fixture failed and no other — the
repaired tests measure their mechanisms, not merely their outcomes.
