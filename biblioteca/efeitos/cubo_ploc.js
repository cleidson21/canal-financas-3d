// Cubo PLOC! — assinatura do canal. Cai do céu, quica com squash e stretch e, ao pousar,
// some com pop (cresce um pouco e some). O contador DIA aparece quando o cubo termina
// de sumir (`tAparece`). Tudo função pura de t; queda por equações de movimento.
//   const cubo = createPlocCube(scene, { pos: [x, y, z], t0: 0.5 });
//   cubo.update(t);  // cubo.tPouso, cubo.tPop, cubo.tAparece
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { material } from '../nucleo/materiais.js';
import { clamp, ease } from '../nucleo/matematica.js';

export function createPlocCube(scene, { pos = [0, 0, 0], t0 = 0, alturaQueda = 4, lado = 0.34, g = 15, restituicao = 0.42, quicadas = 2, espera = 0.22, popS = 0.26 } = {}) {
  const grupo = new THREE.Group();
  grupo.name = 'cubo_ploc';
  grupo.position.set(pos[0], pos[1], pos[2]);
  scene.add(grupo);
  const mats = [0, 1, 2, 3, 4, 5].map((i) => material('cores.efeitos.cubo.' + i));
  const cubo = new THREE.Mesh(new RoundedBoxGeometry(lado, lado, lado, 2, lado * 0.09), mats);
  cubo.name = 'ploc_cubo';
  cubo.position.y = lado / 2; // pivô no fundo: o chão fica fixo no squash
  cubo.castShadow = true;
  cubo.receiveShadow = true;
  const pivo = new THREE.Group();
  pivo.add(cubo);
  grupo.add(pivo);

  // segmentos de voo: queda inicial + `quicadas` subidas/descidas
  const segs = [];
  const tFall = Math.sqrt((2 * alturaQueda) / g);
  let cursor = t0;
  segs.push({ a: cursor, b: cursor + tFall, tipo: 'queda', v0: 0, vImp: g * tFall, amp: 1 });
  cursor += tFall;
  let v = g * tFall;
  for (let i = 1; i <= quicadas; i++) {
    v *= restituicao;
    const dur = (2 * v) / g;
    segs.push({ a: cursor, b: cursor + dur, tipo: 'quique', v0: v, vImp: v, amp: Math.pow(restituicao, i - 1) });
    cursor += dur;
  }
  const tPouso = cursor; // último contato
  const contato = 0.13; // duração do esmagamento em cada impacto
  const impactos = segs.map((s) => ({ t: s.b, amp: s.amp }));
  const vMax = segs[0].vImp;
  const tPop = tPouso + espera;
  const tAparece = tPop + popS;

  function altura(t) {
    for (const s of segs) {
      if (t >= s.a && t < s.b) {
        const tau = t - s.a;
        return { y: s.tipo === 'queda' ? alturaQueda - 0.5 * g * tau * tau : s.v0 * tau - 0.5 * g * tau * tau, seg: s, u: tau / (s.b - s.a), vel: s.tipo === 'queda' ? g * tau : Math.abs(s.v0 - g * tau) };
      }
    }
    return { y: 0, seg: null, u: 0, vel: 0 };
  }

  function update(t) {
    grupo.visible = t >= t0 && t < tAparece;
    if (!grupo.visible) return;
    const h = altura(t);
    let sy = 1;
    // stretch proporcional à velocidade (só no ar)
    if (h.seg) sy = 1 + 0.38 * Math.pow(clamp(h.vel / vMax, 0, 1), 1.2);
    // squash: janela de `contato` s depois de cada impacto, amplitude cai a cada quique
    let y = h.y;
    for (const im of impactos) {
      const tau = t - im.t;
      if (tau >= 0 && tau < contato) {
        const u = tau / contato;
        sy = 1 - 0.46 * im.amp * Math.sin(Math.PI * u);
        y = 0;
      }
    }
    const sxz = 1 / Math.sqrt(sy);
    let escala = 1;
    if (t >= tPop) {
      const k = clamp((t - tPop) / popS, 0, 1);
      escala = k < 0.35 ? 1 + 0.32 * ease.outCubic(k / 0.35) : 1.32 * Math.pow(1 - (k - 0.35) / 0.65, 2);
    }
    pivo.position.y = Math.max(0, y);
    pivo.scale.set(sxz * escala, sy * escala, sxz * escala);
    // giro: yaw que se acalma; inclinação só no ar (zero em todos os impactos)
    const yaw = 0.7 + 3.4 * Math.exp(-1.7 * Math.max(0, t - t0));
    const amp = h.seg ? Math.sin(Math.PI * h.u) * (0.45 * h.seg.amp + 0.05) : 0;
    pivo.rotation.set(0.9 * amp, yaw, -0.7 * amp, 'YXZ');
  }
  update(-1e9);
  return { group: grupo, update, tPouso, tPop, tAparece, impactos, lado, alturaQueda };
}
