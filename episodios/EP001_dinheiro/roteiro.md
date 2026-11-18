# Roteiro EP001 — Como seria viver SEM DINHEIRO?

**Versão canônica:** 1.1 (reescrita de retenção; substitui a 1.0 após aprovação humana)
**Título editorial (somente metadados de publicação, nunca na animação):** Como seria viver SEM DINHEIRO?
**Duração-alvo:** 95–120 s (a duração real é determinada pelos WAVs; ver `timing.json`).
**Formato:** 9:16, 1080×1920, 30 FPS.
**Versão anterior (preservar):** mover a 1.0 para `_arquivo/roteiros_antigos/` (`roteiro_ep001_v1_0.md` e `narracao_ep001_v1_0.json`) antes de sobrescrever.

## Premissa
Nico vive numa vila costeira imaginária sem dinheiro. Tem 40 kg de batatas e precisa de sapatos novos. A troca direta falha por falta de parceiros compatíveis, nem um mapa de trocas resolve, e a vila então experimenta uma ficha comum. Quando a ficha funciona, o vídeo volta no tempo e mostra a peça escondida: ela só circula porque cada um confia que o outro também a aceitará.

**Objetivo pedagógico:** (1) dificuldade de achar parceiros compatíveis na troca direta (dupla coincidência de desejos); (2) utilidade de um meio de troca amplamente aceito; (3) a confiança, invisível, como condição para sua circulação.

**Ressalva obrigatória:** a vila é um experimento fictício. Não é reconstrução histórica universal da origem do dinheiro, as preferências dos comerciantes pertencem só a ela e, nos países reais, a confiança também vem de leis e instituições (assunto de episódios futuros).

**Regra de título:** a animação começa direto no Nico exausto (DIA 3). Sem título, vinheta, nome de canal ou "no vídeo de hoje". Legendas, ícones, placas, contador e diagramas são permitidos.

> Texto de narração = literal. Qualquer alteração deve ser feita aqui **e** em `narracao.json`; `python ferramentas/verificar_roteiro.py episodios/EP001_dinheiro` verifica a igualdade.

## Identidade do canal neste episódio
- **Contador DIA** no canto da tela (DIA 3 → rebobina → DIA 1 → DIA 2 → DIA 3 → DIA 4 ✓). O tempo gasto é o custo do problema.
- **Voltar ao começo:** ícone de rebobinar com linhas de varredura; o cubo **PLOC!** cai e vira o contador (assinatura visual).
- **Piada recorrente:** todo episódio começa com algo do Nico que "pediu demissão" e representa o problema (aqui, o sapato).
- **Fechamento:** "Parabéns", com o contador virando ✓.

## Mapa de gatilhos
| # | Gatilho | Onde | Peça visual |
|---|---|---|---|
| 1 | Abertura no ponto mais baixo + lacuna de curiosidade | S01 | Nico descalço com a torre, DIA 3 |
| 2 | Rebobinar | S01, S09 | Ícone ◀◀, linhas de varredura, cubo PLOC! |
| 3 | Contador DIA | S01–S10 | Contador no canto |
| 4 | Pilha cresce, saco encolhe | S03–S06 | Pilha nas costas do Nico |
| 5 | Falso sucesso, depois erro | S03–S04 | Dois ✓ seguidos, depois X |
| 6 | Solução que falha de forma engraçada | S05 | Mapa que dá a volta |
| 7 | Gancho que se fecha | S06 | Mesmo plano da abertura, DIA 3 |
| 8 | Escala absurda | S06 | Zoom-out: vila inteira de Nicos |
| 9 | Solução nomeada + ponte com o cotidiano | S08 | Ficha vira objetos; padaria |
| 10 | Rebobinar tardio revela a causa | S09 | Instante do S07 em que o sapateiro olha o leiteiro |
| 11 | Fechamento de conquista + gancho + loop | S10 | Parabéns, ✓, sapato descola |

---

## Cena 1 — DIA 3
**Visual:** Plano médio no terraço baixo, fim de tarde. Nico descalço e exausto, equilibrando uma torre absurda (saco de batata, peixe, lenha, galão de leite, caixa de ovos, saco de farinha). Contador DIA 3 no canto. Na última frase: ícone de rebobinar com linhas de varredura; o cubo PLOC! cai, vira o contador e a cena volta ao DIA 1.

