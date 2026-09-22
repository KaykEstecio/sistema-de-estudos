# Design pedagógico de desafios

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Somente quando ativa e Challenges estiverem no escopo da Sprint.
- FUTURO na Sprint 0; consultar PROJECT_SPEC, seções 11–14, e RN13–RN28.

## Responsabilidades

- Orientar QUIZ, CODE, BUG_FIX, CODE_READING, REFACTORING, SQL, API, ARCHITECTURE e PROJECT.
- Selecionar apenas tipos autorizados para a tarefa, sem implementar todos antecipadamente.
- Manter o conteúdo no ChallengeService e a experiência de tentativa no AttemptService.

## Regras obrigatórias

- Definir objetivo de aprendizagem claro, enunciado e resultado esperado verificável.
- Indicar difficulty e difficulty_score em 0–1000, conforme as regras documentadas.
- Usar VERY_EASY, EASY, MEDIUM, HARD ou VERY_HARD para dificuldade textual.
- Relacionar skills e pesos; desafio ativo exige ao menos uma Skill e soma de 100%.
- Fornecer informações necessárias à resolução e eliminar ambiguidades de entrada e saída.
- Construir hints progressivos: conceito → direção técnica → pseudocódigo → orientação avançada.
- Reservar solução completa explicada para etapa posterior; não entregá-la na primeira dica.
- Prever registro de dicas e visualização de solução na tentativa quando implementada.
- Alinhar avaliação ao objetivo e mostrar feedback específico, inclusive resultados parciais.
- Preservar desafios independentes com module_id opcional conforme a arquitetura.

## Não fazer

- Confundir dificuldade textual com domínio global do usuário.
- Exigir conhecimentos não indicados ou penalizar pedido de ajuda como fracasso automático.
- Introduzir execução arbitrária de código, sandbox distribuído ou correção por LLM no MVP.

## Checklist

- [ ] Objetivo, enunciado e resultado esperado permitem avaliação sem ambiguidade?
- [ ] Skills, pesos e dificuldade são coerentes com o objetivo pedagógico?
- [ ] As dicas avançam gradualmente e o feedback ajuda a compreender os erros?
