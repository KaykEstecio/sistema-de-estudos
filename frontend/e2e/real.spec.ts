import { test, expect, login, noOverflow } from './helpers'

test('ciclo real: tentativa, revisão e progresso do dono', async ({ page, request, context }, testInfo) => {
  if (process.env.CODETRACK_QA_DISPOSABLE !== '1' || !process.env.QA_PASSWORD) throw new Error('Execute a jornada real pelo harness Python descartável.')
  const password = process.env.QA_PASSWORD
  const challengeId = Number(process.env.QA_CHALLENGE_ID)
  const skillId = Number(process.env.QA_SKILL_ID)
  expect(Number.isSafeInteger(challengeId) && challengeId > 0).toBe(true)
  const api = 'http://127.0.0.1:8100/api/v1'
  const auth = await request.post(`${api}/auth/login`, { data: { email: 'reviewer@qa.example', password } })
  expect(auth.status()).toBe(200)
  const headers = { Authorization: 'Bearer ' + (await auth.json()).access_token }
  page.on('dialog', dialog => dialog.accept())
  await page.goto('/'); await login(page, 'owner@qa.example', password)
  await page.getByLabel('Área de interesse').selectOption({ label: 'Programming' })
  await page.getByRole('radio', { name: 'Python', exact: true }).check()
  await page.getByRole('button', { name: 'Ver desafio: First practice' }).click()
  await page.getByRole('button', { name: 'Iniciar ou retomar tentativa' }).click()
  const editor = page.getByLabel('Resposta em texto ou código')
  await expect(editor).toHaveValue('')
  const attemptId = Number(page.url().split('/').pop())
  const answer = '  print(1 + 1)\nA soma é 2. 😀  '
  await editor.fill(answer); await page.getByRole('button', { name: 'Salvar rascunho' }).click()
  await expect(page.getByText('Rascunho salvo.', { exact: true })).toBeVisible()
  const changed = await request.patch(`${api}/challenges/${challengeId}`, { headers, data: { title: 'Changed catalog title', is_active: false } })
  expect(changed.status()).toBe(200)
  await page.getByRole('link', { name: 'Voltar às tentativas' }).click()
  await page.getByRole('link', { name: 'Retomar: First practice' }).click()
  await expect(editor).toHaveValue(answer)
  await page.reload(); await login(page, 'owner@qa.example', password)
  await expect(editor).toHaveValue(answer)
  await page.getByRole('button', { name: 'Enviar para revisão' }).click()
  await expect(page.getByText('Sua resposta aguarda revisão manual', { exact: false })).toBeVisible()
  await expect(editor).toHaveCount(0)
  await expect(page.getByRole('link', { name: 'Revisar', exact: true })).toHaveCount(0)
  const adminPage = await context.newPage()
  adminPage.on('dialog', dialog => dialog.accept())
  await adminPage.goto('/entrar'); await login(adminPage, 'reviewer@qa.example', password)
  await adminPage.getByRole('link', { name: 'Revisar', exact: true }).click()
  await adminPage.getByRole('link', { name: `Revisar tentativa #${attemptId}`, exact: true }).click()
  await expect(adminPage.locator('.attempt-context')).toContainText(answer.trim())
  await adminPage.getByLabel('Feedback geral', { exact: true }).fill('Adição explicada com clareza. <b>Texto literal</b>')
  await adminPage.getByLabel(`Classificação da skill #${skillId}`, { exact: true }).selectOption('MET')
  await adminPage.getByLabel(`Justificativa da skill #${skillId}`, { exact: true }).fill('A resposta demonstra soma e resultado.')
  adminPage.removeAllListeners('dialog')
  const dismissed = new Promise<void>(resolve => {
    adminPage.once('dialog', async dialog => { await dialog.dismiss(); resolve() })
  })
  await adminPage.getByRole('link', { name: 'Voltar à fila de revisões' }).click()
  await dismissed
  await expect(adminPage.getByLabel('Feedback geral', { exact: true })).toHaveValue('Adição explicada com clareza. <b>Texto literal</b>')
  adminPage.removeAllListeners('dialog')
  adminPage.on('dialog', dialog => dialog.accept())
  await noOverflow(adminPage)
  await adminPage.screenshot({ path: testInfo.outputPath('admin-desktop.png'), fullPage: true })
  await adminPage.setViewportSize({ width: 390, height: 844 }); await noOverflow(adminPage)
  await adminPage.screenshot({ path: testInfo.outputPath('admin-mobile.png'), fullPage: true })
  // The server commits, but the browser receives an error: reconcile without a second POST.
  let submissions = 0
  await adminPage.route(`**/reviews/attempts/${attemptId}/evaluation`, async route => {
    submissions += 1
    const response = await route.fetch()
    expect(response.status()).toBe(201)
    await route.fulfill({ status: 503, contentType: 'application/json', body: '{"detail":"Response unavailable"}' })
  })
  await adminPage.getByRole('button', { name: 'Registrar avaliação', exact: true }).click()
  await expect(adminPage.getByRole('alert')).toContainText('Não foi possível confirmar o envio')
  await expect(adminPage.getByRole('button', { name: 'Registrar avaliação', exact: true })).toBeDisabled()
  await adminPage.getByRole('button', { name: 'Consultar resultado do envio' }).click()
  await expect(adminPage.getByRole('status')).toContainText('Avaliação registrada')
  expect(submissions).toBe(1)
  await expect(adminPage.locator('main b')).toHaveCount(0)
  await adminPage.getByRole('link', { name: 'Voltar à fila de revisões' }).click()
  await expect(adminPage.getByText('Nenhuma revisão nesta página.', { exact: true })).toBeVisible()
  await adminPage.close()
  await page.getByRole('button', { name: 'Atualizar avaliação' }).click()
  await expect(page.getByRole('heading', { name: 'Feedback geral' })).toBeVisible()
  await expect(page.locator('.evaluation-skills')).toContainText('Atendido')
  await expect(page.getByRole('link', { name: 'Revisar conteúdos desta habilidade' })).toHaveAttribute('href', `/estudar?skill=${skillId}`)
  await expect(page.locator('main b')).toHaveCount(0)
  await page.locator('.attempt-evaluation').scrollIntoViewIfNeeded(); await noOverflow(page)
  await page.screenshot({ path: testInfo.outputPath('desktop.png') })
  await page.setViewportSize({ width: 390, height: 844 }); await noOverflow(page)
  await page.screenshot({ path: testInfo.outputPath('mobile.png') })
  await page.getByRole('link', { name: 'Voltar ao painel', exact: true }).click()
  await expect(page.locator('.skill-progress-list')).toContainText('504')
  await page.getByLabel('Área de interesse').selectOption({ label: 'Programming' })
  await page.getByRole('radio', { name: 'Python', exact: true }).check()
  await expect(page.getByText('Não há atividades elegíveis', { exact: false })).toBeVisible()
  await page.getByRole('button', { name: 'Sair', exact: true }).click(); await login(page, 'other@qa.example', password)
  await page.getByRole('link', { name: 'Tentativas', exact: true }).click()
  await expect(page.getByText('Você ainda não iniciou uma tentativa.')).toBeVisible()
  await page.goto(`/tentativas/${attemptId}`); await login(page, 'other@qa.example', password)
  await expect(page.getByRole('alert')).toContainText('Tentativa não encontrada')
  await expect(page.locator('.attempt-evaluation')).toHaveCount(0)
  await expect(page).toHaveTitle('CodeTrack')
})

