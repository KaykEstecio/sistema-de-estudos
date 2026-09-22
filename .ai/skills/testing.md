# Testes

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Em alterações que exigem validação, quando ativa na Sprint.
- Na Sprint 0, testar /health e conexão com banco conforme a tarefa; casos de domínio são FUTURO.

## Responsabilidades

- Usar pytest e priorizar: domínio, autenticação, permissões, atualização de skills, evaluation e recommendation.
- Testar regras nos services; usar integração quando HTTP, persistência ou transações forem relevantes.
- Manter fixtures simples, isoladas e compreensíveis.

## Regras obrigatórias

- Vincular casos às regras de `docs/BUSINESS_RULES.md` e ao comportamento observável.
- Para score, testar 0, 1000 e valores externos; verificar limites após atualização.
- Para confidence, testar 0, 1 e valores externos; poucas evidências não devem inflá-la.
- Testar soma de ChallengeSkill igual a 100%, abaixo e acima; desafio ativo sem Skill é inválido.
- Testar ownership: outro usuário não altera tentativa; nova tentativa preserva histórico.
- Testar filtros de recomendação, exclusão de inativos e prioridade de concluídos recentes.
- Testar SkillRequirements atendidos e não atendidos, conforme a regra de seleção vigente.
- Cobrir regressões reproduzíveis e resultados parciais de evaluation quando no escopo.
- Usar PostgreSQL isolado quando o teste depender de constraints ou comportamento do banco.
- Registrar comando, resultado e limitações; não declarar sucesso de testes não executados.

## Não fazer

- Buscar 100% de cobertura artificial ou testar detalhes privados sem valor comportamental.
- Usar banco de produção, mocks que ocultem a regra testada ou fixtures complexas.
- Implementar módulos futuros apenas para satisfazer esta lista de testes.

## Checklist

- [ ] Casos nominais, limites e falhas críticos da mudança estão cobertos?
- [ ] O teste falharia diante da regressão ou violação de regra?
- [ ] A validação executada corresponde ao escopo e suas limitações foram informadas?
