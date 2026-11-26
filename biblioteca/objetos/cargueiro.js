// Cargueiro de madeira: armação simples (2 barras verticais + 2 travessas) com uma
// prateleira atrás, presa ao socket `costas` do Nico. A torre assenta na prateleira.
// Duas alças de corda passam por cima de cada ombro e terminam nas mãos (fechadas).
//   const carga = createCarrier();
//   carga.userData.mount.add(torre);       // a torre se prende ao cargueiro
//   nico.grab(carga, 'costas');            // a cada quadro
//   carga.userData.atualizar(nico);        // a cada quadro, depois da pose (alças seguem as mãos)
// Eixo local: +Y ao longo da armação, +Z para o Nico (frente da armação em z = 0), -Z para trás.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { material } from '../nucleo/materiais.js';

const Y = new THREE.Vector3(0, 1, 0);

function segmento(m, a, b) {
  const d = b.clone().sub(a);
  const len = Math.max(1e-5, d.length());
  m.position.copy(a).addScaledVector(d, 0.5);
  m.quaternion.setFromUnitVectors(Y, d.normalize());
  m.scale.set(1, len, 1);
}

export function createCarrier({ alturaBarras = 0.62 } = {}) {
  const g = new THREE.Group();
  g.name = 'cargueiro';
  const madeira = material('cores.objetos.cargueiro');
  const trav = material('cores.objetos.cargueiroTravessa');
  const mk = (geo, mat, pos, nome) => {
    const m = new THREE.Mesh(geo, mat);
    m.name = nome;
    m.position.set(...pos);
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
    return m;
  };
  const E = 0.025; // espessura das barras
  const barra = new RoundedBoxGeometry(E, alturaBarras + 0.03, E, 1, 0.006);
  for (const x of [-0.085, 0.085]) mk(barra, madeira, [x, (alturaBarras - 0.03) / 2, -E / 2], 'cargueiro_barra');
  mk(new RoundedBoxGeometry(0.205, 0.035, E, 1, 0.006), trav, [0, 0, -E / 2], 'cargueiro_travessa_baixa');
  mk(new RoundedBoxGeometry(0.205, 0.03, E, 1, 0.006), trav, [0, 0.2, -E / 2], 'cargueiro_travessa_alta');
  // prateleira onde a torre assenta (topo em y = 0.0175)
  mk(new RoundedBoxGeometry(0.27, 0.025, 0.2, 1, 0.006), trav, [0, 0.005, -E - 0.1], 'cargueiro_prateleira');

  // ponto de montagem da torre: em cima da prateleira, rente à frente dos itens
  const mount = new THREE.Group();
  mount.name = 'cargueiro_mount';
  mount.position.set(0, 0.0175, -E - 0.002);
  g.add(mount);

  // alças: 3 segmentos fixos no tronco + 1 até a mão
  const geo = new THREE.CylinderGeometry(0.006, 0.006, 1, 6);
  const mc = material('cores.objetos.corda');
  const alcas = {};
  for (const [s, k] of [['L', 1], ['R', -1]]) {
    const segs = [0, 1, 2].map(() => {
      const m = new THREE.Mesh(geo, mc);
      m.name = 'cargueiro_alca';
      m.castShadow = true;
      g.add(m);
      return m;
    });
    const no = new THREE.Mesh(new THREE.SphereGeometry(0.014, 8, 6), mc);
    no.name = 'cargueiro_alca_no';
    g.add(no);
    alcas[s] = { k, segs, no };
  }
  const _a = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];

  g.userData.mount = mount;
  g.userData.alturaBarras = alturaBarras;
  g.userData.grip = { costas: [0, 0, 0], default: [0, 0, 0] };
  // volumes de colisão (auditoria)
  g.userData.proxies = [
    { name: 'cargueiro_barraE', type: 'box', center: [-0.085, alturaBarras / 2, -E / 2], half: [E / 2, alturaBarras / 2 + 0.015, E / 2], r: 0.005 },
    { name: 'cargueiro_barraD', type: 'box', center: [0.085, alturaBarras / 2, -E / 2], half: [E / 2, alturaBarras / 2 + 0.015, E / 2], r: 0.005 },
    { name: 'cargueiro_travessaB', type: 'box', center: [0, 0, -E / 2], half: [0.1025, 0.0175, E / 2], r: 0.005 },
    { name: 'cargueiro_travessaA', type: 'box', center: [0, 0.2, -E / 2], half: [0.1025, 0.015, E / 2], r: 0.005 },
    { name: 'cargueiro_prateleira', type: 'box', center: [0, 0.005, -E - 0.1], half: [0.135, 0.0125, 0.1], r: 0.005 },
  ];

  // Pontos fixos no referencial do tronco (spine): topo do ombro e peito.
  g.userData.atualizar = (nico) => {
    g.updateWorldMatrix(true, true);
    const spine = nico.joints.spine;
    for (const s of ['L', 'R']) {
      const { k, segs, no } = alcas[s];
      // P0: travessa alta do cargueiro (espaço local da armação)
      _a[0].set(k * 0.085, 0.2, -E / 2);
      // P1: por cima do ombro; P2: peito; P3: mão (socket)
      const toLocal = (v) => g.worldToLocal(spine.localToWorld(v));
      _a[1].copy(toLocal(new THREE.Vector3(k * 0.115, 0.298, -0.005)));
      _a[2].copy(toLocal(new THREE.Vector3(k * 0.125, 0.2, 0.112)));
      nico.sockets['hand' + s].getWorldPosition(_a[3]);
      g.worldToLocal(_a[3]);
      segmento(segs[0], _a[0], _a[1]);
      segmento(segs[1], _a[1], _a[2]);
      segmento(segs[2], _a[2], _a[3]);
      no.position.copy(_a[3]);
    }
  };
  return g;
}
