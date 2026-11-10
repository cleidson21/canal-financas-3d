# Relatório de Sincronização Audiovisual — MISSÃO V3.1 (Primeira Montagem Narrada do Nico)

## 1. Resumo Executivo e Escopo

A **MISSÃO V3.1** integra a narração de trabalho gerada pelo Gemini TTS (`audio/narracoes/EP001/testes/narracao_B_flash_lite_V1.wav`, **18,72 segundos**) à animação 3D do **Blender 5.2 LTS** construída na V3 (`episodios/EP001_dinheiro/cenas/cena_01_V3.blend`), produzindo uma montagem audiovisual sincronizada em baixa resolução (`540×960`, 50% de `1080×1920`, `30 FPS`) para avaliação humana antes da renderização Full HD.

### Garantias de Preservação e Restrições Cumpridas
- **Zero reconstrução de modelagem:** O personagem Nico, o sapateiro, a vila, a barraca, os materiais e a iluminação foram preservados integralmente a partir de `cena_01_V3.blend`, alterando exclusivamente os *keyframes* de animação, cortes de câmera, o selo contextual da Frase 2 e a faixa de áudio no VSE.
- **Preservação integral dos arquivos originais:** `cena_01_V3.blend`, `narracao_B_flash_lite_V1.wav`, `scripts/pipeline_v3/` e `scripts/tts/` permanecem intactos.
- **Zero chamadas à API Gemini TTS:** Nenhuma requisição externa foi realizada nesta missão.
- **Status da voz:** A narração `narracao_B_flash_lite_V1.wav` é tratada estritamente como **narração de trabalho** (`approved: false`), sem alteração de velocidade (*time-stretch*) ou tom (*pitch*), e **não é declarada aprovada emocionalmente pelo usuário**.

---

## 2. Análise Acústica da Narração (`timing.json`)

O arquivo `audio/narracoes/EP001/testes/narracao_B_flash_lite_V1.wav` possui as seguintes especificações técnicas verificadas:
- **Taxa de amostragem:** `24.000 Hz`, Mono (`1 canal`), PCM `16-bit`
- **Total de amostras:** `449.280 amostras` (`18,720 segundos` exatos)
- **Correspondência em quadros (30 FPS):** `561,6 quadros` (`frames 1–562`), acrescidos de `0,48s` (`14 quadros`) de sustentação visual (*visual tail hold*) da reação final do Nico, totalizando **`19,20 segundos` (`576 quadros`)**.

### 2.1. Tabela de Tempos Reais das 6 Frases (`timing.json`)

| ID | Frase da Narração | Início (s) | Fim (s) | Duração (s) | Quadros (30 FPS) | Pico Acústico | Sub-segmentos / Pausas Internas |
| :-: | :--- | :-: | :-: | :-: | :-: | :-: | :--- |
| **1** | *"O sapato do Nico pediu demissão."* | `0,41s` | `2,82s` | `2,41s` | `12 – 85` (`73f`) | `0,89s` (`f27`) | `"O sapato"` (`0,41–0,76s` / `f12–23`) · `"do Nico"` (`0,88–1,73s` / `f26–52`) · `"pediu demissão."` (`1,92–2,82s` / `f58–85`) |
| **2** | *"E na vila dele, ninguém usava dinheiro."* | `3,54s` | `5,70s` | `2,16s` | `106 – 171` (`65f`) | `4,85s` (`f146`) | `"E na vila dele,"` (`3,54–4,58s` / `f106–137`) · `"ninguém usava dinheiro."` (`4,58–5,70s` / `f137–171`) |
| **3** | *"Ele tinha um saco de batatas e achou que dava pra trocar por um par novo."* | `6,30s` | `10,54s` | `4,24s` | `189 – 316` (`127f`) | `8,65s` (`f260`) | `"Ele tinha um saco de batatas"` (`6,30–7,92s` / `f189–238`) · `"e achou que dava pra trocar"` (`7,98–9,69s` / `f239–291`) · `"por um par novo."` (`9,77–10,54s` / `f293–316`) |
| **4** | *"Só que o sapateiro não queria batatas."* | `11,08s` | `13,77s` | `2,69s` | `332 – 413` (`81f`) | `13,07s` (`f392`) | `"Só que o sapateiro"` (`11,08–12,21s` / `f332–366`) · pausa (`12,21–12,44s`) · `"não queria batatas."` (`12,44–13,77s` / `f373–413`) |
| **5** | *"Queria leite."* | `14,41s` | `15,44s` | `1,03s` | `432 – 463` (`31f`) | `15,04s` (`f451`) | `"Queria leite."` (`14,41–15,44s` / `f432–463`) |
| **6** | *"Nico... aí complicou."* | `16,15s` | `18,05s` | `1,90s` | `484 – 542` (`58f`) | `16,42s` (`f493`) | `"Nico..."` (`16,15–16,83s` / `f484–505`) · reticências `"..."` (`16,83–17,20s` / `f505–516`) · `"aí complicou."` (`17,20–18,05s` / `f516–542`) |

