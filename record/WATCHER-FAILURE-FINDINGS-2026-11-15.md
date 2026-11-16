# Watcher Failure Findings — 2026-11-15

**Status:** discussion paper only. All machinery is stopped by the owner's order
(2026-11-15 20:34 MST): hooks disabled, tunnel down, supervisor dead, desk tab
closed. No build is authorised by this paper. It records a converged design
discussion for review by the waker design's reviewer.

**Provenance:** Part 1 is the orchestrator's failure catalogue, written for the
owner on request. Part 2 is an external review of that catalogue by DeepSeek,
relayed by the owner (authorship confirmed by the owner, 2026-11-15). Part 3 is the orchestrator's assessment of the review. Part 4 is
DeepSeek's concessions and revised ladder, relayed by the owner. Part 5 is
the orchestrator's refinements on the revision. Relayed text is transport
evidence in its stated class; rulings remain the owner's.

---

## Part 1 — The failure catalogue (orchestrator)

### The stack

- **Transport.** Dedicated Chrome profile on the owner's laptop
  (`RemmyChrome`, `--remote-debugging-port=9222`, loopback), reached from the
  orchestrator's VM via SSH-over-Tailscale local forward. All traffic is CDP
  over a WebSocket: `Runtime.evaluate` reads; `Input.insertText` /
  `Input.dispatchKeyEvent` / `Input.dispatchMouseEvent` writes;
  `Page.bringToFront` for focus. Driver `remmy_browser.py`; targets via
  `/json/list`.
