'use strict';
/*
 * Pulse Bridge — PB-ID source-identity layer (Stage 1, scope item 1).
 *
 * Implements the adopted Gate 1 rule (Stage 0 Pack Rev06 as
 * corrected by Rev07, SS1.3-SS1.5, SS1.8):
 *
 * - A PB-ID derives ONLY from a verified stable source-occurrence
 *   key: a platform-native per-message ID (PBID-SRC1) or a verified
 *   occurrence tuple (PBID-OCC1). Sender and payload are validation
 *   attributes, never identity inputs.
 * - Canonical form: versioned, fixed field order, length-prefixed
 *   UTF-8. Lengths count UTF-8 BYTES. Null encodes as -1:, empty
 *   string as 0:. Every line, including the last, is LF-terminated.
 *   No implicit coercion, no locale-sensitive handling, no Unicode
 *   normalisation, no trimming.
 * - Machine PB-ID: "pb1-" + lowercase hex SHA-256 of the exact
 *   canonical UTF-8 bytes (candidate representation, Pack SS1.3).
 * - Fail-closed: anything that cannot be established exactly is
 *   IDENTITY-UNKNOWN. A PB-ID claimed by two different canonical
 *   source keys is IDENTITY-COLLISION, held in a separate
 *   identity-claim record that retains canonical source-key
 *   material only (never message body or payload).
 *
 * This module is environment-agnostic: the SHA-256 function is
 * injected (node:crypto in fixtures; crypto.subtle in the
 * extension). It touches no storage and no DOM.
 */

const textEncoder = typeof TextEncoder !== 'undefined' ? new TextEncoder() : null;

function utf8ByteLength(value) {
  if (textEncoder) return textEncoder.encode(value).length;
  // Fallback for environments without TextEncoder: count UTF-8 bytes
  // by code point. Surrogate pairs count as one supplementary char.
  let bytes = 0;
  for (const ch of value) {
    const cp = ch.codePointAt(0);
    if (cp < 0x80) bytes += 1;
    else if (cp < 0x800) bytes += 2;
    else if (cp < 0x10000) bytes += 3;
    else bytes += 4;
  }
  return bytes;
}

function encodeField(name, value) {
  // Explicit null is the only absence the canonical form encodes
  // (-1:). Undefined means the field was never supplied — a
  // contract error, never silently encoded. Non-string values are
  // never coerced (Batch 1 review correction, 2026-11-11).
  if (value === null) return name + ':-1:';
  if (typeof value !== 'string') {
    throw new TypeError('field "' + name + '" must be a string or explicit null');
  }
  return name + ':' + utf8ByteLength(value) + ':' + value;
}

function canonicalSourceKey(fields) {
  return (
    'PBID-SRC1\n' +
    encodeField('platform', fields.platform) + '\n' +
    encodeField('conversation', fields.conversation) + '\n' +
    encodeField('message_id', fields.messageId) + '\n'
  );
}

function canonicalOccurrenceKey(fields) {
  return (
    'PBID-OCC1\n' +
    encodeField('platform', fields.platform) + '\n' +
    encodeField('conversation', fields.conversation) + '\n' +
    encodeField('occurrence', fields.occurrence) + '\n'
  );
}

function unknown(reason) {
  return { status: 'IDENTITY-UNKNOWN', reason };
}

/*
 * createIdentity({ sha256Hex })
 * sha256Hex: (utf8Text) => hex string | Promise<hex string>.
 *
 * deriveFromSourceKey(input) resolves to one of:
 *   { status: 'OK', pbid, canonical }
 *   { status: 'IDENTITY-UNKNOWN', reason }
 *
 * input, native form:
 *   { form: 'native', platform, scope: 'global'|'conversation',
 *     conversation, messageId }
 *   scope is REQUIRED and must be exact; missing or invalid scope
 *   is UNKNOWN, never defaulted. A conversation-scoped ID without
 *   a conversation is UNKNOWN. A globally scoped ID may carry
 *   conversation: null (explicit null encodes -1:); a MISSING
 *   conversation field is UNKNOWN in both scopes — absence is
 *   never conflated with explicit null, and non-string field
 *   values are never coerced.
 * input, occurrence form:
 *   { form: 'occurrence', platform, conversation, occurrence }
 * Extra fields (body, sender, ...) are ignored by design: they are
 * not identity inputs (Pack SS1.3, SS1.8 rule 4).
 */
