# Sprint 12C — da leitura à prática

Autorizada pelo usuário em 07/10/2026 após a entrega da área de estudo.

## Recorte

- Converter as dez práticas editoriais em desafios autorais avaliáveis.
- Cada enunciado informa pré-requisitos, entradas, resultados observáveis,
  entrega esperada e critérios públicos por habilidade.
- Exibir desafios da mesma skill no detalhe da aula, paginados por ordem de
  cadastro. É exploração do catálogo, não recomendação personalizada nem
  vínculo exclusivo aula/desafio. Não exige marcar a aula como estudada.
- Reutilizar início/retomada, snapshot, envio, revisão ADMIN e atualização de
  UserSkill existentes. Critérios fazem parte da descrição preservada no snapshot.
- Usar a rubrica manual-v1; não executar respostas nem publicar soluções privadas.
- Publicar pelo contrato administrativo existente, sem importador, seed ou
  migration nova. O JSON editorial usa slugs; IDs são resolvidos no ambiente.

## Critérios de revisão

MET: atende todos os critérios declarados da skill com evidência na resposta.
PARTIALLY_MET: atende parte; indicar exatamente a lacuna observável.
NOT_MET: há evidência de descumprimento dos requisitos da skill.
INSUFFICIENT_EVIDENCE: a resposta não permite concluir; não presumir erro.
Não exigir estilos, casos ou ferramentas não pedidos. Não afirmar que executou
código enviado. Avaliar a explicação e os resultados apresentados, com feedback.
Pesos e dificuldades são decisões editoriais iniciais, não medidas calibradas.

## Validação realizada — 07/10/2026

Build/TypeScript e tipagem E2E aprovados. Harness com 17 testes aprovados, sem
skips/falhas, cleanup confirmado. Novo cenário de navegador cobre leitura →
desafio → tentativa, independente da conclusão da aula, catálogo vazio, falha
recuperável, paginação, ocultação de inativo e snapshot após edição do catálogo.
O ciclo existente de envio → revisão ADMIN → progresso também passou.
Captura mobile inspecionada, sem overflow. Não é auditoria de acessibilidade.

Dez payloads passaram por ChallengeCreate. Casos de fronteira Python/lógica,
consultas SQL e staging Git conferidos; HTTP é cenário ilustrativo revisado.
Dez desafios publicados localmente pela API ADMIN, IDs 1–10; conferência prévia
de título e conteúdo para evitar duplicar/sobrescrever. Não houve alteração de
respostas, leituras ou scores reais. Detalhes em [CONTENT_CURATION.md](CONTENT_CURATION.md).
Sem mudanças de backend, dependências ou migration; suíte backend completa não
foi repetida. CI aprovada para o commit anterior 4d7d03a, não para este diff local.

## Limites

Atualização S12D: o vínculo editorial aula/desafio foi autorizado e implementado
em [LEARNING_IMPROVEMENTS.md](LEARNING_IMPROVEMENTS.md). O catálogo por skill
permanece como exploração adicional; o recorte acima registra a entrega S12C.

Validação técnica não substitui teste pedagógico com alunos reais. Coletar se o
aluno entende o objetivo, resolve uma variação sem copiar e interpreta o feedback.
Roteiro, registro de observações e critérios de conclusão em
[LEARNING_PILOT.md](LEARNING_PILOT.md). Preparação concluída; execução real pendente.
FUTURO: trilhas, edição/versionamento de aulas,
execução automática, gamificação e ampliação de conteúdos após retorno dos alunos.
Deploy segue adiado.
