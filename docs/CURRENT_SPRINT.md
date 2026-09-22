# CodeTrack — Current Sprint

## Sprint atual

```text
SPRINT 0 — FOUNDATION
```

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

---

## S0-T07

Configurar SQLAlchemy.

---

## S0-T08

Testar conexão com banco.

---

## S0-T09

Configurar Alembic.

---

## S0-T10

Criar primeira migration técnica se necessário.

---

## S0-T11

Inicializar frontend React + TypeScript + Vite.

---

## S0-T12

Configurar comunicação básica do frontend com backend.

Não implementar telas de negócio.

---

## S0-T13

Adicionar teste do `/health`.

---

## S0-T14

Atualizar README com execução local.

---

# Definition of Done

Sprint 0 estará concluída quando:

* backend iniciar sem erro;
* frontend iniciar sem erro;
* PostgreSQL estiver disponível;
* backend conseguir conectar ao PostgreSQL;
* Alembic estiver configurado;
* `/health` responder corretamente;
* variáveis sensíveis não estiverem versionadas;
* `.env.example` existir;
* teste básico funcionar;
* documentação de execução estiver atualizada.

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
