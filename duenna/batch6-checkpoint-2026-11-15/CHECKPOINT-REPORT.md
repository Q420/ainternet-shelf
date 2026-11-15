# BATCH 6 CHECKPOINT REPORT — Stage 5 evidence pack & inspection handoff

Builder: Remmy. Governing sheet: BATCH6-CHUNK-SHEET-APPROVED-
2026-11-14 (Alex disposition ALEX-C6-0A-2026-11-14, Amendments
A–B in). Spec: Stage 5 Build Spec Rev 22 as amended by Revs
23–26. This bundle is self-contained per Amendment B: the
frozen F-2 adapter configuration and every pinned input the
verification reports cite are inside it.

## Chunk outcomes

- C6-0b pin verification: 31/31, zero exceptions. Batch 4
  clearance established by citation; the installed launcher
  verified live at the C4-12 pin (9ea9b615…), so SE-7 (v)–(ix)
  ride into G3 by pin citation per the Gap 2 ruling.
- C6-0c zero-egress: loopback-only namespace probe passed;
  room left as found.
- C6-1…C6-4 examiner Steps 0–6: built and proven against the
  cleared batches' genuine records (Batch 3 run-001
  re-executes with zero divergence across 69 invocations;
  all five Batch 3 runs reconstruct bit-exact; all 19 Batch 5
  captures verify, Amendment A closed-set enforced).
- C6-5 stub subject: StubAdapter + loopback service; the real
  adapter classifies every stub response ADAPTER_FAILURE
  (identity) — a stub cannot impersonate the pinned model.
- C6-6 build-configuration enforcement: scoreable builds
  refuse the torn-write injector (exit 3, logged); production
  launcher strings-scanned clean of hook markers.
- C6-7 Gate G5 calibration: PILOT-CALIBRATION-01 issued
  (12/13 ANSWERABLE; T03 unanswerable on the then-current
  substrate), superseded by PILOT-CALIBRATION-02 after the
  T03 remediation (below): **all 13 ANSWERABLE**.
- C6-8 Gate G1: sabotage battery 19/19; examiner
  re-derivation 13/13. **G1 PASS.**
- C6-9 Gate G2: genuinely torn write + between-steps crash
  in the scratch room; examiner verification 12/12.
  **G2 PASS.**
- C6-10 Gate G3: SE-1…SE-7 dossier; (i)/(ii) executed fresh,
  (iii) from G2, (iv) three planted-receipt negatives all
  rejected, (v)–(ix) by pin citation. Crosswalk 12/12.
  **G3 PASS.**
- C6-11 Gate G4: **NOT PASSED** — see the headline finding.
- C6-12: this bundle.

## Headline finding — F-G4-1 (driver/tools insert-contract skew)

The stub full-battery run (G4STUB-20261115-001) stopped
incomplete: the pinned driver's insert helper presents the
pre-correction bare operation_id, which the pinned corrected
tools refuse (PRESENTATION_FORM). T05 STOPPED and T08's
record assembly failed on the refusal; T02/T06 completed;
T09 was never reached. A second driver defect (F-G4-2) then
converted T08's step failure into a harness crash
(op_t08_recovery_inputs KeyError) — the supervisor issued
START + CRASH, no TERMINAL, and Step 0 verifies the partial
record. The examiner re-derives the executed prefix with
zero divergences (test_g4.py 10/10), replaying the refusals
bit-for-bit. Full account: evidence/g4/G4-REPORT.md.

**Asked of adjudication:** the correction route. The
builder's recommendation is a Batch 3 driver correction
(_insert_values presents the tagged form) with a driver
re-pin and a battery re-run, F-G4-2 riding with it — one
chunked correction round per Rule 3. No driver or tools file
was altered under Batch 6 authority.

## Examiner correction (builder's own surface, disclosed)

Gate G4's genuine refusal record exposed an order-sensitivity
defect in the examiner's Step 4 refusal pairing (governance
event precedes its return in genuine records; the audit
matched only against returns already seen). Fixed to
operation-identity pairing, both directions. The pre-fix
examiner is preserved byte-exact in the bundle
(package/examiner/prefix/, sha256 36bf23e1…, reconstruction
verified against the G1 pin); the corrected examiner is
sha256 56492523…. All twelve suites re-verified green.

## T03 remediation (reported here per RB-39's undertaking)

Authorised by Ben 2026-11-15 (Proposal 0.1 route (c) as
amended by the RB-35 precision note; your confirmation of
2026-11-15). Implemented: EXTRACTOR-RULES-02 gained the
three disposition rules (EXT02-R47-1/R60-1/R65-1, patterns as
confirmed); the T03 pack gained alex-combined-adjudication-
r60rev#001 (Correction B needed no new rule — EXT02-CB-1
already extracts it); PILOT-PIN-AUTHORITY-02 regenerated
(exactly two entries superseded); full re-calibration issued
PILOT-CALIBRATION-02 — all 13 instances ANSWERABLE, T03 the
only verdict change, certificate 01 preserved byte-identical.
Record: filings/T03-REFREEZE-AMENDMENT-2026-11-15.md.
Disclosed in that record: the cert-02 re-run overwrote
certificate 01's runner transcript before transcript paths
were made certificate-specific (the certificate artefact
itself is byte-preserved), and test_g1's pin verification
reads the preserved pre-amendment rules (G1's evidence
verifies under its own pins).

## Completeness crosswalk

Rev 26 §2.4 artefacts: PILOT-TOOLS-01 (package/tools/);
EXTRACTOR-RULES-02 (package/data/, amended + pre-amendment
copies); PILOT-DATA-PACKS/EXPECTED/T09/FIXTURES-01
(package/data/); PILOT-CORPUS-SNAPSHOT-01 (package/snapshot/);
driver + record writer (package/driver/); issuance registry
(the IssuanceRegistry in package/tools/pilot_tools.py,
specified Harness §4.2); supervisor + commitments design +
launcher binary and pinned source (package/supervisor/,
binary at its C4-12 pin); adapter + helper path
(package/adapter/, incl. the frozen F-2 configuration,
Amendment B); examiner tooling (package/examiner/);
PILOT-CALIBRATION-01 + its successor (package/calibration/).
Stage 5 evidence pack: evidence/g1 (sabotage battery record
+ re-derivation report), evidence/g2 (interrupted-write
artefacts + verification report), evidence/g3 (SE-1…SE-7
dossier + demonstration artefacts), evidence/g4 (stub
full-battery record + worksheet + G4 report), G5 =
package/calibration/ (certificates + transcripts + audits);
the Batch 5 captures the Step 5 verification cites are at
evidence/batch5-captures/.

Gates: G1 PASS, G2 PASS, G3 PASS, G4 NOT PASSED (F-G4-1),
G5 PASS (PILOT-CALIBRATION-02).

## Invariants held

No live provider call anywhere in Batch 6 (I-1/C6-D2): the
only subject was the scripted stub. Examiner independence
(I-2): no code shared with driver/adapter/supervisor beyond
the pinned pilot_jcs.py and the record-format reader.
Scratch containment (I-3): all runs in scratch trees; the
installed room's commitments were never touched except by
the runs' own supervisor-issued receipts in the scratch
room. Settled artefacts were built and examined as pinned
(C6-D3); every finding above names its governing pin and
clause.

Manifest: MANIFEST.sha256 (standard two-character
separator; `sha256sum -c` clean at assembly).
