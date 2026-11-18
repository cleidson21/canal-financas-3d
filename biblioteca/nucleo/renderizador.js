// Contexto de renderização comum ao catálogo e à captura (mesmo visual nos dois).
import * as THREE from 'three';
import { tokens } from './materiais.js';

export function createContext({ canvas, width, height, params = {} } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(1);
  renderer.setSize(width, height, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  const cam = tokens.camera;
  const camera = new THREE.PerspectiveCamera(cam.fov, width / height, cam.perto, cam.longe);
  return { THREE, renderer, scene, camera, tokens, width, height, params };
}

export function glInfo(renderer) {
  const gl = renderer.getContext();
  const ext = gl.getExtension('WEBGL_debug_renderer_info');
  return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
}

