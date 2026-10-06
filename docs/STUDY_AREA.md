# Área de estudo — Sprint 12B

Implementada em 06/10/2026, por solicitação do usuário. Deploy segue adiado.

## Recorte entregue

- Biblioteca autenticada em `/estudar`, paginada com dez conteúdos por página.
- Filtro por habilidade em `/estudar?skill=ID`.
- Leitura em `/estudar/:id`: explicação, exemplo de código e erros comuns.
- Cadastro manual ADMIN em `/admin/conteudos/novo`, acessível pela biblioteca.
- Marcação pessoal de estudado, persistida e independente do score.
- Atalho na leitura do desafio recomendado para estudar a habilidade selecionada.
- Atalho por habilidade no feedback recebido para revisar materiais relacionados.

## Regras de conteúdo e aprendizagem

Um conteúdo pertence a exatamente uma skill existente e ativa. Cadastro exige
ADMIN autenticado, título (1–200), explicação (1–12.000), exemplo (1–12.000) e
erros comuns (1–6.000 caracteres). Campos somente em branco são rejeitados.
Espaços/indentação do exemplo são preservados. Texto é renderizado literalmente,
sem HTML, Markdown executável, scripts ou execução do exemplo de código.

O ADMIN revisa e confirma antes de publicar. Esta primeira versão publica
diretamente e não permite edição/versionamento; não publica conteúdo gerado
automaticamente. Se a skill for desativada, seus materiais deixam de aparecer
e ficam indisponíveis por URL, inclusive para marcar leitura. Registros de
leitura existentes são preservados. Reativação da skill restaura a disponibilidade.

Qualquer conta autenticada pode estudar conteúdo de uma skill ativa; a biblioteca
não altera os interesses do perfil. As recomendações de desafios mantêm as regras
existentes de elegibilidade. Os links por skill podem levar a uma lista vazia:
isso indica ausência de material cadastrado, não domínio do assunto.

Marcar estudado é uma autodeclaração de leitura. Não gera avaliação, SkillEvidence,
UserSkill, pontos, percentuais de domínio ou mudança de recomendação. A combinação
usuário/conteúdo é única; repetir a operação preserva a primeira data. Outra conta
não vê essa marcação. Não há opção de desfazer a conclusão neste recorte.

## Arquitetura e API

Módulo `backend/app/modules/study`: models, schemas, repository, service, router.
Migration `0009_create_study` cria `study_contents` e `study_completions` com FKs
e restrições. Consulta paginada obtém itens e total no mesmo statement. A conclusão
usa INSERT ON CONFLICT DO NOTHING; não há consulta/escrita de score no módulo.

| Endpoint | Acesso e comportamento |
| --- | --- |
| GET /api/v1/study | Autenticado; skill_id opcional, limit 1–50, offset >= 0 |
| GET /api/v1/study/{id} | Conteúdo disponível e conclusão somente da própria conta |
| POST /api/v1/study | ADMIN; publica conteúdo completo, retorna 201 |
| PUT /api/v1/study/{id}/completion | Marca leitura da identidade autenticada, retorna 200 |

POST não aceita identidades, score ou campos extras. Query params extras são
rejeitados; IDs positivos limitados a 2147483647. Respostas privadas usam no-store.
Ausência de autenticação retorna 401, falta de permissão 403, conteúdo/skill
indisponível 404 e entrada inválida 422. Autorização permanece no backend.

## Falhas e navegação

Listagem/leitura possuem estados de carregamento, erro, vazio e nova consulta.
Marcação de leitura pode ser repetida após perda da resposta, sem duplicar dados.
Cadastro avisa ao sair com texto não salvo; a expiração ainda pode descartar texto.
POST de publicação não é idempotente: em erro de rede/servidor, bloquear reenvio
e orientar consulta da biblioteca antes de iniciar outro cadastro. Não há retry
automático de publicação ou armazenamento de credenciais/rascunhos no navegador.

## Uso local

Aplicar `python -m alembic -c backend/alembic.ini upgrade head` pelo Python do
ambiente backend, a partir da raiz. Migration já aplicada localmente nesta entrega.
No sistema, entrar como ADMIN, abrir **Estudar → Cadastrar conteúdo**, selecionar
a habilidade ativa e publicar. O aluno acessa **Estudar** ou os links em desafios
e feedback. Nenhum conteúdo ou ADMIN foi criado automaticamente no banco local.

## Validação e limites

- Build e TypeScript aprovados.
- Backend complete: 341 passed, nenhum skip, warnings como erros; PostgreSQL
  descartável. Inclui migração/metadata, permissões, revogação de ADMIN, limites,
  leitura repetida, isolamento, skill inativa e ausência de evidências/score.
- Harness: 16 testes de navegador aprovados. ADMIN publica pela interface; aluno
  lê/marca, recarrega e autentica novamente; outra conta permanece sem marcação.
- Conteúdo HTML exibido literalmente; telas claro/escuro em 1440 e 390 px
  inspecionadas, sem overflow. Cleanup dos serviços/bancos de QA confirmado.
- Alembic check local: nenhuma operação pendente após upgrade.

FUTURO: editar/versionar/arquivar conteúdos individualmente, rascunhos de autoria,
trilhas, gamificação, busca textual, anexos e execução de código. Nenhuma validação
de produção, leitor de tela ou outros motores de navegador foi acrescentada.
