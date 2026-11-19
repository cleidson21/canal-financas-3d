// Catálogo: lista os ativos e mostra cada um ao vivo (turntable, galeria de poses,
// testes de movimento com controle de tempo). As cenas são as mesmas da captura.
import { createContext } from '/biblioteca/nucleo/renderizador.js';
import { ATIVOS } from './registro.js';

const nav = document.getElementById('nav');
const main = document.getElementById('main');
const loops = new Set();
let viewers = [];

function el(tag, attrs = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) k === 'class' ? (e.className = v) : (e[k] = v);
  for (const k of kids) e.append(k);
  return e;
}

// Visualizador de uma cena: canvas + tempo (play/pausa/slider). Estado = renderFrame(t).
async function viewer(container, titulo, cena, { w = 300, h = 533, duracao = 8, params = {}, loop = true, extra } = {}) {
  const canvas = el('canvas', { width: w, height: h });
  canvas.style.width = w + 'px';
  canvas.style.height = h + 'px';
  const slider = el('input', { type: 'range', min: 0, max: duracao, step: 1 / 30, value: 0 });
  const rot = el('span', { class: 'rot' }, '0.00s');
  const btn = el('button', {}, '⏸');
  const card = el('div', { class: 'card' }, el('h3', {}, titulo), canvas, el('div', { class: 'ctl' }, btn, slider, rot));
  if (extra) card.querySelector('.ctl').append(extra);
  container.append(card);
  const ctx = createContext({ canvas, width: w, height: h, params });
  const mod = await import(/* @vite-ignore */ cena);
  await mod.build(ctx);
  let t = 0;
  let playing = true;
  let last = performance.now();
  const draw = () => {
    mod.renderFrame(t);
    ctx.renderer.render(ctx.scene, ctx.camera);
    slider.value = t;
    rot.textContent = t.toFixed(2) + 's';
  };
  btn.onclick = () => {
    playing = !playing;
    btn.textContent = playing ? '⏸' : '▶';
  };
  slider.oninput = () => {
    t = Number(slider.value);
    playing = false;
    btn.textContent = '▶';
    draw();
  };
  const tick = (now) => {
    if (playing) {
      t += (now - last) / 1000; // relógio só para tocar a prévia; a cena continua função de t
      if (t > duracao) t = loop ? 0 : duracao;
      draw();
    }
    last = now;
  };
  loops.add(tick);
  draw();
  const v = { ctx, mod, tick, dispose: () => { loops.delete(tick); ctx.renderer.dispose(); ctx.renderer.forceContextLoss(); } };
  viewers.push(v);
  return v;
}

// Galeria: um canvas, uma célula por painel (12 poses × 3 vistas) com scissor.
async function galeria(container, cena) {
  const cols = 9;
  const n = 36;
  const cw = 132;
  const ch = Math.round((cw * 16) / 9);
  const rows = Math.ceil(n / cols);
  const canvas = el('canvas', { width: cols * cw, height: rows * ch });
  canvas.style.width = cols * cw + 'px';
  const legenda = el('div', { class: 'meta' });
  container.append(el('div', { class: 'card' }, el('h3', {}, 'Galeria de poses — 12 poses × 3 vistas (frente, perfil, três-quartos)'), canvas, legenda));
  const ctx = createContext({ canvas, width: cols * cw, height: rows * ch });
  const mod = await import(/* @vite-ignore */ cena);
  await mod.build(ctx);
  ctx.camera.aspect = cw / ch;
  ctx.camera.updateProjectionMatrix();
  const r = ctx.renderer;
  r.setScissorTest(true);
  const nomes = [];
  for (let i = 0; i < n; i++) {
    const x = (i % cols) * cw;
    const y = (rows - 1 - Math.floor(i / cols)) * ch;
    mod.renderFrame(i);
    ctx.camera.aspect = cw / ch;
    ctx.camera.updateProjectionMatrix();
    r.setViewport(x, y, cw, ch);
    r.setScissor(x, y, cw, ch);
    r.render(ctx.scene, ctx.camera);
    if (i % 3 === 0) nomes.push(mod.painel(i).rotulo);
  }
  r.setScissorTest(false);
  legenda.textContent = 'Ordem (3 vistas cada): ' + nomes.join(' · ');
}

async function mostrar(id) {
  for (const v of viewers) v.dispose();
  viewers = [];
  main.innerHTML = '';
  for (const a of nav.querySelectorAll('a')) a.classList.toggle('on', a.dataset.id === id);
  const at = ATIVOS.find((a) => a.id === id) || ATIVOS[0];
  main.append(el('h2', { class: 't' }, at.nome), el('div', { class: 'meta' }, `${at.grupo} · ${at.arquivo} · ${at.estado}`));
  const linha = el('div', { class: 'linha' });
  main.append(linha);
  if (at.turntable) {
    const sel = el('select');
    for (const p of ['idle', 'surprise', 'cheer', 'tired', 'point', 'shrug', 'refuse', 'carry', 'offer', 'receive', 'walk', 'run']) sel.append(el('option', { value: p }, p));
    const v = await viewer(linha, 'Turntable 360° (8 s)', at.turntable, { duracao: 8, extra: sel });
    sel.onchange = () => (v.ctx.params.pose = sel.value);
  }
  for (const t of at.testes || []) await viewer(linha, t.nome, t.cena, { duracao: t.duracao, params: t.params || {} });
  if (at.galeria) {
    const g = el('div', { class: 'linha' });
    g.style.marginTop = '18px';
    main.append(g);
    await galeria(g, at.galeria);
  }
  if (at.folhas) {
    const f = el('div', { class: 'card folhas' }, el('h3', {}, 'Folhas de contato (geradas por: npm run auditoria:nico)'));
    f.style.marginTop = '18px';
    for (const nome of at.folhas) {
      const img = el('img', { src: `/catalogo/folhas/${nome}?v=${Date.now()}`, loading: 'lazy' });
      const d = el('details', {}, el('summary', {}, nome), img);
      img.onerror = () => (d.querySelector('summary').textContent = `${nome} (ainda não gerada)`);
      f.append(d);
    }
    main.append(f);
  }
}

let grupo = null;
for (const a of ATIVOS) {
  if (a.grupo !== grupo) {
    grupo = a.grupo;
    nav.append(el('h2', {}, grupo));
  }
  const link = el('a', { href: '#' + a.id }, a.nome, el('small', {}, a.estado));
  link.dataset.id = a.id;
  nav.append(link);
}
const frame = (now) => {
  for (const f of loops) f(now);
  requestAnimationFrame(frame);
};
requestAnimationFrame(frame);
window.addEventListener('hashchange', () => mostrar(location.hash.slice(1)));
await mostrar(location.hash.slice(1) || 'nico');
window.catalogoPronto = true;
