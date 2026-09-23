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

S1-T08 validada com 73 testes passando (`-W error`), PostgreSQL descartável,
`pip check` sem conflitos e `alembic check` sem diferenças no banco local.
Build/typecheck do frontend também passaram. A integração cobre duas contas
com identidades separadas, duplicidade, validação, permissões e remoção de usuário.
Erros 422 não ecoam valores nem nomes de campos extras fornecidos pelo cliente.
O frontend mantém apenas a verificação de conectividade; não há telas de login.
