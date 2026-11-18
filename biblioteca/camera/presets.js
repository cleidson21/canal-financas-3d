// Presets de enquadramento (tokens.camera.presets). Enquadra um alvo por altura visível.
import * as THREE from 'three';
import { token } from '../nucleo/materiais.js';
import { DEG } from '../nucleo/matematica.js';

// camera: PerspectiveCamera; preset: 'aberto'|'medio'|'detalhe'|'panoramica'
// alvo: [x,y,z] (ponto de interesse); azimute: graus em torno de Y (0 = de frente, +Z)
export function frame(camera, preset, alvo, { azimute = 0, alturaVisivelM, alturaOlho, inclinacaoGraus } = {}) {
  const p = token('camera.presets.' + preset);
  const h = alturaVisivelM ?? p.alturaVisivelM;
  const tilt = (inclinacaoGraus ?? p.inclinacaoGraus) * DEG;
  const dist = h / 2 / Math.tan((camera.fov * DEG) / 2);
  const target = new THREE.Vector3(...alvo);
  const az = azimute * DEG;
  camera.position.set(
    target.x + Math.sin(az) * Math.cos(tilt) * dist,
    target.y + Math.sin(tilt) * dist,
    target.z + Math.cos(az) * Math.cos(tilt) * dist,
  );
  camera.lookAt(target);
  camera.updateProjectionMatrix();
  return { dist, target };
}

