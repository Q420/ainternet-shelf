"use strict";
/* Pulse Bridge — the letterbox (v0.6.3).
 *
 * The smallest machine that solves the handoff problem, per Alex's
 * revised direction (2026-11-06): "The marker tells us there's a
 * handoff. The bubble tells us what to carry. The bubble's identity
 * tells us who sent it."
 *
 *   1. Watch the conversation region for changed content.
 *   2. Look specifically for the seat's RESERVED marker in the
 *      changed nodes.
 *   3. From the marker, climb to the enclosing message bubble.
 *   4. Verify the bubble belongs to the ASSISTANT (per-adapter check)
 *      — a user's bubble can never fire, even with a perfect marker.
 *   5. Verify the marker is the bubble's FIRST line.
 *   6. Wait until the letter's TEXT stops changing: stability is
 *      tracked by the exact text, never by DOM element identity —
 *      every settle check re-queries the bubble fresh from the live
 *      page, and the text must stay identical across the whole
 *      quiet window before anything is verified or carried
 *      (settle-wait fix, Ben's ruling 2026-11-06 22:58 — a bubble
 *      whose element the page replaces mid-render is re-found by
 *      its text; a node that vanishes simply stays pending).
 *   7. Extract the complete bubble text, remove the marker,
 *      and emit ONE held envelope.
 *
 * What is deliberately NOT here: no whole-transcript comparison,
 * no candidate ranking by size, no region diffing. History is
 * never scanned: at startup, every bubble already on the page is
 * absorbed into the seen-set.
 *
 * V6.1 amendment (Alex step 2): the letterbox still builds no
 * generation detector of its own, but the HANDOFF now defers to
 * the adapter's isGenerating() signal — a textually settled
 * letter does not leave while the source page is still
 * generating, and its quiet window re-runs from the end of
 * generation. (In v0.5.1 a mid-generation pause longer than the
 * quiet window could settle a partial letter; the completed
 * letter was then suppressed as "still growing".)
 *
 * V6.3 (Alex's four-stage design, Ben's tap 2026-11-07 02:56):
 * the V6.1 settle still shipped partials live — three of Alex's
 * letters cut at three different lengths in one night. Its two
 * questions were each asked ONCE (one quiet window, one snapshot
 * generation read), it shipped the CACHED text, and growth-
 * suppression then forbade the completed letter from following.
 * Capture is now four explicit stages. OBSERVE: a per-letter
 * loop re-reads the live page on a cadence and records every
 * observation in a settle trail. SETTLE: a letter settles only
 * after LB_MIN_CLEAN_OBS consecutive clean observations (text
 * unchanged, generation off, page readable) spanning the whole
 * quiet window — any growth or generation resets the streak, so
 * one flickered snapshot can never ship a letter. VERIFY: one
 * final live re-read at the gate; what ships is that read (or,
 * when the bubble is momentarily unfindable, the streak-verified
 * text, recorded as such in the trail) — growth found at the
 * gate restarts the settle. COMMIT: the handoff carries the
 * verified payload plus its completeness evidence (observation
 * count, span, verify mode, dispatch length, the trail itself).
 * SUPERSEDE replaces growth-suppression: a letter that grows
 * after a capture travels as a new letter carrying the captured
 * body's fingerprint as its lineage (supersedesFingerprint);
 * the partial is marked superseded downstream, never silently
 * dropped, and a supersede never counts as an independent
 * second message.
 *
 * V0.10.2 — THE BASELINE (Ben's diagnosis + tap, 2026-11-08
 * 02:17–02:19): the pair machine FORGETS a retired letter on
 * purpose (background forgetDetection), so the only guard
 * against a page reload re-firing an old letter was absorb()
 * — one synchronous pass at start, over whatever bubbles exist
 * at that instant. A bubble that hydrates late, or was missed
 * by that pass, was then considered as a fresh sighting and
 * re-carried under a NEW PB-ID (exhibit: Alex's v0.10.0 ruling
 * re-delivered 2026-11-08 02:11, pb-mw7oa3ga, after the seat
 * swaps). Ben's rule: the fetcher may only trigger on a message
 * that comes up NEW. So: at start() the letterbox enters a
 * BASELINE WINDOW (mutation-quiet closes it; hard cap applies).
 * Letters first sighted during the window are flagged and may
 * NOT commit while it is open. When it closes, each flagged
 * letter is judged: a body fingerprint present in the seen
 * record (the persistent delivered ledger, seeded from the
 * background) means history — dropped; a letter whose bubble
 * sits BURIED under later turns is history by construction —
 * dropped; anything else is a stranded letter (posted while
 * the tab was closed or the bridge off) and is released to
 * carry exactly once, after which the record holds it and no
 * reload can ever re-fire it. Mid-generation at load is
 * pending, never history: absorb() stands down while the page
 * is generating, so a still-streaming letter is never
 * snapshotted into the seen-set.
 *
 * Loaded by the content script (window.PB_LETTERBOX) and by the
 * fixture tests (module.exports guard). The detector half is pure
 * logic over a minimal DOM-ish interface (querySelectorAll /
 * closest / innerText / children / classList-ish strings and the
 * adapter callbacks), so the fixture can drive it with a fake DOM.
 */

const LB_SETTLE_MS = 5000;          // V6.3: quiet window the clean streak must span
const LB_OBSERVE_MS = 500;          // V6.3: settle-trail observation cadence
const LB_MIN_CLEAN_OBS = 3;         // V6.3: consecutive clean observations required to settle
const LB_TRAIL_CAP = 160;           // V6.3: observations kept per trail (counters stay exact)
const LB_RESCAN_MS = 2500;          // idle re-scan cadence (safety net)
const LB_MAX_PENDING = 8;           // concurrent letters tracked, max
const LB_BASELINE_MIN_MS = 4000;    // V0.10.2: baseline window minimum span
const LB_BASELINE_QUIET_MS = 3000;  // V0.10.2: mutation quiet that closes the window
const LB_BASELINE_MAX_MS = 20000;   // V0.10.2: baseline window hard cap
const PB_ACK_DELAYS_MS = [2000, 5000, 12000]; // v0.22.0 Part 2: handoff-answer retry schedule (3 retries after the first attempt)