**Gatilho:** Gancho no ponto mais baixo; lacuna de curiosidade (a coisa que você usa e não vê); rebobinar; contador; assinatura PLOC!

**Narração (S01):**
Dia três. O Nico continua sem sapato, e agora carrega meia vila nas costas.

O que faltava pra ele é uma coisa que você usa todo dia sem nem ver.

Vamos voltar ao começo.


## Cena 2 — DIA 1
**Visual:** Close da sola descolando e saindo de cena como quem pede demissão; Nico dá o passo e tropeça. A câmera recua e revela a vila costeira em terraços. Nico mostra o saco ao sapateiro, que recusa: X vermelho sobre as batatas e ícone grande de leite sobre a barraca.

**Gatilho:** Piada recorrente 'pediu demissão'; falha mostrada na hora (X)

**Narração (S02):**
Dia um. O sapato do Nico pediu demissão, e na vila dele ninguém usava dinheiro.

Mas ele tinha quarenta quilos de batata, e achou que dava pra trocar por um par novo.

Só que o sapateiro não queria batata. Queria leite.


## Cena 3 — DIA 1
**Visual:** Cortes rápidos. Barraca do pescador: batatas viram peixe, sinal verde. Barraca do lenhador: peixe vira lenha, sinal verde. O saco de batatas encolhe e a pilha nas costas do Nico cresce a cada troca.

**Gatilho:** Falso sucesso; pilha que cresce

**Narração (S03):**
Então o Nico trocou batata por peixe, e peixe por lenha.

Duas trocas seguidas dando certo?

Isso tá fácil demais.


## Cena 4 — DIA 2
**Visual:** Contador muda para DIA 2. O leiteiro recusa a lenha e aponta o ícone de ovos; o vendedor de ovos aponta o ícone de farinha. Cada recusa tem X vermelho e a pilha fica mais alta e instável.

**Gatilho:** Erro após falso sucesso; defeito visível (pilha); contador

**Narração (S04):**
Pois é.

O leiteiro não queria lenha. Queria ovos.

E o vendedor de ovos queria farinha.


## Cena 5 — DIA 2
**Visual:** Nico desenha um diagrama de setas no chão. A última seta volta ao ícone do sapato, e o vendedor de farinha aparece com o mesmo ícone de sapato. Nico olha para a câmera. Pilha em equilíbrio precário.

**Gatilho:** Solução que falha de forma engraçada (loop do mapa); quebra de previsibilidade

**Narração (S05):**
Então ele fez um mapa de quem queria o quê.

Só que o mapa deu a volta: quem vendia farinha queria... o mesmo sapato que ele.

Nico, você quer comprar um sapato ou abrir uma transportadora?


## Cena 6 — DIA 3
**Visual:** Contador DIA 3 e o MESMO plano da abertura (Nico descalço com a torre), fechando o gancho. A câmera se afasta (zoom-out) e revela a vila inteira de Nicos, cada um com a sua torre, esbarrando uns nos outros. Ícone de relógio no 'bem naquela hora'.

**Gatilho:** Fecha o gancho da abertura; escala absurda; nome do problema

**Narração (S06):**
E ele nem era o único. A vila inteira carregava a própria torre.

O problema não era faltar coisa pra trocar.

Era achar alguém que quisesse exatamente o que você tem, bem naquela hora.


## Cena 7 — DIA 4
**Visual:** Contador DIA 4. Barracas passam a exibir placas com a ficha de madeira. ANTES de aceitar, o sapateiro olha para o leiteiro e o leiteiro levanta uma ficha (setup do S09). Nico vende batatas e recebe fichas (momento separado), depois paga o sapateiro, que usa as mesmas fichas para comprar leite. A pilha de mercadorias desmonta.

**Gatilho:** Solução; plantar a dica que o rebobinar tardio vai revelar; pilha some

**Narração (S07):**
Até que a feira testou uma ideia: todo mundo aceitaria a mesma ficha de madeira.

Nico vendeu batatas, recebeu fichas e comprou o sapato.

E o sapateiro usou as mesmas fichas pra comprar leite.


## Cena 8 — DIA 4
**Visual:** A ficha gira e se transforma em pão, sapato e batata. Corte para uma barraca de pão moderna: Nico paga e o padeiro nem olha o que mais ele carrega.

