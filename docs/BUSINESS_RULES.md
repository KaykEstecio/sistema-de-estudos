# CodeTrack — Business Rules

## RN01 — Usuário

E-mail deve ser único.

Decisão S1-T01: a comparação de unicidade ignora maiúsculas/minúsculas em
todo o endereço, para impedir contas duplicadas por variações de caixa.
Decisão S1-T02: remover espaços externos, validar o endereço com EmailStr e
armazenar o e-mail normalizado em minúsculas. Não remover pontos ou sufixos
de provedores. A validação de formato não confirma posse da caixa de e-mail.

---

## RN02 — Senha

Senha nunca será armazenada em texto puro.

Decisão S1-T04: cadastro aceita de 15 a 128 caracteres, incluindo espaços e
Unicode, sem exigir combinações de maiúsculas, números ou símbolos. Não fazer
trim, normalização ou truncamento. O mínimo considera ausência de MFA; o máximo
limita a entrada mantendo suporte a frases longas. Referência:
[OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html).

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

Decisões S2-T01 — catálogo (contratos definidos; implementação nas próximas tarefas):

- Categorias podem existir sem skills; skill exige categoria existente.
- ADMIN cria/edita categorias e skills e pode mover uma skill para outra categoria.
  STUDENT apenas consulta. Todas as consultas exigem autenticação.
- Slug identifica o recurso: único entre categorias e, separadamente, único
  entre todas as skills, inclusive inativas. Nomes não são únicos. Alterar nome
  não altera slug automaticamente; ADMIN pode editar o slug explicitamente.
- Skill inicia ativa, salvo criação explicitamente inativa por ADMIN.
  STUDENT só vê skills ativas; detalhe inativo responde como não encontrado.
  ADMIN pode consultar ativas e inativas. Desativação mantém o registro e vínculo.
- Categorias permanecem visíveis mesmo vazias ou sem skills ativas.
  Não há desativação de categoria nem exclusão física nesta Sprint.
- Nenhuma operação de catálogo cria UserSkill, altera score ou executa recomendação.

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

Decisões S5-T01 — catálogo de desafios (contrato; implementação pendente):

- ADMIN cadastra e edita; STUDENT apenas consulta. Toda operação exige
  autenticação. Não exigir onboarding, assessment ou UserSkill para consultar.
- Todo desafio cadastrado, inclusive inativo, possui de 1 a 20 skills distintas.
  Começa inativo por padrão; publicação é alteração explícita de is_active.
- Skills vinculadas devem existir. Um desafio ativo só pode ser gravado com
  todas as skills vinculadas ativas. Desafios inativos podem referenciar skills
  inativas para permitir manutenção administrativa.
- STUDENT só vê desafios ativos cujas skills estejam todas ativas. Desativar
  uma skill oculta esses desafios dinamicamente, sem apagar vínculos nem alterar
  is_active do desafio. Reativá-la restaura a visibilidade se as demais estiverem
  ativas. ADMIN pode consultar todos. Detalhe indisponível ao aluno retorna 404.
- Edição substitui a lista de skills inteira quando ela é fornecida, em uma
  transação com os demais campos; não há exclusão física nesta Sprint.
- Conteúdo é preparado por ADMIN: descrição deve apresentar objetivo de
  aprendizagem, enunciado, entradas/saídas e resultado esperado verificável.
  A API valida estrutura, não qualidade pedagógica. Não há seed automático.
- Tipos previstos na especificação são metadados de catálogo nesta Sprint;
  nenhum deles habilita submissão, execução ou correção. Dicas e soluções
  privadas não fazem parte dos campos armazenados ou retornados neste recorte.
- Não há atualização de UserSkill nem efeitos sobre resultados de assessment.

---

## RN14

A soma dos pesos de ChallengeSkill deverá ser:

```text
100%
```

Decisão S5-T01: weight é percentual inteiro entre 1 e 100, sem frações.
A soma deve ser exatamente 100 em toda criação/edição, mesmo inativa.
ChallengeService verifica a soma sobre o estado final e coordena a transação;
o banco garante limites individuais e unicidade de cada par desafio/skill.

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

