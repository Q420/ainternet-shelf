'use strict';
/*
 * Conclusion Build (v0.22.0) fixtures: the retained-handle
 * store, the Part 4 re-look schedule + matcher, the Part 1
 * face words + wording sweep, and the Part 2 acknowledged
 * handoff machine in the letterbox (answer classes, bounded
 * retry, marking only after acceptance, cap-eviction reports).
 * Run: node tests-stage1/conclusion.fixtures.js
 */

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const H = require(path.join(__dirname, '..', 'handles.js'));
global.PB = require(path.join(__dirname, '..', 'protocol.js'));
const PB = global.PB;
const LB = require(path.join(__dirname, '..', 'letterbox.js'));

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ISO = (ms) => new Date(ms).toISOString();
const det = (id, state, body) => ({
  envelope: { message_id: id, from: 'remmy', to: 'alex', body: body || ('body of ' + id), fingerprint: 'fp-' + id },
  crusher: { state },
  at: ISO(0),
});

/* ---------- handles: creation ---------- */

test('a handle is left only by a completed letter: ACKNOWLEDGED and UNVERIFIED qualify; FAILED, ABANDONED, STALLED and crusher-less records do not', () => {
  assert.ok(H.pbHandleFromDetection(det('a', 'ACKNOWLEDGED'), ISO(1000)));
  assert.ok(H.pbHandleFromDetection(det('b', 'UNVERIFIED'), ISO(1000)));
  assert.strictEqual(H.pbHandleFromDetection(det('c', 'FAILED'), ISO(1000)), null);
  assert.strictEqual(H.pbHandleFromDetection(det('d', 'ABANDONED'), ISO(1000)), null);
  assert.strictEqual(H.pbHandleFromDetection(det('e', 'STALLED'), ISO(1000)), null);
  assert.strictEqual(H.pbHandleFromDetection({ envelope: { message_id: 'f' } }, ISO(1000)), null);
});

test('an UNVERIFIED handle carries a re-look armed at close + 60 s; an ACKNOWLEDGED handle carries none', () => {
  const hu = H.pbHandleFromDetection(det('u', 'UNVERIFIED'), ISO(60000));
  assert.strictEqual(hu.relook.nextAt, 120000);
  assert.strictEqual(hu.relook.done, false);
  assert.strictEqual(hu.closeState, 'UNVERIFIED');
  const ha = H.pbHandleFromDetection(det('a', 'ACKNOWLEDGED'), ISO(60000));
  assert.strictEqual(ha.relook, null);
});

/* ---------- handles: consult + capacity ---------- */

test('the intake consult finds a completed letter by envelope id and by body fingerprint under a fresh id (the re-render shape)', () => {
  const st = {};
  H.pbHandlesRecord(st, H.pbHandleFromDetection(det('m1', 'ACKNOWLEDGED'), ISO(0)));
  assert.strictEqual(H.pbHandleConsult(st, { message_id: 'm1', fingerprint: 'other' }).message_id, 'm1');
  assert.strictEqual(H.pbHandleConsult(st, { message_id: 'fresh-id', fingerprint: 'fp-m1' }).message_id, 'm1');
  assert.strictEqual(H.pbHandleConsult(st, { message_id: 'nope', fingerprint: 'fp-nope' }), null);
  assert.strictEqual(H.pbHandleBySupersedes(st, 'fp-m1').message_id, 'm1');
});

test('the store is bounded at the cap and eviction returns the evicted ids, oldest first, so the caller can log them', () => {
  const st = {};
  let lastEvicted = [];
  for (let i = 0; i < H.PB_HANDLE_CAP + 2; i++) {
    lastEvicted = H.pbHandlesRecord(st, H.pbHandleFromDetection(det('h' + i, 'ACKNOWLEDGED'), ISO(i)));
  }
  assert.strictEqual(st.handles.length, H.PB_HANDLE_CAP);
  assert.deepStrictEqual(lastEvicted, ['h1']);
  assert.strictEqual(st.handles[0].message_id, 'h2');
});

/* ---------- handles: added text ---------- */

