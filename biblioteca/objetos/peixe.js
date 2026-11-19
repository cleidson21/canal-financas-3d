// Peixe (rascunho). Deitado de barriga para baixo, cabeça em +X. Origem no centro do fundo.
import * as THREE from 'three';
import { material } from '../nucleo/materiais.js';

export function createFish() {
  const g = new THREE.Group();
  g.name = 'peixe';
  const mk = (geo, tok, pos, rot = [0, 0, 0], sc = [1, 1, 1], nome = 'peixe_parte') => {
    const m = new THREE.Mesh(geo, material(tok));
    m.name = nome;
    m.position.set(...pos);
    m.rotation.set(...rot);
    m.scale.set(...sc);
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
    return m;
  };
  mk(new THREE.SphereGeometry(1, 12, 8), 'cores.objetos.peixe', [0, 0.05, 0], [0, 0, 0], [0.15, 0.05, 0.04], 'peixe_corpo');
  // barriga clara: fatia inferior achatada
  mk(new THREE.SphereGeometry(1, 12, 6), 'cores.objetos.peixeBarriga', [0.005, 0.034, 0], [0, 0, 0], [0.135, 0.028, 0.036], 'peixe_barriga');
  // cauda em leque (vértice junto ao corpo, aberta para fora), achatada em Z
  mk(new THREE.ConeGeometry(0.052, 0.085, 4), 'cores.objetos.peixeNadadeira', [-0.2, 0.05, 0], [0, 0, -Math.PI / 2], [1, 1, 0.22], 'peixe_cauda');
  mk(new THREE.ConeGeometry(0.03, 0.05, 4), 'cores.objetos.peixeNadadeira', [-0.02, 0.1, 0], [0, 0, 0], [1, 1, 0.25], 'peixe_dorsal');
  for (const k of [1, -1]) {
    mk(new THREE.SphereGeometry(0.014, 8, 6), 'cores.objetos.peixeOlho', [0.1, 0.062, k * 0.034], [0, 0, 0], [1, 1, 0.7], 'peixe_olho');
    mk(new THREE.SphereGeometry(0.0075, 8, 6), 'cores.objetos.peixePupila', [0.104, 0.062, k * 0.0425], [0, 0, 0], [1, 1, 0.6], 'peixe_pupila');
  }
  g.userData.altura = 0.12;
  g.userData.profundidade = 0.09;
  g.userData.largura = 0.36;
  g.userData.grip = { default: [0, 0.05, 0] };
  g.userData.proxies = [{ name: 'peixe', type: 'box', center: [-0.03, 0.055, 0], half: [0.19, 0.06, 0.045], r: 0.02 }];
  return g;
}
