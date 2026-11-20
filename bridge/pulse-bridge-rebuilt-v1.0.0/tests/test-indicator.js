"use strict";
/* Test: pbIndicatorFor against Vane's state table
 * (vane-20261120-bridge-indicator-design-01 §2).
 * Extracts the function from the built background.js and
 * feeds it synthetic bridge states. */
const fs = require("fs");
const src = fs.readFileSync(__dirname + "/pulse-bridge/background.js", "utf8");
const start = src.indexOf("function pbIndicatorFor");
const end = src.indexOf("async function pbPushFaceToSeat");
if (start < 0 || end < 0) { console.error("FAIL: pbIndicatorFor not found"); process.exit(1); }
const pbSeatName = (s) => (s === "alex" ? "Alex" : s === "remmy" ? "Remmy" : String(s || ""));
const pbIndicatorFor = eval(src.slice(start, end) + "\npbIndicatorFor;");

function det(from, to, state, at) {
  return {
    at: at || "2026-11-20T00:30:00.000Z",
    envelope: { message_id: "pb-test-001", from, to, body: "x" },
    crusher: { state, trail: [{ state, at: at || "2026-11-20T00:30:00.000Z", note: "" }] },
  };
}
let fails = 0;
function check(label, got, wantWord, wantPhase) {
  const ok = got.word === wantWord && (wantPhase === undefined || got.phase === wantPhase);
  console.log((ok ? "PASS" : "FAIL") + " " + label + " -> word=" + JSON.stringify(got.word) + " phase=" + got.phase);
  if (!ok) fails++;
}

// No exchange -> Ready, inactive
let r = pbIndicatorFor({ detections: [] }, "remmy");
console.log((!r.active && r.word === "Ready" ? "PASS" : "FAIL") + " idle -> Ready/inactive");
if (r.active || r.word !== "Ready") fails++;

// DELIVERING remmy -> alex: sender Sending, receiver Incoming
let st = { detections: [det("remmy", "alex", "DELIVERING")] };
check("sender DELIVERING", pbIndicatorFor(st, "remmy"), "Sending", "inflight");
check("receiver DELIVERING", pbIndicatorFor(st, "alex"), "Incoming", "inflight");

// ACKNOWLEDGED: sender Delivered, receiver Received + confirmation block w/ PB-ID
st = { detections: [det("remmy", "alex", "ACKNOWLEDGED")] };
const sAck = pbIndicatorFor(st, "remmy"), rAck = pbIndicatorFor(st, "alex");
check("sender ACK", sAck, "Delivered", "confirmed");
check("receiver ACK", rAck, "Received", "confirmed");
const confOk = sAck.confirmed && sAck.confirmed.pbId === "pb-test-001" &&
  rAck.confirmed && rAck.confirmed.pbId === "pb-test-001" &&
  /Confirming user turn/.test(sAck.confirmed.evidence);
console.log((confOk ? "PASS" : "FAIL") + " confirmation block carries PB-ID + receiving-side evidence in both windows");
if (!confOk) fails++;

// UNVERIFIED stays distinct from Delivered
st = { detections: [det("remmy", "alex", "UNVERIFIED")] };
check("sender UNVERIFIED", pbIndicatorFor(st, "remmy"), "Unverified", "unverified");
check("receiver UNVERIFIED", pbIndicatorFor(st, "alex"), "Receipt unverified", "unverified");

// STALLED
st = { detections: [det("remmy", "alex", "STALLED")] };
check("sender STALLED", pbIndicatorFor(st, "remmy"), "Stalled", "stalled");
check("receiver STALLED", pbIndicatorFor(st, "alex"), "Disconnected / unavailable", "stalled");

// A live exchange outranks an older terminal one
st = { detections: [
  det("remmy", "alex", "ACKNOWLEDGED", "2026-11-20T00:10:00.000Z"),
  det("alex", "remmy", "DELIVERING", "2026-11-20T00:40:00.000Z"),
] };
check("live outranks old terminal (remmy now receiver)", pbIndicatorFor(st, "remmy"), "Incoming", "inflight");
check("live outranks old terminal (alex now sender)", pbIndicatorFor(st, "alex"), "Sending", "inflight");

// Unrelated seat sees nothing
st = { detections: [det("remmy", "alex", "DELIVERING")] };
r = pbIndicatorFor(st, "crusher");
console.log((!r.active ? "PASS" : "FAIL") + " unrelated seat inactive");
if (r.active) fails++;

console.log(fails === 0 ? "ALL PASS" : fails + " FAILURES");
process.exit(fails ? 1 : 0);
