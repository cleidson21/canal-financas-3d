// Materiais criados SEMPRE a partir de valores/tokens.json (nunca cor fixa no ativo).
import * as THREE from 'three';
import tokens from '../../valores/tokens.json';

export { tokens };

const cache = new Map();

// Busca um valor em tokens por caminho "cores.nico.tenis".
export function token(path) {
  const v = path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), tokens);
  if (v === undefined) throw new Error(`token inexistente: ${path}`);
  return v;
}

// Material low-poly (sombreamento facetado). Compartilhado por caminho de token.
export function material(path, opts = {}) {
  const key = path + JSON.stringify(opts);
  if (cache.has(key)) return cache.get(key);
  const m = new THREE.MeshStandardMaterial({
    color: new THREE.Color(token(path)),
    roughness: opts.roughness ?? 0.85,
    metalness: 0,
    flatShading: opts.flat ?? true,
  });
  m.userData.token = path;
  cache.set(key, m);
  return m;
}

