"use strict";
/* Pulse Bridge — protocol core (platform-independent, pure logic).
 *
 * Implements Alex's Blueprint v1.0 §2 (routing markers) and the day-one
 * envelope decision (Alex's vision relay, 2026-11-06): every internal
 * bridge message carries {message_id, from, to, type, priority,
 * reply_to, body} so tasks, replies, review requests, acks and approvals
 * can be added later without rebuilding the protocol.
 *
 * Loaded by the background service worker (importScripts), by the popup
 * (script tag) and by the Node test suite (module.exports guard).
 */

/* Reserved handoff markers (Ben + Alex, 2026-11-06): a string no
 * ordinary conversation produces. The marker IS the hook — the seat
 * says who is speaking, the marker says who it is for. The old word
 * markers ("FOR ALEX:") are retired: a sentence a human might say
 * can never be a trigger. */
const PB_MARKERS = [
  { marker: "\u27e6PULSE-BRIDGE:TO-ALEX\u27e7", to: "alex" },
  { marker: "\u27e6PULSE-BRIDGE:TO-REMMY\u27e7", to: "remmy" },
  /* V0.13.0: Crusher, the retrieval occupant, is addressable in the
   * same format (Ben's design + veto, Alex's CRUSHER-SEAT ruling and
   * addressability proof, 2026-11-09). "crusher" is not a seat and
   * has no tab: the background routes crusher-addressed detections
   * down their own lane (see handleDetection) and they never enter
   * the pair machine. Listed LAST so lbMarkerForSeat — which takes
   * the first marker pointing away from a seat — keeps returning
   * the pair marker for both real seats, unchanged. */
  { marker: "\u27e6PULSE-BRIDGE:TO-CRUSHER\u27e7", to: "crusher" },
];

const PB_TYPES = ["message", "task", "reply", "review_request", "ack", "approval"];

/* Parse a completed message's text for a handoff marker.
 * V0.12.0 DELIMITER RULE (Ben's proposal, approved as proposed by
 * Ben's tap + words, 2026-11-08): the marker is a routing DELIMITER,
 * not a message-prefix requirement. The whole message is scanned;
 * the FIRST line that EQUALS a reserved marker exactly — a
 * standalone line, case-sensitive, nothing else on that line — is
 * the delimiter. Everything above it is discarded for bridge
 * delivery (it is the sender's user-facing text); the body is
 * everything beneath the marker line. A marker quoted inside a
 * sentence never routes, and a marker with no body beneath it
 * never routes. Only the first standalone occurrence triggers:
 * later marker lines inside the extracted body are payload and
 * pass through unchanged. (Pre-v0.12.0 the marker had to be the
 * first non-blank line; that prefix rule is retired.) */
function pbParseMarker(text) {
  if (!text) return null;
  const lines = String(text).split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    for (const { marker, to } of PB_MARKERS) {
      if (line === marker) {
        const body = lines.slice(i + 1).join("\n").trim();
        if (!body) return null;
        return { to, body };
      }
    }
  }
  return null;
}

/* Turn-text normalisation for the turn-capture trigger: keeps line
 * structure (the marker is a first-LINE test) while removing the
 * whitespace jitter a live page adds between reads. Applied to every
 * region snapshot, so prefix comparisons stay honest. */
