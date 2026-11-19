// CUBO PLOC!: cai do céu em frente ao Nico, quica com squash/stretch e some com pop
// dando lugar ao contador DIA (que entra com pop no instante em que o cubo termina de sumir).
import { montar } from './_ep001_comum.js';
import { frame } from '/biblioteca/camera/presets.js';
import { createDiaCounter } from '/biblioteca/efeitos/contador_dia.js';
import { createPlocCube } from '/biblioteca/efeitos/cubo_ploc.js';

export const DURACAO = 4;
let ctx, M, hud, cubo, mov;

export function build(c) {
  ctx = c;
  M = montar(ctx, { descalco: true, quantidade: 6, altura: 1.7 });
  mov = M.nico.play('exausto_com_carga', 0);
  cubo = createPlocCube(ctx.scene, { pos: [0.75, 0, 0.35], t0: 0.3, alturaQueda: 4.2, lado: 0.3 });
  hud = createDiaCounter(ctx, [{ t: cubo.tAparece, dia: 1 }]);
}

export function renderFrame(t) {
  mov(t);
  M.prender(t);
  M.cen.update(t);
  M.cen.seguir(0.3, 0.3);
  frame(ctx.camera, 'medio', [0.15, 0.95, 0], { azimute: 70, alturaVisivelM: 3.1, inclinacaoGraus: 3 });
  cubo.update(t);
  hud.update(t);
}

export function marcos() {
  const i = cubo.impactos[0].t;
  return { queda: i - 0.14, squash: i + 0.05, pop: cubo.tPop + 0.1, contador: cubo.tAparece + 0.2, tAparece: cubo.tAparece, tPouso: cubo.tPouso };
}
