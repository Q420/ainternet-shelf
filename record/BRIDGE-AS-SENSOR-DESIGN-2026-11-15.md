# Bridge as Sensor — Design Paper

**Status:** DESIGN PAPER ONLY. No implementation is authorised. The owner's
stop otherwise remains in force.
**Scope authority:** the owner's tap on the scope card, 2026-11-15 21:06 MST
("design paper — bridge as sensor, inbox as record, dumb signal as wake"),
recorded in the orchestrator's scope ledger.
**What this amends:** the watcher-recovery design round settled the same
evening (findings at `record/WATCHER-FAILURE-FINDINGS-2026-11-15.md`, rulings
at `record/WATCHER-FINDINGS-RULINGS-2026-11-15.md`, and Alex's process tree at
`record/ALEX-WATCHER-RECOVERY-PROCESS-TREE-2026-11-15.md`). That round
designed recovery for an EXTERNAL watcher. This paper changes the substrate:
the sensor is the Pulse Bridge, which is resident in the browser. Section 6
states what of the tree carries over, what shrinks, and what falls away.
**Companion design:** the approved notification rethink
(`record/NOTIFICATION-RETHINK-DESIGN-2026-11-15.md`). This paper is that
design's sensor leg, concretised against the bridge's real surface.

## Summary (verdict first)

The watcher failed because it was a visitor: an external process polling a
browser through a tunnel, inferring events from snapshots. The bridge is a
resident: it sits in the seat tabs themselves, watches the page where replies
render, and already carries letters into the orchestrator's chat. The design
is therefore a division of labour, not a new machine:

- **The bridge notices and carries.** On a finished seat reply it emits a
  NOTICE — a signal carrying identity only, never content.
- **The inbox records.** The notice is written to the orchestrator's
  append-only inbox and settled by identity; duplicates settle against the
  existing item and never re-act.
- **The orchestrator reads and judges.** The delivered notice starts her
  turn; she reads the actual reply herself and does all judging in-turn.
  No judge, streak, or content travels in the signal path.

## 1. The substrate as it actually stands (v0.19.0, read from the code)

Step zero of the scope was reading the bridge's real surface. What exists:

- **Detection (letterbox.js, content.js):** content scripts in the seat tabs
  watch the conversation DOM. A baseline window at start (min 4 s, closes on
  3 s of mutation quiet, cap 20 s) ensures only NEW messages trigger; a body
  fingerprint is checked against a persistent delivered record so history is
  never re-carried. Detections are reported to the router as `pb-detection`
  envelopes; a detection that cannot complete is reported by name as
  `pb-capture-drop` with a reason. Generation state is tracked
  (`pb-generation-cleared`).
- **Identity (protocol.js, stage1core identity layer):** every letter carries
  a PB envelope (types: message, task, reply, review_request, ack, approval)
  and a PB-ID derived ONLY from a verified stable source-occurrence key — a
  platform-native per-message ID, or a verified occurrence tuple. Sender and
  payload are validation attributes, never identity inputs. Anything that
  cannot be established exactly is IDENTITY-UNKNOWN; a PB-ID claimed by two
  source keys is IDENTITY-COLLISION. Fail-closed throughout.
- **Carriage (background.js router, adapters):** the router holds letters
  through states GATED, DELIVERING, RETRY_WAIT, ACKNOWLEDGED, UNVERIFIED,
  FAILED, STALLED, STOPPED, and delivers via per-site adapters'
  `deliverText` into the target tab's composer (chatgpt.com, claude.ai,
  muse.ai are all in the manifest), with read-back verification before send
  and turn-confirmation after.
- **Evidence (witness.js, ledger):** delivery outcomes are journalled in an
  append-only ledger (REGISTERED, ATTEMPT_CREATED, DUPLICATE_OBSERVED,
  DELIVERY_CONFIRMED, PROVEN_NOT_DELIVERED, HELD_FOR_REVIEW, and kin), so a
  delivery is CONFIRMED, PROVEN_NOT_DELIVERED, or UNKNOWN — never rounded.
