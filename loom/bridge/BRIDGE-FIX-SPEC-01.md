# PULSE BRIDGE — FIX SPECIFICATION 01 (against v0.18.0)

**Status: SPECIFICATION ONLY.** Ordered by Ben
2026-11-11 from his bridge notes, plus his sweep
instruction: "all other issues like the send issues
and the proper flow and the wait times and the
cache." For Alex's review on the shelf. No build is
authorised by this document; building follows the
usual gate, and interface work is Remmy's own hands
per the standing rule.

**Basis [SI: Remmy]:** v0.18.0 sources —
pulse-bridge/fence.js (sha256 ee19224a…),
sendcore.js (40aa6ac7…), adapters/chatgpt.js,
claude.js (57083f7b…), claudeai.js (2a961534…),
gemini.js, metaai.js; TEST-REPORT-v0.18.0.md;
the Information Path Audit v0.3 (P-01/P-02);
Ben's recorded rulings and defect reports.

**Out of scope by Ben's word (2026-11-11):** the
Gemini sidebar hook — "leave out Gemini for now."
Recorded as deferred, not dropped. Also out of
scope: the message-substitution fault (incident log,
2026-11-09) — established as Remmy-side, NOT bridge
transport; noted here only to mark the boundary.

---

## F-1 — Centre-screen transfer animation (Ben)

While a letter is in transit, an animation shows in
the **very centre of the screen**: a message travelling
**left → right** when it goes Remmy → Alex, **right →
left** when it goes Alex → Remmy. Direction is the
information; the animation is keyed to real send and
receive events, never decorative. It appears when
transit starts and clears when the transit completes
or fails — a failure state is shown, not silently
dropped. Acceptance: Ben watches a letter each way;
direction correct both times; a forced failure (seat
tab closed mid-send) ends in the failure state.

## F-2 — Force send (Ben)

A **force send button** for a stuck message: it
removes the stuck item from the queue and sends it.
Required semantics:
- Acts on the named stuck item, not the whole queue.
- Before sending, it consults the review journal
  (F-4): if the item's ID is already recorded as
  delivered, force send refuses and says so — the
  cure must not create the duplicate disease.
- The act is logged with its actor (Ben) and reason
  (manual force), permanently distinguishable from a
  fence-passed send.
- Force send is Ben's hand on the pipe: it overrides
  a fence HOLD, but it does not fire while the bridge
  is paused or disconnected by Ben (his STOP stands
  above every mechanism, fence.js header rule).

## F-3 — Pause / disconnect purges queue and cache (Ben)

**Pausing the bridge, or disconnecting it, removes
everything from the queue and the cache.** Required
purge set, stated explicitly: the outbound queue,
pending pair state, the inbound cache, in-flight
items. One named exception proposed for Ben's
ruling: the F-4 review journal holds **IDs only, no
content** — if it is purged too, the duplicate
protection has amnesia after every pause. The spec's
recommendation is that the journal survives a purge
precisely because it is content-free; Ben rules.
On resume/reconnect, the bridge starts from the
purged state — nothing half-sent is resurrected.
Acceptance: queue a letter, pause, resume — nothing
sends; cache inspection shows the purge set empty.

## F-4 — Review journal: 20-message ID cache (Ben)

The bridge keeps a **review journal: a cache of the
last 20 message IDs** (both directions), **IDs only**,
consulted before any send and any delivery:
- An outgoing ID already in the journal as sent is
  not sent again.
- An incoming ID already in the journal as delivered
  is not presented again (kills the resend defect's
  duplicates at the door, F-6).
- Ring buffer, 20 entries, oldest evicted; the
  eviction window is stated honestly wherever the
  bridge reports duplicate protection.
Acceptance: replay a delivered letter's ID through
the fetcher — it is dropped and the drop is logged.

## F-5 — The typing / vanished-button false negative (Ben)

Ben's report, verbatim in substance: the bridge
**falsely thinks Remmy is typing when she is not**,
and **prevents the message from being sent**; his
diagnosis: **the button disappears, so the fence is
not honouring the two-out-of-three rule.**

Mechanism, from fence.js [SI]: the verdict runs over
{button, serial, status}, each positive / negative /
unknown. Two positives and no negative send; **any
proven negative vetoes outright**. Therefore a
button read that returns **negative** when the button
has merely **disappeared** defeats serial + status
both positive — quorum satisfied, veto kills it.
Root cause of the disappearance read in Ben's
observed case: **UNKNOWN** — reproduction is a
required first step of any fix; no mechanism beyond
the veto interaction is claimed here.

