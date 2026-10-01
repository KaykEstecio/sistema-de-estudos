import { createContext, useContext, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { api } from './services/api'

export interface User { id: number; name: string; email: string; role: 'STUDENT' | 'ADMIN'; onboarding_completed: boolean }
interface Auth { user: User | null; client: AxiosInstance | null; expired: boolean; refreshUser: (signal: AbortSignal) => Promise<void>; login: (email: string, password: string, signal: AbortSignal) => Promise<void>; logout: () => void }
const Context = createContext<Auth | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [client, setClient] = useState<AxiosInstance | null>(null)
  const [expired, setExpired] = useState(false)
  const generation = useRef(0)
  const controller = useRef(new AbortController())
  const expiry = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  useEffect(() => () => { controller.current.abort(); clearTimeout(expiry.current) }, [])
  function clear(expiration = false) {
    generation.current += 1
    clearTimeout(expiry.current)
    controller.current.abort()
    controller.current = new AbortController()
    setUser(null); setClient(null); setExpired(expiration)
  }
  async function login(email: string, password: string, pageSignal: AbortSignal) {
    clear()
    const current = generation.current
    const signal = AbortSignal.any([controller.current.signal, pageSignal])
    const { data } = await api.post<{ access_token: string; expires_in: number }>('/auth/login', { email, password }, { signal })
    const authenticated = axios.create({ baseURL: '/api/v1', timeout: 10000,
      headers: { Authorization: `Bearer ${data.access_token}` }, signal: controller.current.signal })
    const identity = await authenticated.get<User>('/auth/me', { signal })
    if (current !== generation.current || signal.aborted) return
    authenticated.interceptors.response.use(response => {
      if (current !== generation.current) throw new axios.CanceledError()
      return response
    }, (error: unknown) => {
      if (current === generation.current && axios.isAxiosError(error) && error.response?.status === 401) clear(true)
      return Promise.reject(error)
    })
    setUser(identity.data); setClient(() => authenticated)
    expiry.current = setTimeout(() => { if (current === generation.current) clear(true) }, data.expires_in * 1000)
  }
  async function refreshUser(signal: AbortSignal) {
    if (!client) throw new axios.CanceledError()
    const current = generation.current
    const { data } = await client.get<User>('/auth/me', { signal })
    if (current !== generation.current || signal.aborted) throw new axios.CanceledError()
    setUser(data)
  }
  return <Context.Provider value={{ user, client, expired, login, refreshUser, logout: () => clear() }}>{children}</Context.Provider>
}

export function useAuth() {
  const auth = useContext(Context)
  if (!auth) throw new Error('AuthProvider ausente')
  return auth
}