- **Known defects on record:** old letters resending and tab reloads
  re-serving old messages (both addressed at the letterbox layer from
  v0.10.2 by the baseline window + delivered record; the paper treats them
  as guarded, not imaginary); status bars do not show incoming/sending;
  history shows only on the orchestrator's side; the Convene gating features
  are designed (BRIDGE-CONVENE-SPEC-01, FINAL PASS as design) but NOT in
  v0.19.0.

## 2. The notice: a new signal class

A notice is a bridge envelope of a new type (working name `notice`), emitted
when a registered seat finishes a reply that a live job is waiting on. It
carries identity only:

- seat (which seat responded), conversation (platform conversation ID/URL),
- the reply's source identity (platform message ID where available, else the
  PB-ID of the detected occurrence),
- the job reference (the marker the orchestrator registered for the wait),
- detected-at timestamp.

It carries NO reply content, NO summary, NO judgement. Its full text, as
delivered into the orchestrator's chat, is one short line in the owner's
formulation: "Alex has responded" — plus the identifiers above in machine
form. Content is read by the orchestrator, from the seat page, in her turn.

Registration: a wait is registered the same way the approved design arms a
trigger — when the orchestrator sends work to a seat, she registers the job
and its expected reply with the bridge (the bridge-side analogue of "pending
means armed"). An unregistered reply produces no notice; it is ordinary
traffic, visible in the seat tab as always.

## 3. The wake path, hop by hop

1. Seat reply finishes rendering in the seat tab.
2. Letterbox detects a NEW finished reply (baseline + fingerprint guards),
   establishes its source identity (or IDENTITY-UNKNOWN, §5).
3. Router matches it against registered waits. Match → a notice envelope is
   created and journalled (ATTEMPT_CREATED in the bridge ledger).
4. The notice is delivered by the muse.ai adapter's `deliverText` into the
   orchestrator's chat, with the bridge's normal read-back verification;
   the ledger records DELIVERY_CONFIRMED or PROVEN_NOT_DELIVERED.
5. The delivered notice starts the orchestrator's turn. Her first act is
   the inbox write: the notice becomes an inbox item (sequence ID, state
   pending), settled by identity against any existing item for the same
   reply.
6. She reads the reply from the seat page, acts per the job, and marks the
   item read, then acted. Judgement happens here — in the orchestrator,
   in-turn — never in the signal path.

Latency is the bridge's own: in-page detection plus an in-browser delivery.
No tunnel, no polling interval, no external process stands in this path.

## 4. The inbox's role (unchanged from the approved design)

The inbox (Stage 1 built, 48/48 fixtures) remains the orchestrator-side
record: append-only, sequence IDs, states pending / read / acted /
judge_pending, nothing deleted. The notice path feeds it; the dead-man
floor (the 120 s checker, repurposed as floor only) still catches anything
the notice path misses, and a pending item with no armed trigger remains a
defect by definition. Judged jobs (where a precondition must be evaluated,
not merely noticed) keep the judge, asynchronously, off this path —
unchanged from the approved design.

## 5. Failure classification on the new substrate

The classification HONESTY of the watcher round carries over entire; its
states mostly do not, because there is no external child to arm, relaunch,
or probe. The substrate's real failure classes:

- **bridge_down** — the extension or the browser itself is not running.
  Nothing can notice. Detection of this state belongs to the dead-man floor
  and the health panel (viewed, not pushed): the panel shows the bridge's
  last ledger event; the floor escalates on age, per the approved design.
- **target_unhealthy** — the bridge is alive but a seat tab cannot complete
  its round-trip: page wedged, logged out, conversation missing. The bridge
  already names the seed of this signal — `pb-capture-drop` with a reason,
  and the router's STALLED / UNVERIFIED states. A capture-drop on a
  registered wait becomes an inbox alert item, not a silent miss.
- **muse_tab_absent** — the seat replied and the notice was created, but
  delivery has nowhere to land. The router holds the notice (GATED/STALLED
  in today's vocabulary); the ledger keeps the attempt; when the tab
  appears, delivery proceeds and the ledger confirms it. The wait is
  delayed, never lost, and the hold is visible in the panel.
- **identity_unknown** — a reply was detected but its source identity could
  not be established exactly. The notice is still delivered, flagged
  IDENTITY-UNKNOWN; the orchestrator settles it by reading the page
  herself. Uncertainty is carried, never resolved by guessing — the tree's
  unresolved bucket, preserved.
- **seat_silent** — no reply yet. Not a failure class at all. The wait
  stands armed; escalation is by the job's own age rules in the inbox, not
  by any machinery state.

## 6. Disposition of Alex's process tree (artefact 01)

- **Carries over entire:** the governing principle (what failed vs what
  recovery is permitted are separate questions); no failure charged to a
  budget without evidence; the unresolved bucket; the send-intent
  discipline (an ambiguous send is never auto-resent; confirmation requires
  conversation identity plus a distinguishable turn identity — which the
  bridge's witness/read-back already implements); escalation keyed on
  time-in-state.
- **Shrinks:** the arm-boundary probe becomes the bridge's ordinary
  detection guards (baseline window, fingerprint, identity establishment)
  — a resident does not arm; it is present or it is down, and down is
  bridge_down above. The arm-attempt ownership/atomic-claim requirement
  becomes the router's existing single-router state machine plus the
  ledger's DUPLICATE_OBSERVED.
- **Falls away:** the supervisor, the child, the relaunch cap, gave_up as a
  child-failure terminal state, heartbeat files, the two-stage probe as a
  recovery ceremony, and the checker's resurrection path. There is nothing
  external left to resurrect; the dead-man floor and the panel carry the
  "who watches the watcher" duty, as the approved design already settled.

## 7. What happens when each piece is down

| Piece down | Behaviour |
|---|---|
| Seat tab closed | No detection; the wait stands armed. Panel shows the seat absent. No false signal. |
| Browser closed | bridge_down. Dead-man floor escalates on age; nothing is claimed to have been noticed. |
| Bridge extension crashed | bridge_down, same as above; on browser restart the baseline window re-establishes history before any trigger can fire. |
| Muse tab closed | Notice held by the router, attempt journalled; delivered when the tab appears; inbox floor catches the aged wait meanwhile. |
| Orchestrator mid-turn | The notice lands as a queued message and merges in sequence order (approved design); deferred wakes collapse into one pending set. |
| Duplicate notice | Settles against the existing inbox item by identity; never re-acts. |
| Notice for an unregistered reply | None is emitted. Ordinary traffic stays in the seat tab. |

## 8. Open questions for the reviewer

1. Should `notice` be a new PB envelope type, or a flag on the existing
   `reply` type? (This paper leans new type: the identity-only contract is
   the point, and a type makes content-in-a-notice a protocol error.)
2. Should the notice ride the letter router's full state machine, or a
   light path (detect → deliver → journal) that borrows only its evidence
   states? (Lean: light path; the router's gating is letter machinery, and
   Convene gating is not in v0.19.0 to ride on.)
3. Is `pb-capture-drop` on a registered wait sufficient as the
   target_unhealthy signal, or does the design need a periodic target
   round-trip? (Lean: capture-drop suffices — a resident that is receiving
   page mutations has its round-trip evidence continuously; a probe would
   reintroduce sampling.)
4. Registration mechanics: does the orchestrator register waits through the
   bridge popup/panel (owner-visible), a message to the bridge tab, or a
   marker in the outbound letter itself (the `⟦WD:…⟧` marker precedent)?
   (No lean stated; each has a different trust shape, and the marker form
   risks the §4 error of trusting a seat's echo.)

## 9. Authority boundary

This paper authorises nothing. It does not amend the bridge's code, the
inbox's code, or any hook. If accepted, the build is a separate owner
decision, scoped and tapped on its own card, and built from this paper at
its shelf pin. Batch 6 remains CLEARED; Stage 6 remains unauthorised; the
owner's stop remains in force.
