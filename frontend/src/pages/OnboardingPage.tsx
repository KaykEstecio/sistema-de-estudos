import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import axios from 'axios'
import { Link } from 'react-router'
import { useAuth } from '../auth'

const experiences = { NEVER_PROGRAMMED: 'Nunca programei', BEGINNER: 'Iniciante', BASIC: 'Conhecimento básico', INTERMEDIATE: 'Intermediário', ADVANCED: 'Avançado' }
type Experience = keyof typeof experiences
interface Profile { onboarding_completed: boolean; declared_experience: Experience | null; interest_category_ids: number[]; primary_goal: { goal_type: string; description: string | null } | null }
interface Category { id: number; name: string }
interface CategoryPage { items: Category[]; total: number }

function failure(error: unknown) {
  const status = axios.isAxiosError(error) ? error.response?.status : undefined
  if (status === 409) return 'O perfil mudou. Recarregue os dados antes de salvar novamente.'
  if (status === 404) return 'Uma categoria não está mais disponível. Recarregue os dados e revise seus interesses.'
  if (status === 422) return 'Revise a experiência, os interesses e os limites do objetivo.'
  if (status === 403) return 'Sua conta não tem permissão para esta operação.'
  return 'Não foi possível concluir a operação. Seus campos foram preservados; tente novamente.'
}

export default function OnboardingPage() {
  const { client, refreshUser, user } = useAuth()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedNames, setSelectedNames] = useState<Category[]>([])
  const [total, setTotal] = useState(0)
  const [experience, setExperience] = useState<Experience | ''>('')
  const [interests, setInterests] = useState<number[]>([])
  const [goal, setGoal] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [more, setMore] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)
  const [reload, setReload] = useState(0)
  const pending = useRef(false)
  const controller = useRef(new AbortController())

  useEffect(() => {
    const abort = new AbortController()
    controller.current = abort
    setLoading(true); setError(''); setSaved(false)
    async function load() {
      if (!client) return
      try {
        const [response, catalog] = await Promise.all([
          client.get<Profile>('/onboarding', { signal: abort.signal }),
          client.get<CategoryPage>('/categories', { params: { limit: 20, offset: 0 }, signal: abort.signal }),
        ])
        const data = response.data
        const missing = data.interest_category_ids.filter(id => !catalog.data.items.some(item => item.id === id))
        const names = await Promise.all(missing.map(id => client.get<Category>(`/categories/${id}`, { signal: abort.signal })))
        if (abort.signal.aborted) return
        setProfile(data); setExperience(data.declared_experience ?? '')
        setInterests(data.interest_category_ids); setGoal(data.primary_goal?.goal_type ?? '')
        setDescription(data.primary_goal?.description ?? '')
        setCategories(catalog.data.items); setTotal(catalog.data.total)
        setSelectedNames(names.map(item => item.data))
      } catch (cause) { if (!abort.signal.aborted && !axios.isCancel(cause)) setError(failure(cause)) }
      finally { if (!abort.signal.aborted) setLoading(false) }
    }
    void load()
    return () => abort.abort()
  }, [client, reload])

  async function loadMore() {
    if (!client || more) return
    setMore(true); setError('')
    const signal = controller.current.signal
    try {
      const { data } = await client.get<CategoryPage>('/categories', { params: { limit: 20, offset: categories.length }, signal })
      if (!signal.aborted) { setCategories(previous => [...previous, ...data.items]); setTotal(data.total) }
    } catch (cause) { if (!signal.aborted && !axios.isCancel(cause)) setError(failure(cause)) }
    finally { if (!signal.aborted) setMore(false) }
  }
  function toggle(id: number) {
    setSaved(false)
    setInterests(previous => previous.includes(id) ? previous.filter(value => value !== id) : previous.length < 20 ? [...previous, id] : previous)
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!client || !profile || pending.current) return
    if (!experience || !interests.length || !goal.trim()) { setError('Informe sua experiência, escolha ao menos um interesse e preencha o objetivo.'); return }
    pending.current = true; setBusy(true); setError(''); setSaved(false)
    const signal = controller.current.signal
    try {
      const payload = { declared_experience: experience, interest_category_ids: interests, primary_goal: { goal_type: goal.trim(), description: description.trim() || null } }
      const { data } = await client.request<Profile>({ url: '/onboarding', method: profile.onboarding_completed ? 'PATCH' : 'POST', data: payload, signal })
      if (signal.aborted) return
      setProfile(data); setSaved(true)
      try { await refreshUser(signal) }
      catch (cause) { if (!signal.aborted && !axios.isCancel(cause)) setError('Perfil salvo. Não foi possível atualizar a sessão; salve novamente para tentar sincronizar.') }
    } catch (cause) { if (!signal.aborted && !axios.isCancel(cause)) setError(failure(cause)) }
    finally { pending.current = false; if (!signal.aborted) setBusy(false) }
  }

  return <main className="auth-main onboarding-main">
    <h1>Seu ponto de partida</h1><p className="subtitle">Conte o que você quer aprender. Sua experiência declarada não define uma nota.</p>
    {loading && <p role="status">Carregando seu perfil e interesses…</p>}
    {error && <div className="error" role="alert">{error} <button type="button" className="text-button" disabled={busy || more} onClick={() => setReload(value => value + 1)}>Recarregar dados (descarta alterações)</button></div>}
    {saved && <p className="notice" role="status">Perfil salvo com sucesso.</p>}
    {!loading && profile && <form className="auth-form" onSubmit={submit} onChange={() => setSaved(false)}>
      <fieldset disabled={busy} className="onboarding-fields">
        <label htmlFor="experience">Experiência com programação<select id="experience" required value={experience} onChange={event => setExperience(event.target.value as Experience | '')}><option value="">Selecione sua experiência</option>{Object.entries(experiences).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        <fieldset className="interests"><legend>Seus interesses</legend><p id="interest-help">Escolha de 1 a 20 áreas. {interests.length} selecionadas.</p>
          {total === 0 && <p className="notice">Ainda não há categorias disponíveis. O catálogo precisa ser cadastrado antes de continuar.</p>}
          {[...categories, ...selectedNames.filter(item => !categories.some(category => category.id === item.id))].map(category => <label className="interest-option" key={category.id}><input type="checkbox" checked={interests.includes(category.id)} disabled={!interests.includes(category.id) && interests.length >= 20} aria-describedby="interest-help" onChange={() => toggle(category.id)} />{category.name}</label>)}
          {categories.length < total && <button type="button" className="text-button" disabled={more} onClick={() => void loadMore()}>{more ? 'Carregando…' : 'Carregar mais interesses'}</button>}
        </fieldset>
        <label htmlFor="goal">Objetivo de aprendizagem<input id="goal" required maxLength={120} value={goal} onChange={event => setGoal(event.target.value)} placeholder="Ex.: aprender a criar aplicações web" /></label>
        <label htmlFor="description">Mais detalhes (opcional)<textarea id="description" rows={4} maxLength={2000} value={description} onChange={event => setDescription(event.target.value)} /></label>
        <button className="primary" disabled={total === 0 || more} type="submit">{busy ? 'Salvando…' : profile.onboarding_completed ? 'Salvar alterações' : 'Salvar meu perfil'}</button>
      </fieldset>
    </form>}
    {user?.onboarding_completed && <p className="alternate"><Link to="/diagnostico">Continuar para diagnóstico →</Link></p>}
  </main>
}
