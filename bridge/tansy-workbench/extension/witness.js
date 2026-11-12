"use strict";
/* Pulse Bridge — MUTATION WITNESS (v0.3.2, diagnostic only).
 *
 * Alex's ruling (2026-11-06 21:22): arrival capture is approved as
 * the next design CANDIDATE, its premise to be proven by witnesses
 * first — the static structural read (already in the adapters) plus
 * THIS: a live watch over one complete generation cycle.
 *
 * The witness observes the conversation region continuously —
 * childList AND characterData, subtree on — because an app may build
 * a message three ways: insert a complete subtree, insert an empty
 * shell then fill it, or reuse an element and mutate its text. It
 * records NUMBERS, BOOLEANS AND LABELS ONLY: counts, lengths, event
 * ordering, structural paths, tag/class labels. It NEVER records
 * message text. The reserved marker is searched for, never quoted:
 * the record carries "found", a line index, and lengths — nothing
 * else about the content.
 *
 * It changes NOTHING: detection stays the v0.3.0 turn-capture loop,
 * sending stays locked off. The witness watches births and takes
 * notes; Alex reads the notes before any production arrival
 * detector is designed.
 */
(function () {
  const MAX_CYCLES = 3;      // closed cycles retained
  const MAX_EVENTS = 60;     // timeline entries per cycle
  const MAX_CANDIDATES = 5;  // candidate subtrees per cycle
  const MAX_CHAIN = 20;      // ancestor chain entries (Alex's cap)
  const MIN_CANDIDATE_CHARS = 20;
  const GROSS_GROWTH_CHARS = 200; // region growth that opens a no-generation cycle

  function clsOf(el) {
    const cn = (el.className && el.className.baseVal !== undefined)
      ? el.className.baseVal : String((el && el.className) || "");
    return cn.slice(0, 60);
  }

  /* Structural path of element-child indexes from the region root. */
  function pathOf(el, stopAt) {
    const parts = [];
    let n = el;
    while (n && n !== stopAt && n.parentElement) {
      const p = n.parentElement;
      parts.unshift(Array.prototype.indexOf.call(p.children, n));
      n = p;
      if (parts.length > 40) break;
    }
    return parts.join(".");
  }

  function elementOf(node) {
    if (!node) return null;
    if (node.nodeType === 1) return node;
    return node.parentElement || null;
  }

  function PB_WITNESS(adapter) {
    let observer = null;
    let pollTimer = null;
    let running = false;

    let region = null;
    let lastIdleTextLen = null;
    let lastPollText = null;   // settle tracking inside a cycle
    let quietReads = 0;
    let totalReads = 0;
    let gen = false;

    const cycles = [];
    let cur = null;
    const totals = { batches: 0, mutations: 0, batchesOutsideRegion: 0, regionMissing: 0 };

    function tNow() { return Date.now(); }

    function pushEvent(c, label) {
      if (c.timeline.length >= MAX_EVENTS) { c.timelineTruncated = true; return; }
      c.timeline.push({ seq: c.eventSeq++, tMs: tNow() - c.openedAtMs, label });
    }

    function openCycle(trigger) {
      const now = tNow();
      cur = {
        openedAt: new Date(now).toISOString(),
        openedAtMs: now,
        trigger,                    // "generation" | "growth-no-generation-flag"
        eventSeq: 0,
        timeline: [],
        timelineTruncated: false,
        genObserved: trigger === "generation",
        genStartSeen: trigger === "generation",
        genEndSeen: false,
        settleStarted: false,
        settleCompleted: false,
        quietReads: 0,
        totalReads: 0,
        mutations: 0,
        childListRecords: 0,
        characterDataRecords: 0,
        addedNodes: 0,
        removedNodes: 0,
        textEdits: 0,
        regionTextStart: null,
        regionTextPeak: 0,
        regionTextFinal: null,
        markerFound: false,
        markerFoundAtEvent: null,
        markerSubtrees: [],
        markerChain: [],
        candidates: [],
        noCandidateReason: null,
        _addedRoots: new Set(),
        _grown: new Map(),
        _firstGrowthSeen: false,
        _markerSearchedText: "",
      };
      pushEvent(cur, trigger === "generation" ? "cycle-open:generation-flag" : "cycle-open:growth-no-generation-flag");
      const startText = safeRegionText();
      cur.regionTextStart = startText.length;
      cur.regionTextPeak = startText.length;
      cur._markerSearchedText = startText;
      lastPollText = startText;
      quietReads = 0; totalReads = 0;
    }

    function safeRegionText() {
      try { return adapter.captureTurnText() || ""; } catch (e) { return ""; }
    }

    function refreshRegion() {
      try { region = adapter.regionEl(); } catch (e) { region = null; }
      return region;
    }

    /* Find the deepest elements whose text contains the marker.
     * Returns up to 3, in document order. Elements only — the marker
     * itself is never copied into the record. */
    function deepestMarkerContainers(root, marker) {
      const hits = [];
      for (const el of root.querySelectorAll("*")) {
        const t = el.innerText || "";
        if (t.includes(marker)) hits.push(el);
      }
      const set = new Set(hits);
      return hits.filter((el) =>
        !Array.from(el.querySelectorAll("*")).some((d) => set.has(d))).slice(0, 3);
    }

    function noteMarker(reg, text) {
      if (!cur || cur.markerFound) return;
      for (const m of PB.PB_MARKERS) {
        if (!text.includes(m.marker)) continue;
        cur.markerFound = true;
        cur.markerFoundAtEvent = cur.eventSeq;
        pushEvent(cur, "marker-first-seen");
        const deep = deepestMarkerContainers(reg, m.marker);
        cur.markerSubtrees = deep.map((el) => ({
          path: pathOf(el, reg),
          tag: el.tagName ? el.tagName.toLowerCase() : "?",
          cls: clsOf(el),
          textLen: (el.innerText || "").length,
        }));
        if (deep.length) {
          const chain = [];
          let n = deep[deep.length - 1];
          while (n && chain.length < MAX_CHAIN) {
            chain.push({
              tag: n.tagName ? n.tagName.toLowerCase() : "?",
              cls: clsOf(n),
              textLen: (n.innerText || "").length,
            });
            if (n === reg) break;
            n = n.parentElement;
          }
          cur.markerChain = chain;
        }
        return;
      }
    }

    function onMutations(records) {
      totals.batches++;
      const reg = refreshRegion();
      if (!reg) { totals.regionMissing++; return; }
      let inside = 0;
      for (const r of records) {
        let relevant = false;
        try {
          relevant = r.target === reg || reg.contains(r.target);
          if (!relevant && r.addedNodes) {
            for (const n of r.addedNodes) {
              if (n === reg || (n.nodeType === 1 && reg.contains(n))) { relevant = true; break; }
            }
          }
        } catch (e) { relevant = false; }
        if (!relevant) continue;
        inside++;
        totals.mutations++;
        if (!cur) continue; // outside a cycle: the poll loop opens cycles
        cur.mutations++;
        if (r.type === "childList") {
          cur.childListRecords++;
          cur.addedNodes += r.addedNodes ? r.addedNodes.length : 0;
          cur.removedNodes += r.removedNodes ? r.removedNodes.length : 0;
          if (r.addedNodes) {
            for (const n of r.addedNodes) {
              if (n.nodeType === 1) cur._addedRoots.add(n);
            }
          }
        } else if (r.type === "characterData") {
          cur.characterDataRecords++;
          cur.textEdits++;
          const el = elementOf(r.target);
          if (el) cur._grown.set(el, (cur._grown.get(el) || 0) + 1);
        }
      }
      if (!inside) { totals.batchesOutsideRegion++; return; }
      if (!cur) return;
      const text = safeRegionText();
      if (text.length > cur.regionTextPeak) cur.regionTextPeak = text.length;
      if (!cur._firstGrowthSeen && text.length > (cur.regionTextStart || 0)) {
        cur._firstGrowthSeen = true;
        pushEvent(cur, "first-region-growth");
      }
      if (text !== cur._markerSearchedText) {
        cur._markerSearchedText = text;
        noteMarker(reg, text);
      }
    }

    function candidateInfo(el, reg, origin) {
      const raw = el.innerText || "";
      const norm = PB.pbNormTurn(raw);
      const lines = norm.split("\n");
      let firstNonBlank = -1;
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].trim() !== "") { firstNonBlank = i; break; }
      }
      let markerLineIndex = -1;
      let markerFirstLine = false;
      for (let i = 0; i < lines.length; i++) {
        for (const m of PB.PB_MARKERS) {
          if (lines[i].includes(m.marker)) {
            if (markerLineIndex === -1) markerLineIndex = i;
            if (i === firstNonBlank && lines[i].trim() === m.marker) markerFirstLine = true;
          }
        }
      }
      return {
        origin,
        path: pathOf(el, reg),
        tag: el.tagName ? el.tagName.toLowerCase() : "?",
        cls: clsOf(el),
        textLen: raw.length,
        firstLineLen: firstNonBlank >= 0 ? lines[firstNonBlank].length : 0,
        markerInText: markerLineIndex !== -1,
        markerLineIndex,
        markerFirstLine,
      };
    }

    function closeCycle() {
      const reg = region;
      const text = safeRegionText();
      cur.regionTextFinal = text.length;
      cur.quietReads = quietReads;
      cur.totalReads = totalReads;
      if (reg) {
        const picked = new Map();
        for (const el of cur._addedRoots) {
          try { if (reg.contains(el)) picked.set(el, "added"); } catch (e) { /* detached */ }
        }
        for (const [el, hits] of cur._grown) {
          if (hits < 3) continue;
          try { if (reg.contains(el) && !picked.has(el)) picked.set(el, "grown"); } catch (e) { /* detached */ }
        }
        // An added root that only wraps a picked descendant adds no
        // information: keep the deepest picked node per branch.
        const els = Array.from(picked.keys());
        const deepest = els.filter((el) => !els.some((o) => o !== el && el.contains(o)));
        const infos = deepest
          .map((el) => candidateInfo(el, reg, picked.get(el)))
          .filter((i) => i.textLen >= MIN_CANDIDATE_CHARS)
          .sort((a, b) => b.textLen - a.textLen)
          .slice(0, MAX_CANDIDATES);
        cur.candidates = infos;
        if (!infos.length) {
          cur.noCandidateReason = cur.mutations === 0
            ? "no-mutations-inside-region"
            : "no-subtree-reached-minimum-size";
        }
        const marked = infos.find((i) => i.markerFirstLine);
        cur.payloadShapeExtractable = !!marked;
      } else {
        cur.noCandidateReason = "region-not-found";
        cur.payloadShapeExtractable = false;
      }
      pushEvent(cur, "cycle-close");
      delete cur._addedRoots;
      delete cur._grown;
      delete cur._firstGrowthSeen;
      delete cur._markerSearchedText;
      delete cur.openedAtMs;
      cycles.push(cur);
      while (cycles.length > MAX_CYCLES) cycles.shift();
      cur = null;
      quietReads = 0; totalReads = 0; lastPollText = null;
    }

    function poll() {
      const reg = refreshRegion();
      let isGen = false;
      try { isGen = !!adapter.isGenerating(); } catch (e) { isGen = false; }
      if (!reg) { lastIdleTextLen = null; gen = isGen; return; }
      const text = safeRegionText();

      if (!cur) {
        if (isGen) {
          openCycle("generation");
        } else if (lastIdleTextLen !== null &&
                   text.length - lastIdleTextLen >= GROSS_GROWTH_CHARS) {
          openCycle("growth-no-generation-flag");
        }
        lastIdleTextLen = text.length;
        gen = isGen;
        return;
      }

      // Inside a cycle.
      totalReads++;
      if (text.length > cur.regionTextPeak) cur.regionTextPeak = text.length;
      if (text !== cur._markerSearchedText) {
        cur._markerSearchedText = text;
        noteMarker(reg, text);
      }
      if (isGen && !gen) {
        cur.genObserved = true;
        if (!cur.genStartSeen) { cur.genStartSeen = true; pushEvent(cur, "generation-flag-on"); }
      }
      if (!isGen && gen && cur.genStartSeen && !cur.genEndSeen) {
        cur.genEndSeen = true;
        cur.settleStarted = true;
        pushEvent(cur, "generation-flag-off:settle-begins");
      }
      gen = isGen;

      const settling = cur.genStartSeen ? !isGen : true;
      if (!settling) { lastPollText = text; quietReads = 0; return; }
      if (lastPollText !== null && PB.pbTextsMatch(lastPollText, text)) {
        quietReads++;
        if (quietReads === 1) pushEvent(cur, "first-quiet-read");
      } else {
        quietReads = 0;
      }
      lastPollText = text;
      if (quietReads >= 2) {
        cur.settleCompleted = true;
        closeCycle();
        lastIdleTextLen = text.length;
      }
    }

    return {
      start() {
        if (running) return;
        running = true;
        refreshRegion();
        try { lastIdleTextLen = safeRegionText().length; } catch (e) { lastIdleTextLen = null; }
        observer = new MutationObserver(onMutations);
        observer.observe(document.body, { childList: true, subtree: true, characterData: true });
        pollTimer = setInterval(poll, 500);
      },
      getSnapshot() {
        return {
          version: "0.3.2",
          seat: adapter.seat,
          platform: adapter.platform,
          url: location.href,
          totals,
          liveCycle: cur ? {
            trigger: cur.trigger,
            genObserved: cur.genObserved,
            mutations: cur.mutations,
            addedNodes: cur.addedNodes,
            textEdits: cur.textEdits,
            markerFound: cur.markerFound,
          } : null,
          cycles,
        };
      },
    };
  }

  window.PB_WITNESS = PB_WITNESS;
})();
