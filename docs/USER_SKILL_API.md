# Consulta de progresso — S7A-T04

`GET /api/v1/users/me/skills` exige Bearer válido e consulta somente a identidade
autenticada. ADMIN também consulta apenas seu próprio progresso. Não aceita
user_id, filtro de atividade ou outros parâmetros extras.

Query: limit inteiro 1–100 (padrão 20), offset inteiro >= 0 (padrão 0).
Ordenação estável por skill_id crescente. Resposta 200:

```json
{
  "items": [{
    "skill_id": 1,
    "score": 520,
    "confidence": "0.047619",
    "attempts": 1,
    "successful_attempts": 1,
    "last_practiced_at": "2026-09-30T12:00:00Z",
    "updated_at": "2026-09-30T13:00:00Z"
  }],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

Sem progresso: items vazio e total 0. Offset além da última página retorna items
vazio mantendo total. Inclui progresso de skills desativadas para preservar o
histórico. Não retorna perfil vazio para skills ainda sem evidência avaliável.
Campos internos, origem do diagnóstico, acumuladores e histórico de revisão não
são expostos nesta rota. Leitura não atualiza scores, datas ou evidências.

confidence é string decimal para preservar a precisão. É um indicador
experimental de volume/estabilidade da evidência, não probabilidade de domínio.
attempts conta evidências avaliáveis aplicadas; successful_attempts conta MET.
last_practiced_at é a maior data de submissão aplicada, não a data da revisão.

Sucesso inclui Cache-Control: no-store. Autenticação ausente/inválida: 401;
query inválida ou extra: 422, também no-store conforme os handlers existentes.
Paginação por offset não constitui snapshot entre requisições concorrentes.

## Validação

5 testes integrados passaram em 7,64 s, com warnings como erros:
test_progress_access.py, test_skill_integration.py, test_evaluation_service.py
e test_evaluation_http.py. PostgreSQL descartável.

Incluem consulta autenticada, isolamento STUDENT/ADMIN, paginação, skills inativas,
ausência de campos internos, reenvio, rollback e revisão tardia. Teste com duas
sessões e barreira imediatamente antes do lock força avaliações de tentativas
distintas do mesmo aluno a disputar o progresso. O histórico antes/depois é
encadeado e o resultado final confere com a política aplicada na ordem registrada.
