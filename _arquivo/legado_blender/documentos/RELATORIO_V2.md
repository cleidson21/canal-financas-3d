# RELATÓRIO TÉCNICO — Evolução da Animação 3D Low-Poly (Nico 15s)

## 1. Diagnóstico do Projeto Original (`Teste1.blend` / `nico_teste_15s.py`)

A inspeção técnica e a renderização de referência de `Teste1.blend` no **Blender 5.2.3 LTS** revelaram problemas críticos que impediam seu uso visual:

1. **Cena totalmente cinza na renderização EEVEE (Bug de localização em português):**
   - No script original (`nico_teste_15s.py`), os materiais buscavam o nó shader pelo nome em inglês `mat.node_tree.nodes.get('Principled BSDF')`.
   - Como o Blender 5.2.3 LTS local cria nós com nomes traduzidos em português (`'BSDF - Pré-fundamentado'` e `'Saída de material'`), `.get('Principled BSDF')` retornava `None`.
   - Apenas `mat.diffuse_color` (cor de viewport sólida) era preenchida, deixando todos os shaders EEVEE no cinza padrão `(0.8, 0.8, 0.8)`.
2. **Personagem fora de quadro e caminhando de lado:**
   - Nos primeiros segundos (quadros 1 a 28), o Nico estava completamente fora da borda esquerda do enquadramento vertical `9:16` (apenas sua sombra aparecia).
   - O personagem foi modelado olhando para `-Y`, mas deslocava-se em `+X` deslizando sem rotação corporal nem articulação de membros ("crab-walking" de lado).
3. **Saco de batatas flutuando no quadro inicial e abandonado no chão:**
   - Nos quadros iniciais (`0–2s`), o cubo do saco de batatas já aparecia pendurado no canto superior esquerdo e projetava sombra antes do momento da queda.
   - Após cair, o saco ficava para trás no chão enquanto o Nico deslizava sozinho até o balcão, quebrando a lógica narrativa da tentativa de troca no balcão.
4. **Ausência dos elementos narrativos obrigatórios do storyboard:**
   - Não havia sapato danificado visível (`0–2s`).
   - Não havia produto desejado na loja (par de sapatos novos) nem vendedor.
   - Havia apenas uma placa `X` sem contraste, faltando completamente o **símbolo de leite** (`11–13s`) e a **reação cômica de frustração** (`13–15s`).
5. **Taxa de quadros fora da especificação:**
   - `Teste1.blend` estava configurado em `24 FPS` (`360 quadros`), enquanto o storyboard exigia `30 FPS` (`450 quadros` para 15 segundos).

---

## 2. O Que Foi Melhorado em `Teste1_V2.blend`

| Dimensão | Protótipo Original (`Teste1.blend`) | Nova Versão (`Teste1_V2.blend`) |
| :--- | :--- | :--- |
| **Taxa e Duração** | 24 FPS (360 quadros) | **30 FPS exatos (450 quadros = 15,0 s)** |
| **Materiais e Cores** | Tudo cinza no EEVEE (falha em pt_BR) | **Paleta Scene-Linear vibrante, imune ao idioma (`bl_idname`)** |
| **Personagem Nico** | 9 cubos/esfera estáticos sem rosto nem articulação | **Hierarquia articulada de 19 pivôs/partes**, cabeça expressiva, olhos com brilho, sobrancelhas e boca animadas, mãos com polegar |
| **Sapato Danificado** | Inexistente (dois cubos marrons iguais) | **Tênis direito rasgado com sola frontal articulada** ("boca de jacaré") + meia vermelha e dedão expostos |
| **Cenário da Feira** | 4 blocos lisos sem contexto | **Vila low-poly completa**: caminho de terra e pedras, árvores em camadas, colinas, 3 casas ao fundo, nuvens, barraca com toldo listrado, prateleiras, caixotes, par de tênis novos em exposição e Vendedor |
| **Saco de Batatas** | Cubo marrom que caía e ficava para trás | **Saco de estopa modelado com corda e batatas douradas**, queda acelerada + *squash & stretch* + poeira de impacto, **carregado pelo Nico** e **depositado sobre o balcão (`Z = 0.96`)** |
| **Símbolos de Recusa** | Apenas um X fino (cinza no render) | **Placa 3D com X vermelho em alto-relevo** + **Placa azul-marinho com Caixa de Leite 3D, Copo de Leite e Check Verde (`✓`)** com animação elástica (*overshoot*) |
| **Cinematografia** | Câmera ortográfica quase parada, cortando o personagem | **Câmera em perspectiva (`45mm`) com `TRACK_TO` (`Camera_Target`)** e 6 movimentos dedicados ao formato vertical `9:16` |

