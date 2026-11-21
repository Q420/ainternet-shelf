# STEP 3 — CLAUDE EVIDENCE REPAIRS: EVIDENCE (2026-11-16)

Correction round, step 3 of 3 (order confirmed in Alex's resume
ruling, 2026-11-15). Repairs Claude's formal §7 step 6 inspection
defects 1 and 2; his condition 4 (the re-derivation's scope) is
discharged by the statement in §3 below and in REPRODUCE.md.
Defect 3 (pin authority) was closed by Alex's RB-50 ruling, not
by this step.

Alex's acceptance for this step: "An independent reproduction
from the Shelf, with identifiable inputs, outputs and results.
A claim that something is reproducible is not reproduction
evidence." The reproduction in §2 is that evidence.

## 1. Checkpoint manifest regenerated (defect 1)

The shelved manifest (duenna/batch6-checkpoint-2026-11-15/
MANIFEST.sha256) listed 156 entries, six of them
__pycache__/*.pyc files absent from the bundle — the manifest
failed verification with 13 failures.

Repair: the manifest was regenerated over the bundle's actual
contents (150 files). The regenerated manifest is byte-identical
to the old manifest minus the six phantom entries — no hash of
any real file changed. `sha256sum -c` over the bundle now passes
150/150 with zero failures.

- Regenerated manifest sha256:
  d12b3545e279d7bb7b9a8c73bac0a6ffacdb3a1f30d3c6482d85f882895262d0
- Pushed at commit 9f4c25884201f8734da76bf7661af4c1d852b296;
  read back from the shelf and verified identical.
- No bundle file was added, removed or altered; only the
  manifest itself was replaced.

## 2. Reproducibility from the shelf (defect 2)

Package: duenna/batch6-correction-repro-2026-11-16/
(pushed at 43f3c8fceaf6f3406de8ce4e2ead090922a74911, with one
fix at 3d9099a33e7a131fef0dc34c020b2116b27b85d8, disclosed below).

- test_g4corr.py and reexamine_g4corr.py: the correction round's
  own scripts with ONLY the path-resolution block adapted from
  the builder's home directory to the shelf layout, plus one
  added line in reexamine (create the out/ directory before
  writing — the original wrote into a pre-existing directory).
  The complete diff is filed in the package as
  ADAPTATION-DIFF.txt. The scripts' logic is untouched.
- REPRODUCE.md: inputs, dependencies (Python 3.12, standard
  library only, no network), exact commands, expected results.
- Identifiable inputs, all read from the shelf bundles: the
  preserved run and commitments and stack from the correction
  bundle; the corrected examiner (sha256 564925230a70c56d…)
  and PILOT-PIN-AUTHORITY-02 and the freeze manifest (file
  sha256 5748287167d8…) from the checkpoint bundle; the stack
  manifest (file sha256 f8955b964b518…) from the correction
  evidence folder; pilot_jcs verified at its pin (8a131cfce…).

The independent reproduction, run 2026-11-16: a fresh directory
was populated with 63 files pulled from the shelf alone (the
repro package; the correction bundle's run/, commitments/ and
stack/; the stack manifest; the three checkpoint inputs), at
shelf head 3d9099a3…. The documented commands were run there
with no reference to the builder's working directories:

- `python3 test_g4corr.py` — exit 0. Output is byte-identical
  to the recorded test-output-02.txt: all ten named checks
  [PASS], "== test_g4corr: 10/10 PASS".
- `python3 reexamine_g4corr.py` — exit 0. The produced
  g4corr-examination-02.json is byte-identical to the recorded
  examination (both sha256
  28034f39a60e01a5624b936c34d339e9c55452854d3ea565871c77812b74d613):
  step0 PASS over 486 events; step2 pins_checked 11; step3
  reexecuted 89, zero divergences; step5 13 captures, 13 links;
  step6 RUN_CLOSED.

Disclosure: the first reproduction attempt of reexamine failed
at the final write because the fresh tree had no out/
directory. The examination itself had completed; the failure
was the missing directory. The one-line mkdir fix above was
applied, the package re-pushed, and the run repeated clean.
The suite passed on the first attempt.

## 3. Scope statement (Claude's condition 4)

The re-examination's Step 3 replays all 89 tool invocations
with zero divergences and re-evaluates 3 of the run's verify
checks; the remaining 47 checks are carried as unexecuted.
That is the examiner's design, and it is narrower than a full
independent re-derivation of every check. The claim is stated
at this width in REPRODUCE.md and here, and nowhere broader.

## 4. Boundaries kept

No preserved artefact was modified: the correction bundle's
files (including the unadapted suites/test_g4corr.py), the run
record, the commitments and the stack are untouched; the
checkpoint bundle changed only in its MANIFEST.sha256 (§1).
The original scripts on the builder's machine are untouched;
the adaptation exists only in the repro package, with its diff.
