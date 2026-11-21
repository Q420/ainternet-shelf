"use strict";
/* Pulse Bridge — BRIDGE ALERT (v0.16.0, popup only).
 *
 * Ben's design (2026-11-09, refined in the open with Remmy,
 * approved as proposed by Alex, pb-mwa3fjpj): the watchdog's
 * bell. When work freezes or something needs Ben, Remmy raises
 * an alert and Ben is reached where the work is — in the
 * browser, on the bridge.
 *
 * ARCHITECTURE (Ben's correction, carried by Alex pb-mwa3dolm):
 * an alert is a local browser-extension EVENT, not a chat
 * message. It is not a letter, it does not enter the letter
 * protocol, it has no PB-ID and expects no reply. The bridge is
 * involved only in detecting the raise and showing the popup.
 * (The fix-options window and the action buttons — UNFREEZE /
 * RESTART / RESYNC / LET_GO — are a LATER build; this build is
 * the popup only, per Ben's go 2026-11-09 17:53.)
 *
 * HOW A RAISE TRAVELS: Remmy writes a small directive block in
 * her own Muse message —
 *
 *   ⟦BRIDGE-ALERT⟧
 *   id: alert-20261109-1755-test
 *   seat: alex
 *   what: <one headline line>
 *   detail: <optional second line>
 *
 * The alert.js instance on the muse.ai surface detects the
 * block in the page text and reports the parsed fields to the
 * background (pb-alert-raise). The background records the
 * alert, resolves the AFFECTED SEAT's registered tab, and that
 * tab's alert.js renders the popup and plays the chime. If the
 * affected seat has no registered tab, the popup falls back to
 * every registered seat tab and says so on its face — targeting
 * is never pretended.
 *
 * THE RULES (Ben's, with Alex's plain safeguards):
 *   - ONE chime per alert ID, ever. Reloads, re-detection,
 *     popup re-rendering and polling never replay it. The
 *     chime is claimed exactly once, in the background, before
 *     any tab is told to play it (at-most-once by construction).
 *   - The popup persists until Ben closes it. Closing is the
 *     ACKNOWLEDGEMENT — it never claims the underlying work is
 *     resolved. An acknowledged alert never fires again.
 *   - An unacknowledged alert survives reloads: a tab that
 *     loads later pulls it (pb-alert-pending) and shows it
 *     WITHOUT a second chime.
 *   - Duplicate detection is by alert ID: the same raise
 *     sighted again (the bridge re-rendering Remmy's message,
 *     the scanner's next poll) changes nothing.
 *   - The popup is a pure overlay. Alert code never touches a
 *     composer, a send path, or a generating response.
 *
 * This file is loaded in two places, like crusher.js: as a
 * content script on every bridge surface (detection runs only
 * on muse.ai; rendering runs everywhere) and by the background
 * worker via importScripts, which uses only the pure logic.
 */

const PB_ALERT_MARKER = "⟦BRIDGE-ALERT⟧";
const PB_ALERT_SEATS = ["remmy", "alex"];
const PB_ALERT_MAX_RECORDS = 50;

/* Parse the FIRST complete directive block in a text. Lines
 * after the marker are read as `key: value` while they match a
 * known key; the block ends at the first other line, so letter
 * text or prose following the block is never swallowed.
 * Returns {id, seat, headline, detail} or null. `what` is
 * required; `seat` is kept raw (lowercased) — whether it names
 * a real seat is the targeting step's question, not the
 * parser's. */
function pbAlertParse(text) {
  if (!text || typeof text !== "string") return null;
  const lines = text.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() !== PB_ALERT_MARKER) continue;
    const got = {};
    for (let j = i + 1; j < lines.length; j++) {
      const m = /^(id|seat|what|detail):\s*(.*)$/.exec(lines[j].trim());
      if (!m) break;
      got[m[1]] = m[2].trim();
    }
    if (!got.what) return null;
    return {
      id: got.id || null,
      seat: got.seat ? got.seat.toLowerCase() : null,
      headline: got.what,
      detail: got.detail || "",
    };
  }
  return null;
}

/* Parse EVERY directive block in a text (a long chat may hold
 * several raises; the detector reports each once per page
 * load and the background dedups the rest by ID). */
function pbAlertParseAll(text) {
  if (!text || typeof text !== "string") return [];
  const out = [];
  const lines = text.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() !== PB_ALERT_MARKER) continue;
    const got = {};
    for (let j = i + 1; j < lines.length; j++) {
      const m = /^(id|seat|what|detail):\s*(.*)$/.exec(lines[j].trim());
      if (!m) break;
      got[m[1]] = m[2].trim();
    }
    if (got.what) {
      out.push({
        id: got.id || null,
        seat: got.seat ? got.seat.toLowerCase() : null,
        headline: got.what,
        detail: got.detail || "",
      });
    }
  }
  return out;
}

