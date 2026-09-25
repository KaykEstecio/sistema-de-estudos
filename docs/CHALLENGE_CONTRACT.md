# Contrato do catálogo de desafios — S5-T01

Status: persistência, schemas, repository, service e endpoints implementados
nas S5-T02 a T04; integração final validada na S5-T05. Decisões de domínio: BUSINESS_RULES.md,
RN13–RN16. Mantém monólito modular e padrões do catálogo existente.

## Recorte e decisões técnicas

POST/PATCH administrativos foram escolhidos por reutilizarem JWT, roles e
padrões de manutenção de Categories/Skills. Não criar importador adicional.
Sem exclusão física, autoria visual, tentativas, execução de código ou avaliação.

Os nove tipos da especificação são aceitos como classificação: QUIZ, CODE,
BUG_FIX, CODE_READING, REFACTORING, SQL, API, ARCHITECTURE e PROJECT. Não há
payload especializado por tipo nesta Sprint. Alternativas públicas de um QUIZ,
por exemplo, podem constar do enunciado; não existe campo de gabarito.

Objetivo e resultado esperado ficam na descrição, sem novos campos antecipados.
Todos os textos são conteúdo, nunca HTML confiável ou código executável.
module_id, ChallengeHint, soluções e critérios privados de correção ficam FUTURO.

## Entrada e limites

IDs são inteiros positivos até 2147483647. No JSON, números inteiros e booleanos
são estritos: não converter strings, floats ou booleanos em IDs/pesos.
Enums usam os valores exatos em maiúsculas. Rejeitar campos extras.

| Campo | Contrato de criação |
| --- | --- |
| title | String obrigatória, trim externo, 1–200 caracteres |
| description | String obrigatória, trim externo, 1–20000 caracteres |
| challenge_type | Enum obrigatório com os nove valores acima |
| difficulty | Enum obrigatório VERY_EASY/EASY/MEDIUM/HARD/VERY_HARD |
| difficulty_score | Inteiro obrigatório, 0–1000 |
| estimated_minutes | Inteiro obrigatório, 1–1440 |
| starter_code | String até 20000 caracteres ou null; padrão null; preservar espaços e quebras de linha |
| is_active | Booleano estrito, padrão false |
| skills | Lista obrigatória, 1–20 objetos com skill_id e weight; IDs distintos |

Cada weight é inteiro entre 1 e 100; soma exatamente 100, validada pelo service.
Título não é identificador único; IDs identificam desafios. Não adicionar slug.

PATCH exige ao menos um campo. Omitido preserva o valor; null só é aceito em
starter_code. skills, quando fornecido, substitui a lista completa. Sempre validar
o estado resultante, inclusive quando se altera apenas is_active ou descrição.
id, datas, module_id, solução, gabarito e ownership não são campos de entrada.

Exemplo estrutural de criação (skill_id deve existir; não é conteúdo revisado):

```json
{
  "title": "Somar dois inteiros",
  "description": "Objetivo: praticar soma. Implemente soma(a, b) retornando a + b para dois inteiros. Exemplo: soma(2, 3) deve retornar 5.",
  "challenge_type": "CODE",
  "difficulty": "VERY_EASY",
  "difficulty_score": 100,
  "estimated_minutes": 10,
  "starter_code": "def soma(a, b):\n    pass\n",
  "skills": [{"skill_id": 1, "weight": 100}]
}
```

## Saídas, filtros e permissões

ChallengeRead contém id, todos os campos de criação, created_at e updated_at
(datas com fuso). skills contém somente skill_id e weight, ordenados por skill_id.
Nenhum dado de tentativa, resposta correta, solução ou desempenho é retornado.
Lista e detalhe usam a mesma projeção; não duplicar contratos prematuramente.

| Operação | Acesso | Sucesso |
| --- | --- | --- |
| GET /api/v1/challenges | Usuário autenticado | 200, página |
| GET /api/v1/challenges/{id} | Usuário autenticado | 200, ChallengeRead |
| POST /api/v1/challenges | ADMIN | 201, ChallengeRead |
| PATCH /api/v1/challenges/{id} | ADMIN | 200, ChallengeRead |

