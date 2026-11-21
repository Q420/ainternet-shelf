"use strict";
/* Pulse Bridge — background router (v0.6.0, CRUSHER).
 *
 * STAGE 3 (v0.5.0, Ben's tap 2026-11-06 22:22): registration +
 * detection + DELIVERY. A held detection is carried to the OTHER
 * seat's registered tab, whose content script types it into the
 * conversation and sends it — under Ben's rule: delivery runs while
 * the bridge is unpaused and both tabs are registered ("my hand on
 * it means I have not turned it off"); his presence is the monitor.
 *
 * CRUSHER v1 (Ben's tap on the revised scope, 2026-11-06 23:41):
 * every letter's transport is run as an explicit state machine
 * (crusher.js). Delivery outcomes are recorded as Crusher states —
 * ACKNOWLEDGED (receipt evidence), UNVERIFIED (sent, unconfirmed;
 * the machine says "I don't know"), FAILED (pre-send, finally,
 * true stage named), STALLED (destination unreachable), HELD
 * (paused at attempt time). Retry is machine-bounded: pre-send
 * stage failures only, PB_CRUSHER_MAX_ATTEMPTS total, never after
 * the send click. The popup renders the state + trail per letter.
 *
 * CRUSHER V6.1 (Alex's consultation ruling, Ben's tap 2026-11-07
 * 02:44): identity re-keyed on the envelope message_id (dedup,
 * ledgers, marks); proven-absence retry (verdict "absent" only,
 * max 2, 30s apart, same id; exhaustion = terminal STALLED);
 * destination-generation stalls; attempt accounting on every path
 * (busy deferrals and machinery errors are noted, never silent);
 * the delivery queue drains itself when an attempt finishes.
 *
 * CRUSHER V6.2 (Ben's tap, 2026-11-07 02:24, on the V6.1 LIVE
 * test's evidence): a QUEUE PUMP serves letters oldest-actionable-
 * first across both directions; proven-absence retries now wait
 * in RETRY_WAIT with a due time instead of sleeping 30s inside
 * the delivery slot; generating/unreachable stalls re-queue
 * themselves (bounded) instead of parking until an external
 * sweep; an alarm/timer wakes the pump when a wait comes due.
 * The proven-absence policy itself is unchanged (Alex ruling 2).
 *
 * V7 — THE PAIR MACHINE (Alex's direction 2026-11-07 03:12, his
 * answers 03:14, Ben's tap 03:15): the router stops being a
 * queue and becomes a process tree. ONE active pair: carry a
 * call, watch for its reply, carry the reply, retire, repeat.
 * The pump now serves ONLY the pair's current letter; every
 * other detection waits in a ONE-message buffer (newest wins,
 * evictions logged, never silent) or becomes the pair's reply /
 * a resume-by-speaking follow-up. The pair record persists, so
 * a worker or extension restart resumes the exchange instead of
 * asking Ben to reconstruct it. Carries keep the full V6.1/V6.2
 * discipline (confirmation, proven-absence, self-requeue) —
 * those are step-internal details now, not a state archive.
 */
importScripts("protocol.js", "crusher.js", "fence.js", "storage.js", "alert.js");

/* V8 (0.8.0): the platform is a fact about the TAB, not the seat —
 * read it off the tab's own URL (a claude.ai tab registered as the
 * alex seat is platform "claudeai", never "chatgpt"). The seat↔
 * platform pairings of v0.7 and earlier survive only as the
 * fallback for a URL that names no known host. */
function pbPlatformForUrl(url, role) {
  const u = String(url || "");
  if (u.includes("muse.ai")) return "muse";
  if (u.includes("chatgpt.com")) return "chatgpt";
  if (u.includes("claude.ai")) return "claudeai";
  if (u.includes("gemini.google.com")) return "gemini";
  if (u.includes("meta.ai")) return "metaai";
  return role === "remmy" ? "muse" : "chatgpt";
}

async function handleRegister(role, tab) {
  const state = await pbLoadState();
  state.registrations[role] = {
    tabId: tab.id,
    windowId: tab.windowId,
    url: tab.url || "",
    title: tab.title || "",
    platform: pbPlatformForUrl(tab.url, role),
    registeredAt: new Date().toISOString(),
  };
  pbLog(state, `Registered ${role.toUpperCase()} tab (${tab.title || tab.url || tab.id})`);
  await pbSaveState(state);
  return state;
}

/* ===== V7 — THE PAIR MACHINE =====
 * Helpers over a loaded state object (they mutate + log; the
 * caller saves). The machine remembers the current transaction,
 * not the conversation. */

function pairDetection(state, id) {
  if (!id) return null;
  return state.detections.find((d) => d.envelope && d.envelope.message_id === id) || null;
}

/* Remove a detection and its dedup entries. Retired letters are
 * forgotten ON PURPOSE — the letterbox's history absorption is
 * what keeps them from re-firing off the page. */
function forgetDetection(state, id) {
  const det = pairDetection(state, id);
  if (!det) return null;
  state.detections = state.detections.filter((d) => d !== det);
  if (det.envelope) {
    if (state.fpToId) delete state.fpToId[det.envelope.fingerprint];
    if (state.seenIds) state.seenIds = state.seenIds.filter((x) => x !== id);
  }
  return det;
}

function startPair(state, callId) {
  const det = pairDetection(state, callId);
  if (!det) return;
  const e = det.envelope;
  state.pair = {
    step: "carry-call", from: e.from, to: e.to,
    callId, replyId: null, pendingReplyId: null, callOutcome: null,
    failedReason: null, failedWhich: null,
    /* V0.12.1: auto-retry bookkeeping for a parked pair — how
     * many fresh attempts changed conditions have earned, when
     * it parked, and which tab the destination seat held then. */
    autoRetries: 0, parkedAt: null, parkedDestTab: null,
    startedAt: new Date().toISOString(),
  };
  pbLog(state, `PAIR OPEN ${e.from} → ${e.to}: carrying "${e.body.slice(0, 60)}${e.body.length > 60 ? "…" : ""}"`);
}

/* Retire the active pair: forget its letters, put the outcome
 * on the log, and (unless told otherwise) promote the buffered
 * message into the next pair. */
function retirePair(state, outcomeText, promote = true, hist = null) {
  const pair = state.pair;
  if (!pair) return;
  /* V0.15.0: the face's Earlier list is fed from here — a
   * plain record of how exchanges resolved, kept after the
   * letters themselves are forgotten. Display only. */
  if (hist && hist.seat && hist.kind) {
    if (!Array.isArray(state.faceHistory)) state.faceHistory = [];
    state.faceHistory.push({ at: new Date().toISOString(), seat: hist.seat, kind: hist.kind });
    if (state.faceHistory.length > 20) state.faceHistory = state.faceHistory.slice(-20);
  }
  pbLog(state, `PAIR CLOSED ${pair.from} → ${pair.to}: ${outcomeText}`);
  /* V0.17.0 (Ben's ledger lifecycle): the closing pair's
   * serials retire into the completed record — out of the
   * active count, never forgotten entirely; duplicate
   * detection reads the completed record after the letters
   * themselves are forgotten below. */
  if (typeof PB_FENCE !== "undefined") {
    const retired = [];
    for (const lid of [pair.callId, pair.replyId, pair.pendingReplyId]) {
      if (!lid) continue;
      const ld = pairDetection(state, lid);
      if (ld && ld.serial != null) retired.push({ serial: ld.serial, id: lid });
    }
    if (retired.length) PB_FENCE.pbFenceRetireSerials(state, retired);
  }
  for (const lid of [pair.callId, pair.replyId]) {
    if (!lid) continue;
    const ld = pairDetection(state, lid);
    /* V0.15.0: an ABANDONED letter's record STANDS — Ben's
     * decision, its interventions and its trail stay
     * inspectable, and its fingerprint stays deduped so the
     * page can never re-fire it as a new letter. Delivered
     * letters are forgotten as before: the delivered ledger
     * and the letterbox's history carry them. */
    if (ld && ld.crusher && ld.crusher.state === "ABANDONED") continue;
    forgetDetection(state, lid);
  }
  if (pair.pendingReplyId && pairDetection(state, pair.pendingReplyId)) {
    /* V7.3: a reply was still waiting in the pending slot as
     * this pair closed (its call failed finally, or Ben retired
     * the pair mid-wait). It is a real letter: if the buffer is
     * free it takes the slot and starts the next pair below; if
     * the buffer is occupied by a newer follow-up, the waiting
     * reply is retired VISIBLY — never silently orphaned. */
    if (!state.bufferId) {
      state.bufferId = pair.pendingReplyId;
      pbLog(state, "PAIR: the reply that waited in the pending slot takes the buffer — it will start the next pair");
    } else {
      pbLog(state, "PAIR: a reply was waiting in the pending slot as the pair closed, and the buffer is occupied by a newer message — the waiting reply is retired visibly, not carried");
      forgetDetection(state, pair.pendingReplyId);
    }
  }
  state.pair = null;
  if (promote && state.bufferId) {
    const bufId = state.bufferId;
    state.bufferId = null;
    if (pairDetection(state, bufId)) {
      pbLog(state, `PAIR: the buffered message starts the next pair`);
      startPair(state, bufId);
    } else {
      /* V0.12.1: the buffer named a letter whose detection is no
       * longer in the record (pre-v0.12.1 FIFO eviction could take
       * it). That loss is recorded on the log — never silent. */
      pbLog(state, `PAIR: the buffered message (${bufId}) is missing from the record — it cannot start the next pair. The letter is lost from the bridge's record; this line is its trace.`);
    }
  }
}

/* The pair's progression judge. Idempotent; called when carries
 * finish, detections route, and the worker wakes. It moves the
 * pair ONLY on confirmed carry outcomes: ACKNOWLEDGED (or
 * UNVERIFIED — sent, question mark kept) completes a carry;
 * FAILED or a terminal stall parks the pair in
 * failed-recoverable with nothing erased. */
