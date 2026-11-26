// AIvory feed producer — generates the v1 state feed from the framework's
// real run records. Spec: ben-teamily/BUILD-SPEC-AIVORY-PRODUCER-2026-11-25.md
// Usage: node producer.mjs --records <live-demo dir> --out <feed.json> --artifacts-dir <dir>
//
// Fails closed (Gate 3 corrections G3-02/G3-03): a report that is present
// but malformed, unreadable, or structurally incomplete stops generation;
// a filing record without a well-formed sha256 digest stops generation;
// a digest mismatch stops generation. Nothing is written on failure:
// artifacts are staged and copied only after the generated feed validates,
// and the feed itself is written via a temporary file and rename.
// A directory with no report.json at all is not a report-bearing run and
// is skipped — absence is distinguished from corruption.
//
// Field definitions: a run's `completed` is true exactly when its loop
// completed successfully (outcome "completed"). A declined run finished
// but did not complete: completed is false. Feed values are a projection
// from the per-run report.json records (derived matter), named as such
// in the feed's `provenance`.
//
// `decisions` is null: no decision-record source exists, so the decision
// inventory is unavailable — never an empty queue (G3-05).
import { readFile, writeFile, readdir, mkdir, stat, rename } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { validateFeed } from "../feed-contract.mjs";

const args = process.argv.slice(2);
const opt = name => { const i = args.indexOf("--" + name); return i >= 0 ? args[i + 1] : null; };
const recordsDir = opt("records"), outFile = opt("out"), artifactsDir = opt("artifacts-dir");
if (!recordsDir || !outFile || !artifactsDir) { console.error("required: --records --out --artifacts-dir"); process.exit(2); }

const fail = msg => { console.error("FAIL CLOSED: " + msg); process.exit(1); };
const isCount = v => Number.isInteger(v) && v >= 0;

const JOB = {
  title: "Write the standing brief: what the framework is, what has been proven, what is open, the honest next step",
  target_words: 600, floor_words: 550,
  source_names: ["stock-take.md", "a3-pass.md", "index-tail.md"]
};
const words = text => text.split(/\s+/).filter(Boolean).length;
const sha256 = buf => createHash("sha256").update(buf).digest("hex");

const entries = (await readdir(recordsDir, { withFileTypes: true }))
  .filter(e => e.isDirectory() && e.name.startsWith("demo-")).map(e => e.name).sort();

const runs = [], stagedArtifacts = [];
for (const run of entries) {
  const dir = path.join(recordsDir, run);
  let raw;
  try { raw = await readFile(path.join(dir, "report.json"), "utf8"); }
  catch (e) {
    if (e.code === "ENOENT") continue; // no report: not a report-bearing run directory
    fail(`${run}: report.json is present but unreadable (${e.code || e.message})`);
  }
  let report;
  try { report = JSON.parse(raw); }
  catch { fail(`${run}: report.json is malformed JSON`); }
  if (!report || typeof report !== "object" || Array.isArray(report)) fail(`${run}: report is not an object`);
  const lr = report.loop_result;
  if (!lr || typeof lr !== "object" || Array.isArray(lr)) fail(`${run}: loop_result is missing or malformed`);
  if (!isCount(lr.iterations)) fail(`${run}: loop_result.iterations is missing or not a non-negative integer`);
  if (!isCount(report.event_count)) fail(`${run}: event_count is missing or not a non-negative integer`);
  let dispatches;
  if (Array.isArray(report.dispatches)) dispatches = report.dispatches.length;
  else if (isCount(report.dispatches)) dispatches = report.dispatches;
  else fail(`${run}: dispatches is missing or malformed`);
  const outcome = lr.ok && lr.outcome !== "decline" ? "completed" : (lr.outcome === "decline" ? "declined" : "stalled");
  const entry = { run, outcome, completed: outcome === "completed",
    iterations: lr.iterations, events: report.event_count, dispatches,
    brief_filed: !!report.brief_filed, brief_words: null,
    report_ref: `collaboration-framework/live-demo/${run}/report.json` };
  if (report.model_pin) entry.model = report.model_pin;
  let briefBuf = null;
  try { briefBuf = await readFile(path.join(dir, "brief.md")); } catch {}
  if (briefBuf) entry.brief_words = words(briefBuf.toString("utf8"));
  try { await stat(path.join(dir, "opening-transcript.json")); entry.transcript_ref = `collaboration-framework/live-demo/${run}/opening-transcript.json`; } catch {}
  if (entry.brief_filed) {
    const digest = report.brief_filed && report.brief_filed.sha256;
    if (typeof digest !== "string" || !/^[0-9a-f]{64}$/.test(digest)) {
      fail(`${run}: filing record carries no well-formed sha256 digest — no artifact may be emitted`);
    }
    if (!briefBuf) fail(`${run}: filing record present but brief.md is missing`);
    if (sha256(briefBuf) !== digest) fail(`${run}: brief.md sha256 does not match its filing record`);
    const name = `${run}-brief.md`;
    stagedArtifacts.push({ name: `${run} brief`, path: `aivory/artifacts/${name}`, bytes: briefBuf.length,
      source_ref: `collaboration-framework/live-demo/${run}/brief.md`, buf: briefBuf, file: name });
  }
  runs.push(entry);
}

const sourcesDir = path.join(recordsDir, "demo-round6", "run", "sandbox", "sources");
const sources = [];
for (const name of JOB.source_names) {
  let s;
  try { s = await stat(path.join(sourcesDir, name)); }
  catch { fail(`standing job source is missing: ${name}`); }
  sources.push({ path: `sources/${name}`, bytes: s.size });
}

const feed = { kind: "aivory-state-feed", schema_version: 1, generated_at: new Date().toISOString(),
  provenance: "Projected by aivory/producer from the per-run report.json records under collaboration-framework/live-demo (derived matter, not the record itself).",
  job: { title: JOB.title, target_words: JOB.target_words, floor_words: JOB.floor_words, sources },
  offices: [], historical_runs: runs,
  artifacts: stagedArtifacts.map(({ buf, file, ...rest }) => rest),
  decisions: null };

const verdict = validateFeed(feed);
if (!verdict.ok) fail("generated feed does not validate — " + verdict.reason);

// Publication happens only after validation: artifacts first, then the
// feed via a temporary file renamed into place, so a failed generation
// leaves any previously published feed and artifacts untouched.
await mkdir(artifactsDir, { recursive: true });
for (const a of stagedArtifacts) await writeFile(path.join(artifactsDir, a.file), a.buf);
const tmpOut = outFile + ".tmp";
await writeFile(tmpOut, JSON.stringify(feed, null, 2) + "\n", "utf8");
await rename(tmpOut, outFile);

const totals = runs.reduce((a, r) => ({ runs: a.runs + 1, events: a.events + r.events, dispatches: a.dispatches + r.dispatches,
  iterations: a.iterations + r.iterations, filed: a.filed + (r.brief_filed ? 1 : 0),
  completed: a.completed + (r.outcome === "completed" ? 1 : 0), stalled: a.stalled + (r.outcome === "stalled" ? 1 : 0),
  declined: a.declined + (r.outcome === "declined" ? 1 : 0) }), { runs: 0, events: 0, dispatches: 0, iterations: 0, filed: 0, completed: 0, stalled: 0, declined: 0 });
console.log("generated:", JSON.stringify(totals));
console.log("validated as feed v" + verdict.version + " -> " + outFile);
