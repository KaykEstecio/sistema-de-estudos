# Sprint 8 — planejamento do recomendador

Status: recorte e política definidos por delegação do usuário em 30/09/2026;
implementação realizada na Sprint 8. Contratos vigentes em RECOMMENDATION_POLICY.md
e RECOMMENDATION_API.md. O restante preserva o planejamento histórico.
As decisões abertas abaixo registram o planejamento original; a política resolve
essas escolhas e CURRENT_SPRINT.md registra a sequência atual.
Sucede a [Sprint 7A](SPRINT_7A.md). Referências: RN37–RN46 e seções 15–17
da especificação. Não altera a política manual-skill-v1.

## Primeiro recorte recomendado

Recomendação determinística de desafios para uma skill explicitamente escolhida
pelo usuário dentre seus interesses. A escolha evita inventar prioridades entre
skills ou interpretar o objetivo escrito em texto livre. O sistema escolhe
atividades, mantendo o progresso individual por habilidade.

O primeiro contrato deve considerar dificuldade, evidência/confiança e histórico,
explicando os fatores que determinaram cada sugestão. Não produzir nível global
nem apresentar confiança como probabilidade de sucesso.

## Dados disponíveis e limites

| Dado | Uso proposto |
| --- | --- |
| UserInterest → Category → Skill | Validar a seleção dentro dos interesses atuais |
| UserSkill | Score por habilidade e quantidade/estabilidade de evidência |
| Challenge e ChallengeSkill | Dificuldade, skills e pesos do desafio atual |
| ChallengeAttempt | Diferenciar tentativa aberta, submetida e repetição |
| AttemptEvaluation | Diferenciar submissão de evidência efetivamente avaliada |
| UserGoal | Contexto declarado; sem inferir competências pelo texto |
| AssessmentResult | Diagnóstico independente; não criar UserSkill durante consulta |

SkillRequirement e metas numéricas por objetivo não existem no código. Permanecem
FUTURO: não declarar pré-requisitos satisfeitos ou diagnosticar uma lacuna em
relação a uma meta inexistente. Também não existem dados de dicas ou tempo efetivo.

## Regras já determinadas

- Somente desafios ativos, com skills existentes e ativas; reutilizar a semântica
  de visibilidade do catálogo, inclusive quando o solicitante for ADMIN.
- Consultar somente perfil e histórico da identidade autenticada.
- RecommendationService seleciona e explica; não avalia, altera UserSkill,
  inicia tentativa ou faz commit como efeito colateral de uma consulta.
- Cada recomendação precisa de motivo verdadeiro e reproduzível, baseado nos
  dados usados. Empates exigem ordenação estável.
- Submissão não significa aprovação nem domínio. Tentativa aberta deve ser
  distinguida de nova atividade, evitando recomendar reinício acidental.
- Histórico recente reduz prioridade, conforme RN40. Dificuldade muito acima
  não deve entrar como sugestão normal; muito abaixo deve ser revisão.
- A proporção conceitual 20/60/20 não será tratada como quota rígida.
- Sem catálogo elegível, retornar ausência explícita de sugestões; não relaxar
  silenciosamente as regras nem inventar conteúdo.

## Decisões da política a definir antes do código

1. Entrada sem UserSkill: oferecer exploração inicial com limites explícitos ou
   indicar diagnóstico/prática inicial. A rota não pode inventar progresso 500
   como se fosse evidência nem exigir UserSkill de modo que impeça a primeira prática.
2. Desafios com múltiplas skills: avaliar todas as habilidades envolvidas, para
   não esconder uma habilidade desconhecida ou fraca atrás da skill selecionada.
   Definir tratamento de evidência ausente e agregação sem criar nível global.
3. Faixas de dificuldade próxima, revisão e progressão; influência de confidence
   e volume de evidências. Definir parâmetros experimentais com exemplos.
4. Significado e janela de “recente”, tratamento de submissão aguardando revisão,
   tentativas abertas e revisão de desafios já praticados.
5. Ordem dos critérios, desempates, limite de resultados e justificativas.

Esses parâmetros não estão aprovados por este documento. A escolha do recorte
não equivale a aprovação de coeficientes pedagógicos. Uma política candidata
deve mostrar cenários concretos antes da implementação.

## Sequência de trabalho

| Tarefa | Entrega | Estado |
| --- | --- | --- |
| S8-T01 | Inventário e proposta de recorte | Concluída neste documento |
| S8-T02 | Política candidata, parâmetros e exemplos de seleção | Próxima |
| S8-T03 | Contrato HTTP, schemas, erros e estratégia de consultas | Após política definida |
| S8-T04 | Cálculo puro e testes dos critérios aprovados | FUTURO |
| S8-T05 | Repository, RecommendationService e rota autenticada | FUTURO |
| S8-T06 | Integração, regressão e documentação | FUTURO |

Não criar tabelas ou migrations antecipadamente. Decidir no contrato se a primeira
versão calcula sugestões sob demanda ou precisa de registro persistido, conforme
os requisitos concretos. Dashboard, tela de desafios, ML e LLM estão fora do recorte.

## Cenários obrigatórios de validação

- Mesmo contexto produz a mesma ordem e explicações; alteração de evidência pode
  mudar a seleção de modo justificável.
- Usuário forte em Python e fraco em SQL não recebe nível médio global.
- Ausência de progresso, confiança baixa e skill secundária desconhecida possuem
  comportamento explícito, sem bloquear todo acesso à primeira prática.
- Desafio ou skill desativados nunca aparecem, inclusive após mudança do catálogo.
- Histórico de outra conta não altera as sugestões; ADMIN não seleciona outro dono.
- Tentativa aberta, submissão pendente de revisão, revisão tardia e repetição têm
  efeitos distintos e documentados.
- Limites das faixas/janelas, empates e lista vazia são testados.
- Consulta não modifica scores, evidências, datas ou tentativas.

## Validação do planejamento

Conferidos CURRENT_SPRINT, RN37–RN46, especificação, catálogo e models existentes.
Alteração documental; nenhum teste de execução necessário nesta etapa e nenhum
resultado de implementação do recomendador é declarado.
