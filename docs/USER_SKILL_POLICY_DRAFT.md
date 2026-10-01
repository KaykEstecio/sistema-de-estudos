# Política aprovada de UserSkill — v1

Status: aprovada pelo usuário em 30/09/2026; cálculo puro implementado na S7A-T01.
Identificador: manual-skill-v1. Persistência e integração implementadas; não calibrada.
Escolha já feita: conversão determinística da classificação do ADMIN.
Os parâmetros abaixo são hipóteses de produto, não resultados científicos.

## Conversão e atualização do score

MET = 1; PARTIALLY_MET = 0,5; NOT_MET = 0. Esses números representam o resultado
observado, não o domínio do usuário. INSUFFICIENT_EVIDENCE não gera atualização,
contagem de prática avaliada ou aumento de confiança.

Para cada skill do snapshot:

```text
s = score atual, de 0 a 1000
d = difficulty_score do snapshot
w = peso da skill / 100
n = attempt_number, no mínimo 1
y = resultado observado (0, 0,5 ou 1)
p = limitar(0,5 + (s - d) / 1000, mínimo 0,05, máximo 0,95)
a = w / n
novo_score = arredondar_metade_para_cima(limitar(s + 40 × a × (y - p), 0, 1000))
```

p é uma expectativa heurística, não uma probabilidade calibrada. A escala 1000
usa a amplitude existente de score/dificuldade. Os limites 0,05/0,95 evitam
expectativas absolutas. O fator 40 limita cada evidência a uma pequena parte da
escala; deve ser revisto com dados. Peso distribui o efeito pelas skills;
1/n reduz influência de repetição do mesmo desafio. Não mede ajuda recebida.
Usar Decimal para aritmética e arredondamento reproduzíveis.

| Score anterior | Dificuldade | Resultado | Peso | Tentativa | Novo score |
| --- | --- | --- | --- | --- | --- |
| 500 | 500 | MET | 100% | 1 | 520 |
| 500 | 500 | PARTIALLY_MET | 100% | 1 | 500 |
| 500 | 500 | NOT_MET | 100% | 1 | 480 |
| 500 | 800 | MET | 100% | 1 | 532 |
| 500 | 200 | MET | 100% | 1 | 508 |
| 500 | 500 | MET | 60% | 1 | 512 |
| 500 | 500 | MET | 100% | 2 | 510 |

Um parcial pode aumentar ou diminuir o score conforme expectativa anterior.
Pesos baixos/repetições podem produzir mudança arredondada zero; ainda são
evidência registrada. Isso deve ficar explícito ao usuário.

## Inicialização aprovada

Na primeira evidência avaliável, usar como base o último diagnóstico concluído
para a skill antes do início daquela tentativa, se existir; registrar sua origem.
Sem diagnóstico elegível, usar 500 como ponto neutro técnico, confiança zero;
não apresentar esse ponto como domínio comprovado ou nível definitivo.
Inicialização aceita como hipótese experimental nesta versão.

Não criar UserSkill apenas por cadastrar interesse ou concluir Assessment.
Um diagnóstico posterior não sobrescreve progresso. Manter a base escolhida
imutável após inicialização. A primeira evidência aplica a fórmula à base.

## Confiança experimental, separada de sucesso

Confiança indica estabilidade/quantidade da evidência, não aprovação. Para cada
evidência avaliável guardar a e o resíduo r = y - p, calculado antes da atualização.
Acumular M = soma(a), R = soma(a × r), Q = soma(a × r²).

```text
variância = máximo(0, Q/M - (R/M)²)
confidence = limitar((M / (M + 20)) × máximo(0, 1 - variância), 0, 0,95)
```

M=0 implica confiança 0. Arredondar a seis casas decimais somente na saída;
precisão de armazenamento dos acumuladores deve ser definida no contrato técnico.
O parâmetro 20 mantém confiança baixa com pouca evidência: uma unidade de peso
gera no máximo 0,047619; cinco, 0,2; vinte, 0,5. Resíduos inconsistentes reduzem
o indicador em relação ao mesmo volume consistente; não há garantia de redução
a cada nova contradição, pois quantidade também aumenta.

Este indicador não demonstra que a estimativa está correta: revisões repetidas
com o mesmo viés podem ser consistentes. O teto 0,95 não significa 95% de acerto.
Não usar para decisões de alto impacto nem como probabilidade de domínio.

## Aplicação e histórico aprovados

- Uma aplicação por (evaluation_id, skill_id), inclusive registro de descarte por
  evidência insuficiente, para evitar duplicação e permitir auditoria.
- Nova revisão e atualização no mesmo commit, coordenadas por services separados.
- Avaliações já existentes não são convertidas silenciosamente; eventual carga
  retroativa exige tarefa explícita com versão e ordem definidas.
- Serializar por usuário; aplicar na ordem de processamento confirmada e registrar
  essa ordem. Revisão tardia não reescreve histórico nem simula prática recente.
- attempts conta evidências avaliáveis aplicadas; successful_attempts conta MET.
- last_practiced_at é o máximo submitted_at das evidências aplicadas, não a data
  da revisão. Preservar score/confiança antes/depois e parâmetros usados.
- Nenhuma atualização para evidência insuficiente isolada; não criar perfil vazio.

## Verificação exploratória executada

Simulação local sem banco: 5.292 combinações de score, dificuldade, peso e número
de tentativa. Verificados limites 0–1000, ordenação NOT_MET ≤ PARTIALLY_MET ≤ MET,
ausência de perda em MET e de ganho em NOT_MET. Exemplos da tabela calculados.
Isso verifica propriedades aritméticas, não eficácia pedagógica. Não equivale aos
testes de integração, calibração e concorrência da implementação futura.

## Implementação incremental

Conjunto aprovado: ponto inicial, mapeamento, fator 40, expectativa, repetição
e indicador de confiança. Cálculo isolado usa contexto Decimal local com precisão
28 e ROUND_HALF_UP, independente do contexto do chamador. Acumuladores não são
arredondados a seis casas; somente a saída de confidence. Precisão persistida
foi especificada na S7A-T02 em USER_SKILL_STORAGE.md para garantir reprodução da sequência.
24 testes passaram em 0,56 s, incluindo os exemplos e a grade de 5.292 cenários.
S7A-T03 integra avaliações novas e progresso na mesma transação. Próximo passo:
consulta exclusiva pelo dono e testes integrados adicionais, antes de Recommendation.
