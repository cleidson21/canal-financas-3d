# TTS-003 — Puck consolidada; EP001 pronto para continuar o animatic

Data: 2026-11-05, America/Bahia. **Decisão editorial registrada: Puck é o narrador oficial nesta fase. A narração completa aprovada foi preservada. Nenhuma nova voz, chamada Gemini/Azure ou render completo foi produzido.**

## Perfil e integridade

`audio/perfis/narrador_principal.json` agora identifica Gemini TTS, `gemini-3.8-flash-lite-tts`, Puck, pt-BR, narrador brasileiro descontraído, humor observador e ironia moderada. A referência editorial é `audio/narracoes/EP001/EP001_NARRACAO_COMPLETA_V1.wav`. Aprovação: **audição e decisão explicitamente reportadas pelo usuário nesta missão**, não audição atribuída ao agente. O perfil registra nove hashes: narração completa e os oito segmentos que a compõem. Aprovação editorial habilita reutilização; não habilita geração remota/paga.

Nenhum WAV, texto narrado, roteiro, storyboard, timing, SRT/ASS, cena/modelo Blender ou manifesto histórico foi reescrito. Os metadados antigos continuam como registro da geração passada; a nova aprovação fica no perfil oficial, sem trocar datas/status históricos dentro do EP001.

Inventário de 402 arquivos anteriores: 363 intactos no caminho original, 13 arquivos de testes públicos movidos com hashes iguais, 20 arquivos pessoais/derivados retirados por solicitação explícita e 6 atualizações autorizadas (perfil, contrato/guia e três arquivos do módulo Gemini). Foram conferidos 152 arquivos canônicos e manifestos históricos. Evidência: `testes/tts_003/integrity.json`; pesos de modelos, excluídos desse inventário inicial, foram movidos em cinco grupos com as pastas de amostras.

## Voz pessoal retirada; locais rejeitados separados

A gravação M4A pessoal, sua cópia WAV, transcrições/autorização dessa referência, WAV sintetizado com sua voz, metadados diretos e cache NPZ/JSON do prompt/embedding foram removidos do workspace. **Não foram arquivados como áudio ou prompt pessoal.** Logs diretos dessa referência também foram retirados. O mapa exato está em `testes/tts_003/retirada_e_arquivo.json`.

Presets públicos CustomVoice/Piper e pesos Qwen/Piper ficam em `arquivo/tts_locais_rejeitados/TTS_003/`; o ambiente Python isolado e implementações foram mantidos. Perfis locais são históricos rejeitados em `audio/perfis/historico/`. Backups e manifestos anteriores permanecem integrais; por isso registros técnicos antigos ainda podem citar arquivos agora retirados. Esses registros não contêm a gravação/embedding removidos. Não restaurar nem baixar modelos automaticamente. Suítes anteriores que dependem da referência retirada são históricas, não o comando atual de aceitação.

## Consumo e proteção

O gerador central Gemini passou a conferir modelo/voz/idioma oficiais; preservar qualquer WAV existente, inclusive com `--overwrite`; conferir o hash de reutilizações aprovadas; recusar sidecar preexistente; e gravar novas saídas exclusivamente. Não há fallback de voz/modelo.

`audio/perfis/politica_geracao.json` bloqueia geração remota, verificações remotas e geração paga. Novas chamadas futuras exigem nova autorização, habilitação explícita de perfil/política e permissão de uso único vinculada a requisição, fingerprint da chave existente e projeto declarado. A evidência manual de catálogo/cotas/camada gratuita deve ser recente (até uma hora); estado pago/desconhecido é recusado. O cliente SDK tem uma tentativa; quota 429 interrompe o fluxo e persiste bloqueio, sem retry nem troca de chave/projeto. A consulta de catálogo não é teste de síntese nem prova de cota.

