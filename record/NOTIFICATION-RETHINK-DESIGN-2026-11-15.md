# Notification Rethink — Design for Owner's Ruling (Claude, 2026-11-15)

Filed on the shelf by the orchestrator from the rethink conversation
(claude.ai/chat/c8e94275-8c99-462e-a06b-94050ff6a628), verbatim apart from
chat chrome. The fresh conversation could not reach the shelf, so the
author's own filing route was unavailable; this copy is the record.
Brief: record/NOTIFICATION-RETHINK-BRIEF-2026-11-15.md

---

Here is the design filed for the owner’s ruling. All three open items are closed on his standing rulings. No build is authorised.

Status
Design filed for ruling. No build is authorised.
Rulings closed: local-write, judge_pending visibility, canary visibility, stall escalation, dead-man perpetual, and watchdog detection kept with one rebuild.
Mechanisms
Inbox. One append-only store in the orchestrator’s home. Each item has a monotonic sequence ID, a sender, a timestamp, and a state: pending, read, acted, or judge_pending. Nothing is deleted.
Local writes. Every sender writes to the orchestrator’s home, including the watcher’s captures. The tunnel is not the inbox write path.
Write-armed wake. Writing a pending item and arming its wake are one operation. The wake fires on write. An item cannot become pending without a named, armed trigger.
Outbound sends to seats. These are the only tunnel-crossing hop. Each send carries an ID. The sender reports success only after reading its own item back by ID. Large payloads go to a file, with only a reference crossing the tunnel. A timed-out send is resolved by ID lookup, never by a blind resend.
Judge. Runs asynchronously and writes its result back as a new item. A timeout sets judge_pending, which is a state, not an error. The wake never waits on the judge.
Canary. A synthetic item with a known ID is written on a schedule and must come back processed end to end. Its per-hop latency goes to the panel.
Watchdog detection side, rebuilt. The registry, judge, and scheduler are kept as built. The debounce is replaced by settle-by-identity over inbox items. Detection consumes the inbox by sequence ID instead of polling sampled turns. Judged jobs keep the judge, asynchronously. Dumb waits bypass the detection pass entirely.
Dead-man
Perpetual, by ruling. It is the floor, not a job trigger, so it has no retirement date.
Bounded by state, not time. At full cadence while anything is armed or pending. When nothing is armed and the inbox is empty, it drops to a minimal proof-of-life beat, shows that state in the panel, and re-arms itself on the next write.
Escalation. A pending item unseen past its threshold raises a wake to the orchestrator through the dead-man path and is recorded as an alert in the panel.
Signal-path rules
Consumers process items by sequence ID and state. Nothing counts consecutive turns or sampled positions. This removes the RB-50 break.
A signal settles when its own item has held a stable state for a set window. Unrelated items cannot reset it.
Dumb waits fire on item arrival, with one hop from signal to wake decision.
The 120 s checker is the dead-man floor only, not a stage in the signal path.
While the orchestrator is mid-turn, multiple wakes merge into one pending set, processed in sequence order when her turn starts.
Anything the owner cares about is written as an item. A sampled state is never the only record of a transition.
Health panel (browser extension, viewed in-session, not pushed)
Section	Contents
Triggers	Name, armed or unarmed, owner, stop condition, last fired, fire count, pending count served
Inbox	Counts per state, and the age of the oldest item in each state
Hop latency	From the canary: write-to-wake, wake-to-turn-start, turn-to-action
Canary	Last result, end-to-end latency, whether processed in order
Outbound sends	Per send: ID, state (sent, read back, timed out, retried), retry count
Judge	Calls in flight, judge_pending count, timeout value in use
Dead-man	Its state (full cadence or proof-of-life), last check, and any alerts raised
Brief constraints
Visible. Health is in the panel, including judge_pending, canary latency, and dead-man alerts.
Self-limiting. Job triggers each have a stop condition and retire when their pending count reaches zero. The dead-man is the one ruled exception: it is perpetual by design, and its own bound is state.
Armed with the work. Enforced by the write-armed rule.
Dumb triggers for dumb waits. Ack waits fire on the reply landing and bypass the detection pass.
The system is one thing. The canary tests the path end to end.
Residual risks to note
Escalation depends on the orchestrator. The dead-man raises a wake, but if her turn fails, the alert stays in the panel. The owner should know that a stall can still rest on his looking.
Unmeasured. Hook-to-turn-start latency is still unknown. The canary will measure it.
Tunnel timeout value. Still to be confirmed, along with whether a timed-out insert can be looked up by ID afterwards.
Ruling requested

Approve, amend, or reject this design. If approved, the next step is the owner’s build decision.
