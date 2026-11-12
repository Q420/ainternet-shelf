"use strict";
/* Pulse Bridge — CRUSHER, the Bridge Officer (v0.6.0).
 *
 * Ben and Alex's design, Remmy's build, 2026-11-06:
 * "Crusher is an agent inside the bridge whose job is to manage
 * message transportation between Ben, Alex and Remmy. He isn't a
 * fourth conversational participant. He's infrastructure."
 *
 * Crusher v1 is a deterministic STATE MACHINE — no LLM. The
 * reasoning seat is DEFINED here (the transition table and the
 * outcome vocabulary are its fences) but UNOCCUPIED: unplug the
 * brain-that-isn't-there and the cargo still arrives intact or
 * not at all, because there is no brain in the transport path.
 *
 * Every letter Crusher manages carries an explicit state and a
 * trail of timestamped state events. His only outputs are those
 * events — he never writes prose anywhere. (Standing order, Ben
 * 2026-11-06: if Crusher ever starts contributing unsolicited
 * opinions, the disciplinary procedure is "SHUT UP, WESLEY!")
 *
 * BLACK BOX status: PARKED by Ben 2026-11-06 23:29 — Crusher v1
 * sees message text exactly as the v0.5.x router did (he must, to
 * route by fingerprint); envelope-only transport is future work.
 *
 * Legal transitions (anything else is refused and logged):
 *   OBSERVING    → CAPTURING     a marked bubble sighted
 *   CAPTURING    → SETTLING      settle window opens
 *   SETTLING     → VERIFIED      text stable + speaker verified
 *                  (a letter that fails verification goes straight
 *                   to FAILED with the true stage — see letterbox)
 *   VERIFIED     → DELIVERING    background accepts the handoff
 *   DELIVERING   → ACKNOWLEDGED  receipt evidence: a confirming
 *                                user turn in the destination
 *   DELIVERING   → UNVERIFIED    send clicked but no confirming
 *                                turn appeared — the machine says
 *                                "I don't know" instead of FAILED
 *   DELIVERING   → FAILED        a pre-send stage failed finally
 *                                (after the bounded retry policy)
 *   DELIVERING   → STALLED       destination unreachable: tab not
 *                                registered / content script dead
 *   any delivery → HELD          bridge paused at attempt time —
 *                                the letter waits for Ben's hand
 *
 * The DETECTION half of the states (OBSERVING..VERIFIED) is
 * reported by the letterbox, which remains the sensor; Crusher's
 * own machine starts at the handoff (VERIFIED) and owns
 * DELIVERING onward. The letterbox's internal settle bookkeeping
 * is unchanged from v0.5.1.
 *
 * Retry policy (fork 3, Remmy's line, in the approved scope):
 * machine-bounded — a delivery attempt may be retried only when
 * it failed BEFORE the send click (stages: gating, adapter,
 * composer, engage, type, verify-type, send-button), at most
 * PB_CRUSHER_MAX_ATTEMPTS attempts total. After the send click:
 * never retried — the outcome is ACKNOWLEDGED or UNVERIFIED.
 *
 * CRUSHER V6.1 (Alex's consultation ruling, 2026-11-07; Ben's tap
 * to build, 02:44): the machine grows the ruling's fences —
 *   - identity is the envelope message_id (protocol/storage carry
 *     that change; this file owns the policy numbers below);
 *   - PROVEN-ABSENCE retry: when confirmation positively
 *     establishes absence (verdict "absent" — never "unknown"),
 *     a delivery may be retried at most PB_CRUSHER_MAX_ABSENCE_
 *     RETRIES times, PB_CRUSHER_ABSENCE_RETRY_DELAY_MS apart,
 *     always under the SAME message_id. Exhaustion is STALLED
 *     with the evidence preserved — not a failure, not a guess.
 *   - destination deference is bounded by PB_CRUSHER_DEFER_MAX_MS:
 *     delivery waits that long for the destination to stop
 *     generating (Ben's button-state gate reads the state), then
 *     STALLS with the reason named. "generating" is deliberately
 *     NOT a pre-send stage: it is not retried on the 1200ms loop,
 *     it is waited out inside the attempt and then stalled.
 *   - attempt accounting: pbCrusherNote lets any attempt path
 *     leave a trail entry WITHOUT moving the state, so no letter
 *     can sit unexplained (the v0.6.0 goodnight jam, Finding 4).
 *
 * CRUSHER V6.2 (Ben's tap, 2026-11-07 02:24, after the V6.1 live
 * test): the machine learns queue manners from what the live test
 * did to it —
 *   - RETRY_WAIT: a letter with a scheduled next attempt WAITS
 *     WITHOUT holding the bridge. V6.1's absence retry slept 30s
 *     inside the single delivery slot while every other letter —
 *     both directions — stood deferred behind it, and fresh
 *     letters could jump older waiting ones. Now any "try again
 *     later" (proven-absence retry, generating requeue,
 *     unreachable requeue) parks the letter in RETRY_WAIT with a
 *     due time; the pump serves letters oldest-actionable-first.
 *   - generating / unreachable stalls SELF-REQUEUE, bounded by
 *     PB_CRUSHER_MAX_AUTO_RETRIES automatic requeues; V6.1 parked
 *     them in STALLED until some external event fired a sweep.
 *     Budget exhaustion still lands in STALLED, where Ben's
 *     sweeps (registration, resume) own it, as before.
 *   - the proven-absence policy itself is UNCHANGED (Alex ruling
 *     2: max 2 retries, same message_id, exhaustion terminal).
 *     What changed is only WHERE the letter waits between them.
 */

