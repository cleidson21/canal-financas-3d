// Objetos novos do EP001 em roda (câmera orbita): peixe, lenha, galão, caixa de ovos,
// saco de farinha e saco de batata, no terraço baixo.
import * as THREE from 'three';
import { createTerracoBaixo } from '/biblioteca/cenarios/terraco_baixo.js';
import { createFish } from '/biblioteca/objetos/peixe.js';
import { createFirewood } from '/biblioteca/objetos/lenha.js';
import { createMilkJug } from '/biblioteca/objetos/galao_leite.js';
import { createEggBox } from '/biblioteca/objetos/caixa_ovos.js';
import { createFlourSack } from '/biblioteca/objetos/saco_farinha.js';
import { createSack } from '/biblioteca/objetos/saco.js';
import { frame } from '/biblioteca/camera/presets.js';

export const DURACAO = 10;
let ctx, cen;

export function build(c) {
  ctx = c;
  cen = createTerracoBaixo(ctx);
  const fabricas = [createSack, createFish, createFirewood, createMilkJug, createEggBox, createFlourSack];
  fabricas.forEach((f, i) => {
    const o = f();
    const a = (i / fabricas.length) * Math.PI * 2;
    o.position.set(Math.cos(a) * 0.55, 0, Math.sin(a) * 0.55);
    o.rotation.y = -a + Math.PI / 2;
    ctx.scene.add(o);
  });
  cen.seguir(0, 0);
}

export function renderFrame(t) {
  cen.update(t);
  frame(ctx.camera, 'medio', [0, 0.1, 0], { azimute: (360 * t) / DURACAO, alturaVisivelM: 1.9, inclinacaoGraus: 22 });
}
