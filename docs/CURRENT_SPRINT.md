# CodeTrack — Current Sprint

## Sprint atual

SPRINT 12 — DEPLOY INICIAL (PLANEJAMENTO)

Planejamento iniciado em 05/10/2026. S12-T01 concluída em
[DEPLOY_PLAN.md](DEPLOY_PLAN.md); nenhuma publicação/configuração de produção.
Próxima tarefa: S12-T02 — definir contrato de configuração, roteamento,
migrations, validação e recuperação. Implementação e criação de recursos
dependem dessas definições; não implementar funcionalidades novas de produto.

## Refinamento visual autorizado em 05/10/2026

Preferência visual atual: manter a inspiração no Duolingo com foco na cor azul.
Azul aplicado à marca, botões, links, seleção, cartões e medidores; tema escuro
usa azul luminoso sobre superfícies azul profundo. Violeta permanece secundário.
Validação da paleta azul: build/tipos e inspeção Playwright nos dois temas em
320/390/768/1440 px aprovados, sem overflow ou erros de console; cleanup
confirmado. Contraste dos pares principais de ação/link verificados >= 4,8:1.

Direção adicional solicitada: Duolingo como inspiração, a partir de link do
Mobbin. A página do Mobbin não ficou acessível; consultado o material oficial
[Core tabs redesign](https://blog.duolingo.com/core-tabs-redesign/).
Aplicados tipografia Nunito local com licença OFL, botões com relevo, cantos
arredondados, ícones decorativos na navegação/indicadores, etapas conectadas no
cadastro/login e paletas verde/azul/violeta com escuro azul profundo.
Preservados os contratos, revisão manual e indicadores reais; sem novas
funcionalidades de gamificação ou dependências npm.
Validação desta direção: build/tipos aprovados, 15 testes Playwright sem
falhas/skips; inspeção adicional com banco descartável em 320/390/768/1440 px
nos dois temas, sem overflow/overlay/erros de console. Capturas atualizadas em
TEMP/codetrack-refinement-qa; cleanup confirmado. Sem commit/deploy.

Novo pedido: evoluir o design e incluir tema escuro. Autorizados temas claro,
escuro e automático, preferência local persistida e adaptação ao sistema;
refinamento do painel/controles mantendo contratos e regras existentes.
Validar persistência, teclado, contraste e jornada nos dois temas.

Implementado: seletor Claro/Escuro/Automático, inicialização antes do React,
preferência codetrack.theme no navegador, acompanhamento do sistema e sync
entre abas, com fallback para storage bloqueado. Paletas por variáveis CSS
abrangem superfícies, controles, mensagens e editor; color-scheme acompanha a
seleção. Painel em duas colunas no desktop e medidores do score real por skill.
Testes versionados de tema: dois cenários em cada viewport; jornada real agora
em escuro e casos controlados em claro. Build/tipos e 15 testes passaram após
ajustes finais de cabeçalho/contraste, sem skips/falhas, cleanup confirmado.
Contrastes calculados dos pares principais de texto >= 4,5:1; bordas de campos
reforçadas. Não equivale a auditoria integral de acessibilidade.
Inspeção visual final com banco descartável em ambos os temas: cadastro, painel,
tentativas, resolução, perfil e seleção do diagnóstico em 320/390/768/1440 px,
sem overflow, overlay ou erros de console; execução temporária aprovada e cleanup
confirmado. Capturas TEMP/codetrack-refinement-qa/dark-*.png e light-*.png,
com transições finalizadas para comparar as cores estáveis. Demais limites de
navegador/leitor de tela permanecem. Nenhum commit/deploy realizado.

Pedido explícito do usuário: refinamento visual da interface antes de continuar
o deploy. Recorte: navegação ativa, tipografia, cores, espaçamento, formulários,
painel e composição da resolução de desafios em desktop/mobile. Preservar rotas,
contratos, dados, autenticação e regras de aprendizagem. Sem dependências novas.
Validar build/tipos, jornada Playwright e capturas das telas afetadas. O contrato
de deploy S12-T02 será retomado depois deste refinamento.

Concluído: navegação por NavLink com indicação de página atual e destino do
atalho de conteúdo focável; login/cadastro em composição de duas colunas no
desktop, com formulário primeiro no mobile; paleta verde e neutros, tipografia
local, espaçamento e estados de controles consistentes. Painel agrupa perfil e
indicadores; resolução dispõe contexto e resposta lado a lado no desktop.
Formulários, seleção de habilidades, tentativas e avaliação compartilham o estilo.
Não foram adicionadas dependências, dados demonstrativos no produto ou mudanças
de API/regras. Identificadores históricos de skills continuam vindo do contrato.

Validação em 05/10: build/TypeScript aprovados; 11 testes do harness passaram,
sem skips/falhas, cleanup confirmado. Inspeção adicional temporária com API e
banco descartáveis aprovou cadastro, painel, tentativas, resolução, perfil e
seleção do diagnóstico em 320/390/768/1440 px, navegação ativa e ausência de
overflow/overlay/erros de console. Login também inspecionado em desktop/mobile.
Capturas em TEMP/codetrack-refinement-qa e TEMP/codetrack-login-*.png; scripts
temporários não são testes de regressão versionados. Chromium Windows via
Playwright (Browser plugin ausente). Sem teste de leitor de tela ou outros
motores; não declara auditoria WCAG. A suíte backend não foi repetida nesta
alteração de apresentação. Alterações ainda sem commit.

## Histórico da Sprint anterior

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

S12-T02 — contrato de deploy conforme DEPLOY_PLAN.md. Sprint 11 encerrada;
Sprint 12 em planejamento. CI remota precisa ser conferida após publicação,
sem presumir aprovação. Nenhum recurso externo criado nesta etapa.
