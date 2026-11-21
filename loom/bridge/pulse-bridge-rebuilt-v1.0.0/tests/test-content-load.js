"use strict";
/* Load test: run the built content.js top-level under DOM/chrome
 * stubs (per the standing lesson: syntax checks are not enough —
 * a ReferenceError during initial wiring kills the whole script).
 * Harness stubs are deliberately dumb; a throw whose stack lands
 * in the stub layer is a harness gap, a throw in content.js code
 * is a build defect. */
const fs = require("fs");
const vm = require("vm");

function makeEl() {
  const el = {
    children: [], style: {}, dataset: {}, className: "", id: "",
    textContent: "", innerHTML: "", value: "",
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    appendChild(c) { this.children.push(c); return c; },
    removeChild() {}, remove() {},
    addEventListener() {}, removeEventListener() {},
    setAttribute() {}, getAttribute() { return null; },
    querySelector() { return null; }, querySelectorAll() { return []; },
    closest() { return null; }, focus() {}, click() {},
    getBoundingClientRect() { return { top: 0, left: 0, width: 0, height: 0 }; },
  };
  return el;
}

const listeners = {};
const sandbox = {
  console,
  setInterval: (...a) => { const t = setInterval(...a); t.unref(); return t; },
  setTimeout: (...a) => { const t = setTimeout(...a); t.unref(); return t; },
  clearInterval, clearTimeout,
  Date, JSON, Math, Promise, Set, Map, Array, Object, String, Number, Boolean, RegExp, Error,
  location: { pathname: "/c/test", href: "https://chatgpt.com/c/test", hostname: "chatgpt.com" },
  navigator: { userAgent: "stub" },
  MutationObserver: class { observe() {} disconnect() {} },
  ResizeObserver: class { observe() {} disconnect() {} },
  IntersectionObserver: class { observe() {} disconnect() {} },
  requestAnimationFrame: (fn) => { fn(); return 0; },
  getComputedStyle: () => ({}),
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
sandbox.document = {
  body: makeEl(), documentElement: makeEl(), head: makeEl(),
  createElement: () => makeEl(), createTextNode: () => ({}),
  getElementById: () => null, getElementsByTagName: () => [],
  querySelector: () => null, querySelectorAll: () => [],
  addEventListener() {}, removeEventListener() {},
  readyState: "complete", visibilityState: "visible",
};
sandbox.chrome = {
  runtime: {
    onMessage: { addListener: (fn) => { listeners.msg = fn; } },
    sendMessage: async () => ({ ok: true, state: { detections: [], registrations: {} }, yourSeat: null }),
    id: "stub",
  },
  storage: { local: { get: async () => ({}), set: async () => {}, remove: async () => {} } },
};
sandbox.PB_ADAPTER = {
  seat: "alex", platform: "chatgpt",
  isGenerating: () => false, composerButtonState: () => "ready",
  turnMarks: () => [], newestTurn: () => null,
};
vm.createContext(sandbox);
// Load the real content-script stack in manifest order —
// content.js wires against globals from the files before it.
for (const f of ["protocol.js", "sendcore.js", "crusher.js", "alert.js", "letterbox.js"]) {
  vm.runInContext(fs.readFileSync(__dirname + "/pulse-bridge/" + f, "utf8"), sandbox, { filename: f });
}
const code = fs.readFileSync(__dirname + "/pulse-bridge/content.js", "utf8");
try {
  vm.runInContext(code, sandbox, { filename: "content.js" });
  console.log("PASS content.js top-level load — no throw");
} catch (e) {
  console.error("FAIL content.js threw at load:", e && e.stack ? e.stack.split("\n").slice(0, 4).join("\n") : e);
  process.exit(1);
}
// The boot sequence is async (state pull, then wiring): let the
// microtask queue drain before judging registration.
setTimeout(() => {
  if (typeof listeners.msg !== "function") { console.log("FAIL no onMessage listener captured after boot drain"); process.exit(1); }
  console.log("PASS runtime.onMessage listener registered");
  // Exercise the render path: a confirmed receipt, receiver side.
  try {
    listeners.msg({
      kind: "pb-wait-state",
      face: { seat: "alex", word: "idle", sentence: "All clear. Nothing is waiting.", letters: [], earlier: [] },
      indicator: { active: true, pbId: "pb-test-001", role: "receiver", peer: "Remmy",
        phase: "confirmed", word: "Received", detail: "From Remmy",
        confirmed: { pbId: "pb-test-001", destination: "Alex",
          evidence: "Confirming user turn in the destination conversation",
          at: "2026-11-20T00:30:00.000Z" } },
    }, {}, () => {});
  } catch (e) {
    console.log("FAIL render path threw:", e && e.stack ? e.stack.split("\n").slice(0, 3).join("\n") : e);
    process.exit(1);
  }
  const texts = [];
  (function walk(el) {
    if (!el) return;
    if (el.textContent) texts.push(el.textContent);
    (el.children || []).forEach(walk);
  })(sandbox.document.body);
  const joined = texts.join(" | ");
  const okWord = joined.includes("Received");
  const okId = joined.includes("PB-ID: pb-test-001");
  const okConf = joined.includes("Delivery confirmed");
  console.log((okWord ? "PASS" : "FAIL") + " indicator word rendered");
  console.log((okId ? "PASS" : "FAIL") + " PB-ID rendered");
  console.log((okConf ? "PASS" : "FAIL") + " confirmation block rendered");
  process.exit(okWord && okId && okConf ? 0 : 1);
}, 50);
