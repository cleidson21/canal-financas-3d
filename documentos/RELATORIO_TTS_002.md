# TTS-002 — referência brasileira e comparação Piper

Data: 2026-11-05, America/Bahia. **Base 0.6B e Piper Faber geraram uma amostra cada; ambas passaram na validação técnica. Melhora perceptiva do sotaque e naturalidade aguarda audição humana. Nenhum narrador novo aprovado.**

## Diagnóstico e preservação

CustomVoice existente: `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`, revisão `85e237c12c027371202489a0ec509ded67b5e4b5`, `qwen-tts 0.1.1`, PyTorch `2.10.0+cu128`, Transformers `4.57.3`, Accelerate `1.12.0`, Python `3.12.10`, BF16/SDPA. Seed 42, sampling, top-k 50, top-p 1, temperatura 0,9, penalidade 1,05 e teto de 1.024 tokens; metadados anteriores preservados. A [matriz oficial](https://github.com/QwenLM/Qwen3-TTS) e o código instalado confirmam ausência de instruction control no 0.6B. Português suportado não significa sotaque brasileiro; não existe seletor explícito de sotaque para esses presets.

Ryan, Aiden e Uncle_Fu foram **rejeitados por audição do usuário**, por artificialidade, rigidez e sotaque estrangeiro. Isso é avaliação humana reportada, não uma medição automática. `audio/perfis/narrador_principal.json` agora registra `rejected`, com os três nomes e motivo; seu conteúdo anterior foi arquivado byte a byte em `audio/perfis/historico/INFRA_001/`. Nenhum WAV ou sidecar anterior foi alterado.

Inventário TTS-002: 330 arquivos anteriores; 329 intactos e uma mudança intencional no perfil rejeitado. **15 WAVs anteriores preservados**, incluindo Puck completa/segmentos e os quatro testes INFRA-001. Roteiro, storyboard, legendas, `.blend`, scripts anteriores, backups e manifestos permaneceram iguais. Fonte: `testes/tts_002/baseline.json` e `validation.json`.

## Modelo Base e referência autorizada

[Qwen Base 0.6B oficial](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base), Apache-2.0, revisão `5d83992436eae1d760afd27aff78a71d676296fc`: 2.516.106.051 bytes totais. Tokenizer de 682.293.092 bytes reaproveitado após conferir SHA oficial; pesos principais baixados: 1.829.344.272 bytes. Havia 155.879.874.560 bytes livres antes da preparação. Arquivos verificados em `model_integrity.json`. O venv anterior foi reutilizado, sem reinstalar Qwen/PyTorch/CUDA/FlashAttention.

O caminho Puck inicialmente indicado pelo usuário foi identificado e recusado como fonte de clonagem. Depois o usuário gravou sua própria voz e confirmou expressamente nesta conversa: titularidade, leitura literal do trecho sugerido e autorização de síntese local/reutilização inclusive monetizada. A autorização não aprova artisticamente a voz sintetizada.

Referência: `audio/referencias_vocais/narrador_br_001/referencia.wav.m4a`, original AAC mono 48 kHz, 16,874625 s, preservado. Cópia técnica `referencia.wav`: PCM16 mono 24 kHz, 16,875 s, sem efeitos/normalização/alteração de velocidade/tom. Transcrição confirmada pelo usuário em `transcricao.txt`; autorização em `autorizacao.json`, vinculada aos hashes. SHA-256 do WAV: `dec9d650a08c367adff4058a07c560c903c52dc06542d2a9180fc82a9bff5705`.

Referência válida, sem clipping detectado; pico −13,66 dBFS, RMS −33,79 dBFS. ASR sugeriu diferenças em “uma ideia”/“a ideia” e “sapatos”/“sapato”; foram mantidas separadas da transcrição literalmente confirmada pelo titular. Não se tomou ASR como prova de pronúncia ou transcrição humana.

## Geração e desempenho reais

Pasta: `audio/narracoes/TESTES_LOCAIS_002/`. Mesmo texto solicitado nos dois motores, com parágrafos separados. Uma versão inicial por motor, **sem variações ou busca aleatória**.

- **qwen_base_br_V1.wav:** 12,24 s; PCM16 mono 24 kHz; 587.564 bytes. Síntese 45,59 s; RTF 3,72. Carregamento 17,91 s; extração do prompt 15,46 s; processo completo 81,26 s. Pico −13,97 dBFS; RMS −34,70 dBFS; maior silêncio 1,10 s; clipping detectado zero. O volume bruto é baixo, próximo ao da referência; não foi processado para disfarçar limitações.
- **piper_faber_V1.wav:** 8,162 s; PCM16 mono 22,05 kHz; 359.980 bytes. Síntese CPU 2,41 s; carregamento 8,10 s; RTF 0,30. Pico −5,12 dBFS; RMS −22,05 dBFS; maior silêncio 0,20 s; clipping detectado zero. Ritmo próprio mais rápido, sem aceleração aplicada.

Base executou na RTX 5060 8.151 MiB, driver 621.01: máximo alocado PyTorch 2.957.888.512 bytes (≈2,75 GiB); reservado 3.397.386.240 bytes (≈3,16 GiB); máximo **total GPU amostrado 4.309 MiB**, incluindo desktop/contextos. RSS máximo amostrado do processo: 2.329.186.304 bytes (≈2,17 GiB). Sem OOM, sem fallback. Piper usou ONNX CPU: RSS máximo 147.214.336 bytes; GPU total observada 1.328 MiB não é consumo atribuível ao Piper. Amostragem aproximadamente 0,5 s mais custo do nvidia-smi, podendo perder picos breves; não somar allocator e total da GPU. Nenhum Blender renderizou nem outro modelo pesado ficou simultaneamente na GPU.

O prompt Base foi extraído com áudio+transcrição (`x_vector_only_mode=False`), salvo em NPZ/JSON sem pickle, recarregado e efetivamente usado na síntese. Cache `98ebd0b313ac9b8436cbb73d08f9c454b9197d227d8c03b9fd52f90d7a49b301`; vincula referência/transcrição/autorização/revisão/runtime. Esse teste comprova reutilização técnica, não estabilidade artística entre episódios.

Parâmetros Base: seed 42, BF16/SDPA, idioma Portuguese, sampling, top-k 50, top-p 1, temperatura 0,9, penalidade 1,05, máximo 1.024 tokens; subtalker sampling/top-k 50/top-p 1/temperatura 0,9; entrada não streaming. Sem `instruct`. As configurações e medições brutas constam dos dois `.wav.meta.json`; não se promete identidade perfeita entre execuções.

## Piper: licença e instalação mínima

Voz individual [Faber medium](https://huggingface.co/rhasspy/piper-voices/blob/main/pt/pt_BR/faber/medium/MODEL_CARD): pt-BR, um locutor, 22.050 Hz; card declara **dataset CC0** e fine-tuning a partir de lessac inglês. O repositório de pesos declara MIT. Motor [Piper oficial](https://github.com/OHF-Voice/piper1-gpl): GPL-3.0, geração local gratuita; conservar condições/avisos se redistribuir o motor. Não confundir licença do programa, do dataset e dos pesos. O preset pt-BR não constitui aprovação automática de sotaque/naturalidade.

Modelo ONNX: 63.201.294 bytes; revisão `e7229f7d33a10e145e109b886d661984201ac3c4`; SHA verificado. Adicionados apenas `piper-tts==1.8.0` e `pathvalidate==3.3.1`; nenhuma dependência anterior removida/atualizada, ONNX Runtime 1.31.1 reaproveitado. `pip check` passou. Cadu foi apenas consultado (card com dataset CC0), não instalado. Piper com comprimento 1, noise 0,667/0,8, volume 1 e `normalize_audio=False`; seed não exposta nesta integração, registrada null.

## VoiceDesign: apenas viabilidade

[1.7B VoiceDesign oficial](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign), Apache-2.0, revisão consultada `5ecdb67327fd37bb2e042aab12ff7391903235d3`: **4.520.163.832 bytes** incluindo tokenizer; pesos principais 3.833.402.552 bytes. Só os arquivos BF16 já representam aproximadamente 4,21 GiB, antes de CUDA, ativações, KV e desktop. Uso total real de VRAM nesta RTX/Windows **não medido**; pode pressionar os 8 GB, especialmente com referência/geração longa. Espaço em disco existe, mas não basta para garantir execução.

Mesmo pacote PyTorch oferece a rota Python de descrição de voz; a execução Windows desta variante não foi homologada nesta missão. Poderia receber descrição de narrador masculino brasileiro e idioma Portuguese, sem garantia de sotaque. O projeto documenta design seguido de clonagem: o WAV sintético poderia servir como referência reutilizável, sujeito a nova validação. **Não baixado nem executado**, por priorizar Base menor e referência brasileira real em vez de ampliar modelos.

## Validação e decisão pendente

Os dois WAVs passaram em cabeçalho/PCM íntegro, não silêncio, duração, pico/RMS, silêncio contínuo/clipping, FFprobe e decodificação integral FFmpeg. ASR small local/CPU transcreveu ambos: Base apresentou “de emissão” para “demissão” e “Niko”; Piper apresentou “demissão” e “Niko”. Divergências de ASR não confirmam erros reais nem medem sotaque. Não foi declarada melhora perceptiva sem audição.

Passaram **6 testes TTS-002**, 93 verificações existentes do EP001, preservação por hash e `pip check`. Testes cobrem ausência de referência antes do carregamento, cópia Puck recusada, não sobrescrita, autorização vinculada a hashes/permissões, WAVs reais e cache reutilizado, perfil rejeitado e preservação do original M4A. Logs/códigos de saída: `testes/tts_002/`. Avisos não fatais já conhecidos de SoX/FlashAttention foram preservados nos logs, sem instalações extras. Nenhuma API comercial, upload privado, clonagem Puck ou alteração Blender/EP001.

Ouvir ambos e preencher [ficha de avaliação](FICHA_AVALIACAO_TTS_002.md). A escolha não precisa ser entre eles: rejeitar ambos é um resultado válido. Se a qualidade não bastar, priorizar captação/atuação melhor ou outro locutor voluntário com autorização, antes de modelos maiores ou tentativas aleatórias. Instruções de novos trechos e política de no máximo duas variações fundamentadas: [guia de voz brasileira](TTS_002_GUIA_VOZ_BR.md). Não substituir produção sem decisão explícita do usuário.
