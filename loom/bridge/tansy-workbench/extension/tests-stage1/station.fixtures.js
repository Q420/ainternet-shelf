'use strict';
/*
 * Combined Build, Part C fixtures: the station core state
 * machine — serial append windows, push-through, cancel at
 * the dispatch boundary (Amendment 01 item 6's four cases),
 * the PB-FILE exclusion, and the dispatch handshake mapping.
 * Run: node tests-stage1/station.fixtures.js
 */

const assert = require('node:assert');
const path = require('node:path');
const S = require(path.join(__dirname, '..', 'station.js'));

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }
const item = (pbId, body) => ({ pbId, indexId: 'IDX-20261111-000001', from: 'remmy', to: 'alex', body: body || 'a letter' });

test('the first item is HELD with a 7,500 ms window; the second QUEUES with no window started', () => {
  const st = S.pbStationDefault();
  assert.strictEqual(S.pbStationEnter(st, item('pb-1'), 1000).face, 'HELD');
  assert.strictEqual(st.current.windowExpiresAt, 1000 + 7500);
  assert.strictEqual(S.pbStationEnter(st, item('pb-2'), 1100).face, 'QUEUED');
  assert.strictEqual(st.queue[0].windowOpensAt, null);
});

test('window expiry RELEASES the held item; the pump takes it and the queued item starts a FRESH window', () => {
  const st = S.pbStationDefault();
  S.pbStationEnter(st, item('pb-1'), 0);
  S.pbStationEnter(st, item('pb-2'), 10);
  assert.strictEqual(S.pbStationTick(st, 7499).released, null);
  assert.strictEqual(S.pbStationTick(st, 7500).released, 'pb-1');
  const took = S.pbStationTake(st, 'pb-1', 7600);
  assert.strictEqual(took.took, true);
  assert.strictEqual(took.item.face, 'ATTEMPTING'); // a persisted pre-click attempt is NOT dispatch (Alex SS4)
  assert.strictEqual(st.current.pbId, 'pb-2');
  assert.strictEqual(st.current.windowOpensAt, 7600);
  assert.strictEqual(st.current.windowExpiresAt, 7600 + 7500);
});

test('push-through releases a HELD item immediately and marks it; a queued item cannot be pushed', () => {
  const st = S.pbStationDefault();
  S.pbStationEnter(st, item('pb-1'), 0);
  S.pbStationEnter(st, item('pb-2'), 10);
  assert.strictEqual(S.pbStationPushThrough(st, 'pb-2').ok, false);
  const r = S.pbStationPushThrough(st, 'pb-1');
  assert.strictEqual(r.ok, true);
  assert.strictEqual(st.current.face, 'RELEASED');
  assert.strictEqual(st.current.pushedThrough, true);
});

test('cancel case 1 — before submit: a HELD item is cancelled, recorded, and the queue promotes', () => {
  const st = S.pbStationDefault();
  S.pbStationEnter(st, item('pb-1'), 0);
  S.pbStationEnter(st, item('pb-2'), 10);
  const r = S.pbStationCancel(st, 'pb-1', 500);
  assert.strictEqual(r.cancelled, true);
  assert.strictEqual(st.lastOutcome.outcome, 'CANCELLED');
  assert.strictEqual(st.current.pbId, 'pb-2');
  assert.strictEqual(st.current.face, 'HELD');
});

test('cancel case 2 — the race: cancel after release is too late and reports the true face', () => {
  const st = S.pbStationDefault();
  S.pbStationEnter(st, item('pb-1'), 0);
  S.pbStationPushThrough(st, 'pb-1');
  const r = S.pbStationCancel(st, 'pb-1', 600);
  assert.strictEqual(r.cancelled, false);
  assert.strictEqual(r.reason, 'too-late');
  assert.strictEqual(r.face, 'RELEASED');
  assert.strictEqual(st.current.pbId, 'pb-1'); // still there, undispatched, honestly faced
});

