"use strict";
/*
 * Pulse Bridge — Stage 1 wiring (v0.19.0, Build Plan 01 S3).
 *
 * Connects the Stage 1 core (stage1core.js: identity, ledger,
 * capture session, epoch, migration inventory) to the
 * background router at exactly three seams:
 *
 * 1. Detection acceptance: every accepted detection is
 *    submitted to the capture session and its acknowledgement
 *    is recorded on the bridge state (state.stage1.acks) and in
 *    the run log. Today's adapters supply no qualified native
 *    message identity (Stage 0 census: none qualified), so the
 *    honest live outcome is NOT_REGISTERED with the identity
 *    reason — recorded, never hidden, and the existing flow
 *    proceeds exactly as before. No outbound behaviour changes.
 * 2. Pause / disconnect: the bridge epoch advances and is
 *    persisted BEFORE the pause/disconnect takes effect
 *    (Plan S3 item 8).
 * 3. First touch: the legacy state is inventoried (never
 *    modified) and the inventory summary is stored alongside.
 *
 * Persistence: the ledger and epoch live inside the bridge
 * state object (state.stage1) via the core's export/import.
 * That is a serialised single-instance arrangement — the
 * module's own durability qualification stands (no durable
 * commit or multi-instance allocator is claimed).
 *
 * Authority: the wired ledger is created WITHOUT an authority
 * verifier, so authority-bearing lifecycle transitions stay
 * unavailable in the live bridge until Stage 3 gives Ben's
 * decisions a real channel. Nothing here fakes a proof.
 *
 * Every entry point is failure-isolated: a Stage 1 fault is
 * logged and the router continues untouched.
 */

let pbStage1Ledger = null;
let pbStage1Epoch = null;
let pbStage1Session = null;
let pbStage1HydratedRev = -1;

