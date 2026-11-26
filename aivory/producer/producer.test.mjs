// Producer test suite (Gate 3 correction G3-04) — source-driven tests that
// execute the producer against isolated fixture records, including its
// failure paths. Discovered by `npm test` (node --test); needs no arguments.
// The standing-record audit lives in producer.audit.mjs.
import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtemp, mkdir, writeFile, readFile, stat, rm } from "node:fs/promises";
import { createHash } from "node:crypto";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const PRODUCER = path.join(path.dirname(fileURLToPath(import.meta.url)), "producer.mjs");
const sha256 = text => createHash("sha256").update(text).digest("hex");
const BRIEF = "one two three four five six seven";

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
  for (const run of ["demo-round6", "demo-aaa", "demo-bbb"]) {
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
  assert.equal(feed.artifacts.length, 1);
  const art = await stat(path.join(artifactsDir, "demo-round6-brief.md"));
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
