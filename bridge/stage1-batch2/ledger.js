'use strict';
/*
 * Pulse Bridge — registration ledger core (Stage 1, scope items
 * 2-6). Implements Bridge Registration Contract Rev 02 (FINAL,
 * blob b9cffdbd551b808af3e6e37d7af5b77747ab99e8).
 *
 * Revision 2 (batch 2 review corrections, 2026-11-11):
 * - Authority boundary: authority-bearing transitions require
 *   an injected verifier; unavailable without one.
 * - R-2 promotion requires established EXACT correlation;
 *   UNKNOWN is a hold, never a match.
 * - Intake recording sits inside the same serialisation chain
 *   as registration; the R-2 relationship is deterministic.
 * - importState validates the complete integrity boundary
 *   before any state becomes operational.
 * - Commit discipline: registration stages before publishing;
 *   other mutations roll back on integrity failure; any
 *   integrity failure faults the ledger — no partial commits,
 *   no sequence reuse, no further work on inconsistent state.
 *
 * The ledger is the record: one-to-one permanent Index ID <->
 * PB-ID registration (SS2); IDX-YYYYMMDD-NNNNNN with the UTC
 * date as metadata and the numeric sequence as sole ordering
 * authority (SS3, R-3); idempotent registration with ambiguous
 * outcomes resolved by idempotency identity (SS3.3-3.4); the
 * registration boundary (SS4); the thin routing record (SS5);
 * append-only lifecycle events from the closed core set with
 * the projection as a deterministic fold (SS6, SS9); intake
 * and R-2 promotion (SS4.3, SS7.2A); supersession and the
 * one-shot B boundary (SS7.3-7.4); dispatch vs delivery
 * fact/knowledge (SS7.5-7.6); duplicate counting and the
 * lifetime confirmed-delivered block as a predicate separate
 * from refusal (SS8); the Message Index route kept apart from
 * the Information Index route (SS7.2, SS8.6, SS10).
 *
 * Deliberately NOT decided here (Contract SS13 open items,
 * surfaced rather than silently settled):
 * - SS13.5 event-volume policy: `duplicateEventPolicy` is a
 *   REQUIRED constructor argument ('event' | 'counter-only');
 *   there is no default.
 * - SS13.8 record-integrity canonicalisation: this module uses
 *   a proposed form ('PBR-REC1', length-prefixed fields in SS5
 *   order, SHA-256) pending adoption; verifyIntegrity detects
 *   tampering under that form. The form is NOT adopted by
 *   being implemented.
 * - Admission checks (SS13.2): the caller asserts `admitted`;
 *   `admitted: true` is an assertion, never treated here as
 *   proof that the named checks occurred.
 *
 * AUTHORITY BOUNDARY: a caller's actor string or authorityRef
 * is an assertion, not proof. Authority-bearing transitions
 * (SUPERSEDED, RE_PRESENTATION_DIRECTED, FORCE_SENT, REFUTED,
 * DISCARDED) are decided by an injected `authorityVerifier`
 * supplied by the trusted wiring layer, where proof of the
 * owner's act lives. With no verifier configured those
 * transitions are UNAVAILABLE (rejected).
 *
 * DURABILITY SCOPE: this core demonstrates a serialised
 * single-instance model. It does not by itself establish
 * durable commit, nor a single authoritative allocator across
 * restarts or multiple instances. A persistence/concurrency
 * substrate providing those properties must be selected and
 * proven before the ledger is treated as operationally
 * durable; export/import carries state for restart and
 * integrity checking only.
 *
 * Input discipline follows the batch 1 family rule: non-string
 * or missing identity fields are rejected, never coerced.
 */

const PBIdentity = require('./identity.js');

const CORE_EVENT_TYPES = new Set([
  'REGISTERED',
  'PRE_REGISTRATION_REFUSAL_PROMOTED',
  'DUPLICATE_OBSERVED',
  'ATTEMPT_CREATED',
  'ATTEMPT_VALIDATED',
  'ATTEMPT_REJECTED',
  'REFUSED',
  'REFUTED',
  'SUPERSEDED',
  'RE_PRESENTATION_DIRECTED',
  'DISPATCHED',
  'FORCE_SENT',
  'DELIVERY_CONFIRMED',
  'PROVEN_NOT_DELIVERED',
  'DELIVERY_UNKNOWN',
  'SKIPPED',
  'DISCARDED',
  'HELD_FOR_REVIEW',
  'CLOSED',
  'CORRECTION',
]);

const SYSTEM_ONLY_TYPES = new Set([
  'REGISTERED',
  'PRE_REGISTRATION_REFUSAL_PROMOTED',
  'DUPLICATE_OBSERVED',
  'ATTEMPT_CREATED',
]);

const AUTHORITY_TYPES = new Set([
  'SUPERSEDED',
  'RE_PRESENTATION_DIRECTED',
  'FORCE_SENT',
  'REFUTED',
  'DISCARDED',
]);

const DISPOSITION_TYPES = new Set([
  'REFUSED', 'REFUTED', 'SKIPPED', 'DISCARDED', 'HELD_FOR_REVIEW', 'CLOSED',
]);

function isNonEmptyString(v) {
  return typeof v === 'string' && v.length > 0;
}

function pad(n, w) {
  return String(n).padStart(w, '0');
}

