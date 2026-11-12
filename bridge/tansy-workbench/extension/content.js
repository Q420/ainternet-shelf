"use strict";
/* Pulse Bridge — content script (v0.4, the letterbox).
 *
 * ONE content script; the platform knowledge lives in the adapter
 * (adapters/chatgpt.js / adapters/claude.js expose window.PB_ADAPTER).
 *
 * v0.4 replaces both earlier detectors with Alex's simplified
 * mechanism: watch the region, find the reserved marker, climb to
 * the enclosing bubble, verify the bubble is the assistant's, verify
 * the marker stands alone on a line in the bubble (the v0.12.0
 * delimiter rule — before v0.12.0 it had to be the first line),
 * wait for THAT bubble to stop changing, extract the letter the
 * marker delimits, hold one envelope.
 * (letterbox.js carries the mechanism; this file only wires it:
 * registration gating, the seen-ledger sync, envelope building, and
 * the popup's state query.)
 *
 * The v0.3.2 mutation witness and the v0.3.0 turn-capture loop are
 * retired: their files stay in the repo as evidence but are no
 * longer loaded (manifest), per Alex's "stop expanding the
 * diagnostics" ruling and Ben's build order, 2026-11-06.
 *
 * Detection produces a HELD envelope and hands it to the background
 * router, which dedups and records it. STAGE 3 (v0.5.0): this script
 * also receives pb-deliver for letters addressed to THIS seat's
 * conversation and performs the send through the adapter — only when
 * this tab is the registered seat and the bridge is unpaused, both
 * re-checked at delivery time in the background and here.
 */
