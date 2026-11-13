# Agent B1 - Inspection of Stage 5 Build Spec Rev 13, section 3.5 (lines 2156-2700)

Source: /mnt/user-data/attachments/475f6377-dfad-5672-a7f4-a435c6bdea33/581de8c8-attachment.txt
Scope: lines 2156-2700 (supervisor and commitments custody design, points 1-4 and the descriptor-separation block up to the declared destinations).

## Findings

### B1-1 (High) - lines 2172-2174
Quote: "owns the supervisor program"
Problem: The custody argument depends on pilot-supervisor being the only issuer of receipts. The text protects the supervisor program only by ownership. Nothing in this range says that pilot-harness cannot write the supervisor's interpreter, its imported modules, a shared virtualenv, or any path the supervisor resolves at startup (sys.path, cwd, PYTHONPATH). The only placement rule the spec states (protected placement, in the text after 2700, around 2748) covers the harness executable and its interpreter, not the supervisor. A harness-writable module imported by the supervisor would run inside the issuer under pilot-supervisor and could forge receipts. Point 4 also calls the supervisor an "untrusted in-model identity" in the post-2700 text, which conflicts with its role as issuer.
Fix: Extend the protected-placement rule to the supervisor program, its interpreter, and every module it imports: root-owned or pilot-supervisor-owned, with no write for pilot-harness at any path component. The supervisor runs with a fixed sys.path and no cwd entry. Record this in the gate evidence. Add a negative test in which pilot-harness attempts to plant a module on the supervisor's import path and the attempt fails at the OS boundary. State the supervisor's trusted-computing-base status explicitly.

### B1-2 (High) - lines 2218-2228
Quote: "The launcher accepts no arbitrary input"
Problem: The launcher is described as taking no input beyond the validated run identifier and loading "no code beyond the fixed exec". The spec never says what environment (envp), working directory, umask, or signal disposition the child receives. A whole-document search finds no environment rule for the harness. By default execve() passes the launcher's environment, which the setuid launcher inherits from the pilot-supervisor invoker. Variables such as credentials, PYTHONPATH, PYTHONHOME, or PYTHONSTARTUP would then reach the pilot-harness process. This is an unspecified credential transition and an input channel the design does not account for.
Fix: Specify that the launcher calls execve with a compiled-in envp of named variables only (fixed PATH, no PYTHON* variables, no credentials), a fixed cwd outside every protected tree, a fixed umask, and reset signal dispositions and mask. State explicitly which credentials, if any, the harness may receive and through which path. Add a test that reads the harness's /proc/self/environ, cwd and umask and compares them to the declaration.

### B1-3 (Medium) - lines 2221-2224
Quote: "validated against a strict pattern"
Problem: The pattern is not given. The run identifier is later used to build run-directory paths in an identity that can write under runs/, so an underspecified pattern could admit "/" or ".." sequences. Line 2224 also refuses "a different programme", but the programme path is said to be compiled in, so it is unclear what varies. The argument-vector shape is not defined, and argv[0] handling is unspecified. The builder would have to improvise the validation.
Fix: Give the exact regular expression (for example ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$, with no dot and no slash). Fix the exact argc. State that argv[0] is ignored and never used for exec. Name the refusal cases in demonstration (v): argc 1 and 3, argv[1] of "../x", "a/b", an empty string, 65 characters, and a string containing NUL.

### B1-4 (Low) - lines 2243-2246
Quote: "Threads field of its /proc status equal to 1 at launch"
Problem: "At launch" is undefined. It is unclear whether the reading is taken before the fork or after it, which process reads it, and when. A single-threaded process reads Threads=1 at every moment, so the record proves nothing unless the time and reader are fixed.
Fix: Define the reading point (for example, immediately before fork, read by the launcher from /proc/self/status) and the reader, and record the value in the launch record.

### B1-5 (Medium) - lines 2247-2258
Quote: "a probe invocation ... must observe effective uid 0"
Problem: The build stops if the probe fails, so its method must be exact. The production launcher accepts only a run identifier and spawns a harness, and the spec does not say how a probe invocation observes effective uid inside the privileged window without spawning, or whether it runs the test build or the production binary. The nosuid and no_new_privs checks have no stated observation source either.
Fix: Choose one probe method and name the observation source: for example, the supervisor reads the launcher's /proc/<pid>/status Uid line and NoNewPrivs field, and /proc/self/mountinfo for nosuid, during a launch that aborts at the child's first comparison. Say which binary the probe runs against, and record the observation source in the gate evidence.

