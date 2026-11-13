# Alex — Approval of the Rev 18 Correction Plan Rev 4 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfmwfxl-e-4oxr · Relayed 2026-11-13 ~15:55 MST.
Headline: **APPROVED FOR INCORPORATION.** The Rev 3 HIGH is resolved: the reaped-first race uses observable supervisor events exclusively (received-and-validated, never in-transit inference); the launcher's reaped/sent states prevent duplicate reaping and reporting; his six-scenario matrix cross-check passes in full. **One binding clarification for the Rev 18 draft** (no reopening of the plan): a STATUS **received but not yet validated** when the termination observation is processed does **not** meet the suppression condition — the supervisor commits to class T, and the already-received STATUS is retained and validated as the one permitted class-T STATUS (never discarded, never counted twice, never a second message); event processing must be deterministic regardless of buffering/scheduling order. Authorisation: draft the specified Rev 18 amendments and shelve for full independent inspection — not approval of Rev 18, no implementation/build/Stage 6. Alex offered the independent protocol cross-check (S3–S6 table, ABORT lifecycle, four termination demonstrations) when the draft is shelved.

---

REV 18 PLAN REV 4 — APPROVED FOR INCORPORATION
APPROVED

I retrieved and inspected the complete plan at commit 460a5563.

File: duenna/REV18-CORRECTION-PLAN-REV4-2026-11-13.md

Git blob: a656ec902947fbcc5cd671467dde14838a890bdd

Rev 3, Rev 2, Rev 1, Rev 17 and Plan Rev 6 remain unchanged.

The Rev 3 HIGH finding is resolved.

The reaped-first race now uses observable supervisor events exclusively. The supervisor does not infer whether STATUS is in transit. Its decision depends on whether STATUS has already been received and validated when it processes the termination observation.

The launcher's separate reaped-state and sent-state correctly prevent duplicate reaping and duplicate reporting.

Matrix cross-check

STATUS received and validated before termination is processed — record STATUS; no ABORT — PASS.
STATUS sent but not yet received — commit class-T ABORT; accept STATUS under class T — PASS.
Launcher reaped but has not sent STATUS — class-T ABORT triggers its one STATUS — PASS.
Class-T ABORT arrives after STATUS was sent — reporting no-op; no second STATUS or reaping — PASS.
Second STATUS — record protocol violation — PASS.
Class-F ABORT followed by STATUS — retain fire-and-close violation rule — PASS.

Binding clarification for the Rev 18 draft

There is one event-ordering detail I want made explicit in the specification, without reopening Plan Rev 4.

If STATUS has been received by the supervisor but has not yet been validated when the termination observation is processed, the supervisor has not met the stated condition for suppressing ABORT.

Therefore:

It commits to class T.

The already-received STATUS is retained and validated as the one permitted class-T STATUS.

It must not be discarded, counted twice, or treated as a second message.

Event processing must produce one deterministic outcome regardless of buffering and scheduling order.

This follows the approved received-and-validated rule. It closes the small implementation ambiguity without changing the plan's architecture.

Disposition

Rev 18 correction plan Rev 4 is APPROVED FOR INCORPORATION.

Remmy is authorised to draft the specified Rev 18 amendments and shelve the resulting specification for full independent inspection.

This approval does not approve Rev 18 itself, authorise implementation or a build, or open Stage 6.

I can take the independent protocol cross-check off your workload when the draft is shelved, including the S3–S6 transition table, ABORT lifecycle, and all four termination demonstrations.

Authority unchanged:

Batch 1: CLEARED.

Batch 2: CLOSED.

Rev 17: NOT CLEARED.

Rev 18: awaiting full specification inspection.

No implementation, build, or Stage 6 authorisation.

— Alex
