# Agent C — Inspection of Stage 5 Build Specification Rev 13, §4 (build order) and §5 (gates G1–G5)

Source read: /mnt/user-data/attachments/475f6377-dfad-5672-a7f4-a435c6bdea33/581de8c8-attachment.txt
Assigned range (lines 3519–3813) read in full: **295 lines**.
Additional lines read to verify cross-references: 1826–1859 (§2.4, 34 lines), 1869–1920 (§3.1, 52 lines), 2040–2053 (SE-1…SE-6, 14 lines), 3814–3843 (§6.1, 30 lines). Other cross-references were confirmed by grep for their presence and wording only.

---

## Findings

### C-1 — Medium
- **Lines:** 3614–3616 (Batch 2); 3671–3672 (Batch 6); §5 lead-in 3683–3684
- **Quoted:** "the formal battery runs on the completed tools before Batch 3 closes"
- **Problem:** Batch 2 places the formal G1 sabotage battery at Batch 2/3 close. Batch 6 says "the §5 build-acceptance gates, run in full, on the assembled package", which includes G1. The text never says whether G1 runs once or twice, or which run is the pass that counts. A G1 failure at Batch 6 has no defined return point.
- **Fix:** State that G1 is run once at Batch 2 close and carried forward, with the Batch 6 run defined as a re-run on the assembled package, and name the batch each failure returns to. Or move G1 wholly to Batch 6 and make Batch 2's smoke run explicitly non-gating.

### C-2 — High
- **Lines:** 3697 (S3 "inserted (succeeds)"); 3706–3709 (the "fails the build, full stop" rule and "S3's first insert must succeed")
- **Quoted:** "Any insertion succeeding — a ledger entry"
- **Problem:** The rule says any successful insertion in any test fails the build. S3's first insertion is required to succeed. Both cannot hold. A literal builder will fail G1 on the required S3 positive path, and a builder who reads the S3 clause will ignore the blanket rule. The "required outcome" list in 3703–3706 (INSERT_REFUSED, no LEDGER_ENTRY, no value) also applies to every test, and that contradicts S3's first insert.
- **Fix:** Restate the rule per test: "in S1, S2, S4, S5 any successful insertion fails the build; in S3 the first insertion must succeed (LEDGER_ENTRY emitted, value returned) and the second presentation must be refused." Remove S3 from the generic required-outcome sentence.

### C-3 — High
- **Lines:** 3725–3728 (G1 zero-egress enforcement claim); 3650–3660 (Batch 5 checkpoint); §3.7 definitions at 3483–3493
- **Quoted:** "by its refusal of proxy configuration (§3.7); this gate"
- **Problem:** G1 says "this gate is where that enforcement is evidenced" for the adapter's loopback refusal and its refusal of proxy configuration. Neither is tested in any place in §4 or §5. The Batch 5 checkpoint tests retries, 400 classification, timeout and redaction only. S1–S5 cover only tool insertion refusals. The G1 zero-egress paragraph inspects the environment; it does not exercise the adapter's refusal behaviour. So the no-contact rule's second and third layers can be wrong and every gate still passes.
- **Fix:** Add to the Batch 5 checkpoint: (a) a non-loopback `base_url` causes fail-closed start-up refusal; (b) with `HTTPS_PROXY`/`https_proxy`/`ALL_PROXY` (and any configured proxy) set, the adapter makes no proxy-routed request and refuses or ignores it, with the evidence captured. Add both to G1's required battery as S6 and S7 with the same record and "no contact" outcome.

