import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

const THEME_KEY = 'bugflow-theme'

type Theme = 'dark' | 'light'

export type { Theme }

export function getStoredTheme(): Theme | null {
  try {
    return (localStorage.getItem(THEME_KEY) as Theme | null)
  } catch {
    return null
  }
}

export function setStoredTheme(value: Theme) {
  try {
    localStorage.setItem(THEME_KEY, value)
  } catch {
    // ignore
  }
}

export function getPreferredTheme(): Theme {
  if (typeof window === 'undefined') return 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function applyTheme(theme: Theme) {
  const root = document.documentElement
  root.classList.remove('light', 'dark')
  root.classList.add(theme)
}

export function initializeTheme() {
  const stored = getStoredTheme()
  const theme = stored || getPreferredTheme()
  applyTheme(theme)
  return theme
}

export const ThemeContext = createContext<{
  theme: Theme
  setTheme: (theme: Theme) => void
}>({
  theme: 'dark',
  setTheme: () => undefined,
})

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => initializeTheme())

  const setTheme = (next: Theme) => {
    applyTheme(next)
    setStoredTheme(next)
    setThemeState(next)
  }

  useEffect(() => {
    const stored = getStoredTheme()
    if (stored && stored !== theme) {
      setTheme(stored)
    }
  }, [])

  const value = useMemo(() => ({ theme, setTheme }), [theme])

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  return useContext(ThemeContext)
}

export function toggleTheme(current: Theme): Theme {
  return current === 'dark' ? 'light' : 'dark'
}
