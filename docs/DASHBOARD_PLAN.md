# Sprint 9 — Dashboard básico

Planejamento iniciado em 01/10/2026 após o fechamento da Sprint 8.
Escopo escolhido conforme a delegação do usuário para decisões do projeto.
Sem implementação neste documento.

## Objetivo

Criar uma página autenticada `/dashboard` que mostre o progresso real por skill
e sugestões explicadas, orientando o próximo passo. Sem nível global, gráficos
sem histórico temporal, percentuais de curso concluído ou metas inventadas.

Após login, contas com onboarding concluído chegam ao dashboard; contas sem
onboarding continuam no perfil. O acesso direto autenticado ao dashboard deve
explicar a falta de interesses e oferecer configuração do perfil, sem bloquear
a visualização de progresso já existente. Manter acesso ao diagnóstico e perfil.

## Inventário e decisões

| Necessidade | Estado e decisão |
| --- | --- |
| Sessão | Reutilizar AuthProvider, Bearer em memória e tratamento de 401 |
| Perfil/interesses | API de onboarding existente; objetivo exibido como declaração |
| Progresso | API existente retorna IDs, score, confiança, contagens e datas |
| Nomes de skills inativas | Catálogo STUDENT não resolve; enriquecer no backend para o dono |
| Recomendações | GET /recommendations já implementado, requer escolha focal |
| Catálogo de skills | APIs paginadas disponíveis; não assumir que primeira página contém todas |
| Experiência de desafios | Sem rota frontend; permanece Sprint 10 |

Usar o endpoint já previsto `GET /api/v1/dashboard` como resumo de leitura do
próprio usuário. Definir contrato na S9-T02 antes de implementar: perfil resumido,
indicadores com significado preciso e pequena lista de progresso com nomes e
atividade da skill. Não duplicar política de UserSkill ou Recommendation.
Não ampliar acesso STUDENT ao catálogo inativo; nomes históricos vêm apenas dos
registros de progresso pertencentes à identidade autenticada.

Recomendações continuam em sua rota, carregadas após seleção explícita da skill.
Não chamar o recomendador para todas as skills automaticamente. Sem tabelas novas
ou migrations previstas; repository agrega dados existentes, service coordena,
router permanece simples. Não criar infraestrutura genérica de métricas.

## Conteúdo da primeira tela

1. Boas-vindas e ações de perfil/diagnóstico.
2. Progresso por habilidade: nome, score, confiança experimental, evidências
   avaliáveis e última prática. Diferenciar skill desativada sem apagar histórico.
3. Seleção de skill ativa dentro dos interesses e sugestões de atividades com
   título, dificuldade, tempo estimado, tipo e motivo retornado pela API.
4. Leitura do enunciado de uma sugestão em painel de detalhe na mesma tela,
   usando GET /challenges/{id}. Esse painel não inicia tentativa nem executa código.
   Informar que a resolução pela interface será disponibilizada posteriormente.

Não exibir botão “Começar” sem fluxo implementado. A ação desta Sprint será
“Ver desafio”; ao abrir, revalidar o catálogo. Se indisponível, avisar e atualizar
as sugestões. A resolução, rascunho, submissão e avaliação na interface são FUTURO.

## Estados e integridade

- Sem interesses: orientar configuração e manter progresso existente visível.
- Sem UserSkill: explicar que progresso surge após evidências avaliadas; oferecer
  diagnóstico, sem apresentar score zero ou 500 como dado pessoal.
- Sem sugestões: explicar ausência de atividades elegíveis; não inventar conteúdo
  nem afirmar que todas as skills foram dominadas.
- Confiança mostrada como índice experimental, não percentual de domínio.
- Falhas de perfil, progresso ou recomendações têm estados localizados e ação
  de tentar novamente; loading não aparece como lista vazia.
- Troca rápida de skill cancela/ignora resposta anterior. Logout limpa dados;
  nova conta não reutiliza resultados da anterior. Sem cache de dados pessoais
  em localStorage. Datas apresentadas no fuso do navegador.
- Suporte a teclado, foco visível, mensagens acessíveis e layout responsivo.

## Sequência de tarefas

| Tarefa | Entrega | Estado |
| --- | --- | --- |
| S9-T01 | Inventário, recorte e jornada | Concluída neste plano |
| S9-T02 | Contrato do resumo, contagens, paginação e nomes históricos | Próxima |
| S9-T03 | Backend do resumo e testes de ownership/consistência | Pendente |
| S9-T04 | Layout e frontend do dashboard, navegação e estados vazios | Pendente |
| S9-T05 | Recomendações, seleção de skill e detalhe somente leitura | Pendente |
| S9-T06 | Verificação no navegador, regressão e documentação | Pendente |

S9-T02 deve fixar limites de resposta, ordenação, tratamento de paginação e
significado das contagens. Não somar attempts de UserSkill como total de desafios:
uma avaliação com várias skills conta em cada skill. Evitar estatísticas cujo
significado não possa ser explicado com os dados atuais.

## Validação esperada

Backend: somente dados do dono inclusive ADMIN, nomes de skills desativadas sem
vazar catálogo de terceiros, contagens sem duplicação, ordenação estável e ausência
de efeitos colaterais. Frontend: conta nova, conta com progresso, catálogo vazio,
erro parcial, 401, troca de conta, troca rápida de skill, desafio desativado após
recomendação, teclado e viewport estreito. Testar nomes/descrições como texto.

Preservar autenticação, onboarding e diagnóstico. Não adicionar dependências
sem necessidade. Build e testes pertinentes, além de validação real no navegador,
serão necessários antes de declarar a Sprint concluída.

## Validação do planejamento

Conferidos roadmap, App.tsx e contratos de progresso/recomendação. Não houve
alteração de código, banco ou aparência; não há testes de execução novos nesta tarefa.
