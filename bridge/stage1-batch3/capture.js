'use strict';
/*
 * Pulse Bridge — capture acknowledgement, bridge epoch and
 * owner-review backend (Stage 1 batch 3; Build Plan 01 S3
 * scope items 7-9).
 *
 * Item 7: detection handoff is acknowledged, never fire-and-
 * forget. Every submission resolves to exactly one outcome —
 * REGISTERED, DUPLICATE, NOT_REGISTERED or REGISTRATION_UNKNOWN
 * — tied to the registration result. The letterbox (pending
 * handoffs) may retire a handoff only after a verified
 * registration/duplicate outcome or an explicit recorded
 * disposition. A collision or unidentifiable source is a
 * visible hold on the handoff, never a silent merge and never
 * an invented identity.
 *
 * Item 8: the bridge epoch persists and only moves forward.
 * Pause/disconnect advances it before dispatch eligibility
 * changes (the wiring calls advance() first; the store makes
 * the advance atomic and exportable). Detection, attempt and
 * receipt events carry the epoch; an event from a stale epoch —
 * or with no epoch at all — is rejected fail-closed and creates
 * nothing.
 *
 * Item 9: owner review is a backend over the ledger. Held work
 * keeps its identity and its record; Ben's decision is a
 * lifecycle event appended through the ledger (authority is
 * verified there, at the boundary — this module asserts
 * nothing). There is no purge, retry, reclassification or
 * destruction here: no method removes a record.
 */

const PBIdentity = require('./identity.js');

function isNonEmptyString(v) {
  return typeof v === 'string' && v.length > 0;
}

function clone(x) {
  return x === undefined ? undefined : JSON.parse(JSON.stringify(x));
}

/* ---------------- epoch ---------------- */

function createEpochStore(config) {
  const cfg = config || {};
  let epoch = Number.isInteger(cfg.initialEpoch) && cfg.initialEpoch >= 0 ? cfg.initialEpoch : 0;
  const history = [];

  function current() {
    return epoch;
  }

  function advance(reason) {
    const previous = epoch;
    epoch += 1;
    const entry = { epoch, previousEpoch: previous, reason: reason != null ? reason : null };
    history.push(entry);
    return clone(entry);
  }

  function stamp(kind, data) {
    return Object.assign({}, data || {}, { kind, epoch });
  }

  function admit(evt) {
    if (!evt || !Number.isInteger(evt.epoch)) {
      return { accepted: false, reason: 'epoch-missing' };
    }
    if (evt.epoch !== epoch) {
      return { accepted: false, reason: 'stale-epoch' };
    }
    return { accepted: true };
  }

  function exportState() {
    return { epoch, history: clone(history) };
  }

  function importState(state) {
    if (!state || !Number.isInteger(state.epoch) || state.epoch < 0) {
      return { status: 'REJECTED', reason: 'epoch-malformed' };
    }
    if (state.epoch < epoch) {
      return { status: 'REJECTED', reason: 'epoch-rollback' };
    }
    epoch = state.epoch;
    return { status: 'OK' };
  }

  return { current, advance, stamp, admit, exportState, importState };
}

/* ---------------- capture session ---------------- */

