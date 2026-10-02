# CodeTrack — Backend

Diretório do backend Python 3.12+, FastAPI, SQLAlchemy 2 e Alembic,
com PostgreSQL, conforme a arquitetura de monólito modular.

Estado atual: FastAPI com `/health`, configuração de ambiente e infraestrutura
SQLAlchemy configurada, conexão PostgreSQL validada, Alembic configurado
e testes automatizados do `/health` adicionados na S0-T13.
O ponto de entrada é `app.main:app`.

## Preparar o ambiente

Requisito: Python 3.12+ instalado. O ambiente local foi validado com Python 3.12.10;
o arquivo `.python-version` indica a versão 3.12 para ferramentas compatíveis.
Ele não instala nem seleciona o Python no launcher `py` do Windows.

No PowerShell, a partir da raiz do repositório:

```powershell
py -3.12 -m venv backend/.venv
& backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
& backend/.venv/Scripts/python.exe -m pip check
```

No Linux/macOS, a partir da raiz:

```bash
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python -m pip check
```

Os comandos usam diretamente o Python do ambiente, dispensando sua ativação.
`.venv/` é local e está ignorado pelo Git. `requirements.txt` registra versões
exatas das dependências instaladas, incluindo transitivas, para reprodução.

## Validar a inicialização

No PowerShell, a partir da raiz:

```powershell
Push-Location backend
& .venv/Scripts/python.exe -c "import app, fastapi, pydantic, uvicorn; print('Imports OK')"
Pop-Location
```

Validação realizada no Windows: instalação pelo `requirements.txt`, `pip check`
e importação do pacote `app`, FastAPI, Pydantic e Uvicorn.
Os comandos Linux/macOS ainda não foram executados neste projeto.

## Configurar o ambiente

Na raiz do repositório, crie o arquivo local somente se ainda não existir:

```powershell
if (-not (Test-Path backend/.env)) {
    Copy-Item backend/.env.example backend/.env
}
```

No Linux/macOS:

```bash
test -f backend/.env || cp backend/.env.example backend/.env
```

| Variável | Padrão | Uso |
| --- | --- | --- |
| `APP_NAME` | `CodeTrack` | Título da API; não pode ser vazio. |
| `ENVIRONMENT` | `development` | Aceita `development`, `test` ou `production`. |
| `CODETRACK_DEBUG` | `false` | Depuração do FastAPI; proibida em `production`. |
| `DATABASE_URL` | Sem padrão; obrigatória | Conexão PostgreSQL com driver `postgresql+psycopg`. |

`app/core/config.py` usa Pydantic Settings para validar a configuração no início.
Variáveis do processo têm prioridade sobre `backend/.env`; na ausência de ambos,
valem os padrões dos campos opcionais. `DATABASE_URL` deve ser preenchida.
O caminho do arquivo independe do diretório de execução.
Entradas inválidas impedem a inicialização. Reinicie o servidor após editar `.env`.

O `.env` local está ignorado pelo Git; apenas `.env.example` deve ser versionado.
Não adicione credenciais reais ao exemplo. `pydantic-settings` e sua dependência `python-dotenv` foram
adicionados para carregar e validar o ambiente sem implementar um parser próprio.

Validação realizada: padrões sem arquivo, leitura de arquivo temporário,
prioridade do processo, rejeição de valores inválidos e de depuração em produção,
integração com FastAPI e preservação da resposta da função de `/health`.

## Configurar SQLAlchemy

Em `backend/.env`, preencha `DATABASE_URL` com uma URL no formato
`postgresql+psycopg://USUARIO:SENHA@127.0.0.1:PORTA/BANCO`, substituindo os
marcadores pelos valores do `.env` da raiz. Caracteres especiais em usuário e
senha precisam de codificação de URL. Nunca publique ou registre a URL real.
Alterações nas credenciais do Compose não atualizam este arquivo automaticamente.

`app/database/base.py` fornece `Base` para models e migrations futuras.
`app/database/connection.py` configura engine síncrono e `SessionLocal`.
`get_session` fornece uma sessão por uso e garante fechamento mesmo em falhas;
transações não confirmadas são revertidas ao fechar. O commit é explícito,
coordenado pelo service responsável pela operação quando houver regras de domínio.

SQLAlchemy 2 e Psycopg 3 foram adicionados para persistência PostgreSQL;
o pacote binário do driver permite instalação local sem compilação.
Não há criação automática de tabelas. O model User e a migration
`0001_create_users` foram adicionados na S1-T01; aplique `alembic upgrade head`
com os comandos abaixo antes de usar a persistência de usuários.
O engine só conecta quando uma operação exige acesso ao banco; `/health`
continua sem consultar PostgreSQL, embora a configuração precise ser válida.

Validação da S0-T07: driver, metadados sem tabelas, validação e mascaramento
da URL, sessões independentes e fechamento em sucesso/erro, sem conexão antecipada.
O acesso real do backend ao PostgreSQL foi validado na S0-T08.

## Testar a conexão com PostgreSQL

Com Docker e banco em execução, use na raiz do repositório:

```powershell
Push-Location backend
& .venv/Scripts/python.exe -m app.database.check
Pop-Location
```

No Linux/macOS: entre em `backend/` e execute
`.venv/bin/python -m app.database.check`.

