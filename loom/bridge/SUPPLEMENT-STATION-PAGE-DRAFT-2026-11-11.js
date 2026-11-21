"use strict";
/* Pulse Bridge — THE HELD-MESSAGE STATION (v0.19.0).
 *
 * Ben's design, refined on the fake demo he approved 2026-11-11:
 * every letter in transit stops at one station, centre screen,
 * floating over the top of whichever seat tab Ben is looking at —
 * the station belongs to neither tab. While a letter is held he
 * gets a 7.5-second window: APPEND adds his words at the end of
 * the letter (the seat's own words are never editable, by anyone,
 * in any state) and PUSH THROUGH sends it now. Clicking Append
 * stops the clock while he writes. When the letter is pushed
 * through, the message and its buttons leave the station — it has
 * been sent. The end state stays on the station's face: DELIVERED
 * or SENT-UNCONFIRMED, never silently vanished.
 *
 * This file is the PAGE side only: it renders the station and
 * reports Ben's actions to the background (pb-station-* kinds).
 * The hold itself lives in the background (background.js,
 * pbStationGate), inside attemptDelivery, ahead of the fence.
 * Exactly one letter owns the window at a time (Ben's window
 * lock); later letters queue, and their clocks have not started.
 *
 * Direction follows Ben's real layout: Alex's tab sits on the
 * LEFT, Remmy's on the RIGHT — a letter to Alex travels left, a
 * letter to Remmy travels right.
 */
