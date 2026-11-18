// Infra comum das ferramentas Node: servidor Vite + Chromium (Playwright) headless.
import { createServer } from 'vite';
import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

export const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// Modos de WebGL headless testados nesta máquina:
//  gpu      → Chromium completo em headless novo, ANGLE/D3D11 na GPU
//  software → SwiftShader (CPU), para máquinas sem GPU
const MODOS = {
  gpu: { channel: 'chromium', args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist'] },
  software: { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] },
};

export async function abrirEstudio({ modo = 'gpu' } = {}) {
  const server = await createServer({
    root: RAIZ,
    configFile: path.join(RAIZ, 'vite.config.js'),
    logLevel: 'error',
    clearScreen: false,
    server: { port: 5199, strictPort: false, open: false },
  });
  await server.listen();
  const url = server.resolvedUrls.local[0].replace(/\/$/, '');
  const cfg = MODOS[modo];
  if (!cfg) throw new Error(`modo desconhecido: ${modo}`);
  const browser = await chromium.launch({ headless: true, ...cfg });
  const fechar = async () => {
    await browser.close();
    await server.close();
  };
  return { url, browser, fechar };
}

// Abre a página de captura de uma cena e espera estar pronta.
export async function abrirCena(estudio, cena, { w = 1080, h = 1920, params = {} } = {}) {
  const page = await estudio.browser.newPage({ viewport: { width: w, height: h } });
  const erros = [];
  page.on('pageerror', (e) => erros.push(String(e)));
  page.on('console', (m) => m.type() === 'error' && erros.push(m.text()));
  const qs = new URLSearchParams({ cena: '/' + cena.replace(/\\/g, '/').replace(/^\//, ''), w, h, ...params });
  await page.goto(`${estudio.url}/ferramentas/pagina/captura.html?${qs}`);
  try {
    await page.waitForFunction(() => window.estudioPronto === true, null, { timeout: 60000 });
  } catch (e) {
    throw new Error(`cena não carregou: ${cena}\n${erros.join('\n')}`);
  }
  return page;
}

export function salvarDataUrl(dataUrl, arquivo) {
  fs.mkdirSync(path.dirname(arquivo), { recursive: true });
  fs.writeFileSync(arquivo, Buffer.from(dataUrl.split(',')[1], 'base64'));
}

// Lista de instantes: "0,1.5,3" ou "0:4:0.1" (início:fim:passo, fim incluso).
export function parseTempos(spec) {
  if (spec.includes(':')) {
    const [a, b, s] = spec.split(':').map(Number);
    const n = Math.round((b - a) / s);
    return Array.from({ length: n + 1 }, (_, i) => +(a + i * s).toFixed(4));
  }
  return spec.split(',').map(Number);
}

export function parseArgs(argv) {
  const out = { params: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) continue;
    const k = a.slice(2);
    const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    if (k === 'param') {
      const [pk, pv] = String(v).split('=');
      out.params[pk] = pv;
    } else out[k] = v;
  }
  return out;
}

