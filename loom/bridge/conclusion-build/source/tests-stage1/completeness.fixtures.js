'use strict';
/*
 * Combined Build, Part B item 1 fixtures: the F-6 completeness
 * contract (Stage 0 Pack SS2.2 definitions, adopted under
 * delegation) + Gate 4 Option A append serialization.
 * Run: node tests-stage1/completeness.fixtures.js
 */

const assert = require('node:assert');
const path = require('node:path');
const { createHash } = require('node:crypto');

async function sha256Hex(s) { return createHash('sha256').update(s, 'utf8').digest('hex'); }

const PBComplete = require(path.join(__dirname, '..', 'completeness.js'));
const PB = require(path.join(__dirname, '..', 'protocol.js'));
const C = PBComplete.createCompleteness({ sha256Hex });

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

const FILE_BLOCK = ['[PB-FILE: notes.txt sha256=' + 'a'.repeat(64) + ' bytes=5]', 'hello', '[PB-FILE-END]'].join('\n');

test('chars: Unicode scalar values — an astral character counts as one', async () => {
  const a = await C.analyse('ab\u{1F600}c');
  assert.strictEqual(a.ok, true);
  assert.strictEqual(a.chars, 4);
});

test('chars: an unpaired surrogate is MALFORMED, never silently replaced', async () => {
  const a = await C.analyse('bad \uD800 text');
  assert.strictEqual(a.ok, false);
  assert.strictEqual(a.reason, 'unpaired-surrogate');
});

test('blocks: plain multi-paragraph text is exactly one TEXT block', async () => {
  const a = await C.analyse('para one\n\npara two\n\n\npara three');
  assert.strictEqual(a.blocks, 1);
});

test('blocks: text + one PB-FILE block is two blocks; file alone is one', async () => {
  const both = await C.analyse('see attached\n' + FILE_BLOCK);
  assert.strictEqual(both.blocks, 2);
  const alone = await C.analyse(FILE_BLOCK);
  assert.strictEqual(alone.blocks, 1);
});

test('blocks: multiple or incomplete PB-FILE structure is MALFORMED, never guessed', async () => {
  const two = await C.analyse(FILE_BLOCK + '\n' + FILE_BLOCK);
  assert.strictEqual(two.ok, false);
  const noEnd = await C.analyse('[PB-FILE: x.txt sha256=' + 'b'.repeat(64) + ' bytes=1]\norphan');
  assert.strictEqual(noEnd.ok, false);
  assert.strictEqual(noEnd.reason, 'file-block-incomplete');
});

test('trailer round-trip: serialize -> verify is COMPLETE with the exact payload', async () => {
  const payload = 'Line one.\nLine two, with \u{1F600} flair.';
  const s = await C.serialize(payload);
  assert.strictEqual(s.ok, true);
  const v = await C.verify(s.text);
  assert.strictEqual(v.status, 'COMPLETE');
  assert.strictEqual(v.payload, payload);
});

test('payload trailing newlines are payload, not framing: they survive the round-trip', async () => {
  const payload = 'ends with newline\n';
  const s = await C.serialize(payload);
  const v = await C.verify(s.text);
  assert.strictEqual(v.status, 'COMPLETE');
  assert.strictEqual(v.payload, payload);
});

test('a truncated copy is INCOMPLETE (quarantine), never COMPLETE', async () => {
  const s = await C.serialize('the whole letter, every word of it');
  const cut = s.text.slice(0, s.text.indexOf('every')) + s.text.slice(s.text.indexOf('\nPB-COMPLETE'));
  const v = await C.verify(cut);
  assert.strictEqual(v.status, 'INCOMPLETE');
});

test('grammar strictness: uppercase digest, leading zeros, duplicated trailer are MALFORMED', async () => {
  const s = await C.serialize('strict');
  const upper = await C.verify(s.text.replace(/sha256=([0-9a-f]{10})/, (m, p) => 'sha256=' + p.toUpperCase()));
  assert.strictEqual(upper.status, 'MALFORMED');
  const zeros = await C.verify(s.text.replace('chars=6', 'chars=06'));
  assert.strictEqual(zeros.status, 'MALFORMED');
  assert.strictEqual(zeros.reason, 'leading-zero-ambiguity');
  const dup = await C.verify(s.text + '\n' + s.text.split('\n').pop());
  assert.strictEqual(dup.status, 'MALFORMED');
  assert.strictEqual(dup.reason, 'trailer-duplicated');
});

