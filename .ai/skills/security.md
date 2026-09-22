# Segurança

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Somente quando ativa e a tarefa de segurança estiver no escopo da Sprint.
- FUTURO na Sprint 0; as obrigações de segurança de AGENTS.md continuam válidas.

## Responsabilidades

- Aplicar RN01–RN04 e RN53–RN55 de `docs/BUSINESS_RULES.md`.
- Proteger credenciais, identidade, permissões e ownership no backend FastAPI.
- Manter a solução compatível com a autenticação JWT prevista.

## Regras obrigatórias

- Armazenar somente hash de senha com algoritmo apropriado; nunca senha em texto puro.
- Validar assinatura e expiração do JWT; obter identidade autenticada no backend.
- Impedir que STUDENT altere conteúdo administrativo ou se promova a ADMIN pelo payload.
- Verificar dono de ChallengeAttempt antes de alteração, envio ou solicitação de dica.
- Validar entradas externas com Pydantic; separar schemas públicos do model User.
- Excluir password_hash de respostas e senha, tokens e DATABASE_URL de logs.
- Manter secrets no ambiente e .env ignorado; .env.example contém apenas exemplos sem segredos.
- Configurar CORS para origens necessárias ao frontend; CORS não substitui autorização.
- Centralizar erros seguros e impedir stack traces nas respostas de produção.
- Testar acesso anônimo, permissão insuficiente e tentativa pertencente a outro usuário.

## Não fazer

- Confiar em autorização somente no React, em user_id recebido ou em conteúdo JWT não validado.
- Usar segredo hardcoded, devolver password_hash ou registrar credenciais no diagnóstico.
- Adicionar infraestrutura complexa de identidade ou antecipar Auth/JWT na Sprint 0.

## Checklist

- [ ] Credenciais e dados internos estão ausentes de respostas, logs e arquivos versionados?
- [ ] Roles e ownership são verificados no backend?
- [ ] Falhas de autenticação e autorização possuem cobertura pertinente?
