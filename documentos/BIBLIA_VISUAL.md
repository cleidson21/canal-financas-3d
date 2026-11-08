# Bíblia Visual — Canal 3D de Finanças com Nico (V3)

Este documento é a Bíblia dos Personagens e da identidade visual do estúdio. Aparência oficial do Nico em [nico_base.blend](../personagens/nico_base.blend), com construção em [character_nico.py](../scripts/pipeline_v3/character_nico.py). As descrições de poses, enquadramentos e tempos abaixo pertencem à V3 do piloto e precisam de validação na ação atual.

Para comerciantes, consultar [assets.py](../scripts/producao/assets.py), funções `merchant` e `THEMES`, e as bibliotecas do [catálogo](ESTUDIO_NICO.md). Pescador, lenhador, leiteiro e vendedor de ovos têm implementações procedurais. A ficha de aprovação artística individual e a caracterização editorial permanente de cada papel aguardam preenchimento. A mão atual tem palma e polegar separados. Controles de pega dependem da hierarquia escolhida.


## 1. Direção de Arte e Identidade Estética

O canal adota a estética **Stylized Toy / Clay 3D Educativo** voltada para vídeos verticais (`9:16`, `1080×1920`, `30 FPS`), combinando:
- **Formas Limpas e Táteis**: Superfícies suaves com chanfros generosos (*bevels*) e subdivisão controlada (*Subdivision Surface*), eliminando quinas poligonais duras ou blocos separados nas articulações.
- **Leitura Instantânea em Telas Mobile**: Composição com silhuetas claras, fundo desobstruído atrás dos pontos focais e ícones gráficos 3D autoexplicativos (como a Placa Vermelha `X` e a Placa Azul de Leite com caixa 3D, copo cheio e check verde `✓`).
- **Iluminação Quente de Manhã de Feira**: Sistema de 4 pontos com luz chave solar quente (`Sol_Principal`), preenchimento suave celeste (`Luz_Preenchimento`), luz de recorte traseira (`Luz_Recorte_Rim`) para separar o personagem do fundo e luz dedicada de destaque (`Luz_Destaque_Sapato`) para leitura imediata da sola descolada no *Cold Open*.

---

## 2. Protagonista: Nico V3

### 2.1. Proporções e Anatomia Estilizada
- **Altura Total**: `~1.72 m` em unidades de cena do Blender (`Z = 0.0` na sola do pé até o topo do boné).
- **Proporção Cabeça-Corpo**: Estilo * Toy / Chibi Equilibrado* (~`1 : 3.6`), garantindo que as expressões faciais (olhos, sobrancelhas e boca) sejam perfeitamente legíveis mesmo em planos médios no celular.
- **Membros Contínuos com Armature (`Nico_Armature_V3`)**:
  - Na V3, os braços (`Nico_Braco_Continuo_L/R`) e pernas (`Nico_Perna_Continua_L/R`) são **malhas tubulares contínuas** deformadas suavemente por esqueleto (`Armature` com *Preserve Volume / Dual Quaternion* + *Subdivision Surface*).
  - Isso elimina completamente os vãos retangulares e desconexões de cotovelo/joelho que existiam na V2.
- **Rosto e Cabeça**:
  - Olhos expressivos com esclera branca, íris escura e **duplo brilho especular (*catchlights*)** que dão vida imediata ao olhar.
  - Bochechas levemente coradas (`Mat_nico_cheeks`), orelhas laterais com cavidade interna, nariz arredondado, boca com interior escuro e língua visível.
  - Cabelo castanho-escuro estilizado (`Nico_Cabelo_Base`, costeletas e tufo frontal) encaixado sob o **boné azul com aba curva** (`Nico_Bone_Aba`) e emblema frontal branco.

### 2.2. Estados de Expressão Facial (`_set_facial_expression`)
O rosto do Nico possui 6 estados pré-configurados em [`anim_character.py`](../scripts/pipeline_v3/anim_character.py):
1. `neutral`: Sobrancelhas relaxadas, boca neutra.
2. `worried_shoe`: Cantos internos das sobrancelhas erguidos em preocupação ao olhar para a sola descolada.
3. `surprised`: Sobrancelhas arqueadas no alto e boca aberta em `"O"` (usado no tropeço em `1.5s` e no susto da recusa em `11.7s–12.5s`).
4. `happy_idea`: Sobrancelhas confiantes e sorriso largo otimista (usado em `3.5s` ao ter a ideia de trocar as batatas e em `9.5s` ao ofertá-las no balcão).
5. `effort`: Sobrancelhas contraídas em esforço físico ao levantar e carregar o saco de 40 kg de batatas (`4.0s–8.5s`).
6. `frustrated`: Sobrancelhas franzidas em indignação cômica e boca aberta no encolher de ombros final (`14.5s`).

