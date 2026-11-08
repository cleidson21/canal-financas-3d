# API de produção 3D — prova PROD-002

Ferramentas locais para Blender 5.2.3 LTS; reaproveitam `pipeline_v3` e a geometria/rig original do Nico. Nenhum módulo gera voz ou acessa APIs. Não há dependência de MCP para executar.

## Recursos

- `assets`: estruturas de barraca parametrizadas por materiais, expositores e decoração; três papéis de comerciante a partir da mesma malha de cabeça aprovada e esquema de pivôs; mercadorias com pontos de apoio. As bibliotecas exportadas são neutras e ficam nos diretórios compartilhados do projeto.
- `motions`: solver de dois elos aplicado aos controles existentes, curvas com duração/intensidade, `offer`, `accept`, `refuse`, `deliver`, `receive`, `point`, `surprise`, `satisfaction`, `distrust`, `transport`, `look_at`, `settle`. `bind_transfer` usa offsets distintos de pega, um único objeto e frame de troca de posse. Não é simulação de dedos ou física rígida.
- `cameras`: presets `wide`, `medium`, `goods_close`, `reaction_close`, `negotiation`, `comparative`. `shot` combina duração, deslocamento de câmera/alvo e cortes por marcadores. Travelling e aproximação são parâmetros de `travel`/`target_travel`, não movimentos aleatórios.
- `build_scene`: composição demonstradora de duas trocas a partir de uma especificação JSON. Bake em keyframes normais; abrir o `.blend` não exige handlers nem executar scripts embutidos. A especificação é um ponto de entrada simples, não um editor ou gerador universal de qualquer história.
- `render_scene`: auditar antes, depois renderizar TODOS os quadros temporais da cena; cache retomável, sem duplicar holds. `render_variants` isola as três bibliotecas para inspeção.
- `validate_scene`: verifica abertura, rig, curvas, câmeras, quatro contatos, separação de mercadorias e apoio dos pés. A validação geométrica não substitui a inspeção visual.
- `finish_preview`: encode contínuo, finalizador de áudio existente e comparação com o V1. Usa somente Pillow/numpy já instalados no ambiente, sem importar motores TTS.

## Nova cena

Criar uma especificação versionada com episódio, segmento, timing canônico, fonte de Nico/cenário, personagens, barracas, mercadorias, resolução, FPS e saída. Ler as frases do segmento e planejar ações/cortes com tempos locais. Para histórias além das duas trocas demonstradas, compor uma função de atuação usando os módulos; não copiar a geometria ou um script inteiro para cada episódio.

No Blender, anexar a coleção desejada de `cenarios/barracas_PROD002_V2.blend` e o papel correspondente de `personagens/comerciantes_PROD002_V2.blend`; posicionar seus roots. As coleções têm a mesma origem e sockets documentados no objeto-raiz. `objetos/mercadorias_PROD002_V2.blend` contém os objetos neutros de troca. Configurações ficam em `assets.THEMES`; não editar bibliotecas aprovadas em lugar.

Coordenar as mãos do doador e receptor nos lados opostos do objeto, conferir alcance e distância entre palmas e usar offsets de apoio consistentes. Na transferência, os dois pontos de suporte devem reconstruir o mesmo centro da mercadoria. Keyframes de apoio dos pés ficam no mundo para evitar deslizamento ao virar o corpo. Usar movimentos completos quando a fala descreve ação; reservar holds expressivos para pausas justificadas.

Antes de renderizar, validar contatos, enquadramento e quadros-chave. Depois, medir o vídeo decodificado e comparar com a fala real. Preservar os WAVs, caminhos e hashes. Uma nova versão de vídeo exige outro nome/pasta; o finalizador não deve sobrescrever uma prévia existente.

## Executar a prova atual, a partir da raiz

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$spec = 'episodios/EP001_dinheiro/TESTES/cena03.json'
# Validar a entrega atual sem construir nem renderizar.
& $blender -b --factory-startup --disable-autoexec --offline-mode --python-exit-code 1 -P scripts/producao/validate_scene.py -- $spec episodios/EP001_dinheiro/ENTREGAS/CENA03_EDITAVEL.blend

# Para uma reconstrução autorizada, usar uma saída livre em .cache/EP001/.
& $blender -b --factory-startup --disable-autoexec --offline-mode --python-exit-code 1 -P scripts/producao/build_scene.py -- $spec
& $blender -b --factory-startup --disable-autoexec --offline-mode --python-exit-code 1 -P scripts/producao/validate_scene.py -- $spec
```

O construtor recusa sobrescrever a cena. A especificação legada grava em `.cache/EP001/S03_V2/`. O ponto de entrada `render_scene.py` foi desativado porque reaproveitava PNGs pela existência do arquivo. Use o render por plano para gerar novos quadros. `finish_preview.py` continua vinculado à estrutura histórica e ao cache da prova PROD-002.

O modo `nico_arm_solver: "anatomical"` é opcional para trajetórias novas do Nico. O bake recusa salvar quando um alvo excede a tolerância de 0,005 unidade. O alvo original da mão direita no quadro 30 excede o comprimento do braço, e o alvo esquerdo no quadro 472 exige flexão acima do limite. A decupagem atual segue usando a cena de referência.

## Render incremental por plano

`render_plan.py` lê um JSON de planos e abre o `.blend` já preparado uma vez, em modo de leitura. Liste os IDs para renderizar várias câmeras na mesma sessão. A partir da raiz, use o mesmo executável do Blender:

```powershell
$teste = 'episodios/EP001_dinheiro/TESTES'
$spec = "$teste/ANIM003_PLANOS.json"
$flags = @('-b', '--factory-startup', '--disable-autoexec', '--offline-mode', '--python-exit-code', '1')
& $blender @flags -P scripts/producao/render_plan.py -- $spec corpo --frame 41
& $blender @flags -P scripts/producao/render_plan.py -- $spec corpo lateral --audit
# Inspecione as imagens em cache antes de avançar.
& $blender @flags -P scripts/producao/render_plan.py -- $spec lateral --range 38 45
& $blender @flags -P scripts/producao/render_plan.py -- $spec lateral --shot --preview "$teste/ANIM003_lateral_revisao.mp4"
```

Use um ID e a câmera existente no `.blend`, com `frames` inclusivos e `audit_frames` dentro do plano. A prévia opcional é um MP4 técnico sem áudio de um único plano, com nome novo. O cache separa as saídas por plano e pelo conteúdo do `.blend`, dependências externas do Blender, entradas adicionais declaradas em `inputs`, configuração de render e versão do motor. Cada PNG recebe SHA-256 após a verificação da gravação. Para retomar, repita o mesmo comando. Os registros `PLAN` mostram os quadros renderizados e a contagem reaproveitada. `BATCH` mostra abertura, preparação, primeiro quadro e duração da sessão. Para mover curvas ou aplicar novas poses, salve um novo `.blend` antes de renderizar.
