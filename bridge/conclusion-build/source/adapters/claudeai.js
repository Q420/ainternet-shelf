"use strict";
/* Pulse Bridge adapter — Claude (claude.ai) (seat: alex).
 * Platform knowledge lives ONLY here (Blueprint §11).
 *
 * THIRD SURFACE, FIRST REFILL (v0.8.0, Ben's tap 2026-11-07
 * 05:02): Ben pointed the bridge at a claude.ai window ("im using
 * you and claude") and the seat test failed at the door — the
 * extension had no script on that host at all ("Receiving end
 * does not exist"). This adapter gives the ALEX seat a second
 * possible home: Claude on claude.ai, sitting in the seat Ben
 * registers him under (the seat name stays "alex" for the test,
 * Ben's ruling 04:55).
 *
 * EVIDENCE STATUS (2026-11-07): written against Ben's live
 * console probe of his own claude.ai tab (05:05 PST), not
 * inference:
 *  - turns: [data-testid="transcript-row"] containers, 8 on the
 *    probed page = 4 user + 4 assistant. Inside each row, the
 *    message element wears [data-testid="user-message"] or
 *    [data-testid="assistant-message"].
 *  - user text: the user-message element's innerText is the
 *    message, clean — no nameplate (receipt-friendly).
 *  - assistant text: the assistant-message element's innerText
 *    OPENS with a screen-reader echo: "Claude responded: <first
 *    line>" then a blank line, then the full body. bubbleText
 *    strips that echo (see _stripResponseEcho) — this surface's
 *    nameplate lesson, caught by the probe BEFORE the build
 *    instead of by a failed night after it.
 *  - composer: a TipTap/ProseMirror contenteditable div,
 *    [data-testid="chat-input"], aria-label "Write your prompt
 *    to Claude" — engaged BY THAT NAME (Ben's named-box rule).
 *  - generation: assistant rows carry data-is-streaming
 *    ("true" while streaming); a stop-face button is the other
 *    witness (Ben's button gate).
 * The delivery engine below (engage / type / button gate /
 * element-watching receipt) is the shared V6.1–V7.2 machinery,
 * inherited unchanged from the Muse adapter; only the platform
 * primitives differ. Self-check reports live counts so the first
 * install verifies the candidates against the real page. */
