'use strict';
/*
 * Stage 1 batch 3 fixtures: capture acknowledgement, bridge
 * epoch, owner-review backend, migration inventory.
 * Build Plan 01 S3 scope items 7-9 + the migration rules.
 * Run: node tests-stage1/batch3.fixtures.js ; exit 0 = pass.
 */

const assert = require('node:assert');
const { createHash } = require('node:crypto');
const identityMod = require('../identity.js');
const ledgerMod = require('../ledger.js');
const captureMod = require('../capture.js');
const migrationMod = require('../migration.js');

async function sha256Hex(s) {
  return createHash('sha256').update(s, 'utf8').digest('hex');
}

const T0 = Date.UTC(2026, 10, 11, 12, 0, 0);

function makeLedger(opts = {}) {
  const clock = { t: T0 };
  return ledgerMod.createLedger({
    now: () => clock.t,
    sha256Hex,
    duplicateEventPolicy: 'event',
    authorityVerifier: opts.noAuthority
      ? undefined
      : (act) => act.actor === 'ben' && typeof act.authorityRef === 'string' && act.authorityRef.length > 0,
    failReadBackOnce: !!opts.failReadBackOnce,
  });
}

function makeSession(opts = {}) {
  const ledger = makeLedger(opts);
  const epochStore = captureMod.createEpochStore({});
  const session = captureMod.createCaptureSession({ ledger, epochStore, sha256Hex });
  return { ledger, epochStore, session };
}

function chatgptSource(msgId) {
  return { form: 'native', platform: 'chatgpt', scope: 'conversation', conversation: 'c-1', messageId: msgId };
}

// In a live-epoch bridge every detection carries the current
// epoch. This helper stamps it openly so the ack-path fixtures
// exercise the ack with the gate satisfied — and the raw
// unstamped path stays visibly tested in the epoch fixtures.
function submit(session, epochStore, det) {
  return session.submitDetection({ ...det, epoch: epochStore.current() });
}

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

/* ---- item 7: capture acknowledgement ---- */

test('a verified registration acknowledges REGISTERED and the handoff may retire', async () => {
  const { session, epochStore } = makeSession();
  const ack = await submit(session, epochStore, { handoffId: 'h1', source: chatgptSource('m-1'), admitted: true });
  assert.strictEqual(ack.outcome, 'REGISTERED');
  assert.ok(ack.indexId);
  assert.ok(ack.pbId.startsWith('pb1-'));
  const ret = session.retireHandoff('h1');
  assert.strictEqual(ret.retired, true);
  assert.strictEqual(session.pendingCount(), 0);
});

test('a second detection of the same source acknowledges DUPLICATE against the same record', async () => {
  const { session, epochStore, ledger } = makeSession();
  const a1 = await submit(session, epochStore, { handoffId: 'h1', source: chatgptSource('m-1'), admitted: true });
  const a2 = await submit(session, epochStore, { handoffId: 'h2', source: chatgptSource('m-1'), admitted: true });
  assert.strictEqual(a2.outcome, 'DUPLICATE');
  assert.strictEqual(a2.indexId, a1.indexId);
  assert.strictEqual(ledger.listByRegistrationOrder().length, 1);
  assert.strictEqual(session.retireHandoff('h2').retired, true);
});

test('a non-admitted candidate acknowledges NOT_REGISTERED and cannot retire without a recorded disposition', async () => {
  const { session, epochStore } = makeSession();
  const ack = await submit(session, epochStore, { handoffId: 'h1', source: chatgptSource('m-1'), admitted: false });
  assert.strictEqual(ack.outcome, 'NOT_REGISTERED');
  assert.strictEqual(session.retireHandoff('h1').retired, false);
  session.recordDisposition('h1', { kind: 'system-refused', actor: 'system', note: 'not admitted at the boundary' });
  assert.strictEqual(session.retireHandoff('h1').retired, true);
});

test('read-back loss acknowledges REGISTRATION_UNKNOWN; the handoff stays pending and resolves by idempotency identity', async () => {
  const { session, epochStore, ledger } = makeSession({ failReadBackOnce: true });
  const ack = await submit(session, epochStore, { handoffId: 'h1', source: chatgptSource('m-1'), admitted: true });
  assert.strictEqual(ack.outcome, 'REGISTRATION_UNKNOWN');
  assert.strictEqual(session.retireHandoff('h1').retired, false);
  const resolved = await session.resolveUnknown('h1');
  assert.strictEqual(resolved.outcome, 'REGISTERED');
  assert.strictEqual(ledger.listByRegistrationOrder().length, 1); // never a second registration
  assert.strictEqual(session.retireHandoff('h1').retired, true);
});

