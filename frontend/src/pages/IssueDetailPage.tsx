import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import Layout from '../components/Layout'
import { api } from '../lib/api'

export default function IssueDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [issue, setIssue] = useState<any>(null)
  const [form, setForm] = useState({ title: '', description: '', status: 'Open', priority: 'Medium', severity: 'Low' })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    api.get(`/api/issues/${id}`).then((res) => {
      setIssue(res.data)
      setForm({
        title: res.data.title || '',
        description: res.data.description || '',
        status: res.data.status || 'Open',
        priority: res.data.priority || 'Medium',
        severity: res.data.severity || 'Low',
      })
    })
  }, [id])

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      const response = await api.put(`/api/issues/${id}`, form)
      setIssue(response.data)
      await queryClient.invalidateQueries({ queryKey: ['issues'] })
      await queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      await queryClient.invalidateQueries({ queryKey: ['analytics'] })
    } catch {
      setError('Unable to update this issue right now.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this issue?')) return
    setDeleting(true)
    try {
      await api.delete(`/api/issues/${id}`)
      await queryClient.invalidateQueries({ queryKey: ['issues'] })
      await queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      await queryClient.invalidateQueries({ queryKey: ['analytics'] })
      navigate('/issues')
    } catch {
      setError('Unable to delete this issue right now.')
    } finally {
      setDeleting(false)
    }
  }

  if (!issue) return <Layout title="Issue Detail"><div className="rounded-2xl border border-border bg-card p-6">Loading...</div></Layout>

  return (
    <Layout title="Issue Detail">
      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-2xl border border-border bg-card p-6">
          <h3 className="text-2xl font-semibold text-foreground">{issue.title}</h3>
          <p className="mt-2 text-muted-foreground">{issue.description || 'No description provided.'}</p>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border border-border bg-background p-4"><p className="text-sm text-muted-foreground">Status</p><p className="font-semibold text-foreground">{issue.status}</p></div>
            <div className="rounded-xl border border-border bg-background p-4"><p className="text-sm text-muted-foreground">Priority</p><p className="font-semibold text-foreground">{issue.priority}</p></div>
            <div className="rounded-xl border border-border bg-background p-4"><p className="text-sm text-muted-foreground">Severity</p><p className="font-semibold text-foreground">{issue.severity}</p></div>
          </div>
        </div>

        <form onSubmit={handleSave} className="rounded-2xl border border-border bg-card p-6">
          <h3 className="text-xl font-semibold text-foreground">Edit issue</h3>
          <p className="mt-2 text-sm text-muted-foreground">Update the issue details and keep the analytics in sync.</p>
          <div className="mt-6 space-y-4">
            <input className="w-full rounded-3xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
            <textarea className="min-h-[180px] w-full rounded-3xl border border-border bg-background px-4 py-3 text-foreground outline-none focus:border-primary" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required />
            <div className="grid gap-4 md:grid-cols-3">
              <label className="rounded-3xl border border-border bg-background px-4 py-3">
                <span className="block text-sm text-muted-foreground">Status</span>
                <select className="mt-2 w-full bg-transparent text-foreground outline-none" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Resolved">Resolved</option>
                </select>
              </label>
              <label className="rounded-3xl border border-border bg-background px-4 py-3">
                <span className="block text-sm text-muted-foreground">Priority</span>
                <select className="mt-2 w-full bg-transparent text-foreground outline-none" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </label>
              <label className="rounded-3xl border border-border bg-background px-4 py-3">
                <span className="block text-sm text-muted-foreground">Severity</span>
                <select className="mt-2 w-full bg-transparent text-foreground outline-none" value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </label>
            </div>
            {error && <p className="text-sm text-rose-400">{error}</p>}
            <div className="flex flex-col gap-3 sm:flex-row">
              <button type="submit" className="rounded-3xl bg-primary px-4 py-3 text-sm font-semibold text-foreground transition hover:bg-accent" disabled={saving}>{saving ? 'Saving...' : 'Save changes'}</button>
              <button type="button" onClick={handleDelete} className="rounded-3xl border border-rose-500/40 px-4 py-3 text-sm font-semibold text-rose-500 transition hover:bg-rose-500/10" disabled={deleting}>{deleting ? 'Deleting...' : 'Delete issue'}</button>
            </div>
          </div>
        </form>
      </div>
    </Layout>
  )
}
