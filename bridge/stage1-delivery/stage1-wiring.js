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
  pbStage1Epoch.importState(state.stage1.epochExport || { epoch: 0 });
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

async function pbStage1OnDetection(state, envelope) {
  try {
    await pbStage1Ensure(state);
    const reg = state.registrations && state.registrations[envelope.from];
    const source = { platform: reg && reg.platform ? reg.platform : undefined };
    const ack = await pbStage1Session.submitDetection({
      handoffId: envelope.message_id,
      source,
      admitted: true,
      epoch: pbStage1Epoch.current(),
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

async function pbStage1OnPauseOrDisconnect(state, why) {
  try {
    await pbStage1Ensure(state);
    const adv = pbStage1Epoch.advance(why);
    await pbStage1Persist(state);
    pbLog(state, 'Stage 1 epoch advanced to ' + adv.epoch + ' (' + why + ') before dispatch eligibility changed');
    return adv;
  } catch (err) {
    try { pbLog(state, 'Stage 1 epoch advance fault: ' + (err && err.message)); } catch (e) { /* never break pause */ }
    return null;
  }
}