/* A deterministic fallback ID from the raise's own content, so
 * the same rendered message re-sighted after a reload computes
 * the SAME id and dedups against the stored record. Remmy
 * normally supplies an explicit id; this is the safety net. */
function pbAlertAutoId(parsed) {
  const seed = [parsed.seat || "", parsed.headline || "", parsed.detail || ""].join("|");
  let h = 5381;
  for (let i = 0; i < seed.length; i++) h = ((h * 33) ^ seed.charCodeAt(i)) >>> 0;
  return "auto-" + h.toString(36);
}

function pbAlertSanitizeId(raw) {
  const s = String(raw || "").replace(/[^A-Za-z0-9_-]/g, "").slice(0, 64);
  return s || null;
}

/* A fresh alert record from parsed fields. Sanitising happens
 * HERE, in the background's hands — the page's parse is a
 * report, never trusted as state. */
function pbAlertRecord(parsed, at) {
  const id = pbAlertSanitizeId(parsed && parsed.id) || pbAlertAutoId(parsed || {});
  return {
    id,
    seat: PB_ALERT_SEATS.includes(parsed && parsed.seat) ? parsed.seat : null,
    headline: String((parsed && parsed.headline) || "").slice(0, 200),
    detail: String((parsed && parsed.detail) || "").slice(0, 300),
    at: at || new Date().toISOString(),
    chimed: false,
    acked: false,
  };
}

function pbAlertFind(records, id) {
  return (records || []).find((r) => r && r.id === id) || null;
}

/* The one-chime claim: returns true exactly once per record —
 * the first caller latches it. Acked records never chime. */
function pbAlertClaimChime(rec) {
  if (!rec || rec.chimed || rec.acked) return false;
  rec.chimed = true;
  return true;
}

/* Resolve where an alert shows. registrations is the bridge
 * state's {remmy: {tabId,...}|null, alex: {...}|null}.
 * A known seat WITH a registered tab → that tab alone, no
 * fallback. Anything else (seat unregistered, seat unknown)
 * → every registered seat tab, flagged fallback — the popup
 * says so on its face. No registrations at all → no tabs: the
 * alert stays recorded and pending for the first tab to pull. */
function pbAlertTarget(registrations, seat) {
  const regs = registrations || {};
  const tabOf = (s) => (regs[s] && regs[s].tabId != null ? regs[s].tabId : null);
  if (seat && PB_ALERT_SEATS.includes(seat) && tabOf(seat) != null) {
    return { tabIds: [tabOf(seat)], targetSeat: seat, fallback: false };
  }
  const tabIds = [];
  for (const s of PB_ALERT_SEATS) {
    const t = tabOf(s);
    if (t != null && !tabIds.includes(t)) tabIds.push(t);
  }
  return { tabIds, targetSeat: seat || null, fallback: true };
}

/* Bound the record list. Acknowledged records are evicted
 * first (oldest first); unacknowledged ones only when there is
 * no acknowledged record left to evict. */
function pbAlertTrim(records) {
  const list = (records || []).slice();
  while (list.length > PB_ALERT_MAX_RECORDS) {
    const idx = list.findIndex((r) => r && r.acked);
    if (idx >= 0) list.splice(idx, 1);
    else list.shift();
  }
  return list;
}

/* What a tab is allowed to receive about an alert. */
function pbAlertPublic(rec, fallback) {
  return {
    id: rec.id, seat: rec.seat, headline: rec.headline,
    detail: rec.detail, at: rec.at, fallback: !!fallback,
  };
}

const PB_ALERT = {
  PB_ALERT_MARKER, PB_ALERT_SEATS, PB_ALERT_MAX_RECORDS,
  pbAlertParse, pbAlertParseAll, pbAlertAutoId, pbAlertSanitizeId,
  pbAlertRecord, pbAlertFind, pbAlertClaimChime, pbAlertTarget,
  pbAlertTrim, pbAlertPublic,
};
if (typeof window !== "undefined") window.PB_ALERT = PB_ALERT;
if (typeof module !== "undefined" && module.exports) module.exports = PB_ALERT;

/* ================= CONTENT RUNTIME =================
 * Runs only in a real page (the background worker has no
 * window/document and stops at the exports above). */
