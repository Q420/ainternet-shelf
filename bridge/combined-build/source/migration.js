'use strict';
/*
 * Pulse Bridge — legacy migration inventory (Stage 1 batch 3;
 * Build Plan 01 S3, "Must not touch" migration rules).
 *
 * The v0.18.0 state object (chrome.storage key
 * pulseBridgeStateV1) is inventoried, never migrated by
 * destruction: nothing here deletes, truncates or rewrites the
 * source state, and the input object is returned unmodified.
 *
 * Message-bearing legacy stores are classified entry by entry:
 * - the old bridge-assigned message_id is preserved as the
 *   legacy identity — no new identity is invented for a
 *   historical message whose source evidence is unavailable;
 * - classification is 'legacy' where the old system's own
 *   record establishes what the entry is, 'uncertain' where
 *   identity rests on a bare fingerprint with no id mapping;
 * - delivery uses the same fact discipline as the ledger:
 *   'confirmed-delivered' only where the old system recorded a
 *   confirmation, 'proven-not-delivered' for recorded failures,
 *   'unknown' everywhere else;
 * - re-send is blocked wherever delivery is confirmed (the
 *   lifetime block carries over) and wherever delivery history
 *   is uncertain. Only a recorded proven-not-delivered legacy
 *   entry is unblocked, and its route forward is a fresh
 *   managed registration, not a re-send of the legacy item.
 * - the active pair and its buffer are inventoried as
 *   active-held state for owner review — never auto-carried,
 *   never converted into registrations by this inventory.
 * - stores with no message identity (registrations, log,
 *   alerts, serials, operational flags) are accounted for as
 *   preserved; a store this inventory does not recognise is
 *   'unclassified-preserved' — accounted, never dropped.
 */

const MESSAGE_STORES = new Set([
  'detections', 'seen', 'delivered', 'deliveryFailed',
  'deliveredIds', 'deliveryFailedIds', 'seenIds', 'fpToId',
  'completedSerials',
]);

function clone(x) {
  return x === undefined ? undefined : JSON.parse(JSON.stringify(x));
}

function emptyEntry(legacyId, kind, store) {
  return {
    legacyId,
    kind,
    stores: [store],
    classification: 'legacy',
    delivery: 'unknown',
    resendBlocked: true,
    note: null,
  };
}

