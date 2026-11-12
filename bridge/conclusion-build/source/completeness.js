"use strict";
/*
 * Pulse Bridge — F-6 whole-message completeness (Combined Build,
 * Part B item 1). Implements the definitions adopted under
 * Ben's delegation, Stage 0 Pack §2.2 + Gate 4 §4.4:
 *
 * - Character count: Unicode scalar values (code points), not
 *   UTF-16 units, not grapheme clusters. Unpaired surrogates
 *   are MALFORMED — never silently replaced.
 * - Block count: one TEXT block if any text payload exists,
 *   plus one FILE block per syntactically valid PB-FILE block
 *   (current protocol: at most one; nested/multiple/incomplete
 *   PB-FILE structure is MALFORMED, never guessed).
 * - Hash: SHA-256 over the exact UTF-8 bytes of the payload,
 *   excluding the PB-COMPLETE trailer and its one framing LF.
 * - Trailer: exactly one, final line —
 *   PB-COMPLETE: chars=<decimal> blocks=<decimal> sha256=<64 lowercase hex>
 *   No leading-zero ambiguity, no uppercase digest, no
 *   trailing bytes, no second trailer.
 * - Repair/conflict: an incomplete copy quarantines under its
 *   PB-ID and never poisons it — a later complete copy repairs
 *   the quarantine. A divergent COMPLETE payload under an
 *   existing complete record is CONFLICT / OWNER-REVIEW,
 *   never an overwrite, never latest-wins.
 * - Append (Gate 4, Option A): the composite is the original
 *   payload bytes unchanged, one framing LF, the header
 *   "PB-APPEND/1 actor=ben bytes=<decimal> sha256=<hex>"
 *   (count and digest over the segment's exact UTF-8 bytes),
 *   one LF, then Ben's exact segment bytes. One segment per
 *   message; an all-whitespace segment is rejected as empty.
 *   The composite is the F-6 payload: it is counted, hashed
 *   and trailered as a whole, the original digest retained
 *   as provenance by the caller's record.
 *
 * PB-FILE verification stays a separate channel (protocol.js);
 * nothing here substitutes for it, and it cannot satisfy
 * whole-message completeness.
 */

function pbCountScalars(text) {
  let count = 0;
  for (let i = 0; i < text.length; i++) {
    const c = text.charCodeAt(i);
    if (c >= 0xd800 && c <= 0xdbff) {
      const d = text.charCodeAt(i + 1);
      if (!(d >= 0xdc00 && d <= 0xdfff)) return { ok: false, reason: 'unpaired-surrogate' };
      i++; count++;
    } else if (c >= 0xdc00 && c <= 0xdfff) {
      return { ok: false, reason: 'unpaired-surrogate' };
    } else count++;
  }
  return { ok: true, count };
}

const PB_FILE_HEADER_RE = /^\[PB-FILE:\s*[^\]]+\]\s*$/;
const PB_FILE_END_LINE = '[PB-FILE-END]';

/* Structured block analysis over the payload's lines. Returns
 * { ok, blocks, fileBlocks } or { ok:false, reason }. */
function pbAnalyseBlocks(payload) {
  const lines = payload.split('\n');
  const headerIdxs = [];
  let endIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (PB_FILE_HEADER_RE.test(lines[i])) headerIdxs.push(i);
    if (lines[i].trim() === PB_FILE_END_LINE) { if (endIdx === -1) endIdx = i; }
  }
  if (headerIdxs.length > 1) return { ok: false, reason: 'multiple-file-blocks' };
  let fileBlocks = 0;
  let textExists = payload.length > 0;
  if (headerIdxs.length === 1) {
    const h = headerIdxs[0];
    if (endIdx === -1 || endIdx < h) return { ok: false, reason: 'file-block-incomplete' };
    for (let i = h + 1; i < endIdx; i++) {
      if (PB_FILE_HEADER_RE.test(lines[i])) return { ok: false, reason: 'file-block-nested' };
    }
    fileBlocks = 1;
    const outside = lines.slice(0, h).concat(lines.slice(endIdx + 1)).join('\n');
    textExists = outside.length > 0;
  } else if (endIdx !== -1) {
    return { ok: false, reason: 'file-end-without-header' };
  }
  return { ok: true, blocks: (textExists ? 1 : 0) + fileBlocks, fileBlocks };
}

