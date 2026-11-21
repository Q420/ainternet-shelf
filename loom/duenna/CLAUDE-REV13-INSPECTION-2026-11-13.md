# Independent inspection — STAGE5-BUILD-SPEC-13 (pin bab720b2, sha256 ebefa4a1…)

Inspector: Claude (second inspector, commissioned by Ben). Not the builder.
Verdict returns via Ben. Findings below are for the record; each needs Ben/Alex decision.

## VERDICT: NOT YET FIT TO BUILD FROM

Reasons (summarised; detail below):
1. Safety holes in the custody design (no child no_new_privs; environment and supplementary groups unspecified).
2. Contradictions a builder cannot satisfy (refusal object vs "no value"; error-body redaction vs verbatim; S3 vs blanket rule).
3. Gates that can pass without testing what they claim (G1 adapter refusals untested; G2 torn-write evidence from a different build; G5 passes on 13/13 UNANSWERABLE).
4. Process: build go, Stage 6 authorisation and Batch 2 authority are not consistent with §7; Stage 5 contains provider contact (Batch 1 Crusher lane HTTP 429s), contrary to the zero-contact rule.
5. Governing plan pin (S1) does not match the shelved plan text (finding F1).

## Coverage
- Read in full by me: §1, §2, Part 1, Part 3, Part 4, the amendment history (skimmed for changes), §3.7 and G1 (Rev 13 correction).
- Read in full by reviewers (five parallel inspectors, reports in this folder): §3.1–3.4, §3.5 (both halves), §3.6–3.7, §4, §5, §6, §7.
- I verified every High finding against the spec text (quotes and line numbers checked). I did not verify every Medium and Low finding.
- Hash checks against the shelf clone: spec 13 and S3, S4, S5, S6, S7 and all §2.3 source rows match their pins. S1 does not (F1). S10 and the external corpus rows are not in the clone and were not checked.

## HIGH — verified against the text
- A-1 (lines 2010–2012, 3703–3707): refusal object returns `recomputed`, while the same text says "no value"; G1 fails any value returned. Fix: define refusal fields exactly.
- A-2 (lines 3341–3343, 3361–3363): error bodies kept `response_body_raw` verbatim and also "redacted before writing". Direct conflict for 429/5xx bodies. Fix: raw body in restricted file; redacted copy separately hashed.
- B1-2 (lines 2218–2228): no runtime environment rule for the child (envp, cwd, umask, signal disposition). Inherited environment could carry PYTHON* variables or credentials. Fix: compiled-in envp, fixed cwd, reset signals; test by reading /proc.
- B1-8 (lines 2281–2288, 2415–2418): supplementary groups named but no setgroups call, no getgroups read-back. Fix: setgroups(0) before setresgid; read back empty set.
- B2-1 (lines 2802–2815, 3083–3084): nothing requires the harness child to set PR_SET_NO_NEW_PRIVS; no probe that no setuid-root binary is executable by pilot-harness. Fix: set and read back NoNewPrivs before gate release; add demo.
- C-2 (lines 3697, 3706–3709): blanket "any insertion succeeding fails the build" contradicts S3's required first insert. Fix: state the rule per test.
- C-3 (lines 3725–3728, 3650–3660): G1 claims evidence of adapter loopback refusal and proxy refusal, but no battery test exercises them. Fix: add non-loopback base URL and proxy-env tests (S6, S7).
- C-4 (lines 3643–3645, 3733–3748): G2 torn-write runs in scratch build, but Batch 4 says "assembled package"; absence of injector shown by flag record, not by inspecting the compiled artefact. Fix: artefact check on the offered build.
- C-7 (lines 3585–3587): Batch 0 checkpoint does not require the launcher freeze, custody setup artefact or probe output. Fix: extend the checkpoint.
- C-13 (lines 3668, 3790–3793): G5 passes with any number of UNANSWERABLE, including 13/13. Fix: bound UNANSWERABLE exceptions.
- D-1: Build go (22:22) was conditional on both inspections standing (§7 step 3); Claude's only verdict was "not yet" on Rev 11, and no Rev 13 verdict is on the record. Go is not shown to be waived.
- D-3: Stage 6 authorisation dated 19:13, before the build go and before any gate; "effective once the build passes its gates" (Part 3 C). Not the §7 step 7 authorisation.
- D-4: Batch 1 Crusher lane recorded HTTP 429 responses from the provider (Part 4, basis 1). §6.3 item 5 says no provider request in Stage 5. Crusher is not defined in the record. Needs breach record and ruling.
- D-7: Batch 2 authority: Part 3 A says Ben's 07:06 approval covers Batch 2; Part 4 says Alex's letter states Batch 2 "remains closed and unauthorised". Ben's verbatim wording is not in the record (summary from memory).
- D-8: Environment, measured identities (uid 999/997, gid 986/985) and adapter_config_sha256 superseded spec values without an amendment; "wsl reading" accepted by an inspector's interpretation.
- D-9 (lines 3923–3924): spec records the C launcher as "the approved exception" to §6.3 item 4, which says inspectors approve such exceptions. Nothing shows approval.
- D-10 (line 3873): receipt confirmation "discharged by gate G3/G4's step-0", a builder-run gate, contrary to §6.4 and §7 step 6.

## HIGH — partly verified
- B1-6: spec does not spell out the handoff from launcher to supervisor after release; the launcher's code is said to have no commitment path while the parent issues. Confirm the handoff and amend.
- D-2: §7 step 2 says neither verdict is an input; §6.3 item 5 says Alex's clearance reasoned from Claude's findings. Confirm and state it.
- D-6: §5 says "no partial pass"; Part 3 B records G1 "not passed" and S1 "carried open by agreement". Record as not run; remove the agreement.

## HIGH — not verified by me
- A-3 (stub vs transport double placement), B1-1 (supervisor import path / protected placement for the issuer), D-5 (provenance of the F-2 catalogue response; if live, it is D-4).

## Plan pin (not a reviewer finding)
- F1 (Medium): S1 plan pin (2449c259…, 7,497 B, "local, not on the shelf") predates the 16:45 index amendment that the shelved plan (743e7dd4…, 8,205 B) contains; §2.2 says the pin covers the amendment. Re-pin S1 to the shelved bytes and put the pinned bytes on the shelf.

## MEDIUM and LOW (reviewer findings, not individually verified by me)
- Medium: 52. Low: 26. Full text in agent-A.md, agent-B1.md, agent-B2.md, agent-C.md, agent-D.md in this folder.

## What I'd ask Ben to decide before any further build step
1. Whether the 22:22 build go stands, is re-issued, or is voided pending a Rev 13 verdict on the record (D-1).
2. Whether Batch 1 Crusher contact is a breach to rule on (D-4).
3. A verbatim, retrievable record of the Batch 2 go and Alex's written answer (D-7).
4. Whether to issue Rev 14 for the superseded baseline and fix the findings above (D-8, and the High list).

## Limits of this inspection
- Reviewers are separate instances that read only the spec package; they are not the builder, but they are not a human inspector.
- Medium and Low findings are not verified. Some High findings in the "partly verified" and "not verified" groups may change on reading.
- I did not run the harness, the battery, or any build.
