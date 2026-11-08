# Catálogo de Transições

## Recursos existentes

- **Corte por plano — EXPERIMENTAL na execução.** [cameras.shot](../scripts/producao/cameras.py) cria marcadores com câmeras. A decupagem registra intervalos e destinos. O [renderizador por plano](../scripts/producao/render_plan.py) seleciona a câmera declarada em cada plano.
- **Elipse por corte — EXPERIMENTAL na direção.** A prova PROD-002 usa saída e chegada em lugares distintos. É uma decisão de encenação. Registrar direção, destino e continuidade dos objetos no roteiro técnico.
- **Entrada e saída por escala — EXPERIMENTAL e específica.** `pop_scale` em [build_ep001_v2.py](../scripts/producao/build_ep001_v2.py) anima sinais e objetos. Usar como referência da receita existente, com atenção à legibilidade.
- **Montagem de imagens sustentadas — HISTÓRICO no animatic V1.** A timeline [EP001_ANIMATIC_EDITAVEL.blend](../episodios/EP001_dinheiro/ENTREGAS/EP001_ANIMATIC_EDITAVEL.blend) usa poses PNG. Registrar a duração de cada sustentação ao revisar o ritmo.

## Capacidades ausentes

Um catálogo executável genérico de dissolvências, wipes e raccords automatizados está AUSENTE. Escolher uma dessas transições exige justificar a necessidade, implementar apenas o necessário e validar som e imagem.

Para qualquer corte, verificar início e fim, direção do olhar, eixo espacial, continuidade da posse e correspondência do som. Usar a [decupagem](ESTUDIO_NICO.md#autoridade-editorial-e-aprovação) da entrega selecionada e os [critérios de qualidade](CRITERIOS_QUALIDADE.md).
