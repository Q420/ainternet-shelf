# Agent B2: independent inspection of Stage 5 build spec Rev 13, lines 2701-3272

Source: /mnt/user-data/attachments/475f6377-dfad-5672-a7f4-a435c6bdea33/581de8c8-attachment.txt
Lines read in full: 572 (2701-3272 inclusive, in three chunks).

Cross-reference checks used Grep over the whole attachment for: `nosuid` / `no_new_privs`, `Window 1/2`, `Batch 0`, `anchor`, `SE-7`, `G2`/`G3`, `step 0`, `allowlist`, environment/PATH/PYTHON terms, launcher mode, `PR_SET_PDEATHSIG`, `setres*`, `write end`, `release byte`, and the §3.5 / §3.7 / §5 headings. Only pre-2701 text was viewed where noted under NOT CHECKED.

## Findings

### B2-1 (High): harness can reach root through setuid binaries; no no_new_privs before exec
- Lines: 2761-2762 ("OS permissions genuinely prevent it"); 2802-2805 ("why the harness process cannot gain capabilities"); 2813-2815 ("the launch proceeds only if all three are empty"); 3083-3084 (`no_new_privs` checked only as a launcher-side hazard).
- What is wrong: Layer (1) says the untrusted identities `pilot-harness` and `pilot-supervisor` cannot modify the protected tree, because OS permissions prevent it. That holds only while neither identity can gain capabilities later. The spec argues about the exec target's file capabilities and the ambient set at the launch exec only. Nothing requires the child to set `PR_SET_NO_NEW_PRIVS` before its `execve`, and nothing forbids the harness, or the supervisor, from executing a setuid-root program already on the host. If one exists and is executable by the identity, it yields root, which can then rewrite the protected tree, `commitments/`, and the issuance record. Test (i) does not catch this, because it tests only four named operations as `pilot-harness`. The `no_new_privs` mentions at 2255, 3083-3084 and 3580 apply only to the launcher's own inherited flag. The grep found no requirement for the harness child.
- Fix: In the child, after the transitions and the capability read-back, and before the gate release, set `prctl(PR_SET_NO_NEW_PRIVS, 1)`. Read it back with `PR_GET_NO_NEW_PRIVS` and `/proc/self/status` `NoNewPrivs`, require `1`, and record it in the gate evidence beside the six capability values. Add a demonstration: as `pilot-harness`, the harness executes a setuid-root test binary and the attempt fails. Also add a probe that no setuid-root binary is executable by `pilot-harness` or `pilot-supervisor`, or record the `nosuid` status of every filesystem they can reach.

### B2-2 (Medium): harness script's identity and content are outside every identity check
- Lines: 2711-2714 ("where the fixed harness path is a script"); 2826-2829 (records identity "for the executable and for the interpreter alike"); 2893-2894 (invocation is "interpreter-mediated").
- What is wrong: When the fixed harness path is a script, the kernel runs the interpreter, and the interpreter then opens the script by path after the release. The identity records at 2826-2829 and the re-check at 2840-2844 cover only the executable and the interpreter. The script itself is never identity-checked and never hashed, so its replacement or rewrite is not detected by the pre-launch check or the release re-check. The protection for that path is layer (1) alone.
- Fix: Record `st_dev`, `st_ino`, mode, capability set and a SHA-256 digest for the script as well. Include the script in the pre-launch check and the pre-release re-check. Either pass the script to the interpreter through a verified descriptor, or state that the interpreter re-reads it and that the digest is checked again afterwards.

### B2-3 (Medium): the identity comparison cannot see content change or inode reuse, yet the spec claims detection
- Lines: 2858-2861 ("is detected by it: the identity comparison"); 2880-2883 ("the object the re-check verified is the object the exec runs"); 3223-3225 (scenario (ix)(a) is a replacement, not an in-place write).
- What is wrong: `(st_dev, st_ino, mode, capability set)` does not identify an object's content. An in-place rewrite keeps the inode. A delete and re-create can reuse the inode number and copy the mode bits. Neither case fails the comparison, so the claim that a substitution "at or before" the re-check is "detected" is overstated. The phrase "the object ... is the object" equates an identity tuple with an object.
- Fix: Add a SHA-256 digest of the executable, the interpreter and the script to the freeze record. Recompute it at the pre-launch check and the pre-release re-check, on the same opened descriptor used for the identity stat. Add an in-place-rewrite case and an inode-reuse case to demonstration (ix). Otherwise narrow the claim to "identity substitution".

