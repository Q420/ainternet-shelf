'use strict';
/*
 * Stage 1 delivery fixtures: the generated bundle
 * (stage1core.js) carries the four core modules as browser
 * globals, and the wiring file loads without a browser.
 * Run: node tests-stage1/delivery.fixtures.js ; exit 0 = pass.
 */

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');

async function sha256Hex(s) {
  return createHash('sha256').update(s, 'utf8').digest('hex');
}

const tree = path.join(__dirname, '..');
eval(fs.readFileSync(path.join(tree, 'stage1core.js'), 'utf8'));
const wiringCode = fs.readFileSync(path.join(tree, 'stage1-wiring.js'), 'utf8') +
  '\n;globalThis.__wiring = { pbStage1OnDetection, pbStage1OnPauseOrDisconnect, pbStage1Ensure };';
eval(wiringCode);
const { pbStage1OnDetection, pbStage1OnPauseOrDisconnect, pbStage1Ensure } = globalThis.__wiring;

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

test('the bundle publishes all four Stage 1 core modules as globals', async () => {
  assert.strictEqual(typeof globalThis.PBIdentity.createIdentity, 'function');
  assert.strictEqual(typeof globalThis.PBLedger.createLedger, 'function');
  assert.strictEqual(typeof globalThis.PBCapture.createCaptureSession, 'function');
  assert.strictEqual(typeof globalThis.PBCapture.createEpochStore, 'function');
  assert.strictEqual(typeof globalThis.PBCapture.createOwnerReview, 'function');
  assert.strictEqual(typeof globalThis.PBMigration.inventoryLegacyState, 'function');
});

test('the wiring file loads and exposes its three seams without a browser', async () => {
  assert.strictEqual(typeof pbStage1OnDetection, 'function');
  assert.strictEqual(typeof pbStage1OnPauseOrDisconnect, 'function');
  assert.strictEqual(typeof pbStage1Ensure, 'function');
});

test('end-to-end on the bundled globals: register, duplicate, epoch advance, stale rejection', async () => {
  const ledger = globalThis.PBLedger.createLedger({ now: () => Date.UTC(2026, 10, 11), sha256Hex, duplicateEventPolicy: 'event' });
  const epoch = globalThis.PBCapture.createEpochStore({});
  const session = globalThis.PBCapture.createCaptureSession({ ledger, epochStore: epoch, sha256Hex });
  const src = { form: 'native', platform: 'chatgpt', scope: 'conversation', conversation: 'c-1', messageId: 'm-1' };
  const a1 = await session.submitDetection({ handoffId: 'h1', source: src, admitted: true, epoch: epoch.current() });
  assert.strictEqual(a1.outcome, 'REGISTERED');
  const a2 = await session.submitDetection({ handoffId: 'h2', source: src, admitted: true, epoch: epoch.current() });
  assert.strictEqual(a2.outcome, 'DUPLICATE');
  assert.strictEqual(a2.indexId, a1.indexId);
  epoch.advance('pause');
  const stale = await session.submitDetection({ handoffId: 'h3', source: { ...src, messageId: 'm-2' }, admitted: true, epoch: 0 });
  assert.strictEqual(stale.outcome, 'STALE');
  assert.strictEqual(ledger.listByRegistrationOrder().length, 1);
});

test('the bundled migration inventory classifies a legacy state without touching it', async () => {
  const state = { detections: [{ envelope: { message_id: 'old-1', fingerprint: 'fp-1' } }], deliveredIds: ['old-9'], seen: [], log: [] };
  const before = JSON.parse(JSON.stringify(state));
  const inv = globalThis.PBMigration.inventoryLegacyState(state);
  assert.deepStrictEqual(state, before);
  assert.strictEqual(inv.entries.find((e) => e.legacyId === 'old-9').delivery, 'confirmed-delivered');
  assert.strictEqual(inv.entries.find((e) => e.legacyId === 'old-1').resendBlocked, true);
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
  console.log('\ndelivery.fixtures: ' + pass + '/' + tests.length + ' passed, ' + failures.length + ' failed');
  process.exitCode = failures.length ? 1 : 0;
})();
