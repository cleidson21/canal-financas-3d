// Utilidades matemáticas puras (sem estado, sem relógio real).

export const DEG = Math.PI / 180;

export const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
export const lerp = (a, b, k) => a + (b - a) * k;
export const invLerp = (a, b, v) => (b === a ? 0 : clamp((v - a) / (b - a), 0, 1));
export const smoothstep = (a, b, v) => {
  const k = invLerp(a, b, v);
  return k * k * (3 - 2 * k);
};

export const ease = {
  linear: (k) => k,
  inQuad: (k) => k * k,
  outQuad: (k) => k * (2 - k),
  inOutQuad: (k) => (k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2),
  inOutCubic: (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
  outCubic: (k) => 1 - Math.pow(1 - k, 3),
  inOutSine: (k) => -(Math.cos(Math.PI * k) - 1) / 2,
  outBack: (k) => {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2);
  },
};

// Gerador pseudoaleatório com semente (mulberry32). Use sempre com semente fixa.
export function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Interpola uma trilha de chaves [{t, v}] (v número) com easing entre chaves.
export function track(keys, t, easing = ease.inOutCubic) {
  if (t <= keys[0].t) return keys[0].v;
  for (let i = 1; i < keys.length; i++) {
    const k1 = keys[i];
    if (t <= k1.t) {
      const k0 = keys[i - 1];
      return lerp(k0.v, k1.v, (k1.easing || easing)(invLerp(k0.t, k1.t, t)));
    }
  }
  return keys[keys.length - 1].v;
}