test('an unidentifiable source acknowledges NOT_REGISTERED with the identity reason — no identity is invented', async () => {
  const { session, epochStore } = makeSession();
  const ack = await submit(session, epochStore, { handoffId: 'h1', source: { scope: 'platform', platform: 'chatgpt' }, admitted: true });
  assert.strictEqual(ack.outcome, 'NOT_REGISTERED');
  assert.ok(ack.reason && ack.reason.includes('identity'));
  assert.strictEqual(ack.indexId, null);
});

test('an identity collision is a visible hold: NOT_REGISTERED, pending, flagged, retirable only by recorded disposition', async () => {
  const { session, epochStore } = makeSession();
  // Force a collision by pre-claiming m-1's PB-ID under
  // divergent material (the claim store's contract).
  const idn = identityMod.createIdentity({ sha256Hex });
  const derived = await idn.deriveFromSourceKey(chatgptSource('m-1'));
  assert.strictEqual(derived.status, 'OK');
  const store = session.claimStore();
  store.claim(derived.pbid, 'divergent-material');
  const ack = await submit(session, epochStore, { handoffId: 'h1', source: chatgptSource('m-1'), admitted: true });
  assert.strictEqual(ack.outcome, 'NOT_REGISTERED');
  assert.strictEqual(ack.reason, 'identity-collision');
  assert.strictEqual(session.retireHandoff('h1').retired, false);
  session.recordDisposition('h1', { kind: 'owner-review', actor: 'ben', authorityRef: 'owner-act' });
  assert.strictEqual(session.retireHandoff('h1').retired, true);
});

/* ---- item 8: epoch ---- */

test('epoch persists across restart and never rolls back', async () => {
  const store = captureMod.createEpochStore({});
  assert.strictEqual(store.current(), 0);
  const adv = store.advance('pause');
  assert.strictEqual(adv.epoch, 1);
  const restored = captureMod.createEpochStore({});
  const imp = restored.importState(store.exportState());
  assert.strictEqual(imp.status, 'OK');
  assert.strictEqual(restored.current(), 1);
  const bad = restored.importState({ epoch: 0 });
  assert.strictEqual(bad.status, 'REJECTED');
  assert.strictEqual(restored.current(), 1);
});

test('events carry the epoch; stale events are rejected and create nothing', async () => {
  const { session, epochStore, ledger } = makeSession();
  const stamped = epochStore.stamp('detection', { handoffId: 'h1' });
  assert.strictEqual(stamped.epoch, 0);
  epochStore.advance('pause'); // epoch 1
  assert.strictEqual(epochStore.admit(stamped).accepted, false);
  const ack = await session.submitDetection({ handoffId: 'h1', source: chatgptSource('m-1'), admitted: true, epoch: stamped.epoch });
  assert.strictEqual(ack.outcome, 'STALE');
  assert.strictEqual(ledger.listByRegistrationOrder().length, 0);
  const fresh = await session.submitDetection({ handoffId: 'h2', source: chatgptSource('m-2'), admitted: true, epoch: epochStore.current() });
  assert.strictEqual(fresh.outcome, 'REGISTERED');
});

test('a detection with no epoch never reaches registration when an epoch store is configured', async () => {
  const { session, ledger } = makeSession();
  const ack = await session.submitDetection({ handoffId: 'h1', source: chatgptSource('m-1'), admitted: true });
  assert.strictEqual(ack.outcome, 'STALE');
  assert.strictEqual(ack.reason, 'epoch-missing');
  assert.strictEqual(ledger.listByRegistrationOrder().length, 0);
  assert.strictEqual(session.pendingCount(), 0);
});

test('an event with no epoch is rejected fail-closed', async () => {
  const store = captureMod.createEpochStore({});
  assert.strictEqual(store.admit({ kind: 'detection' }).accepted, false);
  assert.strictEqual(store.admit({ kind: 'detection' }).reason, 'epoch-missing');
});

