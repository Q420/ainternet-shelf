'use strict';
/*
 * Combined Build, Part B item 5 fixtures: the FINAL F-5
 * verdict matrix (Ben's ruling, Stage 0 Pack SS2.5; Build
 * Plan 01 SS4 item 5), exercised over all 27 condition
 * combinations, plus the named cases in Ben's own terms.
 * Run: node tests-stage1/fence.fixtures.js
 */

const assert = require('node:assert');
const path = require('node:path');
const F = require(path.join(__dirname, '..', 'fence.js'));

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

/* The spec, restated independently of the implementation:
 * - serial or status NEGATIVE = proven refusal -> hold.
 * - button NEGATIVE + serial POSITIVE + status POSITIVE
 *   = logic-fault.
 * - button NEGATIVE otherwise = hold (the gate's hold).
 * - no negatives: >= 2 positives = send; else hold. */
function specAction(c) {
  if (c.serial === 'negative' || c.status === 'negative') return 'hold';
  if (c.button === 'negative') {
    return (c.serial === 'positive' && c.status === 'positive') ? 'logic-fault' : 'hold';
  }
  const pos = [c.button, c.serial, c.status].filter((v) => v === 'positive').length;
  return pos >= 2 ? 'send' : 'hold';
}

test('all 27 condition combinations follow the final F-5 spec', () => {
  const vals = ['positive', 'negative', 'unknown'];
  let n = 0;
  for (const button of vals) for (const serial of vals) for (const status of vals) {
    const conds = { button, serial, status };
    const v = F.pbFenceVerdict(conds);
    assert.strictEqual(v.action, specAction(conds), JSON.stringify(conds) + ' -> ' + v.action);
    n++;
  }
  assert.strictEqual(n, 27);
});

test("Ben's case: UNKNOWN button + positive serial + positive status PROCEEDS", () => {
  const v = F.pbFenceVerdict({ button: 'unknown', serial: 'positive', status: 'positive' });
  assert.strictEqual(v.action, 'send');
});

test("Ben's case: NEGATIVE button + two positives is LOGIC-FAULT, no send", () => {
  const v = F.pbFenceVerdict({ button: 'negative', serial: 'positive', status: 'positive' });
  assert.strictEqual(v.action, 'logic-fault');
  assert.strictEqual(v.vetoName, 1);
});

test("Ben's case: NEGATIVE button with either other state non-positive is HOLD, not a fault", () => {
  for (const conds of [
    { button: 'negative', serial: 'positive', status: 'unknown' },
    { button: 'negative', serial: 'unknown', status: 'positive' },
    { button: 'negative', serial: 'unknown', status: 'unknown' },
  ]) {
    const v = F.pbFenceVerdict(conds);
    assert.strictEqual(v.action, 'hold', JSON.stringify(conds));
    assert.strictEqual(v.veto, 'button');
  }
});

test('already-delivered (status NEGATIVE) never sends — and is a refusal, not a logic fault', () => {
  const v = F.pbFenceVerdict({ button: 'positive', serial: 'positive', status: 'negative' });
  assert.strictEqual(v.action, 'hold');
  assert.strictEqual(v.refusal, 'status');
});

test('out-of-order (serial NEGATIVE) never sends, even beside a proven-negative button', () => {
  const v = F.pbFenceVerdict({ button: 'negative', serial: 'negative', status: 'positive' });
  assert.strictEqual(v.action, 'hold');
  assert.strictEqual(v.refusal, 'serial');
});

test('insufficient evidence holds: a single positive is never a quorum', () => {
  for (const conds of [
    { button: 'positive', serial: 'unknown', status: 'unknown' },
    { button: 'unknown', serial: 'positive', status: 'unknown' },
    { button: 'unknown', serial: 'unknown', status: 'unknown' },
  ]) {
    assert.strictEqual(F.pbFenceVerdict(conds).action, 'hold', JSON.stringify(conds));
  }
});

test('the two clocks stay distinct: fence recheck is 20s; the adapter defer bound is 45s', () => {
  assert.strictEqual(F.PB_FENCE_RECHECK_MS, 20000);
  const sendcore = require('node:fs').readFileSync(path.join(__dirname, '..', 'sendcore.js'), 'utf8');
  assert.ok(sendcore.includes('45000'), 'sendcore defer bound present');
  assert.ok(sendcore.includes('PB_DEFER_REPORT'), 'defer progress reporting present');
});

test('button condition vocabulary: generating is the only proven negative; unreadable is UNKNOWN', () => {
  assert.strictEqual(F.pbFenceButtonCondition('generating'), 'negative');
  assert.strictEqual(F.pbFenceButtonCondition('ready'), 'positive');
  assert.strictEqual(F.pbFenceButtonCondition('unknown'), 'unknown');
  assert.strictEqual(F.pbFenceButtonCondition(undefined), 'unknown');
  assert.strictEqual(F.pbFenceButtonCondition('anything-else'), 'unknown');
});

(async () => {
  let pass = 0; const failures = [];
  for (const t of tests) {
    try { await t.fn(); pass += 1; console.log('PASS  ' + t.name); }
    catch (e) { failures.push(t.name + ' :: ' + (e && e.message)); console.log('FAIL  ' + t.name + ' :: ' + (e && e.message)); }
  }
  console.log('\nfence.fixtures: ' + pass + '/' + tests.length + ' passed, ' + failures.length + ' failed');
  process.exit(failures.length ? 1 : 0);
})();
