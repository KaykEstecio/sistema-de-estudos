import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useBlocker, useParams } from 'react-router'
import axios from 'axios'
import { useAuth } from '../auth'
import { useRegisterExitGuard } from '../exitGuard'
import { getReviews, getReview, createEvaluation } from '../services/reviews'
import type { Review, EvaluationInput } from '../services/reviews'
import type { AttemptPage } from '../services/attempts'
import type { Classification } from '../services/evaluation'

const labels: Record<Classification, string> = {
  MET: 'Atendido', PARTIALLY_MET: 'Parcialmente atendido', NOT_MET: 'Não atendido',
  INSUFFICIENT_EVIDENCE: 'Evidência insuficiente',
}
const ignored = (error: unknown) => axios.isCancel(error) || (axios.isAxiosError(error) && error.response?.status === 401)

export default function AdminReviewsPage() {
  const { client } = useAuth()
  const [data, setData] = useState<AttemptPage | null>(null)
  const [offset, setOffset] = useState(0)
  const [reload, setReload] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    if (!client) return
    const controller = new AbortController()
    setLoading(true); setError(''); setData(null)
    getReviews(client, offset, controller.signal).then(value => {
      if (!controller.signal.aborted) setData(value)
    }).catch(cause => {
      if (!controller.signal.aborted && !ignored(cause)) setError('Não foi possível consultar a fila. Confira seu acesso de administrador e tente novamente.')
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [client, offset, reload])
  return <main className="dashboard-main">
    <div className="section-heading"><div><p className="eyebrow">Administração</p><h1>Revisões pendentes</h1></div>
      <button className="dashboard-action" disabled={loading} onClick={() => setReload(value => value + 1)}>Atualizar fila</button></div>
    <p className="dashboard-note">Respostas enviadas, da mais antiga à mais recente. Suas próprias tentativas não aparecem aqui.</p>
    {loading && <p role="status">Carregando revisões…</p>}
    {error && <p className="error" role="alert">{error}</p>}
    {data && <>
      <p role="status">{data.total} revisões pendentes · Página {Math.floor(offset / data.limit) + 1}</p>
      {data.items.length ? <ul className="recommendation-list">{data.items.map(item => <li key={item.id}>
        <h2>{item.title}</h2><p>Tentativa #{item.id} · Enviada em {new Date(item.submitted_at!).toLocaleString('pt-BR')}</p>
        <Link className="dashboard-action" to={`/admin/revisoes/${item.id}`}>Revisar tentativa #{item.id}</Link>
      </li>)}</ul> : <p className="notice">Nenhuma revisão nesta página.{offset > 0 && <button className="text-button" onClick={() => setOffset(0)}>Voltar ao início da fila</button>}</p>}
      <nav className="progress-pagination" aria-label="Páginas das revisões">
        <button className="dashboard-action" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - data.limit))}>Anterior</button>
        <button className="dashboard-action" disabled={offset + data.limit >= data.total} onClick={() => setOffset(offset + data.limit)}>Próxima</button>
      </nav>
    </>}
  </main>
}