test('added text: an exact-prefix growth yields the literal suffix; a divergent text is returned whole and flagged, never fabricated into a diff', () => {
  assert.deepStrictEqual(H.pbAddedText('Hello world.', 'Hello world. And more.'), { added: 'And more.', divergent: false });
  const d = H.pbAddedText('Hello world.', 'Something else entirely.');
  assert.strictEqual(d.divergent, true);
  assert.strictEqual(d.added, 'Something else entirely.');
});

/* ---------- Part 4: the re-look schedule ---------- */

test('the late look runs at close +60 s, then every 60 s, and is done after the +10 min look — the letter is never looked at forever', () => {
  const h = H.pbHandleFromDetection(det('r', 'UNVERIFIED'), ISO(0));
  assert.deepStrictEqual(H.pbRelookPlan(h, 59999).action, 'wait');
  assert.deepStrictEqual(H.pbRelookPlan(h, 60000).action, 'look');
  let t = 60000;
  for (let i = 0; i < 10; i++) {
    assert.strictEqual(H.pbRelookPlan(h, t).action, 'look', 'look ' + (i + 1));
    H.pbRelookAfterLook(h, t);
    t += 60000;
  }
  assert.strictEqual(h.relook.looks, 10);
  assert.strictEqual(h.relook.done, true);
  assert.strictEqual(H.pbRelookPlan(h, t).action, 'done');
});

test('an upgraded or acknowledged handle plans no further looks', () => {
  const h = H.pbHandleFromDetection(det('r2', 'UNVERIFIED'), ISO(0));
  h.relook.done = true; h.relook.upgradedAt = ISO(60000);
  assert.strictEqual(H.pbRelookPlan(h, 60000).action, 'done');
  const ha = H.pbHandleFromDetection(det('r3', 'ACKNOWLEDGED'), ISO(0));
  assert.strictEqual(H.pbRelookPlan(ha, 60000).action, 'done');
});

/* ---------- Part 4: the matcher + Part 1: the face words ---------- */

test('the re-look matcher: the body observed inside a USER turn counts; assistant turns, absence and an empty body do not', () => {
  const body = 'The eagle has landed.';
  assert.strictEqual(PB.pbBodyObservedInTurns([{ text: 'You said:\n' + body + '\n⟦PULSE-BRIDGE:TO-ALEX⟧', speaker: 'user' }], body), true);
  assert.strictEqual(PB.pbBodyObservedInTurns([{ text: body, speaker: 'assistant' }], body), false);
  assert.strictEqual(PB.pbBodyObservedInTurns([{ text: 'unrelated', speaker: 'user' }], body), false);
  assert.strictEqual(PB.pbBodyObservedInTurns([{ text: body, speaker: 'user' }], ''), false);
});

test('face words: SENT-UNCONFIRMED reads as what is actually known; every other face passes through unchanged (state keys untouched)', () => {
  assert.strictEqual(PB.pbFaceWords('SENT-UNCONFIRMED'), 'clicked; receipt not yet observed');
  assert.strictEqual(PB.pbFaceWords('DELIVERED-LATE'), 'DELIVERED-LATE');
  assert.strictEqual(PB.pbFaceWords('HELD'), 'HELD');
  assert.strictEqual(PB.pbFaceWords(''), '');
  assert.strictEqual(PB.pbFaceWords(null), '');
});

/* ---------- Part 1: the wording sweep ---------- */

test('wording sweep: no Ben-facing surface still says a letter was "sent, unconfirmed"; the adapters\' receipt errors carry the new words', () => {
  const read = (p) => fs.readFileSync(path.join(__dirname, '..', p), 'utf8');
  for (const f of ['popup.js', 'background.js', 'content.js']) {
    const src = read(f);
    assert.ok(!src.includes('sent, unconfirmed'), f + ' still carries the old phrase');
    assert.ok(!src.includes('sent, but unconfirmed'), f + ' still carries the old phrase');
  }
  for (const a of ['chatgpt.js', 'claude.js', 'claudeai.js', 'gemini.js', 'metaai.js']) {
    const src = read(path.join('adapters', a));
    assert.ok(!src.includes('sent, but unconfirmed; absence not established'), a + ' receipt error not renamed');
    assert.ok(src.includes('clicked; receipt not yet observed; absence not established'), a + ' receipt error missing the new words');
  }
});

/* ---------- Part 2: the acknowledged handoff ---------- */