test('cancel case 3 — duplicate cancel is a no-op, not an error', () => {
  const st = S.pbStationDefault();
  S.pbStationEnter(st, item('pb-1'), 0);
  assert.strictEqual(S.pbStationCancel(st, 'pb-1', 100).cancelled, true);
  const again = S.pbStationCancel(st, 'pb-1', 200);
  assert.strictEqual(again.cancelled, false);
  assert.strictEqual(again.reason, 'not-found');
});

test('cancel case 4 — a QUEUED item can be cancelled in place', () => {
  const st = S.pbStationDefault();
  S.pbStationEnter(st, item('pb-1'), 0);
  S.pbStationEnter(st, item('pb-2'), 10);
  const r = S.pbStationCancel(st, 'pb-2', 300);
  assert.strictEqual(r.cancelled, true);
  assert.strictEqual(r.was, 'QUEUED');
  assert.strictEqual(st.queue.length, 0);
  assert.strictEqual(st.current.pbId, 'pb-1');
});

test('PB-FILE payloads never enter the station (separate channel)', () => {
  const st = S.pbStationDefault();
  const body = 'see attached\n[PB-FILE: data.txt sha256=abc bytes=3]\nxyz\n[PB-FILE-END]';
  const r = S.pbStationEnter(st, item('pb-f', body), 0);
  assert.strictEqual(r.entered, false);
  assert.strictEqual(r.reason, 'pb-file-channel');
  assert.strictEqual(st.current, null);
});

test('handshake mapping: delivered, late, unconfirmed, failed-before-send', () => {
  assert.strictEqual(S.pbStationHandshake({ crusherState: 'ACKNOWLEDGED' }), 'DELIVERED');
  assert.strictEqual(S.pbStationHandshake({ crusherState: 'ACKNOWLEDGED', wasUnconfirmed: true }), 'DELIVERED-LATE');
  assert.strictEqual(S.pbStationHandshake({ crusherState: 'UNVERIFIED' }), 'SENT-UNCONFIRMED');
  assert.strictEqual(S.pbStationHandshake({ crusherState: 'DELIVERING' }), 'ATTEMPTING');
  assert.strictEqual(S.pbStationHandshake({ crusherState: 'DELIVERING', submitted: true }), 'TRANSIT');
  assert.strictEqual(S.pbStationHandshake({ crusherState: 'FAILED', stage: 'lease' }), 'FAILED-BEFORE-SEND');
  assert.strictEqual(S.pbStationHandshake({ crusherState: 'FAILED', stage: 'generating' }), 'FAILED-BEFORE-SEND');
  assert.strictEqual(S.pbStationHandshake({ crusherState: 'FAILED', stage: 'confirm' }), 'SENT-UNCONFIRMED');
});


test('append pauses the timer: the window cannot expire while Ben writes, and resumes with its remaining span', () => {
  const st = S.pbStationDefault();
  S.pbStationEnter(st, item('pb-1'), 0);
  const opened = S.pbStationAppendOpen(st, 'pb-1', 5000);
  assert.strictEqual(opened.ok, true);
  assert.strictEqual(opened.remainingMs, 2500);
  assert.strictEqual(S.pbStationTick(st, 99999).released, null); // long past the original expiry — still held
  assert.strictEqual(st.current.face, 'HELD');
  const closed = S.pbStationAppendClose(st, 'pb-1', 100000);
  assert.strictEqual(closed.ok, true);
  assert.strictEqual(closed.windowExpiresAt, 102500); // resumed, not reset
  assert.strictEqual(S.pbStationTick(st, 102500).released, 'pb-1');
});

(async () => {
  let pass = 0; const failures = [];
  for (const t of tests) {
    try { await t.fn(); pass += 1; console.log('PASS  ' + t.name); }
    catch (e) { failures.push(t.name + ' :: ' + (e && e.message)); console.log('FAIL  ' + t.name + ' :: ' + (e && e.message)); }
  }
  console.log('\nstation.fixtures: ' + pass + '/' + tests.length + ' passed, ' + failures.length + ' failed');
  process.exit(failures.length ? 1 : 0);
})();
