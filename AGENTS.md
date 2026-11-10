
# Estúdio Nico — regras do projeto

Idioma: português do Brasil em mensagens e comentários; nomes de código em inglês.

## 1. O que estamos fazendo

Canal de YouTube Shorts (9:16, 1080×1920, 30 fps, 60–100 s) que ensina finanças com animação 3D low-poly.
Cada episódio ensina UMA ideia. O protagonista, Nico, não fala: o narrador conta a história.
`episodios/<EP>/roteiro.md` é canônico. Não altere roteiro, falas ou ordem sem pedido explícito.

## 2. O que define sucesso (nesta ordem)

1. O espectador entende a ideia sem conhecimento prévio, e o fato ensinado é verdadeiro.
2. Os 3 primeiros segundos prendem: um quadro-gancho projetado, não improvisado.
3. A imagem é densa: sempre há algo acontecendo e algo para olhar.
4. Nenhum erro visível de articulação, escala, cor ou continuidade.
5. Reuso: o episódio N+1 deve sair mais rápido que o N.

## 3. Stack e determinismo

- Node LTS, Three.js (versão fixada no `package.json`, sem CDN), Vite, Playwright (Chromium) para captura, ffmpeg para vídeo. Sem Blender.
- Toda cena exporta `build(ctx)` e `renderFrame(t)`. O estado visual é função pura do tempo `t` (segundos). Sem `Math.random` sem semente, sem relógio real. Assim qualquer quadro pode ser capturado e auditado sem renderizar o episódio.
- Unidades: 1 unidade = 1 metro, Y para cima, câmera olhando para -Z.
- Se um critério de fundação falhar, NÃO troque de stack sozinho: relate o problema ao usuário.

## 4. Estrutura (não criar pastas novas na raiz sem pedido)

```
AGENTS.md  CHANGELOG.md  package.json
valores/        tokens.json: cores, escala, câmera, metas de ritmo
biblioteca/     personagens/ cenarios/ objetos/ movimentos/ efeitos/ camera/ legendas/
catalogo/       página que lista e mostra cada ativo; INDEX.md é o índice
modelos/        modelos de cena reutilizáveis
episodios/EPxxx/  roteiro.md  planos.json  revisao.md
ferramentas/    captura, vídeo, auditoria
_arquivo/       legado, somente leitura. Nunca consultar sem pedido.
```

## 5. Personagens e objetos

- Segmentos rígidos presos por juntas (hierarquia de `Group` com pivô na junta). **Proibido skinning, pesos automáticos e tubos deformáveis.**
- Mãos de luva (sem dedos). Rostos simples. Cores sempre vindas de `valores/tokens.json`, nunca fixadas no código do ativo.
- Objeto "segurado" usa encaixe (`grab`/`release` em um socket). Nunca posicione um objeto "perto da mão" por coordenada.
- Cada ativo tem: função de criação com parâmetros, entrada no catálogo e checagem visual. Ativo só vale como pronto depois que o usuário aprova (`[aprovado dd/mm]` no INDEX).

## 6. Animação

- Poses nomeadas e movimentos parametrizados em `biblioteca/movimentos/`. Interpolação com easing; nada de salto entre poses.
- Limites de junta no código, no sentido anatômico (cotovelo e joelho dobram para um lado só).
- Passos: fase = distância percorrida ÷ comprimento do passo. Pé apoiado não desliza.
- Antes de criar um movimento, procure no catálogo. Antes de animar uma ação complexa, teste-a isolada.

## 7. Câmera, ritmo e atenção (metas iniciais, ajustáveis em `valores/tokens.json`)

- Gancho nos 3 primeiros segundos: o quadro mais marcante do episódio.
- Evento visual novo a cada 2 s ou menos. Nenhuma tomada além de 5 s sem mudança de câmera ou de ação.
- Mudança de enquadramento a cada 2–4 s. Plano aberto para contexto, médio para intenção, detalhe só para objeto.
- Todo plano tem um elemento de destaque (rótulo, ícone, efeito ou número).
- Legenda grande, palavra por palavra, em área segura. Sem título dentro da animação.
- Transições vêm de `biblioteca/camera/`. Cada uma tem propósito narrativo.

## 8. Fluxo por etapas, com parada em cada uma

1. Decupagem: `planos.json` (id, intervalo, câmera, ação, objetos, legenda, transição).
2. Bloqueio: caixas cinza, posições e câmeras. Só movimento e enquadramento.
3. Animação: personagens e objetos.
4. Polimento: luz, partículas, rótulos, efeitos.
5. Captura final.
   Em cada etapa: gerar uma folha de contato dos quadros-chave (início/fim de plano, instantes de contato, picos de movimento), conferir contra os critérios deste arquivo e **declarar falhas encontradas, sem maquiar**. Só então pedir aprovação.
   Nunca renderize o episódio inteiro para verificar uma articulação: capture o quadro.

## 9. Economia de contexto

- Leia apenas: este arquivo, `catalogo/INDEX.md` e os arquivos do plano em andamento.
- Não crie relatórios, manifestos, hashes, fichas de aprovação ou documentos de missão. Registro único: `CHANGELOG.md`, uma linha por mudança.
- Não duplique funções: busque no catálogo primeiro. Não reescreva ativo aprovado sem pedido.
- Peça só a informação que impeça de seguir; senão, decida, anote a suposição em uma linha e continue.

## 10. Proibições

APIs pagas ou de voz sem autorização; instalar dependências sem avisar o que e quanto pesa; criar pastas na raiz; apagar arquivos (use `git mv` para `_arquivo/`); inventar números de posição ou tempo; declarar "validado" sem ter olhado os quadros.

## 11. Correções pontuais

Quando o usuário apontar um erro: reproduza o quadro, corrija só o componente responsável, recapture o mesmo quadro e mostre antes/depois. Sem refatorações alheias.

## 12. Respostas

Curtas. Diga o que mudou, onde ver (comando ou URL local) e o que ainda falha.
