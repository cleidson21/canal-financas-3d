// Nico — protagonista. Segmentos rígidos presos por juntas (sem skinning), luvas sem
// dedos, rosto simples. Cores de valores/tokens.json. API determinística (NICO_SPEC §3):
//   createNico(opts) → { group, joints, sockets, setPose(nome,t), play(mov,t0,params),
//                        look(alvo), expression(nome), grab(obj,socket), release(obj,posMundo) }
// Tudo é função do tempo: chame setPose/play → look → expression → grab/release a cada quadro.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { material, token } from '../../nucleo/materiais.js';
import { DEG, clamp } from '../../nucleo/matematica.js';
import { createSkeleton, restPose, applyPose, mergePose, measureJoints, checkLimits } from '../bipede/rig.js';
import { bipedProxies } from '../bipede/colisao.js';
import { EXPRESSIONS, POSES, poseKey } from '../../movimentos/poses.js';
import { createLocomotion, createTurn } from '../../movimentos/locomocao.js';
import { GESTURES, livePose, blinkAt } from '../../movimentos/gestos.js';

const SOCKET_ALIAS = {
  mãoE: 'handL', maoE: 'handL', mãoD: 'handR', maoD: 'handR',
  antebraçoE: 'forearmL', antebracoE: 'forearmL', antebraçoD: 'forearmR', antebracoD: 'forearmR',
  antebraços: 'forearms', antebracos: 'forearms', topoCabeça: 'headTop', topoCabeca: 'headTop', alvoOlhar: 'lookTarget',
};

// Mapa peça → token de cor (usado pelo teste automático de cores).
export const PART_TOKENS = {
  bone: 'cores.nico.bone', bone_aba: 'cores.nico.bone', bone_botao: 'cores.nico.bone',
  camiseta: 'cores.nico.camiseta', manga: 'cores.nico.camiseta', ombro: 'cores.nico.camiseta',
  bermuda: 'cores.nico.bermuda', bermuda_perna: 'cores.nico.bermuda',
  pele: 'cores.nico.pele', cabelo: 'cores.nico.cabelo', tenis: 'cores.nico.tenis', sola: 'cores.nico.sola',
  olho: 'cores.nico.olho', pupila: 'cores.nico.pupila', boca: 'cores.nico.boca', sobrancelha: 'cores.nico.sobrancelha',
  luva: 'cores.nico.luva', palpebra: 'cores.nico.pele',
  pe_luva: 'cores.nico.luva', sola_solta: 'cores.nico.sola',
};

