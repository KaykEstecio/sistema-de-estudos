# CodeTrack — Current Sprint

## Sprint atual

SPRINT 3 — ONBOARDING

Status: concluída; S3-T01 a S3-T05 validadas.
Histórico: [Sprint 0](SPRINT_0.md), [Sprint 1](SPRINT_1.md) e [Sprint 2](SPRINT_2.md).

## Objetivo e fundamento

Permitir que o usuário autenticado informe experiência declarada, interesses
múltiplos e objetivo principal, consulte e atualize seu próprio onboarding.
Base: PROJECT_SPEC.md, seções 6 e 21; BUSINESS_RULES.md, RN47–RN49 e RN53–RN55;
ARCHITECTURE.md, UserInterest, UserGoal e GET/POST/PATCH /api/v1/onboarding.

A autoavaliação descreve experiência declarada; não representa domínio medido,
não cria nível global e não inicializa UserSkill ou score.

## Escopo

- Contratos e decisões de persistência do onboarding.
- UserInterest e UserGoal conforme arquitetura; local de armazenamento da
  experiência declarada será definido antes de criar migration.
- Schemas, repositories e OnboardingService necessários ao fluxo.
- GET, POST e PATCH /api/v1/onboarding, sempre vinculados ao usuário do token.
- Conclusão transacional com onboarding_completed, conforme contrato S3-T01.
- Validação de categorias de interesse existentes e prevenção de duplicidade.
- Testes isolados de integração, autorização, concorrência e rollback.

ADMIN pode operar apenas seu próprio onboarding por essas rotas. Não criar
consulta/edição do perfil de terceiros nem aceitar user_id fornecido pelo cliente.
Reutilizar autenticação e catálogo existentes. Não criar camadas vazias.

## FUTURO — fora do escopo

Assessment (Sprint 4), UserSkill e inicialização/atualização de scores,
SkillRequirement, recomendações, tracks, challenges, attempts e dashboard.
Telas de onboarding, login ou administração; frontend permanece com verificação
de conectividade. Sem LLM, novos provedores ou mudança de stack.
Gerenciamento independente de múltiplos objetivos fica fora deste recorte;
o fluxo inicial coleta o objetivo principal descrito na especificação.

## Sequência de tarefas

Executar uma tarefa por vez e registrar evidências antes de avançar.

### S3-T01 — Contratos e regras do onboarding

Status: concluída. RN47–RN49 e seção Onboarding da arquitetura atualizadas com
experiência declarada, interesses, objetivo, conclusão, PATCH, concorrência e
contratos HTTP. Persistência usa coluna de User e models já previstos.
Revisão documental realizada; nenhum código ou migration alterado nesta tarefa.

Definir payloads e respostas de GET/POST/PATCH na arquitetura, mantendo as rotas
previstas. Definir representação das cinco opções de experiência e sua
persistência; os models atuais ainda não possuem esse campo.
Definir goal_type/description a partir dos exemplos da especificação, sem
tratá-los automaticamente como enum fechado. Definir cardinalidade/limites de
interesses, tratamento de priority, objetivo principal e unicidade por usuário.
Definir leitura antes da conclusão, repetição de POST, PATCH antes/depois da
conclusão, listas omitidas/vazias, substituição de interesses e valores nulos.
Estabelecer quando onboarding_completed muda e como alterações simultâneas
preservam consistência. Documentar erros 401/404/409/422 aplicáveis.
Registrar decisões novas no documento responsável; mudanças arquiteturais
significativas seguem a regra de aprovação de AGENTS.md.

### S3-T02 — Persistência e migration

Status: concluída. User.declared_experience, UserInterest e UserGoal criados;
migration 0003_create_onboarding com FKs RESTRICT, unicidade, defaults, índices
e constraints de experiência/conclusão. Estado antigo de conclusão é redefinido
conforme contrato. Downgrade preserva usuários/catálogo e limpa conclusão.
Validação: 112 testes passaram com `-W error`, incluindo onze testes PostgreSQL
isolados. Upgrade/downgrade/reaplicação e constraints cobertos. Migration aplicada
ao banco local; alembic check sem diferenças e pip check sem conflitos.

