# Canal Finanças 3D — contrato de execução

## Fontes e arquitetura
- Roteiro canônico: `episodios/<episodio>/roteiro.md`; storyboard: `storyboard.md` no mesmo diretório. Não confundir o `timing.json` da raiz (piloto) com o do episódio completo.
- Bibliotecas: `personagens/`, `cenarios/`, `objetos/`. Nico e sua identidade seguem `documentos/BIBLIA_VISUAL.md`.
- Python Blender: `scripts/pipeline_v3/`; TTS: `scripts/tts/`; legendas: `scripts/legendas/`. Preservar os motores existentes.
- Áudio: `audio/narracoes/`; perfis: `audio/perfis/`; publicação: `episodios/<episodio>/publicacao/`.

## Integridade
- Nunca sobrescrever versões aprovadas, WAVs existentes, bibliotecas de produção ou manifestos SHA-256. Nunca apagar backups.
- Criar saídas versionadas e identificáveis; testar scripts antes de aceitar alterações. Documentar versões, downloads, licenças e dependências externas.
- Não executar scripts de construção/render sem conferir suas saídas: alguns comandos antigos salvam cenas/bibliotecas canônicas.
- Preservar roteiro aprovado. Mudanças editoriais, voz, velocidade e tom dependem de autorização específica.

## Produção
- Narrador oficial: Gemini TTS `gemini-3.8-flash-lite-tts`, Puck, pt-BR; aprovação editorial TTS-003. Não trocar voz/modelo automaticamente nem iniciar novas buscas locais sem nova instrução.
- Perfil: `audio/perfis/narrador_principal.json`. Puck do EP001 completo e oito segmentos aprovados: reutilizar e conferir hashes. A referência é editorial, nunca autorização de clonagem.
- Reutilizar Nico, objetos, cenários, iluminação e estética estabelecidos; câmera 9:16. Validar quadros antes de sequências ou renders completos.
- Usar perfil de narrador aprovado; perfil provisório nunca substitui áudio de produção. Gerar e validar WAV antes de temporizar animação.
- Verificar áudio efetivo após muxing, usando `scripts/pipeline_v3/audio_finalizer.py`.
- Legendas pt-BR por áudio real, SRT e ASS, áreas seguras verificadas; exportar versões com e sem legendas incorporadas.
- YouTube Shorts, Instagram Reels e TikTok: sem título editorial dentro da animação, sem marca d'água; metadados separados.

## Recursos e validação
- Render e tarefas auxiliares locais quando viáveis. Geração remota de voz e paga bloqueadas por padrão; não chamar APIs nesta TTS-003. Não criar/trocar chave ou projeto para contornar cotas.
- Ambientes isolados em `venvs/`; modelos fixados em `models/`. Não alterar ambientes/configurações globais de outros projetos.
- Informar tamanho antes de downloads grandes; cada download acima de 5 GB exige aprovação. Não instalar alternativas em sequência sem diagnóstico.
- Não concorrer benchmarks TTS com render Blender ou modelos grandes. Medir RAM/VRAM; sem repetição indefinida após OOM.
- Testes atuais: `python testes/test_ep001_narracao.py` e `python testes/tts_003/test_generation_policy.py`. Suites locais anteriores são históricas após retirada da referência pessoal/arquivamento de modelos.
- Fluxo: `documentos/PIPELINE_PRODUCAO.md`; consumo: `documentos/POLITICA_NARRACAO_E_COTAS.md`; estado atual: `documentos/RELATORIO_TTS_003.md`.

## Organização permanente
- Para trabalho reutilizável de estúdio, consultar primeiro `documentos/ESTUDIO_NICO.md`, os prompts P01–P06 em `documentos/prompts/` e `documentos/CRITERIOS_QUALIDADE.md`. Registrar aprovação de recursos compartilhados no catálogo e de entregas no índice do episódio.

- Abrir o índice do episódio antes de investigar o histórico. Atualizá-lo a cada entrega e registrar a aprovação com precisão.
- Usar um único `TESTES/` ativo por episódio. Colocar vídeos e projetos para revisão em `ENTREGAS/` e recursos reutilizáveis nas bibliotecas globais.
- Arquivar versões substituídas em `arquivo/<episodio>/`. Preservar os aprovados, backups, evidências e manifestos originais.
- Reutilizar `scripts/` e a resolução de raiz do pipeline. Criar somente a menor mudança necessária, sem refatorações alheias.
- Concentrar temporários em `.cache/<episodio>/` e retirar somente caches comprovadamente regeneráveis após validação.
- Evitar pastas de missão na raiz e novas árvores `producao_vN` sem justificativa arquitetural.
- Usar um registro consolidado por mudança. Consultar resumos, manifestos e logs pontuais antes de repetir leituras, builds ou renders.
- Nos saves automatizados Blender, aplicar `file_preview_type = 'NONE'` apenas no processo de salvamento. Conferir novas pastas inesperadas sem alterar preferências globais.
- Exigir decupagem técnica por plano antes de iniciar uma cena e teste localizado de rig antes de animar uma ação complexa. Conservar as fontes aprovadas e versionar as cópias.
- Auditar quadros-chave antes de renderizar um plano longo. Usar `scripts/producao/render_plan.py` para validar um quadro, intervalo ou plano. Não renderizar o episódio para verificar uma articulação.
- Manter provas de cena em `TESTES/` e o cache dessas provas em `TESTES/cache/`. Usar o índice para localizar o resultado e registrar apenas a evidência necessária.
