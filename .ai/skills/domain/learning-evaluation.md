# Avaliação de aprendizagem

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Somente quando ativa e Evaluation estiver no escopo da Sprint atual.
- FUTURO na Sprint 0; consultar RN27–RN36 em `docs/BUSINESS_RULES.md`.

## Responsabilidades

- Preservar o fluxo Attempt → Evaluation → Skill Update.
- EvaluationService interpreta desempenho; SkillService atualiza UserSkill.
- Produzir feedback que mostre acertos, dificuldades e próximos pontos de atenção.

## Regras obrigatórias

- Considerar resultado, difficulty_score, hints, tentativas, testes e nível atual.
- Considerar tempo quando disponível e pertinente, sem defini-lo como critério isolado.
- Aplicar pesos de ChallengeSkill à atualização das habilidades relacionadas.
- Limitar score a 0–1000 e confidence a 0–1 após a atualização.
- Tratar ajuda como redução de evidência de domínio, sem zerar aprendizagem automaticamente.
- Aumentar confidence com evidências consistentes; poucos exercícios não justificam confiança alta.
- Usar fórmula inicial simples, explícita e explicável; nomear parâmetros e justificar valores.
- Se coeficientes ou critérios não estiverem definidos, explicitar a decisão pendente sem inventar regra.
- Encaminhar persistência pelos responsáveis; ChallengeService não atualiza skills.
- Validar casos de resultado parcial, ajuda, pesos e limites com pytest.

## Não fazer

- Reduzir avaliação a correto/incorreto ou penalizar ajuda exageradamente.
- Usar ML, LLM ou números mágicos que escondam regras pedagógicas.
- Sobrescrever histórico de tentativas ou atualizar UserSkill diretamente no router.

## Checklist

- [ ] O feedback descreve evidências reais e dificuldades específicas?
- [ ] Pesos, score e confidence respeitam as regras?
- [ ] A fórmula pode ser explicada e testada sem ocultar decisões?
