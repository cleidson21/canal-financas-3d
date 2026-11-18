// Folha de contato: junta PNGs numa grade com rótulos. Desenha num canvas do Chromium.
//   node ferramentas/folha.mjs --pasta catalogo/folhas/x --saida catalogo/folhas/x.png --colunas 6
import fs from 'node:fs';
import path from 'node:path';
import { abrirEstudio, parseArgs, salvarDataUrl, RAIZ } from './estudio.mjs';

// itens: [{ arquivo, rotulo }]
export async function montarFolha(browser, itens, saida, { colunas = 6, larguraCelula = 270, titulo = '' } = {}) {
  const page = await browser.newPage();
  const imagens = itens.map((it) => ({
    src: 'data:image/png;base64,' + fs.readFileSync(it.arquivo).toString('base64'),
    rotulo: it.rotulo ?? path.basename(it.arquivo, '.png'),
  }));
  const dataUrl = await page.evaluate(
    async ({ imagens, colunas, larguraCelula, titulo }) => {
      const bitmaps = await Promise.all(
        imagens.map(async (im) => createImageBitmap(await (await fetch(im.src)).blob())),
      );
      const ar = bitmaps[0].height / bitmaps[0].width;
      const cw = larguraCelula;
      const ch = Math.round(cw * ar);
      const rot = 22;
      const topo = titulo ? 34 : 0;
      const linhas = Math.ceil(bitmaps.length / colunas);
      const c = document.createElement('canvas');
      c.width = colunas * cw;
      c.height = topo + linhas * (ch + rot);
      const g = c.getContext('2d');
      g.fillStyle = '#1b1b1f';
      g.fillRect(0, 0, c.width, c.height);
      if (titulo) {
        g.fillStyle = '#fff';
        g.font = 'bold 20px sans-serif';
        g.fillText(titulo, 8, 24);
      }
      bitmaps.forEach((b, i) => {
        const x = (i % colunas) * cw;
        const y = topo + Math.floor(i / colunas) * (ch + rot);
        g.drawImage(b, x, y + rot, cw, ch);
        g.strokeStyle = '#000';
        g.strokeRect(x + 0.5, y + rot + 0.5, cw - 1, ch - 1);
        g.fillStyle = '#e8e8e8';
        g.font = '14px monospace';
        g.fillText(imagens[i].rotulo, x + 4, y + 16);
      });
      return c.toDataURL('image/png');
    },
    { imagens, colunas, larguraCelula, titulo },
  );
  await page.close();
  salvarDataUrl(dataUrl, saida);
  return saida;
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(RAIZ, 'ferramentas/folha.mjs')) {
  const a = parseArgs(process.argv.slice(2));
  if (!a.pasta || !a.saida) {
    console.log('uso: node ferramentas/folha.mjs --pasta <dir com PNGs> --saida <arquivo.png> [--colunas 6] [--titulo txt]');
    process.exit(1);
  }
  const arquivos = fs
    .readdirSync(a.pasta)
    .filter((f) => f.endsWith('.png'))
    .sort()
    .map((f) => ({ arquivo: path.join(a.pasta, f) }));
  const est = await abrirEstudio({ modo: a.modo || 'gpu' });
  await montarFolha(est.browser, arquivos, a.saida, { colunas: Number(a.colunas) || 6, titulo: a.titulo || '' });
  await est.fechar();
  console.log('folha:', a.saida);
}