const PB_TRAILER_RE = /^PB-COMPLETE: chars=(\d+) blocks=(\d+) sha256=([0-9a-f]{64})$/;
const PB_APPEND_RE = /^PB-APPEND\/1 actor=ben bytes=(\d+) sha256=([0-9a-f]{64})$/;

function pbNoLeadingZero(s) { return s === '0' || s[0] !== '0'; }

function createCompleteness(config) {
  if (!config || typeof config.sha256Hex !== 'function') {
    throw new Error('createCompleteness requires sha256Hex');
  }
  const sha256Hex = config.sha256Hex;
  const utf8Bytes = (s) => new TextEncoder().encode(s).length;

  async function analyse(payload) {
    if (typeof payload !== 'string') return { ok: false, reason: 'payload-not-string' };
    const chars = pbCountScalars(payload);
    if (!chars.ok) return { ok: false, reason: chars.reason };
    const blocks = pbAnalyseBlocks(payload);
    if (!blocks.ok) return { ok: false, reason: blocks.reason };
    const sha256 = await sha256Hex(payload);
    return { ok: true, chars: chars.count, blocks: blocks.blocks, sha256 };
  }

  async function buildTrailer(payload) {
    const a = await analyse(payload);
    if (!a.ok) return a;
    return { ok: true, trailer: 'PB-COMPLETE: chars=' + a.chars + ' blocks=' + a.blocks + ' sha256=' + a.sha256, ...a };
  }

  async function serialize(payload) {
    const t = await buildTrailer(payload);
    if (!t.ok) return t;
    return { ok: true, text: payload + '\n' + t.trailer, chars: t.chars, blocks: t.blocks, sha256: t.sha256 };
  }

  /* Verify a serialized message. Returns one of:
   * COMPLETE { payload, chars, blocks, sha256 }
   * INCOMPLETE { reason, declared?, actual? } — well-formed
   *   trailer, but the payload does not match it (truncated,
   *   altered): quarantine, never present as whole.
   * MALFORMED { reason } — the framing itself is not the
   *   adopted grammar: no trust placed in any of it. */
  async function verify(text) {
    if (typeof text !== 'string') return { status: 'MALFORMED', reason: 'not-a-string' };
    const lines = text.split('\n');
    const trailerLines = lines.filter((l) => PB_TRAILER_RE.test(l));
    if (trailerLines.length === 0) return { status: 'MALFORMED', reason: 'trailer-missing' };
    if (trailerLines.length > 1) return { status: 'MALFORMED', reason: 'trailer-duplicated' };
    const last = lines[lines.length - 1];
    const m = PB_TRAILER_RE.exec(last);
    if (!m) return { status: 'MALFORMED', reason: 'trailer-not-final-line' };
    if (!pbNoLeadingZero(m[1]) || !pbNoLeadingZero(m[2])) return { status: 'MALFORMED', reason: 'leading-zero-ambiguity' };
    const declared = { chars: Number(m[1]), blocks: Number(m[2]), sha256: m[3] };
    const payload = lines.slice(0, -1).join('\n');
    const a = await analyse(payload);
    if (!a.ok) return { status: 'MALFORMED', reason: a.reason, declared };
    if (a.chars !== declared.chars || a.blocks !== declared.blocks || a.sha256 !== declared.sha256) {
      return { status: 'INCOMPLETE', reason: 'payload-mismatch', declared, actual: { chars: a.chars, blocks: a.blocks, sha256: a.sha256 }, payload };
    }
    return { status: 'COMPLETE', payload, chars: a.chars, blocks: a.blocks, sha256: a.sha256 };
  }

  /* Gate 4 Option A append: composite = original + framing LF
   * + header + LF + Ben's exact segment bytes. */
  async function appendSegment(payload, segment) {
    if (typeof segment !== 'string' || segment.trim().length === 0) {
      return { ok: false, reason: 'append-segment-empty' };
    }
    if (typeof payload !== 'string') return { ok: false, reason: 'payload-not-string' };
    const bytes = utf8Bytes(segment);
    const sha256 = await sha256Hex(segment);
    const header = 'PB-APPEND/1 actor=ben bytes=' + bytes + ' sha256=' + sha256;
    return { ok: true, composite: payload + '\n' + header + '\n' + segment, header, segmentBytes: bytes, segmentSha256: sha256 };
  }

  async function splitAppend(composite) {
    if (typeof composite !== 'string') return { ok: false, reason: 'not-a-string' };
    const lines = composite.split('\n');
    const idxs = [];
    lines.forEach((l, i) => { if (PB_APPEND_RE.test(l)) idxs.push(i); });
    if (idxs.length === 0) return { ok: true, appended: false, original: composite, segment: null };
    if (idxs.length > 1) return { ok: false, reason: 'append-header-ambiguous' };
    const i = idxs[0];
    const m = PB_APPEND_RE.exec(lines[i]);
    if (!pbNoLeadingZero(m[1])) return { ok: false, reason: 'leading-zero-ambiguity' };
    const segment = lines.slice(i + 1).join('\n');
    if (utf8Bytes(segment) !== Number(m[1])) return { ok: false, reason: 'append-bytes-mismatch' };
    if ((await sha256Hex(segment)) !== m[2]) return { ok: false, reason: 'append-sha-mismatch' };
    return { ok: true, appended: true, original: lines.slice(0, i).join('\n'), segment };
  }

  return { analyse, buildTrailer, serialize, verify, appendSegment, splitAppend, utf8Bytes };
}

