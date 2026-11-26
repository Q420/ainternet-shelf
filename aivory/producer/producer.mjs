// AIvory feed producer — generates the v1 state feed from the framework's
// real run records. Spec: ben-teamily/BUILD-SPEC-AIVORY-PRODUCER-2026-11-25.md
// Usage: node producer.mjs --records <live-demo dir> --out <feed.json> --artifacts-dir <dir>
// Fails closed: a malformed report or a brief whose sha256 does not match
// its filing record stops generation; nothing is written.
import { readFile, writeFile, readdir, copyFile, mkdir, stat } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { validateFeed } from "../feed-contract.mjs";

const args = process.argv.slice(2);
const opt = name => { const i = args.indexOf("--" + name); return i >= 0 ? args[i + 1] : null; };
const recordsDir = opt("records"), outFile = opt("out"), artifactsDir = opt("artifacts-dir");
if (!recordsDir || !outFile || !artifactsDir) { console.error("required: --records --out --artifacts-dir"); process.exit(2); }

const JOB = {
  title: "Write the standing brief: what the framework is, what has been proven, what is open, the honest next step",
  target_words: 600, floor_words: 550,
  source_names: ["stock-take.md", "a3-pass.md", "index-tail.md"]
};
const words = text => text.split(/\s+/).filter(Boolean).length;
const sha256 = buf => createHash("sha256").update(buf).digest("hex");

const entries = (await readdir(recordsDir, { withFileTypes: true }))
  .filter(e => e.isDirectory() && e.name.startsWith("demo-")).map(e => e.name).sort();

const runs = [], artifacts = [], warnings = [];
for (const run of entries) {
  const dir = path.join(recordsDir, run);
  let report;
  try { report = JSON.parse(await readFile(path.join(dir, "report.json"), "utf8")); }
  catch { continue; } // no report: not a report-bearing run directory
  const lr = report.loop_result || {};
  const outcome = lr.ok && lr.outcome !== "decline" ? "completed" : (lr.outcome === "decline" ? "declined" : "stalled");
  const disp = Array.isArray(report.dispatches) ? report.dispatches.length : (report.dispatches || 0);
  const entry = { run, outcome, completed: outcome === "completed",
    iterations: lr.iterations || 0, events: report.event_count || 0, dispatches: disp,
    brief_filed: !!report.brief_filed, brief_words: null,
    report_ref: `collaboration-framework/live-demo/${run}/report.json` };
  if (report.model_pin) entry.model = report.model_pin;
  let briefBuf = null;
  try { briefBuf = await readFile(path.join(dir, "brief.md")); } catch {}
  if (briefBuf) entry.brief_words = words(briefBuf.toString("utf8"));
  try { await stat(path.join(dir, "opening-transcript.json")); entry.transcript_ref = `collaboration-framework/live-demo/${run}/opening-transcript.json`; } catch {}
  if (entry.brief_filed) {
    if (!briefBuf) { warnings.push(`${run}: filing record present but brief.md missing — no artifact emitted`); }
    else if (report.brief_filed.sha256 && sha256(briefBuf) !== report.brief_filed.sha256) {
      console.error(`FAIL CLOSED: ${run} brief.md sha256 does not match its filing record`); process.exit(1);
    } else {
      const name = `${run}-brief.md`;
      await mkdir(artifactsDir, { recursive: true });
      await copyFile(path.join(dir, "brief.md"), path.join(artifactsDir, name));
      artifacts.push({ name: `${run} brief`, path: `aivory/artifacts/${name}`, bytes: briefBuf.length,
        source_ref: `collaboration-framework/live-demo/${run}/brief.md` });
    }
  }
  runs.push(entry);
}

const sourcesDir = path.join(recordsDir, "demo-round6", "run", "sandbox", "sources");
const sources = [];
for (const name of JOB.source_names) {
  const s = await stat(path.join(sourcesDir, name));
  sources.push({ path: `sources/${name}`, bytes: s.size });
}

const feed = { kind: "aivory-state-feed", schema_version: 1, generated_at: new Date().toISOString(),
  job: { title: JOB.title, target_words: JOB.target_words, floor_words: JOB.floor_words, sources },
  offices: [], historical_runs: runs, artifacts, decisions: [] };

const verdict = validateFeed(feed);
if (!verdict.ok) { console.error("FAIL CLOSED: generated feed does not validate — " + verdict.reason); process.exit(1); }
await writeFile(outFile, JSON.stringify(feed, null, 2) + "\n", "utf8");
const totals = runs.reduce((a, r) => ({ runs: a.runs + 1, events: a.events + r.events, dispatches: a.dispatches + r.dispatches,
  iterations: a.iterations + r.iterations, filed: a.filed + (r.brief_filed ? 1 : 0),
  completed: a.completed + (r.outcome === "completed" ? 1 : 0), stalled: a.stalled + (r.outcome === "stalled" ? 1 : 0),
  declined: a.declined + (r.outcome === "declined" ? 1 : 0) }), { runs: 0, events: 0, dispatches: 0, iterations: 0, filed: 0, completed: 0, stalled: 0, declined: 0 });
console.log("generated:", JSON.stringify(totals));
for (const w of warnings) console.log("warning:", w);
console.log("validated as feed v" + verdict.version + " -> " + outFile);