/* The marker line and the marker element: given an element whose
 * text contains a reserved marker, return the deepest elements that
 * contain it (the marker's own line elements — usually one <p>). */
function lbMarkerElements(rootEl, marker) {
  if (!rootEl || !rootEl.querySelectorAll) return [];
  const hits = [];
  for (const el of rootEl.querySelectorAll("*")) {
    const t = el.innerText || "";
    if (t.includes(marker)) hits.push(el);
  }
  const set = new Set(hits);
  return hits.filter((el) =>
    !Array.from(el.querySelectorAll("*")).some((d) => set.has(d)));
}

/* First non-blank line of a text block, trimmed. */
function lbFirstLine(text) {
  const lines = String(text || "").split(/\r?\n/);
  for (const l of lines) if (l.trim() !== "") return l.trim();
  return "";
}

/* Does this bubble's text open with the reserved marker as its first
 * line? (Line 0 only — a marker quoted on line 2 never counts.)
 * Kept for the fixtures that cite it; routing itself is governed by
 * the v0.12.0 delimiter rule (lbHasStandaloneMarker / pbParseMarker). */
function lbMarkerFirstLine(text, marker) {
  return lbFirstLine(text) === marker;
}

/* V0.12.0 DELIMITER RULE (Ben, 2026-11-08): does this text contain
 * the marker as a STANDALONE line anywhere — the routing test that
 * replaced the first-line requirement? A marker inside a sentence
 * does not count; the line must equal the marker exactly. */
function lbHasStandaloneMarker(text, marker) {
  for (const l of String(text || "").split(/\r?\n/)) {
    if (l.trim() === marker) return true;
  }
  return false;
}

/* Create a detector bound to one page's adapter + callbacks.
 *   adapter:   { seat, regionEl(), listBubbles(), bubbleSpeaker(el),
 *                markerForSeat, isGenerating() [optional — V6.1:
 *                while it reports true, no letter hands off and
 *                the settle quiet window re-runs from the end of
 *                generation] }
 *   onHandoff: function(envelope-ish {from,to,body,fingerprint})
 *   seenSeed:  array of fingerprints already known (background ledger)
 * The detector owns: the pending (settling) set and the seen-set.
 * It never sends anything itself; it only calls onHandoff. */