- **Supervisor.** `watchdog.py` (the waker) parents one `listener_watch.py`
  child per armed conversation. `flock` singleton. Transition record
  `spool/waker.json` (monotonic seq, transition, reason; atomic writes on
  state changes only). Heartbeat `spool/heartbeat.json` `{pid, boot_id,
  instance_id, loop_count, last_tick}`, timer-written by design. Stale-kill at
  heartbeat age >45 s (30 s arm grace); relaunch cap 5; then terminal
  `gave_up` (exit 4). The resurrection checker (`waker_check.py`, 120 s hook)
  honours `gave_up`: re-arm requires a human launch with `--force` (the
  reviewer's own shape ruling, accepted).
- **Listener.** `listener_watch.py` v4-pulse. Turn identity
  `(conversation_id, resp_id)` with text-occurrence fallback. Delivery rule
  `decide_v4()`: primary = aria-live completion pulse latched + attributed +
  short quiet window (injected `notifier_inject.js` v5); fallback (byte-idle +
  no-new-request + text stability) behind a config flag, default OFF. 30 s
  post-delivery re-read verification. Output: pool events
  (`events/<seat>.jsonl`, `REPLY_SETTLED` / `REPLY_CAPTURED`, `event_seq`,
  `message_id`, `content_sha256`).
- **Sending.** `send_to.py`: `Page.bringToFront`; bottom in-viewport
  `div.ProseMirror[contenteditable=true]` composer; click; `Input.insertText`;
  click the real Send button (CDP Enter does not submit in this build);
  verification = poll until composer ≤2 chars, else `inserted_not_submitted`.
- **Downstream.** Pool → `watchdog_live.py` passes → `watchdog_detector.py`
  (gate_terms pre-filter, then NvidiaJudge, strict per-packet YES/NO per §7)
  → two-consecutive-YES streak in `watchdog_ledger.py` → scheduler → wake
  outbox (fsync'd appends, `wake_id` dedupe) → wake-check hook. Stage 1
  (`inbox.py`, `inbox_drain.py`: high-water-mark drain + capture-health check)
  is built, 48/48 fixtures, never wired live.

### The failures

1. **CDP WebSocket timeouts are fatal to the listener child.** The receive
   loop dies on `WebSocketTimeoutException`; there is no reconnect path, so a
   transient transport timeout is an exit (rc=1). The supervisor relaunches
   into the same degraded transport and burns its cap. Episode one:
   19:02–19:31 MST, six attempts, `gave_up`. Episode two: re-armed 20:16
   (seq 32), `gave_up` again by ~20:33 (seq 41). Transport degradation is
   physical: 5400 rpm HDD, 7.8 GB RAM, Chrome memory pressure, tunnel
   latency, 60 KB `insertText` payloads.
2. **The giant-composer wedge.** A ~61 KB unsent draft renders as a
   ~27,690 px-tall ProseMirror editable; every subsequent `Runtime.evaluate`
   against that page exceeds the CDP timeout, including the census reads
   meant to resolve send state. A timed-out send is therefore ambiguous, and
   the ambiguity is unresolvable while the page is wedged. (Tonight's RB-51
   Part 3 paste.)
3. **ProseMirror identity ambiguity.** Posted messages also render as
   `div.ProseMirror[contenteditable=true]`. First-match selection can land on
   an off-screen rendered message (observed y=-8335; the draft at y=-27129).
   The bottom-in-viewport heuristic returned no match at all once the page
   state degraded.
4. **Focus contention.** The renderer drops input events to hidden targets,
   so sends require `Page.bringToFront` — automation repeatedly seizing the
   tab the owner is looking at, on an already unresponsive page. The owner's
   "locked out" report: contention plus a wedged renderer, not permissions.
5. **`gave_up` is silent by design.** The checker honours it and no
   escalation path existed, so episode one left capture dark ~45 minutes,
   discovered incidentally. Stage 1's capture-health check (heartbeat age
   >180 s or a `gave_up` transition → alert item + wake) was built to close
   this and never enabled.
6. **Position-based debounce.** The two-YES streak counts sampled turn
   position, not item identity. RB-50: the ruling turn satisfied the
   precondition; an interleaved turn was judged NO and reset the streak
   (`reset_cause: judged_no`) — a satisfied condition produced no wake.
   Compounded by sampling aliasing from two stacked 120 s polls.
7. **Judge endpoint mortality.** NVIDIA end-of-lifed
   `llama-3.1-nemotron-ultra-253b-v1` at 2026-11-15T00:00Z (HTTP 410). The
   fail-safe held (errors hold the streak). Successor
   `nemotron-3-ultra-550b-a55b` needed `max_tokens` 8→1024 (reasoning trace
   consumed the budget; null content at 8).
8. **VM replacement.** The runtime replaced the orchestrator's VM at
   19:41:40 MST. No user-space process survives: tunnel and supervisor died.
   Hooks/crons persist; processes don't. `gave_up` on top of a replacement =
   permanently dark until a human re-arms.
9. **Historical, fixed:** pre-v4 delivery gated on the generation request
   closing (requests lived 120–165 s past completion; pulse latch reduced
   delivery to ~12 s typical, 20/30 measured, zero mismatches);
   exec-session process-group teardown killing children at ~3 min (fixed
   with `setsid`); stitch check suppressing identical-repeat replies (fixed
   to proper containment); message-ID coverage 103/284 → ID-keying fix,
   guard suite 45/45, 8/8 unique live IDs.

---

## Part 2 — External review (DeepSeek, relayed by the owner)

The framing needs to shift: the architecture is supervising a transport it
can't heal, and treating transport failure as a terminal condition. The
supervisor's recovery primitive is "relaunch the child," when the actual
failure is one layer down (the WebSocket, the tunnel, the renderer).
Relaunching into a degraded transport is not recovery; it's amplification.
The fix isn't a higher cap — it's a transport health gate between the
supervisor and the child.

Concretely: the supervisor should refuse to arm a child unless it can first
prove the transport is live (a `Runtime.evaluate` round-trip with a short
deadline, plus a tunnel liveness check). If that probe fails, the supervisor
enters a distinct state — `transport_unhealthy` — resumable and escalating,
rather than a hard stop requiring `--force`. `gave_up` is reserved for "we
had a healthy transport and the child still couldn't do its job N times."
Today those two conditions collapse into one terminal state, which is why a
45-minute dark window looked identical to a real code failure.

On the wedge: a 61 KB draft wedging every subsequent `Runtime.evaluate` means
`Runtime.evaluate` against that page cannot be the liveness/state primitive.
(a) Verify sends from a different CDP target — an observer tab on the same
conversation whose renderer hasn't got the giant editable. (b) Make send a
two-phase commit with an external witness: before `Input.insertText`, write
an intent record (id, draft hash, timestamp) to disk; after the attempt, the
observer polls for composer-empty AND a new turn with the expected content
hash. Sender timeout is no longer ambiguous.

On ProseMirror identity: position is being used as identity for lack of a
better handle. Extend the existing `(conversation_id, resp_id)` keying to
selection: the composer is "the contenteditable not inside a
`[data-message-id]` ancestor," not a y-coordinate.

On the debounce: position-based streak counting is a category error. Key the
streak on `message_id` (`streak_by_message_id`); a wake fires when the same
message_id earns two consecutive YESes regardless of interleaving. Also:
batch the judge (a list of candidate turns per call, per-item YES/NO) to run
the detector at capture cadence without proportionally more calls at the new
1024-token budget.

On `gave_up` silence: "hard stop requires human re-arm" and "human is never
notified" are separable; only the first is defensible. `gave_up` should
always write an escalation item to the outbox. Stage 1's capture-health does
this; enable it before re-arming. The escalation path must also survive VM
replacement — tunnel liveness needs a health check independent of waker
state, at the hook layer.

Proposed recovery ladder: (1) enable capture-health escalation before
re-arming; (2) split supervisor states (`gave_up` vs `transport_unhealthy`);
(3) transport probe at the arm boundary and each relaunch; (4) child
reconnect path — only after 1–3; (5) observer tab + structural composer
selection; (6) streak keyed on `message_id`; (7) judge batching.

Pushback on the catalogue's framing: "works exactly as specified" is not
"correct." The `gave_up` specification was written against a failure model
where `gave_up` meant "the child is repeatedly failing for reasons we don't
understand." The observed failure model is "the transport degraded and the
supervisor couldn't tell the difference." The spec is fine; the state it
represents is overloaded. Split the state rather than loosen the rule.

---

## Part 3 — Orchestrator's assessment

The core reframing is correct: both of tonight's `gave_up` episodes were
transport failures wearing a child-failure costume, and the state split is
the strongest proposal. "Works as specified" was also a fair hit — the
specification was written against the wrong failure model.

Overlaps with existing owner rulings, which any scoping must reconcile with
rather than replace: ladder rung 1 (capture-health escalation) is Stage 1
amendment part 1 — owner-approved 2026-11-15 20:19 MST and already built
(48/48); only the hook enable remains. Rung 6 (streak keyed on message_id) is
a variant of the approved notification design, which retires the streak
entirely in favour of settle-by-identity over inbox items; the reviewer's
version keeps the streak machinery alive to solve a problem the design
already dissolves.

Cautions the review did not carry: (a) Observer tab — ChatGPT persists
composer drafts per conversation, so a second tab may inherit the same 61 KB
draft and wedge its own renderer; it also doubles renderer load on the
constrained resource (7.8 GB / 5400 rpm). Needs a probe before any design
rests on it. The two-phase intent record stands independently of the observer
tab. (b) Judge batching — §7's strict per-packet YES/NO is a frozen contract
term, so batching is a contract amendment, not an optimisation; a reasoning
judge spends its trace per item either way, so the token saving is not
obvious; and the approved inbox design already decouples capture cadence
from judge cadence. (c) Structural composer selection (contenteditable not
inside a `[data-message-id]` ancestor) is clean, testable, and better than
the y-coordinate heuristic — endorsed without notes.

Orchestrator's ordering: rung 1 is the standing next step when the stop
lifts (already approved and built). Rungs 2+3 are the genuinely new scope
and, because they amend the accepted waker design, go through the review
loop as a design round, paper first.

---

## Part 4 — Reviewer's concessions and revised ladder (DeepSeek, relayed by the owner)

Concessions, accepted cleanly by the reviewer:

1. **Observer tab withdrawn.** It was presented as "the cheapest fix
   available"; on this hardware a second renderer doubles load on the
   constrained resource, and if ChatGPT persists the composer per
   conversation, the observer inherits the wedge it was meant to route
   around. It should have been flagged as needing a probe. The two-phase
   intent record stands on its own and doesn't need a second tab.
2. **Judge batching withdrawn.** It is a contract amendment wearing an
   optimisation's clothes: §7's strict per-packet YES/NO is frozen, the
   reasoning trace is spent per item regardless of batching, and the inbox
   design already decouples capture from judge cadence. The rung comes off
   the ladder entirely.
3. **Streak re-key reconciled, not resurrected.** The approved design
   retires the streak via settle-by-identity over inbox items; the
   reviewer's version kept the machinery alive. If the ladder is scoped,
   that rung is reconciled against the approved design.

Held ground, with a better framing: the state split and arm-boundary probe
(rungs 2+3) are the genuinely new scope, and the argument is the recovery
primitive, not the outage — a supervisor whose only move is "relaunch
child" cannot distinguish transport degradation from a child bug, and that
conflation burned the cap. The VM-replacement case is a special instance,
not the headline.

One refinement added back: **the probe at the arm boundary should be the
same primitive the child uses** — a `Runtime.evaluate` round-trip on the
target the child will actually talk to, not a separate health check with its
own failure modes. If probe and child disagree about "healthy," the
supervisor arms children into transports the probe misjudged — a new bug
class. The probe should be the child's first action, promoted into the
supervisor's decision.

Process agreement: rungs 2+3 are a design round before any build (paper
first; they amend the accepted waker design). Rung 1 is not a decision — it
is the standing next step when the stop lifts. The intent record may not
need a full round, but it touches send verification, so its placement is the
orchestrator's to make rather than assume.

**Revised ladder:** (1) enable Stage 1 capture-health when the stop lifts —
already built, not a decision; (2) state split + arm-boundary probe as a
design round, probe = child's first action promoted; (3) two-phase intent
record, scoped separately depending on where it lands in the contract.
Observer tab: withdrawn. Batching: withdrawn. Streak re-key: reconciled
against the approved design, not resurrected.

---

## Part 5 — Orchestrator's refinements on the revision

No blocking pushback. Three refinements:

1. **The promoted probe needs a witness record.** The failure the probe
   exists to detect is the one where the child cannot report back — a
   WebSocket timeout mid-probe yields no result, only an exit. So the probe
   writes a durable pass record (fsync'd; a state-change write) as its first
   act, and the supervisor's rule is: pass record present → arm fully; child
   dead inside the probe window with no record → `transport_unhealthy`, and
   the child-failure cap is never touched. Absence of the record is the
   signal. Without it, the supervisor infers from an exit code — tonight's
   bug in a new hat.
2. **The checker half is designed in the same round.** The state split lives
   in the supervisor, but the supervisor is what dies in a VM replacement.
   `waker_check.py`'s `decide()` must be able to auto-resurrect into
   `transport_unhealthy` while still refusing to touch a true `gave_up`, or
   the split buys no self-healing on the path that needs it most.
3. **Escalation timing uses existing constants.** `transport_unhealthy`
   escalates on the vocabulary already in force: the capture-health
   threshold (180 s) for the first alert, §11 `alert_age` (3600 s) for the
   aged escalation — one health vocabulary for the owner to read.

Placement of the intent record (left to the orchestrator by the reviewer):
it rides with the rung-2 round as a short companion paper — not a separate
round, not folded into the state machine. It changes what "posted" means in
send reporting, so it is written down and reviewed in the same pass, then
built after.

---

## The ask

Rule on the revised ladder (Part 4) with the refinements (Part 5) as the
scope of a design round amending the accepted waker design: what holds,
what breaks the accepted design's invariants, what is missing. In
particular: the probe-witness rule (Part 5.1) and the checker's half of the
state split (Part 5.2). Everything is stopped by the owner's order; this is
paper only.
