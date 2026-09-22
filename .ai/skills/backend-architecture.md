# Arquitetura de backend

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Em mudanças no backend FastAPI, quando esta skill estiver ativa na Sprint.
- Na Sprint 0, limitar o trabalho à fundação; serviços de domínio abaixo são FUTURO.

## Responsabilidades

- Manter o monólito modular em Python 3.12+, FastAPI, Pydantic e SQLAlchemy 2.
- Router: HTTP e dependências; schema: entrada, saída e validação.
- Service: regras e coordenação; repository: consultas e persistência; model: ORM.
- ChallengeService gerencia desafios; AttemptService gerencia tentativas.
- EvaluationService avalia desempenho; SkillService atualiza habilidades.
- RecommendationService seleciona próximas atividades.

## Regras obrigatórias

- Consultar `docs/ARCHITECTURE.md`, seções 3–5, antes de distribuir responsabilidades.
- Criar módulos e camadas somente conforme a tarefa exigir; preservar tipagem.
- Coordenar operações entre módulos pelos services responsáveis, sem ciclos de dependência.
- Encaminhar atualização de UserSkill ao SkillService, inclusive após Evaluation.
- Explicar decisões relevantes com código simples, compreensível para aprendizado.

## Não fazer

- Criar services gigantes, regras em routers ou consultas espalhadas pelas camadas.
- Introduzir microserviços, CQRS, Event Sourcing ou arquitetura distribuída.
- Criar interfaces, factories ou módulos vazios para necessidades hipotéticas.

## Checklist

- [ ] Cada operação tem um responsável e dependências compreensíveis?
- [ ] As camadas existentes bastam, sem misturar desafio, tentativa, avaliação e skills?
- [ ] O diff respeita a tarefa atual e possui validação proporcional?