Decisão S5-T01: difficulty e difficulty_score são informados pelo administrador.
Não há conversão automática ou faixas de equivalência aprovadas entre eles.
Ambos devem ser coerentes na revisão do conteúdo, sem inferir nível do usuário.

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

Decisão S6-T01: leitura também é exclusiva do dono, inclusive perante ADMIN.
Tentativa inexistente e tentativa de terceiro retornam 404 indistinguível.

---

## RN19

Uma tentativa finalizada não deve ser sobrescrita como se nunca tivesse ocorrido.

---

## RN20

Nova tentativa deverá preservar histórico anterior.

Decisões S6-T01 (contrato; implementação pendente): estados IN_PROGRESS e
SUBMITTED, sem aprovação/reprovação. Uma aberta por usuário/desafio; iniciar
novamente retoma a aberta. Após submit, novo início incrementa attempt_number.
Snapshot preserva enunciado, dificuldade e skills/pesos do início. Edição ou
desativação posterior não impede concluir a tentativa existente; novos inícios
exigem desafio e skills ativos. Não exigir onboarding ou assessment.

---

## RN21

Rascunhos poderão ser salvos.

Decisão S6-T01: resposta textual até 20000 caracteres para todos os tipos, sem
execução/correção. String vazia limpa rascunho; submit exige texto não branco.
Após submit, resposta e contexto não podem ser editados. Repetir submit retorna
o registro salvo, sem novas datas ou avaliação. Detalhes em ATTEMPT_CONTRACT.md.

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

Decisão S6-T01: não criar AttemptEvent neste recorte; timestamps da tentativa
registram início/submissão. GET e retomada não geram eventos ou alteram atividade.
Histórico de tentativas é preservado, mas não versões de cada rascunho.

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

Recorte S7 aprovado em 29/09/2026: avaliação manual qualitativa por ADMIN,
com evidência e feedback por skill, sem autorrevisão ou atualização de UserSkill.
Permissões, rubrica e idempotência no [contrato](EVALUATION_CONTRACT.md).
RN32–RN36 permanecem requisitos da futura atualização de habilidades; não há
coeficientes ou notas implícitos nas classificações qualitativas.

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

Recorte S7A aprovado: a [política manual-skill-v1](USER_SKILL_POLICY_DRAFT.md)
define a conversão experimental das classificações e substitui a ausência de
atualização do recorte S7 para avaliações novas. SkillService aplica progresso
na mesma transação da avaliação. Avaliações antigas não recebem backfill.
Assessment continua independente; seu resultado elegível serve apenas de base
na primeira evidência avaliável. Persistência e corte: [contrato](USER_SKILL_STORAGE.md).

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

Recorte S8: implementação determinística por skill focal explícita, conforme
[skill-focus-v1](RECOMMENDATION_POLICY.md). Usa interesses, referências por skill,
confiança e histórico do dono; explica cada sugestão. Objetivo textual não é
interpretado e pré-requisitos/metas de domínio permanecem FUTURO. Consulta sem
persistência ou alteração de progresso. Contrato em [RECOMMENDATION_API.md](RECOMMENDATION_API.md).

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

Decisão S3-T01: experiência declarada aceita NEVER_PROGRAMMED, BEGINNER, BASIC,
INTERMEDIATE e ADVANCED. É informação de perfil; não modifica score, confidence
ou UserSkill e não atribui um nível global de domínio.

---

## RN48

Interesses podem ser múltiplos.

Decisão S3-T01: conclusão exige de 1 a 20 categorias distintas existentes,
inclusive categorias sem skills ativas. Não há preferência ordinal neste fluxo:
todos os UserInterest recebem priority=1. A ordem enviada não representa ranking.
Na edição, uma lista fornecida substitui todos os interesses; ausência preserva
a seleção. Lista vazia, repetida ou com categoria inexistente é rejeitada.

---

## RN49