async function advancePair() {
  const state = await pbLoadState();
  const pair = state.pair;
  if (!pair) return;
  let changed = false;
  if (pair.step === "failed-recoverable") {
    /* V0.15.0 — RETIREMENT IS ABOLISHED (Ben's ruling; spec
     * 4.7). The v0.12.1 auto-retry judge is gone: it reset the
     * letter's record and answered to a conditions-changed
     * heuristic. Now the LETTER's own recovery ladder is the
     * only policy. When its schedule comes due, the judge
     * simply returns the pair to carrying — the record, its
     * failure history and its PB-ID untouched. A STOPPED
     * letter rests here as needs-you until Ben's hand (Try
     * again / Let it go) moves it; an ABANDONED letter
     * resolves the exchange as abandoned. Nothing else can
     * leave a pair parked: every other state carries a live
     * driver (a due time, a gate watch, or a named pause). */
    const failedId = pair.failedWhich === "reply" ? pair.replyId : pair.callId;
    const det = pairDetection(state, failedId);
    if (det && det.crusher) {
      const cs = det.crusher.state;
      if (cs === "ABANDONED") {
        retirePair(state, "let go by Ben — exchange closed as abandoned", true,
          { seat: det.envelope.to, kind: "abandoned" });
        changed = true;
      } else if (cs === "STOPPED") {
        /* needs you — rests until Ben acts (spec 4.2). */
      } else if ((cs === "RETRY_WAIT" || cs === "STALLED" || cs === "FAILED") && !det.crusher.pausedAt && !det.crusher.terminalStall) {
        const due = Date.parse(det.crusher.nextAttemptAt || "") || 0;
        if (cs === "FAILED" || due <= Date.now()) {
          if (cs === "FAILED") {
            /* A legacy FAILED record enters the ladder at a
             * due-now step; the pump takes it from there. */
            det.crusher.nextAttemptAt = new Date().toISOString();
            pbCrusherTransition(det.crusher, "RETRY_WAIT",
              "legacy FAILED record enters the recovery ladder", new Date().toISOString());
          }
          const whichF = pair.failedWhich;
          pair.step = whichF === "reply" ? "carry-reply" : "carry-call";
          pair.failedReason = null; pair.failedWhich = null;
          pair.parkedAt = null; pair.parkedDestTab = null;
          if (state.deliveryFailedIds) state.deliveryFailedIds = state.deliveryFailedIds.filter((x) => x !== failedId);
          if (state.deliveryFailed && det.envelope) state.deliveryFailed = state.deliveryFailed.filter((x) => x !== det.envelope.fingerprint);
          pbLog(state, `PAIR RECOVERY ${pair.from} → ${pair.to}: the ${whichF || "letter"}'s own schedule came due — carrying it again (failure ${det.crusher.recovery ? det.crusher.recovery.failures : "?"} on its record)`);
          changed = true;
        }
      }
    }
  }
  if (pair.step === "carry-call" || pair.step === "carry-reply") {
    const which = pair.step === "carry-call" ? "call" : "reply";
    const det = pairDetection(state, which === "call" ? pair.callId : pair.replyId);
    if (det && det.crusher) {
      const cs = det.crusher.state;
      if (cs === "ACKNOWLEDGED" || cs === "UNVERIFIED") {
        if (which === "call") {
          pair.step = "await-reply";
          pair.callOutcome = cs;
          pbLog(state, cs === "ACKNOWLEDGED"
            ? `PAIR: call confirmed delivered — now watching for ${pair.to}'s reply`
            : `PAIR: call sent but UNCONFIRMED — watching for a reply; the question mark stays on the record`);
          changed = true;
        } else {
          retirePair(state, cs === "ACKNOWLEDGED"
            ? "reply confirmed delivered — exchange complete"
            : "reply sent but unconfirmed — exchange closed with the question mark on the record",
            true, cs === "ACKNOWLEDGED" ? { seat: pair.from, kind: "delivered" } : null);
          changed = true;
        }
      } else if (cs === "ABANDONED") {
        retirePair(state, "let go by Ben — exchange closed as abandoned", true,
          { seat: det.envelope.to, kind: "abandoned" });
        changed = true;
      } else if (cs === "FAILED" || cs === "STOPPED" || (cs === "STALLED" && det.crusher.terminalStall)) {
        const trail = det.crusher.trail || [];
        pair.step = "failed-recoverable";
        pair.failedWhich = which;
        pair.failedReason = (trail.length && trail[trail.length - 1].note) || cs;
        /* V0.12.1: stamp the park so the auto-retry judge below
         * can tell whether conditions have CHANGED since (fresh
         * traffic, or the destination seat's tab moved). */
        pair.parkedAt = new Date().toISOString();
        const destSeat = which === "call" ? pair.to : pair.from;
        const destReg = state.registrations && state.registrations[destSeat];
        pair.parkedDestTab = destReg ? destReg.tabId : null;
        pbLog(state, `PAIR FAILED — RECOVERABLE: the ${which} could not be carried (${pair.failedReason}). Nothing was erased; Retry or Retire from the popup.`);
        changed = true;
      }
    }
  }
  if (state.pair && pair.step === "await-reply") {
    /* V7.3 STANDING RECONCILE: the awaited reply may already be
     * in the building — in the pair's pending slot (it arrived
     * while the call carried) or in the buffer (it arrived
     * before this pair began waiting, or before a restart).
     * Consume it AS the reply. This runs on every judge pass —
     * carry finishes, detections, worker wakes — so a pair
     * never sits watching for what it already holds. */
    let candidateId = null;
    let source = null;
    if (pair.pendingReplyId && pairDetection(state, pair.pendingReplyId)) {
      candidateId = pair.pendingReplyId;
      source = "the pending slot";
    } else if (state.bufferId) {
      const buf = pairDetection(state, state.bufferId);
      if (buf && buf.envelope.from === pair.to && buf.envelope.to === pair.from) {
        candidateId = state.bufferId;
        source = "the buffer";
      }
    }
    if (candidateId) {
      if (candidateId === pair.pendingReplyId) pair.pendingReplyId = null;
      if (candidateId === state.bufferId) state.bufferId = null;
      pair.replyId = candidateId;
      pair.step = "carry-reply";
      pbLog(state, `PAIR: the reply was already here (${source}) — carrying it back to ${pair.from}`);
      changed = true;
    }
  }
  if (changed) {
    await pbSaveState(state);
    if (state.pair && (state.pair.step === "carry-call" || state.pair.step === "carry-reply")) {
      pumpQueue().catch(() => {});
    }
  }
}

/* V0.11.0 P1 — FILE HANDOFF VERIFICATION (Ben's item, Alex's
 * ruling, 2026-11-08). Runs beside the pair machine when a letter
 * is accepted: if the body carries a PB-FILE block, the content AS
 * TRANSPORTED is hashed (SHA-256 over its UTF-8 bytes — raw bytes
 * are authoritative) and compared against the sender's declared
 * hash. The outcome is recorded on the envelope and in the
 * fileTransfers ledger, and logged. A failed handoff never blocks
 * or fails the letter itself — it is a labelled outcome ON the
 * letter. An LF-normalised match is recorded as a diagnostic
 * (lfMatch) and NEVER upgrades a mismatch. */
async function pbVerifyFileTransfer(envelope) {
  let parsed = null;
  try { parsed = PB.pbParseFileBlock(envelope.body); } catch (e) { parsed = null; }
  if (!parsed) return; // no file in this letter — nothing to record
  const at = new Date().toISOString();
  const rec = {
    at, messageId: envelope.message_id, from: envelope.from, to: envelope.to,
    name: parsed.ok ? parsed.name : null,
    declaredSha256: parsed.ok ? parsed.declaredSha256 : null,
    declaredBytes: parsed.ok ? parsed.declaredBytes : null,
    actualSha256: null, actualBytes: null,
    status: null, lfMatch: false, outcome: null,
    reason: parsed.ok ? null : parsed.reason,
  };
  if (parsed.ok) {
    rec.actualBytes = PB.pbUtf8Bytes(parsed.content).length;
    let actualSha256 = null;
    let lfSha256 = null;
    try {
      actualSha256 = await PB.pbSha256Hex(parsed.content);
      const lf = parsed.content.replace(/\r\n/g, "\n");
      if (lf !== parsed.content) lfSha256 = await PB.pbSha256Hex(lf);
    } catch (e) { /* hashing unavailable — handled honestly below */ }
    rec.actualSha256 = actualSha256;
    if (parsed.declaredSha256 && !actualSha256) {
      rec.status = "unverifiable";
    } else {
      const v = PB.pbFileVerdict(parsed, actualSha256, lfSha256);
      rec.status = v.status;
      rec.lfMatch = !!v.lfMatch;
    }
  } else {
    rec.status = "malformed";
  }
  const state = await pbLoadState();
  const det = state.detections.find((d) => d.envelope && d.envelope.message_id === envelope.message_id);
  if (det) det.envelope.fileTransfer = rec;
  /* Race closure: verification is fire-and-forget beside a fast
   * delivery — if the letter was ALREADY acknowledged before this
   * record landed, the outcome completes here instead of in the
   * delivery path (which looked before the record existed). */
  if ((state.deliveredIds || []).includes(envelope.message_id)) {
    rec.outcome = rec.status === "verified" ? "FILE_CONTENT_DELIVERED_VERIFIED" : "FILE_HANDOFF_FAILED";
  }
  if (!state.fileTransfers) state.fileTransfers = [];
  state.fileTransfers.push(rec);
  if (state.fileTransfers.length > 50) state.fileTransfers = state.fileTransfers.slice(-50);
  if (rec.status === "verified") {
    pbLog(state, `FILE "${rec.name}" (${rec.from} → ${rec.to}): content matches the sender's raw-byte SHA-256 (${rec.actualBytes} bytes) — verified at the router; the delivery outcome completes when the letter is acknowledged`);
  } else if (rec.status === "mismatch") {
    pbLog(state, `FILE "${rec.name}" (${rec.from} → ${rec.to}): HASH MISMATCH — the handoff FAILED at transport (LF-normalised diagnostic match: ${rec.lfMatch ? "yes" : "no"}). The letter still carries; the file must not be treated as delivered`);
  } else if (rec.status === "malformed") {
    pbLog(state, `FILE (${rec.from} → ${rec.to}): PB-FILE block rejected — ${rec.reason}. The letter still carries; no file was handed off`);
  } else if (rec.status === "undeclared") {
    pbLog(state, `FILE "${rec.name}" (${rec.from} → ${rec.to}): block extracted but UNDECLARED (no sha256 in the header) — content cannot be verified; it is unverified text, not a verified file`);
  } else {
    pbLog(state, `FILE "${rec.name}" (${rec.from} → ${rec.to}): hashing unavailable in the worker — the handoff cannot be verified (that is not a pass)`);
  }
  await pbSaveState(state);
}

async function handleDetection(envelope, senderTabId) {
  const state = await pbLoadState();
  // Which seat did this detection come from? The sender tab must be the
  // registered tab for envelope.from — an unregistered tab cannot speak
  // for a seat.
  const reg = state.registrations[envelope.from];
      if (!reg || reg.tabId !== senderTabId) {
    pbLog(state, `Ignored detection claiming seat ${envelope.from} from an unregistered tab`);
    await pbSaveState(state);
    return { accepted: false, reason: "unregistered-tab" };
  }
  /* CRUSHER V6.1 (Alex ruling 1): dedup keys on the envelope
   * message_id — the authoritative identity. The fingerprint index
   * (fpToId) bridges the letterbox's sightings to that identity:
   * the same letter sighted again (a re-render, a content-script
   * reload) arrives under a freshly minted envelope but the SAME
   * fingerprint, and is recognised as the same letter — while a
   * genuinely new letter always carries a new id. */
  if (!state.seenIds) state.seenIds = [];
  if (!state.fpToId) state.fpToId = {};
  if (state.seenIds.includes(envelope.message_id) || state.fpToId[envelope.fingerprint]) {
    return { accepted: false, reason: "duplicate" };
  }
  state.seenIds.push(envelope.message_id);
  if (state.seenIds.length > PB_MAX_SEEN) state.seenIds = state.seenIds.slice(-PB_MAX_SEEN);
  state.fpToId[envelope.fingerprint] = envelope.message_id;
  pbMarkSeen(state, envelope.fingerprint);
  pbRecordDetection(state, {
    envelope,
    detectedIn: envelope.from,
    tabId: senderTabId,
    at: new Date().toISOString(),
  });
  /* V0.13.0 CRUSHER LANE (Ben's design, his veto of the veto, and
   * the ferry correction, 2026-11-09): traffic addressed to
   * Crusher NEVER enters the pair machine or the buffer — the
   * additivity invariant, now mechanical. A question from the
   * other seat is carried to REMMY's seat as a separate, visibly
   * flagged delivery (the retrieval harness lives there; Remmy's
   * turn is the invocation, in the open — no pretending the ferry
   * was a telephone). A question authored on Remmy's own seat is
   * already in her chat: nothing is carried, and the log line
   * below is its invocation record. Crusher's answers travel back
   * as ordinary pair letters; they need no lane. */
  if (envelope.to === "crusher") {
    if (envelope.from === "remmy") {
      pbLog(state, `CRUSHER Q (local, from the remmy seat): "${envelope.body.slice(0, 60)}${envelope.body.length > 60 ? "…" : ""}" — addressed in Remmy's own chat; nothing carried`);
      await pbSaveState(state);
      return { accepted: true };
    }
    const fromName = envelope.from === "alex" ? "Alex" : envelope.from;
    const delivery = PB.pbEnvelope({
      from: envelope.from,
      to: "remmy",
      body: "FOR CRUSHER — a question addressed to Crusher by " + fromName +
            ", delivered to Remmy's seat for invocation. The question:\n\n" + envelope.body,
    });
    delivery.crusherFor = envelope.message_id;
    pbRecordDetection(state, {
      envelope: delivery,
      detectedIn: envelope.from,
      tabId: senderTabId,
      at: new Date().toISOString(),
    });
    pbLog(state, `CRUSHER Q ${envelope.from} → crusher: "${envelope.body.slice(0, 60)}${envelope.body.length > 60 ? "…" : ""}" — carrying the question to Remmy's seat, flagged; the pair machine is not involved`);
    await pbSaveState(state);
    pumpCrusher(false).catch(() => {});
    return { accepted: true };
  }
  pbLog(state,
    `VERIFIED ${envelope.from} → ${envelope.to}: "${envelope.body.slice(0, 60)}${envelope.body.length > 60 ? "…" : ""}" (the pair machine has it)`);
  /* V0.11.0 P1: file-handoff verification rides beside the pair
   * machine (fire-and-forget; it records and logs its own outcome
   * and can never block, delay or fail the letter). */
  pbVerifyFileTransfer(envelope).catch(() => {});

  /* V6.3 SUPERSEDE + V7 RECOVERY: the lineage resolves through
   * the fingerprint index. If it names an ACTIVE record — the
   * pair's call or reply, or the buffered message — the grown
   * letter is a RECOVERY: it takes the slot and is carried (the
   * partial is marked SUPERSEDED on its way out; Alex's ruling:
   * supersession is a recovery mechanism, not normal operation).
   * If it names nothing active, the pair already retired and the
   * grown letter is simply a new message — it routes below. */
  if (envelope.supersedesFingerprint) {
    const origId = state.fpToId[envelope.supersedesFingerprint];
    const orig = origId && pairDetection(state, origId);
    if (orig) {
      orig.supersededBy = envelope.message_id;
      envelope.supersedesId = origId;
      pbLog(state, `⤳ …${String(envelope.message_id).slice(-6)} completes …${String(origId).slice(-6)} — the earlier partial capture is SUPERSEDED by the full letter`);
      const pair = state.pair;
      if (pair && pair.callId === origId) {
        forgetDetection(state, origId);
        pair.callId = envelope.message_id;
        pair.step = "carry-call";
        pair.callOutcome = null;
        pair.failedReason = null; pair.failedWhich = null;
        pbLog(state, `PAIR RECOVERY: the call grew after capture — carrying the completed version`);
      } else if (pair && pair.replyId === origId) {
        forgetDetection(state, origId);
        pair.replyId = envelope.message_id;
        pair.step = "carry-reply";
        pair.failedReason = null; pair.failedWhich = null;
        pbLog(state, `PAIR RECOVERY: the reply grew after capture — carrying the completed version`);
      } else if (pair && pair.pendingReplyId === origId) {
        forgetDetection(state, origId);
        pair.pendingReplyId = envelope.message_id;
        pbLog(state, `PAIR: the waiting reply was completed by its grown version`);
      } else if (state.bufferId === origId) {
        forgetDetection(state, origId);
        state.bufferId = envelope.message_id;
        pbLog(state, `PAIR: the buffered message was completed by its grown version`);
      } else {
        // Active record but no slot claims it (should not
        // happen): fall through to normal routing below.
        await pbSaveState(state);
        pumpQueue().catch(() => {});
        return { accepted: true };
      }
      await pbSaveState(state);
      pumpQueue().catch(() => {});
      return { accepted: true };
    }
  }

  /* V7 ROUTING — one active pair, one buffer slot. */
  const pair = state.pair;
  if (!pair) {
    startPair(state, envelope.message_id);
  } else if (pair.step === "await-reply" && envelope.from === pair.to && envelope.to === pair.from) {
    pair.replyId = envelope.message_id;
    pair.step = "carry-reply";
    pbLog(state, `PAIR: the reply arrived — carrying it back to ${pair.from}`);
  } else if (pair.step === "await-reply" && envelope.from === pair.from && envelope.to === pair.to) {
    /* RESUME-BY-SPEAKING: the waiting seat sent a follow-up
     * instead of an answer arriving. The old pair closes on the
     * record (its call WAS confirmed; no reply came), and the
     * follow-up opens a fresh pair. The buffer is NOT promoted
     * here — the follow-up is newer and takes the pair. */
    retirePair(state, `closed by a follow-up from ${pair.from} — no reply arrived; the conversation resumed by speaking`, false);
    startPair(state, envelope.message_id);
  } else if (pair.step === "carry-call" && envelope.from === pair.to && envelope.to === pair.from && !pair.pendingReplyId) {
    /* V7.3 PENDING REPLY: the awaited seat answered while the
     * call is still being carried. The reply's identity belongs
     * to the PAIR, not to the clock: it waits in a slot on the
     * pair record — never in the evictable buffer — and the
     * pair judge consumes it the moment the call resolves. A
     * second reply-direction letter while one already waits is
     * a follow-up and buffers normally (the branch below). */
    pair.pendingReplyId = envelope.message_id;
    pbLog(state, `PAIR: ${envelope.from}'s reply arrived while the call is still carrying — held in the pair's pending slot`);
  } else {
    /* THE BUFFER: one slot, newest wins. An evicted letter is
     * retired VISIBLY in the log — never silently dropped. */
    if (state.bufferId) {
      const evicted = pairDetection(state, state.bufferId);
      if (evicted) {
        pbLog(state, `BUFFER: "${evicted.envelope.body.slice(0, 60)}${evicted.envelope.body.length > 60 ? "…" : ""}" superseded while pending by a newer message — retired visibly, never carried`);
        forgetDetection(state, state.bufferId);
      }
    }
    state.bufferId = envelope.message_id;
    pbLog(state, `BUFFERED ${envelope.from} → ${envelope.to}: waits for the active pair to retire`);
  }
  await pbSaveState(state);
  // A detection does not attempt delivery itself — it wakes the
  // pump, which serves the pair's current letter and nothing
  // else. Attempt machinery errors are accounted on the letter's
  // trail inside the pump — never swallowed.
  pumpQueue().catch(() => {});
  return { accepted: true };
}