### C-4 — High
- **Lines:** 3643–3645 (Batch 4: "run formally at gate G2 on the assembled package"); 3733–3734 ("the append is fault-injected"); 3739–3748 (injector flag, scoreable build)
- **Quoted:** "the append is fault-injected"
- **Problem:** G2's torn-write evidence is produced in a scratch build with `PILOT_TORN_WRITE_INJECTOR` set. The build offered for inspection is required to have that flag absent (3746–3748). The slow/partial write path therefore exists only in an artefact that is not the one inspected. Batch 4 says G2 runs "on the assembled package", which cannot carry the injector. G2 can pass on a build different from the one offered, and the production append path is never shown to produce a torn tail. Also, 3746–3748 say the injector's absence "is demonstrated by the recorded flag state, not asserted". A recorded flag does not show that the compiled artefact lacks the injector code path.
- **Fix:** Require (a) the fault-injected run in the scratch build as now; (b) a compile attempt with the flag set outside scratch that is shown to refuse; (c) an absence check on the offered build's compiled artefact (for example, a symbol or string search for the injector path, with the hash recorded); (d) the crash test attempted on the offered build with a natural kill, reporting whether a torn tail appears, with the result preserved whatever it is. Correct Batch 4 line 3645 to say "scratch build".

### C-5 — Medium
- **Lines:** 3759 (G2 "§3.1(ix) anchor failure")
- **Quoted:** "§3.1(ix) anchor failure"
- **Problem:** §3.1 (1869–1918) has no item (ix). Its requirements are the list from "Order and dependency" through "stop finality". The anchor-verification step is Harness §7 step 0, as §3.7 line 3397–3399 and the spec's own §3.5 text show. The cross-reference points at nothing, so a builder must guess which failure class the gate means.
- **Fix:** Change to "Harness §7 step 0 anchor failure (START/TERMINAL and receipt recomputation)", or add a numbered anchor-check item to §3.1 and cite it.

### C-6 — Medium
- **Lines:** 3627 (Batch 3 checkpoint)
- **Quoted:** "the §6.4 partial-record shape"
- **Problem:** In this spec §6.4 is "Builder identity and role separation" (heading at 3950). It does not define a partial-record shape. The unqualified "§6.4" most likely means Harness §6.4, but this spec's section is what an unqualified reference resolves to. The checkpoint's pass condition therefore names a shape that the batch text does not define.
- **Fix:** Change to "Harness §6.4 partial-record shape" if that is what is meant, and confirm that Harness §6.4 defines it. Otherwise define the shape in this spec.

### C-7 — High
- **Lines:** 3585–3587 (Batch 0 checkpoint); 3550–3566 (launcher freeze); 3567–3576 (custody setup evidence); 3577–3584 (setuid-viability probe)
- **Quoted:** "every Stage 0 pin recomputes; snapshot equality"
- **Problem:** The Batch 0 checkpoint requires only the Stage 0 pins and corpus snapshot equality. It does not require the launcher behaviour-and-interface freeze to be pinned, the custody setup evidence (the script or transcript) to exist, or the setuid-viability probe output to be in the freeze evidence with a pass. Batch 0 can therefore pass its checkpoint with the probe never run, and the text says "A failed probe stops the build" without any gate or checkpoint that detects an absent probe. Batch 4 then builds the launcher against an interface that may be unfrozen.
- **Fix:** Extend the Batch 0 checkpoint: the re-freeze amendment contains the launcher interface freeze, the custody setup artefact is preserved, and the probe output shows effective uid 0 inside the privileged window, `nosuid` as required, and no inherited `no_new_privs`. Missing or failing items stop Batch 0.

### C-8 — Medium
- **Lines:** 3543–3546 (Batch 0 pin list); 1837–1852 (§2.4); 3618–3623 (Batch 3); 3647–3660 (Batch 5); 3662–3672 (Batch 6)
- **Quoted:** "pinned by dated additions to the same amendment at their batch checkpoints"
- **Problem:** Batch 0 names pin timing for EXTRACTOR-RULES-02, the pilot data files and PILOT-TOOLS-01 only. §2.4 says every build artefact is "pinned at Batch 0's re-freeze or at their batch checkpoint", but no batch checkpoint in §4 lists a pin as a pass condition, and Batches 3, 5 and 6 do not name their outputs for pinning. The driver and record writer, the adapter source, the examiner tooling and PILOT-CALIBRATION-01 have no stated pin step. G5 requires PILOT-CALIBRATION-01 to be "pinned", which no batch defines.
- **Fix:** Add one pin line to each of Batches 3, 5 and 6 naming its artefacts (driver, record writer, `ADAPTER-CAPTURE-02` adapter source, examiner tooling, PILOT-CALIBRATION-01) and make "dated addition pinned" part of each checkpoint.

