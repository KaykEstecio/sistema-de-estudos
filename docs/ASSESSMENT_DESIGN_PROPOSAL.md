# Assessment inicial — contrato S4-T01

Status: contrato definido após confirmação do recorte pelo usuário. Documento
complementar à arquitetura; o nome do arquivo preserva a origem da proposta.
Persistência na S4-T02; início/consulta/respostas na S4-T04; finish na S4-T05.
Referências: PROJECT_SPEC.md §7, BUSINESS_RULES.md RN50–RN52 e CURRENT_SPRINT.md.

## Recorte proposto

Diagnóstico INITIAL de múltipla escolha com uma resposta correta por questão,
sem execução de código, dicas, tempo como critério ou LLM. O usuário seleciona
de 1 a 3 skills ativas pertencentes às categorias dos seus interesses, escolhendo
as que deseja diagnosticar para seu objetivo. Essa escolha explícita representa
a relevância ao objetivo; o sistema não interpreta palavras do objetivo livre.

Seleção explícita confirmada pelo usuário na S4-T01 como concretização da RN50.
Seleção automática por objetivo fica FUTURO. Não interpretar texto livre por
palavras ou alterar o contrato do onboarding.

Cada skill precisa de três questões ativas disponíveis; seleção determinística
por ID crescente. Falta de conteúdo rejeita a criação inteira, sem diagnóstico
parcial. Total de 3 a 9 questões. Não usar experiência declarada para escolher
uma dificuldade ou atribuir pontos nesta versão.

Os limites de três skills/três questões são decisões S4-T01 para manter o
primeiro fluxo pequeno e testável; não há evidência de calibração pedagógica.

## Conteúdo e autoria

AssessmentQuestion, entidade proposta do módulo assessments, contém uma skill,
enunciado, quatro alternativas identificadas A/B/C/D, opção correta e is_active.
Conteúdo inicial deve ser revisado antes de ser usado como diagnóstico real.
Fixtures artificiais servem somente aos testes e não viram seed de produção.

Provisionamento mínimo: importação local de arquivo JSON validado, com código
estável por questão. Sem endpoint de autoria ou painel. Importação somente de
novas questões, em transação única, rejeitando códigos duplicados no arquivo ou
no banco e skills inexistentes. Atualização de conteúdo fica FUTURO. O operador
local fornece questões revisadas; conteúdo dos testes não é conteúdo pedagógico
aprovado. Nenhuma questão será publicada automaticamente nesta tarefa.

Ao iniciar, copiar texto, alternativas e gabarito para AssessmentItem privado.
Mudanças posteriores no banco de questões não afetam uma prova iniciada.
Gabarito não aparece em nenhum schema público, inclusive após finalização.
Snapshots preservam a reprodutibilidade, sem infraestrutura de versionamento.

## Ciclo de vida proposto

- Exigir onboarding concluído e autenticação; STUDENT e ADMIN operam somente
  seus próprios diagnósticos.
- Uma prova aberta por usuário. POST repetido enquanto houver prova aberta
  retorna 409, sem criar cópia. Retomada por GET do ID retornado na criação.
- Resposta contém item_id e selected_option. Item precisa pertencer à prova.
  Reenvio substitui a escolha enquanto aberta; mantém uma resposta por item.
- Finish exige todas as questões respondidas; faltantes retornam 409 sem concluir.
- Finish repetido retorna o mesmo resultado persistido (200), sem reavaliar.
- Respostas após conclusão retornam 409. Não há reset, exclusão ou expiração.
- Após concluir, usuário pode iniciar outra prova. Sem aleatoriedade, ela poderá
  repetir questões; repetir a prova não representa aumento de confiança.

## Resultado — decisão S4-T01

Por skill: correct_count, question_count e score. Score é percentual
de acertos escalado para 0–1000, arredondado ao inteiro mais próximo com metade
para cima: 0/3 → 0, 1/3 → 333, 2/3 → 667, 3/3 → 1000.

Não exibir BEGINNER/EXPERT como conclusão de domínio a partir desse score: ele
resume acertos deste diagnóstico e não mede competência com precisão calibrada.

AssessmentResult mantém confidence=0 nesta versão: não há calibração de
confiança de domínio disponível. Esse valor significa ausência de confiança
calibrada, não ausência de acertos ou incapacidade do aluno. Documentar como
INITIAL_DIAGNOSTIC_CONFIDENCE=0 no código; não aumentar por repetição.

Recorte confirmado: persistir somente AssessmentResult, sem UserSkill. A RN51
permite inicialização, mas não a exige. Se ela for desejada agora, definir como
preservar valores existentes, attempts/successful_attempts e histórico, mantendo
SkillService responsável pela atualização. Não sobrescrever domínio aprendido
por resultado de prova repetida.

## Contratos HTTP

