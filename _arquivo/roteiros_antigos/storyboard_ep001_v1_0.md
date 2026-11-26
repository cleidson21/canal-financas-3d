# Storyboard técnico EP001 — Como seria viver SEM DINHEIRO?

Piloto de 15 s preservado em `legado/storyboard_piloto_15s_V3_1.md`.
Os tempos exatos vêm de `timing.json` (medidos dos WAVs); aqui estão ações e enquadramentos. Duração narrada medida na V1: ≈101 s de áudio de segmentos (ver `documentos/RELATORIO_NARRACAO_EP001.md`).

**Regras visuais globais:** 9:16; sem título/vinheta; legendas na faixa segura (ver abaixo); comerciantes sem rigging complexo (barraca + mãos/gesto simples + placa "quero X"); mercadorias nunca somem sem causa; fichas só circulam a partir da Cena 6.

**Áreas seguras (1080×1920, conservadoras):** UI de plataformas costuma ocupar topo (~0–250 px), lateral direita (~140 px, a partir de ~y 1100) e rodapé (~y > 1500). Rosto/ação principal: y 300–1050. Legenda: caixa y 1180–1440, x 90–900. Ícones/placas explicativas: y 300–1100, x 60–940. Valores a validar em celular real (Fase E).

| Cena | Seg. | Plano | Ação / enquadramento | Reuso V3.1.1 | Novo |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | S01 | 1a Close baixo da sola descolando | Passo, sola abre, tropeço | Plano 1 (abertura) | — |
| 1 | S01 | 1b Recuo → geral da vila | Câmera revela feira/vila; ícones de troca direta (batata↔peixe) discretos ao fundo | Cenário vila/feira | ícones de troca |
| 2 | S02 | 2a Médio Nico + saco | Saco de batatas; Nico aponta para sapatos novos | Planos 2,4,5 | — |
| 2 | S02 | 2b Recusa | Sapateiro nega; X vermelho + placa de leite | Plano 6 | — |
| 2 | S02 | 2c Reação | Surpresa → frustração leve | Plano 7 | — |
| 3 | S03 | 3a Barraca pescador (corte) | Placa "quero batata"; Nico entrega algumas; recebe peixe; sinal verde | Batatas | barraca pescador, peixe, sinal ✓ |
| 3 | S03 | 3b Barraca lenhador (corte) | Placa "quero peixe"; entrega peixe; recebe lenha; ✓ | — | barraca lenhador, lenha |
| 3 | S03 | 3c Close Nico desconfiado | Olhar de lado ("fácil demais"); (Carimbo da Dúvida: candidato) | Carimbo (experimental) | — |
| 4 | S04 | 4a Barraca leiteiro | Nico oferece lenha; leiteiro recusa, aponta ovos (ícone ovo) | — | barraca leiteiro, leite, ovos |
| 4 | S04 | 4b Barraca ovos | Quer farinha | — | barraca ovos, farinha |
| 4 | S04 | 4c Diagrama | Setas/ícones expandem: lenha→leite→ovos→farinha→? | — | diagrama animado |
| 4 | S04 | 4d Close Nico | Cansaço/ironia (pausa da piada) | Rosto Nico | — |
| 5 | S05 | 5 Nico exausto + mercadorias | Mercadorias surgem/somem em órbita simples; sapato ainda rasgado | Sapato, batatas | — |
| 6 | S06 | 6a Feira testa ideia | Barracas ganham sinal "aceita ficha" | — | ficha, sinal de aceitação |
| 6 | S06 | 6b Nico vende batatas | Recebe fichas (pescador/outra barraca) | Batatas | fichas |
| 6 | S06 | 6c Compra sapatos | Entrega fichas ao sapateiro, leva sapatos | Sapatos | — |
| 6 | S06 | 6d Sapateiro compra leite | Mesmas fichas → leiteiro (venda e compra em momentos distintos) | — | — |
| 7 | S07 | 7a Close na ficha | Câmera se aproxima | — | ficha madeira |
| 7 | S07 | 7b Sinais somem | Nico tenta pagar; X; ninguém aceita | Placa X | — |
| 7 | S07 | 7c Sinais voltam | Placas reaparecem; negociações retomam | — | — |
| 8 | S08 | 8a Nico comemora | Sapatos novos | Nico/sapatos | — |
| 8 | S08 | 8b Panorâmica de objetos | Batata, peixe, lenha, ficha | — | — |
| 8 | S08 | 8c Retorno ao Nico | Enquadramento estável (pergunta) | — | — |
| 8 | S08 | 8d (opcional) Mão desconhecida | Ficha idêntica no último instante | — | mão simples |

## Inventário de recursos
| Recurso | Estado | Local |
| :-- | :-- | :-- |
| Nico V3 + Armature + animações | EXISTE, reutilizar | `personagens/nico_base.blend`, `pipeline_v3/character_nico.py`, `anim_character.py` |
| Cenário vila / feira / barraca de sapatos / carrinho | EXISTE | `cenarios/*.blend`, `pipeline_v3/environment_fair.py` |
| Sacos de batatas | EXISTE | `objetos/batatas.blend` |
| Sapatos novos | EXISTE | `objetos/sapatos.blend` |
| Placa X vermelha / placa de leite | EXISTE | `objetos/fichas.blend` (nome histórico: contém sinais gráficos, **não** fichas de pagamento) |
| Carimbo da Dúvida | EXISTE (experimental) | `objetos/carimbo_duvida.blend` |
| Narração, finalizador FFmpeg, auditoria | EXISTE | `scripts/tts/`, `pipeline_v3/audio_finalizer.py` |
| Barraca pescador / peixe | CRIAR | `objetos/` (novo .blend) |
| Barraca lenhador / lenha | CRIAR | idem |
| Barraca leiteiro, leite (objeto), ovos, farinha | CRIAR | idem |
| Ficha de madeira padronizada | CRIAR (renomear contexto: `objetos/ficha_pagamento.blend`) | idem |
| Sinais de aceitação (✓/placa "aceita ficha") | CRIAR | idem |
| Diagrama de trocas animado | CRIAR | `scripts/pipeline_v3/diagrama_trocas.py` |
| Legendas SRT/ASS | CRIAR | `scripts/legendas/` |