### 2.2. Intervalos de Silêncio e Transições Visuais

| Intervalo | Início (s) | Fim (s) | Duração (s) | Quadros (30 FPS) | Função Narrativa / Visual |
| :--- | :-: | :-: | :-: | :-: | :--- |
| **Silêncio Inicial** | `0,00s` | `0,41s` | `0,41s` | `1 – 12` | *Cold open* já em movimento: câmera em close-up acompanha o início do passo do tênis direito. |
| **Pausa 1 → 2** | `2,82s` | `3,54s` | `0,72s` | `85 – 106` | Nico recupera o equilíbrio após o tropeço (`f85–99`) e corte seco no `f100` (`3,33s`) para o plano geral da vila e feira. |
| **Pausa 2 → 3** | `5,70s` | `6,30s` | `0,60s` | `171 – 189` | Leitura visual do selo `"Sem Dinheiro"` e corte no `f187` (`6,23s`) para o plano médio do Nico ao lado do carrinho com as batatas. |
| **Pausa 3 → 4** | `10,54s` | `11,08s` | `0,54s` | `316 – 332` | Nico sustenta o gesto confiante apontando do saco de batatas no balcão para o par de sapatos novos antes da reação do sapateiro. |
| **Pausa 4 → 5** | `13,77s` | `14,41s` | `0,64s` | `413 – 432` | Impacto visual do **X Vermelho** sobre as batatas antes do corte de ênfase (`f432`) para a placa grande do **Leite**. |
| **Pausa 5 → 6** | `15,44s` | `16,15s` | `0,71s` | `463 – 484` | Leitura clara do ícone do Leite (`f463–479`) e corte no `f480` (`16,00s`) para o *Medium Close-Up* da reação do Nico. |
| **Silêncio Final WAV + Hold** | `18,05s` | `19,20s` | `1,15s` | `542 – 576` | Sustentação cômica final (*shrug* frustrado do Nico + saco de batatas rejeitado) para que o corte final não seja abrupto. |

Visualização gerada do alinhamento de *waveform* e envelope RMS:
- `episodios/EP001_dinheiro/previews/v3_1/waveform_timing_v3_1.png`

---

## 3. Mapa de Direção de Câmera e Ação Sincronizada (7 Planos)

