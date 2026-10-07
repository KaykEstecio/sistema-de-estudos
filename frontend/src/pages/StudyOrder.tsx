import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import axios from 'axios'
import { useAuth } from '../auth'
import type { StudyContent } from '../services/study'

export default function StudyOrder({ content }: { content: StudyContent }) {
  const { client } = useAuth()
  const [position, setPosition] = useState(content.study_order?.toString() ?? '')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const pending = useRef<AbortController | null>(null)
  useEffect(() => () => pending.current?.abort(), [])
  async function save(event: FormEvent) {
    event.preventDefault()
    if (!client || pending.current) return
    const controller = new AbortController(); pending.current = controller; setBusy(true); setMessage(''); setError('')
    try {
      await client.put(`/study/${content.id}/order`, { study_order: position === '' ? null : Number(position) }, { signal: controller.signal })
      if (!controller.signal.aborted) setMessage('Ordem de leitura salva. Consulte a sequência da habilidade para conferir.')
    } catch (cause) {
      if (!controller.signal.aborted && !axios.isCancel(cause) && !(axios.isAxiosError(cause) && cause.response?.status === 401)) setError('Não foi possível confirmar a ordem. Confira a posição e seu acesso. Repetir a mesma escolha não duplica o registro.')
    } finally { if (!controller.signal.aborted) { pending.current = null; setBusy(false) } }
  }
  return <section className="attempt-context" aria-label="Organização da leitura">
    <h2>Ordem de leitura</h2><p>Defina uma posição de 1 a 10.000 dentro desta habilidade. Deixe vazio para não incluir na sequência. Isso não bloqueia aulas nem altera score.</p>
    <form className="auth-form" onSubmit={save}>
      <label htmlFor="study-order">Posição editorial<input id="study-order" type="number" min={1} max={10000} step={1} value={position} disabled={busy} onChange={event => { setPosition(event.target.value); setMessage('') }} /></label>
      <button className="dashboard-action" disabled={busy}>{busy ? 'Salvando ordem…' : 'Salvar ordem de leitura'}</button>
    </form>
    {error && <p className="error" role="alert">{error}</p>}
    {message && <p role="status">{message}</p>}
  </section>
}
