# Planejamento de avaliação — S7-T01

Status: histórico da proposta. Revisão manual escolhida em 29/09/2026;
o contrato vigente é [EVALUATION_CONTRACT.md](EVALUATION_CONTRACT.md).
Referências: BUSINESS_RULES.md
RN29–RN36, ARCHITECTURE.md e ATTEMPT_CONTRACT.md.

## Decisão de entrada

As tentativas atuais armazenam texto livre para nove tipos de desafio. Não há
executor, gabarito privado ou rubrica de correção. O cálculo do Assessment usa
alternativas e gabaritos próprios, portanto não serve como corretor dessas tentativas.

| Caminho | Benefício | Trabalho necessário |
| --- | --- | --- |
| Revisão manual por ADMIN (proposta recomendada) | Permite avaliar texto e código sem executar código não confiável | Rubrica, evidências e feedback; acesso específico e restrito à revisão |
| Correção objetiva | Resultado reproduzível para alternativas com gabarito | Restringir tipos, autoria privada de gabaritos e snapshot coerente; texto livre permanece sem avaliação |

A recomendação manual não aprova automaticamente novos poderes de ADMIN.
A rota atual de tentativas continua limitada ao dono. Não haverá painel de revisão
no frontend nesta etapa, salvo mudança explícita de escopo.

## Decisões que o contrato deve resolver

1. Quem produz a evidência e quais tipos de desafio são atendidos.
2. Rubrica: critérios, escala, resultado parcial e feedback obrigatório.
3. Tratamento de evidências indisponíveis: testes, dicas e tempo não medidos
   ficam ausentes; tempo entre início e envio não é tempo efetivo de estudo.
4. Uma avaliação definitiva ou reavaliações versionadas; preservação do histórico.
5. Se UserSkill entra nesta Sprint ou fica explicitamente adiado.
6. Se incluído, valores iniciais por skill, fórmula de atualização, impacto dos
   pesos/dificuldade/repetição e confiança. Nenhum coeficiente está aprovado.
7. Como impedir atualização duplicada e garantir rollback de avaliação/progresso.
8. Dados públicos, dados privados de correção e erros por ator autorizado.

## Invariantes já documentadas

- EvaluationService avalia; SkillService atualiza habilidades.
- ChallengeService e routers não atualizam scores.
- Pesos vêm do contexto histórico da tentativa, não do catálogo editado depois.
- Não reduzir toda avaliação a um booleano de acerto.
- Score permanece em 0–1000; confiança em 0–1, sem confiança alta com pouca evidência.
- Feedback deve refletir evidências reais; sem inventar execução, dicas ou medição.
- Não modificar resposta submetida, snapshot ou avaliações do Assessment.

## Casos mínimos para o contrato

Tentativa não submetida; tentativa de terceiro; evidência inválida ou incompleta;
resultado parcial; repetição da mesma operação; duas avaliações concorrentes;
catálogo alterado após início; skill desativada; falha durante persistência.
Se houver UserSkill: inicialização, pesos, limites, consistência da confiança e
ausência de ganho duplicado. Exemplos numéricos dependem da fórmula definida.

## Validação desta etapa

Inspecionados modelos, schemas e service de tentativas e diagnóstico, além da
documentação prioritária. Não houve mudança de código, migration ou execução
de avaliação. Testes de implementação não se aplicam a esta alteração documental.

## Recorte manual proposto em 29/09/2026

Esta seção é uma proposta para decisão do usuário, não uma regra aprovada.

- ADMIN revisa somente tentativas submetidas, por uma operação específica de
  revisão. A consulta atual de tentativas continua exclusiva do dono.
- O revisor recebe resposta e snapshot; não precisa de e-mail, credenciais ou
  outros dados pessoais. O estudante consulta apenas a própria avaliação.
- A revisão registra evidência e feedback para cada skill do snapshot. Para cada
  skill, o revisor indica atendimento ausente, parcial ou completo dos requisitos
  explicitados no desafio e justifica a classificação com trechos/observações.
- Se o enunciado não permite verificar uma skill, registrar evidência insuficiente,
  sem converter ausência de evidência em erro ou acerto. Não penalizar critérios
  que não foram exigidos pelo desafio.
- Feedback geral obrigatório: pontos atendidos, pontos a melhorar e orientação
  de estudo. Orientação textual do revisor não é RecommendationService.
- Uma avaliação imutável por tentativa neste primeiro recorte. Reenvio idêntico
  pelo mesmo revisor retorna a avaliação existente; conteúdo diferente ou outro
  revisor concorrente recebe conflito. Correções/reavaliações ficam FUTURO.
- Proibir autorrevisão, inclusive quando o autor da tentativa é ADMIN.
- Sem nota numérica ou confiança inventadas: a primeira entrega registra a
  avaliação qualitativa. Atualização de UserSkill ficaria explicitamente adiada
  até definir a fórmula pedagógica, caso este recorte seja aceito.

### Exemplo de retorno qualitativo proposto

Desafio exige percorrer uma lista e somar somente valores positivos. A resposta
percorre a lista corretamente, mas soma também os negativos. O feedback aponta
esse comportamento e sua relação com as skills do snapshot. Não afirma que
testes foram executados; não deduz desempenho em habilidades não observáveis.
O revisor pode marcar atendimento parcial e recomendar revisar a condição do
filtro. Isso não altera o score do usuário nem o resultado de seu Assessment.

### Consequência para o roadmap

Esse recorte entrega Evaluation qualitativa, mas não fecha o ciclo adaptativo.
Antes de Recommendation, será necessário planejar UserSkill e sua atualização.
Essa mudança de recorte depende de escolha explícita; a Sprint atual permanece
em S7-T01, sem autorizar migrations ou endpoints por meio desta proposta.
