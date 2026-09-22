# Diagnóstico de falhas

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Quando houver falha reproduzível na stack do CodeTrack e esta skill estiver ativa.
- Investigar apenas componentes existentes e autorizados na Sprint.

## Responsabilidades

- Localizar falhas entre React/Vite/Axios, FastAPI, SQLAlchemy, Alembic, PostgreSQL e Docker.
- Separar sintomas da causa e preservar código funcional.
- Explicar a causa de forma que o desenvolvedor consiga reproduzir o diagnóstico.

## Regras obrigatórias

- Seguir: reproduzir → coletar erro → identificar camada → formular hipótese → testar hipótese → corrigir causa → validar regressão.
- Registrar ação/comando, resultado esperado, resultado observado e ambiente relevante.
- Coletar mensagens e logs mínimos, removendo secrets e dados sensíveis.
- No frontend, verificar URL, resposta HTTP, configuração Vite e tratamento de erro Axios.
- No FastAPI, distinguir roteamento, validação Pydantic, service e persistência.
- No banco, verificar disponibilidade Docker/PostgreSQL, conexão e estado das migrations Alembic.
- Testar uma hipótese por vez com a menor intervenção que produza evidência.
- Aplicar correção na camada responsável e repetir a reprodução original.
- Adicionar teste de regressão para regra crítica ou bug que justifique cobertura.
- Informar o que foi confirmado e o que permanece sem validação.

## Não fazer

- Alterar configurações aleatoriamente, reinstalar dependências sem hipótese ou ocultar exceções.
- Reescrever módulos inteiros para corrigir falhas pequenas.
- Expor .env, DATABASE_URL, tokens ou senhas ao coletar evidências.

## Checklist

- [ ] A reprodução e a hipótese têm evidências verificáveis?
- [ ] A correção resolve a causa na camada responsável?
- [ ] O cenário original foi repetido e a regressão pertinente foi validada?
