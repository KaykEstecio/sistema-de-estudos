# Curadoria inicial de conteúdo — 06/10/2026

Lote: [fundamentals-v1.json](../content/study/fundamentals-v1.json).
Pedido do usuário: pesquisar referências institucionais e de educadores e
preparar conteúdo útil para o CodeTrack. Não se trata de ranking universal de
"melhores cursos"; a seleção prioriza autoria identificável, exercícios,
fundamentos compatíveis com o projeto e possibilidade de conferir os exemplos.

## Referências selecionadas

| Referência | Papel no lote | Limite da revisão |
| --- | --- | --- |
| [Harvard CS50P](https://cs50.harvard.edu/python/) | Sequência institucional de fundamentos de Python e aprofundamento | Página e estrutura consultadas; curso completo não realizado |
| [University of Helsinki, MOOC 2026](https://programming-26.mooc.fi/) | Referência de aprendizagem por exercícios | Página do curso e unidade de entrada de dados consultadas |
| [Curso em Vídeo, Mundo 1](https://www.cursoemvideo.com/curso/python-3-mundo-1/) | Complemento em português para iniciantes | Página do curso consultada |
| [Curso em Vídeo, aula 10 no YouTube](https://www.youtube.com/watch?v=K10u3XIf1-Q) | Complemento audiovisual sobre condições | Autoria e tema verificados; não assistido integralmente |
| [Python, tutorial](https://docs.python.org/3/tutorial/) | Conferência técnica de texto, números, condições e laços | Páginas introduction e controlflow consultadas |
| [PostgreSQL, consultas](https://www.postgresql.org/docs/current/tutorial-select.html) | SELECT, filtro e ordenação | Página consultada; exemplo testado no PostgreSQL local |
| [MDN, HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview) | Requisição, resposta e cabeçalhos | Página consultada; troca HTTP do lote é ilustrativa |
| [Pro Git](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) | Área de preparação e commit | Página consultada; comandos testados em repositório temporário |

Textos, exemplos e exercícios do lote são originais. Não foram copiados capítulos,
transcrições de vídeos ou exercícios avaliativos dessas instituições. Links são
referências e aprofundamento, não endosso, parceria ou certificação. Material
gratuito para consultar não implica permissão de republicação integral.

## Sequência sugerida

1. Python: texto não é número — tipos e conversão; depois prática sem copiar.
2. Lógica: decisões e casos de fronteira — condição e testes do limite.
3. Python: acumulador — rastreamento passo a passo e lista vazia.
4. SQL: selecionar, filtrar e ordenar — resultado esperado e alteração de filtro.
5. HTTP: pedido e resposta — leitura de uma troca e observação no navegador.
6. Git: commit consciente — editar, preparar e comparar diferenças.

As três últimas são introduções independentes e exigem seus próprios
pré-requisitos. Esta sequência é editorial, não uma trilha obrigatória do sistema.
A biblioteca continua ordenada por publicação. Não adicionar bloqueios artificiais.

Cada aula contém objetivo observável, pré-requisitos, estimativa de tempo,
explicação curta, exemplo, previsão de resultado, prática de transferência,
erros comuns e autocorreção. Tempos são estimativas editoriais, não medições.
Exercícios no texto são prática autônoma: não criam desafios avaliáveis nem score.

## Revisão e validação

- Seis entradas passaram por StudyCreate, com limites atuais do produto.
- Três exemplos Python executados, saídas comparadas ao arquivo do lote.
- SQL executado no PostgreSQL: resultado Bruno/35 e Lia/20, sem tabelas permanentes.
- JSON da troca HTTP validado; nenhuma chamada feita ao domínio ilustrativo.
- Git validado em repositório temporário: edição posterior ao add não entrou no
  primeiro commit. Nenhuma configuração Git global ou histórico do projeto alterado.
- Referências anexadas à explicação publicada, sem necessidade de nova migration.

Revisão técnica realizada pelo assistente; não houve avaliação independente de
professor nem medição de aprendizagem com alunos. Não declarar eficácia comprovada.
Na utilização inicial, observar se o aluno consegue explicar e resolver a variação
sem copiar; feedback e dificuldades reais orientam o próximo lote.

## Publicação local

O banco estava sem skills, conteúdos e ADMIN. O usuário designou uma conta
cadastrada para administração; ela foi promovida sem alteração de senha.
Criadas quatro categorias e cinco skills (python, logic, sql, http, git).
Seis conteúdos publicados por StudyService, IDs locais 1–6, com referências.
Não modificados interesses, tentativas, avaliações, scores ou leituras do usuário.
Não registrar o e-mail pessoal no repositório; a identidade foi conferida apenas
na operação local. Nenhuma conta/credencial foi criada pelo lote.

O JSON é a fonte editorial revisável, não um seed automático. Uma execução de
publicação confere conteúdo existente e não deve sobrescrevê-lo nem duplicá-lo.
Outros ambientes exigem mapear skills por slug e publicar com ADMIN autorizado;
os IDs locais não são portáveis. Correções de aulas já publicadas continuam
dependentes do recorte futuro de edição/versionamento.

## Segundo lote — 06/10/2026

Continuação autorizada pelo usuário: publicado
[practice-foundations-v1.json](../content/study/practice-foundations-v1.json).
Quatro aulas adicionais: funções com retorno, entrada inválida, testes de funções
e JOIN. IDs locais 7–10; biblioteca agora com dez conteúdos. Mesma conta ADMIN
autorizada, sem alterar score, leituras ou regras da aplicação.

Referências consultadas: Python (Defining Functions e Handling Exceptions),
[CS50P, Unit Tests](https://cs50.harvard.edu/python/notes/5/) e
[PostgreSQL 17, Joins](https://www.postgresql.org/docs/17/tutorial-join.html).
Cada aula contém seus links, pré-requisitos, prática e critérios de autocorreção.
Textos/exemplos originais; nenhuma reprodução de aulas ou avaliações externas.

Validação: quatro entradas aceitas por StudyCreate, três saídas Python conferidas,
defeito deliberado na fronteira detectado por AssertionError; consultas INNER e
LEFT JOIN verificadas no PostgreSQL, incluindo Dani/NULL na variante esquerda.
Não houve alteração de código funcional, dependência ou migration neste lote.

## Práticas avaliáveis — 07/10/2026

Recorte S12C autorizado e descrito em [STUDY_PRACTICE.md](STUDY_PRACTICE.md).
Dez desafios autorais em [challenges-v1.json](../content/study/challenges-v1.json),
derivados das dez aulas, com critérios públicos por skill e revisão manual-v1.
Publicados pela API administrativa com a conta já designada, IDs locais 1–10:
criação inativa seguida de ativação explícita, sem sobrescrever conteúdo existente.
O JSON é fonte editorial; não é seed ou importador automático.

Dez payloads validados por ChallengeCreate; referências cruzadas de aula/skill
conferidas. Casos de seis práticas Python/lógica e quatro consultas PostgreSQL
conferidos. Cenário Git executado em repositório temporário, incluindo alteração
depois de add; nenhuma configuração global modificada. HTTP revisado como troca
ilustrativa, sem chamadas ao domínio do exemplo. Dificuldades são estimativas.

Próximo passo pedagógico: experimentar com alunos e registrar dificuldades antes
de ampliar a biblioteca. A validação técnica não comprova eficácia educacional.

## Ordem de leitura — 07/10/2026

S12E: [reading-order-v1.json](../content/study/reading-order-v1.json) registra
as cinco sequências editoriais e suas justificativas. Dez aulas ordenadas pela
API ADMIN, em posições 10, 20 etc., sem IDs fixos no frontend. Python apresenta
funções antes das práticas que as utilizam; SQL apresenta SELECT antes de JOIN.
Números nos títulos históricos não determinam essa ordenação. Sem alterar textos,
leituras ou scores existentes. Não equivale a pré-requisito obrigatório.
