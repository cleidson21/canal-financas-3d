// Volumes de colisão aproximados (cápsulas, esferas, caixas arredondadas) presos às
// juntas. Usados só na auditoria: "nenhuma peça atravessa outra".
import * as THREE from 'three';

export function bipedProxies(d) {
  const P = [];
  const add = (o) => P.push(o);
  add({ name: 'pelve', joint: 'pelvis', type: 'box', center: [0, 0, 0], half: [d.pelve.largura / 2, d.pelve.altura / 2, d.pelve.profundidade / 2], r: 0.05 });
  add({
    name: 'tronco',
    joint: 'spine',
    type: 'box',
    center: [0, d.tronco.altura / 2, 0],
    half: [d.tronco.largura / 2, d.tronco.altura / 2, d.tronco.profundidade / 2],
    r: d.tronco.raioCanto,
  });
  add({ name: 'cabeca', joint: 'head', type: 'sphere', center: [0, d.cabeca.centroY, 0], r: d.cabeca.raio });
  for (const s of ['L', 'R']) {
    // braço e coxa começam afastados da junta-mãe (a região do ombro/quadril se sobrepõe por construção)
    add({ name: 'braco' + s, joint: 'upperArm' + s, type: 'capsule', a: [0, -0.3 * d.braco.comprimento, 0], b: [0, -d.braco.comprimento, 0], r: d.braco.raio });
    add({ name: 'antebraco' + s, joint: 'elbow' + s, type: 'capsule', a: [0, 0, 0], b: [0, -d.antebraco.comprimento, 0], r: d.antebraco.raio });
    add({ name: 'mao' + s, joint: 'wrist' + s, type: 'sphere', center: [0, -d.mao.raio * 0.9, 0], r: d.mao.raio * 0.9 });
    add({ name: 'coxa' + s, joint: 'thigh' + s, type: 'capsule', a: [0, -0.35 * d.coxa.comprimento, 0], b: [0, -d.coxa.comprimento, 0], r: d.coxa.raio });
    add({ name: 'canela' + s, joint: 'knee' + s, type: 'capsule', a: [0, 0, 0], b: [0, -d.canela.comprimento, 0], r: d.canela.raio });
    add({
      name: 'pe' + s,
      joint: 'ankle' + s,
      type: 'box',
      center: [0, -d.pe.tornozeloY / 2, d.pe.comprimento / 2 - d.pe.calcanhar],
      half: [d.pe.largura / 2, d.pe.tornozeloY / 2, d.pe.comprimento / 2],
      r: 0.025,
    });
  }
  return P;
}

// Pares que se tocam por construção (vizinhos na hierarquia).
const ADJ = new Set(
  ['pelve|tronco', 'pelve|coxaL', 'pelve|coxaR', 'bracoL|antebracoL', 'bracoR|antebracoR', 'antebracoL|maoL', 'antebracoR|maoR', 'coxaL|canelaL', 'coxaR|canelaR', 'canelaL|peL', 'canelaR|peR'].flatMap((p) => [p, p.split('|').reverse().join('|')]),
);

const v3 = (a) => new THREE.Vector3(...a);

function world(prx, obj) {
  obj.updateWorldMatrix(true, false);
  // escala do objeto (ex.: itens da torre): distâncias e raios saem em metros de mundo
  const sc = obj.matrixWorld.getMaxScaleOnAxis();
  const w = { ...prx, obj, sc, rw: prx.r * sc };
  if (prx.type === 'capsule') {
    w.A = obj.localToWorld(v3(prx.a));
    w.B = obj.localToWorld(v3(prx.b));
  } else if (prx.type === 'sphere') {
    w.C = obj.localToWorld(v3(prx.center));
  } else {
    w.inv = obj.matrixWorld.clone().invert();
    // pontos do núcleo da caixa (para testar caixa contra caixa)
    const core = prx.half.map((h) => Math.max(0, h - prx.r));
    w.samples = [];
    for (const i of [-1, 0, 1]) for (const j of [-1, 0, 1]) for (const k of [-1, 0, 1])
      w.samples.push(obj.localToWorld(new THREE.Vector3(prx.center[0] + i * core[0], prx.center[1] + j * core[1], prx.center[2] + k * core[2])));
  }
  return w;
}

