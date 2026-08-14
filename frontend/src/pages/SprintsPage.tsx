import { useState, useMemo, useEffect, type DragEvent, type FormEvent } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'
import type { Issue, Project, Sprint } from '../lib/types'

const WORKFLOW = ['Open', 'Assigned', 'In Progress', 'In Review', 'Resolved', 'Verified', 'Closed'] as const

export default function SprintsPage() {
  const qc = useQueryClient()
  const { data: sprints = [] } = useQuery<Sprint[]>({
    queryKey: ['sprints'],
    queryFn: async () => (await api.get('/api/sprints')).data,
  })
  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => (await api.get('/api/projects')).data,
  })
  const { data: issues = [] } = useQuery<Issue[]>({
    queryKey: ['issues'],
    queryFn: async () => (await api.get('/api/issues', { params: { size: 200 } })).data,
  })

  const blank = { name: '', goal: '', start_date: '', end_date: '', status: 'Planned', project_id: '' }
  const [form, setForm] = useState<any>(blank)
  const [editing, setEditing] = useState<number | null>(null)

  useEffect(() => {
    if (!form.project_id && projects[0]) {
      setForm((current: any) => ({ ...current, project_id: String(projects[0].id) }))
    }
  }, [projects, form.project_id])

  const sprintIssues = useMemo(() => {
    const map = new Map<number, Issue[]>()
    for (const sprint of sprints) map.set(sprint.id, [])
    for (const issue of issues) {
      if (issue.sprint_id == null) continue
      const current = map.get(issue.sprint_id) || []
      current.push(issue)
      map.set(issue.sprint_id, current)
    }
    return map
  }, [sprints, issues])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    const payload = { ...form, project_id: Number(form.project_id) }
    if (editing) await api.put(`/api/sprints/${editing}`, payload)
    else await api.post('/api/sprints', payload)
    setForm(blank)
    setEditing(null)
    qc.invalidateQueries({ queryKey: ['sprints'] })
    qc.invalidateQueries({ queryKey: ['dashboard'] })
  }

  const handleDeleteSprint = async (sprintId: number) => {
    if (!window.confirm('Delete sprint?')) return
    await api.delete(`/api/sprints/${sprintId}`)
    qc.invalidateQueries({ queryKey: ['sprints'] })
    qc.invalidateQueries({ queryKey: ['issues'] })
    qc.invalidateQueries({ queryKey: ['dashboard'] })
  }

  const moveIssue = async (issueId: number, nextStatus: string) => {
    const currentIssue = issues.find((item) => item.id === issueId)
    if (!currentIssue || currentIssue.status === nextStatus) return

    await api.put(`/api/issues/${issueId}`, { status: nextStatus })
    qc.invalidateQueries({ queryKey: ['issues'] })
    qc.invalidateQueries({ queryKey: ['sprints'] })
    qc.invalidateQueries({ queryKey: ['dashboard'] })
  }

  const onDragStart = (event: DragEvent<HTMLDivElement>, issueId: number) => {
    event.dataTransfer.setData('text/plain', JSON.stringify({ issueId }))
  }

  const onDrop = async (event: DragEvent<HTMLDivElement>, status: string) => {
    event.preventDefault()
    const raw = event.dataTransfer.getData('text/plain')
    if (!raw) return
    try {
      const { issueId } = JSON.parse(raw)
      await moveIssue(Number(issueId), status)
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Unable to move issue')
    }
  }

  const allowDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  return (
    <Layout title="Sprints">
      <div className="grid gap-6 lg:grid-cols-[1fr_.65fr]">
        <section className="space-y-4">
          <div className="rounded-3xl border border-border bg-card p-5 shadow-glow">
            <h2 className="text-xl font-semibold">Sprint List</h2>
            <div className="mt-4 space-y-4">
              {sprints.length === 0 ? (
                <p className="text-sm text-muted-foreground">No sprints yet.</p>
              ) : (
                sprints.map((sprint) => {
                  const sprintItems = sprintIssues.get(sprint.id) || []
                  const resolvedCount = sprintItems.filter((issue) => issue.status === 'Resolved').length
                  const progress = sprintItems.length ? Math.round((resolvedCount / sprintItems.length) * 100) : 0

                  return (
                    <div key={sprint.id} className="rounded-2xl border border-border bg-background p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="font-semibold">{sprint.name}</h3>
                          <p className="mt-1 text-sm text-muted-foreground">{sprint.goal || 'No sprint goal provided.'}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              setEditing(sprint.id)
                              setForm({ ...sprint, project_id: String(sprint.project_id) })
                            }}
                            className="text-sm text-primary"
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDeleteSprint(sprint.id)}
                            className="text-sm text-rose-500"
                          >
                            Delete
                          </button>
                        </div>
                      </div>

                      <div className="mt-4 flex items-center justify-between text-sm text-muted-foreground">
                        <span>{sprintItems.length} issues</span>
                        <span>{resolvedCount} resolved</span>
                      </div>
                      <div className="mt-2 h-2 rounded bg-border">
                        <div className="h-2 rounded bg-primary" style={{ width: `${progress}%` }} />
                      </div>
                      <div className="mt-3 text-xs text-muted-foreground">
                        {sprint.start_date} to {sprint.end_date} · {sprint.status}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </section>

        <aside className="space-y-4 rounded-3xl border border-border bg-card p-6 shadow-glow">
          <form onSubmit={submit} className="space-y-3">
            <h3 className="text-lg font-semibold">{editing ? 'Edit Sprint' : 'Create Sprint'}</h3>
            <input
              className="w-full rounded-xl border border-border bg-background p-3"
              placeholder="Sprint name"
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
            />
            <textarea
              className="w-full rounded-xl border border-border bg-background p-3"
              placeholder="Goal"
              value={form.goal}
              onChange={(event) => setForm({ ...form, goal: event.target.value })}
            />
            <input
              type="date"
              className="w-full rounded-xl border border-border bg-background p-3"
              value={form.start_date}
              onChange={(event) => setForm({ ...form, start_date: event.target.value })}
            />
            <input
              type="date"
              className="w-full rounded-xl border border-border bg-background p-3"
              value={form.end_date}
              onChange={(event) => setForm({ ...form, end_date: event.target.value })}
            />
            <select
              className="w-full rounded-xl border border-border bg-background p-3"
              value={String(form.project_id)}
              onChange={(event) => setForm({ ...form, project_id: event.target.value })}
            >
              <option value="">Select project</option>
              {projects.map((project) => (
                <option key={project.id} value={String(project.id)}>{project.project_name}</option>
              ))}
            </select>
            <div className="flex gap-2">
              <button type="submit" className="rounded-xl bg-primary px-4 py-2 text-foreground">Save</button>
              <button
                type="button"
                onClick={() => {
                  setForm(blank)
                  setEditing(null)
                }}
                className="rounded-xl border border-border px-4 py-2"
              >
                Cancel
              </button>
            </div>
          </form>
        </aside>
      </div>

      <section className="mt-6 rounded-3xl border border-border bg-card p-6 shadow-glow">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Agile Workflow</p>
            <h2 className="text-2xl font-semibold">Kanban Board</h2>
          </div>
          <div className="rounded-full bg-primary/10 px-3 py-1 text-sm text-primary">Live</div>
        </div>

        <div className="grid gap-4 xl:grid-cols-7">
          {WORKFLOW.map((status) => {
            const columnIssues = issues.filter((issue) => issue.status === status)

            return (
              <div
                key={status}
                onDragOver={allowDrop}
                onDrop={(event) => onDrop(event, status)}
                className="min-h-[260px] rounded-2xl border border-border bg-background p-3"
              >
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="font-semibold">{status}</h3>
                  <span className="rounded-full bg-card px-2 py-1 text-xs text-muted-foreground">{columnIssues.length}</span>
                </div>

                <div className="space-y-3">
                  {columnIssues.length === 0 ? (
                    <div className="rounded-xl border border-dashed border-border bg-card p-3 text-sm text-muted-foreground">
                      No issues in {status}
                    </div>
                  ) : (
                    columnIssues.map((issue) => (
                      <div
                        key={issue.id}
                        draggable
                        onDragStart={(event) => onDragStart(event, issue.id)}
                        className="rounded-xl border border-border bg-card p-3 shadow-sm"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="font-medium text-foreground">{issue.title}</h4>
                          <span className="rounded-full bg-primary/10 px-2 py-1 text-[10px] font-medium uppercase text-primary">
                            {issue.severity}
                          </span>
                        </div>

                        <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
                          <span className="rounded-full bg-background px-2 py-1 text-muted-foreground">{issue.priority}</span>
                          <span className="rounded-full bg-background px-2 py-1 text-muted-foreground">{issue.assignee_name || 'Unassigned'}</span>
                        </div>

                        <div className="mt-3 text-xs text-muted-foreground">
                          <div>Assignee: {issue.assignee_name || 'Unassigned'}</div>
                          <div>Sprint: {issue.sprint_name || 'No sprint'}</div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </section>
    </Layout>
  )
}
