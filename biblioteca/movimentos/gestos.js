// Movimentos parametrizados (gestos) como função pura do tempo local tl (s).
// Cada um devolve uma pose parcial; o personagem mistura com restPose().
import { blendPose } from '../personagens/bipede/rig.js';
import { POSES, poseKey } from './poses.js';
import { ease, clamp, smoothstep } from '../nucleo/matematica.js';

const strip = ({ label, locomotion, ...rest }) => rest;

// Respiração leve + piscada, sem semente aleatória: piscadas em instantes fixos.
export function breathe(t, amp = 1) {
  const s = Math.sin((2 * Math.PI * t) / 3.4);
  return {
    pelvis: { drop: 0.004 + 0.0015 * amp * (1 + s) },
    spine: { flex: 1.2 * amp * s },
    neck: { pitch: -0.8 * amp * s },
  };
}

export function blinkAt(t, period = 3.7, offset = 1.3, dur = 0.16) {
  const k = (((t - offset) % period) + period) % period;
  return k < dur ? Math.sin((Math.PI * k) / dur) : 0;
}

// Soma campos numéricos de b sobre a (para camadas aditivas como respiração).
export function addPose(a, b) {
  const out = { ...a };
  for (const [k, v] of Object.entries(b)) {
    if (v && typeof v === 'object' && a[k] && typeof a[k] === 'object') {
      out[k] = { ...a[k] };
      for (const [kk, vv] of Object.entries(v)) if (typeof vv === 'number') out[k][kk] = (a[k][kk] ?? 0) + vv;
    } else if (a[k] === undefined) out[k] = v;
  }
  return out;
}

// Pose nomeada estática com vida (respiração/piscada) no instante t.
export function livePose(rest, name, t) {
  const p = blendPose(rest, { ...rest, ...mergeParts(rest, strip(POSES[poseKey(name)])) }, 1);
  const breath = breathe(t, ['tired', 'exhausted_load', 'carry_back'].includes(poseKey(name)) ? 0 : 1);
  const out = addPose(p, breath);
  out.face = { ...out.face, blink: blinkAt(t) };
  return out;
}

function mergeParts(base, over) {
  const out = {};
  for (const [k, v] of Object.entries(over)) out[k] = v && typeof v === 'object' && !Array.isArray(v) ? { ...base[k], ...v } : v;
  return out;
}

// Transição de A para B com easing (entrada) e retorno opcional.
function transition(rest, from, to, tl, dur, easing = ease.inOutCubic) {
  const a = from ? livePose(rest, from, tl) : rest;
  const b = livePose(rest, to, tl);
  return blendPose(a, b, easing(clamp(tl / dur, 0, 1)));
}

// Gestos com duração própria. params.from = pose de partida (padrão 'idle').
export const GESTURES = {
  // recusar: balança a cabeça 3 vezes e volta
  refuse(rest, tl, p = {}) {
    const base = transition(rest, p.from || 'idle', 'refuse', tl, 0.25);
    const env = smoothstep(0, 0.15, tl) * (1 - smoothstep(1.2, 1.5, tl));
    base.neck = { ...base.neck, yaw: 32 * Math.sin(2 * Math.PI * 2.2 * tl) * env };
    return base;
  },
  // comemorar: sobe os braços com overshoot e pulsa nos joelhos
  cheer(rest, tl, p = {}) {
    const base = transition(rest, p.from || 'idle', 'cheer', tl, 0.35, ease.outBack);
    const pump = Math.sin(2 * Math.PI * 2.0 * tl) * smoothstep(0.3, 0.5, tl);
    base.pelvis = { ...base.pelvis, drop: base.pelvis.drop + 0.015 * pump };
    base.shoulderL = { ...base.shoulderL, abd: base.shoulderL.abd + 8 * pump };
    base.shoulderR = { ...base.shoulderR, abd: base.shoulderR.abd + 8 * pump };
    return base;
  },
  // cansado: tronco sobe e desce com respiração ofegante
  tired(rest, tl, p = {}) {
    const base = transition(rest, p.from || 'idle', 'tired', tl, 0.6);
    const pant = Math.sin(2 * Math.PI * 1.7 * tl) * smoothstep(0.4, 0.7, tl);
    base.spine = { ...base.spine, flex: base.spine.flex - 3 * pant };
    base.neck = { ...base.neck, pitch: base.neck.pitch + 2 * pant };
    return base;
  },
  surprise: (rest, tl, p = {}) => transition(rest, p.from || 'idle', 'surprise', tl, 0.18, ease.outBack),
  // exausto com carga: balança o peso de um pé para o outro (período 2,6 s) e arfa
  exhausted_load(rest, tl, p = {}) {
    const base = transition(rest, p.from || 'idle', 'exhausted_load', tl, 0.5);
    const w = Math.sin((2 * Math.PI * tl) / 2.6) * smoothstep(0.3, 0.9, tl);
    const pant = Math.sin(2 * Math.PI * 1.5 * tl) * smoothstep(0.3, 0.9, tl);
    base.pelvis = { ...base.pelvis, x: 0.008 * w, roll: 0.8 * w, drop: base.pelvis.drop + 0.0012 * pant };
    base.spine = { ...base.spine, side: -6 * w, flex: base.spine.flex - 1.5 * pant };
    base.neck = { ...base.neck, roll: 4 * w };
    return base;
  },
  point: (rest, tl, p = {}) => transition(rest, p.from || 'idle', 'point', tl, 0.35, ease.outBack),
  shrug(rest, tl, p = {}) {
    const up = transition(rest, p.from || 'idle', 'shrug', tl, 0.3, ease.outCubic);
    const down = smoothstep(1.0, 1.4, tl);
    return blendPose(up, livePose(rest, 'idle', tl), down);
  },
  offer: (rest, tl, p = {}) => transition(rest, p.from || 'idle', 'offer', tl, 0.5),
  receive: (rest, tl, p = {}) => transition(rest, p.from || 'idle', 'receive', tl, 0.5),
  // genérico: de uma pose a outra em `dur`. abrir: graus de abdução extra no meio do
  // caminho (braços contornam um objeto em vez de atravessá-lo).
  pose(rest, tl, p) {
    const out = transition(rest, p.from || 'idle', p.to, tl, p.dur ?? 0.5, p.easing ? ease[p.easing] : ease.inOutCubic);
    if (p.abrir) {
      const bump = p.abrir * Math.sin(Math.PI * clamp(tl / (p.dur ?? 0.5), 0, 1));
      out.shoulderL = { ...out.shoulderL, abd: out.shoulderL.abd + bump };
      out.shoulderR = { ...out.shoulderR, abd: out.shoulderR.abd + bump };
    }
    return out;
  },
};

