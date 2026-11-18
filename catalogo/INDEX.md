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
