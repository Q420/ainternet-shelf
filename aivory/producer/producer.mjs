// AIvory feed producer — generates the v1 state feed from the framework's
// real run records. Spec: ben-teamily/BUILD-SPEC-AIVORY-PRODUCER-2026-11-25.md
// Usage: node producer.mjs --records <live-demo dir> --out <feed.json> --artifacts-dir <dir>
//
// Fails closed (Gate 3 corrections G3-02/G3-03; re-examination
// 2026-11-26): a report that is present but malformed, unreadable, or
// structurally incomplete stops generation; lifecycle data is validated
// (loop_result.ok a boolean, loop_result.outcome a recognised value,
// the pair consistent) before any classification; a filing record
// without a well-formed sha256 digest stops generation; a digest
// mismatch stops generation. Generation and validation write nothing.
// Publication is staged and generation-safe: artifact files are
// immutable and content-versioned (their names carry the full filing
// digest), so a new generation never replaces a file any published
// feed references. Publication is no-clobber: an artifact destination
// that already exists is verified against its digest and left
// untouched; one occupied by different content fails closed. New
// artifacts are written under temporary names and renamed into place,
// and the feed is renamed last as the single switch — any failure
// before that switch leaves the previous feed and every artifact it
// references byte-identical.
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
  if (typeof lr.ok !== "boolean") fail(`${run}: loop_result.ok is missing or not a boolean`);
  if (!["yield", "decline", "stalled"].includes(lr.outcome)) fail(`${run}: loop_result.outcome is missing or not a recognised value (${JSON.stringify(lr.outcome)})`);
  if (!isCount(lr.iterations)) fail(`${run}: loop_result.iterations is missing or not a non-negative integer`);
  if (!isCount(report.event_count)) fail(`${run}: event_count is missing or not a non-negative integer`);
  let dispatches;
  if (Array.isArray(report.dispatches)) dispatches = report.dispatches.length;
  else if (isCount(report.dispatches)) dispatches = report.dispatches;
  else fail(`${run}: dispatches is missing or malformed`);
  // Classification is defined only for the lifecycle pairs the records
  // actually carry; any other pair is inconsistent data and fails closed.
  let outcome;
  if (lr.ok === true && lr.outcome === "yield") outcome = "completed";
  else if (lr.ok === true && lr.outcome === "decline") outcome = "declined";
  else if (lr.ok === false && lr.outcome === "stalled") outcome = "stalled";
  else fail(`${run}: inconsistent lifecycle pair (ok=${lr.ok}, outcome=${JSON.stringify(lr.outcome)})`);
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
    const name = `${run}-brief-${digest}.md`;
    stagedArtifacts.push({ name: `${run} brief`, path: `aivory/artifacts/${name}`, bytes: briefBuf.length,
      source_ref: `collaboration-framework/live-demo/${run}/brief.md`, buf: briefBuf, file: name, digest });
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
  artifacts: stagedArtifacts.map(({ buf, file, digest, ...rest }) => rest),
  decisions: null };

const verdict = validateFeed(feed);
if (!verdict.ok) fail("generated feed does not validate — " + verdict.reason);

// Publication: no-clobber for artifacts — a destination that already
// exists is verified against the filing digest and left untouched; a
// destination occupied by different content fails closed. New
// artifacts are written under temporary names and renamed into place.
// The feed is then renamed last as the single atomic switch.
await mkdir(artifactsDir, { recursive: true });
for (const a of stagedArtifacts) {
  const dest = path.join(artifactsDir, a.file);
  let existing = null;
  try { existing = await readFile(dest); }
  catch (e) { if (e.code !== "ENOENT") fail(`artifact destination is present but unreadable: ${a.file} (${e.code || e.message})`); }
  if (existing) {
    if (sha256(existing) !== a.digest) fail(`artifact destination already occupied by different content: ${a.file}`);
    continue;
  }
  await writeFile(dest + ".tmp", a.buf);
  await rename(dest + ".tmp", dest);
}
await writeFile(outFile + ".tmp", JSON.stringify(feed, null, 2) + "\n", "utf8");
await rename(outFile + ".tmp", outFile);

const totals = runs.reduce((a, r) => ({ runs: a.runs + 1, events: a.events + r.events, dispatches: a.dispatches + r.dispatches,
  iterations: a.iterations + r.iterations, filed: a.filed + (r.brief_filed ? 1 : 0),
  completed: a.completed + (r.outcome === "completed" ? 1 : 0), stalled: a.stalled + (r.outcome === "stalled" ? 1 : 0),
  declined: a.declined + (r.outcome === "declined" ? 1 : 0) }), { runs: 0, events: 0, dispatches: 0, iterations: 0, filed: 0, completed: 0, stalled: 0, declined: 0 });
console.log("generated:", JSON.stringify(totals));
console.log("validated as feed v" + verdict.version + " -> " + outFile);
