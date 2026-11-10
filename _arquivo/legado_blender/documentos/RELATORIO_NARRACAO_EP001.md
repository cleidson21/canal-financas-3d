# Relatório — Narração, temporização e legendas do EP001 (Fases A–C)

Data: 2026-11-04 · Motor: `gemini-3.8-flash-lite-tts`, voz `Puck`, pt-BR (reutilizando `scripts/tts/`).

## 1. Custos e limites verificados
- `python -m scripts.tts.cli check`: credencial válida (variável de ambiente), modelo listado.
- Pesquisa de preços (fontes secundárias, **reconferir no AI Studio**): camada gratuita sem custo, mas com a ressalva de que entradas/saídas podem ser usadas por Google para melhorar produtos; limites por projeto só no painel do AI Studio. Camada paga ≈ US$ 6 / 1 M tokens de áudio até 31/12/2026 (~25 tokens/s).
- Nenhuma garantia de gratuidade foi presumida. Consumo real: 8 chamadas de TTS (1 teste + 2 + 5), tokens por chamada registrados em cada `.wav.meta.json` (campo `usage`; ex.: S01 = 173 tokens totais).
- Salvaguardas em `scripts/tts/gerar_ep001.py`: nunca sobrescreve WAV, exige `--confirmar` para >2 chamadas.

## 2. Segmentos gerados (V1)
| ID | Cena | Duração | RMS fala (dBFS) | Pico (dBFS) | Aprovação |
| :-- | :-- | --: | --: | --: | :-- |
| S01 | 1 | 6,08 s | −15,5 | −1,2 | pendente (ouvir) |
| S02 | 2 | 13,48 s | −17,4 | −1,4 | pendente |
| S03 | 3 | 17,52 s | −17,2 | −1,0 | pendente |
| S04 | 4 | 14,44 s | −17,2 | −1,7 | pendente |
| S05 | 5 | 9,24 s | −15,9 | −1,0 | pendente |
| S06 | 6 | 20,12 s | −15,4 | −1,3 | pendente |
| S07 | 7 | 13,80 s | −15,5 | −1,2 | pendente |
| S08 | 8 | 6,64 s | −15,7 | −1,8 | pendente |

**Total de fala + gaps (0,10 s):** **102,12 s** — ≈2 % acima do teto editorial de 100 s. Não houve aceleração de voz. Opções (a decidir): aceitar, ou cortar pausas/ajustar texto de S06 (o maior segmento).

## 3. Continuidade entre segmentos
- Medida objetiva: RMS de fala varia 1,95 dB entre segmentos (S02–S04 ≈ −17,3; S01, S05–S08 ≈ −15,6). Diferença pequena, mas existente; **não foi aplicada normalização**. Recomendação: normalizar por segmento para ≈ −16 dBFS na montagem final.
- Timbre/interpretação: **não avaliados por audição** — o agente não escuta áudio. Pendência obrigatória: ouvir `audio/narracoes/EP001/EP001_NARRACAO_COMPLETA_V1.wav` e decidir se gera uma versão contínua (`V2`) para comparação, conforme a regra do roteiro.

## 4. Conferência texto × fala (ASR local)
Transcrição automática (faster-whisper `small`) comparada ao roteiro. Divergências a confirmar de ouvido (podem ser erro do ASR, não da voz):
- S03: "Niko"/"o lenha" (ASR) — roteiro: "Nico", "lenha".
- S05: "falta coisa" (ASR) vs "faltar coisa".
- S06: "comprou sapatos" (ASR) vs "comprou **os** sapatos"; "usou ... para" (ASR) vs "Usou ... pra" — **as legendas seguem o roteiro**; se a voz de fato omitiu "os", ajustar a legenda ou regenerar S06.
- S07: "Por que confiava" (ASR) vs "Porque confiava".

## 5. Temporização
- Fonte: WAVs reais; palavras alinhadas por ASR local com texto do roteiro (cobertura 91–100 %, ≤3 palavras interpoladas por segmento, registradas em `timing.json`).
- Limites de frase e palavra vêm do ASR (precisão típica de dezenas de ms, não de quadros). Antes do render final, validar sincronia em pontos-chave de ouvido.
- `timing.json` contém: segmentos (id, texto, direção vocal, modelo/voz, WAV, duração, níveis, tokens, aprovação), frases e palavras com tempo global.

## 6. Legendas
- `legendas/EP001_LEGENDAS.srt` (49 cues, ≤2 linhas de ≤26 caracteres, sem sobreposição, só as palavras narradas, sem ponto final visual; "…" nas reticências).
- `legendas/EP001_LEGENDAS.ass` (1080×1920, Arial 66 negrito, contorno escuro, fade 60 ms, caixa inferior com MarginV 480 → ocupa aprox. y 1180–1440).
- Ainda não queimadas em vídeo; não verificadas sobre rosto/objetos (depende da animação, Fase E).
- Alguns cues quebram no meio da oração ("quilos de batata e / achou"); aceitável como primeiro rascunho, refinável.

## 7. Dependências adicionadas
- `faster-whisper` 1.2.1 (+ctranslate2, numpy) instalados com pip no Python do sistema; modelo `Systran/faster-whisper-small` baixado do Hugging Face. Usado só para alinhamento (não é sistema de voz).
- Nota: o PyAV instalado é incompatível com `faster-whisper`; o decode usa o FFmpeg já localizado por `audio_finalizer`.

## 8. Reprodução
```powershell
python -m scripts.tts.gerar_ep001 listar
python -m scripts.tts.gerar_ep001 gerar --ids S01 --versao 1        # teste curto
python -m scripts.tts.gerar_ep001 gerar --todos --versao 1 --confirmar
python -m scripts.legendas.align_ep001 --modelo small               # ASR -> _alinhamento_asr.json
python -m scripts.legendas.montar_ep001                             # WAV completo, timing.json, SRT, ASS
python testes\test_ep001_narracao.py                                # 94 verificações
```
(Remover/renomear `EP001_NARRACAO_COMPLETA_V1.wav` não é necessário para nova versão: use `--versao 2`.)