async function pbStage1Sha256Hex(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function pbStage1Ensure(state) {
  if (!state.stage1) {
    const inv = PBMigration.inventoryLegacyState(state);
    state.stage1 = {
      revision: 0,
      ledgerExport: null,
      epochExport: { epoch: 0, history: [] },
      migrationSummary: inv.summary,
      migrationStores: inv.stores.map((s) => ({ name: s.name, classification: s.classification, count: s.count })),
      acks: [],
      integrityFault: false,
      unreconciled: null,
      tokens: {},
    };
    pbLog(state, 'Stage 1: legacy state inventoried (' + inv.summary.entries + ' entries, ' +
      inv.summary.uncertain + ' uncertain, ' + inv.summary.resendBlocked + ' re-send blocked); legacy stores untouched');
  }
  if (pbStage1Session && pbStage1HydratedRev === state.stage1.revision) return true;
  pbStage1Ledger = PBLedger.createLedger({
    now: () => Date.now(),
    sha256Hex: pbStage1Sha256Hex,
    duplicateEventPolicy: 'event',
  });
  if (state.stage1.ledgerExport) {
    const imp = await pbStage1Ledger.importState(state.stage1.ledgerExport);
    if (imp.status !== 'OK') {
      state.stage1.integrityFault = true;
      pbLog(state, 'Stage 1: ledger import fault (' + (imp.reason || imp.status) + ') — registrations will answer UNKNOWN');
    }
  }
  pbStage1Epoch = PBCapture.createEpochStore({});
  const eimp = pbStage1Epoch.importState(state.stage1.epochExport || { epoch: 0 });
  if (eimp.status !== 'OK') {
    state.stage1.integrityFault = true;
    pbLog(state, 'Stage 1: epoch import fault (' + (eimp.reason || eimp.status) + ') — epoch state unverifiable, detections fail closed');
  }
  if (state.stage1.tokens && typeof state.stage1.tokens === 'object') {
    for (const seat of Object.keys(state.stage1.tokens)) {
      if (!pbStage1TokenRecordValid(state.stage1.tokens[seat])) {
        state.stage1.integrityFault = true;
        delete state.stage1.tokens[seat];
        pbLog(state, 'Stage 1: detection token record for ' + seat + ' failed validation at load — discarded; outstanding candidates for that seat fail closed');
      }
    }
  }
  pbStage1Session = PBCapture.createCaptureSession({
    ledger: pbStage1Ledger,
    epochStore: pbStage1Epoch,
    sha256Hex: pbStage1Sha256Hex,
  });
  pbStage1HydratedRev = state.stage1.revision;
  return true;
}

async function pbStage1Persist(state) {
  state.stage1.ledgerExport = pbStage1Ledger.exportState();
  state.stage1.epochExport = pbStage1Epoch.exportState();
  state.stage1.revision += 1;
  pbStage1HydratedRev = state.stage1.revision;
}

/* ---- Combined Build, Part A stream 2: detection tokens (D1,
 * as closed with Alex). The background issues one token per
 * seat, bound to the registered tab, a registration generation
 * and the epoch. The content script snapshots it when a
 * candidate FIRST enters settle; the pending record carries
 * that exact snapshot to handoff, which can never fetch or
 * refresh it. Admission validates every binding against the
 * authoritative record; any disagreement is a STALE rejection,
 * never a repair. Rotation — epoch advance, tab change,
 * invalid record — dooms every pending candidate holding the
 * old token, by design. The token proves epoch-at-capture
 * inside trusted code; it is NOT per-message authentication,
 * and duplicate protection stays with identity/fingerprints.
 * Records persist inside state.stage1, in the same state
 * object (and therefore the same save) as the epoch. ---- */
function pbStage1TokenRecordValid(rec) {
  return !!rec && typeof rec.token === 'string' && rec.token.length > 0 &&
    Number.isInteger(rec.generation) && rec.generation >= 1 &&
    Number.isInteger(rec.epoch) && rec.epoch >= 0 &&
    (typeof rec.tabId === 'number' || typeof rec.tabId === 'string');
}

async function pbStage1MintTokenValue(seat, tabId, generation, epoch) {
  let rand = '';
  try {
    const bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    rand = Array.from(bytes).map((b) => b.toString(16).padStart(2, '0')).join('');
  } catch (e) { rand = String(Date.now()) + '|' + String(Math.random()); }
  const hash = await pbStage1Sha256Hex(seat + '|' + tabId + '|' + generation + '|' + epoch + '|' + rand);
  return 'dt1-' + hash.slice(0, 32);
}

async function pbStage1TokenEnsure(state, seat, tabId) {
  await pbStage1Ensure(state);
  if (!state.stage1.tokens || typeof state.stage1.tokens !== 'object') state.stage1.tokens = {};
  const cur = pbStage1Epoch.current();
  const rec = state.stage1.tokens[seat];
  if (pbStage1TokenRecordValid(rec) && String(rec.tabId) === String(tabId) && rec.epoch === cur) {
    return { record: rec, changed: false };
  }
  const generation = pbStage1TokenRecordValid(rec) ? rec.generation + 1 : 1;
  const fresh = {
    token: await pbStage1MintTokenValue(seat, tabId, generation, cur),
    generation,
    epoch: cur,
    tabId,
    issuedAt: new Date().toISOString(),
  };
  state.stage1.tokens[seat] = fresh;
  pbLog(state, 'Stage 1: detection token ' + (generation > 1 ? 'rotated' : 'issued') + ' for ' + seat + ' (generation ' + generation + ', epoch ' + cur + ')');
  return { record: fresh, changed: true };
}

async function pbStage1OnDetection(state, envelope, senderTabId) {
  try {
    await pbStage1Ensure(state);
    /* Token admission gate (D1): the snapshot the candidate
     * took at settle start, validated against the authoritative
     * current record. A rejection is recorded as a STALE ack —
     * the Stage 1 record fails closed while the bridge's own
     * flow proceeds exactly as before. */
    const snap = envelope.tokenSnapshot || null;
    const staleAck = (reason) => {
      state.stage1.acks.push({
        handoffId: envelope.message_id, outcome: 'STALE', reason,
        indexId: null, epoch: pbStage1Epoch.current(), at: new Date().toISOString(),
      });
      if (state.stage1.acks.length > 100) state.stage1.acks = state.stage1.acks.slice(-100);
      pbLog(state, 'Stage 1 ack STALE (' + reason + ') for ' + envelope.message_id);
      return { outcome: 'STALE', reason, indexId: null };
    };
    if (!snap || typeof snap.token !== 'string' || !Number.isInteger(snap.epoch) || !Number.isInteger(snap.generation)) {
      return staleAck('token-missing');
    }
    const trec = state.stage1.tokens && state.stage1.tokens[envelope.from];
    if (!pbStage1TokenRecordValid(trec)) return staleAck('token-unissued');
    if (trec.token !== snap.token || trec.generation !== snap.generation) return staleAck('token-rotated');
    if (String(trec.tabId) !== String(snap.tabId)) return staleAck('token-tab-mismatch');
    if (senderTabId != null && String(snap.tabId) !== String(senderTabId)) return staleAck('token-sender-mismatch');
    if (snap.epoch !== pbStage1Epoch.current()) return staleAck('epoch-stale');
    const reg = state.registrations && state.registrations[envelope.from];
    const source = { platform: reg && reg.platform ? reg.platform : undefined };
    const ack = await pbStage1Session.submitDetection({
      handoffId: envelope.message_id,
      source,
      admitted: true,
      epoch: snap.epoch,
    });
    state.stage1.acks.push({
      handoffId: envelope.message_id,
      outcome: ack.outcome,
      reason: ack.reason || null,
      indexId: ack.indexId || null,
      epoch: pbStage1Epoch.current(),
      at: new Date().toISOString(),
    });
    if (state.stage1.acks.length > 100) state.stage1.acks = state.stage1.acks.slice(-100);
    await pbStage1Persist(state);
    pbLog(state, 'Stage 1 ack ' + ack.outcome + (ack.reason ? ' (' + ack.reason + ')' : '') + ' for ' + envelope.message_id);
    return ack;
  } catch (err) {
    try { pbLog(state, 'Stage 1 wiring fault on detection ' + envelope.message_id + ': ' + (err && err.message)); } catch (e) { /* never break capture */ }
    return null;
  }
}

/* Combined Build, Part A (Correction Basis streams 1 + 3):
 * an epoch transition is a three-part result — advanced,
 * saved, read-back matched — never just "advanced in memory".
 * The safety action itself (pause / disconnect) is NEVER
 * blocked by a Stage 1 fault: the caller proceeds regardless
 * of what this returns. What a fault changes is the RECORD:
 * an unreconciled condition is written onto the bridge state
 * where Ben and the panel can see it, and resume is gated on
 * reconciliation (pbStage1OnResume) instead of proceeding on
 * an unverified epoch. */
function pbStage1VerifyEpochReadBack(expectedEpoch) {
  try {
    const probe = PBCapture.createEpochStore({});
    const imp = probe.importState(pbStage1Epoch.exportState());
    return imp.status === 'OK' && probe.current() === expectedEpoch &&
      probe.exportState().history.length === pbStage1Epoch.exportState().history.length;
  } catch (e) { return false; }
}

async function pbStage1OnPauseOrDisconnect(state, why) {
  try {
    await pbStage1Ensure(state);
    const un = state.stage1.unreconciled;
    const transitionId = (un && un.kind === 'epoch-transition' && un.why === String(why) && un.transitionId)
      ? un.transitionId
      : String(why) + ':' + (pbStage1Epoch.current() + 1);
    const adv = pbStage1Epoch.advance(why, transitionId);
    await pbStage1Persist(state);
    if (!pbStage1VerifyEpochReadBack(adv.epoch)) throw new Error('epoch read-back mismatch after save');
    if (state.stage1.unreconciled && state.stage1.unreconciled.transitionId === transitionId) {
      state.stage1.unreconciled = null;
    }
    pbLog(state, 'Stage 1 epoch advanced to ' + adv.epoch + ' (' + why + '), saved and verified by read-back before dispatch eligibility changed');
    return { status: 'ADVANCED', epoch: adv.epoch, verified: true, alreadyApplied: !!adv.alreadyApplied };
  } catch (err) {
    try {
      const prev = state.stage1.unreconciled;
      state.stage1.unreconciled = {
        kind: 'epoch-transition',
        why: String(why),
        transitionId: (prev && prev.kind === 'epoch-transition' && prev.why === String(why) && prev.transitionId)
          ? prev.transitionId
          : String(why) + ':' + (pbStage1Epoch ? pbStage1Epoch.current() : '?'),
        at: new Date().toISOString(),
        detail: (err && err.message) || 'unknown',
      };
      pbLog(state, 'Stage 1 epoch transition UNRECONCILED (' + why + '): ' + state.stage1.unreconciled.detail + ' — the safety action proceeds; resume is gated until reconciliation verifies');
    } catch (e) { /* never break pause */ }
    return { status: 'FAULT', verified: false };
  }
}

/* Part A item 8 (Amendment 01): reset preservation. Reset is
 * Ben clearing connections — it is not licence to erase the
 * permanent Stage 1 record. The record (ledger export, epoch
 * export WITH history, acknowledgements, unreconciled
 * condition, migration inventory) carries into the fresh
 * state; detection tokens do not — clearing the token records
 * revokes every outstanding snapshot. Returns true when a
 * record was preserved. */
function pbStage1PreserveAcrossReset(priorState, newState) {
  if (!priorState || !priorState.stage1 || !newState) return false;
  const s1 = priorState.stage1;
  newState.stage1 = {
    revision: (Number.isInteger(s1.revision) ? s1.revision : 0) + 1,
    ledgerExport: s1.ledgerExport || null,
    epochExport: s1.epochExport || { epoch: 0, history: [] },
    migrationSummary: s1.migrationSummary || null,
    migrationStores: s1.migrationStores || [],
    acks: s1.acks || [],
    integrityFault: !!s1.integrityFault,
    unreconciled: s1.unreconciled || null,
    tokens: {},
  };
  return true;
}

/* Resume gate: CLEAR when nothing is outstanding; RECONCILED
 * when a fresh verified save makes the persisted epoch export
 * match the live store exactly; UNRECONCILED otherwise, and
 * the caller holds the bridge paused and says so. */
async function pbStage1OnResume(state) {
  try {
    await pbStage1Ensure(state);
    const un = state.stage1.unreconciled;
    if (!un) return { status: 'CLEAR' };
    if (un.kind !== 'epoch-transition') return { status: 'UNRECONCILED', detail: 'unreconciled ' + un.kind };
    await pbStage1Persist(state);
    const probe = PBCapture.createEpochStore({});
    const imp = probe.importState(state.stage1.epochExport || { epoch: 0 });
    if (imp.status !== 'OK') return { status: 'UNRECONCILED', detail: 'epoch export import ' + (imp.reason || imp.status) };
    if (probe.current() !== pbStage1Epoch.current()) return { status: 'UNRECONCILED', detail: 'epoch read-back mismatch' };
    state.stage1.unreconciled = null;
    await pbStage1Persist(state);
    pbLog(state, 'Stage 1: epoch transition reconciled and verified by read-back — resume unblocked');
    return { status: 'RECONCILED', epoch: pbStage1Epoch.current() };
  } catch (err) {
    return { status: 'UNRECONCILED', detail: (err && err.message) || 'unknown' };
  }
}
