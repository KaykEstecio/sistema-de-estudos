# Sprint 12E — orientação de leitura por habilidade

Continuação autorizada em 07/10/2026: reduzir a dúvida sobre por onde começar.
Sem trilhas obrigatórias, nível global, execução automática ou mudança de score.

Aula possui study_order opcional, inteiro 1–10000, definido por ADMIN. Null
significa fora da sequência editorial. Empates são permitidos e resolvidos por
id crescente; posições são prioridades editoriais, não números de etapas únicos.
PUT /study/{id}/order aceita {study_order: inteiro ou null}; idempotente, só ADMIN,
skill ativa, com no-store. Corpo inválido 422; sem acesso 401/403; aula ausente ou
inativa 404. Não modifica texto, prática indicada, conclusão ou tentativas.

GET /study?skill_id=… ordena por study_order ASC NULLS LAST, id ASC. Sem filtro,
a biblioteca mantém publicação recente primeiro. StudySummary expõe study_order.
StudyPage inclui has_sequence e next_content (StudySummary ou null). Somente com
skill explícita: has_sequence indica existência de aulas ordenadas; next_content
é a primeira delas ainda não marcada pelo usuário, consultada em todo o conjunto,
independente da página. Sem filtro: false/null. Leituras de outra conta não
interferem. Skill inativa: lista vazia, false/null. Consulta não altera dados.

Interface: cada cartão oferece acesso à sequência da habilidade; no filtro,
destacar próxima leitura e informar quando todas estão marcadas ou quando ainda
não existe sequência. Todas as aulas continuam acessíveis. No detalhe, ADMIN
edita posição e qualquer aluno retorna à sequência para escolher o próximo passo.
Não dizer que leitura completa significa domínio ou que a sugestão é adaptação
calculada por score. Demais recomendações seguem suas regras existentes.

Migration 0011 adiciona a coluna e constraint; sem seed. Catálogo local será
ordenado explicitamente pelo material editorial, sem inferência em runtime.

Validar permissões, limites, null, empates, paginação, isolamento da conclusão,
inativos, ausência de alteração de UserSkill; navegador ADMIN configura e aluno
segue a orientação. Piloto pedagógico continua pendente.

## Evidências — 07/10/2026

Migration 0011 aplicada localmente; Alembic check sem diferenças. Dez aulas
ordenadas pela API ADMIN conforme [reading-order-v1.json](../content/study/reading-order-v1.json).
Build, tipos e backend completo aprovados: 341 passed, warnings como erros,
sem skips. Teste study ampliado verifica limites, autorização, empates, null,
paginação independente da sugestão, isolamento e skill inativa.

Harness com 19 testes aprovados; novo caso cobre ADMIN configurando a ordem,
aluno seguindo duas leituras, estado de sequência concluída e outra conta
recebendo sua própria primeira leitura. Captura mobile inspecionada, sem overflow.
Cleanup confirmado. Sem teste pedagógico real, novo commit ou deploy.
