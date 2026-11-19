// Feixe de lenha (rascunho): 5 toras amarradas por corda, deitadas ao longo de X.
import * as THREE from 'three';
import { material } from '../nucleo/materiais.js';
import { rng } from '../nucleo/matematica.js';

export function createFirewood() {
  const g = new THREE.Group();
  g.name = 'lenha';
  const r = 0.035;
  const comp = 0.34;
  const rand = rng(11);
  const lado = material('cores.objetos.lenha');
  const miolo = material('cores.objetos.lenhaMiolo');
  const geo = new THREE.CylinderGeometry(r, r, comp, 8, 1);
  const pos = [
    [0, r, -0.075], [0, r, 0], [0, r, 0.075],
    [0, r + 0.063, -0.0375], [0, r + 0.063, 0.0375],
  ];
  pos.forEach((p, i) => {
    // eixo do cilindro (Y) deitado ao longo de X; grupos do cilindro: [lado, topo, fundo]
    const m = new THREE.Mesh(geo, [lado, miolo, miolo]);
    m.name = 'lenha_tora';
    m.position.set(p[0] + (rand() - 0.5) * 0.02, p[1], p[2]);
    m.rotation.set(0, (rand() - 0.5) * 0.12, Math.PI / 2);
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
  });
  const corda = new THREE.Mesh(new THREE.BoxGeometry(0.024, 0.145, 0.245), material('cores.objetos.corda'));
  corda.name = 'lenha_corda';
  corda.position.set(0, 0.0675, 0);
  corda.castShadow = true;
  g.add(corda);
  g.userData.altura = 0.135;
  g.userData.profundidade = 0.25;
  g.userData.largura = comp;
  g.userData.grip = { default: [0, 0.065, 0] };
  g.userData.proxies = [{ name: 'lenha', type: 'box', center: [0, 0.0675, 0], half: [comp / 2, 0.0675, 0.125], r: 0.02 }];
  return g;
}
