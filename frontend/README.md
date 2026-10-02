# CodeTrack — Frontend

React, TypeScript, Vite, Tailwind CSS, React Router e Axios. A interface permite
cadastro/login, onboarding, diagnóstico, painel por habilidade, recomendação,
início/retomada de tentativas, salvamento, envio e consulta de revisão manual.
Conteúdo precisa estar cadastrado; não há seed automático nem painel ADMIN.

## Execução local

Node.js 22.12+; ambiente validado com Node 24.14.1. Na raiz do repositório:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

Abra o endereço mostrado pelo Vite, normalmente <http://127.0.0.1:5173>.
Use Ctrl+C para encerrar. API na porta 8000 e PostgreSQL precisam estar
preparados conforme [iniciar os serviços](../README.md#iniciar-os-serviços).
O proxy local encaminha `/health` e `/api/v1` à API; não acompanha `dist/`.
Produção será definida na Sprint de deploy.

O token Bearer fica em memória; recarregar exige novo login. Logout ou sessão
expirada limpa os dados da conta. Salve respostas antes de sair; rascunhos
não salvos podem ser perdidos. Envio exige confirmação e torna a resposta
somente leitura, aguardando revisão manual por ADMIN.

## Validação e build

```powershell
npm --prefix frontend run build
npm --prefix frontend run typecheck:e2e
npm --prefix frontend run preview
```

O build verifica os tipos do produto e gera `dist/`. `preview` serve o build
localmente, sem o proxy da API; não é servidor de produção. Instale dependências
com `npm ci` usando package-lock.json. `node_modules/` e `dist/` são ignorados.

## QA de navegador e CI

Instalação de Chromium, testes controlados e jornada real descartável estão em
[e2e/README.md](e2e/README.md). QA usa portas 4173/8100 próprias. Casos controlados
usam HTTP simulado; jornada real usa PostgreSQL e API preparados pelo harness.

O [workflow Quality](../.github/workflows/quality.yml) instala as dependências,
executa backend completo, build, tipos de QA e todos os projetos de navegador
com PostgreSQL 17 descartável. Instruções e limites em
[qualidade](../docs/QUALITY_CONTRACT.md). Consulte a
[Sprint atual](../docs/CURRENT_SPRINT.md) antes de implementar.
