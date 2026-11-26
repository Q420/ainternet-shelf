import test from "node:test";
import assert from "node:assert/strict";
import { validateFeed } from "./feed-contract.mjs";

const run = { run: "historical-01", outcome: "completed", iterations: 2, events: 5, dispatches: 1 };
const legacy = { kind: "aivory-state-feed", runs: [run] };
const v1 = {
  kind: "aivory-state-feed",
  schema_version: 1,
  generated_at: "2026-11-25T19:00:00Z",
  job: { title: "A real assignment", sources: [{ path: "sources/brief.md", bytes: 12 }] },
  offices: [{ id: "office-01", role: "Brief Writer", occupant: "model/name", status: "running", journal_ref: "records/office-01/journal.jsonl" }],
  historical_runs: [run],
  artifacts: [{ path: "outputs/brief.md", bytes: 120 }],
  decisions: [{ id: "decision-01", title: "Approve external action", status: "pending" }]
};

test("accepts the explicitly recognized legacy feed as version 0", () => {
  assert.deepEqual(validateFeed(legacy), { ok: true, version: 0, reason: null });
});

test("accepts a complete version 1 feed", () => {
  assert.deepEqual(validateFeed(v1), { ok: true, version: 1, reason: null });
});

test("rejects version 1 without its own generation timestamp", () => {
  const broken = { ...v1 };
  delete broken.generated_at;
  assert.equal(validateFeed(broken).ok, false);
});

test("rejects malformed historical counters", () => {
  const broken = { ...legacy, runs: [{ ...run, events: "five" }] };
  assert.equal(validateFeed(broken).ok, false);
});

test("rejects a historical run presented as a current office without role identity", () => {
  const broken = { ...v1, offices: [{ id: "historical-01", status: "completed" }] };
  assert.equal(validateFeed(broken).ok, false);
});

test("rejects malformed artifact metadata", () => {
  const broken = { ...v1, artifacts: [{ path: "out.md", bytes: -1 }] };
  assert.equal(validateFeed(broken).ok, false);
});
