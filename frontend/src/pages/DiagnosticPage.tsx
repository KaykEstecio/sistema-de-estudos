import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import axios from 'axios'
import { useAuth } from '../auth'
import { assessmentError, lastAssessment, rememberAssessment, validId } from '../services/assessment'
import type { Assessment, Skill } from '../services/assessment'

export default function DiagnosticPage() {
  const { client, user } = useAuth()
  const navigate = useNavigate()
  const [skills, setSkills] = useState<Skill[]>([])
  const [selected, setSelected] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)
  const [resume, setResume] = useState('')
  const pending = useRef(false)
  const controller = useRef(new AbortController())
  const last = user ? lastAssessment(user.id) : ''
  useEffect(() => {
    const abort = new AbortController(); controller.current = abort
    setLoading(true); setError('')
    async function load() {
      if (!client) return
      try {
        const { data } = await client.get<{ interest_category_ids: number[] }>('/onboarding', { signal: abort.signal })
        const groups = await Promise.all(data.interest_category_ids.map(async category => {
          const collected: Skill[] = []
          let offset = 0
          while (true) {
            const page = await client.get<{ items: Skill[]; total: number }>('/skills', { params: { category_id: category, is_active: true, limit: 100, offset }, signal: abort.signal })
            collected.push(...page.data.items); offset += page.data.items.length
            if (!page.data.items.length || offset >= page.data.total) return collected
          }
        }))
        if (!abort.signal.aborted) {
          const available = [...new Map(groups.flat().map(skill => [skill.id, skill])).values()]
          setSkills(available); setSelected(previous => previous.filter(id => available.some(skill => skill.id === id)))
        }
      } catch (cause) { if (!abort.signal.aborted && !axios.isCancel(cause)) setError(assessmentError(cause)) }
      finally { if (!abort.signal.aborted) setLoading(false) }
    }
    void load(); return () => abort.abort()
  }, [client, retry])
  async function start() {
    if (!client || !user || pending.current || !selected.length) return
    pending.current = true; setBusy(true); setError('')
    const signal = controller.current.signal
    try {
      const { data } = await client.post<Assessment>('/assessments', { skill_ids: selected }, { signal })
      if (!signal.aborted) { rememberAssessment(user.id, data.id); navigate(`/diagnostico/${data.id}`) }
    } catch (cause) { if (!signal.aborted && !axios.isCancel(cause)) setError(assessmentError(cause)) }
    finally { pending.current = false; if (!signal.aborted) setBusy(false) }
  }
  return <main className="auth-main onboarding-main"><h1>Diagnóstico inicial</h1><p className="subtitle">Escolha de 1 a 3 habilidades dos seus interesses para identificar seu ponto de partida.</p>
    {error && <p className="error" role="alert">{error}</p>}
    {loading ? <p role="status">Carregando habilidades…</p> : <>
      {!skills.length ? <p className="notice">Não há habilidades ativas disponíveis nos seus interesses. <Link to="/onboarding">Revisar perfil</Link></p> : <fieldset className="auth-form interests" disabled={busy}><legend>Habilidades ({selected.length}/3)</legend>{skills.map(skill => <label className="interest-option" key={skill.id}><input type="checkbox" checked={selected.includes(skill.id)} disabled={!selected.includes(skill.id) && selected.length === 3} onChange={() => setSelected(previous => previous.includes(skill.id) ? previous.filter(id => id !== skill.id) : [...previous, skill.id])} />{skill.name}</label>)}<button className="primary" disabled={!selected.length} onClick={() => void start()}>{busy ? 'Iniciando…' : 'Iniciar diagnóstico'}</button></fieldset>}
      <button className="text-button" disabled={busy} onClick={() => setRetry(value => value + 1)}>Atualizar habilidades</button>
    </>}
    <section className="resume"><h2>Retomar diagnóstico</h2>{last && <p><Link to={`/diagnostico/${last}`}>Abrir último diagnóstico neste navegador (#{last})</Link></p>}
      <p>Guarde o link ou o número do diagnóstico. Em outro navegador, informe o número para retomá-lo.</p>
      <form className="auth-form" onSubmit={event => { event.preventDefault(); if (validId(resume)) navigate(`/diagnostico/${resume}`) }}><label>Número do diagnóstico<input inputMode="numeric" pattern="[1-9][0-9]*" required value={resume} onChange={event => setResume(event.target.value)} /></label><button className="primary" disabled={!validId(resume)}>Abrir diagnóstico</button></form>
    </section></main>
}
