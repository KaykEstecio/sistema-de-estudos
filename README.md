# CodeTrack

## Estado de implementação

Sprint 0 em andamento. S0-T01 a S0-T05 concluídas: estrutura inicial, ambiente
Python, configuração por variáveis de ambiente e FastAPI com `/health`.
Consulte a [execução do backend](backend/README.md).
O backend responde com `{"status":"ok"}`; frontend e banco ainda não estão configurados.
Próxima tarefa: S0-T06 — configurar PostgreSQL com Docker.

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
