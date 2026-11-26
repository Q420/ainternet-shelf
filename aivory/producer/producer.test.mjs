// Producer test suite (Gate 3 correction G3-04) — source-driven tests that
// execute the producer against isolated fixture records, including its
// failure paths. Discovered by `npm test` (node --test); needs no arguments.
// The standing-record audit lives in producer.audit.mjs.
import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtemp, mkdir, writeFile, readFile, stat, rm, chmod } from "node:fs/promises";
import { createHash } from "node:crypto";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const PRODUCER = path.join(path.dirname(fileURLToPath(import.meta.url)), "producer.mjs");
const sha256 = text => createHash("sha256").update(text).digest("hex");
const BRIEF = "one two three four five six seven";
const BRIEF7 = "alpha beta gamma delta";

async function fixtureRecords() {
  const root = await mkdtemp(path.join(os.tmpdir(), "aivory-producer-test-"));
  const records = path.join(root, "records");
  const write = async (rel, content) => {
    const p = path.join(records, rel);
    await mkdir(path.dirname(p), { recursive: true });
    await writeFile(p, content);
  };
  // demo-round6: a completed run (loop yielded) with a properly filed brief and a transcript.
  await write("demo-round6/report.json", JSON.stringify({
    loop_result: { ok: true, outcome: "yield", iterations: 2 },
    event_count: 10, dispatches: [{}, {}, {}],
    brief_filed: { sha256: sha256(BRIEF), authored_by: "worker", filed_by: "office" }
  }));
  await write("demo-round6/brief.md", BRIEF);
  await write("demo-round6/opening-transcript.json", "{}");
  await write("demo-round6/run/sandbox/sources/stock-take.md", "AAAA");
  await write("demo-round6/run/sandbox/sources/a3-pass.md", "BB");
  await write("demo-round6/run/sandbox/sources/index-tail.md", "CCC");
  // demo-round7: a second completed run with its own filed brief (no transcript).
  await write("demo-round7/report.json", JSON.stringify({
    loop_result: { ok: true, outcome: "yield", iterations: 3 },
    event_count: 20, dispatches: [{}],
    brief_filed: { sha256: sha256(BRIEF7), authored_by: "worker", filed_by: "office" }
  }));
  await write("demo-round7/brief.md", BRIEF7);
  // demo-aaa: a stalled run.
  await write("demo-aaa/report.json", JSON.stringify({
    loop_result: { ok: false, outcome: "stalled", iterations: 1 },
    event_count: 4, dispatches: []
  }));
  // demo-bbb: a declined run.
  await write("demo-bbb/report.json", JSON.stringify({
    loop_result: { ok: true, outcome: "decline", iterations: 1 },
    event_count: 2, dispatches: [{}]
  }));
  // demo-empty: no report.json — not a report-bearing directory.
  await mkdir(path.join(records, "demo-empty"), { recursive: true });
  return { root, records };
}

function runProducer(records, out, artifactsDir) {
  return spawnSync(process.execPath,
    [PRODUCER, "--records", records, "--out", out, "--artifacts-dir", artifactsDir],
    { encoding: "utf8" });
}

async function expectFailure(mutate, label) {
  const { root, records } = await fixtureRecords();
  await mutate(records);
  const out = path.join(root, "feed.json");
  const res = runProducer(records, out, path.join(root, "artifacts"));
  assert.notEqual(res.status, 0, label + ": producer must exit non-zero");
  await assert.rejects(stat(out), label + ": no feed may be written on failure");
  await rm(root, { recursive: true, force: true });
}

