# CodeTrack — Frontend

Diretório do frontend React com TypeScript, Vite, Tailwind CSS,
React Router e Axios.

Estado atual: React + TypeScript + Vite com comunicação básica via Axios
ao endpoint `/health`, implementada na S0-T12.

## Execução local

Requisito: Node.js 22.12+; ambiente validado com Node 24.14.1 e npm 11.11.0.
Na raiz do repositório:

```powershell
cd frontend
npm ci
npm run dev
```

Abra o endereço mostrado pelo Vite, normalmente <http://127.0.0.1:5173>.
Use Ctrl+C para encerrar. Os comandos npm também funcionam no Linux/macOS.

## Validação e build

```powershell
npm run typecheck
npm run build
npm run preview
```

O build executa a checagem TypeScript estrita e gera `dist/`.
`preview` serve esse build localmente; não é um servidor de produção.
As versões diretas estão fixadas no package.json e as transitivas no package-lock.json.
`node_modules/` e `dist/` são ignorados pelo Git.

Validação S0-T11: build e TypeScript passaram; página inspecionada no Chrome
em viewport desktop, com título e textos renderizados. Mobile não foi validado.
Tailwind CSS e React Router fazem parte da stack planejada e serão adicionados
conforme seu uso nas próximas tarefas; ainda não há telas de negócio.

## Comunicação com o backend

Inicie o backend em um terminal separado, a partir da raiz do repositório:

```powershell
& backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Depois execute o frontend com `npm run dev` em `frontend/`.
O Vite encaminha `/health` para `http://127.0.0.1:8000/health` via proxy local.
O navegador usa a mesma origem do frontend, sem necessidade de liberar CORS
no backend nesta etapa. O proxy não faz parte dos arquivos estáticos de `dist/`;
o roteamento de produção será definido na Sprint de deploy.

`src/services/health.ts` usa Axios com timeout de cinco segundos e valida
que a resposta contém `status: "ok"`. A página mostra carregamento, sucesso
ou erro e permite verificar novamente; requisições são canceladas ao desmontar.
O estado confirma a resposta da API, não a disponibilidade do banco.

Validação S0-T12: build e TypeScript passaram; no Chrome, sucesso com backend
ativo, erro após desligá-lo e recuperação pelo botão após reiniciá-lo.

Consulte [a Sprint atual](../docs/CURRENT_SPRINT.md) antes de implementar.
