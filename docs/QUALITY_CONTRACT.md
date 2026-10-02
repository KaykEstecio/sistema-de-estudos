# Qualidade — matriz e contrato S11-T02

Definido em 02/10/2026. Modos backend implementados na S11-T03; harness de
navegador implementado na S11-T04. Base: QUALITY_PLAN.md e fechamento SPRINT_10.md.

## Matriz por risco

| Risco | Comportamento exigido | Evidência disponível no repositório | Lacuna/ação |
| --- | --- | --- | --- |
| Identidade inválida/role | 401/403 e nenhuma promoção pelo cliente | test_tokens, test_login, test_identity, test_user_schemas | Revisar cenários atuais; não duplicar sem lacuna |
| Acesso a tentativas de terceiro | 404 inclusive ADMIN nas rotas do dono | test_attempt_flow, test_attempt_history, test_evaluation_http | Consolidar troca de conta no navegador |
| Histórico perdido/edição após envio | Snapshot independente, SUBMITTED imutável | test_attempt_repository, test_attempt_flow | Jornada versionada com catálogo alterado/inativo |
| Corrida/rollback parcial | Uma aberta por par; submit idempotente; transações atômicas | test_attempt_flow, test_catalog_concurrency, test_evaluation_service, test_skill_integration | Revisar asserts de domínio; adicionar só reprodução ausente |
| Revisão indevida | ADMIN não autor, conjunto exato de skills, avaliação imutável | test_evaluation_http, test_evaluation_schemas, test_evaluation_service | Jornada real com revisor separado |
| Score/confiança incorretos | Política por skill, limites e insuficiência sem falso erro | test_skill_policy, test_skill_integration, test_progress_access | Reutilizar testes; validar valor conhecido no ciclo real |
| Recomendação incorreta | Elegibilidade por skill, histórico, inativos e pending | test_recommendation_policy, test_recommendation_integration | Jornada após revisão e catálogo desativado |
| Resumo/índice vazam dados | Contagem e página do dono, snapshot e no-store | test_dashboard, test_attempt_history | Paginação/vazio e limpeza entre contas no navegador |
| PATCH falha mas resposta é enviada | Submit depende de PATCH confirmado | QA temporário S10-T05, sem teste versionado | Versionar cenário HTTP controlado prioritário |
| Resposta do submit se perde | GET reconcilia; não cria tentativa nova | QA temporário S10-T05 | Versionar resultado incerto, GET falha/retry |
| Conflito apaga texto local | Preservar divergente para cópia | QA temporário S10-T05 | Versionar conflito SUBMITTED |
| Resposta tardia após logout/rota | Abort/geração, nenhum dado reintroduzido | AuthProvider e QA temporários S9/S10 | Versionar cenário determinístico com resposta atrasada |
| 404 de avaliação vira espera falsa | Confirmar acesso/status; erro distinto de pendência | QA temporário S10-T06 | Versionar 404 com falha de confirmação e 503 |
| Saída/teclado perde edição | Confirmação, foco/labels e operação compreensível | QA de bloqueio S10-T05; verificação visual básica | Revisão dirigida de teclado/histórico/logout e limites |
| Testes aprovam sem integração | Modo completo não aceita ausência de configuração ou skips | migrated_database hoje usa pytest.skip sem configuração | S11-T03: preflight e falha explícita |
| QA depende de máquina pessoal | Harness reproduzível, cleanup e sem secrets em logs | Scripts TEMP/cache pessoal, não versionados | S11-T04: harness/cenários versionados |

Os nomes na coluna de evidências referem-se a `backend/tests/test_*.py` quando
não indicados como QA temporário. Existência de arquivo não implica cobertura
de qualquer variação; S11-T05 deve conferir asserts antes de adicionar testes.
Resultados históricos não substituem execução final da Sprint.

## Backend: modos explícitos

