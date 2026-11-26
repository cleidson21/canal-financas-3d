// Medidas da carga (terminal, sem arquivo): joelhos, tronco, cotovelos, queda da pelve,
// distância cabeça–carga, pilha–costas, balanço da torre, cubo e ícone do rebobinar.
//   node ferramentas/medir_carga.mjs
import { abrirEstudio, abrirCena } from './estudio.mjs';

const est = await abrirEstudio();
const f = (v, d = 1) => (typeof v === 'number' ? v.toFixed(d) : String(v));
try {
  for (const [painel, tmax] of [['exausto', 5.2], ['cambalear', 4.2]]) {
    const page = await abrirCena(est, 'catalogo/cenas/pecas_nico_torre.js', { w: 64, h: 64, params: { painel } });
    const r = await page.evaluate((tmax) => {
      const a = [];
      for (let t = 0; t <= tmax + 1e-9; t += 0.05) a.push(window.estudio.chamar('medir', t));
      return a;
    }, tmax);
    console.log(`\n== ${painel} (${r.length} amostras)`);
    for (const k of ['joelhoL', 'joelhoR', 'tronco', 'cotoveloL', 'pelveDropCm', 'cabecaMm', 'pilhaCostasCm', 'torreLat', 'torreFrente']) {
      const rr = r.filter((x) => x.t >= 1.0); // regime (sem a transição a partir do parado)
      const v = rr.map((x) => x[k]);
      const min = Math.min(...v);
      const max = Math.max(...v);
      console.log(`  ${k.padEnd(14)} min ${f(min)} (t=${f(rr[v.indexOf(min)].t, 2)})  max ${f(max)} (t=${f(rr[v.indexOf(max)].t, 2)})`);
    }
    const pior = r.filter((x) => x.t >= 1.0).reduce((a, b) => (b.cabecaMm < a.cabecaMm ? b : a));
    console.log(`  cabeça–carga mínima: ${f(pior.cabecaMm)} mm com "${pior.cabecaItem}" em t=${f(pior.t, 2)}`);
    const col = await page.evaluate((tmax) => {
      const out = {};
      for (let t = 0; t <= tmax + 1e-9; t += 0.1) {
        const a = window.estudio.chamar('auditar', t);
        for (const l of a.limites) (out['LIMITE ' + l.split('=')[0]] ||= []).push(t.toFixed(1));
        for (const c of a.colisoes) (out[c.a + '×' + c.b] ||= []).push(`${t.toFixed(1)}:${(c.penetracao * 1000).toFixed(1)}mm`);
      }
      return out;
    }, tmax);
    for (const [k, v] of Object.entries(col)) console.log(`  ! ${k}: ${v.length} amostras (${v[0]} … ${v[v.length - 1]})`);
    if (!Object.keys(col).length) console.log('  sem limites violados nem interpenetração (amostras a 0,1 s)');
    await page.close();
  }
  {
    const page = await abrirCena(est, 'catalogo/cenas/pecas_cubo.js', { w: 360, h: 640 });
    const m = await page.evaluate(() => window.estudio.chamar('marcos'));
    const r = await page.evaluate((fim) => {
      const a = [];
      for (let i = 0; i <= Math.ceil(fim * 30) + 2; i++) a.push(window.estudio.chamar('medirCubo', i / 30));
      return a;
    }, m.tAparece);
    const vis = r.filter((x) => x.visivel);
    const sy = vis.map((x) => x.sy);
    const sx = vis.map((x) => x.sx);
    console.log(`\n== cubo: sy ${f(Math.min(...sy), 3)}–${f(Math.max(...sy), 3)}, sxz ${f(Math.min(...sx), 3)}–${f(Math.max(...sx), 3)} (inclui o pop final)`);
    const tPop = m.pop - 0.1;
    const pre = vis.filter((x) => x.t < tPop);
    console.log(`   sem o pop final: sy ${f(Math.min(...pre.map((x) => x.sy)), 3)}–${f(Math.max(...pre.map((x) => x.sy)), 3)}, sxz máx ${f(Math.max(...pre.map((x) => x.sx)), 3)}`);
    const sq = r.filter((x) => x.visivel && x.t < tPop && x.sy < 0.999).map((x) => x.t.toFixed(2));
    console.log(`   quadros com squash (sy<1): ${sq.length} → ${sq.join(' ')} | impactos em ${m.impactos.map((x) => x.toFixed(2)).join(' ')}`);
    await page.close();
  }
  {
    const page = await abrirCena(est, 'catalogo/cenas/pecas_rebobinar.js', { w: 360, h: 640 });
    const rs = [];
    for (const t of [1.95, 2.3, 2.6]) rs.push(await page.evaluate((t) => window.estudio.chamar('medirIcone', t), t));
    console.log('\n== rebobinar ícone:', rs.map((x) => `t=${x.t}: ${f(x.larguraFrac * 100)}% da largura, centro a ${f(x.yFracTopo * 100)}% do topo`).join(' | '));
    await page.close();
  }
} finally {
  await est.fechar();
}
