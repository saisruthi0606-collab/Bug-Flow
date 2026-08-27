import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../lib/api'

type Risk = { issue_id: number; title: string; severity: string; priority: string; status: string; risk_score: number; risk_level: string; reasons: string[] }
type Radar = { issues: Risk[]; summary: Record<string, number>; methodology: string }

export default function RiskRadarPage() {
  const { data, isLoading } = useQuery<Radar>({ queryKey: ['risk-radar'], queryFn: async () => (await api.get('/api/risk')).data })
  return <Layout title="Defect Risk Radar">
    <p className="text-sm text-muted-foreground">{data?.methodology || 'Transparent issue-level risk signals.'}</p>
    <div className="mt-5 grid gap-3 sm:grid-cols-4">{['Critical', 'High', 'Medium', 'Low'].map(level => <div key={level} className="rounded-2xl border border-border bg-card p-4"><p className="text-sm text-muted-foreground">{level} risk</p><p className="mt-1 text-2xl font-semibold">{data?.summary[level] ?? 0}</p></div>)}</div>
    <section className="mt-6 rounded-3xl border border-border bg-card p-5 shadow-glow"><h2 className="font-semibold">Ranked issues</h2>{isLoading ? <p className="mt-4 text-sm text-muted-foreground">Loading risk signals…</p> : <div className="mt-4 space-y-3">{data?.issues.map(issue => <Link key={issue.issue_id} to={`/issues/${issue.issue_id}`} className="block rounded-xl border border-border bg-background p-4 hover:border-primary"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="font-medium">BUG-{issue.issue_id} — {issue.title}</p><p className="mt-1 text-xs text-muted-foreground">{issue.severity} · {issue.priority} · {issue.status}</p></div><div className="text-right"><p className="text-xl font-semibold text-primary">{issue.risk_score}/100</p><p className="text-xs text-muted-foreground">{issue.risk_level}</p></div></div><p className="mt-3 text-sm text-muted-foreground">{issue.reasons.join(' · ')}</p></Link>)}</div>}</section>
  </Layout>
}