test('estudo: ADMIN publica e leitura permanece isolada por conta', async ({ page }, testInfo) => {
  if (process.env.CODETRACK_QA_DISPOSABLE !== '1' || !process.env.QA_PASSWORD) throw new Error('Use o harness descartável.')
  const password = process.env.QA_PASSWORD
  page.on('dialog', dialog => dialog.accept())
  await page.goto('/entrar'); await login(page, 'reviewer@qa.example', password)
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  await page.getByRole('link', { name: 'Cadastrar conteúdo', exact: true }).click()
  await page.getByLabel('Habilidade', { exact: true }).selectOption({ label: 'Python' })
  await page.getByLabel('Título', { exact: true }).fill('Somar valores em Python')
  await page.getByLabel('Explicação', { exact: true }).fill('Use + para somar. <b>Texto literal</b>')
  await page.getByLabel('Exemplo de código', { exact: true }).fill('print(1 + 1)')
  await page.getByLabel('Erros comuns', { exact: true }).fill('Strings concatenam; números somam.')
  await page.getByRole('button', { name: 'Publicar conteúdo', exact: true }).click()
  await expect(page.getByRole('status')).toContainText('Conteúdo publicado')
  await page.getByRole('button', { name: 'Abrir conteúdo publicado' }).click()
  await expect(page.getByRole('heading', { name: 'Somar valores em Python' })).toBeVisible()
  const path = new URL(page.url()).pathname
  await page.getByRole('button', { name: 'Sair', exact: true }).click()
  await login(page, 'owner@qa.example', password)
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  await expect(page.getByRole('link', { name: 'Cadastrar conteúdo', exact: true })).toHaveCount(0)
  await page.getByRole('link', { name: 'Estudar: Somar valores em Python' }).click()
  await expect(page.locator('main b')).toHaveCount(0)
  await page.getByRole('button', { name: 'Marcar como estudado' }).click()
  await expect(page.getByText('Conteúdo marcado como estudado.', { exact: true })).toBeVisible()
  for (const theme of ['light', 'dark']) {
    await page.getByLabel('Tema da interface').selectOption(theme)
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 900 }); await noOverflow(page)
      await page.screenshot({ path: testInfo.outputPath(`study-${theme}-${width}.png`), fullPage: true, animations: 'disabled' })
    }
  }
  await page.reload(); await login(page, 'owner@qa.example', password)
  await expect(page.getByText('Conteúdo marcado como estudado.', { exact: true })).toBeVisible()
  expect(new URL(page.url()).pathname).toBe(path)
  await page.getByRole('button', { name: 'Sair', exact: true }).click()
  await login(page, 'other@qa.example', password)
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  await page.getByRole('link', { name: 'Estudar: Somar valores em Python' }).click()
  await expect(page.getByRole('button', { name: 'Marcar como estudado' })).toBeVisible()
})

