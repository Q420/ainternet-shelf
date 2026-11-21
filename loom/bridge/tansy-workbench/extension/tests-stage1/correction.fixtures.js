'use strict';
/*
 * Combined Build Part A fixtures: Correction Basis streams
 * 1 + 3 (epoch lifecycle honesty) and the checked-import
 * regression addition. Token/stream-2 cases live with the
 * token work. Run: node tests-stage1/correction.fixtures.js
 */

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const { createEpochStore } = require(path.join(__dirname, '..', 'capture.js'));

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

/* ---- epoch store: history-preserving import ---- */

test('epoch export -> import restores the history whole, not just the number', () => {
  const a = createEpochStore({});
  a.advance('pause', 'pause:1');
  a.advance('disconnect', 'disconnect:2');
  const b = createEpochStore({});
  const imp = b.importState(a.exportState());
  assert.strictEqual(imp.status, 'OK');
  assert.strictEqual(b.current(), 2);
  const h = b.exportState().history;
  assert.strictEqual(h.length, 2);
  assert.strictEqual(h[0].reason, 'pause');
  assert.strictEqual(h[1].previousEpoch, 1);
});

test('import rejects a broken history chain and leaves the store untouched', () => {
  const s = createEpochStore({});
  s.advance('pause', 'pause:1');
  const imp = s.importState({ epoch: 2, history: [{ epoch: 2, previousEpoch: 0, reason: 'x' }] });
  assert.strictEqual(imp.status, 'REJECTED');
  assert.strictEqual(imp.reason, 'epoch-history-malformed');
  assert.strictEqual(s.current(), 1);
  assert.strictEqual(s.exportState().history.length, 1);
});

test('import rejects a history that does not end at the stated epoch', () => {
  const s = createEpochStore({});
  const imp = s.importState({ epoch: 3, history: [{ epoch: 1, previousEpoch: 0 }] });
  assert.strictEqual(imp.status, 'REJECTED');
  assert.strictEqual(imp.reason, 'epoch-history-mismatch');
  assert.strictEqual(s.current(), 0);
});

test('import still rejects rollback (an older epoch than the live one)', () => {
  const s = createEpochStore({});
  s.advance('pause', 'pause:1');
  const imp = s.importState({ epoch: 0, history: [] });
  assert.strictEqual(imp.status, 'REJECTED');
  assert.strictEqual(imp.reason, 'epoch-rollback');
});

/* ---- epoch store: idempotent transition identity ---- */

test('advance with the same transitionId advances exactly once (uncertain-save retry)', () => {
  const s = createEpochStore({});
  const first = s.advance('pause', 'pause:1');
  const retry = s.advance('pause', 'pause:1');
  assert.strictEqual(s.current(), 1);
  assert.strictEqual(first.alreadyApplied, undefined);
  assert.strictEqual(retry.alreadyApplied, true);
  assert.strictEqual(retry.epoch, 1);
  assert.strictEqual(s.exportState().history.length, 1);
});

test('advance with different transitionIds advances once each', () => {
  const s = createEpochStore({});
  s.advance('pause', 'pause:1');
  s.advance('disconnect', 'disconnect:2');
  assert.strictEqual(s.current(), 2);
});

/* ---- wiring: checked import + transition results + resume gate ---- */

const { createHash } = require('node:crypto');
async function sha256Hex(s) { return createHash('sha256').update(s, 'utf8').digest('hex'); }
void sha256Hex;

const tree = path.join(__dirname, '..');
globalThis.pbLog = () => {};
eval(fs.readFileSync(path.join(tree, 'stage1core.js'), 'utf8'));
const wiringCode = fs.readFileSync(path.join(tree, 'stage1-wiring.js'), 'utf8') +
  '\n;globalThis.__w = { pbStage1Ensure, pbStage1OnPauseOrDisconnect, pbStage1OnResume, pbStage1OnDetection, pbStage1TokenEnsure, pbStage1PreserveAcrossReset };';
eval(wiringCode);
const W = globalThis.__w;

function freshState() {
  return { registrations: {}, detections: [], runLog: [] };
}

