// CUBO PLOC!: cai do céu em frente ao Nico, quica com squash/stretch e some com pop. O
// contador DIA nasce onde o cubo sumiu (posição de tela) e desliza até o canto em ~0,3 s.
import { montar } from './_ep001_comum.js';
import { createDiaCounter } from '/biblioteca/efeitos/contador_dia.js';
import { createPlocCube } from '/biblioteca/efeitos/cubo_ploc.js';

export const DURACAO = 4;
let ctx, M, hud, cubo, mov;

export function build(c) {
  ctx = c;
  M = montar(ctx, { descalco: true, quantidade: 6, altura: 1.45 });
  mov = M.nico.play('exausto_com_carga', 0);
  cubo = createPlocCube(ctx.scene, { pos: [0.7, 0, 0.45], t0: 0.3, alturaQueda: 4.2 });
  hud = createDiaCounter(ctx, [{ t: cubo.tAparece, dia: 1, de: cubo.centro }]);
}

export function renderFrame(t) {
  mov(t);
  M.prender(t);
  M.cen.update(t);
  M.cen.seguir(0.3, 0.3);
  M.enquadrar(70, 0.1);
  cubo.update(t);
  hud.update(t);
}

export function marcos() {
  const i = cubo.impactos[0].t;
  return { queda: i - 0.1, squash: i + 0.05, pop: cubo.tPop + 0.1, contador: cubo.tAparece + 0.1, tAparece: cubo.tAparece, tPouso: cubo.tPouso, impactos: cubo.impactos.map((x) => x.t) };
}

// escala do cubo (sy, sxz) e visibilidade no instante t
export function medirCubo(t) {
  renderFrame(t);
  const piv = cubo.group.children[0];
  return { t, visivel: cubo.group.visible, sy: piv.scale.y, sx: piv.scale.x, y: piv.position.y };
}