/* CRUSHER — carry one letter to its destination tab, state by
 * state. Bounded retry on pre-send stage failures only; after the
 * send click the outcome is ACKNOWLEDGED or UNVERIFIED, never a
 * retry. STALLED (destination unreachable) is retryable by a later
 * sweep once the destination exists again.
 *
 * CRUSHER V6.1: the letter is keyed on its envelope message_id
 * everywhere. New outcome paths: a receipt verdict of "absent"
 * (confirmation positively established the letter is not there)
 * earns the bounded proven-absence retry under the SAME id, and
 * exhaustion is a terminal STALLED with the evidence preserved;
 * a receipt verdict of "unknown" stays UNVERIFIED and is never
 * retried (an inability to observe is not evidence of absence);
 * a "generating" stage (the destination never stopped generating
 * inside the bounded defer) is STALLED, not failed. And every
 * exit leaves a trail entry — including the busy exit that used
 * to swallow the goodnight letter whole (Finding 4). */
let pbDelivering = false;
async function attemptDelivery(envelope) {
  const id = envelope.message_id;
  if (pbDelivering) {
    // Serialised: one letter at a time. V6.1: the deferral is
    // ACCOUNTED on the waiting letter's trail, and the finally
    // block below drains the queue when the current delivery ends.
    try {
      const st = await pbLoadState();
      const det = st.detections.find((d) => d.envelope && d.envelope.message_id === id);
      if (det) {
        if (!det.crusher) det.crusher = pbCrusherRecord(envelope, det.at);
        if (det.crusher.state === "VERIFIED" || det.crusher.state === "HELD" || det.crusher.state === "STALLED" || det.crusher.state === "RETRY_WAIT") {
          pbCrusherNote(det.crusher, "attempt deferred — the pair's active carry is still running; this letter is served when it finishes", new Date().toISOString());
          await pbSaveState(st);
        }
      }
    } catch (e) { /* accounting is best-effort here; the drain below still runs this letter */ }
    return;
  }
  pbDelivering = true;
  try {
    let state = await pbLoadState();
    if (PB.pbAlreadyDelivered(state, id)) return;
    const det = state.detections.find((d) => d.envelope && d.envelope.message_id === id);
    if (!det) return;
    if (!det.crusher) det.crusher = pbCrusherRecord(envelope, det.at);
    if (det.crusher.state === "ACKNOWLEDGED" || det.crusher.state === "UNVERIFIED" ||
        det.crusher.state === "ABANDONED") return; // terminal states never re-run
    if (det.crusher.terminalStall) return; // V6.1: evidence-preserved stall — Ben's hand only
    if (det.crusher.pausedAt) return; // V0.15.0: Ben paused this letter — no attempt while paused
    if (state.paused) {
      if (det.crusher.state === "VERIFIED" || det.crusher.state === "RETRY_WAIT") {
        pbCrusherMark(state, id, "held", "", "bridge paused at attempt time", new Date().toISOString());
        pbLog(state, `HELD ${envelope.from} → ${envelope.to}: bridge paused — letter waits for Ben's hand`);
        await pbSaveState(state);
      }
      return;
    }
    const dest = state.registrations[envelope.to];
    if (!dest || !dest.tabId) {
      /* V0.15.0: a missing destination is a transient failure
       * on the ladder. The letter keeps its STALLED face while
       * it waits (the pump serves it when its time comes due),
       * and the ladder — not a sweep of Ben's — drives it. */
      if (det.crusher.state !== "STALLED") {
        pbCrusherMark(state, id, "stalled", "registration", "destination tab not registered", new Date().toISOString());
        pbLog(state, `STALLED ${envelope.from} → ${envelope.to}: destination tab not registered — recovery ladder engaged`);
      }
      {
        const c = det.crusher;
        const now = Date.now();
        pbRecoveryInit(c, now);
        c.recovery.failures += 1;
        if (pbRecoveryExhausted(c, now)) {
          pbCrusherTransition(c, "STOPPED", "recovery exhausted — destination never registered", new Date(now).toISOString());
          c.stopReason = "RECOVERY_EXHAUSTED";
          c.nextAttemptAt = null;
          pbLog(state, `NEEDS YOU ${envelope.from} → ${envelope.to}: the destination never came back — recovery exhausted`);
        } else {
          const ladder = (typeof PB_TEST_LADDER_MS !== "undefined") ? PB_TEST_LADDER_MS : PB_LADDER_MS;
          const delay = ladder[Math.min(c.recovery.failures - 1, ladder.length - 1)];
          c.nextAttemptAt = new Date(now + delay).toISOString();
          pbCrusherNote(c, `destination still not registered — recovery failure ${c.recovery.failures}, next check in ${Math.round(delay / 1000)}s`, new Date(now).toISOString());
          pbLog(state, `RECOVERY ${envelope.from} → ${envelope.to}: destination missing — failure ${c.recovery.failures}, next check in ${Math.round(delay / 1000)}s`);
        }
      }
      await pbSaveState(state);
      schedulePumpWake(state);
      return;
    }
    /* V0.17.0 — THE SEND-SAFETY FENCE (Ben's design, his
     * ruling; fence.js) stands where the v0.14.0 gate stood:
     * consulted HERE, before the DELIVERING transition, so a
     * held letter has made NO attempt — nothing typed, clicked
     * or engaged, and neither `attempts` nor any retry counter
     * moves. Three conditions, each answered positive /
     * negative / unknown from evidence:
     *   1 button status — the destination query's word
     *     ("generating" is a proven negative, "ready" a
     *     positive, "unknown" never a pass either way);
     *   2 serial order — the ledger's count (fence.js);
     *   3 message status — delivered is a state, checked.
     * Two positives and no negative: the attempt proceeds
     * (the old gate's "ready or unknown proceeds" is the
     * special case where conditions 2 and 3 carry it). A
     * negative vetoes. A hold keeps the letter in GATED with
     * the condition named on its trail; the five-minute bound
     * runs from the FIRST entry, exactly as the gate's did.
     * A superseded reply never sends: its pair closes as
     * superseded and the newer message starts the next pair —
     * Ben's reconcile, never an auto-redirect. */
    {
      const gen = await pbQueryGeneration(dest.tabId);
      const stF = await pbLoadState();
      const detF = stF.detections.find((d) => d.envelope && d.envelope.message_id === id);
      if (!detF) return;
      if (!detF.crusher) detF.crusher = pbCrusherRecord(envelope, detF.at);
      if (detF.serial == null) {
        const n = PB_FENCE.pbFenceAssignSerial(stF, detF);
        pbLog(stF, `LEDGER ${envelope.from} → ${envelope.to}: a pre-fence letter joins the count as #${n}`);
      }
      const bufDet = stF.bufferId ? pairDetection(stF, stF.bufferId) : null;
      const c1 = PB_FENCE.pbFenceButtonCondition(gen);
      const c2 = PB_FENCE.pbFenceSerialCondition(stF.detections, detF, stF.pair, bufDet);
      const c3 = PB_FENCE.pbFenceStatusCondition(stF.deliveredIds, detF);
      const verdict = PB_FENCE.pbFenceVerdict({ button: c1, serial: c2.value, status: c3.value });
      const tally = `fence: button ${c1} · serial ${c2.value} (${c2.why}) · status ${c3.value} (${c3.why})`;
      if (verdict.action === "send") {
        if (detF.crusher.fenceHold || detF.crusher.fenceRecheckAt) {
          delete detF.crusher.fenceHold;
          delete detF.crusher.fenceRecheckAt;
          pbCrusherNote(detF.crusher, tally + " — the fence passes; the attempt proceeds", new Date().toISOString());
        }
        await pbSaveState(stF);
        state = stF;
        /* fall through to the DELIVERING transition below */
      } else if (c2.superseded) {
        pbCrusherTransition(detF.crusher, "ABANDONED", "superseded by a newer message — not sent (" + tally + ")", new Date().toISOString());
        detF.delivery = { status: "held", reason: "superseded by a newer message — reply not sent", at: new Date().toISOString(), crusher: true };
        pbLog(stF, `SUPERSEDED ${envelope.from} → ${envelope.to}: a newer message from ${envelope.to} arrived while this reply waited — the reply is not sent; the pair closes and the newer message starts the next pair`);
        retirePair(stF, "the reply was superseded by a newer message — not sent", true);
        await pbSaveState(stF);
        return;
      } else {
        const nowIso = new Date().toISOString();
        const c = detF.crusher;
        const vetoTxt = verdict.veto
          ? "condition " + verdict.vetoName + " (" + PB_FENCE.pbFenceConditionName(verdict.vetoName) + ")"
          : "the quorum unmet — " + verdict.positives + " positive, " + verdict.unknowns.join(", ") + " unproven";
        const firstHold = !c.fenceHold && !c.fenceRecheckAt;
        if (verdict.vetoName === 1) {
          /* Condition 1's hold IS the old gate: it keeps the
           * gate's own bookkeeping (a recheck cadence, but no
           * fenceHold flag — a pure button hold that times out
           * is a GATE_TIMEOUT, as it always was). */
          c.fenceRecheckAt = new Date(Date.now() + PB_FENCE.PB_FENCE_RECHECK_MS).toISOString();
        } else {
          c.fenceHold = {
            condition: verdict.vetoName || 0,
            detail: verdict.vetoName === 2 ? c2.why : verdict.vetoName === 3 ? c3.why : tally,
            since: (c.fenceHold && c.fenceHold.since) || nowIso,
            recheckAt: new Date(Date.now() + PB_FENCE.PB_FENCE_RECHECK_MS).toISOString(),
          };
        }
        if (c.state !== "GATED") {
          pbCrusherTransition(c, "GATED", "fence hold — held by " + vetoTxt + "; no attempt made", nowIso);
          c.gateSince = nowIso;
        } else {
          if (!c.gateSince) c.gateSince = nowIso;
          pbCrusherNote(c, "fence hold continues — held by " + vetoTxt + " (" + tally + ")", nowIso);
        }
        if (firstHold) {
          if (verdict.vetoName === 1) {
            /* Condition 1's hold IS the old gate — its log
             * words stand, the fence tally rides the trail. */
            pbCrusherNote(c, tally, nowIso);
            pbLog(stF, `GATED ${envelope.from} → ${envelope.to}: destination generating — no attempt made; waiting for the send button`);
          } else {
            pbLog(stF, `FENCE HOLD ${envelope.from} → ${envelope.to}: held by ${vetoTxt} — ${c.fenceHold.detail}; no attempt made`);
          }
        }
        c.gateWake = false;
        await pbSaveState(stF);
        schedulePumpWake(stF);
        await pbPushWait(stF, detF);
        return;
      }
    }
    const detNow = state.detections.find((d) => d.envelope && d.envelope.message_id === id) || det;
    pbCrusherTransition(detNow.crusher, "DELIVERING", "attempt " + (detNow.crusher.attempts + 1), new Date().toISOString());
    detNow.crusher.nextAttemptAt = null; // V6.2: the wait is over; the attempt is running
    await pbSaveState(state);
    await pbPushWait(state, detNow); // V0.14.0: the panel shows ATTEMPTING
    const text = PB.pbCarriedText(envelope.from, envelope.body, id);
    let lastStage = "", lastError = "";
    while (true) {
      state = await pbLoadState();
      const d2 = state.detections.find((d) => d.envelope && d.envelope.message_id === id);
      if (!d2) return;
      if (!d2.crusher) d2.crusher = pbCrusherRecord(envelope, d2.at);
      d2.crusher.attempts += 1;
      await pbSaveState(state);
      let res = null;
      let unreachable = false;
      try {
        res = await chrome.tabs.sendMessage(dest.tabId, { kind: "pb-deliver", text });
      } catch (e) {
        unreachable = true;
        res = { ok: false, stage: "unreachable", error: "destination content script unreachable: " + String(e && e.message || e) };
      }
      if (res && res.ok) {
        state = await pbLoadState();
        pbCrusherMark(state, id, "acknowledged", "", "", new Date().toISOString());
        pbLog(state, `ACKNOWLEDGED ${envelope.from} → ${envelope.to}: "${envelope.body.slice(0, 60)}${envelope.body.length > 60 ? "…" : ""}" (receipt confirmed)`);
        if (res.duplicates && res.duplicates > 1) {
          pbLog(state, `DUPLICATE ARRIVAL ${envelope.from} → ${envelope.to}: the letter's PB-ID appears on ${res.duplicates} user turns in the destination — same id, recognised as one letter`);
        }
        /* V0.11.0 P2: a rollover happened inside this delivery —
         * record it (the letter kept its PB-ID and landed in the
         * NEW conversation; Alex's invariants 2 and 4). */
        if (res.rollover) {
          if (!state.rollovers) state.rollovers = [];
          state.rollovers.push({
            at: new Date().toISOString(), seat: envelope.to,
            fromUrl: res.rollover.fromUrl || null, toUrl: res.rollover.toUrl || null,
            fromTitle: res.rollover.fromTitle || null,
            notice: res.rollover.notice || null, letterId: id,
          });
          if (state.rollovers.length > 10) state.rollovers = state.rollovers.slice(-10);
          pbLog(state, `ROLLOVER ${envelope.to}: the destination conversation was full ("Context window full") — a new chat was opened and this letter landed there under the same PB-ID (rollover notice: ${res.rollover.notice || "unknown"})`);
        }
        /* V0.11.0 P1: complete the file transfer's outcome now
         * that the letter is acknowledged in the destination. A
         * router-verified file whose letter landed earns
         * FILE_CONTENT_DELIVERED_VERIFIED (content received and
         * hash-checked; the bridge wrote no file). Any other
         * recorded status completes as FILE_HANDOFF_FAILED at the
         * end-to-end level — the letter arrived, the file did not
         * verify. */
        const detOk = state.detections.find((d) => d.envelope && d.envelope.message_id === id);
        const ft = detOk && detOk.envelope && detOk.envelope.fileTransfer;
        if (ft) {
          ft.outcome = ft.status === "verified" ? "FILE_CONTENT_DELIVERED_VERIFIED" : "FILE_HANDOFF_FAILED";
          const led = (state.fileTransfers || []).find((r) => r.messageId === id);
          if (led) led.outcome = ft.outcome;
          pbLog(state, `FILE "${ft.name}" (${envelope.from} → ${envelope.to}): transport outcome ${ft.outcome}`);
        }
        await pbSaveState(state);
        return;
      }
      lastStage = (res && res.stage) || "deliver";
      lastError = (res && res.error) || "delivery refused";
      state = await pbLoadState();
      const d3 = state.detections.find((d) => d.envelope && d.envelope.message_id === id);
      const attempts = d3 && d3.crusher ? d3.crusher.attempts : PB_CRUSHER_MAX_ATTEMPTS;
      if (lastStage === "receipt" && res && res.verdict === "absent") {
        /* V6.1 PROVEN-ABSENCE RETRY (Alex ruling 2): confirmation
         * positively established the letter is NOT in the
         * destination. Bounded: at most PB_CRUSHER_MAX_ABSENCE_
         * RETRIES retries, spaced out, same message_id and the
         * same carried text (the PB-ID line identifies any
         * duplicate arrival as the same letter). Exhaustion is a
         * terminal STALLED with the evidence preserved. */
        const used = d3 && d3.crusher ? (d3.crusher.absenceRetries || 0) : PB_CRUSHER_MAX_ABSENCE_RETRIES;
        if (used < PB_CRUSHER_MAX_ABSENCE_RETRIES) {
          if (d3 && d3.crusher) d3.crusher.absenceRetries = used + 1;
          pbLog(state, `ABSENT ${envelope.from} → ${envelope.to}: confirmation established the letter is not there — proven-absence retry ${used + 1}/${PB_CRUSHER_MAX_ABSENCE_RETRIES} (bridge free meanwhile)`);
          /* V6.2: the retry WAITS IN RETRY_WAIT — the letter holds
           * nothing while the 30s runs. V6.1 slept here, inside
           * the one delivery slot, while every other letter on
           * the bridge stood deferred behind it. The pump serves
           * the retry when its due time comes, behind any letter
           * that became actionable earlier. */
          await scheduleRetryWait(state, id, PB_CRUSHER_ABSENCE_RETRY_DELAY_MS,
            `absence established after attempt ${attempts} — proven-absence retry ${used + 1}/${PB_CRUSHER_MAX_ABSENCE_RETRIES} in ${Math.round(PB_CRUSHER_ABSENCE_RETRY_DELAY_MS / 1000)}s, same PB-ID`);
          return;
        }
        /* V0.15.0: proven-absence exhaustion is a transient
         * failure like any other — the ladder takes it from
         * here (spec 4.1/4.2). No terminal stall. */
        const d4 = state.detections.find((d) => d.envelope && d.envelope.message_id === id);
        pbLog(state, `ABSENT ${envelope.from} → ${envelope.to}: proven-absence retries exhausted — the recovery ladder takes over`);
        if (d4 && d4.crusher) pbRecoveryFail(state, d4, "absence established on every attempt");
        await pbSaveState(state);
        await pbPushWait(state, d4 || det);
        return;
      }
      if (lastStage === "receipt") {
        /* Verdict "unknown" (or no verdict): the machine could not
         * establish absence, so it says "I don't know" — UNVERIFIED,
         * never retried. An inability to observe an event is not
         * evidence the event did not happen (Alex ruling 2). */
        pbCrusherMark(state, id, "unverified", lastStage, lastError, new Date().toISOString());
        pbLog(state, `UNVERIFIED ${envelope.from} → ${envelope.to}: ${lastError} — sent, but unconfirmed; absence not established, never auto-retried`);
        await pbSaveState(state);
        return;
      }
      if (unreachable || lastStage === "unreachable") {
        /* V6.2: an unreachable destination is a "not yet", not a
         * parking lot — the letter re-queues ITSELF, bounded, and
         * the bridge stays free for other letters meanwhile. Only
         * budget exhaustion parks it in STALLED for Ben's sweeps. */
        /* V0.15.0: an unreachable destination is a transient
         * failure on the ladder — no auto-retry counter, no
         * parking (spec 4.1/4.2). */
        if (d3 && d3.crusher) pbRecoveryFail(state, d3, `destination unreachable: ${lastError}`);
        await pbSaveState(state);
        await pbPushWait(state, d3 || det);
        return;
      }
      if (lastStage === "generating") {
        /* The destination was still generating when the bounded
         * defer ran out (Ben's button gate held the send — nothing
         * was engaged, typed or clicked). V6.1 parked this in
         * STALLED until some external event fired a sweep; V6.2
         * re-queues the letter itself, bounded — when the page
         * goes quiet, the pump tries again on its own. */
        /* V0.15.0: an in-attempt defer that ran out is a
         * transient failure on the ladder (the pre-delivery
         * gate of v0.14.0 remains the primary mechanism; this
         * endpoint is its backstop). */
        if (d3 && d3.crusher) pbRecoveryFail(state, d3, `destination still generating at the defer bound: ${lastError}`);
        await pbSaveState(state);
        await pbPushWait(state, d3 || det);
        return;
      }
      if (lastStage === "context-full") {
        /* V0.11.0 P2: the destination conversation is full and the
         * rollover could not complete (no banner button, or the
         * new chat never became ready). The letter was NOT
         * delivered into the full conversation (Alex's invariant
         * 3). This is a stall for Ben's hand — never a failure:
         * nothing was sent, and the evidence (the adapter's own
         * words) is preserved on the record. */
        pbCrusherMark(state, id, "stalled", lastStage, lastError, new Date().toISOString());
        pbLog(state, `STALLED ${envelope.from} → ${envelope.to}: ${lastError}`);
        await pbSaveState(state);
        return;
      }
      if (pbCrusherIsPresend(lastStage) && attempts < PB_CRUSHER_MAX_ATTEMPTS) {
        if (d3 && d3.crusher) {
          pbCrusherNote(d3.crusher, `attempt ${attempts} failed pre-send at stage "${lastStage}" — retrying`, new Date().toISOString());
        }
        pbLog(state, `DELIVERING ${envelope.from} → ${envelope.to}: pre-send stage "${lastStage}" failed (attempt ${attempts}/${PB_CRUSHER_MAX_ATTEMPTS}) — retrying: ${lastError}`);
        await pbSaveState(state);
        await new Promise((r) => setTimeout(r, PB_CRUSHER_RETRY_DELAY_MS));
        continue;
      }
      /* V0.15.0: even the last-resort failure is transient —
       * the ladder decides whether the letter waits or needs
       * Ben. FAILED is no longer a resting place. */
      {
        const dF2 = state.detections.find((d) => d.envelope && d.envelope.message_id === id);
        pbLog(state, `FAILURE ${envelope.from} → ${envelope.to} at stage "${lastStage}": ${lastError} — handed to the recovery ladder`);
        if (dF2 && dF2.crusher) pbRecoveryFail(state, dF2, `failed at stage "${lastStage}": ${lastError}`);
        await pbSaveState(state);
        await pbPushWait(state, dF2 || det);
      }
      return;
    }
  } finally {
    pbDelivering = false;
    /* V0.14.0: whatever this attempt left on the record, the
     * destination panel hears it (DELIVERED on the ACK path,
     * WAITING-RETRY after a requeue, STOPPED on a terminal mark).
     * Best-effort by design — the view never gates the machine. */
    try {
      const stW = await pbLoadState();
      const detW = stW.detections.find((d) => d.envelope && d.envelope.message_id === id);
      /* V0.15.0: a pause Ben pressed mid-attempt lands HERE, as
       * the attempt settles — never mid-insert (spec 3.3). A
       * letter that resolved anyway records the pause as moot. */
      if (detW && detW.crusher && detW.crusher.pausePending) {
        detW.crusher.pausePending = false;
        const csW = detW.crusher.state;
        if (csW !== "ACKNOWLEDGED" && csW !== "UNVERIFIED" && csW !== "ABANDONED") {
          detW.crusher.pausedAt = new Date().toISOString();
          pbLog(stW, `PAUSED ${detW.envelope.from} → ${detW.envelope.to}: Ben's pause landed as the attempt settled`);
        } else {
          pbCrusherNote(detW.crusher, "Ben's pause arrived as the letter resolved — moot", new Date().toISOString());
        }
        await pbSaveState(stW);
      }
      if (detW) await pbPushWait(stW, detW);
    } catch (e) { /* view only */ }
    // V6.2: hand the slot back to the QUEUE PUMP — the next
    // oldest actionable letter is served now, not whenever the
    // next external event happens to fire a sweep (Finding 4).
    // When this attempt ran INSIDE the pump, the call is a no-op
    // (the pump's own loop continues); when it ran standalone,
    // the pump starts here.
    pumpQueue().catch(() => {});
  }
}

