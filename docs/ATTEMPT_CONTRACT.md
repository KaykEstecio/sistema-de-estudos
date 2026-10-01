# Contrato de tentativas — S6-T01

Status: persistência, schemas e repository implementados nas S6-T02/T03;
início, consulta e rascunho implementados na S6-T04; submissão na S6-T05.
Integração final validada na S6-T06. Regras de domínio em
BUSINESS_RULES.md, RN17–RN23. Sem alteração de stack ou arquitetura.

## Ciclo de vida

IN_PROGRESS → SUBMITTED. Não há estado de aprovação, reprovação ou avaliação
nesta Sprint. Uma tentativa submetida conserva resposta e contexto imutáveis.
O dono pode consultar qualquer tentativa própria, inclusive submetida.
ADMIN não tem acesso adicional a tentativas de terceiros.

Uma tentativa aberta por par usuário/desafio. Iniciar novamente retorna a mesma
tentativa aberta; após submissão, inicia outra com número anterior + 1 (primeira=1).
Repetir início após submissão pode criar nova tentativa: não há chave de
idempotência geral. A resposta informa ID e attempt_number para distingui-las.

Novo início exige desafio ativo, ao menos uma skill vinculada e todas ativas,
para qualquer role. Não exige onboarding ou assessment: não há dependência
funcional desses dados para salvar uma resposta. Não cria UserSkill.
Retomar uma tentativa já aberta tem precedência sobre disponibilidade atual.

Edição/desativação posterior do catálogo não impede consultar, salvar ou
submeter uma tentativa existente. Ela utiliza o snapshot original, evitando
mudar o enunciado durante a resolução. Um novo início usa o catálogo atual.

## Resposta e contexto

Os nove tipos aceitam somente resposta textual nesta Sprint, preservando espaços
e quebras de linha. Isso permite registrar texto/código sem interpretar, executar,
validar sintaxe, abrir URLs ou afirmar correção. Não há upload ou resposta JSON
especializada por tipo. Projetos podem ser descritos em texto, sem ingestão externa.

draft_answer é string estrita de até 20000 caracteres, NOT NULL, inicialmente
vazia. Não preencher com starter_code automaticamente; ele está no snapshot.
PATCH exige exatamente draft_answer; string vazia limpa o rascunho, null é inválido.
Submit exige resposta com ao menos um caractere não branco, sem normalizar o texto
salvo. Submissão usa o último rascunho persistido; não recebe resposta no corpo.

Snapshot JSONB independente guarda title, description, challenge_type, difficulty,
difficulty_score, estimated_minutes, starter_code e skills (skill_id/weight,
ordenados por ID). Copiar os limites do contrato de desafios. Não incluir
is_active, datas mutáveis, gabaritos ou dados de usuário. IDs de skills são
referências históricas no documento, não relações mutáveis. Snapshot não pode
ser enviado/alterado pelo cliente e não é refeito em retomada ou submit.

## HTTP

Extensão S10-T03: listagem paginada exclusiva do dono em GET /api/v1/attempts,
conforme [ATTEMPT_EXPERIENCE_CONTRACT.md](ATTEMPT_EXPERIENCE_CONTRACT.md).
As operações individuais abaixo mantêm seus contratos e não aceitam paginação.

Todas as rotas exigem Bearer token e usam Cache-Control: no-store. IDs positivos
até 2147483647; rejeitar queries extras em todas as operações.

| Operação | Entrada | Sucesso |
| --- | --- | --- |
| POST /api/v1/challenges/{id}/attempts | Sem corpo | 201 nova, 200 retomada; AttemptRead |
| GET /api/v1/attempts/{id} | Sem query | 200 AttemptRead, sem mutações |
| PATCH /api/v1/attempts/{id} | draft_answer obrigatório | 200 AttemptRead |
| POST /api/v1/attempts/{id}/submit | Sem corpo | 200 AttemptRead |

Sem corpo significa zero bytes; inclusive objetos vazios são rejeitados.
PATCH rejeita campos extras, status, user_id, contadores e timestamps.

```json
{"draft_answer": "def soma(a, b):\n    return a + b\n"}
```

AttemptRead: id, challenge_id, status, draft_answer, attempt_number,
challenge_snapshot, started_at, submitted_at e last_activity_at. Não expor
user_id desnecessariamente ou coleção de eventos. Datas UTC com fuso.