function pbNormTurn(text) {
  return String(text || "")
    .replace(/\r\n/g, "\n")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

/* The turn delta: text appended to the region since the frozen
 * snapshot. Returns the appended text, "" when nothing was appended,
 * or null when attribution is impossible (no baseline, or the region
 * did not grow by appending — an edit or re-render — in which case
 * the caller resyncs silently and claims nothing). */
function pbTurnDelta(prev, cur) {
  if (!prev) return null;
  if (cur === prev) return "";
  if (cur.startsWith(prev)) return cur.slice(prev.length).replace(/^\n+/, "");
  return null;
}

/* Cross-check used on DETECTION evidence: the text a detector extracted
 * from the page must be compared against the message the page settles on
 * before anything is carried (the v0.1.0 lesson: reads can disagree with
 * the page). Normalisation: trim, collapse internal whitespace runs. */
function pbNormalise(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function pbTextsMatch(a, b) {
  return pbNormalise(a) === pbNormalise(b);
}

/* CONCLUSION BUILD (v0.22.0), Part 1: the Ben-facing words for a
 * station face. Face VALUES are state keys and do not change
 * (SENT-UNCONFIRMED stays the stored value); what Ben READS is
 * this mapping, applied at every render surface (popup history,
 * the station overlay). The old face read "sent, unconfirmed" —
 * a delivery claim the evidence does not carry. The new words
 * state only what is known: the click happened; no receipt has
 * been observed. Any other face passes through unchanged. */
function pbFaceWords(face) {
  if (face === "SENT-UNCONFIRMED") return "clicked; receipt not yet observed";
  return face || "";
}

/* CONCLUSION BUILD (v0.22.0), Part 4: the late re-observation
 * matcher. Given the destination page's turns as plain data
 * ({text, speaker}) and a retained letter body, is the body now
 * observable as a settled USER turn — the shape a delivered
 * letter takes in the destination conversation (it was typed
 * there as Ben's own message)? Containment on normalised text:
 * the page's turn carries the letter plus its marker line and
 * any platform dressing, so the body appears inside it. Pure
 * and fixture-driven; the content script gathers the turns
 * through the adapter's existing bubble interface — the same
 * settled-turn observation the receipt verdict already uses. */
function pbBodyObservedInTurns(turns, body) {
  const needle = pbNormalise(body);
  if (!needle || !Array.isArray(turns)) return false;
  for (const t of turns) {
    if (!t || t.speaker !== "user") continue;
    const hay = pbNormalise(t.text);
    if (hay && hay.includes(needle)) return true;
  }
  return false;
}

/* Content fingerprint for loop/dup prevention: two sightings of the
 * same body from the same sender are the same message, even re-rendered. */
function pbFingerprint(from, body) {
  const s = from + "\n" + pbNormalise(body);
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0;
  return "fp-" + h.toString(16);
}

let pbSeq = 0;
function pbMessageId() {
  pbSeq += 1;
  return "pb-" + Date.now().toString(36) + "-" + pbSeq.toString(36) +
         "-" + Math.floor(Math.random() * 1e6).toString(36);
}

/* Build an envelope. Defaults keep a plain relay a plain relay:
 * type "message", priority "normal", no reply_to. */
function pbEnvelope({ from, to, body, type = "message", priority = "normal", replyTo = null }) {
  if (!PB_TYPES.includes(type)) throw new Error("unknown envelope type: " + type);
  return {
    message_id: pbMessageId(),
    from,
    to,
    type,
    priority,
    reply_to: replyTo,
    body,
    fingerprint: pbFingerprint(from, body),
    detected_at: new Date().toISOString(),
  };
}

/* STAGE 3 — the carried text. What actually lands in the destination
 * conversation: a visible provenance header + the letter body, and
 * deliberately NO reserved marker — a carried letter can never be
 * re-detected as a fresh handoff, so the bridge cannot loop. The
 * header wording was disclosed to Ben in the Stage 3 scope (2026-11-06)
 * before he approved the build.
 *
 * CRUSHER V6.1 (Alex ruling 1, 2026-11-07): the envelope message_id
 * is the letter's authoritative identity, and the carried text now
 * wears it on a PB-ID line directly under the header. The ID line
 * is a CONFIRMATION AID — it lets the destination page expose
 * something independently observable (see pbTurnConfirms) — never
 * the identity mechanism itself; the envelope remains the source
 * of truth, and every retry carries the SAME id. */
function pbCarriedText(from, body, messageId) {
  const name = from === "remmy" ? "Remmy" : from === "alex" ? "Alex" : from;
  const head = "Via Pulse Bridge, from " + name + ":";
  const idLine = messageId ? "\nPB-ID: " + messageId : "";
  return head + idLine + "\n\n" + String(body || "");
}

/* The bridge ID a carried text wears, if any. */
function pbExtractBridgeId(text) {
  const m = /PB-ID: (pb-[a-z0-9-]+)/i.exec(String(text || ""));
  return m ? m[1] : null;
}

/* V7.1 NAMEPLATE STEP-OVER (live defect, caught 2026-11-07): the
 * Muse surface prepends a speaker nameplate line — "You:" — to
 * every rendered user bubble, so a delivered turn's text opens
 * with the nameplate, not the carried header. The strict prefix
 * test in pbTurnConfirms then failed on EVERY delivery into that
 * surface while the PB-ID sat visible in the bubble: the receipt
 * detector positively declared absence (full quiet window,
 * readable tail) and the proven-absence retry redelivered the
 * letter — duplicates on 4 of 4 live pairs. A live DOM read of a
 * delivered bubble (Ben, 2026-11-07 03:48) isolated it: user
 * classification correct, PB-ID present, first line "You:".
 * Alex's ruling: step over the KNOWN presentation prefix, then
 * apply the identity tests at full strictness — never loosen to
 * "PB-ID appears anywhere". Exactly one known prefix is bypassed,
 * exactly once; anything else still meets the header test as-is.
 * Works on the normalised text, where the nameplate line has
 * collapsed to the leading token "You:". */
const PB_NAMEPLATE_PREFIXES = ["You:"];
function pbStripNameplate(t) {
  for (const p of PB_NAMEPLATE_PREFIXES) {
    if (t === p) return "";
    if (t.startsWith(p + " ")) return t.slice(p.length + 1);
  }
  return t;
}

/* SEEABLE CONFIRMATION (Crusher V6.1, Alex step 4): does a rendered
 * user turn confirm a carried letter? The turn must open with the
 * carried header and carry the letter's PB-ID line. The ID sits at
 * the TOP of the carried text, so a page that collapses or
 * truncates the tail of a long turn still exposes it — the v0.6.0
 * full-text equality could not see a delivered long letter at all
 * (Finding 1 of the v1.1 consultation). A carried text with no ID
 * line (pre-V6.1 shape) falls back to full-text equality.
 * V7.1: the rendered turn is first stepped over its known speaker
 * nameplate (see pbStripNameplate) — presentation is not identity,
 * and the header + exact-ID tests below are unchanged. */
function pbTurnConfirms(turnText, carriedText) {
  const carried = String(carriedText || "");
  const head = pbNormalise(carried.split("\n")[0] || "");
  const t = pbStripNameplate(pbNormalise(turnText));
  if (!head || !t.startsWith(head)) return false;
  const id = pbExtractBridgeId(carried);
  if (id) return t.includes("PB-ID: " + id);
  return t === pbNormalise(carried);
}

/* Delivery dedup (Crusher V6.1, Alex ruling 1): keyed on the
 * envelope message_id — the authoritative identity — not on the
 * text fingerprint. A message_id enters the delivered ledger when
 * its delivery is confirmed; attempted-and-failed ids are recorded
 * separately so a failure is never silently retried by a later
 * state change. (The fingerprint survives as detection evidence
 * and as the bridge between the letterbox's sightings and the
 * envelope that carries the id — see background's fpToId index.) */
function pbAlreadyDelivered(state, messageId) {
  return (state.deliveredIds || []).includes(messageId) ||
         (state.deliveryFailedIds || []).includes(messageId);
}

/* ---- V0.11.0 P1 — FAITHFUL FILE HANDOFF (Ben's items, Alex's
 * ruling, Remmy+Alex design decisions, 2026-11-08) ----
 * A marked letter may carry ONE Markdown file inside an explicit
 * envelope:
 *
 *   [PB-FILE: <filename> sha256=<64 hex> bytes=<n>]
 *   ...the file's exact content...
 *   [PB-FILE-END]
 *
 * The sha256/bytes parameters are optional in syntax but a block
 * without them is UNDECLARED — extracted, never verified. The
 * content is the exact substring between the header line's newline
 * and the newline preceding the [PB-FILE-END] line (so a file
 * ending in "\n" shows an empty last line before the END marker).
 * Raw bytes are the authoritative integrity basis (Alex's ruling):
 * the hashes below are SHA-256 over the content's UTF-8 bytes, and
 * an LF-normalised match is a DIAGNOSTIC ONLY — it never upgrades
 * a mismatch to verified. Ambiguous, nested, multiple or
 * incomplete blocks are rejected, never guessed at. */
const PB_FILE_END = "[PB-FILE-END]";
const PB_FILE_OUTCOMES = ["FILE_DELIVERED_VERIFIED", "FILE_CONTENT_DELIVERED_VERIFIED", "FILE_HANDOFF_FAILED"];

function pbParseFileBlock(body) {
  if (!body) return null;
  const lines = String(body).split("\n");
  const headerIdxs = [];
  for (let i = 0; i < lines.length; i++) {
    if (/^\[PB-FILE:\s*[^\]]+\]\s*$/.test(lines[i])) headerIdxs.push(i);
  }
  if (!headerIdxs.length) return null; // no file in this letter — normal
  if (headerIdxs.length > 1) {
    return { ok: false, reason: "multiple PB-FILE blocks — v1 carries one file per letter" };
  }
  const h = headerIdxs[0];
  const inner = /^\[PB-FILE:\s*([^\]]+)\]\s*$/.exec(lines[h])[1];
  let name = inner.trim();
  let declaredSha256 = null;
  let declaredBytes = null;
  const shaM = /(?:^|\s)sha256=([0-9a-fA-F]{64})(?=\s|$)/.exec(inner);
  if (shaM) { declaredSha256 = shaM[1].toLowerCase(); name = inner.slice(0, shaM.index).trim(); }
  const bytM = /(?:^|\s)bytes=(\d+)(?=\s|$)/.exec(inner);
  if (bytM) {
    declaredBytes = parseInt(bytM[1], 10);
    if (!shaM || bytM.index < shaM.index) name = inner.slice(0, bytM.index).trim();
  }
  if (!name) return { ok: false, reason: "PB-FILE header carries no filename" };
  let end = -1;
  for (let i = h + 1; i < lines.length; i++) {
    if (lines[i].trim() === PB_FILE_END) { end = i; break; }
  }
  if (end < 0) return { ok: false, reason: "missing " + PB_FILE_END + " — incomplete block, rejected rather than guessed" };
  const content = lines.slice(h + 1, end).join("\n");
  if (/^\[PB-FILE:\s*[^\]]+\]\s*$/m.test(content)) {
    return { ok: false, reason: "nested PB-FILE header inside the block — ambiguous, rejected" };
  }
  return { ok: true, name, declaredSha256, declaredBytes, content };
}

