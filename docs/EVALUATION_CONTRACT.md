# Avaliação manual — contrato S7-T01

Recorte escolhido pelo usuário em 29/09/2026: revisão manual por ADMIN,
qualitativa e com feedback por skill. Modelos e migration implementados na S7-T02;
schemas, repository e service implementados na S7-T03; rotas integradas na S7-T05.
Migration validada somente em banco isolado.
Substitui as alternativas de EVALUATION_PLAN.md para esta Sprint.

## Regras e evidências

Somente tentativas SUBMITTED podem ser revisadas. Os nove tipos existentes são
atendidos como respostas textuais; nenhum código, URL ou arquivo é executado.
Usar resposta e snapshot históricos, inclusive quando o catálogo foi alterado
ou desativado. Nunca modificar tentativa ou seu estado para registrar avaliação.

Rubrica `manual-v1`: exatamente um resultado para cada skill do snapshot,
sem repetição ou skill adicional. Cada resultado contém skill_id, classificação
e justificativa textual de 1–2000 caracteres, após trim:

| Classificação | Significado |
| --- | --- |
| NOT_MET | Evidência observável de que requisitos ligados à skill não foram atendidos |
| PARTIALLY_MET | Parte desses requisitos foi atendida; explicar o que falta |
| MET | Requisitos observáveis ligados à skill foram atendidos |
| INSUFFICIENT_EVIDENCE | Resposta/enunciado não permite concluir; não equivale a erro |

Feedback geral obrigatório, texto de 1–4000 caracteres após trim: pontos atendidos,
limitações e orientação. Não impor requisitos ausentes no enunciado. A API valida
estrutura/completude; a qualidade da análise é responsabilidade do revisor.
Não alegar testes executados, uso de dicas ou tempo efetivo não registrados.
Dificuldade e número da tentativa são contexto, sem penalidades automáticas.

Sem score ou confidence nesta entrega. Não criar ou atualizar UserSkill; pesos
permanecem no snapshot para uso futuro, sem fórmula fictícia. O cálculo do
Assessment permanece intacto. Planejar atualização de habilidades antes de
Recommendation: revisão qualitativa, sozinha, não fecha o ciclo adaptativo.

## Acesso

ADMIN pode consultar uma tentativa submetida por ID para revisão e registrar
sua avaliação por rotas específicas. Não há listagem global ou painel nesta Sprint.
Não expor e-mail, credenciais ou outros dados do autor na revisão.
Autorrevisão é proibida, inclusive para ADMIN. Rotas existentes de attempts
continuam exclusivas do dono; não ampliar sua autorização.

O dono consulta sua avaliação por rota própria. Outro usuário, inclusive ADMIN,
recebe 404 nessa rota; o revisor usa a rota administrativa. Role é conferida
no backend, não recebida no payload. Falta de autenticação: 401.

## HTTP

Todas as respostas usam Cache-Control: no-store; IDs inteiros positivos até
2147483647. Rejeitar campos/query extras. Nenhum payload aceita identidade do
autor/revisor, datas, versão da rubrica, score ou confidence.

| Operação | Acesso | Sucesso |
| --- | --- | --- |
| GET /api/v1/reviews/attempts/{id} | ADMIN, não autor | 200 com AttemptRead e evaluation nullable |
| POST /api/v1/reviews/attempts/{id}/evaluation | ADMIN, não autor | 201 nova; 200 repetição idêntica |
| GET /api/v1/attempts/{id}/evaluation | Dono | 200 EvaluationRead |

POST recebe feedback e skills [{skill_id, classification, justification}].
EvaluationRead: id, attempt_id, rubric_version, feedback, skills, created_at.
Identidade do revisor fica registrada internamente; não é necessária ao payload
público. Resultados por skill ordenados por skill_id.

403: não ADMIN na rota de revisão ou autorrevisão. 404: tentativa inexistente,
tentativa de terceiro na rota do dono ou avaliação ainda ausente. 409: tentativa
não submetida, avaliação existente incompatível ou revisor diferente tentando
publicar novamente. 422: estrutura inválida ou conjunto de skills divergente.
Conferir permissão/ownership antes de revelar estado ou conteúdo.

## Persistência e concorrência

Tabela `attempt_evaluations`: id Identity PK; attempt_id FK RESTRICT UNIQUE;
reviewer_id FK users RESTRICT; rubric_version String(30), inicialmente manual-v1;
feedback String(4000); created_at DateTime UTC com fuso e default now().
Textos obrigatórios não brancos e versão fixada por constraint nesta entrega.

Tabela `attempt_evaluation_skills`: evaluation_id FK RESTRICT e skill_id integer
positivo como chave composta; classification String(30) com check dos quatro
valores; justification String(2000) não branca. skill_id é referência histórica
validada contra snapshot; não depende do estado atual do catálogo.

EvaluationService coordena autorização, validação, lock e commit/rollback.
Repository consulta, adiciona e faz flush, sem commit. Bloquear a tentativa
FOR UPDATE e reler antes de verificar avaliação existente. A constraint UNIQUE
é proteção adicional. Persistir avaliação e todos os resultados atomicamente.

Uma avaliação imutável por tentativa. Mesmo revisor e payload normalizado igual
(skills ordenadas, textos trim) retornam o registro salvo sem mudar timestamps.
Payload diferente ou outro revisor recebem 409. Sem PATCH/DELETE de avaliação;
reavaliação/correção ficam FUTURO. Não sobrescrever histórico silenciosamente.

## Testes exigidos

Schema: limites, enums, nulos, booleanos como IDs, duplicatas e campos extras.
Service: parcial/insuficiente, skills faltantes/adicionais, autorrevisão,
não submetida, repetição idêntica/divergente, catálogo alterado e rollback.
Integração: dono, outro estudante, ADMIN, concorrência entre revisores e ausência
de duplicatas. Migration: upgrade/downgrade isolados e constraints reais.
Nenhum teste deve atribuir nota numérica ou criar UserSkill neste recorte.
