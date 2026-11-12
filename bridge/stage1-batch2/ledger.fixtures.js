'use strict';
/*
 * Stage 1 — Batch 2 fixtures: registration ledger.
 *
 * Governing text: Bridge Registration Contract Rev 02 (FINAL),
 * commit 61d5693bffb214fd86ffecc6aba0ba8679003559, blob
 * b9cffdbd551b808af3e6e37d7af5b77747ab99e8; Build Plan 01
 * Stage 1 scope items 2-6 and the Stage 1 acceptance fixture
 * classes (duplicate registration; atomic sequence races/gaps;
 * write-success/read-back-loss; retry with same idempotency
 * identity; R-2 promotion/correlation UNKNOWN; refusal
 * supersession; confirmed-delivered lifetime block; migration
 * is batch 3).
 *
 * Run: node tests-stage1/ledger.fixtures.js
 */
const assert = require('node:assert');
const crypto = require('node:crypto');
const path = require('node:path');

const ledgerMod = require(path.join(__dirname, '..', 'ledger.js'));

const sha256Hex = (text) =>
  crypto.createHash('sha256').update(text, 'utf8').digest('hex');

const T0 = Date.UTC(2026, 10, 11, 12, 0, 0); // 2026-11-11T12:00:00Z

function makeLedger(opts = {}) {
  const clock = { t: T0 };
  const ledger = ledgerMod.createLedger({
    now: () => clock.t,
    sha256Hex,
    duplicateEventPolicy: opts.duplicateEventPolicy || 'event',
    initialSequence: opts.initialSequence || 0,
    failReadBackOnce: !!opts.failReadBackOnce,
  });
  return { ledger, clock };
}

let pbCounter = 0;
function pbid() {
  pbCounter += 1;
  return 'pb1-' + sha256Hex('fixture-message-' + pbCounter);
}

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

/* ---- SS3: allocator, format, ordering ---- */

test('first registration: Index ID form is IDX-YYYYMMDD-NNNNNN with the UTC date and sequence 1', async () => {
  const { ledger } = makeLedger();
  const r = await ledger.register({ pbId: pbid(), idempotencyKey: 'k1', messageIndexRef: 'msg/1', admitted: true });
  assert.strictEqual(r.status, 'REGISTERED');
  assert.strictEqual(r.record.indexId, 'IDX-20261111-000001');
  assert.strictEqual(r.record.sequence, 1);
  assert.strictEqual(r.record.dateBasis, 'UTC');
});

test('sequences are monotonic across registrations and the date segment never orders', async () => {
  const { ledger, clock } = makeLedger();
  const a = await ledger.register({ pbId: pbid(), idempotencyKey: 'a', messageIndexRef: 'm/a', admitted: true });
  clock.t = Date.UTC(2026, 10, 12, 1, 0, 0); // next UTC day
  const b = await ledger.register({ pbId: pbid(), idempotencyKey: 'b', messageIndexRef: 'm/b', admitted: true });
  const c = await ledger.register({ pbId: pbid(), idempotencyKey: 'c', messageIndexRef: 'm/c', admitted: true });
  assert.deepStrictEqual([a.record.sequence, b.record.sequence, c.record.sequence], [1, 2, 3]);
  assert.ok(b.record.indexId.startsWith('IDX-20261112-'));
  const ordered = ledger.listByRegistrationOrder().map((r) => r.sequence);
  assert.deepStrictEqual(ordered, [1, 2, 3]);
});

test('sequence width expands past 6 digits and ordering stays numeric, never lexical (R-3)', async () => {
  const { ledger } = makeLedger({ initialSequence: 999998 });
  const a = await ledger.register({ pbId: pbid(), idempotencyKey: 'a', messageIndexRef: 'm/a', admitted: true });
  const b = await ledger.register({ pbId: pbid(), idempotencyKey: 'b', messageIndexRef: 'm/b', admitted: true });
  assert.strictEqual(a.record.indexId, 'IDX-20261111-999999');
  assert.strictEqual(b.record.indexId, 'IDX-20261111-1000000');
  // Lexical string sort would place 1000000 before 999999; the ledger must not.
  const ordered = ledger.listByRegistrationOrder().map((r) => r.sequence);
  assert.deepStrictEqual(ordered, [999999, 1000000]);
});