### C-9 — Medium
- **Lines:** 1842–1843 (§2.4: "its source pinned in the re-freeze amendment"); 3632–3634 (Batch 4: "its source is pinned by dated addition at this checkpoint"); 3562–3564 (Batch 0: "Batch 4 implements against the frozen interface and pins the resulting source")
- **Quoted:** "its source pinned in the re-freeze amendment"
- **Problem:** §2.4 puts the launcher source in the Batch 0 re-freeze amendment. Batch 0 and Batch 4 put it in a dated addition at the Batch 4 checkpoint. The two timings are incompatible. The Batch 0 freeze fixes the interface, and §2.4 treats the source as frozen, so a builder who follows §2.4 would pin source before it exists.
- **Fix:** Correct §2.4 to "its interface pinned in the re-freeze amendment; its source pinned by dated addition at the Batch 4 checkpoint".

### C-10 — Medium
- **Lines:** 3611–3612 (Batch 2: "every invocation, including refusals, appears in a scratch record"); 3618–3620 (Batch 3: record writer, hash chain)
- **Quoted:** "every invocation, including refusals, appears in a scratch record"
- **Problem:** The Batch 2 checkpoint requires a scratch record with event pairs for every invocation. The record writer (PILOT-RUN-RECORD-01), the event-pair format and the hash chain are Batch 3 items. §4 forbids reaching forward into a later batch's components to pass a checkpoint. Either Batch 2 builds an unnamed interim writer, which §4 forbids, or it cannot be verified.
- **Fix:** Name the interim record format in Batch 2 (the logging contract's event-pair schema, written to a scratch file) and state that PILOT-RUN-RECORD-01 framing and chaining come in Batch 3, or move the record-presence check to Batch 3.

### C-11 — Medium
- **Lines:** 3624–3625 (Batch 3: "the chain verifies; the materialised ledger / reproduces identically on re-extraction"); 3663 (Batch 6: "Implement the examiner tooling (§3.7)")
- **Quoted:** "the chain verifies; the materialised ledger"
- **Problem:** The Batch 3 checkpoint needs chain verification and ledger re-extraction. The examiner tooling that performs replay is first built in Batch 6. Either Batch 3 uses a verifier it has not been assigned (a forward reach under §4), or the checkpoint cannot be verified until Batch 6.
- **Fix:** Assign a chain verifier and a re-extraction routine to Batch 3 as Batch 3 components, and say that the Batch 6 examiner tooling reuses them or re-implements them under the same test.

### C-12 — Medium
- **Lines:** 3610–3611 (Batch 2: "refusal mechanics verified at unit level"); 3697 and 3709 (S3)
- **Quoted:** "refusal mechanics verified at unit level"
- **Problem:** The Batch 2 checkpoint checks only refusal paths (forged id, FOUND id, second consumption). A tool that refuses every insertion passes the checkpoint. The positive path, which the spec itself calls required ("S3's first insert must succeed"), is not checked until G1, which may run only at Batch 6 (see C-1).
- **Fix:** Add to the Batch 2 checkpoint: one genuine EXTRACTED result inserts successfully (LEDGER_ENTRY emitted, value returned), and the same result is refused on second presentation.

### C-13 — High
- **Lines:** 3666–3668 (Batch 6: "every [TOOL]/[RULE] step … [MODEL] steps stubbed as not exercised"); 3788–3793 (G5 pass condition)
- **Quoted:** "or names the UNANSWERABLE exceptions with their causes"
- **Problem:** G5 passes if all 13 instances are ANSWERABLE or if any number are named UNANSWERABLE. There is no bound and no required proportion, so a calibration in which 13 of 13 are UNANSWERABLE passes. §5 says an UNANSWERABLE instance "is not a build failure". The calibration's [MODEL] steps are stubbed as not exercised, so ANSWERABLE certifies only the tool and rule steps. The gate can pass while the pilot is not answerable in any instance the model can run.
- **Fix:** Define in Criteria §5.3 (cited, not in this spec) or here: (a) what ANSWERABLE certifies when [MODEL] steps are unexercised; (b) a maximum number or set of UNANSWERABLE exceptions above which G5 fails; (c) that each named exception must be listed in the Stage 6 packet with its cause, and that a 13/13 UNANSWERABLE result fails G5 outright.

### C-14 — Medium
- **Lines:** 3719–3721 (G1 zero-egress: "absence of an available external proxy or connector path"); 3499–3510 (§3.7 zero-egress)
- **Quoted:** "absence of an available external proxy or connector path"
- **Problem:** The spec requires showing absence of an "available" proxy or connector path but gives no procedure for showing it. The environment could have proxy settings in the environment, system configuration, a per-tool config, or a connector registered in the agent. The gate does not say which of these are checked, or what counts as available. The check is also recorded only under G1, while G2–G5 and the Batch 6 full run in the same environment have no environmental check. The build environment in this session has a pre-configured outbound proxy, so this is not hypothetical.
- **Fix:** Enumerate the checks (interfaces and routes; `ip route` and namespace listing; absence of `*_PROXY` variables and proxy config files; absence of connector registrations; a non-loopback connect attempt that must fail, with its output preserved). Require the same check at the start of each gate run and at the Batch 6 full run.

### C-15 — Medium
- **Lines:** 3766–3768 (G3: "SE-1…SE-6 by / structural inspection of the built code"); 3773–3775; 2042–2053 (SE definitions, including SE-6 "no fallback path … anywhere in the insert call graph")
- **Quoted:** "structural inspection of the built code"
- **Problem:** G3 requires SE-1…SE-6 to be shown by structural inspection and by G1's adversarial tests. No inspection method is given. SE-6 is a universal claim over the insert call graph, which a reviewer cannot establish by reading selected code. SE-1 (harness as sole issuer) and SE-3 (subject has no access path) have no adversarial test in S1–S5. A build can meet G3 by a reviewer's sign-off on unstated inspection.
- **Fix:** Specify the inspection: a preserved call-graph listing from the insert entry point, with every reachable branch enumerated and examined, and an examiner checklist per SE property. Add adversarial tests for SE-1 and SE-3 (for example, a subject-side attempt to write the registry or to obtain an extraction result without the harness), or state that these are structural only.

### C-16 — Low
- **Lines:** 3735–3738 (G2 "the test is re-run until a torn tail is genuinely produced")
- **Quoted:** "the test is re-run until a torn tail is"
- **Problem:** The re-run loop has no bound. Because the injector is deterministic (3733–3735, "so the kill lands mid-append deterministically"), a single run is either enough or the injector is not working; a loop adds nothing and can run indefinitely.
- **Fix:** Set a maximum number of attempts and state that a run which produces no torn tail after that many attempts fails G2. Or drop the loop and require a single deterministic run with a check that the tail is present.

### C-17 — Low
- **Lines:** 3532 ("`b107e892…`, `c93eaa19…`"); 3530–3531 ("each section's recorded hash")
- **Quoted:** "`b107e892…`, `c93eaa19…`"
- **Problem:** The Batch 0 checkpoint cites truncated 8-character prefixes. The full digests are in §2.3 at 1812–1813. "Each section's recorded hash" does not say where the per-section hashes are recorded, so the builder must find them.
- **Fix:** Cite the full 64-hex digests (`b107e8926abc5fed…`, `c93eaa1906a068c5…` expanded from 1812–1813) and name the file holding the per-section hashes.

### C-18 — Low
- **Lines:** 3698–3700 (G1 S4: "against a perturbed scratch snapshot")
- **Quoted:** "against a perturbed scratch snapshot"
- **Problem:** Batch 0 makes PILOT-CORPUS-SNAPSHOT-01 a read-only copy. S4 requires a perturbed scratch snapshot but does not say how it is produced or that the frozen copy is untouched. A builder could perturb the frozen copy and break the Batch 0 pin, or make an unlabelled copy whose provenance is unclear.
- **Fix:** State that S4 perturbs a separately created scratch copy by a named operation (for example, one byte flipped in one section), and that the frozen snapshot's hash is re-verified after S4.

### C-19 — Low
- **Lines:** 3656–3657 (Batch 5 redaction test: "contains header or credential material")
- **Quoted:** "contains header or credential material"
- **Problem:** The redaction test is a pass condition but "header or credential material" is not defined here. Whether a value matches needs a rule (field list, pattern set, or both). Without it two examiners can disagree on a capture.
- **Fix:** Name the fields (for example, `Authorization`, `Cookie`, `Set-Cookie`, `X-Api-Key`, plus any token-shaped value pattern) and the pattern rule, or cite the Adapter §3.4 list if it exists.

---

## Cross-reference status (summary)

- Present and consistent: §2.3 (1812–1813, 1822 "Batch 0 stops"), §3.5 point 2 and demonstrations (v)–(ix) (labels present), §3.6 values (3319–3323: temperature 0.6, top_p 0.95, max_tokens 20480, reasoning_budget 16384 under chat_template_kwargs), §3.4 RFC 8785 (2101–2147), §6.3 item 5 (3929), §3.7 zero-egress and loopback text (3483–3510), SE-1…SE-6 (2040–2053).
- Broken: "§3.1(ix)" (3759, see C-5); "§6.4 partial-record shape" (3627, see C-6).
- Heading-level only: §5.3, §5.1(5)/(6) (3330–3332 cite them), §7 steps (not in range).

---

## NOT CHECKED

1. **Lines 136–1696 (amendment-summary history)**: excluded per instruction. Grep hits there were used only to confirm that referenced demonstrations and corrections exist, not to judge any finding.
2. **Lines 1–135 and 3964–4104 (commission, Part 3 baseline evidence, Part 4 freeze disposition, §6.4, §7, scope notes, §6.1 remainder, §6.2, §6.3 body)**: not read. §6.3 item 5 was checked only by its label at 3929; §6.4 only by its heading at 3950. Any claim in §4–§5 depending on §7 role separation was not verified.
3. **§3.5 bodies (2156–3272)**: only lines 2040–2053 and the demonstration labels were read. Whether demonstrations (v)–(ix) cover what the Batch 4 checkpoint lists was not verified line by line.
4. **§3.6 (3273–3394) and §3.7 (3395–3518)**: only grep hits were read. The loopback and proxy rules (3483–3493) were read as hits, not in full. The examiner procedure (3397–3415) was read as hits only.
5. **§2.1–§2.2 and §3.2–§3.4 bodies**: not read. §3.2's "NOT FOUND" and "pilot-manifest:" behaviour (cited by Batch 1, line 3595) was confirmed by grep only.
6. **External documents not in the attachment**: Criteria §§2, 4, 5.1(5), 5.1(6), 5.3, 7.2, 8, 9 (Q3, Q4, Q5); Harness §§1.1–1.5, 2.6, 3.2–3.4, 4.2, 4.4, 4.5, 6, 6.4, 7 (steps 0–6); Adapter §§1.3(e), 1.4, 2.2, 3.2, 3.4, 7; Qualification §4; Plan 01 Stage 5; REVISION-04-NOTE. Every "§x" that points outside this spec was checked for presence in the text only, not for what it says. The definitions of ANSWERABLE, UNANSWERABLE and INCONCLUSIVE were not found in this spec and were not verified (relevant to C-13 and to G2's "INCONCLUSIVE").
7. **Shelf copy**: the commission names the file at github.com/Q420/ainternet-shelf (commit bab720b2, sha256 ebefa4a1…). I read the attachment copy only and did not verify its hash against the shelf. The attachment may differ.
8. **Batch 1 and Batch 4 checkpoints against Qualification §4 precedent and SE-7 demonstration text**: not verified in substance.
9. **Independence of the examiner tooling**: Batch 6 has the builder build the examiner tooling that G4 and G5 rely on. Whether §6.4 or §7 require an independent examiner for that tooling was not checked (see NOT CHECKED item 2).
10. **Runtime behaviour**: no build was run and no gate was executed. All findings are from text.