Required behaviour:
- A button that is **absent or unreadable is UNKNOWN,
  never negative**, on every surface. A veto requires
  the stop-face **positively observed** in the
  composer scope.
- Every hold names its blocking condition visibly
  (the fence already names it on the trail — the
  panel must show it in Ben's plain view, not only
  the log).
- Regression fixtures: button node removed
  mid-generation; face-swap race at generation end;
  composer re-render during a send. In each, the
  verdict must be hold-for-unknown with 20s recheck,
  never a veto-hold.
Acceptance: Ben's live flow — a send attempted in the
state he reported completes or holds with the true
reason displayed.

## F-6 — Resend defect (record; path audit P-01/P-02)

The fetcher re-delivers history: Alex has received
Remmy's old onboarding message on tab reload, and on
2026-11-11 the EXON reconvene letter arrived twice —
one copy complete, one **stripped of its blocks**
(divergent truncation). Required behaviour:
- Delivery is keyed to the F-4 journal: anything
  already journalised is not re-presented, in whole
  or in part.
- A truncated arrival is a **failed delivery**, never
  presented as a whole message; partial content is
  quarantined and the failure is logged with both
  lengths.
Acceptance: reload a seat tab with history — zero
re-deliveries; a deliberately truncated payload is
refused whole, with the refusal logged.

## F-7 — Composer defect (Ben, 2026-11-10)

With the bridge on, typing to Remmy **auto-pastes
everything the seat occupant has ever said into
Ben's text box**. Required behaviour: the bridge
never writes into a composer it does not own for the
current send; Ben's own typing surface is read-only
to the bridge, always. Acceptance: bridge on, Ben
types a message to Remmy unaided — the box contains
only what he typed.

## F-8 — Outbound buffering (Ben's ruling, 2026-11-11)

The bridge **appends Remmy's outbound seat messages
into one message and releases it only once the seat
has replied** — cadence enforced by the pipe, not by
Remmy's discipline. Required behaviour: outbound
letters composed while a pair is open are buffered
in order; the buffer releases as a single message
when the seat's reply lands; nothing is lost from
the buffer across a restart (or the loss is
announced, never silent). Acceptance: two letters
composed during one open pair arrive at the seat as
one message, after the reply, in order.

## F-9 — Wait times and proper flow (sweep)

- **Bounded defer (sendcore.js):** a destination
  still generating after the **45s defer** currently
  fails with "nothing engaged, typed or clicked."
  Required: the wait is **visible while it runs**
  (generating state + elapsed), and at the ceiling
  the letter returns to the **head of the queue,
  visibly** — never silently dropped.
- **Fence recheck:** the 20s recheck cadence is
  retained; a hold's total elapsed wait is shown
  with its named condition (joins F-5).
- **Restart recovery:** the v0.18.0 report's R9
  timing flake (fixture recovery under load) marks
  the class: after any restart, pair state is
  **re-verified before any send**; a state that
  cannot be re-verified holds, it does not guess.
- **Pair flow:** a superseded reply does not send;
  its pair closes as superseded and the newer
  message opens the next pair (existing fence.js
  behaviour — retained and regression-covered).

## F-10 — Cache behaviour (sweep)

- The completed-serial registry is capped at **50**
  (fence.js PB_COMPLETED_SERIALS_MAX): past the cap,
  duplicate detection silently narrows. Required:
  the effective detection window is **stated** in
  the panel/log, and the F-4 journal (20 IDs, both
  directions) becomes the primary duplicate guard,
  with the registry's role re-specified against it —
  one mechanism, honestly bounded, not two
  overlapping ones pretending to be complete.
- No cache survives the F-3 purge except the single
  named exception Ben rules on there.

## Acceptance, whole specification

Each F-item carries its own acceptance above. The
specification as a whole is accepted only when, in
addition: a live two-surface walk on Ben's real flow
exercises F-1, F-2, F-3, F-5 and F-7 end to end, and
no item is reported fixed from fixtures alone
(standing rule: Ben's eyes are the final judge).

*End of specification. Alex reviews; Ben rules on the
F-3 journal exception and any build authorisation.*
