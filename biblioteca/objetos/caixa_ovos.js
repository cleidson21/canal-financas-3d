// Caixa de ovos (rascunho): cartela com 6 ovos e tampa aberta atrás (-Z).
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { material } from '../nucleo/materiais.js';

export function createEggBox() {
  const g = new THREE.Group();
  g.name = 'caixa_ovos';
  const cart = material('cores.objetos.cartela');
  const base = new THREE.Mesh(new RoundedBoxGeometry(0.26, 0.05, 0.17, 1, 0.01), cart);
  base.name = 'ovos_cartela';
  base.position.set(0, 0.025, 0);
  g.add(base);
  const ovoGeo = new THREE.SphereGeometry(0.03, 10, 8);
  for (const x of [-0.075, 0, 0.075])
    for (const z of [-0.04, 0.04]) {
      const o = new THREE.Mesh(ovoGeo, material('cores.objetos.ovo'));
      o.name = 'ovo';
      o.position.set(x, 0.05 + 0.012, z);
      o.scale.set(1, 1.25, 1);
      o.castShadow = true;
      o.receiveShadow = true;
      g.add(o);
    }
  // tampa articulada na borda de trás, aberta ~100°
  const hinge = new THREE.Group();
  hinge.name = 'ovos_dobradica';
  hinge.position.set(0, 0.05, -0.085);
  hinge.rotation.x = (-100 * Math.PI) / 180;
  const tampa = new THREE.Mesh(new RoundedBoxGeometry(0.26, 0.012, 0.1, 1, 0.005), cart);
  tampa.name = 'ovos_tampa';
  tampa.position.set(0, 0, 0.05);
  hinge.add(tampa);
  g.add(hinge);
  g.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true;
      o.receiveShadow = true;
    }
  });
  g.userData.altura = 0.15;
  g.userData.profundidade = 0.19;
  g.userData.largura = 0.26;
  g.userData.grip = { default: [0, 0.03, 0] };
  g.userData.proxies = [{ name: 'ovos', type: 'box', center: [0, 0.07, -0.01], half: [0.13, 0.075, 0.095], r: 0.015 }];
  return g;
}
