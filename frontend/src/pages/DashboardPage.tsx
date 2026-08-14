import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'
import { Bug, FolderKanban, UserCircle, BarChart3, PieChart } from 'lucide-react'

type DashboardData = {
  total_projects: number
  total_issues: number
  open_issues: number
  resolved_issues: number
  critical_issues: number
  issue_status: Array<{ status: string; count: number }>
  priority_distribution: Array<{ priority: string; count: number }>
  severity_distribution: Array<{ severity: string; count: number }>
  sprint_summary: Array<{ id: number; name: string; issue_count: number; progress: number }>
  recent_activity: Array<{ id:number; issue_id:number; action:string; details?:string; created_at:string }>
  duplicate_detection: { flagged_issues:number; total_issues:number }
  bug_trends: Array<{ date: string; count: number }>
  ai_health_score?: number
  ai_report?: { summary: string; risk_level: string; insights: string[]; recommendations: string[] }
  similar_issues?: Array<{ issue_id:number; title:string; similar_issue_id:number; similar_issue_title:string; similarity:number }>
}

export default function DashboardPage({ user }: { user: any }) {
  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await api.get<DashboardData>('/api/dashboard')
      return response.data
    },
  })

  const highPriority = data?.priority_distribution.find((item) => item.priority === 'High')?.count ?? 0
  const mediumPriority = data?.priority_distribution.find((item) => item.priority === 'Medium')?.count ?? 0
  const lowPriority = data?.priority_distribution.find((item) => item.priority === 'Low')?.count ?? 0

  const trendRows = useMemo(() => data?.bug_trends ?? [], [data])
  const aiHealthScore = data?.ai_health_score ?? 0
  const aiReport = data?.ai_report ?? { summary: 'No AI report available.', risk_level: 'Low', insights: [], recommendations: [] }
  const similarIssues = data?.similar_issues ?? []

  if (isLoading) {
    return (
      <Layout title="Dashboard">
        <div className="rounded-3xl border border-border bg-card p-6 text-center text-muted-foreground">Loading dashboard metrics…</div>
      </Layout>
    )
  }

  return (
    <Layout title="Dashboard">
      <div className="grid gap-6 xl:grid-cols-4">
        <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <div className="flex items-center gap-3 text-accent">
            <UserCircle size={24} />
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">Welcome</p>
              <h3 className="text-xl font-semibold text-foreground">{user?.full_name || 'User'}</h3>
            </div>
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            You are logged in as <span className="font-medium text-foreground">{user?.role || 'Reporter'}</span>.
          </p>
        </div>

        <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <div className="flex items-center gap-3 text-primary">
            <FolderKanban size={24} />
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">Projects</p>
              <h3 className="text-3xl font-semibold text-foreground">{data?.total_projects}</h3>
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <div className="flex items-center gap-3 text-primary">
            <Bug size={24} />
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">Issues</p>
              <h3 className="text-3xl font-semibold text-foreground">{data?.total_issues}</h3>
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <div className="flex items-center gap-3 text-primary">
            <BarChart3 size={24} />
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">Critical</p>
              <h3 className="text-3xl font-semibold text-foreground">{data?.critical_issues}</h3>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <section className="rounded-3xl border border-border bg-card p-6 shadow-glow"><h2 className="font-semibold text-foreground">Bugs by Severity</h2><div className="mt-4 space-y-2">{data?.severity_distribution.map(item => <div key={item.severity} className="flex justify-between text-sm"><span>{item.severity}</span><span>{item.count}</span></div>)}</div></section>
        <section className="rounded-3xl border border-border bg-card p-6 shadow-glow"><h2 className="font-semibold text-foreground">Sprint Progress</h2><div className="mt-4 space-y-3">{data?.sprint_summary.map(s => <div key={s.id}><div className="flex justify-between text-sm"><span>{s.name}</span><span>{s.progress}%</span></div><div className="mt-1 h-2 bg-border"><div className="h-2 bg-primary" style={{width:`${s.progress}%`}} /></div></div>)}</div></section>
        <section className="rounded-3xl border border-border bg-card p-6 shadow-glow"><h2 className="font-semibold text-foreground">Recent Activity</h2><div className="mt-4 space-y-2">{data?.recent_activity.slice(0,4).map(a => <p key={a.id} className="text-sm"><span className="font-medium">{a.action}</span><span className="text-muted-foreground"> {a.details}</span></p>)}</div><p className="mt-4 text-sm text-muted-foreground">Duplicates flagged: {data?.duplicate_detection.flagged_issues ?? 0}</p></section>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">Overview</p>
              <h2 className="text-2xl font-semibold text-foreground">Issue status</h2>
            </div>
            <div className="rounded-full bg-primary/10 px-3 py-1 text-sm text-primary">Live</div>
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            {data?.issue_status.map((item) => (
              <div key={item.status} className="rounded-3xl border border-border bg-background p-5 text-center">
                <p className="text-sm text-muted-foreground">{item.status}</p>
                <p className="mt-3 text-3xl font-semibold text-foreground">{item.count}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <div className="mb-4 flex items-center gap-3 text-primary">
            <PieChart size={24} />
            <h2 className="text-2xl font-semibold text-foreground">Priority distribution</h2>
          </div>
          <div className="space-y-3">
            <div className="rounded-3xl bg-background p-4">
              <p className="text-sm text-muted-foreground">High</p>
              <p className="mt-2 text-2xl font-semibold text-foreground">{highPriority}</p>
            </div>
            <div className="rounded-3xl bg-background p-4">
              <p className="text-sm text-muted-foreground">Medium</p>
              <p className="mt-2 text-2xl font-semibold text-foreground">{mediumPriority}</p>
            </div>
            <div className="rounded-3xl bg-background p-4">
              <p className="text-sm text-muted-foreground">Low</p>
              <p className="mt-2 text-2xl font-semibold text-foreground">{lowPriority}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">AI Health</p>
          <div className="mt-4 flex items-center justify-between gap-4">
            <div>
              <div className="text-4xl font-semibold text-foreground">{aiHealthScore}</div>
              <div className="text-sm text-muted-foreground">Health score</div>
            </div>
            <div className="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">{aiReport.risk_level}</div>
          </div>
          <p className="mt-4 text-sm text-muted-foreground">{aiReport.summary}</p>
          <ul className="mt-4 space-y-2 text-sm">
            {aiReport.insights.map((insight) => (
              <li key={insight} className="rounded-xl border border-border bg-background p-3">{insight}</li>
            ))}
          </ul>
        </section>

        <section className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">AI Guidance</p>
          <ul className="mt-4 space-y-3 text-sm">
            {aiReport.recommendations.map((recommendation) => (
              <li key={recommendation} className="rounded-xl border border-border bg-background p-3">{recommendation}</li>
            ))}
          </ul>
        </section>
      </div>

      <div className="mt-8 rounded-3xl border border-border bg-card p-6 shadow-glow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">7-day trend</p>
            <h2 className="text-2xl font-semibold text-foreground">Recent bug volume</h2>
          </div>
          <Link to="/issues" className="rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-foreground transition hover:bg-accent">See issues</Link>
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-7">
          {trendRows.map((item) => (
            <div key={item.date} className="rounded-3xl border border-border bg-background p-4 text-center">
              <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">{item.date.slice(5)}</p>
              <p className="mt-3 text-2xl font-semibold text-foreground">{item.count}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8 rounded-3xl border border-border bg-card p-6 shadow-glow">
        <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">Similar issues</p>
        <h2 className="text-2xl font-semibold text-foreground">Top 5 near-duplicates</h2>
        <div className="mt-4 space-y-3">
          {similarIssues.length === 0 ? (
            <p className="text-sm text-muted-foreground">No near-duplicate issues detected.</p>
          ) : (
            similarIssues.map((entry) => (
              <div key={`${entry.issue_id}-${entry.similar_issue_id}`} className="rounded-xl border border-border bg-background p-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-medium">{entry.title}</div>
                    <div className="text-muted-foreground">Matches {entry.similar_issue_title}</div>
                  </div>
                  <div className="rounded-full bg-primary/10 px-2 py-1 text-xs text-primary">{entry.similarity}%</div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </Layout>
  )
}


