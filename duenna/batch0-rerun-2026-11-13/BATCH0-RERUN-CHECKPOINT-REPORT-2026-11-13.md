# BATCH 0 RE-RUN CHECKPOINT REPORT — STAGE 5 BUILD, NEMOTRON PILOT

**Batch:** 0 — Re-freeze and freeze checks (Build Spec 13, §4), RE-RUN.
**Built from:** the shelved specification at commit `bab720b2`
(`STAGE5-BUILD-SPEC-13.md`, sha256
`ebefa4a14b73e8f3bfbb7f7188d4524de88460c38c2acd2eec302f584b8394b7`,
re-verified in-room at Step 2 of the run).
**Environment:** the Ubuntu room (WSL2, Ubuntu 26.04.1 LTS, kernel
6.18.58.1-microsoft-standard-WSL2) on Ben's laptop — the candidate
environment ACCEPTED for this re-run by Alex's adjudication
pb-mwep7new (2026-11-13), on the acceptance-probe evidence shelved
at 844439bc.
**Authorisation:** Ben's go, 2026-11-13 ~00:13 MST (tap on scope
card + "And run the thing so I can watch lol"), recorded in the
scope ledger.
**Build root (in-room):** `/srv/nemotron-pilot/`.
**Date:** 2026-11-13 (MST). Run window 01:16:36–01:16:46 MST.
**Zero provider contact:** no provider request of any kind was
made; Nemotron was not called.
**Transcript:** `BATCH0-RERUN-TRANSCRIPT.log` in this bundle —
the complete session output, streamed live to
`/home/ben/batch0-rerun.log` in the room so Ben could watch.

## Checkpoint verdict

**PASSED.** Every Batch 0 item is complete in this environment.
The two findings that stopped the original run — F-1 (the setuid
launcher assumption defeated by inherited NoNewPrivs) and F-3
(custody trees not establishable) — are **resolved here by direct
re-execution**, not by argument: the frozen probe, compiled from
the frozen source and installed in the launcher's exact shape
under the build root, opened the privileged window for
pilot-supervisor (euid 0 observed) and refused pilot-harness; the
custody trees were established under the build root, read back as
assigned, and separation was live-tested in both directions. The
original Batch 0 checkpoint on Remmy's VM remains **NOT PASSED**
as history, exactly as Alex ruled; this re-run supersedes nothing
in that record — it answers it.

## Item-by-item state

### 1. Frozen artefacts carried in unchanged — VERIFIED
All 28 staged freeze files sha256-verified in-room against the
manifest computed from the VM originals — every line OK (Step 1).
The freeze that Batch 0 produced is the freeze this re-run ran
on; nothing was regenerated, edited, or substituted. (The JCS
conformance run at item 4 rewrites its two results files in the
room copy; the regenerated results are byte-identical to the
frozen files, which is itself recorded at Step 4.)

### 2. Stage 0 pin re-verification — DONE
The governing spec re-verified at its pin in-room (Step 2).
The freeze's pin-verification record (pin-verification.json)
travels inside the verified artefacts; its corpus-bearing pins
were additionally re-executed in-room at item 3.

### 3. PILOT-CORPUS-SNAPSHOT-01 — DONE, re-executed in-room
Both snapshot files equal their Stage 0 pins at copy time in the
room (sections `b107e892…`, manifest `c93eaa19…`). The freeze's
own verifier ran in-room against the room copies: **1,156
sections across 79 documents — every recorded section hash and
every document digest chain recomputes; zero mismatches**
(`all_sections_verified: true`; Step 3). §4's checkpoint
condition — every Stage 0 pin recomputes, snapshot equality
recorded, a corpus pin mismatch stops the build — is satisfied;
no mismatch occurred.

### 4. RFC 8785 (JCS) implementation pin — DONE, re-executed in-room
PILOT-JCS 1.0.0 source verified at its pin (`8a131cfc…`); the RFC
8785 source text staged and verified at its recorded hash
(`63d52294…`); the frozen conformance runner re-executed in-room:
**35/35 PASS, exit 0**, and the regenerated results file is
byte-identical to the frozen results (Step 4).

