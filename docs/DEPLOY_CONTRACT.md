# Sprint 12 — Contrato de deploy

S12-T02, definido em 05/10/2026. Complementa [DEPLOY_PLAN.md](DEPLOY_PLAN.md).
Este contrato define a implementação seguinte; não comprova produção publicada.

## Configuração por serviço

| Serviço | Diretório | Instalação/build | Execução/saída |
| --- | --- | --- | --- |
| Vercel, frontend Vite | frontend | npm ci; npm run build | dist |
| Render, API Python | backend | python -m pip install -r requirements.txt | python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" |
| PostgreSQL | Gerenciado no Render | PostgreSQL 17, mesma região da API | Persistência independente dos serviços |

Runtime Python segue backend/.python-version (3.12); Node 24.x, compatível com
o engine do frontend. Conferir a versão efetiva nos logs de build. Sem --reload
em produção. PORT é fornecida pelo Render, não é configuração do frontend.
Não instalar o backend no projeto Vercel nem executar Vite dev em produção.

| Variável da API | Contrato |
| --- | --- |
| ENVIRONMENT | production |
| CODETRACK_DEBUG | false |
| DATABASE_URL | Segredo do provedor; driver postgresql+psycopg, host e banco obrigatórios |
| JWT_SECRET_KEY | Segredo aleatório próprio do ambiente, no mínimo 32 bytes |
| JWT_ACCESS_TOKEN_MINUTES | 30, dentro do intervalo implementado de 1 a 120 |

Adaptar somente o esquema da URL PostgreSQL fornecida ao driver exigido,
preservando credenciais codificadas e parâmetros. Confirmar TLS/rede conforme
o destino; não imprimir nem versionar a URL. Segredos ficam no Render.
Nenhuma variável VITE_* deve receber segredo. A API exige validar JWTSettings
antes da liberação, pois /health isoladamente não verifica o segredo JWT.

## Roteamento do frontend

Destino externo: origem HTTPS pública da API, sem credenciais, query ou fragmento.
A origem real ainda precisa ser informada; não criar domínio fictício em arquivo
ativo. A S12-T03 deve configurar frontend/vercel.json e validar estas regras:

