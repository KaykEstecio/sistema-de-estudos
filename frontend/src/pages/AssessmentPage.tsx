import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router'
import axios from 'axios'
import { useAuth } from '../auth'
import { assessmentError, forgetAssessment, rememberAssessment, validId } from '../services/assessment'
import type { Assessment, Item, Option, Skill } from '../services/assessment'

export default function AssessmentRoute() {
  const { id = '' } = useParams()
  return <AssessmentPage key={id} id={id} />
}
function AssessmentPage({ id }: { id: string }) {
  const { client, user } = useAuth()
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [names, setNames] = useState<Record<number, string>>({})
  const [drafts, setDrafts] = useState<Record<number, Option>>({})
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')
  const [retry, setRetry] = useState(0)
  const pending = useRef(false)
  const controller = useRef(new AbortController())
  useEffect(() => {
    const abort = new AbortController(); controller.current = abort
    setLoading(true); setError('')
    async function load() {
      if (!client || !user) return
      if (!validId(id)) { setError('Número de diagnóstico inválido.'); setLoading(false); return }
      try {
        const { data } = await client.get<Assessment>(`/assessments/${id}`, { signal: abort.signal })
        if (abort.signal.aborted) return
        setAssessment(data); rememberAssessment(user.id, data.id)
        const skills = await Promise.allSettled([...new Set(data.items.map(item => item.skill_id))].map(skill => client.get<Skill>(`/skills/${skill}`, { signal: abort.signal })))
        if (!abort.signal.aborted) setNames(Object.fromEntries(skills.flatMap(result => result.status === 'fulfilled' ? [[result.value.data.id, result.value.data.name]] : [])))
      } catch (cause) {
        if (!abort.signal.aborted && !axios.isCancel(cause)) {
          if (axios.isAxiosError(cause) && cause.response?.status === 404) { forgetAssessment(user.id, id); setAssessment(null) }
          setError(assessmentError(cause))
        }
      } finally { if (!abort.signal.aborted) setLoading(false) }
    }
    void load(); return () => abort.abort()
  }, [client, user?.id, id, retry])
  async function save(item: Item) {
    const choice = drafts[item.id]
    if (!client || !choice || pending.current) return
    pending.current = true; setBusy(true); setError(''); setStatus('')
    const signal = controller.current.signal
    try {
      const { data } = await client.post<Item>(`/assessments/${id}/answers`, { item_id: item.id, selected_option: choice }, { signal })
      if (!signal.aborted) {
        setAssessment(previous => previous ? { ...previous, items: previous.items.map(value => value.id === data.id ? data : value) } : null)
        setDrafts(previous => { const next = { ...previous }; delete next[item.id]; return next })
        setStatus(`Resposta da questão ${item.position} salva.`)
      }
    } catch (cause) { if (!signal.aborted && !axios.isCancel(cause)) setError(assessmentError(cause)) }
    finally { pending.current = false; if (!signal.aborted) setBusy(false) }
  }
  async function finish() {
    if (!client || pending.current) return
    pending.current = true; setBusy(true); setError(''); setStatus('')
    const signal = controller.current.signal
    try {
      try {
        const { data } = await client.post<Assessment>(`/assessments/${id}/finish`, undefined, { signal })
        if (!signal.aborted) setAssessment(data)
      } catch (cause) {
        if (signal.aborted || axios.isCancel(cause)) return
        // Uma resposta perdida não significa que a conclusão falhou no servidor.
        const { data } = await client.get<Assessment>(`/assessments/${id}`, { signal })
        if (!signal.aborted) { setAssessment(data); if (!data.completed_at) setError(assessmentError(cause)) }
      }
    } catch (cause) { if (!signal.aborted && !axios.isCancel(cause)) setError(assessmentError(cause)) }
    finally { pending.current = false; if (!signal.aborted) setBusy(false) }
  }
  const dirty = assessment?.items.some(item => drafts[item.id] && drafts[item.id] !== item.selected_option)
  const allAnswered = assessment?.items.every(item => item.selected_option !== null)
  return <main className="auth-main onboarding-main"><h1>{assessment?.completed_at ? 'Seu resultado' : 'Seu diagnóstico'}</h1>
    <p className="subtitle">Diagnóstico #{id}</p><p className="notice">Guarde este <Link to={`/diagnostico/${id}`}>link do diagnóstico</Link> para retomar após entrar. Apenas respostas salvas permanecem no servidor.</p>
    {error && <p role="alert" className="error">{error}</p>}{status && <p role="status" className="notice">{status}</p>}
    {loading ? <p role="status">Carregando diagnóstico…</p> : assessment && (assessment.completed_at ? <>
      <p className="notice">Resultado provisório por habilidade. Confiança 0 indica ausência de calibração, não fracasso. Este diagnóstico ainda não inicializa suas skills.</p>
      {assessment.results.map(result => <section className="question" key={result.skill_id}><h2>{names[result.skill_id] ?? `Skill #${result.skill_id}`}</h2><p>{result.correct_count} de {result.question_count} respostas corretas</p><p>Score: {result.score} / 1000</p><p>Confiança: {result.confidence}</p></section>)}
    </> : <>
      <p>{assessment.items.filter(item => item.selected_option).length} de {assessment.items.length} respostas salvas.</p>
      {assessment.items.map(item => <fieldset className="question auth-form interests" key={item.id} disabled={busy}><legend>Questão {item.position} · {names[item.skill_id] ?? `Skill #${item.skill_id}`}</legend><p className="question-prompt">{item.prompt}</p>{(Object.entries(item.options) as [Option, string][]).map(([option, label]) => <label key={option} className="interest-option"><input type="radio" name={`question-${item.id}`} checked={(drafts[item.id] ?? item.selected_option) === option} onChange={() => { setDrafts(previous => ({ ...previous, [item.id]: option })); setStatus('') }} />{option}. {label}</label>)}<p>{drafts[item.id] && drafts[item.id] !== item.selected_option ? 'Alteração ainda não salva.' : item.selected_option ? 'Resposta salva.' : 'Escolha uma alternativa.'}</p><button className="text-button" disabled={!drafts[item.id] || drafts[item.id] === item.selected_option} onClick={() => void save(item)}>Salvar resposta</button></fieldset>)}
      <button className="primary" disabled={busy || !allAnswered || !!dirty} onClick={() => void finish()}>{busy ? 'Aguarde…' : 'Concluir diagnóstico'}</button><p>Salve todas as respostas antes de concluir.</p>
    </>)}
    {!loading && <button className="text-button" disabled={busy} onClick={() => setRetry(value => value + 1)}>Consultar novamente</button>}
    <p className="alternate"><Link to="/diagnostico">Voltar aos diagnósticos</Link></p></main>
}
