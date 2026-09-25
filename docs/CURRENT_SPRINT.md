# CodeTrack — Current Sprint

## Sprint atual

SPRINT 6 — ATTEMPTS

Status: concluída; S6-T01 a S6-T06 concluídas.
Histórico: [Sprint 0](SPRINT_0.md), [Sprint 1](SPRINT_1.md),
[Sprint 2](SPRINT_2.md), [Sprint 3](SPRINT_3.md), [Sprint 4](SPRINT_4.md)
e [Sprint 5](SPRINT_5.md).

## Objetivo e fundamento

Permitir iniciar, salvar, retomar e submeter tentativas próprias, preservando
histórico. Base: PROJECT_SPEC.md, fluxo da seção 12 e roadmap; BUSINESS_RULES.md,
RN17–RN23; ARCHITECTURE.md, ChallengeAttempt, AttemptEvent e endpoints Attempts.
Submissão não significa aprovação: avaliação pertence à Sprint 7.

## Estado inicial

Catálogo de desafios e manutenção administrativa implementados. Desafios podem
ser editados/desativados e dependem da atividade das skills para visibilidade.
Não há tentativas, hints, soluções privadas ou avaliação de desafios. Assessment
não inicializa UserSkill. Não exigir desempenho inexistente para iniciar prática.

## Escopo

- Definir ciclo de vida, formato da resposta e preservação do contexto do desafio.
- Persistir tentativas com vínculo a usuário/desafio e histórico preservado.
- POST /api/v1/challenges/{id}/attempts, GET/PATCH /api/v1/attempts/{id}
  e POST /api/v1/attempts/{id}/submit, conforme contrato a definir.
- Ownership sempre pela identidade autenticada; regras no AttemptService.
- Delimitar eventos mínimos úteis antes de criar AttemptEvent.
- Testes de autorização, transações, concorrência e integração PostgreSQL isolada.

## Decisões necessárias na S6-T01

Lacunas resolvidas no [contrato S6-T01](ATTEMPT_CONTRACT.md) e RN17–RN23:

- Estados e transições; significado de submissão sem avaliação automática.
- Tipos de desafio atendidos e formato/limites de draft_answer. O catálogo aceita
  nove tipos como metadados; isso não define nove formatos de resposta.
- Pré-condições de início: disponibilidade do desafio, onboarding e assessment.
- Quantidade de tentativas em andamento por usuário/desafio, numeração e
  comportamento de início repetido/concorrente e nova tentativa após submissão.
- Retomada de tentativa e descoberta de seu ID sem inventar dashboard ou listagem
  geral; definir se o próprio início retorna a tentativa em andamento.
- Efeito de edição/desativação do desafio ou skill sobre tentativas existentes.
  Definir snapshot mínimo para preservar enunciado e vínculos históricos.
- Campos editáveis, omissão/null, resposta vazia, timestamps e origem dos valores.
  Não confiar no cliente para status, dono, número, notas ou contadores.
- Imutabilidade após submissão, repetição de submit, idempotência e disputa entre
  salvar/submeter/iniciar. Fixar limites transacionais e ordem de locks.
- Se AttemptEvent entra agora, definir somente eventos observáveis necessários,
  sem duplicar respostas sensíveis em metadata ou gerar evento em toda leitura.
- Campos previstos de execução, ajuda, testes, tempo e difficulty_rating: decidir
  quais pertencem ao recorte; não preencher valores que pareçam evidência real.
- Erros HTTP, projeções públicas e proteção contra acesso por terceiros, inclusive
  ADMIN: administração de conteúdo não concede acesso a respostas pessoais.

Registrar decisões nos documentos responsáveis, distinguindo-as de requisitos
preexistentes. Mudanças arquiteturais significativas exigem aprovação.

## FUTURO — fora do escopo

Evaluation e feedback de desempenho (Sprint 7), recomendação (Sprint 8), dashboard,
interface de resolução, execução de código, LLM, atualização de UserSkill e scores.
Hints/soluções e endpoint /hint permanecem FUTURO: não há conteúdo privado ou
contrato de provisionamento implementado. Regras RN24–RN28 serão aplicadas quando
essa funcionalidade entrar no escopo. Não criar contadores fictícios de ajuda.
Filtro completed de desafios aguarda definição de conclusão/avaliação; não
interpretar submissão como sucesso. Sem abandono automático ou tarefas agendadas.

## Sequência de tarefas

Executar uma tarefa por vez, respeitando as dependências.

### S6-T01 — Contratos e ciclo de vida

Status: concluída. Contrato define resposta textual, estados IN_PROGRESS/SUBMITTED,
retomada por início repetido, snapshot e submissão idempotente. Sem AttemptEvent,
avaliação, hints ou contadores fictícios. Revisão documental, sem código ou banco.

Resolver as lacunas acima, delimitar entidades/campos e registrar contratos,
transições, erros, snapshots e concorrência antes de alterar código.
Atualizar ARCHITECTURE.md e BUSINESS_RULES.md com decisões consolidadas.

### S6-T02 — Models e migration

Status: concluída. ChallengeAttempt e migration 0006_create_attempts implementados.
Snapshot JSONB, FKs RESTRICT, número único por usuário/desafio, índice parcial
de tentativa aberta e constraints de estado/datas. Migration revisada e aplicada
ao banco local. Validação: 193 testes passaram com `-W error`, incluindo 27 testes
PostgreSQL isolados. Cobertos limites, snapshot independente, histórico, constraints
e downgrade/reaplicação. Alembic sem diferenças e pip check aprovado.
Transições, ownership e formato completo do snapshot aguardam schemas/service.

