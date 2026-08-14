import { useQuery } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'

type Data = {
  total_issues: number
  open_issues: number
  resolved_issues: number
  critical_issues: number
  total_projects: number
  issue_status: any[]
  workflow_distribution: any[]
  priority_distribution: any[]
  severity_distribution: any[]
  duplicate_detection: { flagged_issues: number; total_issues: number }
  sprint_summary: any[]
  ai_health_score?: number
  ai_report?: { summary: string; risk_level: string; insights: string[]; recommendations: string[] }
}

export default function AnalyticsPage() {
  const { data } = useQuery<Data>({ queryKey: ['analytics'], queryFn: async () => (await api.get('/api/dashboard')).data })
  const severity = data?.severity_distribution || []
  const priority = data?.priority_distribution || []
  const resolution = data?.total_issues ? Math.round((data.resolved_issues / data.total_issues) * 100) : 0
  const duplicate = data?.total_issues ? Math.round((data.duplicate_detection.flagged_issues / data.total_issues) * 100) : 0
  const aiReport = data?.ai_report || { summary: 'No report available.', risk_level: 'Low', insights: [], recommendations: [] }
  const aiHealthScore = data?.ai_health_score ?? 0

  return (
    <Layout title="Analytics">
      <div className="grid gap-4 sm:grid-cols-4">
        {[['Open Issues', data?.open_issues], ['Resolved Issues', data?.resolved_issues], ['Critical Bugs', data?.critical_issues], ['Projects', data?.total_projects]].map(([label, value]) => (
          <div key={String(label)} className="rounded-3xl border border-border bg-card p-5 shadow-glow">
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className="mt-2 text-3xl font-semibold">{value ?? 0}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        {[['Issue Status', data?.issue_status], ['Workflow Distribution', data?.workflow_distribution], ['Priority Distribution', priority], ['Severity Distribution', severity]].map(([title, rows]) => (
          <section key={String(title)} className="rounded-3xl border border-border bg-card p-6 shadow-glow">
            <h2 className="font-semibold">{title}</h2>
            <div className="mt-4 space-y-3">
              {(rows as any[] || []).map((row) => {
                const label = row.status || row.priority || row.severity
                return (
                  <div key={label}>
                    <div className="flex justify-between text-sm"><span>{label}</span><span>{row.count}</span></div>
                    <div className="mt-1 h-2 rounded bg-border"><div className="h-2 rounded bg-primary" style={{ width: `${data?.total_issues ? (row.count / data.total_issues) * 100 : 0}%` }} /></div>
                  </div>
                )
              })}
            </div>
          </section>
        ))}
      </div>

      <section className="mt-6 rounded-3xl border border-border bg-card p-6 shadow-glow">
        <h2 className="font-semibold">AI Analysis Report</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-border bg-background p-4">
            <p className="text-sm text-muted-foreground">Health Score</p>
            <p className="mt-2 text-3xl font-semibold">{aiHealthScore}</p>
          </div>
          <div className="rounded-xl border border-border bg-background p-4">
            <p className="text-sm text-muted-foreground">Resolution Rate</p>
            <p className="mt-2 text-3xl font-semibold">{resolution}%</p>
          </div>
          <div className="rounded-xl border border-border bg-background p-4">
            <p className="text-sm text-muted-foreground">Duplicate Signal</p>
            <p className="mt-2 text-3xl font-semibold">{duplicate}%</p>
          </div>
        </div>
        <div className="mt-5 rounded-xl border border-border bg-background p-4">
          <div className="mb-2 text-sm font-medium text-primary">Status: {aiReport.risk_level}</div>
          <p className="text-sm text-muted-foreground">{aiReport.summary}</p>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <div>
            <h3 className="font-medium">Insights</h3>
            <ul className="mt-2 space-y-2 text-sm text-muted-foreground">
              {(aiReport.insights || []).map((item) => <li key={item}>• {item}</li>)}
            </ul>
          </div>
          <div>
            <h3 className="font-medium">Recommendations</h3>
            <ul className="mt-2 space-y-2 text-sm text-muted-foreground">
              {(aiReport.recommendations || []).map((item) => <li key={item}>• {item}</li>)}
            </ul>
          </div>
        </div>
      </section>
    </Layout>
  )
}
