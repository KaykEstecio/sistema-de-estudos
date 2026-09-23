# CodeTrack — Current Sprint

## Sprint atual

SPRINT 1 — USER + AUTH

Status: concluída; S1-T01 a S1-T08 validadas.
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

Executar uma tarefa por vez, validar e registrar o resultado. Status por tarefa abaixo.

### S1-T01 — Model User e migration

Status: concluída. Model User e migration `0001_create_users` implementados.
Decisões de tipos/defaults registradas na arquitetura; unicidade sem distinção
de caixa registrada na RN01. Nove testes passaram com `-W error`, incluindo
upgrade, defaults ORM/SQL, constraints, downgrade e reaplicação em banco descartável.
Migration aplicada ao banco local; `alembic check` sem diferenças.

Criar model tipado no módulo users e registrar metadados no Alembic.
Usar id, name, email, password_hash, role, onboarding_completed, created_at
 e updated_at conforme a arquitetura. Garantir e-mail único, roles válidas
 e onboarding_completed inicialmente falso.
Validar aplicação e reversão da migration em banco de teste descartável.
Não usar dados de desenvolvimento para testes destrutivos.

### S1-T02 — Schemas e persistência

Status: concluída. UserCreate/UserRead e UserRepository implementados;
normalização registrada na RN01 e contratos na arquitetura. EmailStr utiliza
email-validator para validar formato sem implementar regex própria.
Validação: 18 testes passaram com `-W error`, incluindo PostgreSQL descartável,
consulta por ID/e-mail, rollback, duplicidade e exclusão de credenciais na saída.
`pip check` sem conflitos. Ainda não há endpoint de cadastro ou hash de senha.

Definir schemas públicos e repository para cadastro e consulta de usuário.
Não retornar password_hash. Documentar validação de nome/e-mail e duplicidade.

### S1-T03 — Hash de senha

Status: concluída. core/security.py implementa hash_password e verify_password
com Argon2id/argon2-cffi, salt aleatório e perfil explícito RFC_9106_LOW_MEMORY.
Parâmetros e justificativa registrados na arquitetura. Senhas não são modificadas.
Validação: 25 testes passaram com `-W error`, incluindo PostgreSQL isolado,
senhas corretas/incorretas, salt, espaços, caixa, Unicode, não truncamento
e hashes inválidos. `pip check` sem conflitos.

Implementar hash e verificação em core/security.py com biblioteca mantida,
justificando dependência e parâmetros. Não modificar a senha antes do hash.
Testar senha correta, incorreta e armazenamento sem texto puro.

### S1-T04 — Cadastro

Status: concluída. UserService controla hash/transação e traduz somente a
violação do índice único de e-mail; router retorna 201/409/422. Cadastro aceita
apenas os campos públicos e cria STUDENT. Erros de validação omitem conteúdo
recebido. Política de senha registrada na RN02 e contrato na arquitetura.
Validação: 32 testes passaram com `-W error`, incluindo PostgreSQL descartável,
cadastro HTTP, concorrência real, rollback, campos privilegiados e credenciais
ausentes das respostas. /health continua independente do banco.

Implementar serviços e router simples para POST /api/v1/auth/register.
Retornar 201, tratar duplicidade com 409 e entrada inválida com 422.
Garantir unicidade inclusive diante de concorrência e impedir atribuição pública de ADMIN.

### S1-T05 — Configuração e utilitários JWT

Status: concluída. PyJWT 2.14.0, JWTSettings e core/tokens.py implementados.
HS256 fixo, validade padrão de 30 minutos e claims documentados na arquitetura.
Segredo sem default, protegido por SecretStr; exemplo sem valor real.
Validação: 70 testes passaram com `-W error`, incluindo PostgreSQL isolado e
regressões anteriores. JWT cobre assinatura, algoritmo, expiração, claims,
IDs e configuração inválidos. Login permanece na S1-T06.

