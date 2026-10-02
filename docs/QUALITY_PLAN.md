# Sprint 11 — Testes e qualidade

Planejamento em 02/10/2026 após a Sprint 10. Recorte baseado na jornada entregue
e nas lacunas observadas; não representa validação adicional já executada.
Regras de domínio e stack permanecem vigentes. Não criar funcionalidades de produto.

## Objetivo

Tornar a verificação do ciclo adaptativo reproduzível e revisar riscos concretos
antes do planejamento de deploy. Corrigir somente problemas demonstrados por
reprodução, com testes proporcionais; sem meta artificial de cobertura.

## Inventário e prioridades

| Área | Evidência atual | Trabalho autorizado |
| --- | --- | --- |
| Backend | 328 testes aprovados na Sprint 10, com PostgreSQL real descartável | Preservar regressão e identificar lacunas por risco |
| Configuração dos testes | Fixture migrated_database pula integração sem CODETRACK_TEST_ADMIN_URL | Distinguir modo rápido de validação completa; modo completo falha sem banco/configuração |
| Navegador | Jornadas Chrome passaram; scripts em TEMP dependem do cache local de Playwright | Criar harness e cenários versionados/reproduzíveis, com fixtures isoladas |
| Sessão/ownership | Testes por módulo e QA de duas contas disponíveis | Revisar transições, respostas obsoletas e limpeza de dados; acrescentar somente lacunas reais |
| Interface | Labels, foco, avisos e mobile verificados | Revisar teclado, recuperação de erro e navegação protegida de ponta a ponta |
| Execução/documentação | README ainda registra números históricos da Sprint 6 nas instruções de testes | Atualizar comandos, pré-requisitos, modos e evidências atuais |
| Automação | Nenhum workflow encontrado em .github/workflows nesta inspeção | Adicionar verificação de testes/build sem deploy, após contratos locais definidos |

Não rerodar toda a suíte na etapa de planejamento: a base é o fechamento
[SPRINT_10.md](SPRINT_10.md), não um novo resultado atribuído a esta Sprint.
Cobertura existente não prova ausência de falhas; um item da matriz pode concluir
que os testes atuais já bastam, sem criar testes duplicados.

## Recorte e sequência

1. S11-T01: inventário, prioridades e escopo neste documento.
2. S11-T02: matriz de riscos → comportamento esperado → testes existentes → lacunas;
   definir comandos/modos de validação e contrato do harness antes de implementá-lo.
3. S11-T03: tornar validação backend completa explícita e segura. Verificar banco
   antes de iniciar integração; impedir aprovação completa com skips de ambiente.
   Manter modo rápido útil e documentado. Usar fixture descartável já existente.
4. S11-T04: incorporar harness de navegador e casos críticos ao repositório;
   eliminar dependência de caminhos pessoais/cache TEMP. Cobrir jornada real e
   falhas relevantes com HTTP controlado; proteger dados de desenvolvimento.
5. S11-T05: executar revisão de sessão, autorização, recuperação de falhas e teclado;
   corrigir achados reproduzidos, com regressão dirigida e sem reescritas amplas.
6. S11-T06: automatizar testes backend/build e checks de navegador adequados em
   CI; atualizar instruções locais. Workflow versionado de qualidade, sem publicar
   aplicação, alterar ambiente remoto ou configurar secrets reais.
7. S11-T07: executar validação final, registrar achados/resoluções/limites e fechar
   a Sprint somente com os checks exigidos aprovados.

## Reprodutibilidade e proteção dos dados

- Harness e cenários de QA são entregáveis específicos desta Sprint, versionados
  como código de teste; relatórios, screenshots e tokens ficam fora do código
  versionado. Não copiar scripts temporários sem revisar fixtures e asserts.
- Criar apenas bancos com nome aleatório codetrack_test_UUID, migrar neles e
  removê-los em finally; nunca executar cleanup/migration de QA no banco local.
- Gerar credenciais de teste por execução, sem logs de senha/token/DATABASE_URL.
- Falta de banco/porta ocupada deve explicar pré-requisito, não reiniciar ou matar
  serviço alheio. Encerrar somente processos iniciados pelo harness.
- Reutilizar pytest, SQLAlchemy, Alembic e scripts npm existentes. Playwright já
  foi usado como ferramenta; sua disponibilidade reproduzível será definida na
  S11-T02. Dependência de desenvolvimento só se necessária a esse objetivo,
  justificada no contrato; não adicionar ferramentas genéricas de lint/coverage
  apenas para aumentar o número de checks.
- Validação completa deve indicar ausência de integrações puladas. Modo rápido
  não pode ser apresentado como garantia equivalente à jornada completa.
- CI usa PostgreSQL de teste e valores descartáveis, sem depender de .env pessoal.
  Não requer publicação ou chamada remota ao GitHub nesta etapa de implementação.

## Critérios de saída

Matriz de riscos revisada; comandos reproduzíveis em ambiente configurado;
backend completo com warnings como erros e sem skips de ambiente; frontend com
build/TypeScript aprovados; jornada real e cenários críticos de falha aprovados;
revisão de teclado/foco/feedback com limites explícitos; isolamento e cleanup
verificados; documentação atualizada e workflow de qualidade coerente com comandos
locais. Execução remota de CI, se não ocorrer, deve ser registrada como não validada.

Firefox/Safari e leitor de tela serão declarados como não verificados se não houver
ferramenta disponível; não alegar conformidade WCAG completa. Não estabelecer
limites de desempenho de produção sem medir e definir contexto.

## FUTURO

Deploy (Sprint 12), painel ADMIN, execução/correção automática, autosave,
controle de versão de rascunho entre abas, calibração pedagógica das políticas,
infraestrutura de observabilidade/alertas, pentest e ensaio de carga de produção.
Qualquer achado que exija mudança arquitetural significativa deve ser descrito
e submetido à aprovação antes da alteração, conforme AGENTS.md.
