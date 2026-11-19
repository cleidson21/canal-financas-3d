// Terraço baixo (cenário mínimo, EP001 cena 1): chão em degraus descendo até o mar,
// mar ao fundo com marolas e veleiros distantes, montanha low-poly atrás, luz direcional
// de fim de tarde. Sem barracas. Plano do Nico em y = 0, câmera olhando para -Z.
//   const cen = createTerracoBaixo(ctx);  cen.seguir(x, z);  cen.update(t);
import * as THREE from 'three';
import { token, material } from '../nucleo/materiais.js';
import { rng } from '../nucleo/matematica.js';

export function createTerracoBaixo(ctx, { luz = 'fimDeTarde' } = {}) {
  const { scene } = ctx;
  const L = token('luz.' + luz);
  const cor = (p) => new THREE.Color(token(p));

  // céu em gradiente (vertical, na tela) + neblina quente
  const cv = document.createElement('canvas');
  cv.width = 8;
  cv.height = 256;
  const g = cv.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 0, 256);
  grad.addColorStop(0, token('cores.cena.ceuTopo'));
  grad.addColorStop(0.62, token('cores.cena.ceuBase'));
  grad.addColorStop(1, token('cores.cena.ceuBase'));
  g.fillStyle = grad;
  g.fillRect(0, 0, 8, 256);
  const ceu = new THREE.CanvasTexture(cv);
  ceu.colorSpace = THREE.SRGBColorSpace;
  scene.background = ceu;
  scene.fog = new THREE.Fog(cor('cores.cena.neblinaTarde'), 45, 430);

  scene.add(new THREE.HemisphereLight(new THREE.Color(L.ceu), new THREE.Color(L.solo), L.hemisferioIntensidade));
  const sol = new THREE.DirectionalLight(new THREE.Color(L.sol), L.solIntensidade);
  sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048);
  Object.assign(sol.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: 0.5, far: 40 });
  sol.shadow.bias = -0.0006;
  sol.shadow.normalBias = 0.012;
  scene.add(sol, sol.target);
  const dir = new THREE.Vector3(...L.solDirecao).normalize().multiplyScalar(14);

  const rect = (w, h, d, tok, x, y, z, nome) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material(tok));
    m.name = nome;
    m.position.set(x, y, z);
    m.castShadow = true;
    m.receiveShadow = true;
    scene.add(m);
    return m;
  };
  // Terraço (topo em y = 0) e três degraus até o cais baixo, tudo em caixas largas
  const LARG = 60;
  rect(LARG, 1, 11, 'cores.cena.terracoChao', 0, -0.5, 2.3, 'terraco_chao'); // z de -3.2 a 7.8
  const degraus = [
    [-3.2 - 0.3, 0.2],
    [-3.2 - 0.9, 0.4],
    [-3.2 - 1.5, 0.6],
  ];
  degraus.forEach(([zc, desc], i) => rect(LARG, 1, 0.6, i % 2 ? 'cores.cena.terracoDegrau' : 'cores.cena.terracoBorda', 0, -desc - 0.5, zc, 'terraco_degrau'));
  rect(LARG, 1, 2.2, 'cores.cena.terracoDegrau', 0, -0.6 - 0.5 - 0.0, -3.2 - 1.8 - 1.1, 'terraco_cais');

  // juntas do piso (0,5 m) para ler o movimento dos pés
  const juntas = new THREE.Group();
  juntas.name = 'terraco_juntas';
  const mj = material('cores.cena.terracoBorda', { flat: false });
  const gx = new THREE.PlaneGeometry(14, 0.012);
  const gz = new THREE.PlaneGeometry(0.012, 11);
  for (let i = -14; i <= 14; i++) {
    const a = new THREE.Mesh(gx, mj);
    a.rotation.x = -Math.PI / 2;
    a.position.set(0, 0.001, -3.2 + (i + 14) * 0.38);
    if (a.position.z > 7.8) continue;
    a.receiveShadow = true;
    juntas.add(a);
    const b = new THREE.Mesh(gz, mj);
    b.rotation.x = -Math.PI / 2;
    b.position.set(i * 0.5, 0.0012, 2.3);
    b.receiveShadow = true;
    juntas.add(b);
  }
  scene.add(juntas);

  // bolardos na borda do cais
  for (const x of [-3.2, -1.1, 1.3, 3.5]) {
    const b = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.085, 0.3, 8), material('cores.cena.montanhaSombra'));
    b.name = 'terraco_bolardo';
    b.position.set(x, 0.15, -3.0);
    b.castShadow = true;
    b.receiveShadow = true;
    scene.add(b);
  }

  // mar + marolas
  const YM = -1.35;
  const mar = new THREE.Mesh(new THREE.PlaneGeometry(900, 900), material('cores.cena.mar', { flat: false }));
  mar.name = 'mar';
  mar.rotation.x = -Math.PI / 2;
  mar.position.set(0, YM, -300);
  mar.receiveShadow = true;
  scene.add(mar);
  const rand = rng(21);
  const marolas = Array.from({ length: 46 }, () => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), material('cores.cena.marClaro', { flat: false }));
    m.name = 'marola';
    m.rotation.x = -Math.PI / 2;
    const z = -9 - Math.pow(rand(), 1.6) * 110;
    const e = { m, x0: (rand() - 0.5) * 120, z, w: 1.2 + rand() * 3.5 * (1 + -z / 40), f: 0.15 + rand() * 0.2, fase: rand() * 6.28 };
    m.scale.set(e.w, 0.07 * (1 + -z / 60), 1);
    m.position.set(e.x0, YM + 0.01, z);
    scene.add(m);
    return e;
  });

  // veleiros distantes
  const barcos = [[-9, -34, 1.0], [11, -52, 1.4], [-24, -78, 2.0]].map(([x, z, s], i) => {
    const b = new THREE.Group();
    b.name = 'veleiro';
    const casco = new THREE.Mesh(new THREE.BoxGeometry(2.2 * s, 0.5 * s, 0.8 * s), material('cores.cena.terracoBorda'));
    casco.position.y = 0.25 * s;
    const vela = new THREE.Mesh(new THREE.ConeGeometry(0.75 * s, 2.6 * s, 3), material('cores.objetos.farinha'));
    vela.position.set(0, 1.8 * s, 0);
    vela.scale.z = 0.12;
    b.add(casco, vela);
    b.position.set(x, YM, z);
    scene.add(b);
    return { b, s, x, z, fase: i * 1.7 };
  });

  // montanha low-poly atrás do mar (cones de poucas facetas, sombras alternadas)
  const serra = new THREE.Group();
  serra.name = 'montanha';
  const r2 = rng(33);
  const picos = [[-150, 26, 70], [-90, 40, 90], [-35, 30, 80], [30, 52, 110], [90, 34, 85], [150, 25, 72], [-5, 22, 100]];
  picos.forEach(([x, h, r], i) => {
    const geo = new THREE.ConeGeometry(r, h, 5 + Math.floor(r2() * 2), 1);
    const m = new THREE.Mesh(geo, material(i % 2 ? 'cores.cena.montanhaSombra' : 'cores.cena.montanha'));
    m.name = 'montanha_pico';
    m.position.set(x, YM + h / 2 - 1, -265 - (i % 3) * 22);
    m.rotation.y = r2() * 3;
    serra.add(m);
    const topo = new THREE.Mesh(new THREE.ConeGeometry(r * 0.28, h * 0.28, 5), material('cores.cena.montanhaTopo'));
    topo.name = 'montanha_topo';
    topo.position.set(x, YM + h - h * 0.14 - 1, -265 - (i % 3) * 22);
    topo.rotation.y = m.rotation.y;
    serra.add(topo);
  });
  scene.add(serra);

  const seguir = (x, z) => {
    sol.target.position.set(x, 0, z);
    sol.position.set(x + dir.x, dir.y, z + dir.z);
  };
  seguir(0, 0);

  function update(t) {
    for (const e of marolas) e.m.position.x = e.x0 + 1.4 * Math.sin(2 * Math.PI * e.f * t + e.fase);
    for (const o of barcos) {
      o.b.position.y = YM + 0.08 * o.s * Math.sin(1.1 * t + o.fase);
      o.b.rotation.z = 0.04 * Math.sin(0.9 * t + o.fase);
    }
  }
  return { seguir, update, sol, bordaZ: -3.2, nivelMar: YM };
}
