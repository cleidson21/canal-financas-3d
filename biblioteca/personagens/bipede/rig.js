// Esqueleto bípede de segmentos rígidos (sem skinning). Cada junta é um Group com
// pivô no ponto de articulação. Pose = ângulos semânticos em graus (flexão positiva
// no sentido anatômico) + pés por IK de 2 ossos (pé apoiado fica onde foi posto).
// Convenção: Y para cima, personagem de frente para +Z, esquerda do personagem = +X.
import * as THREE from 'three';
import { DEG, clamp } from '../../nucleo/matematica.js';

const SIDES = { L: 1, R: -1 };

export function createSkeleton(d) {
  const g = (name, parent, x = 0, y = 0, z = 0) => {
    const o = new THREE.Group();
    o.name = name;
    o.position.set(x, y, z);
    if (parent) parent.add(o);
    return o;
  };
  const j = {};
  j.root = g('root');
  j.pelvis = g('pelvis', j.root, 0, d.pelve.y, 0);
  j.spine = g('spine', j.pelvis, 0, d.tronco.cinturaY, 0);
  j.neck = g('neck', j.spine, 0, d.pescoco.y, 0);
  j.head = g('head', j.neck, 0, d.pescoco.comprimento, 0);
  const hipY = d.pe.tornozeloY + d.canela.comprimento + d.coxa.comprimento - d.pelve.y;
  for (const [s, k] of Object.entries(SIDES)) {
    j['shoulder' + s] = g('shoulder' + s, j.spine, k * d.ombro.x, d.ombro.y, 0);
    j['upperArm' + s] = g('upperArm' + s, j['shoulder' + s]);
    j['elbow' + s] = g('elbow' + s, j['upperArm' + s], 0, -d.braco.comprimento, 0);
    j['wrist' + s] = g('wrist' + s, j['elbow' + s], 0, -d.antebraco.comprimento, 0);
    j['hip' + s] = g('hip' + s, j.pelvis, k * d.quadrilX, hipY, 0);
    j['thigh' + s] = g('thigh' + s, j['hip' + s]);
    j['knee' + s] = g('knee' + s, j['thigh' + s], 0, -d.coxa.comprimento, 0);
    j['ankle' + s] = g('ankle' + s, j['knee' + s], 0, -d.canela.comprimento, 0);
  }
  const standPelvisY = d.pelve.y;
  return { joints: j, dims: d, standPelvisY };
}

// Pose de repouso completa (todos os campos). Poses nomeadas sobrescrevem campos.
export function restPose(d) {
  return {
    pelvis: { drop: 0.004, flex: 0, yaw: 0, roll: 0, x: 0, z: 0 },
    spine: { flex: 0, side: 0, twist: 0 },
    neck: { pitch: 0, yaw: 0, roll: 0 },
    shoulderL: { flex: 0, abd: 6, twist: 0 },
    shoulderR: { flex: 0, abd: 6, twist: 0 },
    elbowL: { flex: 10 },
    elbowR: { flex: 10 },
    wristL: { flex: 0, dev: 0 },
    wristR: { flex: 0, dev: 0 },
    footL: { x: d.quadrilX, z: 0, yaw: 0, pitch: 0, lift: 0, pivot: 0 },
    footR: { x: -d.quadrilX, z: 0, yaw: 0, pitch: 0, lift: 0, pivot: 0 },
    face: { expr: 'neutra', blink: 0 },
  };
}

// Mistura profunda de poses (números interpolados; strings da pose dominante).
export function blendPose(a, b, w) {
  if (w <= 0) return a;
  if (w >= 1) return b;
  const out = {};
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
    const va = a[k];
    const vb = b[k];
    if (va === undefined) out[k] = vb;
    else if (vb === undefined) out[k] = va;
    else if (typeof va === 'number' && typeof vb === 'number') out[k] = va + (vb - va) * w;
    else if (Array.isArray(va)) out[k] = va.map((x, i) => x + (vb[i] - x) * w);
    else if (typeof va === 'object' && va && vb) out[k] = blendPose(va, vb, w);
    else out[k] = w < 0.5 ? va : vb;
  }
  return out;
}

// Sobrepõe campos (merge profundo) — usado para compor poses parciais.
export function mergePose(base, over) {
  if (!over) return base;
  const out = { ...base };
  for (const [k, v] of Object.entries(over)) {
    if (v && typeof v === 'object' && !Array.isArray(v) && base[k] && typeof base[k] === 'object') out[k] = { ...base[k], ...v };
    else out[k] = v;
  }
  return out;
}

const _v = new THREE.Vector3();
const _q = new THREE.Quaternion();
const _e = new THREE.Euler();
const DOWN = new THREE.Vector3(0, -1, 0);

