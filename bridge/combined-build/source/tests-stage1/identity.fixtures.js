'use strict';
/*
 * Stage 1 — Batch 1 fixtures: PB-ID source-identity layer.
 *
 * Governing text: Stage 0 Pack Rev06 (as corrected by Rev07),
 * Gate 1 adopted rule SS1.3-SS1.5 and SS1.8, vectors SS1.7.
 * Build Plan 01 Stage 1, scope item 1 and Acceptance fixtures:
 * deterministic identity vectors; same-source re-fetch; identical
 * text with distinct occurrence; same text with no occurrence
 * discriminator; Unicode and whitespace canonicalisation; forced
 * digest-collision simulation.
 *
 * Run: node tests-stage1/identity.fixtures.js
 * Exit 0 = all pass. Per-test lines are printed; the count is the
 * report — no aggregate without the per-test lines.
 */
const assert = require('node:assert');
const crypto = require('node:crypto');
const path = require('node:path');

const identity = require(path.join(__dirname, '..', 'identity.js'));

const sha256Hex = (text) =>
  crypto.createHash('sha256').update(text, 'utf8').digest('hex');

const idn = identity.createIdentity({ sha256Hex });

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

/* ---- Published deterministic vectors (Pack SS1.7) ---- */

test('vector 1 (published): chatgpt native digest matches SS1.7', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: 'm-009',
  });
  assert.strictEqual(r.status, 'OK');
  assert.strictEqual(
    r.pbid,
    'pb1-5a3432bfe135f734c4a4befbd021f661fe7029f193bc14317e3a5f036fb93bac');
});

test('vector 1 (published): canonical preimage bytes are exact', async () => {
  const canonical = identity.canonicalSourceKey({
    platform: 'chatgpt', conversation: 'c-001', messageId: 'm-009',
  });
  assert.strictEqual(
    canonical,
    'PBID-SRC1\nplatform:7:chatgpt\nconversation:5:c-001\nmessage_id:5:m-009\n');
});

test('vector 2 (published): metaai native digest matches SS1.7 (algorithm example)', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'metaai', scope: 'conversation',
    conversation: 'prompt-123', messageId: 'turn-04',
  });
  assert.strictEqual(r.status, 'OK');
  assert.strictEqual(
    r.pbid,
    'pb1-139870e7642b68ec8ae2a0d2489a1e53bcab1b3fa70fe70745975763d2966698');
});

test('occurrence form: module digest equals independent node-crypto digest of hand-written preimage', async () => {
  const preimage =
    'PBID-OCC1\nplatform:4:muse\nconversation:5:cv-42\noccurrence:6:occ-99\n';
  const expected = 'pb1-' + sha256Hex(preimage);
  const r = await idn.deriveFromSourceKey({
    form: 'occurrence', platform: 'muse',
    conversation: 'cv-42', occurrence: 'occ-99',
  });
  assert.strictEqual(r.status, 'OK');
  assert.strictEqual(r.canonical, preimage);
  assert.strictEqual(r.pbid, expected);
});

/* ---- Determinism and occurrence distinction (SS1.5) ---- */

test('same source occurrence re-fetched derives the same PB-ID', async () => {
  const input = {
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: 'm-009',
  };
  const a = await idn.deriveFromSourceKey(input);
  const b = await idn.deriveFromSourceKey({ ...input });
  assert.strictEqual(a.status, 'OK');
  assert.strictEqual(a.pbid, b.pbid);
});

test('sender/body are not identity inputs: same source key with different body metadata, same PB-ID', async () => {
  const base = {
    form: 'native', platform: 'muse', scope: 'conversation',
    conversation: 'cv-1', messageId: 'mm-1',
  };
  const a = await idn.deriveFromSourceKey({ ...base, body: 'hello', sender: 'alex' });
  const b = await idn.deriveFromSourceKey({ ...base, body: 'HELLO EDITED', sender: 'remmy' });
  assert.strictEqual(a.status, 'OK');
  assert.strictEqual(a.pbid, b.pbid);
});

