# Critérios de Qualidade

Uma aprovação técnica exige evidência reproduzível para o uso testado. A aprovação editorial, visual e de atuação exige decisão humana identificada. O [catálogo do estúdio](ESTUDIO_NICO.md) registra ativos compartilhados e o índice do episódio registra entregas.

## Para promover um ativo ou movimento

1. Registrar origem, versão, licença quando aplicável, dependências e SHA-256 dos arquivos usados.
2. Conferir identidade pela [Bíblia Visual](BIBLIA_VISUAL.md), aparência no formato de destino e escala em relação aos recursos existentes.
3. Validar hierarquia real, transformações, materiais, texturas, caminhos, câmeras e coleções. Indicar quando a inspeção foi apenas documental.
4. Para movimento, testar alcance, cotovelos de ambos os lados, silhueta dos ombros, continuidade de rotações e comportamento sob giro do tronco.
5. Para pega, exigir contato antes da transferência, apoio legível, ausência de salto, posse consistente e objeto visível na retirada. Conferir palma, polegar e pés em quadros intermediários e em pelo menos duas vistas.
6. Registrar tolerâncias e erros medidos para aquele teste. Os 0,005 de tolerância do construtor atual e os limites angulares de seus solvers são guardas de implementação. A naturalidade e a adequação a outros rigs continuam dependentes de revisão.
7. Obter decisão humana com data, arquivo/hash, escopo aprovado e restrições. Registrar a decisão no local de autoridade, sem promover versões por inferência.

## Para aprovar um plano

A decupagem deve conter ID, áudio/timing, intervalo, câmera, atores, trajetórias, passos, olhar, expressão, objetos, contato e transferência, poses críticas e critérios de validação. Conferir enquadramento, continuidade espacial, ritmo e leitura da ação nos quadros de auditoria antes da sequência curta.

Validar o cache pela assinatura de entrada e pelos checksums. Reabrir o projeto e testar dependências. No arquivo exportado, verificar duração, FPS, resolução, decodificação integral e faixas de áudio. Após muxing, usar [audio_finalizer.py](../scripts/pipeline_v3/audio_finalizer.py) para verificar a narração efetiva. Conferir SRT/ASS, palavras narradas e áreas seguras.

Uma revisão deve terminar com APROVADO no escopo declarado, EXPERIMENTAL com pendências, HISTÓRICO ou AUSENTE. O campo livre `status` de um JSON e a palavra “validado” em um relatório não substituem uma decisão artística humana.