Opção pytest `--quality-mode=fast|complete` implementada na S11-T03; ausência da
opção mantém compatibilidade com execução pytest anterior. Comandos a partir da raiz:

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests --quality-mode=fast -q -W error
& backend/.venv/Scripts/python.exe -m pytest backend/tests --quality-mode=complete -q -W error
```

Fast executa testes independentes de PostgreSQL e reporta integrações como
deselecionadas, não como aprovadas. Identificar integração pela dependência
resolvida de migrated_database na coleta, sem manter lista manual de nomes.
Se surgir outra fixture de banco, registrá-la explicitamente nesse mecanismo.
Não iniciar Docker nem carregar automaticamente .env no pytest.

Complete exige CODETRACK_TEST_ADMIN_URL definido no ambiente. Antes de executar
testes, validar URL PostgreSQL e conexão SELECT 1 com tempo finito (cinco segundos
para conexão), sem imprimir URL, credenciais ou stack trace de configuração.
Erro termina com código não zero e instrução curta sobre configuração/banco.
Permissão de criar bancos continua sendo exercitada pela fixture descartável.
Não permitir URL de driver/engine alheio à stack. Descartar conexão preflight.

Em complete, qualquer teste skipped torna a saída não zero, inclusive se o pytest
retornar sucesso por padrão. Não há exceção autorizada nesta Sprint; se for
necessária, documentar caso/razão antes de criar whitelist. Falhas de testes
mantêm seu código normal. Não esconder skips, failures ou resultado da coleta.
Os testes de domínio existentes permanecem intactos.

Configuração local segue backend/README.md: URL administrativa obtida localmente,
sem copiar valores reais para comandos/documentos versionados. CI recebe URL de
PostgreSQL descartável pelo ambiente, sem .env de desenvolvedor. Os números de
testes não são fixados como condição de aprovação, pois mudam com a suíte.

## Harness de navegador

Entregáveis previstos: módulo Python em backend/scripts para preparação/cleanup,
configuração Playwright e testes em frontend/e2e, scripts npm test:e2e. São código
de QA solicitado no recorte, versionado; capturas/relatórios ficam ignorados ou
em diretório temporário. Não versionar os artefatos de execução.

Playwright como dependência de desenvolvimento é necessário para eliminar caminho
pessoal do cache e permitir instalação reproduzível por npm ci. Justificativa
limitada a QA; não entra no bundle de produto. Definir/pinar versão e atualizar
lockfile na S11-T04 após verificar compatibilidade. Nenhum framework adicional de
testes frontend ou ferramenta de coverage/lint previsto.

Comando planejado de jornada completa:

```powershell
& backend/.venv/Scripts/python.exe backend/scripts/browser_qa.py
```

O harness deve:

1. Validar URL administrativa e portas de QA livres. Usar localhost:4173 para
   frontend e localhost:8100 para API por padrão, independentes dos servidores
   de desenvolvimento. Porta ocupada falha sem encerrar processo existente.
2. Criar banco codetrack_test_UUID, migrar até head e gerar senha/JWT aleatórios.
   Criar fixtures mínimas: aluno, ADMIN revisor diferente, outra conta, categoria,
   skill e desafio elegível; não usar progressos fictícios para a jornada real.
3. Iniciar apenas os serviços de QA necessários, ocultos no Windows, com timeout
   de readiness. Configurar proxy de Vite para API de QA por variável local restrita
   ao harness; não mudar o proxy padrão de desenvolvimento ou produção.
4. Rodar Playwright com parâmetros de URL e credenciais em ambiente, não query/CLI
   ou arquivo versionado. Chromium desktop/mobile é obrigatório; Chrome instalado
   pode ser opção local, mas CI não depende dele.
5. Recolher exit code e sempre encerrar processos próprios, descartar conexões e
   remover somente banco gerado. Cleanup também após falha, timeout/interrupção
   tratável. Logs de falha não devem imprimir respostas autenticadas/headers.

Testes HTTP controlados podem rodar sobre frontend sem API real, utilizando o
mesmo runner; nunca afirmar integração por mocks. Fluxo real e fluxo controlado
terão projetos/comandos distinguíveis na configuração. Nada inicia revisão ou
submissão no banco local; chamadas de teste se restringem à API descartável.

## Casos mínimos versionados

Real: login/onboarding de fixture, selecionar skill, iniciar, salvar Unicode,
retomar após login, enviar, pendência, revisar como ADMIN por API, consultar feedback,
verificar progresso conhecido e isolamento de outra conta. Snapshot de catálogo
alterado/desativado deve sobreviver. Usar IDs retornados, sem assumir PK fixa.

Controlado: PATCH falha sem submit, confirmação cancelada, envio concluído com
resposta perdida, GET de reconciliação falha/retry, 409 preserva local, sessão
expirada/troca de conta, resposta atrasada ignorada, 404 avaliação versus erro,
paginação/vazio, saída dirty por link/histórico/logout e limite Unicode.
Consolidar cenários sem copiar toda a bateria histórica ou criar dezenas de
testes que repitam detalhes internos. Validar comportamento e chamadas relevantes.

Revisão manual dirigida: tabulação e foco visível, labels, mensagens de erro/status,
confirmações e mobile sem overflow. Sem promessa de auditoria WCAG completa.

## Automação e aprovação

S11-T06 define workflow que prepara Python compatível com stack, Node compatível,
PostgreSQL 17 de teste e dependências fixadas, executa backend complete, build e
projetos Playwright escolhidos. Sem deploy, secrets reais ou escrita em serviços
externos. Testes locais verificam comandos; execução remota deve ser relatada
separadamente e não pode ser inventada.

Critérios finais: nenhum failure/skip de ambiente no backend complete; build
aprovado; jornada real e casos críticos de falha aprovados; nenhum erro JS
inesperado/overlay/overflow nos viewports definidos; cleanup e isolamento
confirmados; achados com reprodução, correção ou limitação justificada registrada.
Não ampliar escopo para funcionalidades FUTURO como controle de versão entre abas.

## Evidências S11-T03

Executado em 02/10/2026 com Python do backend/.venv e warnings como erros:

```text
pytest backend/tests --quality-mode=fast -q -W error --tb=short
290 passed, 46 deselected in 14.99s

