// Galão de leite (rascunho): corpo torneado, faixa azul, tampa verde e alça lateral (+X).
import * as THREE from 'three';
import { material } from '../nucleo/materiais.js';

export function createMilkJug() {
  const g = new THREE.Group();
  g.name = 'galao';
  const mk = (geo, tok, pos, rot = [0, 0, 0], nome) => {
    const m = new THREE.Mesh(geo, material(tok));
    m.name = nome;
    m.position.set(...pos);
    m.rotation.set(...rot);
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
    return m;
  };
  const prof = [[0, 0], [0.085, 0], [0.1, 0.018], [0.1, 0.17], [0.085, 0.22], [0.045, 0.248], [0.04, 0.275], [0, 0.275]].map(([r, y]) => new THREE.Vector2(r, y));
  mk(new THREE.LatheGeometry(prof, 12), 'cores.objetos.galao', [0, 0, 0], [0, 0, 0], 'galao_corpo');
  mk(new THREE.CylinderGeometry(0.1035, 0.1035, 0.05, 12, 1, true), 'cores.objetos.galaoFaixa', [0, 0.1, 0], [0, 0, 0], 'galao_faixa');
  mk(new THREE.CylinderGeometry(0.046, 0.046, 0.034, 10), 'cores.objetos.galaoTampa', [0, 0.292, 0], [0, 0, 0], 'galao_tampa');
  mk(new THREE.TorusGeometry(0.052, 0.011, 6, 10, Math.PI), 'cores.objetos.galao', [0.095, 0.15, 0], [0, 0, -Math.PI / 2], 'galao_alca');
  g.userData.altura = 0.31;
  g.userData.profundidade = 0.2;
  g.userData.largura = 0.27;
  g.userData.grip = { default: [0, 0.15, 0] };
  g.userData.proxies = [{ name: 'galao', type: 'box', center: [0.02, 0.155, 0], half: [0.14, 0.155, 0.1], r: 0.05 }];
  return g;
}
