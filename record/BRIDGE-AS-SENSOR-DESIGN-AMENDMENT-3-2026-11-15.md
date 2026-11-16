# Bridge as Sensor — Amendment 3: Wait Lifecycle Clarifications

**Amends:** `record/BRIDGE-AS-SENSOR-DESIGN-2026-11-15.md` as amended by
Amendments 1 and 2.
**Required by:** Alex's Amendment 2 ruling
(`record/ALEX-BRIDGE-SENSOR-AMEND2-RULING-2026-11-15.md`): the retained
registration-mechanics item is closed in its essential trust-boundary
design; the three clarifications below are required before the paper is
build-ready. Where this amendment and the earlier papers disagree, this
amendment governs.
**Status:** DESIGN PAPER ONLY. No implementation is authorised. The owner's
stop otherwise remains in force.

## 1. The registration point (ruling amendment 1)

Amendment 2 said registration occurs when the bridge reads the marker at
carriage. This section names the exact committing event: **a wait is
registered only when the carrying letter's delivery is CONFIRMED** — the
bridge's existing witness outcome (read-back / turn confirmation, ledger
DELIVERY_CONFIRMED). Before that moment the wait exists in one named
pre-state:

- **ISSUING** — the letter is in carriage, outcome not yet known. No wait
  is registered; no notice can fire.
- On **DELIVERY_CONFIRMED** — the wait registers in the state Amendment 2
  defines (open, or held if a HOLD accompanied it).
- On **PROVEN_NOT_DELIVERED** — the wait is never registered. The letter's
  failure is handled by the existing send discipline (journalled; never
  silently resent). An unissued request must not look issued: nothing in
  the inbox or the panel may show a wait for a letter that provably never
  arrived.
- On **UNKNOWN** (ambiguous send) — the wait is recorded as **UNCONFIRMED**:
  visible in the inbox as an unresolved wait, and it can fire NO notice
  until the delivery resolves to CONFIRMED by the bridge's confirmation
  evidence (conversation identity plus a distinguishable turn identity,
  per the settled send-intent discipline). If it resolves to
  PROVEN_NOT_DELIVERED, the UNCONFIRMED record is struck and journalled.
  An ambiguous send is never silently treated as confirmed — in either
  direction.

## 2. Replies that land during a HOLD (ruling amendment 2)

Detection does not stop during a hold; only the notice is suppressed.

- A reply landing while its wait is held is captured and journalled by the
  bridge with its source identity and detected-at time, exactly as if the
  wait were open. It is retained against the wait.
- On **RESUME**, each retained reply fires its notice, in landing order,
  carrying its ORIGINAL source identity and detected-at time. A retained
  reply is never re-detected or represented as a new reply when the hold
  lifts; the letterbox's fingerprint and delivered-record guards apply to
  it as to any captured reply.
- On **CLOSE** of a held wait with replies retained, the retained replies
  are journalled as disposed-by-close and fire no notices. The record of
  their landing is not deleted.

Nothing that lands during a hold disappears from the notification path:
it is noticed late, by design, with its identity intact — or disposed by
an explicit CLOSE, on the record.

## 3. Multi-part counting and the PARTIAL lifecycle (ruling amendment 3)

- **What counts.** A part counts toward `⟦ASK:<job>×<n>⟧` only when its
  occurrence is distinct and identity-established (platform message ID or
  PB-ID, per the base paper's identity layer). An IDENTITY-UNKNOWN
  occurrence is recorded against the wait as an **unresolved candidate**:
  it does not advance the count, and it is counted or discarded only when
  the orchestrator establishes the source occurrence from the seat page
  herself (Amendment 1 §A4). The count never advances on a guess.
- **PARTIAL is an escalation, not a completion.** When the wait's
  escalation age passes with counted parts outstanding, the wait enters
  the PARTIAL state and raises one inbox alert item. The inbox represents
  PARTIAL as its own state, visibly distinct from complete; an incomplete
  response is never represented as complete.
- **The wait stays open.** In PARTIAL, later parts still count and still
  fire their notices. The wait closes on the nth counted part, or on
  CLOSE, as before.
- **No repeated PARTIAL spam.** The PARTIAL escalation fires once per
  escalation-age threshold. A further escalation requires a further
  threshold — the next age multiple in the job record, or the
  orchestrator re-arming the escalation explicitly. A single threshold
  crossing never produces repeated alerts.
