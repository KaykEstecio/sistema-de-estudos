import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import { Link, useParams } from 'react-router'
import { useAuth } from '../auth'
import { getAttempt, getAttempts } from '../services/attempts'
import type { Attempt, AttemptPage } from '../services/attempts'

const date = (value: string) => new Date(value).toLocaleString('pt-BR')
const status = (value: string) => value === 'IN_PROGRESS' ? 'Em andamento' : 'Enviada'
function showError(cause: unknown, signal: AbortSignal) {
  return !signal.aborted && !axios.isCancel(cause) && !(axios.isAxiosError(cause) && cause.response?.status === 401)
}

export default function AttemptsPage() {
  const { client } = useAuth()
  const [offset, setOffset] = useState(0)
  const [reload, setReload] = useState(0)
  const [page, setPage] = useState<AttemptPage | null>(null)
  const [error, setError] = useState('')
  const title = useRef<HTMLHeadingElement>(null)
  useEffect(() => { title.current?.focus() }, [])
  useEffect(() => {
    if (!client) return
    const controller = new AbortController()
    setPage(null); setError('')
    getAttempts(client, offset, controller.signal).then(result => {
      if (!controller.signal.aborted) setPage(result)
    }).catch((cause: unknown) => { if (showError(cause, controller.signal)) setError('Não foi possível carregar suas tentativas.') })
    return () => controller.abort()
  }, [client, offset, reload])
  return <main className="dashboard-main">
    <h1 ref={title} tabIndex={-1}>Minhas tentativas</h1>
    <p className="dashboard-note">Retome seus rascunhos ou consulte respostas enviadas.</p>
    {!page && !error && <p role="status">Carregando tentativas…</p>}
    {error && <div role="alert" className="error">{error} <button className="text-button" onClick={() => setReload(value => value + 1)}>Tentar novamente</button></div>}
    {page && <>
      {!page.total ? <div className="dashboard-empty"><p>Você ainda não iniciou uma tentativa.</p><Link to="/dashboard">Encontrar um desafio no painel</Link></div>
        : !page.items.length ? <p className="notice">Não há tentativas nesta página. <button className="text-button" onClick={() => setOffset(0)}>Voltar à primeira página</button></p>
        : <ul className="recommendation-list">{page.items.map(item => <li key={item.id}>
          <p className="eyebrow">{status(item.status)} · Tentativa {item.attempt_number}</p>
          <h2>{item.title}</h2><p className="dashboard-note">Última atividade: {date(item.last_activity_at)}</p>
          <Link className="dashboard-action" to={`/tentativas/${item.id}`} aria-label={`${item.status === 'IN_PROGRESS' ? 'Retomar' : 'Ver envio'}: ${item.title}`}>{item.status === 'IN_PROGRESS' ? 'Retomar' : 'Ver envio'}</Link>
        </li>)}</ul>}
      {page.total > 0 && <nav className="progress-pagination" aria-label="Páginas das tentativas">
        <button className="dashboard-action" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - page.limit))}>Anterior</button>
        <p role="status">Página {Math.floor(offset / page.limit) + 1} · {page.total} tentativas</p>
        <button className="dashboard-action" disabled={offset + page.limit >= page.total} onClick={() => setOffset(offset + page.limit)}>Próxima</button>
      </nav>}
    </>}
  </main>
}

export function AttemptDetailPage() {
  const { id = '' } = useParams()
  const { user } = useAuth()
  if (!/^[1-9]\d*$/.test(id) || Number(id) > 2147483647) return <main className="dashboard-main"><h1>Tentativa não encontrada</h1><Link to="/tentativas">Voltar às tentativas</Link></main>
  return <AttemptDetail key={`${user?.id}:${id}`} id={Number(id)} />
}
function AttemptDetail({ id }: { id: number }) {
  const { client } = useAuth()
  const [attempt, setAttempt] = useState<Attempt | null>(null)
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)
  const heading = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    if (!client) return
    const controller = new AbortController()
    setAttempt(null); setError('')
    getAttempt(client, id, controller.signal).then(result => {
      if (!controller.signal.aborted) setAttempt(result)
    }).catch((cause: unknown) => {
      if (showError(cause, controller.signal)) setError(axios.isAxiosError(cause) && cause.response?.status === 404
        ? 'Tentativa não encontrada.' : 'Não foi possível carregar a tentativa.')
    })
    return () => controller.abort()
  }, [client, id, reload])
  useEffect(() => { if (attempt) heading.current?.focus() }, [attempt])
  return <main className="dashboard-main attempt-detail">
    <Link to="/tentativas">Voltar às tentativas</Link>
    {!attempt && !error && <p role="status">Carregando tentativa…</p>}
    {error && <div role="alert" className="error">{error} <button className="text-button" onClick={() => setReload(value => value + 1)}>Tentar novamente</button></div>}
    {attempt && <>
      <p className="eyebrow">{status(attempt.status)} · Tentativa {attempt.attempt_number}</p>
      <h1 ref={heading} tabIndex={-1}>{attempt.challenge_snapshot.title}</h1>
      <p className="dashboard-note">Dificuldade {attempt.challenge_snapshot.difficulty_score}/1.000 · cerca de {attempt.challenge_snapshot.estimated_minutes} min</p>
      <h2>Enunciado</h2><p className="challenge-description">{attempt.challenge_snapshot.description}</p>
      {attempt.challenge_snapshot.starter_code && <><h2>Código inicial</h2><pre><code>{attempt.challenge_snapshot.starter_code}</code></pre></>}
      <h2>Habilidades do desafio</h2><ul>{attempt.challenge_snapshot.skills.map(skill => <li key={skill.skill_id}>Skill #{skill.skill_id} · peso {skill.weight}%</li>)}</ul>
      <h2>{attempt.status === 'SUBMITTED' ? 'Resposta enviada' : 'Rascunho salvo'}</h2>
      {attempt.draft_answer ? <pre>{attempt.draft_answer}</pre> : <p>Nenhuma resposta salva ainda.</p>}
      {attempt.status === 'IN_PROGRESS' && <p className="notice">A edição e o envio pela interface estarão disponíveis na próxima etapa.</p>}
      <p className="dashboard-note">Iniciada em {date(attempt.started_at)}{attempt.submitted_at && ` · Enviada em ${date(attempt.submitted_at)}`}</p>
    </>}
  </main>
}
