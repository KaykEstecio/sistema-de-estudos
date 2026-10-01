# Sprint 6A — Frontend dos fluxos iniciais

Concluída em 28/09/2026. Etapa intermediária autorizada antes da Sprint 7.

## Entrega

- Cadastro, login, logout, identidade confirmada e sessão em memória.
- Perfil com experiência, interesses paginados e objetivo; criação e edição.
- Diagnóstico com seleção de 1–3 skills elegíveis, salvamento explícito,
  retomada por link/ID e resultado provisório por habilidade.
- Mensagens de vazio, conflito, falha e sessão expirada; layout responsivo.
- Nenhuma mudança de domínio, score global, inicialização de UserSkill ou
  recomendação. React Router/Tailwind seguem a stack documentada.

## Evidências

Chrome com API real e PostgreSQL temporário, dados sintéticos separados do banco
local. Criação/edição de perfil, paginação e limite de 20 interesses passaram.
Diagnóstico iniciado, respondido, retomado e concluído: 2/3 acertos, score 667/1000,
confiança 0. Controles bloquearam conclusão antes do salvamento.

Conflitos de conteúdo insuficiente e prova aberta exibidos sem perder seleção.
503 e timeout preservaram a alternativa; reenvio manual funcionou. Para timeout,
o servidor de teste atrasou 12 segundos, acima dos 10 segundos do cliente.
Conclusão salva cuja resposta foi substituída por 503 foi recuperada por GET.

401 encerrou sessão com aviso. Temporizador testado com `expires_in=3` somente na
resposta do login de teste: retorno automático ao login sem nova chamada protegida.
Segunda conta não recebeu atalho da primeira e obteve 404 ao tentar seu diagnóstico.

Login por Enter, radios por setas, salvamento por Tab/Enter e checkboxes por Espaço.
Screenshots inspecionadas no Chrome: desktop e viewport 390×844, incluindo perfil,
seleção, questões e resultado. Sem erros de execução registrados pelo console.

`npm --prefix frontend run build`: TypeScript e build aprovados.
`pytest backend/tests -q -W error --tb=short` com PostgreSQL isolado:
206 testes passaram em 75,69 s. `git diff --check` aprovado.

## Limites conhecidos

- Verificação manual no Chrome; não é auditoria integral de acessibilidade,
  teste com leitor de tela ou cobertura de todos os navegadores/dispositivos.
- Temporizador acelerado não equivale a aguardar 30 minutos nem valida relógio
  do sistema ou suspensão de aba. O backend continua validando o JWT.
- Falhas injetadas representam 503, timeout e perda do sucesso após persistência;
  não houve desconexão física da rede.
- Sem endpoint de descoberta de diagnóstico aberto: outro navegador precisa do ID.
- Token em memória: recarregar exige login. Respostas não salvas são locais.
- Produção, conteúdo pedagógico revisado e fidelidade visual completa ao conceito
  permanecem fora desta validação. Ver `design/AUTH_REVIEW.md`.

## Próximo passo

Definir tarefas e critérios da Sprint 7 — Evaluation antes de implementar.