function shoulderEuler(side, f, a, tw) {
  return _e.set(-f * DEG, side * tw * DEG, side * a * DEG, 'XZY');
}

// Limita o ombro a um cone de swing (desvio máximo do braço em relação ao repouso).
function clampShoulder(side, s, L) {
  let f = s.flex;
  let a = s.abd;
  const tw = clamp(s.twist, L.ombroTorcao[0], L.ombroTorcao[1]);
  const swing = (ff, aa) => {
    _q.setFromEuler(shoulderEuler(side, ff, aa, tw));
    return Math.acos(clamp(_v.copy(DOWN).applyQuaternion(_q).dot(DOWN), -1, 1)) / DEG;
  };
  if (swing(f, a) > L.ombroCone) {
    let lo = 0;
    let hi = 1;
    for (let i = 0; i < 20; i++) {
      const m = (lo + hi) / 2;
      if (swing(f * m, a * m) > L.ombroCone) hi = m;
      else lo = m;
    }
    f *= lo;
    a *= lo;
  }
  return { flex: f, abd: a, twist: tw };
}

const smin = (a, b, k = 0.008) => {
  const h = clamp(0.5 + (0.5 * (b - a)) / k, 0, 1);
  return b + (a - b) * h - k * h * (1 - h);
};

// Aplica a pose ao esqueleto. Estado resultante depende só de (pose, root atual).
// root (posição/rumo) é responsabilidade do chamador ou do movimento.
export function applyPose(sk, pose, L) {
  sk.limits = L;
  const j = sk.joints;
  const d = sk.dims;
  const p = pose;
  // Tronco, pescoço
  j.spine.rotation.set(
    clamp(p.spine.flex, ...L.tronco.flex) * DEG,
    clamp(p.spine.twist, ...L.tronco.torcao) * DEG,
    -clamp(p.spine.side, ...L.tronco.lado) * DEG,
    'YXZ',
  );
  j.neck.rotation.set(
    clamp(p.neck.pitch, ...L.pescoco.pitch) * DEG,
    clamp(p.neck.yaw, ...L.pescoco.yaw) * DEG,
    clamp(p.neck.roll, ...L.pescoco.roll) * DEG,
    'YXZ',
  );
  // Braços (FK)
  for (const [s, k] of Object.entries(SIDES)) {
    const sh = clampShoulder(k, p['shoulder' + s], L);
    j['shoulder' + s].rotation.copy(shoulderEuler(k, sh.flex, sh.abd, sh.twist));
    j['elbow' + s].rotation.set(-clamp(p['elbow' + s].flex, ...L.cotovelo.flex) * DEG, 0, 0);
    const w = p['wrist' + s];
    j['wrist' + s].rotation.set(-clamp(w.flex, ...L.punho.flex) * DEG, 0, k * clamp(w.dev, ...L.punho.desvio) * DEG, 'XZY');
  }
  // Pelve: altura preferida, limitada pelo alcance das pernas até os pés
  j.pelvis.rotation.set(p.pelvis.flex * DEG, p.pelvis.yaw * DEG, p.pelvis.roll * DEG, 'YXZ');
  j.root.updateMatrixWorld(true);
  const feet = {};
  const reach = (d.coxa.comprimento + d.canela.comprimento) * 0.985;
  const base = sk.standPelvisY - p.pelvis.drop;
  let pelvisY = base;
  j.pelvis.position.set(p.pelvis.x || 0, base, p.pelvis.z || 0);
  j.root.updateMatrixWorld(true);
  const scaleY = Math.max(1e-6, j.root.getWorldScale(_v).y);
  for (const s of Object.keys(SIDES)) {
    feet[s] = footTarget(sk, p['foot' + s]);
    // altura máxima da pelve para que o quadril alcance o tornozelo-alvo
    const hip = j['hip' + s].getWorldPosition(new THREE.Vector3());
    const dx = hip.x - feet[s].ankle.x;
    const dz = hip.z - feet[s].ankle.z;
    const h2 = reach * reach - dx * dx - dz * dz;
    const maxHipY = feet[s].ankle.y + Math.sqrt(Math.max(0, h2));
    pelvisY = smin(pelvisY, base + (maxHipY - hip.y) / scaleY);
  }
  j.pelvis.position.y = pelvisY;
  j.root.updateMatrixWorld(true);
  for (const s of Object.keys(SIDES)) solveLeg(sk, s, feet[s]);
  j.root.updateMatrixWorld(true);
  return { pelvisY, feet };
}

