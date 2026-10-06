import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useBlocker, useNavigate, useParams, useSearchParams } from 'react-router'
import axios from 'axios'
import { useAuth } from '../auth'
import { useRegisterExitGuard } from '../exitGuard'
import { getStudy, getStudyPage } from '../services/study'
import type { StudyContent, StudyPage as StudyPageData, StudyInput } from '../services/study'

const ignored = (cause: unknown) => axios.isCancel(cause) || (axios.isAxiosError(cause) && cause.response?.status === 401)

export default function StudyPage() {
  const { client, user } = useAuth()
  const [params] = useSearchParams()
  const skill = params.get('skill')
  const skillId = skill ? Number(skill) : undefined
  const valid = !skill || (/^[1-9]\d*$/.test(skill) && Number(skill) <= 2147483647)
  const [offset, setOffset] = useState(0)
  const [reload, setReload] = useState(0)
  const [data, setData] = useState<StudyPageData | null>(null)
  const [error, setError] = useState('')
  useEffect(() => {
    if (!client || !valid) return
    const controller = new AbortController()
    setData(null); setError('')
    getStudyPage(client, skillId, offset, controller.signal).then(value => { if (!controller.signal.aborted) setData(value) })
      .catch(cause => { if (!controller.signal.aborted && !ignored(cause)) setError('Não foi possível carregar os conteúdos.') })
    return () => controller.abort()
  }, [client, skillId, offset, reload, valid])
  return <main className="dashboard-main"><p className="eyebrow">Aprender antes de praticar</p><h1>Área de estudo</h1>
    <p className="dashboard-note">Explicações e exemplos por habilidade. Marcar como estudado não altera seu score.</p>
    {user?.role === 'ADMIN' && <Link className="dashboard-action" to="/admin/conteudos/novo">Cadastrar conteúdo</Link>}
    {skill && <p className="dashboard-note">Conteúdos da skill #{skill}. <Link to="/estudar">Ver todas as habilidades</Link></p>}
    {!valid && <p className="error" role="alert">Habilidade inválida.</p>}
    {error && <p className="error" role="alert">{error} <button className="text-button" onClick={() => setReload(value => value + 1)}>Tentar novamente</button></p>}
    {valid && !data && !error && <p role="status">Carregando conteúdos…</p>}
    {valid && data && <>
      <p role="status">{data.total} conteúdos · Página {Math.floor(offset / 10) + 1}</p>
      {data.items.length ? <ul className="recommendation-list">{data.items.map(item => <li key={item.id}>
        <p className="eyebrow">{item.skill_name}</p><h2>{item.title}</h2>
        <p>{item.completed_at ? 'Estudado' : 'Ainda não marcado como estudado'}</p>
        <Link className="dashboard-action" to={`/estudar/${item.id}`}>Estudar: {item.title}</Link>
      </li>)}</ul> : <p className="notice">Nenhum conteúdo disponível nesta página.{offset > 0 && <button className="text-button" onClick={() => setOffset(0)}>Voltar à primeira página</button>}</p>}
      <nav className="progress-pagination" aria-label="Páginas dos conteúdos"><button className="dashboard-action" disabled={offset === 0} onClick={() => setOffset(offset - 10)}>Anterior</button>
        <button className="dashboard-action" disabled={offset + 10 >= data.total} onClick={() => setOffset(offset + 10)}>Próxima</button></nav>
    </>}
  </main>
}

export function StudyDetailPage() {
  const { id } = useParams()
  const { client } = useAuth()
  const [data, setData] = useState<StudyContent | null>(null)
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)
  const [busy, setBusy] = useState(false)
  const pending = useRef<AbortController | null>(null)
  useEffect(() => {
    if (!client) return
    setData(null); setError('')
    const controller = new AbortController()
    if (!/^[1-9]\d*$/.test(id || '') || Number(id) > 2147483647) { setError('Conteúdo inválido.'); return }
    getStudy(client, Number(id), controller.signal).then(value => { if (!controller.signal.aborted) setData(value) })
      .catch(cause => { if (!controller.signal.aborted && !ignored(cause)) setError('Conteúdo indisponível ou falha de conexão.') })
    return () => controller.abort()
  }, [client, id, reload])
  useEffect(() => () => pending.current?.abort(), [])
  async function complete() {
    if (!client || !data || pending.current) return
    const controller = new AbortController(); pending.current = controller; setBusy(true); setError('')
    try {
      const result = await client.put<StudyContent>(`/study/${data.id}/completion`, undefined, { signal: controller.signal })
      if (!controller.signal.aborted) setData(result.data)
    } catch (cause) {
      if (!controller.signal.aborted && !ignored(cause)) setError('Não foi possível confirmar a leitura. Você pode tentar marcar novamente sem duplicar o registro.')
    } finally { if (!controller.signal.aborted) { pending.current = null; setBusy(false) } }
  }
  return <main className="dashboard-main attempt-detail"><Link to="/estudar">Voltar aos conteúdos</Link>
    {error && <p className="error" role="alert">{error} {!data && <button className="text-button" onClick={() => setReload(value => value + 1)}>Tentar novamente</button>}</p>}
    {!data && !error && <p role="status">Carregando leitura…</p>}
    {data && <><p className="eyebrow">{data.skill_name}</p><h1>{data.title}</h1>
      <section className="attempt-context"><h2>Explicação</h2><p className="challenge-description">{data.explanation}</p>
        <h2>Exemplo de código</h2><pre><code>{data.code_example}</code></pre>
        <h2>Erros comuns</h2><p className="challenge-description">{data.common_mistakes}</p></section>
      <p className="dashboard-note">A leitura não comprova domínio e não altera seu score. Pratique para produzir evidências.</p>
      {data.completed_at ? <p className="notice" role="status">Conteúdo marcado como estudado.</p> : <button className="primary" disabled={busy} onClick={() => void complete()}>{busy ? 'Salvando…' : 'Marcar como estudado'}</button>}
      <p className="alternate"><Link to="/dashboard">Ir ao painel para praticar</Link></p>
    </>}
  </main>
}