test('a detection with no epoch is also rejected when the epoch store is unavailable (reviewer-added regression)', async () => {
  const ledger = makeLedger();
  const session = captureMod.createCaptureSession({ ledger, sha256Hex });
  const ack = await session.submitDetection({
    handoffId: 'h-no-store-no-epoch',
    source: chatgptSource('m-no-store-no-epoch'),
    admitted: true,
  });
  assert.strictEqual(ack.outcome, 'STALE');
  assert.strictEqual(ack.reason, 'epoch-unverifiable');
  assert.strictEqual(ledger.listByRegistrationOrder().length, 0);
  assert.strictEqual(session.pendingCount(), 0);
});

test('a detection is rejected when the epoch store is unavailable, even if it carries an epoch', async () => {
  const ledger = makeLedger();
  const session = captureMod.createCaptureSession({ ledger, sha256Hex });
  const ack = await session.submitDetection({
    handoffId: 'h-no-epoch-store',
    source: chatgptSource('m-no-epoch-store'),
    admitted: true,
    epoch: 0,
  });
  assert.strictEqual(ack.outcome, 'STALE');
  assert.strictEqual(ack.reason, 'epoch-unverifiable');
  assert.strictEqual(ledger.listByRegistrationOrder().length, 0);
  assert.strictEqual(session.pendingCount(), 0);
});

/* ---- item 9: owner-review backend ---- */

test('held work keeps identity and record; Ben decision is a lifecycle event; nothing is purged', async () => {
  const { session, epochStore, ledger } = makeSession();
  const review = captureMod.createOwnerReview({ ledger });
  const ack = await submit(session, epochStore, { handoffId: 'h1', source: chatgptSource('m-1'), admitted: true });
  const idx = ack.indexId;
  assert.strictEqual(review.listReviewItems().length, 0);
  const held = await review.hold(idx, { actor: 'ben', authorityRef: 'owner-act' });
  assert.strictEqual(held.status, 'APPLIED');
  const items = review.listReviewItems();
  assert.strictEqual(items.length, 1);
  assert.strictEqual(items[0].indexId, idx);
  assert.strictEqual(items[0].pbId, ack.pbId);
  const decided = await review.decide(idx, { decision: 'discard', actor: 'ben', authorityRef: 'owner-act' });
  assert.strictEqual(decided.status, 'APPLIED');
  assert.strictEqual(review.listReviewItems().length, 0);
  // The record is untouched by the decision: still registered,
  // still retrievable by the message route.
  assert.strictEqual(ledger.messageLookup(ack.pbId).status, 'FOUND');
  assert.strictEqual(ledger.currentState(idx).activeDisposition, 'DISCARDED');
});

test('an unverified discard is refused at the authority boundary and the item stays queued', async () => {
  const { session, epochStore, ledger } = makeSession();
  const review = captureMod.createOwnerReview({ ledger });
  const ack = await submit(session, epochStore, { handoffId: 'h1', source: chatgptSource('m-1'), admitted: true });
  await review.hold(ack.indexId, { actor: 'ben', authorityRef: 'owner-act' });
  const decided = await review.decide(ack.indexId, { decision: 'discard', actor: 'mallory', authorityRef: 'forged' });
  assert.strictEqual(decided.status, 'REJECTED');
  assert.strictEqual(review.listReviewItems().length, 1);
});

test('refused registrations appear in the review queue in registration order', async () => {
  const { ledger } = makeSession();
  const review = captureMod.createOwnerReview({ ledger });
  const r1 = await ledger.register({ pbId: 'pb1-' + 'a'.repeat(64), idempotencyKey: 'k1', messageIndexRef: 'm/1', admitted: true });
  const r2 = await ledger.register({ pbId: 'pb1-' + 'b'.repeat(64), idempotencyKey: 'k2', messageIndexRef: 'm/2', admitted: true });
  await ledger.appendEvent(r2.record.indexId, { type: 'REFUSED', actor: 'system', data: { failedCheck: 'x' } });
  await ledger.appendEvent(r1.record.indexId, { type: 'REFUSED', actor: 'system', data: { failedCheck: 'x' } });
  const items = review.listReviewItems();
  assert.deepStrictEqual(items.map((i) => i.indexId), [r1.record.indexId, r2.record.indexId]);
});

/* ---- migration inventory ---- */

