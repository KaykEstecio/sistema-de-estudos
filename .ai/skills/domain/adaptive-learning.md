# Aprendizagem adaptativa

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Somente quando ativa e a funcionalidade adaptativa estiver autorizada na Sprint.
- FUTURO na Sprint 0; consultar PROJECT_SPEC, seções 6–10 e 15–17, e RN45–RN52.

## Responsabilidades

- Verificar o ciclo perfil → evidência → knowledge gap → atividade adequada → nova evidência → recalibração.
- Preservar o fluxo Onboarding → Assessment → UserSkill → Recommendation → Challenge → Attempt → Evaluation → Skill Update.
- Distinguir Track, caminho organizado, de Skill, conhecimento mensurável.

## Regras obrigatórias

- Manter níveis por Skill; considerar score, confidence e histórico conjuntamente.
- Tratar autoavaliação do onboarding como informação inicial, não prova de domínio.
- Priorizar assessment de skills relevantes aos interesses e objetivo principal.
- Tratar resultado inicial como provisório e permitir recalibração por desempenho posterior.
- Identificar lacunas em competências necessárias ou relevantes abaixo do esperado documentado.
- Verificar que recomendações reagem às evidências reais das skills envolvidas.
- Manter EvaluationService, SkillService e RecommendationService com papéis separados.
- Explicar ao usuário por que a atividade corresponde ao seu perfil e evidências.
- Testar cenários com níveis diferentes por skill e novas evidências, quando no escopo.

## Não fazer

- Reduzir CodeTrack a curso linear com progress bar ou um nível único por usuário.
- Confundir conclusão de Track com domínio comprovado de todas as skills.
- Inventar nível esperado, fórmula ou módulo futuro para completar o ciclo antecipadamente.

## Checklist

- [ ] A atividade é justificável pelo perfil e pelas evidências disponíveis?
- [ ] Uma mudança de desempenho pode alterar a recomendação de forma explicável?
- [ ] Track organiza conteúdo sem substituir UserSkill e recalibração?