test('aula oferece práticas paginadas e preserva critérios na tentativa', async ({ page, request }, testInfo) => {
  if (process.env.CODETRACK_QA_DISPOSABLE !== '1' || !process.env.QA_PASSWORD) throw new Error('Use o harness descartável.')
  const password = process.env.QA_PASSWORD
  const api = 'http://127.0.0.1:8100/api/v1'
  const auth = await request.post(`${api}/auth/login`, { data: { email: 'reviewer@qa.example', password } })
  expect(auth.status()).toBe(200)
  const headers = { Authorization: 'Bearer ' + (await auth.json()).access_token }
  const category = await request.post(`${api}/categories`, { headers, data: { name: 'Practice QA', slug: 'practice-qa' } })
  expect(category.status()).toBe(201)
  const skill = await request.post(`${api}/skills`, { headers, data: { name: 'Practice skill', slug: 'practice-skill', category_id: (await category.json()).id } })
  expect(skill.status()).toBe(201)
  const skillId = (await skill.json()).id
  const lesson = await request.post(`${api}/study`, { headers, data: { skill_id: skillId, title: 'Praticar depois de ler', explanation: 'Uma leitura não é uma avaliação.', code_example: 'print(2)', common_mistakes: 'Confundir leitura e domínio.' } })
  expect(lesson.status()).toBe(201)
  const lessonId = (await lesson.json()).id
  let challengeId = 0
  await page.goto('/entrar'); await login(page, 'other@qa.example', password)
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  await page.getByRole('link', { name: 'Estudar: Praticar depois de ler' }).click()
  const practice = page.getByRole('region', { name: 'Pratique Practice skill' })
  await expect(practice).toContainText('Nenhum desafio disponível')
  for (let i = 1; i <= 7; i++) {
    const response = await request.post(`${api}/challenges`, { headers, data: {
      title: `Prática QA ${i}`, description: 'Critério público: justificar a soma. <b>Texto literal</b>',
      challenge_type: 'CODE', difficulty: 'EASY', difficulty_score: 100, estimated_minutes: 10,
      skills: [{ skill_id: skillId, weight: 100 }], is_active: i !== 7,
    } })
    expect(response.status()).toBe(201)
    if (i === 1) challengeId = (await response.json()).id
  }
  let failRequests = true
  await page.route('**/challenges?*', async route => {
    if (failRequests) await route.fulfill({ status: 503, contentType: 'application/json', body: '{}' })
    else await route.continue()
  })
  await page.getByRole('link', { name: 'Voltar aos conteúdos' }).click()
  await page.getByRole('link', { name: 'Estudar: Praticar depois de ler' }).click()
  await expect(practice.getByRole('alert')).toContainText('Não foi possível carregar')
  failRequests = false
  await practice.getByRole('button', { name: 'Recarregar práticas' }).click()
  await expect(practice.getByRole('heading', { name: 'Prática QA 1', exact: true })).toBeVisible()
  await practice.getByRole('button', { name: 'Próximas práticas' }).click()
  await expect(practice.getByRole('heading', { name: 'Prática QA 6', exact: true })).toBeVisible()
  await expect(practice.getByRole('heading', { name: 'Prática QA 7', exact: true })).toHaveCount(0)
  await expect(practice.getByRole('button', { name: 'Próximas práticas' })).toBeDisabled()
  await practice.getByRole('button', { name: 'Práticas anteriores' }).click()
  await practice.locator('summary').filter({ hasText: 'Ver enunciado: Prática QA 1' }).click()
  await expect(practice.locator('b')).toHaveCount(0)
  await page.setViewportSize({ width: 390, height: 844 }); await noOverflow(page)
  await page.screenshot({ path: testInfo.outputPath('study-practice-mobile.png'), fullPage: true })
  await practice.getByRole('button', { name: 'Iniciar ou retomar tentativa' }).first().click()
  await expect(page.getByLabel('Resposta em texto ou código')).toBeVisible()
  const attemptPath = new URL(page.url()).pathname
  const changed = await request.patch(`${api}/challenges/${challengeId}`, { headers, data: { description: 'Critério alterado depois do início.', is_active: false } })
  expect(changed.status()).toBe(200)
  await page.reload(); await login(page, 'other@qa.example', password)
  await expect(page).toHaveURL(new RegExp(`${attemptPath}$`))
  await expect(page.locator('main')).toContainText('Critério público: justificar a soma.')
  await expect(page.locator('main')).not.toContainText('Critério alterado depois do início.')
  const ownerAuth = await request.post(`${api}/auth/login`, { data: { email: 'other@qa.example', password } })
  const read = await request.get(`${api}/study/${lessonId}`, { headers: { Authorization: 'Bearer ' + (await ownerAuth.json()).access_token } })
  expect((await read.json()).completed_at).toBeNull()
})