O comando usa a configuração e as sessões reais do backend para executar
`SELECT 1`. Não cria tabelas nem altera registros; fecha a sessão e libera o pool.
Sucesso retorna código 0. Falha retorna código 1 e uma mensagem sem URL,
credenciais ou traceback. Confira o código imediatamente após o comando Python
com `$LASTEXITCODE` no PowerShell ou `$?` no shell Linux/macOS.

Validação no Windows: consulta real retornou 1; conexão a porta indisponível
retornou código 1 sem expor credenciais. Os seis testes de configuração passaram.

A configuração de depuração usa exclusivamente `CODETRACK_DEBUG`, evitando
conflitos com o `DEBUG` usado por outras ferramentas. Em arquivos `.env` antigos,
renomeie `DEBUG` para `CODETRACK_DEBUG`. Não é necessário alterar o DEBUG global.
O valor de `CODETRACK_DEBUG` no processo tem prioridade sobre o arquivo local.

Execute somente os testes de configuração a partir da raiz:

```powershell
Push-Location backend
& .venv/Scripts/python.exe -m unittest discover -s tests -p test_config.py -v
Pop-Location
```

Os casos também são executados pelo pytest instalado na S0-T13.
Cobrem conflito com DEBUG externo, precedência do ambiente,
valor padrão, entrada inválida e proteção de produção.

## Migrations com Alembic

O arquivo `alembic.ini` define caminhos relativos à sua própria localização.
`alembic/env.py` usa `Base.metadata` e a configuração de conexão do backend;
a URL não é armazenada no INI. Os módulos de models deverão ser importados
no `env.py` conforme forem implementados, para registrar seus metadados.

Na raiz do repositório, com PostgreSQL disponível:

```powershell
& backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini current
& backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini check
& backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini upgrade head --sql
```

`current` consulta a revisão aplicada; sem revisões, pode não imprimir nada.
`check` verifica diferenças entre schema e metadados sem gerar arquivos de revisão.
`upgrade head --sql` gera SQL sem executá-lo no banco.
No Linux/macOS, substitua o executável por `backend/.venv/bin/python`.

Quando houver alteração de schema autorizada pela Sprint:

```powershell
& backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini revision --autogenerate -m "descrever alteracao"
# Revise upgrade e downgrade do arquivo gerado antes de aplicar.
& backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini upgrade head
```

Validação histórica S0-T09, antes do model User: `current` acessou
o PostgreSQL, `check` não detectou alterações e a geração offline produziu
apenas uma transação vazia. `pip check` passou.

## Executar a aplicação

No PowerShell, a partir da raiz do repositório:

```powershell
& backend/.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

No Linux/macOS, a partir da raiz:

```bash
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Acesse a documentação em <http://127.0.0.1:8000/docs> e o contrato OpenAPI
em <http://127.0.0.1:8000/openapi.json>. Use Ctrl+C para encerrar o servidor.
`--reload` recarrega o processo durante o desenvolvimento local.

## Verificar a saúde da aplicação

Com o servidor em execução, abra <http://127.0.0.1:8000/health> ou execute:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```

`GET /health` retorna HTTP 200 e JSON `{"status":"ok"}`. A rota verifica apenas
se a aplicação responde; não consulta o banco ou serviços externos.
A raiz `/` continua sem rota definida.

Validação HTTP realizada no Windows: status 200, conteúdo `application/json`,
corpo exato, presença no OpenAPI e rejeição de POST com 405.

## Testes automatizados

Modos de qualidade implementados na S11-T03, a partir da raiz:

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests --quality-mode=fast -q -W error
& backend/.venv/Scripts/python.exe -m pytest backend/tests --quality-mode=complete -q -W error
```

`fast` deseleciona testes cuja cadeia de fixtures depende de migrated_database;
não acessa PostgreSQL e não representa validação completa. `complete` exige
CODETRACK_TEST_ADMIN_URL no ambiente, no formato postgresql+psycopg, e banco
disponível com permissão para criar/remover bancos descartáveis. Verifica SELECT 1
antes dos testes, com timeout de conexão/consulta, sem expor credenciais.
Qualquer skip torna a execução completa reprovada. Não carrega .env automaticamente
nem inicia Docker. Configure o ambiente local e inicie `docker compose up -d db --wait`
quando usar o PostgreSQL de desenvolvimento como servidor dos bancos descartáveis.
Nunca use servidor de produção para os testes.

Para carregar apenas a URL local já configurada sem imprimi-la, use o Python do
ambiente (python-dotenv já é dependência), a partir da raiz:

```powershell
@'
import os
from dotenv import dotenv_values
import pytest
os.environ['CODETRACK_TEST_ADMIN_URL'] = dotenv_values('backend/.env')['DATABASE_URL']
raise SystemExit(pytest.main(['backend/tests', '--quality-mode=complete', '-q', '-W', 'error']))
'@ | & backend/.venv/Scripts/python.exe -
```

Somente bancos com nomes aleatórios gerados pela fixture são migrados/removidos.
Histórico de resultados abaixo pertence às etapas antigas; contrato vigente em
`docs/QUALITY_CONTRACT.md`. Execução sem --quality-mode continua compatível com
o comportamento anterior de integração opt-in:

Na raiz do repositório, após instalar `backend/requirements.txt`:

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests -q
```

