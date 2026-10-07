# Piloto de aprendizagem — Sprint 12C

Status: roteiro preparado; nenhuma sessão com aluno real realizada ou medida.
Complementa [STUDY_PRACTICE.md](STUDY_PRACTICE.md). Não adiciona funcionalidades.

## Preparação

Começar com uma sessão individual de aproximadamente 30 minutos; o tempo é uma
estimativa para organizar a conversa, não uma meta de desempenho. Usar alguém
que conheça variáveis, strings e inteiros. Se esses pré-requisitos faltarem,
registrar a lacuna e não interpretar a dificuldade como falha do aluno.

Iniciar o ambiente conforme [README](../README.md#iniciar-os-serviços). Usar uma
conta STUDENT de teste, separada da conta ADMIN que fará a revisão. O participante
digita sua própria senha; não registrá-la nas anotações. As tentativas e avaliações
ficam persistidas e a avaliação pode alterar o progresso dessa conta. Não usar a
conta pessoal do administrador para simular o aluno: autorrevisão é proibida.

Explicar: estamos testando a clareza do material e da interface. Pedir que a pessoa
descreva o que está tentando fazer. Não gravar tela por padrão nem anotar nome,
e-mail, senha ou outros dados pessoais. Usar um identificador como P01.

## Percurso inicial

1. Entrar como STUDENT e abrir **Estudar**, depois **Ver sequência de Python**.
   Observar se identifica **Seu próximo passo de leitura** e a aula
   **01 · Python: texto não é número** (conta ainda sem leituras marcadas).
   Pedir que explique o que espera aprender. Não explicar os botões antes da
   tentativa de uso. A sugestão orienta leitura; não classifica domínio.
2. Ler a explicação e prever o resultado do exemplo antes de olhar a resposta.
   Perguntar qual é a diferença entre somar números e concatenar textos.
3. Encontrar **Prática desta aula**, com **Prática 01 · Python: somar entradas
   numéricas** em destaque. Observar se identifica a entrega solicitada e
   distingue essa indicação do catálogo em **Explorar outros desafios de Python**.
4. Iniciar a tentativa, escrever a solução e a explicação, salvar o rascunho,
   voltar à lista e retomar. Confirmar com o aluno que a resposta foi preservada.
5. Enviar para revisão. Perguntar o que espera que aconteça a seguir. A resposta
   esperada é revisão manual; não sugerir que haverá execução ou correção imediata.
6. Em sessão separada, o ADMIN abre **Revisar**, lê a resposta e aplica os critérios
   públicos do snapshot. Justifica a classificação e orienta o próximo passo.
   Não preencher uma avaliação fictícia apenas para fazer o roteiro avançar.
7. O aluno atualiza a avaliação, explica o feedback e consulta o painel.
   Perguntar se consegue distinguir leitura concluída, desempenho na tentativa
   e progresso por habilidade. Não prometer um valor específico de score.

Se o aluno precisar de ajuda, registrar primeiro onde parou, depois o tipo de
ajuda dada: navegação, vocabulário, conceito ou solução. Não tratar resposta
assistida como evidência independente. Se ocorrer erro técnico, registrar a etapa
e a mensagem pública; não colar tokens, logs sensíveis ou respostas privadas.

## Pequena variação depois do feedback

Fora da avaliação do desafio original, pedir que preveja o resultado de
somar_textos('12', '-5') e explique o raciocínio sem copiar a aula. Resultado
esperado: inteiro 7; concatenar as strings produziria '12-5'. Esta observação é
qualitativa e não altera a classificação já registrada nem o score.

Caso o participante já conheça bem esse conteúdo, registrar esse fato. Sucesso
isolado não demonstra que a aula ensinou o conceito. Não usar velocidade ou
marcação de leitura como prova de domínio.

## Registro por sessão

Copiar este bloco para uma anotação local, preenchendo somente o observado.
Não versionar registros individuais ou capturas com dados pessoais.

```text
Participante: P__
Data:
Experiência/pré-requisitos declarados, sem identificação pessoal:
Dispositivo e navegador:
Aula e desafio:

Etapa | O que tentou | O que ocorreu | Ajuda fornecida | Dificuldade
Localizar aula:
Entender explicação:
Escolher prática:
Salvar e retomar:
Enviar e aguardar revisão:
Interpretar feedback/progresso:
Resolver a variação:

Conseguiu explicar o conceito? Evidência resumida:
Conseguiu resolver a variação? Independente / com ajuda / não observado:
O que mudaria na aula, segundo o participante:
Problema técnico reproduzível, se houve:
Próxima ação proposta e motivo:
```

## Como decidir o próximo ajuste

Separar dificuldade de navegação, pré-requisito ausente, ambiguidade do conteúdo
e falha técnica. Anotar a observação concreta antes de propor uma solução.
Um defeito reproduzível que impeça continuar merece correção imediata; dúvidas
de linguagem ou escolha de prática precisam de evidências do ponto de confusão.
Se não houver evidência suficiente, registrar como questão em aberto.

Consolidar apenas achados anônimos no projeto. Para cada ajuste, definir o
problema, o menor recorte de correção e como verificar com outra tentativa de uso.
Edição de aulas publicadas e trilhas continuam
FUTURO: um achado pode justificar propor esse escopo, não autoriza implementá-lo.
Não ampliar o catálogo apenas para compensar uma dificuldade ainda não entendida.

## Critério de conclusão do piloto

Há pelo menos uma sessão real registrada, distinção entre observações e
interpretações, e uma decisão fundamentada de corrigir, investigar ou manter.
Isso conclui uma rodada exploratória, não comprova eficácia pedagógica.
Até acontecer, manter a atividade de execução do piloto pendente na Sprint.
