# CodeTrack

## Estado de implementação

Sprint 1 concluída: cadastro, login JWT, identidade autenticada e verificação
de permissões no backend. Evidências no [fechamento da Sprint 1](docs/SPRINT_1.md).
Sprint 2 — Categories + Skills com contratos definidos (S2-T01); models e API
do catálogo ainda não implementados, conforme o
[planejamento atual](docs/CURRENT_SPRINT.md).

Sprint 0 concluída: backend FastAPI, frontend React + TypeScript + Vite,
PostgreSQL com Docker, SQLAlchemy, Alembic e comunicação via `/health`.
A migration inicial cria a tabela users. A interface continua como verificação
de conectividade; telas de autenticação e funcionalidades de aprendizagem são FUTURO.

## Executar localmente

Requisitos: Python 3.12+, Node.js 22.12+ e Docker Desktop com engine Linux
e Docker Compose. Validado no Windows com Python 3.12.10 e Node 24.14.1.
Os comandos PowerShell abaixo partem da raiz do repositório.

### Preparação inicial

```powershell
py -3.12 -m venv backend/.venv
& backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
npm --prefix frontend ci
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
```

Antes de iniciar, preencha `POSTGRES_PASSWORD` no `.env` da raiz e
`DATABASE_URL` em `backend/.env` com as mesmas credenciais, banco e porta.
Consulte a [configuração do backend](backend/README.md#configurar-sqlalchemy)
para formato e codificação da URL. Use `CODETRACK_DEBUG=false`.
Configure também `JWT_SECRET_KEY` com um segredo aleatório no ambiente ou
`backend/.env`, conforme [utilitários JWT](backend/README.md#utilitários-jwt-s1-t05).
Os exemplos não contêm credenciais reais; os arquivos `.env` não são versionados.

### Iniciar os serviços

Primeiro, inicie o banco:

```powershell
docker compose up -d --wait --wait-timeout 60
& backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini upgrade head
```

Em um terminal, inicie a API:

```powershell
& backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Em outro terminal, inicie o frontend:

```powershell
npm --prefix frontend run dev
```

Abra <http://127.0.0.1:5173> (ou a porta informada pelo Vite).
A página deve mostrar “Servidor disponível”. O proxy local encaminha `/health`
à API na porta 8000. A documentação da API fica em <http://127.0.0.1:8000/docs>.
O proxy de desenvolvimento não acompanha os arquivos estáticos de produção.

### Conferir o ambiente

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests -q
& backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini check
npm --prefix frontend run build
Push-Location backend
& .venv/Scripts/python.exe -m app.database.check
Pop-Location
```

Com CODETRACK_TEST_ADMIN_URL configurada, 73 testes passam, incluindo cinco
testes PostgreSQL que criam e removem bancos descartáveis. Sem essa variável,
esses cinco são pulados. Consulte [testes do backend](backend/README.md).
Alembic deve indicar ausência de novas operações e o build deve concluir.
`/health` não consulta o banco. Na conclusão da Sprint 1, os 73 testes passaram
com `-W error`; Alembic, dependências e build também foram validados.

Para encerrar API e frontend, use Ctrl+C nos respectivos terminais.
Para parar o banco mantendo os dados, use `docker compose stop`.
Instruções adicionais: [backend](backend/README.md) e [frontend](frontend/README.md),
incluindo variantes Linux/macOS, ainda não executadas neste projeto.

## PostgreSQL local com Docker

Requisito: Docker Desktop em execução com engine Linux e Docker Compose.
Os comandos abaixo partem da raiz do repositório.

O Compose usa a imagem oficial `postgres:17-alpine`, mantendo a versão principal
17, um volume nomeado para persistência e publicação somente em `127.0.0.1`.

Na primeira configuração, copie `.env.example` para `.env` somente se ainda
não existir. No PowerShell:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Preencha `POSTGRES_PASSWORD` no `.env` local com uma senha própria. O exemplo
deixa a senha vazia propositalmente: Compose recusa iniciar sem esse valor.
O `.env` da raiz configura Docker; `backend/.env` configura FastAPI.
Ambos estão ignorados pelo Git. Não exiba a configuração resolvida com segredos.

```powershell
docker compose config --quiet
docker compose up -d --wait --wait-timeout 60
docker compose ps
docker compose exec db sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Os mesmos comandos Docker funcionam no Linux/macOS. Caso a porta 5432 esteja
ocupada, ajuste `POSTGRES_PORT` no `.env` antes de iniciar.
Use `docker compose stop` para parar e `docker compose up -d --wait` para retomar.
`docker compose down` remove containers e rede, preservando o volume.
Não use `down -v` para parar: isso apaga os dados persistidos.

As variáveis POSTGRES_DB, POSTGRES_USER e POSTGRES_PASSWORD inicializam somente
um volume vazio. Alterar o `.env` depois não modifica credenciais já criadas.
O usuário configurado é o administrador do banco de desenvolvimento local.
A conexão SQLAlchemy do backend está configurada e foi validada na S0-T08.

Plataforma adaptativa para aprendizagem e prática de programação.

O CodeTrack analisa habilidades, objetivos, interesses e desempenho para recomendar conteúdos e desafios compatíveis com o nível atual de cada usuário.

---

## Objetivo

O sistema busca responder:

> Qual é a melhor atividade para este usuário realizar agora?

Em vez de obrigar todos os usuários a seguirem exatamente a mesma trilha.

---

## Principais conceitos

```text
User
Skills
Learning Profile
Assessment
Track
Challenge
Attempt
Evaluation
Recommendation
Progress
```

---

## Diferencial

Um usuário não possui apenas:

```text
nível = intermediário
```

Ele possui níveis separados por competência:

```text
Python: 650
Logic: 580
SQL: 320
HTTP: 210
Git: 590
```

O sistema utiliza essas informações para identificar lacunas e escolher atividades adequadas.

---

## Modos da plataforma

### Aprender

Conteúdos guiados.

### Praticar

Desafios adaptativos.

### Construir

Mini-projetos e atividades maiores.

---

## Stack

### Backend

```text
Python
FastAPI
SQLAlchemy
Alembic
PostgreSQL
Pydantic
pytest
```

### Frontend

```text
React
TypeScript
Vite
Tailwind CSS
React Router
Axios
```

### Infraestrutura

```text
Docker
GitHub
Vercel
Render
```

---

## Arquitetura

```text
React
  ↓
HTTP / JSON
  ↓
FastAPI
  ↓
Services
  ↓
Repositories
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

Padrão:

```text
Monólito modular
```

---

## Estrutura

```text
codetrack/

├── AGENTS.md
├── README.md
│
├── docs/
│   ├── PROJECT_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── BUSINESS_RULES.md
│   └── CURRENT_SPRINT.md
│
├── backend/
│
└── frontend/
```

---

## Documentação

Leia:

```text
docs/PROJECT_SPEC.md
```

para compreender o produto.

Leia:

```text
docs/ARCHITECTURE.md
```

para compreender a arquitetura.

Leia:

```text
docs/BUSINESS_RULES.md
```

para compreender regras de negócio.

Leia:

```text
docs/CURRENT_SPRINT.md
```

antes de implementar qualquer tarefa.
