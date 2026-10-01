import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { Link, useNavigate } from 'react-router'
import { startAttempt } from '../services/attempts'
import { useAuth } from '../auth'
import { getChallenge, getRecommendations, getSkills } from '../services/recommendations'
import type { CatalogSkill, ChallengeDetail, Recommendations, SkillPage } from '../services/recommendations'

function failed(cause: unknown, signal: AbortSignal) {
  return !signal.aborted && !axios.isCancel(cause) && !(axios.isAxiosError(cause) && cause.response?.status === 401)
}
const kinds = { EXPLORATION: 'Exploração', PRACTICE: 'Prática', PROGRESSION: 'Progressão', REVIEW: 'Revisão' }

export default function DashboardRecommendations({ interests, refreshContext }: {
  interests: { category_id: number; name: string }[]; refreshContext: () => void
}) {
  const { client } = useAuth()
  const [category, setCategory] = useState('')
  const selected = interests.some(item => String(item.category_id) === category) ? category : ''
  useEffect(() => { if (!selected) setCategory('') }, [selected])
  return <section className="dashboard-recommendations" aria-labelledby="recommendations-title">
    <h2 id="recommendations-title">O que praticar a seguir</h2>
    <p className="dashboard-note">Escolha uma habilidade para ver atividades e entender por que foram sugeridas.</p>
    {!interests.length ? <p className="notice"><Link to="/onboarding">Escolha seus interesses no perfil</Link> para consultar sugestões.</p>
      : <label className="recommendation-label">Área de interesse<select value={selected} onChange={event => setCategory(event.target.value)}>
        <option value="">Selecione uma área</option>{interests.map(item => <option key={item.category_id} value={item.category_id}>{item.name}</option>)}
      </select></label>}
    {client && selected && <SkillPicker key={selected} client={client} category={Number(selected)} refreshContext={refreshContext} />}
  </section>
}

function SkillPicker({ client, category, refreshContext }: { client: AxiosInstance; category: number; refreshContext: () => void }) {
  const [offset, setOffset] = useState(0)
  const [reload, setReload] = useState(0)
  const [page, setPage] = useState<SkillPage | null>(null)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<CatalogSkill | null>(null)
  useEffect(() => {
    const controller = new AbortController()
    setPage(null); setError('')
    getSkills(client, category, offset, controller.signal).then(result => {
      if (!controller.signal.aborted) setPage(result)
    }).catch((cause: unknown) => { if (failed(cause, controller.signal)) setError('Não foi possível carregar as habilidades.') })
    return () => controller.abort()
  }, [client, category, offset, reload])
  return <div className="skill-picker">
    {!page && !error && <p role="status">Carregando habilidades…</p>}
    {error && <div className="error" role="alert">{error} <button className="text-button" onClick={() => setReload(value => value + 1)}>Tentar carregar habilidades novamente</button></div>}
    {page && <>
      {page.total === 0 ? <p className="notice">Ainda não há habilidades ativas nesta área.</p>
        : <fieldset><legend>Habilidade para praticar</legend>
          <div className="skill-options">{page.items.map(skill => <label key={skill.id}>
            <input type="radio" name="recommendation-skill" value={skill.id} checked={selected?.id === skill.id} onChange={() => setSelected(skill)} />{skill.name}
          </label>)}</div>
          {!page.items.length && <p>Nenhuma habilidade nesta página.</p>}
          <nav className="progress-pagination" aria-label="Páginas das habilidades disponíveis">
            <button className="dashboard-action" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - page.limit))}>Habilidades anteriores</button>
            <p>Página {Math.floor(offset / page.limit) + 1} · {page.total} habilidades</p>
            <button className="dashboard-action" disabled={offset + page.limit >= page.total} onClick={() => setOffset(offset + page.limit)}>Próximas habilidades</button>
          </nav>
        </fieldset>}
    </>}
    {selected && <Suggestions key={selected.id} client={client} skill={selected} refreshContext={refreshContext} />}
  </div>
}