const PB_CRUSHER_STATES = [
  "OBSERVING", "CAPTURING", "SETTLING", "VERIFIED",
  "DELIVERING", "ACKNOWLEDGED", "UNVERIFIED", "FAILED", "STALLED", "HELD",
  "RETRY_WAIT",
  /* V0.14.0 (SPEC-V0.14.0, Alex's ALEX-FINAL authorisation
   * pb-mw958sfx-2-3x50, Ben's tap 2026-11-09 02:55): GATED — the
   * send-side button gate holds a letter BEFORE any attempt while
   * the destination is generating (no attempt, no budget spent);
   * STOPPED — the gate's bounded wait expired (GATE_TIMEOUT):
   * terminal, never self-resuming; only an explicit intervention
   * (a fresh record, Ben's retry) moves the letter again. */
  "GATED", "STOPPED",
];

const PB_CRUSHER_TRANSITIONS = {
  OBSERVING: ["CAPTURING"],
  CAPTURING: ["SETTLING"],
  SETTLING: ["VERIFIED", "FAILED"],
  VERIFIED: ["DELIVERING", "HELD", "STALLED", "GATED", "ABANDONED"],
  DELIVERING: ["ACKNOWLEDGED", "UNVERIFIED", "FAILED", "STALLED", "HELD", "RETRY_WAIT"],
  HELD: ["DELIVERING", "STALLED", "GATED", "ABANDONED"],
  ACKNOWLEDGED: [],
  UNVERIFIED: [],
  FAILED: ["RETRY_WAIT", "STOPPED", "ABANDONED"],
  STALLED: ["DELIVERING", "GATED", "RETRY_WAIT", "VERIFIED", "ABANDONED", "HELD"],
  RETRY_WAIT: ["DELIVERING", "STALLED", "HELD", "GATED", "ABANDONED", "VERIFIED", "STOPPED"],
  GATED: ["DELIVERING", "STOPPED", "HELD", "ABANDONED"],
  /* V0.15.0: STOPPED is terminal for the MACHINE (it never
   * resumes on its own) — Ben's Try again re-enters it at
   * VERIFIED with history intact; his Let it go resolves it. */
  STOPPED: ["VERIFIED", "ABANDONED"],
  /* V0.15.0: terminal, reachable only by Ben's recorded
   * decision — the machine can never abandon a letter. */
  ABANDONED: [],
};

/* Pre-send stages: a failure at one of these may be retried,
 * because nothing has been sent yet. Everything else is final. */
const PB_CRUSHER_PRESEND_STAGES = [
  "gating", "adapter", "composer", "engage", "type", "verify-type", "send-button",
];
const PB_CRUSHER_MAX_ATTEMPTS = 3;
const PB_CRUSHER_RETRY_DELAY_MS = 1200;

/* V6.1 proven-absence retry (Alex ruling 2): two retries maximum,
 * 30 seconds apart, only on positively established absence. The
 * delay honours a test seam (PB_TEST_ABSENCE_RETRY_DELAY_MS) so
 * the fixture can run the policy in milliseconds; production
 * always sees 30000. */
const PB_CRUSHER_MAX_ABSENCE_RETRIES = 2;
const PB_CRUSHER_ABSENCE_RETRY_DELAY_MS =
  (typeof PB_TEST_ABSENCE_RETRY_DELAY_MS !== "undefined" && PB_TEST_ABSENCE_RETRY_DELAY_MS > 0)
    ? PB_TEST_ABSENCE_RETRY_DELAY_MS : 30000;

/* V6.1 destination deference bound (Alex design (c)): how long a
 * delivery waits for the destination page to stop generating
 * before it stalls with the reason named. */
const PB_CRUSHER_DEFER_MAX_MS = 45000;

