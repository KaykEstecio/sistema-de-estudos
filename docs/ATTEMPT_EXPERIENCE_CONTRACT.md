# Experiência de tentativas — contrato S10-T02

Definido em 01/10/2026. Listagem implementada na S10-T03. Interface de lista,
início/retomada e leitura implementada na S10-T04, com QA específico pendente.
Edição/envio e consulta de avaliação ainda pendentes.
Complementa [ATTEMPT_CONTRACT.md](ATTEMPT_CONTRACT.md) sem alterar suas operações.
Escopo em [CHALLENGE_EXPERIENCE_PLAN.md](CHALLENGE_EXPERIENCE_PLAN.md).

## Listagem do dono

`GET /api/v1/attempts?limit=10&offset=0`

Bearer obrigatório. STUDENT e ADMIN recebem somente tentativas próprias; não
aceitar user_id ou qualquer seleção de identidade. Não exigir onboarding ou
assessment. Incluir IN_PROGRESS e SUBMITTED, mesmo com catálogo desativado.

| Parâmetro | Regra |
| --- | --- |
| limit | Inteiro, padrão 10, mínimo 1, máximo 50 |
| offset | Inteiro, padrão 0, mínimo 0 |

Sem filtros nesta entrega. Rejeitar queries extras com 422, inclusive status,
challenge_id e user_id. Paginação inválida retorna 422; identidade inválida, 401.
Sucesso 200 com `Cache-Control: no-store`, inclusive coleção vazia. Usar o
tratamento seguro de erros existente, sem dados pessoais em mensagens.

Resposta `AttemptPage`: items, total, limit, offset. total conta todas as tentativas
do dono antes da paginação. limit/offset refletem os parâmetros validados.
Offset além do total retorna items vazio e mantém o total real, sem 404.

Cada `AttemptSummary` contém somente:

| Campo | Origem e formato |
| --- | --- |
| id | ID da tentativa |
| challenge_id | ID do desafio original |
| title | challenge_snapshot.title, nunca título atual do catálogo |
| status | IN_PROGRESS ou SUBMITTED |
| attempt_number | Inteiro positivo |
| started_at | Data UTC com fuso |
| submitted_at | Data UTC com fuso, null em IN_PROGRESS |
| last_activity_at | Data UTC com fuso |

Não retornar draft_answer, snapshot completo, user_id, feedback ou dados do
revisor. Não inferir avaliação a partir de SUBMITTED: a consulta ocorre no detalhe.
Ordenar por last_activity_at DESC e id DESC para desempate determinístico.
Uma nova atividade pode mudar páginas entre requisições; paginação por offset
não representa um histórico congelado. Atualizar a lista ao retornar a ela.

Repository projeta apenas campos necessários, filtrando dono na contagem e nos
itens. Obter contagem e página no mesmo snapshot de leitura (preferir uma consulta),
inclusive para página vazia. Sem locks de escrita, commit, atualização de datas
ou acesso ao catálogo necessário à autorização. Service compõe a saída; router
valida entrada e autentica. A dependência atual de query vazia deve continuar
nas operações antigas e permitir paginação apenas na nova rota.

## Navegação e leitura

Rotas protegidas `/tentativas` e `/tentativas/:id`, IDs positivos até 2147483647.
A lista oferece Retomar para IN_PROGRESS e Ver envio para SUBMITTED. Página
vazia além do total oferece voltar à primeira; coleção sem tentativas oferece
voltar ao painel. Loading, erro com retry e vazio são estados distintos.

Iniciar/retomar no detalhe recomendado chama o POST existente sem corpo, uma
única vez por ação explícita. Desabilitar botão enquanto aguarda; 200/201 navegam
para o ID retornado. 404 informa indisponibilidade e permite atualizar sugestões.
Em resultado incerto por falha de rede, orientar consultar a lista antes de tentar
novamente: POST de início não é idempotente após submissão. Não repetir em loop.

No detalhe, GET da tentativa é a fonte de status, snapshot e resposta persistida.
Loading bloqueia edição; 404 informa tentativa não encontrada, sem distinguir
terceiros; falha temporária oferece retry. Renderizar texto/código sem executar
HTML, Markdown ativo, URLs ou código. Identificar skills como Skill #ID quando
o contrato não fornecer nomes. Desativação do catálogo não impede retomada.

## Edição, salvamento e envio

Manter texto local separado da última resposta confirmada pelo servidor. Dirty
significa diferença exata, incluindo espaços/quebras. Limite de 20000 caracteres
Unicode como no backend; não confiar somente em maxlength UTF-16 para a contagem.
Vazio é permitido ao salvar; somente espaços não permitem enviar.

