# Sprint 8 — Recommendation

Concluída em 01/10/2026 no recorte skill-focus-v1.

## Entrega

Política experimental skill-focus-v1, schemas, seleção pura, repository,
RecommendationService e GET /api/v1/recommendations. Usuário escolhe uma skill
ativa de seus interesses; recomendações consideram cada habilidade envolvida,
dificuldade, confiança e histórico. ADMIN acessa somente seu próprio contexto.

Uma instrução SQL reúne o contexto; seleção e explicações não escrevem dados.
Primeira prática usa diagnóstico disponível ou exploração introdutória, sem criar
progresso fictício. Tentativas abertas e submissões sem revisão são excluídas;
recência reduz prioridade. Evidência fraca numa skill não é escondida por outra.

Contratos: [política](RECOMMENDATION_POLICY.md), [API](RECOMMENDATION_API.md).
Planejamento histórico: [RECOMMENDATION_PLAN.md](RECOMMENDATION_PLAN.md).

## Validação

Testes focados anteriores: 67 passaram, incluindo PostgreSQL descartável,
transação READ ONLY, contagem de consultas, HTTP e isolamento. Política testada
em 3.280 combinações e 120 permutações de entrada.

Build frontend com TypeScript aprovado em 01/10/2026. git diff --check aprovado;
Git mantém avisos de normalização LF/CRLF. Destinos dos links locais revisados
conferidos. Regressão final: `pytest backend/tests -q -W error --tb=short`, com
CODETRACK_TEST_ADMIN_URL configurada sem expor credenciais: **324 testes passaram
em 102,81 s**, incluindo bancos PostgreSQL descartáveis e migrations existentes.

A primeira execução aguardou conexão com PostgreSQL parado e foi interrompida.
Docker Compose foi iniciado e ficou saudável; a suíte foi reiniciada com timeout
de conexão de cinco segundos, somente no ambiente do processo de testes.

## Uso e limites

Rota disponível via Swagger, com Bearer e skill_id; limit padrão 5, máximo 10.
Não houve nova tela, migration ou deploy. Aplicar as migrations existentes até
0008 antes de usar esta versão; os testes aplicam migrations somente em bancos
descartáveis. A inicialização do container não aplica migrations ao banco local.

Escolhas numéricas são hipóteses de produto, não calibração pedagógica. Score e
confiança não representam probabilidade de sucesso. Dificuldade única comparada
a cada skill pode restringir desafios mistos e produzir lista vazia. Não relaxar
tetos para preencher resultados. O catálogo permanece acessível para escolha manual.

Não há interpretação do objetivo textual, pré-requisitos, metas numéricas por
objetivo, histórico persistido de sugestões, ML ou LLM. A consulta não reserva
conteúdo: AttemptService revalida disponibilidade ao iniciar a tentativa.
Não houve medição de desempenho com catálogo em volume de produção nem nova
verificação visual; frontend foi apenas compilado nesta tarefa.

## Próximo passo

Planejar o recorte da Sprint 9 — Dashboard, conforme roadmap, usando os contratos
já disponíveis. Dashboard e experiência de desafios no frontend seguem FUTURO
até abertura explícita do respectivo escopo em CURRENT_SPRINT.md.
