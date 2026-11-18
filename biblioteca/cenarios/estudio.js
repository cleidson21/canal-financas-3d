// Cenário neutro de catálogo: chão com grade de 0,1 m (para ver deslize de pé),
// fundo liso, luz de céu + sol com sombra. Tudo vindo de tokens.
import * as THREE from 'three';
import { token, material } from '../nucleo/materiais.js';

export function createStudio(scene, { tamanho = 8, grade = 0.1 } = {}) {
  scene.background = new THREE.Color(token('cores.cena.fundo'));
  const luz = token('luz');
  const hemi = new THREE.HemisphereLight(new THREE.Color(luz.ceu), new THREE.Color(luz.solo), luz.hemisferioIntensidade);
  scene.add(hemi);
  const sol = new THREE.DirectionalLight(new THREE.Color(luz.sol), luz.solIntensidade);
  sol.position.set(...luz.solDirecao);
  sol.castShadow = true;
  sol.shadow.mapSize.set(luz.sombraMapa, luz.sombraMapa);
  const s = 2.5;
  Object.assign(sol.shadow.camera, { left: -s, right: s, top: s, bottom: -s, near: 0.1, far: 30 });
  sol.shadow.bias = -0.0005;
  sol.shadow.normalBias = 0.01;
  scene.add(sol, sol.target);

  const chao = new THREE.Mesh(new THREE.PlaneGeometry(tamanho, tamanho), material('cores.cena.chao', { flat: false }));
  chao.name = 'chao';
  chao.rotation.x = -Math.PI / 2;
  chao.receiveShadow = true;
  scene.add(chao);

  // Linhas da grade como faixas finas (malhas, para sair no passe de cor também)
  const linhas = new THREE.Group();
  linhas.name = 'grade';
  const n = Math.round(tamanho / grade);
  const g = new THREE.PlaneGeometry(tamanho, 0.004);
  const mat = material('cores.cena.chaoLinha', { flat: false });
  for (let i = 0; i <= n; i++) {
    const v = -tamanho / 2 + i * grade;
    const forte = Math.abs(v - Math.round(v)) < 1e-6;
    const a = new THREE.Mesh(g, mat);
    a.rotation.x = -Math.PI / 2;
    a.position.set(0, 0.0005, v);
    a.scale.y = forte ? 2.5 : 1;
    const b = a.clone();
    b.rotation.z = Math.PI / 2;
    b.position.set(v, 0.0006, 0);
    linhas.add(a, b);
  }
  linhas.traverse((o) => o.isMesh && (o.receiveShadow = true));
  scene.add(linhas);

  // A sombra acompanha um alvo (o personagem) para manter resolução
  const seguir = (x, z) => {
    sol.position.set(x + luz.solDirecao[0], luz.solDirecao[1], z + luz.solDirecao[2]);
    sol.target.position.set(x, 0, z);
  };
  return { hemi, sol, chao, linhas, seguir };
}

