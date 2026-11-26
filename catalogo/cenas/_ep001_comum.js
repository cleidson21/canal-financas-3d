// Base comum das cenas de verificação das peças do EP001.
// Monta terraço baixo + Nico (opções) + cargueiro nas costas + torre sobre o cargueiro.
import * as THREE from 'three';
import { createTerracoBaixo } from '/biblioteca/cenarios/terraco_baixo.js';
import { createNico } from '/biblioteca/personagens/nico/index.js';
import { createTower } from '/biblioteca/objetos/torre_mercadorias.js';
import { createCarrier } from '/biblioteca/objetos/cargueiro.js';
import { frameNicoTorre } from '/biblioteca/camera/presets.js';
import { distanciaMinima } from '/biblioteca/personagens/nico/checagem.js';

export function montar(ctx, { descalco = true, sapatoQuebrado = false, quantidade = 6, altura = 1.45, comTorre = true } = {}) {
  const cen = createTerracoBaixo(ctx);
  const nico = createNico({ descalco, sapatoQuebrado });
  ctx.scene.add(nico.group);
  let torre = null;
  let carrier = null;
  if (comTorre) {
    carrier = createCarrier();
    torre = createTower({ quantidade, altura });
    carrier.userData.mount.add(torre);
    ctx.scene.add(carrier);
  }
  // Encaixa o cargueiro e atualiza alças e balanço. A torre balança em oposição à
  // inclinação lateral do tronco (±3°) e um pouco para frente e para trás.
  const prender = (t) => {
    if (!torre) return;
    nico.grab(carrier, 'costas');
    const lado = nico.pose.spine.side || 0; // ±7° no cambalear
    torre.userData.balancar((lado * 3) / 7, 1.2 * Math.sin(2 * Math.PI * 0.5 * t));
    carrier.userData.atualizar(nico);
  };
  // altura do ponto mais alto: costas (≈0,5 m) + torre; sempre ≥ Nico
  const alturaTotal = torre ? Math.max(1.7, 0.5 + torre.userData.alturaReal) : 1.7;
  // o conjunto Nico+torre se estende para trás: o alvo recua 22 cm contra o rumo do Nico
  const enquadrar = (az, x = 0) => {
    const h = nico.group.rotation.y;
    return frameNicoTorre(ctx.camera, alturaTotal, { azimute: az, alvoX: x - 0.22 * Math.sin(h), alvoZ: -0.22 * Math.cos(h) });
  };
  const auditoria = () => {
    const o = [];
    if (torre) {
      for (const it of torre.userData.itens) o.push({ obj: it, proxies: it.userData.proxies });
      o.push({ obj: carrier, proxies: carrier.userData.proxies });
    }
    return o;
  };
  // métricas da carga no instante atual (a pose já aplicada)
  const medir = () => {
    const m = nico.measure();
    const J = nico.joints;
    const out = {
      joelhoL: m.joelhoL.flex,
      joelhoR: m.joelhoR.flex,
      tronco: m.tronco.flex,
      cotoveloL: m.cotoveloL.flex,
      cotoveloR: m.cotoveloR.flex,
      pelveDropCm: (nico.skeleton.standPelvisY - J.pelvis.position.y) * 100,
    };
    if (torre) {
      const d = distanciaMinima(nico, auditoria());
      out.cabecaMm = d.dist * 1000;
      out.cabecaItem = d.item;
      // centro da pilha (sem o peixe) até as costas, na horizontal, ao longo do rumo do Nico
      const h = nico.group.rotation.y;
      const fwd = new THREE.Vector3(Math.sin(h), 0, Math.cos(h));
      const costas = J.spine.localToWorld(new THREE.Vector3(0, 0.06, -0.1)); // costas na altura da base da torre
      out.pilhaCostasCm = costas.clone().sub(torre.userData.centro()).setY(0).dot(fwd) * 100;
      out.torreLat = torre.rotation.z / (Math.PI / 180);
      out.torreFrente = torre.rotation.x / (Math.PI / 180);
    }
    return out;
  };
  return { cen, nico, torre, carrier, prender, enquadrar, auditoria, medir, alturaTotal };
}
