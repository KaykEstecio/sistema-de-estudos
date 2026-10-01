# Política de recomendação — skill-focus-v1

Decisão inicial tomada por delegação do usuário em 30/09/2026: “pode prosseguir,
escolhendo o melhor para o projeto”. Parâmetros abaixo são escolhas experimentais
de produto, não resultados de calibração. Não modificam manual-skill-v1.

## Recorte

O usuário escolhe uma skill ativa dentre suas categorias de interesse. O serviço
calcula até cinco sugestões por padrão, no máximo dez, sob demanda. Não grava
Recommendation nem cria UserSkill. A entidade conceitual Recommendation da
arquitetura permanece reservada para um futuro histórico de sugestões.

Escolha: priorizar simplicidade, explicações verificáveis e primeira prática
acessível. Objetivo textual não é interpretado; não há pré-requisitos cadastrados
nem metas de domínio por objetivo. Não anunciar lacunas ou requisitos satisfeitos.

## Referência por skill envolvida

Aplicar a tabela a **todas** as skills do desafio, inclusive secundárias fora dos
interesses. A seleção de interesse restringe a skill focal, não oculta as demais.

| Dados disponíveis | Referência r | Teto de dificuldade |
| --- | --- | --- |
| UserSkill com confidence >= 0,20 e attempts >= 5 | score | min(1000, score + 200) |
| Demais UserSkills | score | min(1000, score + 100) |
| Sem UserSkill, com diagnóstico concluído | score do diagnóstico | min(1000, score + 100) |
| Sem ambos | 100, apenas âncora de seleção | 200 |

UserSkill sempre prevalece sobre diagnóstico posterior. Na ausência dele, usar o
último AssessmentResult do dono para a skill, com completed_at <= instante da
consulta; desempatar por completed_at DESC e Assessment.id DESC. Diagnóstico
aberto é ignorado. Seu uso na seleção não o transforma em progresso persistido.

Confiança baixa restringe a margem de progressão, sem reduzir o score. O limiar
0,20 e cinco evidências permitem experimentar progressão após algum histórico;
não significam domínio confirmado. Evidência ausente nunca assume score pessoal
500. A âncora 100/teto 200 favorece conteúdo introdutório enquanto se coleta
evidência. Um diagnóstico pode orientar a primeira prática sem esperar revisão.

## Elegibilidade e histórico

1. Desafio ativo, pelo menos uma skill, todas ativas e incluindo a focal.
2. Dificuldade d deve ser <= teto de **cada** skill. Uma skill forte não compensa
   dificuldade excessiva para outra, mesmo se esta possuir peso baixo.
3. Excluir desafios com qualquer tentativa IN_PROGRESS do dono. Retomada continua
   no fluxo de tentativas, sem criar outra tentativa pela recomendação.
4. Excluir desafios com qualquer tentativa SUBMITTED ainda sem AttemptEvaluation
   do dono. Evita repetir enquanto a evidência aguarda revisão. Avaliação antiga
   ou INSUFFICIENT_EVIDENCE conta como revisão recebida, sem presumir sucesso.
5. Entre os restantes, “recente” significa última submitted_at >= agora - 7 dias
   e <= agora. Exatamente sete dias conta como recente. Nenhuma data de revisão
   renova essa janela. Sem submissão, não é recente.

Consulta usa um único agora UTC fornecido à política. Mesmos dados e mesmo agora
produzem o mesmo resultado; avanço do tempo pode mudar a prioridade. Datas futuras
de prática são inconsistentes: excluir o candidato afetado, sem usar como evidência.
Sem elegíveis, devolver lista vazia; não aumentar os tetos automaticamente.
Catálogo comum continua acessível para escolha manual, inclusive primeira prática.

## Tipo e ordenação

Para candidato elegível, delta_i = d - r_i; maior_delta = max(delta_i).
Determinar um único tipo nesta ordem:

- Se alguma skill não possui UserSkill: EXPLORATION (evidência inicial/provisória).
- Senão, se maior_delta < -200: REVIEW (abaixo de todas as referências).
- Senão, se maior_delta > 100: PROGRESSION.
- Senão: PRACTICE.

Limites inclusivos: -200 e +100 ainda são PRACTICE. Um desafio abaixo de uma skill
e próximo de outra não é rotulado como revisão de todas. Explicar diferenças por
skill. Tipos descrevem a relação com a evidência, não aprovação pedagógica.

