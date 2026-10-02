# Frontend inicial — contrato S6A-T01

Status: planejamento definido; implementação nas S6A-T02 a T05.
Integra APIs existentes, sem alterar autenticação ou regras de domínio.

## Jornada e rotas

| Rota | Acesso e comportamento |
| --- | --- |
| / | Encaminha para /entrar sem sessão; com sessão, usa estado do onboarding |
| /entrar | Login com e-mail e senha; link para cadastro |
| /cadastro | Nome, e-mail e senha; sucesso encaminha ao login com confirmação |
| /onboarding | Autenticado; criação ou edição do perfil declarado |
| /diagnostico | Autenticado e onboarding concluído; seleção e retomada |
| /diagnostico/:id | Autenticado; consulta prova própria, questões ou resultado |
| demais | Página não encontrada com retorno seguro |

Cadastro usa POST /auth/register; não tratar cadastro como sessão autenticada.
Login usa POST /auth/login e confirma identidade em GET /auth/me antes de liberar
conteúdo. Sem destino pendente válido, login encaminha ao onboarding incompleto
ou /diagnostico. Destinos pendentes só aceitam rotas internas conhecidas, sem
redirecionamentos externos. Uma prova própria já criada pode ser consultada pelo
link direto mesmo se o perfil local estiver desatualizado; backend decide acesso.
ADMIN percorre a mesma jornada, sem painel administrativo nesta Sprint.

## Sessão e privacidade

Token Bearer mantido somente em memória, por um contexto React simples. Não
armazenar token ou senha em localStorage/sessionStorage, URL ou logs. Não há
refresh token, cookie de sessão ou endpoint de logout no backend atual.
Recarregar a página ou abrir outra aba exige novo login; informar esse comportamento
na documentação de uso. Logout limpa token, identidade e dados pessoais em memória.
Não sugerir que logout revoga o JWT no servidor; ele continua válido até expirar.

401 em chamada protegida encerra a sessão e leva ao login com mensagem de expiração.
401 no login permanece no formulário com erro de credenciais. Falha de rede ou 5xx
em /me permite tentar novamente, sem liberar rotas protegidas nem inventar identidade.
Respostas de requisições anteriores ao logout/troca de conta não podem repovoar
estado: cancelar requisições e conferir a sessão atual antes de aplicar resultados.

O servidor mantém toda autorização. Proteção de rotas melhora navegação, mas não
substitui checagem de token/ownership. Nenhuma regra depende de role enviada pelo
cliente. Renderizar textos como texto, sem HTML injetado.

## Cliente HTTP e integração

Instância Axios com baseURL /api/v1 e timeout definido. Bearer somente nessa
instância, evitando cabeçalho global para URLs externas. Serviços tipados por
domínio (auth, onboarding, catálogo e assessment), usando AbortSignal nas leituras.
Não instalar biblioteca de estado global, formulários ou cache sem necessidade.

Vite encaminha /api/v1 para http://127.0.0.1:8000 e mantém /health. React Router
organiza a navegação; Tailwind compõe estilos conforme stack oficial. Verificar
versões e documentação oficial ao configurar as dependências na T02.

Produção permanece FUTURO: Vercel precisa de fallback SPA para rotas de página e
encaminhamento /api/v1 ao backend, ou configuração explícita de origem da API/CORS.
Não supor que o proxy do Vite acompanha o build; não publicar nesta etapa.

## Formulários e comportamento

Cadastro respeita limites reais de UserCreate, incluindo senha de 15–128 caracteres,
sem trim da senha. Usar autocomplete adequado, labels e botão para mostrar/ocultar
senha. Login aceita senhas conforme LoginRequest. Não salvar credenciais.

Onboarding carrega GET /onboarding e categorias paginadas. Experiência usa exatamente
os cinco valores do backend, com rótulos em português. Selecionar 1–20 categorias
distintas, objetivo até 120 caracteres e descrição opcional até 2000. Perfil
incompleto usa POST; completo usa PATCH. Atualizar identidade após conclusão.
Catálogo vazio bloqueia envio e explica falta de opções. Paginar/carregar mais
sem presumir que a primeira página contém todos os interesses existentes.