function legacyState() {
  return {
    registrations: { remmy: { tabId: 1 }, alex: null },
    paused: false,
    seen: ['fp-aaa', 'fp-bbb'],
    detections: [
      { envelope: { message_id: 'legacy-id-1', fingerprint: 'fp-aaa' }, detectedIn: 'alex', at: 1 },
      { envelope: { message_id: 'legacy-id-2', fingerprint: 'fp-ccc' }, detectedIn: 'remmy', at: 2 },
      { envelope: { message_id: 'legacy-id-3', fingerprint: 'fp-ddd' }, detectedIn: 'alex', at: 3 },
    ],
    delivered: ['fp-aaa'],
    deliveryFailed: [],
    deliveredIds: ['legacy-id-9'],
    deliveryFailedIds: ['legacy-id-2'],
    seenIds: ['legacy-id-1', 'legacy-id-9'],
    fpToId: { 'fp-aaa': 'legacy-id-1' },
    pair: { step: 'await-reply', from: 'remmy', to: 'alex', callId: 'legacy-id-1' },
    bufferId: 'legacy-id-2',
    fileTransfers: [{ messageId: 'legacy-id-9', status: 'verified' }],
    rollovers: [],
    alerts: [{ id: 'a1' }],
    serialNext: 7,
    completedSerials: [{ serial: 3, id: 'legacy-id-7' }],
    log: [{ at: 1, text: 'x' }],
    futureUnknownStore: [{ z: 1 }],
  };
}

test('migration inventories every legacy store and never modifies or drops the source state', async () => {
  const state = legacyState();
  const before = JSON.parse(JSON.stringify(state));
  const inv = migrationMod.inventoryLegacyState(state);
  assert.deepStrictEqual(state, before); // preserved, untouched
  const storeNames = inv.stores.map((s) => s.name);
  for (const name of Object.keys(before)) {
    assert.ok(storeNames.includes(name), 'store inventoried: ' + name);
  }
  const unknown = inv.stores.find((s) => s.name === 'futureUnknownStore');
  assert.strictEqual(unknown.classification, 'unclassified-preserved');
});

test('a pending legacy detection with no outcome anywhere keeps its old PB-ID, delivery unknown, re-send blocked', async () => {
  const inv = migrationMod.inventoryLegacyState(legacyState());
  const e = inv.entries.find((x) => x.legacyId === 'legacy-id-3');
  assert.strictEqual(e.classification, 'legacy');
  assert.strictEqual(e.delivery, 'unknown');
  assert.strictEqual(e.resendBlocked, true);
});

test('delivery truth flows across the legacy fpToId mapping: the mapped detection inherits the recorded carry', async () => {
  const inv = migrationMod.inventoryLegacyState(legacyState());
  const e = inv.entries.find((x) => x.legacyId === 'legacy-id-1');
  // fp-aaa sits in delivered[] and fpToId ties it to legacy-id-1.
  assert.strictEqual(e.delivery, 'confirmed-delivered');
  assert.strictEqual(e.resendBlocked, true);
});

test('a legacy confirmed delivery stays blocked for life; a legacy proven failure is recorded, not blocked', async () => {
  const inv = migrationMod.inventoryLegacyState(legacyState());
  const delivered = inv.entries.find((x) => x.legacyId === 'legacy-id-9');
  assert.strictEqual(delivered.delivery, 'confirmed-delivered');
  assert.strictEqual(delivered.resendBlocked, true);
  const failed = inv.entries.find((x) => x.legacyId === 'legacy-id-2');
  assert.strictEqual(failed.delivery, 'proven-not-delivered');
  assert.strictEqual(failed.resendBlocked, false);
});

test('a fingerprint with no id mapping is an uncertain identity, never upgraded', async () => {
  const inv = migrationMod.inventoryLegacyState(legacyState());
  const e = inv.entries.find((x) => x.legacyId === 'fp-bbb');
  assert.strictEqual(e.classification, 'uncertain');
  assert.strictEqual(e.kind, 'fingerprint');
});

test('the active pair and buffer are inventoried as held active state, never auto-carried', async () => {
  const inv = migrationMod.inventoryLegacyState(legacyState());
  const pair = inv.stores.find((s) => s.name === 'pair');
  assert.strictEqual(pair.classification, 'active-held');
  assert.strictEqual(inv.summary.activeHeld, 1);
});

(async () => {
  let pass = 0;
  const failures = [];
  for (const t of tests) {
    try {
      await t.fn();
      pass += 1;
      console.log('PASS  ' + t.name);
    } catch (err) {
      failures.push({ name: t.name, err });
      console.log('FAIL  ' + t.name + '\n      ' + String(err && err.message).split('\n')[0]);
    }
  }
  console.log('\nbatch3.fixtures: ' + pass + '/' + tests.length + ' passed, ' + failures.length + ' failed');
  process.exitCode = failures.length ? 1 : 0;
})();
