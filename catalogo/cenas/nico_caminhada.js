// Caminhada de 4 s do Nico (teste de pés fixos). Câmera de perfil acompanhando
// em travelling; a grade de 0,1 m no chão mostra se o pé apoiado desliza.
import { createStudio } from '/biblioteca/cenarios/estudio.js';
import { createNico } from '/biblioteca/personagens/nico/index.js';
import { token } from '/biblioteca/nucleo/materiais.js';
import { auditPose, solePoints } from '/biblioteca/personagens/nico/checagem.js';

export const DURACAO = 4.6;
const T0 = 0.3;
const DUR_ANDAR = 4.0;

let ctx, nico, studio, walk;

export function build(c) {
  ctx = c;
  studio = createStudio(ctx.scene, { tamanho: 10 });
  nico = createNico();
  ctx.scene.add(nico.group);
  const cfg = token('locomocao.caminhar');
  const len = cfg.velocidade * (DUR_ANDAR - cfg.aceleracaoS);
  walk = nico.play('caminhar', T0, { from: [-len / 2, 0], to: [len / 2, 0], duration: DUR_ANDAR });
}

export function renderFrame(t) {
  const r = walk(t);
  const x = nico.group.position.x;
  studio.seguir(x, 0);
  const cam = ctx.params.vista === 'frente' ? [x + 2.6, 0.55, 2.6] : [x, 0.5, 3.4];
  ctx.camera.position.set(...cam);
  ctx.camera.lookAt(x, 0.45, 0);
  return r;
}

export function auditar(t) {
  renderFrame(t);
  return auditPose(nico);
}

// Deslize do pé apoiado: amostra a 240 Hz; ponto de contato = calcanhar/ponta com
// altura < 2 mm. Soma o deslocamento horizontal enquanto o ponto segue no chão.
export function deslize(passo = 1 / 240) {
  const out = { L: { max: 0, quando: 0 }, R: { max: 0, quando: 0 } };
  let prev = null;
  const H = 0.002;
  const acum = { L: { heel: 0, toe: 0 }, R: { heel: 0, toe: 0 } };
  const limites = [];
  const colisoes = [];
  for (let t = 0; t <= DURACAO + 1e-9; t += passo) {
    renderFrame(t);
    const sp = solePoints(nico);
    if (prev) {
      for (const s of ['L', 'R'])
        for (const k of ['heel', 'toe']) {
          const a = prev[s][k];
          const b = sp[s][k];
          if (a.y < H && b.y < H) {
            acum[s][k] += Math.hypot(b.x - a.x, b.z - a.z);
            if (acum[s][k] > out[s].max) out[s] = { max: acum[s][k], quando: +t.toFixed(3), ponto: k };
          } else acum[s][k] = 0;
        }
    }
    const lim = nico.checkLimits();
    if (lim.length) limites.push({ t: +t.toFixed(3), lim });
    const a = auditPose(nico);
    if (a.colisoes.length) colisoes.push({ t: +t.toFixed(3), c: a.colisoes });
    prev = { L: { heel: sp.L.heel.clone(), toe: sp.L.toe.clone() }, R: { heel: sp.R.heel.clone(), toe: sp.R.toe.clone() } };
  }
  return { deslize: out, limites: limites.slice(0, 5), nLimites: limites.length, colisoes: colisoes.slice(0, 5), nColisoes: colisoes.length };
}

