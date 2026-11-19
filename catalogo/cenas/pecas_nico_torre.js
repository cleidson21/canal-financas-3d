// Poses novas do Nico + torre nas costas, em 3 painéis (?painel=exausto|cambalear|quebrado).
//  exausto   : descalço, `exausto_com_carga`, torre com 6 itens, DIA 3
//  cambalear : descalço, `cambalear` (andar lento com carga), torre com 3 itens
//  quebrado  : `sapatoQuebrado` andando, torre com 1 item (a ponta da sola pende)
import { montar } from './_ep001_comum.js';
import { frame } from '/biblioteca/camera/presets.js';
import { createDiaCounter } from '/biblioteca/efeitos/contador_dia.js';
import { auditPose } from '/biblioteca/personagens/nico/checagem.js';

const PAINEIS = {
  exausto: { opts: { descalco: true, quantidade: 6, altura: 1.7 }, az: 80, alvo: [0, 0.95, 0], altVis: 3.1 },
  cambalear: { opts: { descalco: true, quantidade: 3, altura: 0.75 }, az: 12, alvo: [-0.1, 0.65, 0], altVis: 2.0 },
  quebrado: { opts: { descalco: false, sapatoQuebrado: true, quantidade: 1, altura: 0.35 }, az: 14, alvo: [0.2, 0.5, 0], altVis: 1.8 },
};
export const DURACAO = 5;

let ctx, M, hud, mov, cfg;

export function build(c) {
  ctx = c;
  const nome = ctx.params.painel || 'exausto';
  cfg = PAINEIS[nome];
  M = montar(ctx, cfg.opts);
  hud = createDiaCounter(ctx, [{ t: -99, dia: 3 }]);
  const n = M.nico;
  if (nome === 'exausto') mov = n.play('exausto_com_carga', 0);
  else if (nome === 'cambalear') mov = n.play('cambalear', 0, { from: [-0.5, 0], to: [0.9, 0], duration: 4.2, upper: 'carga_costas', expr: 'cansada' });
  else mov = n.play('caminhar', 0, { from: [-0.6, 0], to: [1.1, 0], duration: 3.0, upper: 'carga_costas', expr: 'cansada' });
  // a pose de quem anda (não a de quem está parado)
  const x0 = nome === 'exausto' ? 0 : -0.5;
  n.group.position.set(x0, 0, 0);
}

export function renderFrame(t) {
  mov(t);
  M.prender(t);
  M.cen.update(t);
  const x = M.nico.group.position.x;
  M.cen.seguir(x, 0);
  frame(ctx.camera, 'medio', [cfg.alvo[0] + (ctx.params.painel === 'exausto' ? 0 : x), cfg.alvo[1], cfg.alvo[2]], { azimute: cfg.az, alturaVisivelM: cfg.altVis, inclinacaoGraus: 3 });
  hud.update(t);
}

export function auditar(t) {
  renderFrame(t);
  const o = [];
  if (M.torre) for (const it of M.torre.userData.itens) o.push({ obj: it, proxies: it.userData.proxies });
  return auditPose(M.nico, o);
}
