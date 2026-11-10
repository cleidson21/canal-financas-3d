# ANIM-003 — Prova de alcance e pega

A prova de 3,5 s usa a malha, os materiais e a armature da Cena 3. Em [TESTES](./), abra o [Blender editável](ANIM003_RIG_TESTE_V2.blend), a [prévia](ANIM003_RIG_TESTE.mp4) ou o [comparativo](ANIM003_COMPARATIVO.jpg). No Blender, use Numpad 0 para a câmera de corpo inteiro e selecione `ANIM003_Lateral` para a segunda vista. No MP4, o corpo inteiro aparece à esquerda e a vista lateral à direita.

## Onde manter cada parte

- **Personagem e deformação.** [character_nico.py](../../../scripts/pipeline_v3/character_nico.py) cria Nico em `build_character_nico`. `_setup_nico_armature_and_skinning` cria os ossos, pesos e vínculos. [anim_character.py](../../../scripts/pipeline_v3/anim_character.py) contém a atuação do piloto e a função de expressão reaproveitada pela Cena 3.
- **Atuação PROD-002.** [build_scene.py](../../../scripts/producao/build_scene.py) resolve os controles em `nico_actor`, define pés em `foot_pose` e dirige os alvos em `pose_scene`. [motions.py](../../../scripts/producao/motions.py) resolve `hand → aim_chain` e grava posições de objetos em `bind_transfer`. [assets.py](../../../scripts/producao/assets.py) fornece barracas, comerciantes e mercadorias. [cameras.py](../../../scripts/producao/cameras.py) cria as câmeras e os cortes por marcadores.
- **Render.** [render_plan.py](../../../scripts/producao/render_plan.py) abre o projeto editável e executa um único ID da especificação. Use [os comandos por plano](../../../scripts/producao/README.md#render-incremental-por-plano). A [decupagem S03](CENA03_DECUPAGEM.json) endereça as nove câmeras existentes para revisão. Os novos cues são instruções para a próxima edição.

## Diagnóstico da fonte

`Nico_Armature_V3` tem 11 ossos. Pelve é a raiz de tronco e pernas, com joelhos filhos das pernas. Cabeça e braços saem do tronco. Cada antebraço é filho do braço correspondente. Os ossos de deformação apontam em +Y no repouso, com roll zero, para copiar a orientação dos controles Empty. Os membros estendem-se aproximadamente em −Z e a frente do personagem é −Y. Cada osso usa `COPY_TRANSFORMS` WORLD → WORLD com o Empty correspondente. As palmas e polegares são malhas filhas do controle de antebraço. A Cena 3 guarda 526 chaves quaternion lineares por componente nos controles de braço e antebraço. As palmas seguem os pais e as transferências dos objetos são trajetórias gravadas por quadro, com deslocamentos no espaço de mundo.

A malha contínua dos braços tem pesos espelhados e progressivos, 50/50 no centro do cotovelo, com preservação de volume. No MP4 e no Blender, foram inspecionados os quadros 118, 178 e 268, correspondentes à oferta de batatas, à recepção do peixe e à entrega ao lenhador. No quadro 118, o cotovelo direito está em X local 0,073 contra X 0,280 do ombro. No 268, o componente medial do polo chega a 0,182 unidade e a flexão a aproximadamente 110°. O braço esquerdo chega a 151° no quadro 472. O alvo da mão sozinho não determina uma pose. Com a direção de dobra fixa em −Y no mundo e com o giro de Nico, a solução antiga admite cotovelos apontando para dentro. Os ossos reproduzem essa pose conforme o vínculo existente. O comparativo manteve o modelo e os pesos e isolou a diferença no solver, indicando problema de direção de pose com deformação resultante da pose.

O animatic V1 é uma timeline de 223 tiras PNG que cobrem todos os 3.064 quadros. A mediana por tira é 18 quadros e a maior tira individual dura 20 quadros. Mudanças pequenas entre imagens consecutivas prolongam a sensação de imobilidade. Um plano com ação física requer amostras temporais contínuas de uma cena 3D. O VSE continua útil para montagem e pausas deliberadas.

## Correção e verificação

`pose_arm` resolve os mesmos dois segmentos com polo relativo ao tronco, para fora e levemente atrás do personagem. Define a rotação axial no plano de flexão e grava quaternions contínuos. A janela de 12° a 120° evita extensão reta e compressão extrema. O teste manteve o mecanismo de skinning e usa a pega relativa à mão a partir do quadro 41. Foi usado o balcão da Cena 3 com dois suportes instanciados da mesma malha. A ação e a pose dos pés foram preparadas somente na cópia de teste.

- Em 167 amostras a cada meio quadro, cruzamentos braço direito × camisa passaram de 144 para zero. Flexão direita entre 26,3° e 113,1° e variação máxima de 4,72° em meio quadro.
- Sem interseção palma/polegar × batata ou contato indevido com o tampo na amostra. Distância de pega até 0,0038 unidade Blender, erro relativo de transporte até 0,00062 unidade e deslocamento na troca de suporte inferior a 0,000001 unidade. Pés fixos, com folga máxima da sola de 0,001 unidade.
- Cada render de 84 quadros reaproveitou cinco quadros de auditoria. Repetições de um quadro e de três quadros reaproveitaram todos. Foi comprovada a invalidação por bytes de uma dependência e a rejeição de quadro corrompido. O plano de batatas da decupagem renderizou só o quadro 118 da referência. Os números e hashes estão nas [evidências](ANIM003_EVIDENCIAS.json).

## Reproduzir e revisar

`anim003_teste.py` aceita `depois` ou `antes` e um novo caminho `.blend` dentro de `TESTES/`. Execute com o Blender em modo offline e startup de fábrica. Use [ANIM003_PLANOS.json](ANIM003_PLANOS.json) para o teste corrigido e [ANIM003_ANTES.json](ANIM003_ANTES.json) para a referência controlada. O último é regenerável e fica no cache. O arquivo de origem é aberto em leitura. A versão legada conserva `aim_chain` para reprodução das cenas existentes.

O rig ainda tem mão estilizada sem articulação independente dos dedos. O teste cobre uma pega, com raiz estável e dois ângulos, e não certifica as quatro transferências com comerciantes. A decupagem é editável e renderiza os planos de referência. Aplicar os novos cues e retestar peixe, lenha e transferências entre dois personagens depende da revisão humana da prova.
