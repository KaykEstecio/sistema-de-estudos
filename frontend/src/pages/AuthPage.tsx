import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import { useAuth } from '../auth'
import { api, errorMessage } from '../services/api'

export default function AuthPage({ register = false }: { register?: boolean }) {
  const auth = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [show, setShow] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const pending = useRef(false)
  const active = useRef(true)
  const abort = useRef<AbortController | null>(null)
  useEffect(() => { active.current = true; return () => { active.current = false; abort.current?.abort() } }, [])
  const from = location.state?.from
  const destination = !auth.user?.onboarding_completed ? '/onboarding'
    : typeof from === 'string' && /^\/(dashboard|onboarding|(?:diagnostico|tentativas)(?:\/[1-9]\d*)?)$/.test(from)
      ? from : '/dashboard'
  if (auth.user) return <Navigate to={destination} replace />
  async function submit(event: FormEvent) {
    event.preventDefault()
    if (pending.current) return
    pending.current = true; setBusy(true); setError('')
    abort.current = new AbortController()
    try {
      if (register) {
        await api.post('/auth/register', { name, email, password }, { signal: abort.current.signal })
        if (active.current) navigate('/entrar', { replace: true, state: { registered: true } })
      } else await auth.login(email, password, abort.current.signal)
    } catch (err) { if (active.current) setError(errorMessage(err)) }
    finally { pending.current = false; if (active.current) setBusy(false) }
  }
  return <main className="auth-main">
    <h1>{register ? 'Crie sua conta' : 'Entre no CodeTrack'}</h1>
    <p className="subtitle">{register ? 'Comece seu aprendizado em programação.' : 'Continue seu aprendizado em programação.'}</p>
    <form onSubmit={submit} className="auth-form">
      {!register && location.state?.registered && <p className="notice" role="status">Conta criada. Entre com seu e-mail e senha.</p>}
      {!register && auth.expired && <p className="notice" role="status">Sua sessão expirou. Entre novamente.</p>}
      {error && <p className="error" role="alert">{error}</p>}
      <fieldset disabled={busy} className="grid gap-6">
        <legend className="sr-only">{register ? 'Dados para cadastro' : 'Dados para entrar'}</legend>
        {register && <label>Nome<input autoComplete="name" required maxLength={120} value={name} onChange={e => setName(e.target.value)} /></label>}
        <label>E-mail<input type="email" autoComplete="email" required maxLength={320} placeholder="seu@email.com" value={email} onChange={e => setEmail(e.target.value)} /></label>
        <label>Senha<span className="password-field"><input type={show ? 'text' : 'password'} autoComplete={register ? 'new-password' : 'current-password'} required minLength={register ? 15 : 1} maxLength={128} placeholder={register ? 'Pelo menos 15 caracteres' : 'Digite sua senha'} value={password} onChange={e => setPassword(e.target.value)} aria-describedby={register ? 'password-help' : undefined} /><button type="button" className="reveal" aria-pressed={show} onClick={() => setShow(!show)}>{show ? 'Ocultar' : 'Mostrar'}</button></span></label>
        {register && <p id="password-help" className="help">Use de 15 a 128 caracteres. Espaços são permitidos.</p>}
        <button className="primary" type="submit">{busy ? 'Aguarde…' : register ? 'Criar conta' : 'Entrar'}</button>
      </fieldset>
    </form>
    <p className="alternate">{register ? 'Já tem conta? ' : 'Ainda não tem conta? '}<Link to={register ? '/entrar' : '/cadastro'}>{register ? 'Entrar' : 'Criar conta'}</Link></p>
  </main>
}
