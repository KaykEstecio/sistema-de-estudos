# CodeTrack — Business Rules

## RN01 — Usuário

E-mail deve ser único.

---

## RN02 — Senha

Senha nunca será armazenada em texto puro.

---

## RN03 — Roles

Inicialmente:

```text
STUDENT
ADMIN
```

---

## RN04 — Administração

Usuários STUDENT não podem alterar conteúdos administrativos.

---

# Skills

## RN05

Cada Skill pertence a uma Category.

---

## RN06

Um usuário pode possuir apenas um UserSkill para cada Skill.

Constraint:

```text
UNIQUE(user_id, skill_id)
```

---

## RN07 — Score

Score deve permanecer:

```text
0 <= score <= 1000
```

---

## RN08 — Confidence

Confidence deve permanecer:

```text
0 <= confidence <= 1
```

---

## RN09 — Faixas

Escala inicial:

```text
0–199
BEGINNER

200–399
BASIC

400–599
INTERMEDIATE

600–799
ADVANCED

800–1000
EXPERT
```

---

## RN10

Não usar score isoladamente para determinar domínio.

Considerar também confidence e histórico.

---

# Skill Requirements

## RN11

Skills podem possuir pré-requisitos.

Exemplo:

```text
FastAPI

Python >= 400
HTTP >= 300
REST >= 300
```

---

## RN12

O recomendador deverá considerar pré-requisitos quando aplicável.

---

# Challenge

## RN13

Todo Challenge ativo deve possuir pelo menos uma Skill relacionada.

---

## RN14

A soma dos pesos de ChallengeSkill deverá ser:

```text
100%
```

---

## RN15

Difficulty Score deverá permanecer entre:

```text
0 e 1000
```

---

## RN16

Dificuldade textual:

```text
VERY_EASY
EASY
MEDIUM
HARD
VERY_HARD
```

---

# Attempt

## RN17

Toda tentativa pertence a:

```text
1 User
1 Challenge
```

---

## RN18

Usuário só poderá alterar suas próprias tentativas.

---

## RN19

Uma tentativa finalizada não deve ser sobrescrita como se nunca tivesse ocorrido.

---

## RN20

Nova tentativa deverá preservar histórico anterior.

---

## RN21

Rascunhos poderão ser salvos.

---

## RN22

A aplicação deve permitir retomar uma tentativa em andamento.

---

# Attempt Events

## RN23

Eventos relevantes podem ser registrados:

```text
STARTED
CODE_EXECUTED
ANSWER_CHANGED
HINT_REQUESTED
SUBMITTED
FAILED
PASSED
ABANDONED
RESUMED
```

Não registrar eventos irrelevantes.

---

# Hints

## RN24

Hints deverão ser progressivos.

Ordem conceitual:

```text
Hint 1
conceito

Hint 2
orientação técnica

Hint 3
pseudocódigo

Hint 4
orientação avançada

Solution
solução completa explicada
```

---

## RN25

Toda dica utilizada deve ser registrada.

---

## RN26

Visualizar solução completa deve ser registrado.

---

## RN27

Solicitar ajuda não significa automaticamente fracassar.

---

## RN28

Quanto maior a ajuda necessária, menor a evidência de domínio proveniente daquela tentativa.

Não aplicar penalização exagerada.

---

# Evaluation

## RN29

Uma tentativa não será avaliada somente como:

```text
correct / incorrect
```

A avaliação poderá considerar:

* resultado;
* dificuldade;
* tentativas;
* dicas;
* testes;
* tempo;
* nível atual.

---

## RN30

EvaluationService não deverá atualizar banco diretamente de forma desorganizada.

A atualização de domínio deverá ocorrer através do SkillService.

---

## RN31

ChallengeService não será responsável por atualizar Skills.

---

# Skill Update

## RN32

Depois de uma avaliação válida, Skills relacionadas poderão ser atualizadas.

---

## RN33

A atualização deverá considerar o peso do ChallengeSkill.

Exemplo:

```text
Logic = 60%
Loops = 40%
```

---

## RN34

Score deve ser sempre limitado entre 0 e 1000.

---

## RN35

Confidence deverá aumentar conforme novas evidências consistentes forem coletadas.

---

## RN36

Poucos exercícios não devem produzir confidence artificialmente alta.

---

# Recommendation

## RN37

A versão inicial será baseada em regras determinísticas.

Não utilizar Machine Learning ou LLM.

---

## RN38

O recomendador deverá considerar quando disponíveis:

* objetivo;
* interesses;
* UserSkills;
* confidence;
* knowledge gaps;
* SkillRequirements;
* histórico;
* dificuldade;
* challenges recentes.

---

## RN39

Challenges inativos nunca deverão ser recomendados.

---

## RN40

Challenges já concluídos recentemente deverão possuir prioridade reduzida, exceto quando utilizados como revisão.

---

## RN41

Challenges muito abaixo do nível deverão ser usados principalmente para revisão.

---

## RN42

Challenges muito acima do nível não deverão ser recomendados normalmente.

---

## RN43

Toda recomendação deverá possuir um motivo explicável.

---

## RN44

Distribuição conceitual de atividades:

```text
20% revisão
60% nível atual
20% acima do nível
```

Não tratar essa proporção como requisito matemático rígido.

---

# Knowledge Gap

## RN45

Uma knowledge gap representa uma Skill necessária ou relevante cujo nível está abaixo do esperado.

---

## RN46

Knowledge gaps relacionadas ao objetivo do usuário poderão receber maior prioridade.

---

# Onboarding

## RN47

O nível informado pelo usuário é apenas uma autoavaliação.

Não deve substituir dados reais de desempenho.

---

## RN48

Interesses podem ser múltiplos.

---

## RN49

Um objetivo poderá ser marcado como principal.

---

# Assessment

## RN50

Assessments deverão priorizar Skills relevantes ao perfil e objetivo.

---

## RN51

Resultado do Assessment poderá inicializar UserSkill.

---

## RN52

Assessment inicial não deve ser considerado avaliação definitiva.

Desempenho posterior deve recalibrar o perfil.

---

# Segurança

## RN53

A API nunca deverá retornar `password_hash`.

---

## RN54

Autorização deverá ser validada no backend.

---

## RN55

Variáveis sensíveis devem permanecer no ambiente.

---

# Desenvolvimento

## RN56

Não adicionar dependência sem problema concreto.

---

## RN57

Não adicionar arquitetura avançada preventivamente.

---

## RN58

Cada módulo deve possuir responsabilidade clara.

---

## RN59

Regra de negócio complexa não deve ficar no router.

---

## RN60

Nova funcionalidade deve respeitar a Sprint atual.
