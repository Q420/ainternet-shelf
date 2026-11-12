'use strict';
/*
 * Pulse Bridge — registration ledger core (Stage 1, scope items
 * 2-6). Implements Bridge Registration Contract Rev 02 (FINAL,
 * blob b9cffdbd551b808af3e6e37d7af5b77747ab99e8):
 *
 * - One-to-one, permanent Index ID <-> PB-ID registration (SS2).
 * - Index ID: IDX-YYYYMMDD-NNNNNN; UTC date segment is metadata;
 *   the numeric sequence is the sole ordering authority and is
 *   allocated from one never-resetting counter (SS3, R-3).
 * - Idempotent registration; ambiguous outcomes resolve by
 *   idempotency identity, never by allocating again (SS3.3-3.4).
 * - Registration boundary: detection is not registration; only
 *   an admitted candidate with a stable PB-ID registers (SS4).
 * - Thin routing record (SS5): no message body, ever.
 * - Append-only lifecycle events from the closed core set (SS6);
 *   the current-state projection is a deterministic fold of the
 *   events (SS9).
 * - Intake refusals and R-2 promotion (SS4.3, SS7.2A);
 *   supersession and the one-shot B re-presentation boundary
 *   (SS7.3-7.4); dispatch vs delivery fact/knowledge (SS7.5-7.6);
 *   duplicate counting and the lifetime confirmed-delivered
 *   send block as a predicate separate from refusal (SS8).
 * - Message Index route and Information Index route are kept
 *   apart: the information route never returns message records.
 *
 * Deliberately NOT decided here (Contract SS13 open items,
 * surfaced rather than silently settled):
 * - SS13.5 event-volume policy: `duplicateEventPolicy` is a
 *   REQUIRED constructor argument ('event' | 'counter-only');
 *   there is no default.
 * - SS13.8 record-integrity canonicalisation: this module uses
 *   a proposed form ('PBR-REC1', length-prefixed fields in SS5
 *   order, SHA-256) pending adoption; verifyIntegrity detects
 *   tampering under that form.
 * - Admission checks (SS13.2): the caller asserts `admitted`;
 *   the ledger enforces the boundary mechanics, not the checks.
 *
 * Persistence/concurrency substrate is the in-memory authority
 * behind a serialised mutation chain; export/import carries the
 * full state for restart and integrity checking. All injected
 * dependencies (clock, SHA-256) keep fixtures deterministic.
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

  let counter = Number.isInteger(config.initialSequence) ? config.initialSequence : 0;
  let eventSeq = 0;
  let attemptSeq = 0;
  let intakeSeq = 0;
  let faulted = false;
  let failReadBackArmed = !!config.failReadBackOnce;

  const byIndex = new Map();   // indexId -> record
  const byPbid = new Map();    // pbId -> record
  const eventsByIndex = new Map(); // indexId -> [event]
  const attempts = new Map();  // attemptId -> attempt
  const intake = new Map();    // intakeId -> intake record (never mutated after creation)
  const promotedIntake = new Set(); // intakeIds already promoted
  const idempotency = new Map(); // key -> { pbId, indexId }
  const eligibility = new Map(); // indexId -> { supersessionEventId, consumedByAttemptId }

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

  function appendEventInternal(rec, fields) {
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
    eventsByIndex.get(rec.indexId).push(ev);
    applyProjection(rec, ev);
    return ev;
  }

  // The projection fold: one function used both incrementally
  // (per committed event) and by rebuildProjection (full replay),
  // which is what makes the rebuild deterministic by construction.
  function applyProjection(rec, ev) {
    rec.latestEventId = ev.eventId;
    rec.recordRevision += 1;
    switch (ev.type) {
      case 'REGISTERED':
        rec.activeDisposition = 'REGISTERED';
        rec.activeDispositionEventId = ev.eventId;
        break;
      case 'PRE_REGISTRATION_REFUSAL_PROMOTED':
        rec.activeDisposition = ev.data && ev.data.refusalType ? ev.data.refusalType : 'REFUSED';
        rec.activeDispositionEventId = ev.eventId;
        break;
      case 'REFUSED':
      case 'REFUTED':
      case 'SKIPPED':
      case 'DISCARDED':
      case 'HELD_FOR_REVIEW':
      case 'CLOSED':
        rec.activeDisposition = ev.type;
        rec.activeDispositionEventId = ev.eventId;
        break;
      case 'SUPERSEDED':
        rec.activeDisposition = 'SUPERSEDED';
        rec.activeDispositionEventId = ev.eventId;
        break;
      case 'ATTEMPT_CREATED':
        rec.latestAttemptId = ev.attemptId;
        break;
      case 'DUPLICATE_OBSERVED':
        rec.duplicateCount += 1;
        break;
      case 'DELIVERY_CONFIRMED':
      case 'PROVEN_NOT_DELIVERED':
        rec.deliveryConflict = deliveryConflictFor(rec.indexId);
        break;
      default:
        break;
    }
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

  function deliveryConflictFor(indexId) {
    const { confirmed, provenNot } = deliverySets(indexId);
    return confirmed.size > 0 && provenNot.size > 0;
  }

  function hasConfirmedDelivery(indexId) {
    return deliverySets(indexId).confirmed.size > 0;
  }

  function correlationHold(pbId) {
    for (const entry of intake.values()) {
      if (entry.correlation === 'UNKNOWN' && entry.candidatePbId === pbId) return true;
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
      byIndex.set(indexId, rec);
      byPbid.set(rec.pbId, rec);
      eventsByIndex.set(indexId, []);
      appendEventInternal(rec, { type: 'REGISTERED', actor: input.actor != null ? input.actor : 'system' });

      // R-2 promotion: an exact-PB-ID intake refusal becomes the
      // first disposition-bearing event; the intake record itself
      // is never modified.
      for (const entry of intake.values()) {
        if (entry.pbId === rec.pbId && !promotedIntake.has(entry.intakeId)) {
          promotedIntake.add(entry.intakeId);
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
          });
          break;
        }
      }

      rec.recordIntegrity = await computeIntegrity(rec);
      counter = sequence;
      idempotency.set(input.idempotencyKey, { pbId: rec.pbId, indexId });

      // Read-back verification before success is reported (SS3.3).
      const readBack = byIndex.get(indexId);
      const verified = readBack === rec &&
        readBack.pbId === rec.pbId &&
        (await computeIntegrity(readBack)) === rec.recordIntegrity;
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
      const rec = byIndex.get(indexId);
      if (!rec) return { status: 'REJECTED', reason: 'unknown-index' };
      if (!fields || !CORE_EVENT_TYPES.has(fields.type)) {
        return { status: 'REJECTED', reason: 'unknown-event-type' };
      }
      if (SYSTEM_ONLY_TYPES.has(fields.type)) {
        return { status: 'REJECTED', reason: 'system-only-event' };
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
      rec.recordIntegrity = await computeIntegrity(rec);
      return { status: 'APPLIED', event: clone(ev) };
    });
  }

  async function createAttempt(indexId, opts) {
    return serial(async () => {
      const rec = byIndex.get(indexId);
      if (!rec) return { status: 'HELD', reasons: ['unknown-index'] };
      const options = opts || {};
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
        attemptSeq += 1;
        const attemptId = 'ATT-' + pad(attemptSeq, 6);
        attempts.set(attemptId, {
          attemptId, indexId, pbId: rec.pbId, status: 'created',
          via: 're-presentation', deliveryKnowledge: 'UNKNOWN', forceSent: false,
        });
        elig.consumedByAttemptId = attemptId;
        const ev = appendEventInternal(rec, {
          type: 'ATTEMPT_CREATED', actor: options.actor != null ? options.actor : 'system',
          attemptId, causationEventId: dir.eventId,
        });
        rec.recordIntegrity = await computeIntegrity(rec);
        void ev;
        return { status: 'CREATED', attemptId };
      }
      // Initial processing attempt.
      const reasons = admissionReasons(rec);
      if (DISPOSITION_TYPES.has(rec.activeDisposition)) {
        reasons.push('disposition:' + rec.activeDisposition);
      }
      if (rec.activeDisposition === 'SUPERSEDED') {
        reasons.push('superseded-requires-re-presentation');
      }
      if (reasons.length > 0) return { status: 'HELD', reasons };
      attemptSeq += 1;
      const attemptId = 'ATT-' + pad(attemptSeq, 6);
      attempts.set(attemptId, {
        attemptId, indexId, pbId: rec.pbId, status: 'created',
        via: 'initial', deliveryKnowledge: 'UNKNOWN', forceSent: false,
      });
      appendEventInternal(rec, {
        type: 'ATTEMPT_CREATED', actor: options.actor != null ? options.actor : 'system', attemptId,
      });
      rec.recordIntegrity = await computeIntegrity(rec);
      return { status: 'CREATED', attemptId };
    });
  }

  async function observeDuplicate(pbId) {
    return serial(async () => {
      const rec = byPbid.get(pbId);
      if (!rec) return { status: 'NOT_REGISTERED' };
      if (duplicateEventPolicy === 'event') {
        appendEventInternal(rec, { type: 'DUPLICATE_OBSERVED', actor: 'detector' });
      } else {
        rec.duplicateCount += 1;
        rec.recordRevision += 1;
      }
      rec.recordIntegrity = await computeIntegrity(rec);
      return { status: 'OK', duplicateCount: rec.duplicateCount };
    });
  }

  async function recordIntakeRefusal(input) {
    const entry = {
      intakeId: 'INT-' + pad((intakeSeq += 1), 6),
      pbId: isNonEmptyString(input && input.pbId) ? input.pbId : null,
      candidatePbId: isNonEmptyString(input && input.candidatePbId) ? input.candidatePbId : null,
      correlation: input && input.correlation === 'UNKNOWN' ? 'UNKNOWN' : 'EXACT',
      type: input && input.type === 'REFUTED' ? 'REFUTED' : 'REFUSED',
      actor: input && input.actor != null ? input.actor : null,
      authorityRef: input && input.authorityRef != null ? input.authorityRef : null,
      failedCheck: input && input.failedCheck != null ? input.failedCheck : null,
      evidenceRef: input && input.evidenceRef != null ? input.evidenceRef : null,
      occurredAt: input && typeof input.occurredAt === 'number' ? input.occurredAt : now(),
    };
    intake.set(entry.intakeId, entry);
    return clone(entry);
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
    const fresh = {
      indexId: stored.indexId,
      pbId: stored.pbId,
      sequence: stored.sequence,
      registeredAt: stored.registeredAt,
      dateBasis: stored.dateBasis,
      messageIndexRef: stored.messageIndexRef,
      activeDisposition: 'REGISTERED',
      activeDispositionEventId: null,
      latestEventId: null,
      latestAttemptId: null,
      duplicateCount: duplicateEventPolicy === 'event' ? 0 : stored.duplicateCount,
      recordRevision: 0,
      recordIntegrity: stored.recordIntegrity,
      deliveryConflict: false,
    };
    // Replay against a scratch event view so the fold's delivery
    // computation reads the same history.
    for (const ev of eventsByIndex.get(indexId)) {
      applyProjection(fresh, ev);
    }
    fresh.deliveryConflict = deliveryConflictFor(indexId);
    return fresh;
  }

  async function verifyIntegrity(indexId) {
    const rec = byIndex.get(indexId);
    if (!rec) return false;
    return (await computeIntegrity(rec)) === rec.recordIntegrity;
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
    // The Information Index never returns message records
    // (Contract SS7.2, SS8.6, SS10). Admission of information is
    // a separate governance path, not a ledger lookup.
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

  function importState(state) {
    const fail = (reason) => {
      faulted = true;
      return { status: 'INTEGRITY_FAULT', reason };
    };
    if (!state || typeof state !== 'object' || !Array.isArray(state.records)) {
      return fail('state-malformed');
    }
    const seqs = new Set();
    const pbids = new Set();
    let maxSeq = 0;
    for (const rec of state.records) {
      if (seqs.has(rec.sequence)) return fail('duplicate-sequence');
      if (pbids.has(rec.pbId)) return fail('duplicate-pb-id');
      seqs.add(rec.sequence);
      pbids.add(rec.pbId);
      if (rec.sequence > maxSeq) maxSeq = rec.sequence;
    }
    if (!Number.isInteger(state.counter) || state.counter < maxSeq) {
      return fail('counter-rollback');
    }
    counter = state.counter;
    eventSeq = state.eventSeq || 0;
    attemptSeq = state.attemptSeq || 0;
    intakeSeq = state.intakeSeq || 0;
    byIndex.clear(); byPbid.clear(); eventsByIndex.clear();
    attempts.clear(); intake.clear(); promotedIntake.clear();
    idempotency.clear(); eligibility.clear();
    for (const rec of state.records) {
      byIndex.set(rec.indexId, rec);
      byPbid.set(rec.pbId, rec);
    }
    for (const [k, v] of Object.entries(state.eventsByIndex || {})) {
      eventsByIndex.set(k, v);
    }
    for (const att of state.attempts || []) attempts.set(att.attemptId, att);
    for (const entry of state.intake || []) intake.set(entry.intakeId, entry);
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