test('ADMIN indica prática da aula e aluno inicia o desafio específico', async ({ page, request }, testInfo) => {
  if (process.env.CODETRACK_QA_DISPOSABLE !== '1' || !process.env.QA_PASSWORD) throw new Error('Use o harness descartável.')
  const password = process.env.QA_PASSWORD
  const api = 'http://127.0.0.1:8100/api/v1'
  const auth = await request.post(`${api}/auth/login`, { data: { email: 'reviewer@qa.example', password } })
  expect(auth.status()).toBe(200)
  const headers = { Authorization: 'Bearer ' + (await auth.json()).access_token }
  const lesson = await request.post(`${api}/study`, { headers, data: { skill_id: Number(process.env.QA_SKILL_ID), title: 'Aula com prática própria', explanation: 'Aprenda uma soma.', code_example: 'print(1 + 1)', common_mistakes: 'Confundir strings e números.' } })
  expect(lesson.status()).toBe(201)
  const lessonId = (await lesson.json()).id
  // Keep this fixture out of personalized recommendations used by the main journey.
  const challenge = await request.post(`${api}/challenges`, { headers, data: {
    title: 'Prática específica da aula', description: 'Explique 1 + 1 = 2.', challenge_type: 'CODE',
    difficulty: 'HARD', difficulty_score: 900, estimated_minutes: 10, is_active: true,
    skills: [{ skill_id: Number(process.env.QA_SKILL_ID), weight: 100 }],
  } })
  expect(challenge.status()).toBe(201)
  const challengeId = (await challenge.json()).id
  await page.goto('/entrar'); await login(page, 'reviewer@qa.example', password)
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  await page.getByRole('link', { name: 'Estudar: Aula com prática própria' }).click()
  await page.getByRole('button', { name: 'Usar nesta aula: Prática específica da aula', exact: true }).click()
  await expect(page.getByText('Indicação de prática atualizada.', { exact: true })).toBeVisible()
  await expect(page.getByRole('region', { name: 'Prática desta aula', exact: true })).toContainText('Prática específica da aula')
  await page.getByRole('button', { name: 'Sair', exact: true }).click()
  await login(page, 'other@qa.example', password)
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  await page.getByRole('link', { name: 'Estudar: Aula com prática própria' }).click()
  const primary = page.getByRole('region', { name: 'Prática desta aula', exact: true })
  await expect(primary).toContainText('Prática específica da aula')
  await expect(page.getByRole('button', { name: /Usar nesta aula/ })).toHaveCount(0)
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 900 }); await noOverflow(page)
    await page.screenshot({ path: testInfo.outputPath(`linked-practice-${width}.png`), fullPage: true })
  }
  await primary.getByRole('button', { name: 'Iniciar ou retomar tentativa' }).click()
  await expect(page.getByLabel('Resposta em texto ou código')).toBeVisible()
  await expect(page.locator('main')).toContainText('Explique 1 + 1 = 2.')
  await request.patch(`${api}/challenges/${challengeId}`, { headers, data: { is_active: false } })
  // Start is idempotent but creates a real draft; leave it out of later owner assertions.
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  await page.getByRole('link', { name: 'Estudar: Aula com prática própria' }).click()
  await expect(primary).toHaveCount(0)
  await expect(page.getByText('Esta aula ainda não tem uma prática específica disponível.', { exact: false })).toBeVisible()
  const current = await request.get(`${api}/study/${lessonId}/practice`, { headers })
  expect(current.status()).toBe(200); expect(await current.json()).toBeNull()
})

