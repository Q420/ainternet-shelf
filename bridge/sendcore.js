"use strict";
/* Pulse Bridge — send core (v0.18.0): the send-decision logic,
 * shared by every surface adapter.
 *
 * WHY THIS FILE EXISTS (Ben's root-cause ruling, 2026-11-09):
 * the bridge's send path was written once and copied into five
 * adapters. The whole-page stop veto — the flaw that left
 * letters "pasted but not sent" on Alex's surface — lived in
 * every copy, so v0.17.0's correct fix on the ChatGPT adapter
 * still left the other surfaces carrying it. Pass 1 of this
 * build narrowed the read in every remaining copy; this module
 * ends the copying for the decision logic itself: button
 * classification, the composer scope, the composer button
 * state and the generating verdict now live HERE, once. An
 * adapter keeps only its platform knowledge — its candidate
 * selectors, its composer name, its typing and receipt
 * machinery — and delegates every send decision to these
 * functions, passing itself as the first argument.
 *
 * The rule the functions encode (Ben's fence, condition 1):
 * the verdict comes from THE COMPOSER'S OWN BUTTON and
 * nowhere else. A scope that shows neither face answers
 * "unknown" — never a pass, never a veto. Each adapter's
 * isGenerating() stays behind in the adapter as EVIDENCE for
 * the receipt's reads; it does not feed any function here.
 *
 * Loaded as a content script on every bridge surface (after
 * protocol.js in the manifest lists) and required directly by
 * the Node fixture for this module. */

const PB_SEND = {
  pbButtonLabel(b) {
    return String((b && b.getAttribute && (b.getAttribute("aria-label") || b.getAttribute("data-testid"))) || "");
  },

  pbButtonIsStop(adapter, b) {
    if (/stop/i.test(PB_SEND.pbButtonLabel(b))) return true;
    return adapter.candidates.stop.some((s) => { try { return !!(b.matches && b.matches(s)); } catch (e) { return false; } });
  },

  pbButtonIsSend(adapter, b) {
    if (/stop/i.test(PB_SEND.pbButtonLabel(b))) return false;
    if (/send/i.test(PB_SEND.pbButtonLabel(b))) return true;
    return adapter.candidates.send.some((s) => { try { return !!(b.matches && b.matches(s)); } catch (e) { return false; } });
  },

  pbComposerScope(adapter) {
    const start = adapter._engagedComposer || adapter.findComposer();
    if (!start) return null;
    if (start.closest) {
      const form = start.closest("form");
      if (form) return form;
      let n = start;
      for (let i = 0; i < 5 && n.parentElement; i++) {
        n = n.parentElement;
        if (n.querySelector && n.querySelector("button")) return n;
      }
      return start.parentElement || null;
    }
    return (start.ownerDocument || document).body || null;
  },

  pbComposerButtonState(adapter) {
    const scope = PB_SEND.pbComposerScope(adapter);
    if (!scope || !scope.querySelectorAll) return "unknown";
    try {
      const btns = Array.from(scope.querySelectorAll("button"));
      if (btns.some((b) => PB_SEND.pbButtonIsStop(adapter, b))) return "generating";
      if (btns.some((b) => PB_SEND.pbButtonIsSend(adapter, b))) return "ready";
    } catch (e) { /* a scope that cannot be read testifies to nothing */ }
    return "unknown";
  },

  pbDestinationGenerating(adapter) {
    return PB_SEND.pbComposerButtonState(adapter) === "generating";
  },

  /* Finding the button to CLICK keeps its wider search —
   * the composer's scope first, then the page. Finding is not
   * a veto: a button found here is still classified by
   * pbButtonIsStop before any click (in the adapters'
   * deliverText), and the state verdicts above never read
   * this wider scope. */
  pbFindSendButton(adapter) {
    const scope = PB_SEND.pbComposerScope(adapter);
    if (scope && scope.querySelectorAll) {
      const btns = Array.from(scope.querySelectorAll("button"));
      const byAttr = btns.find((b) => adapter.candidates.send.some((s) => {
        try { return b.matches && b.matches(s); } catch (e) { return false; }
      }));
      if (byAttr) return byAttr;
      const byName = btns.find((b) => /send/i.test(b.getAttribute("aria-label") || ""));
      if (byName) return byName;
    }
    for (const s of adapter.candidates.send) {
      const el = document.querySelector(s);
      if (el) return el;
    }
    const btns = Array.from(document.querySelectorAll("button"));
    return btns.find((b) => /send/i.test(b.getAttribute("aria-label") || "")) || null;
  },

  /* The bounded defer: never engage a destination that is
   * still generating — wait it out, bounded, or stall with
   * the reason named. Built entirely on the verdict above. */
  async pbWaitForDestinationIdle(adapter) {
    const maxMs = (typeof window !== "undefined" && window.PB_TEST_DEFER_MAX_MS) ||
      (typeof PB_CRUSHER !== "undefined" && PB_CRUSHER.PB_CRUSHER_DEFER_MAX_MS) || 45000;
    const started = Date.now();
    while (PB_SEND.pbDestinationGenerating(adapter)) {
      if (Date.now() - started >= maxMs) {
        return { ok: false, stage: "generating", error: "destination still generating after a " + Math.round(maxMs / 1000) + "s defer — nothing engaged, typed or clicked" };
      }
      await new Promise((r) => setTimeout(r, 500));
    }
    return { ok: true };
  },
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = PB_SEND;
}