export function AdminReviewPage() {
  const { id } = useParams()
  const { client } = useAuth()
  const [review, setReview] = useState<Review | null>(null)
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)
  const [loading, setLoading] = useState(true)
  const attemptId = Number(id)
  useEffect(() => {
    if (!client) return
    const controller = new AbortController()
    setReview(null); setError(''); setLoading(true)
    if (!/^[1-9]\d*$/.test(id || '') || attemptId > 2147483647) {
      setError('Identificador de tentativa inválido.'); setLoading(false)
      return
    }
    getReview(client, attemptId, controller.signal).then(value => {
      if (!controller.signal.aborted) setReview(value)
    }).catch(cause => {
      if (!controller.signal.aborted && !ignored(cause)) setError('Revisão indisponível. Verifique seu acesso e se a tentativa foi enviada.')
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [client, id, attemptId, reload])
  return <main className="dashboard-main attempt-detail">
    <Link to="/admin/revisoes">Voltar à fila de revisões</Link><h1>Revisar tentativa #{id}</h1>
    {loading && <p role="status">Carregando resposta…</p>}
    {error && <div className="error" role="alert"><p>{error}</p><button className="dashboard-action" onClick={() => setReload(value => value + 1)}>Tentar novamente</button></div>}
    {review && <ReviewForm key={review.attempt.id} initial={review} />}
  </main>
}

function ReviewForm({ initial }: { initial: Review }) {
  const { client } = useAuth()
  const [evaluation, setEvaluation] = useState(initial.evaluation)
  const [feedback, setFeedback] = useState('')
  const [skills, setSkills] = useState(initial.attempt.challenge_snapshot.skills.map(item => ({ skill_id: item.skill_id, classification: '' as Classification | '', justification: '' })))
  const [busy, setBusy] = useState(false)
  const [uncertain, setUncertain] = useState(false)
  const [error, setError] = useState('')
  const operation = useRef<AbortController | null>(null)
  const locked = useRef(false)
  const guarded = !evaluation && (busy || uncertain || Boolean(feedback) || skills.some(item => item.classification || item.justification))
  const blocker = useBlocker(guarded)
  useRegisterExitGuard(guarded)
  useEffect(() => {
    if (blocker.state === 'blocked') {
      if (window.confirm('Sair da revisão? O feedback não salvo será perdido. Um envio em andamento pode ter sido concluído.')) blocker.proceed()
      else blocker.reset()
    }
  }, [blocker.state, blocker.proceed, blocker.reset])
  useEffect(() => {
    if (!guarded) return
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = '' }
    window.addEventListener('beforeunload', warn)
    return () => window.removeEventListener('beforeunload', warn)
  }, [guarded])
  useEffect(() => () => operation.current?.abort(), [])
  async function check() {
    if (!client || locked.current) return
    locked.current = true; setBusy(true); setError('')
    const controller = new AbortController(); operation.current = controller
    try {
      const current = await getReview(client, initial.attempt.id, controller.signal)
      if (!controller.signal.aborted) { setEvaluation(current.evaluation); setUncertain(false) }
    } catch (cause) {
      if (!controller.signal.aborted && !ignored(cause)) setError('Não foi possível confirmar o resultado. Consulte novamente antes de reenviar.')
    } finally { locked.current = false; if (!controller.signal.aborted) setBusy(false) }
  }
  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!client || locked.current || uncertain || evaluation) return
    if (!feedback.trim() || skills.some(item => !item.classification || !item.justification.trim())) {
      setError('Preencha o feedback, a classificação e a justificativa de cada habilidade.'); return
    }
    if (!window.confirm('Registrar avaliação definitiva? Ela não poderá ser editada e atualizará o progresso conforme as evidências.')) return
    locked.current = true; setBusy(true); setError('')
    const controller = new AbortController(); operation.current = controller
    const payload: EvaluationInput = { feedback, skills: skills.map(item => ({ ...item, classification: item.classification as Classification })) }
    try {
      const value = await createEvaluation(client, initial.attempt.id, payload, controller.signal)
      if (!controller.signal.aborted) setEvaluation(value)
    } catch (cause) {
      if (!controller.signal.aborted && !ignored(cause)) {
        setUncertain(true); setError('Não foi possível confirmar o envio. Consulte o resultado antes de tentar novamente; outra revisão pode já existir.')
      }
    } finally { locked.current = false; if (!controller.signal.aborted) setBusy(false) }
  }
  const attempt = initial.attempt
  return <div className="attempt-workspace">
    <section className="attempt-context"><h2>{attempt.challenge_snapshot.title}</h2>
      <p className="challenge-description">{attempt.challenge_snapshot.description}</p>
      {attempt.challenge_snapshot.starter_code && <><h3>Código inicial</h3><pre>{attempt.challenge_snapshot.starter_code}</pre></>}
      <h2>Resposta enviada</h2><pre>{attempt.draft_answer}</pre>
      <h3>Habilidades e pesos</h3><ul>{attempt.challenge_snapshot.skills.map(item => <li key={item.skill_id}>Skill #{item.skill_id} · {item.weight}%</li>)}</ul>
    </section>
    <section className="attempt-answer"><h2>Avaliação manual</h2>
      {error && <p className="error" role="alert">{error}</p>}
      {evaluation ? <><p className="notice" role="status">Avaliação registrada. Esta tentativa já foi revisada.</p>
        <h3>Feedback geral</h3><p className="challenge-description">{evaluation.feedback}</p>
        <ul className="evaluation-skills">{evaluation.skills.map(item => <li key={item.skill_id}><h4>Skill #{item.skill_id} · {labels[item.classification]}</h4><p className="challenge-description">{item.justification}</p></li>)}</ul>
      </> : <form onSubmit={submit}>
        <p className="dashboard-note">Avalie cada habilidade do contexto original. Evidência insuficiente não significa erro. A avaliação é definitiva.</p>
        <fieldset disabled={busy || uncertain} className="grid gap-6"><legend className="sr-only">Feedback da revisão</legend>
          <div><label htmlFor="review-feedback">Feedback geral</label><textarea id="review-feedback" required maxLength={4000} rows={4} value={feedback} onChange={event => setFeedback(event.target.value)} /></div>
          {skills.map((item, index) => <fieldset key={item.skill_id} className="grid gap-3"><legend>Skill #{item.skill_id}</legend>
            <label htmlFor={`classification-${item.skill_id}`}>Classificação da skill #{item.skill_id}</label><select id={`classification-${item.skill_id}`} required value={item.classification} onChange={event => setSkills(values => values.map((value, i) => i === index ? { ...value, classification: event.target.value as Classification } : value))}>
              <option value="">Escolha uma classificação</option>{Object.entries(labels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
            <div><label htmlFor={`justification-${item.skill_id}`}>Justificativa da skill #{item.skill_id}</label><textarea id={`justification-${item.skill_id}`} required maxLength={2000} rows={3} value={item.justification} onChange={event => setSkills(values => values.map((value, i) => i === index ? { ...value, justification: event.target.value } : value))} /></div>
          </fieldset>)}
          <button className="primary" type="submit">{busy ? 'Registrando…' : 'Registrar avaliação'}</button>
        </fieldset>
      </form>}
      {uncertain && !evaluation && <button className="dashboard-action" disabled={busy} onClick={() => void check()}>Consultar resultado do envio</button>}
    </section>
  </div>
}