test('distinct occurrence IDs with identical sender/body derive different PB-IDs', async () => {
  const base = {
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', body: 'identical text', sender: 'alex',
  };
  const a = await idn.deriveFromSourceKey({ ...base, messageId: 'm-100' });
  const b = await idn.deriveFromSourceKey({ ...base, messageId: 'm-101' });
  assert.strictEqual(a.status, 'OK');
  assert.strictEqual(b.status, 'OK');
  assert.notStrictEqual(a.pbid, b.pbid);
});

test('same occurrence with edited payload keeps the same PB-ID (occurrence form)', async () => {
  const base = {
    form: 'occurrence', platform: 'muse', conversation: 'cv-7', occurrence: 'o-1',
  };
  const a = await idn.deriveFromSourceKey({ ...base, body: 'draft' });
  const b = await idn.deriveFromSourceKey({ ...base, body: 'draft, edited and grown' });
  assert.strictEqual(a.pbid, b.pbid);
});

/* ---- Fail-closed: IDENTITY-UNKNOWN (SS1.5) ---- */

test('conversation-scoped native ID with missing conversation is IDENTITY-UNKNOWN', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: null, messageId: 'm-009',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
});

test('globally scoped native ID with null conversation derives OK and encodes -1:', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'global',
    conversation: null, messageId: 'g-1',
  });
  assert.strictEqual(r.status, 'OK');
  assert.ok(r.canonical.includes('\nconversation:-1:\n'));
});

test('null conversation and empty conversation encode differently (-1: vs 0:) and derive different PB-IDs', async () => {
  const a = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'global',
    conversation: null, messageId: 'g-1',
  });
  const b = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'global',
    conversation: '', messageId: 'g-1',
  });
  assert.strictEqual(a.status, 'OK');
  assert.strictEqual(b.status, 'OK');
  assert.ok(b.canonical.includes('\nconversation:0:\n'));
  assert.notStrictEqual(a.pbid, b.pbid);
});

test('native form with no message ID is IDENTITY-UNKNOWN (no discriminator)', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: null, body: 'some text', sender: 'alex',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
});

test('native form with empty message ID is IDENTITY-UNKNOWN', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: '',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
});

test('occurrence form with missing occurrence discriminator is IDENTITY-UNKNOWN', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'occurrence', platform: 'muse', conversation: 'cv-1', occurrence: null,
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
});

test('occurrence form with missing conversation is IDENTITY-UNKNOWN', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'occurrence', platform: 'muse', conversation: null, occurrence: 'o-1',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
});

test('missing platform is IDENTITY-UNKNOWN', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: null, scope: 'global',
    conversation: null, messageId: 'g-1',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
});

test('hash service failure is IDENTITY-UNKNOWN, never a throw (fail-closed)', async () => {
  const broken = identity.createIdentity({
    sha256Hex: () => { throw new Error('hash unavailable'); },
  });
  const r = await broken.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: 'm-009',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
});

/* ---- Canonicalisation exactness: Unicode and whitespace (SS1.3) ---- */

test('UTF-8 byte lengths: precomposed e-acute counts 2 bytes', async () => {
  const canonical = identity.canonicalSourceKey({
    platform: 'muse', conversation: 'cv', messageId: 'é',
  });
  assert.ok(canonical.includes('\nmessage_id:2:é\n'));
});

test('no Unicode normalisation: decomposed e-acute counts 3 bytes and derives a different PB-ID', async () => {
  const a = await idn.deriveFromSourceKey({
    form: 'native', platform: 'muse', scope: 'conversation',
    conversation: 'cv', messageId: 'é',
  });
  const b = await idn.deriveFromSourceKey({
    form: 'native', platform: 'muse', scope: 'conversation',
    conversation: 'cv', messageId: 'é',
  });
  assert.ok(b.canonical.includes('\nmessage_id:3:é\n'));
  assert.notStrictEqual(a.pbid, b.pbid);
});

