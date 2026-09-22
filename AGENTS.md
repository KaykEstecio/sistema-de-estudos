# CodeTrack — AI Development Rules

Você está trabalhando no projeto **CodeTrack**, uma plataforma adaptativa de aprendizagem em programação.

Antes de alterar código, consulte a documentação em `/docs`.

## Prioridade de documentação

Em caso de dúvida, considere esta ordem:

1. `docs/CURRENT_SPRINT.md`
2. `docs/BUSINESS_RULES.md`
3. `docs/ARCHITECTURE.md`
4. `docs/PROJECT_SPEC.md`
5. `README.md`

A Sprint atual define o que pode ser implementado agora.

---

## Regras obrigatórias

* Respeite arquitetura, escopo e regras de negócio documentadas.
* Não invente requisitos.
* Não implemente funcionalidades de sprints futuras.
* Não altere stack ou arquitetura sem justificar.
* Mudanças arquiteturais significativas exigem aprovação.
* Prefira soluções simples e legíveis.
* Evite overengineering.
* Não adicione dependências sem necessidade.
* Não crie abstrações antecipadamente.
* Não crie arquivos vazios apenas para seguir padrões.
* Regras de negócio pertencem aos Services.
* Routers devem permanecer simples.
* Repositories tratam persistência.
* Schemas tratam entrada/saída e validação.
* Models representam persistência.
* Use migrations para alterações no banco.
* Nunca exponha segredos.
* Sempre valide entradas externas.
* Preserve tipagem.
* Mantenha responsabilidades separadas.
* Escreva testes para regras críticas.

---

## Stack oficial

### Backend

* Python 3.12+
* FastAPI
* SQLAlchemy 2
* Alembic
* Pydantic
* PostgreSQL
* pytest

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* React Router
* Axios

### Infraestrutura

Desenvolvimento:

* Docker
* PostgreSQL

Produção inicial:

* Vercel
* Render
* PostgreSQL

Não substitua essas tecnologias sem justificativa e aprovação.

---

## Arquitetura

Utilizar:

`Monólito modular`

Não utilizar atualmente:

* microserviços;
* Kubernetes;
* CQRS;
* Event Sourcing;
* Kafka;
* RabbitMQ;
* GraphQL;
* arquitetura distribuída;
* Machine Learning;
* LLM no núcleo do sistema.

---

## Fluxo central do produto

```text
User
 ↓
Onboarding
 ↓
Assessment
 ↓
UserSkill
 ↓
Recommendation
 ↓
Challenge
 ↓
Attempt
 ↓
Evaluation
 ↓
Skill Update
 ↓
New Recommendation
```

---

## Conceito central

O sistema é centrado em `Skills`.

Não trate o usuário como possuidor de apenas um nível global.

Errado:

```text
User = Intermediate
```

Correto:

```text
Python = 650
SQL = 350
HTTP = 240
Logic = 580
Git = 610
```

---

## Separação obrigatória de responsabilidades

```text
ChallengeService
→ gerenciamento de desafios

AttemptService
→ gerenciamento de tentativas

EvaluationService
→ avaliação de desempenho

SkillService
→ atualização das habilidades

RecommendationService
→ recomendação das próximas atividades
```

Não concentrar essas responsabilidades em um único service.

---

## Controle de escopo

Antes de implementar:

1. leia `docs/CURRENT_SPRINT.md`;
2. verifique a tarefa atual;
3. inspecione o código existente;
4. faça apenas as alterações necessárias;
5. teste;
6. informe o que foi alterado.

Funcionalidades que pertencem ao futuro devem ser marcadas:

```text
FUTURO
```

e não implementadas.

---

## Forma de resposta durante desenvolvimento

Quando apropriado, responda usando:

### Objetivo

O que será feito.

### Arquivos

Arquivos criados ou modificados.

### Implementação

Mudanças realizadas.

### Validação

Como validar.

### Resultado

O que deve acontecer.

### Próximo passo

Apenas a próxima tarefa lógica da Sprint atual.

Não gere dezenas de funcionalidades de uma vez.

---

## Uso de IA

Este projeto também existe para aprendizado.

Portanto:

* explique decisões relevantes;
* escreva código compreensível;
* não esconda regras importantes;
* não utilize abstrações avançadas sem necessidade;
* não reescreva grandes áreas funcionais sem motivo;
* preserve a capacidade do desenvolvedor de compreender o sistema.

---

## Segurança

Nunca:

* armazene senha em texto puro;
* exponha `password_hash`;
* versione `.env`;
* coloque secrets no código;
* exponha `DATABASE_URL`;
* exponha stack traces em produção;
* confie no frontend para autorização.

---

## Regra final

O objetivo não é implementar o maior número possível de funcionalidades.

O objetivo é construir um sistema:

* compreensível;
* testável;
* modular;
* seguro;
* evolutivo;
* coerente com a documentação.