started_at e last_activity_at iguais no início; submitted_at inicialmente null.
Salvar texto diferente atualiza last_activity_at; reenviar o mesmo rascunho é
no-op. Retomada e GET não alteram datas. Submit define submitted_at e
last_activity_at no mesmo instante. Repetir submit devolve os dados salvos sem
alterar timestamps. PATCH após submit retorna 409 mesmo com texto idêntico.

Erros: 401 para identidade inválida; 404 para tentativa inexistente/de terceiro
ou desafio indisponível ao criar nova tentativa; 409 para PATCH após submissão,
submit sem resposta ou limite de numeração atingido; 422 para entrada inválida.
Falhas inesperadas seguem tratamento seguro existente, sem conteúdo pessoal.
Não revelar existência de tentativa de terceiros ao validar seu estado.

## Persistência

ChallengeAttempt em challenge_attempts:

- id Identity integer PK; user_id e challenge_id NOT NULL, FKs RESTRICT.
- status String(20) NOT NULL, default IN_PROGRESS, check nos dois estados.
- draft_answer String(20000) NOT NULL, default string vazia.
- attempt_number integer NOT NULL, check > 0.
- challenge_snapshot JSONB NOT NULL, check jsonb_typeof = object; formato completo
  validado internamente por schema antes de gravar. Documento sem FK interna.
- started_at e last_activity_at DateTime com fuso, NOT NULL, default now().
- submitted_at DateTime com fuso nullable. Check exige null em IN_PROGRESS e
  não null em SUBMITTED; datas de atividade/submissão não anteriores ao início.
- UNIQUE(user_id, challenge_id, attempt_number); índice único parcial
  (user_id, challenge_id) WHERE status='IN_PROGRESS'; índice challenge_id para FK.

execution_count, hints_used, passed_tests, total_tests, time_spent_seconds e
user_difficulty_rating permanecem FUTURO, sem zeros que pareçam evidência medida.
Sem exclusão de tentativas ou cascades destrutivas. Não criar tabela AttemptEvent
nesta Sprint: início e submissão já têm timestamps; não há consumidor de auditoria
detalhada. RN23 permite eventos, não obriga registrar todos; avaliar necessidade
quando execução/ajuda entrar no escopo. Não armazenar cópias de cada rascunho.

## Transações e concorrência

AttemptService coordena validação e commit/rollback; repository só consulta e
faz flush. Não delegar avaliação ou atualização de habilidade a esse service.

Início: bloquear User FOR UPDATE e reler; procurar tentativa aberta do par.
Se existir, bloqueá-la FOR UPDATE e reler antes de retornar. Se uma submissão
concorrente a fechou, reconsultar o estado e seguir com nova criação. Caso nova,
bloquear Challenge FOR SHARE, verificar publicação, carregar vínculos e bloquear
skills FOR SHARE em ID crescente. Copiar contexto e calcular MAX(attempt_number)+1
sob lock do usuário. Rejeitar overflow de inteiro como 409. Persistir atomicamente.
Esse lock por usuário é simples e suficiente no monólito, sem lock distribuído.

PATCH/submit: buscar pelo ID e dono e bloquear tentativa FOR UPDATE com releitura.
Não bloquear User ou catálogo nesses caminhos. GET consulta somente por ID/dono.
Ordem de início: usuário → tentativa existente OU desafio → skills. Manutenção
de desafio já segue desafio → skills; evita inversão com as operações existentes.

Na corrida PATCH/submit, vence a ordem dos locks: se PATCH primeiro, submit usa
o texto salvo; se submit primeiro, PATCH retorna 409. Submits repetidos não duplicam
operações. Uma falha após flush reverte todos os campos e a sessão fica recuperável.
Unicidade no banco reforça a proteção de início concorrente.

## Validação prevista

Migration com upgrade/downgrade/reaplicação preservando dados anteriores;
constraints de status, numeração, timestamps, FKs e unicidade. Schemas verificam
limites, extras e separação entre campos públicos/internos. Testar duas contas,
ADMIN terceiro, início repetido/concorrente, rascunho vazio, retomada, snapshots
após edição/desativação, submit idempotente, imutabilidade, nova tentativa,
disputa PATCH/submit e rollback após falha parcial. Nenhum efeito sobre assessment,
onboarding ou UserSkill; sem execução ou avaliação de respostas.