Um objetivo poderá ser marcado como principal.

Decisões S3-T01 para o recorte inicial:

- Onboarding concluído possui exatamente um objetivo principal. Este fluxo não
  cria objetivos secundários nem oferece escolha de is_primary pelo cliente.
- goal_type é texto curto informado pelo usuário; exemplos da especificação
  não constituem lista fechada. description é opcional.
- POST registra experiência, interesses e objetivo e marca onboarding_completed
  na mesma transação. Não há rascunho persistido nesta Sprint.
- POST repetido após conclusão retorna conflito; PATCH antes da conclusão também.
  PATCH válido altera o perfil mantendo a conclusão; não existe operação de reset.
- STUDENT e ADMIN consultam/editam somente seu próprio onboarding. Ownership e
  estado de conclusão são determinados pelo backend.
- Escritas simultâneas do mesmo usuário são serializadas. Duas conclusões
  concorrentes produzem um sucesso e um conflito; PATCH aplica apenas campos
  enviados sobre o estado atual, com a última escrita prevalecendo nesses campos.

---

# Assessment

## RN50

Assessments deverão priorizar Skills relevantes ao perfil e objetivo.

Decisão S4-T01 confirmada: usuário escolhe de 1 a 3 skills ativas dentro das
categorias dos seus interesses, conforme seu objetivo. Cada skill exige três
questões de múltipla escolha disponíveis. Sem mapeamento automático de texto livre.

---

## RN51

Resultado do Assessment poderá inicializar UserSkill.

Recorte S4-T01 confirmado: resultados persistidos somente em AssessmentResult;
não inicializar nem sobrescrever UserSkill nesta Sprint.

---

## RN52

Assessment inicial não deve ser considerado avaliação definitiva.

Decisão S4-T01: score representa acertos/questões × 1000, arredondado com metade
para cima. confidence=0 indica ausência de calibração de confiança de domínio,
não ausência de aprendizagem. Não classificar domínio global por esse resultado.
Finalização exige todas as respostas e é idempotente; repetir diagnóstico não
aumenta confidence. Contratos detalhados no documento vinculado à arquitetura.

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

## Área de estudo — decisão da Sprint 12B (06/10/2026)

Conteúdo manual pertence a uma skill ativa e só pode ser publicado por ADMIN.
Leitura é autenticada; a marcação de estudado é privada por usuário e idempotente.
Concluir leitura não inicializa UserSkill, não altera score, não gera SkillEvidence
e não representa domínio. Desafios e avaliações ligam materiais por skill sem
alterar as regras de recomendação. Contrato em [STUDY_AREA.md](STUDY_AREA.md).

Decisão S12C (07/10/2026): a leitura também oferece desafios do catálogo pela
mesma skill, sem exigir conclusão da aula e sem chamar essa lista de recomendação
personalizada. Critérios públicos pertencem ao enunciado e ao snapshot da tentativa;
classificação manual e atualização de UserSkill seguem as políticas existentes.
Recorte em [STUDY_PRACTICE.md](STUDY_PRACTICE.md).

Decisão S12D (07/10/2026): ADMIN pode indicar ou remover uma prática principal
por aula. Vínculo opcional, com desafio ativo que inclua a skill da aula e todas
as suas skills ativas. A consulta oculta dinamicamente indicações indisponíveis
ou incompatíveis, inclusive para ADMIN. Não exige conclusão da leitura, não
altera recomendação personalizada nem evidências de domínio. Critérios continuam
no snapshot da tentativa. Contrato em [LEARNING_IMPROVEMENTS.md](LEARNING_IMPROVEMENTS.md).

Decisão S12E (07/10/2026): ordem editorial opcional por habilidade, configurada
por ADMIN. A primeira leitura ainda não marcada é orientação de estudo, não
recomendação de domínio. Todas as aulas permanecem acessíveis; conclusão de outra
conta não interfere. Nenhuma atualização de UserSkill. Contrato e ordenação em
[STUDY_GUIDANCE.md](STUDY_GUIDANCE.md).
