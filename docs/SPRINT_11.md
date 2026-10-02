# Sprint 11 — Testes e qualidade

Concluída em 02/10/2026 no recorte de QUALITY_PLAN.md. Matriz de riscos,
contratos e evidências por tarefa em [QUALITY_CONTRACT.md](QUALITY_CONTRACT.md).
Stack, arquitetura e políticas de aprendizagem preservadas.

## Entrega

- Pytest com modos fast/complete: seleção explícita de integrações, preflight
  PostgreSQL seguro e modo completo que reprova configuração ausente e skips.
- Harness versionado com banco aleatório, migrations, fixtures, serviços próprios,
  readiness, timeouts e cleanup inclusive nas falhas exercitadas.
- Playwright 1.63.0 de desenvolvimento, tipos de QA separados e projetos
  controlados desktop/mobile mais jornada real com API/PostgreSQL descartáveis.
- Revisão de sessão, ownership, recuperação de falhas e teclado. Corrigida perda
  de foco ao salvar rascunho, com regressão que falhou antes e passou depois.
- Workflow Quality para push/PR/manual, backend completo, dependências, build
  e navegador; PostgreSQL 17 descartável, actions fixadas por SHA, sem deploy.
- Instruções locais atualizadas no README raiz, frontend e QA; comandos backend
  documentados no backend/README.

## Validação final

Consolidação dos checks mais recentes da S11-T06, executados após a correção de
foco e com o código final desta Sprint. S11-T07 alterou apenas documentação;
não repetiu a suíte sem mudança de código ou novo achado.

| Check | Resultado |
| --- | --- |
| Backend complete, PostgreSQL descartável, -W error | 340 passed in 121.24s; nenhum skip |
| Harness de navegador e tipos de QA | 11 aprovados; zero skips, falhas ou flaky |
| Build e tipos do produto | Aprovados |
| pip check | Sem dependências incompatíveis |
| Workflow actionlint | Nenhum diagnóstico |
| git diff --check | Aprovado |

Navegador: Chromium no Windows, localhost:4173/API:8100, desktop 1440x1000 e
mobile 390x844. Browser plugin ausente; usado Playwright do projeto.
Jornada real cobre login, seleção por skill, início, resposta Unicode, retomada,
snapshot após catálogo alterado/inativo, envio, revisão ADMIN pela API,
feedback, progresso conhecido 504 e isolamento de outra conta. Casos controlados
cobrem falhas de salvamento/envio, reconciliação, conflito, expiração, respostas
tardias, pendência versus erro, paginação, saída protegida e continuidade por teclado.
Mocks não são apresentados como prova de integração.

No fechamento foram conferidos links locais dos documentos de execução/qualidade
(nenhum ausente), relatório final com 11 expected/0 skipped/0 unexpected/0 flaky,
portas 4173/8100 livres e **zero bancos codetrack_test_* restantes**. .env e
frontend/test-results/results.json continuam ignorados. Nenhum banco de
desenvolvimento foi migrado/populado pelo QA. Artefatos são sobrescritos a cada
execução e não constituem histórico permanente.

## Limites

GitHub Actions não foi executado remotamente e Ubuntu não foi reproduzido neste
computador. Validação estática do workflow e execução Windows não comprovam CI
Linux; conferir a aba Actions após publicação. Não houve commit/push nesta etapa.
O contrato permite fechar a Sprint com essa limitação explicitamente registrada.

Revisão de acessibilidade dirigida, sem auditoria WCAG completa, leitor de tela,
Firefox/Safari ou dispositivo físico. Avisos de fechamento dependem do navegador.
Texto não salvo pode ser perdido na expiração/encerramento abrupto; o último
salvamento prevalece entre abas. Políticas de confiança/recomendação permanecem
experimentais. Produção, carga, pentest e calibração pedagógica não foram validados.

## Próximo passo

Planejar Sprint 12 — deploy inicial, antes de alterar configuração ou publicar:
inventariar requisitos de Vercel, Render e PostgreSQL, definir configuração,
migrations, segurança, verificação e recuperação. Executar CI remota após
publicação antes de usar seu resultado como evidência de release. Deploy,
painel ADMIN, autosave e execução automática continuam FUTURO até seu recorte.
