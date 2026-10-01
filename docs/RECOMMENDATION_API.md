# Contrato HTTP — recomendações S8-T03

Status: schemas, rota, repository e service implementados na S8-T05.
Política: [skill-focus-v1](RECOMMENDATION_POLICY.md).

## Requisição

`GET /api/v1/recommendations?skill_id=1&limit=5`

Bearer obrigatório. skill_id obrigatório, inteiro 1–2147483647; limit inteiro
1–10, padrão 5. Parâmetros extras rejeitados. Sem offset: retorna as primeiras
sugestões do contexto atual, não uma página do catálogo.

Identidade vem da autenticação; ADMIN também recebe apenas seu próprio contexto
e as mesmas restrições de catálogo. Skill focal precisa estar ativa e pertencer
a uma categoria de interesse atual. Não exigir UserSkill ou diagnóstico; não
exigir flag onboarding_completed além da associação de interesse necessária.

## Resposta

200 retorna policy_version="skill-focus-v1", generated_at UTC, skill_id, limit,
items e empty_reason. Sem itens, empty_reason="NO_ELIGIBLE_CHALLENGES"; com itens,
empty_reason=null. Não expor contagem ou detalhes dos candidatos excluídos.

Cada item contém challenge_id, title, difficulty_score, estimated_minutes,
kind (EXPLORATION/PRACTICE/PROGRESSION/REVIEW), practiced_recently, reason e skills.
Cada skill contém skill_id, weight, source, reference_score e confidence.

| source | reference_score | confidence |
| --- | --- | --- |
| USER_SKILL | score persistido | string decimal, preservando precisão |
| ASSESSMENT | score do diagnóstico | null |
| NONE | null | null |

Âncora técnica 100 nunca aparece como score pessoal. A lista de skills é ordenada
por ID, sem duplicatas e com pesos somando 100. Toda sugestão inclui a skill focal.
Não retornar IDs de avaliações, revisores, respostas ou acumuladores internos.
Campos e consistência validados em recommendations/schemas.py.

reason é produzido por templates no service a partir dos fatores da seleção;
deve indicar evidência provisória/limitada e prática recente quando aplicável.
Não descrever distância próxima de todas as skills quando somente uma está próxima.
Texto não contém probabilidades de sucesso ou domínio comprovado.

## Erros e efeitos

- 401: autenticação ausente/inválida, com WWW-Authenticate: Bearer.
- 404: skill inexistente, inativa ou fora dos interesses, sempre com detail
  “Skill indisponível para recomendação.”, sem distinguir os casos.
- 422: query inválida ou extra, seguindo o handler existente.
- Cache-Control: no-store no sucesso e nesses erros.

GET não persiste Recommendation, não inicia tentativa nem modifica progresso,
evidências ou datas. Sem candidatos não é erro; retorna 200 com lista vazia.
O catálogo continua disponível para escolha manual.

## Estratégia de consultas e responsabilidades

Router adapta HTTP e autenticação. RecommendationService valida seleção focal,
prepara dados para a política pura e constrói explicações. Repository apenas lê.
Não criar tabelas, migrations, cache ou dependências para este recorte.

Obter o conjunto em uma instrução SQL com subconsultas/CTEs, para uma visão
consistente por instrução no PostgreSQL sem alterar o isolamento global:

1. CTE de skill focal autorizada por user_id e UserInterest.
2. Candidatos ativos que contêm a focal; excluir aqueles com skill inativa.
3. Links de todas as skills do candidato, não somente a focal.
4. LEFT JOIN de UserSkill filtrado pelo dono. Diagnóstico mais recente por skill
   do dono via ordenação completed_at DESC/Assessment.id DESC, concluído até agora.
5. Histórico agregado por challenge_id do dono: existência de tentativa aberta,
   submissão sem avaliação, datas futuras e última submissão. Usar EXISTS para
   avaliações, evitando multiplicação pelas classificações por skill.

Partir da focal com LEFT JOIN aos candidatos permite distinguir focal inválida
(nenhuma linha) de focal válida sem candidatos (linha sem desafio). Agrupar linhas
por desafio no repository em estruturas tipadas; nenhuma consulta por candidato.
Passar um único instante UTC como parâmetro da instrução e da política.

Filtrar candidatos pela focal no banco, mas não aplicar LIMIT por ID antes da
seleção. Política aplica tetos individuais, classificação, recência e ordenação
ao conjunto completo; somente depois limita a resposta. Medir custo com catálogo
real antes de otimizar ou definir novos limites funcionais.

A resposta não reserva conteúdo. AttemptService continua revalidando visibilidade
ao iniciar tentativa, pois o catálogo pode mudar após a consulta.

## Validação

`pytest backend/tests/test_recommendation_schemas.py -q -W error --tb=short`:
25 testes passaram em 0,19 s. Cobrem limites e extras de query, serialização
Decimal, fontes de evidência incompatíveis, ausência explícita, skill focal,
duplicação, soma dos pesos e timestamp com fuso. Na S8-T03 ainda não havia rota.

S8-T04 validou seleção e fronteiras da política. Na S8-T05, comando pytest com
test_recommendation_integration.py, test_recommendation_policy.py e
test_recommendation_schemas.py, opções -q -W error --tb=short: 67 testes passaram
em 5,67 s. PostgreSQL descartável; consulta contada (uma instrução SQL), executada
sob SET TRANSACTION READ ONLY, incluindo HTTP. Cobertos ownership inclusive ADMIN,
diagnóstico de terceiros/futuro ignorado, empate por ID, precedência de UserSkill,
catálogo inativo, submissão sem revisão, tentativa aberta, recência e lista vazia.
S8-T06 concluída: 324 testes passaram em 102,81 s na regressão completa em
01/10/2026; TypeScript/build frontend aprovados. [Fechamento](SPRINT_8.md).
Não há medição de desempenho
em volume de produção nem validação pedagógica.
