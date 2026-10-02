# CodeTrack — Current Sprint

## Sprint atual

SPRINT 11 — TESTS & QUALITY

Concluída em 02/10/2026. Fechamento em [SPRINT_11.md](SPRINT_11.md), com
validação local aprovada e CI remota explicitamente não executada.
Recorte em [QUALITY_PLAN.md](QUALITY_PLAN.md).
Sprint anterior concluída: [SPRINT_10.md](SPRINT_10.md).

## Escopo

Verificação reproduzível do ciclo entregue: configuração explícita dos testes,
harness de navegador versionado, revisão de sessão/ownership/falhas/teclado,
correção de achados comprovados, automação de qualidade e documentação.
Preservar stack, arquitetura e políticas de aprendizagem.

FUTURO: deploy (Sprint 12), funcionalidades novas de produto, painel ADMIN,
execução automática, autosave e controle de versão de rascunhos entre abas.

## Tarefas

- [x] S11-T01 — inventário, prioridades e recorte em QUALITY_PLAN.md.
- [x] S11-T02 — matriz de riscos/testes/lacunas e contrato dos modos fast/complete
  e do harness de navegador em QUALITY_CONTRACT.md. Dependência Playwright de QA
  justificada para reprodutibilidade; versão/instalação pendentes na S11-T04.
  Sem código ou novos resultados de testes nesta etapa.
- [x] S11-T03 — --quality-mode fast/complete, preflight PostgreSQL com timeout e
  erros seguros, falha de complete com skips e compatibilidade sem opção.
  Fast: 290 passed, 46 deselected em 14,99 s. Complete: 336 passed em 118,50 s,
  sem skips, PostgreSQL descartável, warnings como erros. Oito testes dos modos
  passaram após ajuste de encoding da captura de subprocessos no Windows.
  Comandos atualizados no README e backend/README; evidências no contrato.
- [x] S11-T04 — harness Python, Playwright 1.63.0 fixado como dev dependency,
  projetos controlados desktop/mobile e jornada real; tipagem de QA, relatórios
  ignorados, portas próprias e cleanup. Nove testes passaram sem skips/falhas;
  modo controlado isolado: 8 passed em 10,7 s; histórico dirigido: 2 passed em 4,3 s.
  Quatro testes de pré-requisitos/cleanup passaram em 4,46 s com PostgreSQL
  descartável, warnings como erros. Build e tipos aprovados. Instruções em
  frontend/e2e/README.md; evidências e limites em QUALITY_CONTRACT.md.
- [x] S11-T05 — revisão de sessão, ownership, falhas e teclado. Corrigida perda
  de foco ao salvar rascunho, reproduzida em desktop/mobile; regressão por teclado
  versionada. Harness: 11 aprovados, sem skips/falhas, cleanup confirmado.
  Backend dirigido: 9 passed em 12,63 s, PostgreSQL descartável e warnings como
  erros. Build/tipos aprovados; evidências e limites em QUALITY_CONTRACT.md.
- [x] S11-T06 — workflow Quality em push/PR/manual, Ubuntu 24.04, Python 3.12,
  Node 24.14.1 e PostgreSQL 17 descartável; actions fixadas por SHA, permissão
  somente leitura. actionlint aprovou. Execução local: backend completo
  340 passed em 121,24 s, sem skips; navegador 11 aprovados, cleanup confirmado;
  build/tipos e pip check aprovados. README raiz/frontend/QA atualizados.
  Execução remota Linux/GitHub ainda não realizada; limites no contrato.
- [x] S11-T07 — critérios de saída conferidos e fechamento em SPRINT_11.md.
  Evidências finais da S11-T06 mantidas (sem mudança posterior de código).
  Links locais/diff aprovados; portas QA livres, zero bancos descartáveis
  restantes, .env e relatórios ignorados. Limites de CI/acessibilidade registrados.

## Skills ativas

Documentação e testes locais em `.ai/skills` nesta etapa. Aplicar segurança,
code-review, debugging e arquitetura conforme achados; skills de frontend e
verificação visual quando houver execução/revisão da interface.
Regras de negócio nos services; repositories não fazem commit.

## Definition of Done

- [x] Recorte e prioridades documentados com base em evidências existentes.
- [x] Matriz de riscos e critérios de validação definidos.
- [x] Validação backend completa não aprova integrações puladas por ambiente.
- [x] Harness de navegador executável sem caminhos pessoais ou scripts TEMP.
- [x] Jornada real, recuperação de falhas e isolamento aprovados.
- [x] Revisão de teclado/foco e achados documentados com limites.
- [x] Automação e comandos locais atualizados, sem deploy.
- [x] Validação final e fechamento registrados.

## Próxima tarefa

Planejar Sprint 12 — deploy inicial, definindo recorte e pré-requisitos antes
de alterar configuração ou publicar. Sprint 11 encerrada; Sprint 12 ainda não
ativa. CI remota precisa ser conferida após publicação, sem presumir aprovação.
