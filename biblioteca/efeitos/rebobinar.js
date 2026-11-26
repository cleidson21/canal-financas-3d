// REBOBINAR: `rebobinar(t0, duracao)` — o tempo da CENA corre ao contrário e aparecem
// linhas de varredura horizontais, um véu escuro e o ícone ◀◀ (dois triângulos).
//   const rw = createRewind(ctx, { t0: 2.0, duracao: 1.2, volta: 0 });
//   const tc = rw.tempoCena(t);   // use tc em renderFrame(tc) da cena
//   rw.update(t);                 // desenha o overlay (função pura de t)
// Antes de t0 a cena segue t; entre t0 e t0+duracao o tempo da cena vai de t0 até `volta`
// (com easing de fita acelerando e freando); depois a cena continua a partir de `volta`.
import * as THREE from 'three';
import { token } from '../nucleo/materiais.js';
import { rng, ease, clamp, smoothstep } from '../nucleo/matematica.js';
import { popScale } from './contador_dia.js';

export function createRewind(ctx, { t0, duracao, volta = 0, linhas = 30, semente = 5 }) {
  const { camera, scene } = ctx;
  if (!camera.parent) scene.add(camera);
  const cor = (p) => new THREE.Color(token(p));
  const grupo = new THREE.Group();
  grupo.name = 'rebobinar';
  grupo.position.z = -1;
  camera.add(grupo);
  const mat = (tok, op = 1) =>
    new THREE.MeshBasicMaterial({ color: cor(tok), transparent: true, opacity: op, depthTest: false, depthWrite: false, toneMapped: false, fog: false });
  const prep = (m, ordem) => {
    m.renderOrder = ordem;
    grupo.add(m);
    return m;
  };

  const veu = prep(new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat('cores.efeitos.rebobinarVeu', 0)), 900);

  const rand = rng(semente);
  const barras = Array.from({ length: linhas }, (_, i) => ({
    fase: i / linhas + (rand() - 0.5) * 0.02,
    alt: 0.0035 + rand() * 0.012,
    vel: 0.9 + rand() * 0.9,
    op: 0.25 + rand() * 0.45,
    mesh: prep(new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat('cores.efeitos.rebobinarLinha', 0)), 910),
  }));
  // duas faixas largas e fracas, como a banda de ruído de uma fita
  const faixas = [0.37, 0.81].map((f, i) => ({ f, vel: 0.35 + 0.2 * i, mesh: prep(new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat('cores.efeitos.rebobinarLinha', 0)), 905) }));

  // ícone ◀◀ : placa circular escura + anel + dois triângulos apontando para a esquerda
  const icone = new THREE.Group();
  icone.name = 'rebobinar_icone';
  const ordemIcone = 920;
  const placa = new THREE.Mesh(new THREE.CircleGeometry(0.095, 40), mat('cores.efeitos.rebobinarVeu', 0));
  const anel = new THREE.Mesh(new THREE.RingGeometry(0.088, 0.097, 40), mat('cores.efeitos.rebobinarIcone', 0));
  const tri = () => {
    const w = 0.055;
    const h = 0.07;
    const s = new THREE.Shape();
    s.moveTo(-w / 2, 0);
    s.lineTo(w / 2, h / 2);
    s.lineTo(w / 2, -h / 2);
    s.closePath();
    return new THREE.Mesh(new THREE.ShapeGeometry(s), mat('cores.efeitos.rebobinarIcone', 0));
  };
  const triA = tri();
  const triB = tri();
  triA.position.x = -0.028;
  triB.position.x = 0.028;
  for (const [m, o] of [[placa, ordemIcone], [anel, ordemIcone + 1], [triA, ordemIcone + 2], [triB, ordemIcone + 2]]) {
    m.renderOrder = o;
    icone.add(m);
  }
  grupo.add(icone);

  function tempoCena(t) {
    if (t <= t0) return t;
    if (t >= t0 + duracao) return volta + (t - t0 - duracao);
    return t0 - (t0 - volta) * ease.inOutCubic((t - t0) / duracao);
  }

  function update(t) {
    const k = (t - t0) / duracao;
    const ativo = k > 0 && k < 1;
    grupo.visible = ativo;
    if (!ativo) return;
    const mh = Math.tan((camera.fov * Math.PI) / 360);
    const mw = mh * camera.aspect;
    const env = smoothstep(0, 0.1, k) * (1 - smoothstep(0.88, 1, k));
    const tau = t - t0;
    veu.scale.set(mw * 2.2, mh * 2.2, 1);
    veu.material.opacity = 0.3 * env;
    for (const b of barras) {
      const u = (((b.fase - b.vel * tau * 0.9) % 1) + 1) % 1; // desce pela tela
      b.mesh.position.set(0, mh - u * 2 * mh, 0);
      b.mesh.scale.set(mw * 2.2, b.alt * 2 * mh, 1);
      // cintilar determinístico por linha
      b.mesh.material.opacity = b.op * env * (0.55 + 0.45 * Math.sin(2 * Math.PI * (7 + b.vel * 3) * tau + b.fase * 40));
    }
    for (const f of faixas) {
      const u = (((f.f - f.vel * tau) % 1) + 1) % 1;
      f.mesh.position.set(0, mh - u * 2 * mh, 0);
      f.mesh.scale.set(mw * 2.2, 0.07 * 2 * mh, 1);
      f.mesh.material.opacity = 0.1 * env;
    }
    // ícone: pop de entrada, flutua e os dois triângulos piscam em sequência (◀ ◀)
    const pop = popScale(clamp(tau / 0.28, 0, 1));
    const sai = 1 - smoothstep(0.86, 1, k);
    const s = 0.31 * pop * sai * (1 + 0.04 * Math.sin(2 * Math.PI * 3 * tau));
    icone.scale.set(s, s, 1);
    icone.position.set(0, mh - 0.25 * 2 * mh, 0); // 25% abaixo do topo: terço superior, sob o contador
    placa.material.opacity = 0.78;
    anel.material.opacity = 1;
    const ciclo = (tau * 3.2) % 1;
    triA.material.opacity = 0.45 + 0.55 * (ciclo < 0.5 ? 1 : 0.2);
    triB.material.opacity = 0.45 + 0.55 * (ciclo < 0.5 ? 0.2 : 1);
  }
  update(-1e9);
  return { tempoCena, update, t0, duracao, fim: t0 + duracao, group: grupo };
}
