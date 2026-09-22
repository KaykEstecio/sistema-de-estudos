# CodeTrack — Current Sprint

## Sprint atual

SPRINT 1 — USER + AUTH

Status: aberta para implementação incremental; tarefas de código pendentes.
Fundação concluída e evidências anteriores: [Sprint 0](SPRINT_0.md).

## Objetivo e escopo

Permitir cadastro, login e consulta da identidade autenticada na API.
Seguir ARCHITECTURE.md e RN01–RN04, RN53–RN55 de BUSINESS_RULES.md.

- Model User e migration Alembic em PostgreSQL.
- Schemas Pydantic, repository e services de usuários/autenticação.
- Hash de senha, login, emissão e validação de access token JWT.
- POST /api/v1/auth/register, POST /api/v1/auth/login e GET /api/v1/auth/me.
- Autorização no backend com roles STUDENT e ADMIN.
- Testes críticos e documentação dos contratos e variáveis necessárias.

Cadastro público cria STUDENT, sem permitir promoção a ADMIN pelo payload.
Criar camadas somente quando utilizadas; manter /health independente do banco.

## FUTURO — fora do escopo

Categories, Skills, UserSkill, onboarding funcional, assessment, tracks,
challenges, attempts, evaluation, recommendation e dashboard funcional.
Refresh token, recuperação de senha, confirmação de e-mail, login social,
MFA, painel administrativo e telas de autenticação não fazem parte deste recorte.
O frontend atual continua como verificação de conectividade.

## Sequência de tarefas

Todas pendentes. Executar uma tarefa por vez, validar e registrar o resultado.

### S1-T01 — Model User e migration

Criar model tipado no módulo users e registrar metadados no Alembic.
Usar id, name, email, password_hash, role, onboarding_completed, created_at
 e updated_at conforme a arquitetura. Garantir e-mail único, roles válidas
 e onboarding_completed inicialmente falso.
Validar aplicação e reversão da migration em banco de teste descartável.
Não usar dados de desenvolvimento para testes destrutivos.

### S1-T02 — Schemas e persistência

Definir schemas públicos e repository para cadastro e consulta de usuário.
Não retornar password_hash. Documentar validação de nome/e-mail e duplicidade.

### S1-T03 — Hash de senha

Implementar hash e verificação em core/security.py com biblioteca mantida,
justificando dependência e parâmetros. Não modificar a senha antes do hash.
Testar senha correta, incorreta e armazenamento sem texto puro.

### S1-T04 — Cadastro

Implementar serviços e router simples para POST /api/v1/auth/register.
Retornar 201, tratar duplicidade com 409 e entrada inválida com 422.
Garantir unicidade inclusive diante de concorrência e impedir atribuição pública de ADMIN.

### S1-T05 — Configuração e utilitários JWT

Definir e documentar algoritmo, validade e claims antes de usá-los.
Segredo somente no ambiente; exemplo sem valor real.
Testar assinatura inválida, expiração e claims ausentes/inválidos.

### S1-T06 — Login

Implementar POST /api/v1/auth/login com validação de credenciais e access token.
Documentar entrada e resposta. Falhas retornam 401 sem diferenciar usuário
inexistente de senha errada. Não registrar senha, hash ou token em logs.

### S1-T07 — Identidade e permissões

Implementar dependência de autenticação e GET /api/v1/auth/me.
Validar token e existência do usuário no backend, com resposta pública.
Testar token ausente, inválido, expirado e usuário inexistente.
Validar roles sem criar endpoints administrativos futuros.

### S1-T08 — Integração e documentação

Testar cadastro → login → me em PostgreSQL de teste isolado, duplicidade,
validação, roles e ausência de password_hash nas respostas.
Preservar regressões da Sprint 0 e atualizar instruções e contratos.

## Decisões a registrar durante a implementação

- S1-T01/T02: tipo de identificador, tamanhos e normalização/comparação de e-mail.
- S1-T03/T04: política e limites de senha, algoritmo de hash e biblioteca.
- S1-T05/T06: biblioteca JWT, algoritmo, validade, claims e contrato de login.

Esses detalhes ainda não estão fixados. Documentar decisões justificadas no
arquivo responsável, sem apresentá-las como requisitos anteriores.
Mudanças significativas de arquitetura seguem as regras de AGENTS.md.

## Definition of Done

- [ ] Model User e migration validados em PostgreSQL.
- [ ] E-mail único na persistência, com duplicidade tratada.
- [ ] Senha somente como hash; dados internos ausentes das respostas.
- [ ] Cadastro público cria apenas STUDENT.
- [ ] Login retorna JWT válido; credenciais inválidas retornam 401.
- [ ] Assinatura, expiração e identidade verificadas no backend.
- [ ] GET /api/v1/auth/me retorna somente o usuário autenticado.
- [ ] Autorização e falhas críticas possuem testes.
- [ ] Secrets permanecem no ambiente; exemplos sem credenciais reais.
- [ ] Testes da Sprint e regressões da fundação passam.
- [ ] Contratos, decisões e instruções atualizados.

## Active AI Skills

Carregar somente as pertinentes à tarefa:

- [backend-architecture](../.ai/skills/backend-architecture.md)
- [database-modeling](../.ai/skills/database-modeling.md)
- [api-design](../.ai/skills/api-design.md)
- [security](../.ai/skills/security.md)
- [testing](../.ai/skills/testing.md)
- [debugging](../.ai/skills/debugging.md)
- [documentation](../.ai/skills/documentation.md)

FUTURO — inativas: code-review, learning-evaluation, recommendation-engine,
adaptive-learning e challenge-design. Ativação não amplia o escopo.

## Próxima tarefa

S1-T01 — criar Model User e a migration correspondente.
