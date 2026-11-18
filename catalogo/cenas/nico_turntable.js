// Turntable do Nico: câmera orbita 360° em 8 s ao redor do personagem parado.
import { createStudio } from '/biblioteca/cenarios/estudio.js';
import { createNico } from '/biblioteca/personagens/nico/index.js';
import { frame } from '/biblioteca/camera/presets.js';

export const DURACAO = 8;
let ctx, nico;

export function build(c) {
  ctx = c;
  createStudio(ctx.scene);
  nico = createNico();
  ctx.scene.add(nico.group);
}

export function renderFrame(t) {
  const pose = ctx.params.pose || 'idle';
  nico.setPose(pose, t);
  frame(ctx.camera, 'medio', [0, 0.62, 0], { azimute: (360 * t) / DURACAO, alturaVisivelM: 1.55, inclinacaoGraus: 6 });
}

