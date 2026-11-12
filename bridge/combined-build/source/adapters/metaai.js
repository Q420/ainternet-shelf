"use strict";
/* Pulse Bridge adapter — Meta AI (www.meta.ai) (seat: alex).
 * Platform knowledge lives ONLY here (Blueprint §11).
 *
 * FIFTH SURFACE (v0.10.0, Alex's authorisation 2026-11-08
 * 01:11 PST, bridge letter pb-mw7m591r-3-h0lu, ⟦ALEX-FINAL⟧,
 * under Ben's delegation "He can initiate builds"). Alex's
 * added gate rides with the build: implementation, fixture
 * and regression FIRST; live account interaction only after
 * the results and proposed exposure steps are reviewed by
 * Alex and authorised by Ben. The anti-automation account
 * risk stands recorded as an INFERENCE, not an established
 * fact. Guest mode is explicitly out of scope.
 *
 * EVIDENCE STATUS (2026-11-08): written against Ben's
 * three-phase console probe of his own signed-in meta.ai tab
 * (PROBE-metaai-2026-11-08.js; PROBE-REPORT-metaai-2026-11-08.md)
 * — observed, not inferred:
 *  - turns: the conversation lives at meta.ai/prompt/<id>;
 *    turns are wrapped in [data-message-item] (4 items across
 *    2 exchanges, 10 across 5 — counts reconciled twice); user
 *    turns carry [data-user-message]; assistant turns carry
 *    data-testid="assistant-message".
 *  - nameplates: NONE. An assistant turn's innerText opens
 *    with the reply text itself, a user turn's with the
 *    sender's raw words — no "X said" label, no response echo.
 *    The FIRST surface with nothing to strip: bubbleText reads
 *    the raw turn text and the strict header + PB-ID checks
 *    downstream do all the work (Alex's requirement: no
 *    nameplate stripping in this adapter).
 *  - composer: THE DOUBLE. The testid "composer-input" exists
 *    twice at once — a TEXTAREA at rect 0x0 with a null
 *    offsetParent (present but hidden: a form mirror / decoy)
 *    and a visible contenteditable DIV (571x27 at rest, 586x27
 *    in conversation). The rumoured textarea[aria-label="Ask
 *    Meta AI"] does NOT exist; the box carries no accessible
 *    name at all (aria=null in every probe), so its identity
 *    here is testid + visibility, not a name. Alex's rule,
 *    implemented in findComposer: NEVER engage the hidden
 *    textarea — require the visible contenteditable, nonzero
 *    dimensions, correct testid; anything less fails closed.
 *  - send: [data-testid="composer-send-button"], aria-label
 *    "Send", present at rest in both page states.
 *  - generation: a PAIRED BUTTON SWAP, caught mid-stream by
 *    Ben (he requested an extended answer to widen the
 *    window). While Meta AI generates, composer-stop-button
 *    (aria-label "Stop") is present AND the send button is
 *    ABSENT; at rest the reverse. No data-streaming or
 *    aria-busy attributes exist in either state — the swap
 *    is the witness. Completion (Alex's standing rule):
 *    generation observed, then stop gone AND send restored,
 *    content settled, newborn-bubble receipt confirmed.
 *  - shadow DOM: none relevant (a Next.js route announcer
 *    only). Light DOM throughout.
 *  - React input: RESOLVED by the v0.10.1 delivery probe
 *    (2026-11-08): the editor is Lexical; it accepts a
 *    synthetic paste and a full insertText as genuine,
 *    cancels synthetic beforeinput outright, and certifies
 *    registration by enabling its send button (disabled
 *    while its model is empty). _typeInto runs the
 *    paste-first ladder and delivery waits for that
 *    certificate — insertion is still never believed to be
 *    delivery: verify-type re-reads the box, and the
 *    newborn-bubble receipt alone confirms (Alex: "Do not
 *    assume successful DOM insertion means successful
 *    delivery").
 * The delivery engine (engage / button gate / element-
 * watching receipt) is the shared V6.1–V7.2 machinery,
 * inherited from the Claude/Gemini adapters; only the
 * platform primitives differ. Self-check reports live counts
 * so the first install verifies the candidates against the
 * real page. */