Diagnóstico lista skills ativas das categorias escolhidas, por paginação de
GET /skills?category_id=...&is_active=true. Manter seleção de 1–3 skills entre
páginas/categorias e esclarecer que o usuário escolhe as relevantes ao objetivo.
POST /assessments cria prova; navegar imediatamente ao ID retornado.

GET /assessments/{id} é a fonte de respostas e resultado. Alternativas são radios
agrupados por questão. Salvar cada resposta explicitamente antes de avançar;
mostrar salvando/salva/erro, bloquear duplo envio e manter escolha local em falha.
Não permitir finalização enquanto houver resposta pendente ou gravação em curso.
POST /finish sem corpo conclui; em falha de rede, consultar novamente antes de
concluir que falhou. Reenvio de finish é seguro pelo contrato idempotente.

Resultado mostra acertos, total e score por skill. Exibir que é diagnóstico
provisório; confidence=0 significa ausência de calibração, não fracasso. Não
mostrar nível global, gabarito, evolução fictícia ou recomendações inexistentes.
Se nome de skill não estiver mais disponível, usar “Skill #ID” sem esconder resultado.

## Retomada e limites conhecidos

Após iniciar, persistir apenas o último ID de assessment em localStorage, com chave
separada pelo ID de usuário confirmado por /me. Não persistir respostas, resultados,
perfil ou token. Se armazenamento falhar, o link direto continua funcionando.
Esse ID é um atalho, nunca prova de acesso; toda retomada faz GET autenticado.

Na página /diagnostico, oferecer “Retomar diagnóstico” quando houver ID salvo,
e opção de informar o ID de uma prova própria. Mostrar o link da prova para guardar.
Ao receber 404, remover atalho inválido e mostrar estado indisponível. Ao receber
prova concluída, abrir seu resultado e permitir novo diagnóstico.

409 de criação pode significar prova aberta, onboarding incompleto ou conteúdo
insuficiente. Exibir mensagem segura do backend e ação pertinente, sem tentar
outro POST automaticamente. Sem ID local ou link, a API atual não descobre a prova
aberta; não prometer recuperação automática entre navegadores. Não adicionar
endpoint para contornar essa limitação nesta tarefa. Registrar como melhoria futura.

## Erros e interface

403: explicar falta de permissão. 404: recurso indisponível, sem dados de terceiros.
409: explicar conflito e permitir recuperar estado. 422: associar loc conhecido
ao campo correspondente; demais erros em resumo acessível. Falhas de rede/5xx
usam mensagem neutra e botão de tentar novamente, sem traceback ou erro bruto.
Não repetir automaticamente operações de escrita. Evitar duplicidade enquanto
requisição está em andamento e preservar dados digitados em falhas recuperáveis.

Estrutura visual: identidade CodeTrack, navegação curta “Meu perfil”/“Diagnóstico”
e “Sair”; formulário central com largura legível. Cadastro/login sem menus privados.
Paleta clara com contraste, títulos consistentes, sem gráficos ou métricas fictícias.
Celular em coluna única; desktop aproveita largura sem espalhar campos.
Foco visível, navegação por teclado, fieldset/legend, labels, aria-live para status
e resumo de erros. Não comunicar sucesso/erro somente por cor.

## Validação prevista

Login válido/inválido, cadastro duplicado, logout e 401; acesso direto e reload.
Perfil vazio/existente, seleção paginada e falhas de salvamento. Diagnóstico sem
conteúdo, aberto, completo, retomado, terceiro e indisponível. Verificar respostas
persistidas, finalização, isolamento entre contas e latência sem duplo envio.
Build/TypeScript e navegador em desktop/celular/teclado. Sem dados reais inventados.
# Atualização S9-T04 — painel pessoal

Rota autenticada /dashboard implementada sobre GET /api/v1/dashboard. Home e login
passam a encaminhar contas com onboarding concluído ao painel; sem onboarding,
mantêm /onboarding. Retorno após login aceita /dashboard na lista de rotas locais.
Acesso direto ao painel não exige onboarding e orienta configuração de interesses.

