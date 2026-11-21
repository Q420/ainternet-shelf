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
  if (!state.pair) {
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
