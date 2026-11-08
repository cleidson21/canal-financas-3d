# Versionamento do Estúdio Nico

GIT-001 em 2026-11-08. Git local inicializado na branch main, origin configurado para [cleidson21/canal-financas-3d](https://github.com/cleidson21/canal-financas-3d) e Git LFS 3.7.1 habilitado localmente. A API autenticada pelo Git Credential Manager confirmou visibilidade privada e permissão de escrita. A consulta de todas as referências confirmou o remoto vazio antes do primeiro commit. O 404 do conector anterior refletia a indisponibilidade de acesso por aquela credencial. Publicação do pacote documental em preparação.

## Preparação entregue

[.gitignore](../.gitignore) exclui credenciais usuais, ambientes, modelos, caches, logs, sequências regeneráveis, referências externas e backups locais. O histórico é excluído por padrão, com exceção explícita do projeto do piloto que ainda é entrada dos construtores atuais. As 223 poses PNG usadas pelo master VSE V1 são dependências, e permanecem elegíveis para inclusão revisada junto daquele master.

[.gitattributes](../.gitattributes) prepara LFS para `.blend`, WAVs, vídeos e imagens selecionadas. O LFS usa ponteiros no Git e armazena os binários separadamente. Os limites dependem do plano da conta. O GitHub bloqueia arquivos acima de 100 MiB no Git comum. Conferir o armazenamento e tráfego disponíveis antes do primeiro envio. [Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage), [limites de arquivos](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

## Procedimento de versionamento

1. Confirmar o repositório privado e a conta com acesso. Revisar licenças dos recursos selecionados e verificar segredos também nos arquivos de código, JSON e documentação.
2. Conferir Git nesta raiz, branch `main`, LFS local e `origin`. A inicialização e a conexão foram realizadas na GIT-001.
3. Preparar o primeiro commit com lista explícita de caminhos revisados. Começar pelos documentos, prompts, regras e código. Acrescentar bibliotecas e dependências necessárias por nomes específicos, com tamanho e hash conferidos.
4. Usar `git check-ignore -v` para exclusões, `git check-attr filter -- <arquivo>` para LFS e `git lfs status` para confirmar os binários antes do commit.
5. Revisar `git diff --cached --name-status`, `git diff --cached --check` e o conteúdo textual staged. O índice deve conter apenas a lista autorizada. Conferir que nenhum arquivo grande entrou como blob Git comum.
6. Validar uma recuperação local dos arquivos selecionados, incluindo biblioteca-fonte, áudio, fontes editoriais e dependências do projeto escolhido. Comprovar os testes que se pretende suportar. Uma entrega em VSE depende das imagens referenciadas.
7. Após autorização de publicação do checkpoint, enviar a branch e os objetos LFS e conferir ambos no destino. Revisões de código devem anteceder mudanças na branch principal. Backups recuperáveis continuam necessários.

Os testes históricos podem exigir manifestos e arquivos de `backups/` e `arquivo/` que foram excluídos da seleção automática. A lista mínima desses materiais precisa de revisão própria. A P00 valida a preparação dos filtros e documentos, sem certificar um clone operacional completo.

Os comandos de inicialização abaixo foram usados na GIT-001, a partir da raiz do projeto.

```powershell
git init -b main
git lfs install --local
git remote add origin https://github.com/cleidson21/canal-financas-3d.git
```

## Pacote documental GIT-001

Lista explícita de 21 arquivos, com nenhum binário ou objeto LFS no pacote inicial.

```text
AGENTS.md
README.md
.gitignore
.gitattributes
.env.example
documentos/ESTUDIO_NICO.md
documentos/PIPELINE_PRODUCAO.md
documentos/CRITERIOS_QUALIDADE.md
documentos/VERSIONAMENTO.md
documentos/BIBLIA_MUNDO.md
documentos/BIBLIA_VISUAL.md
documentos/LINGUAGEM_CAMERA.md
documentos/CATALOGO_MOVIMENTOS.md
documentos/CATALOGO_TRANSICOES.md
documentos/prompts/P01_PROJETAR_CENARIO_V1.md
documentos/prompts/P02_CONSTRUIR_PERSONAGEM_V1.md
documentos/prompts/P03_DIRIGIR_CENA_V1.md
documentos/prompts/P04_ANIMAR_PLANO_V1.md
documentos/prompts/P05_AUDITAR_ANIMACAO_V1.md
documentos/prompts/P06_FINALIZAR_PLANO_V1.md
episodios/EP001_dinheiro/00_ABRIR_EP001.md
```

A auditoria do pacote confirmou texto UTF-8, tamanho reduzido e placeholder fictício no .env.example. Dois links de código na Bíblia Visual foram convertidos para caminhos relativos para retirar caminhos locais de usuário. Os links para código, bibliotecas, áudio, vídeos, roteiro, timing, relatórios e documentos fora desta lista continuam válidos apenas quando os recursos existem no disco local. Esses destinos ficam fora do primeiro envio e terão links indisponíveis no GitHub até uma publicação posterior revisada.

Guardar mudanças de texto em commits pequenos. Versionar ativos com decisão e hash, evitando regravar bibliotecas aprovadas para mudanças de episódio. Usar um editor por arquivo Blender durante uma alteração e considerar travas LFS se houver colaboração simultânea.
