# CodeTrack — Sprint 0 (histórico)

Registro arquivado da fundação. Para escopo e skills ativos, consulte
[CURRENT_SPRINT.md](CURRENT_SPRINT.md); as restrições abaixo são históricas.

## Sprint atual

```text
SPRINT 0 — FOUNDATION
```

Status: concluída. S0-T01 a S0-T14 finalizadas; S0-T10 avaliada sem necessidade
de migration técnica. Sprint 1 permanece FUTURO até sua abertura e detalhamento.

---

# Objetivo

Criar uma fundação técnica limpa para o CodeTrack.

Ao final da Sprint 0 deverá ser possível executar:

```text
Frontend
Backend
Database
```

de forma previsível.

---

# Escopo permitido

Implementar:

* estrutura inicial do monorepo;
* backend FastAPI;
* frontend React + TypeScript;
* Vite;
* PostgreSQL;
* Docker;
* SQLAlchemy;
* Alembic;
* configuração de ambiente;
* `.env`;
* `.env.example`;
* `.gitignore`;
* endpoint `/health`;
* documentação inicial.

---

# Fora do escopo

Não implementar durante esta Sprint:

```text
User
Auth
JWT

Category
Skill
UserSkill

Onboarding
Assessment

Track
Challenge
Attempt

Evaluation
Progress
Recommendation

Dashboard funcional
```

---

# Estrutura alvo

```text
codetrack/

├── AGENTS.md
├── README.md

├── docs/
│   ├── PROJECT_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── BUSINESS_RULES.md
│   └── CURRENT_SPRINT.md

├── backend/

└── frontend/
```

---

# Backend mínimo esperado

```text
backend/

app/
├── main.py
├── core/
└── database/

tests/

alembic/

.env.example
```

Não é obrigatório criar módulos futuros agora.

---

# Primeiras tarefas

## S0-T01

Criar estrutura inicial do repositório.

Status: concluída. Documentação organizada, Git inicializado e diretórios
`backend/` e `frontend/` criados com documentação de seu estado inicial.

---

## S0-T02

Inicializar backend Python.

Status: concluída. Ambiente local isolado com Python 3.12.10, pacote `app`
e dependências FastAPI/Uvicorn registradas em `backend/requirements.txt`.
Validação no Windows: instalação pelo arquivo de dependências, `pip check`,
importação de `app`, FastAPI, Pydantic e Uvicorn e isolamento do ambiente.

---

## S0-T03

Criar aplicação FastAPI mínima.

Status: concluída. Ponto de entrada `backend/app/main.py` com aplicação FastAPI
e título CodeTrack; comandos de execução documentados no README do backend.
Validação no Windows: Uvicorn iniciado em porta local 8765, `/docs` e
`/openapi.json` com HTTP 200, título correto e contrato sem rotas próprias.
`/` e `/health` retornaram 404, conforme esta etapa. Servidor de validação encerrado.

---

## S0-T04

Status: concluída. `GET /health` implementado em `backend/app/main.py`, sem
dependências externas. Validação HTTP local: 200, conteúdo `application/json`,
JSON exato `{"status":"ok"}`, presença no OpenAPI e POST rejeitado com 405.
Servidor de validação encerrado. Teste persistente com pytest permanece na S0-T13.

Criar endpoint:

```text
GET /health
```

Resposta esperada:

```json
{
  "status": "ok"
}
```

---

## S0-T05

Configurar variáveis de ambiente.

Status: concluída. `app/core/config.py` carrega e valida APP_NAME, ENVIRONMENT
e DEBUG com Pydantic Settings. Criados `backend/.env.example` e `.env` local
ignorado pelo Git; FastAPI utiliza o título e a depuração configurados.
Validados padrões, leitura de arquivo, precedência do processo, entradas inválidas,
bloqueio de DEBUG em production, integração com a aplicação e `pip check`.
Próxima tarefa: S0-T06 — configurar PostgreSQL com Docker.

---

## S0-T06

Configurar PostgreSQL com Docker.

Status: concluída; PostgreSQL iniciado e validado no Docker.
`compose.yaml` define PostgreSQL 17, volume persistente, healthcheck e porta
publicada somente em 127.0.0.1. `.env.example` da raiz documenta as variáveis;
o `.env` local contém senha gerada e permanece ignorado pelo Git.
`docker compose config --quiet` passou. Após o Docker Desktop iniciar,
`docker compose up -d --wait --wait-timeout 60` concluiu com container saudável.
`pg_isready` confirmou conexões disponíveis e `SELECT 1` executou com sucesso
dentro do container. Porta publicada: 127.0.0.1:5432.
A conexão do backend ainda será configurada e testada nas tarefas S0-T07/S0-T08.

---

## S0-T07

Configurar SQLAlchemy.

Status: concluída. SQLAlchemy 2 e Psycopg 3 instalados; base declarativa,
engine síncrono, SessionLocal e dependência get_session configurados.
DATABASE_URL obrigatória e mascarada nas configurações, com valor somente no ambiente.
Validados driver, URL, metadados vazios, sessões independentes, fechamento em
sucesso/erro e ausência de conexão antecipada. `pip check` passou.
Correção de configuração: depuração usa CODETRACK_DEBUG para evitar conflito
com DEBUG herdado de outras ferramentas; .env local e exemplo migrados.
Testes de regressão cobrem isolamento, precedência, valores inválidos e produção.
Não foram criadas tabelas ou migrations; acesso real será validado na S0-T08.

---