test('concurrent registrations for distinct PB-IDs receive unique monotonic sequences', async () => {
  const { ledger } = makeLedger();
  const inputs = Array.from({ length: 10 }, (_, i) => ({
    pbId: pbid(), idempotencyKey: 'cc' + i, messageIndexRef: 'm/' + i, admitted: true,
  }));
  const results = await Promise.all(inputs.map((i) => ledger.register(i)));
  const seqs = results.map((r) => r.record.sequence).sort((x, y) => x - y);
  assert.deepStrictEqual(seqs, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
  assert.strictEqual(new Set(results.map((r) => r.record.indexId)).size, 10);
});

test('a candidate that is not admitted is NOT_REGISTERED and consumes no sequence', async () => {
  const { ledger } = makeLedger();
  const r = await ledger.register({ pbId: pbid(), idempotencyKey: 'x', messageIndexRef: 'm/x', admitted: false });
  assert.strictEqual(r.status, 'NOT_REGISTERED');
  const ok = await ledger.register({ pbId: pbid(), idempotencyKey: 'y', messageIndexRef: 'm/y', admitted: true });
  assert.strictEqual(ok.record.sequence, 1);
});

test('counter rollback on import is an INTEGRITY_FAULT and registration stops', async () => {
  const { ledger } = makeLedger();
  await ledger.register({ pbId: pbid(), idempotencyKey: 'a', messageIndexRef: 'm/a', admitted: true });
  const state = ledger.exportState();
  state.counter = 0; // rolled back below the committed sequence
  const { ledger: restored } = makeLedger();
  const imp = restored.importState(state);
  assert.strictEqual(imp.status, 'INTEGRITY_FAULT');
  const r = await restored.register({ pbId: pbid(), idempotencyKey: 'b', messageIndexRef: 'm/b', admitted: true });
  assert.strictEqual(r.status, 'INTEGRITY_FAULT');
});

/* ---- SS3.3/SS3.4: idempotency and ambiguous outcomes ---- */

test('retry with the same idempotency identity returns the existing registration; counter advances once', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  const a = await ledger.register({ pbId: p, idempotencyKey: 'same', messageIndexRef: 'm/1', admitted: true });
  const b = await ledger.register({ pbId: p, idempotencyKey: 'same', messageIndexRef: 'm/1', admitted: true });
  assert.strictEqual(a.record.indexId, b.record.indexId);
  const next = await ledger.register({ pbId: pbid(), idempotencyKey: 'other', messageIndexRef: 'm/2', admitted: true });
  assert.strictEqual(next.record.sequence, 2);
});

test('the same PB-ID under a different idempotency key resolves to the existing record — never a second registration', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  const a = await ledger.register({ pbId: p, idempotencyKey: 'k1', messageIndexRef: 'm/1', admitted: true });
  const b = await ledger.register({ pbId: p, idempotencyKey: 'k2', messageIndexRef: 'm/1', admitted: true });
  assert.strictEqual(b.record.indexId, a.record.indexId);
  assert.strictEqual(ledger.listByRegistrationOrder().length, 1);
});

test('the same idempotency key carrying a different PB-ID is a CONFLICT, not a retry', async () => {
  const { ledger } = makeLedger();
  await ledger.register({ pbId: pbid(), idempotencyKey: 'dup', messageIndexRef: 'm/1', admitted: true });
  const r = await ledger.register({ pbId: pbid(), idempotencyKey: 'dup', messageIndexRef: 'm/2', admitted: true });
  assert.strictEqual(r.status, 'CONFLICT');
});

test('write-success/read-back-loss resolves by idempotency identity, never by allocating again', async () => {
  const { ledger } = makeLedger({ failReadBackOnce: true });
  const p = pbid();
  const r = await ledger.register({ pbId: p, idempotencyKey: 'amb', messageIndexRef: 'm/1', admitted: true });
  assert.strictEqual(r.status, 'REGISTRATION_UNKNOWN');
  const resolved = await ledger.resolveByIdempotency('amb');
  assert.strictEqual(resolved.status, 'REGISTERED');
  assert.strictEqual(resolved.record.pbId, p);
  const next = await ledger.register({ pbId: pbid(), idempotencyKey: 'n', messageIndexRef: 'm/2', admitted: true });
  assert.strictEqual(next.record.sequence, 2); // exactly one sequence was consumed
});