test('supplementary-plane character counts UTF-8 bytes (4), not UTF-16 units (2)', async () => {
  const canonical = identity.canonicalSourceKey({
    platform: 'muse', conversation: 'cv', messageId: '\u{1D11E}',
  });
  assert.ok(canonical.includes('\nmessage_id:4:\u{1D11E}\n'));
});

test('whitespace inside a value is preserved, never trimmed or collapsed', async () => {
  const a = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: 'm-009',
  });
  const b = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: ' m-009 ',
  });
  assert.ok(b.canonical.includes('\nmessage_id:7: m-009 \n'));
  assert.notStrictEqual(a.pbid, b.pbid);
});

test('delimiter-looking content inside a value cannot forge a field boundary', async () => {
  const a = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'x\nmessage_id:5:zzzzz', messageId: 'real',
  });
  const b = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'x', messageId: 'zzzzz\nmessage_id:4:real',
  });
  assert.strictEqual(a.status, 'OK');
  assert.strictEqual(b.status, 'OK');
  assert.notStrictEqual(a.pbid, b.pbid);
});

/* ---- Identity-claim record and collision policy (SS1.5) ---- */

test('claim store: first claim is CLAIMED, identical re-claim is MATCH', async () => {
  const store = identity.createClaimStore();
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: 'm-009',
  });
  assert.strictEqual(store.claim(r.pbid, r.canonical), 'CLAIMED');
  assert.strictEqual(store.claim(r.pbid, r.canonical), 'MATCH');
});

test('forced digest collision: a second, different source key at the same PB-ID is IDENTITY-COLLISION and never overwrites', async () => {
  const constant = identity.createIdentity({ sha256Hex: () => 'a'.repeat(64) });
  const a = await constant.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: 'm-001',
  });
  const b = await constant.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-002', messageId: 'm-002',
  });
  assert.strictEqual(a.pbid, b.pbid); // the forced collision itself
  const store = identity.createClaimStore();
  assert.strictEqual(store.claim(a.pbid, a.canonical), 'CLAIMED');
  assert.strictEqual(store.claim(b.pbid, b.canonical), 'IDENTITY-COLLISION');
  assert.strictEqual(store.get(a.pbid), a.canonical); // original retained
});

test('claim record retains canonical source-key material only — no body, no payload', async () => {
  const store = identity.createClaimStore();
  store.claim('pb1-test', 'PBID-SRC1\nplatform:7:chatgpt\n');
  const record = store.record('pb1-test');
  assert.deepStrictEqual(Object.keys(record).sort(), ['canonical', 'pbid']);
});

/* ---- Input contract: no coercion, no defaulting (Batch 1 review correction) ---- */

test('missing conversation FIELD (absent, not null) under global scope is IDENTITY-UNKNOWN', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'global', messageId: 'g-1',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
  assert.strictEqual(r.reason, 'conversation-missing');
});

test('explicit null conversation under global scope still derives OK (null is stated, not absent)', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'global',
    conversation: null, messageId: 'g-1',
  });
  assert.strictEqual(r.status, 'OK');
});

test('missing scope is IDENTITY-UNKNOWN — never silently defaulted', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt',
    conversation: 'c-001', messageId: 'm-009',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
  assert.strictEqual(r.reason, 'scope-invalid');
});

test('invalid scope values are IDENTITY-UNKNOWN (wrong case, non-string)', async () => {
  const a = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'GLOBAL',
    conversation: null, messageId: 'g-1',
  });
  const b = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 42,
    conversation: null, messageId: 'g-1',
  });
  assert.strictEqual(a.status, 'IDENTITY-UNKNOWN');
  assert.strictEqual(b.status, 'IDENTITY-UNKNOWN');
});

test('numeric message ID is rejected, never coerced to a string', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: 9009,
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
  assert.strictEqual(r.reason, 'message-id-invalid');
});

test('numeric platform is rejected, never coerced', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 7, scope: 'global',
    conversation: null, messageId: 'g-1',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
});

test('object conversation value is rejected, never coerced', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'global',
    conversation: { id: 'c-001' }, messageId: 'g-1',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
  assert.strictEqual(r.reason, 'conversation-invalid');
});

