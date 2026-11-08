# Arquitetura do Repositório e Pipeline Escalável (V3)

Este documento descreve a arquitetura histórica V3 e o piloto. A navegação e as fontes vigentes do estúdio estão em [ESTUDIO_NICO.md](ESTUDIO_NICO.md) e [PIPELINE_PRODUCAO.md](PIPELINE_PRODUCAO.md).


## 1. Visão Geral da Nova Estrutura de Diretórios

Na **Versão 3 (V3)**, o projeto do canal 3D de educação financeira com o protagonista **Nico** foi migrado de uma estrutura plana na raiz para uma arquitetura modular orientada a episódios e bibliotecas reutilizáveis de *assets* (`.blend`):

```text
canal-financas-3d/
├── README.md                                  # Guia rápido de uso, visão geral e comandos CLI
├── .gitignore                                 # Regras para ignorar temporários (.blend1, __pycache__)
├── backups/
│   └── legado/                                # Preservação integral e auditada (SHA-256) da V1 e V2
│       ├── MANIFESTO_MIGRACAO.json            # Manifesto criptográfico SHA-256 dos 28 arquivos migrados
│       ├── Teste1.blend                       # Cena original V1 intacta
│       ├── Teste1_V2.blend                    # Cena original V2 intacta
│       ├── preview_15s.mp4                    # Render MP4 original da V2 intacto
│       ├── build_scene_v2.py                  # Script original da V2 intacto
│       ├── kit_nico_blender/                  # Kit procedural inicial V1
│       ├── pipeline_v2/                       # Pacote modular da V2
│       └── previews/                          # Stills e vídeo low-res originais da V2
├── personagens/
│   └── nico_base.blend                        # Biblioteca reutilizável do protagonista Nico V3 + Armature
├── cenarios/
│   ├── feira.blend                            # Biblioteca reutilizável da barraca de sapatos + carrinho
│   └── vila.blend                             # Biblioteca reutilizável do terreno, caminho de pedras e vila
├── objetos/
│   ├── batatas.blend                          # Saco de batatas de 40 kg em estopa com batatas visíveis
│   ├── sapatos.blend                          # Par de tênis novos (vermelho/ouro) em pedestal expositor
│   └── fichas.blend                           # Sinais gráficos 3D (Placa X Vermelho + Placa Grande de Leite)
├── episodios/
│   └── EP001_dinheiro/                        # Episódio 001: O Problema da Dupla Coincidência de Desejos
│       ├── roteiro.md                         # Roteiro narrativo de 15 segundos (7 planos)
│       ├── storyboard.md                      # Storyboard técnico quadro a quadro (30 FPS / 450 frames)
│       ├── cenas/
│       │   ├── cena_01_V2.blend               # Cópia funcional da cena V2
│       │   └── cena_01_V3.blend               # Cena principal V3 completa e pronta para render
│       ├── previews/
│       │   ├── comparativo_V2_vs_V3.png       # Prancha comparativa lado a lado (8 momentos V2 × V3)
│       │   ├── v2/                            # Stills da V2 para comparação histórica
│       │   └── v3/
│       │       ├── auditoria/                 # 7 frames obrigatórios da Seção 17 (0.5s a 14.5s)
│       │       ├── closeups/                  # 4 close-ups dedicados (sapato frontal/perfil, rosto, corpo)
│       │       └── aberturas/                 # Stills comparativos das Aberturas A e B
│       ├── renders/                           # Diretório para sequências de frames finais
│       └── videos/
│           ├── abertura_A_3s.mp4              # Teste de Abertura A (Close-up do sapato abrindo primeiro)
│           ├── abertura_B_3s.mp4              # Teste de Abertura B (Plano aberto do tropeço primeiro)
│           ├── preview_15s_V2.mp4             # Vídeo 15s da V2 preservado
│           ├── preview_15s_V3_lowres.mp4      # Preview rápido 15s da V3
│           └── preview_15s_V3.mp4             # Render final 15s da V3 (1080×1920, 30 FPS, H.264)
├── referencias/
│   ├── videos/                                # Vídeos de referência analisados (Banco.mp4, videoplayback*.mp4)
│   └── imagens/                               # Pranchas de frames extraídos dos vídeos de referência
├── scripts/
│   ├── build_scene.py                         # Orquestrador principal da V3 (CLI e aba Scripting)
│   ├── montar_cena.py                         # Ponto de entrada modular para montagem de cenário/personagens
│   ├── animar_objetos.py                      # Ponto de entrada modular para animação de personagens/props
│   ├── configurar_camera.py                   # Ponto de entrada modular para direção de câmera 9:16
│   ├── build_scene_v2.py                      # Orquestrador legado da V2 atualizado com pathlib.Path
│   ├── pipeline_v2/                           # Pacote legado da V2
│   └── pipeline_v3/                           # Pacote principal da Arquitetura V3
│       ├── __init__.py
│       ├── config.py                          # Constantes, caminhos pathlib, beats e paleta Scene-Linear
│       ├── scene_setup.py                     # Limpeza idempotente, coleções e configuração EEVEE
│       ├── primitives.py                      # Primitivas BMesh chanfradas, subdivididas e com UV
│       ├── materials_lighting.py              # Biblioteca Principled BSDF 4.0+ e iluminação de 4 pontos
│       ├── character_nico.py                  # Nico V3 com Armature contínua e tênis reconstruído
│       ├── environment_fair.py                # Vila, caminho de pedras, carrinho de mão e barraca V3
│       ├── anim_props.py                      # Animação do saco 40 kg (carrinho -> balcão 'PLOC!') e placas
│       ├── anim_character.py                  # Walk cycle com peso, expressões faciais e atuação do Nico
│       ├── cinematography.py                  # Direção de 7 planos verticais 9:16 + suporte Abertura A/B
│       ├── asset_library.py                   # Gerador automatizado das 6 bibliotecas .blend reutilizáveis
│       └── render_pipeline.py                 # Renderização de stills, close-ups, MP4 e prancha V2×V3
├── documentos/
│   ├── ARQUITETURA.md                         # Este documento
│   ├── BIBLIA_VISUAL.md                       # Diretrizes visuais, proporções do Nico V3 e paleta
│   ├── GUIA_DE_PRODUCAO.md                    # Passo a passo para criar novos episódios (EP002+)
│   ├── RELATORIO_V2.md                        # Relatório técnico histórico da V2
│   └── RELATORIO_V3.md                        # Relatório técnico completo da Missão V3
└── testes/
    ├── migrar_estrutura.py                    # Script de migração em 2 estágios com verificação SHA-256
    └── test_pipeline_v3.py                    # Suíte automatizada de testes técnicos no Blender headless
```

