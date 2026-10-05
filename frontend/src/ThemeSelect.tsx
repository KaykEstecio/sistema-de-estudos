import { useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'
const readTheme = (value: string | null | undefined): Theme => value === 'light' || value === 'dark' ? value : 'system'

export default function ThemeSelect() {
  const [preference, setPreference] = useState<Theme>(() => readTheme(document.documentElement.dataset.themePreference))

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    function apply() {
      document.documentElement.dataset.theme = preference === 'system' ? media.matches ? 'dark' : 'light' : preference
      document.documentElement.style.colorScheme = document.documentElement.dataset.theme
      document.documentElement.dataset.themePreference = preference
    }
    function sync(event: StorageEvent) {
      if (event.key === 'codetrack.theme' || event.key === null) setPreference(readTheme(event.newValue))
    }
    apply()
    media.addEventListener('change', apply)
    window.addEventListener('storage', sync)
    return () => {
      media.removeEventListener('change', apply)
      window.removeEventListener('storage', sync)
    }
  }, [preference])

  function change(value: string) {
    const next = readTheme(value)
    setPreference(next)
    try { localStorage.setItem('codetrack.theme', next) } catch { /* Mantém a escolha durante esta sessão. */ }
  }

  return <label className="theme-select"><span>Tema</span>
    <select aria-label="Tema da interface" value={preference} onChange={event => change(event.target.value)}>
      <option value="system">Automático</option><option value="light">Claro</option><option value="dark">Escuro</option>
    </select>
  </label>
}
