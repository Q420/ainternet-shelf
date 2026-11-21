"use strict";
/* Pulse Bridge — RETAINED HANDLES (Conclusion Build, v0.22.0).
 *
 * The spine of the build (the joint plan, ruled in 2026-11-11):
 * a conclusion must not outlive its evidence. Hand-off, verdict
 * and forget each wrote a conclusion with no durable handle to
 * the evidence that would let it be revised. When a pair closes,
 * the forget loop deletes the detection, its fingerprint index
 * entry and its seen-id — and with them every way to (a) fold a
 * later exact re-sighting as the duplicate it is, (b) recognise
 * a completion that grew after the pair closed, or (c) revise
 * an UNVERIFIED verdict when the receipt is observed late.
 *
 * A handle is what pair close now leaves behind: a small,
 * persisted, bounded shadow of the completed letter — its id,
 * its seats, its full body, its fingerprint, and how it closed.
 * Parts 2, 3 and 4 of the build all consume this one store:
 *   Part 2 — intake consults it: an exact re-sighting of a
 *            completed letter answers duplicate (terminal) from
 *            the handle, background-side, after the forget loop
 *            has run.
 *   Part 3 — a supersede whose lineage names a handle is a
 *            letter that GREW AFTER COMPLETION: it is held as a
 *            growth notice for Ben's decision, never routed as
 *            a new letter and never carried automatically.
 *   Part 4 — a handle that closed UNVERIFIED carries a bounded
 *            re-look schedule; a late observation upgrades the
 *            verdict to DELIVERED-LATE. The pass can only revise
 *            the verdict — it has no path to a send.
 *
 * Pure logic over plain state, in the fence.js / station.js
 * mould: the background owns the store, the alarms and the log;
 * this file owns the shapes and the schedule. No DOM, no chrome.
 *
 * Capacity disposition (convene spec §1.3 — every bounded store
 * states one): PB_HANDLE_CAP handles, newest kept. Eviction of
 * the oldest is returned to the caller so it can be LOGGED,
 * never silent. Named consequence, accepted in the scope: a
 * re-sighting, a growth or a late look arriving after its
 * handle was evicted behaves as the pre-v0.22.0 build did —
 * bounded memory with its failure mode on the label. ABANDONED
 * letters never take handles: their records already stand. */

const PB_HANDLE_CAP = 300;
const PB_RELOOK_FIRST_MS = 60000;   // first late look: close + 60 s
const PB_RELOOK_STEP_MS = 60000;    // then every 60 s
const PB_RELOOK_END_MS = 600000;    // last look: close + 10 min

function pbHandlesEnsure(state) {
  if (!state || typeof state !== "object") return [];
  if (!Array.isArray(state.handles)) state.handles = [];
  return state.handles;
}

/* Build the handle a closing detection leaves behind, or null
 * when the letter did not complete: only ACKNOWLEDGED and
 * UNVERIFIED closes are completions (the pair judge's own rule:
 * those two, and only those two, complete a carry). FAILED,
 * STALLED, ABANDONED and never-carried letters take no handle —
 * their existing behaviour stands untouched. */
function pbHandleFromDetection(det, closedAtIso) {
  if (!det || !det.envelope || !det.crusher) return null;
  const cs = det.crusher.state;
  if (cs !== "ACKNOWLEDGED" && cs !== "UNVERIFIED") return null;
  const parsedClose = Date.parse(closedAtIso);
  const closedMs = Number.isFinite(parsedClose) ? parsedClose : Date.now();
  return {
    message_id: det.envelope.message_id,
    from: det.envelope.from || null,
    to: det.envelope.to || null,
    body: det.envelope.body || "",
    fingerprint: det.envelope.fingerprint || null,
    closedAt: closedAtIso,
    closeState: cs,
    relook: cs === "UNVERIFIED"
      ? { looks: 0, nextAt: closedMs + PB_RELOOK_FIRST_MS, done: false, upgradedAt: null }
      : null,
  };
}

/* Record a handle, trimming the store to its cap from the
 * oldest end. Returns the evicted message_ids (oldest first)
 * so the caller can log every eviction. */