test('wiring checks the epoch import result: a malformed epoch export raises the integrity fault', async () => {
  const state = freshState();
  state.stage1 = {
    revision: 0, ledgerExport: null, epochExport: { epoch: 'not-a-number' },
    migrationSummary: null, migrationStores: [], acks: [], integrityFault: false, unreconciled: null,
  };
  await W.pbStage1Ensure(state);
  assert.strictEqual(state.stage1.integrityFault, true);
});

test('wiring pause transition returns ADVANCED + verified and persists the new epoch', async () => {
  const state = freshState();
  const res = await W.pbStage1OnPauseOrDisconnect(state, 'pause');
  assert.strictEqual(res.status, 'ADVANCED');
  assert.strictEqual(res.verified, true);
  assert.strictEqual(state.stage1.epochExport.epoch, res.epoch);
  assert.strictEqual(state.stage1.epochExport.history.length, 1);
  assert.strictEqual(state.stage1.unreconciled, null);
});

test('resume gate: CLEAR with nothing outstanding', async () => {
  const state = freshState();
  await W.pbStage1Ensure(state);
  const res = await W.pbStage1OnResume(state);
  assert.strictEqual(res.status, 'CLEAR');
});

test('resume gate: a recorded unreconciled transition reconciles against a verified save', async () => {
  const state = freshState();
  await W.pbStage1OnPauseOrDisconnect(state, 'pause');
  state.stage1.unreconciled = { kind: 'epoch-transition', why: 'pause', transitionId: 'pause:1', at: new Date().toISOString(), detail: 'simulated' };
  const res = await W.pbStage1OnResume(state);
  assert.strictEqual(res.status, 'RECONCILED');
  assert.strictEqual(state.stage1.unreconciled, null);
});

test('resume gate: an unreconciled condition of an unknown kind keeps resume UNRECONCILED', async () => {
  const state = freshState();
  await W.pbStage1Ensure(state);
  state.stage1.unreconciled = { kind: 'something-unforeseen', at: new Date().toISOString(), detail: 'simulated' };
  const res = await W.pbStage1OnResume(state);
  assert.strictEqual(res.status, 'UNRECONCILED');
  assert.ok(state.stage1.unreconciled);
});

/* ---- detection tokens (D1), one shared bridge state ---- */

const tstate = freshState();
tstate.registrations = { remmy: { platform: 'claude' }, alex: { platform: 'chatgpt' } };
let snap1 = null;
let snap2 = null;

test('token: ensure issues a record bound to seat, tab and epoch; the same binding is stable', async () => {
  const a = await W.pbStage1TokenEnsure(tstate, 'remmy', 42);
  assert.strictEqual(a.changed, true);
  assert.strictEqual(a.record.generation, 1);
  assert.strictEqual(a.record.tabId, 42);
  snap1 = { token: a.record.token, generation: a.record.generation, epoch: a.record.epoch, tabId: a.record.tabId };
  const b = await W.pbStage1TokenEnsure(tstate, 'remmy', 42);
  assert.strictEqual(b.changed, false);
  assert.strictEqual(b.record.token, snap1.token);
});

test('token: admission accepts a candidate whose snapshot matches the authoritative record', async () => {
  const ack = await W.pbStage1OnDetection(tstate, { message_id: 'tok-ok-1', from: 'remmy', tokenSnapshot: snap1 }, 42);
  assert.notStrictEqual(ack.outcome, 'STALE');
});

test('token: admission rejects a tokenless detection (no tokenless path)', async () => {
  const ack = await W.pbStage1OnDetection(tstate, { message_id: 'tok-none-1', from: 'remmy' }, 42);
  assert.strictEqual(ack.outcome, 'STALE');
  assert.strictEqual(ack.reason, 'token-missing');
});

test('token: REGRESSION — a candidate snapshotted before a pause is rejected when handed off after it', async () => {
  await W.pbStage1OnPauseOrDisconnect(tstate, 'pause');
  const ack = await W.pbStage1OnDetection(tstate, { message_id: 'tok-pre-pause', from: 'remmy', tokenSnapshot: snap1 }, 42);
  assert.strictEqual(ack.outcome, 'STALE');
  assert.strictEqual(ack.reason, 'epoch-stale');
});