/* Quarantine / repair / conflict record, keyed by PB-ID.
 * Pure bookkeeping: it decides what a copy MEANS, never what
 * the bridge displays — presentation stays with the caller. */
function createCompletenessRegister() {
  const complete = new Map();    // pbId -> { payload, sha256 }
  const quarantined = new Map(); // pbId -> { arrivals, lastReason }
  return {
    async submit(pbId, text, completeness) {
      const v = await completeness.verify(text);
      if (v.status === 'COMPLETE') {
        const prior = complete.get(pbId);
        if (prior) {
          if (prior.payload === v.payload) return { status: 'ALREADY_COMPLETE', verdict: v };
          return { status: 'CONFLICT', verdict: v, heldPayload: prior.payload };
        }
        const repaired = quarantined.has(pbId);
        quarantined.delete(pbId);
        complete.set(pbId, { payload: v.payload, sha256: v.sha256 });
        return { status: repaired ? 'REPAIRED' : 'COMPLETE', verdict: v };
      }
      if (complete.has(pbId)) return { status: v.status, verdict: v, note: 'complete-record-stands' };
      const q = quarantined.get(pbId) || { arrivals: 0, lastReason: null };
      q.arrivals += 1; q.lastReason = v.reason;
      quarantined.set(pbId, q);
      return { status: v.status, verdict: v, arrivals: q.arrivals };
    },
    isComplete(pbId) { return complete.has(pbId); },
    isQuarantined(pbId) { return quarantined.has(pbId); },
    completedPayload(pbId) { const r = complete.get(pbId); return r ? r.payload : null; },
  };
}

const PBComplete = { createCompleteness, createCompletenessRegister, _internal: { pbCountScalars, pbAnalyseBlocks } };

if (typeof module !== 'undefined' && module.exports) {
  module.exports = PBComplete;
}
if (typeof globalThis !== 'undefined') {
  globalThis.PBComplete = PBComplete;
}
