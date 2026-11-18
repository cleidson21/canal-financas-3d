// Locomoção (caminhar/correr) em linha reta, como função pura do tempo.
// Regra: fase = distância percorrida ÷ comprimento do passo. Cada pé apoiado tem
// posição fixa no mundo (com rolagem calcanhar→ponta em torno de um ponto fixo),
// então não desliza por construção. A perna chega lá por IK no rig.
import { DEG, clamp, lerp, ease, smoothstep } from '../nucleo/matematica.js';

// dims: escala do personagem; cfg: tokens.locomocao.<tipo>
// opts: { from:[x,z], to:[x,z], t0, duration?, speed?, step? }
export function createLocomotion(dims, cfg, opts) {
  const [x0, z0] = opts.from;
  const [x1, z1] = opts.to;
  const len = Math.hypot(x1 - x0, z1 - z0);
  const heading = Math.atan2(x1 - x0, z1 - z0);
  const dir = [Math.sin(heading), Math.cos(heading)];
  const left = [Math.cos(heading), -Math.sin(heading)];
  const N = Math.max(1, Math.round(len / (opts.step ?? cfg.passo)));
  const L = len / N;
  const sigma = cfg.apoio;
  const ta = cfg.aceleracaoS;
  const t0 = opts.t0 ?? 0;
  let vmax;
  let T;
  if (opts.duration) {
    T = opts.duration;
    vmax = len / (T - ta);
  } else {
    vmax = opts.speed ?? cfg.velocidade;
    T = len / vmax + ta;
  }
  const P = dims.pe;
  const heelLen = P.calcanhar;
  const toeLen = P.comprimento - P.calcanhar;
  const ankH = P.tornozeloY;
  const hipX = dims.quadrilX;

  const integ = (u) => u * u * u - (u * u * u * u) / 2; // ∫ smoothstep
  function dist(t) {
    const tl = t - t0;
    if (tl <= 0) return 0;
    if (tl >= T) return len;
    if (tl < ta) return vmax * ta * integ(tl / ta);
    if (tl > T - ta) return len - vmax * ta * integ((T - tl) / ta);
    return 0.5 * vmax * ta + vmax * (tl - ta);
  }
  function speedFactor(t) {
    const tl = t - t0;
    if (tl <= 0 || tl >= T) return 0;
    return Math.min(smoothstep(0, ta, tl), smoothstep(0, ta, T - tl));
  }
  function timeAt(d) {
    let a = t0;
    let b = t0 + T;
    for (let i = 0; i < 40; i++) {
      const m = (a + b) / 2;
      if (dist(m) < d) a = m;
      else b = m;
    }
    return (a + b) / 2;
  }

  // Passos n = 1..N+1. Passo ímpar move o pé direito (R), par o esquerdo (L).
  const S = (n) => (n <= 0 ? 0 : Math.min(n, N) * L);
  const swingStart = (n) => Math.max(0, (n - 2 + sigma) * L);
  const swingEnd = (n) => (n === N + 1 ? len : Math.min(len, (n - sigma) * L));
  const footOfStep = (n) => (n % 2 === 1 ? 'R' : 'L');
  const stepsOf = (f) => {
    const out = [];
    for (let n = f === 'R' ? 1 : 2; n <= N + 1; n += 2) out.push(n);
    return out;
  };

  // Estado de apoio do pé (ao longo do caminho): ângulo e altura do tornozelo.
  function stanceAnkle(Spos, dd, land, toeoff, k) {
    const p0 = 14 * k; // calcanhar toca com a ponta erguida
    const p1 = 22 * k; // ponta empurra com o calcanhar erguido
    const heelWin = 0.22 * L;
    const toeWin = 0.32 * L;
    if (dd < land + heelWin && Number.isFinite(land)) {
      const pitch = p0 * (1 - ease.inOutSine(clamp((dd - land) / heelWin, 0, 1)));
      return heelPivot(Spos, pitch);
    }
    if (dd > toeoff - toeWin && Number.isFinite(toeoff)) {
      const q = p1 * ease.inOutSine(clamp((dd - (toeoff - toeWin)) / toeWin, 0, 1));
      return toePivot(Spos, q);
    }
    return { along: Spos, h: ankH, pitch: 0 };
  }
  function heelPivot(Spos, p) {
    const r = p * DEG;
    const heel = Spos - heelLen;
    return { along: heel + heelLen * Math.cos(r) - ankH * Math.sin(r), h: heelLen * Math.sin(r) + ankH * Math.cos(r), pitch: p };
  }
  function toePivot(Spos, q) {
    const r = q * DEG;
    const toe = Spos + toeLen;
    return { along: toe - toeLen * Math.cos(r) + ankH * Math.sin(r), h: toeLen * Math.sin(r) + ankH * Math.cos(r), pitch: -q };
  }

  function footState(f, dd, k, kAt) {
    const steps = stepsOf(f);
    for (const n of steps) {
      const a = swingStart(n);
      const b = swingEnd(n);
      if (dd >= a && dd < b) {
        // balanço: do estado de saída (ponta) ao de chegada (calcanhar)
        const prev = steps[steps.indexOf(n) - 1];
        const from = stanceAnkle(S(n - 2), a, prev ? swingEnd(prev) : -Infinity, a, kAt(a));
        const to = stanceAnkle(S(n), b, b, Infinity, kAt(b));
        const u = (dd - a) / (b - a);
        const ue = ease.inOutSine(u);
        return {
          along: lerp(from.along, to.along, ue),
          h: lerp(from.h, to.h, ue) + cfg.alturaPe * Math.max(k, 0.35) * Math.sin(Math.PI * u),
          pitch: lerp(from.pitch, to.pitch, ue),
          swing: true,
          u,
        };
      }
    }
    // apoio: último passo concluído deste pé
    let last = null;
    for (const n of steps) if (swingEnd(n) <= dd) last = n;
    const next = steps.find((n) => swingStart(n) > dd);
    const Spos = last ? S(last) : 0;
    const land = last ? swingEnd(last) : -Infinity;
    const toeoff = next !== undefined ? swingStart(next) : Infinity;
    return { ...stanceAnkle(Spos, dd, land, toeoff, k), swing: false };
  }

  function at(t) {
    const dd = dist(t);
    const k = speedFactor(t);
    const kAt = (d2) => speedFactor(timeAt(d2));
    const phi = dd / L;
    const run = sigma < 0.5;
    const feet = {};
    const pose = {};
    for (const f of ['L', 'R']) {
      const st = footState(f, dd, k, kAt);
      const lat = (f === 'L' ? 1 : -1) * hipX;
      feet[f] = st;
      pose['foot' + f] = {
        world: true,
        ankle: [x0 + dir[0] * st.along + left[0] * lat, st.h, z0 + dir[1] * st.along + left[1] * lat],
        yaw: heading / DEG,
        pitch: st.pitch,
      };
    }
    // quanto cada pé está à frente da pelve (−1..1), para balanço de braço e torção
    const fwd = (f) => clamp((feet[f].along - dd) / (sigma * L), -1, 1);
    const bob = cfg.balanco * k * Math.cos(2 * Math.PI * phi) * (run ? 1 : -1);
    pose.pelvis = { drop: 0.004 + cfg.descida * k + bob, yaw: -4 * k * (fwd('L') - fwd('R')) / 2, roll: 0, flex: 0 };
    pose.spine = { flex: cfg.inclinacao * k, twist: 6 * k * (fwd('L') - fwd('R')) / 2, side: 0 };
    pose.neck = { pitch: -cfg.inclinacao * k * 0.6, yaw: 0, roll: 0 };
    const armL = cfg.bracoFlex * k * fwd('R');
    const armR = cfg.bracoFlex * k * fwd('L');
    const elbowBase = run ? 85 : 12;
    pose.shoulderL = { flex: armL, abd: 7, twist: 0 };
    pose.shoulderR = { flex: armR, abd: 7, twist: 0 };
    pose.elbowL = { flex: elbowBase * Math.max(k, run ? 1 : 0) + 10 + Math.max(0, armL) * 0.5 };
    pose.elbowR = { flex: elbowBase * Math.max(k, run ? 1 : 0) + 10 + Math.max(0, armR) * 0.5 };
    return {
      root: { x: x0 + dir[0] * dd, z: z0 + dir[1] * dd, heading },
      pose,
      feet,
      d: dd,
      k,
      phase: phi,
    };
  }

  return { at, dist, timeAt, duration: T, length: len, stepLength: L, steps: N, t0, heading, vmax };
}

