// Captura quadros de uma cena (renderFrame(t)) em PNG e, opcionalmente, folha de contato.
//   node ferramentas/captura.mjs --cena catalogo/cenas/nico_caminhada.js --intervalo 0:4:0.1 \
//        --w 360 --h 640 --folha [--colunas 8] [--modo gpu|software] [--param chave=valor]
import path from 'node:path';
import { abrirEstudio, abrirCena, parseArgs, parseTempos, salvarDataUrl, RAIZ } from './estudio.mjs';
import { montarFolha } from './folha.mjs';

export async function capturar(estudio, { cena, tempos, w = 1080, h = 1920, saida, params = {}, prefixo = 'q' }) {
  const page = await abrirCena(estudio, cena, { w, h, params });
  const info = await page.evaluate(() => window.estudio.info());
  const arquivos = [];
  const t0 = Date.now();
  for (const t of tempos) {
    const url = await page.evaluate((t) => window.estudio.quadro(t), t);
    const arq = path.join(saida, `${prefixo}_${t.toFixed(2).padStart(7, '0')}.png`);
    salvarDataUrl(url, arq);
    arquivos.push({ arquivo: arq, rotulo: `t=${t.toFixed(2)}s`, t });
  }
  const msPorQuadro = (Date.now() - t0) / tempos.length;
  await page.close();
  return { arquivos, info, msPorQuadro };
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(RAIZ, 'ferramentas/captura.mjs')) {
  const a = parseArgs(process.argv.slice(2));
  if (!a.cena || !(a.t || a.intervalo)) {
    console.log('uso: node ferramentas/captura.mjs --cena <arquivo.js> (--t 0,1,2 | --intervalo 0:4:0.1) [--w 1080 --h 1920] [--saida dir] [--folha [arq.png]] [--colunas 6] [--modo gpu|software] [--param k=v]');
    process.exit(1);
  }
  const tempos = parseTempos(String(a.t || a.intervalo));
  const nome = path.basename(a.cena, '.js');
  const saida = a.saida || path.join(RAIZ, 'catalogo/folhas', nome);
  const est = await abrirEstudio({ modo: a.modo || 'gpu' });
  const r = await capturar(est, {
    cena: a.cena,
    tempos,
    w: Number(a.w) || 1080,
    h: Number(a.h) || 1920,
    saida,
    params: a.params,
  });
  console.log(`renderer: ${r.info.renderer}`);
  console.log(`${r.arquivos.length} quadros ${r.info.width}x${r.info.height} em ${saida} — ${r.msPorQuadro.toFixed(0)} ms/quadro (render+PNG)`);
  if (a.folha) {
    const arq = typeof a.folha === 'string' ? a.folha : saida + '.png';
    await montarFolha(est.browser, r.arquivos, arq, { colunas: Number(a.colunas) || 6, titulo: `${nome}` });
    console.log('folha:', arq);
  }
  await est.fechar();
}

