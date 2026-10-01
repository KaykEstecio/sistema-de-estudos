# Sprint 10 — Experiência de desafios

Planejamento iniciado em 01/10/2026 após a Sprint 9, conforme a delegação do
usuário para escolher os próximos passos. Este recorte ainda não foi implementado.

## Objetivo e inventário

Completar a jornada entre recomendação e consulta da revisão manual.

| Necessidade | Estado e decisão |
| --- | --- |
| Descobrir desafio | Dashboard já oferece recomendações e detalhe |
| Iniciar/retomar | POST /api/v1/challenges/{id}/attempts existente |
| Consultar | GET /api/v1/attempts/{id} existente |
| Salvar | PATCH /api/v1/attempts/{id} existente |
| Enviar | POST /api/v1/attempts/{id}/submit existente |
| Recuperar tentativas | Falta listagem; incluir GET /api/v1/attempts paginado, exclusivo do dono |
| Ler revisão | GET /api/v1/attempts/{id}/evaluation existente |

Uma tentativa aberta deixa de aparecer nas recomendações. A listagem permite
retomá-la sem depender de uma URL guardada pelo aluno. Seu resumo usará o snapshot,
sem carregar todas as respostas no índice. Ordenação, limites e campos serão
fechados na S10-T02 em [ATTEMPT_EXPERIENCE_CONTRACT.md](ATTEMPT_EXPERIENCE_CONTRACT.md).
Não prever novas tabelas, migrations ou dependências.

Preservar [ATTEMPT_CONTRACT.md](ATTEMPT_CONTRACT.md) e
[EVALUATION_CONTRACT.md](EVALUATION_CONTRACT.md), sem mudar as regras de domínio.

## Jornada

1. Ação explícita no detalhe recomendado inicia/retoma e navega para
   `/tentativas/:id`. Nunca criar tentativa durante renderização.
2. Navegação autenticada oferece `/tentativas`, com paginação, loading,
   vazio, erro/retry e links para recuperar rascunhos e envios.
3. Detalhe apresenta snapshot, número, status e resposta. Enunciado e código
   são texto escapado; starter_code não substitui o rascunho automaticamente.
4. IN_PROGRESS permite edição textual e salvamento explícito, indicando
   alterações locais, salvamento em andamento, sucesso e falha.
5. Envio exige resposta não vazia e confirmação de que não será editável.
   Salvar alterações com sucesso antes de enviar; falha interrompe a sequência
   e preserva o texto. Não executar PATCH e submit em paralelo.
6. SUBMITTED mostra resposta somente leitura, avaliação disponível ou espera
   por revisão. Oferecer atualização manual e retorno ao painel, sem polling.

## Consistência e segurança

- Reutilizar AuthProvider e proteção de rotas. Incluir rotas válidas no retorno
  do login, preservando encaminhamento de contas sem onboarding ao perfil.
  Não adicionar requisito de onboarding/assessment à API de tentativas.
- Não persistir token ou rascunho em localStorage. Resposta salva vem do backend.
  Avisar sobre alterações não salvas ao sair, quando o navegador permitir;
  explicar que expiração de sessão/fechamento pode perder texto ainda não salvo.
- Bloquear ações simultâneas e ignorar respostas obsoletas após troca de rota/conta.
  Autorização e transições continuam sob responsabilidade do backend.
- Em falha de rede ao enviar, consultar estado antes de nova ação; preservar
  idempotência e não criar outra tentativa automaticamente.
- Reconciliar conflitos com o servidor sem sobrescrever silenciosamente edição
  local. Detalhar estados e recuperação na S10-T02.
- Usar snapshot mesmo após edição/desativação do catálogo. Retomada pela lista
  não depende de disponibilidade nas recomendações.
- Confirmar acesso à tentativa antes de interpretar 404 da avaliação como espera.
  Falhas de rede/servidor não significam ausência de revisão.
- Snapshot contém IDs de skills, não nomes históricos. Usar identificação por ID
  quando não houver nome disponível no contrato; não inventar nomes.
- INSUFFICIENT_EVIDENCE não significa reprovação. Frontend não calcula notas nem
  atualiza UserSkill; a política existente é aplicada pelo backend na revisão.

## Validação prevista

Backend: paginação, ordenação, autenticação, isolamento inclusive ADMIN,
catálogo inativo e ausência de escrita. Reutilizar testes de ciclo de vida.
Frontend: TypeScript/build e navegador desktop/mobile; iniciar, retomar após
login, salvar Unicode, falha antes do envio, confirmação, conflito, sessão
expirada, troca rápida de rota, avaliação pendente/disponível, texto escapado,
foco, teclado e ausência de overflow. Fechamento com API real e PostgreSQL
descartável. Planejamento documental não equivale a testes dessas funcionalidades.

## FUTURO

Execução de código, correção automática, editor especializado, autosave, anexos,
painel de revisão ADMIN, novas rubricas/políticas, score no frontend e deploy.