/* ===== V0.14.0 — MECHANISM B (background half): wait-state views.
 * The background is the source of truth; the destination page's
 * panel is a view. pbWaitView maps a delivery record to the exact
 * payload a panel renders — display state, plain-words reason
 * class, and the record's REAL nextAttemptAt (null whenever no
 * attempt is scheduled: a GATED wait never shows a countdown,
 * because when the page will free up is genuinely unknown).
 * Filtering is done HERE (Alex's ruling): a tab is only ever sent
 * its own seat's views, and the pull handler below answers only
 * the seat the asking tab is registered under — fail closed when
 * no registration names the tab. */
function pbWaitReason(det) {
  const c = det.crusher;
  let text = "";
  if (det.delivery && det.delivery.reason) text += " " + det.delivery.reason;
  if (c && c.trail && c.trail.length) text += " " + (c.trail[c.trail.length - 1].note || "");
  const t = text.toLowerCase();
  if (t.includes("superseded")) return "superseded — not sent";
  if (t.includes("out of order")) return "held — out of order";
  if (t.includes("fence")) return "held by the send fence";
  if (t.includes("absence")) return "letter not there — retrying";
  if (t.includes("unreachable") || t.includes("not registered")) return "page unreachable";
  if (t.includes("generating")) return "page busy writing";
  if (t.includes("insertion")) return "page refused the text";
  return "other";
}

