# Estúdio Nico 1.0

Entrada operacional do estúdio. Para produzir um plano, comece pelo [manual](PIPELINE_PRODUCAO.md). Para localizar uma entrega, abra o [EP001](../episodios/EP001_dinheiro/00_ABRIR_EP001.md).

A classificação abaixo descreve o escopo de uso. APROVADO identifica uma referência já estabelecida pelo contrato do projeto ou uma decisão humana explícita. EXPERIMENTAL identifica código, provas e candidatos que exigem validação no uso pretendido. HISTÓRICO identifica versões substituídas. AUSENTE identifica uma capacidade ou decisão ainda sem implementação ou registro. Arquivo existente e teste técnico aprovado, por si, não conferem aprovação artística.

## Recursos e fontes de verdade

- **Nico — APROVADO como referência de aparência.** [nico_base.blend](../personagens/nico_base.blend), regido pela [Bíblia Visual e dos Personagens](BIBLIA_VISUAL.md). O construtor reutilizável é [character_nico.py](../scripts/pipeline_v3/character_nico.py), função `build_character_nico`. Alterar o construtor exige gerar e revisar uma nova versão da biblioteca.
- **Rig e controladores — EXPERIMENTAL para novas ações.** A mesma biblioteca contém a armature V3. [motions.py](../scripts/producao/motions.py) resolve os controles Empty seguidos pelos ossos. A prova de punho e polegar está em [ANIM004_RIG_V3.blend](../episodios/EP001_dinheiro/TESTES/ANIM004_RIG_V3.blend). O código atual também contém `set_nico_grip`. Essa função e a prova de punho têm hierarquias distintas e exigem conferência antes da reutilização.
- **Comerciantes — EXPERIMENTAL.** A definição procedural está em [assets.py](../scripts/producao/assets.py), `merchant` e `THEMES`. [comerciantes_EP001_V2.blend](../personagens/comerciantes_EP001_V2.blend) é a biblioteca mais recente identificada. [comerciantes_PROD002_V2.blend](../personagens/comerciantes_PROD002_V2.blend) permanece referência da prova S03. Aprovação artística individual dos papéis está pendente.
- **Movimentos — EXPERIMENTAL, reutilizáveis com teste de rig.** [Catálogo](CATALOGO_MOVIMENTOS.md) e [motions.py](../scripts/producao/motions.py). As curvas gravadas em cada projeto são a execução daquele plano. A coreografia de `build_scene.py` e `build_ep001_v2.py` é específica do EP001.
- **Vila — APROVADO como cenário base de referência.** [vila.blend](../cenarios/vila.blend) e a geografia procedural de [environment_fair.py](../scripts/pipeline_v3/environment_fair.py), `build_village_and_fair`. Ampliações e posições das barracas na montagem EP001-V2 são EXPERIMENTAIS e estão no construtor do episódio. Consulte a [Bíblia do Mundo](BIBLIA_MUNDO.md).
- **Feira e barracas.** [feira.blend](../cenarios/feira.blend) é a referência base APROVADA para preservação. [barracas_EP001_V2.blend](../cenarios/barracas_EP001_V2.blend) e [barracas_PROD002_V2.blend](../cenarios/barracas_PROD002_V2.blend) são EXPERIMENTAIS. A construção reutilizável das variantes fica em `assets.stall`.
- **Objetos base — APROVADOS como referências protegidas.** [batatas.blend](../objetos/batatas.blend), [sapatos.blend](../objetos/sapatos.blend) e [fichas.blend](../objetos/fichas.blend). O último contém sinais gráficos de troca, com nome histórico. [Mercadorias EP001-V2](../objetos/mercadorias_EP001_V2.blend), [mercadorias PROD-002](../objetos/mercadorias_PROD002_V2.blend), [ficha de pagamento](../objetos/ficha_pagamento.blend) e [carimbo](../objetos/carimbo_duvida.blend) são EXPERIMENTAIS. O conteúdo exportado de `ficha_pagamento.blend` usa a coleção de objetos do episódio e precisa de inspeção antes de ser tratado como ativo neutro.
- **Materiais e cores.** A paleta de identidade APROVADA está na [Bíblia Visual](BIBLIA_VISUAL.md). Sua representação numérica em código é `config.PALETTE` em [config.py](../scripts/pipeline_v3/config.py), aplicada por [materials_lighting.py](../scripts/pipeline_v3/materials_lighting.py). As cores EXPERIMENTAIS dos comerciantes e mercadorias ficam em `assets.THEMES` e `assets.goods`. Os materiais salvos em uma biblioteca preservam a versão daquele ativo.
- **Câmeras — EXPERIMENTAIS como presets, formato vertical APROVADO.** [cameras.py](../scripts/producao/cameras.py) contém `PRESETS` e `shot`. A câmera efetivamente salva no plano registra sua execução. [Linguagem de Câmera](LINGUAGEM_CAMERA.md) define o uso sem duplicar os parâmetros.
- **Iluminação — APROVADA como direção visual, EXPERIMENTAL na adaptação a novos planos.** `setup_world_and_lighting` em [materials_lighting.py](../scripts/pipeline_v3/materials_lighting.py) implementa a luz da Bíblia Visual. Validar silhueta e legibilidade a cada enquadramento.
- **Renderização — EXPERIMENTAL com validação técnica existente.** [render_plan.py](../scripts/producao/render_plan.py) é o ponto de entrada por plano ou lote, com cache por assinatura e checksum. [README da produção](../scripts/producao/README.md) contém os comandos. `render_scene.py` é HISTÓRICO e seu ponto de entrada está desativado.
- **Montagem e áudio.** A Puck e seus WAVs são APROVADOS conforme o contrato TTS-003, em [audio/narracoes/EP001](../audio/narracoes/EP001/) e [narrador_principal.json](../audio/perfis/narrador_principal.json). [audio_finalizer.py](../scripts/pipeline_v3/audio_finalizer.py) é reutilizável para muxing e verificação. `finalize_ep001_v2.py` é EXPERIMENTAL e específico da montagem integral EP001-V2. Uma montagem genérica de transições permanece AUSENTE.
- **Histórico — HISTÓRICO.** Pilotos, checkpoints e evidências estão em [arquivo/EP001](../arquivo/EP001/). A duração de 15 s em `pipeline_v3/config.py` e a atuação em `anim_character.py` pertencem ao piloto. Os construtores atuais ainda dependem de um [projeto-fonte do piloto](../arquivo/EP001/piloto/cenas/cena_01_V3_1.blend). Essa dependência deve ser mantida no pacote de reprodução.

