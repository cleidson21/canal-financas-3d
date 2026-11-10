# Manual de Produção — Estúdio Nico 1.0

Comece pelo [catálogo do estúdio](ESTUDIO_NICO.md), pelo [índice do episódio](../episodios/EP001_dinheiro/00_ABRIR_EP001.md) e pelo [contrato de execução](../AGENTS.md). Consulte os arquivos necessários ao plano atual.

## Fluxo por episódio e plano

1. Ler o roteiro e storyboard canônicos e identificar a versão aprovada. Mudanças editoriais exigem autorização.
2. Reutilizar o narrador e os WAVs aprovados. A política atual está em [POLITICA_NARRACAO_E_COTAS.md](POLITICA_NARRACAO_E_COTAS.md). Uma nova geração exige autorização específica e os controles existentes de TTS.
3. Conferir o timing medido pelo áudio real no episódio. O `timing.json` da raiz pertence ao piloto.
4. Reutilizar personagens, mundo e objetos do catálogo. Projetar apenas a lacuna necessária e registrar seu estado de aprovação.
5. Preparar ou revisar a decupagem com ID, frase, tempos, quadros, câmera, personagens, deslocamentos, passos, braços/pernas, olhar, expressão, objetos, contatos, transferências e poses-chave.
6. Auditar o rig para a ação pretendida. Trabalhar numa cópia identificada dentro de `TESTES/`, com cache em `TESTES/cache/`. Recursos neutros aprovados podem ser promovidos às bibliotecas globais mediante decisão explícita.
7. Animar somente o intervalo autorizado, reaproveitando [motions.py](../scripts/producao/motions.py). As receitas `build_scene.py` e `build_ep001_v2.py` são específicas do EP001. Conferir todas as suas saídas antes de executá-las.
8. Usar [render_plan.py](../scripts/producao/render_plan.py) para quadro, intervalo ou lote de planos. Seguir os [comandos existentes](../scripts/producao/README.md#render-incremental-por-plano). Validar e inspecionar os quadros críticos antes da prévia contínua.
9. Aplicar os [critérios de qualidade](CRITERIOS_QUALIDADE.md) e obter a revisão humana. Registrar arquivo/hash, data, escopo e restrições no índice do episódio ou na entrada do ativo compartilhado.
10. Depois da autorização de finalização, compor o plano com o áudio aprovado, usando [audio_finalizer.py](../scripts/pipeline_v3/audio_finalizer.py), e conferir o áudio após muxing. As legendas devem seguir o áudio real.
11. Verificar MP4, duração, resolução, FPS, faixas e decodificação. Entregar versões com e sem legendas incorporadas quando o escopo exigir. Metadados editoriais ficam em `publicacao/`.
12. Atualizar o índice, preservar as fontes aprovadas e retirar apenas caches comprovadamente regeneráveis. Publicação requer instrução específica.

## Prompts do fluxo

[P01 Cenário](prompts/P01_PROJETAR_CENARIO_V1.md) → [P02 Personagem](prompts/P02_CONSTRUIR_PERSONAGEM_V1.md), quando houver lacunas → [P03 Direção](prompts/P03_DIRIGIR_CENA_V1.md) → [P04 Animação](prompts/P04_ANIMAR_PLANO_V1.md) → [P05 Auditoria](prompts/P05_AUDITAR_ANIMACAO_V1.md) → [P06 Finalização](prompts/P06_FINALIZAR_PLANO_V1.md).

Os templates são instruções para uma missão delimitada. Preencher entradas e autorizações antes de executar. As condições de parada limitam cada etapa.

## Execução e ambiente

Usar os ambientes isolados já disponíveis, Blender em processo dedicado com `--factory-startup --disable-autoexec --offline-mode`, e saída nova conferida antes do comando. Resolução de raiz em [pipeline_v3/config.py](../scripts/pipeline_v3/config.py). Auditar RAM/VRAM e tempo quando a execução exigir recursos relevantes. Evitar repetir render sem alteração pertinente.

O perfil atual está em [narrador_principal.json](../audio/perfis/narrador_principal.json). O TTS-003 aprovou a Puck e o áudio EP001 existente. Os motores locais anteriores foram rejeitados. O [relatório TTS-003](RELATORIO_TTS_003.md) documenta essa decisão. [GUIA_DE_PRODUCAO.md](GUIA_DE_PRODUCAO.md) e [ARQUITETURA.md](ARQUITETURA.md) conservam procedimentos do piloto e devem ser lidos nesse contexto.

Para versionamento, seguir a [preparação Git](VERSIONAMENTO.md). A passagem para uma nova máquina exige validar dependências e ambiente antes de certificar a reprodução.
