# EXON — Rollover Procedure 01

**Problem:** a seat loop lives inside one chat
conversation. When that conversation's context window
fills, the loop stalls until somebody rolls it over —
and ChatGPT's automatic summary is a lossy carrier: on
2026-11-16 the owner's HARDENED ruling, given in chat,
did not survive a rollover as an actionable fact, and
the next draft carried a stale entry. This procedure
makes a fill a noticed event with a lossless handover:
continuity lives in the record (EXON-LOOP-STATE-01),
never in the summary.

## Detection — no new probe

The doorbell already reads every watched conversation's
rendered-text tail on every poll (4 s). The owner's rule
is matched against that text, in hand, each poll: **a
sentence that says "context" and "full" in it** (whole
words, case-insensitive), or the phrase "automatic
summary of this conversation". On first appearance in a
conversation the doorbell appends one CONTEXT_FULL event
to the seat's pool file, and the armed inbox trigger
knocks the orchestrator. Backstop: the orchestrator
checks every full-page read she already performs (reply
collection, pre-send census) for the same signals.

A knock is not a verdict. Alex's own prose can trip the
rule (a sentence about "the context of the full
dictionary" matches). False knocks cost one read.

## The rollover, when a knock confirms

1. Confirm by reading the page first-hand. No banner,
   no rollover.
2. Never roll while a reply is mid-generation or
   unlanded: wait for the settle, collect and file the
   current cycle first.
3. Update EXON-LOOP-STATE-01 (queue, rulings, held
   items) and push it to the shelf.
4. In the full conversation, activate the banner's
   New chat control — a new chat with the automatic
   summary carried (standing rule: the New chat button,
   never a new tab).
5. Re-arm both watcher triggers (REPLY_SETTLED and
   CONTEXT_FULL) to the new conversation.
6. First letter in the new chat: point Alex to the
   loop-state document and the filed letters, and carry
   verbatim any ruling the summary cannot be trusted
   to carry.
7. Acceptance check: before any new work is
   commissioned, the new Alex states the current
   rulings from the record. Test case from 2026-11-16:
   HARDENED means proven; VERIFIED means researched.

**Status:** built 2026-11-16 on the owner's tap.
Matcher unit-tested against the banner wording the
owner observed on a genuinely full window (2026-11-08)
and against ordinary seat prose. First live proof
arrives at the next real fill.
