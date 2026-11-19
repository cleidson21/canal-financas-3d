// Saco de farinha (rascunho): almofada clara com boca amarrada e rótulo vermelho.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { material } from '../nucleo/materiais.js';

export function createFlourSack() {
  const g = new THREE.Group();
  g.name = 'saco_farinha';
  const add = (geo, tok, pos, nome) => {
    const m = new THREE.Mesh(geo, material(tok));
    m.name = nome;
    m.position.set(...pos);
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
    return m;
  };
  add(new RoundedBoxGeometry(0.24, 0.27, 0.13, 2, 0.055), 'cores.objetos.farinha', [0, 0.135, 0], 'farinha_corpo');
  add(new RoundedBoxGeometry(0.1, 0.06, 0.075, 2, 0.025), 'cores.objetos.farinha', [0, 0.285, 0], 'farinha_boca');
  add(new THREE.BoxGeometry(0.11, 0.01, 0.082), 'cores.objetos.sacoAmarra', [0, 0.262, 0], 'farinha_amarra');
  add(new THREE.BoxGeometry(0.13, 0.1, 0.004), 'cores.objetos.farinhaRotulo', [0, 0.14, 0.0655], 'farinha_rotulo');
  g.userData.altura = 0.315;
  g.userData.profundidade = 0.13;
  g.userData.largura = 0.24;
  g.userData.grip = { default: [0, 0.14, 0] };
  g.userData.proxies = [{ name: 'farinha', type: 'box', center: [0, 0.15, 0], half: [0.12, 0.155, 0.065], r: 0.04 }];
  return g;
}