No Linux/macOS, use `backend/.venv/bin/python -m pytest backend/tests -q`.
Também é possível executar `python -m pytest` dentro de `backend/`, usando
o Python do ambiente virtual. A configuração está em `backend/pytest.ini`.

Os testes HTTP usam AsyncClient e ASGITransport do HTTPX, com o plugin AnyIO
do pytest em asyncio, sem iniciar Uvicorn ou exigir Docker. O contexto de
lifespan da aplicação é executado explicitamente para inicialização e encerramento.
O teste de `/health` ignora o `.env` local e bloqueia conexões Psycopg para
garantir que o endpoint continua independente do banco. Verifica status 200,
JSON exato, tipo de conteúdo e rejeição de POST com 405.

Validação após correção dos avisos: 8 testes passaram (6 de configuração e 2 HTTP)
com `-W error`, e `pip check` passou. A troca do TestClient pelo transporte ASGI
removeu o uso das interfaces depreciadas, sem filtros para ocultar avisos.

Para validar também a ausência de avisos:

```powershell
& backend/.venv/Scripts/python.exe -m pytest backend/tests -q -W error
```

Consulte [a Sprint atual](../docs/CURRENT_SPRINT.md) antes de implementar.

## Teste de integração da migration User

O teste `tests/test_user_migration.py` é opt-in. Defina `CODETRACK_TEST_ADMIN_URL`
no ambiente local com uma conexão PostgreSQL de teste cujo usuário possa criar
e remover bancos. Não publique o valor. Execute o mesmo comando pytest acima.
Sem essa variável, o teste é pulado e os testes independentes continuam rodando.

O teste cria um banco novo `codetrack_test_<uuid>`, aplica a migration, verifica
defaults/constraints, reverte e reaplica, e remove somente esse banco criado
pelo próprio teste. O banco da conexão administrativa não é usado para tabelas de teste.
Validação S1-T01: 9 testes passaram com `-W error`, incluindo integração PostgreSQL.
Banco local atualizado para `0001_create_users`; `alembic check` sem diferenças.

Na S1-T02, a integração também verifica UserRepository (consulta por ID/e-mail,
duplicidade e rollback sem commit implícito). Testes de schemas verificam
normalização, campos inválidos/privilegiados, preservação da senha e resposta
sem hash. Resultado da S1-T02 com PostgreSQL de teste: 18 testes passaram.
EmailStr requer a dependência email-validator, adicionada ao requirements.txt.

## Hash de senhas

`app/core/security.py` oferece hash_password e verify_password com argon2-cffi.
Argon2id usa salt aleatório por hash; parâmetros estão documentados na arquitetura.
As funções não normalizam nem truncam a senha e não fazem persistência.
O endpoint de cadastro e sua política inicial de senha foram implementados na S1-T04.

Resultado S1-T03: 25 testes passaram com `-W error`, incluindo integração
PostgreSQL. Sem CODETRACK_TEST_ADMIN_URL, 24 testes rodam e 1 é pulado.

## Cadastro (S1-T04)

`POST /api/v1/auth/register` recebe name, email e password em JSON.
Senha: 15 a 128 caracteres, preservando espaços e Unicode. Retorna 201 com
usuário STUDENT, onboarding_completed=false e sem credenciais. E-mail duplicado
retorna 409; entrada inválida ou campos extras retornam 422 sem ecoar valores.
Login e JWT foram implementados nas S1-T05/S1-T06.

Resultado S1-T04: 32 testes passaram com `-W error`. A fixture em conftest.py
cria bancos descartáveis também para cadastro HTTP e concorrência. Sem
CODETRACK_TEST_ADMIN_URL, os três testes PostgreSQL são pulados.

## Utilitários JWT (S1-T05)

`app/core/tokens.py` fornece create_access_token(user_id, settings) e
decode_access_token(token, settings), que retorna o ID validado ou levanta
InvalidAccessToken com mensagem genérica. Use JWTSettings de core/config.py.
Login usa esses utilitários desde a S1-T06; autenticação de rotas desde S1-T07.

Configure JWT_SECRET_KEY no ambiente ou backend/.env com segredo aleatório de
pelo menos 32 bytes. O arquivo .env.example mantém o valor vazio. Para gerar
diretamente no arquivo local sem imprimir o segredo, execute da raiz:

```powershell
& backend/.venv/Scripts/python.exe -c "import secrets; from dotenv import set_key; set_key('backend/.env', 'JWT_SECRET_KEY', secrets.token_urlsafe(32))"
```

Esse comando substitui a chave anterior, invalidando tokens emitidos com ela.
JWT_ACCESS_TOKEN_MINUTES é opcional (padrão 30, intervalo 1–120).
Algoritmo, emissor, destinatário e claims estão definidos na arquitetura.
Não compartilhe o .env nem tokens reais. Migrations e /health não usam JWTSettings.

Resultado S1-T05: 70 testes passaram com `-W error`, incluindo os três testes
PostgreSQL. Testes JWT usam segredos efêmeros e não dependem do .env local.

## Login (S1-T06)

`POST /api/v1/auth/login` recebe JSON com email e password. Retorna 200 com
access_token, token_type="bearer" e expires_in (segundos). JWT_SECRET_KEY deve
estar configurada conforme a seção anterior. A resposta impede armazenamento
em cache. Não use credenciais reais em exemplos, logs ou arquivos versionados.

