/* Pulse Bridge — §1.9 BOUNDED IDENTITY CENSUS v2 (authorised by Ben, 2026-11-11 17:35 PST).
 *
 * v1 scoped its search to known turn selectors and found zero
 * turns on the first run — an empty result that says nothing
 * about the platform. v2 widens the net WITHIN the same bounds:
 * a document-wide census of candidate identity attributes
 * (any attribute whose name suggests an identifier), plus the
 * turn-scoped detail whenever turns are found.
 *
 * Bounds unchanged from §1.9: read-only; no clicks, focus,
 * typing, sending, navigation, refresh or mutation; message
 * bodies/prompts/attachments are NEVER read — tag names, class
 * names and attribute NAMES only; id-like values are emitted
 * only as length + shape class + short fingerprint.
 *
 * Run on the tab WITH THE CONVERSATION OPEN AND VISIBLE.
 * F12 → Console, paste, Enter. Send the PB-CENSUS block back.
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
      if (/id/i.test(a.name)) { rec.len = a.value.length; rec.shape = shape(a.value); rec.fnv = fnv(a.value); }
      out.attrs.push(rec);
    }
    var keys = Object.keys(el).filter(function (k) { return k.indexOf("__reactProps") === 0; });
    if (keys.length) {
      try {
        var props = el[keys[0]];
        if (props && typeof props === "object") out.reactPropKeys = Object.keys(props).slice(0, 30);
      } catch (e) {}
    }
    return out;
  }
  function censusTurn(root, maxEls) {
    var els = [root], desc = root.querySelectorAll("*");
    for (var i = 0; i < desc.length && els.length < maxEls; i++) els.push(desc[i]);
    return els.map(describeEl);
  }
  function ancestors(el, n) {
    var out = [], cur = el.parentElement;
    while (cur && out.length < n && cur !== document.body) { out.push(describeEl(cur)); cur = cur.parentElement; }
    return out;
  }

  var host = location.hostname;
  var report = {
    probe: "PB-CENSUS-1.9-v2", host: host, at: new Date().toISOString(),
    conversationPathPresent: /\/c\/|\/chat\//.test(location.pathname),
    idAttributeCensus: {}, turns: []
  };

  /* Document-wide census of candidate identity attributes:
   * for every attribute in the document whose name contains
   * "id", count its elements, its distinct values (by
   * fingerprint) and the shapes its values take. */
  var all = document.querySelectorAll("*");
  var seen = {};
  for (var i = 0; i < all.length; i++) {
    var el = all[i];
    for (var j = 0; j < el.attributes.length; j++) {
      var at = el.attributes[j];
      if (!/id/i.test(at.name)) continue;
      var key = el.tagName.toLowerCase() + "@" + at.name;
      if (!seen[key]) seen[key] = { elements: 0, values: {}, shapes: {} };
      seen[key].elements++;
      seen[key].values[fnv(at.value)] = true;
      seen[key].shapes[shape(at.value)] = true;
    }
  }
  Object.keys(seen).forEach(function (k) {
    report.idAttributeCensus[k] = {
      elements: seen[k].elements,
      distinctValues: Object.keys(seen[k].values).length,
      shapes: Object.keys(seen[k].shapes)
    };
  });

  if (host.indexOf("chatgpt") >= 0) {
    report.platform = "chatgpt";
    var turns = document.querySelectorAll('[data-testid^="conversation-turn-"], article[data-turn-id], [data-turn-id]');
    report.turnCount = turns.length;
    var start = Math.max(0, turns.length - 8);
    for (var t = start; t < turns.length; t++) {
      report.turns.push({ index: t, elements: censusTurn(turns[t], 40), ancestors: ancestors(turns[t], 3) });
    }
  } else if (host.indexOf("muse.ai") >= 0) {
    report.platform = "muse";
    var bubbles = document.querySelectorAll(".hatch-chat-groupable-bubble");
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
  return report.platform + ": " + report.turnCount + " turns; id-attribute kinds: " + Object.keys(report.idAttributeCensus).length;
})();
