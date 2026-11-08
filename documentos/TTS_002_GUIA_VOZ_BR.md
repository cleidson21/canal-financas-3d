# TTS local com referência brasileira

Usar `venvs/tts_local/Scripts/python.exe`; não reinstalar o pipeline. A nova entrada é `python -m scripts.tts.br_local`, com provedores `qwen_base_local` e `piper_local`. O módulo antigo `local.py` e o gerador Gemini permanecem preservados.

## Referência e autorização

Pasta inicial: `audio/referencias_vocais/narrador_br_001/`; instruções completas no README dessa pasta. WAV mono PCM16, 3–30 s; recomendar 10–20 s naturais, sem efeitos. Transcrição literal conferida pelo titular. A autorização precisa identificar origem/titular, permitir síntese e reutilização comercial e vincular os hashes de WAV/TXT. O template vazio não é autorização. Nenhum arquivo privado é enviado a serviços.

Na TTS-002 o usuário confirmou expressamente nesta conversa: a gravação é sua, leu exatamente o trecho sugerido e autoriza síntese local/reutilização monetizada. Por isso foram criados `transcricao.txt` e `autorizacao.json`, sem tratar a saída do ASR como transcrição aprovada automaticamente. O original M4A foi preservado e uma cópia PCM16 24 kHz criada por conversão técnica, sem normalização, aceleração ou mudança de tom.

```powershell
# Inspeção local, sem sintetizar
& venvs/tts_local/Scripts/python.exe -m scripts.tts.br_local inspect-reference
# Primeiro teste: já executado nesta missão; não sobrescrever!
# Para novo texto autorizado, criar seu TXT e usar novo nome:
& venvs/tts_local/Scripts/python.exe -m scripts.tts.br_local generate --provider qwen_base_local --text-file fala_nova.txt --output audio/narracoes/TESTES_LOCAIS_002/fala_nova_V1.wav
# Comparador CPU com mesma fonte de texto; saída também deve ser nova:
& venvs/tts_local/Scripts/python.exe -m scripts.tts.br_local generate --provider piper_local --text-file fala_nova.txt --output audio/narracoes/TESTES_LOCAIS_002/piper_fala_nova_V1.wav
```

O prompt do Base é extraído da referência com `x_vector_only_mode=False` (ICL com transcrição). O cache NPZ/JSON fica em `models/voice_prompts/`, sem pickle, vinculado a modelo/revisão/runtime e hashes de referência, transcrição e autorização. O primeiro teste recarrega esse cache antes da única síntese; próximas chamadas reutilizam-no. Mudanças de referência geram outra identidade de cache; não prometemos igualdade perfeita de timbre ou bytes.

A inferência usa caminhos locais e flags offline, sem download automático. Falha antes de carregar o modelo se a referência/autorização estiver ausente ou incoerente. Sem GPU/VRAM suficiente, não troca para serviço externo. Saídas existentes e sidecars são recusados. Base sem controle `instruct`; sotaque/prosódia são condicionados pela referência, com resultado sujeito à audição.

## Configuração inicial e variações limitadas

Base 0.6B BF16/SDPA, seed 42, português, top-k 50, top-p 1, temperatura 0,9, penalidade de repetição 1,05, máximo 1.024 tokens; parâmetros do subtalker também registrados. Modelo fixo na revisão `5d83992436eae1d760afd27aff78a71d676296fc`.

Geração inicial: uma versão, sem busca aleatória. Se a audição revelar defeito específico, registrar o defeito antes de testar no máximo duas variações fundamentadas. Priorizar melhor captação/transcrição/atuação da referência; depois pontuação e segmentos curtos com frases completas. Não alterar roteiro aprovado, não usar pontuação artificial excessiva e não tentar remover sotaque com equalização, velocidade ou pitch. Alterações de amostragem são secundárias e devem permanecer documentadas.

Piper Faber é uma comparação CPU, `length_scale=1`, sem normalização e volume 1. Não foi acelerado artificialmente; sua duração pode ser menor pelo ritmo próprio do motor. Ruído de amostragem usa os valores padrão documentados no metadata; não há seed exposta por esta integração (registrada como null). Não presumir qualidade artística por constar pt-BR no modelo.

## Aceitação

Preencher `FICHA_AVALIACAO_TTS_002.md`. Um teste acústico aprovado só comprova integridade/nível/silêncio/clipping. A decisão sobre sotaque brasileiro, naturalidade, humor e identidade é humana. O perfil CustomVoice anterior está rejeitado e arquivado como histórico. Nenhum novo narrador está aprovado e nenhum comando acima autoriza gerar/substituir o EP001 completo.