| Plano | Quadros | Tempo (s) | Frase Associada | Ação Visual e Enquadramento 9:16 | Still de Auditoria |
| :-: | :-: | :-: | :--- | :--- | :--- |
| **Shot 1** | `1 – 99` | `0,00 – 3,30s` | **Frase 1:** *"O sapato do Nico pediu demissão."* | Close-up da sola fina descolando em *"boca de jacaré"* com meia interna visível (`f12–48`); câmera recua no instante em que a sola engancha na pedra (`f52`) e Nico tropeça exatamente em *"pediu demissão"* (`f58–85`). | `frame_035_01_frase1_sapato_abrindo.png` / `frame_068_02_frase1_pediu_demissao_tropeco.png` |
| **Shot 2** | `100 – 186` | `3,33 – 6,20s` | **Frase 2:** *"E na vila dele, ninguém usava dinheiro."* | Plano aberto contextualizando a vila rústica, a barraca da feira e o Nico com o carrinho. Em *"ninguém usava dinheiro"* (`f134–185`), surge o **Selo 3D Sem Dinheiro** (`Selo_Sem_Dinheiro_Root`: moeda dourada com cifrão cortada por faixa vermelha de proibição). | `frame_150_03_frase2_vila_sem_dinheiro.png` |
| **Shot 3A** | `187 – 238` | `6,23 – 7,93s` | **Frase 3A:** *"Ele tinha um saco de batatas..."* | Plano médio-aberto do Nico ao lado do carrinho de madeira: gesto confiante de ideia (`f194–216`), agachamento de antecipação (`f227`) e levantamento do saco de 40kg junto ao peito (`f238`). | `frame_204_04_frase3a_ideia_saco_batatas.png` |
| **Shot 3B** | `239 – 290` | `7,97 – 9,67s` | **Frase 3B:** *"...e achou que dava pra trocar..."* | *Tracking shot* acompanhando 4 passos pesados e ancorados no chão (`13 quadros` por passo) carregando o saco de batatas até a barraca. | `frame_259_05_frase3b_caminhada_trocar.png` |
| **Shot 4** | `291 – 368` | `9,70 – 12,27s` | **Frase 3C + 4A:** *"...por um par novo. / Só que o sapateiro..."* | Saco de batatas aterrissa no balcão no `f298` (`9,93s`) com *squash & stretch* e pufes de poeira; Nico aponta para o par novo (`f306–366`) enquanto o sapateiro balança a cabeça negando em *"Só que o sapateiro..."* (`f334–366`). | `frame_310_06_frase3c_balcao_par_novo.png` |
| **Shot 5** | `369 – 431` | `12,30 – 14,37s` | **Frase 4B:** *"...não queria batatas."* | Enquadramento da recusa: sapateiro ergue o braço esquerdo e a placa **X Vermelho** (`Placa_Recusa_X_Root`) salta com *overshoot* elástico sobre o saco de batatas (`f373–392`); Nico recua surpreso. | `frame_392_07_frase4_nao_queria_batatas_x.png` |
| **Shot 6** | `432 – 479` | `14,40 – 15,97s` | **Frase 5:** *"Queria leite."* | Corte de ênfase para a direita: a placa do X recua discretamente (`scale 0.76`) e a **Placa Grande do Leite** (`Placa_Desejo_Leite_Root`: caixa 3D + copo + check verde) salta em destaque no pico de *"leite"* (`f432–451`). | `frame_451_08_frase5_queria_leite.png` |
| **Shot 7** | `480 – 576` | `16,00 – 19,20s` | **Frase 6:** *"Nico... aí complicou."* | *Medium Close-Up* final: em *"Nico..."* (`f484–505`) ele olha do ícone do leite para o saco de batatas; na pausa `"..."` (`f505–516`) e em *"aí complicou"* (`f516–542`), faz o *shrug* cômico de frustração olhando para a câmera, sustentado até `f576` (`19,20s`). | `frame_530_09_frase6_nico_ai_complicou.png` |

---

## 4. Avaliação Comparativa da Assinatura Visual Opcional ("Carimbo da Dúvida")