### B2-4 (Medium): protected-placement audit runs only at freeze, not at each launch
- Lines: 2705-2706 ("verified at build time and again before every launch"); 2829-2835 (path-component audit recorded "at the freeze"); 2822-2824 (resolution repeated at each checkpoint); 3249-3258 (scenario (ix)(c) tests the audit only at freeze).
- What is wrong: The launch-time identity records cover the leaf executable and interpreter only. No directory component's owner, mode or group is re-checked at pre-launch or at the pre-release re-check. Layer (1) depends on every component being root-owned and not writable by the untrusted identities, so that precondition is never re-established for each launch, despite the wording at 2705-2706.
- Fix: Repeat the full component audit (owner, group, mode, and ACL / extended attributes) for both resolved paths at every pre-launch check and at the pre-release re-check. Record each component's `st_dev`/`st_ino`/mode in the run's pre-launch record. Add a case where a component is made group-writable after freeze but before launch, and require the launch to refuse it.

### B2-5 (Medium): descriptor-destination check compares paths, not inodes
- Lines: 3056-3060 ("resolved destinations (`/proc/self/fd/` targets)"); 3061-3065 (negative case compares path); 2918-2921 (retained set).
- What is wrong: The check reads the path string under `/proc/self/fd/` and compares it to the declared set. A writable fd whose inode is also reachable under an unprotected name (hard link, or a bind mount, or a path that has been renamed) passes this check. Scenario (vi) then accepts a child that writes through fd 1 into a protected inode. Descriptors `0`/`1`/`2` are excused from the write probe, so this route is not closed by the probe either.
- Fix: For fds `0`/`1`/`2`, compare `(st_dev, st_ino)` of the resolved object against the set of protected identities: every file under `commitments/`, `issuance-record.jsonl`, and the protected installation tree. Reject any match. Add a scratch test in which the stdout target is a hard link to a protected scratch inode under an unprotected name, and require the abort.

### B2-6 (Medium): issuance record ordering and crash recovery are undefined
- Lines: 2931 ("then appends its issuance entry"); 2959-2961 ("written by the supervisor at the moment of issuance"); 2968-2970 ("a receipt with no corresponding entry" is a custody finding).
- What is wrong: The receipt is written first and the entry appended second. A supervisor crash between the two leaves a genuine receipt with no entry. Under 2968-2970 that is a custody finding, though the supervisor did issue it. The spec gives no write order that avoids this, no recovery rule, and no handling of a torn final line in `issuance-record.jsonl`.
- Fix: Define the order explicitly, for example: write the entry, then `fsync`, then write the receipt, then `fsync`. Or define the reverse order and the examiner's treatment of an entry without a receipt. Define how a torn trailing line in the issuance record is handled (truncate-and-log, or refuse). Add a supervisor-kill-between-writes case to the test list.

### B2-7 (Medium): no receipt rule for a child that exits after the terminal event but before the file is closed
- Lines: 2933-2934 ("and the record file closed"); 2941-2943 (CRASH applies "without** a terminal event having been flushed").
- What is wrong: TERMINAL requires the record file to be closed, but the spec never says how the supervisor observes that. CRASH requires that no terminal event was flushed. A child that flushes `RUN_CLOSED` and then dies before closing matches neither rule, so no receipt is defined for it. The spec also does not say what observation counts as "closed".
- Fix: Define the observation in terms the supervisor can make: TERMINAL if the child exits with status 0 after a terminal event was flushed, computed over the file's bytes at exit. CRASH in every other case. Add a test for a child that dies between flush and close.

### B2-8 (Medium): when the supervisor itself dies after release, no receipt is defined
- Lines: 3151-3154 ("even though no parent survives to reap it"); 3158-3164 (post-release parent death: the child's termination must be shown); 2941-2943 (CRASH is issued by the supervisor on observation).
- What is wrong: After a post-release parent death the supervisor is gone, so no CRASH or TERMINAL receipt is issued. The run has a START receipt and no ending. The spec does not say how the examiner treats that state, and the test at 3158-3164 requires only the child's termination to be shown.
- Fix: Define the examiner's outcome for a START with neither TERMINAL nor CRASH (for example, an "unterminated run" custody finding, with the backstop's kill recorded in the run log). Add that outcome to the examiner's criteria and to the post-release test's expected evidence.

### B2-9 (Medium): production launcher's freedom from test hooks is asserted, not verified
- Lines: 3124-3126 ("a test-only build feature" "compiled out of the production launcher"); 3101-3103 ("the production launcher contains no such feed").
- What is wrong: The spec states that the fault-injection hooks are compiled out of production. Nothing requires the deployed launcher's identity to be recorded, nor that the hook is absent from that binary. The fault-injection evidence from the test build therefore does not establish properties of the deployed binary.
- Fix: Require the production launcher's SHA-256 and mode to be recorded at Batch 0. Require a check that the hook symbols are absent from that binary, for example by `nm` or `objdump` output recorded as gate evidence. Require that the production build hash equals the source pin used for the test build apart from the feature flag.