E-mail inexistente e senha incorreta retornam o mesmo 401; entrada inválida ou
campos extras retornam 422. A senha não sofre trim ou normalização. Login aceita
1–128 caracteres; cadastro continua exigindo 15–128.

Validação S1-T06: 72 testes passaram com `-W error`, incluindo quatro testes
PostgreSQL opt-in. Sem CODETRACK_TEST_ADMIN_URL, esses quatro são pulados.

## Identidade e permissões (S1-T07)

`GET /api/v1/auth/me` recebe Authorization: Bearer <access_token> e retorna
somente os campos públicos do usuário autenticado. Token ausente, inválido,
expirado ou usuário removido/inexistente retornam 401. Role é consultada no
banco a cada requisição; nunca depende de autorização enviada pelo frontend.

get_current_user e require_admin ficam em users/dependencies.py. A regra de
ADMIN fica em AuthService; STUDENT recebe 403 quando essa permissão é exigida.
Não há rota administrativa pública nesta Sprint.

Validação S1-T07: 73 testes passaram com `-W error`, incluindo cinco testes
PostgreSQL opt-in. Sem CODETRACK_TEST_ADMIN_URL, esses cinco são pulados.

## Fechamento da Sprint 1

Histórico de validação da Sprint 1; estado mais recente na seção Sprint 2 abaixo.

S1-T08 validada com 73 testes passando (`-W error`), PostgreSQL descartável,
`pip check` sem conflitos e `alembic check` sem diferenças no banco local.
Build/typecheck do frontend também passaram. A integração cobre duas contas
com identidades separadas, duplicidade, validação, permissões e remoção de usuário.
Erros 422 não ecoam valores nem nomes de campos extras fornecidos pelo cliente.
O frontend mantém apenas a verificação de conectividade; não há telas de login.

## Sprint 2 — persistência do catálogo

Migration 0002_create_catalog adiciona categories e skills, com vínculo obrigatório,
restrição de exclusão da categoria referenciada, slugs únicos/validados e ativação
padrão. Downgrade desta revisão remove apenas catálogo, preservando users.
Não há seed nem endpoints de catálogo nesta etapa.

S2-T02: 74 testes passaram com `-W error`, incluindo seis testes PostgreSQL
opt-in. Migration aplicada ao banco local; alembic check e pip check passaram.

Nesta validação, o .venv original estava em Python 3.14 com pydantic_core
incompatível. Foi preservado, e um ambiente separado Python 3.12.10 foi criado:

```powershell
py -3.12 -m venv backend/.validation/.venv
& backend/.validation/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
& backend/.validation/.venv/Scripts/python.exe -m pytest backend/tests -q -W error
```

Configure CODETRACK_TEST_ADMIN_URL para incluir os seis testes de banco.
Correção em 24/09/2026: backend/.venv recriado com Python 3.12.10 e as versões
fixadas em requirements.txt. O ambiente incompatível foi preservado em
backend/.validation/backup-<data-hora>/.venv, ignorado pelo Git. Não é mais
necessário usar o ambiente alternativo: os comandos normais deste guia voltaram
a funcionar. Imports nativos, 74 testes com `-W error`, pip check e alembic check
passaram no .venv principal. Se houver terminal com ambiente antigo ativado,
feche-o e abra outro; no editor, selecione backend/.venv/Scripts/python.exe.

Ao recriar ambientes, use explicitamente `py -3.12 -m venv` em diretório novo;
não reutilize pacotes binários de um ambiente criado com outra versão de Python.

### Schemas e repositories do catálogo (S2-T03)

Módulos categories/skills possuem contratos de criação, PATCH, leitura e páginas.
PATCH preserva campos omitidos e aceita null somente para limpar description.
Repositories recebem dados validados, fazem flush e deixam commit/rollback ao
service. Consultas usam filtros, contagem e paginação no banco com ordem por ID.
Ainda não há rotas de catálogo ou autorização aplicada a essas consultas.

Validação: 108 testes passaram com `-W error` no backend/.venv principal,
incluindo sete testes PostgreSQL opt-in. Cobertura inclui limites de entrada,
normalização, campos extras, filtros de ativos/inativos, rollback de criação e
edição, falha de unicidade e leitura após commit em nova sessão.

### Consulta autenticada do catálogo (S2-T04)

GET /api/v1/categories, /categories/{id}, /skills e /skills/{id}, todos sob
o prefixo /api/v1, exigem Authorization: Bearer <token>. Listagens aceitam
limit (1–100, padrão 20) e offset (>=0); retornam items/limit/offset/total.
Skills também aceita category_id e is_active. STUDENT vê somente ativas;
is_active=false retorna 403 e detalhe inativo retorna 404. ADMIN vê ambas.
Categorias vazias permanecem visíveis. Parâmetros desconhecidos retornam 422.
POST/PATCH do catálogo implementados na S2-T05, conforme seção abaixo.

Validação: 109 testes passaram com `-W error`, incluindo oito testes PostgreSQL
opt-in, consulta HTTP real, visibilidade e regressões de autenticação.

### Manutenção administrativa (S2-T05)

