# Revisão de código

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Quando a revisão for pertinente e esta skill estiver ativa na Sprint.
- FUTURO na Sprint 0: não está na lista de skills ativas.

## Responsabilidades

- Revisar o diff e contexto relevante, com foco em defeitos concretos.
- Verificar clareza, responsabilidades, duplicação, acoplamento e tipagem.
- Verificar validações, segurança, regras de negócio e testes do CodeTrack.

## Regras obrigatórias

- Comparar escopo com CURRENT_SPRINT e decisões com ARCHITECTURE antes de sugerir mudanças.
- Verificar router/schema/service/repository/model e separação dos cinco services centrais.
- Verificar limites de UserSkill, pesos de ChallengeSkill e histórico/ownership de attempts quando aplicáveis.
- Conferir migrations, respostas sem password_hash e ausência de secrets.
- Relatar arquivo/linha, cenário que dispara o problema, impacto e correção mínima sugerida.
- Classificar BLOCKER: impede execução/entrega ou causa violação crítica comprovada.
- Classificar HIGH: defeito relevante de segurança, integridade ou regra central.
- Classificar MEDIUM: falha localizada de comportamento ou manutenção com impacto demonstrável.
- Classificar LOW: melhoria pequena de clareza ou consistência com ganho concreto.
- Usar severidades apenas para qualidade técnica, nunca para priorização de produto.
- Distinguir fatos de hipóteses e declarar lacunas de validação.

## Não fazer

- Reescrever código automaticamente durante revisão sem solicitação de correção.
- Propor refatoração estética, abstrações preventivas ou funcionalidades futuras.
- Inventar problemas para preencher categorias ou afirmar testes não executados.

## Checklist

- [ ] Cada achado tem evidência, impacto e localização?
- [ ] Foram verificadas as regras críticas realmente afetadas?
- [ ] As sugestões são proporcionais e preservam legibilidade para aprendizado?