test('sequência editorial orienta a próxima leitura sem misturar contas', async ({ page, request }, testInfo) => {
  if (process.env.CODETRACK_QA_DISPOSABLE !== '1' || !process.env.QA_PASSWORD) throw new Error('Use o harness descartável.')
  const password = process.env.QA_PASSWORD
  const api = 'http://127.0.0.1:8100/api/v1'
  const auth = await request.post(`${api}/auth/login`, { data: { email: 'reviewer@qa.example', password } })
  const headers = { Authorization: 'Bearer ' + (await auth.json()).access_token }
  const category = await request.post(`${api}/categories`, { headers, data: { name: 'Guidance', slug: 'guidance' } })
  const skill = await request.post(`${api}/skills`, { headers, data: { name: 'Leitura guiada', slug: 'guided-reading', category_id: (await category.json()).id } })
  expect(skill.status()).toBe(201)
  const skillId = (await skill.json()).id
  for (const title of ['Primeiro passo', 'Segundo passo']) {
    const response = await request.post(`${api}/study`, { headers, data: { skill_id: skillId, title, explanation: 'Uma explicação curta.', code_example: 'print(1)', common_mistakes: 'Leitura não é domínio.' } })
    expect(response.status()).toBe(201)
  }
  await page.goto('/entrar'); await login(page, 'reviewer@qa.example', password)
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  for (const [title, order] of [['Primeiro passo', '10'], ['Segundo passo', '20']]) {
    await page.getByRole('link', { name: `Estudar: ${title}`, exact: true }).click()
    await page.getByLabel('Posição editorial').fill(order)
    await page.getByRole('button', { name: 'Salvar ordem de leitura', exact: true }).click()
    await expect(page.getByText('Ordem de leitura salva.', { exact: false })).toBeVisible()
    await page.getByRole('link', { name: 'Voltar aos conteúdos', exact: true }).click()
  }
  await page.getByRole('button', { name: 'Sair', exact: true }).click()
  await login(page, 'other@qa.example', password)
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  await page.getByRole('link', { name: 'Ver sequência de Leitura guiada', exact: true }).first().click()
  const guidance = page.getByRole('region', { name: 'Orientação de leitura' })
  await expect(guidance.getByRole('link', { name: 'Continuar leitura: Primeiro passo' })).toBeVisible()
  await page.setViewportSize({ width: 390, height: 844 }); await noOverflow(page)
  await page.screenshot({ path: testInfo.outputPath('reading-guidance-mobile.png'), fullPage: true })
  for (const title of ['Primeiro passo', 'Segundo passo']) {
    await guidance.getByRole('link', { name: `Continuar leitura: ${title}` }).click()
    await expect(page.getByLabel('Posição editorial')).toHaveCount(0)
    await page.getByRole('button', { name: 'Marcar como estudado', exact: true }).click()
    await expect(page.getByText('Conteúdo marcado como estudado.', { exact: true })).toBeVisible()
    await page.getByRole('link', { name: 'Ver sequência de Leitura guiada', exact: true }).click()
  }
  await expect(guidance).toContainText('Você marcou todas as leituras desta sequência')
  await expect(page.getByRole('link', { name: 'Estudar: Primeiro passo', exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Sair', exact: true }).click()
  await login(page, 'owner@qa.example', password)
  await page.getByRole('link', { name: 'Estudar', exact: true }).click()
  await page.getByRole('link', { name: 'Ver sequência de Leitura guiada', exact: true }).first().click()
  await expect(guidance.getByRole('link', { name: 'Continuar leitura: Primeiro passo' })).toBeVisible()
})
