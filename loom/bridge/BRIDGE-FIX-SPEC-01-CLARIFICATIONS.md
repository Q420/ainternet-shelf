# BRIDGE FIX SPECIFICATION 01 — CLARIFICATIONS ADDENDUM

Binding addendum to BRIDGE-FIX-SPEC-01.md, answering
Alex's technical review (pb-mwcf39wn-u-ioqt) finding
by finding. Where this addendum and the base
specification differ, this addendum governs.
Specification level only — no build authorised.
Ben's F-3 journal-survival ruling remains his.

## F-2 — Force send: override scope, enumerated

Force send may override ONLY these hold classes:
(a) a fence hold-for-unknown (a condition unproven,
no veto recorded); (b) a defer-ceiling return-to-
queue; (c) pair state unverifiable after restart
(F-9's hold). Force send must NEVER bypass:
- an ID already journalised as delivered (F-4);
- Ben's STOP, and the paused/disconnected state;
- a superseded pair (it stays closed);
- an incomplete or truncated message (F-6);
- a proven negative veto — a positively observed
  stop-face means the destination is genuinely
  generating; forcing types into a live generation.

## F-3 / F-8 — The lifecycle conflict, resolved by event class

Alex is right that one item cannot be guaranteed
both to survive and to be purged. The two events
now have explicitly different semantics:
- **Deliberate pause/disconnect (Ben's act):**
  purges queue, pair state, inbound cache AND the
  outbound buffer. The buffer's discard is
  **announced before destruction**, listing every
  constituent PB-ID it held — Ben's "everything"
  is honoured, and nothing vanishes silently.
- **Restart/crash (not Ben's act):** the buffer
  persists, is re-verified on recovery, and
  releases only under F-8's rule (after the seat's
  reply).
- **Overlap:** a restart while paused recovers
  INTO the paused state; the purge already happened
  at pause time and is not repeated or undone.

## In-flight purge

A send already dispatched to a destination cannot
be recalled, and the specification no longer
pretends otherwise. On purge, a dispatched item is
marked **DISPATCHED-UNCONFIRMED** in the journal.
A late confirmation updates its disposition to
DELIVERED-LATE and is logged; the item is never
resent, and any re-presentation is refused by the
journal. Purge clears local state; it does not
rewrite what already left the pipe.

## F-4 — Journal semantics

One journal, both directions, direction recorded
per entry. Every entry carries a **disposition** —
ATTEMPTED, SENT, RECEIVED, DELIVERED (with
RECEIVED-INCOMPLETE and DELIVERED-LATE as recorded
sub-states) — and dispositions are never treated
as interchangeable: duplicate protection keys on
DELIVERED (inbound) and SENT-or-later (outbound).
The journal **persists across restart** (it is the
dedupe memory; losing it on restart would reopen
every duplicate the journal exists to close).
Eviction is strictly oldest-first when the 21st
entry arrives, each eviction is logged, and the
protection window is stated as "the last 20 IDs"
wherever duplicate protection is claimed.

## F-6 — Completeness contract

An ID proves identity, not completeness — agreed.
The letter envelope gains a declared completeness
block: the sender states **total character length,
block count, and the full sha256 of the letter
body** in a trailer line. The receiver verifies
all three before presentation. Any mismatch =
failed delivery: the payload is quarantined, the
failure logged with expected vs observed values,
and the journal records RECEIVED-INCOMPLETE —
never DELIVERED. (This changes the letter format;
adoption of the trailer is a protocol decision for
Ben and Alex, flagged here, not assumed.)

## F-8 — Aggregate identity

A buffered aggregate carries a **manifest line
listing every constituent PB-ID in order**. Each
constituent is journalised individually (SENT, as
part of the named aggregate); acknowledgements and
deduplication resolve per constituent. The
aggregate's own transport ID is for routing only
and never replaces a constituent identity.

## F-10 — One authoritative duplicate mechanism

The **20-ID review journal is authoritative** for
duplicate detection in both directions. The
50-entry completed-serial registry is demoted to
what it actually is — pair bookkeeping (serial
assignment and pair retirement history) — and
makes **no duplicate-protection claim**; its cap
bounds history depth only, and that bound is
stated where the registry is described.

## F-5 — Confirmed

The absent/unreadable-button rule stands as
specified and, as Alex notes, matches the v0.18.0
shared send-core design (unreadable composer state
returns unknown, not a negative veto). The
regression fixtures must preserve exactly that
distinction: unknown → hold with recheck; only a
positively observed stop-face may veto.

*End of addendum. Alex re-reviews; no build
specification is prepared until he accepts these
clarifications, and no implementation is authorised
by any of it.*
