# Nico e biblioteca-base — especificação v1

Valores numéricos são propostas iniciais. A fonte de verdade passa a ser `valores/tokens.json`; mude lá, não no código.

## 1. Nico: identidade
Homem comum, atrapalhado, que aprende com os erros. Não fala. Quem comunica pensamentos é o narrador; o corpo comunica reações.
- Silhueta: cabeça grande (cerca de 1/3 da altura), tronco compacto, membros curtos e legíveis de longe.
- Roupa fixa em todos os episódios: boné azul, camiseta laranja, bermuda azul, tênis azul-escuro com sola branca.
- Cores propostas: boné `#2F6FE4`, camiseta `#F28A2E`, bermuda `#2A5FCC`, pele `#EBC8A5`, cabelo `#3B2A20`, tênis `#2B3A55`, sola `#F4F4F0`.
- Altura total: 1,2 u. O tênis **nunca** muda de cor ou forma ao longo do vídeo.

## 2. Construção (segmentos rígidos, sem skinning)
Hierarquia de juntas, cada junta é um `Group` com pivô no ponto de articulação:

```
raiz → pelve → tronco → pescoço → cabeça (boné e rosto como filhos)
tronco → ombroE/D → braço → antebraço → mão (luva)
pelve → quadrilE/D → coxa → canela → pé
```
- Peças: cápsulas e caixas arredondadas; uma esfera pequena visível em cada cotovelo, joelho e ombro, para a junta ler como junta.
- Mão: luva única, sem dedos. Rosto: olhos esféricos com pupila, sobrancelhas como barras (a expressão vem da rotação), boca com 4 formas (neutra, aberta, sorriso, preocupada).
- **Sockets** (pontos de encaixe): `mãoE`, `mãoD`, `antebraçoE`, `antebraçoD` (para carregar saco com os dois braços), `topoCabeça`, `alvoOlhar`.
- Limites de junta (graus, aplicados no código): cotovelo 0 a 145 (só dobra para frente), joelho 0 a 140 (só para trás), ombro com cone de 150, pescoço ±60 horizontal e ±30 vertical, tronco ±25.

## 3. API esperada
```
createNico(opts) → { group, joints, sockets,
  setPose(nome, t), play(movimento, t0, params),
  look(alvo), expression(nome), grab(obj, socket), release(obj, posMundo) }
```
Tudo é função de `t` (determinístico). Sem estado oculto.

## 4. Poses e movimentos mínimos
Parado (respiração leve), caminhar (parâmetros: velocidade, comprimento do passo, pé sem deslizar), correr, surpresa, comemorar, cansado/ofegante, apontar, dar de ombros, recusar (cabeça), carregar saco (dois braços), estender objeto, receber objeto.

## 5. Biblioteca-base mínima (tudo no catálogo)
| Grupo | Itens |
|---|---|
| Personagens | Nico; comerciante genérico (variação por cor, chapéu, avental) |
| Cenário | Vila costeira em terraços (ver seção 6); barraca modular com 4 variações de toldo |
| Objetos | batata e saco, peixe, lenha, galão de leite, sapato, ficha |
| Efeitos | PLOC! (queda e escala), explosão de partículas, seta, rótulo em cápsula, X e ✓ com pop, ícones de tempo (acelerar, voltar) |
| Câmera | presets aberto, médio, detalhe, panorâmica; movimentos dolly-in, órbita, whip pan, subida |
| Transições | corte seco, zoom através de objeto, whip pan, corte por correspondência de forma, passagem de tempo |
| Legendas | palavra por palavra, centro-baixo, área segura (implementação na etapa 2) |

## 6. Vila (proposta a aprovar)
Vila costeira em encosta: mar ao fundo, montanha atrás, três terraços ligados por escada.
- Terraço baixo: porto, barraca de peixe.
- Terraço médio: feira (sapateiro, leite, lenha).
- Terraço alto: casas e árvores.
Combina com a tela vertical (empilha ação), explica por que peixe, lenha e leite existem juntos e dá um "lugar" reconhecível. Sem nome por enquanto.

## 7. Critérios de aceitação do Nico (o agente executa e declara falhas)
1. Galeria de 12 poses, cada uma em 3 vistas (frente, perfil, três-quartos).
2. Teste de limites: nenhuma junta ultrapassa seu intervalo; nenhuma peça atravessa outra nas poses da galeria.
3. Caminhada de 4 s: pés fixos no apoio, quadros a cada 0,1 s em folha de contato.
4. Teste de encaixe: pegar o saco com os dois braços, caminhar 3 s, soltar. Objeto nunca atravessa o corpo nem flutua.
5. Cores iguais em todas as cenas (teste automático contra `tokens.json`).
6. Resultado visível em uma página do catálogo, com turntable.
A decisão final de aprovação é sua, olhando as imagens.
