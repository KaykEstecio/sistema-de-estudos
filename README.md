# CodeTrack

Para abrir o projeto no computador, siga [Iniciar os serviços](#iniciar-os-serviços).
Na primeira execução, faça antes a [Preparação inicial](#preparação-inicial).

## Estado de implementação

Sprint 12B entregue localmente: área de estudo por habilidade, publicação manual
ADMIN, explicação/exemplo/erros comuns e conclusão individual sem alterar score.
Links em desafios e feedback conectam estudo e prática. Aplicar migration 0009.
Uso em [STUDY_AREA.md](docs/STUDY_AREA.md). Última validação: 341 testes backend
completos e 16 de navegador aprovados, além de build e Alembic check.

Painel ADMIN de revisão implementado localmente (Sprint 12A): fila paginada,
contexto histórico, resposta do aluno e avaliação manual por habilidade em
`/admin/revisoes`. Login ADMIN abre a fila; cadastro público permanece STUDENT.
Detalhes em [painel de revisão](docs/ADMIN_REVIEW_PANEL.md).
Deploy adiado pelo usuário; o planejamento da Sprint 12 fica preservado.

Sprint 11 — testes e qualidade concluída: modos backend fast/complete, harness
reproduzível de navegador, revisão de sessão/acesso/teclado e workflow Quality.
Validação local: 340 testes backend e 11 navegador aprovados; CI remota ainda
não executada. Evidências e limites no [fechamento](docs/SPRINT_11.md).

Sprint 1 concluída: cadastro, login JWT, identidade autenticada e verificação
de permissões no backend. Evidências no [fechamento da Sprint 1](docs/SPRINT_1.md).
Sprint 2 — Categories + Skills concluída: persistência, consulta autenticada,
manutenção administrativa e validação integrada ([histórico](docs/SPRINT_2.md)).
Sprint 3 — Onboarding concluída: persistência, fluxo HTTP e integração entre
contas validados ([histórico](docs/SPRINT_3.md)).
Sprint 4 — Assessment concluída: início, respostas, resultados por skill e
importação local de questões revisadas ([fechamento](docs/SPRINT_4.md)).
Sprint 5 — Challenges concluída: catálogo autenticado, API administrativa,
publicação e integração validados ([fechamento](docs/SPRINT_5.md)).
Sprint 6 — Attempts concluída: início, retomada, rascunho, submissão e histórico
validados ([fechamento](docs/SPRINT_6.md)).
Sprint 6A — Frontend dos fluxos iniciais: jornada e integração definidas para
cadastro/login, onboarding e diagnóstico implementados e validados
([plano atual](docs/CURRENT_SPRINT.md), [jornada](docs/FRONTEND_JOURNEY.md)).
Sprint 6A concluída; evidências e limites no [fechamento](docs/SPRINT_6A.md).

Sprint 0 concluída: backend FastAPI, frontend React + TypeScript + Vite,
PostgreSQL com Docker, SQLAlchemy, Alembic e comunicação via `/health`.
A migration inicial cria a tabela users. A interface oferece cadastro e login;
o onboarding está disponível em `/onboarding` após entrar. Sem categorias no
banco, a tela explica a ausência e bloqueia o envio. Em `/diagnostico`, escolha
de 1 a 3 habilidades, salve cada resposta e conclua para ver o resultado.
Guarde o link ou o número para retomar; o navegador também oferece o último
diagnóstico acessado pela conta. Apenas respostas salvas são persistidas.
É necessário ter skills e questões revisadas cadastradas para iniciar.

Sprint 7 — Avaliação manual concluída no recorte qualitativo
([fechamento e limites](docs/SPRINT_7.md)). O ADMIN consulta uma tentativa submetida em
`GET /api/v1/reviews/attempts/{id}` e registra feedback em
`POST /api/v1/reviews/attempts/{id}/evaluation`. O dono consulta em
`GET /api/v1/attempts/{id}/evaluation`. Uso pelo Swagger nesta etapa, sem painel
administrativo. Entrada e permissões no [contrato](docs/EVALUATION_CONTRACT.md).
É necessário aplicar a migration 0007 usando as instruções de Alembic abaixo.
O recorte qualitativo original não atualizava score/UserSkill; a Sprint 7A
acrescenta esse comportamento para avaliações novas, conforme descrito abaixo.

Sprint 7A — UserSkill concluída ([validação e limites](docs/SPRINT_7A.md)):
política determinística experimental, persistência de
progresso, histórico de evidências e integração atômica com avaliações novas.
Consulta exclusiva do próprio usuário em `GET /api/v1/users/me/skills`, disponível
pelo Swagger e agora no painel da Sprint 9. Contratos de [política](docs/USER_SKILL_POLICY_DRAFT.md),
[persistência](docs/USER_SKILL_STORAGE.md) e [API](docs/USER_SKILL_API.md).
Antes de iniciar esta versão, execute `alembic upgrade head` conforme as instruções
abaixo, incluindo a migration 0008. Avaliações antigas não são convertidas.
Score e confiança não representam domínio comprovado; a política não foi calibrada.

Sprint 8 — Recomendação concluída no backend ([validação e limites](docs/SPRINT_8.md)):
`GET /api/v1/recommendations?skill_id=1&limit=5`, com Bearer autenticado.
Informe o ID de uma skill ativa pertencente aos seus interesses. O resultado
considera evidências por habilidade, dificuldade e histórico; cada sugestão
explica sua seleção. Sem progresso, usa diagnóstico disponível ou exploração
introdutória. Uma lista vazia indica ausência de candidatos elegíveis.
Uso pelo Swagger; nenhuma nova tela ou migration nesta Sprint. A consulta não
inicia tentativa nem altera progresso. [Contrato](docs/RECOMMENDATION_API.md) e
[política experimental](docs/RECOMMENDATION_POLICY.md).

## Executar localmente

Sprint 9 concluída: após login e onboarding, `/dashboard` mostra resumo,
progresso paginado e recomendações por skill selecionada. “Ver desafio” abre o
enunciado. A Sprint 10 adiciona iniciar/retomar tentativa, `/tentativas` para
recuperar rascunhos/envios, salvar resposta textual, enviar para revisão manual
e consultar feedback por habilidade. Respostas enviadas ficam somente leitura.
Use um desafio publicado por ADMIN; a aplicação não cria conteúdo automaticamente.
Contrato em [ATTEMPT_EXPERIENCE_CONTRACT.md](docs/ATTEMPT_EXPERIENCE_CONTRACT.md).
Contas sem onboarding chegam ao perfil. Validação e limites:
[Sprint 9](docs/SPRINT_9.md) e [Sprint 10](docs/SPRINT_10.md).

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

Use este procedimento sempre que quiser ver o projeto. Abra o Docker Desktop
e aguarde o engine iniciar. Abra dois terminais PowerShell na pasta raiz do
projeto (a pasta que contém este README, backend e frontend).

**Terminal 1 — banco e API:** inicie o banco e aplique as migrations:

```powershell
docker compose up -d --wait --wait-timeout 60
& backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini upgrade head
```

Se os comandos acima terminarem sem erro, inicie a API no mesmo terminal:

```powershell
& backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Deixe esse terminal aberto. **Terminal 2 — frontend:**

```powershell
npm --prefix frontend run dev
```

Deixe o segundo terminal aberto e acesse:

| Endereço | O que visualizar |
| --- | --- |
| <http://127.0.0.1:5173> | Frontend; use a porta indicada pelo Vite se for diferente |
| <http://127.0.0.1:8000/docs> | Swagger para testar cadastro, login, catálogo, diagnóstico e tentativas |
| <http://127.0.0.1:8000/health> | Verificação da API: resposta `{"status":"ok"}` |

A interface permite cadastro, login, perfil, diagnóstico, painel e tentativas,
incluindo consulta de feedback por habilidade. Recarregar a página exige novo
login porque o token fica somente em memória. Administração de conteúdo e
revisão manual são realizadas pelo Swagger nesta etapa.
Para endpoints protegidos, faça login em `/api/v1/auth/login`
e use o access_token no botão **Authorize**. Operações administrativas exigem ADMIN.
Os fluxos estão descritos no [README do backend](backend/README.md).

O proxy local encaminha `/health` e `/api/v1` à API na porta 8000.
O proxy de desenvolvimento não acompanha os arquivos estáticos de produção.

Se não abrir: confirme que os dois terminais continuam rodando. Se o frontend
mostrar servidor indisponível, confira a API em `/health`. Se login ou operações
com dados falharem, confira `docker compose ps` e as migrations; `/health` não
testa a conexão com o PostgreSQL. Erro de conexão com Docker exige iniciar o
Docker Desktop. Porta 8000 ocupada exige encerrar a outra instância da API antes
de repetir o comando; o proxy do frontend espera essa porta.

Para encerrar, pressione **Ctrl+C** nos dois terminais e execute
`docker compose stop` na raiz para parar o banco preservando os dados.

### Conferir o ambiente

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests --quality-mode=complete -q -W error
& backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini check
npm --prefix frontend run build
Push-Location backend
& .venv/Scripts/python.exe -m app.database.check
Pop-Location
```

O modo `complete` exige CODETRACK_TEST_ADMIN_URL e PostgreSQL disponível; falha
antes dos testes se faltar configuração e reprova qualquer skip. Para checagem
sem banco, use `--quality-mode=fast`, que deseleciona integrações explicitamente.
Configuração e comandos seguros em [testes do backend](backend/README.md).
Alembic deve indicar ausência de novas operações e o build deve concluir.
`/health` não consulta o banco. Evidências atuais e limites ficam no
[contrato de qualidade](docs/QUALITY_CONTRACT.md); números históricos de outras
Sprints não substituem a validação atual.

Para testes de navegador, instale Chromium e execute a jornada descartável
conforme [QA do frontend](frontend/e2e/README.md). O
[workflow Quality](.github/workflows/quality.yml) verifica backend completo,
dependências, build e navegador em pushes, pull requests e execução manual.
Usa PostgreSQL 17 de teste e não depende de secrets ou `.env` pessoais.
Configuração versionada não significa execução remota aprovada; consulte
o resultado na aba Actions do GitHub após publicar as mudanças.

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
