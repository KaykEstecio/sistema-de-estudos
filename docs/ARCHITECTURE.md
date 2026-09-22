# CodeTrack — Architecture

## 1. Padrão

Utilizar:

```text
Modular Monolith
```

Não utilizar microserviços neste momento.

---

# 2. Fluxo técnico

```text
Frontend
React + TypeScript
        ↓
HTTP / JSON
        ↓
FastAPI
        ↓
Router
        ↓
Service
        ↓
Repository
        ↓
SQLAlchemy
        ↓
PostgreSQL
```

---

# 3. Backend

Estrutura planejada:

```text
backend/

├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── base.py
│   │
│   ├── modules/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── categories/
│   │   ├── skills/
│   │   ├── onboarding/
│   │   ├── assessments/
│   │   ├── tracks/
│   │   ├── challenges/
│   │   ├── attempts/
│   │   ├── evaluation/
│   │   ├── progress/
│   │   └── recommendations/
│   │
│   └── shared/
│
├── tests/
├── alembic/
├── requirements.txt
└── .env.example
```

Não criar todos os módulos antecipadamente se ainda não forem necessários.

---

# 4. Camadas

## Router

Responsável por:

* HTTP;
* query/path parameters;
* dependencies;
* códigos HTTP;
* chamada do service.

Evitar regras de negócio.

---

## Schema

Responsável por:

* request;
* response;
* validação;
* serialização.

Utilizar Pydantic.

---

## Service

Responsável por:

* regras de negócio;
* decisões;
* coordenação entre repositories;
* validações de domínio.

---

## Repository

Responsável por:

* queries;
* persistência;
* acesso ao banco.

---

## Model

Responsável pela representação ORM.

---

# 5. Principais Services

```text
AuthService
UserService
SkillService
AssessmentService
ChallengeService
AttemptService
EvaluationService
ProgressService
RecommendationService
```

Responsabilidades devem permanecer separadas.

---

# 6. Banco

Utilizar:

```text
PostgreSQL
```

ORM:

```text
SQLAlchemy 2
```

Migrations:

```text
Alembic
```

Mudanças estruturais devem possuir migration.

---

# 7. Entidades principais

```text
User
Category
Skill
UserSkill
SkillRequirement

UserInterest
UserGoal

Assessment
AssessmentResult

Track
Module

Challenge
ChallengeSkill
ChallengeHint

ChallengeAttempt
AttemptEvent

Recommendation
```

---

# 8. DER conceitual

```text
USER
 │
 ├── USER_SKILL ─────────────── SKILL
 │                                │
 │                                ├── CATEGORY
 │                                │
 │                                └── SKILL_REQUIREMENT
 │
 ├── USER_INTEREST
 │
 ├── USER_GOAL
 │
 ├── ASSESSMENT
 │
 ├── CHALLENGE_ATTEMPT
 │        │
 │        ├── ATTEMPT_EVENT
 │        │
 │        └── CHALLENGE
 │               │
 │               └── CHALLENGE_SKILL ── SKILL
 │
 └── RECOMMENDATION


TRACK
 │
 └── MODULE
        │
        └── CHALLENGE
```

---

# 9. Models planejados

## User

```text
id
name
email
password_hash
role
onboarding_completed
created_at
updated_at
```

---

## Category

```text
id
name
slug
description
```

---

## Skill

```text
id
category_id
name
slug
description
is_active
```

---

## UserSkill

```text
id
user_id
skill_id
score
confidence
attempts
successful_attempts
last_practiced_at
updated_at
```

Constraint:

```text
UNIQUE(user_id, skill_id)
```

---

## SkillRequirement

```text
id
skill_id
required_skill_id
minimum_score
```

---

## UserInterest

```text
id
user_id
category_id
priority
```

---

## UserGoal

```text
id
user_id
goal_type
description
is_primary
created_at
```

---

## Track

```text
id
title
slug
description
difficulty
is_active
created_at
```

---

## Module

```text
id
track_id
title
description
position
```

---

## Challenge

```text
id
module_id
title
description
challenge_type
difficulty
difficulty_score
estimated_minutes
starter_code
is_active
created_at
updated_at
```

`module_id` poderá ser nullable para desafios independentes.

---

## ChallengeSkill

```text
challenge_id
skill_id
weight
```

---

## ChallengeHint

```text
id
challenge_id
level
content
```

---

## ChallengeAttempt

```text
id
user_id
challenge_id
status
draft_answer
attempt_number
execution_count
hints_used
passed_tests
total_tests
time_spent_seconds
user_difficulty_rating
started_at
submitted_at
last_activity_at
```

---

## AttemptEvent

```text
id
attempt_id
event_type
metadata
created_at
```

---

## Assessment

```text
id
user_id
assessment_type
started_at
completed_at
```

---

## AssessmentResult

```text
id
assessment_id
skill_id
score
confidence
```

---

## Recommendation

```text
id
user_id
challenge_id
recommendation_score
reason
status
created_at
```

---

# 10. API padrão

Prefixo:

```text
/api/v1
```

---

# 11. Endpoints planejados

## Auth

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

Refresh token poderá ser adicionado posteriormente.

---

## Onboarding

```text
GET   /api/v1/onboarding
POST  /api/v1/onboarding
PATCH /api/v1/onboarding
```

---

## Skills

```text
GET /api/v1/skills
GET /api/v1/skills/{id}
GET /api/v1/users/me/skills
```

---

## Assessments

```text
POST /api/v1/assessments
GET  /api/v1/assessments/{id}

POST /api/v1/assessments/{id}/answers
POST /api/v1/assessments/{id}/finish
```

---

## Challenges

```text
GET /api/v1/challenges
GET /api/v1/challenges/{id}
```

Possíveis filtros:

```text
skill
difficulty
type
completed
```

---

## Attempts

```text
POST  /api/v1/challenges/{id}/attempts
GET   /api/v1/attempts/{id}
PATCH /api/v1/attempts/{id}

POST /api/v1/attempts/{id}/submit
POST /api/v1/attempts/{id}/hint
```

---

## Recommendations

```text
GET /api/v1/recommendations
```

---

## Dashboard

```text
GET /api/v1/dashboard
```

---

# 12. Status HTTP

Utilizar adequadamente:

```text
200 OK
201 Created
204 No Content

400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
500 Internal Server Error
```

---

# 13. Segurança

Obrigatório:

```text
password hashing
JWT
role authorization
Pydantic validation
CORS
environment variables
centralized error handling
```

Nunca armazenar segredos no repositório.

---

# 14. Frontend

Estrutura inicial sugerida:

```text
frontend/

src/
├── components/
├── pages/
├── layouts/
├── services/
├── hooks/
├── contexts/
├── types/
├── utils/
└── routes/
```

Criar pastas somente quando forem necessárias.

---

# 15. Git

Branches opcionais:

```text
main
develop
feature/*
fix/*
```

Commits:

```text
feat: configure FastAPI application

feat: add database connection

feat: add user registration

fix: prevent duplicated email

test: add authentication tests
```

---

# 16. Testes

Backend:

```text
pytest
```

Prioridade:

* regras de domínio;
* autenticação;
* permissões;
* Skills;
* Evaluation;
* Recommendation.

Não perseguir 100% de cobertura artificialmente.
