"use strict";
/* Pulse Bridge — popup dashboard (Blueprint §3C, Stages 1–2).
 *
 * Shows seat registrations, pause state, recorded detections (Stage 2
 * proof — held, never sent) and the run log; sends registration /
 * pause / reset commands to the background router. Registration always
 * applies to the tab that was active when the popup opened.
 */

const $ = (sel, root) => (root || document).querySelector(sel);

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function fmtTime(iso) {
  try { return new Date(iso).toLocaleTimeString(); } catch (e) { return iso || ""; }
}

function render(state) {
  for (const role of ["remmy", "alex"]) {
    const box = $("#seat-" + role);
    const reg = state.registrations[role];
    const dot = $(".dot", box);
    const status = $(".status", box);
    const meta = $(".meta", box);
    if (reg) {
      dot.classList.add("on");
      status.innerHTML = "";
      status.appendChild(dot);
      status.appendChild(document.createTextNode("CONNECTED"));
      meta.textContent = (reg.title || reg.url || ("tab " + reg.tabId)) +
        " · registered " + fmtTime(reg.registeredAt);
    } else {
      dot.classList.remove("on");
      status.innerHTML = "";
      status.appendChild(dot);
      status.appendChild(document.createTextNode("NOT REGISTERED"));
      meta.textContent = "";
    }
  }

  $("#pauseBtn").textContent = state.paused ? "Resume bridge" : "Pause bridge";

  /* COMBINED BUILD, Part A (the D2 tells — the only new panel
   * items in this part): two minimum safety-status tells.
   * (1) A Stage 1 integrity fault exists. (2) Paused is told
   * apart from saved-and-verified: an unreconciled epoch
   * transition says so in plain words, and a clean pause says
   * that too. The fuller Stage 1 display is Part D work. */
  const s1box = $("#stage1box");
  if (s1box) {
    const s1 = state.stage1 || null;
    const tells = [];
    if (s1 && s1.integrityFault) {
      tells.push("⚠ Stage 1 integrity fault — part of the registration record failed its checks. Letters still flow; the record is not fully trusted.");
    }
    if (s1 && s1.unreconciled) {
      tells.push("⚠ This pause is NOT verified-saved: an epoch change could not be confirmed (" + (s1.unreconciled.why || "transition") + "). Resume stays held until it reconciles.");
    } else if (s1 && state.paused) {
      tells.push("Paused — and the pause is saved and verified.");
    }
    s1box.textContent = tells.join(" ");
    s1box.style.display = tells.length ? "" : "none";
  }

  /* V7 — THE PAIR: the whole state of the bridge in one glance.
   * One exchange, one step, plain words. */
  const pairBox = $("#pairbox");
  const findDet = (id) => (state.detections || []).find((d) => d.envelope && d.envelope.message_id === id);
  const carryWords = (det) => {
    if (!det || !det.crusher) return "waiting to be carried";
    const cs = det.crusher.state;
    if (cs === "ACKNOWLEDGED") return "confirmed delivered";
    if (cs === "UNVERIFIED") return "sent, unconfirmed";
    if (cs === "RETRY_WAIT") return "waiting to retry on its own";
    if (cs === "STALLED") return "stalled — a sweep or Retry gives it another attempt";
    if (cs === "FAILED") return "failed";
    return cs.toLowerCase().replace(/_/g, " ");
  };
  const pairLines = [];
  /* COMBINED BUILD, Part D — FIRST-RUN HONESTY (Plan 01
   * SS5.11): on an install where nothing has ever crossed,
   * say exactly that — what is running, what to do first,
   * and what is NOT yet proven — instead of an empty pair
   * box pretending to be a status. */
  const firstRun = !state.pair && !(state.detections || []).length;
  if (firstRun) {
    pairLines.push("The bridge is running — and nothing has crossed yet.");
    pairLines.push("No letter has been sent or received on this install, so delivery is UNPROVEN here. That is the honest starting line, not an error.");
    pairLines.push("To begin: open each seat's tab, and register it from this popup (one tab per seat). Then write a letter with its marker in a seat tab — the bridge carries it from there.");
  } else if (!state.pair) {
    pairLines.push("No active pair — watching for the newest message.");
  } else {
    const p = state.pair;
    const call = findDet(p.callId);
    const reply = p.replyId ? findDet(p.replyId) : null;
    if (p.step === "carry-call") {
      pairLines.push(`① CARRYING THE CALL — ${esc(p.from.toUpperCase())} → ${esc(p.to.toUpperCase())}: ${esc(carryWords(call))}`);
      if (call) pairLines.push(`“${esc(call.envelope.body.slice(0, 90))}${call.envelope.body.length > 90 ? "…" : ""}”`);
    } else if (p.step === "await-reply") {
      pairLines.push(`② CALL DELIVERED (${p.callOutcome === "UNVERIFIED" ? "sent, unconfirmed" : "confirmed"}) — WATCHING FOR ${esc(p.to.toUpperCase())}'S REPLY`);
    } else if (p.step === "carry-reply") {
      pairLines.push(`③ CARRYING THE REPLY — ${esc(p.to.toUpperCase())} → ${esc(p.from.toUpperCase())}: ${esc(carryWords(reply))}`);
      if (reply) pairLines.push(`“${esc(reply.envelope.body.slice(0, 90))}${reply.envelope.body.length > 90 ? "…" : ""}”`);
    } else if (p.step === "failed-recoverable") {
      pairLines.push(`✖ FAILED — RECOVERABLE: the ${esc(p.failedWhich || "letter")} could not be carried (${esc(p.failedReason || "see its trail")}). Nothing was erased — Retry it, or Retire the pair.`);
    }
  }
  if (state.bufferId) {
    const buf = findDet(state.bufferId);
    if (buf) pairLines.push(`BUFFER: one message waiting (${esc(buf.envelope.from.toUpperCase())} → ${esc(buf.envelope.to.toUpperCase())}) — it starts the next pair when this one retires.`);
  }
  pairBox.innerHTML = pairLines.map((l) => `<div>${l}</div>`).join("");
  $("#pairRetryBtn").style.display = state.pair ? "" : "none";
  $("#pairRetireBtn").style.display = state.pair ? "" : "none";

  /* COMBINED BUILD, Part D — HISTORY PARITY (Amendment 01
   * item 5; Ben's requirement, overriding Plan 01 SS5.9):
   * ONE shared exchange history, rendered from the same
   * background record whichever seat's popup Ben opens —
   * newest first, plain state words, the letter's number
   * (serial + Index ID) and its seal state. Not a second
   * ledger: the same detections the detail list below shows,
   * in the words Ben reads. */
  const histBox = $("#historybox");
  if (histBox) {
    const ackFor = (id) => ((state.stage1 && state.stage1.acks) || []).find((a) => a.message_id === id);
    const stateWords = (d) => {
      if (d.stationFace) return d.stationFace.toLowerCase().replace(/-/g, " ");
      const cs = d.crusher && d.crusher.state;
      switch (cs) {
        case "ACKNOWLEDGED": return "delivered";
        case "UNVERIFIED": return "sent, unconfirmed";
        case "DELIVERING": return "sending now";
        case "GATED": return "held by the fence";
        case "HELD": return "held";
        case "RETRY_WAIT": return "waiting to retry";
        case "STALLED": return "stopped — needs a hand";
        case "FAILED": return "failed";
        case "STOPPED": return "stopped";
        case "ABANDONED": return "let go";
        default: return "waiting to be carried";
      }
    };
    const sealWords = (d) => {
      const c = d.completeness;
      if (!c) return "";
      if (c.status === "COMPLETE" || c.status === "REPAIRED") return " · sealed whole";
      if (c.status === "INCOMPLETE" || c.status === "MALFORMED" || c.status === "CONFLICT") return " · seal broken — held apart";
      return "";
    };
    const dets = (state.detections || []).slice().reverse().slice(0, 8);
    histBox.innerHTML = dets.length ? dets.map((d) => {
      const e = d.envelope || {};
      const ack = ackFor(e.message_id);
      const num = (d.serial != null ? "#" + d.serial : "no number yet") +
        (ack && ack.indexId ? " · " + esc(ack.indexId) : "");
      return "<div>" + esc(num) + " — " + esc((e.from || "?").toUpperCase()) + " → " +
        esc((e.to || "?").toUpperCase()) + " · " + esc(stateWords(d)) + esc(sealWords(d)) + "</div>";
    }).join("") : '<div class="empty">Nothing has crossed yet.</div>';
  }

  const detBox = $("#detections");
  if (!state.detections.length) {
    detBox.innerHTML = '<div class="empty">Nothing detected yet.</div>';
  } else {
    detBox.innerHTML = state.detections.slice().reverse().map((d) => {
      const e = d.envelope;
      const body = e.body.length > 220 ? e.body.slice(0, 220) + "…" : e.body;
      let status = "HELD — awaiting delivery conditions";
      if (d.crusher && d.crusher.state) {
        const c = d.crusher;
        const note = c.trail && c.trail.length ? (c.trail[c.trail.length - 1].note || "") : "";
        status = "CRUSHER: " + c.state;
        if (c.attempts) status += " · attempts: " + c.attempts;
        if (c.absenceRetries) status += " · absence retries: " + c.absenceRetries;
        if (e.message_id) status += " · id …" + e.message_id.slice(-6);
        if (note) status += " · " + note;
        if (c.state === "ACKNOWLEDGED") status += " — receipt confirmed";
        if (c.state === "UNVERIFIED") status += " — sent, but unconfirmed (absence was not established, so no retry)";
        if (c.state === "FAILED") status += " — final";
        if (c.state === "STALLED" && c.terminalStall) status += " — proven-absence retries exhausted; evidence preserved (Ben's hand to move it)";
        else if (c.state === "STALLED") status += " — a later sweep retries when the destination returns";
        if (c.state === "HELD") status += " — waits for the bridge to resume";
        if (c.state === "RETRY_WAIT") status += " — waiting for its next attempt; it retries on its own and the bridge is free meanwhile";
      } else if (d.delivery && d.delivery.status === "delivered") {
        status = "DELIVERED " + fmtTime(d.delivery.at) + " — confirmed in the destination conversation";
      } else if (d.delivery && d.delivery.status === "failed") {
        status = "DELIVERY FAILED " + fmtTime(d.delivery.at) + " — " + (d.delivery.reason || "") + " (not retried automatically)";
      }
      // V6.3: lineage + capture evidence, on any row carrying them.
      if (d.supersededBy) status += " · ↩ SUPERSEDED by …" + String(d.supersededBy).slice(-6);
      if (e.supersedesId) status += " · ⤳ completes …" + String(e.supersedesId).slice(-6);
      if (e.capture) status += " · capture: " + e.capture.observations + " obs · verified " + e.capture.verifyMode + " · " + e.capture.dispatchLength + " chars";
      return '<div class="det"><b>' + esc(e.from.toUpperCase()) + " → " +
        esc(e.to.toUpperCase()) + "</b> · " + esc(fmtTime(d.at)) +
        "<br>" + esc(body) + "<br><i>" + esc(status) + "</i></div>";
    }).join("");
  }

  const logBox = $("#log");
  if (!state.log.length) {
    logBox.innerHTML = '<div class="empty">—</div>';
  } else {
    logBox.innerHTML = state.log.slice().reverse().map((l) =>
      "<div>" + esc(fmtTime(l.at)) + " — " + esc(l.text) + "</div>").join("");
  }
}

