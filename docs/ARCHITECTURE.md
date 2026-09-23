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

Decisões de persistência da S1-T01:

- Tabela `users`; ID inteiro gerado por PostgreSQL Identity.
- `name`: varchar(120); `email`: varchar(320); hash em text.
- Todos os atributos abaixo são obrigatórios na persistência.
- Unicidade por índice `ux_users_email_lower` em lower(email), sem índice redundante.
- Role armazenada em varchar com CHECK STUDENT/ADMIN, padrão STUDENT no ORM e banco.
- onboarding_completed inicia falso no ORM e banco; onboarding funcional é FUTURO.
- Datas usam timezone, com padrão now() no banco. updated_at é atualizado pelo
  SQLAlchemy nas operações ORM; SQL manual deve definir esse campo explicitamente.
- Não há geração de hash no model; utilitários ficam em core/security.py.

Contratos preparados na S1-T02 e usados pelo cadastro na S1-T04:

- `UserCreate`: name com 1–120 caracteres após trim, email válido até 320
  caracteres e password não vazio em SecretStr, sem trim ou normalização.
- Campos extras são rejeitados, inclusive role, onboarding_completed e password_hash.
- A senha é excluída da serialização do schema de entrada. Os limites e a política
  de senha de cadastro estão definidos na RN02: de 15 a 128 caracteres.
- `UserRead`: id, name, email, role, onboarding_completed, created_at e updated_at;
  leitura por atributos do ORM, sem credenciais na saída.
- `UserRepository`: get_by_id, get_by_email e create com hash já calculado.
  Consulta e-mail sem distinção de caixa; create faz flush, nunca commit.
- IntegrityError por duplicidade é propagado; o service faz rollback e tradução
  para erro de domínio/HTTP 409 na S1-T04, inclusive em concorrência.

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

### Contratos do catálogo — decisão S2-T01

Contratos planejados para a Sprint 2; ainda não implementados. A rota
`/users/me/skills` acima é FUTURO, pois depende de UserSkill.

| Método | Caminho | Permissão | Sucesso |
| --- | --- | --- | --- |
| GET | /api/v1/categories | Autenticado | 200, página de categorias |
| GET | /api/v1/categories/{id} | Autenticado | 200, categoria |
| POST | /api/v1/categories | ADMIN | 201, categoria criada |
| PATCH | /api/v1/categories/{id} | ADMIN | 200, categoria atualizada |
| GET | /api/v1/skills | Autenticado | 200, página de skills |
| GET | /api/v1/skills/{id} | Autenticado | 200, skill |
| POST | /api/v1/skills | ADMIN | 201, skill criada |
| PATCH | /api/v1/skills/{id} | ADMIN | 200, skill atualizada |

Não adicionar DELETE, PUT ou rotas separadas de ativação. PATCH de Skill aceita
is_active. Reutilizar get_current_user e require_admin da Sprint 1.

Campos e persistência:

| Campo | Contrato |
| --- | --- |
| id | INTEGER com Identity, gerado pelo banco; entrada de path de 1 a 2147483647 |
| name | Obrigatório na criação; string de 1–120 caracteres após trim |
| slug | Obrigatório na criação; trim e minúsculas; 1–120 caracteres; padrão ASCII `^[a-z0-9]+(?:-[a-z0-9]+)*$` |
| description | String opcional; trim, máximo 2000 caracteres; omitida ou null vira NULL; vazia após trim vira NULL |
| category_id | Somente Skill; inteiro JSON estrito positivo até 2147483647, obrigatório e existente |
| is_active | Somente Skill; booleano JSON estrito, não nulo; default true no ORM e banco |

Slug é informado explicitamente: não transliterar acentos nem gerar a partir de
name. Unicidade global por tabela, via constraints uq_categories_slug e
uq_skills_slug; strings persistidas já normalizadas. Usar CHECK de formato
do slug no banco para impedir variantes fora do padrão por escrita direta.
name/slug usam VARCHAR(120), description VARCHAR(2000) anulável. Demais campos
são NOT NULL. FK skills.category_id → categories.id com ON DELETE RESTRICT,
índice ix_skills_category_id; não criar cascata de exclusão. Não adicionar
timestamps ou campos não previstos aos models deste recorte.