function createCaptureSession(config) {
  if (!config || !config.ledger) throw new Error('createCaptureSession requires a ledger');
  if (typeof config.sha256Hex !== 'function') throw new Error('createCaptureSession requires sha256Hex');
  const ledger = config.ledger;
  const epochStore = config.epochStore || null;
  const identity = PBIdentity.createIdentity({ sha256Hex: config.sha256Hex });
  const claims = PBIdentity.createClaimStore();
  const pending = new Map();
  const retired = new Map();

  async function submitDetection(detection) {
    if (!detection || !isNonEmptyString(detection.handoffId)) {
      return { handoffId: null, outcome: 'NOT_REGISTERED', reason: 'handoff-id-invalid', pbId: null, indexId: null };
    }
    const handoffId = detection.handoffId;

    // Epoch gate first, fail-closed: when an epoch store is
    // configured, EVERY detection passes through admit() — an
    // epoch-less detection is rejected 'epoch-missing' by the
    // same rule admit() applies everywhere else, never waved
    // past the gate for lacking the field the gate checks.
    // A stale or unverifiable detection creates nothing — not
    // even a pending entry.
    if (epochStore) {
      const verdict = epochStore.admit({ epoch: detection.epoch });
      if (!verdict.accepted) {
        return { handoffId, outcome: 'STALE', reason: verdict.reason, pbId: null, indexId: null };
      }
    } else if (detection.epoch != null) {
      return { handoffId, outcome: 'STALE', reason: 'epoch-unverifiable', pbId: null, indexId: null };
    }

    let entry = pending.get(handoffId);
    if (!entry) {
      entry = { handoffId, ack: null, disposition: null, holdReason: null };
      pending.set(handoffId, entry);
    }
    if (entry.ack && (entry.ack.outcome === 'REGISTERED' || entry.ack.outcome === 'DUPLICATE')) {
      return clone(entry.ack);
    }

    const derived = await identity.deriveFromSourceKey(detection.source || {});
    if (derived.status !== 'OK') {
      entry.ack = {
        handoffId, outcome: 'NOT_REGISTERED', reason: 'identity:' + derived.reason,
        pbId: null, indexId: null,
      };
      entry.holdReason = entry.ack.reason;
      return clone(entry.ack);
    }
    const claimResult = claims.claim(derived.pbid, derived.canonical);
    if (claimResult === 'IDENTITY-COLLISION') {
      entry.ack = {
        handoffId, outcome: 'NOT_REGISTERED', reason: 'identity-collision',
        pbId: derived.pbid, indexId: null,
      };
      entry.holdReason = 'identity-collision';
      return clone(entry.ack);
    }

    const result = await ledger.register({
      pbId: derived.pbid,
      idempotencyKey: 'handoff:' + handoffId,
      messageIndexRef: 'capture:' + handoffId,
      admitted: detection.admitted === true,
    });
    let ack;
    if (result.status === 'REGISTERED') {
      ack = {
        handoffId,
        outcome: result.duplicate ? 'DUPLICATE' : 'REGISTERED',
        pbId: derived.pbid, indexId: result.record.indexId, reason: null,
      };
    } else if (result.status === 'REGISTRATION_UNKNOWN') {
      ack = { handoffId, outcome: 'REGISTRATION_UNKNOWN', reason: result.reason || null, pbId: derived.pbid, indexId: null };
    } else if (result.status === 'INTEGRITY_FAULT') {
      // Outcome not established; the honest member of the
      // plan's four-outcome set is REGISTRATION_UNKNOWN.
      ack = { handoffId, outcome: 'REGISTRATION_UNKNOWN', reason: 'ledger-integrity-fault', pbId: derived.pbid, indexId: null };
    } else {
      ack = { handoffId, outcome: 'NOT_REGISTERED', reason: result.reason || result.status, pbId: derived.pbid, indexId: null };
    }
    entry.ack = ack;
    return clone(ack);
  }

  async function resolveUnknown(handoffId) {
    const entry = pending.get(handoffId);
    if (!entry || !entry.ack) return { handoffId, outcome: 'NOT_REGISTERED', reason: 'no-such-handoff' };
    if (entry.ack.outcome !== 'REGISTRATION_UNKNOWN') return clone(entry.ack);
    const resolved = await ledger.resolveByIdempotency('handoff:' + handoffId);
    if (resolved.status === 'REGISTERED' && resolved.record) {
      entry.ack = {
        handoffId, outcome: 'REGISTERED', reason: null,
        pbId: resolved.record.pbId, indexId: resolved.record.indexId,
        resolvedFromUnknown: true,
      };
    }
    return clone(entry.ack);
  }

  function recordDisposition(handoffId, disposition) {
    const entry = pending.get(handoffId);
    if (!entry) return { recorded: false, reason: 'no-such-handoff' };
    entry.disposition = {
      kind: disposition && disposition.kind != null ? disposition.kind : null,
      actor: disposition && disposition.actor != null ? disposition.actor : null,
      authorityRef: disposition && disposition.authorityRef != null ? disposition.authorityRef : null,
      note: disposition && disposition.note != null ? disposition.note : null,
    };
    return { recorded: true };
  }

  function retireHandoff(handoffId) {
    const entry = pending.get(handoffId);
    if (!entry) return { retired: false, reason: 'no-such-handoff' };
    const verified = entry.ack &&
      (entry.ack.outcome === 'REGISTERED' || entry.ack.outcome === 'DUPLICATE');
    if (!verified && !entry.disposition) {
      return { retired: false, reason: entry.holdReason ? 'held:' + entry.holdReason : 'outcome-unverified' };
    }
    pending.delete(handoffId);
    retired.set(handoffId, entry);
    return { retired: true, ack: clone(entry.ack), disposition: clone(entry.disposition) };
  }

  function pendingCount() {
    return pending.size;
  }

  function claimStore() {
    return claims;
  }

  return { submitDetection, resolveUnknown, recordDisposition, retireHandoff, pendingCount, claimStore };
}

/* ---------------- owner review ---------------- */

const REVIEW_DISPOSITIONS = new Set(['HELD_FOR_REVIEW', 'REFUSED', 'REFUTED', 'SUPERSEDED']);
const DECISIONS = {
  hold: 'HELD_FOR_REVIEW',
  skip: 'SKIPPED',
  discard: 'DISCARDED',
  close: 'CLOSED',
  refute: 'REFUTED',
};

function createOwnerReview(config) {
  if (!config || !config.ledger) throw new Error('createOwnerReview requires a ledger');
  const ledger = config.ledger;

  function listReviewItems() {
    return ledger.listByRegistrationOrder()
      .filter((rec) => REVIEW_DISPOSITIONS.has(rec.activeDisposition))
      .map((rec) => ({
        indexId: rec.indexId,
        pbId: rec.pbId,
        activeDisposition: rec.activeDisposition,
        eventCount: ledger.events(rec.indexId).length,
      }));
  }

  async function hold(indexId, act) {
    return ledger.appendEvent(indexId, {
      type: 'HELD_FOR_REVIEW',
      actor: act && act.actor != null ? act.actor : null,
      authorityRef: act && act.authorityRef != null ? act.authorityRef : null,
    });
  }

  async function decide(indexId, input) {
    const type = input && DECISIONS[input.decision];
    if (!type) return { status: 'REJECTED', reason: 'unknown-decision' };
    return ledger.appendEvent(indexId, {
      type,
      actor: input.actor != null ? input.actor : null,
      authorityRef: input.authorityRef != null ? input.authorityRef : null,
    });
  }

  return { listReviewItems, hold, decide };
}

const PBCapture = { createCaptureSession, createEpochStore, createOwnerReview };

if (typeof module !== 'undefined' && module.exports) {
  module.exports = PBCapture;
}
if (typeof globalThis !== 'undefined') {
  globalThis.PBCapture = PBCapture;
}