async function refresh() {
  const res = await chrome.runtime.sendMessage({ kind: "pb-get-state" });
  if (res && res.ok) render(res.state);
  refreshLive();
  refreshDiag();
}

async function refreshLive() {
  const box = $("#livestate");
  try {
    const res = await chrome.runtime.sendMessage({ kind: "pb-state-query" });
    if (!res || !res.ok || !res.page) {
      box.innerHTML = '<div class="empty">The active tab is not a bridge page (or its content script is not loaded — reload the tab).</div>';
      return;
    }
    const p = res.page;
    const lines = [];
    lines.push("seat: " + esc(p.seat) + " · platform: " + esc(p.platform));
    lines.push("this tab id: " + esc(res.tabId) + " · registered tab id: " +
      esc(p.registeredTabId == null ? "none" : p.registeredTabId));
    lines.push("DETECTION IN THIS TAB: " +
      (p.enabled ? "LIVE" : "OFF — this tab is not the registered tab for its seat, or the bridge is paused"));
    lines.push("message bubbles on page: " + esc(p.messages) +
      " \u00b7 letterbox armed in this tab: " + (p.enabled ? "yes" : "no"));
    /* V0.19.1 TERMINAL READOUT (Ben's tap, 2026-11-11): the
     * newest message as retrieval sees it — its exact first
     * line, and the marker verdict. Plain lines, no dump. */
    const r = p.retrieval;
    if (r && r.empty) {
      lines.push("&gt; newest message: (no messages on this page yet)");
    } else if (r) {
      lines.push("&gt; newest message: &quot;" + esc(r.firstLine || "") + "&quot;");
      if (r.marker && r.cleanLine) {
        lines.push("&gt; marker: FOUND \u2014 " + esc(r.marker) + " \u00b7 a letter; the letterbox carries it");
      } else if (r.marker) {
        lines.push("&gt; marker: in the text but NOT a clean line \u2014 ignored");
      } else {
        lines.push("&gt; marker: NOT FOUND \u2014 not a letter; ignored");
      }
    }
    box.innerHTML = '<div class="det">' + lines.join("<br>") + "</div>";
  } catch (e) {
    box.innerHTML = '<div class="empty">Live state unavailable.</div>';
  }
}