test('token: handoff cannot refresh — an old token dressed in the new epoch is still rejected', async () => {
  const r = await W.pbStage1TokenEnsure(tstate, 'remmy', 42);
  assert.strictEqual(r.changed, true);
  snap2 = { token: r.record.token, generation: r.record.generation, epoch: r.record.epoch, tabId: r.record.tabId };
  const forged = { token: snap1.token, generation: snap1.generation, epoch: snap2.epoch, tabId: 42 };
  const ack = await W.pbStage1OnDetection(tstate, { message_id: 'tok-forged', from: 'remmy', tokenSnapshot: forged }, 42);
  assert.strictEqual(ack.outcome, 'STALE');
  assert.strictEqual(ack.reason, 'token-rotated');
});

test('token: admission rejects a snapshot arriving from a different tab than its binding', async () => {
  const ack = await W.pbStage1OnDetection(tstate, { message_id: 'tok-wrong-tab', from: 'remmy', tokenSnapshot: snap2 }, 999);
  assert.strictEqual(ack.outcome, 'STALE');
  assert.strictEqual(ack.reason, 'token-sender-mismatch');
});

test('token: restart recovery — the persisted record is recovered, not re-minted', async () => {
  const copy = JSON.parse(JSON.stringify(tstate));
  const r = await W.pbStage1TokenEnsure(copy, 'remmy', 42);
  assert.strictEqual(r.changed, false);
  assert.strictEqual(r.record.token, snap2.token);
});

test('token: restart unverifiable — a malformed persisted record is discarded at load and the seat re-issues clean', async () => {
  const copy = JSON.parse(JSON.stringify(tstate));
  copy.stage1.tokens.remmy = { token: 5 };
  copy.stage1.revision = 9999; // force rehydration, as a fresh worker would do
  await W.pbStage1Ensure(copy);
  assert.strictEqual(copy.stage1.integrityFault, true);
  assert.strictEqual(copy.stage1.tokens.remmy, undefined);
  const r = await W.pbStage1TokenEnsure(copy, 'remmy', 42);
  assert.strictEqual(r.changed, true);
  assert.strictEqual(r.record.generation, 1);
});


test('token: a current-generation token is reusable — a second candidate with the same snapshot is admitted', async () => {
  const ack = await W.pbStage1OnDetection(tstate, { message_id: 'tok-ok-2', from: 'remmy', tokenSnapshot: snap2 }, 42);
  assert.notStrictEqual(ack.outcome, 'STALE');
});


test('reset preservation (Part A item 8): the permanent record survives reset, tokens are revoked', async () => {
  const before = JSON.parse(JSON.stringify(tstate));
  const fresh = { registrations: {}, detections: [], runLog: [] };
  const kept = W.pbStage1PreserveAcrossReset(before, fresh);
  assert.strictEqual(kept, true);
  assert.deepStrictEqual(fresh.stage1.ledgerExport, before.stage1.ledgerExport);
  assert.deepStrictEqual(fresh.stage1.epochExport, before.stage1.epochExport);
  assert.strictEqual(fresh.stage1.epochExport.history.length, before.stage1.epochExport.history.length);
  assert.deepStrictEqual(fresh.stage1.acks, before.stage1.acks);
  assert.deepStrictEqual(fresh.stage1.tokens, {});
  const ack = await W.pbStage1OnDetection(fresh, { message_id: 'tok-after-reset', from: 'remmy', tokenSnapshot: snap2 }, 42);
  assert.strictEqual(ack.outcome, 'STALE');
  assert.strictEqual(ack.reason, 'token-unissued');
});

(async () => {
  let pass = 0; const failures = [];
  for (const t of tests) {
    try { await t.fn(); pass += 1; console.log('PASS  ' + t.name); }
    catch (e) { failures.push(t.name + ' :: ' + (e && e.message)); console.log('FAIL  ' + t.name + ' :: ' + (e && e.message)); }
  }
  console.log('\ncorrection.fixtures: ' + pass + '/' + tests.length + ' passed, ' + failures.length + ' failed');
  process.exit(failures.length ? 1 : 0);
})();