// Alvo do pé: tornozelo em coordenadas de mundo + orientação do pé.
// Pé em espaço da raiz por padrão; {world:true, ankle:[x,y,z]} para locomoção.
// pivot: 0 = tornozelo; +1 = gira em torno do calcanhar; -1 = em torno da ponta.
function footTarget(sk, f) {
  const d = sk.dims;
  const j = sk.joints;
  const rootQ = j.root.getWorldQuaternion(new THREE.Quaternion());
  const yawQ = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), (f.yaw || 0) * DEG);
  const pitchQ = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -(f.pitch || 0) * DEG);
  let q;
  let ankle;
  if (f.world) {
    q = yawQ.multiply(pitchQ);
    ankle = new THREE.Vector3(...f.ankle);
  } else {
    q = rootQ.clone().multiply(yawQ).multiply(pitchQ);
    // ponto de contato no chão sob o tornozelo, em espaço da raiz
    const contact = new THREE.Vector3(f.x, f.lift || 0, f.z);
    const flat = new THREE.Vector3(0, d.pe.tornozeloY, 0);
    let rel = flat.clone();
    if (f.pivot) {
      // gira o pé em torno do calcanhar (pivot>0) ou da ponta (pivot<0) mantendo esse ponto fixo
      const pv = new THREE.Vector3(0, 0, f.pivot > 0 ? -d.pe.calcanhar : d.pe.comprimento - d.pe.calcanhar);
      const pq = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -(f.pitch || 0) * DEG);
      rel = pv.clone().add(flat.clone().sub(pv).applyQuaternion(pq));
    }
    rel.applyQuaternion(yawQ);
    ankle = contact.add(rel);
    j.root.localToWorld(ankle);
  }
  return { ankle, q };
}

const _ = {
  H: new THREE.Vector3(),
  D: new THREE.Vector3(),
  u: new THREE.Vector3(),
  p: new THREE.Vector3(),
  t: new THREE.Vector3(),
  K: new THREE.Vector3(),
  s: new THREE.Vector3(),
  x: new THREE.Vector3(),
  y: new THREE.Vector3(),
  z: new THREE.Vector3(),
  m: new THREE.Matrix4(),
  qa: new THREE.Quaternion(),
  qb: new THREE.Quaternion(),
};

// IK analítico de 2 ossos: joelho aponta para a frente do pé (dobra só para trás).
function solveLeg(sk, s, target) {
  const j = sk.joints;
  const d = sk.dims;
  const l1 = d.coxa.comprimento;
  const l2 = d.canela.comprimento;
  const hip = j['hip' + s];
  hip.getWorldPosition(_.H);
  _.D.subVectors(target.ankle, _.H);
  const dist = clamp(_.D.length(), Math.abs(l1 - l2) + 1e-4, (l1 + l2) * 0.9999);
  _.u.copy(_.D).normalize();
  const cosA = clamp((l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist), -1, 1);
  const alpha = Math.acos(cosA);
  // polo: frente do pé
  _.p.set(0, 0, 1).applyQuaternion(target.q);
  _.p.addScaledVector(_.u, -_.p.dot(_.u)).normalize();
  _.t.copy(_.u).multiplyScalar(Math.cos(alpha)).addScaledVector(_.p, Math.sin(alpha)).normalize();
  _.K.copy(_.H).addScaledVector(_.t, l1);
  _.s.copy(_.H).addScaledVector(_.u, dist).sub(_.K).normalize();
  // base do quadril: -Y = coxa, +Z = frente do joelho
  _.y.copy(_.t).negate();
  _.z.copy(_.p).addScaledVector(_.t, -_.p.dot(_.t)).normalize();
  _.x.crossVectors(_.y, _.z).normalize();
  _.m.makeBasis(_.x, _.y, _.z);
  _.qa.setFromRotationMatrix(_.m);
  hip.parent.getWorldQuaternion(_.qb);
  hip.quaternion.copy(_.qb.invert().multiply(_.qa));
  const knee = Math.acos(clamp(_.t.dot(_.s), -1, 1));
  j['knee' + s].rotation.set(knee, 0, 0);
  // tornozelo: orientação do pé no mundo
  hip.updateMatrixWorld(true);
  j['knee' + s].getWorldQuaternion(_.qb);
  j['ankle' + s].quaternion.copy(_.qb.invert().multiply(target.q));
  // limite anatômico do tornozelo (no balanço o pé segue a canela além do limite)
  _e.setFromQuaternion(j['ankle' + s].quaternion, 'XYZ');
  const lim = sk.limits?.tornozelo?.flex || [-45, 45];
  const fx = clamp(-_e.x / DEG, lim[0], lim[1]);
  if (Math.abs(fx + _e.x / DEG) > 1e-6) {
    _e.x = -fx * DEG;
    j['ankle' + s].quaternion.setFromEuler(_e);
  }
}