---

## 3. O Tênis Direito Danificado ("Boca de Jacaré")

Um dos elementos narrativos centrais do Episódio 001 é o tênis direito gasto do Nico. Na V3, sua construção geométrica em [`character_nico.py`](../scripts/pipeline_v3/character_nico.py) segue regras estritas:
1. **Proibição Absoluta de Esferas Protuberantes**: A esfera vermelha/salmão da V2 (`Nico_Dedao_Exposto_R`) foi permanentemente removida.
2. **Corpo Superior Intacto (`Nico_Tenis_Corpo_R`)**: Mantém o formato completo de um tênis escuro com biqueira branca integrada (`Nico_Tenis_Biqueira_R`), cadarços brancos e sola traseira fixa no calcanhar.
3. **Sola Frontal Fina e Articulada (`Nico_Tenis_SolaFrontal_R`)**: Placa frontal fina branca (`espessura = 0.013 m`) com palmilha interna escura (`Nico_Tenis_SolaFrontal_Interno_R`), cujo pivô fica exatamente no meio do pé (`Y = -0.008, Z = 0.016`).
4. **Abertura e Fechamento Rítmicos ("Boca de Jacaré")**:
   - Quando o pé direito levanta no passo (`frame 15`, `frame 28`, e a cada passo da caminhada), `Nico_Tenis_SolaFrontal_R` rotaciona para baixo (`+26°` a `+32°`), abrindo um vão triangular nítido entre a biqueira superior intacta e a sola fina.
   - Dentro da cavidade escura (`Nico_Tenis_FundoEscuro_R`), vê-se apenas uma faixa discreta e plana da meia vermelha (`Nico_Tenis_MeiaInterna_R`) — sem qualquer volume saindo para fora do sapato.

---

## 4. Paleta de Cores Oficial (sRGB Perceptual → Scene Linear)

| Categoria | Material | Cor sRGB `(R, G, B)` | Papel Visual |
| :--- | :--- | :---: | :--- |
| **Nico V3** | `Mat_nico_skin` | `(0.94, 0.70, 0.52)` | Pele quente suave (*subsurface* sutil) |
| **Nico V3** | `Mat_nico_shirt` | `(0.98, 0.45, 0.09)` | Camiseta laranja vibrante (alto destaque contra o verde/azul) |
| **Nico V3** | `Mat_nico_cap_blue` | `(0.14, 0.44, 0.88)` | Boné azul royal com aba curva |
| **Nico V3** | `Mat_nico_shorts_blue` | `(0.14, 0.30, 0.62)` | Bermuda azul marinho |
| **Nico V3** | `Mat_nico_shoe_body` | `(0.22, 0.23, 0.26)` | Lona cinza-chumbo do tênis gasto |
| **Nico V3** | `Mat_nico_shoe_sole` | `(0.95, 0.93, 0.89)` | Borracha off-white da sola e biqueira |
| **Feira & Props** | `Mat_burlap_sack` | `(0.68, 0.48, 0.26)` | Estopa rústica do saco de 40 kg de batatas |
| **Feira & Props** | `Mat_potato_gold` | `(0.94, 0.76, 0.32)` | Batatas douradas visíveis no topo do saco e no carrinho |
| **Feira & Props** | `Mat_new_shoe_red` | `(0.88, 0.16, 0.16)` | Vermelho vivo do par de sapatos novos desejados |
| **Feira & Props** | `Mat_new_shoe_gold` | `(0.98, 0.78, 0.16)` | Detalhes dourados metálicos dos sapatos novos |
| **Símbolos UI** | `Mat_sign_x_red` | `(0.96, 0.10, 0.10)` | `X` vermelho vivo de recusa sobre as batatas |
| **Símbolos UI** | `Mat_sign_milk_bg` | `(0.10, 0.22, 0.40)` | Fundo azul-marinho de alto contraste para a caixa de leite branca |
| **Símbolos UI** | `Mat_sign_check_green` | `(0.16, 0.84, 0.32)` | Check verde (`✓`) indicando o produto aceito pelo vendedor |
