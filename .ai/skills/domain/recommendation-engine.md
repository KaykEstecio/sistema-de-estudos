# Motor de recomendação

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Somente quando ativa e Recommendation Engine estiver no escopo da Sprint.
- FUTURO na Sprint 0; consultar RN11–RN12 e RN37–RN46 em BUSINESS_RULES.

## Responsabilidades

- Concentrar seleção de próximas atividades no RecommendationService.
- Relacionar objetivo, interesses, UserSkill, confidence e knowledge gaps.
- Considerar SkillRequirements, difficulty_score, histórico e desafios recentes quando disponíveis.

## Regras obrigatórias

- Implementar inicialmente algoritmo determinístico e baseado em regras explícitas.
- Filtrar desafios inativos e considerar pré-requisitos aplicáveis antes da classificação.
- Reduzir prioridade de concluídos recentes, exceto revisão justificada.
- Usar desafios muito abaixo do nível principalmente para revisão.
- Evitar normalmente desafios muito acima do nível atual das skills relevantes.
- Dar atenção às lacunas relacionadas ao objetivo do usuário.
- Usar aproximadamente 20% revisão, 60% nível atual e 20% acima como orientação, não quota rígida.
- Gerar reason compreensível para cada recomendação, fiel aos critérios realmente utilizados.
- Definir desempate estável e testar que os mesmos dados produzem a mesma seleção.
- Explicitar critérios ou limiares ainda indefinidos; não inventar domínio ausente.
- Testar filtros, pré-requisitos, histórico e ausência de candidatos elegíveis.

## Não fazer

- Usar LLM, embeddings, machine learning ou modelos externos.
- Recomendar inativos ou forçar a proporção ignorando elegibilidade.
- Usar apenas um nível global ou fornecer reason genérica desconectada da seleção.

## Checklist

- [ ] Candidatos respeitam atividade, pré-requisitos e dificuldade aplicáveis?
- [ ] Histórico e novas evidências afetam a prioridade de forma verificável?
- [ ] Cada resultado tem reason fiel e comportamento determinístico?
