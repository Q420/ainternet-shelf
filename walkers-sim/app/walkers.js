// Walkers Sim — Stage A: physics quadruped (no brain yet).
// Governing sheets: SPEC-SHEET-01 (EXP-CONFIG v1), BUILD-SHEET-01 Stage A.
import { World, Vec2, Box, Circle, RevoluteJoint } from "./vendor/planck.mjs";

export const CFG = {
  gravity: -9.8, step: 1 / 60, velIters: 8, posIters: 3,
  torso: { w: 0.9, h: 0.3, density: 5 },
  leg: { thigh: 0.45, shin: 0.45, thick: 0.09, density: 2 },
  hipRange: 0.9, kneeMin: -1.6, kneeMax: 0,
  footR: 0.06, footFriction: 0.9,
  groundFriction: 1.0,
  hipY: -0.12,
  maxMotorTorque: 8, motorSpeedCap: 6,
};
// All creature fixtures share this NEGATIVE collision group: creature parts
// never collide with each other (co-located leg pairs pass through), while
// creature-vs-ground (group 0) collides normally.
export const CREATURE_GROUP = -1;

export function buildWorld() {
  const world = new World({ gravity: new Vec2(0, CFG.gravity) });
  const ground = world.createBody({ type: "static", position: new Vec2(0, 0) });
  ground.createFixture({ shape: new Box(60, 0.5, new Vec2(0, -0.5)), friction: CFG.groundFriction, restitution: 0, userData: { ground: true } });
  return { world, ground };
}

// Four legs: front pair + back pair, anchors offset by 0.04 m within each pair
// so no two bodies are perfectly coincident. 8 revolute joints, motors OFF
// (Stage A is a doll). Returns parts in render order.
export function buildQuadruped(world, spawnTorsoY) {
  const parts = [];
  const joints = [];
  const add = (name, body) => { parts.push({ name, body }); return body; };
  const fix = (shape, density, friction) => ({ shape, density, friction, filterGroupIndex: CREATURE_GROUP });

  const torso = add("torso", world.createBody({ type: "dynamic", position: new Vec2(0, spawnTorsoY) }));
  torso.createFixture({ shape: new Box(CFG.torso.w / 2, CFG.torso.h / 2), density: CFG.torso.density, friction: 0.5, filterGroupIndex: CREATURE_GROUP, userData: { torso: true } });

  const legDefs = [
    { name: "front-a", hipX: 0.30 }, { name: "front-b", hipX: 0.34 },
    { name: "back-a", hipX: -0.34 }, { name: "back-b", hipX: -0.30 },
  ];
  const legs = [];
  let legIndex = 0;
  for (const def of legDefs) {
    const hipPos = new Vec2(def.hipX, spawnTorsoY + CFG.hipY);
    const thigh = add(def.name + "-thigh", world.createBody({ type: "dynamic", position: new Vec2(hipPos.x, hipPos.y - CFG.leg.thigh / 2) }));
    thigh.createFixture(fix(new Box(CFG.leg.thick / 2, CFG.leg.thigh / 2), CFG.leg.density, 0.5));
    const kneePos = new Vec2(hipPos.x, hipPos.y - CFG.leg.thigh);
    const shin = add(def.name + "-shin", world.createBody({ type: "dynamic", position: new Vec2(kneePos.x, kneePos.y - CFG.leg.shin / 2) }));
    shin.createFixture(fix(new Box(CFG.leg.thick / 2, CFG.leg.shin / 2), CFG.leg.density, 0.5));
    shin.createFixture({ shape: new Circle(new Vec2(0, -CFG.leg.shin / 2), CFG.footR), density: CFG.leg.density, friction: CFG.footFriction, filterGroupIndex: CREATURE_GROUP, userData: { foot: legIndex } });

    const hipJoint = new RevoluteJoint({
      bodyA: torso, bodyB: thigh,
      localAnchorA: new Vec2(def.hipX, CFG.hipY), localAnchorB: new Vec2(0, CFG.leg.thigh / 2),
      lowerAngle: -CFG.hipRange, upperAngle: CFG.hipRange, enableLimit: true,
      enableMotor: false, maxMotorTorque: CFG.maxMotorTorque,
    });
    const kneeJoint = new RevoluteJoint({
      bodyA: thigh, bodyB: shin,
      localAnchorA: new Vec2(0, -CFG.leg.thigh / 2), localAnchorB: new Vec2(0, CFG.leg.shin / 2),
      lowerAngle: CFG.kneeMin, upperAngle: CFG.kneeMax, enableLimit: true,
      enableMotor: false, maxMotorTorque: CFG.maxMotorTorque,
    });
    world.createJoint(hipJoint);
    world.createJoint(kneeJoint);
    joints.push(hipJoint, kneeJoint);
    legs.push({ name: def.name, thigh, shin, hipJoint, kneeJoint });
    legIndex++;
  }
  return { torso, parts, legs, joints };
}

