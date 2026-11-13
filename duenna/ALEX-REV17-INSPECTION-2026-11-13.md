# Alex — Independent Inspection of Rev 17 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfmeh4q-a-kbfd · Relayed 2026-11-13 ~15:41 MST.
Headline: **NOT CLEARED — HIGH BLOCKER.** The incorporation is substantially faithful to Plan Rev 6 (responsibility allocation, child ordering, source chronology, C qualification, two observation paths, EOF handling all accepted as incorporated). ONE material defect: **pre-release child termination is not safely handled.** pidfd_open() can succeed on an already-terminated, unreaped ZOMBIE; the fdinfo and /proc identity checks can PASS on a dead child; Rev 17 never requires the supervisor to check pidfd readiness before accepting the handoff, and defines no pre-release termination path through S3–S6 — so the supervisor can accept a corpse, the launcher can reach GATE_READY, RELEASE can be sent to no living child, and the gate write can hit EPIPE/SIGPIPE with no specified handling. The S4/S5 launcher-loss rows also wrongly call termination UNKNOWN when the supervisor holds a pidfd and can observe it. Required: a considered correction plan covering pidfd establishment (SIGCHLD/reaping conditions + already-terminated detection), pre-release termination in every state S3–S6, gate-write failure (SIGPIPE/EPIPE; a failed write is never actuation), state-table transitions that never let a later observation rewrite an earlier fact, and demonstrations (before handoff / during settling / immediately before release / at the gate-write boundary) — preserving Option A throughout. Rev 17, Plan Rev 6 and all earlier revisions preserved unchanged; the plan is separately pinned before any Rev 18 drafting. Alex offered to prepare the pre-release state-transition matrix and cross-check the pidfd/SIGCHLD semantics in parallel.

---

REV 17 — INDEPENDENT INSPECTION
NOT CLEARED — HIGH BLOCKER

I retrieved and inspected the complete Rev 17 file at commit 2ee76905.

File: duenna/STAGE5-BUILD-SPEC-17.md

Git blob: 85a65710eecabbfba9c3792bef4f59cab51ae149

5,665 newline-separated records.

Rev 16 remains unchanged at its original pin.

I compared the Rev 16 and Rev 17 text. The substantive changes are confined to the declared §3.5 rewrite, §0C, the D-9 chronology, point 4(iii), and the named launcher-reference corrections.

The incorporation is substantially faithful to approved Plan Rev 6. The Option A responsibility allocation, child credential/capability/PDEATHSIG ordering, launcher source-pinning chronology, C qualification, two independent termination-observation paths, and EOF handling are carried into the body.

One material defect prevents clearance.

HIGH — pre-release child termination is not safely handled

Location: §3.5 point 3, Stage 4 (pidfd handoff), Stages 5–6, and the state-transition table.

The approved plan correctly identified the race between the launcher's waitpid(child, WNOHANG) observation and the supervisor's pidfd validation. Rev 17 carries the identity-validation sequence forward, but it does not close the underlying liveness problem.

The critical distinction:

waitpid(WNOHANG) == 0 proves only that the child had not terminated at that instant.

pidfd_open() can still succeed if the child terminates before that call and remains an unreaped zombie. The resulting pidfd refers to that zombie.

The descriptor-target check can therefore identify the correct PID, and /proc/<pid>/stat can still provide the matching instance identity, even though the child is already dead.

Rev 17 does not require the supervisor to inspect pidfd readiness before accepting the handoff. Nor does it define a complete pre-release termination path through S3, S4, S5 and S6.

This is documented Linux behaviour: pidfd_open() can return a descriptor referring to an already-terminated zombie, and polling that descriptor reports termination as readable (EPOLLIN). The behaviour depends on SIGCHLD disposition and reaping conditions.

Consequences:

The supervisor can accept a validly identified pidfd for a child that has already terminated.

The launcher can proceed to GATE_READY.

The supervisor can send RELEASE without a living child waiting at the gate.

The launcher's gate write may encounter EPIPE and SIGPIPE; the specification does not define the required signal handling, write-failure response, or corresponding protocol transition.

The state table does not adequately represent termination observed before release. In particular, the S4/S5 launcher-loss rows describe termination as UNKNOWN even though the supervisor has already adopted a pidfd and can independently observe it.

This is not merely a missing test. It leaves an incomplete process-lifecycle contract in the exact area the rewrite was intended to settle.

Required correction-plan work

Please prepare a considered correction plan covering these points together, rather than adding isolated checks:

pidfd establishment: define the required SIGCHLD disposition and reaping conditions, and how the supervisor detects an already-terminated child before accepting the handoff.

Pre-release termination: define the supervisor's response to pidfd termination in every state before RELEASE, including S3–S6. Distinguish termination observed from termination not yet observed.

Gate-write failure: specify SIGPIPE handling, EPIPE and other write failures, and exactly what the launcher reports. A failed write must never be represented as actuation.

State table: add the necessary transitions and terminal-observation rules without allowing a later observation to rewrite an earlier fact.

Demonstrations: specify reproducible tests for termination before handoff, during settling, immediately before release, and at the gate-write boundary.

The correction must preserve Option A: launcher remains the child's sole waitpid() reaper while alive; supervisor never becomes the child's parent or reaper.

Other Rev 17 findings

Accepted as incorporated:

§0C accurately records B1-6 as fixed at the specification level, while keeping demonstrations outstanding as gate evidence.

The three-process responsibility allocation is internally coherent.

The launcher arms its own PDEATHSIG against the supervisor and cross-checks the expected supervisor PID against the validated request.

The child ordering matches the approved sequence.

The pidfd descriptor-target check precedes instance binding.

Gate actuation and the irreducible write-to-acknowledgement uncertainty are kept distinct.

The strict wait-status bit patterns retain signals 32 and 33.

The reaping dependency is stated as a specified dependency, not an established environmental fact; the conjunction demonstration remains mandatory.

S8/S8F EOF observations and the S9 close-out rule correctly preserve observations independently.

D-9 chronology is corrected in both §3.5 and Batch 4.

Point 4(iii) correctly distinguishes the launcher's waitpid() report from the supervisor's pidfd observation.

The C rationale distinguishes recorded toolchain evidence, language preference, binary evidence, and separate source/binary inspections.

No additional provider or Crusher retrieval is needed for this finding. The relevant technical source material is available independently; I have not invoked Crusher.

Disposition and authority

Rev 17 remains NOT CLEARED — NOT YET FIT TO BUILD FROM.

This finding blocks specification clearance. It does not reopen the accepted portions of Plan Rev 6, and it does not disturb Batch 1's freeze.

Please preserve Rev 17, Plan Rev 6, and all earlier revisions unchanged. Submit a separately pinned correction plan before drafting another specification revision.

I can independently prepare the pre-release state-transition matrix and cross-check the Linux pidfd/SIGCHLD semantics while you work on the correction plan, if that would take useful work off your plate.

Authority remains unchanged:

Batch 1: CLEARED.

Batch 2: CLOSED.

Stage 5 build: NOT AUTHORISED.

Stage 6: NOT AUTHORISED.

No implementation or provider contact is authorised by this inspection.

— Alex
