# Sprint 9 — Dashboard

Concluída em 01/10/2026. Contratos: [resumo](DASHBOARD_API.md),
[jornada](DASHBOARD_PLAN.md), [recomendações](RECOMMENDATION_API.md).

## Entrega

GET /api/v1/dashboard retorna perfil, contagens sem duplicação e progresso
paginado do dono, incluindo nomes atuais de skills inativas com vínculo próprio.
Uma consulta SQL, sem escrita. Dashboard em /dashboard apresenta esses dados,
seleção paginada de skill, recomendações explicadas e detalhe somente leitura.
Estados de loading, vazio e falha com retry; cancelamento de respostas antigas.

Login encaminha conta sem onboarding ao perfil antes de considerar retorno a
rota anterior. Conta com onboarding concluído chega ao painel por padrão.
Acesso direto autenticado ao painel continua permitido sem onboarding.

## Validação final

- Backend: `pytest backend/tests -q -W error --tb=short`, com conexão de testes
  configurada sem expor credenciais: **326 testes passaram em 116,64 s**.
- Frontend: `npm --prefix frontend run build`, TypeScript e Vite aprovados após
  as correções finais de redirecionamento e favicon.
- Playwright/Chrome headless, frontend em 127.0.0.1:5173 e API real em
  127.0.0.1:8000, PostgreSQL descartável com migrations até 0008.
- Desktop 1440x1000 e mobile 390x844: login, paginação do progresso, seleção
  preservada, recomendação, enunciado e código como texto, fechamento com retorno
  de foco, ausência de overflow, logout/troca de conta, onboarding e sessão em
  memória após reload. Título/URL corretos, sem overlay ou erros no console.
- Testes com respostas controladas nas tarefas anteriores cobriram falhas,
  retry, respostas fora de ordem, catálogo paginado e recurso indisponível.
- Revisados labels, agrupamento por fieldset/legend, headings, estados anunciados
  e foco de leitura. Não constitui auditoria completa WCAG ou com leitor de tela.

Browser plugin ausente: usado Playwright do cache, sem dependência nova no projeto.
Scripts e screenshots ficaram em diretório temporário fora do repo. API de teste
encerrada e banco descartável removido ao final; nenhum dado local foi migrado.

## Correções encontradas na validação

Retorno após logout mantinha /dashboard e tinha prioridade sobre onboarding de
uma conta nova. Corrigida a ordem no AuthPage e repetido o cenário com API real.
404 de favicon identificado no console: adicionado favicon SVG, repetida a
verificação sem erros. A primeira preparação de dados de teste também precisou
informar experiência declarada para respeitar a constraint de onboarding.

## Limites e próximo passo

Nenhuma migration nova, deploy ou execução de código. Enunciado é somente leitura;
rascunho/submissão na interface e painel ADMIN seguem FUTURO. Confiança e políticas
de recomendação continuam experimentais, sem calibração pedagógica. Não testados
Safari/Firefox, leitores de tela ou catálogos em escala de produção.

Próximo trabalho: planejar a Sprint 10 — experiência de desafios sobre as APIs
existentes, preservando ownership, histórico e avaliação manual. Definir recorte
antes de implementar.
