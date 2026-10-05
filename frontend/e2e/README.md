# Testes de navegador

Playwright 1.63.0 é dependência de desenvolvimento fixada no lockfile.
Instruções partem da raiz do repositório, com Node 22.12+ e Python do backend:

```powershell
npm --prefix frontend ci
Push-Location frontend
npx playwright install chromium
Pop-Location
npm --prefix frontend run test:e2e:controlled
```

O projeto controlado inicia Vite em 127.0.0.1:4173 e usa HTTP simulado, sem exigir
PostgreSQL/API. Porta ocupada não é reutilizada. Executa cinco cenários em
desktop 1440x1000 e mobile 390x844, mais dois cenários de tema por viewport.
Inclui typecheck específico de QA. Casos controlados de tentativas usam tema claro;
a jornada real usa tema escuro. Os testes de tema verificam alternância pelo
sistema/teclado, persistência após reload, sincronização entre abas e storage
bloqueado. Total atual do harness: 15 testes, sem usar contagem como critério fixo.
No Linux/CI, dependências nativas do browser podem exigir
`npx playwright install --with-deps chromium`, conforme a documentação oficial.

Jornada real e projetos controlados juntos:

```powershell
docker compose up -d db --wait
& backend/.venv/Scripts/python.exe backend/scripts/browser_qa.py --local-env
```

`--local-env` autoriza explicitamente ler a URL administrativa de backend/.env.
Sem essa opção, fornecer CODETRACK_TEST_ADMIN_URL pelo ambiente. Não usar servidor
de produção; a conta deve poder criar/remover bancos descartáveis.
O harness usa 4173/8100, recusa portas ocupadas, prepara banco codetrack_test_UUID,
fixtures e migrations, gera credenciais por execução e inicia serviços próprios.
Ao finalizar/falhar, encerra somente seus processos e remove o banco gerado.
Não migra/popula banco local. Mensagens de configuração/cleanup não expõem URL.

`test:e2e:real` exige o ambiente preparado pelo harness e reprova se não houver
essa configuração; não contém skip silencioso. Não execute diretamente sobre
serviços de desenvolvimento. Default `test:e2e` seleciona todos os projetos,
portanto deve ser usado pelo harness para a jornada real.

Artefatos ignorados: frontend/test-results (JSON e screenshots). Traces e vídeos
desativados para evitar gravação de credenciais/headers; não commitar relatórios.
O harness resume resultado sem retransmitir logs HTTP autenticados. Não há retry
automático de testes; falhas precisam ser analisadas.

`real.spec.ts` verifica início/salvamento, retomada após login, snapshot após
alteração/desativação, envio, espera, revisão por ADMIN via API, progresso 504 e
isolamento. IDs vêm da preparação/API, sem assumir PK fixa. O mesmo ciclo inclui
desktop/mobile. Mocks verificam cenários de falha, não provam integração real.

Referências: [projetos](https://playwright.dev/docs/test-projects),
[servidor de testes](https://playwright.dev/docs/test-webserver) e
[instalação de browsers](https://playwright.dev/docs/browsers).

## CI em Linux

O workflow Quality prepara Python 3.12, Node 24.14.1 e PostgreSQL 17 no runner
Ubuntu 24.04, instala Chromium com --with-deps e executa este harness sem
--local-env. A URL administrativa vem do serviço descartável do job.
Com dependências instaladas e CODETRACK_TEST_ADMIN_URL configurada no ambiente:

```bash
python -m pytest backend/tests --quality-mode=complete -q -W error --tb=short
npm --prefix frontend run build
(cd frontend && npx --no-install playwright install --with-deps chromium)
python backend/scripts/browser_qa.py
```

O harness verifica tipos de QA e executa todos os projetos; não é necessário
repetir o modo controlado no workflow. Sem upload automático de screenshots,
traces ou respostas autenticadas. A validação local no Windows não comprova
execução Linux: conferir o resultado remoto na aba Actions após commit/push.
