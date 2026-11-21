/* Pulse Bridge — §1.9 BOUNDED IDENTITY CENSUS (authorised by Ben, 2026-11-11 17:35 PST).
 *
 * Read-only inspection of message/turn STRUCTURE and candidate
 * identity ATTRIBUTES on ONE already-open tab. Bounds, from the
 * Stage 0 pack §1.9 authorisation:
 *   - no clicks, focus, typing, sending, navigation, refresh,
 *     cache purge, forced re-fetch, or any page mutation;
 *   - conversation bodies, prompts and attachment contents are
 *     NEVER read: this script reads tag names, class names and
 *     attribute NAMES only. For id-like attribute VALUES it emits
 *     only a length, a shape class and a short non-cryptographic
 *     fingerprint — never the value itself;
 *   - one run per tab; output is one JSON block for the redacted
 *     evidence report.
 *
 * Run: open the tab, F12 → Console, paste this whole file, Enter.
 * Send the printed PB-CENSUS block back to Remmy.
 */
(function () {
  "use strict";
  function fnv(str) {
    var h = 0x811c9dc5;
    for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = (h * 0x01000193) >>> 0; }
    return ("0000000" + h.toString(16)).slice(-8);
  }
  function shape(v) {
    if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v)) return "uuid";
    if (/^[0-9]+$/.test(v)) return "digits";
    if (/^[0-9a-f]+$/i.test(v)) return "hex";
    if (/^[A-Za-z0-9_-]+$/.test(v)) return "token";
    return "other";
  }
  function describeEl(el) {
    var out = { tag: el.tagName.toLowerCase(), attrs: [] };
    var cls = (el.getAttribute && el.getAttribute("class")) || "";
    if (cls) out.classes = cls.split(/\s+/).filter(Boolean).slice(0, 6);
    for (var i = 0; i < el.attributes.length; i++) {
      var a = el.attributes[i];
      if (a.name === "class" || a.name === "style") continue;
      var rec = { name: a.name };
      if (/id/i.test(a.name)) {
        rec.len = a.value.length;
        rec.shape = shape(a.value);
        rec.fnv = fnv(a.value);
      }
      out.attrs.push(rec);
    }
    var keys = Object.keys(el).filter(function (k) { return k.indexOf("__reactProps") === 0; });
    if (keys.length) {
      try {
        var props = el[keys[0]];
        if (props && typeof props === "object") out.reactPropKeys = Object.keys(props).slice(0, 30);
      } catch (e) { /* keys only; values never touched */ }
    }
    return out;
  }
  function censusTurn(root, maxEls) {
    var els = [root];
    var desc = root.querySelectorAll("*");
    for (var i = 0; i < desc.length && els.length < maxEls; i++) els.push(desc[i]);
    return els.map(describeEl);
  }
  function ancestors(el, n) {
    var out = [], cur = el.parentElement;
    while (cur && out.length < n && cur !== document.body) { out.push(describeEl(cur)); cur = cur.parentElement; }
    return out;
  }

  var host = location.hostname;
  var report = { probe: "PB-CENSUS-1.9", host: host, at: new Date().toISOString(), turns: [] };

  if (host.indexOf("chatgpt") >= 0) {
    var turns = document.querySelectorAll('[data-testid^="conversation-turn-"], article[data-turn-id]');
    report.platform = "chatgpt";
    report.turnCount = turns.length;
    var start = Math.max(0, turns.length - 8);
    for (var t = start; t < turns.length; t++) {
      report.turns.push({ index: t, elements: censusTurn(turns[t], 40), ancestors: ancestors(turns[t], 3) });
    }
  } else if (host.indexOf("muse.ai") >= 0) {
    var bubbles = document.querySelectorAll(".hatch-chat-groupable-bubble");
    report.platform = "muse";
    report.turnCount = bubbles.length;
    var s2 = Math.max(0, bubbles.length - 8);
    for (var b = s2; b < bubbles.length; b++) {
      report.turns.push({ index: b, elements: censusTurn(bubbles[b], 25), ancestors: ancestors(bubbles[b], 5) });
    }
  } else {
    report.platform = "unrecognised-host";
  }

  var text = "PB-CENSUS-BEGIN\n" + JSON.stringify(report, null, 1) + "\nPB-CENSUS-END";
  console.log(text);
  try { copy(text); console.log("(also copied to clipboard)"); } catch (e) {}
  return report.platform + ": " + report.turnCount + " turns found, census printed above";
})();
