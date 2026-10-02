# Sprint 10 — Experiência de desafios

Concluída em 02/10/2026. Recorte em CHALLENGE_EXPERIENCE_PLAN.md e contrato em
ATTEMPT_EXPERIENCE_CONTRACT.md. Stack e monólito modular preservados.

## Entrega

GET /api/v1/attempts lista tentativas do dono, inclusive ADMIN, com paginação,
contagem e itens no mesmo snapshot SQL. Títulos vêm do snapshot histórico;
respostas e dados do revisor não são expostos no índice. Sem migration nova.

Frontend: lista, início/retomada por recomendação, leitura de contexto histórico,
editor textual, salvamento explícito, envio confirmado e avaliação manual.
Resposta enviada é somente leitura. Falha ao salvar impede submit; resultado
incerto consulta estado antes de outra ação. Conflito mantém versão local
divergente para cópia. Avisos de saída por links/histórico, logout e beforeunload.
React Router usa createBrowserRouter/RouterProvider para bloqueio de navegação.
Sem dependências adicionais ou execução de código.

Avaliação apresenta feedback/rubrica/data e resultados por skill, com atualização
manual e retorno ao painel. 404 revalida acesso antes de mostrar espera;
erro de consulta não é tratado como ausência de revisão. Sem polling.

## Validação

- Backend: `pytest backend/tests -q -W error --tb=short`, conexão de testes
  configurada localmente: **328 passed in 100.77s** em PostgreSQL descartável.
- Frontend: `npm --prefix frontend run build` aprovou TypeScript e Vite.
- Playwright/Chrome headless, frontend 127.0.0.1:5173, API real 127.0.0.1:8000,
  migrations até 0008 em banco descartável. Desktop 1440x1000, mobile 390x844.
- Aluno selecionou skill, iniciou desafio, salvou espaços/quebras/emoji e retomou
  pela lista após novo login. ADMIN alterou título/desativou o catálogo pela API;
  snapshot permaneceu intacto e a tentativa existente pôde ser enviada.
- Tela mostrou espera; outro ADMIN de teste publicou revisão MET pela API.
  Atualização manual mostrou feedback e classificação. Painel mostrou UserSkill
  504, consistente com base 500, dificuldade 100, peso 100 e tentativa 1.
  Desafio desativado não voltou às recomendações.
- Outra conta recebeu lista vazia e 404 ao acessar a tentativa do aluno.
  Texto HTML permaneceu literal, sem overlay, erro JS inesperado ou overflow.
- QA controlado das tarefas anteriores cobriu paginação, falhas/retry, resultado
  de envio perdido, conflito, limite Unicode, expiração, troca de conta/rota e
  cancelamento de navegação. Registros detalhados no contrato.

Browser plugin ausente: usado Playwright já disponível, sem instalar pacotes.
Scripts externos `%TEMP%/codetrack-attempt-real.py` e
`%TEMP%/codetrack-attempt-real.cjs`. Screenshots inspecionados:
`%TEMP%/codetrack-sprint10-real-desktop.png` e
`%TEMP%/codetrack-sprint10-real-mobile.png`.
API temporária encerrada e banco descartável removido. Banco local não migrado
nem populado por esse QA. Docker PostgreSQL ficou ativo e saudável para desenvolvimento.

## Ajustes durante validação

A primeira execução da regressão encontrou três erros de conexão porque o
container estava parado; após iniciá-lo, a execução completa passou. A primeira
asserção de score da fixture esperava 508 por cálculo incorreto: a política vigente
produz 504 neste caso. Corrigida somente a expectativa de teste e repetida a jornada.
Nenhuma falha da aplicação exigiu alteração de código nesta etapa final.

## Limites e próximo passo

Revisão ADMIN continua pela API; painel administrativo é FUTURO. Não há autosave,
execução/correção automática, upload ou editor especializado. Texto não salvo pode
ser perdido em expiração/encerramento abrupto; último PATCH prevalece entre abas.
Skills históricas são identificadas por ID quando o snapshot não registra nome.

Labels, foco, anúncios de estado, confirmação e navegação foram verificados;
não constitui auditoria completa WCAG ou com leitores de tela. Firefox/Safari,
produção e volume elevado não foram validados. Políticas de confiança e recomendação
continuam experimentais. Próximo trabalho: planejar Sprint 11 — testes e qualidade,
com inventário de riscos e escopo documentado antes de implementar novas mudanças.