/* V6.2 self-requeue (Ben's tap, 2026-11-07): a letter stalled by
 * a still-generating or unreachable destination re-queues ITSELF
 * after this delay — the pump, woken by an alarm/timer, gives it
 * the next attempt without waiting for Ben's hand or an unrelated
 * sweep. At most PB_CRUSHER_MAX_AUTO_RETRIES automatic requeues;
 * then the letter parks in STALLED, where registration/resume
 * sweeps own it (the V6.1 behaviour, now the last resort instead
 * of the only one). The delay honours a test seam so fixtures run
 * the policy in milliseconds. */
const PB_CRUSHER_REQUEUE_DELAY_MS =
  (typeof PB_TEST_REQUEUE_DELAY_MS !== "undefined" && PB_TEST_REQUEUE_DELAY_MS > 0)
    ? PB_TEST_REQUEUE_DELAY_MS : 20000;
const PB_CRUSHER_MAX_AUTO_RETRIES = 4;

/* V0.14.0 Mechanism A — the send-side button gate's bound
 * (Alex's ruling, value approved by Ben 2026-11-09): a letter may
 * wait in GATED at most five minutes; past the bound it stops
 * (STOPPED / GATE_TIMEOUT) — still no attempt, still no budget,
 * and a human decides what happens next. The bound honours a
 * test seam so fixtures run it in milliseconds. */
const PB_GATE_MAX_MS =
  (typeof PB_TEST_GATE_MAX_MS !== "undefined" && PB_TEST_GATE_MAX_MS > 0)
    ? PB_TEST_GATE_MAX_MS : 300000;

/* A fresh Crusher record for one envelope. */
function pbCrusherRecord(envelope, at) {
  return {
    state: "VERIFIED",
    attempts: 0,
    absenceRetries: 0, // V6.1: proven-absence retries used
    autoRetries: 0,    // V6.2: automatic requeues used (generating/unreachable)
    nextAttemptAt: null, // V6.2: RETRY_WAIT due time (ISO) — the pump serves it then
    /* V0.14.0 gate bookkeeping: gateSince (ISO) starts the
     * five-minute bound; gateWake marks a cleared-notification (or
     * a wide sweep) so the pump may re-check; stopReason names a
     * STOPPED letter's cause ("GATE_TIMEOUT"); gateTimeoutPending
     * means the B6 failure popup still owes Ben a showing;
     * gateTimeoutNotified latches once it has been shown. */
    gateSince: null, gateWake: false, stopReason: null,
    gateTimeoutPending: false, gateTimeoutNotified: false,
    /* V0.15.0 (spec sections 3-4): the bounded recovery
     * ladder's bookkeeping, the letter-pause overlay, and the
     * human intervention record. Commands never reset these. */
    recovery: null, pausedAt: null, pausePending: false,
    interventions: [], abandonedBy: null,
    trail: [{ state: "VERIFIED", at: at || new Date().toISOString(), note: "handoff accepted" }],
  };
}

/* V6.1 attempt accounting: append a trail entry WITHOUT moving
 * the state. Every attempt path — deferred, caught, retried —
 * leaves its mark through here or through a transition, so a
 * letter's record always says what happened to it. */
function pbCrusherNote(rec, note, at) {
  rec.trail.push({ state: rec.state, at: at || new Date().toISOString(), note: String(note || "") });
}

/* Move a record to a new state. Returns true when the transition
 * is legal; on an illegal transition the record does not move and
 * the attempt is noted in the trail (never silently dropped). */
function pbCrusherTransition(rec, to, note, at) {
  const when = at || new Date().toISOString();
  const legal = (PB_CRUSHER_TRANSITIONS[rec.state] || []).includes(to);
  if (!legal) {
    rec.trail.push({ state: rec.state, at: when, note: "REFUSED transition " + rec.state + " → " + to + (note ? " (" + note + ")" : "") });
    return false;
  }
  rec.state = to;
  rec.trail.push({ state: to, at: when, note: note || "" });
  return true;
}

function pbCrusherIsPresend(stage) {
  return PB_CRUSHER_PRESEND_STAGES.includes(stage);
}

const PB_CRUSHER = {
  PB_CRUSHER_STATES, PB_CRUSHER_TRANSITIONS,
  PB_CRUSHER_PRESEND_STAGES, PB_CRUSHER_MAX_ATTEMPTS, PB_CRUSHER_RETRY_DELAY_MS,
  PB_CRUSHER_MAX_ABSENCE_RETRIES, PB_CRUSHER_ABSENCE_RETRY_DELAY_MS, PB_CRUSHER_DEFER_MAX_MS,
  PB_CRUSHER_REQUEUE_DELAY_MS, PB_CRUSHER_MAX_AUTO_RETRIES, PB_GATE_MAX_MS,
  pbCrusherRecord, pbCrusherTransition, pbCrusherIsPresend, pbCrusherNote,
};
if (typeof window !== "undefined") window.PB_CRUSHER = PB_CRUSHER;
if (typeof module !== "undefined" && module.exports) module.exports = PB_CRUSHER;
