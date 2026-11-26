// HUD "DIA n" no canto superior direito, dentro da área segura (tokens.hud.seguro).
// Preso à câmera (filho dela): acompanha qualquer enquadramento. A cada troca de dia o
// número faz pop (escala 0 → 1 com overshoot) e o selo dá um pulso curto.
// Estado = função pura de t: o calendário é uma lista [{ t, dia, de? }].
// de (opcional, [x,y,z] de mundo ou função de t): o selo NASCE na posição de tela desse ponto
// (ex.: onde o cubo PLOC! sumiu) e desliza até o canto em hud.deslizeS (≈0,3 s).
//   const hud = createDiaCounter(ctx, [{ t: -99, dia: 3 }, { t: 3.2, dia: 1 }]);
//   hud.update(t);   // a cada quadro, depois de posicionar a câmera
import * as THREE from 'three';
import { token } from '../nucleo/materiais.js';
import { clamp, lerp, ease } from '../nucleo/matematica.js';

// 0 → 1 com overshoot (pico ≈ 1.17), k em [0,1]
export function popScale(k, overshoot = 2.6) {
  if (k <= 0) return 0;
  if (k >= 1) return 1;
  const c3 = overshoot + 1;
  return 1 + c3 * Math.pow(k - 1, 3) + overshoot * Math.pow(k - 1, 2);
}

function roundRect(g, x, y, w, h, r) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

function textura(canvas) {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

export function createDiaCounter(ctx, calendario, opts = {}) {
  const { camera, scene } = ctx;
  if (!camera.parent) scene.add(camera);
  const hud = token('hud');
  const grupo = new THREE.Group();
  grupo.name = 'hud_dia';
  grupo.position.z = -1; // 1 m à frente da câmera
  camera.add(grupo);

  const mat = (map) =>
    new THREE.MeshBasicMaterial({ map, transparent: true, depthTest: false, depthWrite: false, toneMapped: false, fog: false });

  // selo: cápsula escura com borda de acento e a palavra DIA
  const W = 512;
  const Hh = 192;
  const c = document.createElement('canvas');
  c.width = W;
  c.height = Hh;
  const g = c.getContext('2d');
  roundRect(g, 6, 6, W - 12, Hh - 12, 70);
  g.fillStyle = hud.fundo;
  g.globalAlpha = 0.9;
  g.fill();
  g.globalAlpha = 1;
  g.lineWidth = 10;
  g.strokeStyle = hud.acento;
  g.stroke();
  g.fillStyle = hud.texto;
  g.font = '800 92px "Arial Black", Arial, sans-serif';
  g.textAlign = 'left';
  g.textBaseline = 'middle';
  g.fillText('DIA', 48, Hh / 2 + 6);
  const selo = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat(textura(c)));
  selo.renderOrder = 1000;
  grupo.add(selo);

  const numeros = new Map();
  const texNumero = (txt) => {
    if (!numeros.has(txt)) {
      const cv = document.createElement('canvas');
      cv.width = 256;
      cv.height = 256;
      const x = cv.getContext('2d');
      x.fillStyle = hud.acento;
      x.font = '900 190px "Arial Black", Arial, sans-serif';
      x.textAlign = 'center';
      x.textBaseline = 'middle';
      x.fillText(txt, 128, 134);
      numeros.set(txt, textura(cv));
    }
    return numeros.get(txt);
  };
  const numMat = mat(texNumero(String(calendario[0].dia)));
  const numero = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), numMat);
  numero.renderOrder = 1001;
  grupo.add(numero);

  const lista = [...calendario].sort((a, b) => a.t - b.t);
  const popS = opts.popS ?? hud.popS;
  const deslizeS = opts.deslizeS ?? hud.deslizeS;

  function layout() {
    const meioAlto = Math.tan((camera.fov * Math.PI) / 360); // z = 1
    const meioLarg = meioAlto * camera.aspect;
    const hb = 2 * meioAlto * hud.contadorAltura;
    const wb = hb * (W / Hh);
    const cx = meioLarg - hud.seguro.direita * 2 * meioLarg - wb / 2;
    const cy = meioAlto - hud.seguro.topo * 2 * meioAlto - hb / 2;
    return { hb, wb, cx, cy };
  }

  function update(t) {
    let e = null;
    for (const it of lista) if (it.t <= t) e = it;
    grupo.visible = !!e;
    if (!e) return;
    const tau = t - e.t;
    const k = clamp(tau / popS, 0, 1);
    const L = layout();
    let cx = L.cx;
    let cy = L.cy;
    let sb = 1;
    if (e.de) {
      // nasce na posição de tela do ponto `de` e desliza até o canto
      const p = typeof e.de === 'function' ? e.de(t) : e.de;
      camera.updateMatrixWorld(true);
      const pc = camera.worldToLocal(new THREE.Vector3(p[0], p[1], p[2]));
      const x1 = pc.x / -pc.z;
      const y1 = pc.y / -pc.z;
      const u = ease.inOutCubic(clamp(tau / deslizeS, 0, 1));
      cx = lerp(x1, L.cx, u);
      cy = lerp(y1, L.cy, u);
      sb = popScale(clamp(tau / (deslizeS * 0.8), 0, 1));
    }
    const pulso = 1 + 0.07 * Math.sin(Math.PI * k) * (e.t > -50 ? 1 : 0);
    selo.scale.set(L.wb * pulso * sb, L.hb * pulso * sb, 1);
    selo.position.set(cx, cy, 0);
    numMat.map = texNumero(String(e.valor ?? e.dia));
    const s = popScale(e.t > -50 ? k : 1);
    const nh = L.hb * 0.92;
    numero.scale.set(nh * s * sb, nh * s * sb, 1);
    numero.position.set(cx + L.wb * 0.2 * sb, cy - L.hb * 0.005 * sb, 0);
  }  update(-1e9);
  return { group: grupo, update, layout };
}