---

## 2. Convenções de Nomenclatura

### 2.1. Coleções do Blender (`bpy.data.collections`)
Todas as cenas de episódios e bibliotecas seguem a taxonomia padronizada de 5 coleções:
1. `Col_Cenario_Vila` — Terreno, colinas, caminho de terra, pedras de piso, árvores, arbustos, casas distantes e nuvens.
2. `Col_Feira_Barraca` — Barraca do sapateiro, balcão em ripas, prateleiras traseiras, caixas de estoque, toldo listrado, par de sapatos novos no expositor, vendedor e carrinho de mão de madeira (`Carrinho_Batatas_Root`).
3. `Col_Personagem_Nico` — Protagonista Nico V3 (`Nico_Root`, `Nico_Armature_V3`, malhas contínuas de braços e pernas, cabeça expressiva, boné azul e tênis direito com sola frontal articulada `Nico_Tenis_SolaFrontal_R`).
4. `Col_Props_Animados` — Objetos com animação narrativa própria (`Saco_Batatas_Root`, `Poeira_Impacto_1..6`, `Placa_Recusa_X_Root`, `Placa_Desejo_Leite_Root`).
5. `Col_Luzes_Cameras` — Sistema de iluminação de 4 pontos (`Sol_Principal`, `Luz_Preenchimento`, `Luz_Recorte_Rim`, `Luz_Destaque_Sapato`) e rigor de câmera (`Camera_Principal`, `Camera_Target`).

### 2.2. Materiais (`bpy.data.materials`)
- Todos os materiais utilizam o prefixo `Mat_` (ex.: `Mat_nico_skin`, `Mat_nico_shirt`, `Mat_burlap_sack`, `Mat_milk_blue`).
- As cores são definidas em **sRGB perceptual** em [`config.py`](file:///c:/Users/Cleidson/Videos/canal-financas-3d/scripts/pipeline_v3/config.py) e convertidas matematicamente para **Scene Linear** via `_srgb_to_linear()`, garantindo fidelidade cromática sob o gerenciamento de cor **AgX + Medium High Contrast** do Blender 5.2 LTS.

---

## 3. Resolução Portátil de Caminhos (`pathlib.Path`)

Nenhum módulo dentro de `scripts/pipeline_v3/` utiliza caminhos absolutos fixos de máquina (`C:\Users\...`). A raiz do repositório é resolvida dinamicamente em [`config.py`](file:///c:/Users/Cleidson/Videos/canal-financas-3d/scripts/pipeline_v3/config.py#L6-L11):

```python
def get_project_root() -> Path:
    here = Path(__file__).resolve()
    return here.parent.parent.parent
```

Ao salvar qualquer arquivo `.blend` em [`render_pipeline.py`](file:///c:/Users/Cleidson/Videos/canal-financas-3d/scripts/pipeline_v3/render_pipeline.py) ou [`asset_library.py`](file:///c:/Users/Cleidson/Videos/canal-financas-3d/scripts/pipeline_v3/asset_library.py), é utilizado `bpy.ops.wm.save_as_mainfile(..., relative_remap=True)`, garantindo portabilidade entre máquinas.

---

## 4. Como Reaproveitar as Bibliotecas `.blend` em Novos Episódios

Os ativos em `personagens/`, `cenarios/` e `objetos/` são gerados automaticamente por [`asset_library.py`](file:///c:/Users/Cleidson/Videos/canal-financas-3d/scripts/pipeline_v3/asset_library.py) e podem ser:
1. **Anexados (`Append`) ou Vinculados (`Link`)** manualmente no Blender (`File > Append / Link`) selecionando a coleção correspondente (ex.: `personagens/nico_base.blend > Collection > Col_Personagem_Nico`).
2. **Instanciados via Script Python** importando os construtores parametrizados de `pipeline_v3` (`character_nico.build_character_nico`, `environment_fair.build_village_and_fair`, `anim_props.build_potato_sack_geometry`), o que permite customizar poses, expressões e keyframes para cada novo episódio.

