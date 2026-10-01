# UserSkill — histórico do planejamento

Status: plano executado na Sprint 7A. Em 30/09/2026, o usuário delegou a escolha
e aprovou a política determinística. Cálculo, persistência, integração transacional
e consulta pelo dono foram implementados. Estado e validação em CURRENT_SPRINT.md;
contratos vigentes em USER_SKILL_POLICY_DRAFT.md, USER_SKILL_STORAGE.md e
USER_SKILL_API.md. O restante deste documento preserva o planejamento original:
alternativas e tarefas abaixo não representam pendências atuais.

## Dados disponíveis

- AssessmentResult: score por skill e confiança inicial 0, atualmente diagnóstico
  independente. Seu contrato não inicializa UserSkill automaticamente.
- Avaliação manual: classificação, justificativa e feedback, sem nota numérica.
- Tentativa: autor, snapshot com skills/pesos/dificuldade, número e datas.
- Ausentes: execução real, dicas utilizadas, tempo efetivo e confiança calibrada.

## Invariantes

Um registro por (user_id, skill_id), score 0–1000 e confidence 0–1.
SkillService será o único responsável pela atualização. Uma evidência não pode
ser aplicada duas vezes, inclusive sob concorrência ou repetição HTTP.
Preservar a origem da evidência, versão da política e valores antes/depois para
explicar mudanças. Usar pesos do snapshot e não o catálogo atual.
Classificação INSUFFICIENT_EVIDENCE não deve virar nota zero por conveniência.
Perfil declarado e passagem de tempo não constituem evidência de domínio.

## Modalidade escolhida

A avaliação qualitativa não estabelece uma escala numérica. Há dois caminhos
para planejar a atualização, sem modificar avaliações já gravadas:

| Caminho | Consequência |
| --- | --- |
| Política determinística sobre classificações (proposta preferida) | Preserva a revisão atual; exige definir a tradução das classificações e uma fórmula explícita |
| Nota numérica atribuída pelo ADMIN | Exige nova rubrica/versionamento e critérios para os revisores; avaliações antigas continuam qualitativas |

A primeira opção foi escolhida: o ADMIN continua registrando classificação e
justificativa; SkillService aplica uma política única, explícita e versionada.
Isso evita exigir uma nova nota subjetiva do revisor e preserva o contrato da
avaliação manual. É uma decisão de consistência técnica, não uma afirmação de
validade pedagógica. Nenhuma classificação recebeu valor numérico definitivo.

### Diretrizes para o contrato da política

- Preservar a avaliação original; registrar a conversão como evidência derivada.
- Separar o desempenho observado do score acumulado: MET não significa tornar
  automaticamente o usuário EXPERT, e NOT_MET não significa zerar seu histórico.
- INSUFFICIENT_EVIDENCE não atualiza score nem aumenta confiança de domínio.
- PARTIALLY_MET representa evidência parcial; a fórmula deve explicar seu efeito
  em relação ao score anterior e à dificuldade, sem bônus fixo universal.
- Versionar parâmetros e guardar a versão aplicada; mudanças futuras não
  recalculam silenciosamente avaliações já processadas.
- Não converter confiança em probabilidade de domínio sem calibração. Qualquer
  indicador inicial deve ser apresentado como provisório e sustentado por histórico.

A próxima tarefa é preparar uma política candidata com exemplos calculados de
inicialização, acerto parcial, dificuldade, repetição e evidência contraditória.
Essa candidata deve explicitar suas hipóteses; a escolha da modalidade não
constitui validação empírica de coeficientes nem autoriza implementar números ocultos.

## Sequência de tarefas proposta

1. Definir fonte inicial: adoção explícita de diagnóstico ou primeira evidência
   avaliável; comportamento sem diagnóstico, em múltiplos diagnósticos e em
   diagnóstico posterior à prática. Não sobrescrever progresso silenciosamente.
2. Definir fórmula com exemplos: classificação, pesos, dificuldade, repetição,
   resultado parcial e evidência insuficiente. Distinguir desempenho na tentativa
   de domínio acumulado. Definir como evidência contraditória afeta confiança.
3. Definir attempts/successful_attempts e last_practiced_at: o que é contado e
   qual data representa prática; avaliações tardias não devem parecer prática nova.
4. Implementar UserSkill e registro mínimo de aplicação de evidência, com migration,
   unicidade, constraints e índices necessários. Sem implementar Recommendation.
5. Implementar SkillService, transações e consulta exclusiva do próprio usuário.
   Definir ordem de aplicação das evidências e lock para avaliações concorrentes.
6. Testar inicialização, limites, rollback, idempotência, pesos, confiança, evidência
   tardia e isolamento entre contas. Documentar a política e suas limitações.

## Critérios de liberação para código

Contrato com política numérica, parâmetros e exemplos definidos; estratégia para
histórico existente e escopo explícitos. Não criar tabelas antecipadamente ou
alterar endpoints de Assessment/Evaluation antes dessas decisões.

## Validação deste planejamento

Política aprovada e exemplos em [USER_SKILL_POLICY_DRAFT.md](USER_SKILL_POLICY_DRAFT.md).
Simulação e testes do cálculo executados, sem atualização de dados persistidos.

Conferidos RN06–RN10, RN32–RN36, modelo UserSkill da arquitetura, contrato de
avaliação manual e fechamento da Sprint 7. Alteração apenas documental.