Tela mostra perfil declarado, contagens e progresso por skill com paginação de
dez registros, nomes atuais e estado inativo. Confiança é índice experimental,
não percentual de domínio. Loading, falha com retry, vazio e página excedente
têm estados próprios. Requisições são canceladas ao sair/trocar de página;
componente é remontado por identidade, sem cache persistente de dados pessoais.

Validação: build/TypeScript aprovados; Playwright com Chrome headless em
http://127.0.0.1:5173, API controlada, desktop 1440x1000 e mobile 390x844.
Login/redirecionamento, loading, paginação, falha/retry, conta sem progresso,
logout/troca de conta e foco por teclado passaram; sem erro JS, overlay ou overflow.
Browser plugin não disponível; usado Playwright do cache de ferramentas, sem
dependência adicionada ao projeto. Capturas e script temporários fora do repositório.
Backend real e acessibilidade completa ainda serão verificados na S9-T06.
Recomendações/detalhe somente leitura seguem na S9-T05; resolução é FUTURO.
# Atualização S9-T05 — recomendações no painel

DashboardRecommendations.tsx integra escolha explícita de categoria dos interesses,
catálogo ativo paginado de vinte skills e sugestões da API. Há estados locais de
loading, vazio, erro e retry. Categoria nova desmonta a seleção anterior; mudanças
de skill cancelam respostas antigas. A paginação do resumo mantém a seleção de
recomendações; enquanto recarrega, o último resumo permanece visível junto ao
estado de loading/erro. Nenhum valor zero é fabricado em falhas.

“Ver desafio” consulta enunciado e revalida presença nas sugestões atuais, inclusive
para ADMIN. Se a sugestão sair da lista ou o recurso ficar indisponível, informa e
recarrega. Detalhe somente leitura, com texto/código escapados e gestão de foco.
Não inicia tentativa ou executa código. O catálogo pode mudar após a leitura;
a resolução permanece FUTURO na Sprint 10.

Build e TypeScript passaram. Playwright/Chrome headless com API controlada em
http://127.0.0.1:5173, desktop 1440x1000 e mobile 390x844: catálogo paginado,
progresso paginado preservando seleção, respostas fora de ordem, retry, recurso
indisponível, categoria vazia, retorno de foco e texto escapado verificados.
Sem overlay, overflow horizontal ou erros inesperados de JavaScript/console;
404/503 foram simulados intencionalmente. Browser plugin ausente; Playwright
do cache, sem dependências novas no projeto. Script e screenshots fora do repo.
Integração real e revisão final continuam na S9-T06.

# Atualização Sprint 10 — tentativas e avaliação manual

Esta atualização substitui as indicações históricas de resolução FUTURO acima.
`/tentativas` lista rascunhos e envios do dono; `/tentativas/:id` lê o snapshot
histórico e permite editar/salvar enquanto IN_PROGRESS. O detalhe recomendado
oferece início/retomada por ação explícita. Login preserva retorno à tentativa
para conta com onboarding concluído; sessão permanece em memória.

Envio confirmado salva dirty antes de submit. Falha ao salvar impede envio;
resultado incerto/409 consulta o estado, preservando texto local divergente para
cópia. SUBMITTED é somente leitura e consulta avaliação manual, com atualização
explícita, feedback e resultados por skill. 404 revalida ownership antes de indicar
espera; falhas de conexão apresentam erro. Sem polling ou cálculo de score no UI.

React Router configurado com createBrowserRouter/RouterProvider para useBlocker;
avisos para links/histórico, logout e beforeunload. Nenhuma dependência nova.
Rascunho não salvo pode ser perdido em expiração/encerramento; salvamentos em
abas distintas continuam sujeitos ao último PATCH aceito. Limites informados.
Contrato e evidências por tarefa em ATTEMPT_EXPERIENCE_CONTRACT.md.

Jornada real de 02/10/2026 usou banco PostgreSQL descartável: recomendação, início,
salvamento Unicode, retomada após login, snapshot após desativação do catálogo,
envio, espera, revisão ADMIN pela API, feedback e progresso no painel passaram.
Score inicial 500 evoluiu para 504 com MET, dificuldade 100, peso 100 e tentativa 1,
conforme manual-skill-v1. Isolamento de outra conta e mobile verificados.
API temporária encerrada e banco removido; dados locais preservados.