window.PB_ADAPTER = {
  seat: "alex",
  platform: "claudeai",

  /* CRUSHER v1 (Ben's fix, 2026-11-06 23:37): the composer is
   * engaged BY ITS NAME — the box that says what it is. On
   * claude.ai the box's name is its aria-label, "Write your
   * prompt to Claude" (Ben's probe, 2026-11-07). Structural
   * selectors find twins; the name is the real box's identity,
   * the same one a person (or a screen reader) uses. */
  composerName: "Write your prompt to Claude",

  candidates: {
    messages: [
      '[data-testid="assistant-message"]',
      '[data-testid="transcript-row"]',
    ],
    composer: [
      '[data-testid="chat-input"]',
      'div[contenteditable="true"]',
      "textarea",
    ],
    stop: [
      'button[aria-label="Stop response"]',
      'button[aria-label="Stop generating"]',
      'button[aria-label="Stop"]',
      '[data-testid="stop-button"]',
    ],
    send: [
      'button[aria-label="Send message"]',
      'button[aria-label="Send"]',
      '[data-testid="send-button"]',
    ],
  },

  _firstMatch(selectors) {
    for (const s of selectors) {
      const found = document.querySelectorAll(s);
      if (found.length) return { selector: s, elements: Array.from(found) };
    }
    return { selector: null, elements: [] };
  },

  /* Diagnostics: describe the top of the chat column so a human can
   * SEE the real message structure (Blueprint §11 evidence). */
  _describe(el, depth) {
    if (!el || depth > 3) return null;
    const attrs = {};
    for (const name of ["data-testid", "data-role", "data-author",
                        "data-message-author-role", "role", "aria-label"]) {
      const v = el.getAttribute && el.getAttribute(name);
      if (v) attrs[name] = v;
    }
    return {
      tag: el.tagName ? el.tagName.toLowerCase() : "?",
      cls: ((el.className && el.className.baseVal !== undefined)
             ? el.className.baseVal : String(el.className || "")).slice(0, 90),
      attrs,
      text: (el.innerText || "").replace(/\s+/g, " ").trim().slice(0, 70),
      children: depth < 3
        ? Array.from(el.children || []).slice(0, 6).map((c) => this._describe(c, depth + 1))
        : [],
    };
  },

  _columnRoot() {
    const main = document.querySelector("main");
    if (main) return main;
    const inp = document.querySelector('[data-testid="chat-input"]');
    if (inp) {
      let n = inp;
      for (let i = 0; i < 14 && n.parentElement; i++) n = n.parentElement;
      return n;
    }
    return document.body;
  },

  /* PROBE: run EVERY candidate, not just the first that bites —
   * this is the diagnostic that tells the truth about the page. */
  _probe() {
    const queries = {};
    const all = new Set();
    for (const c of this.candidates.messages) all.add(c);
    ["main", "article", '[role="main"]', '[role="log"]', '[role="article"]',
     '[role="list"]', '[role="listitem"]', '[class*="markdown"]',
     '[class*="prose"]', '[class*="message"]', '[class*="Message"]',
     '[class*="bubble"]', '[class*="chat"]', '[class*="turn"]',
     '[class*="response"]', '[class*="agent"]', '[class*="assistant"]']
      .forEach((c) => all.add(c));
    for (const q of all) {
      try { queries[q] = document.querySelectorAll(q).length; }
      catch (e) { queries[q] = -1; }
    }
    const census = {};
    let els = 0;
    for (const el of document.querySelectorAll("*")) {
      els++;
      const cn = (el.className && el.className.baseVal !== undefined)
        ? el.className.baseVal : String(el.className || "");
      for (const tok of cn.split(/\s+/)) {
        if (tok) census[tok] = (census[tok] || 0) + 1;
      }
    }
    const topClasses = Object.entries(census)
      .sort((a, b) => b[1] - a[1]).slice(0, 40);
    return {
      readyState: document.readyState,
      visibility: document.visibilityState,
      totalElements: els,
      queries,
      topClasses,
    };
  },

  /* Find message leaves STRUCTURALLY: the largest elements whose text
   * appears exactly once in the column (duplicated text = a wrapper;
   * wrappers quote their whole subtree). Best candidate wins if tied. */
  _scanLeaves(root) {
    const els = Array.from(root.querySelectorAll("*")).filter((el) => {
      if (el.closest("textarea, button, input, select, nav, header, footer, aside, svg")) return false;
      const cn = el.children.length;
      if (cn !== 0 && cn !== 1) return false;
      const t = (el.innerText || "").trim();
      return t.length >= 12 && t.length <= 20000;
    });
    const counts = new Map();
    for (const el of els) {
      const key = (el.innerText || "").replace(/\s+/g, " ").trim();
      counts.set(key, (counts.get(key) || 0) + 1);
    }
    const uniq = els.filter((el) =>
      counts.get((el.innerText || "").replace(/\s+/g, " ").trim()) === 1);
    uniq.sort((a, b) =>
      (b.innerText || "").length - (a.innerText || "").length);
    return uniq.slice(0, 3).map((el) => ({
      tag: el.tagName.toLowerCase(),
      cls: ((el.className && el.className.baseVal !== undefined)
             ? el.className.baseVal : String(el.className || "")).slice(0, 90),
      length: (el.innerText || "").length,
      startsWith: (el.innerText || "").trim().slice(0, 60),
      tree: this._describe(el.parentElement, 0),
    }));
  },


  landmarks: {
    assistant: "Ha, go for it",
    ben: "wait lol i will teach you",
  },

  /* Normalisation per Alex's ruling: collapse whitespace, trim,
   * preserve case; matching is exact after normalisation. */
  _normText(t) {
    return String(t == null ? "" : t).replace(/\s+/g, " ").trim();
  },

  _nodeInfo(el) {
    const attrs = {};
    for (const name of ["data-testid", "data-role", "data-author",
                        "data-message-author-role", "role", "aria-label"]) {
      const v = el.getAttribute && el.getAttribute(name);
      if (v) attrs[name] = String(v).slice(0, 120);
    }
    return {
      tag: el.tagName ? el.tagName.toLowerCase() : "?",
      cls: ((el.className && el.className.baseVal !== undefined)
             ? el.className.baseVal : String(el.className || "")).slice(0, 120),
      attrs,
      childCount: el.children ? el.children.length : 0,
      text: this._normText(el.innerText || "").slice(0, 40),
    };
  },

  /* Structural path of element-child indexes (zero-based) from scope. */
  _pathOf(el, stopAt) {
    const parts = [];
    let n = el;
    while (n && n !== stopAt && n.parentElement) {
      const p = n.parentElement;
      parts.unshift(Array.prototype.indexOf.call(p.children, n));
      n = p;
      if (parts.length > 40) break;
    }
    return parts.join(".");
  },

  _depthBelow(el, root) {
    let d = 0, n = el;
    while (n && n !== root && n.parentElement) { d++; n = n.parentElement; }
    return d;
  },

  _hierarchy(scope) {
    const nodes = [];
    let truncated = false;
    const walk = (el, depth, path) => {
      if (nodes.length >= 100) { truncated = true; return; }
      nodes.push(Object.assign(this._nodeInfo(el), { depth, path }));
      if (depth >= 5) return;
      const kids = Array.from(el.children || []);
      if (kids.length > 8) truncated = true;
      kids.slice(0, 8).forEach((k, i) =>
        walk(k, depth + 1, path === "" ? String(i) : path + "." + i));
    };
    walk(scope, 0, "");
    return { nodes, truncated, siblingIndexBase: 0 };
  },

  _landmarkReport(scope, landmark) {
    const norm = this._normText(landmark);
    const containers = [];
    for (const el of scope.querySelectorAll("*")) {
      if (this._normText(el.innerText || "").includes(norm)) containers.push(el);
    }
    if (!containers.length) {
      return { landmark, found: false, containerCount: 0, note: "not found" };
    }
    const set = new Set(containers);
    const deepest = containers.filter((el) =>
      !Array.from(el.querySelectorAll("*")).some((d) => set.has(d)));
    const wrappers = containers.slice()
      .sort((a, b) => (a.innerText || "").length - (b.innerText || "").length)
      .slice(0, 20)
      .map((el) => Object.assign(this._nodeInfo(el), {
        textLength: (el.innerText || "").length,
        path: this._pathOf(el, scope),
      }));
    const branches = deepest.slice(0, 5).map((el) => {
      const chainEls = [];
      let n = el;
      while (n) {
        chainEls.push(n);
        if (n === scope) break;
        n = n.parentElement;
      }
      return {
        truncated: chainEls.length > 20,
        chain: chainEls.slice(0, 20).map((node) => {
          const info = Object.assign(this._nodeInfo(node),
            { path: this._pathOf(node, scope) });
          if (node.parentElement) {
            const sibs = Array.from(node.parentElement.children);
            info.siblingCount = sibs.length;
            info.siblingsWithoutLandmark = sibs.filter((s) =>
              s !== node &&
              !this._normText(s.innerText || "").includes(norm)).length;
          }
          return info;
        }),
      };
    });
    return {
      landmark, found: true,
      containerCount: containers.length,
      deepestCount: deepest.length,
      wrappers, branches,
      branchesTruncated: deepest.length > 5,
    };
  },

  _candidatesReport(scope) {
    const seen = new Map();
    for (const sel of ['[class*="bubble"]', '[class*="message"]']) {
      for (const el of scope.querySelectorAll(sel)) {
        if (!seen.has(el)) seen.set(el, []);
        seen.get(el).push(sel);
      }
    }
    const all = Array.from(seen.entries());
    const aNorm = this._normText(this.landmarks.assistant);
    const bNorm = this._normText(this.landmarks.ben);
    const items = all.slice(0, 50).map(([el, matchedBy]) => {
      const t = this._normText(el.innerText || "");
      return Object.assign(this._nodeInfo(el), {
        matchedBy,
        path: this._pathOf(el, scope),
        depth: this._depthBelow(el, scope),
        containsAssistantLandmark: t.includes(aNorm),
        containsBenLandmark: t.includes(bNorm),
      });
    });
    return { total: all.length, shown: items.length, truncated: all.length > 50, items };
  },


  /* TURN CAPTURE (v0.3.0): the conversation region's text. Prefers
   * the [role="log"] region the census found; falls back to the chat
   * column, then the body. The trigger reads DELTAS of this text —
   * never message containers. (v0.4: captureTurnText remains only for
   * the popup's live-state readout; detection no longer uses it.) */
  regionEl() {
    return document.querySelector("main") || this._columnRoot() || document.body;
  },

  captureTurnText() {
    const r = this.regionEl();
    return PB.pbNormTurn(r ? (r.innerText || "") : "");
  },

  /* STRUCTURAL READ (Alex-approved design, 2026-11-06): read-only map
   * of the conversation region. Called ONLY from selfCheck(). */
  structuralRead() {
    const logs = Array.from(document.querySelectorAll('[role="log"]'));
    const frame = {
      isTop: window.top === window,
      host: location.hostname,
      path: location.pathname,
    };
    const defs = [];
    if (logs.length) {
      logs.slice(0, 3).forEach((log) => defs.push({ scopeKind: "log", root: log }));
    } else {
      defs.push({ scopeKind: "document-fallback", root: document.body });
    }
    return {
      frame,
      logCount: logs.length,
      scopesTruncated: logs.length > 3,
      siblingIndexBase: 0,
      scopes: defs.map(({ scopeKind, root }) => ({
        scopeKind,
        root: Object.assign(this._nodeInfo(root), {
          descendantCount: root.querySelectorAll("*").length,
          directChildCount: root.children ? root.children.length : 0,
        }),
        hierarchy: this._hierarchy(root),
        landmarks: {
          assistant: this._landmarkReport(root, this.landmarks.assistant),
          ben: this._landmarkReport(root, this.landmarks.ben),
        },
        candidates: this._candidatesReport(root),
      })),
    };
  },

  listAssistantMessages() {
    return this._firstMatch(this.candidates.messages).elements;
  },

  /* ==== v0.4 LETTERBOX HOOKS ====
   * markerForSeat: the destination marker this seat's page watches
   * for (the alex seat's page watches TO-REMMY). bubbleOf climbs
   * from a marker element to its enclosing transcript row.
   * bubbleSpeaker reads WHICH message element the row carries —
   * identity from the page's own testids, not from styling.
   * listBubbles enumerates the rows for the letterbox's history
   * absorb and for the receipt's birth watch. */
  get markerForSeat() { return PB_LETTERBOX.lbMarkerForSeat(this.seat); },

  bubbleOf(el) {
    if (!el || !el.closest) return null;
    return el.closest('[data-testid="transcript-row"]');
  },

  bubbleSpeaker(bubble) {
    if (!bubble || !bubble.querySelector) return "unknown";
    if (bubble.querySelector('[data-testid="user-message"]')) return "user";
    if (bubble.querySelector('[data-testid="assistant-message"]')) return "assistant";
    return "unknown";
  },

  listBubbles() {
    return Array.from(document.querySelectorAll('[data-testid="transcript-row"]'));
  },

  /* The row's message element carries the text; the row itself
   * also wears action bars and chrome. Assistant text arrives
   * wrapped in the page's screen-reader echo — stripped here so
   * the letterbox and the receipt see the message itself. */
  bubbleText(bubble) {
    if (!bubble) return "";
    let el = bubble;
    if (bubble.querySelector) {
      el = bubble.querySelector('[data-testid="user-message"], [data-testid="assistant-message"]') || bubble;
    }
    const t = el.innerText || "";
    return this.bubbleSpeaker(bubble) === "assistant" ? this._stripResponseEcho(t) : t;
  },

  /* claude.ai wraps assistant text in a screen-reader echo: the
   * innerText opens "Claude responded: <first line>", a blank
   * line, then the full body (Ben's probe, 2026-11-07 — the
   * probed sample's body opened with the echoed line verbatim).
   * Strip the wrapper: drop the label, and when the segment
   * before the first blank line is a prefix of what follows,
   * drop the segment too — what remains is the message. A short
   * reply with no duplication keeps everything after the label. */
  _stripResponseEcho(t) {
    const s = String(t == null ? "" : t);
    if (!s.startsWith("Claude responded:")) return s;
    const rest = s.slice("Claude responded:".length).replace(/^\s+/, "");
    const idx = rest.indexOf("\n\n");
    if (idx > 0) {
      const head = rest.slice(0, idx).trim();
      const body = rest.slice(idx + 2).replace(/^\s+/, "");
      if (head && body.startsWith(head)) return body;
    }
    return rest;
  },

  messageText(el) {
    return (el.innerText || "").trim();
  },

  isGenerating() {
    if (document.querySelector('[data-is-streaming="true"]')) return true;
    return !!document.querySelector(this.candidates.stop.join(", "));
  },

  /* ---- CRUSHER v1: named-box delivery (shared shape) ----
   * Ben's fix (2026-11-06 23:37): engage the composer BY ITS NAME
   * (adapter.composerName). The steps, each gated on the last:
   *   engage — find the box by its accessible name (aria-label,
   *     placeholder, role=textbox name, or the textarea
   *     placeholder), prefer the VISIBLE candidate, CLICK into it
   *     like a person (the page then wakes its own send button),
   *     then focus.
   *   type — through the adapter's _typeInto (the editor's own
   *     input path, per platform).
   *   verify-type — the text is re-read from THAT box.
   *   send-button — looked up in the engaged box's own
   *     neighbourhood (its form / composer container chain), with
   *     the old global candidates as fallback.
   *   receipt — V7.2 element-watching confirmation (the send's
   *     newborn bubble carrying the PB-ID; see
   *     _awaitConfirmation). A miss is reported as stage
   *     "receipt" WITH a verdict: "absent" earns Crusher's
   *     bounded proven-absence retry; "unknown" is UNVERIFIED
   *     (sent, unconfirmed) — never a failure. */
  _accessibleName(el) {
    return (el.getAttribute && (el.getAttribute("aria-label") || el.getAttribute("placeholder"))) || "";
  },
  _isVisible(el) {
    if (typeof el.getClientRects === "function") return el.getClientRects().length > 0;
    return true; // minimal DOMs (fixtures): presence counts as visible
  },
  findComposer() {
    if (this._engagedComposer && this._isVisible(this._engagedComposer)) {
      return this._engagedComposer;
    }
    const name = this.composerName || "";
    if (name) {
      const pool = new Set();
      for (const s of this.candidates.composer) {
        try { for (const el of document.querySelectorAll(s)) pool.add(el); } catch (e) { /* bad selector: skip */ }
      }
      try { for (const el of document.querySelectorAll("textarea, [contenteditable='true'], [role='textbox']")) pool.add(el); } catch (e) { /* */ }
      const named = Array.from(pool).filter((el) => this._accessibleName(el).trim() === name);
      const hit = named.find((el) => this._isVisible(el)) || named[0];
      if (hit) return hit;
    }
    return this._firstMatch(this.candidates.composer).elements[0] || null;
  },
  engageComposer() {
    const composer = this.findComposer();
    if (!composer) return null;
    try { composer.click(); } catch (e) { /* engagement falls through to focus */ }
    try { composer.focus(); } catch (e) { /* */ }
    this._engagedComposer = composer;
    return composer;
  },
  _composerScope() {
    return PB_SEND.pbComposerScope(this);
  },
  findSendButton() {
    return PB_SEND.pbFindSendButton(this);
  },
  /* ---- CRUSHER V6.1: generation deference + Ben's button gate ----
   * (Alex step 3; Ben's fix, 2026-11-07 01:46): the composer's
   * button WEARS the page's state — one morphing control whose
   * face is Stop while the page generates and Send when it can
   * accept one. v0.6.0's delivery never looked: a click during
   * generation landed on the stop face, killed the reply, and
   * never sent. Now the state is read from the button itself —
   * by its accessible label / stable attributes, re-queried live
   * at every decision, never from a stale reference or position.
   * Delivery never engages, types, or clicks while the
   * destination is generating: it waits, bounded by
   * PB_CRUSHER_DEFER_MAX_MS, then stalls with the reason named. */
  /* v0.18.0: the send-decision logic lives in sendcore.js
   * (PB_SEND) — one home, shared by every adapter. The
   * methods below delegate; this adapter keeps only its
   * platform knowledge (candidates, composer, typing,
   * receipt). */
  _buttonLabel(b) {
    return PB_SEND.pbButtonLabel(b);
  },
  _buttonIsStop(b) {
    return PB_SEND.pbButtonIsStop(this, b);
  },
  _buttonIsSend(b) {
    return PB_SEND.pbButtonIsSend(this, b);
  },
  /* The destination's generation state as the interface itself
   * reports it: "generating" while a stop face shows (in the
   * engaged composer's own neighbourhood ONLY — v0.18.0: this
   * read was narrowed to the composer, exactly as v0.17.0 did
   * on the ChatGPT surface; the whole page no longer testifies
   * at a send decision, and isGenerating() no longer feeds it),
   * "ready" when a send face shows and no stop face does,
   * "unknown" when neither face can be found. */
  composerButtonState() {
    return PB_SEND.pbComposerButtonState(this);
  },
  _destinationGenerating() {
    return PB_SEND.pbDestinationGenerating(this);
  },
  async _waitForDestinationIdle() {
    return PB_SEND.pbWaitForDestinationIdle(this);
  },
  /* ---- V7.2: ELEMENT-WATCHING RECEIPT (Ben's overrule) ----
   * Ben's diagnosis (2026-11-07): the V6.1 receipt "is waiting
   * for a time limit instead of watching the actual page
   * element." That scan re-derived the landing on every poll —
   * rebuild the bubble list, classify speakers, slice the last
   * 6 user turns, demand the text OPEN with the header — three
   * inferences stacked, and the 2026-11-07 live night broke on
   * them in both directions (the Muse "You:" nameplate; a
   * still-unnamed link on ChatGPT) while the letters sat
   * landed in plain sight. Ben overruled Alex's confirmation
   * design; the retry policy the verdicts feed is UNCHANGED.
   * Now deliverText snapshots the page's bubbles BEFORE the
   * send click, and this scan watches for what the click
   * births: a bubble element that was not in the snapshot.
   *   - a newborn (not positively the other seat's) carrying
   *     this letter's exact PB-ID -> CONFIRMED. Identity is
   *     anchored to the node and its birth, never to an
   *     opening line: whatever nameplate or label the surface
   *     wraps the message in is presentation, not identity.
   *   - newborn bubbles that are not ours are reported as
   *     foreign: the page DID something during the window,
   *     so absence is not provable -> UNVERIFIED upstream.
   *   - no newborn at all -> "readable": the window's tail
   *     decides ABSENT, proven by watching.
   * Speaker classification is used ONLY to exclude: a bubble
   * positively identified as the other seat's can quote a
   * PB-ID in reply and must never confirm a delivery. It is
   * never required to include. (The V6.1 matcher,
   * pbTurnConfirms, survives as the id-less fallback inside
   * the newborn node only.) */
  _scanConfirmation(text, baseline) {
    let bubbles;
    try {
      bubbles = this.listBubbles();
    } catch (e) {
      return { verdict: "unreadable", matches: 0, foreign: false };
    }
    const id = PB.pbExtractBridgeId(text);
    let matches = 0;
    let foreign = false;
    for (const b of bubbles) {
      if (baseline && baseline.has(b)) continue; // present before the send — not its child
      let speaker = "unknown";
      try { speaker = this.bubbleSpeaker(b); } catch (e) { /* unclassifiable is not the other seat's */ }
      if (speaker === "assistant") continue;
      let t = "";
      try { t = this.bubbleText(b); } catch (e) { continue; }
      const hit = id ? t.includes("PB-ID: " + id) : PB.pbTurnConfirms(t, text);
      if (hit) matches++;
      else foreign = true;
    }
    if (matches > 0) return { verdict: "confirmed", matches, foreign };
    return { verdict: "readable", matches: 0, foreign };
  },
  async _awaitConfirmation(text, baseline) {
    const polls = (typeof window !== "undefined" && window.PB_TEST_RECEIPT_POLLS) || 24;
    const pollMs = (typeof window !== "undefined" && window.PB_TEST_RECEIPT_POLL_MS) || 500;
    /* V6.2 (theory 1, from the 2026-11-07 live test): a page that
     * is still GENERATING cannot testify. Its turns are mid-render,
     * and a scan there can read a clean picture that simply omits
     * the letter it is looking for — V6.1 turned exactly that into
     * "proven absence" and resent letters that had landed, on BOTH
     * platforms in one night. So a poll only COUNTS when the
     * destination is quiet (Ben's button gate reads the state);
     * polls taken mid-generation are evidence of nothing and are
     * not counted. The window is `polls` COUNTED polls, bounded by
     * a wall-clock cap: a page that never sits still long enough
     * yields UNKNOWN — never absence. On a page quiet throughout,
     * the timing and the verdicts are exactly V6.1's. */
    const capMs = (typeof window !== "undefined" && window.PB_TEST_RECEIPT_CAP_MS) || 120000;
    const started = Date.now();
    let cleanTail = 0; // consecutive counted, readable, matchless polls at the window's end
    let counted = 0;
    let sawForeign = false; // V7.2: a newborn bubble that was not ours appeared
    while (counted < polls) {
      await new Promise((r) => setTimeout(r, pollMs));
      const scan = this._scanConfirmation(text, baseline);
      if (scan.verdict === "confirmed") return { ok: true, duplicates: scan.matches };
      if (scan.foreign) sawForeign = true;
      let generating = false;
      try { generating = this._destinationGenerating(); } catch (e) { /* an unreadable button state is not evidence of generation */ }
      if (generating) {
        if (Date.now() - started >= capMs) break;
        continue; // the page is streaming — this poll testifies to nothing
      }
      counted++;
      cleanTail = scan.verdict === "readable" ? cleanTail + 1 : 0;
      if (Date.now() - started >= capMs) break;
    }
    if (counted >= polls && cleanTail >= 4 && !sawForeign) {
      return { ok: false, stage: "receipt", verdict: "absent", error: "no new turn appeared — absence established (page quiet and readable throughout the counted window, and the send birthed no bubble)" };
    }
    if (sawForeign) {
      return { ok: false, stage: "receipt", verdict: "unknown", error: "new turns appeared during the receipt window but none carried this letter's PB-ID — clicked; receipt not yet observed; absence not established, never auto-retried" };
    }
    return { ok: false, stage: "receipt", verdict: "unknown", error: "no confirming turn could be observed — the destination page was not quiet and readable through the receipt window" };
  },
  async deliverText(text) {
    // V6.1 deference (Alex step 3): never engage a destination
    // that is still generating — wait it out, bounded, or stall.
    const defer = await this._waitForDestinationIdle();
    if (!defer.ok) return defer;
    const composer = this.engageComposer();
    if (!composer) return { ok: false, stage: "composer", error: "composer not found (by name or structure)" };
    const typed = await this._typeInto(composer, text);
    if (!typed.ok) return typed;
    await new Promise((r) => setTimeout(r, 350));
    if (!PB.pbTextsMatch(this._composerText(composer), text)) {
      return { ok: false, stage: "verify-type", error: "composer text did not land" };
    }
    // Ben's gate at the moment that matters: re-read the button
    // state live. If the page began generating while we typed —
    // or the only button the lookup finds is wearing its stop
    // face — the click does not happen.
    if (this._destinationGenerating()) {
      return { ok: false, stage: "generating", error: "destination began generating before the send click — the click was not made" };
    }
    /* V6.2 (theory 2 — Ben's idle-tab observation): on a tab
     * nobody is touching, the page may render its send button a
     * beat AFTER the text lands. A single instantaneous lookup
     * calls that "no button" and the letter dies there. Wait for
     * the button the way a person would: briefly, and watching
     * for generation to start instead. */
    let btn = this.findSendButton();
    const btnWaitMs = (typeof window !== "undefined" && window.PB_TEST_BUTTON_WAIT_MS) || 3000;
    const btnWaitStart = Date.now();
    while (!btn && Date.now() - btnWaitStart < btnWaitMs) {
      if (this._destinationGenerating()) {
        return { ok: false, stage: "generating", error: "destination began generating while waiting for its send button — the click was not made" };
      }
      await new Promise((r) => setTimeout(r, 250));
      btn = this.findSendButton();
    }
    if (!btn) return { ok: false, stage: "send-button", error: "send button not found after typing" };
    if (this._buttonIsStop(btn)) {
      return { ok: false, stage: "generating", error: "the composer button is wearing its stop face — the click was not made" };
    }
    /* V7.2: snapshot the page's bubbles BEFORE the click —
     * the receipt watches for the node the click births (see
     * _scanConfirmation). A snapshot that cannot be taken
     * degrades the watch to page-wide; the scans that follow
     * still speak for the page's readability either way. */
    let baseline = null;
    try { baseline = new Set(this.listBubbles()); } catch (e) { baseline = null; }
    btn.click();
    // Receipt (V7.2): element-watching confirmation.
    return this._awaitConfirmation(text, baseline);
  },

  _composerText(composer) {
    return composer.tagName === "TEXTAREA" ? (composer.value || "") : (composer.innerText || "");
  },

  /* Muse typing, V6.2: type the way a person does FIRST —
   * insertText into the focused box (engageComposer has already
   * clicked and focused it), the same path the ChatGPT adapter
   * has always used. The native setter below remains as the
   * fallback — a textarea's value set programmatically is seen by
   * the app framework, but on the live page it may never summon
   * the send button a person's keystrokes would (Ben's idle-tab
   * observation, 2026-11-07). The insert is verified against the
   * box's actual text before it is believed; a refused or
   * unlanded insert falls through to the setter. */
  async _typeInto(composer, text) {
    try {
      if (typeof document !== "undefined" && document.execCommand &&
          typeof window !== "undefined" && window.getSelection) {
        if (composer.tagName === "TEXTAREA") {
          try {
            composer.selectionStart = 0;
            composer.selectionEnd = (composer.value || "").length;
          } catch (e) { /* the caret is a nicety, not a requirement */ }
        } else {
          const sel = window.getSelection();
          const range = document.createRange();
          range.selectNodeContents(composer);
          sel.removeAllRanges();
          sel.addRange(range);
        }
        const okIns = document.execCommand("insertText", false, text);
        if (okIns && PB.pbTextsMatch(this._composerText(composer), text)) return { ok: true };
      }
    } catch (e) { /* the human path is unavailable here — fall through to the setter */ }
    try {
      const setter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype, "value").set;
      setter.call(composer, text);
      composer.dispatchEvent(new Event("input", { bubbles: true }));
    } catch (e) {
      return { ok: false, stage: "type", error: String(e && e.message || e) };
    }
    return { ok: true };
  },

  _userTurnCount() {
    return this.listBubbles().filter((b) => this.bubbleSpeaker(b) === "user").length;
  },

  _lastUserTurnTextMatches(text) {
    const users = this.listBubbles().filter((b) => this.bubbleSpeaker(b) === "user");
    if (!users.length) return false;
    return PB.pbTextsMatch(this.bubbleText(users[users.length - 1]), text);
  },

  /* Self-check: live counts for every candidate, surfaced in the popup
   * (content.js answers pb-selfcheck). This is how an unverified
   * adapter gets verified: numbers from the real page, not guesses. */
  selfCheck() {
    const counts = {};
    for (const group of ["messages", "composer", "stop", "send"]) {
      counts[group] = {};
      for (const s of this.candidates[group]) {
        counts[group][s] = document.querySelectorAll(s).length;
      }
    }
    return {
      platform: this.platform,
      seat: this.seat,
      url: location.href,
      title: document.title,
      matched: {
        messages: this._firstMatch(this.candidates.messages).selector,
        composer: this._firstMatch(this.candidates.composer).selector,
      },
      composerName: this.composerName || "",
      composerByName: (() => {
        if (!this.composerName) return false;
        const pool = new Set();
        for (const el of document.querySelectorAll("textarea, [contenteditable='true'], [role='textbox']")) pool.add(el);
        return Array.from(pool).some((el) => this._accessibleName(el).trim() === this.composerName);
      })(),
      counts,
      sampleTree: this._describe(this._columnRoot(), 0),
      scan: this._scanLeaves(this._columnRoot()),
      probe: this._probe(),
      columnMarker: !!document.querySelector('[data-hatch-chat-column="true"]'),
      structural: this.structuralRead(),
    };
  },
};
