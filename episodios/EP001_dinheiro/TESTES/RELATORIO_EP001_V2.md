# Relatório de Produção e Validação — EP001-V2 (Episódio Completo 3D)

## 1. Resumo da Entrega (`EP001_V2`)

Produção integral em 3D contínuo (3.064 quadros a 30 FPS, `102,133s`, vertical 9:16) das oito cenas do episódio **"Como seria viver SEM DINHEIRO?"**, preservando integralmente a narração aprovada Gemini TTS `Puck` (`102,12s`) e todas as versões/bibliotecas anteriores.

### Entregáveis Finais (`episodios/EP001_dinheiro/ENTREGAS/`)

| Arquivo | Especificação | SHA-256 | Status |
|---|---|---|---|
| [EP001_COMPLETO_V2_COM_LEGENDAS.mp4](file:///c:/Users/Cleidson/Videos/canal-financas-3d/episodios/EP001_dinheiro/ENTREGAS/EP001_COMPLETO_V2_COM_LEGENDAS.mp4) | `1080×1920`, 30 FPS, H.264 + AAC 24 kHz, legendas ASS incorporadas | `75fcd88c98d8d7924c89b018465161969acfca2c6c9a80dbe49022746b74b8f8` | Validado (`0` erros de decode) |
| [EP001_COMPLETO_V2_SEM_LEGENDAS.mp4](file:///c:/Users/Cleidson/Videos/canal-financas-3d/episodios/EP001_dinheiro/ENTREGAS/EP001_COMPLETO_V2_SEM_LEGENDAS.mp4) | `1080×1920`, 30 FPS, H.264 + AAC 24 kHz, sem legendas incorporadas | `f34c018d1510dc9ad895467bafc2a9beb194d0356d6c16a1587ca425d3f94e85` | Validado (`0` erros de decode) |
| [EP001_PREVIA_V2.mp4](file:///c:/Users/Cleidson/Videos/canal-financas-3d/episodios/EP001_dinheiro/ENTREGAS/EP001_PREVIA_V2.mp4) | `360×640`, 30 FPS, H.264 + AAC 24 kHz, prévia completa leve | `b9578e9947bc40c21fddefa22d6dd6bda854a3af099998f3c938cb2cca64a8e9` | Validado (`0` erros de decode) |
| [EP001_COMPLETO_V2_EDITAVEL.blend](file:///c:/Users/Cleidson/Videos/canal-financas-3d/episodios/EP001_dinheiro/ENTREGAS/EP001_COMPLETO_V2_EDITAVEL.blend) | Projeto 3D mestre editável com todas as 8 cenas, 24 câmeras e faixa VSE | Gerado em `181,33s` (`file_preview_type='NONE'`) | Validado |

---

## 2. Status por Cena e Melhorias Realizadas

- **Cena 1 (`S01` — quadros `1..185` | `0,00s..6,13s`) — O sapato pediu demissão**:
  - Abertura direta sem título ou vinheta no passo do Nico, com a sola frontal direita descolada abrindo em *"boca de jacaré"*, enganchando na pedra do caminho no quadro `42`, pico de tropeço corporal com braços em moinho no quadro `55` (enquadramento ajustado para preservar o boné e corpo inteiro) e revelação panorâmica da feira da vila com o selo contextual 3D *Sem Dinheiro*.
- **Cena 2 (`S02` — quadros `186..592` | `6,17s..19,70s`) — A primeira tentativa**:
  - Gesto de ideia, agachamento de antecipação e levantamento pesado do saco de 40 kg de batatas (`q238..256`), caminhada de 4 passos plantados até a barraca do sapateiro, arremesso no balcão (`PLOC!` em `q318` com *squash & stretch* e poeira), recusa do sapateiro com aceno negativo e pedido de leite, e reação cômica de frustração do Nico com o *Carimbo da Dúvida*.
- **Cena 3 (`S03` — quadros `593..1121` | `19,73s..37,33s`) — Uma sorte inacreditável**:
  - Integração das melhorias `PROD-002` + `ANIM-004`: polo de cotovelo relativo ao tronco (`pose_arm`), pega com oposição de polegar (`set_nico_grip`), aventais orgânicos moldados ao tronco dos comerciantes, entrega de batatas (`q710`) por peixe (`q770`), caminhada até o lenhador com chegada antecipada da câmera (`q818`), entrega do peixe (`q860`) por lenha pesada (`q905` com afundamento físico da pelve) e close expressivo com sobrancelha assimétrica em *"Isso tá fácil demais"*.
- **Cena 4 (`S04` — quadros `1122..1557` | `37,38s..51,86s`) — A coincidência acabou**:
  - Barraca azul/branca do leiteiro (que recusa a lenha e aponta para ovos) e barraca amarela/terracota do vendedor de ovos com chapéu de palha, cestas de vime e saco de farinha (que recusa ovos e pede farinha). Setas 3D em cadeia e gag física da *transportadora* (`q1416..1557`) com Nico sustentando a pilha oscilante de caixote, saco, lenha, farinha e ovos na altura do peito, mantendo o rosto e expressão de esforço 100% visíveis.
- **Cena 5 (`S05` — quadros `1558..1837` | `51,90s..61,20s`) — Dupla coincidência de desejos**:
  - Nico exausto no centro aberto da feira (`X=10,75`), cercado pelas mercadorias no chão e com a sola rasgada aberta em primeiro plano (`S05_P01`), seguido pelo plano aberto (`S05_P02`) que demonstra visualmente a falha da dupla coincidência de desejos entre as barracas sem obstruir o rosto de nenhum comerciante.
- **Cena 6 (`S06` — quadros `1838..2444` | `61,23s..81,43s`) — A ideia da ficha**:
  - Apresentação da **Ficha de Madeira** (`ficha_pagamento`) entalhada e surgimento sequencial das placas verdes de aceitação nas barracas (`S06_P01`), seguidos por três negócios distintos em três planos dedicados:
    1. `S06_P02`: Nico vende batatas e recebe fichas de madeira (`q2112..2152`).
    2. `S06_P03`: Nico entrega as fichas ao sapateiro (`q2208`), recebe e calça os sapatos novos vermelhos e dourados (`q2242`, ocultando a malha do tênis antigo sem sobreposição).
    3. `S06_P04`: O sapateiro (com pernas/botas e avental ajustado) vai até a barraca do leiteiro, paga com a mesma ficha (`q2330`), recebe a garrafa de leite (`q2375`) e comemora em *"Agora sim!"*.
- **Cena 7 (`S07` — quadros `2445..2861` | `81,48s..95,33s`) — Confiança**:
  - Close da ficha de madeira na mão do Nico (`S07_P01`), circulação positiva com acenos de confiança mútua entre os comerciantes (`S07_P02`) e contraponto visual (`S07_P03`) em que a placa sobre o balcão do lenhador vira recusa (`X` vermelho posicionado acima do balcão, livre do rosto do lenhador) e a ficha pousada ao lado das toras volta a ser vista como um simples pedaço de madeira.
- **Cena 8 (`S08` — quadros `2862..3064` | `95,38s..102,13s`) — Fechamento e pergunta final**:
  - Callback visual direto à Cena 1 (`S08_P01`) em plano de corpo inteiro mostrando Nico dando passos alegres e batendo o pé direito com o tênis novo vermelho e dourado firme e intacto, encerrando com o convite ao espectador diante das mercadorias da jornada no balcão (`S08_P02`).

---

## 3. Resultados dos Testes e Validação Técnica

1. **Testes Oficiais do Projeto**:
   - `python testes/test_ep001_narracao.py` → `RESULTADO: OK` (todos os WAVs, textos, durações, SRT/ASS e arquivos protegidos verificados e intactos).
   - `python testes/tts_003/test_generation_policy.py` → `Ran 8 tests in 0.430s — OK` (zero chamadas à API TTS).
2. **Validação Audiovisual (`scripts/pipeline_v3/audio_finalizer.py`)**:
   - Relatório completo salvo em [EP001_V2_VALIDACAO.json](file:///c:/Users/Cleidson/Videos/canal-financas-3d/episodios/EP001_dinheiro/TESTES/EP001_V2_VALIDACAO.json).
   - `RMS ativo`: `-17.59 dBFS` (diferença de `0.02 dB` em relação ao WAV original `-17.57 dBFS`).
   - `Peak`: `-1.01 dBFS` (diferença `0.0 dB`).
   - `Lag de sincronia`: `0.0 ms` (`0` amostras).
   - `Correlação de forma de onda`: `0.999907` (`envelope 10ms`: `0.999992`).
   - Todas as `28` frases dos 8 segmentos verificadas individualmente quanto a nível RMS e integridade.
3. **Pranchas de Auditoria Visual (`episodios/EP001_dinheiro/TESTES/cache/auditoria_v2/`)**:
   - [AUDITORIA_EP001_V2_ITER2_PARTE_1.png](file:///c:/Users/Cleidson/Videos/canal-financas-3d/episodios/EP001_dinheiro/TESTES/cache/auditoria_v2/AUDITORIA_EP001_V2_ITER2_PARTE_1.png)
   - [AUDITORIA_EP001_V2_ITER2_PARTE_2.png](file:///c:/Users/Cleidson/Videos/canal-financas-3d/episodios/EP001_dinheiro/TESTES/cache/auditoria_v2/AUDITORIA_EP001_V2_ITER2_PARTE_2.png)
   - [AUDITORIA_EP001_V2_ITER2_PARTE_3.png](file:///c:/Users/Cleidson/Videos/canal-financas-3d/episodios/EP001_dinheiro/TESTES/cache/auditoria_v2/AUDITORIA_EP001_V2_ITER2_PARTE_3.png)

## 4. Pendências

- **Revisão humana final**: Assistir a [EP001_COMPLETO_V2_COM_LEGENDAS.mp4](file:///c:/Users/Cleidson/Videos/canal-financas-3d/episodios/EP001_dinheiro/ENTREGAS/EP001_COMPLETO_V2_COM_LEGENDAS.mp4) para aprovação editorial e artística definitiva antes da publicação.

