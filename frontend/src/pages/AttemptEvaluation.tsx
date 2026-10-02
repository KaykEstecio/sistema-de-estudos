import { useEffect, useState } from 'react'
import axios from 'axios'
import { Link } from 'react-router'
import { useAuth } from '../auth'
import { getEvaluation } from '../services/evaluation'
import { getAttempt } from '../services/attempts'
import type { Evaluation } from '../services/evaluation'

const labels = {
  MET: 'Atendido', PARTIALLY_MET: 'Parcialmente atendido',
  NOT_MET: 'Não atendido', INSUFFICIENT_EVIDENCE: 'Evidência insuficiente',
}

export default function AttemptEvaluation({ attemptId }: { attemptId: number }) {
  const { client } = useAuth()
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
  const [loading, setLoading] = useState(true)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)
  useEffect(() => {
    if (!client) return
    const controller = new AbortController()
    const signal = controller.signal
    setLoading(true); setPending(false); setError(''); setEvaluation(null)
    async function load() {
      try {
        const value = await getEvaluation(client!, attemptId, signal)
        if (!signal.aborted) setEvaluation(value)
      } catch (cause) {
        if (signal.aborted || axios.isCancel(cause) || (axios.isAxiosError(cause) && cause.response?.status === 401)) return
        if (axios.isAxiosError(cause) && cause.response?.status === 404) {
          // A missing review and inaccessible attempt share 404. Recheck ownership.
          try {
            const current = await getAttempt(client!, attemptId, signal)
            if (!signal.aborted) {
              if (current.status === 'SUBMITTED') setPending(true)
              else setError('A tentativa não está enviada. Reabra a tentativa para consultar seu estado atual.')
            }
          } catch (verification) {
            if (signal.aborted || axios.isCancel(verification) || (axios.isAxiosError(verification) && verification.response?.status === 401)) return
            setError('Não foi possível confirmar o acesso à tentativa. Tente consultar novamente.')
          }
        } else setError('Não foi possível carregar a avaliação. Tente consultar novamente.')
      } finally { if (!signal.aborted) setLoading(false) }
    }
    void load()
    return () => controller.abort()
  }, [client, attemptId, reload])

  return <section className="attempt-evaluation" aria-labelledby="evaluation-title" aria-busy={loading}>
    <div className="section-heading"><h2 id="evaluation-title">Avaliação manual</h2>
      <button className="dashboard-action" disabled={loading} onClick={() => setReload(value => value + 1)}>Atualizar avaliação</button>
    </div>
    {loading && <p role="status">Consultando avaliação…</p>}
    {pending && <p className="notice" role="status">Sua resposta aguarda revisão manual por um administrador. Você pode atualizar esta consulta para verificar se a avaliação está disponível.</p>}
    {error && <p className="error" role="alert">{error}</p>}
    {evaluation && <>
      <p className="dashboard-note">Revisada em {new Date(evaluation.created_at).toLocaleString('pt-BR')} · Rubrica {evaluation.rubric_version}</p>
      <h3>Feedback geral</h3><p className="challenge-description">{evaluation.feedback}</p>
      <h3>Resultados por habilidade</h3>
      <ul className="evaluation-skills">{evaluation.skills.map(skill => <li key={skill.skill_id}>
        <h4>Skill #{skill.skill_id} · {labels[skill.classification]}</h4>
        <p className="challenge-description">{skill.justification}</p>
        {skill.classification === 'INSUFFICIENT_EVIDENCE' && <p className="dashboard-note">Evidência insuficiente não equivale a erro; a resposta não permite concluir sobre esta habilidade.</p>}
      </li>)}</ul>
    </>}
    <p className="dashboard-note"><Link to="/dashboard">Voltar ao painel</Link> para consultar seu progresso por habilidade e as próximas recomendações.</p>
  </section>
}