// ---- Stage B: contacts, brain, sensors, settle + evaluation ----
// SPEC-SHEET-04 §3 (settle), §4 (brain/sensors), §6 (fitness), §8b (flags).
export const INPUT_COUNT = 27, HIDDEN_COUNT = 16, OUTPUT_COUNT = 8;
export const GENOME_SIZE = INPUT_COUNT * HIDDEN_COUNT + HIDDEN_COUNT + HIDDEN_COUNT * OUTPUT_COUNT + OUTPUT_COUNT; // 584
export const SPAWN_TORSO_Y = 2.6;

export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export function randomGenome(rng) {
  const g = new Array(GENOME_SIZE);
  for (let i = 0; i < GENOME_SIZE; i++) g[i] = rng() * 2 - 1;
  return g;
}
// Genome order (§4): W1 row-major (16x27), b1 (16), W2 row-major (8x16), b2 (8).
export function forwardPass(genome, inputs) {
  const h = new Array(HIDDEN_COUNT);
  for (let j = 0; j < HIDDEN_COUNT; j++) {
    let s = genome[INPUT_COUNT * HIDDEN_COUNT + j];
    const base = j * INPUT_COUNT;
    for (let i = 0; i < INPUT_COUNT; i++) s += genome[base + i] * inputs[i];
    h[j] = Math.tanh(s);
  }
  const w2off = INPUT_COUNT * HIDDEN_COUNT + HIDDEN_COUNT;
  const out = new Array(OUTPUT_COUNT);
  for (let k = 0; k < OUTPUT_COUNT; k++) {
    let s = genome[w2off + HIDDEN_COUNT * OUTPUT_COUNT + k];
    const base = w2off + k * HIDDEN_COUNT;
    for (let j = 0; j < HIDDEN_COUNT; j++) s += genome[base + j] * h[j];
    out[k] = Math.tanh(s) * CFG.motorSpeedCap;
  }
  return out;
}