test('two simultaneous registrations for the same PB-ID produce exactly one record', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  const [a, b] = await Promise.all([
    ledger.register({ pbId: p, idempotencyKey: 's1', messageIndexRef: 'm/1', admitted: true }),
    ledger.register({ pbId: p, idempotencyKey: 's2', messageIndexRef: 'm/1', admitted: true }),
  ]);
  assert.strictEqual(a.record.indexId, b.record.indexId);
  assert.strictEqual(ledger.listByRegistrationOrder().length, 1);
});

/* ---- SS4/SS5: boundary, permanence, thin record ---- */

test('the routing record carries the SS5 required fields and never the message body', async () => {
  const { ledger } = makeLedger();
  const r = await ledger.register({
    pbId: pbid(), idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true,
    body: 'SECRET BODY TEXT', sender: 'alex',
  });
  const rec = r.record;
  for (const f of ['indexId', 'pbId', 'sequence', 'registeredAt', 'dateBasis',
    'messageIndexRef', 'activeDisposition', 'activeDispositionEventId',
    'latestEventId', 'latestAttemptId', 'duplicateCount', 'recordRevision', 'recordIntegrity']) {
    assert.ok(f in rec, 'missing field ' + f);
  }
  assert.ok(!JSON.stringify(rec).includes('SECRET BODY TEXT'));
});

