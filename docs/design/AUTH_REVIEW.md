# Referência visual e verificação — S6A-T02

Referência: auth-concept.png, gerada para esta tarefa; não é um asset renderizado
na interface. Controles e texto são HTML/React nativos. Direção: branco, teal,
tipografia sem serifa, formulário central sem cartão, bordas discretas.

Comparação visual no Chrome pelo navegador integrado à extensão (IAB indisponível):

- Conteúdo: título, subtítulo, campos, CTA e link inferior preservados.
- Layout: marca à esquerda, acesso ao cadastro à direita, formulário central.
- Tipografia: hierarquia de título, subtítulo e labels preservada; Arial local.
- Paleta: fundo branco, texto escuro e botão teal; sem assets decorativos.
- Espaçamento: controles amplos, sem contêiner/cartão adicional.
- Celular: verificado em 390×844, formulário em uma coluna sem cortes.

Referência inspecionada com view_image; implementação inspecionada via screenshot
do Chrome. Captura em dimensões nativas da referência e comparação por arquivo
de screenshot ainda não realizadas. Diferença intencional: botão sólido sem
textura da imagem gerada. Cadastro acrescenta nome e instrução de senha.

Fluxo real validado: cadastro de conta sintética local, erro de senha, login,
destino protegido, logout e perda da sessão após reload. Build/typecheck aprovados.
Conta de QA mantida no banco local; não houve alteração de contas existentes.
Expiração/401, acessibilidade completa e integração das próximas telas serão
verificadas no fechamento. Não representar esta etapa como frontend completo.
