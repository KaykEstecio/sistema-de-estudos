# Dashboard — contrato S9-T02

Status: contrato e backend implementados em 01/10/2026 na S9-T03.
Recorte: [DASHBOARD_PLAN.md](DASHBOARD_PLAN.md).

## Requisição e autorização

`GET /api/v1/dashboard?limit=10&offset=0`

Bearer obrigatório. limit inteiro 1–50, padrão 10; offset inteiro >= 0, padrão 0.
Paginação aplica-se somente à lista de progresso. Outros parâmetros, inclusive
user_id, são rejeitados. STUDENT e ADMIN consultam exclusivamente a identidade
autenticada. Não exigir onboarding concluído, interesses, Assessment ou UserSkill.

200 inclui Cache-Control: no-store. 401 para autenticação ausente/inválida com
WWW-Authenticate: Bearer; 422 para query inválida ou extra. Esses erros também
incluem no-store. Usuário removido é tratado como autenticação inválida, sem
retornar resumo fictício. Sem dados é 200, não 404.

## Resposta

```json
{
  "profile": {
    "name": "Ana",
    "onboarding_completed": true,
    "primary_goal": {"goal_type": "Backend", "description": null},
    "interests": [{"category_id": 1, "name": "Programação"}]
  },
  "summary": {
    "tracked_skills": 1,
    "submitted_attempts": 3,
    "pending_reviews": 1
  },
  "progress": {
    "items": [{
      "skill_id": 1,
      "name": "Python",
      "is_active": true,
      "score": 520,
      "confidence": "0.047619",
      "attempts": 1,
      "successful_attempts": 1,
      "last_practiced_at": "2026-09-30T12:00:00Z",
      "updated_at": "2026-09-30T13:00:00Z"
    }],
    "total": 1,
    "limit": 10,
    "offset": 0
  }
}
```

profile: nome atual e flag do usuário, objetivo principal ou null e interesses
atuais com nomes das categorias, ordenados por category_id crescente. Objetivo é
texto declarado, sem inferência automática de skills ou metas. Não expor email,
role, hash, token ou objetivos de terceiros neste resumo.

| Contador | Definição exata |
| --- | --- |
| tracked_skills | Quantidade de UserSkill do dono, inclusive skills inativas |
| submitted_attempts | Quantidade de ChallengeAttempt do dono com status SUBMITTED |
| pending_reviews | Tentativas SUBMITTED do dono sem AttemptEvaluation |

Contagens são totais, independentes da página. pending_reviews <= submitted_attempts.
Uma tentativa conta uma vez, mesmo envolvendo várias skills. Repetições são
tentativas distintas; não chamar submitted_attempts de “desafios concluídos” ou
“acertos”. Avaliação INSUFFICIENT_EVIDENCE e avaliação anterior à Sprint 7A já são
revisões recebidas; não entram em pending_reviews. Sem registros, todos valem zero.

progress.total = summary.tracked_skills. items apresenta somente UserSkills
existentes, sem criar linhas para interesses ou diagnóstico. Ordem:
last_practiced_at DESC, skill_id ASC como desempate. Datas com fuso e saída UTC.
Offset além da última página retorna items vazio, mantendo contagens reais.

Nome e is_active vêm do catálogo **atual**, associados ao progresso do dono;
não são snapshots do nome no dia da prática. Skill desativada permanece visível
nessa lista, mas não ganha acesso geral ao catálogo inativo. Não retornar nomes
de skills inativas sem UserSkill do dono. Preservar o comportamento da rota
existente /users/me/skills e seus consumidores.

attempts/successful_attempts dentro de cada linha mantêm o contrato de UserSkill:
evidências avaliáveis aplicadas e classificações MET. Não somá-los para obter
total de tentativas do usuário. confidence é string decimal e índice experimental,
não percentual de domínio. Sem média global de score ou confidence.

## Consulta e responsabilidades

