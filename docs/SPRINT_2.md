# CodeTrack — Current Sprint

## Sprint atual

SPRINT 2 — CATEGORIES + SKILLS

Status: concluída; S2-T01 a S2-T06 validadas.
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

Status: concluída. Models Category/Skill e migration 0002_create_catalog criados.
FK obrigatória com RESTRICT, unicidade e CHECK de slug, índice de categoria e
is_active=true no ORM/banco. Sem endpoints ou dados iniciais de catálogo.
Validação: 74 testes passaram com `-W error`, incluindo PostgreSQL descartável,
constraints, upgrade/downgrade/reaplicação e preservação de users. Migration
aplicada ao banco local; alembic check sem diferenças e pip check sem conflitos.
Validação inicial em backend/.validation/.venv com Python 3.12.10. Em 24/09/2026,
backend/.venv foi recriado com Python 3.12.10 e requirements.txt; imports nativos,
74 testes com `-W error`, pip check e alembic check passaram no ambiente principal.
O ambiente incompatível foi preservado em backup local ignorado pelo Git.

Criar models e migration conforme S2-T01. category_id obrigatório com chave
estrangeira; impedir referências órfãs. Testar defaults, unicidade,
upgrade/downgrade e reaplicação em PostgreSQL descartável. Preservar users.

### S2-T03 — Schemas e repositories

Status: concluída. Schemas de criação, edição parcial, leitura, paginação e
filtros implementados; CategoryRepository e SkillRepository consultam e alteram
persistência sem commit ou autorização. Normalização, limites, campos extras,
null/omissão e booleanos/IDs estritos cobertos. Listas ordenadas por ID com
filtros e contagem no PostgreSQL. Validação: 108 testes passaram com `-W error`,
incluindo sete testes PostgreSQL isolados, rollback e persistência após commit.
Endpoints e regras de visibilidade permanecem nas S2-T04/T05.

Implementar validação, entrada/saída e consultas necessárias. Rejeitar campos
extras. Repositories não fazem commit nem autorização. Testar limites,
consultas e rollback.

### S2-T04 — Consulta do catálogo

Status: concluída. GET de listagem/detalhe de categories e skills implementados,
com autenticação, paginação e filtros no banco. CategoryService/SkillService
tratam existência e visibilidade; routers adaptam erros. STUDENT vê somente
ativas e recebe 403 ao solicitar inativas; ADMIN consulta ambas.
Validação: 109 testes passaram com `-W error`, incluindo oito testes PostgreSQL
isolados. Cobertos catálogo vazio, paginação, detalhes ausentes/inativos, filtros,
parâmetros extras/inválidos, autenticação e mudança de role com o mesmo token.

Implementar services e routers finos para consulta autenticada conforme S2-T01.
Cobrir catálogo vazio, ordenação/paginação, detalhe ausente, categoria relacionada
e visibilidade de inativos. Não retornar níveis ou desempenho inventados.

### S2-T05 — Manutenção administrativa

Status: concluída. POST/PATCH de categorias e skills protegidos por require_admin.
Services controlam commit/rollback, categoria de destino e tradução de constraints
conhecidas para 404/409; edição de Skill consulta primeiro o alvo. Sem DELETE.
Validação: 111 testes passaram com `-W error`, incluindo concorrência real para
slugs de categoria e skill, rollback de edição, troca de categoria, desativação,
limpeza de descrição e rejeição de anônimo/STUDENT com mudança de role.

Criar/editar Category e Skill; alterar is_active em Skill. Usar require_admin;
regras e transações nos services. Validar categoria de destino, duplicidade
inclusive concorrente e rollback. Testar anônimo 401, STUDENT 403 e ADMIN
autorizado, incluindo mudança de role. Não adicionar exclusão física.

### S2-T06 — Integração e documentação

Status: concluída. Fluxo administrativo revisado: criar categoria/skill, consultar,
editar, desativar e reativar, verificando visão STUDENT e mudanças de role.
Procedimento de promoção/reversão de ADMIN local documentado no backend/README.md;
sintaxe validada, sem executar promoção de conta real. Testes usam bancos isolados.
Validação final: 111 testes passaram com `-W error`, incluindo dez testes
PostgreSQL; build/typecheck frontend passou; pip check sem conflitos e alembic
check sem diferenças. Docker saudável. Valores secretos locais não encontrados
nos arquivos rastreados ou candidatos não ignorados. Nenhum deploy realizado.

Testar ADMIN cria categoria → cria skill → consulta → edita/desativa e visão
STUDENT conforme contrato. Documentar preparação explícita e local de ADMIN
para desenvolvimento, sem senha fixa, promoção pública ou credenciais versionadas.
Reexecutar regressões de autenticação, migrations e build frontend.
Atualizar README e evidências antes de concluir a Sprint.

## Definition of Done

- [x] Contratos e decisões do catálogo documentados.
- [x] Models e migration validados em PostgreSQL isolado.
- [x] Cada Skill referencia uma Category existente.
- [x] Unicidade, validação e transações cobertas por testes.
- [x] Consultas respeitam autenticação, visibilidade e limites documentados.
- [x] Somente ADMIN altera o catálogo.
- [x] Ativação/desativação de Skill funciona sem exclusão física.
- [x] Regressões da Sprint 1 e build frontend passam.
- [x] Instruções reproduzíveis e exemplos sem segredos.

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

Nenhuma implementação pendente na Sprint 2. Próximo passo: planejar Sprint 3 —
Onboarding conforme PROJECT_SPEC.md, antes de iniciar novas funcionalidades.