function Suggestions({ client, skill, refreshContext }: { client: AxiosInstance; skill: CatalogSkill; refreshContext: () => void }) {
  const [data, setData] = useState<Recommendations | null>(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [reload, setReload] = useState(0)
  const [challenge, setChallenge] = useState<number | null>(null)
  const [detail, setDetail] = useState<ChallengeDetail | null>(null)
  const [detailError, setDetailError] = useState('')
  const [detailReload, setDetailReload] = useState(0)
  const detailTitle = useRef<HTMLHeadingElement>(null)
  const openButton = useRef<HTMLButtonElement | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    setData(null); setError(''); setChallenge(null); setDetail(null)
    getRecommendations(client, skill.id, controller.signal).then(result => {
      if (!controller.signal.aborted) setData(result)
    }).catch((cause: unknown) => {
      if (!failed(cause, controller.signal)) return
      if (axios.isAxiosError(cause) && cause.response?.status === 404) {
        setError('Esta habilidade não está mais disponível para recomendação. Atualize o perfil ou escolha outra habilidade.')
        refreshContext()
      } else setError('Não foi possível carregar as sugestões.')
    })
    return () => controller.abort()
  }, [client, skill.id, reload, refreshContext])

  useEffect(() => {
    if (challenge === null) return
    const controller = new AbortController()
    setDetail(null); setDetailError('')
    // Revalida elegibilidade também para ADMIN, cujo catálogo permite inativos.
    Promise.all([getChallenge(client, challenge, controller.signal), getRecommendations(client, skill.id, controller.signal)])
      .then(([result, current]) => {
        if (controller.signal.aborted) return
        if (!result.is_active || !current.items.some(item => item.challenge_id === challenge)) {
          setNotice('Este desafio não está mais entre as sugestões disponíveis. A lista foi atualizada.')
          setChallenge(null); setReload(value => value + 1); return
        }
        setDetail(result)
      }).catch((cause: unknown) => {
        if (!failed(cause, controller.signal)) return
        if (axios.isAxiosError(cause) && cause.response?.status === 404) {
          setNotice('O desafio ou a habilidade ficou indisponível. As sugestões foram atualizadas.')
          setChallenge(null); setReload(value => value + 1)
        } else setDetailError('Não foi possível carregar o desafio. Tente novamente.')
      })
    return () => controller.abort()
  }, [client, challenge, skill.id, detailReload])
  useEffect(() => { if (detail) detailTitle.current?.focus() }, [detail])

  return <div className="suggestions">
    <div className="section-heading"><h3>Sugestões para {skill.name}</h3><button className="text-button" onClick={() => { setNotice(''); setReload(value => value + 1) }}>Atualizar sugestões</button></div>
    {notice && <p className="notice" role="status">{notice}</p>}
    {!data && !error && <p role="status">Buscando sugestões…</p>}
    {error && <div className="error" role="alert">{error} <button className="text-button" onClick={() => setReload(value => value + 1)}>Tentar sugestões novamente</button></div>}
    {data?.items.length === 0 && <p className="notice">Não há atividades elegíveis para esta habilidade agora. Isso não significa que você já domina todo o conteúdo.</p>}
    {data && <ul className="recommendation-list">{data.items.map(item => <li key={item.challenge_id}>
      <p className="eyebrow">{kinds[item.kind]}</p><h4>{item.title}</h4>
      <p className="dashboard-note">Dificuldade {item.difficulty_score}/1.000 · cerca de {item.estimated_minutes} min</p>
      <p>{item.reason}</p><button className="dashboard-action" onClick={event => { openButton.current = event.currentTarget; setDetail(null); setDetailError(''); setChallenge(item.challenge_id); setDetailReload(value => value + 1) }}>Ver desafio: {item.title}</button>
    </li>)}</ul>}
    {challenge !== null && <section className="challenge-preview" aria-label="Leitura do desafio">
      <button className="text-button" onClick={() => { setChallenge(null); setDetail(null); openButton.current?.focus() }}>Fechar leitura</button>
      {!detail && !detailError && <p role="status">Carregando desafio…</p>}
      {detailError && <div className="error" role="alert">{detailError} <button className="text-button" onClick={() => setDetailReload(value => value + 1)}>Tentar abrir desafio novamente</button></div>}
      {detail && <><h3 ref={detailTitle} tabIndex={-1}>{detail.title}</h3>
        <StartAttempt key={detail.id} client={client} id={detail.id} />
        <p className="challenge-description">{detail.description}</p>
        {detail.starter_code && <><h4>Código inicial</h4><pre><code>{detail.starter_code}</code></pre></>}
      </>}
    </section>}
  </div>
}

function StartAttempt({ client, id }: { client: AxiosInstance; id: number }) {
  const navigate = useNavigate()
  const pending = useRef<AbortController | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => () => { pending.current?.abort() }, [])
  async function start() {
    if (pending.current) return
    const controller = new AbortController()
    pending.current = controller; setBusy(true); setError('')
    try {
      const attempt = await startAttempt(client, id, controller.signal)
      if (!controller.signal.aborted) navigate(`/tentativas/${attempt.id}`)
    } catch (cause) {
      if (failed(cause, controller.signal)) {
        const status = axios.isAxiosError(cause) ? cause.response?.status : undefined
        setError(status === 404 ? 'Desafio indisponível. Atualize as sugestões.'
          : status === 409 ? 'Não foi possível iniciar outra tentativa deste desafio.'
          : 'Não foi possível confirmar o início. Consulte suas tentativas antes de tentar novamente.')
      }
    } finally { if (!controller.signal.aborted) { pending.current = null; setBusy(false) } }
  }
  return <div><button className="dashboard-action" disabled={busy} onClick={start}>{busy ? 'Abrindo tentativa…' : 'Iniciar ou retomar tentativa'}</button>
    {error && <p className="error" role="alert">{error} <Link to="/tentativas">Consultar tentativas</Link></p>}</div>
}
