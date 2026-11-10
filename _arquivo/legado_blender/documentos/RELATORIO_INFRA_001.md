# INFRA-001 — relatório consolidado

Data: 2026-11-05, America/Bahia. Escopo: infraestrutura, recuperação e amostras; nenhuma produção integral do EP001 ou publicação.

**Resultado:** áudio local operacional na RTX 5060; quatro amostras geradas e tecnicamente válidas. Blender automatizado por CLI com cena e render de teste. MCP não operacional pelos bloqueios descritos abaixo. Aprovação artística pendente; Puck permanece preservada.

## 1. Projeto e recuperação

Codex leu as fontes, scripts, manifesto, documentação e histórico local. Auditoria detalhada em [AUDITORIA_INFRA_001.md](AUDITORIA_INFRA_001.md). Inventário inicial: 247 arquivos, 43 scripts Python, 13 `.blend`, 11 WAVs anteriores e 30 arquivos em backups. Não existe Git nesta raiz; não há SHA de commit ou diff Git a relatar.

A missão anterior alterou o projeto: novas fontes do episódio integral, scripts TTS/alinhamento/montagem, oito segmentos Puck, narração completa, timing, SRT/ASS, metadados editoriais, manifesto e inspeções scratch. Fontes e etapas estão enumeradas na auditoria e em `testes/infra_001/prior_writes.json`. A execução terminou na leitura das APIs existentes e inspeção da cena piloto; não há animatic integral concluído. Não foram identificados scripts parcialmente escritos por análise sintática. A aprovação visual das alterações narrativas e sincronização permanece humana.

## 2. Ambiente confirmado

- Windows detectado: build 19045, UBR 6466, confirmando 10.0.19045.6466. Registro em `testes/infra_001/runtime.json`.
- CPU detectada no registro: Intel Xeon E5-2667 v4 @ 3.20GHz.
- RAM física detectada: 34.192.936.960 bytes, aproximadamente 31,85 GiB. Disponível no inventário inicial: 16.585.375.744 bytes.
- GPU: NVIDIA GeForce RTX 5060; 8.151 MiB; driver 621.01. Uso inicial observado: 2.687 MiB (incluía modelo Ollama e desktop).
- Python do projeto: 3.12.10; `py -0p` não reconhece instalações registradas no contexto de execução. Nenhum venv existente na raiz foi substituído.
- Blender: 5.2.3 LTS, build e13b728c6880.
- FFmpeg e FFprobe: 4.4.1-Jellyfin, localizados pelo resolvedor existente fora de PATH.
- PyTorch local: 2.10.0+cu128; CUDA runtime 12.8; compute capability 12.0. Operação real CUDA `ones * 2` retornou `[2,2,2,2]`. Não foi instalado CUDA Toolkit global, driver ou FlashAttention.

As consultas CIM iniciais foram negadas pelo sandbox; CPU/RAM foram recuperadas pelo registro/API Win32, sem alterar o sistema. Consultas/downloads autorizados precisaram da execução fora da restrição de rede do sandbox. Isso não envolveu envio de áudio ou documentos.

## 3. Blender MCP Runner e alternativa funcional

Extensão encontrada: `brechtcorbeel.blender-mcp-runner` 1.1.1 em `.antigravity-ide/extensions/`. A própria extensão declara Blender 5.1 ou superior; 5.2.3 satisfaz esse requisito declarado, mas não foi homologado via socket nesta missão.

O complemento MCP não apareceu no inventário de pastas nem entre os complementos habilitados nas preferências lidas por processo separado e offline. Blendkit está habilitado. Nenhuma instância interativa Blender foi detectada no início. Nenhum listener foi observado em 9876. Portanto não foi possível executar Python em uma sessão aberta via MCP, nem provar que o botão da extensão alcança Blender.

O servidor stdio fornecido pela extensão falhou ao iniciar: `Cannot find module '@modelcontextprotocol/sdk/server/index.js'`. A instalação contém `out/mcpServer.js`, mas não resolveu sua dependência SDK. A sessão atual do Codex não disponibiliza `execute_blender_python`; encontrar uma extensão no disco não cria uma ferramenta MCP no agente. Evidências: `mcp_server_stderr.log`, código instalado inspecionado e `blender_preferences_stdout.log`.

