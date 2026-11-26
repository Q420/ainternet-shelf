// Producer AUDIT — the five standing-record checks named in the build spec,
// run manually against the real framework records. This is a command-line
// audit script, not a Node test suite (Gate 3 correction G3-01: it was
// renamed out of *.test.mjs so `npm test` discovery cannot mistake it for
// one). The producer's own test suite is producer.test.mjs.
// Usage: node producer.audit.mjs --records <live-demo dir> --feed <generated feed.json> --artifacts-dir <dir>
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { validateFeed } from "../feed-contract.mjs";
const args = process.argv.slice(2);
const opt = n => { const i = args.indexOf("--" + n); return i >= 0 ? args[i + 1] : null; };
const recordsDir = opt("records"), feedFile = opt("feed"), artifactsDir = opt("artifacts-dir");
const feed = JSON.parse(await readFile(feedFile, "utf8"));
let fails = 0; const check = (name, ok, detail = "") => { console.log((ok ? "PASS" : "FAIL") + " " + name + (detail ? " — " + detail : "")); if (!ok) fails++; };

// 1. Validates as v1 under the contract.
const v = validateFeed(feed);
check("feed validates as v1", v.ok && v.version === 1, v.reason || "");

// 2. History cannot become offices: offices empty, no run id inside it.
check("offices empty; no historical run appears as an office",
  Array.isArray(feed.offices) && feed.offices.length === 0 &&
  !feed.historical_runs.some(r => feed.offices.some(o => o.id === r.run || o.run_id === r.run)));

// 3. Every artifact path resolves (in the artifacts dir) with matching bytes.
let artOk = true;
for (const a of feed.artifacts) {
  try { const s = await stat(path.join(artifactsDir, path.basename(a.path))); if (s.size !== a.bytes) artOk = false; }
  catch { artOk = false; }
}
check("every artifact resolves with matching bytes", artOk, feed.artifacts.length + " artifacts");

// 4. Every transcript_ref names a file present under the records root.
let trOk = true;
for (const r of feed.historical_runs) if (r.transcript_ref) {
  try { await stat(path.join(recordsDir, r.run, "opening-transcript.json")); } catch { trOk = false; }
}
check("every transcript_ref verified present", trOk);

// 5. Totals reconcile with the verified figures for the record set.
//    Set of 2026-11-25, as verified at Gate 3; demo-gptoss6 (Ben's
//    ordered office-cycle-v2 proof run, 2026-11-25) added 1 run,
//    111 events, 10 dispatches, 14 iterations, no filing.
//    demo-gptoss7 (office-cycle-v3, stalled at the first call on
//    Groq's wire metering) added 1 run, 21 events, 0 dispatches,
//    1 iteration, no filing; demo-gptoss10 (office-cycle-v7,
//    stalled at iteration 2 on Groq's daily token limit) added
//    1 run, 29 events, 1 dispatch, 2 iterations, no filing.
const t = feed.historical_runs.reduce((a, r) => ({ runs: a.runs + 1, events: a.events + r.events, dispatches: a.dispatches + r.dispatches,
  iterations: a.iterations + r.iterations, filed: a.filed + (r.brief_filed ? 1 : 0),
  completed: a.completed + (r.outcome === "completed" ? 1 : 0), stalled: a.stalled + (r.outcome === "stalled" ? 1 : 0),
  declined: a.declined + (r.outcome === "declined" ? 1 : 0) }), { runs: 0, events: 0, dispatches: 0, iterations: 0, filed: 0, completed: 0, stalled: 0, declined: 0 });
const exp = { runs: 20, completed: 5, stalled: 14, declined: 1, events: 1036, dispatches: 73, iterations: 97, filed: 3 };
check("totals reconcile with the verified figures", Object.keys(exp).every(k => t[k] === exp[k]), JSON.stringify(t));

console.log(fails ? fails + " FAILURES" : "ALL 5 TESTS PASS");
process.exit(fails ? 1 : 0);
