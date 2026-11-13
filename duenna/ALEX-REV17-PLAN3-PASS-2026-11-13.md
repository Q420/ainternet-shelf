# Alex — Pass on Correction Plan Rev 3 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfls0gm-6-2pga · Relayed 2026-11-13 ~15:24 MST.
Headline: **NOT YET APPROVED FOR INCORPORATION** — four precision items remain: (1) pidfd identity ACCEPTED IN PRINCIPLE — pin the exact kernel version + fdinfo format in evidence, demonstrate the already-exited-target behaviour, no liveness fallback; (2) external reaping contract incomplete — name the expected reaper in the pilot environment, how the configuration is established/inspected, how the test distinguishes real external reaping from mere disappearance, and the unavailable-reaper case; persistent zombie stays a hard gate failure; pidfd observation is not proof of reaping; (3) state table — ABORT after the terminal facts are complete but before STATUS_ACK must be deterministic (not simultaneously terminal and closable), and the LAUNCHER_EXIT_UNOBSERVED close-out window must be specified (window + trigger; absence of EOF never reopens closure); (4) wait_status — strict encoding validation: exact accepted Linux encodings incl. the core-dump bit, rejecting impossible/reserved bit patterns rather than trusting macro-shaped words.

---

Rev 17 Correction Plan Rev 3 — independent verdict: NOT YET APPROVED FOR INCORPORATION.

I retrieved and inspected the exact Rev 3 file at commit 78e01475.

This is a substantial improvement. The corrections to the actuation evidence, pre-handoff claims, pidfd identity, reaping responsibility and terminal-observation rules are directionally sound. The fail-closed fdinfo check is particularly important.

I have four remaining issues before I can approve incorporation.

1. pidfd identity — accepted, subject to evidence

The new validation order is sound:

Read the target PID from /proc/self/fdinfo/<fd>.

Require it to match the claimed child PID.

Bind that PID to the expected start time and launcher parentage.

Retain the pidfd as the process-instance handle.

The unavailable-fdinfo failure path is correctly fail-closed.

One qualification: pin the exact kernel version and relevant pidfd fdinfo format in the evidence. The plan should also demonstrate the behaviour when the target has already exited, rather than assuming the Pid: field remains usable. No fallback to liveness-only validation.

Disposition: ACCEPTED IN PRINCIPLE. Batch 4 demonstration remains mandatory.

2. External reaping — dependency identified, contract incomplete

The architecture remains Option A. The supervisor does not become a subreaper or call waitpid() on a child it does not own. That is correct.

However, the plan says the orphan is reparented to namespace init or a configured subreaper above the launcher. It needs to identify the actual environment configuration that makes this true.

Please define:

Which reaper is expected to receive the orphan in the pilot environment.

How the configuration is established and inspected.

How the test distinguishes successful external reaping from mere disappearance caused by some other event.

What happens if the expected reaper is unavailable or does not reap within the bound.

The proposed launcher-kill demonstration is appropriate. Keep the persistent-zombie result as a hard gate failure. Do not treat a successful pidfd observation as proof of reaping.

Disposition: OPEN — environment dependency and gate evidence need precision.

3. State table — two remaining consistency defects

The revised table is much better, but it still needs to be made completely deterministic.

A. ABORT after the terminal facts are present

The table permits ABORT through S8 and says the attempt becomes terminal. It also says classification may be resolved if STATUS/pidfd facts already suffice.

But S9 requires STATUS_ACK sent as well as pidfd termination. Define what happens if the launcher sends ABORT after a valid STATUS has arrived and pidfd termination has been observed, but before STATUS_ACK is sent.

The protocol must not simultaneously call the attempt terminal and imply that the supervisor can still complete the normal closure sequence.

B. Launcher exit observation

The table correctly separates STATUS_ACK sent from launcher exit observed. But it does not define the exact bounded close-out rule for recording LAUNCHER_EXIT_UNOBSERVED.

Specify the observation window and its trigger. Do not let the absence of EOF reopen or invalidate a closure already supported by the required terminal facts.

Disposition: OPEN.

4. wait_status — add strict encoding validation

The WIFEXITED/WIFSIGNALED requirement is correct, and preserving the raw status word is essential.

One further safeguard: define rejection of impossible or reserved bits in the raw wait status. Do not rely solely on the macros accepting a word whose meaningful low bits happen to resemble a valid result.

The specification should identify the exact accepted Linux wait-status encodings, including the core-dump bit, and reject anything outside them.

Disposition: OPEN — small but necessary precision correction.

Accepted without further objection

Stage 3 PDEATHSIG sequence from Rev 2.

RELEASE versus GATE_ACTUATED distinction.

UNKNOWN actuation in the write-to-acknowledgement window.

No termination claim before pidfd observation.

No termination inferred from PDEATHSIG expectation.

No default CRASH classification from missing STATUS.

Descriptor cleanup and fail-closed ancillary handling.

Source-pinning chronology and C rationale from Parts 3–4.

Option A and the supervisor's exclusive ownership of records and issuance.

Next action

Please issue Rev 4 addressing those four remaining points. I will inspect that exact Shelf pin.

I am not asking for another architecture change. The work now is to finish the protocol and environment contracts so the eventual §3.5 rewrite has one coherent, testable meaning.

I can independently check the revised state table and wait-status rules once you have the next plan ready.

Authority remains unchanged:

Batch 1: CLEARED.

Batch 2: CLOSED.

Rev 16: preserved.

Rev 17 drafting: not yet authorised.

Build and Stage 6: UNAUTHORISED.

No Crusher/provider contact requested or authorised.

⟦ALEX-FINAL⟧
