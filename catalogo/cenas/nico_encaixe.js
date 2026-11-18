// Teste de encaixe: Nico pega o saco (dois braços) num caixote à frente, gira 90°,
// caminha 3 s carregando e solta noutro caixote. Alturas e posições dos caixotes são
// DERIVADAS da pose no instante da pega/soltura (o saco fica exatamente onde o encaixe
// o põe: sem salto, sem flutuar).
import * as THREE from 'three';
import { createStudio } from '/biblioteca/cenarios/estudio.js';
import { createNico } from '/biblioteca/personagens/nico/index.js';
import { createSack } from '/biblioteca/objetos/saco.js';
import { createCrate } from '/biblioteca/objetos/caixote.js';
import { token } from '/biblioteca/nucleo/materiais.js';
import { auditPose, contactDistance } from '/biblioteca/personagens/nico/checagem.js';

export const TEMPOS = { pegarIni: 0.5, pega: 1.1, levanta: 1.7, giroFim: 2.9, andarFim: 5.9, solta: 6.5, fim: 7.1 };
export const DURACAO = 7.6;
const X0 = -0.8;
const VEL = 0.6;
const H0 = 0; // de frente para a câmera (+Z) ao pegar
const H1 = Math.PI / 2; // anda para +X

let ctx, nico, studio, saco, caixoteA, caixoteB, walk, turn, gReach, gCarry, gDown, gIdle, posA, posB;

function poseAt(t) {
  const T = TEMPOS;
  // raiz definida a cada quadro só a partir de t (sem herdar do quadro anterior)
  nico.group.position.set(X0 + walk.locomotion.dist(t), 0, 0);
  nico.group.rotation.set(0, t < T.giroFim ? H0 : H1, 0);
  if (t < T.pegarIni) return nico.setPose('idle', t);
  if (t < T.pega) return gReach(t);
  if (t < T.levanta) return gCarry(t);
  if (t < T.giroFim) return turn(t);
  if (t < T.andarFim) return walk(t);
  if (t < T.solta) return gDown(t);
  return gIdle(t);
}

export function build(c) {
  ctx = c;
  studio = createStudio(ctx.scene, { tamanho: 10 });
  nico = createNico();
  ctx.scene.add(nico.group);
  const T = TEMPOS;
  const cfg = token('locomocao.caminhar');
  const dur = T.andarFim - T.giroFim;
  const len = VEL * (dur - cfg.aceleracaoS);
  gReach = nico.play('pose', T.pegarIni, { from: 'idle', to: 'reach', dur: T.pega - T.pegarIni, abrir: 22 });
  gCarry = nico.play('pose', T.pega, { from: 'reach', to: 'carry', dur: T.levanta - T.pega });
  turn = nico.play('virar', T.levanta, { at: [X0, 0], from: H0, to: H1, duration: T.giroFim - T.levanta, upper: 'carry', expr: 'determinada' });
  walk = nico.play('caminhar', T.giroFim, { from: [X0, 0], to: [X0 + len, 0], duration: dur, upper: 'carry', expr: 'determinada' });
  gDown = nico.play('pose', T.andarFim, { from: 'carry', to: 'reach', dur: T.solta - T.andarFim });
  gIdle = nico.play('pose', T.solta, { from: 'reach', to: 'idle', dur: T.fim - T.solta, abrir: 22 });

  saco = createSack();
  ctx.scene.add(saco);
  const ondeFica = (t) => {
    poseAt(t);
    nico.grab(saco, 'antebraços');
    saco.updateWorldMatrix(true, false);
    return saco.getWorldPosition(new THREE.Vector3());
  };
  posA = ondeFica(T.pega);
  posB = ondeFica(T.solta);
  caixoteA = createCrate({ altura: posA.y, largura: 0.34, profundidade: 0.2 });
  caixoteB = createCrate({ altura: posB.y, largura: 0.2, profundidade: 0.34 });
  caixoteA.position.set(posA.x, 0, posA.z);
  caixoteB.position.set(posB.x, 0, posB.z);
  ctx.scene.add(caixoteA, caixoteB);
}

export function renderFrame(t) {
  const T = TEMPOS;
  poseAt(t);
  if (t < T.pega) nico.release(saco, posA, { parent: ctx.scene, rotY: H0 });
  else if (t < T.solta) nico.grab(saco, 'antebraços');
  else nico.release(saco, posB, { parent: ctx.scene, rotY: H1 });
  const x = THREE.MathUtils.clamp(nico.group.position.x, X0, posB.x - 0.25);
  studio.seguir(x, 0);
  ctx.camera.position.set(x + 1.5, 1.1, 3.4);
  ctx.camera.lookAt(x + 0.15, 0.42, 0.1);
}

export function auditar(t) {
  renderFrame(t);
  const objetos = [
    { obj: saco, proxies: saco.userData.proxies },
    { obj: caixoteA, proxies: caixoteA.userData.proxies.map((p) => ({ ...p, name: 'caixoteA' })) },
    { obj: caixoteB, proxies: caixoteB.userData.proxies.map((p) => ({ ...p, name: 'caixoteB' })) },
  ];
  const a = auditPose(nico, objetos);
  const segurando = saco.userData.heldBy != null;
  const contatoBracos = contactDistance(nico, saco, saco.userData.proxies, ['antebracoL', 'antebracoR', 'maoL', 'maoR']);
  saco.updateWorldMatrix(true, false);
  const fundo = saco.getWorldPosition(new THREE.Vector3()).y;
  const apoio = t < TEMPOS.pega ? caixoteA.userData.altura : t >= TEMPOS.solta ? caixoteB.userData.altura : null;
  return {
    ...a,
    segurando,
    contatoBracos,
    folgaApoio: apoio == null ? null : fundo - apoio,
    alturaCaixotes: [caixoteA.userData.altura, caixoteB.userData.altura],
  };
}