Sucesso nunca vira “custo zero”: a cobrança efetiva é registrada `unverified` até conferência independente. Quotas/faturamento da conta **não foram consultados nesta missão**. A documentação pública confirma a existência do modelo; disponibilidade/cota efetiva do projeto permanece não verificada. Detalhes, limitações e contingência Azure F0: [POLITICA_NARRACAO_E_COTAS.md](POLITICA_NARRACAO_E_COTAS.md). O planejador `scripts/tts/plan_generation.py` prepara os hashes offline, sem autorizar geração.

## Compatibilidade do áudio aprovado

- WAV PCM16 mono, 24.000 Hz, 2.450.880 amostras: **102,12 s exatos**, coerentes com o `episodios/EP001_dinheiro/timing.json`. Nenhuma aceleração, mudança de tom, corte ou normalização aplicada.
- FFprobe reconheceu o arquivo e FFmpeg decodificou o áudio integral sem erro. O leitor do finalizador existente aceitou formato e duração. Pico integral −1,01 dBFS; RMS integral −17,57 dBFS.
- Comparação local dos oito segmentos: amplitude de RMS de fala 1,77 dB usando janelas de 20 ms acima de −45 dBFS; nenhum segmento ultrapassou o sinalizador relativo de 3 dB. É um método diferente da métrica histórica de 1,95 dB no timing, que foi preservada. Isso não mede timbre/expressividade nem exige tratamento do áudio aprovado.
- A suíte existente passou: 93 verificações, incluindo texto, oito durações, montagem, SRT/ASS, tempos monotônicos e os 27 hashes do manifesto base. São 49 cues, sem alterar seus tempos.
- Blender 5.2.3 LTS carregou a narração em uma cena factory descartável, a 30 FPS: strip de **3.064 quadros**, velocidade 1. Nenhum `.blend` foi salvo, nenhuma renderização executada e nenhuma sessão do artista alterada. O arredondamento da imagem corresponde a 102,1333 s, com cerca de 13 ms de margem final; o áudio permanece 102,12 s.

O pipeline V3.1 antigo ainda é o piloto: seu comando padrão usa `narracao_B_flash_lite_V1.wav` de 18,72 s e o timing da raiz. **Não executar esse montador como se já fosse o animatic integral.** `scripts/tts/continuity.py` adapta em memória as 28 frases do timing integral para o esquema `phrases` do finalizador, sem modificar a fonte. Exemplo derivado em `testes/tts_003/timing_finalizador_EP001.json`. O muxing final de um vídeo integral ainda não foi testado: depende da futura sequência de imagem e deve usar esse timing integral e duração suficiente, sem encurtar o WAV.

## Testes e continuidade

Passaram **8 testes de proteção** com rede proibida e cliente simulado: bloqueio padrão, identidade editorial, cobrança paga/desconhecida/evidência expirada, reutilização, sidecar/sobrescrita, quota sem retry e bloqueio persistente, autorização de uso único, sucesso sem presumir gratuidade e SDK com uma tentativa. Os WAVs de fixture são apenas bytes sintéticos temporários de teste, não narração. Também passaram a suíte EP001, leitura Blender, decodificação FFmpeg, adaptação de timing e verificação de preservação.

**EP001 está pronto, do ponto de vista da voz e dos insumos, para continuar a fase de animatic com Puck.** Próxima execução: nova cena/versionamento identificável para o integral; reutilizar bibliotecas, seguir o storyboard e timing do episódio; validar quadros-chave e depois trechos curtos em baixa resolução. O animatic integral, sua aprovação visual, muxing e render final continuam pendentes. Nenhuma dessas fases foi iniciada aqui.

Para episódios futuros, a política propõe 3–5 blocos narrativos coerentes como hipótese, um take inicial por bloco e repetição apenas por defeito confirmado; não muda os oito segmentos do EP001. O critério principal permanece pausa, humor e continuidade emocional. Uma contingência Azure teria outra voz e exigiria aprovação artística; não foi criada conta, assinatura, faturamento ou chamada.