### B1-6 (High) - lines 2259-2261, 2267-2271, 2540-2545, 2572-2574, 2615-2616 (also 2232-2234)
Quote: "the parent runs as the run's supervisor"
Problem: The text makes the launcher process the parent of the child. Line 2267 has the parent capture its own getpid(), and the child's waitpid() relationship is held by that parent (2541). After release, the parent "performs every issuance itself" (2543-2545), and the launcher "remains alive until the child's lifecycle completes" (2232-2234). Yet the launcher is specified as a minimal pinned program whose code "contains no commitment-writing operation and no path to the commitments/ store" (2572-2574), which "exists for the milliseconds of one spawn" (2615-2616). The supervisor driver is said to invoke the launcher (2259-2261), which would make the driver, not the launcher, the parent. These cannot all hold. The builder would have to invent the handoff from launcher to supervisor, and the invariant at 2548-2553 (supervisor established before work begins) depends on it.
Fix: Specify the handoff explicitly. After the gate release, the launcher performs a plain exec (same pid, same sole thread, no credential change, subject to the exec condition in the following block) of the pinned supervisor program at a fixed protected path. The supervisor then holds the child relation, the PDEATHSIG thread, and waitpid(). Amend 2571-2574 and 2615-2616 so the launcher's pinned code is limited to the spawn sequence plus that exec. Add a test that the launcher reaches no commitment-writing code without that exec.

### B1-7 (Low) - lines 2262-2265
Quote: "no other process holds either end"
Problem: pipe2() creates both ends, and fork() copies both into the child. The child holds the write end until its exhaustive close, which occurs only after arming (2392-2399). The sentence is false across fork, and the EOF semantics at 2410-2412 depend on the child closing that copy before it blocks. The sparing rule "sparing the gate descriptor" (2399) also does not say which descriptor number is the read end.
Fix: Rewrite as: "the child inherits both ends across fork and closes its write-end copy before blocking; the gate read-end number is recorded at creation." Add a check that the child's /proc/self/fd holds no write end to the gate at the moment it blocks.

### B1-8 (High) - lines 2281-2282, 2285-2288, 2415-2418
Quote: "clears its supplementary groups"
Problem: Clearing supplementary groups is named but neither the call nor its order relative to setresgid()/setresuid() is given, and it is never read back. The uid/gid read-back covers only the three uid and gid values (2285-2287). The child keeps any supplementary groups inherited from the pilot-supervisor invoker. If pilot-supervisor is among them, the running harness is a member of the group that owns the 4710 launcher, so the group-execute control stated at 2193-2195 does not hold for the running process. The group-separation evidence named at 2199 reads group membership from the operating system, which is not the same as the child's runtime group set. The parent (2415-2418) has the same gap.
Fix: Require setgroups(0, NULL) before setresgid() and state that order. Read back getgroups() in both child and parent and require an empty set. Record the observed group set in the launch evidence. Add a test that, with the child's runtime group set as observed, a mid-run attempt by the harness to execute the launcher fails at the OS boundary.

### B1-9 (Medium) - lines 2302-2312
Quote: "from 0 to the maximum the kernel supports"
Problem: The "maximum the kernel supports" has no stated source, so the Method B loop is not reproducibly defined. The "all three sets must be empty" rule (2312) names CapEff, CapPrm and CapAmb only. CapInh and CapBnd are neither required nor excluded, and the spec does not say why. A builder or examiner cannot tell whether a nonzero CapInh or CapBnd is a launch failure.
Fix: Name the source for the maximum (/proc/sys/kernel/cap_last_cap). Either require CapInh and CapBnd to be empty as well, which costs nothing and matches the design's "no capability" claim, or state that they are recorded but not gating and give the reason in one sentence.

### B1-10 (Low) - lines 2346-2349
Quote: "cleared whenever the process changes its effective user or group id"
Problem: The text attributes this behaviour to prctl(2). The man page documents clearing of PDEATHSIG on fork() and on exec of set-user-ID, set-group-ID, or file-capability binaries. It does not document clearing on a uid or gid change. The ordering argument is therefore supported by a citation that does not say what is claimed. The design remains safe because arming follows the transitions and the read-back at 2340-2345 verifies the setting, but the stated basis is wrong.
Fix: Cite the kernel source for the uid-change clearing (commit_creds) or reword as observed behaviour verified by the PR_GET_PDEATHSIG read-back. Add a read-back immediately after the exec, in the harness, to confirm the setting survived.