test("generates a truthful v1 feed from fixture records", async () => {
  const { root, records } = await fixtureRecords();
  const out = path.join(root, "feed.json");
  const artifactsDir = path.join(root, "artifacts");
  const res = runProducer(records, out, artifactsDir);
  assert.equal(res.status, 0, res.stderr);
  const feed = JSON.parse(await readFile(out, "utf8"));
  assert.equal(feed.schema_version, 1);
  // Expected values derived independently from the fixture source reports.
  const expected = { runs: 0, events: 0, dispatches: 0, iterations: 0 };
  for (const run of ["demo-round6", "demo-round7", "demo-aaa", "demo-bbb"]) {
    const report = JSON.parse(await readFile(path.join(records, run, "report.json"), "utf8"));
    expected.runs++; expected.events += report.event_count;
    expected.dispatches += report.dispatches.length;
    expected.iterations += report.loop_result.iterations;
  }
  const totals = feed.historical_runs.reduce((a, r) => ({
    runs: a.runs + 1, events: a.events + r.events,
    dispatches: a.dispatches + r.dispatches, iterations: a.iterations + r.iterations
  }), { runs: 0, events: 0, dispatches: 0, iterations: 0 });
  assert.deepEqual(totals, expected);
  const byRun = Object.fromEntries(feed.historical_runs.map(r => [r.run, r]));
  assert.equal(byRun["demo-round6"].outcome, "completed");
  assert.equal(byRun["demo-round6"].completed, true);
  assert.equal(byRun["demo-aaa"].outcome, "stalled");
  assert.equal(byRun["demo-bbb"].outcome, "declined");
  assert.equal(byRun["demo-bbb"].completed, false); // declined: finished, not completed
  assert.equal(byRun["demo-round6"].brief_words, 7);
  assert.ok(byRun["demo-round6"].transcript_ref);
  assert.equal(feed.offices.length, 0);
  assert.equal(feed.decisions, null); // unavailable, never an empty queue
  assert.equal(feed.artifacts.length, 2);
  // Artifact filenames are immutable and content-versioned by filing digest.
  const art6 = feed.artifacts.find(a => a.path.includes("demo-round6"));
  const art7 = feed.artifacts.find(a => a.path.includes("demo-round7"));
  assert.ok(art6.path.endsWith(`demo-round6-brief-${sha256(BRIEF)}.md`), art6.path);
  assert.ok(art7.path.endsWith(`demo-round7-brief-${sha256(BRIEF7)}.md`), art7.path);
  const art = await stat(path.join(artifactsDir, path.basename(art6.path)));
  assert.equal(art.size, Buffer.byteLength(BRIEF));
  assert.deepEqual(feed.job.sources.map(s => s.bytes), [4, 2, 3]);
  await rm(root, { recursive: true, force: true });
});

test("a missing transcript is not an error; the run carries no transcript_ref", async () => {
  const { root, records } = await fixtureRecords();
  await rm(path.join(records, "demo-round6", "opening-transcript.json"));
  const out = path.join(root, "feed.json");
  const res = runProducer(records, out, path.join(root, "artifacts"));
  assert.equal(res.status, 0, res.stderr);
  const feed = JSON.parse(await readFile(out, "utf8"));
  const r6 = feed.historical_runs.find(r => r.run === "demo-round6");
  assert.equal(r6.transcript_ref, undefined);
  await rm(root, { recursive: true, force: true });
});

test("fails closed on malformed report JSON", () =>
  expectFailure(async records => {
    await writeFile(path.join(records, "demo-aaa", "report.json"), "{not json");
  }, "malformed JSON"));

test("fails closed on a missing counter (no zero defaults)", () =>
  expectFailure(async records => {
    const p = path.join(records, "demo-aaa", "report.json");
    const report = JSON.parse(await readFile(p, "utf8"));
    delete report.event_count;
    await writeFile(p, JSON.stringify(report));
  }, "missing event_count"));

test("fails closed when a filing record carries no digest", () =>
  expectFailure(async records => {
    const p = path.join(records, "demo-round6", "report.json");
    const report = JSON.parse(await readFile(p, "utf8"));
    report.brief_filed = { authored_by: "worker", filed_by: "office" };
    await writeFile(p, JSON.stringify(report));
  }, "filing without digest"));

test("fails closed on a digest mismatch", () =>
  expectFailure(async records => {
    const p = path.join(records, "demo-round6", "report.json");
    const report = JSON.parse(await readFile(p, "utf8"));
    report.brief_filed.sha256 = sha256("some other brief");
    await writeFile(p, JSON.stringify(report));
  }, "digest mismatch"));

test("fails closed when a filed brief file is missing", () =>
  expectFailure(async records => {
    await rm(path.join(records, "demo-round6", "brief.md"));
  }, "filed brief missing"));

test("a failed generation leaves a previously published feed untouched", async () => {
  const { root, records } = await fixtureRecords();
  const p = path.join(records, "demo-round6", "report.json");
  const report = JSON.parse(await readFile(p, "utf8"));
  report.brief_filed.sha256 = sha256("tampered");
  await writeFile(p, JSON.stringify(report));
  const out = path.join(root, "feed.json");
  await writeFile(out, "PREVIOUSLY PUBLISHED");
  const res = runProducer(records, out, path.join(root, "artifacts"));
  assert.notEqual(res.status, 0);
  assert.equal(await readFile(out, "utf8"), "PREVIOUSLY PUBLISHED");
  await rm(root, { recursive: true, force: true });
});