function utcDateSegment(ms) {
  const d = new Date(ms);
  return String(d.getUTCFullYear()) + pad(d.getUTCMonth() + 1, 2) + pad(d.getUTCDate(), 2);
}

function clone(x) {
  return x === undefined ? undefined : JSON.parse(JSON.stringify(x));
}

function numericSuffix(id, prefix) {
  if (typeof id !== 'string' || !id.startsWith(prefix)) return null;
  const n = Number(id.slice(prefix.length));
  return Number.isInteger(n) && n >= 0 ? n : null;
}

function createLedger(config) {
  if (!config || typeof config.now !== 'function') {
    throw new Error('createLedger requires a now() clock');
  }
  if (typeof config.sha256Hex !== 'function') {
    throw new Error('createLedger requires a sha256Hex function');
  }
  if (config.duplicateEventPolicy !== 'event' && config.duplicateEventPolicy !== 'counter-only') {
    throw new Error("duplicateEventPolicy is required: 'event' | 'counter-only' (Contract SS13.5 — no silent default)");
  }
  const now = config.now;
  const sha256Hex = config.sha256Hex;
  const duplicateEventPolicy = config.duplicateEventPolicy;
  const authorityVerifier = typeof config.authorityVerifier === 'function'
    ? config.authorityVerifier : null;

  let counter = Number.isInteger(config.initialSequence) ? config.initialSequence : 0;
  let eventSeq = 0;
  let attemptSeq = 0;
  let intakeSeq = 0;
  let faulted = false;
  let failReadBackArmed = !!config.failReadBackOnce;

  const byIndex = new Map();
  const byPbid = new Map();
  const eventsByIndex = new Map();
  const attempts = new Map();
  const intake = new Map();
  const promotedIntake = new Set();
  const idempotency = new Map();
  const eligibility = new Map();

  let chain = Promise.resolve();
  function serial(fn) {
    const run = chain.then(fn, fn);
    chain = run.then(() => undefined, () => undefined);
    return run;
  }

  function iso(ms) {
    return new Date(ms).toISOString();
  }

  function recordCanonical(rec) {
    const f = PBIdentity.encodeField;
    return (
      'PBR-REC1\n' +
      f('index_id', rec.indexId) + '\n' +
      f('pb_id', rec.pbId) + '\n' +
      f('registration_sequence', String(rec.sequence)) + '\n' +
      f('registered_at', rec.registeredAt) + '\n' +
      f('registration_date_basis', rec.dateBasis) + '\n' +
      f('message_index_ref', rec.messageIndexRef) + '\n' +
      f('active_disposition', rec.activeDisposition) + '\n' +
      f('active_disposition_event_id', rec.activeDispositionEventId) + '\n' +
      f('latest_event_id', rec.latestEventId) + '\n' +
      f('latest_attempt_id', rec.latestAttemptId) + '\n' +
      f('duplicate_count', String(rec.duplicateCount)) + '\n' +
      f('record_revision', String(rec.recordRevision)) + '\n'
    );
  }

  async function computeIntegrity(rec) {
    return 'sha256:' + (await sha256Hex(recordCanonical(rec)));
  }

  function nextEventId() {
    eventSeq += 1;
    return 'EVT-' + pad(eventSeq, 6);
  }

  // Pure projection fold over an explicit event list — the one
  // fold used by rebuildProjection and by import validation.
  function projectFromEvents(evs) {
    const proj = {
      activeDisposition: 'REGISTERED',
      activeDispositionEventId: null,
      latestEventId: null,
      latestAttemptId: null,
      duplicateCount: 0,
      recordRevision: 0,
      deliveryConflict: false,
    };
    const confirmed = new Set();
    const provenNot = new Set();
    for (const ev of evs) {
      proj.latestEventId = ev.eventId;
      proj.recordRevision += 1;
      switch (ev.type) {
        case 'REGISTERED':
          proj.activeDisposition = 'REGISTERED';
          proj.activeDispositionEventId = ev.eventId;
          break;
        case 'PRE_REGISTRATION_REFUSAL_PROMOTED':
          proj.activeDisposition = ev.data && ev.data.refusalType ? ev.data.refusalType : 'REFUSED';
          proj.activeDispositionEventId = ev.eventId;
          break;
        case 'REFUSED':
        case 'REFUTED':
        case 'SKIPPED':
        case 'DISCARDED':
        case 'HELD_FOR_REVIEW':
        case 'CLOSED':
          proj.activeDisposition = ev.type;
          proj.activeDispositionEventId = ev.eventId;
          break;
        case 'SUPERSEDED':
          proj.activeDisposition = 'SUPERSEDED';
          proj.activeDispositionEventId = ev.eventId;
          break;
        case 'ATTEMPT_CREATED':
          proj.latestAttemptId = ev.attemptId;
          break;
        case 'DUPLICATE_OBSERVED':
          proj.duplicateCount += 1;
          break;
        case 'DELIVERY_CONFIRMED':
          if (ev.attemptId) confirmed.add(ev.attemptId);
          break;
        case 'PROVEN_NOT_DELIVERED':
          if (ev.attemptId) provenNot.add(ev.attemptId);
          break;
        default:
          break;
      }
    }
    proj.deliveryConflict = confirmed.size > 0 && provenNot.size > 0;
    return proj;
  }

  // Incremental application of one event to a live record; the
  // delivery-conflict field is recomputed from the record's own
  // history so incremental and full folds agree.
  function applyProjection(rec, ev, evs) {
    const proj = projectFromEvents([...(evs || eventsByIndex.get(rec.indexId) || []), ev]);
    rec.activeDisposition = proj.activeDisposition;
    rec.activeDispositionEventId = proj.activeDispositionEventId;
    rec.latestEventId = proj.latestEventId;
    rec.latestAttemptId = proj.latestAttemptId;
    rec.recordRevision = proj.recordRevision;
    rec.deliveryConflict = proj.deliveryConflict;
    if (duplicateEventPolicy === 'event') {
      rec.duplicateCount = proj.duplicateCount;
    }
  }

  function appendEventInternal(rec, fields, evArray) {
    const ev = {
      eventId: nextEventId(),
      indexId: rec.indexId,
      pbId: rec.pbId,
      type: fields.type,
      occurredAt: fields.occurredAt != null ? iso(fields.occurredAt) : iso(now()),
      recordedAt: iso(now()),
      actor: fields.actor != null ? fields.actor : null,
      authorityRef: fields.authorityRef != null ? fields.authorityRef : null,
      attemptId: fields.attemptId != null ? fields.attemptId : null,
      causationEventId: fields.causationEventId != null ? fields.causationEventId : null,
      supersedesEventId: fields.supersedesEventId != null ? fields.supersedesEventId : null,
      evidenceRef: fields.evidenceRef != null ? fields.evidenceRef : null,
      evidenceClass: fields.evidenceClass != null ? fields.evidenceClass : null,
      data: fields.data != null ? clone(fields.data) : null,
    };
    const arr = evArray || eventsByIndex.get(rec.indexId);
    applyProjection(rec, ev, arr);
    arr.push(ev);
    return ev;
  }

  function deliverySets(indexId) {
    const confirmed = new Set();
    const provenNot = new Set();
    for (const ev of eventsByIndex.get(indexId) || []) {
      if (!ev.attemptId) continue;
      if (ev.type === 'DELIVERY_CONFIRMED') confirmed.add(ev.attemptId);
      if (ev.type === 'PROVEN_NOT_DELIVERED') provenNot.add(ev.attemptId);
    }
    return { confirmed, provenNot };
  }

  function hasConfirmedDelivery(indexId) {
    return deliverySets(indexId).confirmed.size > 0;
  }

  function correlationHold(pbId) {
    for (const entry of intake.values()) {
      if (entry.correlation !== 'UNKNOWN') continue;
      if (entry.candidatePbId === pbId || entry.pbId === pbId) return true;
    }
    return false;
  }

  function admissionReasons(rec) {
    const reasons = [];
    if (hasConfirmedDelivery(rec.indexId)) reasons.push('confirmed-delivered-lifetime-block');
    if (rec.activeDisposition === 'REFUSED' || rec.activeDisposition === 'REFUTED') {
      reasons.push('active-refusal:' + rec.activeDisposition);
    }
    if (correlationHold(rec.pbId)) reasons.push('intake-correlation-unknown');
    return reasons;
  }

  async function checkAuthority(rec, fields) {
    if (!authorityVerifier) return 'authority-mechanism-absent';
    let ok = false;
    try {
      ok = await authorityVerifier({
        type: fields.type,
        actor: fields.actor != null ? fields.actor : null,
        authorityRef: fields.authorityRef != null ? fields.authorityRef : null,
        indexId: rec.indexId,
        pbId: rec.pbId,
        attemptId: fields.attemptId != null ? fields.attemptId : null,
        supersedesEventId: fields.supersedesEventId != null ? fields.supersedesEventId : null,
      });
    } catch (err) {
      return 'authority-not-verified';
    }
    return ok ? null : 'authority-not-verified';
  }

  // Snapshot/rollback discipline for mutations that commit an
  // integrity digest after changing state (SS9): if the digest
  // cannot be computed, restore the snapshot and fault.
  function snapshot(rec) {
    return {
      rec: clone(rec),
      evLen: (eventsByIndex.get(rec.indexId) || []).length,
      eligHad: eligibility.has(rec.indexId),
      elig: clone(eligibility.get(rec.indexId)),
    };
  }

  function rollback(rec, snap, attemptSnap) {
    const evs = eventsByIndex.get(rec.indexId);
    if (evs) evs.length = snap.evLen;
    byIndex.set(rec.indexId, snap.rec);
    byPbid.set(rec.pbId, snap.rec);
    if (snap.eligHad) eligibility.set(rec.indexId, snap.elig);
    else eligibility.delete(rec.indexId);
    if (attemptSnap) {
      if (attemptSnap.existed) attempts.set(attemptSnap.attempt.attemptId, attemptSnap.attempt);
      else attempts.delete(attemptSnap.id);
    }
    faulted = true;
    return snap.rec;
  }

  async function register(input) {
    return serial(async () => {
      if (faulted) return { status: 'INTEGRITY_FAULT' };
      if (!input || typeof input !== 'object') return { status: 'NOT_REGISTERED', reason: 'no-input' };
      if (!isNonEmptyString(input.pbId)) return { status: 'NOT_REGISTERED', reason: 'pb-id-invalid' };
      if (!isNonEmptyString(input.idempotencyKey)) return { status: 'NOT_REGISTERED', reason: 'idempotency-key-invalid' };
      if (!isNonEmptyString(input.messageIndexRef)) return { status: 'NOT_REGISTERED', reason: 'message-index-ref-invalid' };
      if (input.admitted !== true) return { status: 'NOT_REGISTERED', reason: 'not-admitted' };

      const seen = idempotency.get(input.idempotencyKey);
      if (seen) {
        if (seen.pbId !== input.pbId) return { status: 'CONFLICT', reason: 'idempotency-key-carries-different-pb-id' };
        return { status: 'REGISTERED', record: clone(byIndex.get(seen.indexId)), duplicate: true };
      }
      const existing = byPbid.get(input.pbId);
      if (existing) {
        idempotency.set(input.idempotencyKey, { pbId: input.pbId, indexId: existing.indexId });
        return { status: 'REGISTERED', record: clone(existing), duplicate: true };
      }

      // Stage the record and its events locally. Nothing is
      // published — and no sequence is committed — until the
      // integrity digest has been computed (commit boundary).
      const sequence = counter + 1;
      const registeredAt = iso(now());
      const indexId = 'IDX-' + utcDateSegment(now()) + '-' + pad(sequence, 6);
      const rec = {
        indexId,
        pbId: input.pbId,
        sequence,
        registeredAt,
        dateBasis: 'UTC',
        messageIndexRef: input.messageIndexRef,
        activeDisposition: 'REGISTERED',
        activeDispositionEventId: null,
        latestEventId: null,
        latestAttemptId: null,
        duplicateCount: 0,
        recordRevision: 0,
        recordIntegrity: null,
        deliveryConflict: false,
      };
      const stagedEvents = [];
      appendEventInternal(rec, { type: 'REGISTERED', actor: input.actor != null ? input.actor : 'system' }, stagedEvents);

      // R-2 promotion: established EXACT correlation only.
      // UNKNOWN is a hold, never a match (SS4.3, SS7.2A).
      for (const entry of intake.values()) {
        if (entry.correlation === 'EXACT' && entry.pbId === rec.pbId &&
            !promotedIntake.has(entry.intakeId)) {
          appendEventInternal(rec, {
            type: 'PRE_REGISTRATION_REFUSAL_PROMOTED',
            actor: entry.actor,
            authorityRef: entry.authorityRef,
            evidenceRef: entry.evidenceRef,
            occurredAt: entry.occurredAt,
            data: {
              intakeId: entry.intakeId,
              refusalType: entry.type,
              failedCheck: entry.failedCheck,
            },
          }, stagedEvents);
          var promotedId = entry.intakeId;
          break;
        }
      }

      try {
        rec.recordIntegrity = await computeIntegrity(rec);
      } catch (err) {
        faulted = true;
        return { status: 'INTEGRITY_FAULT', reason: 'integrity-calculation-failed' };
      }

      // Commit point: publish record, events, counter advance
      // and the idempotency mapping together.
      byIndex.set(indexId, rec);
      byPbid.set(rec.pbId, rec);
      eventsByIndex.set(indexId, stagedEvents);
      if (typeof promotedId === 'string') promotedIntake.add(promotedId);
      counter = sequence;
      idempotency.set(input.idempotencyKey, { pbId: rec.pbId, indexId });

      // Read-back verification before success is reported (SS3.3).
      let verified = false;
      try {
        const readBack = byIndex.get(indexId);
        verified = readBack === rec &&
          readBack.pbId === rec.pbId &&
          (await computeIntegrity(readBack)) === rec.recordIntegrity;
      } catch (err) {
        verified = false;
      }
      if (!verified || failReadBackArmed) {
        failReadBackArmed = false;
        return { status: 'REGISTRATION_UNKNOWN', reason: 'read-back-unverified' };
      }
      return { status: 'REGISTERED', record: clone(rec) };
    });
  }

  async function resolveByIdempotency(key) {
    const seen = idempotency.get(key);
    if (!seen) return { status: 'NOT_REGISTERED' };
    return { status: 'REGISTERED', record: clone(byIndex.get(seen.indexId)) };
  }

  async function appendEvent(indexId, fields) {
    return serial(async () => {
      if (faulted) return { status: 'INTEGRITY_FAULT' };
      const rec = byIndex.get(indexId);
      if (!rec) return { status: 'REJECTED', reason: 'unknown-index' };
      if (!fields || !CORE_EVENT_TYPES.has(fields.type)) {
        return { status: 'REJECTED', reason: 'unknown-event-type' };
      }
      if (SYSTEM_ONLY_TYPES.has(fields.type)) {
        return { status: 'REJECTED', reason: 'system-only-event' };
      }
      if (AUTHORITY_TYPES.has(fields.type)) {
        const authFailure = await checkAuthority(rec, fields);
        if (authFailure) return { status: 'REJECTED', reason: authFailure };
      }
      const evs = eventsByIndex.get(indexId);

      if (fields.type === 'SUPERSEDED') {
        const target = evs.find((e) => e.eventId === fields.supersedesEventId);
        const targetIsActiveRefusal = target && rec.activeDispositionEventId === target.eventId &&
          (target.type === 'REFUSED' || target.type === 'REFUTED' ||
           target.type === 'PRE_REGISTRATION_REFUSAL_PROMOTED');
        if (!targetIsActiveRefusal) {
          return { status: 'REJECTED', reason: 'supersession-target-not-active-refusal' };
        }
      }
      if (fields.type === 'RE_PRESENTATION_DIRECTED') {
        if (rec.activeDisposition !== 'SUPERSEDED') {
          return { status: 'REJECTED', reason: 'no-open-eligibility' };
        }
        if (fields.causationEventId !== rec.activeDispositionEventId) {
          return { status: 'REJECTED', reason: 'direction-not-linked-to-active-supersession' };
        }
      }
      let attempt = null;
      if (fields.attemptId != null) {
        attempt = attempts.get(fields.attemptId);
        if (!attempt || attempt.indexId !== indexId) {
          return { status: 'REJECTED', reason: 'unknown-attempt' };
        }
      }
      if (fields.type === 'DISPATCHED') {
        if (!attempt) return { status: 'REJECTED', reason: 'attempt-required' };
        if (attempt.status !== 'created' && attempt.status !== 'validated') {
          return { status: 'REJECTED', reason: 'attempt-not-dispatchable' };
        }
      }
      if (fields.type === 'FORCE_SENT') {
        if (!attempt) return { status: 'REJECTED', reason: 'attempt-required' };
        if (attempt.status !== 'created' && attempt.status !== 'validated') {
          return { status: 'REJECTED', reason: 'attempt-not-forceable' };
        }
      }
      if (fields.type === 'DELIVERY_CONFIRMED' || fields.type === 'PROVEN_NOT_DELIVERED' ||
          fields.type === 'DELIVERY_UNKNOWN') {
        if (!attempt) return { status: 'REJECTED', reason: 'attempt-required' };
        if (attempt.status !== 'dispatched') {
          return { status: 'REJECTED', reason: 'attempt-not-dispatched' };
        }
      }
      if (fields.type === 'ATTEMPT_VALIDATED' || fields.type === 'ATTEMPT_REJECTED') {
        if (!attempt) return { status: 'REJECTED', reason: 'attempt-required' };
      }

      const snap = snapshot(rec);
      const attemptSnap = attempt
        ? { id: attempt.attemptId, existed: true, attempt: clone(attempt) } : null;
      const ev = appendEventInternal(rec, fields);
      if (fields.type === 'SUPERSEDED') {
        eligibility.set(indexId, { supersessionEventId: ev.eventId, consumedByAttemptId: null });
      }
      if (fields.type === 'REFUSED' || fields.type === 'REFUTED') {
        eligibility.delete(indexId);
      }
      if (attempt) {
        if (fields.type === 'DISPATCHED' || fields.type === 'FORCE_SENT') {
          attempt.status = 'dispatched';
          if (fields.type === 'FORCE_SENT') attempt.forceSent = true;
        }
        if (fields.type === 'ATTEMPT_VALIDATED') attempt.status = 'validated';
        if (fields.type === 'ATTEMPT_REJECTED') attempt.status = 'rejected';
        if (fields.type === 'DELIVERY_CONFIRMED') attempt.deliveryKnowledge = 'CONFIRMED';
        if (fields.type === 'PROVEN_NOT_DELIVERED') attempt.deliveryKnowledge = 'PROVEN_NOT_DELIVERED';
        if (fields.type === 'DELIVERY_UNKNOWN') attempt.deliveryKnowledge = 'UNKNOWN';
      }
      try {
        rec.recordIntegrity = await computeIntegrity(rec);
      } catch (err) {
        rollback(rec, snap, attemptSnap);
        return { status: 'INTEGRITY_FAULT', reason: 'integrity-calculation-failed' };
      }
      return { status: 'APPLIED', event: clone(ev) };
    });
  }

  async function createAttempt(indexId, opts) {
    return serial(async () => {
      if (faulted) return { status: 'INTEGRITY_FAULT' };
      const rec = byIndex.get(indexId);
      if (!rec) return { status: 'HELD', reasons: ['unknown-index'] };
      const options = opts || {};
      let via;
      if (options.via === 're-presentation') {
        const elig = eligibility.get(indexId);
        if (rec.activeDisposition !== 'SUPERSEDED' || !elig ||
            elig.supersessionEventId !== options.supersedesEventId) {
          return { status: 'HELD', reasons: ['no-open-eligibility'] };
        }
        if (elig.consumedByAttemptId) {
          return { status: 'HELD', reasons: ['eligibility-already-consumed'] };
        }
        const dir = eventsByIndex.get(indexId).find((e) => e.eventId === options.directionEventId);
        if (!dir || dir.type !== 'RE_PRESENTATION_DIRECTED' ||
            dir.causationEventId !== elig.supersessionEventId) {
          return { status: 'HELD', reasons: ['direction-missing-or-unlinked'] };
        }
        if (hasConfirmedDelivery(indexId)) {
          return { status: 'HELD', reasons: ['confirmed-delivered-lifetime-block'] };
        }
        if (correlationHold(rec.pbId)) {
          return { status: 'HELD', reasons: ['intake-correlation-unknown'] };
        }
        via = 're-presentation';
      } else {
        const reasons = admissionReasons(rec);
        if (DISPOSITION_TYPES.has(rec.activeDisposition)) {
          reasons.push('disposition:' + rec.activeDisposition);
        }
        if (rec.activeDisposition === 'SUPERSEDED') {
          reasons.push('superseded-requires-re-presentation');
        }
        if (reasons.length > 0) return { status: 'HELD', reasons };
        via = 'initial';
      }

      const snap = snapshot(rec);
      attemptSeq += 1;
      const attemptId = 'ATT-' + pad(attemptSeq, 6);
      attempts.set(attemptId, {
        attemptId, indexId, pbId: rec.pbId, status: 'created',
        via, deliveryKnowledge: 'UNKNOWN', forceSent: false,
      });
      if (via === 're-presentation') {
        eligibility.get(indexId).consumedByAttemptId = attemptId;
      }
      appendEventInternal(rec, {
        type: 'ATTEMPT_CREATED', actor: options.actor != null ? options.actor : 'system',
        attemptId,
        causationEventId: via === 're-presentation' ? options.directionEventId : null,
      });
      try {
        rec.recordIntegrity = await computeIntegrity(rec);
      } catch (err) {
        rollback(rec, snap, { id: attemptId, existed: false, attempt: null });
        return { status: 'INTEGRITY_FAULT', reason: 'integrity-calculation-failed' };
      }
      return { status: 'CREATED', attemptId };
    });
  }

  async function observeDuplicate(pbId) {
    return serial(async () => {
      if (faulted) return { status: 'INTEGRITY_FAULT' };
      const rec = byPbid.get(pbId);
      if (!rec) return { status: 'NOT_REGISTERED' };
      const snap = snapshot(rec);
      if (duplicateEventPolicy === 'event') {
        appendEventInternal(rec, { type: 'DUPLICATE_OBSERVED', actor: 'detector' });
      } else {
        rec.duplicateCount += 1;
        rec.recordRevision += 1;
      }
      try {
        rec.recordIntegrity = await computeIntegrity(rec);
      } catch (err) {
        rollback(rec, snap, null);
        return { status: 'INTEGRITY_FAULT', reason: 'integrity-calculation-failed' };
      }
      return { status: 'OK', duplicateCount: rec.duplicateCount };
    });
  }

  // Intake recording is inside the same serialisation chain as
  // registration (rev2): the R-2 relationship cannot race. An
  // intake refusal recorded after its PB-ID has registered is
  // marked 'already-registered' on the entry itself, so the
  // caller routes it as a lifecycle REFUSED event instead of
  // expecting a promotion that can no longer occur.
  async function recordIntakeRefusal(input) {
    return serial(async () => {
      if (faulted) return { status: 'INTEGRITY_FAULT' };
      const pb = isNonEmptyString(input && input.pbId) ? input.pbId : null;
      const entry = {
        intakeId: 'INT-' + pad((intakeSeq += 1), 6),
        pbId: pb,
        candidatePbId: isNonEmptyString(input && input.candidatePbId) ? input.candidatePbId : null,
        // Fail-closed (SS4.3, SS7.2A): only an explicitly valid
        // EXACT value is exact. Missing or unrecognised values
        // stay UNKNOWN — uncertainty is never upgraded.
        correlation: input && input.correlation === 'EXACT' ? 'EXACT' : 'UNKNOWN',
        type: input && input.type === 'REFUTED' ? 'REFUTED' : 'REFUSED',
        actor: input && input.actor != null ? input.actor : null,
        authorityRef: input && input.authorityRef != null ? input.authorityRef : null,
        failedCheck: input && input.failedCheck != null ? input.failedCheck : null,
        evidenceRef: input && input.evidenceRef != null ? input.evidenceRef : null,
        occurredAt: input && typeof input.occurredAt === 'number' ? input.occurredAt : now(),
        registrationState: pb && byPbid.has(pb) ? 'already-registered' : 'pre-registration',
      };
      intake.set(entry.intakeId, entry);
      return clone(entry);
    });
  }

  function intakeRefusal(intakeId) {
    return clone(intake.get(intakeId));
  }

  async function sendAdmission(pbId) {
    const rec = byPbid.get(pbId);
    if (!rec) return { allowed: false, reasons: ['not-registered'] };
    const reasons = admissionReasons(rec);
    if (DISPOSITION_TYPES.has(rec.activeDisposition)) {
      reasons.push('disposition:' + rec.activeDisposition);
    }
    return { allowed: reasons.length === 0, reasons };
  }

  function currentState(indexId) {
    const rec = byIndex.get(indexId);
    return rec ? clone(rec) : undefined;
  }

  function rebuildProjection(indexId) {
    const stored = byIndex.get(indexId);
    if (!stored) return undefined;
    const proj = projectFromEvents(eventsByIndex.get(indexId) || []);
    return {
      indexId: stored.indexId,
      pbId: stored.pbId,
      sequence: stored.sequence,
      registeredAt: stored.registeredAt,
      dateBasis: stored.dateBasis,
      messageIndexRef: stored.messageIndexRef,
      activeDisposition: proj.activeDisposition,
      activeDispositionEventId: proj.activeDispositionEventId,
      latestEventId: proj.latestEventId,
      latestAttemptId: proj.latestAttemptId,
      duplicateCount: duplicateEventPolicy === 'event' ? proj.duplicateCount : stored.duplicateCount,
      recordRevision: proj.recordRevision,
      recordIntegrity: stored.recordIntegrity,
      deliveryConflict: proj.deliveryConflict,
    };
  }

  async function verifyIntegrity(indexId) {
    const rec = byIndex.get(indexId);
    if (!rec) return false;
    try {
      return (await computeIntegrity(rec)) === rec.recordIntegrity;
    } catch (err) {
      return false;
    }
  }

  function events(indexId) {
    return clone(eventsByIndex.get(indexId) || []);
  }

  function listByRegistrationOrder() {
    return [...byIndex.values()]
      .sort((a, b) => a.sequence - b.sequence)
      .map((r) => clone(r));
  }

  function messageLookup(pbId) {
    const rec = byPbid.get(pbId);
    if (!rec) return { status: 'NOT_FOUND' };
    return { status: 'FOUND', indexId: rec.indexId, pbId: rec.pbId, messageIndexRef: rec.messageIndexRef };
  }

  function lookupByIndex(indexId) {
    const rec = byIndex.get(indexId);
    if (!rec) return { status: 'NOT_FOUND' };
    return { status: 'FOUND', indexId: rec.indexId, pbId: rec.pbId, messageIndexRef: rec.messageIndexRef };
  }

  function informationLookup() {
    return { status: 'NOT_MESSAGE_KNOWLEDGE' };
  }

  function deliveryKnowledge(indexId, attemptId) {
    const att = attempts.get(attemptId);
    if (!att || att.indexId !== indexId) return 'UNKNOWN';
    return att.deliveryKnowledge;
  }

  function exportState() {
    return clone({
      counter, eventSeq, attemptSeq, intakeSeq,
      records: [...byIndex.values()],
      eventsByIndex: Object.fromEntries(eventsByIndex),
      attempts: [...attempts.values()],
      intake: [...intake.values()],
      promotedIntake: [...promotedIntake],
      idempotency: [...idempotency.entries()],
      eligibility: [...eligibility.entries()],
    });
  }

  // The complete import integrity boundary (rev2, Contract
  // SS9): a state becomes operational only when every check
  // passes. Any failure faults the ledger; nothing is imported
  // partially.
  async function importState(state) {
    const fail = (reason) => {
      faulted = true;
      return { status: 'INTEGRITY_FAULT', reason };
    };
    if (!state || typeof state !== 'object' || !Array.isArray(state.records)) {
      return fail('state-malformed');
    }
    const records = state.records;
    const evMap = state.eventsByIndex || {};
    const seenIndex = new Set();
    const seenPb = new Set();
    const seenSeq = new Set();
    let maxSeq = 0;
    for (const rec of records) {
      if (!rec || !isNonEmptyString(rec.indexId) || !isNonEmptyString(rec.pbId)) {
        return fail('record-identity-malformed');
      }
      if (seenIndex.has(rec.indexId)) return fail('duplicate-index-id');
      if (seenPb.has(rec.pbId)) return fail('duplicate-pb-id');
      if (!Number.isInteger(rec.sequence) || rec.sequence < 1) return fail('sequence-malformed');
      if (seenSeq.has(rec.sequence)) return fail('duplicate-sequence');
      const tail = rec.indexId.slice(rec.indexId.lastIndexOf('-') + 1);
      if (Number(tail) !== rec.sequence) return fail('index-id-sequence-mismatch');
      seenIndex.add(rec.indexId);
      seenPb.add(rec.pbId);
      seenSeq.add(rec.sequence);
      if (rec.sequence > maxSeq) maxSeq = rec.sequence;
    }
    if (!Number.isInteger(state.counter) || state.counter < maxSeq) {
      return fail('counter-rollback');
    }
    const byIdx = new Map(records.map((r) => [r.indexId, r]));

    // Record digests.
    for (const rec of records) {
      let digest;
      try {
        digest = await computeIntegrity(rec);
      } catch (err) {
        return fail('record-integrity-uncomputable');
      }
      if (digest !== rec.recordIntegrity) return fail('record-integrity-mismatch');
    }

    // Event histories: linkage, uniqueness, closed types,
    // per-record start, and fold-verified projections.
    const seenEvents = new Set();
    let maxEventSuffix = 0;
    for (const key of Object.keys(evMap)) {
      if (!byIdx.has(key)) return fail('event-history-for-unknown-index');
    }
    for (const rec of records) {
      const evs = evMap[rec.indexId];
      if (!Array.isArray(evs) || evs.length === 0 || evs[0].type !== 'REGISTERED') {
        return fail('event-history-malformed');
      }
      for (const ev of evs) {
        if (!ev || ev.indexId !== rec.indexId || ev.pbId !== rec.pbId) {
          return fail('event-linkage-broken');
        }
        if (!CORE_EVENT_TYPES.has(ev.type)) return fail('event-type-unknown');
        if (seenEvents.has(ev.eventId)) return fail('duplicate-event-id');
        seenEvents.add(ev.eventId);
        const suf = numericSuffix(ev.eventId, 'EVT-');
        if (suf === null) return fail('event-id-malformed');
        if (suf > maxEventSuffix) maxEventSuffix = suf;
      }
      const proj = projectFromEvents(evs);
      if (proj.activeDisposition !== rec.activeDisposition ||
          proj.activeDispositionEventId !== rec.activeDispositionEventId ||
          proj.latestEventId !== rec.latestEventId ||
          proj.latestAttemptId !== rec.latestAttemptId ||
          proj.deliveryConflict !== rec.deliveryConflict) {
        return fail('projection-unverifiable');
      }
      if (duplicateEventPolicy === 'event') {
        if (proj.duplicateCount !== rec.duplicateCount) return fail('projection-unverifiable');
        if (proj.recordRevision !== rec.recordRevision) return fail('projection-unverifiable');
      } else {
        if (rec.duplicateCount < proj.duplicateCount) return fail('projection-unverifiable');
        if (rec.recordRevision < proj.recordRevision) return fail('projection-unverifiable');
      }
    }
    if (!Number.isInteger(state.eventSeq) || state.eventSeq < maxEventSuffix) {
      return fail('event-counter-rollback');
    }

    // Attempts: unique, linked, and every attempt created by
    // exactly one ATTEMPT_CREATED event (and vice versa).
    const attList = state.attempts || [];
    const seenAtt = new Set();
    let maxAttSuffix = 0;
    for (const att of attList) {
      if (!att || seenAtt.has(att.attemptId)) return fail('duplicate-attempt-id');
      seenAtt.add(att.attemptId);
      const owner = byIdx.get(att.indexId);
      if (!owner || owner.pbId !== att.pbId) return fail('attempt-linkage-broken');
      const suf = numericSuffix(att.attemptId, 'ATT-');
      if (suf === null) return fail('attempt-id-malformed');
      if (suf > maxAttSuffix) maxAttSuffix = suf;
    }
    const createdIds = new Set();
    for (const rec of records) {
      for (const ev of evMap[rec.indexId]) {
        if (ev.type === 'ATTEMPT_CREATED') {
          if (!seenAtt.has(ev.attemptId)) return fail('attempt-linkage-broken');
          if (createdIds.has(ev.attemptId)) return fail('duplicate-attempt-creation');
          createdIds.add(ev.attemptId);
        }
      }
    }
    if (createdIds.size !== seenAtt.size) return fail('attempt-linkage-broken');
    if (!Number.isInteger(state.attemptSeq) || state.attemptSeq < maxAttSuffix) {
      return fail('attempt-counter-rollback');
    }

    // Idempotency mappings must agree with registered records.
    const seenKeys = new Set();
    for (const pair of state.idempotency || []) {
      if (!Array.isArray(pair) || pair.length !== 2) return fail('idempotency-malformed');
      const [key, val] = pair;
      if (seenKeys.has(key)) return fail('duplicate-idempotency-key');
      seenKeys.add(key);
      const rec = byIdx.get(val.indexId);
      if (!rec || rec.pbId !== val.pbId) return fail('idempotency-inconsistent');
    }

    // Intake and promotion references.
    const intakeList = state.intake || [];
    const seenIntake = new Set();
    let maxIntakeSuffix = 0;
    for (const entry of intakeList) {
      if (!entry || seenIntake.has(entry.intakeId)) return fail('duplicate-intake-id');
      seenIntake.add(entry.intakeId);
      const suf = numericSuffix(entry.intakeId, 'INT-');
      if (suf === null) return fail('intake-id-malformed');
      if (suf > maxIntakeSuffix) maxIntakeSuffix = suf;
    }
    if (!Number.isInteger(state.intakeSeq) || state.intakeSeq < maxIntakeSuffix) {
      return fail('intake-counter-rollback');
    }
    for (const id of state.promotedIntake || []) {
      if (!seenIntake.has(id)) return fail('promotion-reference-broken');
    }

    // Eligibility references.
    for (const pair of state.eligibility || []) {
      if (!Array.isArray(pair) || pair.length !== 2) return fail('eligibility-malformed');
      const [indexId, elig] = pair;
      const rec = byIdx.get(indexId);
      if (!rec) return fail('eligibility-reference-broken');
      const sup = (evMap[indexId] || []).find((e) => e.eventId === elig.supersessionEventId);
      if (!sup || sup.type !== 'SUPERSEDED') return fail('eligibility-reference-broken');
      if (elig.consumedByAttemptId != null && !seenAtt.has(elig.consumedByAttemptId)) {
        return fail('eligibility-reference-broken');
      }
    }

    // All checks passed: swap the state in whole.
    counter = state.counter;
    eventSeq = state.eventSeq;
    attemptSeq = state.attemptSeq;
    intakeSeq = state.intakeSeq;
    byIndex.clear(); byPbid.clear(); eventsByIndex.clear();
    attempts.clear(); intake.clear(); promotedIntake.clear();
    idempotency.clear(); eligibility.clear();
    for (const rec of records) {
      byIndex.set(rec.indexId, rec);
      byPbid.set(rec.pbId, rec);
    }
    for (const [k, v] of Object.entries(evMap)) eventsByIndex.set(k, v);
    for (const att of attList) attempts.set(att.attemptId, att);
    for (const entry of intakeList) intake.set(entry.intakeId, entry);
    for (const id of state.promotedIntake || []) promotedIntake.add(id);
    for (const [k, v] of state.idempotency || []) idempotency.set(k, v);
    for (const [k, v] of state.eligibility || []) eligibility.set(k, v);
    faulted = false;
    return { status: 'OK' };
  }

  function __tamperForTest(indexId, fn) {
    const rec = byIndex.get(indexId);
    if (rec) fn(rec);
  }

  return {
    register,
    resolveByIdempotency,
    appendEvent,
    createAttempt,
    observeDuplicate,
    recordIntakeRefusal,
    intakeRefusal,
    sendAdmission,
    currentState,
    rebuildProjection,
    verifyIntegrity,
    events,
    listByRegistrationOrder,
    messageLookup,
    lookupByIndex,
    informationLookup,
    deliveryKnowledge,
    exportState,
    importState,
    __tamperForTest,
  };
}

const PBLedger = { createLedger, CORE_EVENT_TYPES };

if (typeof module !== 'undefined' && module.exports) {
  module.exports = PBLedger;
}
if (typeof globalThis !== 'undefined') {
  globalThis.PBLedger = PBLedger;
}