(function () {
  const adapter = window.PB_ADAPTER;
  if (!adapter) return; // no adapter for this host — stay silent
  if (!window.PB_LETTERBOX) return; // letterbox missing — stay silent

  let enabled = false;
  let letterbox = null;
  /* COMBINED BUILD, Part A stream 2 (D1): the latest detection
   * token record the background issued this tab, refreshed on
   * every state round trip. The letterbox snapshots it when a
   * candidate first enters settle; this page NEVER fetches a
   * token at handoff time. */
  let currentTokenSnapshot = null;

  function safeGenerating(ad) {
    try { return !!ad.isGenerating(); } catch (e) { return false; }
  }

  /* COMBINED BUILD, Part B item 6: the send core's 45-second
   * generating defer reports through here — the background
   * records it on the in-flight letter and the panel face
   * shows the remaining time. Distinct from the fence's
   * 20-second recheck, which never travels this channel. */
  window.PB_DEFER_REPORT = (info) => {
    try {
      chrome.runtime.sendMessage({
        kind: "pb-defer-progress",
        elapsedMs: info.elapsedMs | 0,
        remainingMs: info.remainingMs | 0,
        maxMs: info.maxMs | 0,
        done: !!info.done,
      }).catch(() => {});
    } catch (e) { /* the defer itself never depends on reporting */ }
  };

  async function refreshEnabled() {
    try {
      const res = await chrome.runtime.sendMessage({ kind: "pb-get-state" });
      const state = res && res.state;
      if (!state) { enabled = false; return null; }
      /* V8 (0.8.0): the seat is Ben's registration, not this page's
       * platform. If the background says this tab is registered
       * under a seat, adopt it BEFORE the letterbox starts (the
       * letterbox reads adapter.seat live, so the adoption carries
       * into fingerprints, markers and the envelope's from). With
       * no registration naming this tab, the adapter's built-in
       * default stands — tonight's two surfaces behave exactly as
       * before. */
      if (res.yourSeat && res.yourSeat !== adapter.seat) {
        adapter.seat = res.yourSeat;
      }
      const reg = state.registrations[adapter.seat];
      // This tab speaks only if it IS the registered tab for its seat.
      enabled = !state.paused && !!reg;
      currentTokenSnapshot = res.detectionToken || null;
      return state;
    } catch (e) {
      enabled = false;
      return null;
    }
  }

  function startLetterbox(state) {
    if (letterbox) return;
    letterbox = window.PB_LETTERBOX.pbCreateLetterbox({
      adapter,
      seenSeed: (state && state.seen) || [],
      tokenSource: () => currentTokenSnapshot,
      onHandoff: ({ from, to, body, fingerprint, supersedesFingerprint, capture, tokenSnapshot }) => {
        if (!enabled) return;
        const envelope = PB.pbEnvelope({ from, to, body });
        // Keep the detector's fingerprint so background dedup and
        // the detector agree on what "the same message" means.
        envelope.fingerprint = fingerprint;
        // V6.3: lineage + capture evidence ride the envelope.
        if (supersedesFingerprint) envelope.supersedesFingerprint = supersedesFingerprint;
        if (capture) envelope.capture = capture;
        /* D1: the settle-start token snapshot rides unchanged. */
        if (tokenSnapshot) envelope.tokenSnapshot = tokenSnapshot;
        chrome.runtime.sendMessage({ kind: "pb-detection", envelope }).catch(() => {});
      },
      /* V0.12.1: capture drops (speaker verdict, twin, duplicate,
       * baseline history) are reported to the background, which
       * puts them on the popup log — a letter the letterbox
       * decided not to carry leaves a trace Ben can read. */
      onDrop: ({ reason, firstLine, seat }) => {
        chrome.runtime.sendMessage({ kind: "pb-capture-drop", reason, firstLine, seat }).catch(() => {});
      },
    });
    try { letterbox.start(); } catch (e) { letterbox = null; }
  }

  /* The popup asks this tab (via the background) what it sees. */
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg && msg.kind === "pb-state-query") {
      (async () => {
        let regTabId = null;
        try {
          const res = await chrome.runtime.sendMessage({ kind: "pb-get-state" });
          const reg = res && res.state && res.state.registrations[adapter.seat];
          regTabId = reg ? reg.tabId : null;
        } catch (e) { /* background unreachable — stays null */ }
        sendResponse({
          ok: true,
          seat: adapter.seat,
          platform: adapter.platform,
          enabled,
          registeredTabId: regTabId,
          messages: adapter.listBubbles ? adapter.listBubbles().length : 0,
          /* V0.19.1: the terminal readout — what the letterbox
           * sees in the newest message on this page right now. */
          retrieval: (letterbox && letterbox.peekNewest) ? letterbox.peekNewest() : null,
          generating: adapter.isGenerating ? !!safeGenerating(adapter) : false, // V6.1: the adapter's real signal (v0.4 hardcoded false — no detector by design; the deference gate now reads it)
          regionFound: !!(adapter.regionEl && adapter.regionEl()),
          turnChars: 0, // v0.4: no region text is read for detection
        });
      })();
      return true; // async response
    }
    if (msg && msg.kind === "pb-deliver") {
      (async () => {
        const st = await refreshEnabled();
        if (!enabled) {
          sendResponse({ ok: false, stage: "gating", error: "bridge paused or this tab is not the registered seat" });
          return;
        }
        if (!adapter.deliverText) {
          sendResponse({ ok: false, stage: "adapter", error: "adapter has no deliverText" });
          return;
        }
        try {
          /* COMBINED BUILD, Part B item 4: bind the composer
           * lease to this attempt's identity before anything
           * is engaged, typed or clicked; release it when the
           * delivery settles, and let a broken lease name the
           * failure. */
          if (msg.lease && typeof PB_SEND !== "undefined") {
            const acq = PB_SEND.pbLeaseAcquire(adapter, msg.lease);
            if (!acq.ok) {
              sendResponse({ ok: false, stage: "lease", error: acq.error });
              return;
            }
          }
          const r = await adapter.deliverText(String(msg.text || ""));
          const leaseFault = typeof PB_SEND !== "undefined" ? PB_SEND.pbLeaseRelease() : null;
          if (leaseFault && !(r && r.ok)) {
            sendResponse({ ok: false, stage: "lease", error: leaseFault });
            return;
          }
          // V6.1: forward the confirmation verdict + duplicate
          // count — the router's retry policy turns on them.
          // V0.11.0 P2: forward rollover evidence too — the router
          // records that the letter changed conversations.
          sendResponse(r && r.ok
            ? { ok: true, duplicates: (r && r.duplicates) || 0, rollover: (r && r.rollover) || undefined }
            : { ok: false, stage: (r && r.stage) || "deliver", verdict: (r && r.verdict) || undefined, error: (r && r.error) || "delivery failed" });
        } catch (e) {
          if (typeof PB_SEND !== "undefined") PB_SEND.pbLeaseRelease();
          sendResponse({ ok: false, stage: "deliver", error: String(e && e.message || e) });
        }
      })();
      return true; // async response
    }
    if (msg && msg.kind === "pb-selfcheck") {
      try {
        sendResponse({ ok: true, selfcheck: adapter.selfCheck ? adapter.selfCheck() : null });
      } catch (e) {
        sendResponse({ ok: false, error: String(e && e.message || e) });
      }
    }
    if (msg && msg.kind === "pb-generation-state") {
      /* V0.14.0 Mechanism A: the gate asks, this page answers —
       * the adapter's own button signal, nothing invented. A
       * surface that cannot report reliably answers "unknown",
       * and unknown never blocks (spec A3). */
      let s = "unknown";
      try {
        if (adapter.composerButtonState) s = adapter.composerButtonState();
        else if (adapter.isGenerating) s = adapter.isGenerating() ? "generating" : "ready";
      } catch (e) { s = "unknown"; }
      if (s !== "generating" && s !== "ready") s = "unknown";
      sendResponse({ ok: true, state: s });
    }
    if (msg && msg.kind === "pb-wait-state") {
      /* V0.15.0: the background pushes the seat's whole FACE.
       * The panel renders it verbatim — every string was
       * computed backstage from the spec's copy table. */
      if (msg.face) pbPanelSetFace(msg.face);
    }
    if (msg && msg.kind === "pb-station-state") {
      /* COMBINED BUILD, Part C: the background pushes the ONE
       * station's acknowledged state; this tab renders it as
       * host or mirror exactly as the view says. */
      if (msg.station) pbStationSetView(msg.station, msg.yourSeat);
    }
    return false;
  });

  /* ===== COMBINED BUILD, Part C — THE STATION OVERLAY.
   * One logical station, two rendered surfaces (Station Host
   * Design Note 01 as revised): this overlay renders the
   * background's acknowledged station state. In the HOST
   * window (the background's election, fail-closed) it carries
   * the owner controls; in the mirror it renders the same face
   * with NO controls and the plain line "acting from the other
   * window". The countdown is read off the background's
   * timestamps — this surface owns no timer, no lock, no
   * queue. The travel animation runs only while an item is in
   * TRANSIT (actually submitted) and never claims delivery. */
  const PB_STATION_CSS = `
  #pb-station { position: fixed; z-index: 2147483100; width: 320px; max-width: 94vw;
    background: rgba(13,16,26,.97); color: #e8eaf2; border: 1px solid rgba(140,150,255,.55);
    border-radius: 12px; font: 12px/1.45 -apple-system, "Segoe UI", Roboto, sans-serif;
    box-shadow: 0 10px 34px rgba(0,0,0,.55); user-select: none; transform: translate(-50%,-50%); }
  #pb-station .st-head { display: flex; align-items: center; gap: 8px; padding: 7px 10px;
    cursor: move; border-bottom: 1px solid rgba(140,150,255,.25); }
  #pb-station .st-title { font-size: 10px; letter-spacing: .09em; text-transform: uppercase; color: #9aa3c7; }
  #pb-station .st-face { margin-left: auto; font-family: ui-monospace, Menlo, Consolas, monospace; color: #9fe8c1; font-size: 12px; }
  #pb-station .st-body { padding: 8px 10px 10px; display: flex; flex-direction: column; gap: 7px; }
  #pb-station .st-route { font-weight: 600; }
  #pb-station .st-preview { color: #c6cbdf; white-space: pre-wrap; word-break: break-word; }
  #pb-station .st-timer { font-family: ui-monospace, Menlo, Consolas, monospace; color: #ffd479; }
  #pb-station .st-row { display: flex; gap: 6px; flex-wrap: wrap; }
  #pb-station button.st-btn { background: rgba(99,102,241,.18); color: #e8eaf2;
    border: 1px solid rgba(140,150,255,.5); border-radius: 6px; padding: 3px 9px; font-size: 11.5px; cursor: pointer; }
  #pb-station button.st-btn:hover { background: rgba(99,102,241,.35); }
  #pb-station textarea.st-append { width: 100%; box-sizing: border-box; min-height: 54px;
    background: rgba(255,255,255,.06); color: #e8eaf2; border: 1px solid rgba(140,150,255,.4);
    border-radius: 6px; padding: 6px; font: 12px/1.4 inherit; }
  #pb-station .st-mirror { color: #9aa3c7; font-style: italic; }
  #pb-station .st-outcome { font-family: ui-monospace, Menlo, Consolas, monospace; }
  #pb-station .st-chip { display: inline-block; padding: 2px 8px; border-radius: 999px;
    border: 1px solid rgba(140,150,255,.5); background: rgba(99,102,241,.15); }
  @keyframes pb-st-rtl { from { transform: translateX(70px); opacity: .2; } to { transform: translateX(-70px); opacity: 1; } }
  @keyframes pb-st-ltr { from { transform: translateX(-70px); opacity: .2; } to { transform: translateX(70px); opacity: 1; } }
  #pb-station .st-chip.rtl { animation: pb-st-rtl 1.1s ease-in-out infinite alternate; }
  #pb-station .st-chip.ltr { animation: pb-st-ltr 1.1s ease-in-out infinite alternate; }
  `;
  function pbStationEsc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  const pbStation = { root: null, view: null, seat: null, appendOpen: false, timerInt: null };

  function pbStationCmd(action, extra) {
    const v = pbStation.view;
    if (!v || !pbStation.seat) return Promise.resolve(null);
    return chrome.runtime.sendMessage(Object.assign({
      kind: "pb-station-cmd", action,
      pbId: v.current ? v.current.pbId : null,
      generation: v.generations ? v.generations[pbStation.seat] : null,
    }, extra || {})).catch(() => null);
  }

  function pbStationSetView(view, seat) {
    pbStation.view = view;
    pbStation.seat = seat || pbStation.seat;
    pbRenderStation();
  }

  function pbRenderStation() {
    const v = pbStation.view;
    const show = v && (v.current || v.activeItem ||
      (v.lastOutcome && Date.now() - Date.parse(v.lastOutcome.at || "") < 30000));
    if (!show) {
      if (pbStation.root) { pbStation.root.remove(); pbStation.root = null; }
      if (pbStation.timerInt) { clearInterval(pbStation.timerInt); pbStation.timerInt = null; }
      return;
    }
    if (!pbStation.root) {
      if (!document.getElementById("pb-station-style")) {
        const st = document.createElement("style");
        st.id = "pb-station-style";
        st.textContent = PB_STATION_CSS;
        document.documentElement.appendChild(st);
      }
      const root = document.createElement("div");
      root.id = "pb-station";
      document.documentElement.appendChild(root);
      pbStation.root = root;
      pbStationWireDrag(root);
    }
    const root = pbStation.root;
    const pos = v.position || { xPct: 50, yPct: 50 };
    root.style.left = pos.xPct + "%";
    root.style.top = pos.yPct + "%";
    const isHost = v.hostSeat && pbStation.seat && v.hostSeat === pbStation.seat;
    const cur = v.current;
    const faceWord = cur ? cur.face : (v.activeItem ? v.activeItem.face : (v.lastOutcome ? v.lastOutcome.outcome : ""));
    let html = '<div class="st-head"><span class="st-title">Station</span>' +
      '<span class="st-face">' + pbStationEsc(faceWord) + "</span></div><div class=\"st-body\">";
    if (v.activeItem) {
      const dir = v.activeItem.from === "remmy" ? "rtl" : "ltr";
      const arrow = v.activeItem.from === "remmy" ? "Remmy → Alex" : "Alex → Remmy";
      html += '<div><span class="st-chip ' + (v.activeItem.face === "TRANSIT" ? dir : "") + '">' +
        pbStationEsc(arrow) + " · " + pbStationEsc(v.activeItem.face.toLowerCase().replace(/-/g, " ")) + "</span></div>";
    }
    if (cur) {
      html += '<div class="st-route">' + pbStationEsc(pbSeatName(cur.from)) + " → " + pbStationEsc(pbSeatName(cur.to)) +
        (cur.indexId ? " · " + pbStationEsc(cur.indexId) : "") + "</div>";
      html += '<div class="st-preview">“' + pbStationEsc(cur.bodyPreview) + '”</div>';
      if (cur.face === "HELD") {
        html += cur.appendOpen
          ? '<div class="st-timer">timer paused — you are writing</div>'
          : '<div class="st-timer" data-st-countdown="' + pbStationEsc(cur.windowExpiresAt) + '"></div>';
      }
      if (cur.face === "QUEUED") html += "<div>queued — its window starts when the station frees</div>";
      if (v.queued) html += "<div>+" + v.queued + " more in the queue</div>";
      if (isHost && cur.face === "HELD") {
        if (pbStation.appendOpen) {
          html += '<textarea class="st-append" id="pb-st-append-text" placeholder="Append to the end — your words, under your name. The letter itself is never edited."></textarea>';
          html += '<div class="st-row"><button class="st-btn" data-st-act="commit">Append &amp; send</button>' +
            '<button class="st-btn" data-st-act="close">Back</button></div>';
        } else {
          html += '<div class="st-row">' +
            '<button class="st-btn" data-st-act="append">Append</button>' +
            '<button class="st-btn" data-st-act="push">Push through</button>' +
            '<button class="st-btn" data-st-act="cancel">Cancel</button></div>';
        }
      } else if (isHost && cur.face === "QUEUED") {
        html += '<div class="st-row"><button class="st-btn" data-st-act="cancel">Cancel</button></div>';
      }
    }
    if (!isHost && cur) html += '<div class="st-mirror">acting from the other window</div>';
    if (!cur && v.lastOutcome) {
      html += '<div class="st-outcome">' + pbStationEsc(v.lastOutcome.outcome) + "</div>";
    }
    html += "</div>";
    root.innerHTML = html;
    root.querySelectorAll("[data-st-act]").forEach((b) => {
      b.addEventListener("click", async () => {
        const act = b.getAttribute("data-st-act");
        if (act === "append") {
          const r = await pbStationCmd("append-open");
          if (r && r.ok) { pbStation.appendOpen = true; pbRenderStation(); }
        } else if (act === "close") {
          await pbStationCmd("append-close");
          pbStation.appendOpen = false;
          pbRenderStation();
        } else if (act === "commit") {
          const ta = document.getElementById("pb-st-append-text");
          const r = await pbStationCmd("append-commit", { segment: ta ? ta.value : "" });
          if (r && r.ok) pbStation.appendOpen = false;
          else if (r && r.error) { b.textContent = r.error; }
        } else if (act === "push") {
          await pbStationCmd("push-through");
        } else if (act === "cancel") {
          const target = cur || null;
          const r = await chrome.runtime.sendMessage({
            kind: "pb-station-cmd", action: "cancel",
            pbId: target ? target.pbId : (v.activeItem ? v.activeItem.pbId : null),
            generation: v.generations ? v.generations[pbStation.seat] : null,
          }).catch(() => null);
          if (r && !r.ok && r.error) b.textContent = r.error;
        }
      });
    });
    if (pbStation.timerInt) clearInterval(pbStation.timerInt);
    pbStation.timerInt = setInterval(() => {
      const el = pbStation.root && pbStation.root.querySelector("[data-st-countdown]");
      if (!el) return;
      const left = Math.max(0, Number(el.getAttribute("data-st-countdown")) - Date.now());
      el.textContent = "append window: " + (left / 1000).toFixed(1) + "s";
    }, 200);
  }

  function pbStationWireDrag(root) {
    let drag = null;
    root.addEventListener("mousedown", (ev) => {
      const head = ev.target.closest && ev.target.closest(".st-head");
      if (!head) return;
      drag = { dx: ev.clientX, dy: ev.clientY };
      ev.preventDefault();
    });
    window.addEventListener("mousemove", (ev) => {
      if (!drag || !pbStation.root) return;
      const xPct = Math.max(2, Math.min(98, (ev.clientX / window.innerWidth) * 100));
      const yPct = Math.max(2, Math.min(98, (ev.clientY / window.innerHeight) * 100));
      pbStation.root.style.left = xPct + "%";
      pbStation.root.style.top = yPct + "%";
      drag.xPct = xPct; drag.yPct = yPct;
    });
    window.addEventListener("mouseup", () => {
      if (!drag) return;
      const d = drag; drag = null;
      if (d.xPct != null) pbStationCmd("move", { xPct: d.xPct, yPct: d.yPct });
    });
  }

  /* ===== V0.14.0 Mechanism A (content half): the cleared watch.
   * The same button the receipt machinery watches, polled once a
   * second (cheap, adapter-agnostic): when it LEAVES its stop
   * face, tell the background once — the gate's letters earn
   * their re-check. An edge detector, not a state repeater. */
  let pbLastGen = null;
  setInterval(() => {
    let s = null;
    try {
      if (adapter.composerButtonState) s = adapter.composerButtonState();
      else if (adapter.isGenerating) s = adapter.isGenerating() ? "generating" : "ready";
    } catch (e) { s = null; }
    if (s && pbLastGen === "generating" && s !== "generating") {
      chrome.runtime.sendMessage({ kind: "pb-generation-cleared" }).catch(() => {});
    }
    if (s) pbLastGen = s;
  }, 1000);

  /* ===== V0.15.0: THE PANEL IS THE INTERFACE (spec 2-3).
   * Two forms. Collapsed: one live terminal-style line — the
   * face's word (idle / sending… / waiting / paused / needs
   * you / not a seat). Expanded: the control face — status
   * sentence, this tab's seat (assign / disconnect), bridge
   * pause / resume, live letters with their eligible controls,
   * and today's Earlier lines. The background computes every
   * string and every eligibility (pbFaceFor); the panel only
   * renders and, on Ben's click, issues the spec's commands.
   * The B6 gate-timeout popup still rides the face: a letter
   * whose face entry carries popup:true raises it, once. */
  const PB_PANEL_CSS = `
  #pb-wait-panel { position: fixed; right: 16px; bottom: 16px; z-index: 2147483000;
    width: 300px; max-width: 92vw; background: rgba(17,19,26,.96); color: #e8eaf2;
    border: 1px solid rgba(140,150,255,.45); border-radius: 10px;
    font: 12px/1.45 -apple-system, "Segoe UI", Roboto, sans-serif;
    box-shadow: 0 8px 30px rgba(0,0,0,.5); user-select: none; }
  #pb-wait-panel .pb-head { display: flex; align-items: center; gap: 8px;
    padding: 7px 10px; cursor: move; border-bottom: 1px solid rgba(140,150,255,.25); }
  #pb-wait-panel .pb-word { font-family: ui-monospace, Menlo, Consolas, monospace;
    font-size: 12px; color: #9fe8c1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  #pb-wait-panel .pb-word.pb-severe { color: #ffb3ab; }
  #pb-wait-panel .pb-title { margin-left: auto; font-size: 10px; letter-spacing: .08em;
    text-transform: uppercase; color: #9aa3c7; white-space: nowrap; }
  #pb-wait-panel .pb-toggle { background: none; border: 1px solid rgba(140,150,255,.4);
    color: #e8eaf2; border-radius: 6px; width: 20px; height: 20px; line-height: 1; cursor: pointer; flex: none; }
  #pb-wait-panel .pb-body { padding: 8px 10px 10px; display: flex; flex-direction: column; gap: 8px; }
  #pb-wait-panel .pb-status { font-size: 12.5px; }
  #pb-wait-panel .pb-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  #pb-wait-panel .pb-sec { border-top: 1px solid rgba(140,150,255,.18); padding-top: 7px;
    display: flex; flex-direction: column; gap: 6px; }
  #pb-wait-panel .pb-sec-title { font-size: 10px; letter-spacing: .08em; text-transform: uppercase; color: #9aa3c7; }
  #pb-wait-panel .pb-letter { display: flex; flex-direction: column; gap: 4px; }
  #pb-wait-panel .pb-earlier-line { color: #aab1cc; }
  #pb-wait-panel button.pb-btn { background: rgba(99,102,241,.18); color: #e8eaf2;
    border: 1px solid rgba(140,150,255,.5); border-radius: 6px; padding: 3px 9px;
    font-size: 11.5px; cursor: pointer; }
  #pb-wait-panel button.pb-btn:hover { background: rgba(99,102,241,.35); }
  #pb-wait-panel .pb-popup { border: 1px solid #ff8a75; background: rgba(80,26,18,.92);
    border-radius: 8px; padding: 8px 10px; display: flex; flex-direction: column; gap: 6px; }
  `;

  const pbPanel = {
    root: null, bodyEl: null, wordEl: null, face: null,
    identityBad: false, seat: null, collapsed: false,
    popupShown: new Set(), popupEl: null, x: null, y: null,
  };
  const PB_CMD_LABELS = { pause: "Pause", resume: "Resume", retry: "Try again", abandon: "Let it go" };
  const PB_CMD_KINDS = { pause: "pb-cmd-letter-pause", resume: "pb-cmd-letter-resume", retry: "pb-cmd-letter-retry", abandon: "pb-cmd-letter-abandon" };

  function pbSeatName(seat) { return seat === "alex" ? "Alex" : seat === "remmy" ? "Remmy" : String(seat || ""); }

  function pbPanelSetFace(face) {
    if (!face || !face.seat) return;
    if (pbPanel.seat && face.seat !== pbPanel.seat) return; // bound: never render another seat
    pbPanel.seat = face.seat;
    pbPanel.face = face;
    pbPanel.identityBad = false;
    pbRenderPanel();
  }

  function pbPanelCommand(msg) {
    chrome.runtime.sendMessage(msg).then((res) => {
      if (!res) return;
      if (res.face) { pbPanelSetFace(res.face); return; }
      if (res.ok && res.seat) { pbPanel.seat = res.seat; pbPanel.identityBad = false; if (res.face) pbPanelSetFace(res.face); return; }
      if ((res.ok && res.seat === null) || res.identityUnavailable) {
        pbPanel.identityBad = true; pbPanel.face = null; pbRenderPanel();
      }
    }).catch(() => { /* the face re-pulls on its tick */ });
  }

  function pbBtn(label, fn) {
    const b = document.createElement("button");
    b.className = "pb-btn";
    b.textContent = label;
    b.addEventListener("click", (ev) => { ev.stopPropagation(); fn(); });
    return b;
  }

  function pbShowGatePopup(letter) {
    if (!pbPanel.root || pbPanel.popupShown.has(letter.id)) return;
    pbPanel.popupShown.add(letter.id);
    const name = pbSeatName(pbPanel.seat);
    const el = document.createElement("div");
    el.className = "pb-popup";
    const t = document.createElement("div");
    t.textContent = "⏰ This letter was NOT delivered. " + name + " stayed busy past the five-minute limit, so no attempt was made. The letter is stopped — Try again or Let it go below, when you're ready.";
    const row = document.createElement("div");
    row.className = "pb-row";
    const btn = pbBtn("Dismiss", () => {
      el.remove();
      if (pbPanel.popupEl === el) pbPanel.popupEl = null;
    });
    row.appendChild(btn);
    el.appendChild(t); el.appendChild(row);
    pbPanel.bodyEl.prepend(el);
    pbPanel.popupEl = el;
    chrome.runtime.sendMessage({ kind: "pb-popup-shown", message_id: letter.id }).catch(() => {});
  }

  function pbRenderPanel() {
    if (!pbPanel.root) return;
    const face = pbPanel.face;
    pbPanel.wordEl.textContent = pbPanel.identityBad ? "not a seat" : face ? face.word : "…";
    pbPanel.wordEl.className = "pb-word" + (face && face.word === "needs you" ? " pb-severe" : "");
    const body = pbPanel.bodyEl;
    body.innerHTML = "";
    body.style.display = pbPanel.collapsed ? "none" : "";
    if (pbPanel.collapsed) return;
    if (pbPanel.identityBad || !face) {
      const line = document.createElement("div");
      line.className = "pb-status";
      line.textContent = "This tab is not a seat.";
      body.appendChild(line);
      const row = document.createElement("div");
      row.className = "pb-row";
      row.appendChild(pbBtn("Make this Remmy's seat", () => pbPanelCommand({ kind: "pb-cmd-assign", seat: "remmy" })));
      row.appendChild(pbBtn("Make this Alex's seat", () => pbPanelCommand({ kind: "pb-cmd-assign", seat: "alex" })));
      body.appendChild(row);
      return;
    }
    const status = document.createElement("div");
    status.className = "pb-status";
    status.textContent = face.sentence;
    body.appendChild(status);
    // seat section
    const seatSec = document.createElement("div");
    seatSec.className = "pb-sec";
    const seatRow = document.createElement("div");
    seatRow.className = "pb-row";
    const seatLine = document.createElement("span");
    seatLine.textContent = "This tab is " + pbSeatName(face.seat) + "'s seat.";
    seatRow.appendChild(seatLine);
    seatRow.appendChild(pbBtn("Disconnect", () => pbPanelCommand({ kind: "pb-cmd-disconnect" })));
    seatSec.appendChild(seatRow);
    const bridgeRow = document.createElement("div");
    bridgeRow.className = "pb-row";
    if (face.bridgePaused) {
      const bl = document.createElement("span"); bl.textContent = "The bridge is paused."; bridgeRow.appendChild(bl);
      bridgeRow.appendChild(pbBtn("Resume the bridge", () => pbPanelCommand({ kind: "pb-cmd-bridge-resume" })));
    } else {
      bridgeRow.appendChild(pbBtn("Pause the bridge", () => pbPanelCommand({ kind: "pb-cmd-bridge-pause" })));
    }
    seatSec.appendChild(bridgeRow);
    body.appendChild(seatSec);
    // letters
    for (const letter of face.letters || []) {
      const sec = document.createElement("div");
      sec.className = "pb-sec pb-letter";
      const s = document.createElement("div");
      s.textContent = letter.sentence;
      sec.appendChild(s);
      if (letter.controls && letter.controls.length) {
        const row = document.createElement("div");
        row.className = "pb-row";
        for (const ctl of letter.controls) {
          row.appendChild(pbBtn(PB_CMD_LABELS[ctl] || ctl, () =>
            pbPanelCommand({ kind: PB_CMD_KINDS[ctl], message_id: letter.id })));
        }
        sec.appendChild(row);
      }
      body.appendChild(sec);
      if (letter.popup) pbShowGatePopup(letter);
    }
    // earlier
    if (face.earlier && face.earlier.length) {
      const sec = document.createElement("div");
      sec.className = "pb-sec";
      const title = document.createElement("div");
      title.className = "pb-sec-title";
      title.textContent = "Earlier";
      sec.appendChild(title);
      for (const item of face.earlier) {
        const row = document.createElement("div");
        row.className = "pb-row";
        const l = document.createElement("span");
        l.className = "pb-earlier-line";
        l.textContent = item.line;
        row.appendChild(l);
        for (const ctl of item.controls || []) {
          row.appendChild(pbBtn(PB_CMD_LABELS[ctl] || ctl, () =>
            pbPanelCommand({ kind: PB_CMD_KINDS[ctl], message_id: item.id })));
        }
        sec.appendChild(row);
      }
      body.appendChild(sec);
    }
  }

  function pbCreatePanel() {
    if (pbPanel.root) return;
    if (typeof document === "undefined") return; // no DOM (fixtures, odd embeddings): no panel, no throw
    if (!document.body) { setTimeout(pbCreatePanel, 500); return; }
    if (!document.getElementById("pb-panel-style")) {
      const st = document.createElement("style");
      st.id = "pb-panel-style";
      st.textContent = PB_PANEL_CSS;
      document.head.appendChild(st);
    }
    const root = document.createElement("div");
    root.id = "pb-wait-panel";
    const head = document.createElement("div");
    head.className = "pb-head";
    const word = document.createElement("span");
    word.className = "pb-word";
    word.textContent = "…";
    const title = document.createElement("span");
    title.className = "pb-title";
    title.textContent = "Pulse Bridge";
    const toggle = document.createElement("button");
    toggle.className = "pb-toggle";
    toggle.textContent = "–";
    toggle.addEventListener("click", (ev) => {
      ev.stopPropagation();
      pbPanel.collapsed = !pbPanel.collapsed;
      toggle.textContent = pbPanel.collapsed ? "+" : "–";
      pbRenderPanel();
    });
    head.appendChild(word); head.appendChild(title); head.appendChild(toggle);
    const body = document.createElement("div");
    body.className = "pb-body";
    root.appendChild(head); root.appendChild(body);
    document.body.appendChild(root);
    pbPanel.root = root; pbPanel.bodyEl = body; pbPanel.wordEl = word;
    // Drag by the head (per-instance position only).
    let drag = null;
    head.addEventListener("mousedown", (ev) => {
      if (ev.target === toggle) return;
      drag = { dx: (ev.clientX || 0) - (pbPanel.x == null ? root.offsetLeft || 0 : pbPanel.x), dy: (ev.clientY || 0) - (pbPanel.y == null ? root.offsetTop || 0 : pbPanel.y) };
    });
    document.addEventListener("mousemove", (ev) => {
      if (!drag) return;
      const maxX = Math.max(0, (window.innerWidth || 0) - (root.offsetWidth || 0));
      const maxY = Math.max(0, (window.innerHeight || 0) - (root.offsetHeight || 0));
      pbPanel.x = Math.min(maxX, Math.max(0, (ev.clientX || 0) - drag.dx));
      pbPanel.y = Math.min(maxY, Math.max(0, (ev.clientY || 0) - drag.dy));
      root.style.left = pbPanel.x + "px";
      root.style.top = pbPanel.y + "px";
      root.style.right = "auto";
      root.style.bottom = "auto";
    });
    document.addEventListener("mouseup", () => { drag = null; });
    /* Binding: pulled at creation from THIS tab's registration,
     * immutable per seat for the instance's life (a face naming
     * another seat is refused in pbPanelSetFace). Fail closed:
     * no identity → the assign face, and no records ever. */
    const pull = () => chrome.runtime.sendMessage({ kind: "pb-panel-state" }).then((res) => {
      if (res && res.ok && res.face) { pbPanelSetFace(res.face); return; }
      pbPanel.identityBad = true; pbPanel.face = null; pbRenderPanel();
    }).catch(() => { pbPanel.identityBad = true; pbRenderPanel(); });
    pull();
    /* A slow re-pull keeps the line honest across events the
     * pushes might miss (registration from the popup, another
     * tab's commands). It changes nothing by itself. */
    setInterval(() => { if (pbPanel.root) pull(); }, 10000);
    pbRenderPanel();
  }

  refreshEnabled().then((state) => {
    if (enabled) startLetterbox(state);
    pbCreatePanel(); // V0.14.0: the panel lives on every seat page
    // Registration can arrive after load (Ben registers from the
    // popup): re-check on an interval and start when this tab
    // becomes the registered seat.
    setInterval(async () => {
      const was = enabled;
      const st = await refreshEnabled();
      if (enabled && !letterbox) startLetterbox(st);
      if (!pbPanel.root) pbCreatePanel();
      if (!enabled && was) { /* paused/unregistered: detector stays
        loaded but onHandoff is gated by `enabled` */ }
    }, 4000);
  });
})();
