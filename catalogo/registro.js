// Registro dos ativos mostrados no catálogo. Espelha catalogo/INDEX.md.
export const ATIVOS = [
  {
    id: 'nico',
    nome: 'Nico',
    grupo: 'Personagens',
    arquivo: 'biblioteca/personagens/nico/index.js',
    estado: 'aguardando aprovação',
    turntable: '/catalogo/cenas/nico_turntable.js',
    galeria: '/catalogo/cenas/nico_galeria.js',
    testes: [
      { nome: 'Caminhada 4 s (pés fixos)', cena: '/catalogo/cenas/nico_caminhada.js', duracao: 4.6 },
      { nome: 'Encaixe: pegar saco, andar 3 s, soltar', cena: '/catalogo/cenas/nico_encaixe.js', duracao: 7.6 },
    ],
    folhas: ['1_galeria_poses.png', '3_caminhada.png', '4_encaixe.png'],
  },
  {
    id: 'saco',
    nome: 'Saco de batata',
    grupo: 'Objetos',
    arquivo: 'biblioteca/objetos/saco.js',
    estado: 'rascunho (apoio do teste de encaixe)',
    testes: [{ nome: 'No encaixe', cena: '/catalogo/cenas/nico_encaixe.js', duracao: 7.6 }],
  },
  {
    id: 'caixote',
    nome: 'Caixote',
    grupo: 'Objetos',
    arquivo: 'biblioteca/objetos/caixote.js',
    estado: 'rascunho (apoio do teste de encaixe)',
    testes: [{ nome: 'No encaixe', cena: '/catalogo/cenas/nico_encaixe.js', duracao: 7.6 }],
  },
  {
    id: 'estudio',
    nome: 'Estúdio neutro (chão com grade 0,1 m)',
    grupo: 'Cenários',
    arquivo: 'biblioteca/cenarios/estudio.js',
    estado: 'ferramenta de catálogo',
    testes: [{ nome: 'Sonda WebGL', cena: '/catalogo/cenas/sonda_webgl.js', duracao: 2 }],
  },
];

export const POSES_GALERIA = [
  'idle', 'walk', 'run', 'surprise', 'cheer', 'tired', 'point', 'shrug', 'refuse', 'carry', 'offer', 'receive', 'reach',
];
