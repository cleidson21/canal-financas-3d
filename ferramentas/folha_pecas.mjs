// Folha de contato da PARADA 1 (peças do EP001): 12 quadros em 360×640.
//   node ferramentas/folha_pecas.mjs [--saida catalogo/folhas/pecas_ep001.png]
import path from 'node:path';
import { abrirEstudio, abrirCena, salvarDataUrl, parseArgs, RAIZ } from './estudio.mjs';
import { montarFolha } from './folha.mjs';

const a = parseArgs(process.argv.slice(2));
const W = 360;
const H = 640;
const saida = a.saida || path.join(RAIZ, 'catalogo/folhas/pecas_ep001.png');
const dir = path.join(RAIZ, 'catalogo/folhas/pecas');
const tNico = a.t ? String(a.t).split(',').map(Number) : [1.4, 2.0, 1.6];
const est = await abrirEstudio({ modo: a.modo || 'gpu' });
const itens = [];
try {
  const quadro = async (cena, params, t, rotulo, id) => {
    const page = await abrirCena(est, cena, { w: W, h: H, params });
    const url = await page.evaluate((t) => window.estudio.quadro(t), t);
    const arq = path.join(dir, `${id}.png`);
    salvarDataUrl(url, arq);
    itens.push({ arquivo: arq, rotulo });
    await page.close();
  };
  const marcos = async (cena) => {
    const page = await abrirCena(est, cena, { w: 64, h: 64 });
    const m = await page.evaluate(() => window.estudio.chamar('marcos'));
    await page.close();
    return m;
  };
  await quadro('catalogo/cenas/pecas_nico_torre.js', { painel: 'exausto' }, tNico[0], `1 exausto+torre 6 t=${tNico[0]}`, '01');
  await quadro('catalogo/cenas/pecas_nico_torre.js', { painel: 'cambalear' }, tNico[1], `2 cambalear+torre 3 t=${tNico[1]}`, '02');
  await quadro('catalogo/cenas/pecas_nico_torre.js', { painel: 'quebrado' }, tNico[2], `3 sola solta+torre 1 t=${tNico[2]}`, '03');
  const r = await marcos('catalogo/cenas/pecas_rebobinar.js');
  await quadro('catalogo/cenas/pecas_rebobinar.js', {}, r.antes, `4 rebobinar: antes ${r.antes.toFixed(2)}`, '04');
  await quadro('catalogo/cenas/pecas_rebobinar.js', {}, r.linhas, `5 linhas ${r.linhas.toFixed(2)}`, '05');
  await quadro('catalogo/cenas/pecas_rebobinar.js', {}, r.icone, `6 icone ${r.icone.toFixed(2)}`, '06');
  await quadro('catalogo/cenas/pecas_rebobinar.js', {}, r.depois, `7 depois: DIA 1 ${r.depois.toFixed(2)}`, '07');
  const c = await marcos('catalogo/cenas/pecas_cubo.js');
  await quadro('catalogo/cenas/pecas_cubo.js', {}, c.queda, `8 cubo cai ${c.queda.toFixed(2)}`, '08');
  await quadro('catalogo/cenas/pecas_cubo.js', {}, c.squash, `9 squash ${c.squash.toFixed(2)}`, '09');
  await quadro('catalogo/cenas/pecas_cubo.js', {}, c.pop, `10 pop some ${c.pop.toFixed(2)}`, '10');
  await quadro('catalogo/cenas/pecas_cubo.js', {}, c.contador, `11 contador ${c.contador.toFixed(2)}`, '11');
  await quadro('catalogo/cenas/pecas_rebobinar.js', {}, r.depois - 0.12, `12 pop do DIA ${(r.depois - 0.12).toFixed(2)}`, '12');
  await montarFolha(est.browser, itens, saida, { colunas: 6, larguraCelula: 300, titulo: 'EP001 — peças (parada 1)' });
  console.log('folha:', saida);
} finally {
  await est.fechar();
}
