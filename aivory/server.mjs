import http from "node:http";
import { randomUUID } from "node:crypto";
import { readFile, mkdir, rename, writeFile } from "node:fs/promises";
import path from "node:path";
import { validateFeed } from "./feed-contract.mjs";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(ROOT, ".data");
const STATE_FILE = path.join(DATA_DIR, "state.json");
const FEED_URL = "https://raw.githubusercontent.com/Q420/ainternet-shelf/main/aivory/feed.json";
const HOST = process.env.HOST || "127.0.0.1";
const PORT = Number(process.env.PORT || 4173);

const blankState = () => ({ messages: { orchestrator: [], collaboration: [] }, jobs: [] });
async function readState() {
  try {
    const parsed = JSON.parse(await readFile(STATE_FILE, "utf8"));
    return {
      messages: parsed.messages && typeof parsed.messages === "object" ? parsed.messages : {},
      jobs: Array.isArray(parsed.jobs) ? parsed.jobs : []
    };
  } catch { return blankState(); }
}
let state = await readState();
let writeChain = Promise.resolve();
function persist() {
  writeChain = writeChain.then(async () => {
    await mkdir(DATA_DIR, { recursive: true });
    const temp = STATE_FILE + ".tmp";
    await writeFile(temp, JSON.stringify(state, null, 2), "utf8");
    await rename(temp, STATE_FILE);
  });
  return writeChain;
}
function send(res, status, body, type = "application/json; charset=utf-8") {
  res.writeHead(status, { "Content-Type": type, "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" });
  res.end(type.startsWith("application/json") ? JSON.stringify(body) : body);
}
async function bodyJson(req) {
  let raw = "";
  for await (const chunk of req) {
    raw += chunk;
    if (raw.length > 20000) throw new Error("Request body too large");
  }
  return JSON.parse(raw || "{}");
}
const stamp = () => new Date().toLocaleString("en-CA", { dateStyle: "medium", timeStyle: "medium" });
function ensureThread(key) { state.messages[key] ||= []; }

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || "/", "http://localhost");
  try {
    if (req.method === "GET" && (url.pathname === "/" || url.pathname === "/aivory/index.html")) {
      const html = await readFile(path.join(ROOT, "index.html"), "utf8");
      return send(res, 200, html, "text/html; charset=utf-8");
    }
    if (req.method === "GET" && url.pathname === "/api/state") return send(res, 200, state);
    if (req.method === "GET" && url.pathname === "/api/feed") {
      const upstream = await fetch(FEED_URL, { cache: "no-store", headers: { "Accept": "application/json" } });
      if (!upstream.ok) return send(res, 502, { error: "State feed unreachable", upstream_status: upstream.status });
      const data = await upstream.json();
      const validation = validateFeed(data);
      if (!validation.ok) return send(res, 502, { error: "State feed failed schema validation", reason: validation.reason });
      return send(res, 200, data);
    }
    if (req.method === "POST" && url.pathname === "/api/jobs") {
      const input = await bodyJson(req);
      const text = typeof input.text === "string" ? input.text.trim() : "";
      if (!text || text.length > 8000) return send(res, 400, { error: "Job text must be 1–8000 characters" });
      const time = stamp();
      const job = { id: randomUUID(), text, time, status: "QUEUED", created_at: new Date().toISOString() };
      state.jobs.push(job);
      ensureThread("orchestrator");
      state.messages.orchestrator.push(
        { kind: "user", author: "BEN", time, text },
        { kind: "system", author: "SYSTEM", time, text: "Job request stored as QUEUED by the dashboard server. Framework dispatch is the next layer; no agent has been started." }
      );
      await persist();
      return send(res, 201, { ok: true, state });
    }
    if (req.method === "POST" && url.pathname === "/api/messages") {
      const input = await bodyJson(req);
      const key = typeof input.key === "string" ? input.key : "";
      const text = typeof input.text === "string" ? input.text.trim() : "";
      if (!(key === "collaboration" || /^office:[a-zA-Z0-9._-]{1,100}$/.test(key))) return send(res, 400, { error: "Unknown conversation" });
      if (!text || text.length > 8000) return send(res, 400, { error: "Message must be 1–8000 characters" });
      const time = stamp();
      ensureThread(key);
      state.messages[key].push({ kind: "user", author: "BEN", time, text });
      if (key.startsWith("office:")) state.messages[key].push({ kind: "system", author: "SYSTEM", time, text: "QUEUED · Message stored by the dashboard server. Live office conversation wiring is not connected." });
      await persist();
      return send(res, 201, { ok: true, state });
    }
    return send(res, 404, { error: "Not found" });
  } catch (error) {
    const status = error.message === "Request body too large" ? 413 : 500;
    return send(res, status, { error: status === 413 ? error.message : "Dashboard server error" });
  }
});

server.listen(PORT, HOST, () => {
  process.stdout.write("AIvory dashboard listening on http://" + HOST + ":" + PORT + "\n");
});