## S0-T08

Testar conexão com banco.

Status: concluída. `python -m app.database.check` executa SELECT 1 usando
SessionLocal e a configuração real do backend, sem alterar dados ou schema.
Consulta PostgreSQL validada com retorno 1; sessão fechada e pool liberado.
Cenário de porta indisponível retornou código 1 sem credenciais ou traceback.
Os seis testes de configuração passaram. Comando documentado no README do backend.

---

## S0-T09

Configurar Alembic.

Status: concluída. Alembic instalado com INI sem credenciais, env.py integrado
ao engine e a Base.metadata, template de revisões e diretório versions documentado.
Validados `current` contra PostgreSQL, `check` sem diferenças de schema,
`upgrade head --sql` em modo offline e `pip check` sem conflitos.
Nenhuma revisão foi criada; não há models de domínio nesta Sprint.

---

## S0-T10

Criar primeira migration técnica se necessário.

Status: concluída por avaliação; migration técnica desnecessária nesta etapa.
Base.metadata não contém tabelas de domínio, a inspeção do PostgreSQL não
encontrou tabelas fora do controle Alembic e `alembic check` não detectou
operações novas. Nenhum arquivo de revisão vazio foi criado.
A primeira migration será criada quando houver alteração estrutural autorizada.

---

## S0-T11

Inicializar frontend React + TypeScript + Vite.

Status: concluída. Frontend mínimo criado com React, TypeScript estrito e Vite,
scripts de desenvolvimento/build/preview e dependências registradas no lockfile.
Validação: `npm run build` passou incluindo typecheck; servidor Vite iniciou
e a página foi inspecionada no Chrome em desktop. Servidor de validação encerrado.
Não há telas de negócio ou comunicação com API nesta etapa.

---

## S0-T12

Configurar comunicação básica do frontend com backend.

Status: concluída. Axios consulta `/health` através do proxy local do Vite,
com timeout, validação de resposta, cancelamento e estados de carregamento,
sucesso e falha. Botão permite repetir a verificação.
Build e TypeScript passaram. Chrome confirmou sucesso, falha com API parada
e recuperação após reiniciar o backend. Servidores de validação encerrados.

Não implementar telas de negócio.

---

## S0-T13

Adicionar teste do `/health`.

Status: concluída. pytest e HTTPX instalados; pytest.ini e testes HTTP criados.
GET /health verificado com status 200, application/json e corpo exato;
POST rejeitado com 405. Testes isolados do .env local e do PostgreSQL.
Resultado: 8 testes passaram; pip check sem conflitos. Os avisos de depreciação
foram corrigidos usando HTTPX AsyncClient/ASGITransport com lifespan explícito
no lugar do TestClient. Nova execução com `-W error`: 8 testes passaram sem avisos.

---

## S0-T14

Atualizar README com execução local.

Status: concluída. README consolidado com requisitos, instalação, configuração
dos dois arquivos de ambiente, ordem de inicialização, validação e encerramento.
Links locais e exclusão de arquivos sensíveis/artefatos pelo Git conferidos.
Critérios abaixo revisados com as evidências das tarefas da Sprint.

---

# Definition of Done

Sprint 0 concluída com as seguintes evidências:

- [x] Backend inicia sem erro — Uvicorn validado na S0-T12.
- [x] Frontend inicia sem erro — Vite e renderização no Chrome validados na S0-T12.
- [x] PostgreSQL disponível — container saudável, confirmado na revisão S0-T14.
- [x] Backend conecta ao PostgreSQL — SELECT 1 via SQLAlchemy na S0-T08.
- [x] Alembic configurado — current, check e geração offline validados na S0-T09.
- [x] `/health` responde corretamente — contrato HTTP validado na S0-T13.
- [x] Variáveis sensíveis não versionadas — .env da raiz e backend ignorados e fora do índice.
- [x] Exemplos de ambiente existem — .env.example da raiz e do backend conferidos.
- [x] Teste básico funciona — 8 testes passaram na S0-T13.
- [x] Documentação atualizada — instalação, execução e validação consolidadas na S0-T14.

Limitações registradas: comandos Linux/macOS e viewport mobile não foram
validados. Os avisos de depreciação dos testes foram corrigidos e revalidados.
As verificações visuais e de integração foram feitas no ambiente Windows local.

---

# Critério de saída

Somente após cumprir o Definition of Done avançar para:

```text
SPRINT 1 — USER + AUTH
```

---

# Próxima Sprint

Sprint 1 deverá implementar:

```text
User
Register
Password Hash
Login
JWT
GET /me
```

Não implementar Sprint 1 antecipadamente.

## Active AI Skills

Carregar somente as skills ativas pertinentes à tarefa, a partir de `.ai/skills/`.
Estes arquivos são guias locais do projeto; esta lista define sua ativação por Sprint.
A ativação não autoriza funcionalidades fora do escopo atual.

- [backend-architecture](../.ai/skills/backend-architecture.md)
- [database-modeling](../.ai/skills/database-modeling.md)
- [testing](../.ai/skills/testing.md)
- [debugging](../.ai/skills/debugging.md)
- [documentation](../.ai/skills/documentation.md)

FUTURO — inativas na Sprint 0: `security`, `api-design`, `code-review`,
`learning-evaluation`, `recommendation-engine`, `adaptive-learning` e `challenge-design`.
Sua existência não amplia a Sprint. As regras globais de segurança de `AGENTS.md`
continuam obrigatórias mesmo com a skill `security` inativa.
