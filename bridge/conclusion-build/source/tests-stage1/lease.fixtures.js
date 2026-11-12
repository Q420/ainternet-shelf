'use strict';
/*
 * Combined Build, Part B items 3+4 fixtures: the per-attempt
 * composer lease and the removal of the page-wide send-button
 * fallbacks, proven against the shared send core with DOM
 * stubs (the adapters' own copies of this logic are gone —
 * sendcore.js is the one place it lives).
 * Run: node tests-stage1/lease.fixtures.js
 */

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const S = require(path.join(__dirname, '..', 'sendcore.js'));

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

function btn(label, matchesSend) {
  return {
    getAttribute: (n) => (n === 'aria-label' ? label : null),
    matches: (s) => (s === '[data-send]' ? !!matchesSend : false),
  };
}
function scopeWith(buttons) {
  return { querySelectorAll: (sel) => (sel === 'button' ? buttons : []), querySelector: () => buttons[0] || null };
}
function composerIn(scope) {
  return { isConnected: true, closest: () => null, parentElement: scope };
}
function adapterFor(composer, scope) {
  return {
    name: 'stub',
    candidates: { send: ['[data-send]'], stop: [] },
    _engagedComposer: null,
    findComposer: () => composer,
  };
}

test('lease acquires against the exact composer instance and carries the attempt identity', () => {
  const scope = scopeWith([btn('Send', true)]);
  const composer = composerIn(scope);
  const ad = adapterFor(composer, scope);
  const acq = S.pbLeaseAcquire(ad, { pbId: 'pb-x', indexId: 'IDX-20261111-000001', attemptId: 'pb-x#a1' });
  assert.strictEqual(acq.ok, true);
  assert.strictEqual(acq.lease.composer, composer);
  assert.strictEqual(acq.lease.pbId, 'pb-x');
  assert.strictEqual(acq.lease.indexId, 'IDX-20261111-000001');
  assert.strictEqual(acq.lease.attemptId, 'pb-x#a1');
  assert.strictEqual(S.pbLeaseCheck(ad, 'before typing').ok, true);
  S.pbLeaseRelease();
});

test('no composer on the page: acquisition fails closed, stage lease', () => {
  const ad = { name: 'stub', candidates: { send: [], stop: [] }, _engagedComposer: null, findComposer: () => null };
  const acq = S.pbLeaseAcquire(ad, { pbId: 'pb-x' });
  assert.strictEqual(acq.ok, false);
  assert.strictEqual(acq.stage, 'lease');
});

test('composer instance swap breaks the lease — before typing AND in the defer', async () => {
  const scope = scopeWith([btn('Send', true)]);
  const c1 = composerIn(scope);
  const c2 = composerIn(scope);
  let current = c1;
  const ad = { name: 'stub', candidates: { send: ['[data-send]'], stop: [] }, _engagedComposer: null, findComposer: () => current };
  assert.strictEqual(S.pbLeaseAcquire(ad, { pbId: 'pb-y', attemptId: 'pb-y#a1' }).ok, true);
  current = c2; // the page replaced its composer (or focus moved to another one)
  const chk = S.pbLeaseCheck(ad, 'before typing');
  assert.strictEqual(chk.ok, false);
  assert.ok(/lease broken/.test(chk.error));
  const defer = await S.pbWaitForDestinationIdle(ad);
  assert.strictEqual(defer.ok, false);
  assert.strictEqual(defer.stage, 'lease');
  const fault = S.pbLeaseRelease();
  assert.ok(/lease broken/.test(fault));
  assert.strictEqual(S._lease, null);
});

test('pbFindSendButton finds the button inside the composer scope (by selector, then by name)', () => {
  const scope = scopeWith([btn('Send now', true)]);
  const ad = adapterFor(composerIn(scope), scope);
  assert.ok(S.pbFindSendButton(ad));
  const scope2 = scopeWith([btn('Send message', false)]);
  const ad2 = adapterFor(composerIn(scope2), scope2);
  assert.ok(S.pbFindSendButton(ad2), 'name match inside the scope still works');
});

test('page-wide fallback REMOVED: an empty composer scope yields no button, and no page search happens', () => {
  const scope = scopeWith([]);
  const ad = adapterFor(composerIn(scope), scope);
  // No `document` global exists in this process: the old code
  // would have thrown reaching for the page. The new code
  // answers actuator-unavailable (null) from the scope alone.
  assert.strictEqual(typeof document, 'undefined');
  assert.strictEqual(S.pbFindSendButton(ad), null);
  const src = fs.readFileSync(path.join(__dirname, '..', 'sendcore.js'), 'utf8');
  assert.ok(!src.includes('document.querySelectorAll("button")'), 'no all-buttons page search remains');
  assert.ok(!/for \(const s of adapter\.candidates\.send\) \{\s*const el = document\.querySelector/.test(src), 'no first-candidate document fallback remains');
});

test('under a lease, an engaged composer different from the leased instance yields no button and a named fault', () => {
  const scope = scopeWith([btn('Send', true)]);
  const leased = composerIn(scope);
  const other = composerIn(scope);
  const ad = adapterFor(leased, scope);
  assert.strictEqual(S.pbLeaseAcquire(ad, { pbId: 'pb-z', attemptId: 'pb-z#a2' }).ok, true);
  ad._engagedComposer = other; // the adapter engaged a different box than the lease bound
  assert.strictEqual(S.pbFindSendButton(ad), null);
  const fault = S.pbLeaseRelease();
  assert.ok(/different composer/.test(fault));
});

(async () => {
  let pass = 0; const failures = [];
  for (const t of tests) {
    try { await t.fn(); pass += 1; console.log('PASS  ' + t.name); }
    catch (e) { failures.push(t.name + ' :: ' + (e && e.message)); console.log('FAIL  ' + t.name + ' :: ' + (e && e.message)); }
  }
  console.log('\nlease.fixtures: ' + pass + '/' + tests.length + ' passed, ' + failures.length + ' failed');
  process.exit(failures.length ? 1 : 0);
})();
