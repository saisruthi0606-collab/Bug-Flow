import { Moon, Sun, Bell, UserCircle, Settings2, LogOut } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { toggleTheme, useTheme } from '../lib/theme'
import { clearAuthToken } from '../lib/api'

export default function Topbar() {
  const navigate = useNavigate()
  const { theme, setTheme } = useTheme()

  const handleLogout = () => {
    clearAuthToken()
    navigate('/login')
  }

  return (
    <div className="flex items-center justify-between gap-4 rounded-3xl border border-border bg-card px-4 py-3 shadow-glow backdrop-blur">
      <div className="flex items-center gap-3">
        <div className="rounded-2xl bg-accent/15 p-2 text-accent"><Bell size={18} /></div>
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">Welcome back</p>
          <p className="font-semibold text-foreground">Your AI bug command center</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <button onClick={() => setTheme(toggleTheme(theme))} className="rounded-2xl border border-border bg-background p-2 text-accent transition hover:bg-border/10">
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <Link to="/profile" className="rounded-2xl border border-border bg-background p-2 text-foreground hover:bg-border/10"><UserCircle size={18} /></Link>
        <Link to="/settings" className="rounded-2xl border border-border bg-background p-2 text-foreground hover:bg-border/10"><Settings2 size={18} /></Link>
        <button onClick={handleLogout} className="rounded-2xl border border-border bg-background p-2 text-foreground hover:bg-border/10"><LogOut size={18} /></button>
      </div>
    </div>
  )
}
