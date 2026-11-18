// Página de captura: carrega uma cena (?cena=/caminho.js) e expõe window.estudio
// para a ferramenta Node (Playwright). Estado visual = função pura de t.
import * as THREE from 'three';
import { createContext, glInfo } from '/biblioteca/nucleo/renderizador.js';

const q = new URLSearchParams(location.search);
const width = Number(q.get('w')) || 1080;
const height = Number(q.get('h')) || 1920;
const params = Object.fromEntries(q.entries());

const ctx = createContext({ width, height, params });
document.body.appendChild(ctx.renderer.domElement);

const mod = await import(/* @vite-ignore */ q.get('cena'));
await mod.build(ctx);

function draw(t) {
  mod.renderFrame(t);
  ctx.renderer.render(ctx.scene, ctx.camera);
}

// ---- Passe de cor: compara a cor-base renderizada de cada peça com tokens.json ----
// ID pass (alvo linear, sem MSAA) + passe de albedo (alvo sRGB, sem luz/neblina).
const rtId = new THREE.WebGLRenderTarget(width, height, { samples: 0 });
rtId.texture.colorSpace = THREE.NoColorSpace;
const rtAlb = new THREE.WebGLRenderTarget(width, height, { samples: 0 });
rtAlb.texture.colorSpace = THREE.NoColorSpace;

async function colorPass(t, tokensRaw) {
  draw(t);
  const meshes = [];
  ctx.scene.traverseVisible((o) => {
    if (o.isMesh && o.material && o.material.userData && o.material.userData.token) meshes.push(o);
  });
  const original = meshes.map((m) => m.material);
  const tokenOf = (path) => path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), tokensRaw);
  const paths = [...new Set(original.map((m) => m.userData.token))];
  const bg = ctx.scene.background;
  const fog = ctx.scene.fog;
  ctx.scene.background = new THREE.Color(0, 0, 0);
  ctx.scene.fog = null;
  // ID
  meshes.forEach((m, i) => {
    const id = paths.indexOf(m.material.userData.token) + 1;
    const mat = new THREE.MeshBasicMaterial();
    mat.color.setRGB(id / 255, 0, 0, THREE.LinearSRGBColorSpace);
    m.material = mat;
  });
  ctx.renderer.setRenderTarget(rtId);
  ctx.renderer.render(ctx.scene, ctx.camera);
  const idBuf = new Uint8Array(width * height * 4);
  ctx.renderer.readRenderTargetPixels(rtId, 0, 0, width, height, idBuf);
  // Albedo
  meshes.forEach((m, i) => {
    m.material.dispose();
    m.material = new THREE.MeshBasicMaterial({ color: original[i].color });
  });
  ctx.renderer.setRenderTarget(rtAlb);
  ctx.renderer.render(ctx.scene, ctx.camera);
  const alb = new Uint8Array(width * height * 4);
  ctx.renderer.readRenderTargetPixels(rtAlb, 0, 0, width, height, alb);
  ctx.renderer.setRenderTarget(null);
  meshes.forEach((m, i) => {
    m.material.dispose();
    m.material = original[i];
  });
  ctx.scene.background = bg;
  ctx.scene.fog = fog;

  const stats = {};
  // O alvo de render guarda valores lineares: comparamos com o token convertido para linear
  // (THREE.Color guarda em espaço linear de trabalho).
  const expected = paths.map((p) => new THREE.Color(tokenOf(p)));
  for (let i = 0; i < width * height; i++) {
    const id = idBuf[i * 4];
    if (!id || id > paths.length) continue;
    const p = paths[id - 1];
    const e = expected[id - 1];
    const s = (stats[p] ||= { pixels: 0, diferentes: 0, maxErro: 0 });
    s.pixels++;
    const err = Math.max(
      Math.abs(alb[i * 4] - Math.round(e.r * 255)),
      Math.abs(alb[i * 4 + 1] - Math.round(e.g * 255)),
      Math.abs(alb[i * 4 + 2] - Math.round(e.b * 255)),
    );
    if (err > 2) s.diferentes++;
    s.maxErro = Math.max(s.maxErro, err);
  }
  // Cores declaradas: cor do material x tokens.json bruto (não a cópia em cache do módulo)
  const declaradas = original.map((m, i) => ({
    malha: meshes[i].name,
    token: m.userData.token,
    ok: m.color.getHexString() === new THREE.Color(tokenOf(m.userData.token)).getHexString(),
  }));
  return { stats, declaradasErradas: declaradas.filter((d) => !d.ok) };
}

window.estudio = {
  info: () => ({ renderer: glInfo(ctx.renderer), width, height }),
  quadro(t) {
    draw(t);
    return ctx.renderer.domElement.toDataURL('image/png');
  },
  tempo(t, n = 1) {
    const t0 = performance.now();
    for (let i = 0; i < n; i++) {
      draw(t + i / 30);
      ctx.renderer.getContext().finish();
    }
    return (performance.now() - t0) / n;
  },
  chamar(fn, ...args) {
    if (typeof mod[fn] !== 'function') throw new Error(`cena não exporta ${fn}()`);
    return mod[fn](...args);
  },
  async passeCor(t) {
    const tokensRaw = await (await fetch('/valores/tokens.json', { cache: 'no-store' })).json();
    return colorPass(t, tokensRaw);
  },
};
window.estudioPronto = true;

