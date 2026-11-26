// Torre de mercadorias, empilhada na prateleira do cargueiro (ver cargueiro.js).
//   const torre = createTower({ quantidade: 6, altura: 1.45 });
//   cargueiro.userData.mount.add(torre);
//   torre.userData.balancar(latGraus, frenteGraus);   // rotação rígida em torno da base (±3°)
//   torre.userData.update(t);                         // balanço próprio por senos (uso avulso)
// Ordem de baixo para cima: batata, lenha, galão, ovos, farinha e, no alto, o peixe
// (quantidade 1 = só o saco de batata). O peixe fica DEITADO de perfil (cabeça junto da
// armação, rabo para fora, atrás), 1,5× o tamanho original. Os itens ficam com a frente
// encostada na armação (z = 0) para a pilha ficar rente às costas.
// `altura` é a altura desejada, limitada por `alturaMax` (padrão 1,8 × altura do Nico);
// a escala dos itens fica em [0.55, 1.1], então userData.alturaReal pode diferir.
import * as THREE from 'three';
import { material, token } from '../nucleo/materiais.js';
import { rng, DEG } from '../nucleo/matematica.js';
import { createSack } from './saco.js';
import { createFish } from './peixe.js';
import { createFirewood } from './lenha.js';
import { createMilkJug } from './galao_leite.js';
import { createEggBox } from './caixa_ovos.js';
import { createFlourSack } from './saco_farinha.js';

export const TORRE_BASE = ['batata', 'lenha', 'galao', 'ovos', 'farinha'];
const FABRICA = {
  batata: () => {
    const s = createSack();
    s.userData.profundidade = 0.2;
    s.userData.largura = 0.27;
    return s;
  },
  peixe: createFish,
  lenha: createFirewood,
  galao: createMilkJug,
  ovos: createEggBox,
  farinha: createFlourSack,
};
const ESCALA_PEIXE = 1.5;

export function createTower({ quantidade = 6, altura = 1.45, alturaMax = null, semente = 7 } = {}) {
  const maxH = alturaMax ?? token('escala.torre.alturaMaxNicos') * token('escala.nico.altura');
  const n = Math.max(1, Math.round(quantidade));
  const nomes = n === 1 ? ['batata'] : [...Array.from({ length: n - 1 }, (_, i) => TORRE_BASE[i % TORRE_BASE.length]), 'peixe'];
  const g = new THREE.Group();
  g.name = 'torre';
  const rand = rng(semente);
  const itens = nomes.map((nm) => FABRICA[nm]());
  const base = itens.filter((_, i) => nomes[i] !== 'peixe');
  const somaBase = base.reduce((s, o) => s + o.userData.altura, 0);
  const peixeH = nomes.includes('peixe') ? itens[nomes.indexOf('peixe')].userData.altura * ESCALA_PEIXE : 0;
  const alvo = Math.min(altura, maxH);
  const k = Math.min(1.1, Math.max(0.55, (alvo - peixeH) / somaBase));
  const profPilha = Math.max(...base.map((o) => o.userData.profundidade)) * k;

  const slots = [];
  let y = 0;
  itens.forEach((o, i) => {
    const peixe = nomes[i] === 'peixe';
    const esc = peixe ? ESCALA_PEIXE : k;
    o.scale.setScalar(esc);
    const slot = new THREE.Group();
    slot.name = 'torre_slot';
    slot.position.y = y;
    if (peixe) {
      // de perfil: cabeça (+X do modelo) vira +Z, encostada na frente da armação; corpo e rabo
      // saem para trás da pilha (nunca para a frente, onde está a cabeça do Nico)
      o.rotation.y = -Math.PI / 2;
      o.position.set(0, 0, -0.16 * esc - 0.005);
    } else {
      o.rotation.y = (rand() - 0.5) * 0.14;
      o.position.set((rand() - 0.5) * 0.02, 0, -(o.userData.profundidade * esc) / 2); // frente rente à armação
    }
    slot.add(o);
    g.add(slot);
    slots.push(slot);
    y += o.userData.altura * esc;
  });
  g.userData.alturaReal = y;
  g.userData.escala = k;
  g.userData.quantidade = n;
  g.userData.itens = itens;
  g.userData.nomes = nomes;
  g.userData.alturaMax = maxH;
  // itens da pilha (sem o peixe) para medir o centro
  g.userData.centro = () => {
    g.updateWorldMatrix(true, true);
    const c = new THREE.Vector3();
    const b = new THREE.Box3();
    let cnt = 0;
    itens.forEach((o, i) => {
      if (nomes[i] === 'peixe') return;
      b.setFromObject(o);
      c.add(b.getCenter(new THREE.Vector3()));
      cnt++;
    });
    return c.multiplyScalar(1 / cnt);
  };

  // Balanço rígido em torno da base (a prateleira): lateral (eixo Z) e frente-trás (eixo X).
  g.userData.balancar = (latGraus, frenteGraus = 0) => {
    g.rotation.set(frenteGraus * DEG, 0, latGraus * DEG);
  };
  // Balanço próprio por senos (uso avulso, ±3°): duas frequências incomensuráveis.
  g.userData.update = (t, amp = 1) => {
    const lat = 3 * amp * (0.75 * Math.sin(2 * Math.PI * 0.42 * t) + 0.25 * Math.sin(2 * Math.PI * 1.07 * t + 1.3));
    const fr = 1.5 * amp * Math.sin(2 * Math.PI * 0.31 * t + 0.8);
    g.userData.balancar(lat, fr);
  };
  g.userData.update(0);
  return g;
}
