# Sprint 7 — Avaliação manual

Concluída em 29/09/2026 no recorte qualitativo escolhido pelo usuário.
Contrato: [EVALUATION_CONTRACT.md](EVALUATION_CONTRACT.md).

## Entrega

Migration 0007, modelos de avaliação/resultados por skill, schemas estritos,
repository, EvaluationService e três rotas HTTP. ADMIN revisa tentativas
submetidas de outros usuários por rota específica. O dono consulta sua avaliação;
as permissões das rotas originais de tentativas permanecem inalteradas.

Classificações NOT_MET, PARTIALLY_MET, MET e INSUFFICIENT_EVIDENCE, com justificativa
por skill e feedback geral. Evidências ligadas ao snapshot histórico, sem executar
código ou presumir testes, dicas e tempo efetivo. Uma avaliação por tentativa,
repetição idêntica pelo mesmo revisor retorna o registro existente; divergência
ou outro revisor geram conflito. Lock, unicidade e transação preservam atomicidade.

## Validação

- Suíte completa: `pytest backend/tests -q -W error --tb=short`, com
  CODETRACK_TEST_ADMIN_URL configurada sem expor credenciais: 229 testes passaram
  em 84,30 segundos, incluindo bancos PostgreSQL descartáveis.
- Correção identificada na revisão: handler de validação 422 agora retorna
  Cache-Control: no-store. Teste HTTP reexecutado após a correção: 1 passou
  em 2,66 segundos; assegura cabeçalho em entrada inválida.
- `npm --prefix frontend run build`: TypeScript e build aprovados.
- `git diff --check`: aprovado.
- Upgrade/downgrade e alembic check testados em banco isolado, preservando as
  tentativas anteriores. Concorrência, rollback após flush, ownership, mudança
  de role, autorrevisão, limites, normalização e reenvios cobertos.

## Uso e limites

Aplicar `alembic upgrade head` conforme README antes de usar no banco local.
Nesta Sprint, migrations foram aplicadas somente a bancos de teste; não houve
alteração de dados locais, promoção de contas ou publicação em produção.
Rotas documentadas no OpenAPI/Swagger; sem painel administrativo ou UI de review.
Não há listagem de tentativas para revisão: o ADMIN informa o ID.

A API valida estrutura e autorização, não a qualidade pedagógica do feedback.
Avaliação é imutável; correções/reavaliações exigem evolução futura explícita.
Não há execução automática, score, confidence ou atualização de UserSkill.
S7-T04 foi adiada conscientemente, não implementada nem considerada concluída.

## Próximo passo

Planejar UserSkill e os critérios de atualização antes de iniciar Recommendation.
A classificação qualitativa não deve ser convertida em nota por coeficientes
inventados. Definir inicialização, fórmula, pesos, confiança e idempotência.
