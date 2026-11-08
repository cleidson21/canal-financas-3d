# Roteiro EP001 — Como seria viver SEM DINHEIRO?

**Versão canônica:** 1.0 (roteiro-base aprovado para produção experimental)
**Título editorial (somente metadados de publicação, nunca na animação):** Como seria viver SEM DINHEIRO?
**Duração-alvo:** 85–100 s (a duração real é determinada pelos WAVs; ver `timing.json`).
**Formato:** 9:16, 1080×1920, 30 FPS.
**Piloto anterior (preservado):** `legado/roteiro_piloto_15s_V3_1.md`.

## Premissa
Nico vive numa vila imaginária sem dinheiro. Tem 40 kg de batatas e precisa de sapatos novos. A troca direta falha por falta de parceiros compatíveis; a vila então experimenta uma ficha comum, cuja circulação depende de confiança.

**Objetivo pedagógico:** dificuldade de achar parceiros compatíveis na troca direta (dupla coincidência de desejos); utilidade de um meio de troca amplamente aceito; importância da confiança para sua circulação.

**Ressalva obrigatória:** a vila é um experimento fictício. Não é reconstrução histórica universal da origem do dinheiro, e as preferências dos comerciantes pertencem só a ela.

**Regra de título:** a animação começa direto na ação do sapato. Sem título, vinheta, nome de canal ou "no vídeo de hoje". Legendas, ícones, placas e diagramas são permitidos.

> Texto de narração = literal. Qualquer alteração deve ser feita aqui **e** em `narracao.json`; `testes/test_ep001_narracao.py` verifica a igualdade.

---

## Cena 1 — O sapato pediu demissão
**Visual:** close da sola descolando; Nico dá o passo, o sapato abre, ele tropeça; a câmera recua e revela parcialmente a vila/feira (troca direta insinuada). Reutiliza a abertura V3.1.1.

**Narração (S01):**
O sapato do Nico pediu demissão.

E na vila dele, ninguém usava dinheiro.

## Cena 2 — A primeira tentativa
**Visual:** Nico mostra o saco de batatas ao sapateiro, deseja claramente os sapatos novos; sapateiro recusa; X vermelho sobre as batatas e símbolo grande de leite; surpresa/frustração leve. Reutiliza barraca, vendedor, batatas, placas e reação da V3.1.1.

**Narração (S02):**
Ele tinha quarenta quilos de batata e achou que dava pra trocar por um par novo.

Só que o sapateiro não queria batatas.

Queria leite.

Nico... aí complicou.

## Cena 3 — Uma sorte inacreditável
**Visual:** cortes rápidos. Barraca do pescador: batatas → peixe, sinal verde. Barraca do lenhador: peixe → lenha, sinal verde. Troca fácil, ritmo acelerando. Sem personagens 3D novos complexos; comerciantes = barracas, gestos, placas e mercadorias.

**Narração (S03):**
Mas Nico teve uma ideia.

O pescador queria batatas. Então ele conseguiu um peixe.

E o lenhador queria peixe. Pronto, conseguiu lenha também.

Pera aí... duas trocas seguidas dando certo?

Isso tá fácil demais.

## Cena 4 — A coincidência acabou
**Visual:** Nico chega ao leiteiro com lenha; leiteiro recusa e indica ovos; vendedor de ovos quer farinha; diagrama de setas/ícones se expande (cada tentativa cria outra necessidade), em cortes curtos.

**Narração (S04):**
Pois é.

O leiteiro não queria lenha. Queria ovos.

E o vendedor de ovos queria farinha.

E quem vendia farinha...

Nico, você quer comprar um sapato ou abrir uma transportadora?

## Cena 5 — O verdadeiro problema
**Visual:** Nico exausto cercado de mercadorias; sapato ainda danificado; mercadorias surgem e somem enquanto ele tenta organizar as negociações (complexidade da sequência).

**Narração (S05):**
O problema não era faltar coisa pra trocar.

Era encontrar alguém que quisesse exatamente o que ele tinha, bem naquela hora.

## Cena 6 — A vila encontra uma alternativa
**Visual:** barracas passam a aceitar uma mesma ficha de design original; sinais de aceitação nas lojas; Nico vende parte das batatas por fichas; paga o sapateiro; o sapateiro usa as mesmas fichas para comprar leite. Vender e comprar acontecem em momentos separados.

**Narração (S06):**
Até que a feira resolveu testar uma ideia.

Todo mundo passaria a aceitar uma mesma ficha como pagamento.

Nico vendeu batatas, recebeu fichas e finalmente comprou os sapatos.

E o sapateiro? Usou as mesmas fichas pra comprar leite.

Agora sim!

## Cena 7 — Mas por que confiar?
**Visual:** aproximação da ficha; sinais de aceitação somem; ninguém aceita a ficha; as placas voltam e as negociações retomam. Sistema simplificado de uma comunidade fictícia.

**Narração (S07):**
Mas tem um detalhe.

Por que alguém aceitaria um pedaço de madeira como pagamento?

Porque confiava que outras pessoas também aceitariam.

Sem isso, a ficha não passaria de um pedaço de madeira.

## Cena 8 — Encerramento e engajamento
**Visual:** Nico comemora com sapatos novos; câmera passa por batata, peixe, feixe de lenha e ficha; volta ao Nico. Enquadramento final estável para o espectador pensar. Gancho opcional: mão desconhecida cria uma ficha idêntica (não pode prejudicar a pergunta).

**Narração (S08):**
Agora me conta: se não existisse dinheiro, o que você ofereceria por um par de sapatos?

---

## Revisão de clareza e coerência (Fase A)
| Ponto | Avaliação | Decisão |
| :-- | :-- | :-- |
| Cena 1 diz "ninguém usava dinheiro" e a Cena 6 introduz fichas | Coerente: ficha é acordo, não dinheiro prévio | Fichas só aparecem em cena a partir da Cena 6 (Cena 8 pode mostrá-las já como objeto final) |
| Cena 2 "quarenta quilos de batata" / Cena 3 "Nico entrega algumas batatas" | Coerente: sobra batata | Saco visivelmente menor após cada troca |
| Cena 3 não explica de onde veio o saber das preferências | Aceitável: ele "teve uma ideia" | Placas de "quero X" nas barracas tornam a preferência legível |
| Cena 4: o saco de batata some? | Risco de continuidade | Nico mantém um saco reduzido; lenha na mão; nada some sem causa |
| Cena 6: "Nico vendeu batatas ... comprou sapatos" | Venda e compra em momentos separados | Plano intermediário mostrando Nico com fichas e as barracas recusando/aceitando |
| Cena 7: "pedaço de madeira" | Só vale para a ficha da vila (madeira) | Ficha deve ser **claramente de madeira**; ressalva no comentário educativo |
| Cena 8: engajamento | Uma única pergunta | Sem CTA de curtir/inscrever |

