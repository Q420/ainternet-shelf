# PULSE BRIDGE — FIX SPECIFICATION 02 (CONSOLIDATED, against v0.18.0)

Consolidation of BRIDGE-FIX-SPEC-01, its
CLARIFICATIONS ADDENDUM, Ben's bridge notes rounds 1
and 2 (2026-11-11), and Alex's two reviews
(pb-mwcf39wn-u-ioqt; ALEX-BRIDGE-FIX-CLARIFICATIONS-
REVIEW-01). The addendum is preserved as a linked
record; where any earlier document differs from
this one, **this specification governs**.

**Status: SPECIFICATION ONLY — not build-ready.**
No code changes, tests, reloads or live actions are
authorised by this document. Open Ben decisions are
carried as labelled branches (§13); nothing in this
specification silently decides them.

Basis [SI: Remmy]: v0.18.0 sources — fence.js
(ee19224a…), sendcore.js (40aa6ac7…), adapters;
TEST-REPORT-v0.18.0.md; path audit P-01/P-02.

---

## 1. Transit lifecycle and the centre-screen animation (F-1)

Every letter moves through named states:
COMPOSED → QUEUED → TRANSIT → DELIVERED or FAILED.
The centre-screen animation is bound to TRANSIT and
to nothing else: it appears on entry to TRANSIT and
clears on exit, showing a message travelling
**left → right for Remmy → seat, right → left for
seat → Remmy**. FAILED is a shown end-state, never
a silent disappearance. A letter that never enters
TRANSIT never animates; a stuck TRANSIT is exactly
the state the force-send control (§3) addresses.

## 2. Seat-popup parity and notification timing (Ben, round 2)

The panel/popup behaves **identically on both
seats**: same states, same controls, same timing,
same wording. Sending and receiving **notifications
fire at the event** — a send notification at the
TRANSIT → DELIVERED transition, a receive
notification at verified delivery (§6), never at
composition, queueing, or attempt. The popup does
**not** display a list of completed receipts at the
bottom (Ben: removed) — completed history lives in
the log, not the popup.

## 3. Force send (F-2)

A manual control for a stuck item. It acts on the
named item only, consults the journal (§5) first,
and logs actor (Ben) and reason permanently.
It may override ONLY: (a) hold-for-unknown (§4's
non-veto hold); (b) a defer-ceiling return (§9);
(c) pair state unverifiable after restart.
It must NEVER bypass: an ID journalised DELIVERED;
Ben's STOP; the paused/disconnected state; a
superseded pair; an incomplete message (§6); or a
**proven negative veto** (a positively observed
stop-face — the destination is genuinely
generating). *The never-bypass list is stated as
the specification's position; Ben's ratifying
ruling is recorded as pending (§13).*

## 4. The fence and the UNKNOWN button (F-5)

The verdict runs over {button, serial, status}.
**For the button condition specifically, this
specification's rule supersedes the generic
two-positive/no-negative quorum:** a button that is
absent or unreadable is **UNKNOWN, and UNKNOWN is a
non-veto HOLD with 20-second recheck** — the letter
does not send on the other two positives while the
button is UNKNOWN. A veto requires the stop-face
**positively observed** in the composer scope.
Every hold names its blocking condition in the
panel, in Ben's plain view. Regression fixtures:
button node removed mid-generation; face-swap race
at generation end; composer re-render during a
send — in each, the outcome must be the non-veto
hold, never a veto and never a send.
*This supersession is the specification's position,
written per Alex's requirement that it be explicit;
Ben's ruling is recorded as pending (§13).* Root
cause of Ben's observed "thinks Remmy is typing"
case remains UNKNOWN; reproduction precedes any
mechanism claim in a build.

## 5. The review journal (F-4, F-10)

One journal, both directions, direction recorded
per entry, holding **message IDs only** — the last
**20**. Every entry carries a disposition —
ATTEMPTED, SENT, RECEIVED, DELIVERED, with
RECEIVED-INCOMPLETE and DELIVERED-LATE as recorded
sub-states — never treated as interchangeable.
Duplicate protection keys on DELIVERED (inbound)
and SENT-or-later (outbound). The journal persists
across restart, is consulted before any send and
any presentation, evicts strictly oldest-first at
the 21st entry (each eviction logged), and its
protection window is stated as "the last 20 IDs"
wherever duplicate protection is claimed.
**The journal is the sole authoritative duplicate
mechanism.** The completed-serial registry is pair
bookkeeping only and makes no duplicate claim.
**Migration (F-10):** on first run of the fixed
version, existing seen/delivered/failed ledgers are
imported into the journal with their dispositions
(most recent 20 by time), the completed-serial
registry is frozen as history, and the journal is
authoritative from that moment.

## 6. Completeness contract (F-6)

