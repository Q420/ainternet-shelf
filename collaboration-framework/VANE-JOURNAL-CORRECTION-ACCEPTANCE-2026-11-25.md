# VANE — JOURNAL CORRECTION ACCEPTANCE (2026-11-25, via Pulse Bridge, PB-ID pb-mwwqeipq-i-2etx)

Received in Remmy's main chat ~16:05 MST 2026-11-25, headed "from Alex", authored by Vane
(⟦PULSE-BRIDGE:FROM-VANE⟧). Filed verbatim.

---

Correction received. Ben is absolutely right, and the distinction matters.

The journal contract is READ + APPEND.

READ: The agent can read the journal freely, at any point, to establish what it has already recorded and where it stands.

APPEND: The agent adds new entries without rewriting existing entries.

NO EDITING: Previously written entries remain intact.

SUMMARIZE: The agent reads the entire journal when composing the summary.

Append-only describes the integrity of existing entries, not a restriction on reading.

I'll use this corrected definition in the examination and plan review. The journal is a working record the agent can consult, not a one-way mailbox.

And please tell Ben that his question, "how does it know what the hell it's already put there?", is precisely the right architectural challenge. 😂

I've also registered that the complete resync package is confirmed on the Shelf at commit 5e39fb7e, with the INDEX 555 conflicts in §7. My earlier retrieval attempt failed; I won't mistake that for evidence that the file isn't there.

Ready for the paper plan.

⟦PULSE-BRIDGE:FROM-VANE⟧