---

## 3. Componentes Construídos 100% por Python (`pipeline_v2/`)

Todo o projeto é gerado sem dependências externas por uma arquitetura modular dividida em 9 módulos especializados:

1. [`config.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/config.py): Centraliza resolução (`1080×1920`), `FPS = 30`, `FRAME_END = 450`, tempos exatos dos 6 beats do storyboard, coordenadas de palco e paleta convertida de sRGB para Scene Linear (`_srgb_to_linear`).
2. [`scene_setup.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/scene_setup.py): Limpeza idempotente de blocos de dados órfãos, criação das 5 coleções organizadas, configuração do EEVEE / AgX e utilitário `iter_object_fcurves` compatível com a nova API de **Slotted Actions (`act.layers[].strips[].channelbags[].fcurves`) do Blender 5.2**.
3. [`primitives.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/primitives.py): Construtores geométricos baseados em `bmesh` + modificador `BEVEL` (caixas chanfradas, troncos piramidais, cilindros, icosferas, esferas UV e telhados de duas águas), independentes de seleção ativa de viewport.
4. [`materials_lighting.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/materials_lighting.py): Criação de materiais localizando nós por `node.bl_idname == 'ShaderNodeBsdfPrincipled'` e iluminação cinematográfica de 3 pontos (`Sol_Principal` quente com sombras suaves, `Luz_Preenchimento` de área, `Luz_Recorte_Rim` de contraluz e `Luz_Barraca_Interna`).
5. [`environment_fair.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/environment_fair.py): Construção procedural da vila (`Col_Cenario_Vila`) e da barraca de sapatos (`Col_Feira_Barraca`).
6. [`character_nico.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/character_nico.py): Modelagem e montagem hierárquica do Nico (`Col_Personagem_Nico`) e do Vendedor.
7. [`anim_props.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/anim_props.py): Animação do saco de batatas (queda quadrática, impacto com *squash & stretch*, partículas de poeira, transporte nas mãos do Nico e pouso no balcão) e das placas de recusa (`X` vermelho e `Leite`).
8. [`anim_character.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/anim_character.py): Animação por keyframes do Nico (inspeção do sapato furado, pulo de susto, agachamento para pegar o saco, ciclo de caminhada de 6 passos com flexão de joelho/tornozelo sem deslizar, oferta no balcão e reação final de frustração) e aceno negativo do Vendedor.
9. [`cinematography.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/cinematography.py) e [`render_pipeline.py`](file:///C:/Users/Cleidson/Videos/canal-financas-3d/pipeline_v2/render_pipeline.py): Coreografia de câmera vertical `9:16` e automação de renderização PNG e vídeo MP4 H.264.

---

## 4. Movimentos Implementados e Validados

- **0–2s (Quadros 1–60):** Dolly-in da câmera destacando o Nico levantando o pé direito; a sola frontal descolada abre e fecha duas vezes exibindo a meia vermelha e o dedão enquanto Nico olha preocupado para o sapato.
- **2–4s (Quadros 60–120):** Queda acelerada do saco de batatas no quadro 61–74, impacto no chão com forte *squash* (`scale = (1.36, 1.36, 0.56)`), expansão de 6 nuvens de poeira low-poly, pequeno quique de *stretch* e acomodação; Nico salta assustado, levanta as sobrancelhas e depois tem a ideia de usar o saco para trocar pelo sapato novo.
- **4–8s (Quadros 120–240):** Nico caminha até o saco, agacha flexionando joelhos e tronco (quadro 136), ergue o saco de batatas e realiza um ciclo de caminhada articulado de 6 passos até o balcão acompanhado por um *tracking shot* suave da câmera.
- **8–11s (Quadros 240–330):** Nico deposita o saco de batatas exatamente sobre o tampo do balcão (`Z = 0.96`, sem flutuar nem atravessar a madeira) ao lado do par de tênis novos vermelhos e dourados; Nico aponta propondo a troca enquanto o Vendedor olha para o saco e balança a cabeça negativamente.
- **11–13s (Quadros 330–390):** Surge a placa com o **X vermelho** em escala elástica rápida (quadros 332–348), seguida da placa azul-marinho com a **Caixa de Leite 3D, Copo de Leite e Check Verde (`✓`)** (quadros 360–378).
- **13–15s (Quadros 390–450):** Nico leva as mãos à cabeça em descrença e depois desaba os ombros e o tronco em frustração cômica, virado para a câmera com sobrancelhas franzidas e boca aberta, enquanto a câmera fecha em plano médio-próximo.

---

## 5. Erros Encontrados Durante o Desenvolvimento e Como Foram Corrigidos

1. **Quebra da API `image_settings.file_format = 'FFMPEG'` no Blender 5.2:**
   - *Erro:* No Blender 5.0+, definir `file_format = 'FFMPEG'` diretamente levanta `TypeError` porque `image_settings.media_type` inicia em `'IMAGE'`.
   - *Correção:* Configurar `scene.render.image_settings.media_type = 'VIDEO'` antes de definir `ffmpeg.format = 'MPEG4'` e `ffmpeg.codec = 'H264'`.
2. **Nova arquitetura de Slotted Actions no Blender 5.2:**
   - *Erro:* No Blender 5.2, `action.fcurves` foi substituído pela hierarquia `action.layers -> strip.channelbags -> bag.fcurves`.
   - *Correção:* Implementada a função `iter_object_fcurves(obj)` em `scene_setup.py` que percorre `channelbags` para aplicar interpolação `BEZIER` com `AUTO_CLAMPED` em todos os keyframes.
3. **Cores pastel / lavadas na Iteração 1 de autoavaliação visual:**
   - *Causa:* O Blender espera valores `Base Color` em **Scene Linear RGB**, não em sRGB perceptual, e o fundo do mundo (`0.85`) + luz de preenchimento (`160W`) sob o transform `AgX` lavavam o contraste. Adicionalmente, a caixa de leite branca sobre placa branca tinha baixo contraste.
   - *Correção (Iteração 2):* Adicionada conversão matemática `_srgb_to_linear` na paleta, ajuste da exposição e luzes, elevação do toldo da barraca para `Z = 2.92` e criação de fundo azul-marinho escuro (`Mat_sign_milk_bg`) para a placa do leite.
4. **Geometria do ícone de Check Verde e margem esquerda de câmera (Iterações 3 e 4):**
   - *Causa:* Na Iteração 2, as duas hastes do check verde encontravam-se no topo em vez do vértice inferior, e o ombro direito do Nico tocava a borda esquerda nos quadros `285–430`.
   - *Correção (Iterações 3 e 4):* Recalculada a trigonometria das hastes do check `✓` em torno do vértice inferior `(0.17, -0.055, 0.13)` e recuada suavemente a câmera no eixo `Y` (`-5.22m`) e `X` para garantir margem lateral confortável tanto para o Nico quanto para a placa do leite.

---

## 6. Dependências Externas e Reutilização

- **Dependência de recursos externos:** **Zero (0%).** A cena não utiliza modelos externos, texturas de imagem, Mixamo, plugins pagos nem conexão com a internet. Tudo é construído matematicamente via `bpy` e `bmesh`.
- **Elementos prontos para reutilização em próximos episódios:**
  - O módulo `character_nico.py` pode gerar o Nico (com sapato consertado ou danificado) em qualquer cena.
  - O módulo `environment_fair.py` fornece árvores low-poly, casas distantes, caminho de pedras e barraca de feira parametrizáveis.
  - O módulo `anim_props.py` fornece placas de ícones 3D com animação *overshoot* para representar qualquer conceito econômico futuro (moedas, trigo, peixe, inflação, juros).

---

## 7. O Que Ainda Pode Ser Evoluído para Produção Contínua no YouTube

1. **Rigging com Armature + Inverse Kinematics (IK) e Deformação de Malha (Skinning):**
   - Atualmente o Nico usa uma hierarquia articulada de objetos rígidos parentados a pivôs (`EMPTY`), ideal para estética *toy / maquete low-poly*. Caso se deseje dobrar cotovelos e joelhos com malha contínua sem divisão visível de segmentos, o próximo passo é converter os pivôs em `bpy.types.Armature` com pesos de vértices (*Vertex Groups*).
2. **Edição de Áudio e Sound Design (Pós-produção):**
   - Adicionar a locução do narrador, trilha sonora leve em estilo *pizzicato / ukulele*, o efeito sonoro **"PLOC!"** no quadro 74 (queda do saco), passos nos quadros 148–236, som de *pop/buzzer* no quadro 338 (`X` vermelho), *ding* no quadro 366 (símbolo de leite) e efeito de *trombone triste / suspiro* no quadro 418.