An ID proves identity, not completeness. Each
letter carries a trailer line, exactly:
`PB-COMPLETE: chars=<decimal> blocks=<decimal> sha256=<64 lowercase hex>`
computed over the letter body as transmitted
(UTF-8), where blocks counts the letter's message
blocks. The receiver verifies all three values
before presentation. Any mismatch = failed
delivery: payload quarantined, failure logged with
expected vs observed, journal records
RECEIVED-INCOMPLETE. **An incomplete copy never
poisons its ID:** a later complete copy of the
same ID verifies on its own values and is
delivered; the incomplete entry is superseded in
the journal, with both events logged.
*Adoption of this trailer is a protocol change
requiring Ben's and Alex's explicit adoption
(§13) before any build implements it.*

## 7. Pause, disconnect, purge — and the buffer (F-3, F-8)

Two event classes, different semantics:
- **Deliberate pause/disconnect (Ben's act):**
  purges the outbound queue, pending pair state,
  the inbound cache, in-flight local state, and
  the outbound buffer. The buffer's discard is
  **announced before destruction**, listing every
  constituent PB-ID. A send already dispatched is
  not recalled: it is journalised
  DISPATCHED-UNCONFIRMED; a late confirmation
  updates it to DELIVERED-LATE; it is never resent.
- **Restart/crash (not Ben's act):** queue pair
  state is re-verified before any send (a state
  that cannot be re-verified holds); the buffer
  persists and releases only under §8.
- **Overlap:** restart while paused recovers INTO
  the paused state; the pause purge is neither
  repeated nor undone.
**Journal survival across a deliberate pause is
Ben's open decision (§13)** — both branches are
specified: SURVIVES (journal exempt from the
purge; it holds IDs only) or PURGED (journal
cleared with everything else, and the popup states
that duplicate protection restarts empty). The
build implements the branch Ben rules.

## 8. Outbound buffering and aggregate identity (F-8)

While a pair is open, Remmy's outbound letters are
appended into **one aggregate delivery**, released
only when the seat's reply lands — enforced by the
pipe. The aggregate carries a manifest line:
`PB-AGGREGATE: <transport-id> constituents=<PB-ID, PB-ID, …>` in order.
Each constituent keeps its own identity and its own
§6 completeness values; each is journalised
individually (SENT, as part of the named
aggregate); acknowledgements and deduplication
resolve per constituent. **Partial delivery:** if
the aggregate arrives incomplete, complete
constituents are delivered and journalised;
incomplete ones are quarantined per §6 without
poisoning the delivered ones. **Overflow:** the
buffer holds at most 10 constituents or 60,000
chars; beyond that, composition of a further
letter warns visibly instead of silently dropping.
**Recovery:** after restart, a persisted buffer is
re-verified constituent by constituent before any
release.

## 9. Wait times and the pair machine (F-9)

The 45-second bounded defer becomes an explicit
pair-machine state, **DEFER-WAIT**: entered when
the destination is generating at send time; the
panel shows the generating state and elapsed wait;
exits to TRANSIT on generation end, or at the 45s
ceiling to **QUEUE-HEAD** — the letter resumes the
single active pair's head position (the existing
one-active-pair machine has exactly one head; no
new queue is created) — visibly, never silently
dropped. The fence recheck cadence (20s) is
retained; a hold shows its total elapsed wait with
its named condition.

## 10. Composer ownership (F-7)

The bridge writes into exactly one composer: the
instance it opened for the current send, identified
by that send's serial. Every other composer —
above all **Ben's own typing surface — is read-only
to the bridge, always**. The defect's acceptance
test: bridge on, Ben types to Remmy unaided; the
box contains only what he typed.

## 11. Resend defect (record; P-01/P-02)

Fetcher re-delivery of history is closed by §5 +
§6 jointly: anything journalised DELIVERED is not
re-presented in whole or part; anything failing
completeness is quarantined as a failed delivery,
never presented as a whole message. Acceptance:
reload a seat tab with history — zero
re-deliveries; a deliberately truncated payload is
refused whole, refusal logged.

## 12. Cache behaviour

No cache survives the §7 purge except the single
journal question Ben rules on. Cache windows are
always stated at their true bound (journal: 20
IDs; registry: history only). Nothing in the
bridge may present a bounded window as complete
protection.

## 13. Open decisions (Ben's, and one joint)

1. **Journal survival** across deliberate pause
   (§7) — Ben.
2. **Force-send never-bypass list ratification**
   (§3) — Ben.
3. **UNKNOWN-button supersession ratification**
   (§4) — Ben.
4. **Completeness trailer adoption** (§6) — Ben
   and Alex, as a protocol change.
Until 1–3 are ruled, this specification is a
complete draft with labelled branches, not a build
specification. Item 4 gates §6's implementation
only.

## 14. Acceptance, whole specification

Per-item acceptance stands in §§1–12. The whole is
accepted only when a live two-surface walk on
Ben's real flow exercises §§1, 2, 3, 4 and 10 end
to end, with fixture results reported separately
from the live walk. Nothing is "fixed" from
fixtures alone; Ben's eyes are the final judge.

*End of specification. Alex reviews this
consolidation and the traceability matrix; the
build waits on §13.*