POST /api/v1/categories e /api/v1/skills criam recursos (201); PATCH dos mesmos
caminhos com /{id} edita parcialmente (200). Exigem ADMIN; anônimo recebe 401
e STUDENT 403. Contratos de campos estão em docs/ARCHITECTURE.md.
Slug duplicado retorna 409, categoria/alvo inexistente 404 e entrada inválida
422. Falhas desfazem a transação. is_active permite desativar/reativar skills;
description=null limpa a descrição. Não há DELETE ou criação pública de ADMIN.

Validação S2-T05: 111 testes passaram com `-W error`, incluindo dez testes
PostgreSQL opt-in e disputa simultânea de slugs em ambos os recursos.

### Preparar ADMIN local para desenvolvimento

Cadastre sua conta por POST /api/v1/auth/register e guarde o id retornado.
O cadastro continua criando STUDENT. No banco Docker local, promova somente
essa conta pelo procedimento abaixo, em PowerShell na raiz do repositório.
Substitua `123` pelo id da conta escolhida. Não há senha ou token no comando.

```powershell
$env:CODETRACK_LOCAL_ADMIN_ID = '123'
Push-Location backend
try {
@'
import os
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import Settings
from app.database.connection import SessionLocal, engine
from app.modules.users.models import User, UserRole

settings = Settings()
if settings.environment != "development" or engine.url.host not in {"localhost", "127.0.0.1", "::1"}:
    raise SystemExit("Use somente o banco local em development.")
user_id = int(os.environ["CODETRACK_LOCAL_ADMIN_ID"])
if not 1 <= user_id <= 2147483647:
    raise SystemExit("ID invalido.")
try:
    with SessionLocal.begin() as session:
        user = session.scalar(select(User).where(User.id == user_id).with_for_update())
        if user is None:
            raise SystemExit("Usuario nao encontrado; nenhuma alteracao.")
        user.role = UserRole.ADMIN
    print("Role ADMIN aplicada ao ID informado.")
except SQLAlchemyError:
    raise SystemExit("Falha no banco; transacao revertida.") from None
finally:
    engine.dispose()
'@ | & .venv/Scripts/python.exe -
} finally {
    Pop-Location
    Remove-Item Env:CODETRACK_LOCAL_ADMIN_ID
}
```

Confirme a role por GET /api/v1/auth/me. Faça login se ainda não tiver token.
A mudança de role vale no próximo acesso; não cria uma conta ou senha fixa.
Para reverter, execute o mesmo procedimento trocando a atribuição por
`user.role = UserRole.STUDENT`. Este procedimento é exclusivamente local;
não existe endpoint de promoção de usuários. A promoção de uma conta real não
foi executada durante a validação automática; testes usam bancos descartáveis.

### Fechamento da Sprint 2

S2-T06 concluída: 111 testes passaram com `-W error`, incluindo dez testes
PostgreSQL opt-in. Integração cobre criação, edição, desativação/reativação,
visibilidade STUDENT/ADMIN, duplicidade concorrente, rollback e autenticação.
Build/typecheck frontend, pip check e alembic check passaram. Procedimento de
ADMIN local teve sintaxe validada; nenhuma conta real foi promovida nos testes.
O frontend continua apenas com a verificação de conectividade.

## Sprint 3 — persistência do onboarding

S3-T02 adiciona User.declared_experience, user_interests e user_goals pela
migration 0003_create_onboarding. Há FK RESTRICT, interesse único por usuário e
categoria, prioridade positiva e um único objetivo principal por usuário.
Experiência declarada aceita as cinco opções documentadas na arquitetura;
onboarding_completed=true exige experiência não nula.

Upgrade redefine indicadores anteriores de conclusão para false, pois ainda
não existiam dados de onboarding. Downgrade remove os dados novos e limpa
onboarding_completed, preservando usuários e catálogo. Testado em banco isolado.
Os endpoints do onboarding ainda não estão disponíveis.

Validação S3-T02: 112 testes passaram com `-W error`, incluindo onze testes
PostgreSQL opt-in; migration aplicada localmente, alembic check sem diferenças
e pip check sem conflitos. Nenhuma dependência adicionada.

### Schemas e repository do onboarding (S3-T03)

OnboardingCreate, OnboardingUpdate, OnboardingRead e PrimaryGoal validam os
contratos definidos na arquitetura. PATCH preserva campos omitidos, rejeita
null no primeiro nível e substitui o conteúdo do objetivo quando fornecido.
Interesses exigem IDs estritos, distintos e de 1 a 20 categorias.

OnboardingRepository mantém consultas por usuário, busca de categorias em lote,
substituição de interesses e criação/edição do objetivo principal. Não faz
commit: o service controla a transação. get_user_locked usa releitura do objeto
em cache e lock exclusivo para escrita ou compartilhado para leitura.

Validação S3-T03: 136 testes passaram com `-W error`, incluindo doze testes
PostgreSQL opt-in. Cobertos isolamento entre usuários, rollback, preservação
de id/created_at do objetivo e bloqueio concorrente. Endpoints ainda pendentes.

### Fluxo HTTP de onboarding (S3-T04)

GET/POST/PATCH /api/v1/onboarding exigem Bearer token e operam somente o perfil
do usuário autenticado. GET antes da conclusão retorna perfil vazio; POST grava
perfil completo e conclusão atomicamente (201). POST repetido ou PATCH antes da
conclusão retorna 409. PATCH após conclusão preserva campos omitidos (200).
Categoria ausente retorna 404; entrada/query inválida 422. Respostas não são
armazenáveis em cache. /auth/me reflete onboarding_completed após commit.

