"use strict";
/* Pulse Bridge — THE SEND-SAFETY FENCE (v0.17.0).
 *
 * Ben's design (2026-11-09, his words and his ruling — "im
 * ruling"): the bridge stops asking only the SEND/STOP button
 * for permission and starts asking whether THIS message is
 * safe to send. Three conditions, each answered POSITIVE,
 * NEGATIVE or UNKNOWN from evidence — never from assumption:
 *
 *   Condition 1 — BUTTON STATUS. The destination's composer
 *     button, read on its own face in its own scope: send face
 *     = positive, stop face (the recipient is generating) =
 *     negative, unreadable = UNKNOWN.
 *   Condition 2 — SERIAL ORDER. Every message carries a serial
 *     that advances numerically — keeping track is as easy as
 *     counting. A letter is in order when no earlier serial in
 *     its own lane is still undelivered, and when the letter
 *     is a reply it has not been superseded by a newer message
 *     from the seat it answers. Out of order = negative.
 *     No serial (not yet adopted into the ledger) = UNKNOWN.
 *   Condition 3 — MESSAGE STATUS. Delivered is a state: a
 *     message whose id stands in the delivered ledger, or
 *     whose record is acknowledged or abandoned, can never be
 *     sent again = negative. A live, sendable record =
 *     positive. Anything else = UNKNOWN.
 *
 * THE RULE (Ben's, with Alex's additions): at least two
 * positives AND no negative = send. A proven negative vetoes,
 * whatever the other conditions say. UNKNOWN never counts as
 * a pass. Ben's explicit STOP stands above the quorum (the
 * background's pause and per-letter pause checks run before
 * the fence is ever consulted, unchanged).
 *
 * A held letter is held VISIBLY — the failing or unproven
 * condition is named on its trail and in the log — and never
 * auto-redirected at a newer message. A superseded reply does
 * not send at all: its pair closes as superseded and the newer
 * message starts the next pair (the pair machine's reconcile).
 *
 * This file is the pure logic: conditions over plain state,
 * the verdict, and the ledger's bookkeeping (serial assignment
 * and pair retirement into the completed record). The
 * background gathers the live inputs (the button read costs a
 * tab message) and acts on the verdict. */

const PB_FENCE_TERMINAL = ["ACKNOWLEDGED", "UNVERIFIED", "ABANDONED", "STOPPED", "FAILED"];
const PB_FENCE_SENDABLE = ["VERIFIED", "HELD", "GATED", "RETRY_WAIT", "STALLED"];
const PB_COMPLETED_SERIALS_MAX = 50;
const PB_FENCE_RECHECK_MS = 20000;

/* Condition 1 from the generation query's word. The query
 * layer already speaks this vocabulary ("generating" /
 * "ready" / "unknown"); the fence just refuses to let
 * "unknown" pretend to be either of the others. */
function pbFenceButtonCondition(genWord) {
  if (genWord === "generating") return "negative";
  if (genWord === "ready") return "positive";
  return "unknown";
}

/* Condition 2 over the ledger. `detections` is the state's
 * detection list; `det` the letter under evaluation; `pair`
 * and `bufferDet` describe the machine's current shape.
 * Returns {value, why} — why names the exact shape that
 * decided it, for the trail. */
function pbFenceSerialCondition(detections, det, pair, bufferDet) {
  if (!det || det.serial == null) {
    return { value: "unknown", why: "no serial — not yet adopted into the ledger" };
  }
  const env = det.envelope || {};
  /* Superseded: this letter is its pair's reply, and a NEWER
   * message from the seat it answers is already waiting in
   * the buffer. Ben's case, in his words: a reply to A must
   * not send once B has arrived — it reconciles instead. */
  if (pair && pair.replyId && env.message_id === pair.replyId && bufferDet &&
      bufferDet.envelope && bufferDet.envelope.from === env.to &&
      bufferDet.serial != null) {
    const callDet = (detections || []).find((d) => d.envelope && d.envelope.message_id === pair.callId);
    if (callDet && callDet.serial != null && bufferDet.serial > callDet.serial) {
      return { value: "negative", why: "superseded — a newer message (#" + bufferDet.serial + ") from " + env.to + " arrived while this reply (#" + det.serial + ") waited", superseded: true };
    }
  }
  /* Out of order: an earlier serial in the SAME lane (same
   * from, same to) is still undelivered. The count is the
   * order; a letter never jumps it. */
  for (const m of detections || []) {
    if (!m || m === det || m.serial == null || m.serial >= det.serial) continue;
    const me = m.envelope || {};
    if (me.from !== env.from || me.to !== env.to) continue;
    const st = m.crusher && m.crusher.state;
    if (PB_FENCE_TERMINAL.includes(st)) continue;
    return { value: "negative", why: "out of order — #" + m.serial + " in the same lane is still undelivered; this letter is #" + det.serial, superseded: false };
  }
  return { value: "positive", why: "serial #" + det.serial + " is next in its lane's count" };
}

/* Condition 3: delivered is a state, and it is checked, not
 * assumed. */
