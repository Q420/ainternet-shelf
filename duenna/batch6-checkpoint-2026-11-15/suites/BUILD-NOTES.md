# BATCH 6 — BUILD NOTES

Governing sheet: BATCH6-CHUNK-SHEET-APPROVED-2026-11-14.md (disposition ALEX-C6-0A-2026-11-14, shelf @ e2cab33, blob sha1 3a7632d2…). Build under Ben's 2026-11-13 go (Batches 2–6 in order).

Pre-batch gates:
- C6-0a DONE — Alex's approval recorded on the shelf by his own hand; verified byte-for-byte.
- C6-0b DONE — pin verification manifest (../C6-0B-PIN-VERIFICATION-MANIFEST-2026-11-14.md): 31/31 rows; Alex's condition (a) Batch 4 clearance by citation, (b) launcher binary 9ea9b615… verified live → SE-7 (v)–(ix) by pin citation.
- C6-0c DONE — zero-egress record (../C6-0C-ZERO-EGRESS-RECORD-2026-11-14.md): namespace construction verified, 3 egress attempts blocked, room left as found.

Chunks:
- C6-1 DONE 2026-11-15 — examiner Step 0 (anchor & issuance verification). pilot_examiner.py sha256 2d686af3… (pin in full at checkpoint); test_step0.py 8/8: genuine B4SMOKE START+TERMINAL pass, genuine B4CRASH START+CRASH pass, torn-tail fixture bounds to complete events, fail-closed on missing receipt / TERMINAL+CRASH coexistence / tampered receipt / receipt absent from issuance / completed torn tail / record altered under TERMINAL. Derivations confirmed empirically against Batch 4 artefacts before coding: genesis = sha256(JCS(RUN_STARTED.payload)) == prev_event_sha256; receipt_sha256 = sha256(receipt file bytes). Examiner shares only the pinned pilot_jcs.py (8a131cfc…, copied into this directory) with the rest of the system.
- C6-2 DONE 2026-11-15 — Step 1 chain integrity & Step 2 input identity, in pilot_examiner.py (step1_chain, step2_inputs, verify_snapshot, check_capture; CLI step1/step2). test_step12.py 11/11: genuine records walk clean; seq gap / hash mismatch / rehashed-edit link break each localised at the first divergent event; stub run classified STUB; real pins validate against PILOT-PIN-AUTHORITY-01 + freeze manifest; pin-mismatch fixture caught; corpus snapshot constituent section hashes + digest chains recompute clean; genuine double-lane capture labelled SYNTHETIC (loopback endpoint) with zero findings; forged live-lane capture (endpoint rewritten, record hash recomputed, catalogue hash wrong) REJECTED on the catalogue check. Capture rule grounded in the F-2 config's own catalogue_pin (8a80b8e7f84b…, confirmed identical in the config and the genuine capture).
- C6-3 DONE 2026-11-15 — Step 3 deterministic re-execution & Step 4 insert/carried-provenance audit, in pilot_examiner.py (load_tool_env, step3_replay, step4_audit). Pinned tool artefacts staged in build/tools/ (corpus_source.py 520f36fd…, rules_engine.py 7a232915…, pilot_tools.py df1045f7… — all matching the C6-0b authority pins; EXTRACTOR-RULES-02.json 61095f21…). test_step34.py 8/8: Batch 3 run-001 re-executes with ZERO divergence across all 69 tool invocations (shelf_lookup, source_extract, verify_field, reference_insert, receipt_worksheet); extraction-outcome mismatch localised to its event; registry audit of run-001 clean (17 issuances, 12 consumptions, 0 findings); double consumption, invalid carried provenance (hash), non-null carried source_ref, and unpaired INSERT_REFUSED each detected on fixtures. Two build-time findings: (1) run-001's insert invocations carry the earlier bare-operation_id args form — the replay translates it to the pinned correction form's tagged presentation ({"form":"extracted",…}); the correction form's success result matches the recorded envelope exactly. (2) CHECK coverage boundary: of run-001's 31 CHECK_RESULTs, 3 re-evaluated mechanically (verbatim-rows + verify_field patterns); the other 28 are narrative conditions over subject artefacts whose compared payloads are carried but not re-derived — reported in the step3 result as checks_not_reexecuted, never silently passed. OPEN QUESTION — ANSWERED 2026-11-15: pilot_trees.json (shelved Batch 3 bundle copy) carries each step's `verify` as the same natural-language condition string recorded in CHECK_RESULT — there are no machine-readable check definitions. The examiner's boundary stands: the two data-mechanical patterns re-evaluate; the rest are carried as compared payloads, reported not-re-executed. (The trees DO carry machine-readable failure/recovery policy — failure: STOP, recovery {kind: return_once, max_attempts} — which is Step 6's input at C6-4.)
- C6-4 DONE 2026-11-15 — Step 5 capture integrity + Amendment A, Step 6 outcome reconstruction, full `examine` CLI, interface pinned in EXAMINER-INTERFACE-01.md. Examiner sha256 36bf23e1… (full pin at checkpoint). test_step56.py 7/7; all four suites green (8+11+8+7=34 checks). Step 5: all 19 Batch 5 captures verify clean (record/request/response hashes, attempts' body hashes, retry policy max 2 + byte-identical resend); Amendment A's seven-key closed set is enforced on the WIRE envelope parsed from request_raw (the capture's request_envelope field is the six-key config envelope, checked closed against the F-2 config itself); extra-key negative control rejected; run-001's 7 MODEL_CALL_LINKED preserved outputs verify (response_sha256 = sha256 of the raw output bytes). Step 6: all five Batch 3 runs reconstruct BIT-EXACT — closures and terminal state — across the full closure vocabulary the runs exhibit: COMPLETED (incl. FR-VALID, whose STEP-03 failure is disposed of by its declared rule "the worksheet stands… recorded as a worker error"), STOPPED (tree timeout, run-003 T05), INVALIDATED-INFRASTRUCTURE (adapter-class STEP_FAILED, run-002; RUN_STOPPED invalidated_trees count also verified), INCOMPLETE (all steps passed but RUN_BUDGET_EXCEEDED at that tree, run-004 T05). Closure semantics were derived from the records + the trees' declared failure rules, never copied from the recorded closures; a falsified CHECK_RESULT overturns the recorded closure, localised. Derivation notes: record_sha256 in RUN_CLOSED is the chain head the terminal event closes over (its own prev pointer); T05-STEP-06 legitimately never triggers on a happy path, so completion is judged on triggered steps + reaching the tree's last defined step.
- C6-5 DONE 2026-11-15 — scripted stub subject, two surfaces. (1) StubAdapter (stub_subject.py sha256 a8408d0d…): the harness side of the complete() contract — closed step_inputs, F-2-shaped envelope with the stub identity, F-2 retry policy (scratch delay 0), and genuine ADAPTER-CAPTURE-02 records (same 30 fields, canonical write, record_sha256) with subject pins naming the stub (script sha256 39df6bb6… as catalogue pin; config pin = the stub run config's JCS hash). (2) The stub's loopback HTTP service, against which the REAL Batch 5 adapter classifies every stub response ADAPTER_FAILURE (identity mismatch) and withholds the output — a stub can never impersonate the pinned model through the real adapter; the capture still preserves everything, stub-labelled (response_model_id_served). Stub script (12 calls): Batch 3's proven outputs reused verbatim; fault shapes per Alex's disposition — retry-then-success on T08 (transport-level), malformed on FR-B attempt 1 and truncation on FR-C attempt 1 (recovered by the trees' return-once rules to the original outputs on attempt 2), refusal-shaped on T03. Scratch-only guard: load_stub_config refuses any config not declaring scratch_only + the stub identity + live:false; the F-2 live config contains no stub identity. test_stub.py 6/6; all five suites green (40 checks).
- OPEN ITEM for C6-7: the "13 instances" enumeration is DERIVED, not yet confirmed against a catalogue: the nine trees T01–T09 (PROCESS-TREES via Rev 26 line 3614; packs file keys T01–T08 + T09-FR-A/B/C/VALID) + the four FR variants counted as instances = T01, T02, T03, T04, T05, T06, T07, T08, T09, T09/FR-A, T09/FR-B, T09/FR-C, T09/FR-VALID. The calibration certificate (C6-7/C6-8) must name them exactly; if the count is wrong Alex corrects it at adjudication (one-round item).
- C6-6 DONE 2026-11-15 — build-configuration enforcement for test-only fault hooks. Recon finding: the flag existed only in the spec; no injector implementation existed in the code (Batch 4's torn writes were produced by external manipulation, and its launcher test hooks sit behind PILOT_TEST_HOOKS in the launcher sources). Built: torn_write_injector.py (the test-only slow/partial write path — deterministic fragment writes, torn tails) + build_package.py (two configurations: scoreable REFUSES with PILOT_TORN_WRITE_INJECTOR set, exit 3 logged; scratch with the flag includes the injector + compiles the launcher with PILOT_TEST_HOOKS and records itself NOT scoreable; every build mechanically scans its launcher object for hook markers and writes FLAG-STATE.json + the enforcement log in build/c6-6-evidence/). Production confirmation: the installed launcher on the laptop is still the C4-12 pinned binary (9ea9b615…) and a strings scan finds NO hook markers — hooks compiled out. test_build_flags.py 4/4; all six suites green (44 checks).
- C6-7 DONE 2026-11-15 — Gate G5 calibration pass executed; PILOT-CALIBRATION-01 issued (canonical JSON, sha256 6f3e5979…; runner pilot_calibration.py 5a903694…; transcript calibration-transcript.txt; audit test_calibration.py 7/7). The 13 instances are enumerated in the certificate as T01–T09 (T09 = the obligation-spec instance) + T09/FR-A, FR-B, FR-C, FR-VALID. **12 of 13 ANSWERABLE. T03 is UNANSWERABLE, cause named in the certificate: T03-STEP-03 requires source_extract of the dispositions from alex-combined-adjudication-v010#002, and no EXTRACTOR-RULES-02 field produces a value from that section (all six NOT FOUND) — its dispositions (R47 PASS / R60 FAIL / R65 PASS) exist only as prose no pinned rule covers, and Correction B's status is producible only from ADJ_R60, which is not a T03 pack item.** Remediation (§5.3: rules amendment + re-freeze + re-calibration, or a tree amendment) is an Alex/Ben decision — T03 may not run at Stage 6 until fixed; the finding rides into the C6-12 checkpoint. Measured highlights: R60 §5.2 block — all four fields reproduce by single-match extraction (38/38, both hashes), correction_b OPEN from the adjudication record; T05-STEP-02 cross-record comparison AGREES (854a3e86… == manifest row) so T05's pinned expectation is construction; T06 labels derive == T06_KEY; T07 statuses derive == OB_TRUTH with OB-2/OB-3 absences pinned as designed; T08 seeded-draft failed checks = exactly the designed four (3 missing + correction_b mismatch); T09 worksheets FR-A/B/C REJECT, FR-VALID CLOSE; §5.1(5) synthetic AMBIGUOUS + TYPE FAILURE exercises pass; §5.1(6) config check passes on values (0.6 / 0.95 / 16384 / 20480 / RFC 8785) and the canonical config hash matches the F-2 pin. Substrate note: both hash extractions from the change record span two lines, so the pinned engine's single-line evidence lookup returns "" — the certificate records the evidence span for those rows. Runner history: the first pass wrongly certified T03 (counted extractions from the change record toward a step whose input is the adjudication record); caught on spot-check, corrected, re-run — the certificate of record is the corrected one.
- C6-8 NEXT — Gate G1: provenance sabotage battery S1–S5 against the built PILOT-TOOLS-01 in a scratch run context + zero-egress environment evidence (C6-0c's namespace record is the environment half's starting point; the battery runs against pilot_tools with forged/replayed/stale/ambiguous inserts).

## C6-8 — Gate G1: sabotage battery S1–S5 + zero-egress evidence (2026-11-15)

Runner `g1_battery.py` (sha256 9849114a…) executed by `../g1_run.sh`
inside a fresh loopback-only namespace (unshare -Urn, loopback up,
no routes, environment scrubbed with env -i) in the Batch 6 build
environment. The battery drives the pinned PilotTools through the
driver's RecordShim pattern into a hash-chained RunRecord;
artefacts preserved in `../scratch/g1-run/` (run-record.jsonl,
snap-genuine/, snap-perturbed/, captures/, ENV-INSPECTION.json,
ADAPTER-CHECKS.json, issuance-records.json, BATTERY-RESULT.json,
TRANSCRIPT.txt). Runner checks 19/19.

Outcomes: S3 extract EXTRACTED (38) -> first insert succeeded
(the battery's only LEDGER_ENTRY) -> replay refused
ALREADY_CONSUMED. S1 forged op-4 (the guessable next sequence
number, never issued) refused NO_ISSUANCE. S2: genuine TYPE
FAILURE extraction (fixtures_executed on qwen-ab-results-v1#009 —
pattern genuinely matches, captured token fails the integer type;
the built tools' genuine instance of the spec's FOUND class, a
located-but-not-EXTRACTED issued result) refused NOT_EXTRACTED.
S5: fixtures_executed on qwen-ab-v2r-results#004b AMBIGUOUS (2
candidates, no value) refused NOT_EXTRACTED. S4: genuine EXTRACTED,
corpus rebound to the perturbed scratch copy (CR section text
altered, stated sha256 genuine; swap recorded as HARNESS_NOTE),
refused SNAPSHOT_MISMATCH with recomputed_source_hash ==
sha256(perturbed text). Zero-egress: no default route, external
TCP + DNS blocked, no credential variables in the scrubbed
environment. Adapter (§3.7): non-loopback base URL refused at
start-up (ConfigError); with proxy env poisoned to an unroutable
address the adapter completed its loopback exchange with the stub
service (capture: HTTP 200, ADAPTER_FAILURE identity mismatch) —
proxy structurally ignored (ProxyHandler({})).

Examiner re-derivation `test_g1.py` (sha256 6d1047d0…): 13/13 —
chain verifies; pin block recomputes; full re-execution of every
recorded invocation (following the record's corpus swaps)
reproduces every result, the LEDGER_ENTRY and all five
INSERT_REFUSED events; registry reconstruction == preserved
issuance records; S4 recomputed from the preserved perturbed
artefact; the proxy-check capture passes Step 5 verification.
Report: ../scratch/g1-run/G1-REDERIVATION-REPORT.md.

Vocabulary note for the checkpoint: the spec's G1 text says
"FOUND result" (Harness §8 Q3 vocabulary: EXTRACTOR-ONLY inserts,
no exceptions). The built tools issue no FOUND verification; the
battery's S2 uses the genuine TYPE FAILURE instance and the
mapping is stated in the record and this note for Alex's
adjudication.

Full regression after C6-8: all eight suites green (64 checks).

## C6-9 — Gate G2: torn-tail crash test + between-steps companion (2026-11-15)

Executed in a fully scratch room on the laptop
(/srv/nemotron-pilot/batch6-g2/), mirroring Batch 4's sup-test
rig: scratch launcher compiled from launcher-c3.c with the
scratch HARNESS_PATH + PILOT_TEST_HOOKS (sha256 e773ebd9…),
identity records generated for the scratch tree, supervisor run
as pilot-supervisor against scratch runs/commitments/logs/
evidence only. The installed room was never touched. First
attempt refused both runs at Stage 1 on commitments_custody
(scratch commitments dir mode 755); fixed to 700 and re-ran.

Artefacts (preserved in ../scratch/g2/, fetched byte-identical;
record hashes match the room's own stage summary):
- G2TORN-20261115-001: the harness (g2_harness.py, sha256
  c29500ff… on the room) wrote RUN_STARTED + STEP_TRIGGERED,
  captured event 3's exact line through the genuine writer,
  then rewrote the record through torn_write_injector's slow
  fragmented path (16-byte fragments, 0.35 s); an external
  killer SIGKILLed it ~2 s into the append (killer log pid ==
  the harness's torn-started marker). Result: 1,219 bytes, 2
  complete events + 112 genuinely torn tail bytes, no trailing
  newline. Supervisor CRASH receipt: event_count 2,
  record_file_sha256 d1f48f31… == sha256 of the bytes as they
  lie. No TERMINAL receipt.
- G2BETWEEN-20261115-001: self-SIGKILL after 2 complete
  events, clean ending; CRASH receipt over ebb0025e…; no
  TERMINAL. The between-steps companion (SE-7(iii)).

Examiner verification test_g2.py: 12/12 — Step 0 verifies the
CRASH anchor over the exact bytes incl. the tail; the chain
walk ends at event 2 (tail = no event/step/verdict); trimmed
and plausibly-completed copies are both rejected at Step 0 as
anchor failures (record_file_sha256 mismatch); negative space
holds (no TERMINAL, CRASH entries in the issuance record,
outcomes INCONCLUSIVE); flag states recorded (scratch launcher
carries PILOT_HOOK markers + injector present in the scratch
harness tree; C6-6's scoreable flag state shows neither).
Report: ../scratch/g2/G2-VERIFICATION-REPORT.md.

Full regression after C6-9: all nine suites green (76 checks).

## T03 remediation (side line, Ben's ruling 2026-11-15) — COMPLETE

Implemented Alex's Amendment Draft 0.1 as corrected by RB-39
and confirmed by Alex: PILOT-DATA-PACKS-01 T03 pack +=
alex-combined-adjudication-r60rev#001 (c7eaec18… → b197e93e…);
EXTRACTOR-RULES-02 += EXT02-R47-1/R60-1/R65-1 with the
corrected patterns (7910ef9f…; pre-amendment originals
preserved byte-for-byte in ../../t03-remediation/).
PILOT-PIN-AUTHORITY-02 regenerated (0b6bf252…, two entries
superseded). Full re-calibration issued PILOT-CALIBRATION-02
(1094802a…): all 13 ANSWERABLE; T03 the only verdict change;
PILOT-CALIBRATION-01 preserved byte-identical (6f3e5979…).
Audit test_calibration2.py 8/8. Amendment record:
duenna-letters/T03-REFREEZE-AMENDMENT-2026-11-15.md (shelved,
with the certificate + pin authority). Disclosed there: the
cert-01 transcript log was overwritten by the re-run (runner
transcript path since made certificate-specific); test_g1's
pin check now verifies against the preserved pre-amendment
rules (13/13 re-verified). Full regression: ten suites green
(84 checks).

## C6-10 — Gate G3: SE-1…SE-7 dossier + demonstrations (2026-11-15)

Dossier: G3-DOSSIER.md. SE-1…SE-6 structural inspection of the
pinned pilot_tools.py with line-level code citations, each
paired with executed behavioural evidence (G1 battery, C6-3
replay, C6-5 adapter contract). SE-7(i) executed fresh in the
scratch room: G3VAULT run — create/overwrite/append/delete
against the commitments store all refused EACCES from inside
the genuine harness boundary. SE-7(ii) executed: G3FALSE run —
supervisor START receipt commits the falsified pin block's
actual bytes (genesis 34079eb6…, examiner-recomputed); the
falsified pin is foreign to every pin authority. SE-7(iii)
carried from G2 (C6-9 artefacts + 12/12 report). SE-7(iv):
three planted-receipt negatives executed on scratch copies —
issuance entry removed, planted altered receipt, planted
CRASH beside TERMINAL — all rejected by Step 0 as custody
findings. SE-7(v)–(ix) carried by pin citation per Alex's
C6-0a Gap 2 ruling (C6-0b verified the launcher pin unchanged,
9ea9b615…; Batch 4 checkpoint CLEARED). Crosswalk audit
test_g3.py: 12/12. Full regression: eleven suites green
(96 checks).