// Giro no lugar, em passinhos alternados. Pé apoiado fica fixo; o rumo do corpo é a
// média dos rumos dos pés (o quadril nunca torce mais que meio passo).
// opts: { at:[x,z], from: rumo0 (rad), to: rumo1 (rad), t0, duration, passoGraus? }
export function createTurn(dims, opts) {
  const [cx, cz] = opts.at;
  const h0 = opts.from;
  const dH = opts.to - opts.from;
  const k = Math.max(2, Math.ceil(Math.abs(dH) / (((opts.passoGraus ?? 25) * Math.PI) / 180)) + 1);
  const t0 = opts.t0 ?? 0;
  const T = opts.duration ?? k * 0.3;
  const dt = T / k;
  const ankH = dims.pe.tornozeloY;
  const hipX = dims.quadrilX;
  const lead = dH >= 0 ? 'L' : 'R';
  const other = lead === 'L' ? 'R' : 'L';
  const footOf = (i) => (i % 2 === 0 ? lead : other);
  const targetH = (i) => h0 + dH * Math.min(1, (i + 1) / (k - 1));
  const place = (s, h) => {
    const side = s === 'L' ? 1 : -1;
    return { x: cx + Math.cos(h) * side * hipX, z: cz - Math.sin(h) * side * hipX, h };
  };
  // posição de cada pé no fim de cada passo
  function footAt(s, t) {
    let cur = place(s, h0);
    for (let i = 0; i < k; i++) {
      if (footOf(i) !== s) continue;
      const a = t0 + i * dt;
      const b = a + dt;
      const nxt = place(s, targetH(i));
      if (t < a) return { ...cur, lift: 0 };
      if (t < b) {
        const u = (t - a) / dt;
        const e = ease.inOutSine(u);
        return { x: lerp(cur.x, nxt.x, e), z: lerp(cur.z, nxt.z, e), h: lerp(cur.h, nxt.h, e), lift: 0.035 * Math.sin(Math.PI * u) };
      }
      cur = nxt;
    }
    return { ...cur, lift: 0 };
  }
  function at(t) {
    const pose = {};
    const f = {};
    for (const s of ['L', 'R']) {
      f[s] = footAt(s, t);
      pose['foot' + s] = { world: true, ankle: [f[s].x, ankH + f[s].lift, f[s].z], yaw: f[s].h / DEG, pitch: 0 };
    }
    const heading = (f.L.h + f.R.h) / 2;
    const moving = Math.max(f.L.lift, f.R.lift) / 0.035;
    pose.pelvis = { drop: 0.004 + 0.012 * moving, yaw: 0, roll: 0, flex: 0 };
    return { root: { x: cx, z: cz, heading }, pose };
  }
  return { at, duration: T, steps: k, t0 };
}

