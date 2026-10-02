import type { Page } from '@playwright/test'
import { test, expect, login, noOverflow } from './helpers'

function summary(id: number) {
  return { id, challenge_id: id, title: `Desafio histórico ${id}`, status: id === 11 ? 'SUBMITTED' : 'IN_PROGRESS', attempt_number: 1,
    started_at: '2026-10-02T10:00:00Z', submitted_at: id === 11 ? '2026-10-02T11:00:00Z' : null, last_activity_at: '2026-10-02T11:00:00Z' }
}
function attempt(id: number) {
  return { ...summary(id), draft_answer: 'Saved answer', challenge_snapshot: { title: summary(id).title, description: 'Enunciado <b>literal</b>',
    difficulty_score: 100, estimated_minutes: 15, starter_code: null, skills: [1, 2, 3, 4].map(skill_id => ({ skill_id, weight: 25 })) } }
}
async function setup(page: Page) {
  const state = { owner: 1, failPatch: false, lostSubmit: false, failRead: false, conflict: false, expired: false, failList: false,
    evaluation: 'pending', slow: false, calls: [] as string[], attempts: new Map<number, ReturnType<typeof attempt>>() }
  await page.route('**/api/v1/**', async route => {
    const url = new URL(route.request().url()), method = route.request().method(), p = url.pathname
    const send = (json: unknown) => route.fulfill({ json })
    const fail = (status: number) => route.fulfill({ status, json: {} })
    if (p.endsWith('/auth/login')) return send({ access_token: 'fixture', expires_in: 3600 })
    if (p.endsWith('/auth/me')) return send({ id: state.owner, name: 'QA', role: 'STUDENT', onboarding_completed: true })
    if (state.expired) { state.expired = false; return fail(401) }
    if (p === '/api/v1/attempts') {
      if (state.failList) return fail(503)
      const offset = Number(url.searchParams.get('offset'))
      return send({ items: state.owner === 2 ? [] : offset ? [summary(11)] : Array.from({ length: 10 }, (_, i) => summary(i + 1)),
        total: state.owner === 2 ? 0 : 11, limit: 10, offset })
    }
    if (p.endsWith('/evaluation')) {
      state.calls.push('evaluation')
      const mode = state.evaluation
      if (state.slow) await new Promise(resolve => setTimeout(resolve, 450))
      if (mode === 'pending') return fail(404)
      if (mode === 'error') return fail(503)
      return send({ id: 1, attempt_id: 11, rubric_version: 'manual-v1', created_at: '2026-10-02T12:00:00Z', feedback: 'Feedback <b>literal</b>',
        skills: ['MET', 'PARTIALLY_MET', 'NOT_MET', 'INSUFFICIENT_EVIDENCE'].map((classification, i) => ({ skill_id: i + 1, classification, justification: 'Justificativa.' })) })
    }
    const match = p.match(/\/attempts\/(\d+)(\/submit)?$/)
    if (!match) return fail(404)
    const id = Number(match[1]); state.calls.push(`${method}:${id}${match[2] || ''}`)
    if (!state.attempts.has(id)) state.attempts.set(id, attempt(id))
    const value = state.attempts.get(id)!
    if (method === 'GET') return state.failRead ? fail(503) : send(value)
    if (method === 'PATCH') {
      if (state.failPatch) return fail(503)
      if (state.conflict) { value.status = 'SUBMITTED'; value.draft_answer = 'Other tab sent this'; value.submitted_at = '2026-10-02T11:00:00Z'; return fail(409) }
      expect(Object.keys(route.request().postDataJSON())).toEqual(['draft_answer'])
      value.draft_answer = route.request().postDataJSON().draft_answer
      return send(value)
    }
    expect(route.request().postData()).toBeNull()
    value.status = 'SUBMITTED'; value.submitted_at = '2026-10-02T11:00:00Z'
    return state.lostSubmit ? fail(503) : send(value)
  })
  return state
}
async function open(page: Page, id: number) {
  await page.goto(`/tentativas/${id}`); await login(page, 'qa@example.com', 'test-only-password')
  await expect(page.getByRole('heading', { name: `Desafio histórico ${id}`, exact: true })).toBeVisible()
}