test('explicitly undefined message ID is IDENTITY-UNKNOWN', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: undefined,
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
});

test('occurrence form: missing conversation field is IDENTITY-UNKNOWN, distinct from a stated value', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'occurrence', platform: 'muse', occurrence: 'o-1',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
  assert.strictEqual(r.reason, 'conversation-missing');
});

test('canonical builder itself refuses coercion: numeric field value throws TypeError', async () => {
  assert.throws(
    () => identity.canonicalSourceKey({ platform: 'muse', conversation: 'cv', messageId: 5 }),
    TypeError);
});

test('canonical builder refuses a missing (undefined) field but accepts explicit null', async () => {
  assert.throws(
    () => identity.canonicalSourceKey({ platform: 'muse', messageId: 'm-1' }),
    TypeError);
  const ok = identity.canonicalSourceKey({ platform: 'muse', conversation: null, messageId: 'm-1' });
  assert.ok(ok.includes('\nconversation:-1:\n'));
});

test('claim store refuses a non-string canonical, never coerces it into the record', async () => {
  const store = identity.createClaimStore();
  assert.throws(() => store.claim('pb1-x', 42), TypeError);
  assert.strictEqual(store.get('pb1-x'), undefined);
});

test('claim store refuses a missing canonical and a non-string PB-ID', async () => {
  const store = identity.createClaimStore();
  assert.throws(() => store.claim('pb1-x', undefined), TypeError);
  assert.throws(() => store.claim(42, 'PBID-SRC1\n'), TypeError);
  assert.strictEqual(store.size(), 0);
});

/* ---- Reason classification: null is invalid, absent is missing (Rev2 review correction) ---- */

test('reason: explicit null platform is platform-invalid; absent platform is platform-missing', async () => {
  const a = await idn.deriveFromSourceKey({
    form: 'native', platform: null, scope: 'global',
    conversation: null, messageId: 'g-1',
  });
  const b = await idn.deriveFromSourceKey({
    form: 'native', scope: 'global', conversation: null, messageId: 'g-1',
  });
  assert.strictEqual(a.reason, 'platform-invalid');
  assert.strictEqual(b.reason, 'platform-missing');
});

test('reason: explicit null message ID is message-id-invalid; empty message ID is message-id-invalid', async () => {
  const a = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: null,
  });
  const b = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: 'c-001', messageId: '',
  });
  assert.strictEqual(a.reason, 'message-id-invalid');
  assert.strictEqual(b.reason, 'message-id-invalid');
});

test('reason: explicit null occurrence is occurrence-invalid; absent occurrence is occurrence-missing', async () => {
  const a = await idn.deriveFromSourceKey({
    form: 'occurrence', platform: 'muse', conversation: 'cv-1', occurrence: null,
  });
  const b = await idn.deriveFromSourceKey({
    form: 'occurrence', platform: 'muse', conversation: 'cv-1',
  });
  assert.strictEqual(a.reason, 'occurrence-invalid');
  assert.strictEqual(b.reason, 'occurrence-missing');
});

test('reason: explicit null conversation under conversation scope is conversation-invalid', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: null, messageId: 'm-009',
  });
  assert.strictEqual(r.status, 'IDENTITY-UNKNOWN');
  assert.strictEqual(r.reason, 'conversation-invalid');
});

test('reason: empty conversation under conversation scope is conversation-invalid', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'native', platform: 'chatgpt', scope: 'conversation',
    conversation: '', messageId: 'm-009',
  });
  assert.strictEqual(r.reason, 'conversation-invalid');
});

test('reason: explicit null conversation in occurrence form is conversation-invalid', async () => {
  const r = await idn.deriveFromSourceKey({
    form: 'occurrence', platform: 'muse', conversation: null, occurrence: 'o-1',
  });
  assert.strictEqual(r.reason, 'conversation-invalid');
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
  console.log(`\nidentity.fixtures: ${pass}/${tests.length} passed, ${failures.length} failed`);
  process.exit(failures.length === 0 ? 0 : 1);
})();