POST exige name/slug e, para Skill, category_id; description e is_active têm
os defaults descritos. PATCH exige ao menos um campo editável; ausência preserva
valor, null só é aceito em description. Campos extras e id no corpo são 422.
Sem coerção de números/booleanos para strings. Atualização sem mudança real é
válida e retorna 200. Schemas de saída:

- CategoryRead: id, name, slug, description.
- SkillRead: id, category_id, name, slug, description, is_active.

Não embutir categoria, desempenho individual ou credenciais na skill.
Repositories tratam persistência; CategoryService e SkillService coordenam
validação de existência, visibilidade e transações. Routers adaptam HTTP.
Unicidade é garantida pelo banco inclusive sob concorrência; traduzir apenas
constraints conhecidas para erros de domínio. Outras falhas não viram 409.

Listagem: limit inteiro de 1–100 (default 20), offset inteiro >= 0 (default 0).
Resposta `{"items": [...], "limit": 20, "offset": 0, "total": 0}`; total aplica
os mesmos filtros/visibilidade, antes de paginação. Ordenação fixa por id ASC,
sem ordenação dinâmica. Página vazia retorna 200. Consultas devem ocorrer no
banco, sem carregar todo o catálogo para filtrar em memória.

Skills aceita category_id positivo e is_active=true/false. ADMIN sem is_active
vê ambas; STUDENT sem filtro ou com true vê somente ativas. STUDENT com false
recebe 403. Categoria inexistente no filtro produz página vazia, não 404.
Categories aceita somente paginação. Parâmetros desconhecidos de listagem
são 422; não adicionar busca textual ou filtros além destes nesta Sprint.

Erros seguem o formato `{"detail": "mensagem"}`; 422 reutiliza lista segura
de loc/type/msg da Sprint 1. Precedência: dependência de autenticação/autorização
antes da consulta ao recurso; autorização nunca depende do corpo ou query.

| Código | Condição | Mensagem |
| --- | --- | --- |
| 401 | Ausência/falha de autenticação | Autenticação inválida ou ausente. |
| 403 | STUDENT escreve ou solicita skills inativas | Permissão insuficiente. |
| 404 | Categoria de path ou de escrita não existe | Categoria não encontrada. |
| 404 | Skill não existe ou está inativa para STUDENT | Skill não encontrada. |
| 409 | Slug de categoria já usado | Slug de categoria já cadastrado. |
| 409 | Slug de skill já usado | Slug de skill já cadastrado. |
| 422 | Path, query ou corpo inválido | Lista de erros seguros de validação |

401 mantém WWW-Authenticate: Bearer. Para PATCH de Skill, consultar o alvo antes
de validar a existência de uma nova categoria; transação não persiste alteração
parcial. Mudança de role no banco vale na requisição seguinte.

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

Decisão S1-T03: hash/verificação usam argon2-cffi e o perfil explícito
RFC_9106_LOW_MEMORY: Argon2id, 65536 KiB, 3 iterações, paralelismo 4,
salt aleatório de 16 bytes e hash de 32 bytes. A biblioteca implementa
o algoritmo e gera o salt; não há criptografia própria ou salt fixo.

`hash_password` recebe a senha sem modificações e retorna o hash codificado.
`verify_password` recebe o hash da persistência e retorna falso para senha
incorreta ou hash inválido. Não registra credenciais nem grava no banco.
Falhas ao gerar hash não são convertidas em sucesso ou hash vazio.
UserService utiliza esses utilitários no cadastro desde a S1-T04.

Os parâmetros seguem o [perfil documentado pelo argon2-cffi](https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.profiles.RFC_9106_LOW_MEMORY).
Avaliar custo/memória no ambiente de produção antes do deploy.
Política de comprimento/aceitação de senha está definida na RN02;
hashing não faz trim, normalização ou truncamento.

Contrato implementado S1-T04: `POST /api/v1/auth/register` recebe JSON com
`name`, `email` e `password`; campos extras são rejeitados. Retorna 201 com
UserRead (id, name, email, role, onboarding_completed, created_at, updated_at).
Não autentica nem emite token. E-mail duplicado retorna 409 com
`{"detail":"E-mail já cadastrado."}`. Entrada inválida retorna 422 com lista
`detail`, contendo loc/type/msg; input e ctx são omitidos e msg é genérica
para não reproduzir credenciais, inclusive em JSON inválido. Erros de campos
extras omitem também o nome enviado pelo cliente no último segmento de loc.

