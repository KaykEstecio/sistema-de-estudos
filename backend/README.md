# CodeTrack — Backend

Diretório do backend Python 3.12+, FastAPI, SQLAlchemy 2 e Alembic,
com PostgreSQL, conforme a arquitetura de monólito modular.

Estado atual: aplicação FastAPI com `/health` e configuração de ambiente
implementada na S0-T05. O ponto de entrada é `app.main:app`.

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
| `DEBUG` | `false` | Depuração do FastAPI; proibida em `production`. |

`app/core/config.py` usa Pydantic Settings para validar a configuração no início.
Variáveis do processo têm prioridade sobre `backend/.env`; na ausência de ambos,
valem os padrões. O caminho do arquivo independe do diretório de execução.
Entradas inválidas impedem a inicialização. Reinicie o servidor após editar `.env`.

O `.env` local está ignorado pelo Git; apenas `.env.example` deve ser versionado.
Não adicione credenciais reais ao exemplo. Variáveis de PostgreSQL serão incluídas
nas tarefas do banco. `pydantic-settings` e sua dependência `python-dotenv` foram
adicionados para carregar e validar o ambiente sem implementar um parser próprio.

Validação realizada: padrões sem arquivo, leitura de arquivo temporário,
prioridade do processo, rejeição de valores inválidos e de depuração em produção,
integração com FastAPI e preservação da resposta da função de `/health`.

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
O teste persistente com pytest está previsto na S0-T13.
As dependências de banco e testes serão adicionadas nas tarefas correspondentes.

Consulte [a Sprint atual](../docs/CURRENT_SPRINT.md) antes de implementar.