function createIdentity(deps) {
  const sha256Hex = deps && deps.sha256Hex;
  if (typeof sha256Hex !== 'function') {
    throw new Error('createIdentity requires a sha256Hex function');
  }

  // Field-state discipline (Batch 1 review correction): a missing
  // field (undefined) is never treated as an explicit null, and a
  // non-string value is never coerced. Both fail closed.
  function fieldState(v) {
    if (v === undefined) return 'missing';
    if (v === null) return 'null';
    if (typeof v === 'string') return 'string';
    return 'invalid';
  }

  async function deriveFromSourceKey(input) {
    if (!input || typeof input !== 'object') return unknown('no-input');
    if (fieldState(input.platform) !== 'string' || input.platform.length === 0) {
      return unknown(fieldState(input.platform) === 'invalid' ? 'platform-invalid' : 'platform-missing');
    }

    let canonical;
    if (input.form === 'native') {
      const midState = fieldState(input.messageId);
      if (midState === 'invalid') return unknown('message-id-invalid');
      if (midState !== 'string' || input.messageId.length === 0) {
        return unknown('message-id-missing');
      }
      // Scope is required and must be exact — never defaulted.
      if (input.scope !== 'global' && input.scope !== 'conversation') {
        return unknown('scope-invalid');
      }
      const convState = fieldState(input.conversation);
      if (convState === 'invalid') return unknown('conversation-invalid');
      if (convState === 'missing') return unknown('conversation-missing');
      if (input.scope === 'conversation' &&
          (convState !== 'string' || input.conversation.length === 0)) {
        return unknown('conversation-missing-for-conversation-scoped-id');
      }
      canonical = canonicalSourceKey({
        platform: input.platform,
        conversation: input.conversation,
        messageId: input.messageId,
      });
    } else if (input.form === 'occurrence') {
      const convState = fieldState(input.conversation);
      if (convState === 'invalid') return unknown('conversation-invalid');
      if (convState !== 'string' || input.conversation.length === 0) {
        return unknown('conversation-missing');
      }
      const occState = fieldState(input.occurrence);
      if (occState === 'invalid') return unknown('occurrence-invalid');
      if (occState !== 'string' || input.occurrence.length === 0) {
        return unknown('occurrence-missing');
      }
      canonical = canonicalOccurrenceKey({
        platform: input.platform,
        conversation: input.conversation,
        occurrence: input.occurrence,
      });
    } else {
      return unknown('form-not-recognised');
    }

    let digest;
    try {
      digest = await sha256Hex(canonical);
    } catch (err) {
      return unknown('hash-unavailable');
    }
    if (typeof digest !== 'string' || !/^[0-9a-f]{64}$/.test(digest)) {
      return unknown('hash-result-invalid');
    }
    return { status: 'OK', pbid: 'pb1-' + digest, canonical };
  }

  return { deriveFromSourceKey };
}

/*
 * Identity-claim record (Pack SS1.5): keyed by PB-ID, retains the
 * canonical source-key material so a later claim can be compared
 * with the original. Never stores message body or payload.
 *
 * claim(pbid, canonical) ->
 *   'CLAIMED'            first claim for this PB-ID
 *   'MATCH'              same canonical material claimed again
 *   'IDENTITY-COLLISION' different canonical material at this PB-ID;
 *                        the original record is retained unchanged
 */
function createClaimStore() {
  const claims = new Map();
  return {
    claim(pbid, canonical) {
      if (!claims.has(pbid)) {
        claims.set(pbid, { pbid, canonical });
        return 'CLAIMED';
      }
      return claims.get(pbid).canonical === canonical ? 'MATCH' : 'IDENTITY-COLLISION';
    },
    get(pbid) {
      const rec = claims.get(pbid);
      return rec ? rec.canonical : undefined;
    },
    record(pbid) {
      const rec = claims.get(pbid);
      return rec ? { pbid: rec.pbid, canonical: rec.canonical } : undefined;
    },
    size() {
      return claims.size;
    },
  };
}

const PBIdentity = {
  utf8ByteLength,
  encodeField,
  canonicalSourceKey,
  canonicalOccurrenceKey,
  createIdentity,
  createClaimStore,
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = PBIdentity;
}
if (typeof globalThis !== 'undefined') {
  globalThis.PBIdentity = PBIdentity;
}
