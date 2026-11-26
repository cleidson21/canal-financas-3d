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
    id: 'ep001_nico',
    nome: 'Nico: descalço, sola solta, carga nas costas',
    grupo: 'Personagens',
    arquivo: 'biblioteca/personagens/nico/index.js (opções descalco, sapatoQuebrado; socket costas)',
    estado: 'rascunho (EP001)',
    testes: [
      { nome: 'Exausto com carga + torre 6', cena: '/catalogo/cenas/pecas_nico_torre.js', duracao: 5, params: { painel: 'exausto' } },
      { nome: 'Cambalear + torre 3', cena: '/catalogo/cenas/pecas_nico_torre.js', duracao: 5, params: { painel: 'cambalear' } },
      { nome: 'Sapato quebrado + torre 1', cena: '/catalogo/cenas/pecas_nico_torre.js', duracao: 5, params: { painel: 'quebrado' } },
    ],
  },
  {
    id: 'ep001_objetos',
    nome: 'Torre e objetos (peixe, lenha, galão, ovos, farinha)',
    grupo: 'Objetos',
    arquivo: 'biblioteca/objetos/cargueiro.js, torre_mercadorias.js, peixe.js, lenha.js, galao_leite.js, caixa_ovos.js, saco_farinha.js',
    estado: 'rascunho (EP001)',
    testes: [{ nome: 'Roda de objetos', cena: '/catalogo/cenas/pecas_objetos.js', duracao: 10 }],
  },
  {
    id: 'ep001_efeitos',
    nome: 'Contador DIA, rebobinar, cubo PLOC!',
    grupo: 'Efeitos',
    arquivo: 'biblioteca/efeitos/contador_dia.js, rebobinar.js, cubo_ploc.js',
    estado: 'rascunho (EP001)',
    testes: [
      { nome: 'Rebobinar + contador', cena: '/catalogo/cenas/pecas_rebobinar.js', duracao: 5 },
      { nome: 'Cubo PLOC! → contador', cena: '/catalogo/cenas/pecas_cubo.js', duracao: 4 },
    ],
  },
  {
    id: 'terraco_baixo',
    nome: 'Terraço baixo (fim de tarde)',
    grupo: 'Cenários',
    arquivo: 'biblioteca/cenarios/terraco_baixo.js',
    estado: 'rascunho (EP001)',
    testes: [{ nome: 'Roda de objetos no terraço', cena: '/catalogo/cenas/pecas_objetos.js', duracao: 10 }],
  },  {
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