### B1-11 (Low) - lines 2545-2548
Quote: "The privileged window performs no file writes at all"
Problem: The list of acts in the "privileged window" includes "the gate release", but 2447-2448 has the parent release the gate after its own privilege drop and capability read-back (2420-2433), which is outside the privileged window. The list also omits the pre-fork expected-parent capture and the setgroups step, which are privileged acts. The window boundary is therefore not defined consistently.
Fix: Define the privileged window explicitly by its start and end points (for example, from the pre-fork capture until the parent's setres*() drop completes), and list the acts that fall within it in that order.

### B1-12 (Medium) - lines 2555-2560
Quote: "read access to runs/ granted to pilot-supervisor"
Problem: The text requires the supervisor to read the record file directly, but runs/ is owned by pilot-harness (2177-2178) and the mechanism that grants pilot-supervisor read-only access is not stated (group, other, or ACL). Granting read through "other" makes the directory readable to every account. In addition, the supervisor reads a path inside a harness-owned directory, so the harness can replace that path with a symlink, a FIFO (blocking the issuer), or a hard link while the supervisor is reading, and the bytes hashed for the receipt may come from more than one object or read.
Fix: Specify the grant (for example, an ACL granting pilot-supervisor r-- on the record file only, or a group that contains pilot-supervisor and not pilot-harness). Require the supervisor to open the record with O_NOFOLLOW, verify S_ISREG and st_nlink == 1, read it once through a single descriptor, and compute every hash from that one buffer. Reject the run if any check fails.

### B1-13 (Low) - lines 2658-2667
Quote: "an invariant of the supervisor's own design, not a hope"
Problem: The supervisor-side invariant (no open writable descriptor to commitments/ or issuance-record.jsonl at launch) is asserted but never checked. Test (vi) arranges a hazard on the child side only. Because the launcher, as the privileged parent, inherits the supervisor's full descriptor table before the drop, a writable handle inherited into the privileged process is not excluded by any check. The pinned claim that the launcher performs no file writes while privileged holds only if the invariant holds.
Fix: Require the supervisor to enumerate /proc/self/fd before each launch and abort, with a run-log record, if any descriptor resolves into commitments/ or to issuance-record.jsonl in a writable mode. Add this check to the gate evidence.

### B1-14 (Medium) - lines 2669-2703 (chiefly 2685-2695)
Quote: "that match must establish the pipe's identity"
Problem: The spec requires identity verification of retained descriptors but does not say how identity is established. It says the check resolves "the /proc/self/fd/ target" (2686-2687). That readlink returns a path string, not an object identity. For a regular-file log, a rename, unlink (shown as "(deleted)"), or a second hard link can give a path that looks correct while the object differs. For pipes the spec requires "identity" but does not say to compare fstat() st_dev and st_ino to the pipe ends the supervisor holds. The declared access mode is also incomplete: fd 0 is "/dev/null, or a read-only pipe" (2675) with no mode for /dev/null, and the write-only mode for fds 1 and 2 is implied, not declared.
Fix: State that verification uses fstat() (st_dev, st_ino, and st_rdev for character devices) compared with the object recorded at creation. Declare the access mode for each of fds 0, 1 and 2 (fd 0 O_RDONLY; fds 1 and 2 write-only). For a regular-file log require st_nlink == 1 and an inode not equal to any inode in commitments/. Define "cannot resolve and classify" as an abort with the run-log record.

### B1-15 (Low) - lines 2201, 2212, 2696
Quote: "Alex's correction A"
Problem: Normative text carries review provenance: reviewer names, revision tags such as "(Rev 12, Claude's finding 3)", and a ticket identifier "pb-mweedh0x". The spec states that the normative text governs, but these tags are not testable, they go stale, and they make the reader cross-read the amendment history to know what a clause requires.
Fix: Move provenance to the amendment summary. Keep the normative clauses self-contained, with only section references and pinned hashes.

## Cross-reference checks performed (no finding)
- "§6.3 item 4" (line 2216): a section 6.3 exists (heading at line 3876). Its item 4 content was not read.
- "(v)–(ix)" and demonstration (ix) (line 2622): demonstration (ix) exists in the normative SE-7 list (line 3217).
- "§3.7" (line 2188): a section 3.7 exists (line 3395).
- "Harness §2.6", "Harness §8 Q10", "Harness §2.4" (lines 2158, 2187): these refer to the external Harness document, which is not in the attachment, so they were not verified.

## NOT CHECKED
- Lines read in full, in scope: 2156-2700 (545 lines), read in four chunks (2156-2405, 2406-2655, 2656-2905, 2906-3155, the last three overlapping the out-of-scope portion).
- Lines 2701-3155 were read in the same chunked reads but are outside this agent's assigned scope. No findings were produced for them. They include the exec-condition block, identity continuity layers (1)-(3), the pre-release re-check, the capability-state claims, the issuance points 5-9, the SE-7 demonstrations (i)-(viii), and the start of the demonstration (ix). Issues noticed in passing there, not assessed or counted, for the agent covering that range: the receipt and issuance-record write order and atomicity (2957-2961), the TERMINAL receipt being computed while the harness may still be writing (2932-2939), the examiner verdict for a run with START but no TERMINAL or CRASH after supervisor death (2941-2943), the test build differing from the production launcher (3124-3127), and the phrase "code-order inspection" being accepted for the fail-closed capability branch (3113-3121), which conflicts with the "not code's politeness" rule at 2998-3000.
- Lines 2156-2700 claims that depend on external facts were not verified against live behaviour: Linux clearing of PDEATHSIG on uid change (B1-10), capget() and PR_CAP_AMBIENT semantics (B1-9), close_range() availability, and /proc/self/fd readlink behaviour (B1-14). These are reasoned from knowledge of Linux and were not tested on the target kernel (6.18).
- The Harness document, the gate numbers G1-G5, and §2.1 (the builder must stop and ask) are referenced but not in the attachment or not in range; they were not verified.
- Whether the pinned launcher source and the sha256 pin exist: they are deferred to a dated addition at Batch 4 (line 2211), so not checkable now.
- Memory was not consulted; it contributed nothing to these findings.