### 5. Adapter configuration freeze — DONE (F-2 standing state)
Both canonical preimages verified in-room: the original freeze
(`723f78d9…`, historical) and the standing post-F-2 freeze,
**`adapter_config_sha256` =
`6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb`**
(Step 5). The design-time catalogue evidence stands as Alex
dispositioned it (RECOVERED-DESIGN-TIME-RESPONSE —
COMPLETE-JSON-CONTENT — HELPER-STDOUT-SERIALISATION); no live
listing was taken (Rev 12 rule).

### 6. Launcher behaviour-and-interface freeze — DONE
`launcher-interface-freeze.md` verified at its pin (`6bb9ae80…`)
in-room (Step 6). The A-1 run-identifier grammar amendment
(adopted by Ben 2026-11-12, verified by Alex pb-mwen3tex) and the
F-2 disposition are present in the freeze and hash-verified as
part of item 1. R-1 stands discharged.

### 7. S1 plan discrepancy — carried in its recorded state
Unchanged by this re-run: S1's pin remains the adopted-state plan
(7,497 B, `2449c259…`) against the living file's amended state
(8,205 B, `743e7dd4…`), as recorded in pin-verification.json. Not
re-pinned; the Ben/Alex decision stands open and does not engage
§4's stop rule.

### 8. Custody setup artefact — DONE in-room (F-3 RESOLVED)
The two OS accounts were read back from the operating system
(Step 7): `pilot-supervisor` (uid 999, gid 986) and
`pilot-harness` (uid 997, gid 985), each in its own group only,
nologin shells. **Disclosure:** the accounts pre-exist in this
room — they were created by the acceptance probe, whose shelved
transcript (bundle at 844439bc) is their creation record; this
re-run created nothing silently and re-created nothing. The
build-root trees were established by this re-run and read back
(Step 8): `/srv/nemotron-pilot/runs` pilot-harness 0755;
`/srv/nemotron-pilot/commitments` pilot-supervisor 0700.
Separation live-tested: harness read on commitments DENIED,
harness write on commitments DENIED, supervisor reads its own
custody OK, harness works in its own tree OK. The custody setup
evidence for this environment is Steps 7–8 of the transcript,
together with the probe's creation transcript.

### 9. Launcher environment probe — PASSED in-room (F-1 RESOLVED)
The frozen probe source verified at its pin (`64625db9…`),
compiled in-room, installed `root:pilot-supervisor`, mode 4710,
at `/srv/nemotron-pilot/probe/setuid-probe` — under the build
root, on a filesystem mounted `rw,relatime` (no `nosuid`).
NoNewPrivs reads **0** at PID 1 and in the invoking shell
(Step 9). Invocation A, as pilot-supervisor: **ruid=999, euid=0,
Uid 999/0/0/0, NoNewPrivs 0, "PRIVILEGED WINDOW OBSERVED",
exit 0.** Invocation B, as pilot-harness: **Permission denied,
exit 1.** The setuid assumption the design rests on is verified
in this environment by observation.

### 10. G1 zero-egress evidence, Batch 0's part — DONE (as scoped)
Recorded in-room (Step 10): interfaces (lo + eth0), the WSL NAT
default route, mounts, and the environment's proxy configuration
(**no proxy variables exist in this environment**). Honest
reading, unchanged from Batch 0 and from Alex's adjudication:
the room as it stands is **not** zero-egress; a loopback-only
network namespace is constructible (proven in the acceptance
probe). G1's evidence proper belongs to Batch 6 inside the
constructed gate environment; Batch 0 pre-passes nothing, and
per Alex's ruling this does not block the batch sequence.

## What was not done (by design)

No Batch 1 work. No launcher was built (Batch 4; only its
interface is frozen and its precondition now proven in this
environment). No provider contact, no model call, no index write
(the corpus snapshot travelled as a verified copy; the source
index was not touched). Nothing was improvised: every check ran
in its frozen shape, and the two environment findings from the
original run were answered by re-execution, not workaround.

## Standing state after this checkpoint

- Batch 0: **PASSED** (this re-run, this environment). The
  original VM checkpoint remains NOT PASSED as history.
- F-1: resolved in this environment. F-3: resolved in this
  environment. F-2: closed end-to-end (2026-11-12). A-1: closed.
- Next: Batch 1 begins only on its own authorisation, with Alex
  reviewing this checkpoint first per the build process (Ben's
  2026-11-10 ruling: Remmy works the blueprint in batches, Alex
  reports back and reviews between each stage).
