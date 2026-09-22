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
Não há criação automática de tabelas, models de domínio ou migrations nesta etapa.
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

Não há migrations de domínio nesta etapa. Validação S0-T09: `current` acessou
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
