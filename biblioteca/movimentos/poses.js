// Poses nomeadas (ângulos semânticos em graus; flexão positiva = sentido anatômico)
// e expressões de rosto. Valem para qualquer personagem do esqueleto bípede.
// Cada pose sobrescreve apenas os campos que muda; o resto vem de restPose().

export const EXPRESSIONS = {
  neutra: { mouth: 'neutra', browL: [0, 0], browR: [0, 0], lid: 0.12, pupil: 1 },
  surpresa: { mouth: 'aberta', browL: [10, 0.028], browR: [10, 0.028], lid: 0, pupil: 0.75 },
  alegre: { mouth: 'sorriso', browL: [4, 0.012], browR: [4, 0.012], lid: 0.18, pupil: 1 },
  preocupada: { mouth: 'preocupada', browL: [20, 0.008], browR: [20, 0.008], lid: 0.2, pupil: 1 },
  cansada: { mouth: 'aberta', browL: [12, -0.006], browR: [12, -0.006], lid: 0.5, pupil: 1 },
  determinada: { mouth: 'neutra', browL: [-16, -0.008], browR: [-16, -0.008], lid: 0.22, pupil: 1 },
  confusa: { mouth: 'preocupada', browL: [-10, -0.004], browR: [16, 0.022], lid: 0.1, pupil: 1 },
};

// rótulo (catálogo) + campos da pose
export const POSES = {
  idle: { label: 'parado', face: { expr: 'neutra' } },
  walk: { label: 'caminhar', locomotion: 'caminhar', face: { expr: 'neutra' } },
  run: { label: 'correr', locomotion: 'correr', face: { expr: 'determinada' } },
  surprise: {
    label: 'surpresa',
    pelvis: { drop: 0.025 },
    spine: { flex: -12 },
    neck: { pitch: -8 },
    shoulderL: { flex: 30, abd: 38, twist: -20 },
    shoulderR: { flex: 30, abd: 38, twist: -20 },
    elbowL: { flex: 110 },
    elbowR: { flex: 110 },
    wristL: { flex: -35 },
    wristR: { flex: -35 },
    footR: { z: -0.07 },
    face: { expr: 'surpresa' },
  },
  cheer: {
    label: 'comemorar',
    pelvis: { drop: 0.02 },
    spine: { flex: -6 },
    neck: { pitch: -12 },
    shoulderL: { flex: -12, abd: 140, twist: 0 },
    shoulderR: { flex: -12, abd: 140, twist: 0 },
    elbowL: { flex: 20 },
    elbowR: { flex: 20 },
    footL: { x: 0.1 },
    footR: { x: -0.1 },
    face: { expr: 'alegre' },
  },
  tired: {
    label: 'cansado/ofegante',
    pelvis: { drop: 0.05 },
    spine: { flex: 25 },
    neck: { pitch: -22 },
    shoulderL: { flex: 42, abd: 10, twist: 0 },
    shoulderR: { flex: 42, abd: 10, twist: 0 },
    elbowL: { flex: 8 },
    elbowR: { flex: 8 },
    wristL: { flex: 20 },
    wristR: { flex: 20 },
    footL: { x: 0.11, z: 0.02 },
    footR: { x: -0.11, z: 0.02 },
    face: { expr: 'cansada' },
  },
  point: {
    label: 'apontar',
    spine: { twist: -10 },
    neck: { yaw: -12, pitch: -4 },
    shoulderR: { flex: 92, abd: 12, twist: 0 },
    elbowR: { flex: 0 },
    shoulderL: { flex: 0, abd: 8 },
    footR: { z: 0.05 },
    face: { expr: 'determinada' },
  },
  shrug: {
    label: 'dar de ombros',
    neck: { roll: 12, pitch: -4 },
    shoulderL: { flex: 12, abd: 22, twist: 55 },
    shoulderR: { flex: 12, abd: 22, twist: 55 },
    elbowL: { flex: 90 },
    elbowR: { flex: 90 },
    wristL: { flex: -25 },
    wristR: { flex: -25 },
    face: { expr: 'confusa' },
  },
  refuse: {
    label: 'recusar (cabeça)',
    neck: { yaw: 35, pitch: 4 },
    shoulderR: { flex: 55, abd: 8, twist: 0 },
    elbowR: { flex: 105 },
    wristR: { flex: -45 },
    face: { expr: 'determinada' },
  },
  carry: {
    label: 'carregar saco',
    pelvis: { drop: 0.012 },
    spine: { flex: -6 },
    shoulderL: { flex: 55, abd: 0, twist: 0 },
    shoulderR: { flex: 55, abd: 0, twist: 0 },
    elbowL: { flex: 35 },
    elbowR: { flex: 35 },
    wristL: { flex: 10 },
    wristR: { flex: 10 },
    face: { expr: 'determinada' },
  },
  reach: {
    label: 'pegar (agachar com os braços à frente)',
    pelvis: { drop: 0.03 },
    spine: { flex: 14 },
    neck: { pitch: -6 },
    shoulderL: { flex: 62, abd: 0, twist: 0 },
    shoulderR: { flex: 62, abd: 0, twist: 0 },
    elbowL: { flex: 14 },
    elbowR: { flex: 14 },
    wristL: { flex: 10 },
    wristR: { flex: 10 },
    face: { expr: 'determinada' },
  },
  offer: {
    label: 'estender objeto',
    spine: { flex: 8 },
    neck: { pitch: 6 },
    shoulderR: { flex: 78, abd: 6, twist: 65 },
    elbowR: { flex: 12 },
    wristR: { flex: -10 },
    footR: { z: 0.06 },
    face: { expr: 'alegre' },
  },
  receive: {
    label: 'receber objeto',
    spine: { flex: 6 },
    neck: { pitch: 12 },
    shoulderL: { flex: 50, abd: 10, twist: 55 },
    shoulderR: { flex: 50, abd: 10, twist: 55 },
    elbowL: { flex: 50 },
    elbowR: { flex: 50 },
    wristL: { flex: -15 },
    wristR: { flex: -15 },
    face: { expr: 'alegre' },
  },
};

// As 12 poses da galeria (NICO_SPEC §4), na ordem da spec.
export const GALLERY = ['idle', 'walk', 'run', 'surprise', 'cheer', 'tired', 'point', 'shrug', 'refuse', 'carry', 'offer', 'receive'];

// Aceita o nome em português (rótulo) ou a chave em inglês.
const ALIAS = {
  parado: 'idle', caminhar: 'walk', correr: 'run', surpresa: 'surprise', comemorar: 'cheer',
  cansado: 'tired', ofegante: 'tired', apontar: 'point', darDeOmbros: 'shrug', 'dar de ombros': 'shrug',
  recusar: 'refuse', carregar: 'carry', carregarSaco: 'carry', estender: 'offer', estenderObjeto: 'offer',
  receber: 'receive', receberObjeto: 'receive', pegar: 'reach',
};
export function poseKey(name) {
  const k = POSES[name] ? name : ALIAS[name];
  if (!k) throw new Error(`pose desconhecida: ${name}`);
  return k;
}
