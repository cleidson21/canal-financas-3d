// Folha de contato da PARADA 1b (carga, torre, cubo, rebobinar): 8 quadros em 360×640.
//   node ferramentas/folha_pecas.mjs [--saida catalogo/folhas/pecas_ep001.png]
import path from 'node:path';
import { abrirEstudio, abrirCena, salvarDataUrl, parseArgs, RAIZ } from './estudio.mjs';
import { montarFolha } from './folha.mjs';

const a = parseArgs(process.argv.slice(2));
const W = 360;
const H = 640;
const saida = a.saida || path.join(RAIZ, 'catalogo/folhas/pecas_ep001.png');
const dir = path.join(RAIZ, 'catalogo/folhas/pecas');
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
  const N = 'catalogo/cenas/pecas_nico_torre.js';
  const tEx = a.tex ? Number(a.tex) : 1.3;
  const tCa = a.tca ? Number(a.tca) : 2.1;
  await quadro(N, { painel: 'exausto', az: 8 }, tEx, `1 exausto frente (6 itens) t=${tEx}`, '01');
  await quadro(N, { painel: 'exausto', az: 90 }, tEx, `2 exausto PERFIL t=${tEx}`, '02');
  await quadro(N, { painel: 'exausto', az: 42 }, tEx, `3 exausto 3/4 t=${tEx}`, '03');
  await quadro(N, { painel: 'cambalear', az: 0 }, tCa, `4 cambalear perfil (2 itens) t=${tCa}`, '04');
  const r = await marcos('catalogo/cenas/pecas_rebobinar.js');
  await quadro('catalogo/cenas/pecas_rebobinar.js', {}, r.icone, `5 rebobinar icone ${r.icone.toFixed(2)}`, '05');
  const c = await marcos('catalogo/cenas/pecas_cubo.js');
  await quadro('catalogo/cenas/pecas_cubo.js', {}, c.queda, `6 cubo cai ${c.queda.toFixed(2)}`, '06');
  await quadro('catalogo/cenas/pecas_cubo.js', {}, c.squash, `7 squash ${c.squash.toFixed(2)}`, '07');
  await quadro('catalogo/cenas/pecas_cubo.js', {}, c.tAparece + 0.1, `8 contador desliza ${(c.tAparece + 0.1).toFixed(2)}`, '08');
  await montarFolha(est.browser, itens, saida, { colunas: 4, larguraCelula: 360, titulo: 'EP001 — carga e ajustes (parada 1b)' });
  console.log('folha:', saida);
} finally {
  await est.fechar();
}
