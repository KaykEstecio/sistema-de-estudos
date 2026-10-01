# Sprint 7A — UserSkill

Concluída em 30/09/2026, conforme política experimental aprovada pelo usuário.

## Entrega

- Política pura manual-skill-v1 com Decimal e arredondamento reproduzível.
- Migration 0008: UserSkill, acumuladores de confiança, origem inicial e
  SkillEvidence com unicidade por avaliação/skill e estados antes/depois.
- SkillService aplica avaliações novas na mesma transação de EvaluationService.
  Lock por usuário serializa o progresso; falhas desfazem todas as alterações.
- Primeira evidência avaliável usa diagnóstico elegível anterior à tentativa ou
  base 500. Evidência insuficiente registra descarte, sem criar progresso.
- Reenvios não duplicam evidências. Revisão tardia preserva a maior submitted_at.
- GET /api/v1/users/me/skills: paginação, identidade autenticada e no-store.

Contratos: [política](USER_SKILL_POLICY_DRAFT.md),
[persistência e integração](USER_SKILL_STORAGE.md), [API](USER_SKILL_API.md).

## Validação final

- `pytest backend/tests -q -W error --tb=short`: **257 testes passaram em 90,89 s**,
  com CODETRACK_TEST_ADMIN_URL configurada sem expor credenciais. Inclui PostgreSQL
  descartável, migrations upgrade/downgrade e alembic check, precisão Decimal,
  limites, inicialização, rollback, idempotência, ownership e concorrência.
- `npm --prefix frontend run build`: TypeScript e build Vite passaram.
- `git diff --check`: passou. Git avisa sobre normalização LF/CRLF no Windows;
  não foram encontradas falhas de whitespace pelo check configurado no projeto.
- Destinos dos links locais dos documentos revisados conferidos.

## Uso e limites

Aplicar `alembic upgrade head` seguindo o README antes de iniciar esta versão.
Nesta Sprint, migrations foram validadas em bancos descartáveis; a migration 0008
não foi aplicada ao banco de desenvolvimento por estas tarefas. Sem deploy.

Não há backfill de avaliações antigas nem recálculo silencioso. O diagnóstico
continua independente e não cria UserSkill ao ser concluído. A base escolhida na
primeira evidência permanece registrada e não é sobrescrita por novo diagnóstico.

Score, expectativa e confiança são hipóteses experimentais, sem calibração
empírica. Confiança representa quantidade/estabilidade de evidências, não
probabilidade de domínio; revisões enviesadas podem ser consistentemente erradas.
Não há medição de ajuda, tempo efetivo ou execução automática de código.

A consulta do progresso está disponível pela API/Swagger. Não houve nova tela
nem validação visual adicional nesta Sprint. Recommendation, dashboard e
experiência de desafios no frontend permanecem FUTURO.

## Próximo passo

Planejar o recorte da Sprint 8 — Recommendation, com critérios determinísticos
explícitos e testes esperados antes de implementar. Este fechamento não autoriza
regras ou coeficientes novos nem completa o ciclo adaptativo.
