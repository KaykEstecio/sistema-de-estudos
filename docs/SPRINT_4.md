# CodeTrack — Current Sprint

## Sprint atual

SPRINT 4 — ASSESSMENT

Status: concluída; S4-T01 a S4-T06 concluídas.
Histórico: [Sprint 0](SPRINT_0.md), [Sprint 1](SPRINT_1.md),
[Sprint 2](SPRINT_2.md) e [Sprint 3](SPRINT_3.md).

## Objetivo e fundamento

Oferecer diagnóstico inicial por skill após onboarding, com respostas do usuário
e resultados persistidos. Base: PROJECT_SPEC.md, seção 7 e roadmap;
BUSINESS_RULES.md, RN06–RN10, RN50–RN55; ARCHITECTURE.md, Assessment,
AssessmentResult e endpoints planejados de assessments.

Priorizar competências relevantes a interesses e objetivo. Resultado inicial
é provisório, não um nível global ou avaliação definitiva. Não converter
experiência declarada diretamente em score. Não utilizar LLM ou execução de código.

## Escopo e decisões registradas

- Definir contratos, seleção de skills, questões/respostas e avaliação inicial.
- Persistir Assessment, respostas necessárias e AssessmentResult por skill.
- POST /api/v1/assessments, GET /api/v1/assessments/{id},
  POST /api/v1/assessments/{id}/answers e /finish.
- Garantir ownership pelo token, transações, concorrência e proteção do gabarito.
- Definir na S4-T01 se o resultado inicializará UserSkill nesta Sprint, conforme
  possibilidade da RN51; não criar essa persistência antes dessa decisão.
- Testes PostgreSQL isolados e documentação reproduzível.

Lacunas identificadas no planejamento, resolvidas pelo contrato da S4-T01:

- Não há model/contrato de questão, alternativa, gabarito ou resposta.
- Não há banco de questões revisado ou política de provisionamento de conteúdo.
- Objetivo principal é texto livre; não existe mapeamento para skills. A seleção
  deve definir mecanismo explícito, sem inferir relevância por palavras arbitrárias.
- Fórmula de score/confidence, quantidade de evidências e comportamento de
  diagnóstico incompleto não estão definidos.

Registrar decisões novas e respectivas justificativas. Alterações arquiteturais
significativas exigem aprovação conforme AGENTS.md; não contornar essa regra ao
editar documentação. Não apresentar regras propostas como requisitos anteriores.

## FUTURO — fora do escopo

Challenges (Sprint 5), Attempts (Sprint 6), avaliação de desafios (Sprint 7),
recomendação, SkillRequirement, tracks, dashboard, execução de código e LLM.
Telas de assessment/onboarding e mudanças visuais não fazem parte deste recorte.
Sem painel completo de autoria ou plataforma genérica de provas. Provisionamento
mínimo de conteúdo diagnóstico será delimitado na S4-T01.
Recalibração por desempenho posterior pertence às sprints de avaliação.

## Sequência de tarefas

Executar uma tarefa por vez. As tarefas posteriores dependem dos contratos da S4-T01.

### S4-T01 — Contratos e desenho do diagnóstico

Status: concluída. [Contrato](ASSESSMENT_DESIGN_PROPOSAL.md) consolidado após
confirmação do usuário: múltipla escolha, skills selecionadas dentro dos interesses,
sem UserSkill. Score por acertos; confidence=0 por ausência de calibração.
Importação local somente de novas questões revisadas, sem seed automático.
Arquitetura e RN50–RN52 atualizadas. Revisão documental; nenhum código alterado.

Definir tipo inicial de diagnóstico e de questão, origem/validação do conteúdo,
vínculo com skills e representação persistida de itens e respostas. Definir
seleção determinística por interesses/objetivo, desempate e ausência de conteúdo
elegível. Resolver explicitamente a compatibilidade com objetivo em texto livre.
Definir pré-condições de onboarding, estados, quantidade de itens, tratamento de
respostas ausentes/repetidas/alteradas, retomada, finalização e novas tentativas.
Fixar cálculo por skill, limites de score/confidence e significado provisório;
decidir inicialização de UserSkill e efeito sobre valores preexistentes.
Documentar payloads, respostas, códigos de erro, ownership, não exposição de
gabarito, versionamento/snapshot necessário para resultados reproduzíveis e
concorrência. Delimitar mudanças de models antes de criar migration.

### S4-T02 — Persistência e migrations

Status: concluída. Assessment, AssessmentQuestion, AssessmentItem e AssessmentResult
implementados; migration 0004_create_assessments revisada e aplicada localmente.
FKs RESTRICT, índices, unicidade de prova aberta/posição/resultado e constraints
de tipo, opções e limites implementados. Sem UserSkill ou conteúdo inicial.
Validação: 140 testes passaram com `-W error`, incluindo dezesseis testes
PostgreSQL isolados, snapshots independentes, constraints e downgrade/reaplicação
preservando usuários, catálogo e onboarding. Alembic sem diferenças; pip check OK.