// opts (todas opcionais, só acrescentam; o Nico padrão não muda):
//   descalco: true        → sem tênis; pés de luva (sem dedos), cor de luva
//   sapatoQuebrado: true  → tênis com a ponta da sola solta; a ponta pende quando o pé levanta
export function createNico(opts = {}) {
  const d = opts.dims || token('escala.nico');
  const L = token('juntas');
  const sk = createSkeleton(d);
  const j = sk.joints;
  const group = j.root;
  group.name = opts.name || 'nico';
  const M = (part) => material(PART_TOKENS[part]);
  const flaps = {};

  const add = (parent, geo, part, pos = [0, 0, 0], rot = [0, 0, 0], scale = [1, 1, 1]) => {
    const m = new THREE.Mesh(geo, M(part));
    m.name = part;
    m.position.set(...pos);
    m.rotation.set(...rot);
    m.scale.set(...scale);
    m.castShadow = true;
    m.receiveShadow = true;
    parent.add(m);
    return m;
  };
  const capsule = (r, len, seg = 10) => new THREE.CapsuleGeometry(r, len, 3, seg);
  const sphere = (r, w = 14, h = 10) => new THREE.SphereGeometry(r, w, h);
  const rbox = (w, h, dd, r) => new RoundedBoxGeometry(w, h, dd, 2, r);

  // ---- Corpo ----
  add(j.pelvis, rbox(d.pelve.largura, d.pelve.altura, d.pelve.profundidade, 0.05), 'bermuda');
  const T = d.tronco;
  add(j.spine, rbox(T.largura, T.altura, T.profundidade, T.raioCanto), 'camiseta', [0, T.altura / 2, 0]);
  add(j.neck, new THREE.CylinderGeometry(d.pescoco.raio, d.pescoco.raio, d.pescoco.comprimento + 0.03, 10), 'pele', [0, d.pescoco.comprimento / 2, 0]);

  for (const [s, k] of [['L', 1], ['R', -1]]) {
    // braço: ombro (esfera de junta, manga), braço, cotovelo, antebraço, luva
    add(j['shoulder' + s], sphere(d.ombro.raio), 'ombro');
    const B = d.braco;
    add(j['upperArm' + s], capsule(B.mangaRaio, B.mangaComprimento), 'manga', [0, -B.mangaComprimento / 2, 0]);
    add(j['upperArm' + s], capsule(B.raio, B.comprimento * 0.75), 'pele', [0, -B.comprimento * 0.55, 0]);
    add(j['elbow' + s], sphere(d.cotovelo.raio, 10, 8), 'pele');
    add(j['elbow' + s], capsule(d.antebraco.raio, d.antebraco.comprimento * 0.9), 'pele', [0, -d.antebraco.comprimento / 2, 0]);
    add(j['wrist' + s], sphere(d.mao.raio, 12, 9), 'luva', [0, -d.mao.raio * 0.9, 0.004], [0, 0, 0], [0.82, 1.08, 0.72]);
    // perna: bermuda até ~60% da coxa, joelho, canela, tênis com sola
    const C = d.coxa;
    add(j['thigh' + s], capsule(C.raio, C.comprimento * 0.55), 'bermuda_perna', [0, -C.comprimento * 0.3, 0]);
    add(j['thigh' + s], capsule(C.raio * 0.72, C.comprimento * 0.5), 'pele', [0, -C.comprimento * 0.72, 0]);
    add(j['knee' + s], sphere(d.joelho.raio, 10, 8), 'pele');
    add(j['knee' + s], capsule(d.canela.raio, d.canela.comprimento * 0.85), 'pele', [0, -d.canela.comprimento / 2, 0]);
    const P = d.pe;
    const zc = P.comprimento / 2 - P.calcanhar;
    if (opts.descalco) {
      // pé de luva: caixa arredondada baixa, sem dedos
      const alt = 0.048;
      add(j['ankle' + s], rbox(P.largura * 0.96, alt, P.comprimento * 0.95, 0.021), 'pe_luva', [0, -P.tornozeloY + alt / 2, zc]);
    } else {
      add(j['ankle' + s], rbox(P.largura, P.alturaTenis, P.comprimento, 0.028), 'tenis', [0, -P.tornozeloY + P.alturaSola + P.alturaTenis / 2, zc]);
      const yS = -P.tornozeloY + P.alturaSola / 2;
      if (opts.sapatoQuebrado) {
        // metade de trás da sola presa; metade da frente em pivô no meio do pé
        const meio = P.comprimento / 2;
        add(j['ankle' + s], rbox(P.largura + 0.008, P.alturaSola, meio + 0.006, 0.011), 'sola', [0, yS, zc - meio / 2 - 0.002]);
        const pivo = new THREE.Group();
        pivo.name = 'sola_pivo' + s;
        pivo.position.set(0, yS, zc + 0.004);
        j['ankle' + s].add(pivo);
        add(pivo, rbox(P.largura + 0.008, P.alturaSola, meio + 0.012, 0.011), 'sola_solta', [0, 0, meio / 2 + 0.006]);
        flaps[s] = pivo;
      } else {
        add(j['ankle' + s], rbox(P.largura + 0.008, P.alturaSola, P.comprimento + 0.01, 0.011), 'sola', [0, yS, zc + 0.002]);
      }
    }
  }

  // ---- Cabeça e rosto ----
  const H = d.cabeca;
  const face = new THREE.Group();
  face.name = 'rosto';
  face.position.set(0, H.centroY, 0);
  j.head.add(face);
  add(face, sphere(H.raio, 18, 14), 'pele');
  add(face, new THREE.SphereGeometry(H.raio * 1.025, 18, 8, Math.PI * 0.92, Math.PI * 1.16, Math.PI * 0.3, Math.PI * 0.27), 'cabelo');
  const cap = new THREE.Group();
  cap.name = 'bone';
  cap.position.set(0, 0.035, -0.004);
  cap.rotation.x = -0.3;
  face.add(cap);
  add(cap, new THREE.SphereGeometry(H.raio * 1.07, 18, 8, 0, Math.PI * 2, 0, Math.PI / 2), 'bone');
  add(cap, sphere(0.018, 8, 6), 'bone_botao', [0, H.raio * 1.07, 0]);
  add(face, new THREE.CylinderGeometry(0.2, 0.2, 0.014, 18, 1, false, -Math.PI / 2, Math.PI), 'bone_aba', [0, 0.112, 0.07], [0.15, 0, 0]);
  add(face, sphere(0.035, 10, 8), 'pele', [0, -0.045, H.raio * 0.99], [0, 0, 0], [1, 0.85, 0.9]); // nariz
  for (const k of [1, -1]) add(face, sphere(0.045, 10, 8), 'pele', [k * H.raio * 0.99, -0.02, 0], [0, 0, 0], [0.5, 1, 0.8]); // orelhas

  const eyes = {};
  const brows = {};
  const lids = {};
  for (const [s, k] of [['L', 1], ['R', -1]]) {
    const eye = new THREE.Group();
    eye.name = 'olho' + s;
    eye.position.set(k * 0.07, 0, 0.165);
    face.add(eye);
    add(eye, sphere(0.045, 14, 10), 'olho');
    const pupil = add(eye, sphere(0.022, 16, 12), 'pupila', [0, 0, 0.033], [0, 0, 0], [1, 1, 0.6]);
    eyes[s] = { eye, pupil };
    const lid = new THREE.Group();
    lid.name = 'palpebra' + s;
    eye.add(lid);
    add(lid, new THREE.SphereGeometry(0.049, 14, 6, 0, Math.PI * 2, 0, Math.PI / 2), 'palpebra');
    lids[s] = lid;
    const brow = add(face, rbox(0.075, 0.018, 0.02, 0.008), 'sobrancelha', [k * 0.072, 0.062, 0.18], [-0.3, k * 0.35, 0]);
    brows[s] = { mesh: brow, y0: 0.062 };
  }
  const mouthY = -0.11;
  const mouthZ = Math.sqrt(H.raio * H.raio - mouthY * mouthY) + 0.002;
  const mouth = new THREE.Group();
  mouth.name = 'boca';
  mouth.position.set(0, mouthY, mouthZ);
  mouth.rotation.x = Math.asin(-mouthY / H.raio);
  face.add(mouth);
  const mouths = {
    neutra: add(mouth, rbox(0.07, 0.014, 0.016, 0.006), 'boca'),
    aberta: add(mouth, sphere(0.034, 12, 8), 'boca', [0, -0.004, 0], [0, 0, 0], [1, 0.85, 0.35]),
    sorriso: add(mouth, new THREE.TorusGeometry(0.038, 0.008, 6, 14, Math.PI), 'boca', [0, 0.018, 0], [0, 0, Math.PI]),
    preocupada: add(mouth, new THREE.TorusGeometry(0.034, 0.008, 6, 14, Math.PI), 'boca', [0, -0.016, 0]),
  };

  // ---- Sockets ----
  const sock = (name, parent, pos) => {
    const o = new THREE.Object3D();
    o.name = 'socket_' + name;
    o.position.set(...pos);
    parent.add(o);
    return o;
  };
  const sockets = {
    handL: sock('handL', j.wristL, [0, -d.mao.raio, 0]),
    handR: sock('handR', j.wristR, [0, -d.mao.raio, 0]),
    forearmL: sock('forearmL', j.elbowL, [-d.mao.raio * 0.9, -0.6 * d.antebraco.comprimento, 0]),
    forearmR: sock('forearmR', j.elbowR, [d.mao.raio * 0.9, -0.6 * d.antebraco.comprimento, 0]),
    forearms: sock('forearms', j.spine, [0, 0, 0]),
    headTop: sock('headTop', j.head, [0, H.centroY + H.raio * 1.07 + 0.02 + 0.035, 0]),
    lookTarget: sock('lookTarget', j.head, [0, H.centroY, H.raio + 0.05]),
    // costas: na cintura, rente à camiseta; eixo +Y da carga inclinado 18° para trás, 4 cm afastada da camiseta
    // (a carga sobe atrás da cabeça em vez de atravessá-la). A carga se estende para -Z.
    costas: sock('costas', j.spine, [0, 0.06, -d.tronco.profundidade / 2 - 0.04]),
  };

  const rest = restPose(d);
  sockets.costas.rotation.x = -18 * DEG;
  let current = rest;
  let tNow = 0;
  const _a = new THREE.Vector3();
  const _b = new THREE.Vector3();
  const _qa = new THREE.Quaternion();
  const _qb = new THREE.Quaternion();

  // 'forearms' = ponto médio entre os antebraços, sempre de pé (só gira com o rumo da raiz):
  // um saco abraçado não inclina quando o tronco se curva.
  function updateVirtualSockets() {
    group.updateMatrixWorld(true);
    sockets.forearmL.getWorldPosition(_a);
    sockets.forearmR.getWorldPosition(_b);
    _a.add(_b).multiplyScalar(0.5);
    sockets.forearms.position.copy(j.spine.worldToLocal(_a));
    j.spine.getWorldQuaternion(_qa);
    group.getWorldQuaternion(_qb);
    sockets.forearms.quaternion.copy(_qa.invert().multiply(_qb));
    group.updateMatrixWorld(true);
  }

  function setFace(f = {}) {
    const e = EXPRESSIONS[f.expr || 'neutra'] || EXPRESSIONS.neutra;
    for (const [name, m] of Object.entries(mouths)) m.visible = name === e.mouth;
    for (const [s, k] of [['L', 1], ['R', -1]]) {
      const [inner, dy] = e['brow' + s];
      const b = brows[s];
      b.mesh.position.y = b.y0 + dy;
      b.mesh.rotation.z = -k * inner * DEG;
      const lid = clamp(Math.max(e.lid, f.blink || 0), 0, 1);
      lids[s].rotation.x = -1.25 + lid * 2.85;
      eyes[s].pupil.scale.set(e.pupil, e.pupil, 0.6);
    }
  }

  // Sola solta: a ponta pende quando a ponta do pé está no ar (sem entrar no chão).
  function updateFlaps(t) {
    const P = d.pe;
    for (const s of Object.keys(flaps)) {
      const pt = j['ankle' + s].localToWorld(_a.set(0, -P.tornozeloY, P.comprimento - P.calcanhar));
      const h = Math.max(0, group.worldToLocal(pt).y);
      const meio = P.comprimento / 2;
      const livre = Math.min(1, h / 0.03);
      const alvo = (26 + 7 * Math.sin(2 * Math.PI * 3.6 * t + (s === 'L' ? 0 : 1.7))) * livre * DEG;
      const maxSemChao = Math.asin(Math.min(1, h / meio));
      flaps[s].rotation.x = Math.min(alvo, maxSemChao);
    }
  }

  function applyFull(pose, t = tNow) {
    tNow = t;
    current = mergePose(rest, pose);
    current.face = { ...rest.face, ...(pose.face || {}) };
    applyPose(sk, current, L);
    setFace(current.face);
    for (const s of ['L', 'R']) eyes[s].eye.rotation.set(0, 0, 0);
    updateVirtualSockets();
    updateFlaps(t);
    return current;
  }

  const api = {
    group,
    joints: j,
    sockets,
    dims: d,
    limits: L,
    skeleton: sk,
    rest,
    get pose() {
      return current;
    },
    proxies: bipedProxies(d),
    parts: PART_TOKENS,

    // Pose completa (todos os campos são definidos: sem estado herdado de quadros anteriores)
    applyPose: applyFull,

    // Pose nomeada estática, com respiração/piscada no instante t.
    setPose(name, t = 0) {
      const k = poseKey(name);
      if (POSES[k].locomotion) {
        // locomoção congelada num quadro de contato, no lugar (raiz no ponto atual)
        const cfg = token('locomocao.' + POSES[k].locomotion);
        const x = group.position.x;
        const z = group.position.z;
        const h = group.rotation.y;
        const len = 2.4;
        const fx = Math.sin(h);
        const fz = Math.cos(h);
        const loco = createLocomotion(d, cfg, { from: [x - fx * len / 2, z - fz * len / 2], to: [x + fx * len / 2, z + fz * len / 2] });
        const Ls = loco.stepLength;
        // instante logo após o calcanhar tocar (passo n): d = (n − apoio)·L
        const target = (Math.round(len / 2 / Ls) + 1 - cfg.apoio + 0.08) * Ls;
        const r = loco.at(loco.timeAt(target));
        group.position.set(x, group.position.y, z);
        // desloca os pés para que a pelve fique no ponto atual
        const off = [x - r.root.x, z - r.root.z];
        for (const s of ['L', 'R']) r.pose['foot' + s].ankle = [r.pose['foot' + s].ankle[0] + off[0], r.pose['foot' + s].ankle[1], r.pose['foot' + s].ankle[2] + off[1]];
        return applyFull({ ...r.pose, face: { ...POSES[k].face, blink: blinkAt(t) } }, t);
      }
      return applyFull(livePose(rest, k, t), t);
    },

    // Movimento parametrizado. Retorna uma função pura de t que aplica o movimento.
    //  play('caminhar'|'correr', t0, { from:[x,z], to:[x,z], duration?, speed?, upper?:'carry' })
    //  play('<gesto>', t0, { from?: pose })
    play(name, t0 = 0, params = {}) {
      // tronco/braços de uma pose nomeada por cima da locomoção (ex.: carregar andando)
      const overlay = (pose, t) => {
        if (!params.upper) return pose;
        const up = livePose(rest, params.upper, t);
        const sp = pose.spine || { flex: 0, twist: 0, side: 0 };
        return { ...pose, shoulderL: up.shoulderL, shoulderR: up.shoulderR, elbowL: up.elbowL, elbowR: up.elbowR, wristL: up.wristL, wristR: up.wristR, spine: { ...sp, flex: up.spine.flex + sp.flex * 0.5, twist: sp.twist * 0.3 }, face: { ...up.face, blink: blinkAt(t) } };
      };
      if (name === 'virar' || name === 'turn') {
        const turn = createTurn(d, { ...params, t0 });
        const fn = (t) => {
          const r = turn.at(t);
          group.position.set(r.root.x, group.position.y, r.root.z);
          group.rotation.set(0, r.root.heading, 0);
          applyFull(overlay({ ...r.pose, face: { expr: params.expr || 'neutra', blink: blinkAt(t) } }, t), t);
          return r;
        };
        fn.duration = turn.duration;
        return fn;
      }
      const loc = { caminhar: 'caminhar', walk: 'caminhar', correr: 'correr', run: 'correr', cambalear: 'cambalear', stagger: 'cambalear' }[name];
      if (loc) {
        const cfg = { ...token('locomocao.' + loc), ...(params.cfg || {}) };
        const loco = createLocomotion(d, cfg, { ...params, t0 });
        const fn = (t) => {
          const r = loco.at(t);
          group.position.set(r.root.x, group.position.y, r.root.z);
          group.rotation.set(0, r.root.heading, 0);
          let pose = { ...r.pose, face: { expr: params.expr || 'neutra', blink: blinkAt(t) } };
          if (loc === 'cambalear') {
            // vaivém de quem não aguenta o peso: o quadril e o tronco pendem a cada passo
            const w = Math.sin(Math.PI * r.phase) * r.k;
            pose.pelvis = { ...pose.pelvis, roll: 5 * w, x: 0.022 * w };
            pose.spine = { ...pose.spine, side: -7 * w };
            pose.neck = { ...pose.neck, roll: 4 * w };
          }
          applyFull(overlay(pose, t), t);
          return r;
        };
        fn.locomotion = loco;
        fn.duration = loco.duration;
        return fn;
      }
      const key = GESTURES[name] ? name : poseKey(name);
      const g = GESTURES[key];
      if (!g) throw new Error(`movimento desconhecido: ${name}`);
      return (t) => applyFull(g(rest, Math.max(0, t - t0), params), t);
    },

    // Vira o pescoço (dentro dos limites) e os olhos para um ponto do mundo.
    look(target) {
      if (!target) return;
      const tgt = target.isVector3 ? target : new THREE.Vector3(...target);
      group.updateMatrixWorld(true);
      const local = j.neck.parent.worldToLocal(tgt.clone());
      const base = j.neck.position.clone().add(new THREE.Vector3(0, d.pescoco.comprimento + H.centroY, 0));
      const v = local.sub(base);
      const yaw = Math.atan2(v.x, v.z) / DEG;
      const pitch = -Math.atan2(v.y, Math.hypot(v.x, v.z)) / DEG;
      const ny = clamp(yaw, ...L.pescoco.yaw);
      const np = clamp(pitch, ...L.pescoco.pitch);
      j.neck.rotation.set(np * DEG, ny * DEG, j.neck.rotation.z, 'YXZ');
      // olhos levam o resto (até 25°)
      const ey = clamp(yaw - ny, -25, 25) * DEG;
      const ep = clamp(pitch - np, -20, 20) * DEG;
      for (const s of ['L', 'R']) eyes[s].eye.rotation.set(ep, ey, 0);
      current = { ...current, neck: { ...current.neck, yaw: ny, pitch: np } };
      updateVirtualSockets();
    },

    expression(name, extra = {}) {
      current = { ...current, face: { ...current.face, expr: name, ...extra } };
      setFace(current.face);
    },

    // Encaixa o objeto no socket (idempotente: pode ser chamado a cada quadro).
    // O ponto de pega do objeto (obj.userData.grip[socket]) coincide com o socket.
    grab(obj, socketName) {
      const key = SOCKET_ALIAS[socketName] || socketName;
      const s = sockets[key];
      if (!s) throw new Error(`socket desconhecido: ${socketName}`);
      if (obj.parent !== s) s.add(obj);
      const grip = (obj.userData.grip && (obj.userData.grip[key] || obj.userData.grip.default)) || [0, 0, 0];
      obj.position.set(-grip[0], -grip[1], -grip[2]);
      obj.quaternion.identity();
      obj.userData.heldBy = key;
    },

    // Solta o objeto numa posição de mundo (idempotente). opts.parent: pai (padrão: pai do Nico).
    release(obj, posMundo, opts = {}) {
      const parent = opts.parent || group.parent;
      if (obj.parent !== parent) parent.add(obj);
      const p = posMundo.isVector3 ? posMundo : new THREE.Vector3(...posMundo);
      obj.position.copy(parent.worldToLocal(p.clone()));
      obj.rotation.set(0, opts.rotY || 0, 0);
      obj.userData.heldBy = null;
    },

    measure: () => measureJoints(sk),
    checkLimits: () => checkLimits(measureJoints(sk), L),
  };
  applyFull(rest);
  return api;
}
