// Sonda de WebGL: cena mínima para medir a captura headless (tempo por quadro, renderer).
import * as THREE from 'three';
import { createStudio } from '/biblioteca/cenarios/estudio.js';
import { material } from '/biblioteca/nucleo/materiais.js';

let ctx, cubo;

export function build(c) {
  ctx = c;
  createStudio(ctx.scene);
  cubo = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.4), material('cores.nico.camiseta'));
  cubo.castShadow = true;
  ctx.scene.add(cubo);
  ctx.camera.position.set(0, 1, 4);
  ctx.camera.lookAt(0, 0.4, 0);
}

export function renderFrame(t) {
  cubo.position.y = 0.2 + Math.abs(Math.sin(t * Math.PI)) * 0.5;
  cubo.rotation.y = t;
}

