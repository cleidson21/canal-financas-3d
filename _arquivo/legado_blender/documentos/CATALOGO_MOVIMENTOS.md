# Catálogo de Movimentos

Fonte de código reutilizável em [producao/motions.py](../scripts/producao/motions.py). Os movimentos abaixo são EXPERIMENTAIS para um novo uso até passar pelo [gate de qualidade](CRITERIOS_QUALIDADE.md). As curvas salvas de uma entrega preservam a execução daquela versão.

- **Interpolação e poses.** `smooth`, `track`, `key` e `finalize_curves` oferecem easing e gravação de curvas. A aplicação final é definida na receita do plano.
- **Braços.** `aim_chain` conserva a direção legada, `pose_arm` usa polo no espaço do tronco, e `hand` permite aplicar a solução e gravar curvas. `nico_elbow_pole` fornece a convenção lateral do Nico. Validar alcance real, flexão, continuidade de quaternion, malha avaliada e apoio no objeto.
- **Pega.** `bind_transfer` grava a posse com offsets por mão. `set_nico_grip` move o polegar na hierarquia original. A prova [ANIM004_RIG_V3.blend](../episodios/EP001_dinheiro/TESTES/ANIM004_RIG_V3.blend) contém punho adicional e controle contínuo de pega. Conferir a hierarquia antes de escolher um método.
- **Alcance.** `clamp_nico_reach` limita o alvo a uma faixa geométrica. Medir a diferença entre o alvo pedido e o efetivo, principalmente no instante de contato.
- **Gestos de mão.** `offer`, `deliver`, `receive`, `point` e `transport` compartilham a construção `gesture`. Os nomes descrevem intenções. Coordenação entre personagens e transferência de objetos precisam ser dirigidas.
- **Cabeça e recuperação.** `accept`, `refuse`, `surprise`, `satisfaction`, `distrust`, `look_at` e `settle` fornecem componentes simples. Validar atuação e direção do olhar no enquadramento escolhido.
- **Pés e caminhada.** `foot_pose` em [build_scene.py](../scripts/producao/build_scene.py) e `pose_legs_walk_or_stand` em [build_ep001_v2.py](../scripts/producao/build_ep001_v2.py) são implementações específicas do EP001. Um ciclo genérico aprovado está AUSENTE.
- **Rosto.** `_set_facial_expression` em [anim_character.py](../scripts/pipeline_v3/anim_character.py) fornece os estados da Bíblia Visual. O restante da atuação desse módulo é HISTÓRICO, ligado ao piloto.

A [prova ANIM-004](../episodios/EP001_dinheiro/TESTES/ANIM004_RELATORIO.md) documenta alcance, pega e limitações da trajetória antiga. Registrar nova aprovação com personagem/rig, ação, objeto, escala, duração, vistas testadas e versão/hash. O escopo da aprovação deve acompanhar cada reutilização.
