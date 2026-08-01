import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'
import { BarChart3, PieChart, Activity, TrendingUp } from 'lucide-react'

type AnalyticsData = {
  total_projects: number
  total_issues: number
  open_issues: number
  resolved_issues: number
  critical_issues: number
  issue_status: Array<{ status: string; count: number }>
  priority_distribution: Array<{ priority: string; count: number }>
  bug_trends: Array<{ date: string; count: number }>
}

export default function AnalyticsPage() {
  const { data, isLoading } = useQuery<AnalyticsData>({
    queryKey: ['analytics'],
    queryFn: async () => {
      const response = await api.get<AnalyticsData>('/api/dashboard')
      return response.data
    },
  })

  const statusMap = useMemo(
    () => new Map(data?.issue_status.map((item) => [item.status, item.count]) ?? []),
    [data],
  )

  const priorityMap = useMemo(
    () => new Map(data?.priority_distribution.map((item) => [item.priority, item.count]) ?? []),
    [data],
  )

  if (isLoading) {
    return (
      <Layout title="Analytics">
        <div className="rounded-3xl border border-border bg-card p-6 text-center text-muted-foreground">Loading analytics…</div>
      </Layout>
    )
  }

  return (
    <Layout title="Analytics">
      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              { label: 'Open Issues', value: statusMap.get('Open') ?? 0, icon: Activity },
              { label: 'Resolved', value: statusMap.get('Resolved') ?? 0, icon: BarChart3 },
              { label: 'Critical', value: priorityMap.get('High') ?? 0, icon: PieChart },
              { label: 'Projects', value: data?.total_projects ?? 0, icon: TrendingUp },
            ].map((stat) => {
              const Icon = stat.icon
              return (
                <div key={stat.label} className="rounded-3xl border border-border bg-card p-6 shadow-glow">
                  <div className="flex items-center gap-3 text-primary">
                    <Icon size={22} />
                    <p className="text-sm uppercase tracking-[0.3em] text-muted-foreground">{stat.label}</p>
                  </div>
                  <p className="mt-4 text-4xl font-semibold text-foreground">{stat.value}</p>
                </div>
              )
            })}
          </div>

          <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
            <h2 className="text-xl font-semibold text-foreground">Bug Trends</h2>
            <p className="mt-2 text-sm text-muted-foreground">Track issue volume, priority mix, and resolution cadence over time.</p>
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              {data?.bug_trends.map((trend) => (
                <div key={trend.date} className="rounded-3xl border border-border bg-background p-4">
                  <p className="text-sm text-muted-foreground">{trend.date}</p>
                  <p className="mt-2 text-3xl font-semibold text-foreground">{trend.count}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
            <h2 className="text-xl font-semibold text-foreground">Issue Status</h2>
            <div className="mt-4 space-y-3">
              {['Open', 'In Progress', 'Resolved', 'Blocked'].map((status) => (
                <div key={status} className="flex items-center justify-between rounded-3xl border border-border bg-background px-4 py-3">
                  <span className="text-foreground">{status}</span>
                  <span className="text-primary">{statusMap.get(status) ?? 0}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-border bg-card p-6 shadow-glow">
            <h2 className="text-xl font-semibold text-foreground">Priority Distribution</h2>
            <div className="mt-4 grid gap-3">
              {['High', 'Medium', 'Low'].map((level) => (
                <div key={level} className="rounded-3xl border border-border bg-background px-4 py-3 flex items-center justify-between">
                  <span className="text-foreground">{level}</span>
                  <span className="text-primary">{priorityMap.get(level) ?? 0}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