function inventoryLegacyState(state) {
  const src = state || {};
  const byId = new Map();
  const fpToIdMap = new Map();
  const stores = [];
  let activeHeld = 0;

  function entryFor(legacyId, kind, store) {
    const key = kind + ':' + legacyId;
    if (!byId.has(key)) byId.set(key, emptyEntry(legacyId, kind, store));
    const e = byId.get(key);
    if (!e.stores.includes(store)) e.stores.push(store);
    return e;
  }

  function markDelivered(e) {
    e.delivery = 'confirmed-delivered';
    e.resendBlocked = true;
  }

  function markFailed(e) {
    // A recorded failure wins over unknown, never over a
    // recorded confirmation.
    if (e.delivery !== 'confirmed-delivered') {
      e.delivery = 'proven-not-delivered';
      e.resendBlocked = false;
    }
  }

  for (const name of Object.keys(src)) {
    const value = src[name];
    if (name === 'pair') {
      const held = value != null ? 1 : 0;
      activeHeld += held;
      stores.push({ name, count: held, classification: 'active-held' });
      continue;
    }
    if (name === 'bufferId') {
      stores.push({ name, count: value != null ? 1 : 0, classification: 'active-held' });
      if (value != null) {
        const e = entryFor(value, 'message-id', name);
        e.note = 'buffered by the legacy pair machine; delivery unknown';
      }
      continue;
    }
    if (!MESSAGE_STORES.has(name)) {
      const count = Array.isArray(value) ? value.length
        : (value && typeof value === 'object' ? Object.keys(value).length : (value != null ? 1 : 0));
      const known = ['registrations', 'paused', 'v7migrated', 'fileTransfers',
        'rollovers', 'alerts', 'serialNext', 'log'].includes(name);
      stores.push({ name, count, classification: known ? 'preserved' : 'unclassified-preserved' });
      continue;
    }

    // Message-bearing stores.
    let count = 0;
    if (name === 'detections' && Array.isArray(value)) {
      for (const det of value) {
        count += 1;
        const id = det && det.envelope && det.envelope.message_id;
        if (typeof id === 'string' && id) {
          const e = entryFor(id, 'message-id', name);
          e.note = 'pending legacy detection; never reached a recorded outcome';
        }
      }
    } else if (name === 'fpToId' && value && typeof value === 'object') {
      for (const [fp, id] of Object.entries(value)) {
        count += 1;
        if (typeof id === 'string' && id) {
          fpToIdMap.set(fp, id);
          const e = entryFor(id, 'message-id', name);
          e.note = 'fingerprint ' + fp + ' mapped by the legacy dedup index';
          const fe = entryFor(fp, 'fingerprint', name);
          fe.classification = 'legacy';
          fe.note = 'mapped to ' + id + ' by fpToId';
          fe.resendBlocked = true;
        }
      }
    } else if (Array.isArray(value)) {
      for (const item of value) {
        count += 1;
        if (name === 'completedSerials') {
          if (item && typeof item.id === 'string' && item.id) {
            const e = entryFor(item.id, 'message-id', name);
            markDelivered(e);
            e.note = 'retired pair serial ' + String(item.serial) + ' — pair completed';
          }
          continue;
        }
        if (typeof item !== 'string' || !item) continue;
        const isIdStore = name.endsWith('Ids');
        const e = entryFor(item, isIdStore ? 'message-id' : 'fingerprint', name);
        if (name === 'deliveredIds' || name === 'delivered') markDelivered(e);
        if (name === 'deliveryFailedIds' || name === 'deliveryFailed') markFailed(e);
        if (!isIdStore) {
          // A bare fingerprint — in seen, delivered or failed —
          // cannot prove identity by itself. The fpToId handling
          // upgrades the ones the old system itself mapped.
          e.classification = 'uncertain';
          if (!e.note) e.note = 'fingerprint record with no id mapping consulted';
        }
      }
    }
    stores.push({ name, count, classification: 'inventoried' });
  }

  // Delivery truth flows across the old system's own mapping:
  // a mapped fingerprint and its id share the stronger recorded
  // outcome (confirmed over proven-not-delivered over unknown).
  for (const [fp, id] of fpToIdMap) {
    const fe = byId.get('fingerprint:' + fp);
    const ie = byId.get('message-id:' + id);
    if (!fe || !ie) continue;
    const rank = { 'confirmed-delivered': 3, 'proven-not-delivered': 2, unknown: 1 };
    const strong = rank[fe.delivery] >= rank[ie.delivery] ? fe.delivery : ie.delivery;
    for (const e of [fe, ie]) {
      e.delivery = strong;
      e.resendBlocked = strong !== 'proven-not-delivered';
    }
  }
  const entries = [...byId.values()];
  for (const e of entries) e.stores.sort();
  entries.sort((a, b) => (a.legacyId < b.legacyId ? -1 : a.legacyId > b.legacyId ? 1 : 0));

  const summary = {
    entries: entries.length,
    legacy: entries.filter((e) => e.classification === 'legacy').length,
    uncertain: entries.filter((e) => e.classification === 'uncertain').length,
    resendBlocked: entries.filter((e) => e.resendBlocked).length,
    confirmedDelivered: entries.filter((e) => e.delivery === 'confirmed-delivered').length,
    provenNotDelivered: entries.filter((e) => e.delivery === 'proven-not-delivered').length,
    activeHeld,
    stores: stores.length,
  };

  return { stores, entries, summary };
}

const PBMigration = { inventoryLegacyState };

if (typeof module !== 'undefined' && module.exports) {
  module.exports = PBMigration;
}
if (typeof globalThis !== 'undefined') {
  globalThis.PBMigration = PBMigration;
}