function pbHandlesRecord(state, handle) {
  const handles = pbHandlesEnsure(state);
  if (!handle) return [];
  handles.push(handle);
  const evicted = [];
  while (handles.length > PB_HANDLE_CAP) evicted.push(handles.shift().message_id);
  return evicted;
}

function pbHandleById(state, messageId) {
  if (!messageId) return null;
  return pbHandlesEnsure(state).find((h) => h.message_id === messageId) || null;
}

function pbHandleByFingerprint(state, fingerprint) {
  if (!fingerprint) return null;
  return pbHandlesEnsure(state).find((h) => h.fingerprint === fingerprint) || null;
}

/* Part 2's intake consult: does this envelope re-sight a
 * COMPLETED letter — the same envelope id, or the same body
 * fingerprint under a freshly minted id (the letterbox's
 * re-render shape)? Returns the handle, or null. */
function pbHandleConsult(state, envelope) {
  if (!envelope) return null;
  return pbHandleById(state, envelope.message_id) ||
         pbHandleByFingerprint(state, envelope.fingerprint);
}

/* Part 3's lookup: a supersede names its lineage by the
 * ORIGINAL body's fingerprint — which, for a completed letter,
 * is exactly the handle's fingerprint. */
function pbHandleBySupersedes(state, supersedesFingerprint) {
  return pbHandleByFingerprint(state, supersedesFingerprint);
}

/* The growth notice's added text: the new body minus the
 * handled body. Exact raw-prefix growth gives the literal
 * suffix; whitespace-only divergence still resolves through a
 * normalised comparison; anything else is DIVERGENT — the whole
 * new body is the notice text and the flag says so, rather than
 * a fabricated diff. Display-only: no routing decision ever
 * reads this. */
function pbHandleNorm(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}
function pbAddedText(oldBody, newBody) {
  const oldB = String(oldBody || "");
  const newB = String(newBody || "");
  if (newB.length > oldB.length && newB.startsWith(oldB)) {
    return { added: newB.slice(oldB.length).replace(/^\s+/, ""), divergent: false };
  }
  const oN = pbHandleNorm(oldB), nN = pbHandleNorm(newB);
  if (nN.length > oN.length && nN.startsWith(oN)) {
    return { added: nN.slice(oN.length).replace(/^\s+/, ""), divergent: false };
  }
  return { added: newB, divergent: true };
}

/* Part 4's schedule judge. A handle's relook carries the state;
 * this reads it against the clock:
 *   done  — upgraded already, closed ACKNOWLEDGED (no relook),
 *           the look count is exhausted, or the next look would
 *           fall past the bound.
 *   wait  — the next look is not yet due (nextAt says when).
 *   look  — a look is due now.
 * After a look that does not upgrade, pbRelookAfterLook
 * advances the state (looks + 1, nextAt + STEP, done when the
 * bound is passed). */
function pbRelookPlan(handle, nowMs) {
  if (!handle || !handle.relook || handle.relook.done) return { action: "done" };
  const closedMs = Date.parse(handle.closedAt) || 0;
  if (handle.relook.nextAt > closedMs + PB_RELOOK_END_MS) return { action: "done" };
  if (nowMs < handle.relook.nextAt) return { action: "wait", nextAt: handle.relook.nextAt };
  return { action: "look", nextAt: handle.relook.nextAt };
}
function pbRelookAfterLook(handle, nowMs) {
  if (!handle || !handle.relook) return;
  handle.relook.looks++;
  handle.relook.nextAt += PB_RELOOK_STEP_MS;
  const closedMs = Date.parse(handle.closedAt) || 0;
  if (handle.relook.nextAt > closedMs + PB_RELOOK_END_MS) handle.relook.done = true;
}

const PB_HANDLES = {
  PB_HANDLE_CAP, PB_RELOOK_FIRST_MS, PB_RELOOK_STEP_MS, PB_RELOOK_END_MS,
  pbHandlesEnsure, pbHandleFromDetection, pbHandlesRecord,
  pbHandleById, pbHandleByFingerprint, pbHandleConsult, pbHandleBySupersedes,
  pbAddedText, pbRelookPlan, pbRelookAfterLook,
};
if (typeof module !== "undefined" && module.exports) module.exports = PB_HANDLES;
