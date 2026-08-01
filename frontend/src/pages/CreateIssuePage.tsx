import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'

type AiResponse = {
  enhanced_description: string
  severity: string
  priority: string
  category: string
  component: string
  root_cause: string
  resolution: string
  test_cases: string
  estimated_time: string
  confidence: string
}

type Project = {
  id: number
  project_name: string
}

export default function CreateIssuePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form, setForm] = useState({ title: '', description: '', status: 'Open', priority: 'Medium', severity: 'Low', project_id: 0 })
  const [aiResult, setAiResult] = useState<AiResponse | null>(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiError, setAiError] = useState('')

  const { data: projects = [], isLoading: projectsLoading } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await api.get<Project[]>('/api/projects')
      return response.data
    },
  })

  useEffect(() => {
    if (!form.project_id && projects.length > 0) {
      setForm((current) => ({ ...current, project_id: projects[0].id }))
    }
  }, [projects, form.project_id])

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault()
    await api.post('/api/issues', form)
    await queryClient.invalidateQueries({ queryKey: ['issues'] })
    await queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    await queryClient.invalidateQueries({ queryKey: ['analytics'] })
    navigate('/issues')
  }

  const handleEnhance = async () => {
    if (!form.description.trim()) {
      setAiError('Add a description to improve first.')
      return
    }

    setAiError('')
    setAiLoading(true)

    try {
      const response = await api.post<AiResponse>('/api/ai/enhance', { description: form.description })
      setAiResult(response.data)
      setForm((current) => ({
        ...current,
        description: response.data.enhanced_description,
        priority: response.data.priority,
        severity: response.data.severity,
      }))
    } catch {
      setAiError('Unable to enhance the issue description right now. Try again later.')
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <Layout title="Create Issue">
      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <section className="rounded-3xl border border-border bg-card p-6 shadow-glow">
          <div className="mb-6 flex items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold text-foreground">New Issue</h3>
              <p className="mt-2 text-sm text-muted-foreground">Draft a bug report with AI-enhanced description and priority guidance.</p>
            </div>
            <button type="button" onClick={handleEnhance} className="rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-foreground transition hover:bg-accent" disabled={aiLoading}>
              {aiLoading ? 'Enhancing…' : 'Improve with AI'}
            </button>
          </div>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <input className="rounded-3xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary" placeholder="Issue title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
              <div className="rounded-3xl border border-border bg-background px-4 py-3 text-foreground">
                <label className="block text-sm text-muted-foreground">Project</label>
                <select className="mt-2 w-full bg-transparent text-foreground outline-none" value={form.project_id} onChange={(e) => setForm({ ...form, project_id: Number(e.target.value) })} required>
                  <option value="">Select project</option>
                  {projectsLoading ? <option>Loading projects…</option> : projects.map((project) => <option key={project.id} value={project.id}>{project.project_name}</option>)}
                </select>
              </div>
            </div>
            <textarea className="min-h-[220px] w-full rounded-3xl border border-border bg-background px-4 py-4 text-foreground outline-none transition focus:border-primary" placeholder="Describe the issue" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required />
            <div className="grid gap-4 md:grid-cols-3">
              <label className="block rounded-3xl border border-border bg-background px-4 py-3">
                <span className="block text-sm text-muted-foreground">Status</span>
                <select className="mt-2 w-full bg-transparent text-foreground outline-none" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Resolved">Resolved</option>
                </select>
              </label>
              <label className="block rounded-3xl border border-border bg-background px-4 py-3">
                <span className="block text-sm text-muted-foreground">Priority</span>
                <select className="mt-2 w-full bg-transparent text-foreground outline-none" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </label>
              <label className="block rounded-3xl border border-border bg-background px-4 py-3">
                <span className="block text-sm text-muted-foreground">Severity</span>
                <select className="mt-2 w-full bg-transparent text-foreground outline-none" value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </label>
            </div>
            {aiError && <p className="text-sm text-rose-400">{aiError}</p>}
            <button className="w-full rounded-3xl bg-primary px-5 py-4 text-sm font-semibold text-foreground transition hover:bg-accent">Create Issue</button>
          </form>
        </section>

        <aside className="space-y-6 rounded-3xl border border-border bg-card/80 p-6 shadow-glow">
          <div className="rounded-3xl bg-background p-5">
            <p className="text-sm uppercase tracking-[0.3em] text-accent/80">AI Assistant</p>
            <h2 className="mt-3 text-xl font-semibold text-foreground">Issue intelligence</h2>
            <p className="mt-2 text-sm text-muted-foreground">Refine the description, adjust priority and severity, and review root cause recommendations.</p>
          </div>

          <div className="space-y-4 rounded-3xl border border-border bg-background p-4">
            <p className="text-sm uppercase tracking-[0.32em] text-muted-foreground">AI preview</p>
            {aiResult ? (
              <div className="space-y-4">
                <div className="rounded-3xl bg-card p-4">
                  <p className="text-sm text-muted-foreground">Enhanced description</p>
                  <p className="mt-3 text-sm leading-6 text-foreground">{aiResult.enhanced_description}</p>
                </div>
                <div className="grid gap-3">
                  <div className="rounded-3xl bg-card p-4">
                    <p className="text-sm text-muted-foreground">Root cause</p>
                    <p className="mt-2 text-sm text-foreground">{aiResult.root_cause}</p>
                  </div>
                  <div className="rounded-3xl bg-card p-4">
                    <p className="text-sm text-muted-foreground">Resolution</p>
                    <p className="mt-2 text-sm text-foreground">{aiResult.resolution}</p>
                  </div>
                </div>
                <div className="grid gap-3 text-sm text-muted-foreground">
                  <div className="flex items-center justify-between rounded-2xl bg-background px-4 py-3"><span>Category</span><span className="text-accent">{aiResult.category}</span></div>
                  <div className="flex items-center justify-between rounded-2xl bg-background px-4 py-3"><span>Component</span><span className="text-accent">{aiResult.component}</span></div>
                  <div className="flex items-center justify-between rounded-2xl bg-background px-4 py-3"><span>Confidence</span><span className="text-accent">{aiResult.confidence}</span></div>
                  <div className="flex items-center justify-between rounded-2xl bg-background px-4 py-3"><span>ETA</span><span className="text-accent">{aiResult.estimated_time}</span></div>
                </div>
              </div>
            ) : (
              <div className="rounded-3xl bg-background p-4 text-sm text-muted-foreground">Add a draft description and tap "Improve with AI" to preview suggestion details.</div>
            )}
          </div>
        </aside>
      </div>
    </Layout>
  )
}