export function CreateStudyPage() {
  const { client } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', explanation: '', code_example: '', common_mistakes: '' })
  const [skillId, setSkillId] = useState('')
  const [skills, setSkills] = useState<{ id: number; name: string; is_active: boolean }[]>([])
  const [offset, setOffset] = useState(0)
  const [total, setTotal] = useState(0)
  const [loaded, setLoaded] = useState(false)
  const [reload, setReload] = useState(0)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [uncertain, setUncertain] = useState(false)
  const [created, setCreated] = useState<StudyContent | null>(null)
  const operation = useRef<AbortController | null>(null)
  const dirty = !created && (busy || uncertain || Boolean(skillId) || Object.values(form).some(Boolean))
  const blocker = useBlocker(dirty)
  useRegisterExitGuard(dirty)
  useEffect(() => {
    if (blocker.state === 'blocked') {
      if (window.confirm('Sair do cadastro? O texto não salvo será perdido. Um envio pode ter sido concluído.')) blocker.proceed()
      else blocker.reset()
    }
  }, [blocker.state, blocker.proceed, blocker.reset])
  useEffect(() => {
    if (!dirty) return
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = '' }
    window.addEventListener('beforeunload', warn); return () => window.removeEventListener('beforeunload', warn)
  }, [dirty])
  useEffect(() => () => operation.current?.abort(), [])
  useEffect(() => {
    if (!client) return
    const controller = new AbortController(); setLoaded(false); setError('')
    client.get<{ items: typeof skills; total: number }>('/skills', { params: { limit: 50, offset }, signal: controller.signal })
      .then(({ data }) => { if (!controller.signal.aborted) { setSkills(data.items); setTotal(data.total); setLoaded(true) } })
      .catch(cause => { if (!controller.signal.aborted && !ignored(cause)) setError('Não foi possível carregar as habilidades.') })
    return () => controller.abort()
  }, [client, offset, reload])
  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!client || operation.current || uncertain || created) return
    if (!Object.values(form).every(value => value.trim())) { setError('Preencha todos os campos.'); return }
    if (!window.confirm('Publicar este conteúdo para os alunos? Revise o texto antes de confirmar.')) return
    const controller = new AbortController(); operation.current = controller; setBusy(true); setError('')
    const data: StudyInput = { ...form, skill_id: Number(skillId) }
    try {
      const result = await client.post<StudyContent>('/study', data, { signal: controller.signal })
      if (!controller.signal.aborted) setCreated(result.data)
    } catch (cause) {
      if (!controller.signal.aborted && !ignored(cause)) {
        if (axios.isAxiosError(cause) && cause.response && cause.response.status < 500) setError('Confira a habilidade ativa e os limites dos campos. Seu acesso pode ter sido alterado.')
        else { setUncertain(true); setError('Envio não confirmado. Consulte a biblioteca antes de iniciar outro cadastro para evitar conteúdo duplicado.') }
      }
    } finally { if (!controller.signal.aborted) { operation.current = null; setBusy(false) } }
  }
  return <main className="auth-main onboarding-main"><Link to="/estudar">Voltar à biblioteca</Link><h1>Cadastrar conteúdo</h1>
    <p className="dashboard-note">Publique um conteúdo curto e revisado para uma habilidade. Não há edição após publicar neste recorte.</p>
    {error && <p className="error" role="alert">{error}</p>}
    {created ? <><p role="status">Conteúdo publicado.</p><button className="dashboard-action" onClick={() => navigate(`/estudar/${created.id}`)}>Abrir conteúdo publicado</button></> : <form className="auth-form" onSubmit={submit}>
      <fieldset disabled={busy || uncertain} className="grid gap-6"><legend className="sr-only">Conteúdo de estudo</legend>
        <div><label htmlFor="study-skill">Habilidade</label><select id="study-skill" required disabled={!loaded} value={skillId} onChange={event => setSkillId(event.target.value)}>
          <option value="">Escolha uma habilidade ativa</option>{skills.filter(item => item.is_active).map(item => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select><p className="dashboard-note">Página {Math.floor(offset / 50) + 1} do catálogo.</p>
        <button type="button" className="text-button" disabled={offset === 0 || !loaded} onClick={() => { setSkillId(''); setOffset(offset - 50) }}>Habilidades anteriores</button>{' '}
        <button type="button" className="text-button" disabled={offset + 50 >= total || !loaded} onClick={() => { setSkillId(''); setOffset(offset + 50) }}>Próximas habilidades</button>
        {!loaded && <button type="button" className="text-button" onClick={() => setReload(value => value + 1)}>Recarregar habilidades</button>}</div>
        <label>Título<input required maxLength={200} value={form.title} onChange={event => setForm({ ...form, title: event.target.value })} /></label>
        {(['explanation', 'code_example', 'common_mistakes'] as const).map(key => <div key={key}><label htmlFor={key}>{({ explanation: 'Explicação', code_example: 'Exemplo de código', common_mistakes: 'Erros comuns' })[key]}</label>
          <textarea id={key} required rows={5} maxLength={key === 'common_mistakes' ? 6000 : 12000} value={form[key]} onChange={event => setForm({ ...form, [key]: event.target.value })} /></div>)}
        <button className="primary" disabled={!loaded || !skillId} type="submit">{busy ? 'Publicando…' : 'Publicar conteúdo'}</button>
      </fieldset>
    </form>}
  </main>
}
