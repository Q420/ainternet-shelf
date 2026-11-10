"use strict";
/* Pulse Bridge adapter — ChatGPT (seat: alex).
 * Platform knowledge lives ONLY here (Blueprint §11): if ChatGPT
 * changes its page, this is the one file that changes.
 *
 * EVIDENCE STATUS (2026-11-06): the message selector carried from
 * v0.1.0, where it was the stable side of the pair. The 2026-11-06
 * browser inspection could only see ChatGPT's accessibility tree
 * (roles/names/text), NOT raw HTML — the four working selectors are
 * UNVERIFIED from that inspection, neither confirmed nor refuted.
 * Observed equivalents: turns headed "You said:" / "ChatGPT said:"
 * (h4), composer is a textbox named "Ask ChatGPT", and a Send button
 * exists only while the composer is non-empty. The acceptance walk
 * in Ben's Chrome (real DOM) plus this adapter's selfCheck() counts
 * are the proving ground.
 *
 * LETTERBOX HOOKS history: v0.4.0 keyed on [data-message-author-role]
 * (carried from v0.1.0) — proven DEAD on the live page 2026-11-06
 * (all candidate counts x0). v0.4.1 keys on the turn-block shape and
 * the page's "You said:" / "ChatGPT said:" labels instead. */
window.PB_ADAPTER = {
  seat: "alex",
  platform: "chatgpt",

  /* CRUSHER v1 (Ben's fix, 2026-11-06 23:37): the composer is
   * engaged BY ITS NAME — the box that says "Ask ChatGPT".
   * Structural selectors find twins; the name is the real box's
   * identity, the same one a person (or a screen reader) uses. */
  composerName: "Ask ChatGPT",

  candidates: {
    messages: [
      '[data-message-author-role="assistant"]',
      '[data-testid*="assistant"]',
      "article",
    ],
    composer: [
      "#prompt-textarea",
      'div[contenteditable="true"]',
      "textarea",
    ],
    stop: [
      '[data-testid="stop-button"]',
      'button[aria-label="Stop generating"]',
      'button[aria-label="Stop streaming"]',
    ],
    send: [
      '[data-testid="send-button"]',
      'button[aria-label="Send"]',
      'button[aria-label="Send prompt"]',
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
    const col = document.querySelector('[data-hatch-chat-column="true"]');
    if (col) return col;
    const ta = document.querySelector("textarea");
    if (ta) {
      let n = ta;
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
    assistant: "For Alex: DETECTION TEST 001",
    ben: "i feel like it would be easier to have the extension act as an actual relay",
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
   * column, then the body. (v0.4: captureTurnText remains only for
   * the popup's live-state readout; detection no longer uses it.) */
  regionEl() {
    return document.querySelector('[role="log"]') || this._columnRoot() || document.body;
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

  /* ==== LETTERBOX HOOKS (v0.4.1 — turn-block shape) ====
   * Live evidence (Ben's self-check paste, 2026-11-06 22:13): the
   * v0.1.0 hooks are DEAD on current ChatGPT — [data-message-author-
   * role] x0, [data-testid*=assistant] x0, article x0. What the page
   * actually does: every turn is one block in the transcript column,
   * headed in the accessibility layer by "You said:" or "ChatGPT
   * said:"; user turns additionally wear a .bg-user-message bubble.
   * So the bubble = the turn block (nearest ancestor containing
   * exactly one said-label and no other turn), and the speaker =
   * that label. A climb that reaches the page root without finding
   * a said-label returns null — never guess a container. */
  get markerForSeat() { return PB_LETTERBOX.lbMarkerForSeat(this.seat); },

  _saidLabel(text) {
    const t = String(text || "");
    const userAt = t.search(/(^|\n)\s*You said:/);
    const asstAt = t.search(/(^|\n)\s*ChatGPT said:/);
    if (userAt === -1 && asstAt === -1) return null;
    if (userAt !== -1 && (asstAt === -1 || userAt < asstAt)) return "user";
    return "assistant";
  },

  _saidCount(text) {
    const t = String(text || "");
    const u = (t.match(/You said:/g) || []).length;
    const a = (t.match(/ChatGPT said:/g) || []).length;
    return u + a;
  },

  bubbleOf(el) {
    if (!el) return null;
    // Legacy shape first — if it ever returns, it still works.
    if (el.closest) {
      const legacy = el.closest('[data-message-author-role]') || el.closest("article");
      if (legacy) return legacy;
    }
    // Turn-block climb: the FIRST ancestor (starting at el itself)
    // whose subtree carries exactly one said-label and that label is
    // the first label in its text. That ancestor is one turn.
    let n = el;
    for (let i = 0; i < 40 && n; i++) {
      const text = n.innerText || "";
      if (this._saidCount(text) === 1 && this._saidLabel(text)) return n;
      if (this._saidCount(text) > 1) return null; // climbed past the turn
      n = n.parentElement;
    }
    return null;
  },

  bubbleSpeaker(bubble) {
    if (!bubble) return "unknown";
    const role = bubble.getAttribute && bubble.getAttribute("data-message-author-role");
    if (role === "assistant") return "assistant";
    if (role === "user") return "user";
    const cls = (bubble.className && bubble.className.baseVal !== undefined)
      ? bubble.className.baseVal : String(bubble.className || "");
    if (cls.includes("bg-user-message")) return "user";
    const lbl = this._saidLabel(bubble.innerText || "");
    return lbl || "unknown";
  },

  /* Text of a bubble for detection. ChatGPT's turn blocks carry the
   * page's own label in their text ("ChatGPT said:" / "You said:"
   * as the first line, from the sr-only headings). The letterbox's
   * first-line rule needs the MESSAGE's first line, so strip a
   * leading label line when present. */
  bubbleText(bubble) {
    let t = String((bubble && bubble.innerText) || "");
    t = t.replace(/^\s*(You said:|ChatGPT said:)\s*\n?/, "");
    return t;
  },

  listBubbles() {
    const turns = Array.from(document.querySelectorAll("[data-message-author-role]"));
    if (turns.length) return turns;
    const arts = Array.from(document.querySelectorAll("article"));
    if (arts.length) return arts;
    // Turn-block shape: for each said-label leaf, its turn block.
    const out = [];
    const seenEls = new Set();
    for (const el of document.querySelectorAll("*")) {
      const own = (el.children && el.children.length === 0) ? (el.innerText || "") : "";
      if (own && this._saidLabel(own) && this._saidCount(own) === 1) {
        const b = this.bubbleOf(el);
        if (b && !seenEls.has(b)) { seenEls.add(b); out.push(b); }
      }
    }
    return out;
  },

  messageText(el) {
    return (el.innerText || "").trim();
  },

  /* A stop control exists only while a response streams. */
  isGenerating() {
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
   * engaged composer's own neighbourhood first, then the page),
   * "ready" when a send face shows and no stop face does,
   * "unknown" when neither face can be found.
   *
   * V0.17.0 — THE FENCE'S CONDITION 1 (Ben's design, his
   * ruling): the verdict comes from THE COMPOSER'S OWN BUTTON
   * and nowhere else. The pre-fence reader also scanned the
   * whole document, where ANY stop-labelled element — a hidden
   * stop button the page keeps mounted, a stray control —
   * testified "generating" forever, and letters typed fine
   * and then refused their own send click, at the same stage,
   * every time (Ben's report, 2026-11-09: "pasted but not
   * send"). A scope that shows neither face now answers
   * "unknown" — UNKNOWN never counts as a pass at the fence,
   * and never as a veto either. isGenerating() still exists
   * for the receipt's evidence reads, where a conservative
   * "still writing" yields UNVERIFIED, never a wrongful send;
   * it no longer feeds the send decision. */
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
      return { ok: false, stage: "receipt", verdict: "unknown", error: "new turns appeared during the receipt window but none carried this letter's PB-ID — sent, but unconfirmed; absence not established, never auto-retried" };
    }
    return { ok: false, stage: "receipt", verdict: "unknown", error: "no confirming user turn could be observed — the destination page was not quiet and readable through the receipt window" };
  },
  /* ---- V0.11.0 P2 — CONTEXT-FULL PROBE + ROLLOVER ----
   * (Ben's item, Alex's ruling, Ben's screen evidence
   * 2026-11-08: PROBE-REPORT-chatgpt-context-full-2026-11-08.md.)
   * The probe is READ-ONLY and runs before EVERY delivery into
   * this surface (Alex: a distress-only probe is too late). The
   * observed full state: a bottom banner — an aside[role=status]
   * holding an h3 that reads exactly "Context window full", the
   * summary/upgrade description, and "New chat" / "Upgrade to
   * Plus" buttons — while the composer stays present and editable
   * (the banner, not the box, is the authority). The detector
   * anchors on that structure + exact heading, never on loose
   * keyword text: Ben's probe run caught ordinary conversation
   * content ("completion overreached…") in its liberal scan, and
   * content is not a signal.
   * When the banner is present, deliverText presses the banner's
   * OWN New chat button (never the generic new-chat icon), waits
   * for the new conversation to become ready, sends a rollover
   * notice carrying the minimum bridge state, re-probes, and only
   * then delivers the pending letter — which keeps the SAME
   * PB-ID (the rollover happens inside one delivery attempt, so
   * the router's carried text never changes). If any step cannot
   * complete, the letter is NOT delivered into the full
   * conversation: the attempt returns stage "context-full" and
   * the router stalls it for Ben's hand with the evidence named. */
  probeContextFull() {
    const out = { full: false, actionable: false, button: null, bannerText: "" };
    try {
      const heads = Array.from(document.querySelectorAll('h1, h2, h3, h4, [role="heading"]'));
      for (const h of heads) {
        if (!this._isVisible(h)) continue;
        if (this._normText(h.innerText || h.textContent || "") !== "Context window full") continue;
        // The heading must sit inside the status banner — climb
        // to the aside / role=status ancestor.
        let box = h;
        for (let i = 0; i < 6 && box; i++) {
          if (box.getAttribute && (box.getAttribute("role") === "status" || box.tagName === "ASIDE")) break;
          box = box.parentElement;
        }
        if (!box || !(box.getAttribute && (box.getAttribute("role") === "status" || box.tagName === "ASIDE"))) continue;
        if (!this._isVisible(box)) continue;
        out.full = true;
        out.bannerText = this._normText(box.innerText || "").slice(0, 300);
        const btns = Array.from(box.querySelectorAll ? box.querySelectorAll("button") : []);
        const btn = btns.find((b) => this._normText((b.innerText || "") + " " + (b.getAttribute && b.getAttribute("aria-label") || "")) === "New chat");
        if (btn) { out.actionable = true; out.button = btn; }
        return out;
      }
    } catch (e) { /* an unreadable page testifies to nothing — not full, not healthy: the normal path's own gates decide */ }
    return out;
  },
  async _rollover(pendingText) {
    const probe = this.probeContextFull();
    if (!probe.full) return { ok: true, info: null }; // state changed under us — proceed normally
    if (!probe.actionable || !probe.button) {
      return { ok: false, stage: "context-full", error: "context window full (banner observed) but its New chat button was not found — nothing typed or clicked; the letter was NOT delivered to the full conversation" };
    }
    const fromUrl = (typeof location !== "undefined" && location.href) || "";
    const fromTitle = (typeof document !== "undefined" && document.title) || "";
    try { probe.button.click(); } catch (e) {
      return { ok: false, stage: "context-full", error: "the banner's New chat button refused the click — the letter was NOT delivered to the full conversation" };
    }
    /* Wait for the new conversation: banner gone, a composer
     * present, and the page not generating — two consecutive
     * clean polls, bounded. The tab navigates in place, so the
     * seat's registration (keyed on the tab) follows the rollover;
     * the router records the conversation change off the result. */
    const pollMs = (typeof window !== "undefined" && window.PB_TEST_ROLLOVER_POLL_MS) || 500;
    const maxPolls = (typeof window !== "undefined" && window.PB_TEST_ROLLOVER_POLLS) || 50;
    let clean = 0;
    let ready = false;
    for (let i = 0; i < maxPolls; i++) {
      await new Promise((r) => setTimeout(r, pollMs));
      let okNow = false;
      try {
        okNow = !this.probeContextFull().full && !!this.findComposer() && !this._destinationGenerating();
      } catch (e) { okNow = false; }
      clean = okNow ? clean + 1 : 0;
      if (clean >= 2) { ready = true; break; }
    }
    if (!ready) {
      return { ok: false, stage: "context-full", error: "New chat was pressed but the new conversation did not become ready (banner gone + composer present + not generating) inside the bounded wait — the letter was NOT delivered" };
    }
    /* The rollover notice: minimum operational state only (Alex's
     * ruling) — bridge identity, what this conversation continues,
     * the pending letter's PB-ID and that it follows unchanged.
     * ChatGPT's own automatic summary carries the working content;
     * this notice carries the bridge state, and is a page-level
     * action (no PB-ID of its own — it is not an envelope letter;
     * the router records it in state.rollovers). */
    const pendingId = PB.pbExtractBridgeId(pendingText);
    const notice =
      "Via Pulse Bridge — rollover notice:\n" +
      "This conversation continues \"" + (fromTitle || "the previous conversation") + "\" — that ChatGPT conversation reached its context limit (\"Context window full\"), and Pulse Bridge opened this new chat before delivering the pending letter, so nothing was delivered into the full conversation.\n" +
      "Pending letter: " + (pendingId ? "PB-ID " + pendingId : "(no PB-ID)") + " — it follows in the next message, unchanged, under the same PB-ID.\n" +
      "ChatGPT's automatic summary of the previous conversation carries the working context; this notice carries only the bridge state.";
    const nres = await this._deliverTextDirect(notice);
    let noticeWord;
    if (nres && nres.ok) noticeWord = "confirmed";
    else if (nres && nres.stage === "receipt" && nres.verdict === "absent") noticeWord = "absent";
    else if (nres && nres.stage === "receipt") noticeWord = "unverified";
    else {
      return { ok: false, stage: "context-full", error: "the new conversation opened but the rollover notice could not be sent (" + ((nres && nres.error) || "unknown") + ") — the pending letter was NOT delivered" };
    }
    // Re-probe before the letter: if the new chat is somehow
    // already full, the letter still does not go into it.
    if (this.probeContextFull().full) {
      return { ok: false, stage: "context-full", error: "the new conversation already shows the context-full banner — the letter was NOT delivered" };
    }
    return {
      ok: true,
      info: {
        occurred: true,
        fromUrl,
        toUrl: (typeof location !== "undefined" && location.href) || "",
        fromTitle,
        notice: noticeWord,
      },
    };
  },
  async deliverText(text) {
    // V0.11.0 P2: probe BEFORE anything else — before the
    // generation defer, before the composer is engaged, before a
    // single character is typed (Alex: probe before every
    // delivery; the probe itself never alters a healthy page).
    let rolloverInfo = null;
    try {
      if (this.probeContextFull().full) {
        const ro = await this._rollover(text);
        if (!ro.ok) return ro;
        rolloverInfo = ro.info;
      }
    } catch (e) {
      return { ok: false, stage: "context-full", error: "context probe failed: " + String(e && e.message || e) + " — nothing typed or clicked" };
    }
    const res = await this._deliverTextDirect(text);
    if (res && res.ok && rolloverInfo) res.rollover = rolloverInfo;
    return res;
  },
  async _deliverTextDirect(text) {
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

  async _typeInto(composer, text) {
    try {
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(composer);
      sel.removeAllRanges();
      sel.addRange(range);
      const okIns = document.execCommand("insertText", false, text);
      if (!okIns) return { ok: false, stage: "type", error: "insertText refused" };
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

  /* Self-check: live counts for every candidate, surfaced in the
   * popup via content.js — numbers from the real page. */
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
      contextFull: (() => { try { const p = this.probeContextFull(); return { full: p.full, actionable: p.actionable }; } catch (e) { return null; } })(), // V0.11.0 P2
      sampleTree: this._describe(this._columnRoot(), 0),
      scan: this._scanLeaves(this._columnRoot()),
      probe: this._probe(),
      columnMarker: !!document.querySelector('[data-hatch-chat-column="true"]'),
      structural: this.structuralRead(),
    };
  },
};
