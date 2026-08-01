import { type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import { clearAuthToken } from '../lib/api'

export default function Layout({ children, title }: { children: ReactNode; title: string }) {
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAuthToken()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1">
          <div className="border-b border-border bg-card/80 px-6 py-4 backdrop-blur">
            <Topbar />
          </div>
          <div className="p-6">
            <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-accent/80">BugFlow</p>
                <h1 className="text-3xl font-semibold text-foreground">{title}</h1>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <button onClick={handleLogout} className="rounded-2xl bg-background px-4 py-2 text-sm font-semibold text-foreground transition hover:bg-border">Logout</button>
                <button onClick={() => navigate('/issues/new')} className="rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-foreground transition hover:bg-accent">New Issue</button>
              </div>
            </div>
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
