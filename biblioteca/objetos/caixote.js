// Caixote de feira (apoio). Origem no centro do fundo; topo em y = altura.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { material } from '../nucleo/materiais.js';

export function createCrate({ largura = 0.4, altura = 0.35, profundidade = 0.32 } = {}) {
  const g = new THREE.Group();
  g.name = 'caixote';
  const corpo = new THREE.Mesh(new RoundedBoxGeometry(largura, altura, profundidade, 1, 0.012), material('cores.objetos.caixote'));
  corpo.name = 'caixote_corpo';
  corpo.position.y = altura / 2;
  g.add(corpo);
  // ripas horizontais (relevo) na frente e atrás
  const ripa = new THREE.BoxGeometry(largura + 0.006, altura * 0.12, 0.012);
  for (const z of [1, -1])
    for (const f of [0.25, 0.75]) {
      const r = new THREE.Mesh(ripa, material('cores.objetos.caixoteRipa'));
      r.name = 'caixote_ripa';
      r.position.set(0, altura * f, (z * profundidade) / 2);
      g.add(r);
    }
  g.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true;
      o.receiveShadow = true;
    }
  });
  g.userData.altura = altura;
  g.userData.proxies = [{ name: 'caixote', type: 'box', center: [0, altura / 2, 0], half: [largura / 2, altura / 2, profundidade / 2], r: 0.012 }];
  return g;
}

