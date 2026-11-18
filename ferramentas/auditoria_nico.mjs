// Auditoria do Nico (NICO_SPEC §7). Gera folhas de contato em catalogo/folhas/ e
// imprime falhas no terminal (sem relatório em arquivo).
//   node ferramentas/auditoria_nico.mjs [--modo gpu|software] [--so galeria,caminhada,encaixe,cores,catalogo]
import path from 'node:path';
import { abrirEstudio, abrirCena, parseArgs, parseTempos, salvarDataUrl, RAIZ } from './estudio.mjs';
import { capturar } from './captura.mjs';
import { montarFolha } from './folha.mjs';

const a = parseArgs(process.argv.slice(2));
const so = a.so ? String(a.so).split(',') : ['galeria', 'caminhada', 'encaixe', 'cores', 'catalogo'];
const FOLHAS = path.join(RAIZ, 'catalogo/folhas');
const falhas = [];
const log = (...x) => console.log(...x);
const t0 = Date.now();
const est = await abrirEstudio({ modo: a.modo || 'gpu' });

try {
  // 1+2. Galeria 12×3 e limites/interpenetração nas poses
  if (so.includes('galeria')) {
    const tempos = parseTempos('0:35:1');
    const r = await capturar(est, { cena: 'catalogo/cenas/nico_galeria.js', tempos, w: 360, h: 640, saida: path.join(FOLHAS, 'galeria'), prefixo: 'g' });
    const page = await abrirCena(est, 'catalogo/cenas/nico_galeria.js', { w: 64, h: 64 });
    for (const it of r.arquivos) {
      const p = await page.evaluate((t) => window.estudio.chamar('painel', t), it.t);
      it.rotulo = `${p.rotulo.slice(0, 18)} · ${p.vista}`;
    }
    await montarFolha(est.browser, r.arquivos, path.join(FOLHAS, '1_galeria_poses.png'), { colunas: 9, larguraCelula: 240, titulo: 'Critério 1 — 12 poses × 3 vistas' });
    log(`[1] galeria: ${r.arquivos.length} quadros, ${r.msPorQuadro.toFixed(0)} ms/quadro → catalogo/folhas/1_galeria_poses.png`);
    for (let i = 0; i < 12; i++) {
      const res = await page.evaluate((t) => window.estudio.chamar('auditar', t), i * 3);
      for (const l of res.limites) falhas.push(`[2] pose ${res.rotulo} (t=${i * 3}): limite ${l}`);
      for (const c of res.colisoes) falhas.push(`[2] pose ${res.rotulo} (t=${i * 3}): ${c.a} atravessa ${c.b} em ${(c.penetracao * 1000).toFixed(1)} mm`);
    }
    await page.close();
  }

  // 3. Caminhada de 4 s: quadros a cada 0,1 s + deslize medido a 240 Hz
  if (so.includes('caminhada')) {
    const tempos = parseTempos('0.3:4.3:0.1');
    const r = await capturar(est, { cena: 'catalogo/cenas/nico_caminhada.js', tempos, w: 360, h: 640, saida: path.join(FOLHAS, 'caminhada'), prefixo: 'c' });
    await montarFolha(est.browser, r.arquivos, path.join(FOLHAS, '3_caminhada.png'), { colunas: 9, larguraCelula: 220, titulo: 'Critério 3 — caminhada 4 s, quadros a cada 0,1 s' });
    const page = await abrirCena(est, 'catalogo/cenas/nico_caminhada.js', { w: 64, h: 64 });
    const d = await page.evaluate(() => window.estudio.chamar('deslize'));
    await page.close();
    log(`[3] caminhada: deslize máx. pé E ${(d.deslize.L.max * 1000).toFixed(2)} mm (t=${d.deslize.L.quando}), pé D ${(d.deslize.R.max * 1000).toFixed(2)} mm (t=${d.deslize.R.quando}) → catalogo/folhas/3_caminhada.png`);
    for (const s of ['L', 'R'])
      if (d.deslize[s].max > 0.002) falhas.push(`[3] pé ${s} desliza ${(d.deslize[s].max * 1000).toFixed(1)} mm apoiado (até t=${d.deslize[s].quando}s, ${d.deslize[s].ponto})`);
    for (const l of d.limites) falhas.push(`[3] t=${l.t}: limite ${l.lim.join('; ')}`);
    if (d.nLimites > d.limites.length) falhas.push(`[3] … mais ${d.nLimites - d.limites.length} amostras com limite violado`);
    for (const c of d.colisoes) falhas.push(`[3] t=${c.t}: ${c.c.map((x) => `${x.a}×${x.b} ${(x.penetracao * 1000).toFixed(1)}mm`).join('; ')}`);
    if (d.nColisoes > d.colisoes.length) falhas.push(`[3] … mais ${d.nColisoes - d.colisoes.length} amostras com interpenetração`);
  }

  // 4. Encaixe: pegar saco, caminhar 3 s, soltar
  if (so.includes('encaixe')) {
    const tempos = parseTempos('0:7.6:0.2');
    const r = await capturar(est, { cena: 'catalogo/cenas/nico_encaixe.js', tempos, w: 360, h: 640, saida: path.join(FOLHAS, 'encaixe'), prefixo: 'e' });
    await montarFolha(est.browser, r.arquivos, path.join(FOLHAS, '4_encaixe.png'), { colunas: 9, larguraCelula: 220, titulo: 'Critério 4 — pegar saco, caminhar 3 s, soltar' });
    const page = await abrirCena(est, 'catalogo/cenas/nico_encaixe.js', { w: 64, h: 64 });
    const res = await page.evaluate(() => {
      const out = [];
      for (let i = 0; i <= 7.6 * 30; i++) out.push({ t: i / 30, ...window.estudio.chamar('auditar', i / 30) });
      return out;
    });
    await page.close();
    let maxContato = 0;
    const porTipo = {};
    const reg = (k, msg) => ((porTipo[k] ||= []).push(msg));
    for (const q of res) {
      const tt = q.t.toFixed(2);
      for (const l of q.limites) reg('limite ' + l.split('=')[0], `t=${tt} ${l}`);
      for (const c of q.colisoes) reg(`${c.a}×${c.b}`, `t=${tt} ${(c.penetracao * 1000).toFixed(1)}mm`);
      if (q.segurando) {
        maxContato = Math.max(maxContato, q.contatoBracos);
        if (q.contatoBracos > 0.012) reg('saco solto dos braços', `t=${tt} folga ${(q.contatoBracos * 1000).toFixed(1)}mm`);
      } else if (Math.abs(q.folgaApoio) > 0.002) reg('saco fora do apoio', `t=${tt} folga ${(q.folgaApoio * 1000).toFixed(1)}mm`);
    }
    log(`[4] encaixe: caixotes derivados da pose com altura ${res[0].alturaCaixotes.map((x) => x.toFixed(3)).join(' / ')} m; folga máx. saco↔braços ${(maxContato * 1000).toFixed(1)} mm → catalogo/folhas/4_encaixe.png`);
    for (const [k, v] of Object.entries(porTipo)) falhas.push(`[4] ${k}: ${v.length} quadros (${v[0]}${v.length > 1 ? ' … ' + v[v.length - 1] : ''})`);
  }

  // 5. Cores contra tokens.json em todas as cenas (passe de albedo sem luz)
  if (so.includes('cores')) {
    const casos = [
      ['catalogo/cenas/nico_galeria.js', parseTempos('0:35:1')],
      ['catalogo/cenas/nico_caminhada.js', parseTempos('0:4.5:0.5')],
      ['catalogo/cenas/nico_encaixe.js', parseTempos('0:7.5:0.5')],
      ['catalogo/cenas/nico_turntable.js', parseTempos('0:7:1')],
    ];
    let quadros = 0;
    const tenisVisto = new Set();
    for (const [cena, tempos] of casos) {
      const page = await abrirCena(est, cena, { w: 360, h: 640 });
      for (const t of tempos) {
        const r = await page.evaluate((t) => window.estudio.passeCor(t), t);
        quadros++;
        for (const d of r.declaradasErradas) falhas.push(`[5] ${cena} t=${t}: malha ${d.malha} com cor ≠ ${d.token}`);
        for (const [tok, s] of Object.entries(r.stats)) if (s.diferentes) falhas.push(`[5] ${cena} t=${t}: ${tok} ${s.diferentes}/${s.pixels} px fora do token (erro máx ${s.maxErro})`);
        if (r.stats['cores.nico.tenis']?.pixels) tenisVisto.add(cena);
      }
      await page.close();
    }
    log(`[5] cores: ${quadros} quadros em ${casos.length} cenas comparados pixel a pixel com tokens.json; tênis visível em ${tenisVisto.size}/${casos.length} cenas`);
  }

  // 6. Página do catálogo com turntable
  if (so.includes('catalogo')) {
    const page = await est.browser.newPage({ viewport: { width: 1400, height: 900 } });
    const erros = [];
    page.on('pageerror', (e) => erros.push(String(e)));
    await page.goto(`${est.url}/catalogo/#nico`);
    await page.waitForFunction(() => window.catalogoPronto === true, null, { timeout: 60000 });
    await page.waitForTimeout(1500);
    salvarDataUrl('data:image/png;base64,' + (await page.screenshot()).toString('base64'), path.join(FOLHAS, '6_catalogo.png'));
    await page.close();
    for (const e of erros) falhas.push(`[6] erro na página do catálogo: ${e}`);
    log('[6] catálogo: captura da página → catalogo/folhas/6_catalogo.png');
  }
} finally {
  await est.fechar();
}

log(`\nFALHAS (${falhas.length}):`);
for (const f of falhas) log(' - ' + f);
log(`tempo total: ${((Date.now() - t0) / 1000).toFixed(1)} s`);