function pbCreateLetterbox({ adapter, onHandoff, onDrop, seenSeed, tokenSource, ackDelaysMs }) {
  const marker = adapter.markerForSeat;
  /* V0.13.0: Crusher's marker is watched on BOTH seats' pages
   * alongside the pair marker — a bubble whose only marker is
   * TO-CRUSHER is bridge traffic too (the background lanes it to
   * the retrieval occupant's desk on Remmy's side). Everything
   * downstream (settle, speaker verdict, parse) is shared; the
   * parse resolves which destination a settled bubble is for. */
  const crusherMarker = PB.PB_MARKERS.find((m) => m.to === "crusher") || null;
  /* Every marker text this page watches for (the pair marker plus
   * Crusher's): element searches, scans and the absorb skip all
   * run over the same list, so a crusher bubble is found, pends
   * and is judged exactly like a pair letter. */
  const watchTexts = crusherMarker ? [marker.text, crusherMarker.marker] : [marker.text];
  /* The standalone marker line a text carries, if any (the
   * v0.12.0 delimiter test over the whole marker table). */
  const standaloneMarkerOf = (text) => {
    for (const line of String(text || "").split(/\r?\n/)) {
      const t = line.trim();
      for (const m of PB.PB_MARKERS) if (t === m.marker) return m.marker;
    }
    return null;
  };
  const seen = new Set(seenSeed || []);
  /* V0.12.1: the delivered record exactly as the background
   * seeded it — the ONLY fingerprints the baseline judge may
   * treat as "already handled". The live `seen` set also
   * collects this page run's own sightings and absorptions;
   * it is not a delivery record and the judge no longer
   * consults it. */
  const deliveredSeed = new Set(seenSeed || []);
  /* V0.12.1: every settled letter this detector decides NOT to
   * hand off is reported through onDrop (when the host wires
   * one) — reason + first body line. A settled letter vanishing
   * without a trace was the bridge's original sin; drops are
   * now events with a record, never silence. A drop report must
   * never break capture, so it is wrapped. */
  const reportDrop = (reason, firstLine) => {
    if (typeof onDrop !== "function") return;
    try { onDrop({ reason, firstLine: firstLine || "", seat: adapter.seat }); } catch (e) { /* reporting never breaks capture */ }
  };
  /* CRUSHER (v0.6.0): this letterbox is the officer's SENSOR. Its
   * sightings are Crusher's first states — OBSERVING (region
   * watched), CAPTURING (a marked bubble sighted), SETTLING (the
   * quiet window running), VERIFIED (settled + speaker verified:
   * the handoff below). Crusher's own record begins at VERIFIED
   * in the background; the states before it live here, in the
   * sensor's bookkeeping, deliberately unchanged from v0.5.1. */
  /* Pending letters are keyed by FINGERPRINT (the letter's text
   * identity), never by DOM element (v0.5.1 settle fix). A bubble
   * element the page replaces mid-render is re-found by its text;
   * an element that vanishes leaves the letter pending until the
   * same text is seen again or the entry is superseded. */
  const pending = new Map(); // fingerprint -> entry {key, text, lastChangedAt, firstSeenAt, timer, cleanStreak, obsCount, genOnCount, changeCount, trail, _lastLen}
  /* V6.3: handed-off bodies by normalised text -> body fingerprint.
   * A settled body that strictly EXTENDS one of these is that
   * letter still growing: it travels as a SUPERSEDE carrying the
   * earlier body's fingerprint as lineage (see commit()). */
  const handedOff = new Map(); // normalised body -> bodyFingerprint
  /* V0.12.1: normalised body -> the first body line it carried.
   * pbNormalise flattens line breaks, so a handed-off body's
   * first line cannot be recovered from its key — the twin rule
   * below needs it recorded at handoff time. */
  const handedOffLines = new Map();
  const inflightLines = new Set(); // first body lines of handed-off letters
  /* CONCLUSION BUILD (v0.22.0), Part 2 — NO SILENT EXIT: a
   * handoff is not complete when it is SENT, it is complete
   * when the background ANSWERS. Committed letters wait here,
   * keyed by body fingerprint, until the answer lands in one of
   * the four classes (accepted / duplicate-terminal / rejected /
   * unanswered). The handed-off marking (seen + handedOff) is
   * applied ONLY on accepted or duplicate answers — a letter
   * the background never accepted is never marked, retries on
   * this bounded schedule, and its final failure is reported
   * through onDrop like every other letterbox decision. A host
   * whose onHandoff returns no promise keeps the pre-v0.22.0
   * semantics (fire-and-forget counts as accepted) — the real
   * host (content.js) always answers. */
  const awaitingAck = new Map(); // bodyFp -> {payload, bodyFp, textFp, normBody, firstLine, attempts, timer}
  const ackDelays = Array.isArray(ackDelaysMs) && ackDelaysMs.length ? ackDelaysMs.slice() : PB_ACK_DELAYS_MS.slice();

  function confirmAck(ackEntry) {
    awaitingAck.delete(ackEntry.bodyFp);
    if (ackEntry.timer) { clearTimeout(ackEntry.timer); ackEntry.timer = null; }
    seen.add(ackEntry.bodyFp);
    seen.add(ackEntry.textFp);
    handedOff.set(ackEntry.normBody, ackEntry.bodyFp);
    handedOffLines.set(ackEntry.normBody, ackEntry.firstLine);
    if (ackEntry.firstLine) inflightLines.add(ackEntry.firstLine);
  }

  function settleAck(ackEntry, answer) {
    if (!awaitingAck.has(ackEntry.bodyFp)) return; // superseded by its own growth, or already settled
    const cls = answer && answer.answerClass;
    if (cls === "accepted" || cls === "duplicate") { confirmAck(ackEntry); return; }
    if (ackEntry.attempts <= ackDelays.length) {
      const delay = ackDelays[ackEntry.attempts - 1];
      ackEntry.timer = setTimeout(() => { ackEntry.timer = null; attemptAck(ackEntry); }, delay);
    } else {
      awaitingAck.delete(ackEntry.bodyFp);
      reportDrop(`handoff unconfirmed — the background did not accept this letter after ${ackEntry.attempts} attempts (last answer: ${cls || "none"}); it is NOT marked handed off and can pend again on a later scan`, ackEntry.firstLine);
    }
  }

  function attemptAck(ackEntry) {
    if (!awaitingAck.has(ackEntry.bodyFp)) return;
    ackEntry.attempts++;
    let res;
    try { res = onHandoff(ackEntry.payload); } catch (e) { res = null; }
    if (res && typeof res.then === "function") {
      res.then((ans) => settleAck(ackEntry, ans), () => settleAck(ackEntry, null));
    } else {
      settleAck(ackEntry, { answerClass: "accepted", legacy: true });
    }
  }
  let started = false;
  /* While the page is streaming, bubble elements hold the LATEST
   * text only transiently — an early read often catches the grow-
   * ing EDGE of a bubble (its last paragraph) rather than the whole
   * bubble. Such a partial read must not poison this letter's
   * settle: in a streaming conversation the marker only becomes
   * visible at the edge once (at the marker's own line), so later
   * scans may never re-find the complete letter. The letterbox
   * therefore remembers the longest read it has seen per marker
   * line (its "best read"): a grown or complete read supersedes,
   * and the settle check resolves against the best read rather
   * than demanding an exact-text twin exist on the page right now. */
  let bestReadText = null;    // longest marker-led text seen this run
  /* Delivery-shape identity (v0.5.1): sibling turns of one letter
   * distinguished by their SHARED first body line — the bridge's
   * first-live-night failure had exactly this shape (a user turn and
   * an assistant turn both carrying an identical marked line: the
   * user's copy is a paste/quote, the assistant's is the answer).
   * The confirmed speaker verdict is recorded per first body line
   * from the SIGHTINGS themselves (node-based bubbleSpeaker in
   * consider()), so when a marked letter settles, its speaker is
   * decided by what was actually seen carrying that letter — never
   * by a similarity guess between differently-shaped texts. */
  const sightings = new Map(); // first body line -> Set of speakers seen carrying it
  /* V0.10.2 BASELINE state: the window opens at start(). While
   * it is open, new pending entries are flagged `baseline` and
   * commitLetter defers them; closeBaseline() judges them
   * (record / buried-under-later-turns / stranded-release).
   * baselineLastActivityAt moves on mutation batches and on
   * new sightings — the idle rescan alone never holds the
   * window open. */
  let baselineActive = false;
  let baselineStartedAt = 0;
  let baselineLastActivityAt = 0;

  function textOf(bubble) {
    // An adapter may normalise a bubble's raw page text for
    // detection (e.g. ChatGPT turn blocks carry the page's own
    // "ChatGPT said:" label line). Default: the bubble's own text.
    return adapter.bubbleText ? adapter.bubbleText(bubble)
                              : (bubble.innerText || "");
  }

  function bubbleKey(bubble) {
    // A bubble is identified by its settled text: same text = same
    // message, however the page re-renders it around us.
    return PB.pbFingerprint(adapter.seat, textOf(bubble));
  }

  /* Find the live bubble currently carrying this exact text.
   * Returns the bubble, or null while no bubble carries it (the
   * page is mid-render, or the element was swapped out). The match
   * uses the same normalised comparison as the settle stability
   * check (pbTextsMatch) — the raw strings of two reads of the same
   * letter can differ in whitespace jitter alone, and an exact
   * string compare would strand the letter pending forever. */
  function refindBubble(text) {
    for (const b of liveBubbles()) {
      if (PB.pbTextsMatch(textOf(b), text)) return b;
    }
    return null;
  }

  /* The live bubbles the capture stages may read: the adapter's
   * list, UNION the bubbles the detection scan itself finds (via
   * marker elements + bubbleOf). The union matters: on ChatGPT's
   * turn-block fallback shape the adapter's list can degenerate
   * to label leaves whose stripped text is empty, while the
   * scan's climb from a marker leaf still lands on the true turn
   * block. V6.3's settle gates on readability, so readability
   * must mean "the detection path can still find this letter",
   * not "one adapter helper happens to agree". Deduped by
   * element identity. */
  function liveBubbles() {
    const out = [];
    const seenEls = new Set();
    const push = (b) => { if (b && !seenEls.has(b)) { seenEls.add(b); out.push(b); } };
    if (adapter.listBubbles) {
      try { for (const b of adapter.listBubbles()) push(b); } catch (e) { /* fall through to the scan */ }
    }
    const region = adapter.regionEl && adapter.regionEl();
    if (region && adapter.bubbleOf) {
      for (const mt of watchTexts) {
        for (const el of lbMarkerElements(region, mt)) push(adapter.bubbleOf(el));
      }
    }
    return out;
  }

  /* V6.3 — the four-stage capture machinery. OBSERVE runs as a
   * per-letter loop (observeTick): every LB_OBSERVE_MS it takes
   * one fresh look at the live page and appends it to the
   * letter's settle trail. SETTLE is a judgement over TIME, not
   * a snapshot: LB_MIN_CLEAN_OBS consecutive clean observations
   * (bubble readable, text unchanged, generation off) spanning
   * the whole LB_SETTLE_MS quiet window. Any sighting of growth
   * (via consider()'s merge) or of generation resets both the
   * streak and the quiet clock — a pause, however long, is one
   * dirty observation away from resetting everything, and one
   * flickered generation read can no longer ship a letter
   * because a single read settles nothing. */

  function scheduleTick(entry, delay) {
    if (entry.timer) clearTimeout(entry.timer);
    entry.timer = setTimeout(() => { entry.timer = null; observeTick(entry); }, delay);
  }

  function trailPush(entry, now, generating, readable) {
    entry.obsCount++;
    const chg = entry.text.length !== entry._lastLen;
    if (chg) entry._lastLen = entry.text.length;
    if (entry.trail.length < LB_TRAIL_CAP) {
      entry.trail.push({ dt: now - entry.firstSeenAt, len: entry.text.length, gen: generating, read: readable, chg });
    }
  }

  /* Adopt a grown text into a pending entry in place: the entry
   * (and its trail) survives; the map re-keys to the new text's
   * fingerprint; streak and quiet clock restart. */
  function entryAdoptText(entry, newText, now) {
    const newFp = PB.pbFingerprint(adapter.seat, newText);
    if (newFp !== entry.key) {
      pending.delete(entry.key);
      entry.key = newFp;
      pending.set(newFp, entry);
    }
    entry.text = newText;
    entry.lastChangedAt = now;
    entry.cleanStreak = 0;
    entry.changeCount++;
  }

  /* VERIFY helper: a live bubble whose text strictly EXTENDS the
   * settled text — the same letter, grown past the snapshot.
   * Returns its raw text, or null. */
  function refindGrownText(text) {
    const norm = PB.pbNormalise(text);
    if (!norm) return null;
    for (const b of liveBubbles()) {
      const t = textOf(b);
      const n = PB.pbNormalise(t);
      if (n.length > norm.length && n.startsWith(norm)) return t;
    }
    return null;
  }

  /* V0.10.2: close the baseline window when its conditions are
   * met, judging every flagged letter in the same pass. Called
   * from observeTick and scan — both run on live cadences, so
   * the window closes promptly even on an otherwise idle page. */
  function baselineMaybeClose() {
    if (!baselineActive) return;
    const now = Date.now();
    const span = now - baselineStartedAt;
    const quiet = now - baselineLastActivityAt;
    if ((span >= LB_BASELINE_MIN_MS && quiet >= LB_BASELINE_QUIET_MS) || span >= LB_BASELINE_MAX_MS) {
      baselineActive = false;
      closeBaseline();
    }
  }

  /* Judge the letters first sighted during the baseline window.
   * HISTORY (dropped, never carried): the body fingerprint is
   * in the seen record — the persistent delivered ledger — or
   * the letter's bubble sits buried under later turns (a letter
   * with conversation after it was there before that
   * conversation happened; it cannot be a new message).
   * STRANDED (released to carry once): anything else — a letter
   * posted while the tab was closed or the bridge off. Once it
   * carries, the background records it, and the record check
   * above retires it on every future load. A bubble that cannot
   * be refound at judgement time (mid-render) falls back to the
   * record alone. */
  /* V0.12.1: the live list is a UNION — the adapter's bubbles
   * first, then bubbles the detection scan found appended after
   * — so its order is NOT document order, and "the last bubble
   * on the page" read off it can bury a letter that is in truth
   * the page's last word (a scan-only older bubble appended
   * behind it). Where the DOM offers compareDocumentPosition,
   * burial is judged by true document position; otherwise the
   * union order stands (the v0.10.2 behaviour). */
  function orderedLive() {
    const live = liveBubbles();
    if (live.length > 1 && live[0] && typeof live[0].compareDocumentPosition === "function") {
      return live.slice().sort((a, b) => {
        if (a === b) return 0;
        const p = a.compareDocumentPosition(b);
        if (p & 4) return -1; // b follows a
        if (p & 2) return 1;  // b precedes a
        return 0;
      });
    }
    return live;
  }

  function closeBaseline() {
    const live = orderedLive();
    for (const entry of Array.from(pending.values())) {
      if (!entry.baseline) continue;
      const parsed = PB.pbParseMarker(entry.text);
      const bodyFp = parsed ? PB.pbFingerprint(adapter.seat, parsed.body) : null;
      const recorded = !!(bodyFp && deliveredSeed.has(bodyFp));
      let history = recorded;
      if (!history && parsed) {
        const mine = refindBubble(entry.text);
        if (mine) {
          const idx = live.indexOf(mine);
          if (idx !== -1 && idx < live.length - 1) history = true;
        }
      }
      if (history) {
        if (entry.timer) clearTimeout(entry.timer);
        pending.delete(entry.key);
        if (bodyFp) seen.add(bodyFp);
        seen.add(entry.key);
        /* V0.12.1: a letter judged history by POSITION while it
         * stands in no delivered record is the one baseline
         * judgement that can eat a stranded letter — it is
         * reported. (Recorded letters retiring quietly is the
         * normal reload path and stays quiet.) */
        if (!recorded && parsed) {
          reportDrop("baseline: judged history by position (unrecorded, buried under later turns) — not carried", lbFirstLine(parsed.body).trim());
        }
      } else {
        entry.baseline = false; // stranded: released, carries once
      }
    }
  }

  function observeTick(entry) {
    if (pending.get(entry.key) !== entry) return; // merged away or evicted
    baselineMaybeClose();
    const now = Date.now();
    // OBSERVE: one fresh look. Readability is exact-text refind —
    // a bubble that has grown past the snapshot does not refind
    // here; its growth arrives via consider()'s merge instead.
    let readable = false;
    if (refindBubble(entry.text)) readable = true;
    let generating = null;
    if (adapter.isGenerating) {
      try { generating = !!adapter.isGenerating(); } catch (e) { generating = null; }
    }
    if (generating === true) {
      entry.genOnCount++;
      entry.lastChangedAt = now; // generation active is not quiet
      entry.cleanStreak = 0;
    } else if (readable) {
      entry.cleanStreak++;
    } else {
      entry.cleanStreak = 0; // an unreadable page corroborates nothing
    }
    trailPush(entry, now, generating, readable);
    // SETTLE: streak + span, both required.
    if (entry.cleanStreak >= LB_MIN_CLEAN_OBS && now - entry.lastChangedAt >= LB_SETTLE_MS) {
      commitLetter(entry, now);
      return;
    }
    scheduleTick(entry, LB_OBSERVE_MS);
  }

  function commitLetter(entry, now) {
    /* VERIFY: one final live re-read at the gate. An exact refind
     * ships the LIVE read (whitespace jitter and all), never the
     * cached snapshot. A grown continuation found instead means
     * the letter is still growing: adopt it and restart the
     * settle. No live bubble at all: the streak's own clean
     * observations were each live reads of this exact text, so
     * the letter commits on their evidence — recorded honestly
     * as verifyMode "streak", never dressed up as a live read. */
    /* V0.10.2: a baseline-flagged letter never commits while
     * the window is open — the close judges it first (history
     * dropped, stranded released). Defer and let the tick
     * re-run; the settle evidence keeps accruing meanwhile. */
    if (entry.baseline && baselineActive) {
      baselineMaybeClose();
      if (pending.get(entry.key) !== entry) return; // judged history at the close
      if (entry.baseline && baselineActive) {
        trailPush(entry, now, null, true);
        scheduleTick(entry, LB_OBSERVE_MS);
        return;
      }
    }
    let verifyMode = "streak";
    let finalText = entry.text;
    const live = refindBubble(entry.text);
    if (live) {
      verifyMode = "live";
      finalText = textOf(live);
    } else {
      const grown = refindGrownText(entry.text);
      if (grown) {
        entryAdoptText(entry, grown, now);
        trailPush(entry, now, null, true);
        scheduleTick(entry, LB_OBSERVE_MS);
        return;
      }
    }
    const fp = entry.key;
    pending.delete(fp);
    const nowText = finalText;
    // The text has been identical across the whole quiet window.
    // Final verification, in order. The SPEAKER is decided from
    // the SIGHTINGS recorded for this letter's own first body
    // line (see the sightings map): the letter fires only when
    // the assistant shape was actually seen carrying it and the
    // user shape never was — a user sighting anywhere of the same
    // first line poisons the letter, because delivery-shape twins
    // (a paste in a user turn, the real answer in an assistant
    // turn) must never be carried as user mail. If no sighting
    // named a speaker, fall back to reading the speaker off the
    // live page (a bubble carrying the text, or the adapter's
    // text-based read when it has one). The delimiter rule
    // (pbParseMarker, v0.12.0) runs on the entry's own text — for
    // a completed letter that IS the full text, and the body it
    // extracts is everything beneath the marker line.
    const parsed = PB.pbParseMarker(nowText);
    if (!parsed) { seen.add(fp); return; }
    const firstBodyLine = lbFirstLine(parsed.body).trim();
    const seenSpeakers = sightings.get(firstBodyLine);
    let verdict = "unknown";
    if (seenSpeakers) {
      if (seenSpeakers.has("user")) verdict = "user";
      else if (seenSpeakers.has("assistant")) verdict = "assistant";
    }
    if (verdict === "unknown") verdict = speakerOf(nowText);
    if (verdict !== "assistant") {
      /* V0.12.1: the speaker verdict is a SAFETY rule and it
       * stands — a user sighting of this first body line poisons
       * the letter for this page run (delivery-shape twins must
       * never be carried as user mail), and the sightings only
       * grow, so the verdict can never soften. What changes:
       * the drop is REPORTED, and the letter is marked seen so
       * it stops re-pending and re-failing on every rescan —
       * finality with a trace, not a silent loop. */
      seen.add(PB.pbFingerprint(adapter.seat, parsed.body));
      seen.add(fp);
      reportDrop(`speaker verdict "${verdict}" — not carried`, firstBodyLine);
      return;
    }
    if (!lbHasStandaloneMarker(nowText, marker.text) &&
        !(crusherMarker && lbHasStandaloneMarker(nowText, crusherMarker.marker))) {
      // Not a handoff after all — no standalone marker line (the
      // marker survives only inside a sentence, or it was edited
      // away). Mark seen so we never re-check it. (V0.12.0: the
      // pbParseMarker call above is the routing gate; this is its
      // defensive twin on the settled text. V0.13.0: Crusher's
      // marker satisfies the twin exactly as the pair marker does.)
      seen.add(fp);
      return;
    }
    const bodyFp = PB.pbFingerprint(adapter.seat, parsed.body);
    if (seen.has(bodyFp)) {                    // duplicate sighting
      reportDrop("already handed off this run (duplicate fingerprint) — not carried again", firstBodyLine);
      return;
    }
    if (awaitingAck.has(bodyFp)) {
      /* CONCLUSION BUILD Part 2: this exact body is already
       * committed and waiting on the background's answer —
       * handing it off again would double the letter. */
      reportDrop("already awaiting handoff confirmation — not handed off twice", firstBodyLine);
      return;
    }
    /* V6.3 SUPERSEDE (Alex's rule): a settled body that strictly
     * EXTENDS a body already handed off is that letter still
     * growing — it TRAVELS, carrying the earlier body's
     * fingerprint as its lineage. (v0.5.1–V6.2 growth-suppression
     * silently dropped it here, which is how a premature partial
     * permanently buried the completed letter.) The lineage
     * chains: the map entry moves to the new body, so a third
     * growth supersedes the second, each link traceable. */
    const normBody = PB.pbNormalise(parsed.body);
    /* CONCLUSION BUILD Part 2: growth of a letter whose handoff
     * is still UNCONFIRMED — the original is in no handed-off
     * map yet, so the scan above cannot see it. The grown
     * payload REPLACES the awaiting one, carrying the awaiting
     * body's fingerprint as its lineage: if the original send
     * did land (only its answer was lost), the background folds
     * the growth as a recovery; if it never landed, the growth
     * routes as the letter. Either way exactly one chain of
     * attempts exists for this letter. */
    for (const ackEntry of awaitingAck.values()) {
      if (normBody.startsWith(ackEntry.normBody) && normBody.length > ackEntry.normBody.length) {
        if (ackEntry.timer) { clearTimeout(ackEntry.timer); ackEntry.timer = null; }
        awaitingAck.delete(ackEntry.bodyFp);
        ackEntry.payload = {
          from: adapter.seat,
          to: parsed.to,
          body: parsed.body,
          fingerprint: bodyFp,
          supersedesFingerprint: ackEntry.bodyFp,
          tokenSnapshot: entry.tokenSnapshot || null,
          capture: {
            observations: entry.obsCount,
            genOnCount: entry.genOnCount,
            changeCount: entry.changeCount,
            spanMs: now - entry.firstSeenAt,
            verifyMode,
            dispatchLength: parsed.body.length,
            trail: entry.trail,
          },
        };
        ackEntry.bodyFp = bodyFp;
        ackEntry.textFp = fp;
        ackEntry.normBody = normBody;
        ackEntry.firstLine = firstBodyLine;
        awaitingAck.set(bodyFp, ackEntry);
        attemptAck(ackEntry);
        return;
      }
    }
    let supersedesFingerprint = null;
    for (const [sentNorm, sentFp] of handedOff) {
      if (normBody.startsWith(sentNorm) && normBody.length > sentNorm.length) {
        supersedesFingerprint = sentFp;
        handedOff.delete(sentNorm);
        handedOffLines.delete(sentNorm);
        break;
      }
    }
    // Marker-twin suppression, V0.12.1 (narrowed on Ben's fix
    // order, 2026-11-08): the rule used to suppress ANY later
    // letter repeating a carried letter's first body line — and
    // silently ate genuine replies whose openings were formulaic
    // ("Status report.", "Acknowledged.") whenever an earlier
    // letter had opened the same way. It now suppresses only a
    // REAL twin: a body IDENTICAL to a carried body with this
    // first line (fingerprint dedup above usually takes it
    // first) or a strict PREFIX of one — a stale partial arriving
    // after the whole letter already travelled. Bodies that
    // DIVERGE after the shared first line are different letters
    // and they carry; if one is ever a stale quote, it arrives
    // VISIBLE in the record, where a duplicate can be seen and
    // judged — the standing doctrine: a visible duplicate is
    // recoverable, a silent loss is not. A supersede stays
    // exempt: it repeats the line BY DESIGN, and its lineage —
    // not its opening — is what identifies it. Every remaining
    // suppression is reported via onDrop.
    const firstLine = firstBodyLine;
    if (!supersedesFingerprint) {
      for (const sentNorm of handedOff.keys()) {
        if (handedOffLines.get(sentNorm) !== firstLine) continue;
        if (normBody === sentNorm || sentNorm.startsWith(normBody)) {
          seen.add(bodyFp);
          seen.add(fp);
          reportDrop("twin of an already-carried letter (same first line; body identical to or a prefix of the carried body) — not carried", firstLine);
          return;
        }
      }
    }
    /* COMMIT: the verified payload plus its completeness
     * evidence — the settle trail summary Alex specified
     * (per-observation records ride in capture.trail).
     * CONCLUSION BUILD Part 2: the handoff now WAITS for the
     * background's answer. The seen / handed-off marking that
     * used to be applied here — before the send, on faith —
     * is applied in confirmAck, after an accepted or
     * duplicate-terminal answer. A letter the background never
     * accepts is never marked handed off. */
    const ackEntry = {
      payload: {
        from: adapter.seat,
        to: parsed.to,
        body: parsed.body,
        fingerprint: bodyFp,
        supersedesFingerprint,
        tokenSnapshot: entry.tokenSnapshot || null,
        capture: {
          observations: entry.obsCount,
          genOnCount: entry.genOnCount,
          changeCount: entry.changeCount,
          spanMs: now - entry.firstSeenAt,
          verifyMode,
          dispatchLength: parsed.body.length,
          trail: entry.trail,
        },
      },
      bodyFp, textFp: fp, normBody, firstLine, attempts: 0, timer: null,
    };
    awaitingAck.set(bodyFp, ackEntry);
    attemptAck(ackEntry);
  }

  /* Speaker of a TEXT (not a node): for adapters whose speaker is
   * carried in the text itself (ChatGPT's said-labels) the answer
   * is read off the text; for node-class adapters (Muse) it is
   * read off a live bubble carrying the text. Falls back to the
   * adapter's own read of any bubble carrying the text. */
  function speakerOf(text) {
    if (adapter.textSpeaker) return adapter.textSpeaker(text);
    if (adapter.listBubbles) {
      for (const b of adapter.listBubbles()) {
        if (PB.pbTextsMatch(textOf(b), text)) return adapter.bubbleSpeaker(b);
      }
    }
    return "unknown";
  }

  function consider(bubble) {
    if (!bubble) return;
    const text = textOf(bubble);
    const hasPairMarker = text.includes(marker.text);
    const hasCrusherMarker = !!(crusherMarker && text.includes(crusherMarker.marker));
    if (!hasPairMarker && !hasCrusherMarker) return; // no marker: not ours
    // Record the sighting: this letter's delivery shape and the
    // speaker carrying it. The settle check decides from these —
    // the sightings are the evidence; no similarity guessing.
    const sightingMarkerText = lbHasStandaloneMarker(text, marker.text) ? marker.text
      : (hasCrusherMarker && lbHasStandaloneMarker(text, crusherMarker.marker) ? crusherMarker.marker : null);
    if (sightingMarkerText) {
      const p = PB.pbParseMarker(text);
      if (p) {
        const line = lbFirstLine(p.body).trim();
        if (line) {
          let set = sightings.get(line);
          if (!set) { set = new Set(); sightings.set(line, set); }
          set.add(adapter.bubbleSpeaker(bubble));
        }
      }
    }
    // Track the best (longest) marker-led read (kept for scan use).
    if (text.length > (bestReadText ? bestReadText.length : 0)) {
      bestReadText = text;
    }
    const fp = PB.pbFingerprint(adapter.seat, text);
    if (seen.has(fp)) return;      // already handled
    const entry = pending.get(fp);
    if (entry) {
      // Same letter seen again (its fingerprint IS its text's
      // identity, so a same-key sighting is the same text):
      // just re-arm the observation loop if it ever lapsed.
      if (PB.pbTextsMatch(entry.text, text) && !entry.timer) {
        scheduleTick(entry, 400);
      }
      return;
    }
    // Growth-merge: a new sighting whose text EXTENDS a pending
    // letter (same marker line, body grown) is the same letter,
    // still rendering — not a second letter. V6.3: the pending
    // entry ADOPTS the grown text in place — its settle trail,
    // first-sighting time and counters survive; only the streak
    // and the quiet clock restart. (v0.5.1–V6.2 deleted the old
    // entry and started a fresh one, discarding its history.)
    // This is what makes the settle wait for the FINISHED
    // letter: growth sightings keep arriving while the page
    // renders, and the letter can only settle once growth stops.
    const thisMarker = standaloneMarkerOf(text);
    if (thisMarker) {
      for (const v of pending.values()) {
        if (standaloneMarkerOf(v.text) === thisMarker) {
          const a = PB.pbNormalise(v.text), b = PB.pbNormalise(text);
          if (b.startsWith(a) && b.length > a.length) {
            entryAdoptText(v, text, Date.now());
            trailPush(v, Date.now(), null, true);
            if (!v.timer) scheduleTick(v, LB_OBSERVE_MS);
            return;
          }
        }
      }
    }
    if (pending.size >= LB_MAX_PENDING) {
      // Cap reached: evict the stalest entry so a fresh letter is
      // never starved by corpses of swapped-out renders.
      let oldestFp = null, oldestAt = Infinity;
      for (const [k, v] of pending) {
        if (v.lastChangedAt < oldestAt) { oldestAt = v.lastChangedAt; oldestFp = k; }
      }
      if (oldestFp !== null) {
        const old = pending.get(oldestFp);
        if (old && old.timer) clearTimeout(old.timer);
        pending.delete(oldestFp);
        /* CONCLUSION BUILD Part 2: the cap eviction used to be
         * the letterbox's second silent exit — a pending letter
         * vanished with no record anywhere. It is now reported
         * through the drop channel like every other decision
         * not to carry. */
        try {
          const op = PB.pbParseMarker(old.text);
          reportDrop("pending cap reached — the stalest pending letter was evicted before it could settle", op ? lbFirstLine(op.body).trim() : lbFirstLine(old.text).trim());
        } catch (e) { /* reporting never breaks capture */ }
      }
    }
    const now0 = Date.now();
    const e = {
      key: fp, text, lastChangedAt: now0, firstSeenAt: now0, timer: null,
      cleanStreak: 0, obsCount: 0, genOnCount: 0, changeCount: 0,
      trail: [], _lastLen: text.length,
      /* COMBINED BUILD, Part A stream 2 (D1): the detection
       * token snapshot is taken HERE — the moment the
       * candidate first enters settle — and never again.
       * Growth merges adopt new text but keep this snapshot;
       * handoff carries it unchanged. If the token has
       * rotated since (pause, re-registration), admission
       * rejects the candidate as stale: that is the design,
       * not a failure of the letterbox. */
      tokenSnapshot: (typeof tokenSource === "function" ? (tokenSource() || null) : null),
      /* V0.10.2: first sighted during the baseline window —
       * provisional until the close judges it. */
      baseline: baselineActive,
    };
    pending.set(fp, e);
    if (baselineActive) baselineLastActivityAt = now0;
    scheduleTick(e, 400);
  }

  /* One scan pass: bubbles enclosing any marker occurrence, plus
   * (cheaply) a direct pass over bubbles so a marker that arrived
   * inside an already-present bubble is still found. */
  function scan(scopeEl) {
    baselineMaybeClose();
    const region = scopeEl || (adapter.regionEl && adapter.regionEl());
    if (!region) return;
    for (const mt of watchTexts) {
      for (const el of lbMarkerElements(region, mt)) {
        const bubble = adapter.bubbleOf(el);
        if (bubble) consider(bubble);
      }
    }
  }

  /* Absorb: non-marker bubbles currently on the page are marked
   * seen at start. MARKER bubbles are deliberately NOT absorbed
   * (v0.12.1 — see the loop below): they pend as baseline
   * entries and the baseline judge decides them — history by
   * the delivered record or by burial, stranded letters
   * released. V0.10.2: absorb STANDS DOWN while the page is
   * generating — a letter still streaming at load is pending,
   * not history. */
  function absorb() {
    if (adapter.isGenerating) {
      try { if (adapter.isGenerating()) return; } catch (e) { /* unreadable: absorb as before */ }
    }
    if (!adapter.listBubbles) return;
    for (const b of adapter.listBubbles()) {
      /* V0.12.1: marker-carrying bubbles are NO LONGER absorbed.
       * Absorb used to mark every marked bubble on the page as
       * seen at start — including its body fingerprint — which
       * silently ate the exact letter the baseline window exists
       * to save: one posted while the bridge was off, sitting on
       * an idle page at load. It never even became a pending
       * entry, so the baseline judge never saw it; and the
       * judge's "seen record" was this same polluted set, so the
       * record check could not tell a delivered letter from a
       * merely-present one. Now marker letters pend as baseline
       * entries and are judged on the delivered seed and their
       * document position — nothing else. (The generating
       * stand-down above stays: while the page streams, absorb
       * does nothing at all, as before.) */
      const t = textOf(b);
      if (watchTexts.some((mt) => t.includes(mt))) continue;
      seen.add(PB.pbFingerprint(adapter.seat, t));
    }
  }

  function start(observeTarget) {
    if (started) return;
    started = true;
    /* V0.10.2: the baseline window opens as the letterbox
     * starts — everything already on the page is history until
     * the window's close judges the exceptions (see header). */
    baselineActive = true;
    baselineStartedAt = Date.now();
    baselineLastActivityAt = baselineStartedAt;
    absorb();
    scan();
    const target = observeTarget ||
      (adapter.regionEl && adapter.regionEl()) || document.body;
    const obs = new MutationObserver((records) => {
      if (baselineActive) baselineLastActivityAt = Date.now();
      for (const r of records) {
        for (const n of r.addedNodes || []) {
          if (n && n.nodeType === 1) scan(n);
        }
        if (r.type === "characterData" && r.target && r.target.parentElement) {
          scan(r.target.parentElement);
        }
      }
      scan(); // one region pass per mutation batch — cheap and total
    });
    obs.observe(target, { childList: true, characterData: true, subtree: true });
    setInterval(() => scan(), LB_RESCAN_MS);
    return obs;
  }

  /* V0.19.1 TERMINAL READOUT (Ben's tap, 2026-11-11 21:01 MST):
   * a read-only peek at the newest bubble the letterbox can see —
   * its first line verbatim, and whether a watched marker stands
   * in it as a clean line. The panel shows these two facts in
   * plain terminal lines so Ben can see what retrieval sees,
   * instead of scrolling the adapter self-check dump. This
   * changes nothing about detection: same bubbles, same text,
   * same marker tests the scan itself uses. */
  function peekNewest() {
    try {
      const bubbles = liveBubbles();
      if (!bubbles.length) return { empty: true };
      const text = textOf(bubbles[bubbles.length - 1]) || "";
      let marker = null;
      let cleanLine = false;
      for (const t of watchTexts) {
        if (lbHasStandaloneMarker(text, t)) { marker = t; cleanLine = true; break; }
      }
      if (!marker) {
        for (const t of watchTexts) {
          if (text.includes(t)) { marker = t; break; }
        }
      }
      return { firstLine: lbFirstLine(text).slice(0, 120), marker, cleanLine };
    } catch (e) {
      return null;
    }
  }

  return { start, scan, consider, peekNewest, _seen: seen, _pending: pending, _awaiting: awaitingAck };
}

/* Resolve the seat's marker object ({text, to}) from the protocol
 * table: on a seat's page, the destination marker is the one pointing
 * AWAY from that seat (Remmy's page watches for TO-ALEX and vice
 * versa). The originating seat is verified by bubbleSpeaker, not by
 * the marker — the marker only names the destination. */
function lbMarkerForSeat(seat) {
  for (const m of PB.PB_MARKERS) if (m.to !== seat) return { text: m.marker, to: m.to };
  return null;
}

const PB_LETTERBOX = { pbCreateLetterbox, lbMarkerElements, lbFirstLine, lbMarkerFirstLine, lbHasStandaloneMarker, lbMarkerForSeat, LB_SETTLE_MS, LB_OBSERVE_MS, LB_MIN_CLEAN_OBS, LB_BASELINE_MIN_MS, LB_BASELINE_QUIET_MS, LB_BASELINE_MAX_MS, PB_ACK_DELAYS_MS };
if (typeof window !== "undefined") window.PB_LETTERBOX = PB_LETTERBOX;
if (typeof module !== "undefined" && module.exports) module.exports = PB_LETTERBOX;