(function () {
  if (typeof chrome === "undefined" || !chrome.runtime || !chrome.runtime.sendMessage) return;
  if (window.__pbStationMounted) return;
  window.__pbStationMounted = true;

  var WINDOW_MS = 7500;
  var view = { active: null, lastOutcome: null, queued: 0 };
  var appendOpenLocal = false;
  var tickTimer = null;

  var CSS = [
    "#pb-station{position:fixed;z-index:2147483000;width:300px;max-width:calc(100vw - 24px);",
    "background:rgba(13,18,46,.92);border:1px solid rgba(148,163,255,.5);border-radius:12px;",
    "backdrop-filter:blur(6px);box-shadow:0 12px 38px rgba(0,0,0,.55),0 0 24px rgba(124,108,255,.28);",
    "color:#e6eaff;font:13px/1.45 system-ui,-apple-system,'Segoe UI',sans-serif;padding:10px 12px;display:none}",
    "#pb-station .pb-s-head{display:flex;justify-content:space-between;align-items:center;cursor:grab;",
    "font-size:11px;letter-spacing:.1em;font-weight:700;color:#aab4ff;user-select:none;touch-action:none}",
    "#pb-station .pb-s-head:active{cursor:grabbing}",
    "#pb-station .pb-s-state{font-size:11px;font-weight:700;letter-spacing:.05em;padding:2px 7px;border-radius:999px;",
    "background:rgba(148,163,255,.18);color:#cfd6ff;white-space:nowrap}",
    "#pb-station .pb-s-state.held{background:rgba(250,204,21,.2);color:#fde68a}",
    "#pb-station .pb-s-state.delivered{background:rgba(52,211,153,.2);color:#6ee7b7}",
    "#pb-station .pb-s-state.unconfirmed{background:rgba(251,146,60,.22);color:#fdba74}",
    "#pb-station .pb-s-dest{margin-top:7px;font-size:16px;font-weight:800;letter-spacing:.03em;color:#67e8f9}",
    "#pb-station .pb-s-from{font-size:11px;color:#aab4ff;margin-top:2px}",
    "#pb-station .pb-s-msg{margin-top:7px;white-space:pre-wrap;word-break:break-word;max-height:180px;overflow:auto}",
    "#pb-station .pb-s-count{height:5px;border-radius:999px;background:rgba(148,163,255,.18);margin-top:10px;overflow:hidden}",
    "#pb-station .pb-s-count>div{height:100%;width:100%;background:linear-gradient(90deg,#67e8f9,#a78bfa);transform-origin:left}",
    "#pb-station .pb-s-num{font-size:11px;color:#aab4ff;margin-top:4px;min-height:14px}",
    "#pb-station .pb-s-actions{display:flex;gap:6px;margin-top:8px}",
    "#pb-station button{flex:1;appearance:none;border-radius:8px;padding:7px 6px;font-size:12.5px;cursor:pointer;",
    "border:1px solid rgba(148,163,255,.5);background:rgba(148,163,255,.12);color:#e6eaff;font-weight:600}",
    "#pb-station button.push{background:linear-gradient(90deg,#67e8f9,#a78bfa);color:#0a0f2e;border-color:transparent}",
    "#pb-station button:disabled{opacity:.4;cursor:default}",
    "#pb-station .pb-s-appendbox{margin-top:8px;display:none}",
    "#pb-station textarea{width:100%;box-sizing:border-box;min-height:54px;border-radius:8px;",
    "border:1px solid rgba(148,163,255,.5);background:rgba(6,8,24,.7);color:#e6eaff;padding:7px;",
    "font:13px/1.45 inherit;resize:vertical}",
    "#pb-station .pb-s-queue{margin-top:7px;font-size:11.5px;color:#fde68a}",
    "#pb-station .pb-s-outcome{display:flex;justify-content:space-between;align-items:center;gap:8px}",
    "#pb-station .pb-s-dismiss{flex:0 0 auto;padding:2px 9px}"
  ].join("");

  var style = document.createElement("style");
  style.textContent = CSS;
  document.documentElement.appendChild(style);

  var root = document.createElement("div");
  root.id = "pb-station";
  root.innerHTML =
    '<div class="pb-s-head" id="pb-s-drag"><span>HELD MESSAGE</span><span class="pb-s-state" id="pb-s-state">IDLE</span></div>' +
    '<div id="pb-s-hold">' +
      '<div class="pb-s-dest" id="pb-s-dest"></div>' +
      '<div class="pb-s-from" id="pb-s-from"></div>' +
      '<div class="pb-s-msg" id="pb-s-msg"></div>' +
      '<div class="pb-s-count"><div id="pb-s-bar"></div></div>' +
      '<div class="pb-s-num" id="pb-s-num"></div>' +
      '<div class="pb-s-queue" id="pb-s-queue" style="display:none"></div>' +
      '<div class="pb-s-actions" id="pb-s-actions">' +
        '<button type="button" id="pb-s-append">Append</button>' +
        '<button type="button" class="push" id="pb-s-push">Push through</button>' +
      '</div>' +
      '<div class="pb-s-appendbox" id="pb-s-appendbox">' +
        '<textarea id="pb-s-appendtext" placeholder="Your words, added at the end. Their words above never change."></textarea>' +
        '<div class="pb-s-actions">' +
          '<button type="button" class="push" id="pb-s-commit">Commit append &amp; send</button>' +
          '<button type="button" id="pb-s-back">Back</button>' +
        '</div>' +
      '</div>' +
    '</div>' +
    '<div class="pb-s-outcome" id="pb-s-outcome" style="display:none">' +
      '<span id="pb-s-outcometext"></span>' +
      '<button type="button" class="pb-s-dismiss" id="pb-s-dismiss">Dismiss</button>' +
    '</div>';
  document.documentElement.appendChild(root);

  var el = function (id) { return document.getElementById(id); };
  var stateEl = el("pb-s-state"), destEl = el("pb-s-dest"), fromEl = el("pb-s-from"),
      msgEl = el("pb-s-msg"), barEl = el("pb-s-bar"), numEl = el("pb-s-num"),
      queueEl = el("pb-s-queue"), holdEl = el("pb-s-hold"), outcomeEl = el("pb-s-outcome"),
      outcomeText = el("pb-s-outcometext"), appendBox = el("pb-s-appendbox"),
      appendText = el("pb-s-appendtext"), appendBtn = el("pb-s-append"), pushBtn = el("pb-s-push");

  function seatName(seat) { return seat === "alex" ? "ALEX" : seat === "remmy" ? "REMMY" : String(seat || "?").toUpperCase(); }

  function placeDefault() {
    root.style.left = Math.max(8, (window.innerWidth - 300) / 2) + "px";
    root.style.top = "70px";
  }
  try {
    chrome.storage.local.get(["pbStationPos"], function (r) {
      var p = r && r.pbStationPos;
      if (p && typeof p.left === "number") { root.style.left = p.left + "px"; root.style.top = p.top + "px"; }
      else placeDefault();
    });
  } catch (e) { placeDefault(); }

  (function () {
    var head = el("pb-s-drag"), drag = null;
    head.addEventListener("pointerdown", function (e) {
      var r = root.getBoundingClientRect();
      drag = { dx: e.clientX - r.left, dy: e.clientY - r.top };
      e.preventDefault();
    });
    window.addEventListener("pointermove", function (e) {
      if (!drag) return;
      var x = Math.max(0, Math.min(e.clientX - drag.dx, window.innerWidth - root.offsetWidth));
      var y = Math.max(0, Math.min(e.clientY - drag.dy, window.innerHeight - root.offsetHeight));
      root.style.left = x + "px"; root.style.top = y + "px";
    });
    window.addEventListener("pointerup", function () {
      if (!drag) return; drag = null;
      try { chrome.storage.local.set({ pbStationPos: { left: parseInt(root.style.left, 10), top: parseInt(root.style.top, 10) } }); } catch (e) {}
    });
  })();

  function stopTick() { if (tickTimer) { clearInterval(tickTimer); tickTimer = null; } }

  function render() {
    var a = view.active;
    if (!a) {
      stopTick();
      appendOpenLocal = false;
      appendBox.style.display = "none";
      if (view.lastOutcome) {
        root.style.display = "block";
        holdEl.style.display = "none";
        outcomeEl.style.display = "flex";
        var o = view.lastOutcome;
        stateEl.textContent = o.outcome;
        stateEl.className = "pb-s-state " + (o.outcome === "DELIVERED" ? "delivered" : "unconfirmed");
        outcomeText.textContent = seatName(o.from) + " \u2192 " + seatName(o.to) + " \u2014 " + o.outcome.toLowerCase().replace(/-/g, " ");
      } else {
        root.style.display = "none";
      }
      return;
    }
    root.style.display = "block";
    holdEl.style.display = "block";
    outcomeEl.style.display = "none";
    destEl.textContent = a.to === "alex" ? "\u2190 TO: ALEX" : a.to === "remmy" ? "TO: REMMY \u2192" : "TO: " + seatName(a.to);
    fromEl.textContent = "from " + seatName(a.from) + " \u00b7 " + (a.message_id || "");
    if (!appendOpenLocal) msgEl.textContent = a.body || "";
    if (a.appendOpen) {
      stateEl.textContent = "APPEND OPEN";
      stateEl.className = "pb-s-state held";
      appendBox.style.display = "block";
      var rem = typeof a.remainingMs === "number" ? a.remainingMs : 0;
      barEl.style.transform = "scaleX(" + Math.max(0, rem / WINDOW_MS) + ")";
      numEl.textContent = "Timer stopped \u2014 the window is yours while you write.";
      stopTick();
    } else {
      stateEl.textContent = "HELD";
      stateEl.className = "pb-s-state held";
      appendBox.style.display = "none";
      stopTick();
      tickTimer = setInterval(function () {
        var left = a.endsAt - Date.now();
        if (left <= 0) {
          barEl.style.transform = "scaleX(0)";
          numEl.textContent = "Window closed \u2014 sending\u2026";
          stopTick();
          pull();
          return;
        }
        barEl.style.transform = "scaleX(" + (left / WINDOW_MS) + ")";
        numEl.textContent = (left / 1000).toFixed(1) + "s left in the append window";
      }, 60);
    }
    if (view.queued > 0) {
      queueEl.style.display = "block";
      queueEl.textContent = view.queued + " more letter(s) queued behind this one \u2014 their clocks have not started.";
    } else queueEl.style.display = "none";
    appendBtn.disabled = !!a.appendOpen;
    pushBtn.disabled = false;
  }

  function pull() {
    try {
      chrome.runtime.sendMessage({ kind: "pb-station-get" }, function (res) {
        if (res && res.ok && res.view) { view = res.view; if (!view.active) appendOpenLocal = false; render(); }
      });
    } catch (e) {}
  }

  appendBtn.addEventListener("click", function () {
    if (!view.active) return;
    appendOpenLocal = true;
    chrome.runtime.sendMessage({ kind: "pb-station-append-open", message_id: view.active.message_id }, function () { pull(); });
    appendBox.style.display = "block";
    appendText.focus();
  });
  el("pb-s-back").addEventListener("click", function () {
    if (!view.active) return;
    appendOpenLocal = false;
    chrome.runtime.sendMessage({ kind: "pb-station-append-cancel", message_id: view.active.message_id }, function () { pull(); });
  });
  el("pb-s-commit").addEventListener("click", function () {
    if (!view.active) return;
    var v = appendText.value.replace(/^\s+|\s+$/g, "");
    appendOpenLocal = false;
    appendText.value = "";
    chrome.runtime.sendMessage({ kind: "pb-station-append-commit", message_id: view.active.message_id, text: v }, function () { pull(); });
  });
  pushBtn.addEventListener("click", function () {
    if (!view.active) return;
    appendOpenLocal = false;
    chrome.runtime.sendMessage({ kind: "pb-station-push", message_id: view.active.message_id }, function () { pull(); });
  });
  el("pb-s-dismiss").addEventListener("click", function () {
    chrome.runtime.sendMessage({ kind: "pb-station-dismiss" }, function () { view.lastOutcome = null; render(); });
  });

  chrome.runtime.onMessage.addListener(function (msg) {
    if (msg && msg.kind === "pb-station-state" && msg.view) {
      view = msg.view;
      if (!view.active) appendOpenLocal = false;
      render();
    }
  });

  pull();
  setInterval(function () { if (view.active) pull(); }, 4000);
})();