Corpos e regras detalhados na seção Onboarding de docs/ARCHITECTURE.md.
Não existe rascunho, seleção de outro usuário ou inicialização de score.
Validação S3-T04: 138 testes passaram com `-W error`, incluindo quatorze testes
PostgreSQL opt-in, disputa real de conclusão e rollback após falha parcial.

### Fechamento da Sprint 3

S3-T05 concluída: 139 testes passaram com `-W error`, incluindo quinze testes
PostgreSQL opt-in. Fluxo cadastro/login/onboarding/edição/me validado com duas
contas independentes, incluindo ADMIN no próprio perfil. Tokens identificam
ownership; user_id externo é rejeitado. Autoavaliação não inicializa desempenho.
Regressões de catálogo/autenticação, build/typecheck frontend, pip check e
alembic check passaram. Frontend ainda não possui tela de onboarding.

## Sprint 4 — persistência do diagnóstico

S4-T02: Assessment, AssessmentQuestion, AssessmentItem e AssessmentResult
implementados com migration 0004_create_assessments. Provas têm uma única
instância aberta por usuário; itens guardam cópia independente de texto,
alternativas e gabarito. Resultados são únicos por prova/skill e possuem limites
de score, confidence e contagens. Não há UserSkill, seed ou endpoints nesta etapa.
Formato das alternativas e completude de uma prova serão validados pelas
camadas de entrada/service; a persistência não executa avaliação.

Validação: 140 testes passaram com `-W error`, incluindo dezesseis testes
PostgreSQL opt-in. Downgrade/reaplicação preservam usuários, catálogo e onboarding.
Migration aplicada ao banco local; alembic check e pip check passaram.

### Schemas e repository do diagnóstico (S4-T03)

AssessmentCreate e AnswerCreate rejeitam IDs inválidos, skills repetidas,
ownership e notas fornecidos pelo cliente. QuestionCreate é exclusivo de autoria
privada e exige alternativas A/B/C/D. AssessmentItemRead não contém correct_option;
AssessmentRead reúne somente itens e resultados públicos.

AssessmentRepository consulta provas por usuário com lock/releitura, skills
ativas entre interesses e questões ativas em ordem de ID. Cria snapshots
independentes e grava respostas/resultados com flush, sem commit implícito.
Regras de ciclo de vida e autorização serão aplicadas pelo service na S4-T04.

Validação S4-T03: 155 testes passaram com `-W error`, incluindo dezessete testes
PostgreSQL opt-in. Cobertos entrada, saída sem gabarito, consultas por usuário,
filtros e rollback de criação, resposta e finalização. Ainda não há endpoints.

### Início e respostas do diagnóstico (S4-T04)

POST /api/v1/assessments recebe skill_ids (1–3, distintos); exige onboarding
concluído, skills ativas nos interesses e três questões ativas por skill.
GET /api/v1/assessments/{id} retorna apenas a prova do usuário autenticado.
POST /api/v1/assessments/{id}/answers recebe item_id/selected_option (A/B/C/D)
e retorna o item público atualizado. Reenvio substitui a escolha enquanto aberta.
Todas as rotas exigem Bearer token e omitem gabarito; respostas usam no-store.

Conteúdo insuficiente ou estado incompatível retorna 409; prova de terceiro e
item indisponível retornam 404. Não há seed automático, importador ou /finish
nesta etapa. As questões dos testes são artificiais e ficam em bancos descartáveis.
Validação: 157 testes passaram com `-W error`, incluindo dezenove testes
PostgreSQL opt-in e concorrência real de criação e envio de respostas.

### Finalização do diagnóstico (S4-T05)

POST /api/v1/assessments/{id}/finish, sem corpo ou query, exige Bearer token do
dono da prova. Retorna 409 se houver respostas faltantes; sucesso retorna 200
com prova concluída e resultados por skill. Repetição retorna os mesmos dados
persistidos, sem duplicar resultados ou reavaliar. Terceiros recebem 404.

Score é acertos/questões × 1000 com arredondamento metade para cima. Confidence
é 0 por ausência de calibração, não uma avaliação negativa de aprendizagem.
Correção usa snapshots privados; gabaritos não aparecem nas respostas. UserSkill
não é criado nem alterado. Respostas posteriores à conclusão retornam 409;
outro diagnóstico pode ser iniciado após concluir o anterior.

Validação S4-T05: 165 testes passaram com `-W error`, incluindo vinte testes
PostgreSQL opt-in. Cobertos cálculo, idempotência, finalização concorrente e
rollback após gravação parcial. Importador e integração final aguardam S4-T06.

### Importação local e fechamento (S4-T06)

O importador recebe um arquivo UTF-8 com uma lista JSON não vazia de questões
revisadas. Cada objeto segue QuestionCreate: `code` (slug único), `skill_id`
(ID existente), `prompt`, `options` (objeto com textos A, B, C e D),
`correct_option` (A/B/C/D) e `is_active` (booleano, padrão true).
Campos extras são rejeitados. Textos de alternativas têm até 1000 caracteres,
enunciados até 4000 e códigos até 120.

Com banco iniciado e migrations aplicadas, execute da raiz no PowerShell,
substituindo o caminho pelo arquivo revisado:

