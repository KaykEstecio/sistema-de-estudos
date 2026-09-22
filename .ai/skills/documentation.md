# Documentação

`AGENTS.md` possui prioridade global.
`docs/CURRENT_SPRINT.md` define o escopo atual.
`docs/BUSINESS_RULES.md` define as regras de domínio.
`docs/ARCHITECTURE.md` define as decisões arquiteturais.
Esta skill não tem autoridade para mudar stack, arquitetura ou escopo.
Em caso de conflito, siga a documentação principal; caminhos partem da raiz do repositório.

## Quando usar

- Quando uma mudança autorizada afetar instruções, contratos ou decisões documentadas.
- Usar somente quando ativa; na Sprint 0, manter documentação da fundação.

## Responsabilidades

- Identificar o documento responsável pela informação antes de editar.
- Manter instruções de execução reproduzíveis e estado da Sprint verificável.
- Referenciar documentos existentes sem replicar a especificação.

## Regras obrigatórias

- README.md: execução local e estado real de backend, frontend e banco.
- AGENTS.md: regras globais de desenvolvimento; não reescrevê-las por preferência.
- docs/PROJECT_SPEC.md: visão e comportamento do produto.
- docs/ARCHITECTURE.md: stack, camadas, modelos e contratos técnicos.
- docs/BUSINESS_RULES.md: invariantes e decisões de domínio.
- docs/CURRENT_SPRINT.md: tarefas, escopo, Definition of Done e Active AI Skills.
- .env.example: nomes e exemplos seguros das variáveis necessárias; nunca valores reais sensíveis.
- Atualizar apenas o documento responsável por cada informação alterada.
- Marcar funcionalidades ainda não autorizadas como FUTURO, sem ativá-las implicitamente.
- Registrar testes executados e limitações antes de marcar tarefa ou Sprint concluída.
- Explicar decisões relevantes de forma breve e compreensível para o desenvolvedor.

## Não fazer

- Copiar toda a documentação para skills ou espalhar a mesma decisão em vários arquivos.
- Inventar comandos de execução, resultados de testes ou requisitos de negócio.
- Alterar arquitetura ou escopo por meio de atualização documental não autorizada.

## Checklist

- [ ] Cada informação foi atualizada no documento responsável?
- [ ] Links, caminhos e comandos correspondem ao estado real?
- [ ] O status diferencia trabalho concluído, pendente e FUTURO?