function pbFenceStatusCondition(deliveredIds, det) {
  const env = (det && det.envelope) || {};
  const st = det && det.crusher && det.crusher.state;
  if ((deliveredIds || []).includes(env.message_id) || st === "ACKNOWLEDGED") {
    return { value: "negative", why: "already delivered — a delivered message is never sent again" };
  }
  if (st === "ABANDONED") {
    return { value: "negative", why: "let go — Ben retired this letter; it does not send" };
  }
  if (PB_FENCE_SENDABLE.includes(st)) {
    return { value: "positive", why: "the record is live and sendable (" + st + ")" };
  }
  return { value: "unknown", why: "the record's state (" + (st || "none") + ") proves nothing either way" };
}

/* The verdict. `conds` = {button, serial, status}, each
 * "positive" | "negative" | "unknown".
 *
 * FINAL F-5 (Ben's ruling, Stage 0 Pack SS2.5 / Build Plan 01
 * SS4 item 5 — Combined Build, Part B item 5) refines the
 * original quorum for the button's proven NEGATIVE:
 * - A proven refusal from the record itself — serial order
 *   NEGATIVE (out of order / superseded) or message status
 *   NEGATIVE (already delivered / let go) — never sends. It
 *   is a refusal hold, not a logic fault.
 * - Button NEGATIVE against serial AND status both POSITIVE
 *   is a LOGIC FAULT: the evidence contradicts itself (the
 *   page says the recipient is generating while the record
 *   says this letter is in order and sendable). No send, and
 *   NOT waited out — it stops visibly for a human.
 * - Button NEGATIVE with either other condition non-positive
 *   is an ordinary HOLD (the gate's hold: wait for the page).
 * - Otherwise the quorum stands: UNKNOWN button plus the two
 *   positives proceeds; two positives with no negative send;
 *   anything less holds, naming what is unproven. */
function pbFenceVerdict(conds) {
  const names = { button: 1, serial: 2, status: 3 };
  const entries = Object.entries(conds || {});
  const negatives = entries.filter(([, v]) => v === "negative").map(([k]) => k);
  const positives = entries.filter(([, v]) => v === "positive").map(([k]) => k);
  const unknowns = entries.filter(([, v]) => v === "unknown").map(([k]) => k);
  const base = { positives: positives.length, negatives, unknowns };
  const refusal = ["serial", "status"].find((k) => conds && conds[k] === "negative");
  if (refusal) {
    return { ...base, action: "hold", veto: refusal, vetoName: names[refusal], refusal };
  }
  if (conds && conds.button === "negative") {
    if (conds.serial === "positive" && conds.status === "positive") {
      return { ...base, action: "logic-fault", veto: "button", vetoName: 1, refusal: null };
    }
    return { ...base, action: "hold", veto: "button", vetoName: 1, refusal: null };
  }
  if (positives.length >= 2) return { ...base, action: "send", veto: null, vetoName: null, refusal: null };
  return { ...base, action: "hold", veto: null, vetoName: null, refusal: null };
}

function pbFenceConditionName(n) {
  return n === 1 ? "button status" : n === 2 ? "serial order" : n === 3 ? "message status" : "the fence";
}

/* The ledger's count. Assigns the next serial to a detection
 * that has none (first sight, or adoption of a pre-fence
 * record). Mutates state + detection; returns the serial. */
function pbFenceAssignSerial(state, det) {
  if (!state || !det) return null;
  if (det.serial != null) return det.serial;
  if (typeof state.serialNext !== "number" || state.serialNext < 1) state.serialNext = 1;
  det.serial = state.serialNext;
  state.serialNext += 1;
  return det.serial;
}

/* Pair retirement (Ben's lifecycle): when a pair closes, its
 * letters' serials move into the completed record — out of
 * the active count, never forgotten entirely. The small
 * completed record is what duplicate detection reads.
 * `serials` = [{serial, id}]. Bounded FIFO. */
function pbFenceRetireSerials(state, serials) {
  if (!state) return;
  if (!Array.isArray(state.completedSerials)) state.completedSerials = [];
  for (const s of serials || []) {
    if (!s || s.serial == null) continue;
    if (state.completedSerials.some((c) => c.id === s.id)) continue;
    state.completedSerials.push({ serial: s.serial, id: s.id, at: new Date().toISOString() });
  }
  if (state.completedSerials.length > PB_COMPLETED_SERIALS_MAX) {
    state.completedSerials = state.completedSerials.slice(-PB_COMPLETED_SERIALS_MAX);
  }
}

function pbFenceIsCompleted(state, id) {
  return !!((state && state.completedSerials) || []).some((c) => c.id === id);
}

const PB_FENCE = {
  PB_FENCE_TERMINAL, PB_FENCE_SENDABLE, PB_COMPLETED_SERIALS_MAX, PB_FENCE_RECHECK_MS,
  pbFenceButtonCondition, pbFenceSerialCondition, pbFenceStatusCondition,
  pbFenceVerdict, pbFenceConditionName, pbFenceAssignSerial,
  pbFenceRetireSerials, pbFenceIsCompleted,
};
if (typeof window !== "undefined") window.PB_FENCE = PB_FENCE;
if (typeof module !== "undefined" && module.exports) module.exports = PB_FENCE;