async function mutateReport(records, run, fn) {
  const p = path.join(records, run, "report.json");
  const report = JSON.parse(await readFile(p, "utf8"));
  fn(report);
  await writeFile(p, JSON.stringify(report));
}

test("fails closed when loop_result.outcome is missing", () =>
  expectFailure(records => mutateReport(records, "demo-aaa", r => { delete r.loop_result.outcome; }),
    "missing outcome"));

test("fails closed when loop_result.ok is not a boolean", () =>
  expectFailure(records => mutateReport(records, "demo-aaa", r => { r.loop_result.ok = "false"; }),
    "non-boolean ok"));

test("fails closed on an unrecognised outcome value", () =>
  expectFailure(records => mutateReport(records, "demo-aaa", r => { r.loop_result.outcome = "exploded"; }),
    "unknown outcome"));

test("fails closed on an inconsistent lifecycle pair", () =>
  expectFailure(records => mutateReport(records, "demo-aaa", r => { r.loop_result.ok = true; }),
    "ok=true with outcome=stalled"));

test("a blocked artifacts path fails publication and leaves the feed untouched", async () => {
  const { root, records } = await fixtureRecords();
  const out = path.join(root, "feed.json");
  await writeFile(out, "PREVIOUSLY PUBLISHED");
  const blocked = path.join(root, "artifacts-as-file");
  await writeFile(blocked, "not a directory");
  const res = runProducer(records, out, blocked);
  assert.notEqual(res.status, 0);
  assert.equal(await readFile(out, "utf8"), "PREVIOUSLY PUBLISHED");
  await rm(root, { recursive: true, force: true });
});

async function publishGeneration(root, records) {
  const out = path.join(root, "feed.json");
  const artifactsDir = path.join(root, "artifacts");
  const res = runProducer(records, out, artifactsDir);
  assert.equal(res.status, 0, res.stderr);
  const feed = JSON.parse(await readFile(out, "utf8"));
  const standing = { out, artifactsDir, feedBytes: await readFile(out, "utf8"), artifacts: {} };
  for (const a of feed.artifacts) {
    standing.artifacts[a.path] = await readFile(path.join(artifactsDir, path.basename(a.path)), "utf8");
  }
  return standing;
}

async function assertStandingIntact(standing) {
  assert.equal(await readFile(standing.out, "utf8"), standing.feedBytes);
  for (const [p, bytes] of Object.entries(standing.artifacts)) {
    assert.equal(await readFile(path.join(standing.artifactsDir, path.basename(p)), "utf8"), bytes);
  }
}

test("an occupied artifact destination blocks publication and leaves the standing generation byte-identical", async () => {
  const { root, records } = await fixtureRecords();
  const standing = await publishGeneration(root, records);
  // A new generation: demo-round7's brief changes (with a matching digest).
  const BRIEF7B = "alpha beta gamma delta epsilon";
  await writeFile(path.join(records, "demo-round7", "brief.md"), BRIEF7B);
  await mutateReport(records, "demo-round7", r => { r.brief_filed.sha256 = sha256(BRIEF7B); });
  // Block the new artifact's destination: a directory sits at its versioned path.
  const blockedName = `demo-round7-brief-${sha256(BRIEF7B)}.md`;
  await mkdir(path.join(standing.artifactsDir, blockedName), { recursive: true });
  const res = runProducer(records, standing.out, standing.artifactsDir);
  assert.notEqual(res.status, 0);
  await assertStandingIntact(standing);
  await rm(root, { recursive: true, force: true });
});

test("republishing an unchanged generation reuses artifacts without replacing them", async () => {
  const { root, records } = await fixtureRecords();
  const standing = await publishGeneration(root, records);
  const before = {};
  for (const p of Object.keys(standing.artifacts)) {
    const s = await stat(path.join(standing.artifactsDir, path.basename(p)));
    before[p] = { ino: s.ino, mtimeMs: s.mtimeMs };
  }
  const res = runProducer(records, standing.out, standing.artifactsDir);
  assert.equal(res.status, 0, res.stderr);
  for (const p of Object.keys(standing.artifacts)) {
    const s = await stat(path.join(standing.artifactsDir, path.basename(p)));
    assert.equal(s.ino, before[p].ino, p + ": inode changed — the file was replaced");
    assert.equal(s.mtimeMs, before[p].mtimeMs, p + ": mtime changed — the file was rewritten");
  }
  await rm(root, { recursive: true, force: true });
});

