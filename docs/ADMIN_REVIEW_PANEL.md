# Painel de revisão manual — Sprint 12A

Recorte autorizado em 05/10/2026, com deploy adiado pelo usuário.

## Uso

Entre com uma conta ADMIN existente. O login e o início levam à fila
`/admin/revisoes`; o menu **Revisar** também abre a fila. Cadastros comuns
continuam STUDENT. Este painel não cria nem promove administradores.

A fila apresenta apenas tentativas SUBMITTED sem avaliação, excluindo as
próprias do revisor, da mais antiga à mais recente (desempate por ID).
Há dez itens por página e atualização explícita. Abrir uma tentativa não a
reserva; outro administrador pode revisá-la enquanto a tela estiver aberta.

A tela `/admin/revisoes/:id` mostra o enunciado histórico, código inicial,
resposta enviada e habilidades/pesos do snapshot. IDs históricos das skills
são preservados; nomes atuais do catálogo não substituem esse contexto.

Preencha feedback geral (até 4.000 caracteres) e, para cada skill, classificação
e justificativa (até 2.000). Nenhuma classificação vem pré-selecionada.
Classificações: atendido, parcialmente atendido, não atendido e evidência
insuficiente. Confirmar registra avaliação definitiva; não há edição nesta etapa.
Regras de progresso e idempotência continuam no EvaluationService/SkillService.

Ao sair com texto não enviado, há confirmação; recarregamento/fechamento usa
aviso nativo. Não há rascunho persistido de avaliação. Expiração da sessão ainda
pode descartar o texto. Se o envio falhar, o formulário bloqueia novo POST até
consultar o resultado. Uma avaliação encontrada é mostrada como somente leitura;
se não existir, o texto permanece disponível para corrigir ou reenviar.

## API

Nova rota `GET /api/v1/reviews/attempts?limit=10&offset=0`, autenticada e exclusiva
ADMIN. Limit de 1 a 50; offset >= 0; parâmetros extras rejeitados. Resposta:
`items`, `total`, `limit`, `offset`. Cada item segue AttemptSummary e não inclui
resposta do aluno, identidade, e-mail ou credenciais. Total e página são lidos
num único statement. Respostas usam no-store; role é consultada no banco.

Consulta detalhada e POST continuam nos endpoints de avaliação existentes.
STUDENT recebe 403; ausência de autenticação recebe 401. A proteção visual não
substitui autorização no backend. Alterações entre consulta e POST são tratadas
pela transação existente; conflito não sobrescreve a avaliação de outro revisor.

Sem migration, nova dependência, execução de código ou mudança da política de
aprendizagem. Gestão visual de catálogo/usuários e edição de avaliação ficam
FUTURO, fora deste recorte.

## Validação

Build/TypeScript aprovados. 22 testes backend de avaliação aprovados com
PostgreSQL descartável, cobrindo acesso, fila, paginação/limites, exclusão de
rascunhos e tentativas próprias, remoção da fila, idempotência e concorrência.
Jornada de navegador passou a revisar pelo painel ADMIN; verifica feedback
literal, progresso do dono, fila vazia, desktop/mobile, proteção de saída e
reconciliação após resposta de envio perdida. Harness final: 15 testes aprovados,
nenhum skip/falha, cleanup confirmado. Testes usam contas descartáveis,
não criam administrador no banco de desenvolvimento.
