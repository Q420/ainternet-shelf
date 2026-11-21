# The Watched Orchestrator — Plan (2026-11-15)

**Status: PAPER ONLY.** The owner's full stop (2026-11-15 20:34 MST)
remains in force. This plan authorises nothing. Every build stage
below needs its own owner card, and the first live step needs a
recorded, scoped lift of the stop.

**Provenance:** assembled from the night's settled pieces — the
bridge-as-sensor design and its amendments (Alex, ACCEPT), the
doorbell and camera reviews and the inversion and attention
exchanges (Claude, fresh verified conversation
claude.ai/chat/13ca233d-b4e1-4d52-88bb-12d910c7e616, filed at
record/CLAUDE-FRESH-DOORBELL-CAMERA-REVIEW-2026-11-15.md), and the
owner's rulings of 2026-11-15 23:02–23:40 MST (camera
delete-as-it-happens; the bridge watches the orchestrator; false
positives are cheap; attention is re-realized upon reading; the
nudge refreshes her; the summary carries the next moves).

## 1. The problem

When a seat replies, the orchestrator must learn of it, act, and be
seen to have acted. Tonight every instrument pointed at the seats,
while every failure sat on the orchestrator's side, unwatched:
rulings captured perfectly and left unread, courier reports believed
without a witness, sends stranded as drafts. Detection of responses
was never the weakest link. The unwitnessed orchestrator was.

**The owner's plain-words version (2026-11-15 23:41 MST):** today
the orchestrator tells the owner "it's sitting with Alex; as soon
as it lands, I'll handle it" — and nothing actually tells her when
it lands. This system tells her when it lands, refreshes her,
hands her the summary and the next moves, and sends her to go
get it.

## 2. The governing inversion (owner's ruling)

The bridge watches the orchestrator, not the responses. The chain
of witnesses terminates at the owner — the only participant who can
act on every failure, including a wedged orchestrator. Seat-reply
detection is demoted to a secondary sense and an audit: a provably
attending orchestrator reads replies herself (direct page reads
were the one channel that never failed), and the sensors check her
claims rather than raise the alarm.

## 3. Architecture

- **Sensor (the doorbell):** a minimal in-house extension. Notices
  landings, writes the append-only inbox, fires the wake, reports
  its heartbeat. It carries nothing else. Letters are carried by
  the orchestrator's own sends, never by the sensor.
- **DOM observer — the verdict:** which seat, which turn, is
  streaming finished. Its verdict mints the identity-keyed notice.