Implementar somente persistência definida, com FKs, índices, unicidade e constraints.
Preservar histórico; testar upgrade/downgrade/reaplicação em banco descartável
sem perda dos dados anteriores. Não antecipar entidades de avaliação.

### S6-T03 — Schemas e repository

Status: concluída. Schemas de rascunho, snapshot e resposta pública implementados.
Repository consulta por dono, disponibiliza locks/releitura, numeração e gravações
sem commit. Snapshot é copiado e validado; saída omite user_id.
Validação: 201 testes passaram com `-W error`, incluindo 28 testes PostgreSQL
isolados. Cobertos entrada restrita, limites, skills/pesos, isolamento por dono,
snapshot independente e rollback de criação, rascunho e submissão.
Alembic sem diferenças; transições e autorização HTTP aguardam o service/router.

Validar respostas, IDs, limites e campos extras. Separar entrada de dados internos.
Implementar consultas por dono, locks/releitura e persistência sem commit.
Testar snapshots, consultas, ordenação necessária e rollback.

### S6-T04 — Início, consulta e rascunho

Status: concluída. AttemptService e rotas de início, consulta e rascunho
implementados. Novo início retorna 201; retomada 200 sem alterar datas. Snapshot
preservado após edição/desativação do catálogo; acesso exclusivo do dono,
inclusive perante ADMIN. Locks serializam início e salvamento.
Validação: 203 testes passaram com `-W error`, incluindo 30 testes PostgreSQL
isolados. Cobertos HTTP, acesso de terceiros, entrada inválida, rascunho repetido,
estado submetido, início concorrente e rollback após flush. Alembic e pip check OK.
PostgreSQL local foi reiniciado antes da execução final. /submit aguarda S6-T05.

AttemptService coordena início/retomada e salvamento atômicos; routers finos.
Aplicar ownership e disponibilidade conforme contrato. Testar terceiros,
tentativa inexistente, estados inválidos, início concorrente e preservação de dados.

### S6-T05 — Submissão e histórico

Status: concluída. POST /attempts/{id}/submit implementado, sem corpo/query,
exclusivo do dono. Resposta não branca obrigatória; submissão atômica e repetível,
sem alterar datas já salvas ou avaliar conteúdo. PATCH posterior retorna 409.
Validação: 206 testes passaram com `-W error`, incluindo 33 testes PostgreSQL
isolados. Cobertos HTTP, terceiros, vazios, repetição, rollback após flush,
submits concorrentes, ambas as ordens de salvar/submeter e nova tentativa com
histórico preservado. Alembic sem diferenças.

Implementar submit sem avaliação e transições/eventos definidos na S6-T01.
Testar repetição, resposta ausente, imutabilidade, corrida salvar/submeter,
nova tentativa e rollback após falha parcial, preservando tentativas anteriores.

### S6-T06 — Integração e fechamento

Status: concluída. Integração com cadastro/login, onboarding, assessment e catálogo
valida início, rascunho, retomada, submissão e nova tentativa entre contas distintas.
Edição/desativação do desafio preserva o snapshot; perfil e diagnóstico permanecem
inalterados. Validação final: 206 testes passaram com `-W error`, incluindo 33
testes PostgreSQL isolados. Build/typecheck, pip check, alembic check, links e diff
aprovados. Fluxo local documentado em backend/README.md.
Limites: sem avaliação, execução de código, hints, UserSkill ou tela de resolução.
Conteúdo de testes é sintético; não houve provisionamento pedagógico revisado.

Validar publicação → início → rascunho → retomada → submissão → nova tentativa,
com contas distintas e alterações posteriores no catálogo. Verificar ausência
de efeitos sobre assessment/perfil. Rodar regressões, migrations, dependências e
build/typecheck; documentar fluxo reproduzível, resultados e limitações.

## Definition of Done

- [x] Contratos, estados e formato de resposta definidos antes de implementar.
- [x] Persistência e migrations validadas em PostgreSQL isolado.
- [x] Ownership aplicado em todas as operações.
- [x] Início, rascunho e retomada respeitam estado e disponibilidade.
- [x] Submissão atômica sem avaliação antecipada.
- [x] Histórico e contexto preservados conforme contrato.
- [x] Concorrência, repetição e rollback testados.
- [x] Regressões, build e documentação validados.

## Active AI Skills

Carregar somente as pertinentes à tarefa:

- [backend-architecture](../.ai/skills/backend-architecture.md)
- [database-modeling](../.ai/skills/database-modeling.md)
- [api-design](../.ai/skills/api-design.md)
- [security](../.ai/skills/security.md)
- [testing](../.ai/skills/testing.md)
- [debugging](../.ai/skills/debugging.md)
- [documentation](../.ai/skills/documentation.md)

Skills de desenho de conteúdo, avaliação, recomendação e aprendizagem adaptativa
permanecem inativas neste recorte.

## Validação do planejamento

Roadmap, RN17–RN28, entidades/endpoints previstos e dependências existentes
conferidos. Alteração documental; nenhuma mudança de código ou banco.
Os 192 testes registrados no histórico pertencem ao fechamento da Sprint 5.

## Próxima tarefa

Planejar Sprint 7 — Evaluation conforme o roadmap, antes de implementar.