function pbWaitView(det) {
  if (!det || !det.envelope || !det.crusher) return null;
  const c = det.crusher;
  const e = det.envelope;
  const base = { message_id: e.message_id, from: e.from, to: e.to };
  switch (c.state) {
    case "GATED":
      return { ...base, displayState: "WAITING-GATED", reason: "page busy writing", nextAttemptAt: null };
    case "DELIVERING":
      return { ...base, displayState: "ATTEMPTING", reason: "", nextAttemptAt: null };
    case "RETRY_WAIT":
      return { ...base, displayState: "WAITING-RETRY", reason: pbWaitReason(det), nextAttemptAt: c.nextAttemptAt || null };
    case "ACKNOWLEDGED":
      return { ...base, displayState: "DELIVERED", reason: "", nextAttemptAt: null };
    case "UNVERIFIED":
      return { ...base, displayState: "STOPPED", reason: "sent, but unconfirmed", nextAttemptAt: null };
    case "FAILED":
      return { ...base, displayState: "STOPPED", reason: pbWaitReason(det), nextAttemptAt: null };
    case "STALLED":
      return { ...base, displayState: "STOPPED", reason: pbWaitReason(det), nextAttemptAt: null };
    case "STOPPED":
      return {
        ...base, displayState: "STOPPED",
        reason: c.stopReason === "GATE_TIMEOUT"
          ? "page still writing after 5 minutes — waiting for a human"
          : "stopped",
        nextAttemptAt: null,
        stopReason: c.stopReason || null,
        /* B6: the failure popup rides the view ONLY while the
         * record says it is still owed (gateTimeoutPending); the
         * panel latches it shown and acknowledges via
         * pb-popup-shown, after which no push or rebuild carries
         * it again — one notification per timeout event. */
        raisePopup: !!(c.stopReason === "GATE_TIMEOUT" && c.gateTimeoutPending),
      };
    default:
      return null;
  }
}

/* ===== V0.15.0 — THE FACE (spec sections 2, 5, 6, 7) =====
 * The background computes the panel's whole face for a seat:
 * one live word, one plain sentence, the live letters with
 * their eligible controls, and today's Earlier lines. Every
 * string comes from the spec's copy table (section 7) — the
 * panel renders them verbatim and invents nothing. A record
 * is CURRENT while non-terminal, or terminal in THIS
 * background session; a STOPPED record left by a previous
 * session is historical from the new session's first second
 * and can never headline (the 2026-11-09 03:33 finding). */
const PB_SESSION_START = Date.now();
function pbSeatName(seat) { return seat === "alex" ? "Alex" : seat === "remmy" ? "Remmy" : String(seat || ""); }
function pbFaceTime(iso) {
  const d = new Date(iso);
  if (isNaN(d)) return "";
  let h = d.getHours();
  const ap = h >= 12 ? "PM" : "AM";
  h = h % 12 || 12;
  return h + ":" + String(d.getMinutes()).padStart(2, "0") + " " + ap;
}
function pbFaceFor(state, seat) {
  const name = pbSeatName(seat);
  const pronoun = seat === "alex" ? "he" : "she";
  const letters = [];
  const earlier = [];
  let needsYou = false, pausedAny = false, sending = false, waiting = false;
  let topSev = 0, topSentence = null;
  const consider = (sev, sentence) => { if (sev > topSev) { topSev = sev; topSentence = sentence; } };
  for (const d of state.detections || []) {
    if (!d.envelope || d.envelope.to !== seat || !d.crusher) continue;
    const c = d.crusher;
    const id = d.envelope.message_id;
    const lastAt = (c.trail && c.trail.length) ? c.trail[c.trail.length - 1].at : (d.at || null);
    if (c.state === "STOPPED") {
      const sentence = c.stopReason === "GATE_TIMEOUT"
        ? "Needs you. " + name + " stayed busy for five minutes, so the letter was never sent."
        : "Needs you. A letter to " + name + " couldn't get through, and it has stopped trying on its own.";
      if (Date.parse(lastAt || "") < PB_SESSION_START) {
        earlier.push({ id, line: "To " + name + " — needed you, " + pbFaceTime(lastAt) + ".", controls: ["retry", "abandon"] });
      } else {
        letters.push({ id, sentence, controls: ["retry", "abandon"], popup: !!(c.stopReason === "GATE_TIMEOUT" && c.gateTimeoutPending) });
        needsYou = true; consider(4, sentence);
      }
      continue;
    }
    if (c.state === "ACKNOWLEDGED" || c.state === "UNVERIFIED" || c.state === "ABANDONED") continue;
    let sentence, controls;
    if (c.pausedAt) {
      sentence = "You paused this letter."; controls = ["resume", "abandon"];
      pausedAny = true; consider(3, sentence);
    } else if (c.state === "DELIVERING") {
      sentence = "Sending a letter to " + name + "…"; controls = [];
      sending = true; consider(2, sentence);
    } else if (c.state === "GATED") {
      sentence = "Waiting — " + name + " is still writing. The letter goes the moment " + pronoun + " finishes."; controls = ["pause", "abandon"];
      waiting = true; consider(1, sentence);
    } else if (c.state === "RETRY_WAIT" || c.state === "STALLED" || c.state === "VERIFIED" || c.state === "HELD") {
      sentence = "A letter to " + name + " didn't go through. It will try again on its own.";
      controls = c.state === "STALLED" ? ["abandon"] : ["pause", "abandon"];
      waiting = true; consider(1, sentence);
    } else continue;
    letters.push({ id, sentence, controls });
  }
  for (const h of state.faceHistory || []) {
    if (!h || h.seat !== seat) continue;
    if (new Date(h.at).toDateString() !== new Date().toDateString()) continue;
    earlier.push({ id: null, line: "To " + name + (h.kind === "delivered" ? " — delivered, " : " — you let it go, ") + pbFaceTime(h.at) + ".", controls: [] });
  }
  let word, sentence;
  if (needsYou) { word = "needs you"; sentence = topSentence; }
  else if (state.paused) { word = "paused"; sentence = "Paused. Letters wait until you resume."; }
  else if (pausedAny) { word = "paused"; sentence = topSentence; }
  else if (sending) { word = "sending…"; sentence = topSentence; }
  else if (waiting) { word = "waiting"; sentence = topSentence; }
  else { word = "idle"; sentence = "All clear. Nothing is waiting."; }
  return { seat, word, sentence, bridgePaused: !!state.paused, letters, earlier };
}
async function pbPushFaceToSeat(state, seat) {
  try {
    const reg = state.registrations && state.registrations[seat];
    if (!reg || !reg.tabId) return;
    await chrome.tabs.sendMessage(reg.tabId, { kind: "pb-wait-state", face: pbFaceFor(state, seat) });
  } catch (e) { /* the panel is a view — a failed push never affects delivery */ }
}
async function pbPushWait(state, det) {
  if (!det || !det.envelope) return;
  await pbPushFaceToSeat(state, det.envelope.to);
}

/* ===== V0.14.0 — MECHANISM A: THE SEND-SIDE BUTTON GATE.
 * Ask the destination tab's content script for the page's
 * generation state through the adapter signal. Only an explicit
 * "generating" engages the gate: "ready" proceeds, and anything
 * unreadable is "unknown" — unknown is NOT generating (A3: the
 * gate never invents a block from a page it cannot read, the
 * UNVERIFIED discipline applied to a button). */
async function pbQueryGeneration(tabId) {
  try {
    const r = await chrome.tabs.sendMessage(tabId, { kind: "pb-generation-state" });
    if (r && r.state === "generating") return "generating";
    if (r && (r.state === "ready" || r.state === "available")) return "ready";
    return "unknown";
  } catch (e) {
    return "unknown";
  }
}

/* Gate timeouts: a letter that has waited in GATED past the
 * bound stops — STOPPED with reason GATE_TIMEOUT, still never
 * attempted, still no budget spent, and the B6 popup becomes
 * owed (gateTimeoutPending). Runs on pump passes, so the
 * pb-pump-wake alarm (which also arms on gate deadlines, see
 * schedulePumpWake) fires it even in total silence. */
/* V0.15.0 — interrupted-attempt reconstruction (spec 4.4).
 * A record found in DELIVERING long after its attempt began
 * was interrupted (reload, worker death): its fate is UNKNOWN,
 * never assumed. The interruption counts as one transient
 * failure and the ladder takes the letter — the re-attempt
 * itself runs through the ordinary deliver machinery, whose
 * confirmation either finds the letter already there or
 * establishes absence before any re-send (the proven-absence
 * discipline). Same record, same PB-ID. */
const PB_DELIVERING_STALE_MS = 120000;
async function pbReapStaleDelivering() {
  const state = await pbLoadState();
  const staleMs = (typeof PB_TEST_DELIVERING_STALE_MS !== "undefined") ? PB_TEST_DELIVERING_STALE_MS : PB_DELIVERING_STALE_MS;
  const now = Date.now();
  let changed = false;
  for (const d of state.detections || []) {
    const c = d.crusher;
    if (!c || c.state !== "DELIVERING" || c.pausedAt) continue;
    const lastAt = (c.trail && c.trail.length) ? Date.parse(c.trail[c.trail.length - 1].at) : 0;
    if (!lastAt || now - lastAt < staleMs) continue;
    pbLog(state, `INTERRUPTED ${d.envelope.from} → ${d.envelope.to}: an attempt was cut off mid-flight — its fate is unknown; the ladder takes the letter`);
    pbRecoveryFail(state, d, "attempt interrupted mid-flight (reload or worker death) — fate unknown");
    changed = true;
  }
  if (changed) await pbSaveState(state);
}

async function processGateTimeouts() {
  const state = await pbLoadState();
  const now = Date.now();
  let changed = false;
  for (const d of state.detections) {
    const c = d.crusher;
    if (!c || c.state !== "GATED" || !c.gateSince || c.pausedAt) continue; // V0.15.0: a paused letter's gate clock is frozen
    if (now - Date.parse(c.gateSince) < PB_GATE_MAX_MS) continue;
    if (c.fenceHold) {
      /* V0.17.0: a fence hold past the same five-minute bound
       * stops with its condition named — FENCE_TIMEOUT, the
       * fence's own word, never dressed as a button problem. */
      const condName = PB_FENCE.pbFenceConditionName(c.fenceHold.condition);
      pbCrusherTransition(c, "STOPPED", "fence timeout — held by condition " + c.fenceHold.condition + " (" + condName + ") past the five-minute bound; no attempt was made", new Date().toISOString());
      c.stopReason = "FENCE_TIMEOUT";
      c.gateTimeoutPending = true;
      c.gateWake = false;
      pbLog(state, `STOPPED ${d.envelope.from} → ${d.envelope.to}: FENCE_TIMEOUT — condition ${c.fenceHold.condition} (${condName}) held the letter past the five-minute bound (${c.fenceHold.detail}); no attempt was made and no retry budget was spent; a human must resume it`);
    } else {
      pbCrusherTransition(c, "STOPPED", "gate timeout — the send button never became available inside the bound; no attempt was made", new Date().toISOString());
      c.stopReason = "GATE_TIMEOUT";
      c.gateTimeoutPending = true;
      c.gateWake = false;
      pbLog(state, `STOPPED ${d.envelope.from} → ${d.envelope.to}: GATE_TIMEOUT — the letter waited at the gate past the five-minute bound; no attempt was made and no retry budget was spent; a human must resume it`);
    }
    changed = true;
    await pbPushWait(state, d);
  }
  if (changed) await pbSaveState(state);
}