// ---- Medição (auditoria): ângulos efetivos de cada junta a partir dos quaternions ----
function swingTwist(q, axis) {
  const r = new THREE.Vector3(q.x, q.y, q.z);
  let ang = 2 * Math.atan2(r.dot(axis), q.w);
  if (ang > Math.PI) ang -= 2 * Math.PI;
  if (ang < -Math.PI) ang += 2 * Math.PI;
  return ang / DEG;
}

export function measureJoints(sk) {
  const j = sk.joints;
  const out = {};
  const eul = (o, order) => {
    _e.setFromQuaternion(o.quaternion, order);
    return [_e.x / DEG, _e.y / DEG, _e.z / DEG];
  };
  const sp = eul(j.spine, 'YXZ');
  out.tronco = { flex: sp[0], torcao: sp[1], lado: -sp[2] };
  const nk = eul(j.neck, 'YXZ');
  out.pescoco = { pitch: nk[0], yaw: nk[1], roll: nk[2] };
  const Y = new THREE.Vector3(0, 1, 0);
  for (const [s, k] of Object.entries(SIDES)) {
    const qs = j['shoulder' + s].quaternion;
    const dir = DOWN.clone().applyQuaternion(qs);
    out['ombro' + s] = {
      cone: Math.acos(clamp(dir.dot(DOWN), -1, 1)) / DEG,
      torcao: k * swingTwist(qs, Y),
    };
    const el = eul(j['elbow' + s], 'XYZ');
    out['cotovelo' + s] = { flex: -el[0], foraDoEixo: Math.hypot(el[1], el[2]) };
    const kn = eul(j['knee' + s], 'XYZ');
    out['joelho' + s] = { flex: kn[0], foraDoEixo: Math.hypot(kn[1], kn[2]) };
    const qh = j['hip' + s].quaternion;
    const hd = DOWN.clone().applyQuaternion(qh);
    out['quadril' + s] = {
      flex: Math.atan2(hd.z, -hd.y) / DEG,
      abd: (k * Math.asin(clamp(hd.x, -1, 1))) / DEG,
      torcao: k * swingTwist(qh, Y),
    };
    const an = eul(j['ankle' + s], 'XYZ');
    out['tornozelo' + s] = { flex: -an[0], lateral: Math.hypot(an[1], an[2]) };
    const wr = eul(j['wrist' + s], 'XZY');
    out['punho' + s] = { flex: -wr[0], desvio: k * wr[2] };
  }
  return out;
}

// Compara medições com limites de tokens. Retorna lista de violações.
export function checkLimits(m, L, tol = 0.5) {
  const v = [];
  const chk = (nome, val, [a, b]) => {
    if (val < a - tol || val > b + tol) v.push(`${nome}=${val.toFixed(1)} fora de [${a}, ${b}]`);
  };
  chk('tronco.flex', m.tronco.flex, L.tronco.flex);
  chk('tronco.lado', m.tronco.lado, L.tronco.lado);
  chk('tronco.torcao', m.tronco.torcao, L.tronco.torcao);
  chk('pescoco.yaw', m.pescoco.yaw, L.pescoco.yaw);
  chk('pescoco.pitch', m.pescoco.pitch, L.pescoco.pitch);
  chk('pescoco.roll', m.pescoco.roll, L.pescoco.roll);
  for (const s of ['L', 'R']) {
    chk(`ombro${s}.cone`, m['ombro' + s].cone, [0, L.ombroCone]);
    chk(`ombro${s}.torcao`, m['ombro' + s].torcao, L.ombroTorcao);
    chk(`cotovelo${s}.flex`, m['cotovelo' + s].flex, L.cotovelo.flex);
    chk(`cotovelo${s}.foraDoEixo`, m['cotovelo' + s].foraDoEixo, [0, 0.5]);
    chk(`joelho${s}.flex`, m['joelho' + s].flex, L.joelho.flex);
    chk(`joelho${s}.foraDoEixo`, m['joelho' + s].foraDoEixo, [0, 0.5]);
    chk(`quadril${s}.flex`, m['quadril' + s].flex, L.quadril.flex);
    chk(`quadril${s}.abd`, m['quadril' + s].abd, L.quadril.abd);
    chk(`quadril${s}.torcao`, m['quadril' + s].torcao, L.quadril.torcao);
    chk(`tornozelo${s}.flex`, m['tornozelo' + s].flex, L.tornozelo.flex);
    chk(`tornozelo${s}.lateral`, m['tornozelo' + s].lateral, [0, 20]);
    chk(`punho${s}.flex`, m['punho' + s].flex, L.punho.flex);
    chk(`punho${s}.desvio`, m['punho' + s].desvio, L.punho.desvio);
  }
  return v;
}