| Estado/ação | Comportamento |
| --- | --- |
| IN_PROGRESS sem alterações | Editar; Salvar desabilitado; Enviar se texto não branco |
| Com alterações | Salvar disponível; indicar alterações ainda não salvas |
| Salvando | Bloquear editor e ações concorrentes; capturar exatamente o texto enviado |
| PATCH 200 | Atualizar referência persistida e mostrar confirmação de salvamento |
| PATCH falhou | Preservar texto local, não afirmar salvamento; oferecer nova tentativa |
| Enviar | Confirmação explícita de imutabilidade, com opção de cancelar |
| Envio confirmado | Bloquear editor; salvar dirty primeiro; só após PATCH 200 chamar submit sem corpo |
| SUBMITTED confirmado | Mostrar resposta do servidor somente leitura, sem novo início automático |

Se o PATCH falhar durante a sequência de envio, não chamar submit. Se o envio
retornar erro de rede/5xx, sua conclusão é incerta: GET da tentativa antes de
repetir. SUBMITTED confirma o envio; IN_PROGRESS permite nova confirmação;
se GET falhar, manter estado incerto e oferecer consultar novamente, sem PATCH
ou novo início automático. Abort de requisição não significa rollback no servidor.

409 ao salvar/enviar exige reler a tentativa. Se SUBMITTED, mostrar versão
enviada e, caso diferente, manter temporariamente texto local identificado como
não enviado e disponível para cópia. Se IN_PROGRESS, preservar edição e explicar
o erro; não reenviar automaticamente. 422 preserva o texto e apresenta erro de
validação. Falhas de autenticação seguem o fluxo global de sessão expirada.

Limite existente: não há versão/ETag para detectar PATCH concorrente entre abas.
Enquanto IN_PROGRESS, prevalece o último salvamento aceito; GET antes de salvar
não elimina essa corrida. A Sprint não promete impedir sobrescritas entre abas
nem adiciona controle otimista. Orientar resolver em uma aba. Locks existentes
protegem a transição para SUBMITTED; não são controle de versão de rascunhos.

## Saída e sessão

Avisar antes de navegação voluntária com dirty e durante resultado incerto,
incluindo links internos e logout. beforeunload cobre recarga/fechamento quando
permitido pelo navegador; não garante preservação em encerramento abrupto.
Definir proteção compatível com o router existente durante implementação.
Não armazenar respostas/token em localStorage, sessionStorage ou URL.

Após 401, limpar estado pessoal conforme AuthProvider; texto não salvo pode ser
perdido. Informar esse limite junto ao editor. Novo login permite recuperar o
rascunho persistido pela lista. Respostas atrasadas não podem reintroduzir dados
após logout, troca de usuário ou de tentativa. Ajustar whitelist de retorno do
login, preservando prioridade do onboarding para contas que não o concluíram.

## Avaliação manual

Consultar avaliação somente após confirmar acesso a tentativa SUBMITTED.
200 mostra feedback, rubrica, data e resultados por skill do contrato vigente.
404 nesse contexto indica revisão ainda ausente; outras falhas mostram erro/retry,
nunca espera fictícia. Atualizar por botão, sem polling. IN_PROGRESS não consulta
avaliação. SUBMITTED continua sendo o status mesmo após revisão.

Traduzir MET como Atendido, PARTIALLY_MET como Parcialmente atendido, NOT_MET
como Não atendido e INSUFFICIENT_EVIDENCE como Evidência insuficiente, explicando
que esta última não equivale a erro. Não inventar nota, testes executados ou prazo
para revisão. Revisão manual atualiza UserSkill pelo backend conforme Sprint 7A;
frontend apenas lê a avaliação e oferece voltar ao painel para consultar progresso.

## Critérios de validação

- Listagem: padrão/limites/extras, zero itens, offset além do total, desempates,
  duas contas e ADMIN, snapshot após alteração/inativação, campos restritos,
  no-store e ausência de mutações. Não mascarar total quando página estiver vazia.
- Interface: falha de PATCH impede submit; perda da resposta do submit recupera
  estado; 409 preserva texto local; não criar nova tentativa ao repetir envio.
- Verificar sessão expirada, troca de conta/rota, Unicode, alterações não salvas,
  avaliação ausente versus erro, foco/teclado, anúncios de status e desktop/mobile.
- Validar contratos existentes na regressão. Estes são critérios planejados,
  não resultados de testes executados nesta etapa documental.

## Validação S10-T03

Implementados schemas, consulta por dono, composição no service e rota de listagem.
Sem migration ou dependência nova. Executados com CODETRACK_TEST_ADMIN_URL carregada
localmente, sem exposição de credenciais, e banco PostgreSQL descartável:

```text
python -m pytest backend/tests/test_attempt_history.py backend/tests/test_attempt_flow.py backend/tests/test_attempt_schemas.py backend/tests/test_attempt_repository.py -q -W error --tb=short
15 passed in 14.62s
```

Inclui READ ONLY, consulta única, isolamento entre contas/ADMIN, título histórico
de desafio inativo, desempate, limites/extras e página além do total. Regressão
completa e testes da interface ficam para as tarefas seguintes da Sprint.
