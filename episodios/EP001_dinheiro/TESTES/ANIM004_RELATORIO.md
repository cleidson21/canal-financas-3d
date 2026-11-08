# ANIM-004 — Motor e pega do Nico

[Prévia de 4 s](ANIM004_RIG_V3.mp4) · [Blender editável](ANIM004_RIG_V3.blend) · [Comparativo](ANIM004_COMPARATIVO.png) · [Resultados medidos](ANIM004_RESULTADOS.json)

## Rig e pega

O Blender confirmou controles Empty em cadeia tronco → braço → antebraço. A armature deformadora segue os controles via `COPY_TRANSFORMS`. A palma e o polegar são malhas, com o braço estendido aproximadamente em −Z e a frente de Nico em −Y. A prova reutiliza as malhas originais. O novo punho gira a mão, e a propriedade `grip` (0,0 aberta, 1,0 fechada) move o polegar existente. O primeiro ensaio revelou que um valor inteiro tornava o fechamento discreto e que a abertura deixava o polegar separado. A versão final usa um valor contínuo e uma amplitude que mantém as malhas unidas.

Na prova a 30 FPS, o olhar antecede o alcance, o tronco inclina discretamente e o braço esquerdo contrabalança. A batata permanece na bancada até a confirmação geométrica da pega fechada no quadro 64 (2,10 s). Na pose final ela continua visível em frente ao corpo. A auditoria verificou 239 amostras por variante em três posições próximas do alvo. O comparativo mostra os dois ângulos e as etapas de alcance, contato, retirada e sustentação. A avaliação de naturalidade foi visual, com revisão artística humana pendente.

## Motor

- **Bake.** Três execuções comparáveis da trajetória original deram mediana de **21,46 s → 8,76 s** (−59%). A composição analítica retirou 8.416 atualizações explícitas internas. As duas avaliações por quadro foram mantidas para as matrizes do corpo e as transferências. As posições avaliadas dos comerciantes e dos pés ficaram dentro de 0,000002 unidade da referência.
- **Alcance.** O erro original de 0,031567 no quadro 30 vem de um alvo direito a 0,5465 unidade do ombro, ante 0,5159 de comprimento total. O modo anatômico reduz cruzamentos e inversões na trajetória antiga, mas o alvo esquerdo do quadro 472 fica perto demais para o limite de 120°. O modo é opcional para trajetórias compatíveis, e o construtor interrompe o save acima de 0,005 unidade de erro.
- **Render.** Os mesmos seis quadros de auditoria em dois planos da Cena 3 levaram **78,48 s em processos separados e 40,31 s em lote**. A retomada reaproveitou os seis. Em lote, o projeto abre uma vez, e cada plano conserva sua câmera e seu cache verificado. O ponto de entrada que aceitava PNGs pela existência do arquivo foi desativado. Consulte os [comandos do renderizador](../../../scripts/producao/README.md#render-incremental-por-plano).

A pega estilizada cobre uma batata, sem articulação independente de dedos. A próxima revisão deve avaliar a prova e só então ajustar alvos e testar trocas entre personagens. O .blend de entrega da Cena 3 e sua decupagem continuam como referência.