function renderDiag(selfchecks) {
  const box = $("#diag");
  if (!selfchecks || !selfchecks.length) {
    box.innerHTML = '<div class="empty">No Muse or ChatGPT tab answered. Open one, reload it if the extension was just (re)loaded, then reopen this popup.</div>';
    return;
  }
  box.innerHTML = selfchecks.map((r) => {
    if (!r.ok || !r.selfcheck) {
      return '<div class="det"><b>NO ANSWER</b> — ' + esc(r.url || "") +
        "<br>" + esc(r.error || "content script not reachable") + "</div>";
    }
    const sc = r.selfcheck;
    if (sc.sampleTree) {
      const shown = {
        matched: sc.matched, counts: sc.counts,
        columnMarker: sc.columnMarker,
        sampleTree: sc.sampleTree, scan: sc.scan,
        probe: sc.probe, structural: sc.structural,
      };
      return '<div class="det"><b>' + esc(sc.platform.toUpperCase()) + "</b> · " +
        esc(sc.title || "") + '<div class="mono">' +
        esc(JSON.stringify(shown, null, 1)) +
        "</div></div>";
    }
    const lines = [];
    lines.push("<b>" + esc(sc.platform.toUpperCase()) + "</b> · " + esc(sc.title || ""));
    lines.push("messages match: " + esc(sc.matched.messages || "NONE"));
    lines.push("composer match: " + esc(sc.matched.composer || "NONE"));
    lines.push("composer NAME (Crusher): " +
      esc(sc.composerByName ? "FOUND — \"" + sc.composerName + "\"" : "NOT FOUND — structure fallback only"));
    for (const group of ["messages", "composer", "stop", "send"]) {
      const parts = Object.entries(sc.counts[group])
        .map(([sel, n]) => esc(sel) + " ×" + n);
      lines.push(esc(group) + ": " + parts.join(" · "));
    }
    return '<div class="det">' + lines.join("<br>") + "</div>";
  }).join("");
}

async function refreshDiag() {
  try {
    const res = await chrome.runtime.sendMessage({ kind: "pb-selfcheck" });
    if (res && res.ok) renderDiag(res.selfchecks);
  } catch (e) { /* diagnostics are best-effort */ }
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-register]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await chrome.runtime.sendMessage({ kind: "pb-register", role: btn.dataset.register });
      refresh();
    });
  });
  $("#pauseBtn").addEventListener("click", async () => {
    const res = await chrome.runtime.sendMessage({ kind: "pb-get-state" });
    const paused = res && res.state ? res.state.paused : false;
    await chrome.runtime.sendMessage({ kind: "pb-set-paused", paused: !paused });
    refresh();
  });
  $("#resetBtn").addEventListener("click", async () => {
    await chrome.runtime.sendMessage({ kind: "pb-reset" });
    refresh();
  });
  $("#pairRetryBtn").addEventListener("click", async () => {
    await chrome.runtime.sendMessage({ kind: "pb-pair-retry" });
    refresh();
  });
  $("#pairRetireBtn").addEventListener("click", async () => {
    await chrome.runtime.sendMessage({ kind: "pb-pair-retire" });
    refresh();
  });
  refresh();
});
