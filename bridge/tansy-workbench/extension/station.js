"use strict";
/* Pulse Bridge — THE STATION CORE (Combined Build, Part C).
 *
 * The background-owned state machine for Ben's held-message
 * station (Station Host Design Note 01; Build Plan 01 SS5).
 * Pure logic over plain state, in the fence.js mould: the
 * background owns the station, the timers and the lock;
 * overlays in the two seat windows render acknowledged state
 * and send owner commands here. No DOM lives in this file.
 *
 * Faces an item wears, in order of its life:
 *   HELD        — in the station, append window running;
 *                 push-through and cancel are live.
 *   QUEUED      — waiting behind the held item; its window
 *                 has NOT started (the window is serial).
 *   RELEASED    — window expired or pushed through; the pump
 *                 may dispatch it (all ordinary gates stand).
 *   ATTEMPTING  — the pump took it; a pre-click attempt is
 *                 persisted and running. NOT dispatch (Alex's
 *                 review SS4): nothing has been submitted.
 *   TRANSIT     — the adapter actually submitted; the travel
 *                 animation runs only from here, and it never
 *                 proves delivery.
 *   DELIVERED / FAILED-BEFORE-SEND / SENT-UNCONFIRMED /
 *   DELIVERED-LATE — the dispatch handshake outcomes.
 *   CANCELLED   — Ben's pre-submit disposition (Amendment 01
 *                 item 6); the record is retained.
 *
 * PB-FILE payloads are never station items: they travel the
 * separate PB-FILE channel (Build Plan 01 SS4 item 2). */

const PB_STATION_WINDOW_MS = 7500;
const PB_FILE_HEADER_PRESENT = /^\[PB-FILE:\s*[^\]]+\]\s*$/m;

function pbStationDefault() {
  return { current: null, queue: [], position: { xPct: 50, yPct: 50 }, lastOutcome: null };
}

function pbStationHasFilePayload(body) {
  return PB_FILE_HEADER_PRESENT.test(String(body || ""));
}

/* A letter enters the station. Returns {entered, face} or
 * {entered:false, reason:'pb-file-channel'} for file payloads. */
function pbStationEnter(station, item, nowMs) {
  if (!station || !item || !item.pbId) return { entered: false, reason: "no-item" };
  if (pbStationHasFilePayload(item.body)) return { entered: false, reason: "pb-file-channel" };
  const rec = {
    pbId: item.pbId, indexId: item.indexId || null,
    from: item.from || null, to: item.to || null,
    body: item.body || "", enteredAt: nowMs,
    windowOpensAt: null, windowExpiresAt: null,
    face: "QUEUED", pushedThrough: false, appended: false,
  };
  if (!station.current) {
    rec.face = "HELD";
    rec.windowOpensAt = nowMs;
    rec.windowExpiresAt = nowMs + PB_STATION_WINDOW_MS;
    station.current = rec;
    return { entered: true, face: "HELD" };
  }
  station.queue.push(rec);
  return { entered: true, face: "QUEUED" };
}

/* The window runs out: the held item is RELEASED to the pump.
 * Returns the released pbId, or null. The item stays current
 * until the pump takes it (pbStationTake). */
function pbStationTick(station, nowMs) {
  const c = station && station.current;
  if (c && c.face === "HELD" && !c.appendOpen && nowMs >= c.windowExpiresAt) {
    c.face = "RELEASED";
    return { released: c.pbId };
  }
  return { released: null };
}

/* Push-through: Ben releases the held item now. Only a HELD
 * item can be pushed; anything else is reported, not forced. */
function pbStationPushThrough(station, pbId) {
  const c = station && station.current;
  if (!c || c.pbId !== pbId) return { ok: false, reason: "not-the-held-item" };
  if (c.face !== "HELD") return { ok: false, reason: "not-held", face: c.face };
  c.face = "RELEASED";
  c.pushedThrough = true;
  return { ok: true };
}

/* Cancel (Amendment 01 item 6): an owner disposition that
 * lands ONLY before dispatch. A HELD or QUEUED item is
 * cancelled and its record retained in lastOutcome; a
 * RELEASED-or-later item reports its true face — cancel
 * never claims a recall. Duplicate cancel is a no-op. */
