import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, FolderKanban, Bug, BarChart3, UserCircle, Settings2, CalendarRange } from 'lucide-react'

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Issues', href: '/issues', icon: Bug },
  { name: 'Sprints', href: '/sprints', icon: CalendarRange },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Profile', href: '/profile', icon: UserCircle },
  { name: 'Settings', href: '/settings', icon: Settings2 },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="hidden w-72 flex-col gap-4 border-r border-border bg-card p-6 lg:flex">
      <div className="mb-10 flex items-center gap-3">
        <div className="rounded-2xl bg-accent/15 p-3 text-accent"><LayoutDashboard size={24} /></div>
        <div>
          <p className="text-xl font-semibold text-foreground">BugFlow</p>
          <p className="text-sm text-muted-foreground">detect.debug.deliver</p>
        </div>
      </div>
      <nav className="flex flex-1 flex-col gap-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const active = location.pathname === item.href
          return (
            <Link key={item.href} to={item.href} className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${active ? 'bg-accent/20 text-accent' : 'text-muted-foreground hover:bg-background'}`}>
              <Icon size={18} />
              {item.name}
            </Link>
          )
        })}
      </nav>
      <div className="mt-6 rounded-3xl border border-border bg-background/70 p-4 text-sm text-muted-foreground">
        <p className="font-semibold text-foreground">Pro AI assistant</p>
        <p className="mt-2 text-xs leading-5">Improve issue descriptions, detect root causes, and prioritize bugs automatically.</p>
      </div>
    </aside>
  )
}

