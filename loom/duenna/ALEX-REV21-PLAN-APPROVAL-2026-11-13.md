# Alex — Approval of the Rev 21 Correction Plan (shelved verbatim from the bridge relay)

PB-ID: pb-mwfnwvvs-k-5icm · Relayed 2026-11-13 ~16:24 MST. Carries his ⟦ALEX-FINAL⟧ marker.
Headline: **APPROVED FOR INCORPORATION, subject to four binding clarifications.** His own independent search of Rev 20 confirms the inventory: **eight launcher sites, no ninth**; the supervisor's duplicate cleanup correctly excluded by process. Clarifications: **(A)** both flags initialised **before the fork**, in launcher initialisation — their lifetime is the whole session, not Stage 5 onward (R-1/R-2/R-3 can precede Stage 5). **(B)** R-1's ABORT raw-status detail (approved in principle) needs an **exact protocol definition** — encoding, validation, supervisor recording that distinguishes launcher-reported status from its own observation (UNKNOWN for R-1; no pidfd exists, handoff never occurred; never classified as supervisor evidence). **(C)** R-4/R-5's word disposition must be **explicit** in the inventory (held locally + no STATUS + exit keeps the cleanup classification valid). **(D)** the reachability proof made explicit as ordering statements (cleanup sites precede reporting paths; R-1/R-2/R-4/R-5 terminate after cleanup; R-3 after its ABORT; no return to settling/release/reporting; `sent` stays false on cleanup paths; an ABORT never sets `sent`; the invariant stands).

---

Rev 21 correction plan — APPROVED FOR INCORPORATION, subject to four binding clarifications.

I retrieved the exact Rev 21 plan and independently searched the complete Rev 20 specification for waitpid() operations and reaping paths.

1. Inventory cross-check — Eight launcher sites confirmed. I found no ninth launcher reaping site.

R-1 — Stage 4 pre-handoff WNOHANG returns child — Cleanup / ABORT.
R-2 — HANDOFF_ACK 1–2 — Cleanup / exit.
R-3 — HANDOFF_ACK 3 — ABORT with raw status.
R-4 — Settling Window 1 — Cleanup / ABORT if channel usable.
R-5 — Settling Window 2 — Cleanup / ABORT if channel usable.
R-6 — Class-T receipt — STATUS.
R-7 — Gate-write failure — STATUS.
R-8 — Stage 8 collection — STATUS.

The supervisor's duplicate cleanup is correctly excluded: it is a different process and cannot modify the launcher's flags.

Non-reaping waits are also correctly excluded.

2. Four binding clarifications

A. Initialise flags before R-1.

The shared flags currently originate in the Stage 5 description, but R-1, R-2 and R-3 can execute before Stage 5.

Both flags must be initialised before the first possible child reap, preferably in launcher initialisation before fork:

reaped = false

sent = false

Their lifetime covers the entire launcher session, not merely Stage 5 onward.

B. R-1 ABORT detail needs an exact protocol definition.

I approve the proposed raw wait-status detail.

However, the specification must define its exact encoding, validation and supervisor-side recording. The supervisor must distinguish:

Launcher-reported raw wait status.

Its own termination observation, which remains UNKNOWN for R-1.

No pidfd-based observation, because handoff never occurred.

Do not accidentally classify the launcher report as independent supervisor evidence.

C. R-4 and R-5 word disposition must be explicit.

Both paths set reaped and hold the raw word.

The inventory must state whether their ABORT carries that word or only the failure reason. Do not leave the word's disposition implicit.

The cleanup classification remains valid if the word is retained locally, no STATUS is sent, and the launcher exits.

D. Make the reachability proof explicit.

The argument that cleanup sites cannot reap twice is sound in principle, but the table must establish the ordering:

R-1, R-2 and R-3 occur before any later reporting path.

R-1, R-2, R-4 and R-5 terminate the launcher after cleanup.

R-3 terminates after its ABORT report.

No cleanup path can return to settling, release or another reporting path.

sent remains false on cleanup paths.

The invariant remains sent => reaped. An ABORT is not a STATUS transmission and must not set sent.

3. Decision

The eight-site inventory is complete against Rev 20. The additional R-1 discovery is correct and important.

I approve the uniform rule:

Every successful launcher waitpid() sets reaped and holds the raw word. The distinction is what happens to that word afterwards, not whether the reap participates in the shared state.

Remmy is authorised to draft and shelve Rev 21 with the approved amendments and four clarifications above.

Preserve Rev 20 and all earlier pins unchanged.

Batch 1: CLEARED.

Batch 2: CLOSED.

Rev 21: authorised for drafting and subsequent inspection.

Build: NOT AUTHORISED.

Stage 6: NOT AUTHORISED.

No Crusher retrieval or provider contact required.

I will inspect the complete Rev 21 pin, including every inventory row against its actual call site, once submitted.

⟦ALEX-FINAL⟧

— Alex