**Gatilho:** Nomeação do conceito; ponte com o mundo real

**Narração (S08):**
Isso que a vila inventou tem nome: dinheiro.

É por isso que, até hoje, ninguém na padaria te pergunta o que você tem pra trocar.


## Cena 9 — DIA 4
**Visual:** Close da ficha; as placas somem, a feira fica em silêncio. Rebobinar curto até o instante do S07 em que o sapateiro olha o leiteiro: agora ele hesita e a venda trava. Em seguida mostra o leiteiro levantando a ficha e o sapateiro aceitando. Ficha de madeira SEM a confiança: só um pedaço de madeira no chão.

**Gatilho:** Rebobinar tardio que revela a causa; defeito mostrado na hora

**Narração (S09):**
Mas espera. Por que o sapateiro aceitou um pedaço de madeira?

Vamos voltar um instante: ele só aceitou porque confiou que o leiteiro também aceitaria.

Sem isso, a ficha não passava de um pedaço de madeira.


## Cena 10 — DIA 4
**Visual:** Nico de sapatos novos; contador DIA 4 vira um sinal de visto (✓) e aparece 'PARABÉNS' com confete low-poly. A câmera passa por batata, peixe, lenha e ficha e volta ao Nico. Enquadramento final estável para o espectador pensar. Depois da pergunta, o sapato novo descola de novo (loop com a abertura). Gancho opcional (liga ao EP002): mão desconhecida cria uma ficha idêntica, sem competir com a pergunta.

**Gatilho:** Fechamento de conquista; gancho do próximo episódio; pergunta única; loop

**Narração (S10):**
Parabéns, Nico. Você reinventou o dinheiro.

Falta só todo mundo continuar acreditando nele.

Agora me conta: se não existisse dinheiro, o que você ofereceria por um par de sapatos?


---

## Próximo episódio (gancho)
EP002 provisório: **O que faz uma ficha virar dinheiro de verdade?** Mesma fórmula (problema, solução, novo problema): alguém falsifica a ficha; a vila responde com valor marcado, um emissor responsável, um símbolo e marcas difíceis de copiar. Cada elemento é uma solução nomeada. Fica fora do EP001 para manter uma única ideia central por episódio.

## Revisão de clareza e coerência (Fase A, v1.1)
| Ponto | Avaliação | Decisão |
| :-- | :-- | :-- |
| A abertura é um salto no tempo (DIA 3) | O espectador precisa entender que o resto é o passado | Rebobinar com ícone e contador; o S06 volta ao MESMO plano e fecha o gancho |
| Nico "descalço" no DIA 3, mas só "perde" o sapato no DIA 1 | Coerente: o sapato velho se perdeu no caminho | Nos dias 1 e 2, sapato quebrado; no DIA 3, descalço |
| S01 diz "carrega meia vila nas costas" e S06 diz "a vila inteira carregava a própria torre" | Escalada intencional | Pilha do Nico maior que as dos demais no S06, para o gag funcionar |
| S05: "queria o mesmo sapato que ele" | É piada, não regra econômica | Mostrar o vendedor de farinha com o ícone do sapato e o Nico olhando a câmera |
| S07: a ficha só é aceita depois de um olhar entre sapateiro e leiteiro | Prepara a revelação do S09 | Plano curto, legível, sem narração |
| S08: "tem nome: dinheiro" | Simplificação para o público | Comentário fixado explica meio de troca e as ressalvas |
| S09: rebobinar tardio | Risco de confundir se for longo | Máx. 5 s; mesmo ícone do S01 |
| S09 diz "pedaço de madeira" | Só vale para a ficha da vila | Ficha claramente de madeira em todas as cenas |
| Continuidade da pilha | Risco de sumir sem causa | Pilha só desmonta no S07, quando as fichas assumem o papel; nada some sem causa |
| Engajamento | Uma única pergunta | Sem CTA de curtir/inscrever |

## Comentário fixado (rascunho)
A vila é uma simulação para ilustrar um problema da troca direta e por que um meio de pagamento aceito por todos ajuda. A origem real do dinheiro é mais complexa e variou entre sociedades. Conceitos: dupla coincidência de desejos, meio de troca, confiança. Nos países reais, a confiança vem também de leis, impostos e instituições, tema dos próximos episódios.
