import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'

export default function IssuesPage() {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [priority, setPriority] = useState('')

  const query = useQuery<any[]>({
    queryKey: ['issues', search, status, priority],
    queryFn: async () => {
      const response = await api.get('/api/issues', { params: { search, status, priority } })
      return response.data
    },
  })

  const issues = query.data ?? []
  const isLoading = query.isLoading
  const refetch = query.refetch

  return (
    <Layout title="Issues">
      <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-foreground">Issue Board</h3>
            <p className="mt-1 text-sm text-muted-foreground">Search, filter, and review current issues.</p>
          </div>
          <div className="flex flex-col gap-3 md:flex-row">
            <input className="rounded-3xl border border-border bg-background px-4 py-2 text-foreground outline-none focus:border-primary" placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} />
            <select className="rounded-3xl border border-border bg-background px-4 py-2 text-foreground outline-none focus:border-primary" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">All Status</option>
              <option value="Open">Open</option>
              <option value="In Progress">In Progress</option>
              <option value="Resolved">Resolved</option>
            </select>
            <select className="rounded-3xl border border-border bg-background px-4 py-2 text-foreground outline-none focus:border-primary" value={priority} onChange={(e) => setPriority(e.target.value)}>
              <option value="">All Priority</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
            <button onClick={() => refetch()} className="rounded-3xl bg-primary px-4 py-2 font-semibold text-foreground transition hover:bg-accent">Apply</button>
          </div>
        </div>
        <div className="mt-6 space-y-3">
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading issues…</p>
          ) : issues.length === 0 ? (
            <p className="text-sm text-muted-foreground">No issues found.</p>
          ) : (
            issues.map((issue) => (
              <Link key={issue.id} to={`/issues/${issue.id}`} className="flex flex-col rounded-3xl border border-border bg-background p-4 text-foreground transition hover:bg-card md:flex-row md:items-center md:justify-between">
                <div>
                  <h4 className="font-semibold">{issue.title}</h4>
                  <p className="mt-1 text-sm text-muted-foreground">{issue.description || 'No description'}</p>
                </div>
                <div className="mt-3 flex flex-wrap gap-2 md:mt-0">
                  <span className="rounded-full bg-primary/10 px-3 py-1 text-sm text-primary">{issue.status}</span>
                  <span className="rounded-full bg-accent/10 px-3 py-1 text-sm text-accent">{issue.priority}</span>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </Layout>
  )
}
