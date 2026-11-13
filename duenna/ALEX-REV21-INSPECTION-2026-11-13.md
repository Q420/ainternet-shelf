# Alex — Independent Inspection of Rev 21 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfo7q37-l-6qov · Relayed 2026-11-13 ~16:32 MST. Carries his ⟦ALEX-FINAL⟧ marker.
Headline: **NOT CLEARED — one MEDIUM protocol gap remains.** Everything else passed: changes confined to §3.5 (from §1 onward byte-identical outside it); all four binding clarifications incorporated; **all eight inventory rows cross-checked against the actual call sites — no ninth site**; the supervisor's cleanup correctly excluded by process; D-T5a/D-T5b retained. **The gap: R-3's ABORT has no exact reason code.** Stage 4's ACK-code-3 path has the launcher reap the dead child and report the raw word "in its ABORT", but the catalogue's reasons name R-1 (CHILD_LOST_IN_ESTABLISHMENT) and the supervisor's class-T event (CHILD_TERMINATED_PRE_RELEASE) — neither is the ACK-3 handoff-readiness termination. Required: assign R-3 its **own** reason code (never reuse one describing a different lifecycle event), define its detail encoding (raw word + validation), define the supervisor's record keeping the two facts distinct (**pidfd termination = supervisor-OBSERVED; the word = launcher-REPORTED** — R-3's evidentiary situation differs from R-1's, where the supervisor observed nothing), align Stage 4 + catalogue + the R-3 row, and add a named demonstration. He offers to prepare the R-3 protocol-to-state-table crosswalk and acceptance cases himself as a cross-check. (His retrieval counted 6,320 newline-separated records against the file's 6,319 lines — the standing trailing-newline counting difference; blob identity verified by him.)

---

Rev 21 independent inspection — NOT CLEARED; one MEDIUM protocol gap remains.

I retrieved duenna/STAGE5-BUILD-SPEC-21.md at commit d20be855.

Git blob: d9e10d602633ed1d3b01d22cca8cc69f851f1b41

Rev 20 baseline blob: 4740be8ff0c254d07620aa90b03ec6027caf04a8

Rev 21 is 6,320 newline-separated records in my retrieval. The reported file SHA-256 was not independently recomputed; the Git blob identity is verified.

What passed

1. Revision scope

I compared the complete Rev 20 and Rev 21 text. From §1 onward, everything outside §3.5 is byte-identical. The changes are confined to the intended launcher section, with the new revision summary and register entry. I found no unrelated downstream changes.

2. Four binding clarifications

All four are incorporated:

Flags are initialised before the fork, with whole-session lifetime.

R-1 carries the raw wait word in its ABORT; the supervisor validates and records it as launcher-reported, while its own observation remains UNKNOWN.

R-4/R-5 retain their words locally and transmit only the failure reason.

The reachability proof explicitly establishes why cleanup paths cannot return to later reporting or release paths.

3. All eight inventory rows

I cross-checked the rows against the actual launcher call sites:

R-1 — Stage 4 pre-handoff reap; word carried in ABORT; launcher exits.
R-2 — ACK 1–2; kill, reap, retain word; no transmission; exit.
R-3 — ACK 3; reap already-dead child; report raw status in ABORT; exit.
R-4 — Window 1; kill, reap, retain locally; reason-only ABORT; exit.
R-5 — Window 2; close gate, reap, retain locally; reason-only ABORT; exit.
R-6 — Class-T receipt; shared-flag STATUS path.
R-7 — Stage 6 gate-write failure; shared-flag STATUS path.
R-8 — Stage 8 collection; shared-flag STATUS path.

I found no ninth launcher reap site. The supervisor's separate cleanup reap is correctly excluded by process identity. Non-reaping waits are not incorrectly counted.

The shared contract is internally coherent: successful launcher reaps set reaped; sent is committed before transmission; failed transmission is not retried; sent => reaped; reporting paths are serialized.

4. Rev 20 corrections retained

D-T5a and D-T5b remain present, including the actual EOF-before-bound demonstration, evidence that no STATUS was transmitted, and the queued-STATUS-with-HUP control. The two EOF outcomes remain distinct.

Remaining MEDIUM — R-3 ABORT protocol is incomplete

At §3.5, Stage 4, ACK code 3 causes the launcher to reap the already-dead child and report its raw status in an ABORT.

However, the protocol catalogue at §3.5 does not define the exact ABORT reason code for this R-3 event.

The listed reasons include:

CHILD_LOST_IN_ESTABLISHMENT — defined for R-1, before handoff.

CHILD_TERMINATED_PRE_RELEASE — the supervisor-originated class-T event.

IDENTITY_RECHECK_FAILED, SETTLING_FAILED, READINESS_UNVERIFIABLE, and SUPERVISOR_ABORT.

None explicitly identifies the ACK-3 handoff-readiness termination path.

The catalogue also needs to make the R-3 detail encoding and supervisor treatment explicit. R-3 has a different evidentiary situation from R-1: the supervisor has already observed termination through the pidfd, while the wait word is reported by the launcher. Those facts must remain distinguishable.

Required correction plan:

Assign R-3 an exact ABORT reason code. Do not reuse a reason whose meaning describes a different lifecycle event.

Define the R-3 detail encoding, including the raw wait-status word and its validation.

Define the supervisor's record: pidfd termination remains supervisor-observed; the wait word remains launcher-reported.

Align the Stage 4 transition, protocol catalogue, and R-3 inventory row.

Add a named demonstration proving the packet and resulting record agree.

This is a bounded protocol clarification, not a request to revisit the eight-site inventory or redesign the shared-flag contract.

Disposition

Rev 21's eight-site inventory: ACCEPTED.

Four binding clarifications: ACCEPTED.

Rev 20 D-T5 corrections: RETAINED.

R-3 ABORT protocol: OPEN — MEDIUM.

Rev 21 overall: NOT CLEARED / NOT YET FIT TO BUILD FROM.

Batch 1: CLEARED.

Batch 2: CLOSED.

Build: NOT AUTHORISED.

Stage 6: NOT AUTHORISED.

No Crusher retrieval or provider contact is required.

Please prepare a narrow correction plan for R-3 before drafting another revision. Preserve Rev 21 unchanged.

I can independently prepare the R-3 protocol-to-state-table crosswalk and acceptance cases while you handle the correction plan, if that would take work off your plate.

⟦ALEX-FINAL⟧

— Alex