DashboardRepository lê dados existentes; DashboardService compõe o resumo;
router trata HTTP. Schemas de entrada/saída próprios. Sem migrations, tabelas,
commit, atualização de datas, criação de progresso ou invocação do recomendador.

Usar uma instrução SQL para o resumo, com agregações independentes por usuário:
contar progresso, contar tentativas e pendências com EXISTS/NOT EXISTS, obter
objetivo principal, interesses e página de UserSkill vinculada a Skill.
CTEs/subconsultas evitam multiplicar contagens ao juntar relações um-para-muitos.
Agregar coleções separadamente ou agrupá-las a partir de linhas tipadas, mantendo
limite/offset na página de progresso. Validar com PostgreSQL real, incluindo página
vazia com totais não zero. Sem consulta por linha de progresso.

Consistência garantida dentro da instrução; páginas em requisições distintas
podem mudar após novas avaliações. Não manter snapshot de navegação entre requests.

## Seleção de skills e integração frontend

Resumo não inclui todas as skills do catálogo. Para recomendações:

1. Usuário escolhe categoria dentre profile.interests; sem interesses, exibir
   ação para configurar perfil. Não selecionar skill automaticamente.
2. Consultar GET /api/v1/skills?category_id=...&is_active=true&limit=20&offset=0.
   Filtrar is_active=true explicitamente também para ADMIN. Oferecer páginas
   anterior/próxima usando total/limit/offset; não buscar todo o catálogo de uma vez.
3. Ao selecionar skill, carregar /recommendations?skill_id=...; cancelar/ignorar
   resposta anterior ao mudar categoria/skill. Limpar seleção de skill ao trocar
   categoria. Não usar a primeira página como se contivesse o catálogo completo.
4. Progresso pagina separadamente via /dashboard. Trocar página não deve apagar
   seleção de recomendações válida. Se novo resumo retirar a categoria de interesse,
   limpar seleção e sugestões; 404 do recomendador também exige revalidar contexto.

Falha do resumo apresenta erro com nova tentativa; não substitui dados por zeros.
Falha de catálogo/recomendação/detalhe tem estado local, preservando resumo válido.
Mudança de conta e 401 descartam dados pessoais em memória. Nomes e objetivos
renderizados como texto. Ações para diagnóstico seguem as restrições já existentes.

## Critérios de validação da implementação

- Contagem correta com tentativa de várias skills, repetição, aberta, submetida,
  avaliada e revisão insuficiente/legada; excluir registros de outras contas.
- Perfil incompleto, objetivo null, interesses vazios, sem progresso, página final
  e offset excedente. Desempate estável e contagens independentes da paginação.
- Nome atual de skill desativada com progresso próprio aparece; sem vínculo próprio
  não aparece. ADMIN também não recebe dados de outro usuário.
- Resposta não contém campos privados, SQL não gera N+1 e funciona em transação
  READ ONLY. Conferir filtros do dono em cada agregação.
- HTTP: 200, 401, 422 e no-store; validação de limites e parâmetros extras.
- Frontend posterior: loading/erro/vazio, paginação de ambas as listas, troca
  de categoria/skill/conta e respostas fora de ordem.

## Validação desta tarefa

Schemas, DashboardRepository, DashboardService e rota implementados; sem migration.
Uma instrução SQL reúne contagens independentes, interesses agregados em JSON e
CTE da página de progresso; objetivo principal associado sem duplicar resultados.
Datas de progresso normalizadas para UTC pelo service.

`pytest backend/tests/test_dashboard.py backend/tests/test_progress_access.py
backend/tests/test_recommendation_integration.py -q -W error --tb=short`:
6 testes passaram em 8,66 s, com PostgreSQL descartável. Validados READ ONLY,
consulta única, contagens de tentativas com múltiplas skills/revisão insuficiente,
paginação e offset excedente, empate por skill_id, nome atualizado de skill
inativa, perfil vazio, conta ADMIN isolada, 401/422/no-store e campos públicos.
A regressão completa e a interface permanecem nas próximas tarefas da Sprint.
