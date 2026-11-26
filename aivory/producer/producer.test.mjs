// Producer tests — the five tests named in the build spec.
// Usage: node producer.test.mjs --records <live-demo dir> --feed <generated feed.json> --artifacts-dir <dir>
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

// 5. Totals reconcile with the legacy-verified figures for the 2026-11-25 record set.
const t = feed.historical_runs.reduce((a, r) => ({ runs: a.runs + 1, events: a.events + r.events, dispatches: a.dispatches + r.dispatches,
  iterations: a.iterations + r.iterations, filed: a.filed + (r.brief_filed ? 1 : 0),
  completed: a.completed + (r.outcome === "completed" ? 1 : 0), stalled: a.stalled + (r.outcome === "stalled" ? 1 : 0),
  declined: a.declined + (r.outcome === "declined" ? 1 : 0) }), { runs: 0, events: 0, dispatches: 0, iterations: 0, filed: 0, completed: 0, stalled: 0, declined: 0 });
const exp = { runs: 17, completed: 4, stalled: 12, declined: 1, events: 875, dispatches: 62, iterations: 80, filed: 3 };
check("totals reconcile with the legacy-verified figures", Object.keys(exp).every(k => t[k] === exp[k]), JSON.stringify(t));

console.log(fails ? fails + " FAILURES" : "ALL 5 TESTS PASS");
process.exit(fails ? 1 : 0);
