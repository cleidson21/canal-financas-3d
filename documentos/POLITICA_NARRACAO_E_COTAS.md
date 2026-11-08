# Puck: geração, cotas e continuidade editorial

Decisão vigente de 2026-11-05: **Gemini TTS, `gemini-3.8-flash-lite-tts`, Puck, pt-BR**. O usuário aprovou a narração completa do EP001, sem novas gerações. Referência editorial e nove hashes aprovados em `audio/perfis/narrador_principal.json`; não usar Puck como fonte de clonagem.

## Padrão seguro

- Reutilizar áudio aprovado antes de planejar qualquer chamada. EP001 permanece com seus oito segmentos, 102,12 s, texto, pausas, SRT/ASS e timing originais.
- `generation_enabled=false` no perfil, `remote_generation_enabled=false`, `remote_checks_enabled=false` e `paid_generation_enabled=false` na política. Esta missão não habilita nenhum deles.
- Modelo/voz/idioma são comparados ao perfil oficial antes de qualquer cliente remoto. Sem fallback para outro modelo/voz. Novos áudios sempre têm `approved=false`; sua aprovação humana é separada de integridade acústica.
- WAV existente nunca é sobrescrito, mesmo com a opção antiga `--overwrite`. Áudio aprovado tem hash conferido; sidecar órfão também impede geração. Preservar a versão anterior e escolher nova saída para uma solicitação autorizada futura.
- O SDK usa uma única tentativa; erros não disparam retries automáticos. Erro de cota cria um bloqueio persistente em `audio/controle_geracao/quota_block.json`; parar o lote, revisar cotas e esperar a janela aplicável. Nunca trocar chave/projeto para contornar limites.

## Pré-verificação futura — sem chamada nesta missão

Os [limites Gemini](https://ai.google.dev/gemini-api/docs/rate-limits) são aplicados por projeto, incluindo RPM/TPM/RPD; modelo listado não comprova saldo de cota. Conferir projeto/modelo, uso, limites e camada de faturamento no [AI Studio](https://aistudio.google.com/rate-limit). A [documentação de faturamento](https://ai.google.dev/gemini-api/docs/billing) distingue camada Free de camadas pagas. Não deduzir gratuidade pelo sucesso da API, tokens de usage, ausência de erro ou autenticação.

Antes de uma geração futura explicitamente autorizada:

1. Planejar texto final, estilo, saída nova e quantidade mínima de solicitações. O planejador abaixo é inteiramente offline e mostra hashes da requisição/chave, sem expor a chave.
2. O proprietário confere no AI Studio o projeto da chave existente, modelo disponível e elegível à camada gratuita, faturamento não habilitado e cota disponível. Registrar a evidência, data e validade até uma hora. Sem confirmação de gratuidade, não chamar; não configurar faturamento.
3. Criar uma autorização de uso único baseada em `audio/perfis/autorizacao_geracao.modelo.json`, vinculada ao hash exato da requisição, fingerprint da chave e projeto declarado. O template vazio não autoriza nada. Sem prova de ligação chave/projeto pelo proprietário, os hashes locais não certificam essa associação.
4. Só após nova autorização do usuário, habilitar geração no perfil e política; verificação remota, se solicitada, tem controle próprio. A política paga continua falsa. Esta implementação recusa projetos pagos/estado desconhecido; habilitar pagamento exigiria outra decisão e alteração explícita do controlador.
5. O controlador reserva atomicamente a autorização antes da rede, consulta o modelo por leitura e realiza no máximo uma síntese. Erros consomem a autorização; não é renovada automaticamente. Uma consulta de catálogo bem-sucedida continua sem provar saldo/ausência de cobrança.
6. Registrar requisição literal, estilo, modelo/voz/idioma, parâmetros efetivamente enviados, duração, usage retornado e aprovação pendente. Faturamento efetivo permanece `unverified` até conferência independente; não registrar custo zero por suposição.

```powershell
# Apenas planejar: não usa rede, não cria áudio, não autoriza cobrança
python -m scripts.tts.plan_generation --text-file texto_futuro.txt --output audio/narracoes/EP002/fala_V1.wav --project-id PROJETO_EXISTENTE
# Comparação acústica local de um novo WAV com Puck aprovada
python -m scripts.tts.continuity audio/narracoes/EP002/fala_V1.wav
```

Após autorização futura e preenchimento da evidência, a CLI existente aceita `--permit caminho.json` em `generate`; o texto/direção precisam reproduzir o hash do plano. O lote antigo do EP001 apenas reutiliza V1; não usá-lo para gerar uma versão nova. Não ativar serviços para testar cotas. Regras locais são guardas operacionais, não uma garantia técnica de cobrança do provedor.

## Continuidade entre episódios

Conservar o prompt base aprovado e acrescentar apenas direção de atuação do trecho. Preservar português brasileiro natural, conversa próxima, humor observador e ironia moderada; evitar voz de anúncio/telejornal, entusiasmo forçado e pausas exageradas. Não alterar modelo ou versão do SDK automaticamente. A referência editorial aprovada do EP001 não obriga a imitar suas palavras ou acelerar futuras falas.

Comparar formato, taxa/canais, pico, RMS de fala e silêncio com a referência. `scripts/tts/continuity.py` faz leitura local, sem normalizar, mudar tom/velocidade ou aprovar timbre. Seu RMS de fala usa janelas de 20 ms acima de −45 dBFS; diferenças acima de 3 dB geram sinalização de revisão, não rejeição ou processamento automáticos. Métricas não medem naturalidade, sotaque ou humor. Ouvir nomes, termos econômicos, transições e finais de piada. Novo episódio exige aprovação humana antes de temporizar animação.

## Proposta para episódios futuros — sem alterar EP001

Usar como hipótese inicial 3–5 blocos coerentes, em vez de uma chamada por frase: abertura/contexto; tentativa e complicação; escalada; descoberta/resolução; reflexão/pergunta final. Mesclar dois blocos apenas se a intenção emocional e a inteligibilidade permanecerem estáveis. Faixa exploratória de 15–30 s por bloco, sem tratar duração como regra rígida ou quota comprovada.

Revisar texto e direção antes da primeira chamada. Gerar um take por bloco, ouvir e reutilizar o que passou. Corrigir só o bloco com defeito confirmado; não regenerar tudo nem criar takes preventivos. Menos requisições pode reduzir carga em RPM/RPD e overhead; não garante menor custo/token. Bloco longo aumenta o custo de eventual repetição e pode prejudicar timing de humor. Avaliar primeiro com roteiro futuro aprovado, mantendo pausas/continuidade acima da redução de chamadas.

## Contingência futura Azure Speech F0

A [página oficial de preços](https://azure.microsoft.com/en-us/pricing/details/speech/) informa 0,5 milhão de caracteres mensais gratuitos para TTS neural em F0; [limites F0](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits) são próprios desse plano. Reconferir oferta, região, vozes pt-BR, permissões e limites antes de uso; não presumir direito de conta/projeto já existente.

Nenhuma conta, assinatura, faturamento, chave ou chamada Azure foi criada nesta missão. Uma voz Azure teria outra identidade: não é substituta automática nem reprodução garantida da Puck. Exigiria amostra e aprovação artística antes de uso em produção. Não implementar o provedor agora.
