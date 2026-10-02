import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'

const ExitGuard = createContext({ guarded: false, setGuarded: (_value: boolean) => {} })

export function ExitGuardProvider({ children }: { children: ReactNode }) {
  const [guarded, setGuarded] = useState(false)
  return <ExitGuard.Provider value={{ guarded, setGuarded }}>{children}</ExitGuard.Provider>
}

export function useLogoutGuard() {
  return useContext(ExitGuard).guarded
}

export function useRegisterExitGuard(guarded: boolean) {
  const { setGuarded } = useContext(ExitGuard)
  useEffect(() => {
    setGuarded(guarded)
    return () => setGuarded(false)
  }, [guarded, setGuarded])
}