pytest backend/tests --quality-mode=complete -q -W error --tb=short
336 passed in 118.50s
```

Complete usou CODETRACK_TEST_ADMIN_URL carregada localmente sem imprimir valores;
bancos aleatórios da fixture foram criados/migrados/removidos. Nenhum skip.
Oito testes novos exercitam subprocessos pytest: seleção por fixture transitiva,
configuração ausente, URL inválida/driver incorreto/banco indisponível, ausência
de credencial/traceback na mensagem, skip em execução/coleta e compatibilidade
legada. Reexecução dirigida após tipagem: 8 passed in 10.66s.

Primeira captura falhou no Windows por encoding do stderr em subprocessos;
fixture do teste define PYTHONIOENCODING=utf-8 para saída determinística. Não houve
mudança de regra de domínio. Nenhuma dependência nova; pytester já faz parte do
pytest. Harness de navegador, CI e revisão de riscos permanecem pendentes.

## Evidências S11-T04

Harness backend/scripts/browser_qa.py e frontend/e2e versionados. Playwright
1.63.0 fixado no package/lockfile como ferramenta de desenvolvimento, conforme
justificativa do recorte; Chromium instalado pelo CLI. Uso explícito de --local-env
para ler URL local, ou CODETRACK_TEST_ADMIN_URL em ambiente. Nenhum caminho pessoal.
Proxy QA restrito a http://127.0.0.1:8100; proxy padrão de desenvolvimento mantido.
TypeScript de QA em tsconfig.e2e.json. Traces/vídeos desligados, JSON/screenshots
em frontend/test-results ignorado, sem retransmitir logs autenticados.

Em 02/10/2026, harness confirmou **9 testes aprovados, zero skips/falhas** e
cleanup de serviços próprios/banco. Casos controlados em 1440x1000 e 390x844 e
jornada real com PostgreSQL descartável, revisão por ADMIN via API e score 504.
Modo controlado independente: **8 passed (10.7s)**. Após acrescentar navegação
protegida por histórico, teste dirigido em desktop/mobile: **2 passed (4.3s)**.
Sem erros JS inesperados, overlay ou overflow nos cenários. Browser plugin ausente;
utilizado Playwright instalado no próprio projeto. Integração não é inferida de mocks.

`pytest backend/tests/test_browser_qa.py --quality-mode=complete -q -W error --tb=short`:
**4 passed in 4.46s**. Verificados porta ocupada sem início de processo, configuração
ausente sem conexão, falha de migration/readiness com remoção só do banco gerado,
preservação do banco da fixture, encerramento só de processo próprio e restauração
do ambiente. Build/TypeScript do produto e tipagem dos testes aprovados.

Portas 4173/8100 verificadas livres após execução. Testes geram artefatos ignorados
e cada execução Playwright substitui resultados anteriores; não tratá-los como
histórico persistente. Instruções reproduzíveis em frontend/e2e/README.md.
Validação realizada no Windows; execução Linux/CI permanece S11-T06. Revisão de
teclado/acessibilidade e inventário de achados continuam S11-T05.

## Evidências S11-T05

Revisão realizada em 02/10/2026. Consultados os asserts de test_identity,
test_attempt_flow, test_attempt_history e test_evaluation_http: identidade real,
JWT inválido/expirado, role obtida do banco, dono exclusivo inclusive perante
ADMIN, no-store e revisão separada do autor. Não foi encontrada lacuna nesses
cenários que justificasse duplicar testes ou alterar regras do backend.
Comando dirigido com --quality-mode=complete -q -W error --tb=short nos quatro
arquivos: **9 passed in 12.63s**, com PostgreSQL descartável, nenhum skip.

Achado reproduzido: após editar por teclado (Tab até a resposta, digitar, Tab até
Salvar rascunho, Enter), o efeito dependente do objeto completo da tentativa
movia o foco para o título. O teste novo falhou em desktop e mobile antes da
correção. AttemptsPage agora move o foco somente ao carregar/mudar o status;
AttemptAnswer devolve o foco ao editor após salvamento confirmado e término da
operação. Texto digitado depois continua na resposta; envio ainda leva ao título
da tentativa com o estado atualizado. Nenhuma política de domínio alterada.

Regressão versionada em controlled.spec.ts cobre Tab/Enter, foco inicial,
salvamento e continuação da edição. Inspeção da captura mobile confirmou contorno
visível no editor e texto preservado. Harness completo: **11 testes aprovados,
nenhum skip/falha**, Chromium em 1440x1000 e 390x844, localhost:4173/API:8100;
cleanup confirmado. Browser plugin ausente; usado Playwright do projeto.
Jornada real e cenários controlados existentes reexecutados: expiração 401,
troca de conta, resposta tardia, falha de PATCH sem POST, reconciliação de envio,
conflito com cópia local, erro distinto de pendência e guardas de saída/histórico.
Página identificada, conteúdo presente, sem overlay, erro JS inesperado ou
overflow nos testes. Build e tipos do produto/QA passaram; git diff --check passou.

Limites: revisão dirigida do fluxo de tentativas, não auditoria WCAG completa.
Não houve teste com leitor de tela, outros motores de navegador ou teclado
virtual de dispositivo físico; mobile usa viewport em Chromium no Windows.
Diálogos nativos foram aceitos/cancelados pelo runner; antes de fechar a aba,
o aviso beforeunload depende das políticas do navegador. Regressão backend
completa será reexecutada no fechamento; Linux/CI e automação seguem S11-T06.

## Evidências S11-T06

Em 02/10/2026, criado .github/workflows/quality.yml: push, pull_request e
workflow_dispatch, único job Ubuntu 24.04 com timeout de 20 minutos e concorrência
por referência. PostgreSQL 17 em serviço com healthcheck; credencial explicitamente
descartável e exclusiva do job. Nenhum secret pessoal ou .env de desenvolvimento.
Python usa backend/.python-version (3.12), Node 24.14.1; requirements fixados e
npm ci pelo lockfile. Actions oficiais checkout/setup-python/setup-node v6
resolvidas por git ls-remote e fixadas por SHA; contents: read e checkout sem
persistir credenciais. Não há deploy, upload de relatórios autenticados ou escrita
em serviço externo. Cancelamento do job destrói o runner/serviço efêmeros;
execução normal do harness também confirma seu próprio cleanup.

Etapas: instalação, pip check, pytest completo com warnings como erros, npm ci,
build/tipos do produto, Chromium com dependências Linux, harness (tipos de QA,
todos os projetos, banco e serviços próprios). Não repetir projeto controlado:
ele já participa do harness. Configuração segue a documentação oficial de
[serviços PostgreSQL](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers)
e [instalação Chromium](https://playwright.dev/docs/browsers).

Workflow validado estaticamente por actionlint oficial, baixado em TEMP, sem
dependência adicionada ao projeto. Nenhum diagnóstico. Comandos de execução
validados localmente no Windows com ambiente já instalado:
**340 passed in 121.24s**, backend complete, nenhum skip; **11 testes de navegador
aprovados**, nenhum skip/falha, cleanup confirmado; build/tipos e pip check
aprovados; git diff --check aprovado. A URL local foi obtida sem imprimir valores.

README raiz corrigido quanto às telas disponíveis e evidências históricas;
frontend/README atualizado do estado da fundação para os fluxos atuais;
e2e/README inclui comandos CI/Linux e cinco cenários controlados por viewport.
Backend/README mantém instruções dos modos de testes já implementadas.

Limites: esta etapa não fez commit/push nem executou GitHub Actions, e não
reproduziu Ubuntu no computador. Sintaxe estática e resultados Windows não
comprovam instalação de dependências nativas ou execução do job remoto. Conferir
Actions após publicação e registrar falhas reais se ocorrerem. Nenhum resultado
remoto é declarado aprovado; fechamento segue S11-T07.
