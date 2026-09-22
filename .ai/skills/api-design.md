# Design da API

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Somente quando ativa e a tarefa de API estiver autorizada na Sprint.
- FUTURO na Sprint 0; o contrato técnico vigente continua sendo GET /health.

## Responsabilidades

- Preservar a API REST com prefixo /api/v1 e contratos de `docs/ARCHITECTURE.md`, seção 11.
- Consultar auth (register/login/me), onboarding (GET/POST/PATCH) e skills (listagem/detalhe/usuário).
- Consultar assessments (criação/detalhe/answers/finish) e challenges (listagem/detalhe).
- Consultar attempts (criação/leitura/rascunho/submit/hint), recommendations e dashboard.

## Regras obrigatórias

- Usar recursos e verbos HTTP documentados; manter as ações submit, hint e finish previstas.
- Separar schemas Pydantic de entrada e saída; nunca serializar password_hash.
- Validar parâmetros e payloads; delegar domínio ao service e autorização ao backend.
- Usar 200 para leitura/resultado, 201 para criação e 204 somente sem corpo.
- Distinguir 400, 401, 403, 404, 409 e 422 conforme a causa; 500 com erro seguro.
- Manter respostas e erros consistentes com os contratos existentes.
- Quando necessária, definir paginação com limites validados e ordenação estável.
- Aplicar apenas filtros autorizados; challenges prevê skill, difficulty, type e completed.
- Preservar /health fora de /api/v1, conforme `docs/CURRENT_SPRINT.md`.

## Não fazer

- Criar verbos redundantes em URLs ou renomear ações documentadas por preferência.
- Colocar regras de negócio no router, retornar 200 para falhas ou inventar endpoints.
- Adicionar paginação, filtros ou dashboard funcional fora da tarefa.

## Checklist

- [ ] O contrato corresponde ao recurso, método e schema documentados?
- [ ] Erros, autorização e ownership estão verificados quando aplicáveis?
- [ ] A resposta exclui dados internos e mantém compatibilidade?