window.PB_ADAPTER = {
  seat: "alex",
  platform: "metaai",

  /* Identity on this surface is NOT a name — the box carries
   * no accessible name (probe: aria=null). Its identity is the
   * testid "composer-input" PLUS visibility PLUS being the
   * contenteditable (see findComposer). composerName stays
   * empty so no name-based path can ever engage the phantom
   * textarea by accident. */
  composerName: "",

  candidates: {
    messages: [
      "[data-message-item]",
    ],
    composer: [
      '[data-testid="composer-input"]',
    ],
    stop: [
      '[data-testid="composer-stop-button"]',
      'button[aria-label="Stop"]',
      '[data-testid*="stop"]',
    ],
    send: [
      '[data-testid="composer-send-button"]',
      'button[aria-label="Send"]',
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
                        "data-message-author-role", "role", "aria-label",
                        "data-user-message"]) {
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
    const items = document.querySelectorAll("[data-message-item]");
    if (items.length) {
      let n = items[0];
      for (let i = 0; i < 12 && n.parentElement; i++) {
        n = n.parentElement;
        if (n.querySelectorAll &&
            n.querySelectorAll("[data-message-item]").length >= items.length) {
          if (!n.parentElement ||
              !n.parentElement.querySelectorAll ||
              n.parentElement.querySelectorAll("[data-message-item]").length < items.length) {
            return n;
          }
        }
      }
      return items[0].parentElement || document.body;
    }
    const main = document.querySelector("main");
    if (main) return main;
    const inp = document.querySelector('[data-testid="composer-input"]');
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


  /* Structural anchors for the popup's read-only map: this
   * surface carries NO in-text nameplates (probe, phase 2) —
   * turns are attribute-marked, so there is no landmark string
   * to hunt. The empty landmarks are deliberate; the landmark
   * machinery below reports them as absent rather than
   * pretending a string exists. */
  landmarks: {
    assistant: "",
    ben: "",
  },

  /* Normalisation per Alex's ruling: collapse whitespace, trim,
   * preserve case; matching is exact after normalisation. */
  _normText(t) {
    return String(t == null ? "" : t).replace(/\s+/g, " ").trim();
  },

  _nodeInfo(el) {
    const attrs = {};
    for (const name of ["data-testid", "data-role", "data-author",
                        "data-message-author-role", "role", "aria-label",
                        "data-user-message"]) {
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
    if (!landmark) {
      return { landmark, found: false, containerCount: 0,
               note: "no in-text landmark on this surface — turns are attribute-marked (probe 2026-11-08)" };
    }
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
        containsAssistantLandmark: !!aNorm && t.includes(aNorm),
        containsBenLandmark: !!bNorm && t.includes(bNorm),
      });
    });
    return { total: all.length, shown: items.length, truncated: all.length > 50, items };
  },


  /* TURN CAPTURE (v0.3.0): the conversation region's text. The
   * trigger reads DELTAS of this text — never message containers.
   * (v0.4: captureTurnText remains only for the popup's live-state
   * readout; detection no longer uses it.) */
  regionEl() {
    return this._columnRoot() || document.body;
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
   * from a marker element to its enclosing turn element.
   * bubbleSpeaker reads the turn's own attribute markers —
   * identity from the page's structure, not from styling.
   * listBubbles enumerates the turns in document order for the
   * letterbox's history absorb and for the receipt's birth
   * watch. */
  get markerForSeat() { return PB_LETTERBOX.lbMarkerForSeat(this.seat); },

  bubbleOf(el) {
    if (!el || !el.closest) return null;
    return el.closest("[data-message-item]") ||
           el.closest('[data-user-message], [data-testid="assistant-message"]');
  },

  /* Speaker from the page's own marks (probe, phase 2): a user
   * turn carries [data-user-message] — on the item itself or on
   * a child; an assistant turn carries
   * data-testid="assistant-message", likewise. The user mark is
   * read first: a user item never carries the assistant mark. */
  bubbleSpeaker(bubble) {
    if (!bubble) return "unknown";
    const hasUser = (bubble.getAttribute && bubble.getAttribute("data-user-message") !== null) ||
      !!(bubble.querySelector && bubble.querySelector("[data-user-message]"));
    if (hasUser) return "user";
    const hasAssistant = (bubble.getAttribute && bubble.getAttribute("data-testid") === "assistant-message") ||
      !!(bubble.querySelector && bubble.querySelector('[data-testid="assistant-message"]'));
    if (hasAssistant) return "assistant";
    return "unknown";
  },

  listBubbles() {
    return Array.from(document.querySelectorAll("[data-message-item]"));
  },

  /* NO NAMEPLATE STRIPPING (Alex's requirement; probe phase 2):
   * the turn's innerText IS the message — Meta AI pins no label
   * and no echo onto it. What the letterbox and the receipt see
   * is the raw text; the strict bridge header + PB-ID
   * verification downstream does all the identity work. */
  bubbleText(bubble) {
    if (!bubble) return "";
    return bubble.innerText || "";
  },

  messageText(el) {
    return (el.innerText || "").trim();
  },

  isGenerating() {
    /* The witness is the stop face of the paired swap (Ben
     * caught it mid-stream, 2026-11-08): composer-stop-button
     * present while Meta AI generates, absent at rest in every
     * probe. No streaming attribute exists on this surface, so
     * the button is the testimony — and a page whose state
     * cannot be read still fails closed upstream
     * (composerButtonState never calls an unreadable page
     * "ready" without a send face). */
    return !!document.querySelector(this.candidates.stop.join(", "));
  },

  /* ---- THE COMPOSER: testid + visibility (this surface's
   * identity rule) ----
   * Alex's requirement, verbatim in effect: never engage the
   * hidden textarea; require the visible contenteditable,
   * nonzero dimensions and the correct testid. The probe found
   * testid "composer-input" on TWO elements at once — a 0x0
   * TEXTAREA (a form mirror the page keeps offstage) and the
   * visible contenteditable DIV a person actually types into.
   * A first-match lookup lands in the phantom box and the
   * letter dies silently there (the .ql-clipboard lesson,
   * second surface running) — so the finder below applies all
   * three tests and fails closed (null) when no element passes
   * them. Visibility here means real dimensions from
   * getBoundingClientRect: a rendered-but-zero-size box is
   * hidden for every purpose that matters. */
  _isVisible(el) {
    if (!el) return false;
    try {
      const r = el.getBoundingClientRect && el.getBoundingClientRect();
      if (r) return r.width > 0 && r.height > 0;
    } catch (e) { /* fall through to the rect-list test */ }
    if (typeof el.getClientRects === "function") return el.getClientRects().length > 0;
    return true; // minimal DOMs (fixtures): presence counts as visible
  },
  findComposer() {
    if (this._engagedComposer &&
        this._engagedComposer.getAttribute &&
        this._engagedComposer.getAttribute("data-testid") === "composer-input" &&
        this._engagedComposer.tagName !== "TEXTAREA" &&
        this._isVisible(this._engagedComposer)) {
      return this._engagedComposer;
    }
    const pool = Array.from(document.querySelectorAll('[data-testid="composer-input"]'));
    const hit = pool.find((el) =>
      el.tagName !== "TEXTAREA" &&
      (el.getAttribute("contenteditable") !== null || el.isContentEditable === true) &&
      this._isVisible(el));
    return hit || null;
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
   * button WEARS the page's state. On Meta AI the wear is a
   * paired swap (probe phase 3): the stop face REPLACES the
   * send face while the page generates — one slot, two buttons,
   * never both. v0.6.0's failure mode (clicking a stop face and
   * killing the reply) is impossible here only because the
   * state is read from the buttons themselves — by accessible
   * label / stable testid, re-queried live at every decision,
   * never from a stale reference. Delivery never engages, types,
   * or clicks while the destination is generating: it waits,
   * bounded by PB_CRUSHER_DEFER_MAX_MS, then stalls with the
   * reason named. */
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
  /* V0.10.1: the editor's registration certificate — a send
   * button that is not disabled. On Meta AI the button is
   * present-but-disabled while the editor's model is empty
   * (probe, 2026-11-08), so existence alone testifies to
   * nothing; enabled is the state that means "the editor
   * holds text it can send". */
  _buttonEnabled(b) {
    if (!b) return false;
    if (b.disabled) return false;
    if (b.getAttribute && b.getAttribute("aria-disabled") === "true") return false;
    return true;
  },
  /* The destination's generation state as the interface itself
   * reports it: "generating" while a stop face shows (in the
   * engaged composer's own neighbourhood ONLY — v0.18.0: this
   * read was narrowed to the composer, exactly as v0.17.0 did
   * on the ChatGPT surface; the whole page no longer testifies
   * at a send decision, and isGenerating() no longer feeds it),
   * "ready" when a send face shows and no stop face does,
   * "unknown" when neither face can be found. On this surface
   * "ready" is well-defined precisely because the swap is
   * paired: send restored IS the rest state (Alex's completion
   * condition reads it directly). */
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
   *     opening line.
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
    return { ok: false, stage: "receipt", verdict: "unknown", error: "no confirming turn could be observed — the destination page was not quiet and readable through the receipt window" };
  },
  async deliverText(text) {
    // V6.1 deference (Alex step 3): never engage a destination
    // that is still generating — wait it out, bounded, or stall.
    const defer = await this._waitForDestinationIdle();
    if (!defer.ok) return defer;
    const composer = this.engageComposer();
    if (!composer) return { ok: false, stage: "composer", error: "composer not found (testid + visible + contenteditable — the hidden textarea is never engaged)" };
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
    /* V0.10.1 (the delivery probe's witness): on this surface
     * the send button EXISTS while the editor is still empty —
     * wearing disabled=true. v0.10.0 waited only for existence,
     * clicked a present-but-disabled button, and the click did
     * nothing: the seat test's "pasted but not sent". The
     * button leaving the disabled state is the editor's own
     * certificate that it holds the text in its model, so the
     * wait below is for an ENABLED button — existence earns
     * nothing. A button that never enables means the editor
     * never registered the insertion, whatever the DOM shows:
     * stall at stage "editor" and click nothing. (The wait
     * still watches for generation, as V6.2 taught.) */
    const btnWaitMs = (typeof window !== "undefined" && window.PB_TEST_BUTTON_WAIT_MS) || 5000;
    const btnWaitStart = Date.now();
    let btn = this.findSendButton();
    while (!(btn && this._buttonEnabled(btn)) && Date.now() - btnWaitStart < btnWaitMs) {
      if (this._destinationGenerating()) {
        return { ok: false, stage: "generating", error: "destination began generating while waiting for its send button — the click was not made" };
      }
      await new Promise((r) => setTimeout(r, 250));
      btn = this.findSendButton();
    }
    if (!btn) return { ok: false, stage: "send-button", error: "send button not found after typing" };
    if (!this._buttonEnabled(btn)) {
      return { ok: false, stage: "editor", error: "the text is in the box but the editor never enabled its send button — it did not register the insertion in its model; nothing was clicked" };
    }
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

  /* Meta AI typing — v0.10.1, rebuilt on the delivery probe
   * (Ben's console, 2026-11-08 ~01:50 PST; Ben's tap, Remmy's
   * hands, no Alex gate). The composer is a LEXICAL editor
   * (data-lexical-editor="true" on the box), and the probe
   * settled what it accepts as genuine:
   *   - a synthetic PASTE event: the editor's own handler
   *     takes the text (preventing the default), structures
   *     it into its model, and enables its send button.
   *     Editor-authored insertion — the most native path a
   *     script can offer this framework, and the only one
   *     whose multi-line handling is the editor's own.
   *   - a full-string execCommand("insertText"): genuine on
   *     the probed (single-line) string — send enabled. Its
   *     multi-line behaviour was not probed, so the ladder
   *     carries a line-wise variant between the two
   *     (insertText per line, insertParagraph between),
   *     which speaks the editor's paragraph language.
   *   - per-character insertText: BROKEN — the editor's
   *     re-render orphans the caret after the first char.
   *     Never used.
   *   - a synthetic beforeinput/input sequence: CANCELLED by
   *     the editor — in the live seat test (v0.10.0, three
   *     attempts, final) and again in the probe. REMOVED in
   *     v0.10.1: not a fallback, a wall.
   * The ladder tries paste, then line-wise insert, then the
   * full insert; every path is verified against the box's
   * text before it is believed, and a landed insertion is
   * STILL not a delivery: deliverText re-verifies the box
   * (verify-type), then waits for the editor's own
   * certificate — its send button leaving the disabled state
   * (stage "editor") — and the newborn-bubble receipt alone
   * confirms. */
  _selectComposerContents(composer) {
    try {
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(composer);
      sel.removeAllRanges();
      sel.addRange(range);
    } catch (e) { /* selection aids the paths; every path verifies, so a failed selection fails closed downstream */ }
  },
  async _typeInto(composer, text) {
    // Path 1 — the paste the editor takes itself.
    try {
      if (typeof DataTransfer !== "undefined" && typeof ClipboardEvent !== "undefined") {
        this._selectComposerContents(composer);
        const dt = new DataTransfer();
        dt.setData("text/plain", text);
        composer.dispatchEvent(new ClipboardEvent("paste", {
          bubbles: true, cancelable: true, clipboardData: dt,
        }));
        await new Promise((r) => setTimeout(r, 120));
        if (PB.pbTextsMatch(this._composerText(composer), text)) return { ok: true };
      }
    } catch (e) { /* the paste path is unavailable here — fall through to the inserts */ }
    // Path 2 — line-wise insertText, in the editor's paragraph language.
    try {
      if (typeof document !== "undefined" && document.execCommand) {
        this._selectComposerContents(composer);
        try { document.execCommand("delete", false, null); } catch (e) { /* an empty box needs no clearing */ }
        const lines = String(text).split("\n");
        let ran = false;
        for (let i = 0; i < lines.length; i++) {
          if (i > 0 &&
              !document.execCommand("insertParagraph", false, null)) {
            document.execCommand("insertLineBreak", false, null);
          }
          if (lines[i]) { document.execCommand("insertText", false, lines[i]); ran = true; }
        }
        if (ran && PB.pbTextsMatch(this._composerText(composer), text)) return { ok: true };
      }
    } catch (e) { /* fall through to the full insert */ }
    // Path 3 — the full-string native insert (v0.10.0's path 1).
    try {
      if (typeof document !== "undefined" && document.execCommand) {
        this._selectComposerContents(composer);
        try { document.execCommand("delete", false, null); } catch (e) { /* an empty box needs no clearing */ }
        const okIns = document.execCommand("insertText", false, text);
        if (okIns && PB.pbTextsMatch(this._composerText(composer), text)) return { ok: true };
      }
    } catch (e) { /* fall through to the failure */ }
    return { ok: false, stage: "type", error: "insertion did not land by the paste, line-wise, or full-insert paths" };
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
   * adapter gets verified: numbers from the real page, not guesses.
   * The composerTestid census exists for this surface's double:
   * how many elements wear the testid, how many are visible, how
   * many are textareas — the phantom made countable. */
  selfCheck() {
    const counts = {};
    for (const group of ["messages", "composer", "stop", "send"]) {
      counts[group] = {};
      for (const s of this.candidates[group]) {
        counts[group][s] = document.querySelectorAll(s).length;
      }
    }
    const composers = Array.from(document.querySelectorAll('[data-testid="composer-input"]'));
    const found = this.findComposer();
    return {
      platform: this.platform,
      seat: this.seat,
      url: location.href,
      title: document.title,
      matched: {
        messages: this._firstMatch(this.candidates.messages).selector,
        composer: found ? '[data-testid="composer-input"] (visible contenteditable)' : null,
      },
      composerName: this.composerName || "",
      composerByName: false,
      composerTestid: {
        total: composers.length,
        visible: composers.filter((el) => this._isVisible(el)).length,
        textareas: composers.filter((el) => el.tagName === "TEXTAREA").length,
        engaged: !!found,
      },
      sendEnabled: (() => {
        const b = this.findSendButton();
        return b ? this._buttonEnabled(b) : null;
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
