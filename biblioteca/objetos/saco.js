// Saco de batata (low-poly, torneado). Origem no centro do fundo (y=0 = chão).
import * as THREE from 'three';
import { material } from '../nucleo/materiais.js';

export function createSack({ altura = 0.35, raio = 0.135, profundidade = 0.75 } = {}) {
  const g = new THREE.Group();
  g.name = 'saco';
  const s = altura / 0.35;
  const kr = raio / 0.145; // largura máxima = 2·raio
  const prof = [
    [0, 0], [0.1, 0], [0.135, 0.03], [0.145, 0.1], [0.14, 0.19], [0.12, 0.25], [0.078, 0.29], [0.05, 0.305], [0.062, 0.33], [0.03, 0.348], [0, 0.35],
  ].map(([r, y]) => new THREE.Vector2(r * kr, y * s));
  const corpo = new THREE.Mesh(new THREE.LatheGeometry(prof, 11), material('cores.objetos.saco'));
  corpo.name = 'saco_corpo';
  corpo.scale.z = profundidade;
  const amarra = new THREE.Mesh(new THREE.TorusGeometry(0.054 * s, 0.012 * s, 5, 12), material('cores.objetos.sacoAmarra'));
  amarra.name = 'saco_amarra';
  amarra.rotation.x = Math.PI / 2;
  amarra.position.y = 0.3 * s;
  amarra.scale.y = profundidade;
  for (const m of [corpo, amarra]) {
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
  }
  const hz = raio * profundidade;
  // pega: ponto entre os antebraços fica um pouco atrás do centro (abraço por trás)
  g.userData.grip = { forearms: [0, 0.15 * s, -0.055], default: [0, 0.33 * s, 0] };
  g.userData.proxies = [
    { name: 'saco', type: 'box', center: [0, 0.15 * s, 0], half: [raio, 0.15 * s, hz], r: 0.075 },
    { name: 'saco_topo', type: 'sphere', center: [0, 0.32 * s, 0], r: 0.05 * s },
  ];
  g.userData.altura = altura;
  return g;
}

