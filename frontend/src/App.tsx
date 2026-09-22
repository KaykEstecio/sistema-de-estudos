import { useEffect, useState } from 'react'
import { checkHealth } from './services/health'

export default function App() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    checkHealth(controller.signal).then(
      () => { if (!controller.signal.aborted) setStatus('success') },
      () => { if (!controller.signal.aborted) setStatus('error') },
    )
    return () => controller.abort()
  }, [attempt])

  function retry() {
    setStatus('loading')
    setAttempt((previous) => previous + 1)
  }

  return (
    <main>
      <h1>CodeTrack</h1>
      <p>Aprendizagem e prática de programação.</p>
      <p className="note">Estamos preparando a plataforma.</p>
      <section aria-labelledby="connection-title">
        <h2 id="connection-title">Conexão com o servidor</h2>
        <p role="status">
          {status === 'loading' && 'Verificando conexão…'}
          {status === 'success' && 'Servidor disponível.'}
          {status === 'error' && 'Não foi possível conectar ao servidor. Tente novamente.'}
        </p>
        <button type="button" onClick={retry} disabled={status === 'loading'}>
          Verificar novamente
        </button>
      </section>
    </main>
  )
}