/* V0.17.0: a fence-held letter re-checks itself on a short
 * cadence — when its recheck comes due, its gateWake is set
 * and the pump serves it into a fresh fence evaluation. The
 * hold's five-minute bound runs from gateSince (the first
 * entry), untouched by rechecks: a recheck can release a
 * hold, never extend one. */
async function processFenceRechecks() {
  const state = await pbLoadState();
  const now = Date.now();
  let changed = false;
  for (const d of state.detections) {
    const c = d.crusher;
    if (!c || c.state !== "GATED" || c.pausedAt) continue;
    const due = Math.max(
      c.fenceHold ? (Date.parse(c.fenceHold.recheckAt || "") || 0) : 0,
      c.fenceRecheckAt ? (Date.parse(c.fenceRecheckAt || "") || 0) : 0);
    if (due && due <= now && !c.gateWake) { c.gateWake = true; changed = true; }
  }
  if (changed) await pbSaveState(state);
}

/* V6.2: park a letter in RETRY_WAIT with a due time, and make
 * sure something wakes the pump when the time comes. The letter
 * holds NOTHING while it waits — the delivery slot is free for
 * every other letter (the V6.1 absence sleep, 30 seconds inside
 * the slot, is the hog this replaces). */
/* ===== V0.15.0 — SELF-RECOVERY (spec section 4) =====
 * The bounded ladder: every transient failure schedules the
 * letter's own next attempt from durable timestamps. Nothing
 * ends parked: a letter is always scheduled, gated, paused by
 * a named human, delivered, let go, or needs-you. Exhaustion
 * is defined (12 failures, or 24 unpaused hours) and final —
 * after it, the machine takes no further automatic action. */
const PB_LADDER_MS = [30000, 120000, 300000, 900000, 3600000];
const PB_RECOVERY_MAX_FAILURES = 12;
const PB_RECOVERY_MAX_MS = 24 * 3600 * 1000;

function pbRecoveryInit(c, now) {
  if (!c.recovery) c.recovery = { failures: 0, firstFailureAt: null, windowStart: null, pausedTotalMs: 0 };
  if (!c.recovery.firstFailureAt) {
    c.recovery.firstFailureAt = new Date(now).toISOString();
    c.recovery.windowStart = c.recovery.firstFailureAt;
  }
}
function pbRecoveryExhausted(c, now) {
  if (!c.recovery) return false;
  const maxF = (typeof PB_TEST_EXHAUST_FAILURES !== "undefined") ? PB_TEST_EXHAUST_FAILURES : PB_RECOVERY_MAX_FAILURES;
  const maxMs = (typeof PB_TEST_EXHAUST_MS !== "undefined") ? PB_TEST_EXHAUST_MS : PB_RECOVERY_MAX_MS;
  if (c.recovery.failures >= maxF) return true;
  const start = Date.parse(c.recovery.windowStart || c.recovery.firstFailureAt || "");
  if (isNaN(start)) return false;
  const pausedMs = (c.recovery.pausedTotalMs || 0) + (c.pausedAt ? (now - Date.parse(c.pausedAt)) : 0);
  return (now - start - pausedMs) > maxMs;
}
/* One transient failure lands here. Returns "waiting" (the
 * ladder scheduled the next attempt) or "stopped" (recovery
 * genuinely exhausted — needs you). Mutates only; caller saves. */
function pbRecoveryFail(state, det, note) {
  const c = det.crusher;
  const now = Date.now();
  pbRecoveryInit(c, now);
  c.recovery.failures += 1;
  const at = new Date(now).toISOString();
  if (pbRecoveryExhausted(c, now)) {
    if (c.state !== "RETRY_WAIT" && c.state !== "STALLED" && c.state !== "FAILED") {
      pbCrusherTransition(c, "RETRY_WAIT", note + " — recovery exhausted", at);
    }
    pbCrusherTransition(c, "STOPPED", "recovery exhausted — " + note, at);
    c.stopReason = "RECOVERY_EXHAUSTED";
    c.nextAttemptAt = null;
    det.delivery = { status: "needs-you", reason: note, at, crusher: true };
    pbLog(state, `NEEDS YOU ${det.envelope.from} → ${det.envelope.to}: recovery exhausted after ${c.recovery.failures} failures — the letter stops trying on its own (${note})`);
    return "stopped";
  }
  const ladder = (typeof PB_TEST_LADDER_MS !== "undefined") ? PB_TEST_LADDER_MS : PB_LADDER_MS;
  const delay = ladder[Math.min(c.recovery.failures - 1, ladder.length - 1)];
  c.nextAttemptAt = new Date(now + delay).toISOString();
  if (c.state !== "RETRY_WAIT") pbCrusherTransition(c, "RETRY_WAIT", note, at);
  else pbCrusherNote(c, note, at);
  det.delivery = { status: "retry-wait", reason: note, at, crusher: true };
  pbLog(state, `RECOVERY ${det.envelope.from} → ${det.envelope.to}: failure ${c.recovery.failures} — next attempt in ${Math.round(delay / 1000)}s (${note})`);
  return "waiting";
}

async function scheduleRetryWait(state, id, delayMs, note) {
  const det = state.detections.find((d) => d.envelope && d.envelope.message_id === id);
  if (!det) return;
  if (!det.crusher) det.crusher = pbCrusherRecord(det.envelope, det.at);
  det.crusher.nextAttemptAt = new Date(Date.now() + delayMs).toISOString();
  pbCrusherTransition(det.crusher, "RETRY_WAIT", note, new Date().toISOString());
  det.delivery = { status: "retry-wait", reason: note, at: new Date().toISOString(), crusher: true };
  await pbSaveState(state);
  schedulePumpWake(state);
}

/* Wake the pump when the earliest RETRY_WAIT comes due: a durable
 * chrome.alarms entry (survives the worker sleeping) plus an
 * in-worker timer (fires promptly while the worker lives). Both
 * just call the pump; the pump is guarded and idempotent. */
let pbWakeTimer = null;
function schedulePumpWake(state) {
  let earliest = null;
  for (const d of state.detections) {
    if (d.crusher && !d.crusher.pausedAt && d.crusher.state === "RETRY_WAIT" && d.crusher.nextAttemptAt) {
      const t = Date.parse(d.crusher.nextAttemptAt);
      if (!isNaN(t) && (earliest === null || t < earliest)) earliest = t;
    }
    /* V0.14.0: a GATED letter's deadline is a wake too — the
     * five-minute bound must fire even if no cleared notification
     * ever arrives. */
    if (d.crusher && !d.crusher.pausedAt && d.crusher.state === "GATED" && d.crusher.gateSince) {
      const t = Date.parse(d.crusher.gateSince) + PB_GATE_MAX_MS;
      if (!isNaN(t) && (earliest === null || t < earliest)) earliest = t;
    }
    /* V0.15.0: a dest-missing STALLED letter's ladder step is
     * a wake too — its next check must fire on its own. */
    if (d.crusher && !d.crusher.pausedAt && d.crusher.state === "STALLED" && !d.crusher.terminalStall && d.crusher.nextAttemptAt) {
      const t = Date.parse(d.crusher.nextAttemptAt);
      if (!isNaN(t) && (earliest === null || t < earliest)) earliest = t;
    }
    /* V0.17.0: a fence-held letter's recheck is a wake — the
     * hold must re-evaluate itself even in total silence. */
    if (d.crusher && !d.crusher.pausedAt && d.crusher.state === "GATED") {
      const fh = d.crusher.fenceHold && d.crusher.fenceHold.recheckAt;
      const fr = d.crusher.fenceRecheckAt;
      for (const cand of [fh, fr]) {
        if (!cand) continue;
        const t = Date.parse(cand);
        if (!isNaN(t) && (earliest === null || t < earliest)) earliest = t;
      }
    }
  }
  if (earliest === null) return;
  const delay = Math.max(0, earliest - Date.now());
  if (typeof chrome !== "undefined" && chrome.alarms && chrome.alarms.create) {
    try { chrome.alarms.create("pb-pump-wake", { when: Date.now() + delay + 250 }); } catch (e) { /* the timer below still fires */ }
  }
  if (typeof setTimeout !== "undefined") {
    if (pbWakeTimer) { try { clearTimeout(pbWakeTimer); } catch (e) { /* already fired */ } }
    pbWakeTimer = setTimeout(() => { pbWakeTimer = null; pumpQueue().catch(() => {}); }, delay + 25);
  }
}
if (typeof chrome !== "undefined" && chrome.alarms && chrome.alarms.onAlarm) {
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm && alarm.name === "pb-pump-wake") pumpQueue().catch(() => {});
  });
}

/* THE PUMP — the one door through which a letter reaches
 * attemptDelivery. V6.2 made it a fair queue; V7 makes it a
 * pair servant: the ONLY letter it will ever serve is the
 * active pair's current letter (the call in "carry-call", the
 * reply in "carry-reply"). A letter is actionable in the V6.2
 * senses — VERIFIED or HELD at once, RETRY_WAIT when its due
 * time has come, STALLED too on a Ben-action sweep
 * (includeStalled: registration, resume, pair retry). Terminal
 * states (ACKNOWLEDGED / UNVERIFIED / FAILED), delivered-ledger
 * letters and terminal stalls are never served. Attempt
 * machinery errors are accounted on the letter's own trail —
 * never swallowed. When the pump drains, advancePair() judges
 * the pair's progression on the confirmed outcomes. */
let pbPumping = false;
async function pumpQueue(includeStalled) {
  if (pbPumping) return;
  pbPumping = true;
  try {
    await processGateTimeouts().catch(() => {});
    await processFenceRechecks().catch(() => {});
    await pbReapStaleDelivering().catch(() => {});
    const attempted = new Set();
    const noted = new Set();
    for (let pass = 0; pass < 64; pass++) {
      const state = await pbLoadState();
      if (state.paused) { schedulePumpWake(state); return; }
      const now = Date.now();
      /* V7: the pair's current letter is the only candidate
       * there can ever be. */
      const pairNow = state.pair;
      const currentId = pairNow
        ? (pairNow.step === "carry-call" ? pairNow.callId
          : pairNow.step === "carry-reply" ? pairNow.replyId : null)
        : null;
      let best = null;
      if (currentId && !attempted.has(currentId) && !PB.pbAlreadyDelivered(state, currentId)) {
        const d = pairDetection(state, currentId);
        if (d && d.crusher && !d.crusher.pausedAt) {
          const c = d.crusher;
          const terminal = c.state === "ACKNOWLEDGED" || c.state === "UNVERIFIED" || c.state === "FAILED" || c.state === "STOPPED" || c.terminalStall;
          if (!terminal) {
            if (c.state === "VERIFIED" || c.state === "HELD") best = d;
            else if (c.state === "GATED") {
              /* V0.14.0: a gated letter is served only when its
               * cleared notification landed (gateWake) or Ben's
               * hand widens the pump — the attempt re-checks the
               * button before anything is engaged. */
              if (c.gateWake || includeStalled) best = d;
            }
            else if (c.state === "RETRY_WAIT") {
              const due = Date.parse(c.nextAttemptAt || "") || 0;
              if (due <= now || includeStalled) best = d;
            } else if (c.state === "STALLED" && !c.terminalStall) {
              /* V0.15.0: a ladder-waiting stall is served when
               * its own time comes due (or on Ben's wide sweep),
               * never parked for a human unstick. */
              const due = Date.parse(c.nextAttemptAt || "") || 0;
              if (due <= now || includeStalled) best = d;
            }
          }
        }
      }
      if (!best) { schedulePumpWake(state); return; }
      attempted.add(best.envelope.message_id);
      try {
        await attemptDelivery(best.envelope);
      } catch (e) {
        try {
          const st = await pbLoadState();
          const det = st.detections.find((x) => x.envelope && x.envelope.message_id === best.envelope.message_id);
          if (det && det.crusher) {
            pbCrusherNote(det.crusher, "attempt machinery error: " + String(e && e.message || e), new Date().toISOString());
            pbLog(st, `ACCOUNTED ${best.envelope.from} → ${best.envelope.to}: attempt machinery error noted on the letter's trail`);
            await pbSaveState(st);
          }
        } catch (e2) { /* the accounting path itself failed — nothing further can be recorded */ }
      }
    }
  } finally {
    pbPumping = false;
    // V7: with the slot free, the pair judge reads the confirmed
    // outcomes and moves the exchange forward (or promotes the
    // buffered message into a fresh pair and pumps again).
    advancePair().catch(() => {});
    // V0.13.0: the Crusher lane drains on the same wakes as the
    // pair pump; a wide pump (Ben's hand: unpause, registration)
    // also retries stalled Crusher deliveries.
    pumpCrusher(!!includeStalled).catch(() => {});
  }
}

