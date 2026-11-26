# Prompt 02 — Peças novas e cena do gancho (substitui a Sessão B do Prompt 01)

Por que mudou: o roteiro v1.1 abre com o gancho mais importante (Nico exausto, DIA 3, rebobinar). Testar a biblioteca nessa cena vale mais que uma cena descartável, e ela já exercita os itens mais arriscados: carga nas costas, contador, rebobinar e o cubo PLOC!.

## Antes de colar (você faz, sem IA)
1. Comite o que a Sessão A produziu (a Fase 1 em diante não foi comitada): `git add -A` e `git commit -m "fundação e Nico"`.
2. Instale o ffmpeg (a Sessão A avisou que falta): `winget install Gyan.FFmpeg.Essentials` (cerca de 100 MB). Feche e reabra o terminal.
3. Troque o roteiro (PowerShell, na raiz do repositório):
```
mkdir _arquivo\roteiros_antigos
git mv episodios\EP001_dinheiro\roteiro.md _arquivo\roteiros_antigos\roteiro_ep001_v1_0.md
git mv episodios\EP001_dinheiro\narracao.json _arquivo\roteiros_antigos\narracao_ep001_v1_0.json
git mv episodios\EP001_dinheiro\storyboard.md _arquivo\roteiros_antigos\storyboard_ep001_v1_0.md
copy <pasta-de-downloads>\roteiro.md episodios\EP001_dinheiro\
copy <pasta-de-downloads>\narracao.json episodios\EP001_dinheiro\
copy <pasta-de-downloads>\verificar_roteiro.py ferramentas\
python ferramentas\verificar_roteiro.py episodios\EP001_dinheiro
```
4. Modelo: Sonnet 5.5, esforço médio. Só suba para Opus se o Sonnet falhar duas vezes no mesmo defeito.
5. Os áudios antigos em `audio/narracoes/EP001/` são do texto v1.0: não use. Áudio novo só depois que o texto ficar final.

---

## Prompt (colar no Antigravity)

Leia SOMENTE: `AGENTS.md`, `NICO_SPEC.md`, `catalogo/INDEX.md`, a lista de arquivos de `biblioteca/` e, em `episodios/EP001_dinheiro/roteiro.md`, apenas a seção "Identidade do canal", o "Mapa de gatilhos" e a "Cena 1". Rode uma vez `python ferramentas/verificar_roteiro.py episodios/EP001_dinheiro`.

Regras de economia desta sessão (valem sobre o resto):
- Capturas de verificação em 360×640; folha de contato com no máximo 12 quadros.
- No máximo 2 rodadas de correção por etapa.
- Não refaça a auditoria completa do Nico. Não altere poses ou ativos aprovados; só pode ADICIONAR as opções e o socket listados abaixo.
- Não escreva relatórios em arquivo; só `CHANGELOG.md`.

### Etapa 1 — Peças novas (criar só estas, com entrada no catálogo)
a) **Nico:** opção `descalco` (sem tênis, pés de luva) e opção `sapatoQuebrado` (sola solta). Novo socket `costas`. Novas poses: `exausto_com_carga` (parado, balançando sob peso) e `cambalear` (caminhada lenta com carga, tronco inclinado).
b) **Torre de mercadorias:** objeto parametrizado (`quantidade`, `altura`) que empilha saco de batata, peixe, lenha, galão de leite, caixa de ovos e saco de farinha, presa ao socket `costas`. Balanço deterministico por senos, sem física real.
c) **Objetos que faltam:** peixe, lenha, galão de leite, caixa de ovos, saco de farinha. Rascunhos simples, cores vindas de `valores/tokens.json`.
d) **Contador DIA:** HUD no canto superior direito, dentro da área segura, texto "DIA n", troca com pop (escala com overshoot).
e) **Rebobinar:** efeito `rebobinar(t0, duracao)`: o tempo da cena corre ao contrário, aparecem linhas de varredura horizontais e um ícone ◀◀ geométrico próprio.
f) **Cubo PLOC!:** cubo colorido cai do céu, quica com squash e stretch e, ao pousar, some com pop dando lugar ao contador.
g) **Terraço baixo (cenário mínimo):** chão em degraus, mar ao fundo, montanha low-poly atrás, luz direcional de fim de tarde. Sem barracas.

**Parada 1.** Gere a folha de contato (poses novas, torre com 3 quantidades diferentes, contador, rebobinar em 4 quadros, cubo em 4 quadros). Liste falhas visíveis, sem maquiar, e pare. Aguarde minha aprovação.

### Etapa 2 — Cena do gancho (só depois da minha aprovação)
Crie `episodios/EP001_dinheiro/cenas/S01/` com 10 s, usando só a biblioteca:
- **0 a 6,5 s:** plano médio no terraço baixo. DIA 3. Nico descalço, com a torre, cambaleia por 3 passos e balança parado. Dolly-in lento. Um ajuste de equilíbrio da torre por volta de 3 s.
- **6,5 a 8 s:** rebobinar.
- **8 a 10 s:** o cubo PLOC! cai e vira o contador DIA 1; Nico (opção `sapatoQuebrado`) em plano aberto começa a andar.

Siga o fluxo do `AGENTS.md`, mas faça bloqueio e animação numa só passada. Folha de contato dos quadros-chave e parada antes do polimento. Exporte MP4 1080×1920 a 30 fps.

**Parada 2.** Em até 10 linhas: tempo e iterações gastos, quadros com erro visível, tempo de render por segundo de vídeo e o que faltou na biblioteca.

---

## Como julgar (por você)
- Os 3 primeiros segundos prendem?
- A torre balança de forma convincente, sem atravessar o corpo do Nico?
- O rebobinar é legível em um relance, em tela de celular?
- Quantas rodadas e quanta cota gastou, e o Sonnet precisou reinventar peças?