test("a conflicting occupied artifact destination fails closed", async () => {
  const { root, records } = await fixtureRecords();
  const out = path.join(root, "feed.json");
  await writeFile(out, "PREVIOUSLY PUBLISHED");
  const artifactsDir = path.join(root, "artifacts");
  await mkdir(artifactsDir, { recursive: true });
  // Occupy demo-round6's versioned destination with different content.
  await writeFile(path.join(artifactsDir, `demo-round6-brief-${sha256(BRIEF)}.md`), "impostor content");
  const res = runProducer(records, out, artifactsDir);
  assert.notEqual(res.status, 0);
  assert.equal(await readFile(out, "utf8"), "PREVIOUSLY PUBLISHED");
  await rm(root, { recursive: true, force: true });
});

test("failure at the final feed rename leaves the original feed and its artifacts byte-identical", async (t) => {
  if (process.getuid?.() !== 0) { t.skip("requires root to drop privileges for the failing run"); return; }
  const { root, records } = await fixtureRecords();
  // Run a world-readable copy of the producer inside the fixture tree.
  const prodDir = path.join(root, "producer");
  await mkdir(prodDir, { recursive: true });
  const here = path.dirname(fileURLToPath(import.meta.url));
  await writeFile(path.join(prodDir, "producer.mjs"), await readFile(path.join(here, "producer.mjs"), "utf8"));
  await writeFile(path.join(root, "feed-contract.mjs"), await readFile(path.join(here, "..", "feed-contract.mjs"), "utf8"));
  const feedDir = path.join(root, "feedpub");
  const artifactsDir = path.join(root, "artifacts");
  await mkdir(feedDir, { recursive: true });
  const out = path.join(feedDir, "feed.json");
  const runAs = (uid) => spawnSync(process.execPath,
    [path.join(prodDir, "producer.mjs"), "--records", records, "--out", out, "--artifacts-dir", artifactsDir],
    { encoding: "utf8", ...(uid ? { uid, gid: uid } : {}) });
  // Generation 1 publishes normally.
  const gen1 = runAs(0);
  assert.equal(gen1.status, 0, gen1.stderr);
  const feedBytes = await readFile(out, "utf8");
  const gen1Feed = JSON.parse(feedBytes);
  const artifactBytes = {};
  for (const a of gen1Feed.artifacts) {
    artifactBytes[a.path] = await readFile(path.join(artifactsDir, path.basename(a.path)), "utf8");
  }
  // A new generation is pending: demo-round7's brief changed.
  const BRIEF7B = "alpha beta gamma delta epsilon";
  await writeFile(path.join(records, "demo-round7", "brief.md"), BRIEF7B);
  await mutateReport(records, "demo-round7", r => { r.brief_filed.sha256 = sha256(BRIEF7B); });
  // Make the tree readable by the unprivileged user; the artifacts dir
  // stays writable so the new artifacts land; the feed directory becomes
  // read-only, and the feed's temp file is pre-created world-writable so
  // the run reaches the final rename — which then fails with EACCES,
  // while the original feed file stands untouched at its path.
  spawnSync("chmod", ["-R", "a+rX", root]);
  await chmod(artifactsDir, 0o777);
  await writeFile(path.join(feedDir, "feed.json.tmp"), "");
  await chmod(path.join(feedDir, "feed.json.tmp"), 0o666);
  await chmod(feedDir, 0o555);
  const gen2 = runAs(65534);
  await chmod(feedDir, 0o755);
  assert.notEqual(gen2.status, 0, "the rename must fail");
  assert.ok(!/ERR_MODULE_NOT_FOUND|Cannot find module/.test(gen2.stderr), gen2.stderr);
  assert.equal(await readFile(out, "utf8"), feedBytes);
  for (const [p, bytes] of Object.entries(artifactBytes)) {
    assert.equal(await readFile(path.join(artifactsDir, path.basename(p)), "utf8"), bytes);
  }
  await rm(root, { recursive: true, force: true });
});