test('teclado: salvar mantém o foco na resposta e permite continuar editando', async ({ page }, testInfo) => {
  await setup(page); await open(page, 1)
  const heading = page.getByRole('heading', { name: 'Desafio histórico 1', exact: true })
  const editor = page.getByLabel('Resposta em texto ou código')
  await expect(heading).toBeFocused()
  await page.keyboard.press('Tab'); await expect(editor).toBeFocused()
  await page.keyboard.press('ControlOrMeta+A')
  await page.keyboard.type('Resposta pelo teclado')
  await page.keyboard.press('Tab')
  await expect(page.getByRole('button', { name: 'Salvar rascunho' })).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page.getByText('Rascunho salvo.', { exact: true })).toBeVisible()
  await expect(editor).toBeFocused()
  await page.keyboard.press('End')
  await page.keyboard.type(' com continuação')
  await expect(editor).toHaveValue('Resposta pelo teclado com continuação')
  await noOverflow(page)
  await page.screenshot({ path: testInfo.outputPath('keyboard.png') })
})

test('salvar/enviar: confirmação, falha do PATCH e reconciliação', async ({ page }) => {
  const state = await setup(page); let accept = true
  page.on('dialog', dialog => accept ? dialog.accept() : dialog.dismiss())
  await open(page, 1)
  const editor = page.getByLabel('Resposta em texto ou código')
  await editor.fill('  Unicode 😀\nprint("Olá")  ')
  accept = false; await page.getByRole('button', { name: 'Enviar para revisão' }).click()
  expect(state.calls.filter(call => call.startsWith('POST'))).toEqual([])
  accept = true; state.failPatch = true
  await page.getByRole('button', { name: 'Enviar para revisão' }).click()
  await expect(page.getByRole('alert')).toBeVisible()
  expect(state.calls.filter(call => call.startsWith('POST'))).toEqual([])
  await expect(editor).toHaveValue('  Unicode 😀\nprint("Olá")  ')
  state.failPatch = false; state.lostSubmit = true; state.failRead = true
  await page.getByRole('button', { name: 'Enviar para revisão' }).click()
  await expect(page.getByRole('button', { name: 'Consultar estado da tentativa' })).toBeVisible()
  await expect(editor).toBeDisabled()
  expect(state.calls.filter(call => call.startsWith('PATCH') || call.startsWith('POST')).slice(-2)).toEqual(['PATCH:1', 'POST:1/submit'])
  state.failRead = false
  await page.getByRole('button', { name: 'Consultar estado da tentativa' }).click()
  await expect(page.getByRole('heading', { name: 'Resposta enviada', exact: true })).toBeVisible()
  await expect(editor).toHaveCount(0)
  expect(state.attempts.get(1)?.draft_answer).toBe('  Unicode 😀\nprint("Olá")  ')
  expect(state.calls.filter(call => call.startsWith('POST'))).toHaveLength(1)
  await noOverflow(page)
})

test('rascunho: vazio, Unicode, guardas de saída e conflito', async ({ page }, testInfo) => {
  const state = await setup(page); let accept = true
  page.on('dialog', dialog => accept ? dialog.accept() : dialog.dismiss())
  await open(page, 1)
  const editor = page.getByLabel('Resposta em texto ou código')
  await editor.fill(''); await page.getByRole('button', { name: 'Salvar rascunho' }).click()
  await expect(page.getByText('Rascunho salvo.', { exact: true })).toBeVisible()
  expect(state.attempts.get(1)?.draft_answer).toBe('')
  await expect(page.getByRole('button', { name: 'Enviar para revisão' })).toBeDisabled()
  await page.getByRole('link', { name: 'Voltar às tentativas' }).click()
  await expect(page.getByRole('heading', { name: 'Minhas tentativas' })).toBeVisible()
  await page.goBack(); await expect(editor).toBeVisible()
  await editor.fill('History guard'); accept = false
  await page.goForward(); await expect(page).toHaveURL(/\/tentativas\/1$/)
  await expect(editor).toHaveValue('History guard'); accept = true
  await editor.fill('😀'.repeat(20000)); await expect(page.getByRole('button', { name: 'Salvar rascunho' })).toBeEnabled()
  await editor.fill('😀'.repeat(20001)); await expect(page.getByRole('button', { name: 'Salvar rascunho' })).toBeDisabled()
  await editor.fill('My unsent answer'); accept = false
  await page.getByRole('link', { name: 'Voltar às tentativas' }).click(); await expect(page).toHaveURL(/\/tentativas\/1$/)
  await page.getByRole('button', { name: 'Sair', exact: true }).click(); await expect(editor).toHaveValue('My unsent answer')
  accept = true; state.conflict = true
  await page.getByRole('button', { name: 'Salvar rascunho' }).click()
  await expect(page.getByRole('heading', { name: 'Texto local não enviado' })).toBeVisible()
  await expect(page.locator('main')).toContainText('My unsent answer')
  await expect(page.locator('main')).toContainText('Other tab sent this')
  await noOverflow(page); await page.screenshot({ path: testInfo.outputPath('conflict.png') })
})