function fakeAdapter(bubbles) {
  return {
    seat: 'alex',
    markerForSeat: LB.lbMarkerForSeat('alex'),
    regionEl: () => null,
    listBubbles: () => bubbles,
    bubbleOf: (el) => el,
    bubbleSpeaker: () => 'assistant',
    bubbleText: (b) => b.innerText,
    isGenerating: () => false,
  };
}
const bubbleOf = (text) => ({ innerText: text, querySelectorAll: () => [] });
const MARKER = '⟦PULSE-BRIDGE:TO-REMMY⟧';

test('handoff: a rejected first answer retries; the letter is marked handed off ONLY after the accepted answer', async () => {
  const bubble = bubbleOf(MARKER + '\nLetter one, for Remmy.');
  let calls = 0;
  const lb = LB.pbCreateLetterbox({
    adapter: fakeAdapter([bubble]),
    ackDelaysMs: [30, 60, 90],
    onHandoff: () => { calls++; return Promise.resolve(calls === 1 ? { answerClass: 'rejected', reason: 'test' } : { answerClass: 'accepted' }); },
    onDrop: () => {},
  });
  lb.consider(bubble);
  await sleep(7000); // settle (~5.5 s) + first answer + one retry delay
  assert.strictEqual(calls, 2);
  const bodyFp = PB.pbFingerprint('alex', 'Letter one, for Remmy.');
  assert.ok(lb._seen.has(bodyFp), 'marked after acceptance');
  assert.strictEqual(lb._awaiting.size, 0);
});

test('handoff: a duplicate answer is TERMINAL — marked handed off, never retried', async () => {
  const bubble = bubbleOf(MARKER + '\nLetter two, already recorded.');
  let calls = 0;
  const lb = LB.pbCreateLetterbox({
    adapter: fakeAdapter([bubble]),
    ackDelaysMs: [30, 60, 90],
    onHandoff: () => { calls++; return Promise.resolve({ answerClass: 'duplicate' }); },
    onDrop: () => {},
  });
  lb.consider(bubble);
  await sleep(6200);
  assert.strictEqual(calls, 1);
  assert.ok(lb._seen.has(PB.pbFingerprint('alex', 'Letter two, already recorded.')));
});

test('handoff: a letter the background never answers is NEVER marked handed off, retries are bounded, and the failure is reported as a drop', async () => {
  const bubble = bubbleOf(MARKER + '\nLetter three, into the void.');
  let calls = 0;
  const drops = [];
  const lb = LB.pbCreateLetterbox({
    adapter: fakeAdapter([bubble]),
    ackDelaysMs: [30, 60, 90],
    onHandoff: () => { calls++; return Promise.reject(new Error('worker gone')); },
    onDrop: (d) => drops.push(d),
  });
  lb.consider(bubble);
  await sleep(7000);
  assert.strictEqual(calls, 4); // first attempt + 3 bounded retries
  assert.ok(!lb._seen.has(PB.pbFingerprint('alex', 'Letter three, into the void.')), 'never marked');
  assert.ok(drops.some((d) => d.reason.includes('handoff unconfirmed')), 'the failure left a record');
});

test('letterbox: the pending-cap eviction is reported through the drop channel, never silent', async () => {
  const bubbles = [];
  for (let i = 0; i < 9; i++) bubbles.push(bubbleOf(MARKER + '\nCap letter ' + i + '.'));
  const drops = [];
  const lb = LB.pbCreateLetterbox({
    adapter: fakeAdapter(bubbles),
    ackDelaysMs: [30],
    onHandoff: () => Promise.resolve({ answerClass: 'accepted' }),
    onDrop: (d) => drops.push(d),
  });
  for (const b of bubbles) lb.consider(b);
  assert.strictEqual(lb._pending.size, 8);
  assert.ok(drops.some((d) => d.reason.includes('pending cap reached')), 'eviction reported');
});

/* ---------- runner ---------- */

(async () => {
  let passed = 0;
  const failures = [];
  for (const t of tests) {
    try { await t.fn(); passed++; console.log('ok - ' + t.name); }
    catch (e) { failures.push({ name: t.name, error: e }); console.log('FAIL - ' + t.name + '\n  ' + (e && e.message)); }
  }
  console.log(`\nconclusion.fixtures: ${passed}/${tests.length} passed`);
  process.exit(failures.length ? 1 : 0);
})();
