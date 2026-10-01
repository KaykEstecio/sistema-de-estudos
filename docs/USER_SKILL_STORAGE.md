# Persistência de UserSkill — S7A-T02

Política manual-skill-v1 aprovada. Migration 0008 cria estruturas vazias:
nenhuma avaliação anterior é aplicada. Integração transacional implementada na S7A-T03.

## Estado por usuário e skill

UserSkill: PK id, UNIQUE(user_id, skill_id); FKs RESTRICT para usuário/skill.
Score inteiro 0–1000; confidence NUMERIC(7,6) em 0–0,95. Contadores inteiros
attempts > 0 e 0 <= successful_attempts <= attempts. Registro nasce somente
após a primeira evidência avaliável, já com o efeito calculado.
last_practiced_at e updated_at UTC com fuso, não nulos.

initial_score registra a base 0–1000. initial_assessment_id é nullable e, quando
preenchido, forma FK com skill_id para AssessmentResult. Sem diagnóstico, base
obrigatoriamente 500. SkillService verifica dono, conclusão anterior ao início
da tentativa e desempate por completed_at/ID; o banco não valida essa regra.

mass, residual_sum e squared_residual_sum são NUMERIC sem escala fixa: PostgreSQL
preserva os Decimals produzidos pelo contexto de precisão 28, sem arredondamento
extra ao salvar. Valores finitos; mass > 0; soma quadrática não negativa e
limitada à massa; módulo da soma dos resíduos limitado à massa. Não armazenar
float. Confiança é a saída arredondada a seis casas da política.

## Histórico de aplicação

SkillEvidence: id Identity; user_id/skill_id; evaluation_id; policy_version;
applied boolean; before_state/after_state JSONB nullable; created_at UTC.
UNIQUE(evaluation_id, skill_id); FK composta para o resultado da avaliação.
Índice (user_id, skill_id, id) permite ler a ordem de aplicação por habilidade.
Todas as FKs RESTRICT. Não há FK a UserSkill: descarte pode preceder sua criação.

Para applied=true, before_state/after_state são objetos obrigatórios. Para false,
ambos são SQL NULL; evidência insuficiente não cria UserSkill. Campos e consistência
interna desses objetos são validados por schema no service da S7A-T03.
Eles registram score, confiança, acumuladores e contadores antes/depois;
Decimals serializados como strings para preservar precisão. Na inicialização,
before_state representa base/confiança zero/contadores zero, ainda não persistidos.
Avaliação, tentativa e snapshot referenciados preservam classificação, dificuldade,
peso e número; policy_version fixa os coeficientes. Sem duplicar textos de revisão.

Ordem é a sequência de IDs das evidências por usuário sob lock de User; lacunas
de sequência por rollback são permitidas. ID não representa ordem global de commit.
Ownership entre evidência, avaliação e tentativa é derivado da tentativa autorizada
pelo EvaluationService, sem aceitar identidade do aluno no payload.

## Integração S7A-T03

EvaluationService autoriza o revisor, bloqueia a tentativa e mantém o caminho
idempotente anterior. Apenas após criar uma avaliação nova chama SkillService;
ambos usam a mesma Session e um único commit do coordenador. Qualquer falha
desfaz avaliação, resultados por skill, progresso e histórico.

SkillService serializa as atualizações com FOR NO KEY UPDATE no usuário dono.
Esse lock impede atualizações de progresso concorrentes sem bloquear referências
FK ao usuário. O lock permanece até commit/rollback. Progresso é lido novamente
após o lock; a unicidade de avaliação/skill também protege contra aplicação dupla.
ProgressRepository consulta/persiste sem commit; ProgressState valida e serializa
os estados auditáveis. Evidência insuficiente registra somente o descarte.

Inicialização usa completed_at estritamente anterior ao started_at da tentativa,
ordenado por completed_at DESC e Assessment.id DESC, filtrado pelo dono e skill.
Ausência de resultado usa 500. Origem não muda após a primeira aplicação.

O corte é a criação de uma avaliação por esta versão do service, não uma data
arbitrária: registros anteriores continuam somente qualitativos. Reenviá-los
retorna o resultado existente sem criar evidências ou executar backfill.
Aplicar migration 0008 antes de iniciar esta versão do backend.

## Limites

Imutabilidade e coerência do conjunto dependem do service: não criar triggers ou
regras pedagógicas em migrations. Downgrade remove somente as tabelas novas;
por definição descarta o progresso dessa etapa, preservando avaliações anteriores.
Validar reversão somente em banco de teste, sem executar downgrade no banco local.

## Validação executada

26 testes passaram em 14,42 s (persistência de UserSkill, migration de avaliações
e política pura), com warnings tratados como erros. Banco PostgreSQL descartável:
upgrade/downgrade, preservação das avaliações anteriores, ausência de backfill,
restrições de integridade, precisão Decimal após leitura e `alembic check`.
Migration não aplicada ao banco de desenvolvimento nesta tarefa.