1. /api/v1 e /api/v1/* encaminham ao mesmo caminho na API, preservando query,
   método, corpo, Authorization e status. Erros da API nunca viram index.html.
2. /health encaminha para /health na API.
3. Arquivos existentes, incluindo /theme.js, /fonts/* e /assets/*, são servidos
   com seu conteúdo e tipo corretos.
4. Rotas da SPA retornam index.html, inclusive acesso direto a /tentativas/:id
   e /diagnostico/:id. O React mantém os controles de sessão existentes.

As chamadas continuam relativas no Axios. Não acrescentar CORS amplo: o navegador
usa a origem Vercel. Autorização continua obrigatória na API, inclusive quando
acessada diretamente no Render.

Definir Cache-Control: no-store para /api/v1 e descendentes e /health no proxy.
Preservar no-store da API e não configurar s-maxage ou cache de respostas privadas.
A cobertura atual de headers varia por router; validar sucessos e erros no destino.
HTML e theme.js devem revalidar; assets com hash podem receber cache imutável.
Validar o comportamento efetivo da CDN, não apenas o JSON de configuração.

## Ambientes e publicação

Desenvolvimento continua com Docker local e portas 5173/8000. QA continua com
banco descartável e portas 4173/8100. Não executar o harness contra produção.
Preview só pode chamar API/banco isolados. Enquanto esse destino não existir,
manter previews desativados; não reutilizar a origem de produção em branches.

Primeira publicação é manual, de SHA identificado com CI Quality aprovada.
Manter auto-deploy desativado até fechar a verificação da primeira release.
Registrar SHA, IDs dos deploys, URLs públicas, revisão Alembic e responsável;
nunca incluir tokens, dados pessoais ou valores de variáveis secretas.

## Migrations e banco

Executar a partir de backend, com ambiente do banco de destino explicitamente
selecionado pelo operador. Primeiro conferir identidade do serviço/banco e backup.

```sh
python -m alembic -c alembic.ini current
python -m alembic -c alembic.ini upgrade head
python -m alembic -c alembic.ini current
python -m alembic -c alembic.ini check
python -m app.database.check
```

Somente prosseguir após cada comando terminar com código zero e a revisão atual
corresponder ao head. Executar uma vez por release, nunca em cada worker.
Usar pre-deploy se o plano contratado oferecer; caso contrário, executar em
ambiente controlado com conectividade ao banco antes da publicação manual.
Uma falha interrompe a release; não repetir às cegas nem usar downgrade automático.

/health é liveness. SELECT 1 verifica conexão, mas não substitui a jornada com
persistência. O banco inicial não ganha conteúdo nem ADMIN automaticamente.
Antes da abertura, definir responsável e procedimento auditável de provisionamento
do ADMIN, categorias, skills, questões e desafios revisados usando os mecanismos
existentes; não introduzir promoção pública de usuários ou dados fictícios.

## Verificação para liberar a release

| Verificação | Evidência exigida |
| --- | --- |
| CI do SHA publicado | Backend complete sem skips, build e testes de navegador aprovados |
| Configuração | Runtime esperado, debug desligado, JWT válido, sem secrets em dist |
| Roteamento | SPA direta/reload funciona; API retorna JSON/status original, não HTML |
| Proxy | GET, POST e PATCH funcionam com Bearer; erros 401/403/404/422 preservados |
| Cache | Respostas autenticadas e erros no-store; nenhuma resposta entre contas reutilizada |
| Jornada | Cadastro/login, perfil, diagnóstico, recomendação, salvar/retomar/enviar, revisão e progresso |
| Persistência | Dados de conta de validação permanecem após reinício da API |
| Isolamento | Segunda conta não lê nem altera tentativa da primeira |
| Interface | Tema claro/escuro, fontes, mobile e navegação profunda sem erro |
| Operação | Responsável, backup/retenção, recuperação e conteúdo mínimo registrados |

Usar contas de validação identificadas e conteúdo revisado, sem dados pessoais
reais. Registrar IDs para limpeza controlada posterior. Não declarar aprovação
de produção com base nos testes locais ou somente em /health.

## Recuperação

Falha de interface: retornar ao deploy frontend anterior compatível com a API.
Falha de API: voltar ao SHA anterior somente se compatível com o schema atual.
Rollback de aplicação não desfaz migration nem restaura dados.

Falha de migration/dados: interromper a release e novas gravações afetadas,
preservar evidências sem segredos, avaliar correção incremental. Se restauração
for necessária, restaurar backup em banco separado, conferir schema e registros,
testar jornada e somente então trocar o destino de forma controlada. Preservar
o banco original para investigação; não apagá-lo como parte da recuperação.

Antes da publicação, registrar retenção, frequência de backup, perda de dados
aceitável e prazo de recuperação com o responsável. Fazer ensaio de restauração
isolado; plano ainda não escolhido não é evidência de backup disponível.

## Pendências externas e limites

Faltam URL pública da API, conta/projetos dos provedores, região, plano/custos,
política de backup e responsável pelo conteúdo/ADMIN. A S12-T03 depende da origem
real; contratação e criação de recursos continuam pendentes dessas definições.
Nenhuma mudança de arquitetura ou funcionalidade de produto é necessária aqui.

Fontes oficiais consultadas em 05/10/2026:
[rewrites Vercel](https://vercel.com/docs/routing/rewrites),
[etapas de deploy Render](https://render.com/docs/deploys),
[porta e serviço web Render](https://render.com/docs/web-services).
Render documenta pre-deploy para serviços pagos; isso não seleciona nem autoriza
um plano. As condições devem ser reconferidas na contratação.