/* UTF-8 bytes of a transported string — the byte basis every P1
 * hash and count is taken over. */
function pbUtf8Bytes(text) {
  const s = String(text == null ? "" : text);
  if (typeof TextEncoder !== "undefined") return new TextEncoder().encode(s);
  const bin = unescape(encodeURIComponent(s));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

/* SHA-256 (hex) over the UTF-8 bytes of text. Async: WebCrypto in
 * the browser/worker, Node's webcrypto in fixtures (injected as
 * globalThis.crypto there). Throws when no SubtleCrypto exists —
 * a verification that cannot run is a failed handoff, never a
 * silent pass. */
async function pbSha256Hex(text) {
  const subtle = typeof crypto !== "undefined" && crypto && crypto.subtle;
  if (!subtle) throw new Error("no SubtleCrypto available — cannot hash");
  const digest = await subtle.digest("SHA-256", pbUtf8Bytes(text));
  return Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

/* The verdict over a parsed block, given the hashes actually
 * computed at the receiving/checking end. "verified" requires the
 * declaration AND the raw-byte match; "lf-diagnostic" records that
 * the LF-normalised content matches the declaration — evidence
 * about what a surface did to the bytes, never a pass. */
function pbFileVerdict(parsed, actualSha256, lfSha256) {
  if (!parsed || !parsed.ok) return { status: "malformed" };
  const actualBytes = pbUtf8Bytes(parsed.content).length;
  if (!parsed.declaredSha256) {
    return { status: "undeclared", actualBytes, actualSha256: actualSha256 || null };
  }
  const bytesOk = parsed.declaredBytes == null || parsed.declaredBytes === actualBytes;
  if (actualSha256 && actualSha256 === parsed.declaredSha256 && bytesOk) {
    return { status: "verified", actualBytes, actualSha256 };
  }
  return {
    status: "mismatch",
    actualBytes,
    actualSha256: actualSha256 || null,
    lfMatch: !!(lfSha256 && parsed.declaredSha256 && lfSha256 === parsed.declaredSha256),
  };
}

const PB = { PB_MARKERS, PB_TYPES, pbParseMarker, pbNormalise, pbTextsMatch, pbFingerprint, pbEnvelope, pbNormTurn, pbTurnDelta, pbCarriedText, pbExtractBridgeId, pbTurnConfirms, pbAlreadyDelivered, PB_FILE_END, PB_FILE_OUTCOMES, pbParseFileBlock, pbUtf8Bytes, pbSha256Hex, pbFileVerdict, pbFaceWords, pbBodyObservedInTurns };
if (typeof module !== "undefined" && module.exports) module.exports = PB;
