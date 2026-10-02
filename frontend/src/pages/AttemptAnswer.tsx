import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import { useBlocker } from 'react-router'
import { useAuth } from '../auth'
import { useRegisterExitGuard } from '../exitGuard'
import { getAttempt, saveAttempt, submitAttempt } from '../services/attempts'
import type { Attempt } from '../services/attempts'

export default function AttemptAnswer({ initial, onUpdate }: { initial: Attempt; onUpdate: (value: Attempt) => void }) {
  const { client } = useAuth()
  const [attempt, setAttempt] = useState(initial)
  const [answer, setAnswer] = useState(initial.draft_answer)
  const [busy, setBusy] = useState(false)
  const [uncertain, setUncertain] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [unsent, setUnsent] = useState('')
  const operation = useRef<AbortController | null>(null)
  const editor = useRef<HTMLTextAreaElement>(null)
  const dirty = attempt.status === 'IN_PROGRESS' && answer !== attempt.draft_answer
  const guarded = dirty || busy || uncertain || Boolean(unsent)
  const length = Array.from(answer).length
  const valid = length <= 20000
  const blocker = useBlocker(guarded)
  useRegisterExitGuard(guarded)

  useEffect(() => {
    if (blocker.state === 'blocked') {
      if (window.confirm('Sair desta tentativa? Alterações não salvas serão perdidas. Uma operação em andamento pode ter sido concluída no servidor.')) blocker.proceed()
      else blocker.reset()
    }
  }, [blocker])
  useEffect(() => {
    if (!guarded) return
    function warn(event: BeforeUnloadEvent) { event.preventDefault(); event.returnValue = '' }
    window.addEventListener('beforeunload', warn)
    return () => window.removeEventListener('beforeunload', warn)
  }, [guarded])
  useEffect(() => () => { operation.current?.abort() }, [])
  useEffect(() => {
    if (!busy && notice === 'Rascunho salvo.') editor.current?.focus()
  }, [busy, notice])

  function update(value: Attempt) {
    setAttempt(value); onUpdate(value)
  }

  async function reconcile(local: string, signal: AbortSignal) {
    if (!client) return
    try {
      const current = await getAttempt(client, attempt.id, signal)
      if (signal.aborted) return
      update(current); setUncertain(false)
      if (current.status === 'SUBMITTED') {
        if (local !== current.draft_answer) setUnsent(local)
        setAnswer(current.draft_answer)
        setNotice('Envio confirmado. Sua resposta está disponível somente para leitura.')
        setError('')
      } else {
        setError('A tentativa continua em andamento. Confira sua resposta antes de salvar ou confirmar o envio novamente.')
      }
    } catch (cause) {
      if (signal.aborted || axios.isCancel(cause) || (axios.isAxiosError(cause) && cause.response?.status === 401)) return
      setUncertain(true)
      setError('Não foi possível confirmar o estado da tentativa. Consulte o estado antes de continuar.')
    }
  }

  async function act(kind: 'save' | 'submit' | 'check') {
    if (!client || operation.current) return
    if (kind !== 'check' && (!valid || uncertain)) return
    if (kind === 'submit' && (!answer.trim() || !window.confirm('Enviar sua resposta para revisão manual? Após o envio, ela não poderá ser editada.'))) return
    const controller = new AbortController()
    const signal = controller.signal
    operation.current = controller
    const local = answer
    setBusy(true); setError(''); setNotice('')
    let submitting = false
    try {
      if (kind === 'check') { await reconcile(local, signal); return }
      if (dirty) {
        const saved = await saveAttempt(client, attempt.id, local, signal)
        if (signal.aborted) return
        update(saved)
      }
      if (kind === 'submit') {
        submitting = true
        const sent = await submitAttempt(client, attempt.id, signal)
        if (signal.aborted) return
        update(sent); setAnswer(sent.draft_answer)
        if (sent.draft_answer !== local) setUnsent(local)
        setNotice('Resposta enviada para revisão manual.')
      } else setNotice('Rascunho salvo.')
    } catch (cause) {
      if (signal.aborted || axios.isCancel(cause) || (axios.isAxiosError(cause) && cause.response?.status === 401)) return
      const status = axios.isAxiosError(cause) ? cause.response?.status : undefined
      if (status === 409 || (submitting && (!status || status >= 500))) {
        setUncertain(true)
        await reconcile(local, signal)
      } else if (status === 422) setError('Confira sua resposta: o limite é de 20.000 caracteres e o envio exige texto não vazio.')
      else if (status === 404) { setUncertain(true); setError('Tentativa indisponível. Consulte o estado antes de continuar.') }
      else setError('Não foi possível confirmar o salvamento. Seu texto foi mantido; tente salvar novamente.')
    } finally {
      if (!signal.aborted) { operation.current = null; setBusy(false) }
    }
  }

  return <section className="attempt-answer" aria-labelledby="answer-title">
    <h2 id="answer-title">{attempt.status === 'SUBMITTED' ? 'Resposta enviada' : 'Sua resposta'}</h2>
    {attempt.status === 'IN_PROGRESS' ? <>
      <label htmlFor="attempt-answer">Resposta em texto ou código</label>
      <textarea ref={editor} id="attempt-answer" rows={12} value={answer} disabled={busy || uncertain}
        aria-describedby="answer-help answer-count" onChange={event => { setAnswer(event.target.value); setNotice('') }} />
      <p id="answer-count" className={valid ? 'dashboard-note' : 'error'}>{length.toLocaleString('pt-BR')}/20.000 caracteres</p>
      <p id="answer-help" className="dashboard-note">Salve antes de sair. Texto não salvo pode ser perdido ao fechar a página ou expirar a sessão. Resolva em uma aba; salvamentos em outra aba podem substituir o rascunho.</p>
      <p role="status">{busy ? 'Aguarde: operação em andamento…' : dirty ? 'Alterações ainda não salvas.' : 'Nenhuma alteração local pendente.'}</p>
      <div className="attempt-actions">
        <button className="dashboard-action" disabled={busy || uncertain || !dirty || !valid} onClick={() => void act('save')}>Salvar rascunho</button>
        <button className="primary" disabled={busy || uncertain || !valid || !answer.trim()} onClick={() => void act('submit')}>Enviar para revisão</button>
      </div>
    </> : <pre>{attempt.draft_answer}</pre>}
    {notice && <p className="notice" role="status">{notice}</p>}
    {error && <p className="error" role="alert">{error}</p>}
    {uncertain && <button className="dashboard-action" disabled={busy} onClick={() => void act('check')}>Consultar estado da tentativa</button>}
    {unsent && <div className="notice"><h3>Texto local não enviado</h3><p>Esta versão difere da resposta enviada. Copie o texto antes de sair.</p><pre>{unsent}</pre></div>}
  </section>
}