Não foi instalado servidor alternativo nem alterada configuração global. Plano de reparo posterior: restaurar a dependência da mesma extensão em escopo isolado, identificar o complemento compatível com o protocolo instalado (`type=execute`, JSON terminado por NUL), habilitar/iniciar em sessão descartável e então registrar/testar a ferramenta no host Codex. Não presumir compatibilidade com outro addon só por compartilhar o nome “Blender MCP”. Referência do host: [documentação oficial MCP do Codex](https://developers.openai.com/codex/mcp).

**Alternativa CLI passou:** processo dedicado `-b --factory-startup --disable-autoexec`, geometria, material, câmera, iluminação, salvamento de cena e quadro CPU 144×256. Primeira inspeção visual revelou que apenas `diffuse_color` não coloria o material no Cycles; corrigido para nós Principled e executado novo teste em `visual_v2/`, preservando o primeiro resultado. Código de saída registrado em `blender_blue_exit.json`. Saídas finais: `testes/infra_001/visual_v2/smoke.blend`, `smoke.png`, `blender_result.json`, stdout/stderr separados. Nenhuma cena de produção ou sessão do artista foi usada.

## 4. Ollama

Serviço operacional em `127.0.0.1:11434`, versão 0.40.14. Inventário: `jstzwhc/Qwen3-TTS:latest` (1,0 GB), `bonsai-2:9b`, `gemma4:e4b-it-q4_K_M`, `qwen3.5:9b-q4_K_M` e `qwen3.5:4b-q4_K_M`. Nenhum modelo foi removido ou substituído.

No início, `jstzwhc/Qwen3-TTS` estava carregado (llamacpp, 100% GPU, aproximadamente 1,4 GB). Foi descarregado por expiração normal antes do benchmark; não foi preciso interromper o serviço. RAM de Ollama observada inicialmente: aproximadamente 52 MB de working set do processo servidor, sem somar processos runner; VRAM inicial em `environment.json`.

`/api/show` do pacote instalado retornou apenas `capabilities: ["completion"]`, formato GGUF, família qwen3tts, 1.7B Q4_K_M. A [página do pacote](https://ollama.com/jstzwhc/Qwen3-TTS) apresenta uso de chat/texto e não documenta saída WAV. Não há evidência de síntese utilizável via esse pacote em português ou inglês. Não o tratamos como motor de narração nem tentamos converter texto/tokens em áudio improvisadamente. Ollama permanece disponível para linguagem.

## 5. Qwen local: escolha, dependências e licença

Modelo oficial `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`, revisão fixa `85e237c12c027371202489a0ec509ded67b5e4b5`. Download total aproximado 2,50 GB (pesos principais 1.811.626.576 bytes e tokenizer embutido 682.293.092 bytes). Todos os 13 arquivos conferidos por tamanho; ambos os pesos conferidos pelo SHA-256 LFS oficial (`model_integrity.json`). Não houve download duplicado do tokenizer independente. Maior download individual: wheel PyTorch de aproximadamente 2,87 GB; nenhum arquivo excedeu 5 GB.

Instalação exclusiva em `venvs/tts_local/`; caches e modelo dentro desta raiz e ignorados no Git. Pacote `qwen-tts==0.1.1`, Transformers 4.57.3 e Accelerate 1.12.0 seguem o projeto oficial. Registro completo de instalação e versões em `testes/infra_001/`. Não foi usado WSL, compilação CUDA experimental ou FlashAttention. O runtime usa BF16/SDPA; a documentação recomenda Python 3.12 e apresenta APIs PyTorch, sem garantia específica para toda combinação Windows/GPU. Compatibilidade desta combinação é comprovada apenas pelos testes efetivamente realizados.

O [modelo oficial](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice) e o [código Qwen](https://github.com/QwenLM/Qwen3-TTS/blob/main/LICENSE) declaram Apache-2.0, permitindo o uso local educativo e comercial pretendido sob as condições da licença. Preservar avisos/licenças se houver redistribuição. Dependências e licenças instaladas são inventariadas separadamente; não foi adquirido serviço pago. As vozes são presets oficiais; nenhum áudio Puck ou outra referência privada foi usado para clonagem.

O inventário `dependency_licenses.json` cobre 89 distribuições: licenças Apache, MIT, BSD, ISC e outras livres compatíveis com uso local; inclui soxr LGPL-2.1-or-later e componentes MPL. Essas licenças permitem o uso pretendido; distribuição de runtimes/bibliotecas deve conservar seus avisos e cumprir obrigações próprias. O pacote Python `sox` é BSD-3-Clause; o executável SoX não está instalado e não foi necessário para CustomVoice. Nenhum servidor Gradio foi iniciado.

Esse inventário descreve pacotes Python; componentes binários CUDA incluídos no wheel oficial mantêm os avisos próprios NVIDIA no ambiente instalado. Não foi preparado um pacote de redistribuição de CUDA ou das dependências.

A matriz oficial distingue o 0.6B CustomVoice sem instruction control das variantes 1.7B. A descrição genérica do model card sugere controle de estilo, mas a matriz específica e o código têm prioridade: este adaptador recusa instrução de estilo. Português consta como idioma; **sotaque brasileiro, naturalidade e qualidade não são garantidos pela presença do idioma**. VRAM necessária não foi presumida pela contagem de parâmetros; o adaptador exige conservadoramente 4 GiB livres antes de carregar e as medições reais aparecem nos metadados.

## 6. Interface, perfil e limites de aceitação

`scripts/tts/local.py` implementa seleção de provedor/modelo/voz/idioma/texto/seed, saída WAV exclusiva, duração, integridade e metadados. `local_cli.py` oferece CLI reutilizável. `samples_local.py` restringe o benchmark aos quatro textos/arquivos de teste solicitados. O motor Gemini legado não foi alterado nem chamado; os exports antigos continuam acessíveis por importação lazy. Provedor externo é negado por padrão. Inferência Qwen só carrega caminho local e flags offline; não baixa silenciosamente.

Perfil proposto: `audio/perfis/narrador_principal.json`, Ryan técnico provisório, sem amostra aprovada, sem data de aprovação, produção desabilitada e atualização automática desabilitada. O perfil registra metas interpretativas, mas não afirma que o motor as obedeceu.

Preservação: os 11 WAVs anteriores, roteiro, legendas, bibliotecas, cenas, backups e manifestos são comparados ao inventário inicial por SHA-256. Apenas `.gitignore` e o inicializador TTS anterior têm mudanças intencionais. Não foi produzido áudio completo novo, animação definitiva, render de 102 s ou publicação.

## 7. Retomada incremental do EP001

1. Ouvir as amostras locais, escolher candidato ou rejeitar todos; manter Puck na produção enquanto não houver decisão explícita.
2. Registrar aprovação e hash da amostra escolhida, congelando modelo/runtime/parâmetros. Não substituir automaticamente a narração EP001.
3. Confirmar o contrato do animatic com o áudio original de 102,12 s e o `episodios/EP001_dinheiro/timing.json`; preservar roteiro e legendas atuais.
4. Criar cópia versionada para o animatic integral; reaproveitar Nico/vila/feira. Criar apenas os ativos novos identificados no storyboard, sem sobrescrever bibliotecas.
5. Validar quadros-chave das cenas 1–2 e depois 3–4, 5–6 e 7–8. Checar continuidade das trocas, ficha monetária a partir da cena 6, câmeras 9:16 e áreas seguras.
6. Só após revisão visual, renderizar trechos curtos em baixa resolução e validar áudio efetivo com o finalizador existente. Revisão humana antes de sequência integral.
7. Render final/exportações/publicação são fases posteriores, fora da INFRA-001. Resolver MCP pode melhorar a interação, mas a CLI já oferece automação independente de cotas de IA.

Guia permanente: [PIPELINE_PRODUCAO.md](PIPELINE_PRODUCAO.md); regras concisas: `AGENTS.md`.

## 8. Amostras, desempenho e memória

Diretório: `audio/narracoes/TESTES_LOCAIS_001/`. Todos os arquivos são WAV PCM16 mono, 24.000 Hz, sem normalização/trilha. Mesmo texto nos três candidatos; segundo texto somente na consistência.

- **voz_A.wav — Ryan:** 14,00 s; geração 65,78 s; RTF 4,70; 672.044 bytes. Pico −4,94 dBFS; RMS −24,81 dBFS; maior silêncio 0,70 s. GPU alocada máxima PyTorch 2.600.344.576 bytes; GPU total amostrada 3.566 MiB; RSS máximo durante a geração 2.228.494.336 bytes.
- **voz_B.wav — Aiden:** 11,84 s; geração 42,20 s; RTF 3,56; 568.364 bytes. Pico −2,50 dBFS; RMS −17,88 dBFS; maior silêncio 0,94 s. GPU alocada máxima 2.531.822.080 bytes; GPU total amostrada 4.116 MiB; RSS máximo 2.261.037.056 bytes.
- **voz_C.wav — Uncle_Fu:** 13,52 s; geração 47,74 s; RTF 3,53; 649.004 bytes. Pico −8,75 dBFS; RMS −27,87 dBFS; maior silêncio 0,80 s. GPU alocada máxima 2.583.655.936 bytes; GPU total amostrada 4.119 MiB; RSS máximo 2.261.536.768 bytes.
- **voz_A_consistencia.wav — Ryan:** 11,68 s; geração 41,39 s; RTF 3,54; 560.684 bytes. Pico −7,38 dBFS; RMS −26,69 dBFS; maior silêncio 0,60 s. GPU alocada máxima 2.526.886.400 bytes; GPU total amostrada 4.119 MiB; RSS máximo 2.264.272.896 bytes.

Carregamento inicial: 33,07 s, separado dos tempos de inferência. Processo completo do benchmark: 232,15 s incluindo importação/carregamento, validação, monitoramento e gravação. Seed 42; BF16, SDPA; `max_new_tokens=1024`, sampling, top-k 50, top-p 1, temperatura 0,9 e penalidade 1,05. Subtalker: sampling, top-k 50, top-p 1 e temperatura 0,9; entrada não streaming. Idioma `Portuguese`; nenhuma instrução de estilo. Configuração efetiva e versões completas nos quatro `.wav.meta.json` e `requirements-lock.txt`.

Pico reservado pelo allocator PyTorch: 2.938.109.952 bytes (≈2,74 GiB) em todas as gerações. Pico total GPU amostrado: 4.119 MiB (≈4,02 GiB), inclui desktop/contextos e não representa apenas pesos. Pico RSS amostrado de todo o processo: 2.289.168.384 bytes (≈2,13 GiB); RAM total do sistema usada no pico amostrado: 18.618.093.568 bytes (≈17,34 GiB). Amostragem a cada aproximadamente 0,5 s mais custo do nvidia-smi; pode perder picos breves. As máximas do allocator são medidas separadas, não somar as duas métricas. Recursos brutos em `resources.json`.

Não ocorreu OOM nem fallback CPU/remoto. Não houve Blender renderizando durante o benchmark. Após a saída do processo, nvidia-smi registrou 1.145 MiB usados e `ollama ps` vazio: nenhum modelo TTS foi mantido carregado. Os tempos são de uma execução real, sem média estatística e sem promessa de desempenho idêntico em outras cargas.

As vozes realmente consultadas no modelo foram: aiden, dylan, eric, ono_anna, ryan, serena, sohee, uncle_fu e vivian. Ryan/Aiden foram escolhidos como masculinos em inglês nativo e Uncle_Fu como masculino maduro em chinês nativo, conforme descrições oficiais. Todos foram solicitados em português; não há preset nativo brasileiro certificado pelo catálogo.

## 9. Validação, problemas e aprovação humana

**Quatro de quatro passaram tecnicamente:** RIFF/WAVE, PCM completo, duração, não silêncio, pico/RMS, clipping (fração detectada zero), maior silêncio menor que 1 s, FFprobe e decodificação integral FFmpeg. Os hashes dos WAVs se mantiveram após validação e ASR. Limites locais: clipping severo ≥0,1% dos samples e silêncio contínuo >3 s são recusados, além das regras acústicas já existentes. Duração próxima ao teto de tokens é recusada como possível truncamento; essa heurística não comprova fidelidade semântica da fala.

ASR local existente: faster-whisper small, CPU/int8, sem download, 20,70 s para o lote. Comparações em `asr_validation.json`:

- Ryan: “demissão” reconhecida como “de missão”.
- Aiden: “demissão” reconhecida como “de emissão”.
- Uncle_Fu: “demissão” → “de missão”; “Nico” → “Niko”.
- Consistência: “Pera aí” reconhecida como “Peraí”.

Essas são divergências do reconhecimento automático, **não erros de pronúncia confirmados**. O usuário deve ouvir especialmente “pediu demissão”, nomes, entonação das reticências e sotaque. O texto enviado ao modelo foi exatamente o solicitado. Timbre consistente, sotaque brasileiro, naturalidade, simpatia/ironia e boa adequação ao canal continuam sem aprovação humana; não há pontuação artística inventada. Os candidatos têm volumes naturais diferentes e foram preservados sem processamento.

Testes concluídos: 93 verificações existentes do EP001 (incluindo 27 hashes do manifesto); 12 testes INFRA de proteção de WAV/sidecar, provedores externos desativados, modelo ausente, GPU ausente/VRAM insuficiente simuladas, estilo não suportado, configuração, importação sem SDK Gemini, truncamento, silêncio/clipping, perfil provisório e preservação dos arquivos anteriores. Retornos nativos registrados em `unit_exit.json`, `ep001_exit.json`, `validation_exit.json`, `samples_exit.json`, `asr_exit.json` e `pip_check_exit.json`. As fontes em `scripts/` e os JSONs anteriores foram analisados sem truncamento sintático identificado; a checagem final incluiu 55 fontes entre `scripts/` e `testes/infra_001/`.

Problemas tratados: restrições iniciais do sandbox; dependência MCP ausente e addon/serviço não observado; material Cycles corrigido em segunda cena de teste preservada; avisos não fatais de SoX/FlashAttention; resolução pip escolheu dependências compatíveis sem instalar várias alternativas de motores; nenhum erro de memória. A matriz de recursos do 0.6B evitou prometer controle de estilo inexistente.

`backups/infra_001/` contém as versões originais dos dois arquivos antigos alterados (`tts_init_original.py`, `gitignore_original.txt`), com SHA-256 igual ao inventário inicial. Todos os outros 245 arquivos inventariados continuam byte a byte iguais, incluindo os 11 WAVs anteriores. Sem API Gemini/OpenAI, sem nova chave, upload de áudio, assinatura ou serviço pago. A aprovação pendente decorre do critério artístico solicitado pelo usuário: escolher ou rejeitar candidatos antes de trocar qualquer voz de produção.
