# CodeTrack — Current Sprint

## Sprint atual

SPRINT 10 — CHALLENGE EXPERIENCE

Planejamento iniciado em 01/10/2026. S10-T01/T02 documentadas; S10-T03 implementada.
Recorte em [CHALLENGE_EXPERIENCE_PLAN.md](CHALLENGE_EXPERIENCE_PLAN.md).
Sprint anterior concluída: [SPRINT_9.md](SPRINT_9.md).

## Escopo

Iniciar/retomar tentativa, salvar resposta textual, enviar para revisão manual
 e consultar avaliação. Lista paginada exclusiva do dono para recuperar rascunhos
 e envios. Preservar contratos existentes, stack, sessão em memória e políticas.

FUTURO: execução de código, correção automática, editor especializado, uploads,
autosave, painel de revisão ADMIN e alterações nas políticas de aprendizagem.

## Tarefas

- [x] S10-T01 — inventário, recorte e jornada documentados.
- [x] S10-T02 — contrato de listagem e estados/interações em
  [ATTEMPT_EXPERIENCE_CONTRACT.md](ATTEMPT_EXPERIENCE_CONTRACT.md), incluindo
  falhas de salvamento/envio, concorrência e recuperação de sessão. Sem código.
- [x] S10-T03 — GET /api/v1/attempts paginado, exclusivo do dono, com título do
  snapshot e contagem/página em uma consulta. 15 testes passaram em 14,62 s
  (history, flow, schemas, repository), warnings como erros, PostgreSQL descartável.
  Isolamento inclusive ADMIN, ordenação, paginação vazia, READ ONLY, campos públicos
  e rejeição de queries extras nas operações antigas verificados.
- [ ] S10-T04 — lista autenticada, iniciar/retomar pelo desafio recomendado,
  navegação e leitura do snapshot da tentativa.
  Implementação concluída; validação específica das novas telas pendente.
  Build/TypeScript e regressão Playwright das recomendações passaram.
  Criação do script específico de tentativas rejeitada pela revisão automática
  com “blocked by policy”, sem motivo detalhado. Não marcar QA como concluído.
- [ ] S10-T05 — editar/salvar/enviar, alterações não salvas, conflitos e erros.
- [ ] S10-T06 — leitura da avaliação manual, espera por revisão e retorno ao painel.
- [ ] S10-T07 — regressão, build/TypeScript e navegador desktop/mobile com API real;
  registrar evidências e limites no fechamento da Sprint.

## Skills ativas

Documentação em `.ai/skills/documentation.md` nesta etapa. Aplicar arquitetura,
API, segurança, testes e skills pertinentes de frontend conforme cada tarefa.
Regras de negócio nos services; repositories não fazem commit.

## Definition of Done

- [x] Recorte e jornada definidos sobre os contratos existentes.
- [x] Listagem do dono documentada e testada.
- [ ] Tentativas recuperáveis após novo login.
- [ ] Salvamento/envio sem perda silenciosa de edição.
- [ ] Snapshot preservado; tentativa enviada somente leitura.
- [ ] Avaliação apresentada sem inventar resultado quando pendente.
- [ ] Isolamento, conflitos, acessibilidade e falhas verificados.
- [ ] Regressão e validação no navegador concluídas.

## Próxima tarefa

S10-T04 — concluir validação no navegador da lista, início/retomada e detalhe,
incluindo paginação, erros, retorno após login e troca de conta. Depois S10-T05.
