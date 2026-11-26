// Poses de carga do Nico (cargueiro + torre) em 3 painéis (?painel=exausto|cambalear|quebrado)
// e ângulo de câmera livre (?az=graus) / quantidade de itens (?qtd=n).
//  exausto   : descalço, `exausto_com_carga`, torre com 6 itens, DIA 3
//  cambalear : descalço, `cambalear` (andar lento com carga), torre com 2 itens
//  quebrado  : `sapatoQuebrado` andando, torre com 1 item (a ponta da sola pende)
import { montar } from './_ep001_comum.js';
import { frame } from '/biblioteca/camera/presets.js';
import { createDiaCounter } from '/biblioteca/efeitos/contador_dia.js';
import { auditPose } from '/biblioteca/personagens/nico/checagem.js';

const PAINEIS = {
  exausto: { opts: { descalco: true, quantidade: 6, altura: 1.45 }, az: 70 },
  cambalear: { opts: { descalco: true, quantidade: 2, altura: 0.5 }, az: 0 },
  quebrado: { opts: { descalco: false, sapatoQuebrado: true, quantidade: 1, altura: 0.35 }, az: 14 },
};
export const DURACAO = 5;

let ctx, M, hud, mov, nome, cfg;

export function build(c) {
  ctx = c;
  nome = ctx.params.painel || 'exausto';
  cfg = PAINEIS[nome];
  const opts = { ...cfg.opts };
  if (ctx.params.qtd) opts.quantidade = Number(ctx.params.qtd);
  M = montar(ctx, opts);
  hud = createDiaCounter(ctx, [{ t: -99, dia: 3 }]);
  const n = M.nico;
  if (nome === 'exausto') mov = n.play('exausto_com_carga', 0);
  else if (nome === 'cambalear') mov = n.play('cambalear', 0, { from: [-0.3, 0], to: [0.3, 0], duration: 4.2, upper: 'carga_costas', neckPitch: 8, expr: 'cansada' });
  else mov = n.play('caminhar', 0, { from: [-0.6, 0], to: [1.1, 0], duration: 3.0, upper: 'carga_costas', expr: 'cansada' });
}

export function renderFrame(t) {
  mov(t);
  M.prender(t);
  M.cen.update(t);
  const x = M.nico.group.position.x;
  M.cen.seguir(x, 0);
  const az = ctx.params.az !== undefined ? Number(ctx.params.az) : cfg.az;
  if (nome === 'quebrado') frame(ctx.camera, 'medio', [x + 0.1, 0.5, 0], { azimute: az, alturaVisivelM: 1.8, inclinacaoGraus: 3 });
  else M.enquadrar(az, x);
  hud.update(t);
}

export function auditar(t) {
  renderFrame(t);
  return auditPose(M.nico, M.auditoria());
}

// métricas da carga no instante t (usadas por ferramentas/medir_carga.mjs)
export function medir(t) {
  renderFrame(t);
  return { t, ...M.medir() };
}
