# Modelagem de dados

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Em modelagem, persistência ou migrations autorizadas, com esta skill ativa.
- Na Sprint 0, configurar PostgreSQL, SQLAlchemy 2 e Alembic; entidades são FUTURO.

## Responsabilidades

- Consultar entidades e atributos em `docs/ARCHITECTURE.md`, seções 7–9.
- Identidade e perfil: User, UserInterest, UserGoal.
- Competências: Category, Skill, UserSkill, SkillRequirement.
- Conteúdo: Track, Module, Challenge, ChallengeSkill, ChallengeHint.
- Evidências: ChallengeAttempt, AttemptEvent, Assessment, AssessmentResult.
- Seleção de atividades: Recommendation.

## Regras obrigatórias

- Definir PK, FK e cardinalidade; representar N:N pelas associações documentadas.
- Exigir UNIQUE(user_id, skill_id) em UserSkill e unicidade de e-mail em User.
- Aplicar CHECK para score de habilidade em 0–1000, confidence em 0–1 e difficulty_score em 0–1000.
- Escolher precisão de ChallengeSkill.weight que permita validar total de 100%.
- Validar a soma dos pesos no service em operação transacional; CHECK por linha não valida o conjunto.
- Relacionar Skill a Category; tentativa a User e Challenge; pré-requisitos às duas Skills.
- Justificar nullable; Challenge.module_id pode ser nulo para desafio independente.
- Definir cascades explicitamente, preservando histórico de tentativas (RN19–RN20).
- Adicionar índices por consultas e constraints concretas, sem duplicar índices existentes.
- Versionar alterações estruturais via Alembic e revisar a migration antes de aplicá-la.

## Não fazer

- Criar todas as entidades antecipadamente, colunas redundantes ou migrations vazias.
- Usar criação automática de tabelas como substituto de migrations.
- Aplicar cascade de exclusão que apague evidências sem regra documentada.

## Checklist

- [ ] PK, FK, UNIQUE, CHECK, nullable e relacionamentos expressam as regras aplicáveis?
- [ ] Pesos são validados como conjunto e o histórico está preservado?
- [ ] A migration foi validada em banco de desenvolvimento descartável?
