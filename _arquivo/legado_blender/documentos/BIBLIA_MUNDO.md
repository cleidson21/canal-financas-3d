# Bíblia do Mundo

A [Bíblia Visual](BIBLIA_VISUAL.md) rege o estilo. O cenário base é [vila.blend](../cenarios/vila.blend), com a feira em [feira.blend](../cenarios/feira.blend). As classificações e pendências estão no [catálogo do estúdio](ESTUDIO_NICO.md).

## Mundo existente

O construtor [environment_fair.py](../scripts/pipeline_v3/environment_fair.py), `build_village_and_fair`, contém chão gramado, colinas, caminho de terra com pedras, casas ao fundo, árvores, nuvens e elementos de feira. A direção visual é uma manhã de feira com formas estilizadas e silhuetas legíveis. Coordenadas numéricas de construção permanecem no código e no cenário salvo.

A receita [build_ep001_v2.py](../scripts/producao/build_ep001_v2.py) amplia a área da feira e distribui barracas para a narrativa do EP001. Essas posições pertencem àquela montagem. As variantes de barracas estão em [assets.py](../scripts/producao/assets.py), `stall` e `THEMES`, e nas bibliotecas indicadas no catálogo.

## Continuidade de um novo plano

Registrar cenário-fonte e versão, posições inicial e final, acesso entre barracas, eixo de ação, direção do deslocamento, personagens e objetos que entram ou saem. Um corte de elipse deve indicar destino e continuidade da posse. Mudanças de geografia exigem aprovação antes de atualizar a biblioteca global.

## Campos editoriais a preencher

- Nome e mapa permanente da vila, se forem necessários.
- Relações espaciais aprovadas entre bairros, casas e feira.
- Lugares recorrentes além do material já construído.
- Regras de circulação e variações de horário autorizadas.

Esses campos aguardam decisões editoriais. Os arquivos existentes continuam sendo a referência espacial verificável.