Implementar somente entidades/campos definidos no contrato. FK, unicidade e
constraints para resultados por skill e respostas por item; preservar histórico.
Testar upgrade/downgrade/reaplicação sem perder usuários, catálogo ou onboarding.
Se UserSkill entrar no recorte, aplicar RN06–RN08 e testar limites no banco.

### S4-T03 — Schemas e repositories

Status: concluída. Schemas públicos omitem gabarito/ownership; QuestionCreate
valida autoria privada. AssessmentRepository consulta provas por dono, skills
ativas nos interesses, questões ordenadas e snapshots; grava respostas e
resultados sem commit ou autorização. Validação: 155 testes passaram com
`-W error`, incluindo dezessete testes PostgreSQL isolados. Cobertos limites,
alternativas, campos extras, projeção pública, filtros e rollback de operações.

Validar entrada, opções e vínculos; rejeitar ownership e notas enviados pelo
cliente. Separar contratos públicos de dados de correção. Repositories tratam
persistência sem commit/autorização; testar consultas e rollback.

### S4-T04 — Início e registro de respostas

Status: concluída. AssessmentService e rotas de início/consulta/resposta
implementados. Onboarding obrigatório, seleção por interesses, três questões
ativas por skill, snapshots e ownership pelo token. Locks serializam início e
respostas; erros de estado/conteúdo retornam 409, recursos indisponíveis 404.
Validação: 157 testes passaram com `-W error`, incluindo dezenove testes
PostgreSQL isolados. Cobertos terceiros, ausência de conteúdo, repetição,
concorrência de início/respostas, snapshots e rejeição após conclusão.
Finalização e importação de conteúdo ainda não disponíveis nesta tarefa.

AssessmentService coordena seleção e ciclo de vida. Implementar iniciar,
consultar e responder de acordo com S4-T01; identidade sempre pelo token.
Cobrir ausência de conteúdo, estado inválido, item de outro assessment,
acesso por terceiros e repetição/concorrência de respostas.

### S4-T05 — Finalização e resultados por skill

Status: concluída. Avaliação pura por skill com arredondamento metade para cima,
confidence=0 explícita e sem UserSkill. POST /finish exige respostas completas,
grava resultados/conclusão atomicamente e repete resultado salvo sob lock.
Validação: 165 testes passaram com `-W error`, incluindo vinte testes PostgreSQL
isolados. Cobertos limites, arredondamento, skills independentes, prova incompleta,
HTTP, concorrência, idempotência, rollback após flush e nova prova após concluir.

Implementar correção determinística e finalização atômica conforme contrato.
Manter avaliação separada da coordenação do assessment, sem antecipar avaliação
de challenges. Se autorizado na S4-T01, SkillService inicializa UserSkill;
AssessmentService não concentra atualização de domínio. Testar limites,
evidência insuficiente, repetição/concorrência de finish e falha parcial.

### S4-T06 — Integração e fechamento

Status: concluída. Importador local de JSON validado, sem sobrescrita, com
transação única e rollback integral. Fluxo cadastro → onboarding → diagnóstico
→ respostas → resultados verificado entre contas distintas, sem modificar skills.
Validação: 166 testes passaram com `-W error`, incluindo 21 testes PostgreSQL
isolados. Comando de importação validado em subprocesso, incluindo duplicidade.
Alembic sem diferenças, pip check e build/typecheck do frontend aprovados.
Limitação: nenhum banco de questões pedagógicas revisadas foi importado;
os testes utilizam fixtures sintéticas. Preparação em backend/README.md.

Testar cadastro → onboarding → diagnóstico → respostas → resultados com contas
distintas. Verificar isolamento, dados públicos, resultados reproduzíveis e
ausência de efeitos não autorizados em skills existentes. Documentar preparação
do conteúdo e limites do diagnóstico. Rodar regressões, migrations e build.

## Definition of Done

- [x] Lacunas de conteúdo, seleção, avaliação e UserSkill resolvidas/documentadas.
- [x] Contratos e persistência revisados antes da implementação.
- [x] Migrations e constraints validadas em PostgreSQL isolado.
- [x] Conteúdo diagnóstico provisionável conforme contrato, sem gabarito público.
- [x] Início, consulta e respostas respeitam ownership e estado.
- [x] Finalização produz resultados por skill de forma atômica e reproduzível.
- [x] Score/confidence seguem limites e não representam domínio definitivo.
- [x] Concorrência, repetição, isolamento entre contas e rollback testados.
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

Skills de domínio permanecem inativas até conferir sua adequação ao contrato
de diagnóstico da S4-T01; não reutilizar regras de challenges por analogia.
FUTURO: recommendation-engine, adaptive-learning, challenge-design e code-review.

## Próxima tarefa

Planejar Sprint 5 — Challenges conforme o roadmap, antes de implementar.
