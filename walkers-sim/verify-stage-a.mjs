// Stage A acceptance harness: drop test + render parity, computed independently.
import { chromium } from "playwright-core";

const EXE = "/home/hatch/.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell";
const browser = await chromium.launch({ executablePath: EXE, args: ["--no-sandbox"] });
const page = await browser.newPage({ viewport: { width: 1100, height: 800 } });
page.on("pageerror", e => console.log("PAGE ERROR:", e.message));
await page.goto("http://127.0.0.1:8918/index.html");
await page.waitForFunction(() => window.__WT && window.__WT.frames() > 5);

const samples = [];
for (let i = 0; i < 10; i++) {
  const s = await page.evaluate(() => {
    const bodies = window.__WT.bodies();
    const torso = bodies.find(b => b.name === "torso");
    const v = window.__WT.velocity();
    const nan = bodies.some(b => !isFinite(b.x) || !isFinite(b.y) || !isFinite(b.angle));
    const minY = Math.min(...bodies.map(b => b.y));
    return { torsoY: torso.y, torsoX: torso.x, vx: v.x, vy: v.y, nan, minY, frames: window.__WT.frames() };
  });
  samples.push(s);
  await new Promise(r => setTimeout(r, 400));
}

const parity = await page.evaluate(() => {
  // INDEPENDENT projection: recompute from first principles, not via __WT.project.
  const bodies = window.__WT.bodies();
  const rects = window.__WT.rects();
  const torso = bodies.find(b => b.name === "torso");
  const SCALE = 60, camX = torso.x;
  let maxDiff = 0, worst = null;
  for (const b of bodies) {
    const px = window.innerWidth / 2 + (b.x - camX) * SCALE;
    const py = window.innerHeight * 0.78 - b.y * SCALE;
    const r = rects.find(r => r.name === b.name);
    const d = Math.hypot(r.cx - px, r.cy - py);
    if (d > maxDiff) { maxDiff = d; worst = b.name; }
  }
  return { maxDiff, worst };
});

await browser.close();
const first = samples[0], lastS = samples[samples.length - 1];
console.log("samples (torsoY):", samples.map(s => s.torsoY.toFixed(2)).join(" -> "));
console.log("final torso:", { x: lastS.torsoX.toFixed(3), y: lastS.torsoY.toFixed(3), vx: lastS.vx.toFixed(4), vy: lastS.vy.toFixed(4) });
console.log("any NaN:", samples.some(s => s.nan), "| lowest body centre y:", Math.min(...samples.map(s => s.minY)).toFixed(3));
console.log("parity: max centre diff =", parity.maxDiff.toFixed(2), "px (worst:", parity.worst + ")");
const settled = Math.abs(lastS.vy) < 0.05 && Math.abs(lastS.vx) < 0.05;
const stableBand = lastS.torsoY > 0.3 && lastS.torsoY < 1.15;
console.log("settled:", settled, "| torso rest height in sane band (0.3–1.15):", stableBand);
console.log("ACCEPTANCE:", (!samples.some(s => s.nan) && settled && stableBand && parity.maxDiff <= 2) ? "PASS" : "CHECK");
