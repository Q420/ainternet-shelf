"use strict";
/* Pulse Bridge — persistent state (Blueprint §3, storage.js).
 *
 * One state object in chrome.storage.local:
 *   registrations: { remmy: {tabId, windowId, url, title, platform},
 *                    alex:  {same} | null }
 *   paused:        boolean — the presence switch (Ben's hand on the tap)
 *   seen:          [fingerprint, ...] — dedup ledger (bounded, FIFO)
 *   detections:    [ {envelope, detectedIn, at}, ... ] — Stage 2's proof
 *                    surface: what was detected, where, never yet sent
 *   log:           [ {at, text}, ... ] — visible run log (bounded)
 *
 * Access is serialised through the background worker; content scripts
 * and the popup never write directly.
 */

const PB_STATE_KEY = "pulseBridgeStateV1";
const PB_MAX_SEEN = 300;
const PB_MAX_DETECTIONS = 50;
const PB_MAX_LOG = 40;
const PB_MAX_DELIVERED = 300;

function pbDefaultState() {
  return {
    registrations: { remmy: null, alex: null },
    paused: false,
    seen: [],
    detections: [],
    delivered: [],      // fingerprints carried successfully (Stage 3; v0.6.0 ledger — kept as history)
    deliveryFailed: [], // fingerprints attempted and failed — no silent retry (v0.6.0 ledger)
    /* CRUSHER V6.1 (Alex ruling 1): the AUTHORITATIVE ledgers key
     * on the envelope message_id. seenIds/fpToId are the dedup
     * index: fpToId bridges the letterbox's fingerprint sightings
     * to the envelope id that carries the letter, so the same
     * letter sighted again is recognised as the same letter. */
    deliveredIds: [],      // message_ids confirmed delivered
    deliveryFailedIds: [], // message_ids attempted and failed
    seenIds: [],           // message_ids the router has accepted
    fpToId: {},            // fingerprint -> message_id
    /* V7 — THE PAIR MACHINE (Alex's direction, Ben's tap
     * 2026-11-07 03:15): the router remembers the current
     * TRANSACTION, not the conversation. pair is the ONE active
     * exchange: { step, from, to, callId, replyId, callOutcome,
     * failedReason, startedAt } with step one of "carry-call",
     * "await-reply", "carry-reply", "failed-recoverable".
     * bufferId names the ONE pending detection (newest wins)
     * waiting to start the next pair. seenIds/fpToId now index
     * ONLY the active records (pair letters + buffer); a retired
     * pair's entries are removed — the machine forgets on
     * purpose, and the letterbox's history absorption is what
     * keeps retired letters from re-firing off the page. */
    pair: null,
    bufferId: null,
    v7migrated: false,
    /* V0.11.0 P1: the file-handoff transfer record (Alex's ruling:
     * filename + original-byte hash + transport outcome preserved).
     * Bounded FIFO. Entries: {at, messageId, from, to, name,
     * declaredSha256, declaredBytes, actualSha256, actualBytes,
     * status, lfMatch}. status is the TRANSPORT outcome —
     * "verified" (content matches the sender's raw-byte hash),
     * "mismatch", "undeclared", "malformed". The end-to-end
     * FILE_* labels are earned at the receiving end (a real file
     * written, or content attested), never by this ledger alone. */
    fileTransfers: [],
    /* V0.11.0 P2: rollover record. Entries: {at, seat, fromUrl,
     * toUrl, fromTitle, notice, letterId}. Bounded FIFO. */
    rollovers: [],
    /* V0.16.0 BRIDGE ALERT: alert records (alert.js owns the
     * shape: {id, seat, headline, detail, at, chimed, acked}).
     * Bounded by PB_ALERT_MAX_RECORDS via pbAlertTrim. An
     * unacknowledged record is the popup's persistence: it
     * re-shows on load until Ben closes it. */
    alerts: [],
    /* V0.17.0 THE SEND-SAFETY FENCE (fence.js): the message
     * ledger's count. serialNext is the next serial to assign
     * — serials advance numerically, so keeping track is as
     * easy as counting (Ben's rule). completedSerials is the
     * small retained record of retired pairs' serials
     * ({serial, id, at}, bounded) — duplicate detection reads
     * it after the active record forgets a letter. */
    serialNext: 1,
    completedSerials: [],
    /* CONCLUSION BUILD (v0.22.0): retained handles (handles.js)
     * — the bounded shadow a completed letter leaves at pair
     * close: {message_id, from, to, body, fingerprint, closedAt,
     * closeState, relook}. Duplicate authority for completed
     * letters, the tombstone's evidence, and the late look's
     * retained text. Cap PB_HANDLE_CAP, evictions logged. */
    handles: [],
    log: [],
  };
}