Conforme solicitado na Seção 4 da missão, foi desenvolvido um teste opcional e independente da assinatura visual provisória **"Carimbo da Dúvida"**:
- **Recurso independente reutilizável:** Salvo isoladamente em `objetos/carimbo_duvida.blend` (coleção `Col_Carimbo_Duvida`, objeto raiz `Carimbo_Duvida_Root`), composto por base circular azul-marinho, anel externo dourado e ponto de interrogação 3D (`?`) esculpido em creme/ouro.
- **Comportamento na cena:** Na variante com assinatura (`cena_01_V3_1_com_carimbo.blend`), o carimbo surge com *pop* elástico rápido na pausa de reticências `"Nico..."` (`frames 507–521` / `16,90s–17,37s`) no canto superior esquerdo ao lado do boné do Nico, sem cobrir o rosto do personagem nem interromper o fluxo narrativo.
- **Arquivos para comparação direta:**
  - **Prancha comparativa lado a lado (Frame 530):** `episodios/EP001_dinheiro/previews/v3_1/comparativo_carimbo_duvida.png`
  - **Vídeo MP4 sem assinatura:** `episodios/EP001_dinheiro/videos/preview_V3_1_sem_carimbo_lowres.mp4` (e `preview_V3_1_narrado_lowres.mp4`)
  - **Vídeo MP4 com assinatura:** `episodios/EP001_dinheiro/videos/preview_V3_1_com_carimbo_lowres.mp4`
- **Status de aprovação:** O elemento **não está aprovado definitivamente** nesta missão; aguarda avaliação humana do comparativo.

---

## 5. Planejamento de Efeitos Sonoros Pontuais (SFX — Opcional Futuro)

Nenhum efeito sonoro ou trilha musical foi misturado ao áudio nesta etapa para preservar a avaliação limpa da sincronização da voz. Para a etapa futura de *sound design*, ficam registrados os quadros exatos de sincronismo:
1. **Sapato abrindo (*"boca de jacaré"*):** `Frame 16` (`0,53s`) — som curto de velcro/borracha descolando.
2. **Tropeço na pedra:** `Frame 58` (`1,92s`) — som leve de sola raspando em pedra + desequilíbrio cômico.
3. **Selo Sem Dinheiro (Frase 2):** `Frame 136` (`4,53s`) — *pop* suave de madeira/moeda.
4. **Saco de 40kg no balcão (*"PLOC!"*):** `Frame 298` (`9,93s`) — impacto abafado de saco de estopa pesado sobre madeira.
5. **Placa de Recusa (X Vermelho):** `Frame 375` (`12,50s`) — *pop* negativo curto.
6. **Placa do Leite:** `Frame 434` (`14,47s`) — *ding/pop* brilhante contrastando com a recusa anterior.
7. **Carimbo da Dúvida (se aprovado):** `Frame 509` (`16,97s`) — som curto de carimbo/interrogação cômica.

---

## 6. Instruções Simples para Substituir a Voz Futuramente (Sem Reconstruir a Cena)

Toda a animação V3.1 é parametrizada pelos tempos de `timing.json` e aplica os *keyframes* diretamente sobre a cena `cena_01_V3.blend` já modelada. Para substituir a narração de trabalho por uma nova gravação ou nova geração TTS no futuro **sem reconstruir nenhum modelo 3D**:

### Passo 1 — Atualizar o arquivo de áudio (e opcionalmente `timing.json`)
Coloque o novo arquivo `.wav` na pasta de áudio (por exemplo, `audio/narracoes/EP001/narracao_oficial.wav`). Se os tempos das 6 frases mudarem, atualize apenas os campos `start_frame` / `end_frame` (e `start_sec` / `end_sec`) em `timing.json`.

