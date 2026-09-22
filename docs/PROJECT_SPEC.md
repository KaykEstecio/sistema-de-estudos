# CodeTrack — Product Specification

## 1. Visão

O CodeTrack é uma plataforma adaptativa de aprendizagem em programação.

O sistema deverá analisar:

* conhecimentos;
* interesses;
* objetivos;
* desempenho;
* dificuldades;
* histórico;
* lacunas de conhecimento.

Com essas informações deverá selecionar atividades adequadas para cada usuário.

---

# 2. Objetivos

O sistema deverá:

1. identificar conhecimento inicial;
2. criar perfil de aprendizagem;
3. manter níveis separados por skill;
4. identificar lacunas;
5. recomendar desafios;
6. adaptar dificuldade;
7. registrar tentativas;
8. fornecer feedback;
9. atualizar habilidades;
10. acompanhar evolução.

---

# 3. Perfis

## STUDENT

Pode:

* cadastrar-se;
* fazer login;
* realizar onboarding;
* realizar assessments;
* visualizar skills;
* acessar conteúdos;
* realizar challenges;
* utilizar hints;
* enviar soluções;
* acompanhar progresso;
* receber recomendações.

## ADMIN

Pode:

* criar categorias;
* criar skills;
* configurar pré-requisitos;
* criar tracks;
* criar módulos;
* criar challenges;
* configurar hints;
* editar conteúdo;
* desativar conteúdo.

---

# 4. Conteúdo inicial do MVP

Inicialmente:

* Programming Logic;
* Python;
* SQL;
* HTTP;
* REST API;
* Git.

A arquitetura deve permitir adicionar outras áreas posteriormente.

---

# 5. Categorias futuras possíveis

### Fundamentals

* Logic
* Algorithms
* Data Structures

### Languages

* Python
* JavaScript
* TypeScript
* Java
* C#

### Backend

* HTTP
* REST
* Authentication
* FastAPI
* Node.js

### Frontend

* HTML
* CSS
* JavaScript
* React

### Database

* SQL
* PostgreSQL
* Modeling
* Indexes

### DevOps

* Git
* Docker
* CI/CD

### Automation

* Python
* scripts
* API integrations

---

# 6. Onboarding

Coletar inicialmente:

### experiência declarada

* Never programmed
* Beginner
* Basic
* Intermediate
* Advanced

### interesses

Permitir seleção múltipla.

### objetivo principal

Exemplos:

* aprender do zero;
* melhorar lógica;
* entrar no mercado;
* aprender backend;
* aprender frontend;
* faculdade;
* entrevistas;
* algoritmos;
* automação.

A autoavaliação não define definitivamente o nível do usuário.

---

# 7. Assessment

Depois do onboarding poderá existir um teste diagnóstico.

Deverá avaliar skills relevantes aos interesses e objetivos.

Exemplo:

```text
Objetivo: Backend Python
```

Pode avaliar:

```text
Logic
Python
SQL
HTTP
```

Não é necessário avaliar React nesse cenário.

---

# 8. Skill

Skill representa uma competência mensurável.

Exemplos:

```text
Variables
Conditionals
Loops
Functions
Python
SQL
HTTP
REST
Git
FastAPI
```

---

# 9. UserSkill

Cada usuário poderá possuir nível diferente em cada Skill.

Exemplo:

```text
Python 680
Logic 620
SQL 390
HTTP 260
Git 570
```

Informações importantes:

```text
score
confidence
attempts
successful_attempts
last_practiced_at
```

---

# 10. Tracks

Tracks existem para organizar caminhos.

Exemplo:

```text
Backend Python Developer
```

Mas não são o núcleo adaptativo.

Distinção:

```text
Skill
= conhecimento

Track
= caminho organizado
```

---

# 11. Challenges

Tipos:

```text
QUIZ
CODE
BUG_FIX
CODE_READING
REFACTORING
SQL
API
ARCHITECTURE
PROJECT
```

Cada desafio deverá estar relacionado a uma ou mais Skills.

---

# 12. Experiência do desafio

Fluxo:

```text
Challenge
   ↓
Attempt
   ↓
Solve
   ↓
Hint?
   ↓
Submit
   ↓
Evaluation
   ↓
Feedback
   ↓
Skill Update
```

---

# 13. Sistema de ajuda

Progressão:

```text
Hint 1
conceito

Hint 2
direção técnica

Hint 3
pseudocódigo

Hint 4
orientação avançada

Solution
resolução explicada
```

A solução completa não deverá ser mostrada imediatamente.

---

# 14. Feedback

Evitar:

```text
Incorrect.
```

Preferir:

```text
3/5 tests passed.

✓ positive values
✓ zero
✓ even values

✗ negative values
✗ edge case
```

---

# 15. Recommendation Engine

O recomendador deverá utilizar futuramente:

* objetivos;
* interesses;
* skills;
* confidence;
* lacunas;
* requisitos;
* histórico;
* dificuldade;
* conteúdos recentes.

Inicialmente será determinístico e baseado em regras.

Não utilizar Machine Learning no MVP.

---

# 16. Explicabilidade

Toda recomendação deve possuir razão compreensível.

Exemplo:

```text
Recomendado porque SQL é uma habilidade prioritária
para seu objetivo Backend e este desafio está próximo
do seu nível atual.
```

---

# 17. Knowledge gaps

Exemplo:

```text
Goal: Backend Python

Python = 720
Git = 610
SQL = 480
HTTP = 180
REST = 220
```

O sistema poderá identificar:

```text
HTTP
REST
```

como lacunas.

---

# 18. Projetos progressivos

Posteriormente:

```text
Todo API
```

poderá ser dividido em:

```text
1. model
2. POST /tasks
3. GET /tasks
4. validation
5. authentication
6. tests
```

---

# 19. MVP

O MVP deverá possuir:

* estrutura da aplicação;
* usuários;
* autenticação;
* onboarding;
* categories;
* skills;
* UserSkill;
* SkillRequirement;
* assessment;
* challenges;
* hints;
* attempts;
* evaluation;
* skill update;
* recommendation V1;
* dashboard básico.

---

# 20. Fora do MVP

Não implementar inicialmente:

* generative AI;
* machine learning;
* microservices;
* Kubernetes;
* social network;
* chat;
* forum;
* global ranking;
* mobile app;
* execução arbitrária de código;
* sandbox distribuído;
* análise automática de código por LLM.

---

# 21. Roadmap

```text
Sprint 0
Foundation

Sprint 1
Users + Auth

Sprint 2
Categories + Skills

Sprint 3
Onboarding

Sprint 4
Assessment

Sprint 5
Challenges

Sprint 6
Attempts

Sprint 7
Evaluation

Sprint 8
Recommendation Engine

Sprint 9
Dashboard

Sprint 10
Challenge Experience

Sprint 11
Tests & Quality

Sprint 12
Deploy
```