if (typeof window !== "undefined" && typeof document !== "undefined" &&
    typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {

  const PB_ALERT_CSS = `
  #pb-alert-stack { position: fixed; top: 14px; left: 50%; transform: translateX(-50%);
    z-index: 2147483600; display: flex; flex-direction: column; gap: 8px;
    width: min(560px, 94vw); }
  .pb-alert-card { background: rgba(96,16,10,.97); border: 2px solid #ff5147;
    color: #ffe9e6; border-radius: 10px; padding: 10px 12px;
    box-shadow: 0 10px 34px rgba(0,0,0,.55);
    font: 13px/1.45 -apple-system, "Segoe UI", Roboto, sans-serif; }
  .pb-alert-head { display: flex; align-items: center; gap: 8px; }
  .pb-alert-word { font-weight: 700; letter-spacing: .1em; font-size: 11px;
    text-transform: uppercase; color: #ffb3ab; }
  .pb-alert-seat { font-size: 11px; color: #ffc9c2; border: 1px solid rgba(255,150,140,.55);
    border-radius: 20px; padding: 0 7px; line-height: 17px; }
  .pb-alert-close { margin-left: auto; background: none; border: 1px solid rgba(255,150,140,.6);
    color: #ffe9e6; border-radius: 6px; width: 22px; height: 22px; line-height: 1;
    cursor: pointer; font-size: 13px; flex: none; }
  .pb-alert-close:hover { background: rgba(255,81,71,.3); }
  .pb-alert-headline { font-size: 14.5px; font-weight: 600; margin-top: 5px; }
  .pb-alert-detail { font-size: 12.5px; color: #ffc9c2; margin-top: 2px; }
  .pb-alert-where { font-size: 11px; color: #ff9d94; margin-top: 5px; }
  `;

  function pbAlertSeatName(seat) {
    return seat === "alex" ? "Alex" : seat === "remmy" ? "Remmy" : null;
  }

  function pbAlertStack() {
    let stack = document.getElementById("pb-alert-stack");
    if (stack) return stack;
    if (!document.getElementById("pb-alert-style")) {
      const st = document.createElement("style");
      st.id = "pb-alert-style";
      st.textContent = PB_ALERT_CSS;
      document.head.appendChild(st);
    }
    stack = document.createElement("div");
    stack.id = "pb-alert-stack";
    document.body.appendChild(stack);
    return stack;
  }

  /* The one chime: BEN'S AMAJ7 CHORD (v0.17.0 — his spec, by
   * ear: "a cool futuristic synth chord — amaj7", with an A1
   * added an octave below the A2 and its velocity raised;
   * recipe of record: chord-example.py v3, auditioned and
   * approved by Ben 2026-11-09, queued by him for this build).
   * Detuned saw pairs on A3/C#4/E4/G#4 through a lowpass that
   * sweeps 400→3200 Hz and settles to 2000, a smooth 0.35s
   * attack, sustain to 0.75s, an exponential release to 2.4s;
   * sine body at A2 and A1, an A5 shimmer on top. Generated —
   * no asset. Best-effort by design (Chrome's autoplay rules
   * govern); the popup is the guarantee, the chord the bell.
   * A blocked chime is silent, never an error. */
  function pbAlertChime() {
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      const ctx = new Ctx();
      if (ctx.state === "suspended") ctx.resume().catch(() => {});
      const t = ctx.currentTime;
      /* The chord's shared envelope + filter sweep. */
      const master = ctx.createGain();
      master.gain.setValueAtTime(0.0001, t);
      master.gain.exponentialRampToValueAtTime(0.5, t + 0.35);
      master.gain.setValueAtTime(0.5, t + 0.75);
      master.gain.exponentialRampToValueAtTime(0.0001, t + 2.4);
      const sweep = ctx.createBiquadFilter();
      sweep.type = "lowpass";
      sweep.Q.value = 0.7;
      sweep.frequency.setValueAtTime(400, t);
      sweep.frequency.exponentialRampToValueAtTime(3200, t + 0.9);
      sweep.frequency.exponentialRampToValueAtTime(2000, t + 1.6);
      sweep.connect(master); master.connect(ctx.destination);
      const voice = (type, freq, peak, detune, dest) => {
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.type = type;
        o.frequency.value = freq;
        if (detune) o.detune.value = detune;
        g.gain.value = peak;
        o.connect(g); g.connect(dest || ctx.destination);
        o.start(t); o.stop(t + 2.5);
      };
      /* Chord tones: detuned saw pairs through the sweep. */
      [220, 277.18, 329.63, 415.30].forEach((f) => {
        voice("sawtooth", f, 0.045, -5, sweep);
        voice("sawtooth", f, 0.045, 5, sweep);
      });
      /* Sine body + shimmer, straight to the master. */
      const body = (freq, peak) => {
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.type = "sine";
        o.frequency.value = freq;
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(peak, t + 0.35);
        g.gain.setValueAtTime(peak, t + 0.75);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 2.4);
        o.connect(g); g.connect(ctx.destination);
        o.start(t); o.stop(t + 2.5);
      };
      body(55, 0.30);   /* A1 — Ben's added octave, velocity raised */
      body(110, 0.14);  /* A2 */
      body(880, 0.03);  /* A5 shimmer */
      setTimeout(() => { try { ctx.close(); } catch (e) {} }, 2900);
    } catch (e) { /* the popup already carries the alert */ }
  }

  function pbAlertRender(pub, chime) {
    if (!pub || !pub.id || !document.body) return;
    const stack = pbAlertStack();
    let card = stack.querySelector('[data-alert-id="' + pub.id + '"]');
    if (!card) {
      card = document.createElement("div");
      card.className = "pb-alert-card";
      card.setAttribute("data-alert-id", pub.id);
      card.setAttribute("role", "alert");
      const head = document.createElement("div");
      head.className = "pb-alert-head";
      const word = document.createElement("span");
      word.className = "pb-alert-word";
      word.textContent = "⚠ Remmy needs you";
      head.appendChild(word);
      const seatName = pbAlertSeatName(pub.seat);
      if (seatName) {
        const tag = document.createElement("span");
        tag.className = "pb-alert-seat";
        tag.textContent = seatName + "'s seat";
        head.appendChild(tag);
      }
      const close = document.createElement("button");
      close.className = "pb-alert-close";
      close.textContent = "✕";
      close.setAttribute("aria-label", "Close alert");
      close.addEventListener("click", () => {
        card.remove();
        chrome.runtime.sendMessage({ kind: "pb-alert-ack", id: pub.id }).catch(() => {});
      });
      head.appendChild(close);
      card.appendChild(head);
      const hl = document.createElement("div");
      hl.className = "pb-alert-headline";
      hl.textContent = pub.headline || "";
      card.appendChild(hl);
      if (pub.detail) {
        const d = document.createElement("div");
        d.className = "pb-alert-detail";
        d.textContent = pub.detail;
        card.appendChild(d);
      }
      if (pub.fallback) {
        const w = document.createElement("div");
        w.className = "pb-alert-where";
        w.textContent = seatName
          ? "Shown here because " + seatName + "'s tab isn't open."
          : "Shown here — the affected seat could not be established.";
        card.appendChild(w);
      }
      stack.appendChild(card);
    }
    if (chime) pbAlertChime();
  }

  function pbAlertClear(id) {
    const stack = document.getElementById("pb-alert-stack");
    if (!stack) return;
    const card = stack.querySelector('[data-alert-id="' + id + '"]');
    if (card) card.remove();
  }

  chrome.runtime.onMessage.addListener((msg) => {
    if (!msg) return;
    if (msg.kind === "pb-alert-show" && msg.alert) pbAlertRender(msg.alert, !!msg.chime);
    if (msg.kind === "pb-alert-clear" && msg.id) pbAlertClear(msg.id);
  });

  /* Persistence pull: on load, and slowly thereafter, ask the
   * background for unacknowledged alerts that belong on THIS
   * tab. The background decides targeting and the chime claim;
   * a re-show after reload arrives with chime:false unless
   * this tab is the first surface ever to surface the alert. */
  function pbAlertPull() {
    chrome.runtime.sendMessage({ kind: "pb-alert-pending" }).then((res) => {
      if (!res || !res.ok || !Array.isArray(res.alerts)) return;
      for (const item of res.alerts) {
        if (item && item.alert) pbAlertRender(item.alert, !!item.chime);
      }
    }).catch(() => {});
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setTimeout(pbAlertPull, 600));
  } else {
    setTimeout(pbAlertPull, 600);
  }
  setInterval(pbAlertPull, 20000);

  /* ===== Detection (Remmy's surface only) =====
   * Remmy's raises live in her own messages on muse.ai. The
   * scanner reads the TAIL of the page text (a raise is always
   * recent; the whole history would re-report old blocks every
   * poll — the background dedups by ID regardless, and each
   * block is reported at most once per page load from here). */
  if (location.hostname === "muse.ai") {
    const reported = new Set();
    setInterval(() => {
      try {
        if (!document.body) return;
        const text = document.body.innerText || "";
        const tail = text.length > 30000 ? text.slice(-30000) : text;
        if (!tail.includes(PB_ALERT_MARKER)) return;
        for (const parsed of pbAlertParseAll(tail)) {
          const id = pbAlertSanitizeId(parsed.id) || pbAlertAutoId(parsed);
          if (reported.has(id)) continue;
          reported.add(id);
          chrome.runtime.sendMessage({ kind: "pb-alert-raise", alert: parsed }).catch(() => {});
        }
      } catch (e) { /* detection never breaks the page */ }
    }, 1500);
  }
}
