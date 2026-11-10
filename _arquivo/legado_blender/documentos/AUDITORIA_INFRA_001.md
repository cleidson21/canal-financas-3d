# Auditoria de recuperação — INFRA-001

Data de referência: 2026-11-05 (America/Bahia). Auditoria sem reconstruir animação ou alterar áudio aprovado.

## Evidência e limites

Não existe `.git` nesta raiz; `git status --short` retorna “not a git repository”. Portanto não há diff ou histórico Git para atribuir autoria. Nenhum repositório foi criado automaticamente. O inventário inicial `testes/infra_001/baseline.json` registra 247 arquivos anteriores, tamanhos, mtimes e SHA-256, excluindo bytecode e a própria pasta de evidências.

Foi localizada a sessão anterior `c7ee6611-5efb-4d9d-81f9-165eb9f4dec0` no histórico local do Antigravity. A janela observada é 2026-11-04 11:35–14:54, America/Bahia. As chamadas de ferramentas foram extraídas em `prior_tool_calls.json` e as escritas diretas em `prior_writes.json`; não se atribui autoria apenas por mtime. São evidências locais de operações e resultados, não uma aprovação artística.

## O que a missão interrompida efetivamente alterou/criou

- Moveu os antigos `roteiro.md` e `storyboard.md` para `episodios/EP001_dinheiro/legado/roteiro_piloto_15s_V3_1.md` e `storyboard_piloto_15s_V3_1.md` (operação 22).
- Criou as novas fontes do episódio integral: `episodios/EP001_dinheiro/roteiro.md`, `narracao.json` (26), `storyboard.md` (97); fontes atuais preservadas nesta missão.
- Criou `scripts/tts/gerar_ep001.py` (29), `scripts/legendas/timing_ep001.py` (37), `align_ep001.py` (77), `montar_ep001.py` (123), `scripts/legendas/__init__.py` vazio intencionalmente (41) e `testes/test_ep001_narracao.py` (137).
- Editou `align_ep001.py` para importar a raiz e decodificar com FFmpeg (104); editou agrupamento de cues em `montar_ep001.py` (132); corrigiu normalização textual do teste (142).
- Gerou `audio/narracoes/EP001/segmentos/EP001_S01_V1.wav` a `EP001_S08_V1.wav`, com respectivos `.wav.meta.json` (31,33,41). Os resultados atuais confirmam oito WAVs PCM e metadados Puck.
- Executou análise de pausas e ASR/alinhamento local; criou `episodios/EP001_dinheiro/legendas/_analise_pausas.json` e `_alinhamento_asr.json`.
- A montagem produziu `audio/narracoes/EP001/EP001_NARRACAO_COMPLETA_V1.wav`, `episodios/EP001_dinheiro/timing.json`, `legendas/EP001_LEGENDAS.srt` e `.ass` (123/134). Duração atual medida: 102,12 s; 49 cues.
- Criou `publicacao/METADADOS_PUBLICACAO.md` e `COMENTARIOS.md` (110), `backups/MANIFESTO_EP001_BASE_V3_1_1.json` (137) e `documentos/RELATORIO_NARRACAO_EP001.md` (145); editou o relatório e acrescentou a seção integral no `README.md` (147).
- Criou scripts de inspeção `scratch/peek.py`, `peek2.py`, `dumpw.py`, três imagens `peek_120.png`, `peek_300.png`, `peek_420.png` e `peek2.txt` (170,180,187). As inspeções abriram cenas existentes; não registraram salvamento sobre elas.
- Instalou `faster-whisper` no Python do sistema e baixou o modelo small na missão anterior. Nesta missão o ambiente global não foi atualizado.

As operações que falharam (por exemplo comandos PowerShell com quoting inválido e uma tentativa de heredoc estilo Bash) não são tratadas como alterações concluídas. Os logs também registram a tentativa de remover um log temporário de alinhamento na missão anterior; nenhuma remoção foi repetida nesta missão.

## Estado recuperado

A suíte existente `testes/test_ep001_narracao.py` passou nesta auditoria: texto da narração corresponde ao roteiro, oito WAVs coerentes com timing, 49 cues sem sobreposição, SRT/ASS coerentes e todos os 27 hashes do manifesto base iguais. A cobertura ASR histórica é verificada como dado existente; não foi tratada como nova audição humana.

Todos os `.py` em `scripts/` passaram em `ast.parse`. Não foi encontrado arquivo Python parcialmente escrito; o único arquivo vazio inventariado é o `__init__.py` intencional de legendas. Isso não certifica a semântica de toda função nem elimina a possibilidade de defeitos visuais nos `.blend`.

As cenas V2/V3/V3.1 e bibliotecas mantêm seus hashes históricos. Não existe evidência de animatic integral novo concluído; os últimos registros são leitura das APIs de finalização/render e inspeção dos planos antigos. A animação atual permanece no piloto. Ausência de novos arquivos não é usada como prova isolada: histórico e manifesto corroboram esse limite.

## Pendências e alterações ainda não aceitas

- Aprovação humana da narração original completa, pronúncia e sincronia permanece indicada como pendente no relatório anterior; a instrução atual de preservar a voz tem prioridade, sem regenerar nada.
- O storyboard integral e a nova temporização existem, mas dependem de validação visual contra o animatic que ainda será construído.
- Assets de pescador/peixe, lenha, leiteiro/ovos/farinha, fichas de pagamento e sinais de aceitação precisam ser implementados em versões novas. `objetos/fichas.blend` contém sinais históricos; não presumir fichas monetárias prontas.
- Faltam animatic integral, revisão visual, animação definitiva, render integral, muxing e exportações finais. Nenhum desses passos foi retomado nesta missão.
- `ARQUITETURA.md`, README inicial e `timing.json` da raiz descrevem o piloto; usar as fontes dentro do episódio para o integral, sem reescrever o histórico.

## Ferramentas

Python 3.12.10 disponível por `python.exe`; `py -0p` não encontra instalações registradas neste contexto. Blender detectado: 5.2.3 LTS, hash e13b728c6880. FFmpeg e FFprobe 4.4.1-Jellyfin são localizados pelo resolvedor já existente, mesmo fora de PATH. Hardware, Ollama e dependências locais: `testes/infra_001/environment.json` e relatório consolidado.

Nenhum AGENTS.md existia na raiz; foi criado para consolidar o contrato solicitado. A única alteração necessária em código anterior é o carregamento lazy dos exports em `scripts/tts/__init__.py`; o gerador Gemini e seus parâmetros permanecem preservados. `.gitignore` recebeu apenas os diretórios isolados novos.