```powershell
Push-Location backend
try {
    & .venv/Scripts/python.exe -m app.modules.assessments.import_questions 'C:\conteudo\questoes-revisadas.json'
} finally {
    Pop-Location
}
```

O comando usa a configuração do backend e aceita somente `ENVIRONMENT=development`
com host localhost, 127.0.0.1 ou ::1. Importa apenas questões novas em uma única
transação: código repetido no lote ou no banco, skill inexistente ou falha de
gravação rejeitam o lote inteiro. Não atualiza nem sobrescreve conteúdo existente.
Sucesso retorna código de saída 0 e quantidade importada; falha retorna 1 sem
imprimir gabarito, credenciais ou detalhes internos.

Para iniciar um diagnóstico, cada skill escolhida precisa de três questões
ativas. Sem conteúdo suficiente a API retorna 409. Não há seed automático:
nenhum banco pedagógico revisado foi importado durante o desenvolvimento.
Fixtures dos testes são sintéticas e não comprovam validade pedagógica.
O diagnóstico permanece provisório, com confidence=0 e sem inicializar UserSkill.

Validação final: 166 testes passaram com `-W error`, incluindo 21 testes em
PostgreSQL descartável. Cobertos importação via CLI, duplicidade, rollback e
cadastro → onboarding → diagnóstico → respostas → resultados entre duas contas.
Build/typecheck do frontend, pip check e alembic check também passaram.

## Sprint 5 — persistência de desafios (S5-T02)

Challenge e ChallengeSkill implementados na migration 0005_create_challenges.
Desafios começam inativos; vínculos usam chave composta e FKs RESTRICT.
O banco valida enums, dificuldade 0–1000, duração 1–1440, limites de textos e
peso individual 1–100. Soma dos pesos e publicação serão validadas pelo service.
Não há module_id, hints, tentativas, seed ou endpoints de desafios nesta etapa.

Validação: 167 testes passaram com `-W error`, incluindo 22 testes PostgreSQL
isolados. Upgrade/downgrade/reaplicação preservaram dados anteriores; limites,
unicidade de vínculos e proteção contra exclusão de referências foram testados.
Migration aplicada ao banco local; alembic check e pip check aprovados.

### Schemas e repository de desafios (S5-T03)

Contratos de criação, PATCH, filtros e respostas públicas implementados.
Campos numéricos/booleanos do JSON são estritos; PATCH distingue omissão de null.
Repository aplica visibilidade e filtros no banco antes de paginação e carrega
vínculos em lote. Escritas fazem flush sem commit; locks disponíveis para o service.
Soma dos pesos, publicação, autorização e rotas aguardam S5-T04.

Validação: 189 testes passaram com `-W error`, incluindo 23 testes PostgreSQL
isolados. Cobertos limites, skills repetidas/inativas, filtros combinados,
paginação, substituição dos vínculos e rollback de criação/edição.
Alembic sem diferenças; nenhuma migration adicional necessária.

### API de desafios (S5-T04)

GET /api/v1/challenges e GET /api/v1/challenges/{id} exigem Bearer token.
POST e PATCH no mesmo recurso são exclusivos de ADMIN. Payloads e filtros estão
no [contrato](../docs/CHALLENGE_CONTRACT.md). Desafios começam inativos; publicar
exige is_active=true, pesos somando 100 e todas as skills ativas. Nenhum conteúdo
pedagógico é criado automaticamente.

STUDENT vê apenas desafios ativos com todas as skills ativas. ADMIN consulta
também os demais. Escritas validam o estado final e revertem integralmente em
caso de erro. PATCH concorrente usa lock/releitura, preservando campos omitidos.
Não há tentativas, correção, hints ou atualização de desempenho nesta etapa.

Validação: 192 testes passaram com `-W error`, incluindo 26 testes PostgreSQL
isolados. Cobertos permissões, filtros HTTP, publicação, rollback após flush,
edições concorrentes e publicação durante desativação de skill. Alembic sem
diferenças. Integração final e build da Sprint aguardam S5-T05.

### Validar o catálogo localmente

Com PostgreSQL, migrations e API iniciados conforme o README da raiz:

1. Abra http://127.0.0.1:8000/docs. Faça login com uma conta ADMIN existente
   e use o access_token no botão Authorize. A preparação local de ADMIN está
   documentada acima; cadastro público não concede essa role.
2. Consulte/crie uma categoria e uma skill ativa pelos endpoints administrativos.
3. Envie POST /api/v1/challenges com o exemplo do
   [contrato](../docs/CHALLENGE_CONTRACT.md), substituindo skill_id pelo ID real.
   O exemplo é estrutural: revise o conteúdo antes de utilizá-lo com alunos.
4. Confira o detalhe retornado e publique com PATCH /api/v1/challenges/{id},
   corpo `{"is_active": true}`. Os pesos precisam somar 100.
5. Autentique uma conta STUDENT e consulte listagem/detalhe. A conta pode ler,
   mas não criar nem editar desafios. Desafios inativos retornam 404 no detalhe.
6. Para conferir visibilidade, como ADMIN desative a skill vinculada e consulte
   novamente como STUDENT: o desafio fica oculto. Reative a skill para restaurar
   a visibilidade sem alterar a publicação do desafio.