UserService faz hash, criação, commit e rollback. A restrição PostgreSQL
`ux_users_email_lower` decide unicidade inclusive sob concorrência; somente
SQLSTATE 23505 desse índice vira EmailAlreadyRegistered, traduzido pelo router
para 409. Outras falhas permanecem falhas internas. A resposta pública é
preparada antes do commit e devolvida somente após seu sucesso.

Decisão S1-T05 — JWT:

- Biblioteca PyJWT 2.14.0, para assinatura e validação sem criptografia própria.
- HS256 fixo no servidor, nunca escolhido pelo header recebido. Referência:
  [API PyJWT](https://pyjwt.readthedocs.io/en/stable/api.html).
- Validade padrão de 30 minutos, configurável entre 1 e 120 por
  JWT_ACCESS_TOKEN_MINUTES. Datas em segundos inteiros UTC, sem tolerância extra.
- Claims obrigatórios: sub (ID positivo de User como string decimal), iat,
  exp, iss=codetrack, aud=codetrack-api e token_type=access.
- Assinatura, expiração, emissão futura, emissor, destinatário, tipo e formato
  são validados. exp precisa ser posterior a iat. ID respeita INTEGER PostgreSQL.
- Payload não contém senha, hash, e-mail ou role. JWT é assinado, não cifrado.
  decode_access_token retorna ID; existência e permissões serão consultadas no
  banco desde a S1-T07. Não existe refresh token neste recorte.
- JWTSettings exige JWT_SECRET_KEY com pelo menos 32 bytes, sem valor padrão.
  Gerar com secrets.token_urlsafe(32) e guardar somente no ambiente/.env local.
  Comprimento não garante aleatoriedade; não usar frase escolhida manualmente.
  Rotacionar a chave invalida tokens anteriores.
- JWTSettings é carregado explicitamente ao usar os utilitários; migrations e
  /health não exigem segredo JWT. Settings reconhece as variáveis do .env
  compartilhado. Login utiliza essa configuração desde a S1-T06; autenticação
  de rotas está implementada desde a S1-T07.

Contrato S1-T06: `POST /api/v1/auth/login` recebe JSON com email e password,
sem campos extras. E-mail é validado e normalizado como no cadastro. Senha
aceita 1–128 caracteres sem transformação: o mínimo de criação de senha não
é reaplicado ao login, permitindo rejeitar uma tentativa curta com 401.
Formato inválido, senha vazia/longa ou campos extras retornam 422 sem valores.

AuthService consulta UserRepository, verifica Argon2 e emite JWT somente após
credenciais válidas. Não altera usuário ou role. Usuário inexistente também
executa uma verificação contra hash descartável gerado uma vez por processo,
reduzindo diferença de custo sem prometer tempo constante.

Sucesso retorna 200 com access_token, token_type="bearer" e expires_in em
segundos, com Cache-Control: no-store e Pragma: no-cache. Falhas de credenciais
retornam sempre 401 com `{"detail":"E-mail ou senha inválidos."}` e
WWW-Authenticate: Bearer. Não há logs de senha, hash ou token no serviço.
Endpoint usa JSON, não formulário OAuth2.

Contrato S1-T07: `GET /api/v1/auth/me` exige Authorization: Bearer <token>.
Retorna 200 com UserRead do usuário identificado pelo sub validado e consultado
no banco, sem credenciais e com Cache-Control: no-store. IDs fornecidos pelo
cliente não selecionam outro usuário. Token ausente, malformado, inválido,
expirado ou usuário inexistente retornam o mesmo 401 com
`{"detail":"Autenticação inválida ou ausente."}` e WWW-Authenticate: Bearer.

users/dependencies.py adapta autenticação e autorização para HTTP. AuthService
valida identidade e exige ADMIN quando solicitado; role sempre vem do banco.
A dependência require_admin retorna 403 para STUDENT, 401 para anônimo e aceita
ADMIN. Testada em rota exclusiva de teste; nenhum endpoint administrativo foi
adicionado ao produto. Alteração de role e remoção do usuário valem na próxima
requisição mesmo com um token anteriormente emitido.

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
