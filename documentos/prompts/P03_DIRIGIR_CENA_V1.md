# P03_DIRIGIR_CENA — v1.0

Template do Estúdio Nico. Preencher os campos entre colchetes antes da execução. Campos essenciais ausentes devem ser resolvidos antes da operação dependente.

Leia `AGENTS.md`, `documentos/ESTUDIO_NICO.md`, o índice de [EPISODIO] e os documentos relacionados ao pedido. Consulte outros arquivos apenas por dependência identificada. Trabalhe no projeto atual, com saídas novas em `episodios/[EPISODIO]/TESTES/` e temporários no cache desse diretório. Preserve roteiro, áudio, bibliotecas e entregas aprovadas. Use os motores existentes. APIs, downloads, geração de voz, publicação e render integral exigem autorização específica. Registre aprovação técnica e decisão humana com seus escopos.

Preparar a direção técnica de [CENA] de [EPISODIO] em [ARQUIVO_DE_DECUPAGEM].

## Entradas

Roteiro/storyboard aprovados, WAV e timing oficiais, projeto-fonte [CAMINHO_E_VERSAO], atores, objetos e recursos do catálogo. Selecionar explicitamente a entrega de referência.

## Saídas

Decupagem JSON ligada ao áudio real. Cada plano deve conter `id`, `frames` inclusivos, `camera`, `audit_frames`, frase, tempos, quantidade de quadros, atores, posições inicial/final, passos, membros, olhar, expressão, objetos, contatos/transferências, cenário, poses-chave e critérios de validação.

Para uso no renderizador atual, declarar `blend`, `cache`, `render.resolution`, `render.samples` e `plans`. Nomear câmeras realmente existentes ou marcar sua criação como pendência antes da execução. Não preencher alvos espaciais desconhecidos com números inventados.

## Restrições

Complementar o roteiro. Preservar fala, ordem editorial e duração oficial. Identificar coreografia proposta e referência já executável. Não executar os construtores integrais do EP001 como efeito da decupagem.

## Aprovação

Validar IDs, tempos, faixas, ausência de lacunas/sobreposição não intencional, duração, continuidade, contato e intenção de câmera. Obter revisão da direção.

## Parada

Parar na decupagem e em sua validação estática. A animação pertence ao escopo de um plano autorizado.