Página: items, total, limit e offset. limit padrão 20, entre 1 e 100; offset
inteiro >= 0. Ordenação por id crescente; total considera os mesmos filtros e
visibilidade que items. Sem correspondências, retorna items vazio e total 0.
Offset além dos resultados retorna items vazio, preservando o total filtrado.

Filtros opcionais combinados por AND: skill (ID), difficulty (enum), type (alias
de challenge_type) e is_active (booleano). skill inexistente não gera erro:
retorna página vazia. Não aceitar filtros extras, inclusive completed.
GET de detalhe, POST e PATCH não aceitam query parameters.

ADMIN sem is_active vê ativos e inativos. STUDENT sem filtro ou com true vê
apenas disponíveis segundo RN13; is_active=false retorna 403. O aluno não vê
um desafio parcialmente vinculado a skills inativas, nem mesmo filtrando por
uma de suas skills ativas. Não filtrar por interesses ou objetivo pessoal.

## Erros

- 401: token ausente, inválido ou usuário não autenticável.
- 403: escrita por STUDENT ou filtro de inativos por STUDENT.
- 404: desafio inexistente/indisponível; skill inexistente em escrita administrativa.
- 409: soma dos pesos diferente de 100 ou tentativa de salvar desafio ativo com
  skill inativa. Não persistir alteração parcial.
- 422: entrada inválida, enum/limites, skills repetidas, null indevido, PATCH
  vazio, campos extras ou queries não suportadas.
- 500: falha inesperada, seguindo tratamento seguro existente, sem dados internos.

## Persistência e concorrência

Challenge: id Identity integer PK, campos da tabela de entrada exceto skills,
created_at/updated_at timezone-aware. Strings/enums com limites e checks;
is_active NOT NULL com default false; starter_code nullable. Defaults de datas
no banco, updated_at atualizado nas escritas. Não armazenar module_id ainda.

ChallengeSkill: chave primária composta (challenge_id, skill_id), weight inteiro
NOT NULL com check 1–100. FKs RESTRICT para challenges/skills. Índice em skill_id
para filtro inverso; a PK já atende busca por challenge_id. Em challenges,
índice de is_active/id para listagem; não indexar todos os filtros antecipadamente.
Checks para enums, difficulty_score, duração e limites de texto. Soma e existência
de ao menos uma skill são invariantes do service, não checks entre linhas.

ChallengeService controla transação e rollback. Repository consulta e faz flush,
sem commit. PATCH bloqueia a linha do desafio (FOR UPDATE, com releitura) antes
de compor o estado final e substituir vínculos. Alterações concorrentes são
serializadas; prevalece a última escrita executada sob lock nos campos enviados.
Não introduzir versionamento otimista nesta Sprint.

Na escrita, verificar skills sob lock compartilhado em ordem crescente de ID,
mantido até commit para coordenar com desativação concorrente. Uma desativação
posterior é permitida e passa a ocultar o desafio pela regra dinâmica de leitura.
Não modificar SkillService para atualizar desafios em cascata. Consultas públicas
devem aplicar visibilidade no banco antes de paginação/total, evitando N+1 ao
carregar os vínculos da página. Não prometer snapshot entre requisições paginadas.

## Validação prevista

- Migration: upgrade/downgrade/reaplicação, constraints e preservação de dados.
- Schemas: fronteiras, tipos estritos, nulos, enums e campos extras.
- Service: soma, vínculos inexistentes/inativos, substituição integral e rollback.
- HTTP: ADMIN/STUDENT, filtros, paginação, detalhe oculto e ausência de dados privados.
- Concorrência: PATCH simultâneo e publicação versus desativação de skill.
- Integração: criar inativo, publicar, consultar, desativar skill, verificar ocultação,
  reativar e verificar reaparecimento; nenhum efeito em assessment/UserSkill.

Skill challenge-design aplica-se ao recorte pedagógico do conteúdo. Suas partes
de hints, tentativa e feedback permanecem FUTURO conforme o escopo da Sprint.
