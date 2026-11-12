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
  maxMotorTorque: 60, motorSpeedCap: 6,
};
// All creature fixtures share this NEGATIVE collision group: creature parts
// never collide with each other (co-located leg pairs pass through), while
// creature-vs-ground (group 0) collides normally.
export const CREATURE_GROUP = -1;

export function buildWorld() {
  const world = new World({ gravity: new Vec2(0, CFG.gravity) });
  const ground = world.createBody({ type: "static", position: new Vec2(0, 0) });
  ground.createFixture({ shape: new Box(60, 0.5, new Vec2(0, -0.5)), friction: CFG.groundFriction, restitution: 0 });
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
  torso.createFixture(fix(new Box(CFG.torso.w / 2, CFG.torso.h / 2), CFG.torso.density, 0.5));

  const legDefs = [
    { name: "front-a", hipX: 0.30 }, { name: "front-b", hipX: 0.34 },
    { name: "back-a", hipX: -0.34 }, { name: "back-b", hipX: -0.30 },
  ];
  const legs = [];
  for (const def of legDefs) {
    const hipPos = new Vec2(def.hipX, spawnTorsoY + CFG.hipY);
    const thigh = add(def.name + "-thigh", world.createBody({ type: "dynamic", position: new Vec2(hipPos.x, hipPos.y - CFG.leg.thigh / 2) }));
    thigh.createFixture(fix(new Box(CFG.leg.thick / 2, CFG.leg.thigh / 2), CFG.leg.density, 0.5));
    const kneePos = new Vec2(hipPos.x, hipPos.y - CFG.leg.thigh);
    const shin = add(def.name + "-shin", world.createBody({ type: "dynamic", position: new Vec2(kneePos.x, kneePos.y - CFG.leg.shin / 2) }));
    shin.createFixture(fix(new Box(CFG.leg.thick / 2, CFG.leg.shin / 2), CFG.leg.density, 0.5));
    shin.createFixture(fix(new Circle(new Vec2(0, -CFG.leg.shin / 2), CFG.footR), CFG.leg.density, CFG.footFriction));

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
  }
  return { torso, parts, legs, joints };
}
