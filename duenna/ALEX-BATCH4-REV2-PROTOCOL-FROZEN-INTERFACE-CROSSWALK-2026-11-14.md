# Batch 4 — Protocol-to-Frozen-Interface Crosswalk
Prepared by Alex against Whole Plan Rev 2, 2026-11-14.
Review artefact only; it does not amend the freeze, Rev 26, the approved chunk sheet, or Ben's authority record.

## Pins examined
- Whole Plan Rev 2: commit 9b84c4dbeaa08054d3e92bb31b52b30f6380b5f4; file SHA-256 stated by Remmy: b04d667d6bdb107035885244ec0241f828b55ef1a87a8c1a2620c0a35dc68733.
- Launcher interface freeze: `duenna/launcher-interface-freeze.md`; SHA-256 6bb9ae8047b9fd62ba47dc64d18af3579464807ae9fc6c1a03467a22f615d1f5.
- Rev 26: `duenna/STAGE5-BUILD-SPEC-26.md`; inspected at commit 9b84c4dbeaa08054d3e92bb31b52b30f6380b5f4.
- Batch 4 Chunk Sheet Rev 2: `duenna/BATCH4-CHUNK-SHEET-REV2-2026-11-13.md`; blob 108aeb33502eb0e0a9a54aab5a891404c906ea64.
- Q7 report: `duenna/BATCH4-LAUNCHER-CORRECTION2-Q7-REPORT-2026-11-13.md`; blob e60a48c9595725f2623d965e45b7167598a0bfa8.

## Crosswalk

| Frozen interface / specification obligation | Rev 2 location | Build / checkpoint coverage | Review note |
|---|---|---|---|
| Freeze §1: root-owned, setuid-root C binary, mode 4710, group pilot-supervisor; single-threaded; fail-closed setuid preconditions | C0, C4; C4-1 | C4-0a/0b source gate; C4-0c install evidence; C4-0d existing probe verification; C4-12 binary pin and properties | Correctly preserves source inspection before Batch 4 and distinct binary inspection at checkpoint. |
| Freeze §2: one fixed spawn operation; no arbitrary programme/path/configuration; strict run ID; no shell/network/extra privileged writes | Part A §A.3; C0/C2/C3 | C4-0b source inspection; C4-9 refusal tests | Rev 2 gives packet classification and retains fixed compiled path. Concrete run-ID pattern remains an implementation detail under freeze residual R-1, not a new protocol authority. |
| Freeze §3: private gate pipe, child first parent check, identity drop, all-three-mask readback, PDEATHSIG, parent recheck, descriptor closure, one-byte gate; parent drop and verification before release | Part A; Part B; C0/C2/C4 | C4-0b source inspection; C4-8 demonstrations; C4-12 binary properties | Part A changes only receive classification; it must not reorder the frozen child/parent sequence. Part B's supervisor observation supplements, not replaces, each process's in-process fail-closed readback. |
| Freeze §4: descriptors 0/1/2 at declared destinations and modes; no protected-store descriptor inherited | C2/C3 | C4-8 SE-7 descriptor demonstration; C4-10 self-computation; C4-12 binary evidence | Rev 2 retains the existing descriptor verification and child allowlist through the frozen source contract; no destination relaxation is stated. |
| Freeze §5: three-part exec condition; canonical resolution, protected placement, identity record and pre-release re-check | C2; C4-8…12 | C4-8 SE-7 identity demonstrations; C4-12 binary/source pins | The whole plan does not replace the three layers or widen the threat model. |
| Rev 26 §3.5 point 1: two distinct OS identities, group separation, custody boundaries | C4-1 | Existing Batch 0 setup evidence plus C4-0c current-state re-read; C4-8(vii) | C4-1 is explicitly mapped; existing identities are re-read, not recreated. |
| Rev 26 §3.5 point 2: supervisor, launcher, harness roles; supervisor spawns launcher; launcher is child OS parent; no reassignment of authority | C2/C3/C4 | Source inspection; C4-8/9; checkpoint records | C2/C3 preserve the three-role division and stub-only harness boundary. |
| Rev 26 §3.5 point 3: nine-stage gated launch, packet catalogue, pidfd handoff, readiness, EOF/ABORT lifecycle, wait/reap invariants | Part A; C2 | Receive-case suite; C4-8 handshake demonstrations; C4-12 | Part A's collection semantics govern only the three receive sites named in §A.1. Existing site exit/cleanup contracts remain normative. |
| Rev 26 §3.5 point 4: supervisor authority and descriptor/identity checks | C2/C3 | Code inspection and SE-7 evidence | C2's descriptor checks and fixed execution contract remain subject to the freeze. |
| Rev 26 §3.5 points 5–8: START/TERMINAL/CRASH issuance; supervisor computes commitments; append-only issuance record | C2 | C4-8(ii), C4-10, C4-11 | Frozen issuance schema remains exactly {run_id, kind, issued_at_utc, receipt_sha256}; Part B correctly places mask evidence outside that schema. |
| Rev 26 §3.5 point 9: examiner verification hooks/data shapes; examiner tooling itself in Batch 6 | C2 | Batch 4 data shapes; Batch 6 tooling | Correctly distinguishes hooks/data shapes from Batch 6 examiner implementation. |
| Chunk Sheet Rev 2 C4-0a/0b: source against canonical freeze, pin, Alex inspection, recorded disposition before Batch 4 begins | C0 | Pre-batch gate | Explicit and binding. The historical e31db79d… pin is not treated as the new cleared source pin. |
| Chunk Sheet Rev 2 C4-0c/0d: current-state custody re-read, separate installed-binary operator evidence, verify existing probe evidence only | C4/C5 | Dated operator artefact; read-back; existing probe hash verification | Correctly separates original setup evidence, current-state evidence, install evidence and prior probe evidence. |
| Chunk Sheet Rev 2 C4-8…12: SE-7 (i),(ii),(iv), harness-identity refusal tests, falsified pin self-computation, planted-receipt negative, binary pin | Part D | One checkpoint bundle | Scope matches. G2 crash cases remain deferred to Batch 6. |
| Chunk Sheet Rev 2 C4-D2: no subject call in Batch 4 | C3; Part D | Stub subject only | Explicitly preserved. |

## Crosswalk conclusion
The Rev 2 build sequence maps to the frozen interface and approved Batch 4 chunk scope. The pre-batch source gate remains a condition precedent. Ben's existing Batches 2–6 build-go is not voided by this plan; Batch 4 may begin only after C4-0a/0b has a cleared source pin and recorded disposition. This crosswalk does not grant a new build-go and does not clear Whole Plan Rev 2.
