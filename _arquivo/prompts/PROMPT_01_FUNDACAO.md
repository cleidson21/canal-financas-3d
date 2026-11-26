# Prompt 01 — Fundação do Estúdio Nico

Colar no Antigravity, na raiz do repositório `canal-financas-3d`. Antes, coloque na raiz os arquivos `AGENTS.md` (substituindo o atual) e `NICO_SPEC.md`.
Duas sessões separadas. Não misture.

---

## SESSÃO A — Fundação e Nico (modelo e esforço: ver recomendação no chat)

Você vai reestruturar este repositório do zero. Leia SOMENTE `AGENTS.md` e `NICO_SPEC.md`. Não leia nada dentro de documentos antigos, testes ou scripts além do que esta tarefa citar.

**Fase 0 — Arquivar (sem apagar nada)**
1. Crie `_arquivo/legado_blender/` e mova para lá, com `git mv`, tudo o que existe hoje, EXCETO:
   - `AGENTS.md`, `NICO_SPEC.md`, `.gitignore`, `.gitattributes`, `.vscode/`;
   - `episodios/EP001_dinheiro/roteiro.md`, `storyboard.md`, `narracao.json` e a pasta `publicacao/`;
   - `scripts/legendas/` (mova para `_arquivo/` depois de copiar o que for útil para `ferramentas/` na etapa 2; por ora deixe onde está);
   - `audio/narracoes/EP001/` (não toque nos arquivos de áudio).
2. Não abra, leia nem execute nada do legado. Comite com a mensagem `arquivar legado`.

**Fase 1 — Esqueleto e ferramentas**
1. Verifique Node LTS, ffmpeg e Chromium para Playwright. Diga o que falta e quanto pesa antes de instalar.
2. Crie a estrutura de pastas do `AGENTS.md` (seção 4), `package.json` com Three.js e Vite em versão fixa, e `CHANGELOG.md`.
3. Crie `valores/tokens.json` com as cores, a escala e as metas de ritmo, usando os valores do `NICO_SPEC.md`.
4. Crie a ferramenta de captura em `ferramentas/`: abre uma página, chama `renderFrame(t)` para os instantes pedidos e salva PNGs; e uma opção que junta PNGs em folha de contato. Descubra como capturar WebGL em modo headless na minha máquina (se não houver GPU, use o modo de software do Chromium e me diga o tempo por quadro).

**Fase 2 — Nico**
Construa `biblioteca/personagens/nico` conforme o `NICO_SPEC.md` (segmentos rígidos, sem skinning, sockets, limites de junta, API determinística). Construa também a página `catalogo/` com turntable e a galeria de poses.

**Fase 3 — Auditoria**
Execute os 6 critérios de aceitação da seção 7 do `NICO_SPEC.md`. Gere as folhas de contato. Liste cada falha, com o quadro em que aparece, sem maquiar. Corrija o que for corrigível em até 3 iterações e declare o que restou.

**Parada.** Responda em até 15 linhas: o que foi criado, como abrir o catálogo, falhas restantes, horas ou iterações gastas e a cota consumida, se visível. Não escreva relatórios em arquivo.

---

## SESSÃO B — Teste de fundação (rodar em sessão nova, com outro modelo)

Leia SOMENTE `AGENTS.md`, `catalogo/INDEX.md` e a pasta `biblioteca/`. Use apenas ativos existentes; se faltar algo, liste o que falta antes de criar.

Construa a cena de teste `episodios/TESTE_FUNDACAO/` com 8 a 10 segundos:
1. Plano aberto: Nico entra na vila costeira (terraço médio), caminhando.
2. Corte: Nico bate com uma batata no balcão da barraca do sapateiro. PLOC! no objeto.
3. Rótulo e X vermelho com pop sobre a batata.
4. Corte de câmera com movimento (whip pan ou dolly) para a barraca de peixe.
Dois cortes, um efeito de partículas, um rótulo, nenhum erro de articulação.

Siga o fluxo do `AGENTS.md` (decupagem, bloqueio, animação, polimento), com folha de contato e parada em cada etapa, e exporte um MP4 1080×1920 a 30 fps.

**Parada.** Responda em até 12 linhas: tempo gasto, número de iterações, quadros com erro visível e tempo de renderização por segundo de vídeo.

---

## Como julgar o resultado (por mim, não pelo agente)
- Os 3 primeiros segundos prendem?
- Há erro de articulação visível em movimento?
- O teste da Sessão B foi feito só com a biblioteca, sem reinventar peças?
- Quantas horas e quanta cota foram necessárias?