Definir e documentar algoritmo, validade e claims antes de usá-los.
Segredo somente no ambiente; exemplo sem valor real.
Testar assinatura inválida, expiração e claims ausentes/inválidos.

### S1-T06 — Login

Status: concluída. AuthService, LoginRequest/TokenResponse e POST /api/v1/auth/login
implementados. Contrato JSON documentado na arquitetura; resposta 200 com JWT,
tipo bearer e validade em segundos. Credenciais incorretas recebem o mesmo 401.
Verificação Argon2 também executada para usuário inexistente.
Validação: 72 testes passaram com `-W error`, incluindo cadastro → login em
PostgreSQL isolado, token válido, normalização, senha preservada, falhas e
ausência de credenciais nos logs capturados. Dependências sem conflitos.

Implementar POST /api/v1/auth/login com validação de credenciais e access token.
Documentar entrada e resposta. Falhas retornam 401 sem diferenciar usuário
inexistente de senha errada. Não registrar senha, hash ou token em logs.

### S1-T07 — Identidade e permissões

Status: concluída. GET /api/v1/auth/me e dependências de autenticação e ADMIN
implementados. AuthService valida token, consulta usuário e aplica a regra de
role; adaptadores HTTP retornam 401/403. Nenhuma rota administrativa publicada.
Validação: 73 testes passaram com `-W error`, incluindo PostgreSQL isolado,
cadastro → login → me, token ausente/inválido/expirado, assinatura incorreta,
usuário inexistente/removido e mudança de role com o mesmo token.

Implementar dependência de autenticação e GET /api/v1/auth/me.
Validar token e existência do usuário no backend, com resposta pública.
Testar token ausente, inválido, expirado e usuário inexistente.
Validar roles sem criar endpoints administrativos futuros.

### S1-T08 — Integração e documentação

Status: concluída. Fluxo cadastro → login → me revisado com contas distintas,
duplicidade concorrente, validação, roles e ausência de hash nas respostas.
Corrigido eco de nomes de campos extras nos erros 422, com regressão coberta.
README atualizado para o estado real e configuração JWT documentada.
Validação final: 73 testes passaram com `-W error`, incluindo cinco testes
PostgreSQL isolados; `pip check` sem conflitos; `alembic check` sem novas
operações; build/typecheck frontend concluído; Docker PostgreSQL healthy.
Valores secretos locais não encontrados em arquivos rastreados ou candidatos
não ignorados. Arquivos .env continuam fora do versionamento.

Testar cadastro → login → me em PostgreSQL de teste isolado, duplicidade,
validação, roles e ausência de password_hash nas respostas.
Preservar regressões da Sprint 0 e atualizar instruções e contratos.

## Decisões a registrar durante a implementação

- S1-T01/T02: tipo de identificador, tamanhos e normalização/comparação de e-mail.
- S1-T03/T04: política e limites de senha, algoritmo de hash e biblioteca.
- S1-T05/T06: biblioteca JWT, algoritmo, validade, claims e contrato de login.

Decisões registradas em BUSINESS_RULES.md e ARCHITECTURE.md ao longo da Sprint.
Mudanças significativas de arquitetura seguem as regras de AGENTS.md.

## Definition of Done

- [x] Model User e migration validados em PostgreSQL.
- [x] E-mail único na persistência, com duplicidade tratada.
- [x] Senha somente como hash; dados internos ausentes das respostas.
- [x] Cadastro público cria apenas STUDENT.
- [x] Login retorna JWT válido; credenciais inválidas retornam 401.
- [x] Assinatura, expiração e identidade verificadas no backend.
- [x] GET /api/v1/auth/me retorna somente o usuário autenticado.
- [x] Autorização e falhas críticas possuem testes.
- [x] Secrets permanecem no ambiente; exemplos sem credenciais reais.
- [x] Testes da Sprint e regressões da fundação passam.
- [x] Contratos, decisões e instruções atualizados.

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

Nenhuma tarefa de implementação pendente na Sprint 1. Próximo passo:
definir o escopo da Sprint 2 a partir da especificação, antes de implementar.
