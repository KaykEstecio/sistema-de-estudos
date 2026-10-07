# Melhorias da experiência — Sprint 12D

Autorizadas em 07/10/2026 a partir da análise comparativa: reduzir dificuldades
sem desviar do aprendizado por skills, evidências e revisão manual.

## Prioridade atual: prática específica da aula

Uma aula pode apontar para um desafio principal, escolhido pelo ADMIN. A indicação
é editorial, não uma recomendação calculada ou pré-requisito obrigatório. Outros
desafios da skill continuam acessíveis, identificados como exploração adicional.
Não inferir vínculos por título, posição ou IDs fixos no frontend.

Migration 0010 adiciona challenge_id opcional a study_contents com FK RESTRICT.
GET /api/v1/study/{id}/practice retorna ChallengeRead ou null. Disponível para
usuários autenticados; null quando não há vínculo, o desafio está inativo, alguma
skill dele foi desativada ou a skill da aula deixou de fazer parte do desafio.
Não expor conteúdo administrativo inativo, inclusive a ADMIN nesse endpoint.
PUT na mesma rota exige ADMIN e corpo {challenge_id: inteiro positivo ou null}.
O desafio escolhido deve estar ativo, com todas as skills ativas e incluir a
skill da aula. Repetição é idempotente; null remove só a indicação.
ID inválido/extra: 422; sem acesso: 401/403; aula indisponível: 404; desafio
inexistente, incompatível ou indisponível: 409. Respostas no-store.

Não modifica texto da aula, tentativas, snapshots, avaliações ou progresso.
Editar/desativar desafio pode invalidar dinamicamente a indicação; o ADMIN pode
escolher outra prática. Não há bloqueio de aprendizagem por conclusão da leitura.

## Próximos recortes, ainda não implementados

1. S12E autorizada: orientação por skill com sequência editorial e próximo passo
   de leitura em [STUDY_GUIDANCE.md](STUDY_GUIDANCE.md). Não mede domínio.
2. FUTURO: verificações pequenas com explicação imediata, separadas da avaliação
   aberta. Definir primeiro regras e evidências; sem executor ou LLM no núcleo.
3. FUTURO: edição/versionamento de conteúdos para corrigir dúvidas observadas,
   preservando o contexto histórico e os registros de estudo.
4. FUTURO: melhorias da fila de revisão conforme volume e espera observados;
   não prometer prazo sem capacidade real dos revisores.

O piloto com alunos permanece pendente. Não ampliar catálogo ou gamificação para
compensar problemas não investigados. Deploy continua adiado.

## Validação exigida

Autorização, remoção/repetição do vínculo, compatibilidade da skill, inativos,
revogação de role, persistência, migration e ausência de efeitos sobre progresso.
Navegador: ADMIN escolhe prática; aluno vê a indicação e inicia a tentativa;
desativação não expõe o desafio; erros têm recuperação sem publicação duplicada.

## Entrega e evidências — 07/10/2026

Vínculo implementado, migration 0010 aplicada localmente e Alembic check aprovado.
Dez associações editoriais feitas pela API ADMIN e verificadas por GET, usando
o mapeamento lesson_key do lote e conferindo títulos existentes. Sem IDs fixos
no produto, sem seed automático e sem alterar respostas ou progresso.

Build/TypeScript e tipagem E2E aprovados. Backend completo: 341 passed, sem skips,
warnings como erros. Teste study ampliado cobre autorização, payloads, repetição,
remoção, incompatibilidade, mudança posterior das skills e desativação.
Harness: 18 testes aprovados, cleanup confirmado. Novo fluxo real cobre escolha
pelo ADMIN e início pelo aluno; captura mobile inspecionada, sem overflow.
Não houve teste com aluno real; este continua pendente. CI anterior não cobre
estas mudanças locais, ainda sem commit/deploy.
