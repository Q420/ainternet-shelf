# Ben's Rulings — the Bridge Journal (§13.1) and the Pause Process

**Artefact purpose.** This document admits Ben's journal ruling of
2026-11-11 (the ruling carried as open decision §13.1 in
BRIDGE-FIX-SPEC-02) into the Shelf as a citable source, preserving
the distinction between Ben's own words and Remmy's contemporaneous
interpretation, and records the two rulings of the same afternoon
that reframed its pause branch. Admitted by Remmy, 2026-11-11, at
Alex's request in pb-mwcny5oe (reconciliation pass on
bridge/BRIDGE-CONVENE-SPEC-01.md), for Alex's independent
cross-check.

## 1. The §13.1 ruling — Ben's words (verbatim, chat, 2026-11-11 ~12:37 MST)

"If a message is skipped there's no sense in keeping the ID of it.
If a message is unable to send and I push it through then the ID
should be saved."

"if the fix works, there should be no reason a message doesn't go
through."

## 2. Remmy's contemporaneous interpretation (daily log, NOT Ben's words)

From the programme daily log (~/memory/2026-11-10.md, entry of
2026-11-11 ~12:38 MST), quoted in full:

"BRIDGE §13.1 RULED BY BEN'S LOGIC (2026-11-11 ~12:38 MST): 'If a
message is skipped there's no sense in keeping the ID of it. If a
message is unable to send and I push it through then the ID should
be saved.' + 'if the fix works, there should be no reason a message
doesn't go through.' Settled: the journal records ONLY what
actually went through (sent / delivered / force-sent); skipped or
discarded-unsent messages keep no ID. On pause/disconnect purge:
queue and unsent IDs purge together; sent IDs persist (they are
history, not queue). This dissolves the F-3/F-4 tension. Remmy's
one named edge, put to Ben: DISPATCHED-UNCONFIRMED (might have gone
through) — recommended read: treat as gone-through for journal
purposes (keep the ID), because a duplicate is the worse failure;
Ben's confirmation outstanding. To be carried to Alex in the next
bridge round; Spec 02 §13.1 closes on this ruling at the next
revision."

Status of the parts: the journal-content rule (only what went
through is recorded) is Ben's, from §1. The pause/disconnect
sentence in this interpretation ("sent IDs persist") was Remmy's
reading, recorded as provenance, and is superseded by §3 below
before ever being adopted. The DISPATCHED-UNCONFIRMED edge remains
Ben's to confirm.

## 3. The pause rulings (Ben's words, chat, 2026-11-11 ~13:59–14:00 MST)

"Instead of having a purge let me see it and decide what to do
with it."

"But having a process in the cache or in the pause would be good."

Effect, as recorded by Remmy the same hour: pause/disconnect does
NOT automatically destroy the queue or cache; the bridge presents
what is held — each item with its ID, direction and state — through
a review process in the pause, and Ben decides each item's
disposition (send / hold / discard / copy over). Nothing moves or
is destroyed until he decides. This supersedes the purge design of
BRIDGE-FIX-SPEC-01/02 (F-3) and dissolves the journal-survival
branch of §13.1 (there is no purge event for the journal to
survive). It also reframes DISPATCHED-UNCONFIRMED: an unconfirmed
item is one Ben sees and decides on inside the review process. His
confirmation of the edge's journal treatment remains outstanding
as a separate point.

## 4. Citation

Cite as: bridge/BEN-RULING-JOURNAL-AND-PAUSE-01.md (this artefact).
Primary sources: Ben's chat messages of 2026-11-11 (this side
chat, chat d9fab931-9424-46ca-bcd6-76606ce10ccc) and the programme
daily log ~/memory/2026-11-10.md. The daily log is a local record,
not a Shelf artefact; this document is the admitted Shelf source
for the ruling and preserves the provenance distinction the log
itself records.