/* V0.13.0 — THE CRUSHER LANE'S PUMP. Carries flagged Crusher
 * questions (detections whose envelope carries crusherFor) to
 * Remmy's seat via the ordinary delivery machinery — same states,
 * same honesty: ACKNOWLEDGED or UNVERIFIED after the send, never
 * a silent resend; pre-send failures follow the crusher record's
 * own bounded retry; a STALLED question waits for a wide pump
 * (Ben's hand), exactly like a stalled letter. One attempt per
 * question per pump; the lane never touches pair state. */
let pbCrusherPumping = false;
async function pumpCrusher(wide) {
  if (pbCrusherPumping) return;
  pbCrusherPumping = true;
  try {
    await processGateTimeouts().catch(() => {});
    await processFenceRechecks().catch(() => {});
    await pbReapStaleDelivering().catch(() => {});
    const attempted = new Set();
    for (let pass = 0; pass < 8; pass++) {
      const state = await pbLoadState();
      if (state.paused) return;
      const now = Date.now();
      const cand = (state.detections || []).find((d) => {
        if (!d.envelope || !d.envelope.crusherFor || d.envelope.to !== "remmy") return false;
        if (attempted.has(d.envelope.message_id)) return false;
        if (PB.pbAlreadyDelivered(state, d.envelope.message_id)) return false;
        const c = d.crusher;
        if (!c) return true;
        if (c.pausedAt) return false; // V0.15.0: Ben's pause binds the lane too
        if (c.state === "VERIFIED" || c.state === "HELD") return true;
        if (c.state === "GATED") return !!(c.gateWake || wide);
        if (c.state === "RETRY_WAIT") return (Date.parse(c.nextAttemptAt || "") || 0) <= now;
        if (c.state === "STALLED") return (!c.terminalStall) && (!!wide || (Date.parse(c.nextAttemptAt || "") || 0) <= now);
        return false;
      });
      if (!cand) return;
      attempted.add(cand.envelope.message_id);
      const qid = cand.envelope.crusherFor;
      try {
        await attemptDelivery(cand.envelope);
      } catch (e) { /* attemptDelivery accounts its own machinery errors */ }
      const after = await pbLoadState();
      const det = (after.detections || []).find((d) => d.envelope && d.envelope.message_id === cand.envelope.message_id);
      if (det && det.crusher && !det.crusherQLogged &&
          (det.crusher.state === "ACKNOWLEDGED" || det.crusher.state === "UNVERIFIED")) {
        det.crusherQLogged = true;
        pbLog(after, det.crusher.state === "ACKNOWLEDGED"
          ? `CRUSHER Q DELIVERED to Remmy's seat (flagged) — the question for Crusher (…${String(qid).slice(-6)}) is in her chat; the harness answers from there`
          : `CRUSHER Q sent to Remmy's seat but UNCONFIRMED — the question for Crusher (…${String(qid).slice(-6)}) may or may not be in her chat; it is not resent`);
        await pbSaveState(after);
      }
    }
  } finally {
    pbCrusherPumping = false;
  }
}

/* On resume (unpause) or a fresh registration, Ben's hand widens
 * the pump: held, stalled and not-yet-due letters all get their
 * attempt — his action IS the retry decision for letters the
 * machine parked. (V6.2: the sweep is the pump with its wide flag;
 * V6.1's separate sweep loop is retired.) */
async function sweepHeld() {
  await pumpQueue(true).catch(() => {});
}

/* A worker that wakes for any reason gives due letters their
 * attempt — self-healing between events. */
pumpQueue().catch(() => {});


/* ===== V0.15.0 — HUMAN COMMANDS FROM THE FACE (spec 3) =====
 * The panel ISSUES commands; the background validates and
 * executes them. Validation, in order: the sender tab must be
 * a registered seat tab (assign excepted); letter commands
 * apply only to that seat's own letters; the command must be
 * eligible for the record's state; repeats are idempotent.
 * Every accepted command appends an intervention to the
 * record. No command delivers synchronously — the pump and
 * the gate decide the moment, as for any letter. */
