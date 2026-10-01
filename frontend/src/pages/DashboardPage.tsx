import { useCallback, useEffect, useState } from 'react'
import axios from 'axios'
import { Link } from 'react-router'
import { useAuth } from '../auth'
import { getDashboard } from '../services/dashboard'
import type { Dashboard } from '../services/dashboard'
import DashboardRecommendations from './DashboardRecommendations'

const dates = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium', timeStyle: 'short' })
const confidence = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 6 })

export default function DashboardPage() {
  const { client } = useAuth()
  const [data, setData] = useState<Dashboard | null>(null)
  const [offset, setOffset] = useState(0)
  const [reload, setReload] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const refreshContext = useCallback(() => setReload(value => value + 1), [])

  useEffect(() => {
    if (!client) return
    const controller = new AbortController()
    setLoading(true); setError('')
    getDashboard(client, offset, controller.signal).then(result => {
      if (!controller.signal.aborted) setData(result)
    }).catch((cause: unknown) => {
      if (!controller.signal.aborted && !axios.isCancel(cause)
          && !(axios.isAxiosError(cause) && cause.response?.status === 401)) {
        setError('Não foi possível carregar seu resumo. Tente novamente.')
      }
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [client, offset, reload])

  return <main className="dashboard-main">
    <div className="dashboard-heading">
      <div><p className="eyebrow">Seu aprendizado</p><h1>Meu painel</h1>
        <p className="dashboard-intro">Acompanhe suas habilidades, uma prática de cada vez.</p></div>
      <Link className="dashboard-action" to="/onboarding">Meu perfil</Link>
    </div>
    {loading && <p className="notice" role="status">Carregando seu resumo…</p>}
    {error && <div className="error" role="alert"><p>{error}</p>
      <button className="dashboard-action" onClick={() => setReload(value => value + 1)}>Tentar novamente</button></div>}
    {data && <>
      <section className="dashboard-profile" aria-label="Seu perfil">
        <h2>Olá, {data.profile.name}.</h2>
        {data.profile.primary_goal ? <p>Seu objetivo: <strong>{data.profile.primary_goal.goal_type}</strong></p>
          : <p>Defina seu objetivo para organizar os próximos passos.</p>}
        {data.profile.primary_goal?.description && <p className="goal-description">{data.profile.primary_goal.description}</p>}
        {data.profile.interests.length > 0 ? <p>Interesses: {data.profile.interests.map(item => item.name).join(', ')}.</p>
          : <p className="notice">Você ainda não escolheu seus interesses. <Link to="/onboarding">Configurar perfil</Link></p>}
      </section>
      <dl className="dashboard-stats" aria-label="Resumo de atividade">
        <div><dt>Habilidades acompanhadas</dt><dd>{data.summary.tracked_skills}</dd><p>Com evidências de prática avaliadas.</p></div>
        <div><dt>Tentativas enviadas</dt><dd>{data.summary.submitted_attempts}</dd><p>Inclui novas tentativas do mesmo desafio.</p></div>
        <div><dt>Aguardando revisão</dt><dd>{data.summary.pending_reviews}</dd><p>Envios que ainda não receberam avaliação.</p></div>
      </dl>
      <DashboardRecommendations interests={data.profile.interests} refreshContext={refreshContext} />
      <section className="dashboard-progress" aria-labelledby="progress-title">
        <div className="section-heading"><h2 id="progress-title">Suas habilidades</h2>
          <Link to={data.profile.onboarding_completed ? '/diagnostico' : '/onboarding'}>
            {data.profile.onboarding_completed ? 'Fazer diagnóstico' : 'Preparar meu perfil'}</Link></div>
        <p className="dashboard-note" id="confidence-note">Score de 0 a 1.000 por habilidade. Confiança é um índice experimental de evidência, não um percentual de domínio.</p>
        {data.progress.total === 0 ? <div className="dashboard-empty">
          <h3>Seu progresso começa com a prática</h3>
          <p>As habilidades aparecerão aqui após uma prática com evidência avaliável. O diagnóstico oferece uma referência inicial e fica separado deste progresso.</p>
        </div> : <>
          {data.progress.items.length === 0 ? <p className="notice">Não há habilidades nesta página. <button className="text-button" onClick={() => setOffset(0)}>Voltar à primeira página</button></p>
            : <ul className="skill-progress-list" aria-describedby="confidence-note">{data.progress.items.map(skill => <li key={skill.skill_id}>
              <div className="skill-heading"><h3>{skill.name}</h3>{!skill.is_active && <span className="inactive-label">Desativada no catálogo</span>}</div>
              <dl className="skill-values"><div><dt>Score</dt><dd>{skill.score} <span>/ 1.000</span></dd></div>
                <div><dt>Confiança</dt><dd>{confidence.format(Number(skill.confidence))}</dd></div>
                <div><dt>Evidências avaliáveis</dt><dd>{skill.attempts}</dd></div>
                <div><dt>Avaliações com critérios atendidos</dt><dd>{skill.successful_attempts}</dd></div></dl>
              <p className="practice-date">Última prática: <time dateTime={skill.last_practiced_at}>{dates.format(new Date(skill.last_practiced_at))}</time></p>
            </li>)}</ul>}
          <nav className="progress-pagination" aria-label="Páginas do progresso">
            <button className="dashboard-action" disabled={loading || data.progress.offset === 0} onClick={() => setOffset(Math.max(0, data.progress.offset - data.progress.limit))}>Anterior</button>
            <p role="status">Página {Math.floor(data.progress.offset / data.progress.limit) + 1} · {data.progress.total} habilidades</p>
            <button className="dashboard-action" disabled={loading || data.progress.offset + data.progress.limit >= data.progress.total} onClick={() => setOffset(data.progress.offset + data.progress.limit)}>Próxima</button>
          </nav>
        </>}
      </section>
    </>}
  </main>
}
