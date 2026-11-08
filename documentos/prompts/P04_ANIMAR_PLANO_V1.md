# P04_ANIMAR_PLANO — v1.0

Template do Estúdio Nico. Preencher os campos entre colchetes antes da execução. Campos essenciais ausentes devem ser resolvidos antes da operação dependente.

Leia `AGENTS.md`, `documentos/ESTUDIO_NICO.md`, o índice de [EPISODIO] e os documentos relacionados ao pedido. Consulte outros arquivos apenas por dependência identificada. Trabalhe no projeto atual, com saídas novas em `episodios/[EPISODIO]/TESTES/` e temporários no cache desse diretório. Preserve roteiro, áudio, bibliotecas e entregas aprovadas. Use os motores existentes. APIs, downloads, geração de voz, publicação e render integral exigem autorização específica. Registre aprovação técnica e decisão humana com seus escopos.

Animar apenas [ID_PLANO], quadros [INICIO_FIM], de [EPISODIO].

## Entradas

Decupagem selecionada [CAMINHO], projeto-fonte [CAMINHO_E_VERSAO], recursos aprovados, teste de rig aplicável e limites de render [QUADROS_OU_PREVIA_AUTORIZADOS].

## Saídas

Cópia editável em [NOVO_BLEND], teste numérico das ações relevantes, quadros críticos e prévia curta somente se autorizada. Registrar os parâmetros e o que precisa de revisão humana.

## Restrições

Usar `motions.py` e os controles reais do personagem. Não aplicar automaticamente a solução de um rig a outro. Manter apoio dos pés, direção do cotovelo, alcance e posse dos objetos. O render por plano deve usar `render_plan.py` e seu cache verificado.

## Aprovação

Conferir os dois braços, silhueta do ombro, continuidade de quaternion e alvos avaliados no Blender. Para pega, verificar contato antes da posse, transferência sem salto e objeto legível na retirada. Auditar a câmera principal e perfil quando necessário.

## Parada

Parar após o plano e a validação acordados. Registrar falhas e escopo de aprovação antes de integrar outro plano ou substituir um recurso compartilhado.