async function pbHandleCommand(msg, sender) {
  const tabId = sender.tab && sender.tab.id;
  if (tabId == null) return { ok: false, error: "no sender tab" };
  if (msg.kind === "pb-cmd-assign") {
    const seat = msg.seat === "alex" ? "alex" : "remmy";
    const st2 = await handleRegister(seat, sender.tab);
    return { ok: true, seat, face: pbFaceFor(st2, seat) };
  }
  const state = await pbLoadState();
  let seat = null;
  if (state.registrations) {
    for (const s of Object.keys(state.registrations)) {
      const r = state.registrations[s];
      if (r && r.tabId === tabId) { seat = s; break; }
    }
  }
  if (!seat) return { ok: false, identityUnavailable: true };
  if (msg.kind === "pb-cmd-disconnect") {
    delete state.registrations[seat];
    pbLog(state, `Disconnected ${seat.toUpperCase()} from the panel`);
    await pbSaveState(state);
    return { ok: true, seat: null };
  }
  if (msg.kind === "pb-cmd-bridge-pause" || msg.kind === "pb-cmd-bridge-resume") {
    const want = msg.kind === "pb-cmd-bridge-pause";
    if (state.paused !== want) {
      state.paused = want;
      pbLog(state, want ? "Bridge PAUSED by Ben (panel)" : "Bridge RESUMED by Ben (panel)");
      await pbSaveState(state);
      if (!want) sweepHeld().catch(() => {});
    }
    return { ok: true, face: pbFaceFor(state, seat) };
  }
  const det = pairDetection(state, msg.message_id);
  if (!det || !det.envelope || det.envelope.to !== seat || !det.crusher) {
    return { ok: false, error: "not a letter for this seat", face: pbFaceFor(state, seat) };
  }
  const c = det.crusher;
  const now = Date.now();
  const at = new Date(now).toISOString();
  const refuse = (why) => ({ ok: false, error: why, face: pbFaceFor(state, seat) });
  const intervene = (cmd) => {
    if (!Array.isArray(c.interventions)) c.interventions = [];
    c.interventions.push({ by: "ben", cmd, at, from: c.state });
  };
  if (msg.kind === "pb-cmd-letter-pause") {
    if (c.pausedAt) { /* idempotent */ }
    else if (c.state === "DELIVERING") {
      if (!c.pausePending) { c.pausePending = true; intervene("pause"); pbLog(state, `PAUSE ${det.envelope.from} → ${det.envelope.to}: Ben paused mid-attempt — it lands when the attempt settles`); }
    } else if (["GATED", "RETRY_WAIT", "STALLED", "VERIFIED", "HELD"].includes(c.state)) {
      c.pausedAt = at; intervene("pause");
      pbLog(state, `PAUSED ${det.envelope.from} → ${det.envelope.to}: Ben paused this letter`);
    } else return refuse("this letter cannot be paused now");
  } else if (msg.kind === "pb-cmd-letter-resume") {
    if (c.pausedAt) {
      const span = now - Date.parse(c.pausedAt);
      if (c.state === "RETRY_WAIT" && c.nextAttemptAt) c.nextAttemptAt = new Date(Date.parse(c.nextAttemptAt) + span).toISOString();
      if (c.state === "GATED" && c.gateSince) { c.gateSince = new Date(Date.parse(c.gateSince) + span).toISOString(); c.gateWake = true; }
      if (c.recovery) c.recovery.pausedTotalMs = (c.recovery.pausedTotalMs || 0) + span;
      c.pausedAt = null; intervene("resume");
      pbLog(state, `RESUMED ${det.envelope.from} → ${det.envelope.to}: Ben resumed this letter (its clocks shifted by the paused span)`);
    } else if (c.pausePending) {
      c.pausePending = false; intervene("resume");
    } else return refuse("this letter is not paused");
  } else if (msg.kind === "pb-cmd-letter-retry") {
    if (c.state !== "STOPPED") return refuse("only a letter that needs you can be tried again");
    intervene("retry");
    if (c.recovery) c.recovery.windowStart = at;
    c.stopReason = null;
    if (c.gateTimeoutPending) { c.gateTimeoutPending = false; c.gateTimeoutNotified = true; }
    pbCrusherTransition(c, "VERIFIED", "Ben's Try again — recovery re-entered, history intact", at);
    pbLog(state, `TRY AGAIN ${det.envelope.from} → ${det.envelope.to}: Ben revived the letter (its ${c.recovery ? c.recovery.failures : 0} failures stay on the record)`);
    const pair = state.pair;
    if (pair && pair.step === "failed-recoverable") {
      const fid = pair.failedWhich === "reply" ? pair.replyId : pair.callId;
      if (fid === msg.message_id) {
        pair.step = pair.failedWhich === "reply" ? "carry-reply" : "carry-call";
        pair.failedReason = null; pair.failedWhich = null;
        pair.parkedAt = null; pair.parkedDestTab = null;
      }
    }
  } else if (msg.kind === "pb-cmd-letter-abandon") {
    if (c.state === "ABANDONED") { /* idempotent: already let go — a no-op (spec V4) */ }
    else if (c.state === "DELIVERING" || c.state === "ACKNOWLEDGED" || c.state === "UNVERIFIED") {
      return refuse("this letter cannot be let go now");
    } else {
      intervene("abandon");
      c.abandonedBy = "ben";
      c.pausedAt = null; c.pausePending = false;
      pbCrusherTransition(c, "ABANDONED", "let go by Ben from the panel", at);
      pbLog(state, `LET GO ${det.envelope.from} → ${det.envelope.to}: Ben abandoned this letter — recorded as abandoned, never as delivered`);
    }
  } else {
    return { ok: false, error: "unknown command" };
  }
  await pbSaveState(state);
  if (msg.kind === "pb-cmd-letter-retry" || msg.kind === "pb-cmd-letter-resume") pumpQueue().catch(() => {});
  if (msg.kind === "pb-cmd-letter-abandon") advancePair().catch(() => {});
  const stF = await pbLoadState();
  await pbPushFaceToSeat(stF, seat);
  return { ok: true, face: pbFaceFor(stF, seat) };
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    try {
      if (msg.kind === "pb-register") {
        // Registration always comes from the popup for the ACTIVE tab.
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab) { sendResponse({ ok: false, error: "no active tab" }); return; }
        const state = await handleRegister(msg.role, tab);
        sweepHeld().catch(() => {});
        sendResponse({ ok: true, state });
      } else if (msg.kind === "pb-detection") {
        const res = await handleDetection(msg.envelope, sender.tab && sender.tab.id);
        sendResponse({ ok: true, ...res });
      } else if (msg.kind === "pb-capture-drop") {
        /* V0.12.1: the letterbox's drop reports land on the popup
         * log — the trace of every settled letter not carried. */
        const st = await pbLoadState();
        pbLog(st, `CAPTURE DROP ${msg.seat || "?"}: ${msg.reason || "not carried"} — "${String(msg.firstLine || "").slice(0, 60)}"`);
        await pbSaveState(st);
        sendResponse({ ok: true });
      } else if (msg.kind === "pb-get-state") {
        const st = await pbLoadState();
        /* V8 (0.8.0): tell the asking tab which seat BEN registered
         * it under, if any. The seat is Ben's popup assignment, not
         * the page's platform: content.js adopts yourSeat over its
         * adapter's built-in default, so any surface can sit in
         * either seat (a claude.ai tab as "alex"; tomorrow, a muse
         * tab as "alex"). The popup asks too — it has no tab, so
         * its yourSeat is simply null and ignored there. */
        let yourSeat = null;
        const myTabId = sender.tab && sender.tab.id;
        if (myTabId != null && st.registrations) {
          for (const seatName of Object.keys(st.registrations)) {
            const r = st.registrations[seatName];
            if (r && r.tabId === myTabId) { yourSeat = seatName; break; }
          }
        }
        sendResponse({ ok: true, state: st, yourSeat });
      } else if (msg.kind === "pb-generation-cleared") {
        /* V0.14.0 Mechanism A: the destination page's button left
         * its stop face. The sender tab's seat is the DESTINATION
         * seat; its GATED letters earn a re-check (gateWake) and
         * the pumps run. The attempt itself re-reads the button
         * before engaging anything — this message is a wake, not
         * a verdict. */
        const tabIdC = sender.tab && sender.tab.id;
        const stC = await pbLoadState();
        let seatC = null;
        if (tabIdC != null && stC.registrations) {
          for (const s of Object.keys(stC.registrations)) {
            const r = stC.registrations[s];
            if (r && r.tabId === tabIdC) { seatC = s; break; }
          }
        }
        let woke = false;
        if (seatC) {
          for (const d of stC.detections) {
            if (d.envelope && d.envelope.to === seatC && d.crusher && d.crusher.state === "GATED") {
              d.crusher.gateWake = true;
              woke = true;
            }
          }
        }
        if (woke) {
          await pbSaveState(stC);
          pumpQueue().catch(() => {});
          pumpCrusher(false).catch(() => {});
        }
        sendResponse({ ok: true, woke });
      } else if (msg.kind === "pb-panel-state") {
        /* V0.14.0 Mechanism B: a panel's pull. The asking tab is
         * answered ONLY with its own seat's ACTIVE views (plus a
         * still-owed GATE_TIMEOUT popup) — filtering happens here,
         * never in the panel. FAIL CLOSED: a tab no registration
         * names gets no records at all, only the identity flag. */
        const tabIdP = sender.tab && sender.tab.id;
        const stP = await pbLoadState();
        let seatP = null;
        if (tabIdP != null && stP.registrations) {
          for (const s of Object.keys(stP.registrations)) {
            const r = stP.registrations[s];
            if (r && r.tabId === tabIdP) { seatP = s; break; }
          }
        }
        if (!seatP) {
          sendResponse({ ok: false, identityUnavailable: true });
        } else {
          /* V0.15.0: the pull answers with the seat's whole
           * FACE (pbFaceFor) — same fail-closed filtering. */
          sendResponse({ ok: true, seat: seatP, face: pbFaceFor(stP, seatP) });
        }
      } else if (msg.kind === "pb-popup-shown") {
        /* V0.14.0 B6: the panel has shown the failure popup for
         * this message — the one notification is spent. The
         * STOPPED record itself is untouched (dismissal and
         * display bookkeeping never move the record). */
        const stS = await pbLoadState();
        const dS = stS.detections.find((x) => x.envelope && x.envelope.message_id === msg.message_id);
        if (dS && dS.crusher && dS.crusher.gateTimeoutPending) {
          dS.crusher.gateTimeoutPending = false;
          dS.crusher.gateTimeoutNotified = true;
          await pbSaveState(stS);
        }
        sendResponse({ ok: true });
      } else if (msg.kind === "pb-alert-raise") {
        /* V0.16.0 BRIDGE ALERT: a raise detected on Remmy's
         * surface (alert.js). The record is built HERE from the
         * reported fields (pbAlertRecord sanitises) — state is
         * never trusted from the page. Dedup is by alert ID; an
         * acknowledged alert never fires again. The chime is
         * claimed (latched) before any tab is told to play it:
         * one alert ID, one sound event, ever. */
        const stA = await pbLoadState();
        if (!Array.isArray(stA.alerts)) stA.alerts = [];
        const probeA = PB_ALERT.pbAlertRecord(msg.alert || {});
        let recA = PB_ALERT.pbAlertFind(stA.alerts, probeA.id);
        if (recA && recA.acked) { sendResponse({ ok: true, state: "acked" }); return; }
        if (!recA) {
          recA = probeA;
          stA.alerts.push(recA);
          stA.alerts = PB_ALERT.pbAlertTrim(stA.alerts);
          pbLog(stA, `ALERT ${recA.id} raised → ${recA.seat || "seat unknown"}: ${recA.headline}`);
        }
        const targetA = PB_ALERT.pbAlertTarget(stA.registrations, recA.seat);
        let chimeA = false;
        if (targetA.tabIds.length) chimeA = PB_ALERT.pbAlertClaimChime(recA);
        await pbSaveState(stA);
        let shownA = 0;
        for (let i = 0; i < targetA.tabIds.length; i++) {
          try {
            await chrome.tabs.sendMessage(targetA.tabIds[i], {
              kind: "pb-alert-show",
              alert: PB_ALERT.pbAlertPublic(recA, targetA.fallback),
              chime: chimeA && i === 0,
            });
            shownA++;
          } catch (e) { /* tab unreachable: its load-pull recovers the popup (without a second chime — the claim already latched) */ }
        }
        sendResponse({ ok: true, state: "open", fallback: targetA.fallback, tabs: targetA.tabIds.length, shown: shownA });
      } else if (msg.kind === "pb-alert-pending") {
        /* V0.16.0: a tab asks for its unacknowledged alerts —
         * the popup's persistence across reloads. Targeting is
         * recomputed against CURRENT registrations (a seat's
         * tab may have been reassigned since the raise). The
         * chime claim goes only to the primary target tab, and
         * only if no surface has claimed it yet. */
        const tabIdN = sender.tab && sender.tab.id;
        const stN = await pbLoadState();
        if (!Array.isArray(stN.alerts)) stN.alerts = [];
        const outN = [];
        if (tabIdN != null) {
          let dirtyN = false;
          for (const recN of stN.alerts) {
            if (!recN || recN.acked) continue;
            const tN = PB_ALERT.pbAlertTarget(stN.registrations, recN.seat);
            if (!tN.tabIds.includes(tabIdN)) continue;
            let chN = false;
            if (tN.tabIds[0] === tabIdN && PB_ALERT.pbAlertClaimChime(recN)) { chN = true; dirtyN = true; }
            outN.push({ alert: PB_ALERT.pbAlertPublic(recN, tN.fallback), chime: chN });
          }
          if (dirtyN) await pbSaveState(stN);
        }
        sendResponse({ ok: true, alerts: outN });
      } else if (msg.kind === "pb-alert-ack") {
        /* V0.16.0: Ben closed the popup. Acknowledgement —
         * never a resolution claim; the record itself is
         * untouched apart from the acked flag. The popup
         * clears on every registered tab. */
        const stK = await pbLoadState();
        if (!Array.isArray(stK.alerts)) stK.alerts = [];
        const recK = PB_ALERT.pbAlertFind(stK.alerts, msg.id);
        if (recK && !recK.acked) {
          recK.acked = true;
          pbLog(stK, `ALERT ${recK.id} acknowledged by Ben`);
          await pbSaveState(stK);
        }
        const tabsK = new Set();
        if (stK.registrations) {
          for (const sK of Object.keys(stK.registrations)) {
            const rK = stK.registrations[sK];
            if (rK && rK.tabId != null) tabsK.add(rK.tabId);
          }
        }
        for (const tidK of tabsK) {
          chrome.tabs.sendMessage(tidK, { kind: "pb-alert-clear", id: msg.id }).catch(() => {});
        }
        sendResponse({ ok: true });
      } else if (msg.kind === "pb-state-query") {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab) { sendResponse({ ok: false, error: "no active tab" }); return; }
        try {
          const r = await chrome.tabs.sendMessage(tab.id, { kind: "pb-state-query" });
          sendResponse({ ok: true, tabId: tab.id, page: r });
        } catch (e) {
          sendResponse({ ok: false, tabId: tab.id, error: String(e && e.message || e) });
        }
      } else if (msg.kind === "pb-selfcheck") {
        // Diagnostics: ask every open Muse/ChatGPT tab's content
        // script what its adapter sees on the live page.
        const tabs = await chrome.tabs.query({
          url: ["https://muse.ai/*", "https://chatgpt.com/*", "https://claude.ai/*", "https://gemini.google.com/*", "https://meta.ai/*", "https://www.meta.ai/*"],
        });
        const results = [];
        for (const t of tabs) {
          try {
            const r = await chrome.tabs.sendMessage(t.id, { kind: "pb-selfcheck" });
            results.push({ tabId: t.id, url: t.url, ok: !!(r && r.ok), selfcheck: r && r.selfcheck, error: r && r.error });
          } catch (e) {
            results.push({ tabId: t.id, url: t.url, ok: false, error: String(e && e.message || e) });
          }
        }
        sendResponse({ ok: true, selfchecks: results });
      } else if (msg.kind === "pb-pair-retry") {
        // V7: Ben's hand gives the pair's current letter a fresh
        // attempt (a new crusher record — his tap IS the retry
        // decision, as sweeps always were) and restores the
        // carry step if the pair had parked as failed-recoverable.
        const state = await pbLoadState();
        const pair = state.pair;
        if (pair) {
          const curId = pair.failedWhich === "reply" || pair.step === "carry-reply" ? pair.replyId : pair.callId;
          const det = pairDetection(state, curId);
          if (det) {
            det.crusher = pbCrusherRecord(det.envelope, det.at);
            /* A FAILED mark is terminal in the ledgers
             * (pbAlreadyDelivered reads deliveryFailedIds) —
             * Ben's explicit retry must lift it, or the fresh
             * record would be refused by the pump forever. The
             * lift is his decision, and it is logged below. */
            if (state.deliveryFailedIds) state.deliveryFailedIds = state.deliveryFailedIds.filter((x) => x !== curId);
            if (state.deliveryFailed && det.envelope) state.deliveryFailed = state.deliveryFailed.filter((x) => x !== det.envelope.fingerprint);
          }
          if (pair.step === "failed-recoverable") {
            pair.step = pair.failedWhich === "reply" ? "carry-reply" : "carry-call";
            pair.failedReason = null; pair.failedWhich = null;
            /* V0.12.1: Ben's hand also renews the auto-retry
             * budget — his retry is a fresh decision, and the
             * park stamps clear with it. */
            pair.autoRetries = 0; pair.parkedAt = null; pair.parkedDestTab = null;
          }
          pbLog(state, "PAIR RETRY by Ben — the current letter gets a fresh attempt");
          await pbSaveState(state);
          pumpQueue(true).catch(() => {});
        }
        sendResponse({ ok: true, state });
      } else if (msg.kind === "pb-pair-retire") {
        // V7: Ben retires the active pair from the popup. The
        // retirement is on the log; the buffered message (if
        // any) is promoted into the next pair.
        const state = await pbLoadState();
        if (state.pair) {
          retirePair(state, "retired by Ben from the popup");
          await pbSaveState(state);
          pumpQueue().catch(() => {});
        }
        sendResponse({ ok: true, state });
      } else if (typeof msg.kind === "string" && msg.kind.indexOf("pb-cmd-") === 0) {
        /* V0.15.0: the panel's human commands (spec section 3). */
        sendResponse(await pbHandleCommand(msg, sender));
      } else if (msg.kind === "pb-set-paused") {
        const state = await pbLoadState();
        state.paused = !!msg.paused;
        pbLog(state, state.paused ? "Bridge PAUSED by Ben" : "Bridge RESUMED by Ben");
        await pbSaveState(state);
        if (!state.paused) sweepHeld().catch(() => {});
        sendResponse({ ok: true, state });
      } else if (msg.kind === "pb-reset") {
        const state = pbDefaultState();
        pbLog(state, "Connections reset by Ben");
        await pbSaveState(state);
        sendResponse({ ok: true, state });
      } else {
        sendResponse({ ok: false, error: "unknown message kind" });
      }
    } catch (e) {
      sendResponse({ ok: false, error: String(e && e.message || e) });
    }
  })();
  return true; // async response
});

/* Registration honesty: if a registered tab closes or navigates away
 * from its conversation, the popup must say so (Blueprint §3C). */
chrome.tabs.onRemoved.addListener(async (tabId) => {
  const state = await pbLoadState();
  let changed = false;
  for (const role of ["remmy", "alex"]) {
    if (state.registrations[role] && state.registrations[role].tabId === tabId) {
      pbLog(state, `${role.toUpperCase()} tab closed — registration cleared`);
      state.registrations[role] = null;
      changed = true;
    }
  }
  if (changed) await pbSaveState(state);
});

/* V7 migration + resume, once per worker start. Migration: the
 * old queue's letters have no pair to belong to — they retire
 * unshipped, ON THE LOG, and the machine starts clean (the
 * letterbox's history absorption keeps the page from re-firing
 * them). Resume: a persisted pair in a carry step is picked up
 * by the pump above; this only puts its return on the record. */
(async () => {
  try {
    const state = await pbLoadState();
    if (!state.v7migrated) {
      const n = state.detections.length;
      state.detections = [];
      state.seenIds = [];
      state.fpToId = {};
      state.pair = null;
      state.bufferId = null;
      state.v7migrated = true;
      if (n) pbLog(state, `V7 migration: ${n} queued letter(s) from the old architecture retired unshipped — the pair machine starts clean; this line is their record`);
      await pbSaveState(state);
    } else if (state.pair && (state.pair.step === "carry-call" || state.pair.step === "carry-reply")) {
      pbLog(state, `V7: pair resumed after worker start — ${state.pair.from} → ${state.pair.to}, step ${state.pair.step}`);
      await pbSaveState(state);
    }
  } catch (e) { /* best-effort; routing guards its own state */ }
})();