function boxSdf(w, p) {
  const q = p.clone().applyMatrix4(w.inv).sub(v3(w.center));
  const core = w.half.map((h) => Math.max(0, h - w.r));
  const dx = Math.abs(q.x) - core[0];
  const dy = Math.abs(q.y) - core[1];
  const dz = Math.abs(q.z) - core[2];
  const out = Math.hypot(Math.max(dx, 0), Math.max(dy, 0), Math.max(dz, 0));
  return (out + Math.min(Math.max(dx, dy, dz), 0) - w.r) * w.sc;
}

function segSeg(p1, q1, p2, q2) {
  const d1 = q1.clone().sub(p1);
  const d2 = q2.clone().sub(p2);
  const r = p1.clone().sub(p2);
  const a = d1.dot(d1);
  const e = d2.dot(d2);
  const f = d2.dot(r);
  let s;
  let t;
  const c = d1.dot(r);
  const b = d1.dot(d2);
  const den = a * e - b * b;
  s = den > 1e-12 ? THREE.MathUtils.clamp((b * f - c * e) / den, 0, 1) : 0;
  t = (b * s + f) / e;
  if (t < 0) {
    t = 0;
    s = THREE.MathUtils.clamp(-c / a, 0, 1);
  } else if (t > 1) {
    t = 1;
    s = THREE.MathUtils.clamp((b - c) / a, 0, 1);
  }
  return p1.clone().addScaledVector(d1, s).distanceTo(p2.clone().addScaledVector(d2, t));
}

function pointSeg(p, a, b) {
  const ab = b.clone().sub(a);
  const t = THREE.MathUtils.clamp(p.clone().sub(a).dot(ab) / ab.dot(ab), 0, 1);
  return p.distanceTo(a.clone().addScaledVector(ab, t));
}

const segPoints = (w, n = 10) => Array.from({ length: n + 1 }, (_, i) => w.A.clone().lerp(w.B, i / n));

// Distância entre superfícies (negativa = penetração).
export function distance(a, b) {
  if (a.type === 'box' && b.type !== 'box') return distance(b, a);
  if (a.type === 'sphere' && b.type === 'capsule') return distance(b, a);
  if (a.type === 'capsule' && b.type === 'capsule') return segSeg(a.A, a.B, b.A, b.B) - a.rw - b.rw;
  if (a.type === 'capsule' && b.type === 'sphere') return pointSeg(b.C, a.A, a.B) - a.rw - b.rw;
  if (a.type === 'sphere' && b.type === 'sphere') return a.C.distanceTo(b.C) - a.rw - b.rw;
  if (a.type === 'capsule' && b.type === 'box') return Math.min(...segPoints(a).map((p) => boxSdf(b, p))) - a.rw;
  if (a.type === 'sphere' && b.type === 'box') return boxSdf(b, a.C) - a.rw;
  // caixa x caixa: pontos do núcleo de b (com raio de b) contra o SDF de a
  return Math.min(...b.samples.map((p) => boxSdf(a, p))) - b.rw;
}

// proxies: [{..., joint}] resolvidos em joints; extras: [{..., obj}] (objetos segurados)
export function resolveProxies(proxies, joints) {
  return proxies.map((p) => world(p, p.obj || joints[p.joint]));
}

export function collisions(resolved, { tol = 0.004, skip = ADJ, only = null } = {}) {
  const out = [];
  for (let i = 0; i < resolved.length; i++)
    for (let k = i + 1; k < resolved.length; k++) {
      const a = resolved[i];
      const b = resolved[k];
      if (skip.has(`${a.name}|${b.name}`)) continue;
      if (only && !only(a, b)) continue;
      const dist = distance(a, b);
      if (dist < -tol) out.push({ a: a.name, b: b.name, penetracao: -dist });
    }
  return out;
}

