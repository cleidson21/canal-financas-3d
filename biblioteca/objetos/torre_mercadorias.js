// Torre de mercadorias: pilha de itens presa ao socket `costas` do Nico.
//   const torre = createTower({ quantidade: 6, altura: 1.0 });
//   nico.grab(torre, 'costas');          // a cada quadro (idempotente)
//   torre.userData.update(t);            // balanço determinístico (senos), sem física
// Ordem de baixo para cima: batata, peixe, lenha, galão, ovos, farinha (repete se quantidade > 6).
// `altura` é a altura desejada; a escala dos itens é limitada a [0.55, 1.5], então
// userData.alturaReal pode diferir (ex.: quantidade 1 com altura 1,0 não vira um saco gigante).
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { material } from '../nucleo/materiais.js';
import { rng } from '../nucleo/matematica.js';
import { createSack } from './saco.js';
import { createFish } from './peixe.js';
import { createFirewood } from './lenha.js';
import { createMilkJug } from './galao_leite.js';
import { createEggBox } from './caixa_ovos.js';
import { createFlourSack } from './saco_farinha.js';

export const TORRE_ORDEM = ['batata', 'peixe', 'lenha', 'galao', 'ovos', 'farinha'];
const FABRICA = {
  batata: () => {
    const s = createSack();
    s.userData.profundidade = 0.22;
    s.userData.largura = 0.27;
    return s;
  },
  peixe: createFish,
  lenha: createFirewood,
  galao: createMilkJug,
  ovos: createEggBox,
  farinha: createFlourSack,
};

export function createTower({ quantidade = 6, altura = 1.0, balanco = 1, semente = 7, fase = 0 } = {}) {
  const n = Math.max(1, Math.round(quantidade));
  const g = new THREE.Group();
  g.name = 'torre';
  const rand = rng(semente);
  const itens = Array.from({ length: n }, (_, i) => FABRICA[TORRE_ORDEM[i % TORRE_ORDEM.length]]());
  const somaH = itens.reduce((s, o) => s + o.userData.altura, 0);
  const k = Math.min(1.5, Math.max(0.55, altura / somaH));
  const prof = Math.max(...itens.map((o) => o.userData.profundidade)) * k;
  const larg = Math.max(...itens.map((o) => o.userData.largura)) * k;
  const conteudo = new THREE.Group();
  conteudo.name = 'torre_conteudo';
  conteudo.position.z = -prof / 2; // a carga se estende para trás das costas
  g.add(conteudo);

  // plataforma de carga sob a pilha
  const tabua = new THREE.Mesh(new RoundedBoxGeometry(larg * 0.9, 0.03, prof + 0.02, 1, 0.01), material('cores.objetos.tabua'));
  tabua.name = 'torre_tabua';
  tabua.position.set(0, -0.015, -prof / 2);
  tabua.castShadow = true;
  tabua.receiveShadow = true;
  g.add(tabua);

  const slots = [];
  let y = 0;
  for (const o of itens) {
    const slot = new THREE.Group();
    slot.name = 'torre_slot';
    o.scale.setScalar(k);
    o.rotation.y = (rand() - 0.5) * 0.35; // cada item levemente torto, fixo
    slot.add(o);
    const h = o.userData.altura * k;
    slot.position.set((rand() - 0.5) * 0.03, y, 0);
    slot.userData = { y0: y, yc: y + h / 2, x0: slot.position.x, f: 0.8 + rand() * 0.5, fase: rand() * 6.28 };
    conteudo.add(slot);
    slots.push(slot);
    y += h;
  }
  const H = y;
  g.userData.alturaReal = H;
  g.userData.escala = k;
  g.userData.quantidade = n;
  g.userData.itens = itens; // para auditoria: proxies por item
  g.userData.grip = { costas: [0, 0, 0], default: [0, 0, 0] };
  g.userData.proxies = [{ name: 'torre', type: 'box', center: [0, H / 2, -prof / 2], half: [larg / 2, H / 2, prof / 2], r: 0.02 }];

  // Balanço: a pilha se curva como uma vara; amplitude cresce com o quadrado da altura.
  // Duas senoides (lateral e frente-trás) com períodos incomensuráveis; sem aleatoriedade em t.
  g.userData.update = (t, amp = 1) => {
    const a = 0.07 * H * balanco * amp;
    const s1 = Math.sin(2 * Math.PI * 0.42 * t + fase) + 0.35 * Math.sin(2 * Math.PI * 1.07 * t + 1.3 + fase);
    const s2 = Math.sin(2 * Math.PI * 0.31 * t + 0.8 + fase) + 0.3 * Math.sin(2 * Math.PI * 0.93 * t + fase);
    for (const slot of slots) {
      const u = slot.userData.yc / H;
      const dx = a * u * u * s1;
      const dz = 0.45 * a * u * u * s2;
      slot.position.x = slot.userData.x0 + dx;
      slot.position.z = dz;
      // inclinação = derivada do deslocamento em y (cada item acompanha a curva)
      const dxdy = (2 * a * u * s1) / H;
      const dzdy = (0.9 * a * u * s2) / H;
      slot.rotation.z = -Math.atan(dxdy);
      slot.rotation.x = Math.atan(dzdy);
    }
  };
  g.userData.update(0);
  return g;
}