function pbStationCancel(station, pbId, nowMs) {
  if (!station) return { cancelled: false, reason: "no-station" };
  const c = station.current;
  if (c && c.pbId === pbId) {
    if (c.face === "HELD" || c.face === "QUEUED") {
      station.lastOutcome = { pbId, outcome: "CANCELLED", at: nowMs };
      station.current = null;
      pbStationPromote(station, nowMs);
      return { cancelled: true, was: c.face };
    }
    return { cancelled: false, reason: "too-late", face: c.face };
  }
  const qi = (station.queue || []).findIndex((q) => q.pbId === pbId);
  if (qi >= 0) {
    station.queue.splice(qi, 1);
    station.lastOutcome = { pbId, outcome: "CANCELLED", at: nowMs };
    return { cancelled: true, was: "QUEUED" };
  }
  return { cancelled: false, reason: "not-found" };
}

/* The pump takes a RELEASED item for its attempt. Promotes
 * the next queued item with a FRESH window (serial windows).
 * The taken item's face is ATTEMPTING — a persisted pre-click
 * attempt, which is NOT dispatch (Alex's review SS4). */
function pbStationTake(station, pbId, nowMs) {
  const c = station && station.current;
  if (!c || c.pbId !== pbId) return { took: false, reason: "not-current" };
  if (c.face !== "RELEASED") return { took: false, reason: "not-released", face: c.face };
  c.face = "ATTEMPTING";
  station.current = null;
  pbStationPromote(station, nowMs);
  return { took: true, item: c };
}

/* APPEND PAUSES THE TIMER (Alex's review SS5): while Ben is
 * writing his segment, the window does not run out. Opening
 * records the remaining time; closing resumes from it. No
 * overlapping or resetting windows — the pause preserves the
 * remaining span exactly, it never grants a fresh one. */
function pbStationAppendOpen(station, pbId, nowMs) {
  const c = station && station.current;
  if (!c || c.pbId !== pbId || c.face !== "HELD") return { ok: false, reason: "not-held" };
  if (c.appendOpen) return { ok: true, already: true };
  c.appendOpen = true;
  c.appendRemainingMs = Math.max(0, c.windowExpiresAt - nowMs);
  return { ok: true, remainingMs: c.appendRemainingMs };
}
function pbStationAppendClose(station, pbId, nowMs) {
  const c = station && station.current;
  if (!c || c.pbId !== pbId || !c.appendOpen) return { ok: false, reason: "not-open" };
  c.appendOpen = false;
  c.windowExpiresAt = nowMs + (c.appendRemainingMs || 0);
  delete c.appendRemainingMs;
  return { ok: true, windowExpiresAt: c.windowExpiresAt };
}

function pbStationPromote(station, nowMs) {
  if (station.current || !station.queue.length) return null;
  const next = station.queue.shift();
  next.face = "HELD";
  next.windowOpensAt = nowMs;
  next.windowExpiresAt = nowMs + PB_STATION_WINDOW_MS;
  station.current = next;
  return next;
}

/* The dispatch handshake (Plan 01 SS5.7): map the delivery
 * record's truth onto the station face. `preSubmitStages` are
 * the adapter stages that prove nothing was submitted; a
 * failure there is FAILED-BEFORE-SEND. A confirmation that
 * arrives for an item already recorded SENT-UNCONFIRMED is
 * DELIVERED-LATE. */
const PB_STATION_PRE_SUBMIT_STAGES = ["gating", "adapter", "composer", "engage", "type", "verify-type", "lease", "fence", "generating", "unreachable", "context-full", "send-button"];
function pbStationHandshake(input) {
  const { crusherState, deliveryStatus, stage, wasUnconfirmed, submitted } = input || {};
  if (crusherState === "ACKNOWLEDGED") return wasUnconfirmed ? "DELIVERED-LATE" : "DELIVERED";
  if (crusherState === "UNVERIFIED") return "SENT-UNCONFIRMED";
  if (crusherState === "DELIVERING") return submitted ? "TRANSIT" : "ATTEMPTING";
  if (crusherState === "FAILED" || crusherState === "STOPPED" || deliveryStatus === "failed") {
    return PB_STATION_PRE_SUBMIT_STAGES.includes(stage || "") ? "FAILED-BEFORE-SEND" : "SENT-UNCONFIRMED";
  }
  return null;
}

const PB_STATION = {
  PB_STATION_WINDOW_MS, pbStationDefault, pbStationHasFilePayload,
  pbStationEnter, pbStationTick, pbStationPushThrough, pbStationCancel,
  pbStationTake, pbStationPromote, pbStationHandshake, PB_STATION_PRE_SUBMIT_STAGES,
  pbStationAppendOpen, pbStationAppendClose,
};
if (typeof window !== "undefined") window.PB_STATION = PB_STATION;
if (typeof module !== "undefined" && module.exports) module.exports = PB_STATION;
