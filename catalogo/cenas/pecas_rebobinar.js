// REBOBINAR sobre a cena: Nico cambaleia com a torre (DIA 3); em t0 o tempo corre ao
// contrário com linhas de varredura e ◀◀; ao fim o contador troca para DIA 1 com pop e
// a cena recomeça do início.
import { montar } from './_ep001_comum.js';
import { frame } from '/biblioteca/camera/presets.js';
import { createDiaCounter } from '/biblioteca/efeitos/contador_dia.js';
import { createRewind } from '/biblioteca/efeitos/rebobinar.js';

export const T0 = 1.7;
export const DUR = 1.2;
export const DURACAO = 5;
let ctx, M, hud, rw, mov;

export function build(c) {
  ctx = c;
  M = montar(ctx, { descalco: true, quantidade: 6, altura: 1.7 });
  mov = M.nico.play('cambalear', 0, { from: [-0.5, 0], to: [0.55, 0], duration: 4.2, upper: 'carga_costas', expr: 'cansada' });
  rw = createRewind(ctx, { t0: T0, duracao: DUR, volta: 0 });
  hud = createDiaCounter(ctx, [{ t: -99, dia: 3 }, { t: T0 + DUR, dia: 1 }]);
}

export function renderFrame(t) {
  const tc = rw.tempoCena(t); // o tempo da cena corre ao contrário durante o rebobinar
  mov(tc);
  M.prender(tc);
  M.cen.update(tc);
  M.cen.seguir(M.nico.group.position.x, 0);
  frame(ctx.camera, 'medio', [0.0, 0.95, 0], { azimute: 14, alturaVisivelM: 3.0, inclinacaoGraus: 3 });
  rw.update(t);
  hud.update(t);
}
export function marcos() {
  return { antes: 1.1, linhas: T0 + 0.35, icone: T0 + 0.6, depois: T0 + DUR + 0.2 };
}
