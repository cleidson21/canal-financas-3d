# Catálogo — índice de ativos

Abrir: `npm run catalogo` → http://localhost:5173/catalogo/
Auditoria do Nico (folhas de contato em `catalogo/folhas/`, ignoradas pelo git): `npm run auditoria:nico`
Capturar quadros de qualquer cena: `npm run captura -- --cena <arquivo.js> --t 0,1,2 [--folha]`

Estados: `rascunho` · `aguardando aprovação` · `[aprovado dd/mm]` (só o usuário marca).

## Personagens
| Ativo | Criação | Cenas de checagem | Estado |
|---|---|---|---|
| Nico | `biblioteca/personagens/nico/index.js` → `createNico(opts)` | `catalogo/cenas/nico_turntable.js`, `nico_galeria.js`, `nico_caminhada.js`, `nico_encaixe.js` | aguardando aprovação |
| Esqueleto bípede (base do Nico e do comerciante) | `biblioteca/personagens/bipede/rig.js`, `colisao.js` | via Nico | aguardando aprovação |

## Movimentos
| Ativo | Arquivo | Estado |
|---|---|---|
| Poses nomeadas (12 + `reach`) e expressões | `biblioteca/movimentos/poses.js` | aguardando aprovação |
| Locomoção: caminhar, correr (`createLocomotion`) e giro no lugar (`createTurn`); pé apoiado fixo por construção | `biblioteca/movimentos/locomocao.js` | aguardando aprovação |
| Gestos (respirar, piscar, recusar, comemorar, cansado, surpresa, apontar, dar de ombros, estender, receber, transição `pose`) | `biblioteca/movimentos/gestos.js` | aguardando aprovação |

## Objetos
| Ativo | Criação | Estado |
|---|---|---|
| Saco de batata | `biblioteca/objetos/saco.js` → `createSack()` | rascunho |
| Caixote | `biblioteca/objetos/caixote.js` → `createCrate()` | rascunho |

## EP001 — peças (todas `rascunho`, aguardando sua aprovação)
| Ativo | Arquivo | Como ver |
|---|---|---|
| Nico: opções `descalco`, `sapatoQuebrado`; socket `costas`; poses `exausto_com_carga`, `cambalear`, `carga_costas` | `personagens/nico/index.js`, `movimentos/poses.js`, `gestos.js` | `?painel=exausto\|cambalear\|quebrado` (e `&az=graus`, `&qtd=n`) em `cenas/pecas_nico_torre.js` |
| Cargueiro de madeira + alças de corda (mãos fechadas) | `objetos/cargueiro.js` | idem |
| Torre de mercadorias (`quantidade`, `altura`, `alturaMax` = 1,8 × Nico); assenta no cargueiro; peixe no alto, de perfil | `objetos/torre_mercadorias.js` | idem |
| Peixe, lenha, galão de leite, caixa de ovos, saco de farinha | `objetos/peixe.js`, `lenha.js`, `galao_leite.js`, `caixa_ovos.js`, `saco_farinha.js` | `cenas/pecas_objetos.js` |
| Contador DIA (HUD, pop; `de` = nasce num ponto do mundo e desliza ~0,3 s) | `efeitos/contador_dia.js` | `cenas/pecas_rebobinar.js`, `cenas/pecas_cubo.js` |
| Rebobinar `createRewind({t0, duracao})` | `efeitos/rebobinar.js` | `cenas/pecas_rebobinar.js` |
| Cubo PLOC! | `efeitos/cubo_ploc.js` | `cenas/pecas_cubo.js` |
| Terraço baixo (fim de tarde) | `cenarios/terraco_baixo.js` | todas as cenas acima |
| Preset `frameNicoTorre` (plano médio com a torre inteira em 9:16) | `camera/presets.js` | cenas de carga |

Folha de contato: `node ferramentas/folha_pecas.mjs` → `catalogo/folhas/pecas_ep001.png`.
Medidas da carga no terminal (joelhos, cabeça–torre, pilha–costas, cubo, ícone): `node ferramentas/medir_carga.mjs`.

## Cenários e câmera
| Ativo | Arquivo | Estado |
|---|---|---|
| Estúdio neutro (grade 0,1 m) | `biblioteca/cenarios/estudio.js` | ferramenta |
| Presets de enquadramento | `biblioteca/camera/presets.js` → `frame()` | rascunho |

## Ferramentas
| Ferramenta | Arquivo |
|---|---|
| Captura de quadros (PNG) | `ferramentas/captura.mjs` |
| Folha de contato | `ferramentas/folha.mjs` |
| Auditoria do Nico (NICO_SPEC §7) | `ferramentas/auditoria_nico.mjs` |
| Folha das peças EP001 / medidas da carga | `ferramentas/folha_pecas.mjs`, `ferramentas/medir_carga.mjs` |