test('a registered record is permanent: skip, discard and close never erase the mapping', async () => {
  const { ledger } = makeLedger();
  const r = await ledger.register({ pbId: pbid(), idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  const idx = r.record.indexId;
  await ledger.appendEvent(idx, { type: 'SKIPPED', actor: 'owner' });
  await ledger.appendEvent(idx, { type: 'DISCARDED', actor: 'owner' });
  await ledger.appendEvent(idx, { type: 'CLOSED', actor: 'owner', data: { reason: 'done' } });
  const byIndex = ledger.lookupByIndex(idx);
  assert.strictEqual(byIndex.pbId, r.record.pbId);
  assert.strictEqual(ledger.currentState(idx).indexId, idx);
});

/* ---- SS6/SS9: lifecycle projection, integrity, recovery ---- */

test('the current-state projection is a deterministic fold of the append-only events (rebuild equals stored)', async () => {
  const { ledger } = makeLedger();
  const r = await ledger.register({ pbId: pbid(), idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  const idx = r.record.indexId;
  await ledger.appendEvent(idx, { type: 'HELD_FOR_REVIEW', actor: 'system' });
  await ledger.appendEvent(idx, { type: 'REFUSED', actor: 'system', data: { check: 'demo' } });
  const stored = ledger.currentState(idx);
  const rebuilt = ledger.rebuildProjection(idx);
  assert.deepStrictEqual(rebuilt, stored);
  const ids = ledger.events(idx).map((e) => e.eventId);
  assert.strictEqual(new Set(ids).size, ids.length);
});

test('an unknown event type is rejected loudly, never silently ignored', async () => {
  const { ledger } = makeLedger();
  const r = await ledger.register({ pbId: pbid(), idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  const out = await ledger.appendEvent(r.record.indexId, { type: 'TELEPORTED', actor: 'system' });
  assert.strictEqual(out.status, 'REJECTED');
});

test('system-only events cannot be appended by hand (REGISTERED)', async () => {
  const { ledger } = makeLedger();
  const r = await ledger.register({ pbId: pbid(), idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  const out = await ledger.appendEvent(r.record.indexId, { type: 'REGISTERED', actor: 'system' });
  assert.strictEqual(out.status, 'REJECTED');
});

test('record integrity: tampering is detected by verifyIntegrity', async () => {
  const { ledger } = makeLedger();
  const r = await ledger.register({ pbId: pbid(), idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  const idx = r.record.indexId;
  assert.strictEqual(await ledger.verifyIntegrity(idx), true);
  ledger.__tamperForTest(idx, (rec) => { rec.duplicateCount = 99; });
  assert.strictEqual(await ledger.verifyIntegrity(idx), false);
});

/* ---- SS7.2/SS7.2A/SS4.3: intake refusal and R-2 promotion ---- */

test('R-2: a pre-registration refusal promotes as the first disposition event; intake preserved; registration not blocked', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  const intakeBefore = await ledger.recordIntakeRefusal({
    pbId: p, type: 'REFUSED', actor: 'system', failedCheck: 'fence-demo',
    evidenceRef: 'ev/1', occurredAt: T0 - 1000,
  });
  const r = await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  assert.strictEqual(r.status, 'REGISTERED'); // registration itself not blocked
  const st = ledger.currentState(r.record.indexId);
  assert.strictEqual(st.activeDisposition, 'REFUSED');
  const evs = ledger.events(r.record.indexId);
  assert.strictEqual(evs[0].type, 'REGISTERED');
  assert.strictEqual(evs[1].type, 'PRE_REGISTRATION_REFUSAL_PROMOTED');
  assert.strictEqual(st.activeDispositionEventId, evs[1].eventId);
  const intakeAfter = ledger.intakeRefusal(intakeBefore.intakeId);
  assert.deepStrictEqual(intakeAfter, intakeBefore); // original preserved unchanged
});

test('a promoted refusal blocks attempt creation until superseded', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  await ledger.recordIntakeRefusal({ pbId: p, type: 'REFUSED', actor: 'system', failedCheck: 'x', occurredAt: T0 - 5 });
  const r = await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  const att = await ledger.createAttempt(r.record.indexId, { via: 'initial', actor: 'system' });
  assert.strictEqual(att.status, 'HELD');
  assert.ok(att.reasons.some((x) => x.includes('refus')));
});

test('correlation UNKNOWN: an intake refusal tentatively tied to a candidate holds that item send-admission, and only that item', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  const other = pbid();
  await ledger.recordIntakeRefusal({
    candidatePbId: p, correlation: 'UNKNOWN', type: 'REFUSED', actor: 'system',
    failedCheck: 'x', occurredAt: T0 - 5,
  });
  const r = await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  assert.strictEqual(r.status, 'REGISTERED'); // registration proceeds (no exact correlation, no promotion)
  assert.strictEqual(ledger.currentState(r.record.indexId).activeDisposition, 'REGISTERED');
  const adm = await ledger.sendAdmission(p);
  assert.strictEqual(adm.allowed, false);
  assert.ok(adm.reasons.some((x) => x.includes('correlation')));
  const ro = await ledger.register({ pbId: other, idempotencyKey: 'k2', messageIndexRef: 'm/2', admitted: true });
  const admOther = await ledger.sendAdmission(other);
  assert.strictEqual(admOther.allowed, true);
  assert.strictEqual(ro.status, 'REGISTERED');
});

test('refused content stays retrievable by the message route and never enters the information route', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  await ledger.recordIntakeRefusal({ pbId: p, type: 'REFUSED', actor: 'system', failedCheck: 'x', occurredAt: T0 - 5 });
  await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/refused', admitted: true });
  const msg = ledger.messageLookup(p);
  assert.strictEqual(msg.messageIndexRef, 'm/refused');
  const info = ledger.informationLookup(p);
  assert.strictEqual(info.status, 'NOT_MESSAGE_KNOWLEDGE');
  assert.ok(!('messageIndexRef' in info));
});

/* ---- SS7.3/SS7.4: supersession and the B re-presentation boundary ---- */

async function refusedRegistration() {
  const { ledger } = makeLedger();
  const p = pbid();
  const r = await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  const idx = r.record.indexId;
  const refusal = await ledger.appendEvent(idx, { type: 'REFUSED', actor: 'system', data: { check: 'demo' } });
  return { ledger, idx, p, refusal };
}

test('supersession changes the active disposition and leaves the original refusal untouched', async () => {
  const { ledger, idx, refusal } = await refusedRegistration();
  const sup = await ledger.appendEvent(idx, {
    type: 'SUPERSEDED', actor: 'ben', authorityRef: 'owner-act',
    supersedesEventId: refusal.event.eventId,
  });
  assert.strictEqual(sup.status, 'APPLIED');
  assert.strictEqual(ledger.currentState(idx).activeDisposition, 'SUPERSEDED');
  const original = ledger.events(idx).find((e) => e.eventId === refusal.event.eventId);
  assert.strictEqual(original.type, 'REFUSED');
});

test('a passive duplicate after supersession is count only — no attempt is created', async () => {
  const { ledger, idx, p, refusal } = await refusedRegistration();
  await ledger.appendEvent(idx, { type: 'SUPERSEDED', actor: 'ben', supersedesEventId: refusal.event.eventId });
  const before = ledger.events(idx).length;
  await ledger.observeDuplicate(p);
  const evs = ledger.events(idx);
  assert.strictEqual(ledger.currentState(idx).duplicateCount, 1);
  assert.ok(!evs.some((e) => e.type === 'ATTEMPT_CREATED'));
  assert.ok(evs.length === before + 1); // the DUPLICATE_OBSERVED event only
});

test('B path: supersession + Ben direction yields exactly one fresh attempt; eligibility is one-shot', async () => {
  const { ledger, idx, refusal } = await refusedRegistration();
  const sup = await ledger.appendEvent(idx, { type: 'SUPERSEDED', actor: 'ben', supersedesEventId: refusal.event.eventId });
  const dir = await ledger.appendEvent(idx, {
    type: 'RE_PRESENTATION_DIRECTED', actor: 'ben', authorityRef: 'owner-direction',
    causationEventId: sup.event.eventId,
  });
  assert.strictEqual(dir.status, 'APPLIED');
  const a1 = await ledger.createAttempt(idx, {
    via: 're-presentation', actor: 'system',
    supersedesEventId: sup.event.eventId, directionEventId: dir.event.eventId,
  });
  assert.strictEqual(a1.status, 'CREATED');
  assert.ok(a1.attemptId);
  const a2 = await ledger.createAttempt(idx, {
    via: 're-presentation', actor: 'system',
    supersedesEventId: sup.event.eventId, directionEventId: dir.event.eventId,
  });
  assert.strictEqual(a2.status, 'HELD'); // eligibility already consumed
  const [c1, c2] = await Promise.all([
    ledger.createAttempt(idx, { via: 're-presentation', actor: 'system', supersedesEventId: sup.event.eventId, directionEventId: dir.event.eventId }),
    ledger.createAttempt(idx, { via: 're-presentation', actor: 'system', supersedesEventId: sup.event.eventId, directionEventId: dir.event.eventId }),
  ]);
  assert.ok(!(c1.status === 'CREATED' && c2.status === 'CREATED'));
});

test('re-presentation without a supersession is refused — direction alone creates nothing', async () => {
  const { ledger, idx } = await refusedRegistration();
  const a = await ledger.createAttempt(idx, { via: 're-presentation', actor: 'system', supersedesEventId: 'EVT-nope', directionEventId: 'EVT-nope' });
  assert.strictEqual(a.status, 'HELD');
});

test('a fresh attempt that is refused makes the new refusal active; the old supersession cannot reopen it', async () => {
  const { ledger, idx, refusal } = await refusedRegistration();
  const sup = await ledger.appendEvent(idx, { type: 'SUPERSEDED', actor: 'ben', supersedesEventId: refusal.event.eventId });
  const dir = await ledger.appendEvent(idx, { type: 'RE_PRESENTATION_DIRECTED', actor: 'ben', causationEventId: sup.event.eventId });
  const a1 = await ledger.createAttempt(idx, { via: 're-presentation', actor: 'system', supersedesEventId: sup.event.eventId, directionEventId: dir.event.eventId });
  assert.strictEqual(a1.status, 'CREATED');
  await ledger.appendEvent(idx, { type: 'REFUSED', actor: 'system', attemptId: a1.attemptId, data: { check: 'again' } });
  assert.strictEqual(ledger.currentState(idx).activeDisposition, 'REFUSED');
  const a2 = await ledger.createAttempt(idx, { via: 're-presentation', actor: 'system', supersedesEventId: sup.event.eventId, directionEventId: dir.event.eventId });
  assert.strictEqual(a2.status, 'HELD');
});

/* ---- SS7.5/SS7.6/SS8: dispatch, delivery knowledge, lifetime block ---- */

async function dispatchedAttempt() {
  const { ledger } = makeLedger();
  const p = pbid();
  const r = await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  const idx = r.record.indexId;
  const att = await ledger.createAttempt(idx, { via: 'initial', actor: 'system' });
  await ledger.appendEvent(idx, { type: 'DISPATCHED', actor: 'system', attemptId: att.attemptId });
  return { ledger, idx, p, attemptId: att.attemptId };
}

test('dispatch is not delivery: knowledge stays UNKNOWN after DISPATCHED', async () => {
  const { ledger, idx, attemptId } = await dispatchedAttempt();
  assert.strictEqual(ledger.deliveryKnowledge(idx, attemptId), 'UNKNOWN');
});

test('confirmed delivery blocks send-admission for life under that PB-ID; retrieval still works', async () => {
  const { ledger, idx, p, attemptId } = await dispatchedAttempt();
  await ledger.appendEvent(idx, { type: 'DELIVERY_CONFIRMED', actor: 'system', attemptId, evidenceRef: 'ev/d1' });
  const adm = await ledger.sendAdmission(p);
  assert.strictEqual(adm.allowed, false);
  assert.ok(adm.reasons.some((x) => x.includes('delivered')));
  const att = await ledger.createAttempt(idx, { via: 'initial', actor: 'system' });
  assert.strictEqual(att.status, 'HELD');
  assert.strictEqual(ledger.messageLookup(p).messageIndexRef, 'm/1'); // retrieval unaffected
  assert.strictEqual(ledger.lookupByIndex(idx).pbId, p);
});

test('CONFIRMED on one attempt controls over PROVEN_NOT_DELIVERED on another; the conflict is flagged, never auto-retried', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  const r = await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  const idx = r.record.indexId;
  const a1 = await ledger.createAttempt(idx, { via: 'initial', actor: 'system' });
  await ledger.appendEvent(idx, { type: 'DISPATCHED', actor: 'system', attemptId: a1.attemptId });
  await ledger.appendEvent(idx, { type: 'PROVEN_NOT_DELIVERED', actor: 'system', attemptId: a1.attemptId, evidenceRef: 'ev/nd' });
  assert.strictEqual((await ledger.sendAdmission(p)).allowed, true); // no confirmed delivery yet
  const a2 = await ledger.createAttempt(idx, { via: 'initial', actor: 'system' });
  assert.strictEqual(a2.status, 'CREATED');
  await ledger.appendEvent(idx, { type: 'DISPATCHED', actor: 'system', attemptId: a2.attemptId });
  await ledger.appendEvent(idx, { type: 'DELIVERY_CONFIRMED', actor: 'system', attemptId: a2.attemptId, evidenceRef: 'ev/d' });
  const adm = await ledger.sendAdmission(p);
  assert.strictEqual(adm.allowed, false);
  assert.strictEqual(ledger.currentState(idx).deliveryConflict, true);
});

test('a late delivery confirmation updates the exact attempt and creates no new registration', async () => {
  const { ledger, idx, attemptId } = await dispatchedAttempt();
  const before = ledger.listByRegistrationOrder().length;
  await ledger.appendEvent(idx, { type: 'DELIVERY_CONFIRMED', actor: 'system', attemptId, evidenceRef: 'ev/late' });
  assert.strictEqual(ledger.deliveryKnowledge(idx, attemptId), 'CONFIRMED');
  assert.strictEqual(ledger.listByRegistrationOrder().length, before);
});

test('FORCE_SENT records the owner act at dispatch and asserts no delivery; a pre-dispatch force on a refused attempt records nothing', async () => {
  const { ledger, idx, attemptId } = await dispatchedAttempt();
  assert.strictEqual(ledger.deliveryKnowledge(idx, attemptId), 'UNKNOWN');
  const { ledger: l2, idx: idx2, refusal } = await refusedRegistration();
  const att = await l2.createAttempt(idx2, { via: 'initial', actor: 'system' });
  assert.strictEqual(att.status, 'HELD'); // refused: no attempt exists to force
  const fs = await l2.appendEvent(idx2, { type: 'FORCE_SENT', actor: 'ben', attemptId: att.attemptId || 'ATT-none' });
  assert.strictEqual(fs.status, 'REJECTED');
  void refusal;
});

/* ---- SS8: duplicates ---- */

test('duplicate observation increments the durable count and appends DUPLICATE_OBSERVED under the event policy', async () => {
  const { ledger } = makeLedger({ duplicateEventPolicy: 'event' });
  const p = pbid();
  const r = await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  await ledger.observeDuplicate(p);
  await ledger.observeDuplicate(p);
  const st = ledger.currentState(r.record.indexId);
  assert.strictEqual(st.duplicateCount, 2);
  assert.strictEqual(ledger.events(r.record.indexId).filter((e) => e.type === 'DUPLICATE_OBSERVED').length, 2);
});

test('under the counter-only policy the count increments and no event is appended (SS13.5 stays an explicit policy, never a silent default)', async () => {
  const { ledger } = makeLedger({ duplicateEventPolicy: 'counter-only' });
  const p = pbid();
  const r = await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  await ledger.observeDuplicate(p);
  const st = ledger.currentState(r.record.indexId);
  assert.strictEqual(st.duplicateCount, 1);
  assert.strictEqual(ledger.events(r.record.indexId).filter((e) => e.type === 'DUPLICATE_OBSERVED').length, 0);
});

test('observing a duplicate of an unregistered PB-ID creates nothing', async () => {
  const { ledger } = makeLedger();
  const out = await ledger.observeDuplicate(pbid());
  assert.strictEqual(out.status, 'NOT_REGISTERED');
  assert.strictEqual(ledger.listByRegistrationOrder().length, 0);
});

/* ---- Two retrieval routes (plan scope item 6; contract SS8.6/SS10) ---- */

test('the Index ID route resolves Index -> PB-ID -> message reference, the same destination as the PB-ID route', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  const r = await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/route', admitted: true });
  const viaIndex = ledger.lookupByIndex(r.record.indexId);
  assert.strictEqual(viaIndex.pbId, p);
  assert.strictEqual(viaIndex.messageIndexRef, 'm/route');
  assert.strictEqual(ledger.messageLookup(p).messageIndexRef, viaIndex.messageIndexRef);
});

test('the information route never returns a message record, registered or not', async () => {
  const { ledger } = makeLedger();
  const p = pbid();
  await ledger.register({ pbId: p, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  assert.strictEqual(ledger.informationLookup(p).status, 'NOT_MESSAGE_KNOWLEDGE');
  assert.strictEqual(ledger.informationLookup(pbid()).status, 'NOT_MESSAGE_KNOWLEDGE');
});

/* ---- Input discipline (family rule, batch 1) ---- */

test('register rejects non-string and missing identity fields without coercion', async () => {
  const { ledger } = makeLedger();
  const a = await ledger.register({ pbId: 42, idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  assert.strictEqual(a.status, 'NOT_REGISTERED');
  const b = await ledger.register({ idempotencyKey: 'k', messageIndexRef: 'm/1', admitted: true });
  assert.strictEqual(b.status, 'NOT_REGISTERED');
  assert.strictEqual(ledger.listByRegistrationOrder().length, 0);
});

/* ---- Runner ---- */

(async () => {
  let pass = 0;
  const failures = [];
  for (const { name, fn } of tests) {
    try {
      await fn();
      pass += 1;
      console.log(`PASS  ${name}`);
    } catch (err) {
      failures.push({ name, err });
      console.log(`FAIL  ${name}\n      ${String(err.message).split('\n')[0]}`);
    }
  }
  console.log(`\nledger.fixtures: ${pass}/${tests.length} passed, ${failures.length} failed`);
  process.exit(failures.length === 0 ? 0 : 1);
})();
