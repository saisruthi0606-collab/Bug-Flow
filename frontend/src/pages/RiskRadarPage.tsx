import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../lib/api'

type Risk = { issue_id: number; title: string; severity: string; priority: string; status: string; updated_at?: string; risk_score: number; risk_level: string; reasons: string[] }
type Radar = { role?: string; role_label?: string; issues: Risk[]; role_issues?: Risk[]; summary: Record<string, number>; methodology: string }

export default function RiskRadarPage() {
  const { data, isLoading } = useQuery<Radar>({ queryKey: ['risk-radar'], queryFn: async () => (await api.get('/api/risk')).data })
  const roleIssues = data?.role_issues ?? data?.issues ?? []
  const isReporter = data?.role === 'Reporter'
  const nextStep = (status: string) => status === 'Resolved' ? 'Verification' : status === 'Verified' ? 'Closure' : status === 'Open' || status === 'Assigned' ? 'Investigation / resolution' : status
  return <Layout title="Defect Risk Radar">
    <p className="text-sm text-muted-foreground">{data?.role_label || 'Role-aware risk overview'} · {data?.methodology || 'Transparent issue-level risk signals.'}</p>
    <div className="mt-5 grid gap-3 sm:grid-cols-4">{['Critical', 'High', 'Medium', 'Low'].map(level => <div key={level} className="rounded-2xl border border-border bg-card p-4"><p className="text-sm text-muted-foreground">{level} risk</p><p className="mt-1 text-2xl font-semibold">{data?.summary[level] ?? 0}</p></div>)}</div>
    <section className="mt-6 rounded-3xl border border-border bg-card p-5 shadow-glow"><h2 className="font-semibold">{isReporter ? 'My Issue Risk' : data?.role_label || 'Role-specific risk'}</h2>{isLoading ? <p className="mt-4 text-sm text-muted-foreground">Loading risk signals…</p> : roleIssues.length === 0 ? <p className="mt-4 text-sm text-muted-foreground">{isReporter ? 'No issues have been reported by you yet.' : 'No matching issues found.'}</p> : <div className="mt-4 space-y-3">{roleIssues.map(issue => <Link key={issue.issue_id} to={`/issues/${issue.issue_id}`} className="block rounded-xl border border-border bg-background p-4 hover:border-primary"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="font-medium">BUG-{issue.issue_id} — {issue.title}</p><p className="mt-1 text-xs text-muted-foreground">{issue.severity} · {issue.priority} · {issue.status}</p></div><div className="text-right"><p className="text-xl font-semibold text-primary">{issue.risk_score}/100</p><p className="text-xs text-muted-foreground">{issue.risk_level}</p></div></div><div className="mt-3 grid gap-1 text-xs text-muted-foreground sm:grid-cols-2"><span>Why: {issue.reasons.join(' · ')}</span><span>Next step: {nextStep(issue.status)}</span><span>Progress: {issue.status}</span>{issue.updated_at && <span>Updated: {new Date(issue.updated_at).toLocaleString()}</span>}</div></Link>)}</div>}</section>
    {!isReporter && <section className="mt-6 rounded-3xl border border-border bg-card p-5"><h2 className="font-semibold">Ranked issues</h2><div className="mt-4 space-y-2">{(data?.issues ?? []).slice(0, 5).map(issue => <Link key={issue.issue_id} to={`/issues/${issue.issue_id}`} className="block text-sm text-primary hover:underline">BUG-{issue.issue_id} — {issue.title} ({issue.risk_level})</Link>)}</div></section>}
  </Layout>
}