Implementar models/campos e migration definidos em S3-T01. Aplicar FK de usuário
e categoria, unicidade, constraints e índices justificados. Definir exclusões
sem cascatas implícitas. Validar upgrade/downgrade/reaplicação em PostgreSQL
descartável preservando usuários e catálogo preexistentes.

### S3-T03 — Schemas e repositories

Status: concluída. Schemas de criação, PATCH e resposta implementados com objetivo
validado e interesses distintos/limitados. OnboardingRepository carrega usuário
com lock e releitura, consulta categorias em lote, substitui interesses e mantém
identidade/data do objetivo principal, sem commit ou autorização.
Validação: 136 testes passaram com `-W error`, incluindo doze testes PostgreSQL
isolados. Cobertos limites, campos extras, isolamento entre contas, rollback,
releitura de User em cache e bloqueio de escrita durante leitura compartilhada.
O fluxo HTTP e a regra de conclusão permanecem na S3-T04.

Implementar entrada/saída, validação de opções, limites e edição parcial conforme
contrato. Rejeitar campos extras e ownership externo. Consultas e persistência
nos repositories, sem commit ou autorização; testar normalização e rollback.

### S3-T04 — Fluxo autenticado de onboarding

Status: concluída. OnboardingService e GET/POST/PATCH implementados; identidade
vem do token. Conclusão e perfil gravados atomicamente; escrita serializada por
usuário, leitura coerente, categorias consultadas em lote e erros seguros.
Validação: 138 testes passaram com `-W error`, incluindo quatorze testes PostgreSQL
isolados. Cobertos estado inicial, conclusão, /me atualizado, PATCH, repetição,
categoria ausente, query extra, disputa entre conclusões e rollback de falha parcial.

Implementar OnboardingService e routers finos. Identidade sempre vem do token.
Validar categorias, persistir experiência/interesses/objetivo e atualizar o
estado de conclusão na mesma transação. Cobrir GET/POST/PATCH, repetição,
concorrência e falha parcial. Não modificar skills ou desempenho.

### S3-T05 — Integração e fechamento

Status: concluída. Fluxo público cadastro → login → onboarding → consulta/edição
→ /me validado com contas STUDENT e ADMIN independentes. Tentativas de ownership
externo são rejeitadas; alteração de um perfil não afeta o outro. Categoria
inválida preserva estado; autoavaliação não cria score ou UserSkill.
Validação final: 139 testes passaram com `-W error`, incluindo quinze testes
PostgreSQL isolados. Build/typecheck frontend passou; pip check sem conflitos,
alembic check sem diferenças e Docker saudável. Valores secretos locais não
encontrados nos arquivos rastreados ou candidatos não ignorados. Sem deploy.

Testar cadastro → login → onboarding → consulta/edição e /me atualizado.
Usar duas contas para comprovar isolamento e incluir ADMIN no próprio perfil.
Testar entradas inválidas, categoria ausente, duplicidade e rollback.
Reexecutar regressões de autenticação/catálogo, migrations e build frontend.
Atualizar instruções e status somente após validação.

## Definition of Done

- [x] Contratos e decisões de negócio/persistência documentados.
- [x] Models e migration validados em PostgreSQL isolado.
- [x] Experiência declarada, interesses e objetivo principal persistidos.
- [x] Identidade do token determina o dono dos dados.
- [x] GET/POST/PATCH respeitam validação e semântica documentadas.
- [x] Conclusão e dados são gravados atomicamente.
- [x] Isolamento entre contas, concorrência e rollback testados.
- [x] Nenhum score ou nível global criado pela autoavaliação.
- [x] Regressões, migrations, build e documentação validados.

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

Nenhuma implementação pendente na Sprint 3. Próximo passo: planejar Sprint 4 —
Assessment conforme a especificação, antes de iniciar novas funcionalidades.