Ordenar ascendentemente pela tupla:

```text
(recente ? 1 : 0,
 prioridade_tipo,
 soma(peso_i * abs(d - r_i)),
 challenge_id)
```

prioridade_tipo: PRACTICE e EXPLORATION = 0, PROGRESSION = 1, REVIEW = 2.
Os pesos inteiros somam 100; não é necessário dividir para ordenar. Distância
ponderada só desempata candidatos que já passaram pelo teto individual. Ela não
é armazenada nem apresentada como nível global do usuário.

Revisão também recebe redução de prioridade por recência nesta versão. Não há
espaçamento adaptativo ou quota 20/60/20 obrigatória. Cada desafio aparece uma vez;
pegar os primeiros limit após ordenar todo o conjunto elegível, sem pré-corte
arbitrário de candidatos por ID.

## Explicações

Retornar tipo, sinal de prática recente e referências por skill (fonte, score
quando houver, confiança apenas para UserSkill). Gerar motivo por templates no
service, usando os mesmos dados da classificação, sem LLM.

Exemplos: “Prática introdutória para coletar evidências em SQL”; “Dificuldade
próxima das referências disponíveis em Python e SQL”; “Progressão moderada em
SQL com histórico de prática”; “Revisão abaixo das referências disponíveis”.
Acrescentar indicação de diagnóstico provisório/evidência limitada e de prática
nos últimos sete dias quando aplicável. Não chamar confiança de chance de sucesso.

## Exemplos verificáveis

Todos os candidatos ativos e sem impedimentos históricos, salvo indicação.

| Contexto | Candidato | Resultado |
| --- | --- | --- |
| SQL sem progresso/diagnóstico | d=100 / d=201 | EXPLORATION / excluído |
| SQL diagnóstico 600, sem UserSkill | d=650 / d=701 | EXPLORATION / excluído |
| SQL score 500, confidence 0,10 | d=600 / d=601 | PRACTICE / excluído |
| SQL score 500, confidence 0,20, attempts 5 | d=650 / d=701 | PROGRESSION / excluído |
| Python 800 e SQL 200, ambos com margem 100 | d=400, pesos 90/10 | excluído por SQL, apesar do peso baixo |
| Python 800 e SQL sem evidência | d=200 / d=201 | EXPLORATION / excluído |
| Skill score 700 | d=499 / d=500 | REVIEW / PRACTICE |
| Mesmo tipo, uma skill score 500 | d=480 e d=550, não recentes | 480 primeiro: distância 2000 < 5000 |
| Mesmo tipo, score 500 | d=500 recente e d=550 não recente | 550 primeiro |
| Mesmo tipo, distância e recência | IDs 9 e 3 | ID 3 primeiro |
| Tentativa submetida há 20 dias, avaliada hoje | d elegível | não recente |
| Tentativa aberta ou submissão sem revisão | d elegível | excluído |

## Limitações e evolução

Dificuldade única do desafio é comparada a todas as skills: aproximação
conservadora até existir dificuldade por skill. Pode produzir poucas sugestões,
principalmente em desafios mistos. O produto deve explicar a ausência e melhorar
o catálogo, sem mascará-la com regras relaxadas. Não mede efetividade pedagógica.

Política versionada na resposta; alterações futuras exigem documentação e testes.
Persistência de sugestões, metas por objetivo, SkillRequirement, recomendações
sem escolha focal e análise de eficácia permanecem FUTURO.

## Implementação S8-T04

Seleção pura em backend/app/modules/recommendations/policy.py. Contextos e
resultados são dataclasses imutáveis; relógio explícito e nenhuma consulta ou
escrita. SkillContext mantém evidência por skill; Candidate reúne links e flags
do histórico; Selection retorna tipo, recência e referências usadas.

Repository/service ainda devem resolver autorização, diagnóstico elegível e
histórico do dono. Seleção não substitui essa autorização. A âncora técnica de
ausência de evidência fica separada de score=None; o futuro service deve construir
a resposta pelos schemas, sem serializar diretamente as estruturas internas.

Testes incluem grade de 3.280 combinações, 120 permutações de candidatos,
fronteiras da confiança/quantidade/recência, skills secundárias fracas ou
desconhecidas, precedência de progresso, catálogo inativo, histórico pendente,
ausência de candidatos e entradas inconsistentes. Validam determinismo e contrato,
não eficácia pedagógica. Resultado dos comandos registrado na Sprint atual.