async function pbLoadState() {
  const got = await chrome.storage.local.get(PB_STATE_KEY);
  return Object.assign(pbDefaultState(), got[PB_STATE_KEY] || {});
}

async function pbSaveState(state) {
  await chrome.storage.local.set({ [PB_STATE_KEY]: state });
}

function pbLog(state, text) {
  state.log.push({ at: new Date().toISOString(), text });
  if (state.log.length > PB_MAX_LOG) state.log = state.log.slice(-PB_MAX_LOG);
}

function pbMarkSeen(state, fingerprint) {
  if (!state.seen.includes(fingerprint)) {
    state.seen.push(fingerprint);
    if (state.seen.length > PB_MAX_SEEN) state.seen = state.seen.slice(-PB_MAX_SEEN);
  }
}

function pbRecordDetection(state, detection) {
  /* V0.17.0: every accepted message joins the ledger's count
   * at first sight (fence.js) — the serial the fence's
   * condition 2 reads, assigned here so no accepted letter
   * ever stands outside the count. */
  if (typeof PB_FENCE !== "undefined") PB_FENCE.pbFenceAssignSerial(state, detection);
  if (!detection.crusher) detection.crusher = pbCrusherRecord(detection.envelope, detection.at);
  state.detections.push(detection);
  if (state.detections.length > PB_MAX_DETECTIONS) {
    /* V0.12.1 (Alex's standing design requirement, Ben's fix order
     * 2026-11-08): the FIFO cap must never evict a letter still in
     * play — the active pair's call, reply or pending reply, or
     * the buffered message. Eviction takes the OLDEST UNPROTECTED
     * records only; if every record is protected the cap yields
     * rather than orphan a live letter (an over-cap record is
     * visible in the popup; a vanished letter was not). */
    const protectedIds = new Set();
    if (state.pair) {
      if (state.pair.callId) protectedIds.add(state.pair.callId);
      if (state.pair.replyId) protectedIds.add(state.pair.replyId);
      if (state.pair.pendingReplyId) protectedIds.add(state.pair.pendingReplyId);
    }
    if (state.bufferId) protectedIds.add(state.bufferId);
    /* V0.13.0: a Crusher question still waiting for its flagged
     * delivery to Remmy's seat is in play in exactly the pair
     * sense — the cap must not evict it before the lane drains. */
    for (const d of state.detections) {
      if (d.envelope && d.envelope.crusherFor && d.crusher &&
          d.crusher.state !== "ACKNOWLEDGED" && d.crusher.state !== "UNVERIFIED" &&
          d.crusher.state !== "FAILED") {
        protectedIds.add(d.envelope.message_id);
      }
    }
    /* CONCLUSION BUILD (v0.22.0), Part 3: a letter held as an
     * unresolved GROWTH NOTICE is waiting on Ben's decision —
     * it is in play in exactly the pair sense and the cap must
     * not evict it from under him. */
    for (const d of state.detections) {
      if (d.growthNotice && !d.growthNotice.resolution && d.envelope) {
        protectedIds.add(d.envelope.message_id);
      }
    }
    let excess = state.detections.length - PB_MAX_DETECTIONS;
    state.detections = state.detections.filter((d) => {
      if (excess <= 0) return true;
      const id = d.envelope && d.envelope.message_id;
      if (id && protectedIds.has(id)) return true;
      excess--;
      return false;
    });
  }
}

/* Stage 3 bookkeeping: mark a detection's delivery outcome on the
 * detection record itself (popup reads it) and in the ledgers. */
function pbMarkDelivered(state, fingerprint, at) {
  if (!state.delivered.includes(fingerprint)) {
    state.delivered.push(fingerprint);
    if (state.delivered.length > PB_MAX_DELIVERED) {
      state.delivered = state.delivered.slice(-PB_MAX_DELIVERED);
    }
  }
  for (const d of state.detections) {
    if (d.envelope && d.envelope.fingerprint === fingerprint) {
      d.delivery = { status: "delivered", at };
      if (d.crusher) pbCrusherTransition(d.crusher, "ACKNOWLEDGED", "receipt confirmed in destination conversation", at);
    }
  }
}

function pbMarkDeliveryFailed(state, fingerprint, reason, at) {
  if (!state.deliveryFailed.includes(fingerprint)) {
    state.deliveryFailed.push(fingerprint);
    if (state.deliveryFailed.length > PB_MAX_DELIVERED) {
      state.deliveryFailed = state.deliveryFailed.slice(-PB_MAX_DELIVERED);
    }
  }
  for (const d of state.detections) {
    if (d.envelope && d.envelope.fingerprint === fingerprint) {
      d.delivery = { status: "failed", reason: String(reason || "unknown"), at };
      if (d.crusher) pbCrusherTransition(d.crusher, "FAILED", String(reason || "unknown"), at);
    }
  }
}