Os testes automatizados usam bancos descartáveis e conteúdo sintético. Não há
banco pedagógico revisado provisionado, tela de desafios ou execução de soluções.

Fechamento S5-T05: 192 testes passaram com `-W error`, incluindo 26 testes em
PostgreSQL isolado. O fluxo integrado percorre cadastro/login, onboarding,
assessment e publicação/consulta de desafios com ADMIN e STUDENT. Desativar e
reativar a skill altera a visibilidade sem modificar diagnóstico ou perfil.
Build/typecheck frontend, pip check, alembic check e links locais aprovados.

## Sprint 6 — persistência de tentativas (S6-T02)

ChallengeAttempt implementado na migration 0006_create_attempts, com snapshot
JSONB, resposta textual, datas e estados IN_PROGRESS/SUBMITTED. Uma única tentativa
aberta por usuário/desafio e numeração única; FKs RESTRICT preservam referências.
Não há eventos, contadores de avaliação ou endpoints de tentativas nesta etapa.

Validação: 193 testes passaram com `-W error`, incluindo 27 testes PostgreSQL
isolados. Cobertos constraints, tamanho da resposta, snapshot independente,
histórico e downgrade/reaplicação. Migration aplicada localmente; alembic check
sem diferenças e pip check aprovado. Ownership e transições aguardam o service.

### Schemas e repository de tentativas (S6-T03)

AttemptDraft aceita somente draft_answer textual, preservando espaços e quebras
de linha. ChallengeSnapshot valida o contexto completo, skills distintas e pesos
somando 100. AttemptRead omite user_id e usa datas com fuso.
Repository filtra consultas por dono, oferece locks/releitura e grava sem commit.
Service e rotas ainda não estão disponíveis; regras de transição não são aplicadas
pelo repository.

Validação: 201 testes passaram com `-W error`, incluindo 28 testes PostgreSQL
isolados. Cobertos limites, campos extras, snapshot independente, isolamento e
rollback de criação/rascunho/submissão. Alembic sem diferenças.

### Início, retomada e rascunho (S6-T04)

POST /api/v1/challenges/{id}/attempts, sem corpo, retorna 201 para nova tentativa
ou 200 para retomada da aberta. GET /api/v1/attempts/{id} consulta; PATCH recebe
somente draft_answer. Todas exigem Bearer token do dono, inclusive para ADMIN,
e rejeitam query parameters. Respostas usam no-store.

Novo início exige desafio e skills ativos. Tentativas existentes preservam o
snapshot e continuam acessíveis após edição/desativação do catálogo. Rascunho
vazio limpa a resposta; reenviar texto idêntico não altera last_activity_at.
PATCH em tentativa submetida retorna 409; /submit será implementado na S6-T05.

Validação: 203 testes passaram com `-W error`, incluindo 30 testes PostgreSQL
isolados. Cobertos ownership, HTTP, retomada, snapshot, início concorrente e
rollback após flush. Alembic sem diferenças e pip check aprovado.

### Submissão de tentativas (S6-T05)

POST /api/v1/attempts/{id}/submit exige token do dono e não aceita corpo ou query.
Submete o último rascunho salvo, exigindo texto não branco. Retorna 200 com estado
SUBMITTED e datas persistidas. Reenvio retorna os mesmos dados; PATCH posterior
retorna 409. Não há avaliação ou indicação de aprovação.

Após submissão, novo POST /api/v1/challenges/{id}/attempts cria outra tentativa
se o catálogo estiver disponível, incrementando o número e copiando o contexto
atual. A tentativa anterior permanece consultável e inalterada.

Validação: 206 testes passaram com `-W error`, incluindo 33 testes PostgreSQL
isolados. Cobertos resposta vazia, terceiros, reenvio, nova tentativa, rollback
e concorrência de submissão/salvamento. Alembic sem diferenças.

### Validar tentativas localmente

Com API e banco iniciados e um desafio publicado, use /docs autenticado como
STUDENT. Não é necessário concluir onboarding ou assessment para este fluxo.

1. Envie POST /api/v1/challenges/{id}/attempts sem corpo. Guarde o id retornado.
2. Salve com PATCH /api/v1/attempts/{id}, por exemplo
   `{"draft_answer": "Minha resposta"}`. Espaços e quebras de linha são preservados.
3. Repita o início para retomar: retorna 200 e a mesma tentativa aberta.
4. Envie POST /api/v1/attempts/{id}/submit sem corpo. O estado passa a SUBMITTED;
   reenvio mantém o resultado, e novas edições retornam 409.
5. Inicie novamente no desafio disponível: uma nova tentativa recebe o próximo
   número. GET pelo ID anterior continua retornando a resposta e o contexto salvos.

Outra conta, inclusive ADMIN, recebe 404 ao acessar a tentativa. Edições ou
desativação do desafio não alteram o contexto de uma tentativa existente.
Submissão registra a resposta, sem executar código, avaliar ou atualizar skills.
Não há tela de resolução ou conteúdo pedagógico revisado provisionado.

Fechamento S6-T06: 206 testes passaram com `-W error`, incluindo 33 testes
PostgreSQL isolados. Fluxo integrado completo preserva histórico, perfil e
assessment, inclusive após edição/desativação do catálogo. Build/typecheck,
pip check, alembic check, links locais e diff aprovados.
