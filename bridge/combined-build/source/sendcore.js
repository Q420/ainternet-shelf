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

  /* THE COMPOSER LEASE (Combined Build, Part B item 4).
   * One delivery at a time holds a lease binding the EXACT
   * composer element instance to the attempt's identity
   * (PB-ID + Index ID + Attempt ID). The lease is acquired by
   * the content script when a delivery starts and revalidated
   * at the two moments that matter — before typing (in the
   * idle defer below) and before submit (in pbFindSendButton).
   * A lease that no longer names the page's composer fails
   * the delivery closed with the break named; the bridge
   * never quietly re-targets another composer — above all
   * never one Ben is typing in by hand. */
  _lease: null,
  _leaseFault: null,

  pbLeaseAcquire(adapter, identity) {
    PB_SEND._leaseFault = null;
    let composer = null;
    try { composer = adapter.findComposer ? adapter.findComposer() : null; } catch (e) { composer = null; }
    if (!composer) {
      PB_SEND._lease = null;
      return { ok: false, stage: "lease", error: "composer lease could not be acquired — no composer instance on the page to bind" };
    }
    PB_SEND._lease = {
      pbId: (identity && identity.pbId) || null,
      indexId: (identity && identity.indexId) || null,
      attemptId: (identity && identity.attemptId) || null,
      composer,
      at: Date.now(),
    };
    return { ok: true, lease: PB_SEND._lease };
  },

  pbLeaseCheck(adapter, phase) {
    const L = PB_SEND._lease;
    if (!L) return { ok: true, leased: false };
    let current = null;
    try { current = adapter.findComposer ? adapter.findComposer() : null; } catch (e) { current = null; }
    if (!L.composer || L.composer.isConnected === false || current !== L.composer) {
      PB_SEND._leaseFault = "composer lease broken " + phase + " — the bound composer instance is no longer the page's composer; the delivery stops rather than re-target";
      return { ok: false, leased: true, error: PB_SEND._leaseFault };
    }
    return { ok: true, leased: true };
  },

  pbLeaseRelease() {
    const fault = PB_SEND._leaseFault;
    PB_SEND._lease = null;
    PB_SEND._leaseFault = null;
    return fault;
  },

  /* Finding the button to CLICK. COMBINED BUILD, Part B
   * item 3: the search is the composer's OWN scope, full
   * stop — the page-wide fallbacks (first-candidate document
   * search, any-button-with-send-in-its-name) are REMOVED.
   * A visible button elsewhere on the page is evidence of
   * nothing for this composer; if the leased/own scope holds
   * no send actuator, the outcome is actuator-unavailable
   * (the adapters' send-button stage) — an adapter outcome,
   * never a fence verdict and never a licence to search the
   * page (Part B item 8). Under a lease, the button must
   * belong to the leased composer's scope and the lease must
   * still hold, or no button is returned at all. */
  pbFindSendButton(adapter) {
    const L = PB_SEND._lease;
    if (L) {
      const chk = PB_SEND.pbLeaseCheck(adapter, "before submit");
      if (!chk.ok) return null;
      if (adapter._engagedComposer && adapter._engagedComposer !== L.composer) {
        PB_SEND._leaseFault = "composer lease broken before submit — the adapter engaged a different composer than the leased instance";
        return null;
      }
    }
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
    return null;
  },

  /* The bounded defer: never engage a destination that is
   * still generating — wait it out, bounded, or stall with
   * the reason named. Built entirely on the verdict above.
   *
   * COMBINED BUILD, Part B item 6: the defer is VISIBLE while
   * it runs. Progress (elapsed / remaining / bound) is
   * reported through window.PB_DEFER_REPORT when the content
   * script provides one — at the start, about once a second,
   * and at the end. This 45-second adapter defer stays
   * distinct from the fence's separate 20-second recheck:
   * different mechanism, different clock, different record. */
  async pbWaitForDestinationIdle(adapter) {
    const maxMs = (typeof window !== "undefined" && window.PB_TEST_DEFER_MAX_MS) ||
      (typeof PB_CRUSHER !== "undefined" && PB_CRUSHER.PB_CRUSHER_DEFER_MAX_MS) || 45000;
    const started = Date.now();
    /* Lease revalidation before typing (Part B item 4): the
     * defer is the last shared step every adapter crosses
     * before it engages and types. */
    const leaseChk = PB_SEND.pbLeaseCheck(adapter, "before typing");
    if (!leaseChk.ok) return { ok: false, stage: "lease", error: leaseChk.error };
    const report = (done) => {
      try {
        if (typeof window !== "undefined" && typeof window.PB_DEFER_REPORT === "function") {
          const elapsedMs = Date.now() - started;
          window.PB_DEFER_REPORT({ elapsedMs, remainingMs: Math.max(0, maxMs - elapsedMs), maxMs, done: !!done });
        }
      } catch (e) { /* reporting never disturbs the wait */ }
    };
    let lastReport = 0;
    while (PB_SEND.pbDestinationGenerating(adapter)) {
      if (Date.now() - started >= maxMs) {
        report(true);
        return { ok: false, stage: "generating", deferMs: Date.now() - started, error: "destination still generating after a " + Math.round(maxMs / 1000) + "s defer — nothing engaged, typed or clicked" };
      }
      if (Date.now() - lastReport >= 1000) { report(false); lastReport = Date.now(); }
      await new Promise((r) => setTimeout(r, 500));
    }
    if (Date.now() - started > 0) report(true);
    return { ok: true, deferMs: Date.now() - started };
  },
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = PB_SEND;
}
