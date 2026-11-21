'use strict';
/* Load test: execute background.js top-level in a vm with
 * importScripts + chrome stubs (AGENTS.md: a syntax check is
 * not enough — a ReferenceError during initial wiring kills
 * the whole worker). Not a fixture suite; run once per build. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const store = {};
const listeners = {};
const sandbox = {
  console, setTimeout, clearTimeout, setInterval, clearInterval, Date, JSON, Math, Promise, Error, TypeError, RegExp, Array, Object, String, Number, Boolean, Map, Set, WeakMap, Symbol, Reflect, Proxy, URL, TextEncoder, TextDecoder, queueMicrotask, globalThis: null,
  chrome: {
    storage: { local: {
      get: async (k) => ({ [k]: store[k] }),
      set: async (obj) => { Object.assign(store, obj); },
      remove: async () => {},
    } },
    alarms: { create: () => {}, onAlarm: { addListener: (fn) => { listeners.alarm = fn; } } },
    tabs: { query: async () => [], sendMessage: async () => { throw new Error('no tab'); }, get: async () => null, onRemoved: { addListener: () => {} }, onUpdated: { addListener: () => {} }, onCreated: { addListener: () => {} } },
    windows: { onFocusChanged: { addListener: () => {} }, onRemoved: { addListener: () => {} }, onCreated: { addListener: () => {} }, getLastFocused: async () => null, getAll: async () => [] },
    runtime: { onMessage: { addListener: (fn) => { listeners.message = fn; } }, onInstalled: { addListener: () => {} }, onStartup: { addListener: () => {} } },
    action: { onClicked: { addListener: () => {} } },
  },
  importScripts: (...files) => {
    for (const f of files) {
      const code = fs.readFileSync(path.join(root, f), 'utf8');
      vm.runInContext(code, sandbox, { filename: f });
    }
  },
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
(async () => {
  try {
    const code = fs.readFileSync(path.join(root, 'background.js'), 'utf8');
    vm.runInContext(code, sandbox, { filename: 'background.js' });
    await new Promise((r) => setTimeout(r, 300));
    const need = ['PB_HANDLES', 'PB_STATION', 'PB'];
    for (const n of need) {
      const t = vm.runInContext('typeof ' + n, sandbox);
      if (t !== 'object' && t !== 'function') throw new Error('missing global ' + n + ' (typeof ' + t + ')');
    }
    if (typeof listeners.message !== 'function') throw new Error('onMessage listener not registered');
    if (typeof listeners.alarm !== 'function') throw new Error('onAlarm listener not registered');
    console.log('LOAD TEST PASS: background.js wired clean; PB_HANDLES present; message + alarm listeners registered');
    process.exit(0);
  } catch (e) {
    console.log('LOAD TEST FAIL: ' + (e && e.stack || e));
    process.exit(1);
  }
})();
