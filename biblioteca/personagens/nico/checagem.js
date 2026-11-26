// Checagens do Nico usadas pela auditoria e pelo catálogo (sem efeito visual).
import * as THREE from 'three';
import { resolveProxies, collisions, distance } from '../bipede/colisao.js';

// Limites de junta + interpenetração entre peças do corpo (e objetos opcionais).
// objetos: [{ obj, proxies, ignorar?: [nomes de peça] }]
export function auditPose(nico, objetos = [], tol = 0.004) {
  nico.group.updateMatrixWorld(true);
  const corpo = resolveProxies(nico.proxies, nico.joints);
  const extras = [];
  for (const o of objetos) {
    o.obj.updateWorldMatrix(true, true);
    for (const p of o.proxies) extras.push(...resolveProxies([{ ...p, obj: o.obj }], nico.joints));
  }
  const all = [...corpo, ...extras];
  const extraNames = new Set(extras.map((e) => e.name));
  const col = collisions(all, {
    tol,
    // objeto x objeto do mesmo dono não conta
    only: (a, b) => !(extraNames.has(a.name) && extraNames.has(b.name)),
  });
  return { limites: nico.checkLimits(), colisoes: col };
}

// Menor distância entre as superfícies de um objeto e um conjunto de peças do corpo.
export function contactDistance(nico, obj, proxies, partes) {
  nico.group.updateMatrixWorld(true);
  obj.updateWorldMatrix(true, true);
  const corpo = resolveProxies(nico.proxies.filter((p) => partes.includes(p.name)), nico.joints);
  const ob = resolveProxies(proxies.map((p) => ({ ...p, obj })), nico.joints);
  let best = Infinity;
  for (const a of ob) for (const b of corpo) best = Math.min(best, distance(a, b));
  return best;
}

// Pontos de contato da sola (calcanhar e ponta) em mundo, para medir deslize.
export function solePoints(nico) {
  const d = nico.dims.pe;
  const out = {};
  for (const s of ['L', 'R']) {
    const a = nico.joints['ankle' + s];
    a.updateWorldMatrix(true, false);
    out[s] = {
      heel: a.localToWorld(new THREE.Vector3(0, -d.tornozeloY, -d.calcanhar)),
      toe: a.localToWorld(new THREE.Vector3(0, -d.tornozeloY, d.comprimento - d.calcanhar)),
    };
  }
  return out;
}


// Menor distância (m, entre superfícies; negativa = penetração) entre uma peça do corpo
// (padrão: a cabeça) e os volumes de colisão de objetos. Usa distâncias em escala de mundo.
//   objetos: [{ obj, proxies }]  → { dist, item }
export function distanciaMinima(nico, objetos, parte = 'cabeca') {
  nico.group.updateMatrixWorld(true);
  const corpo = resolveProxies(nico.proxies.filter((p) => p.name === parte), nico.joints);
  let best = Infinity;
  let item = null;
  for (const o of objetos) {
    o.obj.updateWorldMatrix(true, true);
    for (const p of o.proxies) {
      const [r] = resolveProxies([{ ...p, obj: o.obj }], nico.joints);
      for (const c of corpo) {
        const d = distance(r, c);
        if (d < best) {
          best = d;
          item = p.name;
        }
      }
    }
  }
  return { dist: best, item };
}