### B2-10 (Medium): code-order inspection offered as a fallback for the fail-closed capability cases, with no justification required
- Lines: 3113-3121 ("Where a test build cannot interpose the"); 3180-3183 and 3211-3216 (similar fallback for setup-window timing).
- What is wrong: The same test build already has the synthetic-observation hook used in demonstration (viii). The spec does not require the builder to show why the hook cannot be used on a given side. A builder can therefore assert inability and satisfy the fail-closed obligation by reading code, which is weaker evidence than the test the obligation asks for.
- Fix: Allow inspection only with a recorded reason and the inspected source's SHA-256, and state that the capability fail-closed cases must be run as tests. If inspection is kept, require the builder to attach the actual instruction-level evidence, not only the pinned sequence.

### B2-11 (Medium): the harness's interpreter environment, working directory and `sys.path` are unspecified
- Lines: 2893-2894 ("The harness's invocation is interpreter-mediated"); 2710-2714 (interpreter binary identified but its launch form not).
- What is wrong: Whole-spec search finds no rule for the environment passed to the harness child, its working directory, `PYTHONPATH`-type variables, interpreter flags, or whether a `#!/usr/bin/env` line resolves the interpreter through `PATH`. Any of these lets the process started under `pilot-harness` load code the identity checks never saw. The builder would have to improvise these choices.
- Fix: State the child's environment as a fixed, scrubbed allowlist (with `PATH` absent or fixed to the protected tree). Specify the interpreter as an absolute path with isolation flags (`-I -S` or equivalent), a fixed working directory on the protected tree, and no `env` shebang. Add these to the pre-launch record, and add a demonstration that a planted module in the working directory is not imported.

### B2-12 (Low): child's copy of the gate write end is not closed by name
- Lines: 2264-2265 ("no other process holds either end"); 2410-2411 and 3136-3137 (end-of-file depends on the write end being closed).
- What is wrong: Immediately after the fork, the child holds a copy of the write end, so the statement at 2264-2265 is true only after the child closes it. The sequence at 3193 says only "close; gate", which does not name the write end. If the child kept it, end-of-file would never occur.
- Fix: Name the write end as the first descriptor the child closes after the fork, and state it in the pinned sequence.

### B2-13 (Low): fail-closed behaviour for `getcap` and `stat` is not stated
- Lines: 2719-2721 (`getcap` output "preserved as read"); 2726-2727 ("`getcap` reports no capabilities").
- What is wrong: The text does not say that a non-zero exit, an unreadable attribute, or an empty output from an error is a failure. An empty result could be read as "no capabilities" when the check did not run.
- Fix: State that a non-zero exit from `getcap` or `stat`, or any read error, is a launch failure. Record the exit status with the output.

### B2-14 (Low): group-separation test relies on undefined terms
- Lines: 3071-3075 ("any group conferring `pilot-harness` privilege"; "`/etc/group`" as an alternative source).
- What is wrong: "Privilege" is not defined, so the set of groups to test cannot be determined from the text. Reading `/etc/group` and reading `getgrouplist` can disagree under NSS sources such as LDAP or SSSD. The spec allows either without saying which governs.
- Fix: Define the set of groups to be tested as those with write or execute rights on any protected object. Use `getent group` (NSS) as the single source, and record the source in the gate evidence.

### B2-15 (Low): amendment tags inside normative text
- Lines: 2757 ("claim corrected, Rev 09"); 2787-2788 ("(Rev 10)"); 2857 ("corrected, Rev 09").
- What is wrong: Normative clauses carry revision markers. A builder can read the tags as conditions or as superseded text, which makes the normative requirement harder to test. The instruction to ignore amendment history applies to the summary only, so the markers in clauses should not be read as normative.
- Fix: Move the revision references into the amendment summary and leave the clause text clean.

## NOT CHECKED

- Lines 2155-2700 (the start of §3.5 and points 1-4) were not read. Claims here that depend on them are checked only by Grep: the "Window 1" and "Window 2" definitions (2454-2476), the release-byte order (2447-2449), the `setres*` ordering and partial-failure rule (2283-2290), and the allowlist definition (2262-2267). Findings that rely on those lines should be re-checked against the full text.
- "Point 4" (cited at 2777-2779) was not read.
- Cross-references to external documents were not verified. The Harness §2.6 quotation at 2979-2980 ("anyone with write access to the whole record file") does not occur in this attachment, so its source is outside the supplied file. Likewise Harness §4.5 SE-7, Harness §7 step 0, Criteria §7.2(6), and the Stage 0 ("Ben's index rule") reference were checked only as names, not content.
- §3.7 (line 3395 onward) and §5 gate definitions G2 and G3 (line 3681 onward) were not read. The cross-references to them at 3012 and 2988 were checked only for existence.
- Lines 2701-3272 read in full: yes. Not evaluated: amendment-summary history (ignored per instruction).
- Kernel behaviour (PR_SET_PDEATHSIG and thread semantics, `protected_hardlinks`, setuid handling of interpreters, `getcap` on namespaced capabilities) was reasoned from general Linux knowledge and not tested against this build.
- The file FINDINGS-LOG.md in the review output directory was not opened. It is not part of the assigned source.
- Memory was not consulted for this task. The findings draw only on the attachment.