### Passo 2 — Executar o comando único de substituição de voz
No terminal PowerShell, na raiz do projeto (`c:\Users\Cleidson\Videos\canal-financas-3d`), execute:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P "scripts/build_scene_v3_1.py" -- --mode replace-voice --audio "audio/narracoes/EP001/narracao_oficial.wav" --timing "timing.json"
```

Esse comando realiza automaticamente em segundos:
1. Abre `cena_01_V3.blend` preservando 100% da modelagem, materiais e iluminação.
2. Re-calcula a posição de todos os *keyframes* de ação e cortes de câmera conforme `timing.json`.
3. Substitui a faixa de áudio `Narracao_Trabalho_EP001` no Video Sequence Editor (VSE) pelo novo `.wav`.
4. Salva `cena_01_V3_1.blend` (e `cena_01_V3_1_com_carimbo.blend`) e renderiza as novas prévias MP4 sincronizadas e auditadas via FFmpeg/FFprobe.

---

## 7. Correção e Auditoria Automática de Áudio via FFmpeg/FFprobe (V3.1.1)

### 7.1. Diagnóstico da Causa Raiz
Nos MP4s gerados diretamente pela renderização 3D do Blender (`scene.render.use_sequencer = False`), o contêiner MP4 recebia uma faixa `aac` de `19,20s` com bitrate residual (`2.278 bps`) e amostras totalmente zeradas (`RMS = -240,0 dBFS`, `Peak = -240,0 dBFS`).

### 7.2. Solução Implementada (`scripts/pipeline_v3/audio_finalizer.py`)
Sem iniciar nova renderização 3D no Blender e preservando integralmente os arquivos V3 e V3.1 anteriores, foi implementada a etapa automática de finalização e verificação em 10 passos (`finalize_mp4_with_narration` e `verify_finalized_mp4`):
1. **Recebimento do vídeo H.264 e do WAV de narração** (`narracao_B_flash_lite_V1.wav`).
2. **Remoção da faixa silenciosa original** (`-map 0:v:0`).
3. **Muxing AAC sem recodificação do vídeo H.264** (`-c:v copy -c:a aac -b:a 192k -ar 24000 -ac 1`).
4. **Ancoragem em `t = 0.000s`** (`aresample=async=1:first_pts=0`), preservando o silêncio inicial (`0,00s – 0,41s` com `RMS = -72,27 dBFS`).
5. **Preenchimento exclusivo da cauda restante** (`apad=whole_dur=19.200000,atrim=0:19.200000`), completando com silêncio puro (`-240,0 dBFS`) apenas os `0,48s` finais (`18,72s – 19,20s`).
6. **Preservação da duração planejada da cena** (`19,2000s` exatos / `576 quadros` a `30 FPS`).
7. **Validação estrutural com FFprobe** (codec `h264`, `576 frames`, `19,20s`; codec `aac`, `24000 Hz`, `1 canal`, `19,20s`, `112.947 bps`).
8. **Decodificação PCM da faixa AAC do MP4 e verificação de RMS e Pico** para detecção de silêncio.
9. **Comparação com o WAV de origem:**
   - **Deslocamento temporal (lag via FFT cross-correlation):** `0 amostras` (`0,0 ms`).
   - **Correlação de forma de onda (amostra a amostra):** `0,999938`.
   - **Correlação de envelope RMS (janelas de 10 ms):** `0,999995`.
   - **Diferença de RMS global ativo (`0,00s – 18,72s`):** `0,02 dB` (`-18,55 dBFS` no MP4 vs. `-18,53 dBFS` no WAV).
   - **Diferença de Pico:** `0,01 dB` (`-1,52 dBFS` no MP4 vs. `-1,51 dBFS` no WAV).
   - **Verificação individual das 6 frases:** todas as 6 frases validadas com diferença de RMS `<= 0,02 dB`.
10. **Interrupção automática (*Fail-Fast*):** Lança `AudioVerificationError` caso qualquer verificação falhe (validado pelos testes negativos em `testes/test_pipeline_v3_1.py`).

### 7.3. Arquivos MP4 Finalizados e Verificados (Sem Sobrescrever os Anteriores)
- `episodios/EP001_dinheiro/videos/preview_V3_1_1_narrado_lowres.mp4`
- `episodios/EP001_dinheiro/videos/preview_V3_1_1_sem_carimbo_lowres.mp4`
- `episodios/EP001_dinheiro/videos/preview_V3_1_1_com_carimbo_lowres.mp4`
- Relatório JSON completo da auditoria: `episodios/EP001_dinheiro/videos/relatorio_auditoria_audio_V3_1_1.json`


