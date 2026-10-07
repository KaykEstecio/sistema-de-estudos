import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import { useAuth } from '../auth'
import type { ChallengeDetail } from '../services/recommendations'
import { StartAttempt } from './DashboardRecommendations'

interface ChallengePage { items: ChallengeDetail[]; total: number }

export default function StudyPractice({ contentId, skillId, skillName }: { contentId: number; skillId: number; skillName: string }) {
  const { client, user } = useAuth()
  const [primary, setPrimary] = useState<ChallengeDetail | null | undefined>(undefined)
  const [primaryError, setPrimaryError] = useState('')
  const [primaryReload, setPrimaryReload] = useState(0)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const pending = useRef<AbortController | null>(null)
  const [page, setPage] = useState<ChallengePage | null>(null)
  const [offset, setOffset] = useState(0)
  const [reload, setReload] = useState(0)
  const [error, setError] = useState('')
  useEffect(() => () => pending.current?.abort(), [])
  useEffect(() => {
    if (!client) return
    const controller = new AbortController()
    setPrimary(undefined); setPrimaryError('')
    client.get<ChallengeDetail | null>(`/study/${contentId}/practice`, { signal: controller.signal })
      .then(({ data }) => { if (!controller.signal.aborted) setPrimary(data) })
      .catch(cause => {
        if (!controller.signal.aborted && !axios.isCancel(cause) && !(axios.isAxiosError(cause) && cause.response?.status === 401)) setPrimaryError('Não foi possível consultar a prática da aula.')
      })
    return () => controller.abort()
  }, [client, contentId, primaryReload])
  async function choose(challengeId: number | null) {
    if (!client || pending.current) return
    const controller = new AbortController(); pending.current = controller; setSaving(true); setPrimaryError(''); setSaved(false)
    try {
      const { data } = await client.put<ChallengeDetail | null>(`/study/${contentId}/practice`, { challenge_id: challengeId }, { signal: controller.signal })
      if (!controller.signal.aborted) { setPrimary(data); setSaved(true) }
    } catch (cause) {
      if (!controller.signal.aborted && !axios.isCancel(cause) && !(axios.isAxiosError(cause) && cause.response?.status === 401)) {
        setPrimaryError('Não foi possível confirmar a indicação. Confira se o desafio está ativo e pertence à habilidade da aula. Consulte novamente antes de tentar outra escolha.')
      }
    } finally { if (!controller.signal.aborted) { pending.current = null; setSaving(false) } }
  }
  useEffect(() => {
    if (!client) return
    const controller = new AbortController()
    setPage(null); setError('')
    client.get<ChallengePage>('/challenges', {
      params: { skill: skillId, is_active: true, limit: 5, offset }, signal: controller.signal,
    }).then(({ data }) => { if (!controller.signal.aborted) setPage(data) })
      .catch((cause: unknown) => {
        if (!controller.signal.aborted && !axios.isCancel(cause) && !(axios.isAxiosError(cause) && cause.response?.status === 401)) {
          setError('Não foi possível carregar as práticas.')
        }
      })
    return () => controller.abort()
  }, [client, skillId, offset, reload])
  return <section className="dashboard-recommendations" aria-labelledby="study-practice-title">
    <h2 id="study-practice-title">Pratique {skillName}</h2>
    <p className="dashboard-note">Sua resposta será revisada por um ADMIN. Você pode iniciar a prática sem marcar a leitura como estudada.</p>
    {primaryError && <p className="error" role="alert">{primaryError} <button className="text-button" disabled={saving} onClick={() => setPrimaryReload(value => value + 1)}>Consultar prática da aula</button></p>}
    {primary === undefined && !primaryError && <p role="status">Consultando prática da aula…</p>}
    {primary === null && <p className="notice">Esta aula ainda não tem uma prática específica disponível. Você pode explorar os outros desafios, conferindo seus pré-requisitos.</p>}
    {primary && <section className="challenge-preview" aria-label="Prática desta aula">
      <p className="eyebrow">Próximo passo · prática desta aula</p><h3>{primary.title}</h3>
      <p className="dashboard-note">Escolhida pela equipe para este conteúdo · cerca de {primary.estimated_minutes} min</p>
      <p className="challenge-description">{primary.description}</p>
      {primary.starter_code && <pre><code>{primary.starter_code}</code></pre>}
      {client && <StartAttempt key={primary.id} client={client} id={primary.id} />}
    </section>}
    {user?.role === 'ADMIN' && <div><p className="dashboard-note">Escolha abaixo a prática principal desta aula. A indicação não altera avaliações nem progresso.</p>
      <button className="text-button" disabled={saving || primary === undefined} onClick={() => void choose(null)}>Remover indicação de prática</button>
      {saved && <p role="status">Indicação de prática atualizada.</p>}
    </div>}
    <details open={!primary}><summary>Explorar outros desafios de {skillName}</summary>
    <p className="dashboard-note">Catálogo da habilidade, em ordem de cadastro. Estes desafios podem exigir outros conhecimentos; confira os pré-requisitos.</p>
    {!page && !error && <p role="status">Carregando práticas…</p>}
    {error && <p className="error" role="alert">{error} <button className="text-button" onClick={() => setReload(value => value + 1)}>Recarregar práticas</button></p>}
    {page && <>
      {!page.items.length && <p className="notice">Nenhum desafio disponível nesta página.{offset > 0 && <button className="text-button" onClick={() => setOffset(0)}>Voltar ao início das práticas</button>}</p>}
      <ul className="recommendation-list">{page.items.map(item => <li key={item.id}>
        <h3>{item.title}</h3><p className="dashboard-note">Dificuldade {item.difficulty_score}/1.000 · cerca de {item.estimated_minutes} min</p>
        {user?.role === 'ADMIN' && <button className="dashboard-action" disabled={saving || primary?.id === item.id} onClick={() => void choose(item.id)}>Usar nesta aula: {item.title}</button>}
        <details><summary>Ver enunciado: {item.title}</summary>
          <p className="challenge-description">{item.description}</p>
          {item.starter_code && <pre><code>{item.starter_code}</code></pre>}
          {client && <StartAttempt client={client} id={item.id} />}
        </details>
      </li>)}</ul>
      {page.total > 5 && <nav className="progress-pagination" aria-label="Páginas das práticas">
        <button className="dashboard-action" disabled={offset === 0} onClick={() => setOffset(value => value - 5)}>Práticas anteriores</button>
        <p>Página {Math.floor(offset / 5) + 1}</p>
        <button className="dashboard-action" disabled={offset + 5 >= page.total} onClick={() => setOffset(value => value + 5)}>Próximas práticas</button>
      </nav>}
    </>}
    </details>
  </section>
}
