# P06_FINALIZAR_PLANO — v1.0

Template do Estúdio Nico. Preencher os campos entre colchetes antes da execução. Campos essenciais ausentes devem ser resolvidos antes da operação dependente.

Leia `AGENTS.md`, `documentos/ESTUDIO_NICO.md`, o índice de [EPISODIO] e os documentos relacionados ao pedido. Consulte outros arquivos apenas por dependência identificada. Trabalhe no projeto atual, com saídas novas em `episodios/[EPISODIO]/TESTES/` e temporários no cache desse diretório. Preserve roteiro, áudio, bibliotecas e entregas aprovadas. Use os motores existentes. APIs, downloads, geração de voz, publicação e render integral exigem autorização específica. Registre aprovação técnica e decisão humana com seus escopos.

Finalizar [ID_PLANO_OU_MONTAGEM] de [EPISODIO] para revisão em [NOVOS_CAMINHOS_DE_SAIDA].

## Entradas

Decisão de aprovação com escopo, projeto e quadros verificados, assinatura do cache, WAV aprovado, timing, legendas ativas e formatos de entrega solicitados. Conferir dependências e nomes livres antes de executar.

## Saídas

MP4 validado, versões com e sem legendas incorporadas quando solicitadas, projeto editável identificável e índice atualizado com status e hashes.

## Restrições

Usar os recursos existentes de FFmpeg e `audio_finalizer.py`. A montagem `finalize_ep001_v2.py` é específica do EP001 integral e só deve ser executada se esse for o escopo autorizado. Preservar áudio, velocidade, tom e áreas seguras. Metadados editoriais permanecem separados do vídeo.

## Aprovação

Verificar assinatura e integridade dos quadros escolhidos, duração, FPS, resolução, faixa de áudio, correlação/defasagem após muxing e decodificação integral. Conferir palavras e legibilidade das legendas no exportado. Registrar revisão humana da entrega final.

## Parada

Parar após entregar os arquivos e atualizar o índice. A publicação exige uma instrução própria.