## Autoridade editorial e aprovação

- Roteiro, storyboard e timing pertencem ao episódio em [roteiro.md](../episodios/EP001_dinheiro/roteiro.md), [storyboard.md](../episodios/EP001_dinheiro/storyboard.md) e [timing.json](../episodios/EP001_dinheiro/timing.json).
- Para o master integral V2 existente, a especificação executável é [EP001_V2_DECUPAGEM.json](../episodios/EP001_dinheiro/TESTES/EP001_V2_DECUPAGEM.json). Para a prova PROD-002, os nove planos estão em [CENA03_DECUPAGEM.json](../episodios/EP001_dinheiro/TESTES/CENA03_DECUPAGEM.json). Os escopos devem acompanhar o projeto selecionado.
- O [índice do episódio](../episodios/EP001_dinheiro/00_ABRIR_EP001.md) é a fonte operacional do estado de aprovação das entregas. Este catálogo controla a classificação dos recursos compartilhados. Uma promoção deve registrar arquivo, versão, SHA-256, escopo, decisão humana e sua data. Sem decisão identificável, permanece EXPERIMENTAL.
- Uma alteração de código não atualiza automaticamente a biblioteca salva. Divergência entre aparência, código e projeto exige revisão antes de promover uma nova referência.

## Documentos e prompts

- [Mundo](BIBLIA_MUNDO.md) · [Personagens e visual](BIBLIA_VISUAL.md) · [Câmera](LINGUAGEM_CAMERA.md)
- [Movimentos](CATALOGO_MOVIMENTOS.md) · [Transições](CATALOGO_TRANSICOES.md) · [Qualidade](CRITERIOS_QUALIDADE.md) · [Manual](PIPELINE_PRODUCAO.md)
- [P01 Projetar cenário](prompts/P01_PROJETAR_CENARIO_V1.md) · [P02 Construir personagem](prompts/P02_CONSTRUIR_PERSONAGEM_V1.md) · [P03 Dirigir cena](prompts/P03_DIRIGIR_CENA_V1.md)
- [P04 Animar plano](prompts/P04_ANIMAR_PLANO_V1.md) · [P05 Auditar animação](prompts/P05_AUDITAR_ANIMACAO_V1.md) · [P06 Finalizar plano](prompts/P06_FINALIZAR_PLANO_V1.md)
- [Versionamento privado e arquivos grandes](VERSIONAMENTO.md)

## Pendências priorizadas

- **P0.** Obter a revisão humana das entregas V2, das provas de pega e da aparência dos comerciantes. Resolver a precisão de alvos e contatos antes de promover movimentos. O relatório V2 registra revisão artística final pendente.
- **P0.** Confirmar acesso ao remoto privado e revisar a lista exata do primeiro commit, incluindo sigilo, licenças e dependências de reprodução.
- **P1.** Conferir se as bibliotecas base continuam equivalentes ao Nico e à vila usados no master V2. A P00 fez inspeção documental e estática, sem abrir os projetos no Blender.
- **P1.** Validar o conteúdo neutro da ficha de pagamento e separar, numa missão autorizada, receitas específicas do EP001 das capacidades realmente genéricas.
- **P1.** Documentar ambiente mínimo reproduzível e recuperar apenas os arquivos históricos exigidos pelos testes escolhidos. Inicialização Git e clone funcional ainda precisam de validação.
- **P2.** Preencher mapa geográfico editorial, fichas dos comerciantes e catálogo de movimentos com novas aprovações. Avaliar transições adicionais somente quando houver necessidade narrativa.

Preparação P00 em 2026-11-07. Nenhuma aprovação artística nova foi atribuída.
