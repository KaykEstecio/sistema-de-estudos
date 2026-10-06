# Sprint 12 — Deploy inicial

ADIADO em 05/10/2026 por decisão do usuário. Prioridade atual: painel local de
revisão ADMIN, conforme CURRENT_SPRINT.md. Este documento permanece como plano,
sem execução de publicação ou criação de recursos.

Planejamento iniciado em 05/10/2026, após [Sprint 11](SPRINT_11.md).
Esta etapa entrega apenas o recorte; não cria serviços, custos ou publicação.
Preservar Vercel, Render, PostgreSQL e monólito modular.

Em 05/10, usuário priorizou refinamento visual das telas existentes antes do
contrato de deploy. Recorte e validação registrados em CURRENT_SPRINT.md.

## Inventário

- Aplicação funcional e QA local aprovado; GitHub Actions ainda não validado
  remotamente. Há commits locais não publicados na última revisão do Git.
- Frontend usa caminhos relativos /api/v1 e /health. Proxy Vite é local e não
  acompanha dist; ainda não há vercel.json ou configuração Render.
- Backend exige URL postgresql+psycopg. URL fornecida pelo provedor precisa ser
  adaptada explicitamente ao driver existente, preservando parâmetros de conexão.
- Configuração production impede debug=true. JWT exige segredo de pelo menos
  32 bytes; migrations não precisam do segredo JWT.
- /health confirma o processo, não PostgreSQL. Validação de release precisa
  exercitar persistência, não interpretar esse endpoint como saúde do banco.
- Conteúdo e ADMIN não são provisionados automaticamente; não há seed de produção.

## Proposta técnica

Vercel com raiz frontend, npm ci, npm run build e saída dist. Propor rewrites
de /api/v1 e /health para URL HTTPS explícita do Render, antes do fallback SPA
para index.html. Assim, o cliente mantém caminhos relativos e autenticação
existentes. Validar encaminhamento Bearer, status de erro e no-store; não cachear
respostas autenticadas. Não adicionar CORS amplo preventivamente.

Render com raiz backend, instalação por requirements.txt, Python 3.12 e Uvicorn
em 0.0.0.0 na porta fornecida pelo serviço. PostgreSQL no Render, na mesma região
quando disponível, conexão interna e requisitos de TLS conforme o provedor.
Custos, plano, retenção e região devem ser definidos antes de criar recursos.

Migrations explícitas antes de liberar tráfego. Preferir etapa pre-deploy quando
o plano escolhido permitir; se não permitir, definir execução manual controlada.
Não rodar Alembic automaticamente em cada worker e não executar downgrade como
rollback de rotina. Restaurar banco exige backup e procedimento verificados.

Variáveis do backend: DATABASE_URL, JWT_SECRET_KEY, ENVIRONMENT=production,
CODETRACK_DEBUG=false e duração JWT conforme contrato existente. Segredos ficam
somente no provedor; frontend não recebe secrets. URLs públicas são configuração,
não credenciais. Preview não deve escrever no banco de produção.

## Sequência

1. S12-T01 — inventário e recorte neste documento (concluído).
2. S12-T02 — contrato de configuração, roteamento, migrations, validação e
   recuperação concluído em [DEPLOY_CONTRACT.md](DEPLOY_CONTRACT.md), sem criar
   recursos externos. URL pública da API ainda pendente para S12-T03.
3. S12-T03 — implementar apenas arquivos/configuração necessários, com URL
   pública definida e sem secrets versionados; validar tipos/build e rotas.
4. S12-T04 — publicar código no GitHub e conferir CI remota do commit exato.
   Execução remota deve ter evidência; tratar falhas reais antes de release.
5. S12-T05 — preparar recursos e variáveis do provedor após definição de conta,
   plano e custos; migrar banco de destino com procedimento revisado.
6. S12-T06 — publicar e verificar cadastro/login, rota profunda após reload,
   sessão, persistência e jornada com dados de teste isolados no destino.
7. S12-T07 — registrar URLs, evidências, limites e procedimento de recuperação;
   fechar somente com critérios aprovados.

Cada etapa depende da anterior. Continuação do planejamento não significa
aprovação de contratação, uso de conta não identificada ou migração de dados reais.
Pré-requisitos de acesso/custo serão tratados quando necessários, com configuração
concreta para revisão. Não implantar automaticamente ao fazer push nesta etapa.

## Critérios de saída

- CI do commit publicado aprovada, backend completo sem skips, build e browser QA.
- HTTPS, rotas profundas e API encaminhada corretamente; nenhum segredo em bundle.
- Produção sem debug/stack trace exposto; isolamento entre contas validado.
- Migrations até head e persistência verificadas no banco correto.
- Recursos, responsáveis, configuração, conteúdo mínimo e recuperação documentados.
- Backups/retenção e custos conhecidos; não declarar recuperação sem verificá-la.

FUTURO: redesign, painel ADMIN, execução automática, autosave, domínio próprio
obrigatório, infraestrutura distribuída, calibração pedagógica e ensaio de carga.

## Fontes e limites

Documentação oficial consultada em 05/10/2026:
[Vite na Vercel](https://vercel.com/docs/frameworks/frontend/vite),
[rewrites](https://vercel.com/docs/routing/rewrites) e
[deploys Render](https://render.com/docs/deploys).
Compatibilidade/plano devem ser reconferidos antes da configuração real.
Não executados nesta etapa: testes novos, CI remota, migrations ou deploy.
