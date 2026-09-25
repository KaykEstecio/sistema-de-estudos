# CodeTrack — Current Sprint

## Sprint atual

SPRINT 5 — CHALLENGES

Status: concluída; S5-T01 a S5-T05 concluídas.
Histórico: [Sprint 0](SPRINT_0.md), [Sprint 1](SPRINT_1.md),
[Sprint 2](SPRINT_2.md), [Sprint 3](SPRINT_3.md) e [Sprint 4](SPRINT_4.md).

## Objetivo e fundamento

Disponibilizar catálogo autenticado de desafios vinculados a skills.
Base: PROJECT_SPEC.md, seção 11 e roadmap; BUSINESS_RULES.md, RN04 e
RN13–RN16; ARCHITECTURE.md, Challenge, ChallengeSkill e endpoints de Challenges.

Todo desafio ativo deve ter pelo menos uma skill; pesos somam 100% e
difficulty_score fica entre 0 e 1000. Dificuldade textual usa VERY_EASY,
EASY, MEDIUM, HARD ou VERY_HARD. ChallengeService não atualiza habilidades.

## Estado inicial verificado

Autenticação, catálogo, onboarding e assessment implementados. Não há módulo
de challenges, tracks/modules, attempts ou avaliação de desafios. Assessment
não inicializa UserSkill. Não exigir score de usuário inexistente nem reutilizar
questões de assessment como desafios automaticamente.

## Escopo

- Contratos, persistência e migration de Challenge e ChallengeSkill.
- GET /api/v1/challenges e GET /api/v1/challenges/{id} autenticados.
- Provisionamento administrativo mínimo, delimitado na S5-T01.
- Regras no service, persistência no repository e validação nos schemas.
- Testes críticos, integração PostgreSQL isolada e documentação reproduzível.

## Lacunas tratadas na S5-T01

As lacunas abaixo foram resolvidas no [contrato](CHALLENGE_CONTRACT.md) e
nas decisões RN13–RN16. São decisões desta tarefa, não requisitos anteriores:

- Tipos da especificação contemplados e campos exigidos, sem antecipar submissão.
- Limites, campos obrigatórios, padrões e nulabilidade de título, descrição,
  starter_code e estimated_minutes; representação pública.
- Precisão dos pesos, soma, skills duplicadas e comportamento com skills inativas,
  inclusive desativadas depois da publicação.
- Relação entre dificuldade textual e numérica: não inventar faixas.
- Visibilidade, publicação, edição e erros de autorização.
- Meio mínimo de cadastro/manutenção: comparar importação local e endpoints;
  não implementar ambos por antecipação.
- Paginação, ordenação e filtros por skill, difficulty e type.
- Tratamento de module_id sem criar modules ou FK fictícia.
- Delimitação de ChallengeHint: liberação e registro de ajuda dependem de
  tentativas; não expor soluções ou dicas privadas no catálogo.

Registrar decisões nos documentos responsáveis, distinguindo propostas de
requisitos existentes. Mudanças arquiteturais significativas exigem aprovação.

## FUTURO — fora do escopo

Attempts (Sprint 6), submissão e avaliação (Sprint 7), recomendação (Sprint 8),
dashboard, interface de resolução (Sprint 10), execução de código, LLM,
UserSkill, atualização de scores, tracks/modules e filtro completed.
Sem painel de autoria ou geração automática de conteúdo pedagógico.

## Sequência de tarefas

Executar uma tarefa por vez, na ordem de dependência abaixo.

### S5-T01 — Contratos do catálogo de desafios

Status: concluída. Contrato documentado; cadastro/edição via API ADMIN,
tipos como metadados, pesos inteiros, publicação explícita e visibilidade dinâmica
conforme skills ativas. Sem modules, hints ou avaliação. Revisão documental,
sem alteração de código ou banco.

Resolver as lacunas acima com base na especificação e no código existente.
Documentar entradas, saídas, permissões, filtros, erros e provisionamento.
Atualizar ARCHITECTURE.md e BUSINESS_RULES.md com decisões consolidadas.
Delimitar contrato antes de implementar persistência.

### S5-T02 — Models e migration

Status: concluída. Challenge e ChallengeSkill implementados, com migration
0005_create_challenges revisada e aplicada ao banco local. Constraints de tipos,
limites, peso individual, PK composta e FKs RESTRICT; índices conforme contrato.
Validação: 167 testes passaram com `-W error`, incluindo 22 testes PostgreSQL
isolados. Cobertos limites, duplicidade, integridade referencial, downgrade e
reaplicação preservando usuários, onboarding, catálogo e assessment.
Alembic sem diferenças e pip check aprovado. Soma de pesos/publicação aguardam
o service; não há endpoints de desafios nesta etapa.