| Método e caminho | Entrada | Sucesso |
| --- | --- | --- |
| POST /api/v1/assessments | {"skill_ids":[1,2]} | 201, prova e itens públicos |
| GET /api/v1/assessments/{id} | Sem corpo/query | 200, estado e escolhas próprias |
| POST /api/v1/assessments/{id}/answers | {"item_id":1,"selected_option":"B"} | 200, escolha salva |
| POST /api/v1/assessments/{id}/finish | Sem corpo/query | 200, prova concluída e resultados |

Resposta da prova: id, assessment_type=INITIAL, started_at, completed_at,
items ordenados por position e results ordenados por skill_id. Item público:
id, skill_id, position, prompt, options e selected_option (null antes da resposta).
Results vazio antes da conclusão; depois contém skill_id, score, confidence,
correct_count e question_count. Sem user_id, gabarito ou score recebido do cliente.
Cache-Control: no-store. Datas UTC. Prova permanece consultável se skill original
for desativada, pois o conteúdo foi congelado na criação.

Detalhamento S4-T04: agrupar itens por skill_id crescente e, dentro de cada
skill, por ID da questão crescente. /answers retorna o item público atualizado.
Erros usam detail textual fixo, sem entradas do cliente: diagnóstico não encontrado,
skill indisponível, item fora da prova, onboarding pendente, prova aberta existente,
conteúdo insuficiente ou prova já concluída, conforme os códigos abaixo.

Validação: IDs inteiros estritos positivos até 2147483647, skills distintas; opções
exatamente A/B/C/D; extra fields rejeitados. Enunciado 1–4000 caracteres e cada
alternativa 1–1000, após trim. Slug/código de questão 1–120 conforme padrão do
catálogo, único. Alternatives em objeto JSON com exatamente A/B/C/D, sem extras;
selected_option e correct_option são strings restritas a essas chaves.

401 para autenticação inválida. 404 para prova inexistente/de outro usuário,
item fora da prova ou skill indisponível ao usuário. 409 para onboarding pendente,
prova aberta existente, conteúdo insuficiente, respostas faltantes ou prova
encerrada. 422 para dados estruturais inválidos. Checar ownership antes de estado.
Não distinguir a existência de uma prova pertencente a outra conta.

## Persistência

- Assessment: campos existentes; índice único parcial de user_id para
  completed_at IS NULL; assessment_type restrito a INITIAL neste recorte.
- AssessmentQuestion: conteúdo privado de autoria conforme seção acima.
- AssessmentItem: assessment_id, skill_id, position, snapshot privado do conteúdo
  e selected_option anulável. A resposta fica no próprio item; não criar tabela
  adicional de respostas sem necessidade de histórico de edição.
- AssessmentResult: campos previstos mais correct_count/question_count, com
  UNIQUE(assessment_id, skill_id), score 0–1000, confidence 0–1 e contagens válidas.
- FK RESTRICT, sem exclusão física via API; posições únicas por assessment.
  Schemas públicos explícitos nunca serializam snapshots privados integralmente.

IDs usam INTEGER Identity; FKs são obrigatórias, com nomes explícitos. Conteúdo
usa prompt VARCHAR(4000), options JSONB, correct_option VARCHAR(1); respostas
selected_option VARCHAR(1). CHECK limita opções a A/B/C/D, posições positivas,
contagens não negativas com correct_count <= question_count e question_count > 0.
Score INTEGER, confidence NUMERIC(4,3); timestamps TIMESTAMPTZ. Snapshots guardam
skill_id, texto e alternativas; não precisam de FK à questão de origem.
AssessmentResult é único por prova/skill; Item por prova/posição. Índice por FK
quando não coberta pelo prefixo de índice existente. Sem default de gabarito.
Downgrade remove apenas as tabelas do diagnóstico, preservando onboarding,
catálogo e usuários. Extensão do monólito modular sem alteração de stack.

## Transações e responsabilidades

AssessmentService coordena seleção, ownership e ciclo de vida. Avaliação pura
em serviço específico do diagnóstico, sem dependência de desafios. Repositories
fazem persistência; routers adaptam HTTP.

Início bloqueia User para serializar provas abertas; índice parcial garante a
invariante no banco. Resposta e finish bloqueiam Assessment e releem estado.
Finish calcula resultados dos snapshots, grava resultados/completed_at e faz
commit único. GET usa leitura coerente. Falhas revertem toda a operação.

## Estado da decisão

Seleção explícita, múltipla escolha e ausência de UserSkill confirmadas pelo
usuário. Limites, confidence não calibrada e importação somente de novas questões
registrados como decisões S4-T01, sem alegação de validação pedagógica.
Conteúdo real revisado continua sendo pré-requisito operacional para um diagnóstico
útil; a API deverá retornar conflito se não houver conteúdo suficiente.