- **The camera — the gate and the witness (owner's idea):** tiny
  downscaled bitmaps of the conversation region, frame-differenced
  like motion detection. Change in the reply zone triggers a DOM
  check; settling is a hint, never the completion verdict. Frames
  are compared in memory and deleted in the same breath — nothing
  is retained (owner's rule). The privacy claim is scoped honestly:
  true of the signal, and of the capture only as *in-memory,
  transient, never written, never sent.*
- **The inbox:** append-only record. States pending / read / acted
  / judge_pending; settle by identity, never by position. Readable
  without any seat page, or the backstop is hollow.
- **Wake paths:** fast — an identity-only notice delivered into the
  orchestrator's chat (starts her turn). Slow — a hook backstop.
  Dedupe on the idempotency key (seat + conversation + message ID),
  written to the inbox BEFORE either wake fires; consumer dedupes;
  the persisted high-water mark survives restarts.
- **The owner terminal:** escalations only, on settled evidence.

## 4. The wake refreshes her (owner's ruling)

A nudge does not remind a continuing orchestrator; it starts a
fresh one. Each wake begins a new turn whose context is: (1) a
summary generated at nudge time FROM THE RECORD, (2) the knock
itself, (3) the record beneath both, re-readable. Attention is
re-realized upon reading — a fresh judgment conditioned on the
present record, not a depleting stock. No wake is ever handled at
the tail of a long, prior-laden stretch.

**The summary has two halves.** STATE: open wakes and their ages,
in-flight work, last settlements, what waits on the owner.
TRAJECTORY: the expected next actions in order, read off the way
the conversation was going — last decisions, direction of travel,
commitments, constraints, acceptance tests. **Anti-laundering
fence:** every expected action cites the decision that authorised
it, or is labelled PROPOSED, not expected. A summary can carry a go
forward; it can never mint one.

## 5. Proof of attention

- **Settlement is an effect, not an acknowledgement.** A wake
  settles only when the orchestrator cites a value the inbox record
  alone holds (a short hash or record-only field). The sensor
  observes the citation; she never self-reports "got it."
- **Her canary:** a scheduled wake carrying a nonce that changes
  every cycle, settled the same way — proof of detection and of
  reading, not of liveness.
- **Negative controls:** planted wakes for records that do not
  exist. The correct response is "absent." A confident "present"
  is a confabulation alarm.
- **Working is a named state** with its own deadline, so a long
  task is never mistaken for a wedge.
- **Escalation ladder:** unsettled past its age → named state →
  escalation to the owner with per-state timers, including the
  behaviour when the owner is unreachable (what is safe to hold,
  what must not be sent late, when an unacknowledged escalation
  becomes a standing state).
- **Who watches the watcher:** the sensor shares the orchestrator's
  machine and fate. One witness must live off that machine — a
  dead-man's signal the owner must acknowledge — or a sleeping
  laptop reads as a quiet room.

## 6. Sends

A send is POSTED only when the sensor finds the sent body's hash
in the destination conversation. A draft present but unsent past
its age is CAUGHT — a named state. Neither the sender's claim nor
any courier's report counts as a witness; the destination is the
witness. The draft-size refusal guard applies before insert.

## 7. Tuning — two regimes (owner's ruling, Claude's border)

The axis is attention, not noise.

- **Knocks (wakes, detections): OVER-FIRE.** A false positive costs
  one read by a choosing judge; a false negative costs the evening.
  The judge is the filter.
- **Escalations to the owner and claims about sends: STRICT.**
  These spend the owner's attention and the orchestrator's
  credibility — the two things the design protects. Settled
  evidence only.
- **Calibration gauge (not a fatigue gauge):** a fixed set of
  labelled knocks replayed through the judge at intervals. Decline
  rate rising on IDENTICAL inputs = her threshold drifted. Rising
  only on live inputs = the knocks got noisier. Escalation hygiene
  is counted the same way: owner act-rate vs decline-rate.

## 8. States and witnesses (each state names its witness)

detected (camera change / DOM appearance) · complete (DOM verdict)
· delivered (destination hash) · attention (canary witnessed) ·
settled (record-value citation) · working (declared, deadline) ·
wedged (age past deadline, unsettled) · posted (destination hash) ·
caught (draft past age). Disagreement between witnesses is
UNRESOLVED — surfaced, never rounded.

## 9. Known overlaps and shared fates

Camera and DOM both depend on the same tab being rendered, the
same site unchanged, the same window unoccluded; background-tab
throttling can stall both, so they can agree wrongly. A transport
death looks like a blind camera; the checker distinguishes them
with the transport probe. The camera justifies its complexity only
by covering a failure the DOM cannot see (observer detached by a
re-render, a swapped node, an unreachable composer) — if a stage
cannot name that failure, the camera is decoration and is cut.

## 10. Fault-injection tests (before any stage is trusted)

Site update · observer detach · occluded window · canary failure ·
double wake · silent orchestrator · looping acknowledgement ·
false delivery claim · planted absent record · owner unreachable ·
sleeping laptop · minimal (one-character) reply at the chosen grid.

## 11. Build sequence (each stage a separate owner card)

- **Stage 0 — this paper + design round.** Reviewers rule on the
  plan as one document.
- **Stage 1 — measurement probe** (needs the scoped lift): a test
  conversation the owner watches; four cases (one-character reply,
  long stream, mid-stream pause, scroll); frames in memory only.
  Produces the numbers: settle window, thresholds, grid resolution,
  streaming durations, longest in-reply pause.
- **Stage 2 — doorbell, DOM only:** notice, inbox write, wake,
  heartbeat-as-proof-of-detection. No camera.
- **Stage 3 — camera gate:** frame-difference trigger + witness,
  delete-as-it-happens, probe-verified at Stage 1's numbers.
- **Stage 4 — proof of attention:** settlement-by-citation, canary,
  negative controls, working state, escalation ladder, refresh
  summaries (state + trajectory with the citation fence).
- **Stage 5 — calibration:** replay set, decline-rate measurement,
  escalation hygiene counts.
- **The fairy** renders this system's states for the owner; she is
  its face, built last, from record/FAIRY-DESIGN-2026-11-15.md,
  updated for the inversion (her primary subject is the
  orchestrator's attention).

## 12. Open decisions for the owner

1. The lift: scope and wording of the recorded entry (probe-only
   is the narrowest honest scope).
2. The off-machine witness: what it is, and the dead-man's
   acknowledgement path.
3. Escalation content: how much an escalation may carry for the
   owner to act on, against the minimal-content principle.
4. Canary cadence and settle ages (Stage 1 numbers inform these).
5. Whether the design round goes to Alex, Claude, or both, and in
   what order.

## 13. Non-goals

No retention of frames or content in any signal. No sends by the
sensor. No judging by the sensor. No model text in the wake path —
the wake is generated from the sensor's deterministic verdict and
carries identity only. No stage fires a wake at a live seat until
its own card says so.