const clip = v => Math.max(-1, Math.min(1, v));
// Contact state via Planck contact events on the tagged fixtures (§2/§4).
export function attachContacts(world) {
  const state = { contacts: [false, false, false, false], torsoContact: false, beginEvents: 0, endEvents: 0 };
  const classify = c => {
    const pair = [c.getFixtureA(), c.getFixtureB()];
    let foot = -1, torso = false, ground = false;
    for (const f of pair) {
      const ud = f.getUserData();
      if (!ud) continue;
      if (typeof ud.foot === "number") foot = ud.foot;
      if (ud.torso) torso = true;
      if (ud.ground) ground = true;
    }
    return ground ? { foot, torso } : null;
  };
  world.on("begin-contact", c => {
    const hit = classify(c); if (!hit) return;
    state.beginEvents++;
    if (hit.foot >= 0) state.contacts[hit.foot] = true;
    if (hit.torso) state.torsoContact = true;
  });
  world.on("end-contact", c => {
    const hit = classify(c); if (!hit) return;
    state.endEvents++;
    if (hit.foot >= 0) state.contacts[hit.foot] = false;
    if (hit.torso) state.torsoContact = false;
  });
  return state;
}
export function footWorldPoint(leg) {
  return leg.shin.getWorldPoint(new Vec2(0, -CFG.leg.shin / 2));
}
export function footPenetration(quad) {
  let pen = 0;
  for (const leg of quad.legs) pen = Math.max(pen, CFG.footR - footWorldPoint(leg).y);
  return pen;
}
// 27 inputs, §4 order + normalization table.
export function readSensors(quad, contactState, tSec) {
  const tp = quad.torso.getPosition(), tv = quad.torso.getLinearVelocity();
  const inp = new Array(INPUT_COUNT);
  inp[0] = clip(quad.torso.getAngle() / Math.PI);
  inp[1] = clip(quad.torso.getAngularVelocity() / 5);
  inp[2] = clip(tv.x / 5);
  inp[3] = clip(tv.y / 5);
  inp[4] = clip(tp.y / 1.5);
  for (let j = 0; j < 8; j++) {
    const width = j % 2 === 0 ? CFG.hipRange * 2 : (CFG.kneeMax - CFG.kneeMin);
    inp[5 + j] = clip(quad.joints[j].getJointAngle() / width);
    inp[13 + j] = clip(quad.joints[j].getJointSpeed() / 6);
  }
  for (let i = 0; i < 4; i++) inp[21 + i] = contactState.contacts[i] ? 1 : 0;
  inp[25] = Math.sin(2 * Math.PI * tSec);
  inp[26] = Math.cos(2 * Math.PI * tSec);
  return inp;
}
// §3 settle: motors disabled, fresh world, stability held 10 consecutive steps.
export function settleCreature(world, quad, contactState, timeoutSteps) {
  const maxSteps = timeoutSteps || Math.round(5 / CFG.step); // 5 s (SPEC-04 Amendment 1)
  let stableRun = 0, maxPen = 0;
  const history = [];
  for (let s = 1; s <= maxSteps; s++) {
    world.step(CFG.step, CFG.velIters, CFG.posIters);
    maxPen = Math.max(maxPen, footPenetration(quad));
    const tp = quad.torso.getPosition(), tv = quad.torso.getLinearVelocity();
    history.push({ x: tp.x, y: tp.y });
    if (history.length > 10) history.shift();
    let ok = Math.abs(tv.x) < 0.05 && Math.abs(tv.y) < 0.05 && Math.abs(quad.torso.getAngularVelocity()) < 0.1;
    if (ok) for (const j of quad.joints) if (Math.abs(j.getJointSpeed()) >= 0.2) { ok = false; break; }
    if (ok && footPenetration(quad) > 0.005) ok = false;
    if (ok && history.length === 10) {
      const d = Math.hypot(tp.x - history[0].x, tp.y - history[0].y);
      if (d >= 0.005) ok = false;
    }
    if (ok && history.length === 10) stableRun++; else if (!ok) stableRun = 0;
    if (stableRun >= 10) {
      return { ok: true, steps: s, origin: { x: tp.x, y: tp.y }, angle: quad.torso.getAngle(), maxPenetration: maxPen };
    }
  }
  return { ok: false, steps: maxSteps, maxPenetration: maxPen };
}
// Full single evaluation (§3 protocol, §6 scoring, §8b flags).
// Scoring landed with the Stage B harness; qualification stays gated (Stage C).
export function evaluateController(controlFn, opts) {
  const o = opts || {};
  const built = buildWorld();
  const world = built.world;
  const quad = buildQuadruped(world, SPAWN_TORSO_Y);
  const cs = attachContacts(world);
  let mass = 0; for (const p of quad.parts) mass += p.body.getMass();
  const settle = settleCreature(world, quad, cs, o.settleTimeoutSteps);
  if (!settle.ok) {
    return { status: "FAILED-INIT", F: 0, D: 0, T: 0, A: 0, E: 0, flags: ["FAILED-INIT"], settleSteps: settle.steps, stepsScored: 0, maxPenetration: settle.maxPenetration };
  }
  for (const j of quad.joints) j.enableMotor(true);
  const totalSteps = Math.round(12 / CFG.step);
  let prev = null, D = 0, eligSamples = 0, pitchSum = 0, powerSum = 0;
  let unwrapped = 0, prevAngle = quad.torso.getAngle(), omegaInt = 0, maxExcursion = 0, totalVar = 0;
  let unsupported = 0, curUnsup = 0, longestUnsup = 0, transitions = 0, wasSupported = true;
  let maxTorque = 0, maxPen = settle.maxPenetration, terminated = "full", stepsScored = 0;
  for (let s = 1; s <= totalSteps; s++) {
    const t = (s - 1) * CFG.step;
    const inputs = readSensors(quad, cs, t);
    const outputs = controlFn(inputs, t);
    for (let j = 0; j < 8; j++) quad.joints[j].setMotorSpeed(outputs[j]);
    world.step(CFG.step, CFG.velIters, CFG.posIters);
    stepsScored = s;
    maxPen = Math.max(maxPen, footPenetration(quad));
    const tp = quad.torso.getPosition();
    if (!isFinite(tp.x) || !isFinite(tp.y) || !isFinite(quad.torso.getAngle())) { terminated = "nan"; break; }
    let power = 0;
    for (let j = 0; j < 8; j++) {
      const tq = quad.joints[j].getMotorTorque(1 / CFG.step);
      if (Math.abs(tq) > maxTorque) maxTorque = Math.abs(tq);
      power += Math.abs(tq * quad.joints[j].getJointSpeed());
    }
    powerSum += power;
    const pitch = Math.atan2(Math.sin(quad.torso.getAngle()), Math.cos(quad.torso.getAngle()));
    const eligible = tp.y >= 0.55 && Math.abs(pitch) <= 0.6;
    const sample = { x: tp.x, eligible };
    if (prev && prev.eligible && sample.eligible) D += sample.x - prev.x;
    prev = sample;
    if (eligible) { eligSamples++; pitchSum += Math.abs(pitch); }
    const dAng = Math.atan2(Math.sin(quad.torso.getAngle() - prevAngle), Math.cos(quad.torso.getAngle() - prevAngle));
    unwrapped += dAng; totalVar += Math.abs(dAng); prevAngle = quad.torso.getAngle();
    omegaInt += quad.torso.getAngularVelocity() * CFG.step;
    if (Math.abs(unwrapped) > maxExcursion) maxExcursion = Math.abs(unwrapped);
    const supported = cs.contacts.some(Boolean);
    if (!supported) { unsupported++; curUnsup++; if (curUnsup > longestUnsup) longestUnsup = curUnsup; }
    else { if (!wasSupported) transitions++; curUnsup = 0; }
    wasSupported = supported;
    if (cs.torsoContact && s * CFG.step > 0.5) { terminated = "torso-ground"; break; }
  }
  const T = eligSamples * CFG.step;
  const A = eligSamples > 0 ? pitchSum / eligSamples : 0;
  const E = stepsScored > 0 ? (powerSum / stepsScored) / (mass * 9.8 * 1) : 0;
  const flags = [];
  if (terminated === "nan") flags.push("NAN");
  if (maxExcursion >= 2 * Math.PI) flags.push("ROTATOR");
  if (Math.abs(unwrapped - omegaInt) > Math.PI) flags.push("UNRELIABLE");
  const unsupFrac = stepsScored > 0 ? unsupported / stepsScored : 0;
  const longestSec = longestUnsup * CFG.step;
  if (unsupFrac > 0.5 || longestSec > 1.0) flags.push("HOPPER");
  const F = terminated === "nan" ? 0 : 2 * D + 0.3 * T - 2 * A - 0.05 * E;
  return {
    status: terminated === "nan" ? "NAN" : "SCORED", F, D, T, A, E, flags,
    settleSteps: settle.steps, stepsScored, terminated, origin: settle.origin,
    maxTorque, maxPenetration: maxPen, unwrappedAngle: unwrapped, maxExcursion, totalAngularVariation: totalVar,
    unsupportedFraction: unsupFrac, longestUnsupportedSec: longestSec, supportTransitions: transitions, mass,
  };
}

// Genome evaluation = the brain as controller (§4 forward pass).
export function evaluateGenome(genome, opts) {
  return evaluateController((inputs) => forwardPass(genome, inputs), opts);
}