test('register: incomplete quarantines, a later complete copy REPAIRS, identical re-arrival is ALREADY_COMPLETE', async () => {
  const reg = PBComplete.createCompletenessRegister();
  const payload = 'repair me, whole';
  const whole = await C.serialize(payload);
  const partial = payload.slice(0, 6) + whole.text.slice(whole.text.indexOf('\nPB-COMPLETE'));
  const r1 = await reg.submit('pb-test-1', partial, C);
  assert.strictEqual(r1.status, 'INCOMPLETE');
  assert.strictEqual(reg.isQuarantined('pb-test-1'), true);
  const r2 = await reg.submit('pb-test-1', whole.text, C);
  assert.strictEqual(r2.status, 'REPAIRED');
  assert.strictEqual(reg.isComplete('pb-test-1'), true);
  const r3 = await reg.submit('pb-test-1', whole.text, C);
  assert.strictEqual(r3.status, 'ALREADY_COMPLETE');
});

test('register: a divergent COMPLETE payload under a completed PB-ID is CONFLICT, and the held payload stands', async () => {
  const reg = PBComplete.createCompletenessRegister();
  const a = await C.serialize('the original words');
  const b = await C.serialize('different words entirely');
  await reg.submit('pb-test-2', a.text, C);
  const r = await reg.submit('pb-test-2', b.text, C);
  assert.strictEqual(r.status, 'CONFLICT');
  assert.strictEqual(reg.completedPayload('pb-test-2'), 'the original words');
});

test('append (Gate 4 Option A): composite splits back to the exact original and segment', async () => {
  const original = 'the seat\u2019s words, unchanged';
  const seg = 'Ben adds: ship it \u{1F600}';
  const ap = await C.appendSegment(original, seg);
  assert.strictEqual(ap.ok, true);
  const sp = await C.splitAppend(ap.composite);
  assert.strictEqual(sp.ok, true);
  assert.strictEqual(sp.appended, true);
  assert.strictEqual(sp.original, original);
  assert.strictEqual(sp.segment, seg);
});

test('append: an all-whitespace segment is rejected as empty, never rewritten', async () => {
  const ap = await C.appendSegment('payload', '   \n  ');
  assert.strictEqual(ap.ok, false);
  assert.strictEqual(ap.reason, 'append-segment-empty');
});

test('append: the composite takes the F-6 trailer as a whole and verifies COMPLETE', async () => {
  const ap = await C.appendSegment('original body', 'ben segment');
  const s = await C.serialize(ap.composite);
  const v = await C.verify(s.text);
  assert.strictEqual(v.status, 'COMPLETE');
  assert.strictEqual(v.payload, ap.composite);
});

test('append: a second PB-APPEND header is ambiguous and rejected, never guessed', async () => {
  const ap = await C.appendSegment('body', 'one');
  const doubled = ap.composite + '\nPB-APPEND/1 actor=ben bytes=3 sha256=' + 'c'.repeat(64) + '\ntwo';
  const sp = await C.splitAppend(doubled);
  assert.strictEqual(sp.ok, false);
  assert.strictEqual(sp.reason, 'append-header-ambiguous');
});


test('append: the segment is preserved byte-for-byte, including leading/trailing whitespace (Gate 4 SS4.4)', async () => {
  const seg = '  keep my  spaces  \n';
  const ap = await C.appendSegment('original', seg);
  assert.strictEqual(ap.ok, true);
  const sp = await C.splitAppend(ap.composite);
  assert.strictEqual(sp.segment, seg);
});


test('dispatch round-trip: the sealed body verifies COMPLETE; a false seal reads INCOMPLETE', async () => {
  const ser = await C.serialize('the body of the letter');
  assert.strictEqual(ser.ok, true);
  const v = await C.verify(ser.text);
  assert.strictEqual(v.status, 'COMPLETE');
  assert.strictEqual(v.payload, 'the body of the letter');
  const tampered = ser.text.replace('body', 'BODY');
  assert.strictEqual((await C.verify(tampered)).status, 'INCOMPLETE');
  const bad = await C.serialize('text\n[PB-FILE: x.txt sha256=abc bytes=3]\ncontent with no end line');
  assert.strictEqual(bad.ok, false);
  assert.strictEqual(bad.reason, 'file-block-incomplete');
});

(async () => {
  let pass = 0; const failures = [];
  for (const t of tests) {
    try { await t.fn(); pass += 1; console.log('PASS  ' + t.name); }
    catch (e) { failures.push(t.name + ' :: ' + (e && e.message)); console.log('FAIL  ' + t.name + ' :: ' + (e && e.message)); }
  }
  console.log('\ncompleteness.fixtures: ' + pass + '/' + tests.length + ' passed, ' + failures.length + ' failed');
  process.exit(failures.length ? 1 : 0);
})();