Implementar Challenge e ChallengeSkill com FKs, unicidade, índices e constraints
aplicáveis. Distinguir constraints por linha das regras de soma e publicação
coordenadas pelo service. Testar upgrade, downgrade e reaplicação em banco
descartável preservando dados dos módulos anteriores.

### S5-T03 — Schemas e repository

Status: concluída. Schemas de criação, PATCH, consulta e saída implementados,
com limites, tipos estritos no JSON, enums e rejeição de skills repetidas.
Repository aplica filtros/visibilidade antes de paginação, carrega vínculos em
lote e grava sem commit. Locks/releitura disponíveis para coordenação pelo service.
Validação: 189 testes passaram com `-W error`, incluindo 23 testes PostgreSQL
isolados. Cobertos filtros combinados, total paginado, skills inativas, limites,
substituição de vínculos e rollback. Alembic sem diferenças.

Validar limites, enums, IDs, campos extras e vínculos. Implementar consultas
ordenadas/paginadas e gravação sem commit no repository. Separar projeção pública
de conteúdo privado conforme contrato. Testar filtros e rollback.

### S5-T04 — Service, consulta e provisionamento

Status: concluída. ChallengeService valida soma dos pesos, existência/atividade
das skills e estado final sob locks, com commit/rollback atômico. GET de lista
e detalhe autenticados; POST/PATCH exclusivos de ADMIN. Consultas de STUDENT
ocultam desafios indisponíveis; queries extras são rejeitadas.
Validação: 192 testes passaram com `-W error`, incluindo 26 testes PostgreSQL
isolados. Cobertos permissões, publicação, filtros HTTP, rollback após flush,
PATCH concorrente e publicação versus desativação de skill. Alembic sem diferenças.

Implementar o meio de provisionamento definido e as rotas de consulta.
ChallengeService garante pesos, vínculos, estado e transação atômica.
Aplicar autenticação e permissões no backend. Testar STUDENT/ADMIN,
conteúdo indisponível, falhas parciais e concorrência pertinente à escrita.

### S5-T05 — Integração e fechamento

Status: concluída. Fluxo integrado com cadastro/login, onboarding, assessment e
catálogo de desafios validado entre ADMIN e STUDENT. Publicação, ocultação após
desativar skill e reaparecimento após reativação preservam perfil e diagnóstico.
Validação final: 192 testes passaram com `-W error`, incluindo 26 testes PostgreSQL
isolados; build/typecheck frontend, pip check e alembic check aprovados.
Links locais e diff validados. Procedimento manual em backend/README.md.
Limitações: fixtures sintéticas, sem conteúdo pedagógico revisado provisionado,
sem tela de desafios, tentativas, avaliação de soluções ou UserSkill.

Validar preparação de conteúdo → listagem → detalhe entre contas distintas.
Garantir ausência de alterações em assessment e habilidades do usuário.
Rodar regressões, alembic check, verificação de dependências e build/typecheck.
Documentar execução, limites e evidências antes de concluir.

## Definition of Done

- [x] Contratos e provisionamento definidos antes da implementação.
- [x] Desafio ativo tem skills; pesos somam 100%; dificuldade respeita limites.
- [x] Persistência e migration validadas em PostgreSQL isolado.
- [x] Consultas autenticadas, paginadas e com visibilidade conforme contrato.
- [x] Escritas administrativas validadas e atômicas.
- [x] Regras críticas, permissões e rollback testados.
- [x] Nenhuma tentativa, avaliação ou atualização de UserSkill antecipada.
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

- [challenge-design](../.ai/skills/domain/challenge-design.md): ativa somente
  para conteúdo de desafios; hints, tentativas e feedback permanecem FUTURO.

Skills de avaliação,
recomendação e aprendizagem adaptativa permanecem FUTURO.

## Validação deste planejamento

Conferidos roadmap, regras, entidades/endpoints previstos e módulos existentes.
Alteração documental, sem alteração de código ou banco. Os 166 testes registrados
no histórico pertencem ao fechamento da Sprint 4.

## Próxima tarefa

Planejar Sprint 6 — Attempts conforme o roadmap, antes de implementar.
