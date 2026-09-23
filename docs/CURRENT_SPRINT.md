# CodeTrack — Current Sprint

## Sprint atual

SPRINT 2 — CATEGORIES + SKILLS

Status: em andamento; S2-T01 concluída, implementação de código não iniciada.
Histórico: [Sprint 0](SPRINT_0.md) e [Sprint 1](SPRINT_1.md).

## Objetivo e fundamento

Disponibilizar catálogo de categorias e competências, com consulta autenticada
e manutenção por ADMIN. Base: PROJECT_SPEC.md, seções 3, 8 e 21;
ARCHITECTURE.md, modelos Category/Skill e rotas Skills; BUSINESS_RULES.md,
RN04, RN05 e RN53–RN55. Cada Skill pertence a uma Category.
Skill representa competência, não nível global ou desempenho individual.

## Escopo

- Models Category e Skill com migration e vínculo obrigatório.
- Schemas, repositories, services e routers necessários ao catálogo.
- Consulta de categorias, listagem e detalhe de skills.
- Criação/edição por ADMIN e ativação/desativação de Skill via is_active.
- Reutilização da autenticação da Sprint 1; testes isolados e documentação.

Sem exclusão física ou novo campo de ativação em Category neste recorte.
Sem criação de ADMIN pelo cadastro público. Não popular automaticamente o
catálogo nem converter exemplos da especificação em conteúdo obrigatório.

## FUTURO — fora do escopo

Onboarding (Sprint 3), assessment (Sprint 4), UserSkill, inicialização de scores,
SkillRequirement, configuração de pré-requisitos, atualização de domínio,
tracks, challenges, attempts, evaluation, recommendation e dashboard.
GET /api/v1/users/me/skills depende de UserSkill e fica fora deste recorte.
Telas de catálogo/admin e novas funções de autenticação também são FUTURO.
O frontend mantém a verificação de conectividade.

## Sequência de tarefas

Executar uma tarefa por vez, validar e registrar o resultado.

### S2-T01 — Contratos e decisões do catálogo

Status: concluída. Contratos registrados na seção de Skills da arquitetura;
decisões de negócio anexadas à RN05. Definidos campos, defaults, slugs, PATCH,
paginação, visibilidade e erros. Revisão documental de coerência realizada;
nenhum código alterado e nenhum teste de execução necessário nesta tarefa.

Definir contratos na arquitetura antes de codificar. Preservar GET /api/v1/skills
e GET /api/v1/skills/{id}; detalhar rotas Category e escrita administrativa,
ainda não especificadas. Definir tamanhos, descrição, normalização/unicidade
de slug, defaults, ordenação/paginação e visibilidade de inativos por role.
Documentar erros 401/403/404/409/422 e categoria inexistente. Registrar decisões
de negócio no documento responsável, distinguindo-as de requisitos anteriores.
Não alterar stack ou arquitetura.

### S2-T02 — Persistência Category e Skill

Status: pendente.

Criar models e migration conforme S2-T01. category_id obrigatório com chave
estrangeira; impedir referências órfãs. Testar defaults, unicidade,
upgrade/downgrade e reaplicação em PostgreSQL descartável. Preservar users.

### S2-T03 — Schemas e repositories

Status: pendente.

Implementar validação, entrada/saída e consultas necessárias. Rejeitar campos
extras. Repositories não fazem commit nem autorização. Testar limites,
consultas e rollback.

### S2-T04 — Consulta do catálogo

Status: pendente.

Implementar services e routers finos para consulta autenticada conforme S2-T01.
Cobrir catálogo vazio, ordenação/paginação, detalhe ausente, categoria relacionada
e visibilidade de inativos. Não retornar níveis ou desempenho inventados.

### S2-T05 — Manutenção administrativa

Status: pendente.

Criar/editar Category e Skill; alterar is_active em Skill. Usar require_admin;
regras e transações nos services. Validar categoria de destino, duplicidade
inclusive concorrente e rollback. Testar anônimo 401, STUDENT 403 e ADMIN
autorizado, incluindo mudança de role. Não adicionar exclusão física.

### S2-T06 — Integração e documentação

Status: pendente.

Testar ADMIN cria categoria → cria skill → consulta → edita/desativa e visão
STUDENT conforme contrato. Documentar preparação explícita e local de ADMIN
para desenvolvimento, sem senha fixa, promoção pública ou credenciais versionadas.
Reexecutar regressões de autenticação, migrations e build frontend.
Atualizar README e evidências antes de concluir a Sprint.

## Definition of Done

- [x] Contratos e decisões do catálogo documentados.
- [ ] Models e migration validados em PostgreSQL isolado.
- [ ] Cada Skill referencia uma Category existente.
- [ ] Unicidade, validação e transações cobertas por testes.
- [ ] Consultas respeitam autenticação, visibilidade e limites documentados.
- [ ] Somente ADMIN altera o catálogo.
- [ ] Ativação/desativação de Skill funciona sem exclusão física.
- [ ] Regressões da Sprint 1 e build frontend passam.
- [ ] Instruções reproduzíveis e exemplos sem segredos.

## Active AI Skills

Carregar somente as pertinentes à tarefa:

- [backend-architecture](../.ai/skills/backend-architecture.md)
- [database-modeling](../.ai/skills/database-modeling.md)
- [api-design](../.ai/skills/api-design.md)
- [security](../.ai/skills/security.md)
- [testing](../.ai/skills/testing.md)
- [debugging](../.ai/skills/debugging.md)
- [documentation](../.ai/skills/documentation.md)

FUTURO — inativas: code-review, learning-evaluation, recommendation-engine,
adaptive-learning e challenge-design. Ativação não amplia o escopo.

## Próxima tarefa

S2-T02 — criar models Category/Skill e migration, com testes PostgreSQL isolados.