/* CRUSHER (v0.6.0): the officer's record-keeping on a detection.
 * pbCrusherMark is the one door through which delivery outcomes
 * move a letter's state; it keeps the ledgers and the Crusher
 * state in step, so the popup's old lines and the new state line
 * can never disagree.
 *   outcome: "acknowledged" | "unverified" | "failed" | "stalled" | "held"
 *   stage:   the adapter stage that decided it ("" when none)
 *   reason:  the true stage's own words ("" when none)
 * UNVERIFIED deliberately enters NEITHER ledger: pbAlreadyDelivered
 * must never claim it either way.
 *
 * CRUSHER V6.1: the door is keyed on the envelope message_id (Alex
 * ruling 1) and writes the id ledgers (deliveredIds /
 * deliveryFailedIds). The v0.6.0 fingerprint ledgers are no longer
 * written — they remain in the state shape as history only. */
function pbCrusherMark(state, messageId, outcome, stage, reason, at) {
  const when = at || new Date().toISOString();
  if (!state.deliveredIds) state.deliveredIds = [];
  if (!state.deliveryFailedIds) state.deliveryFailedIds = [];
  for (const d of state.detections) {
    if (!d.envelope || d.envelope.message_id !== messageId) continue;
    if (!d.crusher) d.crusher = pbCrusherRecord(d.envelope, d.at);
    if (outcome === "acknowledged") {
      pbCrusherTransition(d.crusher, "ACKNOWLEDGED", "receipt confirmed in destination conversation", when);
      if (!state.deliveredIds.includes(messageId)) {
        state.deliveredIds.push(messageId);
        if (state.deliveredIds.length > PB_MAX_DELIVERED) state.deliveredIds = state.deliveredIds.slice(-PB_MAX_DELIVERED);
      }
      d.delivery = { status: "delivered", at: when, crusher: true };
    } else if (outcome === "unverified") {
      pbCrusherTransition(d.crusher, "UNVERIFIED", String(reason || "send clicked; no confirming turn appeared"), when);
      d.delivery = { status: "unverified", reason: String(reason || "no confirming user turn appeared"), at: when, crusher: true };
    } else if (outcome === "failed") {
      pbCrusherTransition(d.crusher, "FAILED", String(reason || stage || "failed"), when);
      if (!state.deliveryFailedIds.includes(messageId)) {
        state.deliveryFailedIds.push(messageId);
        if (state.deliveryFailedIds.length > PB_MAX_DELIVERED) state.deliveryFailedIds = state.deliveryFailedIds.slice(-PB_MAX_DELIVERED);
      }
      d.delivery = { status: "failed", reason: String(reason || "unknown"), stage: stage || "", at: when, crusher: true };
    } else if (outcome === "stalled") {
      pbCrusherTransition(d.crusher, "STALLED", String(reason || stage || "stalled"), when);
      d.delivery = { status: "stalled", reason: String(reason || "destination unreachable"), stage: stage || "", at: when, crusher: true };
    } else if (outcome === "held") {
      pbCrusherTransition(d.crusher, "HELD", String(reason || "bridge paused"), when);
      d.delivery = { status: "held", reason: String(reason || "bridge paused"), at: when, crusher: true };
    }
    /* COMBINED BUILD, Part C: the station face follows the
     * delivery truth (the handshake in station.js). An
     * acknowledged or unverified outcome means the adapter
     * did submit; a failure turns on its stage. A late
     * acknowledgement of an unconfirmed letter is
     * DELIVERED-LATE — the earlier uncertainty stays on the
     * trail; only the face advances. */
    if (typeof PB_STATION !== "undefined" && d.stationTaken) {
      const face = PB_STATION.pbStationHandshake({
        crusherState: d.crusher.state,
        deliveryStatus: d.delivery && d.delivery.status,
        stage: stage || (d.delivery && d.delivery.stage) || "",
        wasUnconfirmed: d.stationFace === "SENT-UNCONFIRMED",
        submitted: outcome === "acknowledged" || outcome === "unverified",
      });
      if (face) {
        d.stationFace = face;
        if (["DELIVERED", "DELIVERED-LATE", "SENT-UNCONFIRMED", "FAILED-BEFORE-SEND"].includes(face) && state.station) {
          state.station.lastOutcome = { pbId: messageId, outcome: face, at: when };
        }
      }
    }
  }
}
