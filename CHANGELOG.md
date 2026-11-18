# CHANGELOG

- 10/11 arquivar legado: tudo (exceto AGENTS, NICO_SPEC, roteiro/storyboard/narração/publicação do EP001, `scripts/legendas`, `audio/narracoes/EP001`) movido para `_arquivo/legado_blender/` (rastreados com `git mv`; caches, venvs e backups movidos e mantidos fora do git).
- 10/11 stack: `package.json` com three 0.187.0, vite 8.3.7, playwright 1.59.1 (reusa o Chromium 1217 já baixado); `vite.config.js` exclui `_arquivo`.
- 10/11 `valores/tokens.json`: cores, escala, juntas, câmera, ritmo, locomoção (suposições listadas em `_propostas`).
- 10/11 ferramentas: `captura.mjs` (PNG por instante, WebGL headless na GPU via ANGLE/D3D11, ~20–60 ms/quadro), `folha.mjs` (folha de contato), `pagina/harness.js` (inclui passe de cor contra tokens).
- 10/11 biblioteca: esqueleto bípede rígido com IK de perna e limites (`personagens/bipede`), Nico (`personagens/nico`), poses/gestos/locomoção (`movimentos`), saco e caixote (`objetos`), estúdio neutro (`cenarios`), presets de câmera (`camera`), utilidades em `biblioteca/nucleo/` (subpasta nova).
- 10/11 catálogo: `catalogo/index.html` com turntable, galeria 12×3, testes de caminhada e encaixe; `INDEX.md`.
- 10/11 auditoria do Nico (`ferramentas/auditoria_nico.mjs`): limite do tornozelo no IK, giro no lugar (`createTurn`) para o teste de encaixe, saco com largura igual ao vão dos braços.
