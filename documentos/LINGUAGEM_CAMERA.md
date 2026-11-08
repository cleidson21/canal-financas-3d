# Linguagem de Câmera

Formato oficial 9:16, referência de entrega 1080×1920 a 30 FPS, conforme a [Bíblia Visual](BIBLIA_VISUAL.md). Provas podem usar baixa resolução mantendo a proporção. Comparativos técnicos podem reunir duas vistas lado a lado.

## Sistema existente

[producao/cameras.py](../scripts/producao/cameras.py) controla `PRESETS` e `shot`. Os presets presentes são `wide`, `medium`, `goods_close`, `reaction_close`, `negotiation`, `comparative`, `shoe_close` e `fair_panorama`. Posição, alvo e lente permanecem no código. A função usa marcadores de corte e animação de câmera/alvo, com convenção temporal de 30 FPS.

[cinematography.py](../scripts/pipeline_v3/cinematography.py) pertence à receita do piloto. [build_ep001_v2.py](../scripts/producao/build_ep001_v2.py), `setup_shot_cameras`, contém enquadramentos específicos do EP001. Ao revisar uma entrega existente, a câmera salva no projeto é sua referência de execução.

## Critérios de direção

- Mostrar contexto no plano aberto, intenção no plano médio e contato no detalhe.
- Preservar boné, rosto e silhuetas quando forem necessários para a ação.
- Mostrar mão, objeto e apoio na auditoria de uma pega. Acrescentar perfil quando o cotovelo precisar ser avaliado.
- Registrar eixo de ação, direção do olhar e posição de câmera antes e depois do corte.
- Definir uma intenção para cada movimento de câmera. Conferir os tempos com o áudio real.
- Conferir a área segura das legendas na imagem exportada.
- Auditar primeiro os quadros críticos. As combinações câmera/atuação continuam sujeitas à revisão humana.

Para cada plano, usar a especificação do episódio e os [critérios de qualidade](CRITERIOS_QUALIDADE.md).
