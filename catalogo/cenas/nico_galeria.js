// Galeria de poses do Nico: 12 poses × 3 vistas (frente, perfil, três-quartos).
// t ∈ [0, 36): pose = floor(t/3), vista = floor(t) % 3. Fração de t = vida da pose.
import { createStudio } from '/biblioteca/cenarios/estudio.js';
import { createNico } from '/biblioteca/personagens/nico/index.js';
import { GALLERY, POSES } from '/biblioteca/movimentos/poses.js';
import { frame } from '/biblioteca/camera/presets.js';
import { auditPose } from '/biblioteca/personagens/nico/checagem.js';

export const VISTAS = [
  { nome: 'frente', azimute: 0 },
  { nome: 'perfil', azimute: 90 },
  { nome: 'tres-quartos', azimute: 35 },
];
export const DURACAO = GALLERY.length * VISTAS.length;

let ctx;
let nico;

export function build(c) {
  ctx = c;
  createStudio(ctx.scene);
  nico = createNico();
  ctx.scene.add(nico.group);
}

export function painel(t) {
  const i = Math.floor(t);
  const pose = GALLERY[Math.floor(i / 3) % GALLERY.length];
  const vista = VISTAS[i % 3];
  return { pose, rotulo: POSES[pose].label, vista: vista.nome, azimute: vista.azimute };
}

export function renderFrame(t) {
  const p = painel(t);
  nico.group.position.set(0, 0, 0);
  nico.group.rotation.set(0, 0, 0);
  nico.setPose(p.pose, 0.6 + (t % 1));
  frame(ctx.camera, 'medio', [0, 0.62, 0], { azimute: p.azimute, alturaVisivelM: 1.55 });
}

export function auditar(t) {
  renderFrame(t);
  return { ...painel(t), ...auditPose(nico), medidas: nico.measure() };
}