test('lista e sessão: paginação, retry, vazio e expiração', async ({ page }) => {
  const state = await setup(page)
  await page.goto('/tentativas'); await login(page, 'qa@example.com', 'test-only-password')
  await page.getByRole('button', { name: 'Próxima', exact: true }).click()
  await page.getByRole('link', { name: 'Ver envio: Desafio histórico 11' }).click()
  await expect(page.getByRole('heading', { name: 'Resposta enviada', exact: true })).toBeVisible()
  state.failList = true; await page.getByRole('link', { name: 'Voltar às tentativas' }).click()
  await expect(page.getByRole('alert')).toBeVisible()
  state.failList = false; await page.getByRole('button', { name: 'Tentar novamente' }).click()
  await page.getByRole('link', { name: 'Retomar: Desafio histórico 1', exact: true }).click()
  const editor = page.getByLabel('Resposta em texto ou código'); await editor.fill('unsaved')
  state.expired = true; await page.getByRole('button', { name: 'Salvar rascunho' }).click()
  await expect(page.getByRole('heading', { name: 'Entre no CodeTrack' })).toBeVisible()
  await expect(editor).toHaveCount(0)
  state.owner = 2; await login(page, 'other@example.com', 'test-only-password')
  await page.getByRole('link', { name: 'Tentativas', exact: true }).click()
  await expect(page.getByText('Você ainda não iniciou uma tentativa.')).toBeVisible()
  await expect(page.getByText('Desafio histórico 1', { exact: true })).toHaveCount(0)
})

test('avaliação: pendência distinta de erro, acesso e resposta obsoleta', async ({ page }, testInfo) => {
  const state = await setup(page); await open(page, 11)
  await expect(page.getByText('Sua resposta aguarda revisão manual', { exact: false })).toBeVisible()
  state.evaluation = 'error'; await page.getByRole('button', { name: 'Atualizar avaliação' }).click()
  await expect(page.getByRole('alert')).toBeVisible()
  await expect(page.getByText('Sua resposta aguarda revisão manual', { exact: false })).toHaveCount(0)
  state.evaluation = 'available'; await page.getByRole('button', { name: 'Atualizar avaliação' }).click()
  await expect(page.getByRole('heading', { name: 'Feedback geral' })).toBeVisible()
  for (const label of ['Atendido', 'Parcialmente atendido', 'Não atendido', 'Evidência insuficiente']) await expect(page.locator('.evaluation-skills')).toContainText(label)
  await expect(page.locator('main b')).toHaveCount(0)
  await noOverflow(page); await page.screenshot({ path: testInfo.outputPath('evaluation.png') })
  state.evaluation = 'pending'; state.failRead = true
  await page.getByRole('button', { name: 'Atualizar avaliação' }).click()
  await expect(page.getByRole('alert')).toContainText('confirmar o acesso')
  await expect(page.getByText('Sua resposta aguarda revisão manual', { exact: false })).toHaveCount(0)
  state.failRead = false; state.evaluation = 'available'; state.slow = true
  await page.getByRole('button', { name: 'Atualizar avaliação' }).click()
  await expect(page.getByText('Consultando avaliação…')).toBeVisible()
  await page.getByRole('link', { name: 'Tentativas', exact: true }).click()
  await page.getByRole('button', { name: 'Sair', exact: true }).click()
  state.owner = 2; await login(page, 'other@example.com', 'test-only-password')
  await expect(page.getByText('Você ainda não iniciou uma tentativa.')).toBeVisible()
  await page.waitForTimeout(500)
  await expect(page.getByRole('heading', { name: 'Feedback geral' })).toHaveCount(0)
})
